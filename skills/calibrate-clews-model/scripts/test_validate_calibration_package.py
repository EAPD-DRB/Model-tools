"""Tests for the evidence-driven calibration-package validator."""

from __future__ import annotations

import copy
import importlib.util
import json
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

    def ready(self, stage: str) -> dict[str, object]:
        package = copy.deepcopy(self.package)
        for directory in ("data_sources", "data_sources/evidence"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        backlog = self.root / package["backlog"]["path"]
        backlog.parent.mkdir(parents=True, exist_ok=True)
        backlog.write_text("item_id,status\nX,resolved\n", encoding="utf-8")

        def pass_gate(gate: dict[str, object], name: str) -> None:
            artifact = self.root / "documentation" / f"{name}.json"
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("{}\n", encoding="utf-8")
            gate["status"] = "passed"
            gate["artifact"] = str(artifact.relative_to(self.root))

        pass_gate(package["provenance"]["ledger_validation"], "ledger_validation")
        pass_gate(package["provenance"]["populated_input_coverage"], "input_coverage")
        pass_gate(package["connectivity"]["audit"], "connectivity_audit")
        names = VALIDATOR.PRE_SOLVE_GATES
        if stage == "promotion":
            names = VALIDATOR.PROMOTION_GATES
            disposition = package["connectivity"]["finding_dispositions"][0]
            disposition["status"] = "resolved"
            disposition["evidence_ids"] = ["CALC_CONNECTIVITY_FIX"]
        for name in names:
            pass_gate(package["gates"][name], name)
        return package

    def test_template_passes_design(self) -> None:
        self.assertEqual(VALIDATOR.validate_package(self.package, "design"), [])

    def test_pre_solve_requires_complete_inherited_provenance(self) -> None:
        package = self.ready("pre-solve")
        package["provenance"]["complete_inherited_copy"] = False
        errors = VALIDATOR.validate_package(package, "pre-solve", self.root)
        self.assertTrue(
            any("complete_inherited_copy must be true" in e for e in errors)
        )

    def test_benchmark_cannot_drive_parameters(self) -> None:
        package = copy.deepcopy(self.package)
        package["benchmarks"][0]["affected_parameters"] = ["CapacityFactor"]
        errors = VALIDATOR.validate_package(package, "design")
        self.assertTrue(any("cannot affect parameters" in e for e in errors))

    def test_pre_solve_requires_artifacts(self) -> None:
        errors = VALIDATOR.validate_package(self.package, "pre-solve", self.root)
        self.assertTrue(any("status must be passed" in e for e in errors))

    def test_promotion_requires_disposition_evidence(self) -> None:
        package = self.ready("promotion")
        package["connectivity"]["finding_dispositions"][0]["evidence_ids"] = []
        errors = VALIDATOR.validate_package(package, "promotion", self.root)
        self.assertTrue(any("evidence_ids are required" in e for e in errors))

    def test_complete_package_passes_promotion(self) -> None:
        package = self.ready("promotion")
        self.assertEqual(
            VALIDATOR.validate_package(package, "promotion", self.root), []
        )


if __name__ == "__main__":
    unittest.main()
