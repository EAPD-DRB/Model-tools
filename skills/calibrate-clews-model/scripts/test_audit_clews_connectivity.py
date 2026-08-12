"""Synthetic regression tests for the MUIO connectivity audit."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("audit_clews_connectivity.py")
SPEC = importlib.util.spec_from_file_location("audit_clews_connectivity", SCRIPT)
AUDITOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUDITOR)


class ConnectivityAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        gen = {
            "osy-years": ["2020"],
            "osy-scenarios": [{"ScenarioId": "SC_0", "Active": True}],
            "osy-tech": [
                {"TechId": "SUPPLY", "Tech": "Free supply"},
                {"TechId": "USE", "Tech": "Useful process"},
            ],
            "osy-comm": [
                {"CommId": "RESOURCE", "Comm": "Resource"},
                {"CommId": "SERVICE", "Comm": "Service"},
                {"CommId": "ORPHAN", "Comm": "Orphan"},
            ],
        }
        rytcm = {
            "IAR": {
                "SC_0": [{"TechId": "USE", "CommId": "RESOURCE", "MoId": 1, "2020": 1}]
            },
            "OAR": {
                "SC_0": [
                    {"TechId": "SUPPLY", "CommId": "RESOURCE", "MoId": 1, "2020": 1},
                    {"TechId": "USE", "CommId": "SERVICE", "MoId": 1, "2020": 1},
                ]
            },
        }
        ryt = {
            "TAU": {
                "SC_0": [
                    {"TechId": "SUPPLY", "2020": 999999},
                    {"TechId": "USE", "2020": 999999},
                ]
            },
            "CC": {"SC_0": []},
            "FC": {"SC_0": []},
            "TAMaxC": {"SC_0": []},
            "TAMaxCI": {"SC_0": []},
        }
        rytm = {
            "VC": {
                "SC_0": [
                    {"TechId": "SUPPLY", "MoId": 1, "2020": 0},
                    {"TechId": "USE", "MoId": 1, "2020": 1},
                ]
            },
            "TAMUL": {"SC_0": []},
        }
        for name, payload in (
            ("genData.json", gen),
            ("RYTCM.json", rytcm),
            ("RYT.json", ryt),
            ("RYTM.json", rytm),
        ):
            (self.root / name).write_text(json.dumps(payload), encoding="utf-8")
        self.rules = {
            "schema_version": 1,
            "scenario": "SC_0",
            "unbounded_threshold": 99990,
            "technology_roles": {},
            "terminal_commodity_ids": ["SERVICE"],
            "exogenous_commodity_ids": [],
            "required_links": [
                {
                    "rule_id": "USE_NEEDS_RESOURCE_AND_LAND",
                    "technology_ids": ["USE"],
                    "required_input_commodity_ids": ["RESOURCE", "LAND"],
                    "require_all": True,
                    "reason": "Test physical link",
                }
            ],
            "reviewed_exemptions": [],
        }

    def test_detects_unlimited_free_and_missing_link(self) -> None:
        report = AUDITOR.audit(self.root, self.rules)
        kinds = {item["finding_type"] for item in report["findings"]}
        self.assertIn("unlimited_free_output_candidate", kinds)
        self.assertIn("required_link_missing", kinds)
        self.assertIn("unused_commodity", kinds)

    def test_reviewed_exemption_is_separated(self) -> None:
        self.rules["technology_roles"] = {
            "SUPPLY": {"role": "resource_supply", "basis": "boundary"}
        }
        self.rules["reviewed_exemptions"] = [
            {
                "finding_type": "unlimited_free_output_candidate",
                "entity_id": "SUPPLY:1",
                "reason": "Synthetic test exemption",
                "evidence_ids": ["ASM_TEST"],
            }
        ]
        report = AUDITOR.audit(self.root, self.rules)
        self.assertEqual(len(report["reviewed_exemptions"]), 1)
        self.assertNotIn(
            "SUPPLY:1",
            [
                item["entity_id"]
                for item in report["findings"]
                if item["finding_type"] == "unlimited_free_output_candidate"
            ],
        )


if __name__ == "__main__":
    unittest.main()
