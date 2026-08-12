#!/usr/bin/env python3
"""Validate an evidence-driven CLEWs country-calibration package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PRE_SOLVE_GATES = (
    "identifier_integrity",
    "connectivity_review",
    "equation_unit_replay",
    "generated_data_inspection",
    "stock_resource_account_checks",
    "matrix_check",
    "schema_ledger_validation",
)
SOURCE_INPUT_PATCH_GATES = (
    "identifier_integrity",
    "generated_data_inspection",
    "schema_ledger_validation",
    "live_regeneration",
    "result_free_archive_identity",
)
PROMOTION_GATES = PRE_SOLVE_GATES + (
    "solver_run",
    "baseline_comparison",
    "live_regeneration",
    "result_free_archive_identity",
)
MATERIAL_STAGES = {"source-input-patch", "pre-solve", "promotion"}
FINDING_STATUSES = {"pending", "resolved", "declared", "deferred"}
OPTIONAL_GATES = {"matrix_check", "stock_resource_account_checks"}
DELIVERY_STATES = {"working", "source_input_patch", "promoted"}
RESULT_STATUSES = {"absent", "stale", "fresh"}
LEDGER_IDS = {
    "SOURCES.csv": "source_id",
    "CALCULATIONS.csv": "calculation_id",
    "ASSUMPTIONS.csv": "assumption_id",
    "MODEL_MAP.csv": "map_id",
    "GAPS.csv": "item",
    "CHANGES.csv": "change_id",
}


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


def require_resolves(
    values: list[str], allowed: set[str], location: str, errors: list[str]
) -> None:
    for value in values:
        if value not in allowed:
            errors.append(f"{location} does not resolve: {value}")


def resolve(base_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else base_dir / path


def read_json(path: Path, location: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{location} is not readable JSON: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{location} must contain a JSON object")
        return None
    return value


def read_ledger(
    ledger_dir: Path, errors: list[str]
) -> tuple[dict[str, set[str]], dict[str, dict[str, dict[str, str]]]]:
    ids: dict[str, set[str]] = {}
    rows_by_id: dict[str, dict[str, dict[str, str]]] = {}
    for filename, id_field in LEDGER_IDS.items():
        path = ledger_dir / filename
        try:
            with path.open(newline="", encoding="utf-8-sig") as stream:
                rows = list(csv.DictReader(stream))
        except OSError as error:
            errors.append(f"cannot read provenance ledger {path}: {error}")
            rows = []
        indexed = {
            row.get(id_field, "").strip(): row
            for row in rows
            if row.get(id_field, "").strip()
        }
        ids[filename] = set(indexed)
        rows_by_id[filename] = indexed
    return ids, rows_by_id


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def changed_source_json(baseline: Path, candidate: Path) -> set[str]:
    before = {path.name: path for path in baseline.glob("*.json") if path.is_file()}
    after = {path.name: path for path in candidate.glob("*.json") if path.is_file()}
    return {
        name
        for name in set(before) | set(after)
        if name not in before
        or name not in after
        or sha256(before[name]) != sha256(after[name])
    }


def validate_inheritance(
    predecessor: Path, current: Path, retained_evidence: Path, errors: list[str]
) -> None:
    predecessor_ids, predecessor_rows = read_ledger(predecessor, errors)
    current_ids, current_rows = read_ledger(current, errors)
    for filename, id_field in LEDGER_IDS.items():
        missing = sorted(predecessor_ids[filename] - current_ids[filename])
        if missing:
            errors.append(
                f"provenance inheritance dropped {filename} {id_field}s: {missing}"
            )
        if filename == "GAPS.csv":
            continue
        if filename == "MODEL_MAP.csv":
            ignored = {"superseded_by", "notes"}
        else:
            ignored = {"notes"}
        for identifier in sorted(predecessor_ids[filename] & current_ids[filename]):
            before = {
                key: value
                for key, value in predecessor_rows[filename][identifier].items()
                if key not in ignored
            }
            after = {
                key: value
                for key, value in current_rows[filename][identifier].items()
                if key not in ignored
            }
            if before != after:
                errors.append(
                    f"provenance inheritance altered retained {filename} row {identifier}"
                )
    previous_evidence = predecessor / "evidence"
    if not previous_evidence.is_dir():
        errors.append(
            f"predecessor retained evidence does not exist: {previous_evidence}"
        )
        return
    for source in sorted(
        path for path in previous_evidence.rglob("*") if path.is_file()
    ):
        relative = source.relative_to(previous_evidence)
        target = retained_evidence / relative
        if not target.is_file():
            errors.append(
                f"provenance inheritance dropped retained evidence: {relative}"
            )
        elif sha256(source) != sha256(target):
            errors.append(
                f"provenance inheritance altered retained evidence: {relative}"
            )


def validate_gate(
    gate: Any,
    location: str,
    required: bool,
    base_dir: Path,
    errors: list[str],
    *,
    gate_name: str | None = None,
) -> Path | None:
    if not isinstance(gate, dict):
        errors.append(f"{location} must be an object")
        return None
    status = gate.get("status")
    if status not in {"pending", "passed", "failed", "not_applicable"}:
        errors.append(f"{location}.status is invalid")
        return None
    if required and status not in {"passed", "not_applicable"}:
        errors.append(f"{location}.status must be passed or not_applicable")
        return None
    if status == "not_applicable":
        require_text(gate, "reason", location, errors)
        if required and gate_name not in OPTIONAL_GATES:
            errors.append(f"{location} is mandatory and cannot be not_applicable")
        return None
    if status == "passed":
        artifact = gate.get("artifact")
        if not isinstance(artifact, str) or not artifact.strip():
            errors.append(f"{location}.artifact is required when passed")
        elif not resolve(base_dir, artifact).is_file():
            errors.append(f"{location}.artifact does not exist: {artifact}")
        else:
            return resolve(base_dir, artifact)
    return None


def validate_report(
    path: Path | None,
    location: str,
    errors: list[str],
    *,
    schema: str | None = None,
    allowed_statuses: set[str] | None = None,
) -> dict[str, Any] | None:
    if path is None:
        return None
    report = read_json(path, f"{location}.artifact", errors)
    if report is None:
        return None
    if schema is not None and report.get("schema") != schema:
        errors.append(f"{location}.artifact schema must equal {schema}")
    statuses = {"pass"} if allowed_statuses is None else allowed_statuses
    if report.get("status") not in statuses:
        errors.append(f"{location}.artifact status must be one of {sorted(statuses)}")
    return report


def validate_package(
    package: Any,
    stage: str,
    package_dir: Path | None = None,
    case_dir: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    root = case_dir if case_dir is not None else package_dir
    base_dir = Path(root).expanduser().resolve() if root else Path.cwd()
    ledger_ids: dict[str, set[str]] = {}
    ledger_rows: dict[str, dict[str, dict[str, str]]] = {}
    ledger_dir: Path | None = None
    if not isinstance(package, dict):
        return ["package root must be a JSON object"]
    if package.get("schema_version") != 2:
        errors.append("schema_version must equal 2")

    case = package.get("case")
    if not isinstance(case, dict):
        errors.append("case must be an object")
    else:
        for field in (
            "source_case",
            "candidate_case",
            "baseline_run",
            "source_json_dir",
            "candidate_json_dir",
            "scenario",
            "horizon",
            "intended_use",
        ):
            require_text(case, field, "case", errors)
        if case.get("source_case") == case.get("candidate_case"):
            errors.append(
                "case.candidate_case must be disposable and distinct from source_case"
            )
        if stage in MATERIAL_STAGES:
            source_dirs: dict[str, Path] = {}
            for field in ("source_json_dir", "candidate_json_dir"):
                value = case.get(field)
                if isinstance(value, str) and value.strip():
                    source_dirs[field] = resolve(base_dir, value).resolve()
                    if not source_dirs[field].is_dir():
                        errors.append(f"case.{field} does not exist: {value}")
            if len(source_dirs) == 2:
                changed_files = changed_source_json(
                    source_dirs["source_json_dir"], source_dirs["candidate_json_dir"]
                )
                if not list(source_dirs["source_json_dir"].glob("*.json")) and not list(
                    source_dirs["candidate_json_dir"].glob("*.json")
                ):
                    errors.append("case source JSON directories contain no JSON files")
                declared_files = {
                    item.get("source_file")
                    for item in package.get("changes", [])
                    if isinstance(item, dict)
                    and isinstance(item.get("source_file"), str)
                }
                if changed_files != declared_files:
                    errors.append(
                        "actual changed source JSON files must exactly match changes[].source_file: "
                        f"actual={sorted(changed_files)} declared={sorted(declared_files)}"
                    )

    provenance = package.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        for field in (
            "inherited_ledger_dir",
            "predecessor_ledger_dir",
            "retained_evidence_dir",
        ):
            require_text(provenance, field, "provenance", errors)
        if stage in MATERIAL_STAGES:
            resolved: dict[str, Path] = {}
            for field in (
                "inherited_ledger_dir",
                "predecessor_ledger_dir",
                "retained_evidence_dir",
            ):
                value = provenance.get(field)
                if isinstance(value, str) and value.strip():
                    resolved[field] = resolve(base_dir, value).resolve()
                    if not resolved[field].is_dir():
                        errors.append(f"provenance.{field} does not exist: {value}")
            ledger_dir = resolved.get("inherited_ledger_dir")
            predecessor = resolved.get("predecessor_ledger_dir")
            retained = resolved.get("retained_evidence_dir")
            if ledger_dir and ledger_dir.is_dir():
                ledger_ids, ledger_rows = read_ledger(ledger_dir, errors)
            if (
                ledger_dir
                and predecessor
                and retained
                and ledger_dir.is_dir()
                and predecessor.is_dir()
                and retained.is_dir()
            ):
                validate_inheritance(predecessor, ledger_dir, retained, errors)

    backlog = package.get("backlog")
    if not isinstance(backlog, dict):
        errors.append("backlog must be an object")
    else:
        require_text(backlog, "path", "backlog", errors)
        require_text(backlog, "prioritization_basis", "backlog", errors)
        if stage in MATERIAL_STAGES:
            value = backlog.get("path")
            if (
                isinstance(value, str)
                and value.strip()
                and not resolve(base_dir, value).is_file()
            ):
                errors.append(f"backlog.path does not exist: {value}")

    packages = package.get("packages")
    package_ids: set[str] = set()
    package_finding_ids: set[str] = set()
    if not isinstance(packages, list) or not packages:
        errors.append("packages must be a non-empty list")
        packages = []
    for index, item in enumerate(packages):
        location = f"packages[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{location} must be an object")
            continue
        for field in (
            "package_id",
            "name",
            "current_weakness",
            "objective",
            "coherence_basis",
            "completion_test",
            "claim_scope",
        ):
            require_text(item, field, location, errors)
        package_id = item.get("package_id")
        if isinstance(package_id, str):
            if package_id in package_ids:
                errors.append(f"{location}.package_id duplicates {package_id}")
            package_ids.add(package_id)
        require_text_list(item, "affected_sectors", location, errors)
        temporal = item.get("temporal_boundary")
        if not isinstance(temporal, dict):
            errors.append(f"{location}.temporal_boundary must be an object")
        else:
            require_text(
                temporal,
                "evidence_period",
                f"{location}.temporal_boundary",
                errors,
            )
            latest_year = temporal.get("latest_evidence_year")
            if not isinstance(latest_year, int) or isinstance(latest_year, bool):
                errors.append(
                    f"{location}.temporal_boundary.latest_evidence_year must be an integer"
                )
            require_text(
                temporal,
                "post_evidence_treatment",
                f"{location}.temporal_boundary",
                errors,
            )
        evidence_boundary = item.get("evidence_boundary")
        if not isinstance(evidence_boundary, dict):
            errors.append(f"{location}.evidence_boundary must be an object")
        else:
            for field in (
                "geography",
                "quantity",
                "allocation_rule",
                "quality_status",
            ):
                require_text(
                    evidence_boundary,
                    field,
                    f"{location}.evidence_boundary",
                    errors,
                )
        invariants = item.get("invariants")
        if not isinstance(invariants, list) or not invariants:
            errors.append(f"{location}.invariants must be a non-empty list")
        else:
            invariant_names: set[str] = set()
            for invariant_index, invariant in enumerate(invariants):
                invariant_location = f"{location}.invariants[{invariant_index}]"
                if not isinstance(invariant, dict):
                    errors.append(f"{invariant_location} must be an object")
                    continue
                for field in ("name", "metric", "acceptance_rule"):
                    require_text(invariant, field, invariant_location, errors)
                name = invariant.get("name")
                if isinstance(name, str):
                    if name in invariant_names:
                        errors.append(f"{invariant_location}.name duplicates {name}")
                    invariant_names.add(name)
        package_finding_ids.update(
            require_text_list(
                item, "connectivity_finding_ids", location, errors, nonempty=False
            )
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
        evidence_ids = require_text_list(item, "evidence_ids", location, errors)
        model_map_ids = require_text_list(item, "model_map_ids", location, errors)
        if stage in MATERIAL_STAGES and ledger_ids:
            evidence = set().union(
                ledger_ids["SOURCES.csv"],
                ledger_ids["CALCULATIONS.csv"],
                ledger_ids["ASSUMPTIONS.csv"],
            )
            require_resolves(evidence_ids, evidence, f"{location}.evidence_ids", errors)
            require_resolves(
                model_map_ids,
                ledger_ids["MODEL_MAP.csv"],
                f"{location}.model_map_ids",
                errors,
            )
            if (
                isinstance(change_id, str)
                and change_id not in ledger_ids["CHANGES.csv"]
            ):
                errors.append(f"{location}.change_id does not resolve: {change_id}")
            for map_id in model_map_ids:
                row = ledger_rows["MODEL_MAP.csv"].get(map_id)
                if not row:
                    continue
                source_file = str(item.get("source_file", "")).replace("\\", "/")
                model_file = row.get("model_file", "").replace("\\", "/")
                if source_file and not (
                    model_file == source_file or model_file.endswith("/" + source_file)
                ):
                    errors.append(
                        f"{location}.model_map_ids {map_id} maps {model_file}, not {source_file}"
                    )
                if row.get("parameter") != item.get("parameter"):
                    errors.append(
                        f"{location}.model_map_ids {map_id} maps parameter "
                        f"{row.get('parameter')}, not {item.get('parameter')}"
                    )

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
        source_ids = require_text_list(item, "source_ids", location, errors)
        if stage in MATERIAL_STAGES and ledger_ids:
            require_resolves(
                source_ids, ledger_ids["SOURCES.csv"], f"{location}.source_ids", errors
            )

    connectivity = package.get("connectivity")
    dispositions_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(connectivity, dict):
        errors.append("connectivity must be an object")
    else:
        require_text(connectivity, "rules", "connectivity", errors)
        dispositions = connectivity.get("finding_dispositions")
        disposition_ids: set[str] = set()
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
            finding_id = item.get("finding_id")
            if isinstance(finding_id, str):
                if finding_id in disposition_ids:
                    errors.append(f"{location}.finding_id duplicates {finding_id}")
                disposition_ids.add(finding_id)
                dispositions_by_id[finding_id] = item
            if status not in FINDING_STATUSES:
                errors.append(
                    f"{location}.status must be one of {sorted(FINDING_STATUSES)}"
                )
            if stage in {"pre-solve", "promotion"} and status == "pending":
                errors.append(f"{location}.status cannot remain pending at {stage}")
            evidence = require_text_list(
                item, "evidence_ids", location, errors, nonempty=False
            )
            if (
                stage == "promotion"
                and status in {"resolved", "declared", "deferred"}
                and not evidence
            ):
                errors.append(f"{location}.evidence_ids are required at promotion")
            if stage in {"pre-solve", "promotion"} and ledger_ids:
                lineage = set().union(
                    ledger_ids["SOURCES.csv"],
                    ledger_ids["CALCULATIONS.csv"],
                    ledger_ids["ASSUMPTIONS.csv"],
                )
                require_resolves(evidence, lineage, f"{location}.evidence_ids", errors)

    runtime = package.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("runtime must be an object")
    else:
        for field in ("known_good_seconds", "candidate_budget_seconds"):
            value = runtime.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"runtime.{field} must be positive")
        require_text(runtime, "baseline_artifact", "runtime", errors)

    delivery = package.get("delivery")
    if not isinstance(delivery, dict):
        errors.append("delivery must be an object")
    else:
        state = delivery.get("state")
        if state not in DELIVERY_STATES:
            errors.append(f"delivery.state must be one of {sorted(DELIVERY_STATES)}")
        require_text(delivery, "history_artifact", "delivery", errors)
        result_status = delivery.get("result_status")
        if result_status not in RESULT_STATUSES:
            errors.append(
                f"delivery.result_status must be one of {sorted(RESULT_STATUSES)}"
            )
        require_text(delivery, "recertification_command", "delivery", errors)
        if stage == "source-input-patch":
            if state != "source_input_patch":
                errors.append(
                    "delivery.state must equal source_input_patch at source-input-patch"
                )
            if result_status not in {"absent", "stale"}:
                errors.append(
                    "delivery.result_status must be absent or stale at source-input-patch"
                )
        elif stage == "promotion":
            if state != "promoted":
                errors.append("delivery.state must equal promoted at promotion")
            if result_status != "fresh":
                errors.append("delivery.result_status must equal fresh at promotion")
        if stage in {"source-input-patch", "promotion"}:
            history = delivery.get("history_artifact")
            if (
                isinstance(history, str)
                and history.strip()
                and not resolve(base_dir, history).is_file()
            ):
                errors.append(f"delivery.history_artifact does not exist: {history}")

    gates = package.get("gates")
    gate_reports: dict[str, dict[str, Any]] = {}
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
    else:
        required_names = set(PROMOTION_GATES)
        missing = sorted(required_names - set(gates))
        if missing:
            errors.append(f"gates missing required entries: {missing}")
        required = set()
        if stage == "source-input-patch":
            required = set(SOURCE_INPUT_PATCH_GATES)
        elif stage == "pre-solve":
            required = set(PRE_SOLVE_GATES)
        elif stage == "promotion":
            required = set(PROMOTION_GATES)
        for name in PROMOTION_GATES:
            if name in gates:
                path = validate_gate(
                    gates[name],
                    f"gates.{name}",
                    name in required,
                    base_dir,
                    errors,
                    gate_name=name,
                )
                if name == "connectivity_review":
                    report = validate_report(
                        path,
                        f"gates.{name}",
                        errors,
                        schema="clews-connectivity-audit-v1",
                        allowed_statuses={"pass", "findings"},
                    )
                elif name == "baseline_comparison":
                    report = validate_report(
                        path,
                        f"gates.{name}",
                        errors,
                        schema="clews-run-comparison-v1",
                    )
                elif name == "stock_resource_account_checks":
                    report = validate_report(
                        path,
                        f"gates.{name}",
                        errors,
                        schema="clews-resource-account-validation-v1",
                    )
                else:
                    report = validate_report(path, f"gates.{name}", errors)
                if report is not None:
                    gate_reports[name] = report

    if stage in MATERIAL_STAGES:
        rules = connectivity.get("rules") if isinstance(connectivity, dict) else None
        if (
            stage in {"pre-solve", "promotion"}
            and isinstance(rules, str)
            and rules.strip()
            and not resolve(base_dir, rules).is_file()
        ):
            errors.append(f"connectivity.rules does not exist: {rules}")

        case_data = case if isinstance(case, dict) else {}
        connectivity_report = gate_reports.get("connectivity_review")
        if connectivity_report:
            reported_case_value = connectivity_report.get("case_dir")
            if not isinstance(reported_case_value, str) or not reported_case_value:
                errors.append(
                    "gates.connectivity_review artifact.case_dir must be non-empty"
                )
            else:
                reported_case = Path(reported_case_value)
                if not reported_case.is_absolute():
                    reported_case = resolve(base_dir, str(reported_case))
                if reported_case.resolve() != base_dir.resolve():
                    errors.append(
                        "gates.connectivity_review artifact case_dir does not match case root"
                    )
            if connectivity_report.get("scenario") != case_data.get("scenario"):
                errors.append(
                    "gates.connectivity_review artifact scenario does not match case"
                )
            if connectivity_report.get("rule_errors"):
                errors.append("gates.connectivity_review artifact contains rule_errors")
            if connectivity_report.get("unused_exemptions"):
                errors.append(
                    "gates.connectivity_review artifact contains unused_exemptions"
                )
            active_findings = connectivity_report.get("findings", [])
            exempted_findings = connectivity_report.get("reviewed_exemptions", [])
            if not isinstance(active_findings, list) or not isinstance(
                exempted_findings, list
            ):
                errors.append("gates.connectivity_review artifact findings are invalid")
            else:
                active_ids = {
                    item.get("finding_id")
                    for item in active_findings
                    if isinstance(item, dict)
                    and isinstance(item.get("finding_id"), str)
                }
                audit_ids = active_ids | {
                    item.get("finding_id")
                    for item in exempted_findings
                    if isinstance(item, dict)
                    and isinstance(item.get("finding_id"), str)
                }
                require_resolves(
                    sorted(package_finding_ids),
                    audit_ids,
                    "packages[].connectivity_finding_ids",
                    errors,
                )
                for finding_id in sorted(active_ids):
                    disposition = dispositions_by_id.get(finding_id)
                    if disposition is None:
                        errors.append(
                            f"connectivity finding has no disposition: {finding_id}"
                        )
                    elif disposition.get("status") == "pending":
                        errors.append(
                            f"connectivity finding disposition remains pending: {finding_id}"
                        )
                for finding_id in sorted(set(dispositions_by_id) - active_ids):
                    errors.append(
                        f"connectivity disposition does not resolve to an active finding: {finding_id}"
                    )

        provenance_report = gate_reports.get("schema_ledger_validation")
        if provenance_report and ledger_dir:
            reported = Path(str(provenance_report.get("ledger_dir", ""))).expanduser()
            if not reported.is_absolute():
                reported = resolve(base_dir, str(reported))
            if reported.resolve() != ledger_dir.resolve():
                errors.append(
                    "gates.schema_ledger_validation artifact ledger_dir does not match provenance.inherited_ledger_dir"
                )
            allowed_stages = (
                {"delivery"} if stage == "promotion" else {"build", "delivery"}
            )
            if provenance_report.get("stage") not in allowed_stages:
                errors.append(
                    f"gates.schema_ledger_validation artifact stage must be one of {sorted(allowed_stages)}"
                )
            coverage = provenance_report.get("model_inputs")
            if not isinstance(coverage, dict) or coverage.get("uncovered_inputs"):
                errors.append(
                    "gates.schema_ledger_validation artifact must prove complete model-input coverage"
                )

        comparison = gate_reports.get("baseline_comparison")
        if comparison:
            if comparison.get("common_file_count", 0) < 1:
                errors.append(
                    "gates.baseline_comparison artifact compares no common tables"
                )
            for field in ("baseline_only", "candidate_only"):
                if not isinstance(comparison.get(field), list):
                    errors.append(
                        f"gates.baseline_comparison artifact.{field} must be a list"
                    )

        special = {
            "connectivity_review",
            "schema_ledger_validation",
            "baseline_comparison",
            "stock_resource_account_checks",
        }
        for name, report in gate_reports.items():
            if name in special:
                continue
            if report.get("case") != case_data.get("candidate_case"):
                errors.append(
                    f"gates.{name} artifact case does not match candidate_case"
                )
            if report.get("scenario") != case_data.get("scenario"):
                errors.append(f"gates.{name} artifact scenario does not match case")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument(
        "--stage",
        choices=("design", "source-input-patch", "pre-solve", "promotion"),
        default="design",
    )
    parser.add_argument(
        "--case-dir",
        type=Path,
        help="case root; defaults to PACKAGE's parent, or its parent when PACKAGE is in documentation/",
    )
    args = parser.parse_args()
    try:
        package = json.loads(args.package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    package_dir = args.package.resolve().parent
    inferred_case_dir = (
        package_dir.parent if package_dir.name == "documentation" else package_dir
    )
    errors = validate_package(
        package, args.stage, package_dir, args.case_dir or inferred_case_dir
    )
    if errors:
        print("calibration package: FAIL", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"calibration package: PASS (stage={args.stage})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
