"""Tests for the calibration-plan gate validator."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("validate_calibration_plan.py")
SPEC = importlib.util.spec_from_file_location(
    "validate_calibration_plan", SCRIPT_PATH
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)
TEMPLATE = (
    Path(__file__).parents[1]
    / "assets"
    / "calibration-plan.template.json"
)


class CalibrationPlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_template_passes_design_gate(self) -> None:
        self.assertEqual(VALIDATOR.validate_plan(self.plan, "design"), [])

    def test_pending_gates_block_full_solve(self) -> None:
        errors = VALIDATOR.validate_plan(self.plan, "pre-solve")
        self.assertTrue(
            any(
                "initial_year_equation_replay.status must be passed"
                in error
                for error in errors
            )
        )

    def test_complete_evidence_passes_promotion_gate(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["precision_inputs"][0]["sha256"] = "0" * 64
        for name, gate in plan["gates"].items():
            gate["status"] = "passed"
            gate["artifact"] = f"documentation/{name}.json"
        self.assertEqual(
            VALIDATOR.validate_plan(plan, "promotion"),
            [],
        )

    def test_forcing_and_rounded_initialization_are_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        benchmark = plan["intent"]["observations"][2]
        benchmark["affected_parameters"] = ["TAU"]
        benchmark["temporary_pin"] = True
        benchmark["release_year"] = "2025"
        plan["precision_inputs"][0]["precision"] = "rounded_csv"
        errors = VALIDATOR.validate_plan(plan, "design")
        joined = "\n".join(errors)
        self.assertIn("benchmark_only and cannot affect parameters", joined)
        self.assertIn(
            "activity-bound parameter without a real_world_constraint", joined
        )
        self.assertIn("temporary_pin must be false", joined)
        self.assertIn("defines a release_year", joined)
        self.assertIn(
            "initializes the model without a full-precision source", joined
        )


if __name__ == "__main__":
    unittest.main()
