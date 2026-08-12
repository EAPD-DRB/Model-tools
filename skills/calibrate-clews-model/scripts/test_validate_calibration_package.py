"""Tests for the evidence-driven calibration-package validator."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_calibration_package.py")
SPEC = importlib.util.spec_from_file_location("validate_calibration_package", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)
TEMPLATE = Path(__file__).parents[1] / "assets" / "calibration-package.template.json"


class CalibrationPackageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.package = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def write_ledgers(self) -> None:
        contents = {
            "SOURCES.csv": (
                "source_id\n"
                "SRC_COUNTRY_PLANT_REGISTER\n"
                "SRC_COUNTRY_GENERATION\n"
                "SRC_CONNECTIVITY\n"
            ),
            "CALCULATIONS.csv": ("calculation_id\nCALC_EXISTING_STOCK_SURVIVAL\n"),
            "ASSUMPTIONS.csv": "assumption_id\nASM_CONNECTIVITY\n",
            "MODEL_MAP.csv": (
                "map_id,model_file,parameter,superseded_by\n"
                "MAP_EXISTING_STOCK,RYT.json,ResidualCapacity,\n"
            ),
            "GAPS.csv": "item\nGAP_EXAMPLE\n",
            "CHANGES.csv": "change_id\nCHG_EXISTING_STOCK\n",
        }
        for relative in ("data_sources", "predecessor/data_sources"):
            directory = self.root / relative
            (directory / "evidence").mkdir(parents=True)
            (directory / "evidence/source.txt").write_text(
                "retained evidence\n", encoding="utf-8"
            )
            for filename, content in contents.items():
                (directory / filename).write_text(content, encoding="utf-8")

    def ready(self, stage: str) -> dict[str, object]:
        package = copy.deepcopy(self.package)
        package["provenance"]["predecessor_ledger_dir"] = "predecessor/data_sources"
        package["case"]["source_json_dir"] = "source_json"
        package["case"]["candidate_json_dir"] = "candidate_json"
        (self.root / "source_json").mkdir()
        (self.root / "candidate_json").mkdir()
        (self.root / "source_json/RYT.json").write_text("{}\n", encoding="utf-8")
        (self.root / "candidate_json/RYT.json").write_text(
            '{"changed": true}\n', encoding="utf-8"
        )
        self.write_ledgers()
        documentation = self.root / "documentation"
        documentation.mkdir()
        (documentation / "calibration-backlog.csv").write_text(
            "item_id,status\nX,resolved\n", encoding="utf-8"
        )
        (documentation / "HISTORY.md").write_text(
            "# History\n\nSource inputs updated.\n", encoding="utf-8"
        )
        (documentation / "connectivity-rules.json").write_text("{}\n", encoding="utf-8")

        def pass_gate(name: str, report: dict[str, object]) -> None:
            artifact = documentation / f"{name}.json"
            artifact.write_text(json.dumps(report), encoding="utf-8")
            package["gates"][name] = {
                "status": "passed",
                "artifact": str(artifact.relative_to(self.root)),
            }

        names = VALIDATOR.PRE_SOLVE_GATES
        if stage == "source-input-patch":
            names = VALIDATOR.SOURCE_INPUT_PATCH_GATES
            package["delivery"]["state"] = "source_input_patch"
            package["delivery"]["result_status"] = "stale"
        elif stage == "promotion":
            names = VALIDATOR.PROMOTION_GATES
            package["delivery"]["state"] = "promoted"
            package["delivery"]["result_status"] = "fresh"
        generic = {
            "status": "pass",
            "case": package["case"]["candidate_case"],
            "scenario": package["case"]["scenario"],
        }
        for name in names:
            pass_gate(name, generic)
        package["gates"]["stock_resource_account_checks"] = {
            "status": "not_applicable",
            "artifact": None,
            "reason": "Synthetic package has no closed resource account",
        }
        if stage != "source-input-patch":
            pass_gate(
                "connectivity_review",
                {
                    "schema": "clews-connectivity-audit-v1",
                    "status": "pass",
                    "case_dir": str(self.root),
                    "scenario": package["case"]["scenario"],
                    "findings": [],
                    "reviewed_exemptions": [],
                    "rule_errors": [],
                    "unused_exemptions": [],
                },
            )
        pass_gate(
            "schema_ledger_validation",
            {
                "status": "pass",
                "stage": "delivery" if stage == "promotion" else "build",
                "ledger_dir": str(self.root / "data_sources"),
                "model_inputs": {"uncovered_inputs": []},
            },
        )
        if stage == "promotion":
            pass_gate(
                "baseline_comparison",
                {
                    "schema": "clews-run-comparison-v1",
                    "status": "pass",
                    "common_file_count": 1,
                    "baseline_only": [],
                    "candidate_only": [],
                },
            )
        return package

    def validate(self, package: dict[str, object], stage: str) -> list[str]:
        return VALIDATOR.validate_package(
            package, stage, self.root / "documentation", self.root
        )

    def test_template_passes_design(self) -> None:
        self.assertEqual(VALIDATOR.validate_package(self.package, "design"), [])

    def test_complete_package_passes_promotion(self) -> None:
        self.assertEqual(self.validate(self.ready("promotion"), "promotion"), [])

    def test_source_input_patch_passes_without_solver_gates(self) -> None:
        package = self.ready("source-input-patch")
        self.assertEqual(package["gates"]["solver_run"]["status"], "pending")
        self.assertEqual(self.validate(package, "source-input-patch"), [])

    def test_source_input_patch_requires_truthful_delivery_state(self) -> None:
        package = self.ready("source-input-patch")
        package["delivery"]["state"] = "working"
        package["delivery"]["result_status"] = "fresh"
        package["delivery"]["recertification_command"] = ""
        (self.root / "documentation/HISTORY.md").unlink()
        errors = self.validate(package, "source-input-patch")
        self.assertTrue(any("must equal source_input_patch" in e for e in errors))
        self.assertTrue(any("must be absent or stale" in e for e in errors))
        self.assertTrue(any("recertification_command" in e for e in errors))
        self.assertTrue(any("history_artifact does not exist" in e for e in errors))

    def test_pre_solve_checks_inherited_records(self) -> None:
        package = self.ready("pre-solve")
        (self.root / "data_sources/SOURCES.csv").write_text(
            "source_id\nSRC_COUNTRY_GENERATION\nSRC_CONNECTIVITY\n", encoding="utf-8"
        )
        errors = self.validate(package, "pre-solve")
        self.assertTrue(any("inheritance dropped SOURCES.csv" in e for e in errors))

    def test_fabricated_lineage_fails(self) -> None:
        package = self.ready("promotion")
        package["changes"][0]["evidence_ids"] = ["SRC_DOES_NOT_EXIST"]
        package["changes"][0]["model_map_ids"] = ["MAP_DOES_NOT_EXIST"]
        errors = self.validate(package, "promotion")
        self.assertTrue(any("SRC_DOES_NOT_EXIST" in e for e in errors))
        self.assertTrue(any("MAP_DOES_NOT_EXIST" in e for e in errors))

    def test_connectivity_finding_requires_disposition(self) -> None:
        package = self.ready("pre-solve")
        artifact = self.root / package["gates"]["connectivity_review"]["artifact"]
        report = json.loads(artifact.read_text(encoding="utf-8"))
        report["status"] = "findings"
        report["findings"] = [{"finding_id": "required_link_missing:RULE:USE:1"}]
        artifact.write_text(json.dumps(report), encoding="utf-8")
        package["packages"][0]["connectivity_finding_ids"] = [
            "required_link_missing:RULE:USE:1"
        ]
        errors = self.validate(package, "pre-solve")
        self.assertTrue(any("has no disposition" in e for e in errors))

    def test_promotion_requires_disposition_evidence(self) -> None:
        package = self.ready("promotion")
        finding_id = "required_link_missing:RULE:USE:1"
        artifact = self.root / package["gates"]["connectivity_review"]["artifact"]
        report = json.loads(artifact.read_text(encoding="utf-8"))
        report["status"] = "findings"
        report["findings"] = [{"finding_id": finding_id}]
        artifact.write_text(json.dumps(report), encoding="utf-8")
        package["packages"][0]["connectivity_finding_ids"] = [finding_id]
        package["connectivity"]["finding_dispositions"] = [
            {
                "finding_id": finding_id,
                "status": "resolved",
                "resolution": "fixed",
                "evidence_ids": [],
            }
        ]
        errors = self.validate(package, "promotion")
        self.assertTrue(any("evidence_ids are required" in e for e in errors))

    def test_placeholder_gate_artifact_fails(self) -> None:
        package = self.ready("pre-solve")
        artifact = self.root / package["gates"]["identifier_integrity"]["artifact"]
        artifact.write_text("placeholder\n", encoding="utf-8")
        errors = self.validate(package, "pre-solve")
        self.assertTrue(any("not readable JSON" in e for e in errors))

    def test_not_applicable_requires_reason_and_is_restricted(self) -> None:
        package = self.ready("pre-solve")
        package["gates"]["identifier_integrity"] = {
            "status": "not_applicable",
            "artifact": None,
        }
        errors = self.validate(package, "pre-solve")
        self.assertTrue(any("reason must be non-empty" in e for e in errors))
        self.assertTrue(any("mandatory and cannot" in e for e in errors))

    def test_source_diff_is_checked_against_real_files(self) -> None:
        package = self.ready("pre-solve")
        (self.root / "candidate_json/OTHER.json").write_text("{}\n", encoding="utf-8")
        errors = self.validate(package, "pre-solve")
        self.assertTrue(any("actual changed source JSON" in e for e in errors))

    def test_cli_infers_case_root_for_documentation_package(self) -> None:
        package = self.ready("pre-solve")
        package_path = self.root / "documentation/calibration-package.json"
        package_path.write_text(json.dumps(package), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                str(package_path),
                "--stage",
                "pre-solve",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
