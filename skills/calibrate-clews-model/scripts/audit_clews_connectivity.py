#!/usr/bin/env python3
"""Audit MUIO technology/commodity connectivity and unlimited-free candidates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROLE_INPUT_EXEMPT = {"resource_supply", "accounting", "environmental_sink"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(
    document: dict[str, Any], parameter: str, scenario: str
) -> list[dict[str, Any]]:
    value = document.get(parameter, {})
    if not isinstance(value, dict):
        return []
    selected = value.get(scenario, [])
    return selected if isinstance(selected, list) else []


def positive_year_value(row: dict[str, Any], years: list[str]) -> bool:
    return any(
        isinstance(row.get(year), (int, float)) and row[year] > 0 for year in years
    )


def numeric_values(row: dict[str, Any], years: list[str]) -> list[float]:
    return [
        float(row[year]) for year in years if isinstance(row.get(year), (int, float))
    ]


def row_index(
    source: list[dict[str, Any]], include_mode: bool = False
) -> dict[tuple[str, int | None], dict[str, Any]]:
    indexed: dict[tuple[str, int | None], dict[str, Any]] = {}
    for row in source:
        tech = row.get("TechId")
        if not isinstance(tech, str):
            continue
        mode = row.get("MoId") if include_mode else None
        indexed[(tech, mode)] = row
    return indexed


def all_nonpositive(row: dict[str, Any] | None, years: list[str]) -> bool:
    if row is None:
        return True
    values = numeric_values(row, years)
    return not values or max(values) <= 0


def has_finite_upper(
    row: dict[str, Any] | None, years: list[str], threshold: float
) -> bool:
    if row is None:
        return False
    values = numeric_values(row, years)
    return bool(values) and any(-1 < value < threshold for value in values)


def all_zero(row: dict[str, Any] | None, years: list[str]) -> bool:
    if row is None:
        return False
    values = numeric_values(row, years)
    return bool(values) and all(value == 0 for value in values)


def audit(case_dir: Path, rules: dict[str, Any]) -> dict[str, Any]:
    gen = load(case_dir / "genData.json")
    rytcm = load(case_dir / "RYTCM.json")
    ryt = load(case_dir / "RYT.json")
    rytm = load(case_dir / "RYTM.json")
    scenario = str(
        rules.get("scenario")
        or next(
            (
                item.get("ScenarioId")
                for item in gen.get("osy-scenarios", [])
                if item.get("Active")
            ),
            "SC_0",
        )
    )
    years = [str(year) for year in gen.get("osy-years", [])]
    threshold = float(rules.get("unbounded_threshold", 99990))

    technologies = {
        item["TechId"]: item
        for item in gen.get("osy-tech", [])
        if isinstance(item, dict) and isinstance(item.get("TechId"), str)
    }
    commodities = {
        item["CommId"]: item
        for item in gen.get("osy-comm", [])
        if isinstance(item, dict) and isinstance(item.get("CommId"), str)
    }
    roles = rules.get("technology_roles", {})
    terminal = set(rules.get("terminal_commodity_ids", []))
    exogenous = set(rules.get("exogenous_commodity_ids", []))

    mode_inputs: dict[tuple[str, int], set[str]] = defaultdict(set)
    mode_outputs: dict[tuple[str, int], set[str]] = defaultdict(set)
    producers: dict[str, set[str]] = defaultdict(set)
    consumers: dict[str, set[str]] = defaultdict(set)
    for parameter, target, graph in (
        ("IAR", mode_inputs, consumers),
        ("OAR", mode_outputs, producers),
    ):
        for row in rows(rytcm, parameter, scenario):
            tech, commodity, mode = (
                row.get("TechId"),
                row.get("CommId"),
                row.get("MoId"),
            )
            if (
                not isinstance(tech, str)
                or not isinstance(commodity, str)
                or not isinstance(mode, int)
            ):
                continue
            if positive_year_value(row, years):
                target[(tech, mode)].add(commodity)
                graph[commodity].add(f"{tech}:{mode}")

    findings: list[dict[str, Any]] = []

    def add(kind: str, entity: str, severity: str, message: str, detail: Any) -> None:
        findings.append(
            {
                "finding_id": f"{kind}:{entity}",
                "finding_type": kind,
                "entity_id": entity,
                "severity": severity,
                "message": message,
                "detail": detail,
            }
        )

    for commodity, metadata in commodities.items():
        produced, consumed = (
            producers.get(commodity, set()),
            consumers.get(commodity, set()),
        )
        label = metadata.get("Comm", commodity)
        if produced and not consumed and commodity not in terminal:
            add(
                "commodity_without_consumer",
                commodity,
                "medium",
                f"{label} is produced but never consumed",
                sorted(produced),
            )
        if consumed and not produced and commodity not in exogenous:
            add(
                "commodity_without_producer",
                commodity,
                "high",
                f"{label} is consumed but has no modeled producer",
                sorted(consumed),
            )
        if not produced and not consumed and commodity not in terminal | exogenous:
            add(
                "unused_commodity",
                commodity,
                "low",
                f"{label} has no positive input or output ratio",
                {},
            )

    vc = row_index(rows(rytm, "VC", scenario), include_mode=True)
    tamul = row_index(rows(rytm, "TAMUL", scenario), include_mode=True)
    tau = row_index(rows(ryt, "TAU", scenario))
    cc = row_index(rows(ryt, "CC", scenario))
    fc = row_index(rows(ryt, "FC", scenario))
    tamaxc = row_index(rows(ryt, "TAMaxC", scenario))
    tamaxci = row_index(rows(ryt, "TAMaxCI", scenario))

    for key, outputs in sorted(mode_outputs.items()):
        tech, mode = key
        entity = f"{tech}:{mode}"
        role = (
            roles.get(tech, {}).get("role")
            if isinstance(roles.get(tech), dict)
            else None
        )
        inputs = mode_inputs.get(key, set())
        if not inputs and role not in ROLE_INPUT_EXEMPT:
            add(
                "inputless_output_mode",
                entity,
                "medium",
                "Mode has useful output but no positive modeled input and no exempt declared role",
                {"outputs": sorted(outputs), "declared_role": role},
            )
        activity_bounded = has_finite_upper(
            tamul.get(key), years, threshold
        ) or has_finite_upper(tau.get((tech, None)), years, threshold)
        capacity_bounded = has_finite_upper(
            tamaxc.get((tech, None)), years, threshold
        ) or has_finite_upper(tamaxci.get((tech, None)), years, threshold)
        zero_cost = (
            all_nonpositive(vc.get(key), years)
            and all_nonpositive(cc.get((tech, None)), years)
            and all_nonpositive(fc.get((tech, None)), years)
        )
        if not inputs and zero_cost and not activity_bounded and not capacity_bounded:
            add(
                "unlimited_free_output_candidate",
                entity,
                "high",
                "Inputless output mode has no positive modeled cost or finite activity/capacity upper bound",
                {
                    "outputs": sorted(outputs),
                    "declared_role": role,
                    "threshold": threshold,
                },
            )
        if all_zero(tamul.get(key), years) or all_zero(tau.get((tech, None)), years):
            add(
                "zero_upper_requires_export_check",
                entity,
                "medium",
                "Source upper bound is zero; verify that the exporter preserves it as an active bound",
                {
                    "parameters": [
                        name
                        for name, row in (
                            ("TAMUL", tamul.get(key)),
                            ("TAU", tau.get((tech, None))),
                        )
                        if all_zero(row, years)
                    ]
                },
            )

    for item in rules.get("required_links", []):
        if not isinstance(item, dict):
            continue
        required = set(item.get("required_input_commodity_ids", []))
        require_all = item.get("require_all", True)
        for tech in item.get("technology_ids", []):
            modes = sorted(key for key in mode_outputs if key[0] == tech)
            for key in modes:
                present = mode_inputs.get(key, set())
                satisfied = (
                    required <= present if require_all else bool(required & present)
                )
                if not satisfied:
                    entity = f"{key[0]}:{key[1]}"
                    add(
                        "required_link_missing",
                        entity,
                        "high",
                        str(
                            item.get("reason")
                            or "Declared physical input link is missing"
                        ),
                        {
                            "rule_id": item.get("rule_id"),
                            "required": sorted(required),
                            "present": sorted(present),
                            "require_all": require_all,
                        },
                    )

    exemption_keys = {
        (item.get("finding_type"), item.get("entity_id")): item
        for item in rules.get("reviewed_exemptions", [])
        if isinstance(item, dict)
    }
    active, exempted = [], []
    for finding in findings:
        exemption = exemption_keys.get((finding["finding_type"], finding["entity_id"]))
        if exemption:
            finding = {**finding, "exemption": exemption}
            exempted.append(finding)
        else:
            active.append(finding)
    counts = {
        severity: sum(item["severity"] == severity for item in active)
        for severity in ("high", "medium", "low")
    }
    return {
        "schema": "clews-connectivity-audit-v1",
        "case_dir": str(case_dir.resolve()),
        "scenario": scenario,
        "years": years,
        "technology_count": len(technologies),
        "commodity_count": len(commodities),
        "status": "findings" if active else "pass",
        "summary": {"active": len(active), "exempted": len(exempted), **counts},
        "findings": active,
        "reviewed_exemptions": exempted,
        "interpretation": "Findings are audit candidates. Resolve, declare with evidence, or defer in the schema ledger after equation and role review.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on", choices=("none", "high", "all"), default="none")
    args = parser.parse_args()
    try:
        report = audit(args.case_dir.resolve(), load(args.rules))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if args.fail_on == "high" and report["summary"]["high"]:
        return 1
    if args.fail_on == "all" and report["summary"]["active"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
