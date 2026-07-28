"""Regression tests for the CLEWs structural audit."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


AUDIT_PATH = Path(__file__).with_name("audit.py")
SPEC = importlib.util.spec_from_file_location("clews_model_audit", AUDIT_PATH)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUDIT)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_model(root: Path, extra_id: str | None = None) -> Path:
    model = root / "UnderscoreIds"
    write_json(
        model / "genData.json",
        {
            "osy-casename": "UnderscoreIds",
            "osy-version": 1,
            "osy-desc": "Regression fixture",
            "osy-date": "2026-07-28",
            "osy-years": ["2020"],
            "osy-ts": [],
            "osy-techGroups": [{"TG": "ENERGY"}, {"TG": "ENVIRONMENT"}],
            "osy-tech": [
                {
                    "TechId": "TEC_envland_v12",
                    "Tech": "ENV_LAND",
                    "Desc": "Land account",
                    "IAR": [],
                    "OAR": ["COM_env_lcrp_v12"],
                }
            ],
            "osy-comm": [
                {
                    "CommId": "COM_env_lcrp_v12",
                    "Comm": "ENV_LAND_CROP",
                    "Desc": "Cropland account",
                    "UnitId": "km2",
                }
            ],
            "osy-emis": [
                {
                    "EmisId": "EMI_pm_2_5",
                    "Emis": "PM2_5",
                    "Desc": "Fine particulate matter",
                }
            ],
            "osy-scenarios": [
                {
                    "ScenarioId": "SC_base_case",
                    "Scenario": "BASE",
                    "Desc": "Base",
                }
            ],
        },
    )
    identifiers = {
        "SC_base_case": {
            "TechId": "TEC_envland_v12",
            "CommId": "COM_env_lcrp_v12",
            "EmisId": "EMI_pm_2_5",
        }
    }
    if extra_id:
        identifiers["SC_base_case"]["OtherTechId"] = extra_id
    write_json(model / "RT.json", {"TEST": identifiers})
    write_json(
        model / "view" / "resData.json",
        {"osy-cases": [{"Case": "BASE_V14"}]},
    )
    results = model / "res" / "BASE_V14" / "results.txt"
    results.parent.mkdir(parents=True)
    results.write_text("Optimal - objective value 1\n", encoding="utf-8")
    return model


class AuditRegressionTest(unittest.TestCase):
    def test_complete_underscore_ids_and_run_label_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = AUDIT.audit_model(
                str(make_model(Path(tmp)))
            )
        messages = [message for _, message in report.findings]
        self.assertFalse(
            any("missing from genData" in message for message in messages)
        )
        self.assertFalse(
            any("defined but never referenced" in message for message in messages)
        )
        self.assertFalse(
            any("scenario labels" in message for message in messages)
        )

    def test_unknown_underscore_id_is_reported_in_full(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = AUDIT.audit_model(
                str(make_model(Path(tmp), "TEC_missing_part"))
            )
        failures = [
            message
            for level, message in report.findings
            if level == "FAIL"
        ]
        self.assertTrue(
            any("TEC_missing_part" in message for message in failures)
        )


if __name__ == "__main__":
    unittest.main()
