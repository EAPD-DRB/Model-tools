#!/usr/bin/env python3
"""Validate an evidence-driven CLEWs country-calibration package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PRE_SOLVE_GATES = (
    "inherited_provenance",
    "source_diff_allowlist",
    "identifier_integrity",
    "connectivity_review",
    "equation_unit_replay",
    "generated_data_inspection",
    "stock_resource_account_checks",
    "matrix_check",
    "schema_ledger_validation",
)
PROMOTION_GATES = PRE_SOLVE_GATES + (
    "solver_run",
    "baseline_comparison",
    "live_regeneration",
    "result_free_archive_identity",
)
FINDING_STATUSES = {"pending", "resolved", "declared", "deferred"}


def require_text(
    container: dict[str, Any], field: str, location: str, errors: list[str]
) -> None:
    if not isinstance(container.get(field), str) or not container[field].strip():
        errors.append(f"{location}.{field} must be non-empty text")


def require_text_list(
    container: dict[str, Any],
    field: str,
    location: str,
    errors: list[str],
    *,
    nonempty: bool = True,
) -> list[str]:
    value = container.get(field)
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        qualifier = "a non-empty" if nonempty else "a"
        errors.append(f"{location}.{field} must be {qualifier} list of text")
        return []
    return value


def resolve(base_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else base_dir / path


def validate_gate(
    gate: Any,
    location: str,
    required: bool,
    base_dir: Path,
    errors: list[str],
) -> None:
    if not isinstance(gate, dict):
        errors.append(f"{location} must be an object")
        return
    status = gate.get("status")
    if status not in {"pending", "passed", "failed", "not_applicable"}:
        errors.append(f"{location}.status is invalid")
        return
    if required and status not in {"passed", "not_applicable"}:
        errors.append(f"{location}.status must be passed or not_applicable")
        return
    if required and status == "passed":
        artifact = gate.get("artifact")
        if not isinstance(artifact, str) or not artifact.strip():
            errors.append(f"{location}.artifact is required when passed")
        elif not resolve(base_dir, artifact).is_file():
            errors.append(f"{location}.artifact does not exist: {artifact}")


def validate_package(
    package: Any, stage: str, package_dir: Path | None = None
) -> list[str]:
    errors: list[str] = []
    base_dir = Path(package_dir).expanduser() if package_dir else Path.cwd()
    if not isinstance(package, dict):
        return ["package root must be a JSON object"]
    if package.get("schema_version") != 1:
        errors.append("schema_version must equal 1")

    case = package.get("case")
    if not isinstance(case, dict):
        errors.append("case must be an object")
    else:
        for field in (
            "source_case",
            "candidate_case",
            "baseline_run",
            "scenario",
            "horizon",
            "intended_use",
        ):
            require_text(case, field, "case", errors)
        if case.get("source_case") == case.get("candidate_case"):
            errors.append(
                "case.candidate_case must be disposable and distinct from source_case"
            )

    provenance = package.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        for field in ("inherited_ledger_dir", "retained_evidence_dir"):
            require_text(provenance, field, "provenance", errors)
        if provenance.get("complete_inherited_copy") is not True:
            errors.append("provenance.complete_inherited_copy must be true")
        if provenance.get("requires_previous_version_to_interpret") is not False:
            errors.append(
                "provenance.requires_previous_version_to_interpret must be false"
            )
        required = stage in {"pre-solve", "promotion"}
        for field in ("ledger_validation", "populated_input_coverage"):
            validate_gate(
                provenance.get(field),
                f"provenance.{field}",
                required,
                base_dir,
                errors,
            )
        if required:
            for field in ("inherited_ledger_dir", "retained_evidence_dir"):
                value = provenance.get(field)
                if (
                    isinstance(value, str)
                    and value.strip()
                    and not resolve(base_dir, value).is_dir()
                ):
                    errors.append(f"provenance.{field} does not exist: {value}")

    backlog = package.get("backlog")
    if not isinstance(backlog, dict):
        errors.append("backlog must be an object")
    else:
        require_text(backlog, "path", "backlog", errors)
        require_text(backlog, "prioritization_basis", "backlog", errors)
        if stage in {"pre-solve", "promotion"}:
            value = backlog.get("path")
            if (
                isinstance(value, str)
                and value.strip()
                and not resolve(base_dir, value).is_file()
            ):
                errors.append(f"backlog.path does not exist: {value}")

    packages = package.get("packages")
    package_ids: set[str] = set()
    if not isinstance(packages, list) or not packages:
        errors.append("packages must be a non-empty list")
        packages = []
    for index, item in enumerate(packages):
        location = f"packages[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{location} must be an object")
            continue
        for field in ("package_id", "name", "current_weakness", "objective"):
            require_text(item, field, location, errors)
        package_id = item.get("package_id")
        if isinstance(package_id, str):
            if package_id in package_ids:
                errors.append(f"{location}.package_id duplicates {package_id}")
            package_ids.add(package_id)
        require_text_list(item, "affected_sectors", location, errors)
        require_text_list(
            item, "connectivity_finding_ids", location, errors, nonempty=False
        )

    changes = package.get("changes")
    change_ids: set[str] = set()
    if not isinstance(changes, list) or not changes:
        errors.append("changes must be a non-empty list")
        changes = []
    for index, item in enumerate(changes):
        location = f"changes[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{location} must be an object")
            continue
        for field in (
            "change_id",
            "package_id",
            "parameter",
            "source_file",
            "coordinates",
            "model_unit",
            "physical_effect",
        ):
            require_text(item, field, location, errors)
        change_id = item.get("change_id")
        if isinstance(change_id, str):
            if change_id in change_ids:
                errors.append(f"{location}.change_id duplicates {change_id}")
            change_ids.add(change_id)
        if item.get("package_id") not in package_ids:
            errors.append(f"{location}.package_id does not resolve")
        require_text_list(item, "local_equations", location, errors)
        require_text_list(item, "evidence_ids", location, errors)
        require_text_list(item, "model_map_ids", location, errors)
        if item.get("source_diff_allowed") is not True:
            errors.append(f"{location}.source_diff_allowed must be true")

    benchmarks = package.get("benchmarks")
    if not isinstance(benchmarks, list):
        errors.append("benchmarks must be a list")
        benchmarks = []
    for index, item in enumerate(benchmarks):
        location = f"benchmarks[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{location} must be an object")
            continue
        require_text(item, "name", location, errors)
        require_text_list(item, "source_ids", location, errors)
        affected = require_text_list(
            item, "affected_parameters", location, errors, nonempty=False
        )
        if affected:
            errors.append(f"{location} is diagnostic and cannot affect parameters")
        if item.get("diagnostic_only") is not True:
            errors.append(f"{location}.diagnostic_only must be true")

    connectivity = package.get("connectivity")
    if not isinstance(connectivity, dict):
        errors.append("connectivity must be an object")
    else:
        require_text(connectivity, "rules", "connectivity", errors)
        validate_gate(
            connectivity.get("audit"),
            "connectivity.audit",
            stage in {"pre-solve", "promotion"},
            base_dir,
            errors,
        )
        dispositions = connectivity.get("finding_dispositions")
        if not isinstance(dispositions, list):
            errors.append("connectivity.finding_dispositions must be a list")
            dispositions = []
        for index, item in enumerate(dispositions):
            location = f"connectivity.finding_dispositions[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{location} must be an object")
                continue
            require_text(item, "finding_id", location, errors)
            require_text(item, "resolution", location, errors)
            status = item.get("status")
            if status not in FINDING_STATUSES:
                errors.append(
                    f"{location}.status must be one of {sorted(FINDING_STATUSES)}"
                )
            if stage == "promotion" and status == "pending":
                errors.append(f"{location}.status cannot remain pending at promotion")
            evidence = require_text_list(
                item, "evidence_ids", location, errors, nonempty=False
            )
            if (
                stage == "promotion"
                and status in {"resolved", "declared", "deferred"}
                and not evidence
            ):
                errors.append(f"{location}.evidence_ids are required at promotion")

    runtime = package.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("runtime must be an object")
    else:
        for field in ("known_good_seconds", "candidate_budget_seconds"):
            value = runtime.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"runtime.{field} must be positive")
        require_text(runtime, "baseline_artifact", "runtime", errors)

    gates = package.get("gates")
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
    else:
        required_names = set(PROMOTION_GATES)
        missing = sorted(required_names - set(gates))
        if missing:
            errors.append(f"gates missing required entries: {missing}")
        required = set()
        if stage == "pre-solve":
            required = set(PRE_SOLVE_GATES)
        elif stage == "promotion":
            required = set(PROMOTION_GATES)
        for name in PROMOTION_GATES:
            if name in gates:
                validate_gate(
                    gates[name],
                    f"gates.{name}",
                    name in required,
                    base_dir,
                    errors,
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument(
        "--stage",
        choices=("design", "pre-solve", "promotion"),
        default="design",
    )
    args = parser.parse_args()
    try:
        package = json.loads(args.package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    errors = validate_package(package, args.stage, args.package.resolve().parent)
    if errors:
        print("calibration package: FAIL", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"calibration package: PASS (stage={args.stage})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
