#!/usr/bin/env python3
"""Tests for provenance.py. Standard library only.

    python3 -m unittest test_provenance.py -v

Every fixture is built in a temporary directory, so the tests never depend on
the shipped templates.
"""

from __future__ import annotations

import contextlib
import copy
import csv
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional

import provenance

# A minimal ledger that must pass at --stage build. Tests deep-copy this and
# mutate one thing at a time.
CLEAN: Dict[str, List[Dict[str, str]]] = {
    "SOURCES.csv": [
        {
            "source_id": "SRC_IEA_WEB_2023",
            "provider": "IEA",
            "product": "World Energy Balances",
            "edition": "2023 edition",
            "reference_period": "2022",
            "geography": "Kenya",
            "variable": "Natural gas input to electricity plants",
            "source_unit": "ktoe",
            "exact_locator": "Sheet Kenya, row Main activity producer, column Natural gas",
            "url": "https://www.iea.org/data-and-statistics",
            "access_date": "2026-03-11",
            "license": "IEA terms of use",
            "sha256": "",
        }
    ],
    "CALCULATIONS.csv": [
        {
            "calculation_id": "CALC_KTOE_TO_PJ",
            "formula": "pj = ktoe * 0.041868",
            "source_ids": "SRC_IEA_WEB_2023",
            "assumption_ids": "ASM_KTOE_TO_PJ",
            "input_calculation_ids": "",
            "input_values": "ktoe = 1250",
            "input_units": "ktoe",
            "output_value": "52.335",
            "output_unit": "PJ",
            "script_path": "",
            "script_version": "",
        },
        {
            "calculation_id": "CALC_IAR",
            "formula": "iar = fuel_pj / output_pj",
            "source_ids": "SRC_IEA_WEB_2023",
            "assumption_ids": "",
            "input_calculation_ids": "CALC_KTOE_TO_PJ",
            "input_values": "fuel_pj = 52.335; output_pj = 21.4",
            "input_units": "PJ; PJ",
            "output_value": "2.4456",
            "output_unit": "PJ/PJ",
            "script_path": "",
            "script_version": "",
        },
    ],
    "ASSUMPTIONS.csv": [
        {
            "assumption_id": "ASM_KTOE_TO_PJ",
            "statement": "1 ktoe = 0.041868 PJ (IEA convention)",
            "central_value": "0.041868",
            "unit": "PJ/ktoe",
            "evidence_source_ids": "SRC_IEA_WEB_2023",
            "lower_bound": "",
            "upper_bound": "",
        },
        {
            "assumption_id": "ASM_UTIL",
            "statement": "Plant ran at a 0.42 capacity factor in 2022",
            "central_value": "0.42",
            "unit": "fraction",
            "evidence_source_ids": "SRC_IEA_WEB_2023",
            "lower_bound": "0.35",
            "upper_bound": "0.50",
        },
    ],
    "MODEL_MAP.csv": [
        {
            "map_id": "MAP_0001",
            "model_file": "InputActivityRatio.csv",
            "parameter": "InputActivityRatio",
            "entity": "PWRNGCC001",
            "mode": "1",
            "scenario": "REF",
            "years": "2022-2050",
            "value_or_expression": "2.4456",
            "model_unit": "PJ/PJ",
            "evidence_ids": "CALC_IAR",
            "superseded_by": "",
        },
        {
            "map_id": "MAP_0002",
            "model_file": "CapacityFactor.csv",
            "parameter": "CapacityFactor",
            "entity": "PWRNGCC001",
            "mode": "1",
            "scenario": "REF",
            "years": "2022",
            "value_or_expression": "0.42",
            "model_unit": "fraction",
            "evidence_ids": "ASM_UTIL",
            "superseded_by": "",
        },
        {
            "map_id": "MAP_0009",
            "model_file": "TECHNOLOGY.csv",
            "parameter": "TechnologyDescription",
            "entity": "PWROCEAN001",
            "mode": "",
            "scenario": "",
            "years": "",
            "value_or_expression": "Placeholder ocean technology",
            "model_unit": "text",
            "evidence_ids": "SRC_IEA_WEB_2023",
            "superseded_by": "CHG_0002",
        },
    ],
    "GAPS.csv": [
        {
            "item": "Cooling water withdrawal for PWRNGCC001",
            "why_absent": "No plant-level withdrawal data is published",
            "upgrade_source": "Ministry of Water abstraction permit register",
        }
    ],
    "CHANGES.csv": [
        {
            "change_id": "CHG_0001",
            "date": "2026-03-19",
            "class": "B",
            "description": "Set the NGCC input activity ratio from the 2023 IEA balance",
            "model_objects": "PWRNGCC001",
            "evidence_path": "audit/validation_summary.json",
            "map_rows_affected": "MAP_0001",
            "resolve_status": "resolved",
            "author": "k.mwangi",
            "commit": "8c1d4a7",
        },
        {
            "change_id": "CHG_0002",
            "date": "2026-03-21",
            "class": "A",
            "description": "Remove unreferenced placeholder technology PWROCEAN001",
            "model_objects": "PWROCEAN001",
            "evidence_path": "audit/unreferenced_id_audit.json",
            "map_rows_affected": "MAP_0009",
            "resolve_status": "objective_unchanged",
            "author": "a.otieno",
            "commit": "d9a3c15",
        },
    ],
}


def write_ledger(
    directory: Path, tables: Optional[Dict[str, List[Dict[str, str]]]] = None
) -> Path:
    """Write the six CSVs, using each table's canonical column order."""
    tables = tables if tables is not None else copy.deepcopy(CLEAN)
    directory.mkdir(parents=True, exist_ok=True)
    for name in provenance.LEDGER_TABLES:
        rows = tables.get(name, [])
        columns = list(provenance.REQUIRED_COLUMNS[name])
        for row in rows:
            for key in row:
                if key not in columns:
                    columns.append(key)
        with (directory / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({column: row.get(column, "") for column in columns})
    return directory


class LedgerTestCase(unittest.TestCase):
    """Base class giving each test a scratch directory and helpers."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="provenance-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def build(
        self, tables: Optional[Dict[str, List[Dict[str, str]]]] = None, name: str = "ledger"
    ) -> Path:
        return write_ledger(self.tmp / name, tables)

    @staticmethod
    def tables() -> Dict[str, List[Dict[str, str]]]:
        return copy.deepcopy(CLEAN)

    def validate(self, ledger: Path, **kwargs) -> Dict[str, object]:
        return provenance.validate(ledger, **kwargs)

    def assertPasses(self, report: Dict[str, object]) -> None:
        self.assertEqual(
            report["status"], "pass", "unexpected failures: {0}".format(report["failures"])
        )

    def assertFailsWith(self, report: Dict[str, object], needle: str) -> None:
        self.assertEqual(report["status"], "fail", "expected a failure, got a pass")
        joined = " | ".join(str(item) for item in report["failures"])
        self.assertIn(needle, joined)


class CleanLedgerTests(LedgerTestCase):
    def test_clean_fixture_passes_build(self) -> None:
        report = self.validate(self.build())
        self.assertPasses(report)
        self.assertEqual(report["failure_count"], 0)

    def test_clean_fixture_passes_scaffold(self) -> None:
        self.assertPasses(self.validate(self.build(), stage="scaffold"))

    def test_evidence_types_are_derived_not_stored(self) -> None:
        report = self.validate(self.build())
        self.assertEqual(
            report["derived_evidence_types"],
            {"MAP_0001": "derived", "MAP_0002": "estimated", "MAP_0009": "direct"},
        )

    def test_scaffold_ignores_row_level_defects(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["exact_locator"] = ""
        tables["ASSUMPTIONS.csv"][0]["central_value"] = ""
        ledger = self.build(tables)
        self.assertPasses(self.validate(ledger, stage="scaffold"))
        self.assertFailsWith(self.validate(ledger), "exact_locator is blank")

    def test_missing_table_fails(self) -> None:
        ledger = self.build()
        (ledger / "GAPS.csv").unlink()
        self.assertFailsWith(self.validate(ledger), "missing ledger table: GAPS.csv")

    def test_missing_column_fails_and_unknown_column_only_warns(self) -> None:
        tables = self.tables()
        tables["GAPS.csv"][0]["reviewer"] = "a.otieno"
        ledger = self.build(tables)
        report = self.validate(ledger)
        self.assertPasses(report)
        self.assertIn(
            "unknown columns", " | ".join(str(item) for item in report["warnings"])
        )

        text = (ledger / "SOURCES.csv").read_text(encoding="utf-8")
        (ledger / "SOURCES.csv").write_text(
            text.replace("exact_locator,", "locator,", 1), encoding="utf-8"
        )
        self.assertFailsWith(
            self.validate(ledger), "missing required columns: exact_locator"
        )


class SourceTests(LedgerTestCase):
    def test_missing_exact_locator_fails(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["exact_locator"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)),
            "SRC_IEA_WEB_2023: exact_locator is blank",
        )

    def test_missing_access_date_fails(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["access_date"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)), "SRC_IEA_WEB_2023: access_date is blank"
        )

    def test_malformed_access_date_fails(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["access_date"] = "11/03/2026"
        self.assertFailsWith(self.validate(self.build(tables)), "is not an ISO date")

    def test_source_without_url_or_local_file_fails(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["url"] = ""
        self.assertFailsWith(self.validate(self.build(tables)), "the source is unreachable")


class DigestTests(LedgerTestCase):
    payload = b"station,capacity_mw\nKipevu III,750\n"

    def _ledger_with_evidence(self, digest: str) -> Path:
        tables = self.tables()
        tables["SOURCES.csv"][0]["local_file"] = "evidence/capacity.csv"
        tables["SOURCES.csv"][0]["sha256"] = digest
        ledger = self.build(tables)
        evidence = ledger / "evidence" / "capacity.csv"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_bytes(self.payload)
        return ledger

    def test_correct_digest_is_verified_against_the_real_file(self) -> None:
        report = self.validate(
            self._ledger_with_evidence(hashlib.sha256(self.payload).hexdigest())
        )
        self.assertPasses(report)
        self.assertEqual(report["verified_digests"], 1)

    def test_real_sha256_mismatch_fails(self) -> None:
        wrong = hashlib.sha256(b"different bytes entirely").hexdigest()
        report = self.validate(self._ledger_with_evidence(wrong))
        self.assertFailsWith(report, "sha256 mismatch for evidence/capacity.csv")
        self.assertEqual(report["verified_digests"], 0)

    def test_well_formed_digest_with_no_file_is_not_accepted(self) -> None:
        """64 hex zeros must never pass on format alone."""
        tables = self.tables()
        tables["SOURCES.csv"][0]["sha256"] = "0" * 64
        report = self.validate(self.build(tables))
        self.assertFailsWith(report, "names no local evidence file")
        self.assertEqual(report["verified_digests"], 0)

    def test_retained_file_without_digest_fails(self) -> None:
        report = self.validate(self._ledger_with_evidence(""))
        self.assertFailsWith(report, "records no sha256")

    def test_non_hex_digest_fails(self) -> None:
        report = self.validate(self._ledger_with_evidence("not-a-digest"))
        self.assertFailsWith(report, "64 hex characters")

    def test_uppercase_digest_is_accepted(self) -> None:
        digest = hashlib.sha256(self.payload).hexdigest().upper()
        report = self.validate(self._ledger_with_evidence(digest))
        self.assertPasses(report)
        self.assertEqual(report["verified_digests"], 1)

    def test_missing_retained_file_fails(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["local_file"] = "evidence/absent.csv"
        tables["SOURCES.csv"][0]["sha256"] = hashlib.sha256(self.payload).hexdigest()
        self.assertFailsWith(
            self.validate(self.build(tables)), "retained evidence file is missing"
        )

    def test_evidence_path_escaping_the_ledger_fails(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["local_file"] = "../outside.csv"
        tables["SOURCES.csv"][0]["sha256"] = hashlib.sha256(self.payload).hexdigest()
        self.assertFailsWith(
            self.validate(self.build(tables)), "must be a ledger-relative path"
        )


class AssumptionTests(LedgerTestCase):
    def test_blank_central_value_fails(self) -> None:
        tables = self.tables()
        tables["ASSUMPTIONS.csv"][0]["central_value"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)), "ASM_KTOE_TO_PJ: central_value is blank"
        )

    def test_blank_unit_fails(self) -> None:
        tables = self.tables()
        tables["ASSUMPTIONS.csv"][1]["unit"] = ""
        self.assertFailsWith(self.validate(self.build(tables)), "ASM_UTIL: unit is blank")

    def test_bounds_must_bracket_the_central_value(self) -> None:
        tables = self.tables()
        tables["ASSUMPTIONS.csv"][1]["lower_bound"] = "0.60"
        self.assertFailsWith(
            self.validate(self.build(tables)), "bounds do not bracket central_value"
        )


class ReferenceTests(LedgerTestCase):
    def test_dangling_evidence_id_fails(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["evidence_ids"] = "CALC_IAR CALC_DOES_NOT_EXIST"
        self.assertFailsWith(
            self.validate(self.build(tables)),
            "evidence_ids references CALC_DOES_NOT_EXIST",
        )

    def test_blank_evidence_ids_fails(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["evidence_ids"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)), "MAP_0001: evidence_ids is blank"
        )

    def test_dangling_assumption_reference_in_calculation_fails(self) -> None:
        tables = self.tables()
        tables["CALCULATIONS.csv"][0]["assumption_ids"] = "ASM_GHOST"
        self.assertFailsWith(
            self.validate(self.build(tables)), "assumption_ids references ASM_GHOST"
        )

    def test_dangling_evidence_source_in_assumption_fails(self) -> None:
        tables = self.tables()
        tables["ASSUMPTIONS.csv"][0]["evidence_source_ids"] = "SRC_GHOST"
        self.assertFailsWith(
            self.validate(self.build(tables)), "evidence_source_ids references SRC_GHOST"
        )

    def test_dangling_map_row_in_changes_fails(self) -> None:
        tables = self.tables()
        tables["CHANGES.csv"][0]["map_rows_affected"] = "MAP_9999"
        self.assertFailsWith(
            self.validate(self.build(tables)), "map_rows_affected references MAP_9999"
        )

    def test_semicolon_and_space_separators_both_resolve(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["evidence_ids"] = "CALC_IAR;ASM_UTIL"
        self.assertPasses(self.validate(self.build(tables)))
        tables["MODEL_MAP.csv"][0]["evidence_ids"] = "CALC_IAR ASM_UTIL"
        self.assertPasses(self.validate(self.build(tables, name="spaced")))


class IdentifierTests(LedgerTestCase):
    def test_duplicate_id_fails(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"].append(copy.deepcopy(tables["SOURCES.csv"][0]))
        self.assertFailsWith(
            self.validate(self.build(tables)), "duplicate source_id SRC_IEA_WEB_2023"
        )

    def test_duplicate_map_id_fails(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][1]["map_id"] = "MAP_0001"
        self.assertFailsWith(self.validate(self.build(tables)), "duplicate map_id MAP_0001")

    def test_blank_id_fails(self) -> None:
        tables = self.tables()
        tables["ASSUMPTIONS.csv"][1]["assumption_id"] = ""
        self.assertFailsWith(self.validate(self.build(tables)), "assumption_id is blank")

    def test_wrong_prefix_fails(self) -> None:
        tables = self.tables()
        tables["CALCULATIONS.csv"][0]["calculation_id"] = "C-001"
        tables["CALCULATIONS.csv"][1]["input_calculation_ids"] = "C-001"
        self.assertFailsWith(self.validate(self.build(tables)), "must match CALC_<token>")


class CycleTests(LedgerTestCase):
    def test_calculation_cycle_fails(self) -> None:
        tables = self.tables()
        tables["CALCULATIONS.csv"][0]["input_calculation_ids"] = "CALC_IAR"
        report = self.validate(self.build(tables))
        self.assertFailsWith(report, "dependency cycle")
        self.assertEqual(
            1,
            sum(1 for item in report["failures"] if "dependency cycle" in str(item)),
            "a cycle must be reported exactly once",
        )

    def test_self_referencing_calculation_fails(self) -> None:
        tables = self.tables()
        tables["CALCULATIONS.csv"][0]["input_calculation_ids"] = "CALC_KTOE_TO_PJ"
        self.assertFailsWith(
            self.validate(self.build(tables)), "lists itself in input_calculation_ids"
        )

    def test_three_step_cycle_fails(self) -> None:
        tables = self.tables()
        tables["CALCULATIONS.csv"].append(
            {
                "calculation_id": "CALC_THIRD",
                "formula": "x = y",
                "source_ids": "",
                "assumption_ids": "",
                "input_calculation_ids": "CALC_KTOE_TO_PJ",
                "input_values": "y = 1",
                "input_units": "PJ",
                "output_value": "1",
                "output_unit": "PJ",
                "script_path": "",
                "script_version": "",
            }
        )
        tables["CALCULATIONS.csv"][0]["input_calculation_ids"] = "CALC_IAR"
        tables["CALCULATIONS.csv"][1]["input_calculation_ids"] = "CALC_THIRD"
        self.assertFailsWith(self.validate(self.build(tables)), "dependency cycle")

    def test_long_chain_without_a_cycle_passes(self) -> None:
        tables = self.tables()
        previous = "CALC_IAR"
        for index in range(30):
            current = "CALC_CHAIN_{0:02d}".format(index)
            tables["CALCULATIONS.csv"].append(
                {
                    "calculation_id": current,
                    "formula": "x = previous",
                    "source_ids": "",
                    "assumption_ids": "",
                    "input_calculation_ids": previous,
                    "input_values": "previous = 1",
                    "input_units": "PJ",
                    "output_value": "1",
                    "output_unit": "PJ",
                    "script_path": "",
                    "script_version": "",
                }
            )
            previous = current
        tables["MODEL_MAP.csv"][0]["evidence_ids"] = previous
        self.assertPasses(self.validate(self.build(tables)))


class CalculationTests(LedgerTestCase):
    def test_calculation_with_no_lineage_fails(self) -> None:
        tables = self.tables()
        tables["CALCULATIONS.csv"][1]["source_ids"] = ""
        tables["CALCULATIONS.csv"][1]["input_calculation_ids"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)), "needs at least one source_id"
        )

    def test_script_path_without_version_fails(self) -> None:
        tables = self.tables()
        tables["CALCULATIONS.csv"][0]["script_path"] = "scripts/convert.py"
        self.assertFailsWith(
            self.validate(self.build(tables)), "script_version is required"
        )


class ChangeTests(LedgerTestCase):
    def test_class_a_without_evidence_path_fails(self) -> None:
        tables = self.tables()
        tables["CHANGES.csv"][1]["evidence_path"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)),
            "class=A must name the audit artifact",
        )

    def test_class_a_pointing_at_an_active_map_row_fails(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][2]["superseded_by"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)),
            "class=A references MODEL_MAP row MAP_0009, which is still active",
        )

    def test_class_b_may_reference_an_active_map_row(self) -> None:
        self.assertPasses(self.validate(self.build()))

    def test_invalid_class_fails(self) -> None:
        tables = self.tables()
        tables["CHANGES.csv"][0]["class"] = "D"
        self.assertFailsWith(self.validate(self.build(tables)), "class must be one of A, B, C")

    def test_lowercase_class_a_is_still_enforced(self) -> None:
        tables = self.tables()
        tables["CHANGES.csv"][1]["class"] = "a"
        tables["CHANGES.csv"][1]["evidence_path"] = ""
        self.assertFailsWith(
            self.validate(self.build(tables)), "class=A must name the audit artifact"
        )

    def test_bad_commit_fails(self) -> None:
        tables = self.tables()
        tables["CHANGES.csv"][0]["commit"] = "HEAD~1"
        self.assertFailsWith(self.validate(self.build(tables)), "is not a 7-40 character hex")

    def test_superseded_by_must_resolve_to_a_change(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][2]["superseded_by"] = "CHG_9999"
        self.assertFailsWith(
            self.validate(self.build(tables)), "superseded_by references CHG_9999"
        )


class EvidenceTypeTests(LedgerTestCase):
    def test_declared_evidence_type_must_match_the_lineage(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["evidence_type"] = "direct"
        self.assertFailsWith(
            self.validate(self.build(tables)),
            "evidence_type says direct but evidence_ids make it derived",
        )

    def test_declared_evidence_type_matching_the_lineage_passes(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["evidence_type"] = "derived"
        tables["MODEL_MAP.csv"][1]["evidence_type"] = "estimated"
        tables["MODEL_MAP.csv"][2]["evidence_type"] = "direct"
        self.assertPasses(self.validate(self.build(tables)))


class CoverageTests(LedgerTestCase):
    def _inputs(self, *names: str) -> Path:
        inputs = self.tmp / "model_inputs"
        inputs.mkdir(parents=True, exist_ok=True)
        for name in names:
            (inputs / name).write_text(
                "REGION,TECHNOLOGY,YEAR,VALUE\nKE,PWRNGCC001,2022,2.4456\n",
                encoding="utf-8",
            )
        return inputs

    def test_covered_inputs_pass(self) -> None:
        inputs = self._inputs("InputActivityRatio.csv", "CapacityFactor.csv")
        report = self.validate(self.build(), stage="delivery", model_inputs=inputs)
        self.assertPasses(report)
        self.assertEqual(report["model_inputs"]["covered_input_count"], 2)

    def test_uncovered_input_fails(self) -> None:
        inputs = self._inputs(
            "InputActivityRatio.csv", "CapacityFactor.csv", "SpecifiedAnnualDemand.csv"
        )
        self.assertFailsWith(
            self.validate(self.build(), stage="delivery", model_inputs=inputs),
            "populated model inputs have no MODEL_MAP row: SpecifiedAnnualDemand.csv",
        )

    def test_empty_input_file_needs_no_map_row(self) -> None:
        inputs = self._inputs("InputActivityRatio.csv", "CapacityFactor.csv")
        (inputs / "AnnualEmissionLimit.csv").write_text(
            "REGION,EMISSION,YEAR,VALUE\n", encoding="utf-8"
        )
        self.assertPasses(
            self.validate(self.build(), stage="delivery", model_inputs=inputs)
        )

    def test_catch_all_model_file_is_rejected(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["model_file"] = "*"
        inputs = self._inputs("InputActivityRatio.csv", "CapacityFactor.csv")
        report = self.validate(self.build(tables), stage="delivery", model_inputs=inputs)
        self.assertFailsWith(report, "model_file must name one file, not a pattern")
        self.assertFailsWith(report, "InputActivityRatio.csv")

    def test_glob_model_file_is_rejected(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["model_file"] = "model/inputs/*.csv"
        self.assertFailsWith(
            self.validate(self.build(tables)), "model_file must name one file"
        )

    def test_superseded_row_does_not_provide_coverage(self) -> None:
        inputs = self._inputs(
            "InputActivityRatio.csv", "CapacityFactor.csv", "TECHNOLOGY.csv"
        )
        self.assertFailsWith(
            self.validate(self.build(), stage="delivery", model_inputs=inputs),
            "populated model inputs have no MODEL_MAP row: TECHNOLOGY.csv",
        )

    def test_delivery_requires_model_inputs(self) -> None:
        self.assertFailsWith(
            self.validate(self.build(), stage="delivery"),
            "--model-inputs is required at --stage delivery",
        )

    def test_build_stage_skips_coverage_when_not_asked(self) -> None:
        report = self.validate(self.build(), stage="build")
        self.assertPasses(report)
        self.assertNotIn("model_inputs", report)

    def test_path_prefixed_model_file_still_matches(self) -> None:
        tables = self.tables()
        tables["MODEL_MAP.csv"][0]["model_file"] = "model/inputs/InputActivityRatio.csv"
        inputs = self._inputs("InputActivityRatio.csv", "CapacityFactor.csv")
        self.assertPasses(
            self.validate(self.build(tables), stage="delivery", model_inputs=inputs)
        )

    def test_non_csv_model_mapping_is_not_an_unmatched_input_warning(self) -> None:
        tables = self.tables()
        config_row = dict(tables["MODEL_MAP.csv"][0])
        config_row.update(
            {
                "map_id": "MAP_CONFIG",
                "model_file": "config/config.yaml",
                "parameter": "country",
                "value_or_expression": "Kenya",
                "model_unit": "text",
            }
        )
        tables["MODEL_MAP.csv"].append(config_row)
        inputs = self._inputs("InputActivityRatio.csv", "CapacityFactor.csv")
        report = self.validate(
            self.build(tables), stage="delivery", model_inputs=inputs
        )
        self.assertPasses(report)
        self.assertFalse(
            any("config/config.yaml" in warning for warning in report["warnings"])
        )


class CommandLineTests(LedgerTestCase):
    @staticmethod
    def run_cli(argv: List[str]) -> int:
        """Invoke main() with its report suppressed."""
        with io.StringIO() as sink, contextlib.redirect_stdout(sink):
            return provenance.main(argv)

    def test_exit_zero_and_json_report_on_pass(self) -> None:
        ledger = self.build()
        destination = self.tmp / "reports" / "provenance.json"
        code = self.run_cli([str(ledger), "--stage", "build", "--json", str(destination)])
        self.assertEqual(code, 0)
        report = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "pass")

    def test_exit_one_on_fail(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["exact_locator"] = ""
        self.assertEqual(self.run_cli([str(self.build(tables))]), 1)

    def test_json_report_is_written_on_failure_too(self) -> None:
        tables = self.tables()
        tables["SOURCES.csv"][0]["access_date"] = ""
        destination = self.tmp / "provenance.json"
        self.assertEqual(
            self.run_cli([str(self.build(tables)), "--json", str(destination)]), 1
        )
        report = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "fail")

    def test_missing_ledger_directory_fails(self) -> None:
        self.assertEqual(self.run_cli([str(self.tmp / "nowhere")]), 1)


if __name__ == "__main__":
    unittest.main()
