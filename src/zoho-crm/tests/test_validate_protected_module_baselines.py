"""Regression tests for checksum-controlled protected CRM metadata baselines."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


CRM_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    CRM_ROOT / "tools" / "validate-protected-module-baselines.py"
)
SPEC = importlib.util.spec_from_file_location(
    "protected_crm_baseline_validator",
    VALIDATOR_PATH,
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ProtectedCrmBaselineValidatorTests(unittest.TestCase):
    @staticmethod
    def load_documents():
        return validator.load_repository_documents(
            CRM_ROOT / "field-maps" / "protected-modules"
        )

    def test_repository_baselines_are_valid(self) -> None:
        policy, snapshots = self.load_documents()
        self.assertEqual([], validator.validate_documents(policy, snapshots))

    def test_exact_protected_scope_and_aliases_are_locked(self) -> None:
        expected = {
            "leads.json": ("Leads", "Leads", 82, 10),
            "property-assets.json": (
                "Property Assets",
                "Equipment",
                106,
                13,
            ),
            "pets.json": ("Pets", "Pets", 44, 7),
            "vehicles.json": ("Vehicles", "Tenant_Vehicles", 29, 5),
        }
        self.assertEqual(set(expected), set(validator.EXPECTED_BASELINES))
        for filename, (
            display_label,
            api_name,
            field_count,
            section_count,
        ) in expected.items():
            with self.subTest(filename=filename):
                facts = validator.EXPECTED_BASELINES[filename]
                self.assertEqual(display_label, facts["display_label"])
                self.assertEqual(api_name, facts["api_name"])
                self.assertEqual(field_count, facts["field_count"])
                self.assertEqual(section_count, facts["section_count"])

    def test_field_mutation_or_deletion_fails_closed(self) -> None:
        cases = (
            ("leads.json", "field_label", "Changed Lead Field"),
            ("property-assets.json", "api_name", "Changed_Property_Asset"),
            ("pets.json", "data_type", "changed_type"),
        )
        for filename, key, value in cases:
            with self.subTest(filename=filename, key=key):
                policy, snapshots = self.load_documents()
                mutated = copy.deepcopy(snapshots)
                mutated[filename]["fields"][0][key] = value
                errors = validator.validate_documents(policy, mutated)
                self.assertTrue(
                    any(
                        filename in error and "canonical metadata drifted" in error
                        for error in errors
                    ),
                    errors,
                )

        policy, snapshots = self.load_documents()
        deleted = copy.deepcopy(snapshots)
        deleted["vehicles.json"]["fields"].pop()
        errors = validator.validate_documents(policy, deleted)
        self.assertTrue(
            any(
                "vehicles.json" in error and "expected 29 field objects" in error
                for error in errors
            ),
            errors,
        )

    def test_layout_or_section_drift_fails_closed(self) -> None:
        policy, snapshots = self.load_documents()
        mutated = copy.deepcopy(snapshots)
        mutated["vehicles.json"]["layouts"][0]["sections"].pop()

        errors = validator.validate_documents(policy, mutated)

        self.assertTrue(
            any(
                "vehicles.json" in error
                and "expected 5 layout sections" in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                "vehicles.json" in error and "canonical metadata drifted" in error
                for error in errors
            ),
            errors,
        )

    def test_policy_mutation_fails_closed(self) -> None:
        policy, snapshots = self.load_documents()
        mutated = copy.deepcopy(policy)
        mutated["default_mutation_policy"] = "allow"

        errors = validator.validate_documents(mutated, snapshots)

        self.assertIn(
            "protected-module policy drifted from its reviewed checksum",
            errors,
        )
        self.assertIn(
            "protected-module policy must default to deny",
            errors,
        )

    def test_identifier_or_record_metadata_is_rejected(self) -> None:
        policy, snapshots = self.load_documents()
        mutated = copy.deepcopy(snapshots)
        mutated["pets.json"]["fields"][0]["id"] = "metadata-id-must-not-ship"

        errors = validator.validate_documents(policy, mutated)

        self.assertTrue(
            any(
                "pets.json" in error
                and "forbidden identifier, actor, record, or secret key" in error
                for error in errors
            ),
            errors,
        )

    def test_equipment_catalog_never_authorizes_property_asset_writes(self) -> None:
        policy, snapshots = self.load_documents()
        mutated = copy.deepcopy(policy)
        mutated["historical_catalog_guards"][0][
            "authorizes_live_writes"
        ] = True

        errors = validator.validate_documents(mutated, snapshots)

        self.assertTrue(
            any(
                "historical equipment catalog must not authorize" in error
                for error in errors
            ),
            errors,
        )

    def test_every_equipment_catalog_row_is_machine_non_deployable(self) -> None:
        rows = validator.load_catalog_rows("equipment.csv")
        self.assertEqual(13, len(rows))
        for row in rows:
            self.assertEqual(
                validator.EQUIPMENT_HISTORICAL_STATUS,
                row["module_api_name_status"],
            )
            self.assertEqual(
                validator.EQUIPMENT_HISTORICAL_STATUS,
                row["api_name_status"],
            )
            self.assertEqual("do_not_create", row["disposition"])
            self.assertEqual(
                validator.EQUIPMENT_HISTORICAL_PHASE,
                row["phase"],
            )
            self.assertEqual("", row["module_api_name"])
            self.assertEqual("", row["api_name"])

        cases = (
            ("api_name_status", "verified_live_mcp"),
            ("disposition", "governed_current"),
            ("phase", "Production Reconciled"),
            ("module_api_name", "Equipment"),
        )
        for column, value in cases:
            with self.subTest(column=column):
                mutated = copy.deepcopy(rows)
                mutated[0][column] = value
                errors: list[str] = []

                validator.validate_equipment_catalog_rows(mutated, errors)

                self.assertTrue(
                    any(
                        "equipment.csv:row 2 historical-only guard" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_absent_live_leads_proposals_are_protected_and_non_deployable(
        self,
    ) -> None:
        _, snapshots = self.load_documents()
        live_api_names = {
            field["api_name"]
            for field in snapshots["leads.json"]["fields"]
        }
        rows = validator.load_catalog_rows("leads.csv")
        absent_rows = [
            row
            for row in rows
            if row["proposed_api_name"]
            and row["proposed_api_name"] not in live_api_names
        ]
        self.assertEqual(26, len(absent_rows))
        self.assertEqual(
            17,
            sum(
                row["api_name_status"] == "blocked_protected_module"
                for row in absent_rows
            ),
        )
        for row in absent_rows:
            self.assertIn(
                row["api_name_status"],
                validator.LEADS_NONDEPLOYABLE_API_STATUSES,
            )
            self.assertEqual("do_not_create", row["disposition"])
            self.assertEqual(validator.LEADS_BLOCKED_PHASE, row["phase"])
            self.assertIn("Protected Leads no-write boundary", row["notes"])

        cases = (
            ("api_name_status", "proposed_unverified"),
            ("disposition", "candidate"),
            ("phase", "Required Now"),
        )
        for column, value in cases:
            with self.subTest(column=column):
                mutated = copy.deepcopy(rows)
                target = next(
                    row
                    for row in mutated
                    if row["api_name_status"] == "blocked_protected_module"
                )
                target[column] = value
                errors: list[str] = []

                validator.validate_leads_catalog_rows(
                    live_api_names,
                    mutated,
                    errors,
                )

                self.assertTrue(
                    any(
                        "protected absent-live proposal" in error
                        for error in errors
                    ),
                    errors,
                )

        runtime_api = next(row["api_name"] for row in rows if row["api_name"])
        reduced_live_api_names = live_api_names.difference({runtime_api})
        errors = []
        validator.validate_leads_catalog_rows(
            reduced_live_api_names,
            rows,
            errors,
        )
        self.assertTrue(
            any(
                "missing repository/runtime API names" in error
                and runtime_api in error
                for error in errors
            ),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
