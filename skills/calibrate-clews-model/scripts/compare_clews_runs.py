#!/usr/bin/env python3
"""Compare two CLEWs CSV result directories without mistaking row noise for structure."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


STRUCTURAL_FILES = {
    "Demand.csv",
    "AnnualTechnologyEmission.csv",
    "TotalCapacityAnnual.csv",
    "NewCapacity.csv",
    "ObjectiveValue.csv",
}


def table(path: Path) -> tuple[list[str], str, dict[tuple[str, ...], float]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) < 2:
            raise ValueError(f"{path} has no usable header")
        keys, value = reader.fieldnames[:-1], reader.fieldnames[-1]
        values: dict[tuple[str, ...], float] = defaultdict(float)
        for line, row in enumerate(reader, start=2):
            try:
                number = float(row[value])
            except (TypeError, ValueError) as error:
                raise ValueError(f"{path}:{line} {value} is not numeric") from error
            values[tuple(row[key] for key in keys)] += number
    return keys, value, dict(values)


def compare(
    baseline: Path,
    candidate: Path,
    tolerance: float,
    structural_files: set[str] | None = None,
) -> dict[str, Any]:
    structural_files = (
        STRUCTURAL_FILES if structural_files is None else structural_files
    )
    baseline_files = {path.name for path in baseline.glob("*.csv")}
    candidate_files = {path.name for path in candidate.glob("*.csv")}
    if not baseline_files:
        raise ValueError(f"{baseline} contains no CSV result tables")
    if not candidate_files:
        raise ValueError(f"{candidate} contains no CSV result tables")
    common = sorted(baseline_files & candidate_files)
    baseline_only = sorted(baseline_files - candidate_files)
    candidate_only = sorted(candidate_files - baseline_files)
    reports = []
    for name in common:
        bkeys, bvalue, before = table(baseline / name)
        ckeys, cvalue, after = table(candidate / name)
        if bkeys != ckeys or bvalue != cvalue:
            reports.append({"file": name, "status": "schema_mismatch"})
            continue
        keys = set(before) | set(after)
        differences = [after.get(key, 0.0) - before.get(key, 0.0) for key in keys]
        changed = [
            difference for difference in differences if abs(difference) > tolerance
        ]
        total_before, total_after = sum(before.values()), sum(after.values())
        percent = (
            None
            if total_before == 0
            else (total_after - total_before) / abs(total_before) * 100
        )
        reports.append(
            {
                "file": name,
                "status": "changed" if changed else "unchanged",
                "structural_priority": name in structural_files,
                "key_columns": bkeys,
                "value_column": bvalue,
                "baseline_total": total_before,
                "candidate_total": total_after,
                "total_change": total_after - total_before,
                "percent_change": percent,
                "changed_rows": len(changed),
                "maximum_absolute_row_change": max(
                    (abs(value) for value in changed), default=0.0
                ),
            }
        )
    structural = [item for item in reports if item.get("structural_priority")]
    structural_summary = {item["file"]: item["status"] for item in structural}
    for name in baseline_only:
        if name in structural_files:
            structural_summary[name] = "baseline_only"
    for name in candidate_only:
        if name in structural_files:
            structural_summary[name] = "candidate_only"
    schema_mismatch = any(item["status"] == "schema_mismatch" for item in reports)
    return {
        "schema": "clews-run-comparison-v1",
        "status": "fail" if schema_mismatch else "pass",
        "baseline": str(baseline.resolve()),
        "candidate": str(candidate.resolve()),
        "tolerance": tolerance,
        "common_file_count": len(common),
        "baseline_only": baseline_only,
        "candidate_only": candidate_only,
        "structural_files": sorted(structural_files),
        "structural_summary": structural_summary,
        "files": reports,
        "interpretation": "Inspect structural totals before row-level dispatch. Changed activity rows may be alternative optima and require aggregate physical review.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_csv_dir", type=Path)
    parser.add_argument("candidate_csv_dir", type=Path)
    parser.add_argument("--tolerance", type=float, default=1e-7)
    parser.add_argument(
        "--structural",
        action="append",
        metavar="CSV",
        help="structural-priority result table; repeat to replace the defaults",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance < 0:
        print("FAIL: tolerance must be finite and nonnegative", file=sys.stderr)
        return 2
    try:
        structural = set(args.structural) if args.structural else None
        report = compare(
            args.baseline_csv_dir, args.candidate_csv_dir, args.tolerance, structural
        )
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
