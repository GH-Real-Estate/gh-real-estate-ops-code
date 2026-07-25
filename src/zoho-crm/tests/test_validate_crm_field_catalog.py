"""Focused regression tests for the governed CRM field-catalog validator."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


CRM_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = CRM_ROOT / "tools" / "validate-crm-field-catalog.py"
SPEC = importlib.util.spec_from_file_location("crm_field_catalog_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class CrmFieldCatalogValidatorTests(unittest.TestCase):
    @staticmethod
    def load_repository_rows() -> list[tuple[Path, dict[str, str]]]:
        catalog_dir = CRM_ROOT / "field-maps" / "crm-module-fields"
        return [
            (path, row.copy())
            for path, row in validator.load_catalog_dir(catalog_dir)
        ]

    def test_repository_catalog_is_valid(self) -> None:
        rows = self.load_repository_rows()
        self.assertEqual([], validator.validate_rows(rows))

    def test_live_manifest_has_expected_production_scope(self) -> None:
        self.assertEqual(15, len(validator.DEALS_CREATED_LIVE_MANIFEST))
        self.assertEqual(33, len(validator.LEASE_CREATED_LIVE_MANIFEST))
        self.assertEqual(7, len(validator.LEASE_REUSED_LIVE_MANIFEST))
        self.assertEqual(40, len(validator.LEASE_PLACED_LIVE_MANIFEST))
        self.assertEqual(83, validator.JULY_24_RECONCILIATION_CREATED_COUNT)
        self.assertEqual(
            4,
            validator.JULY_24_STANDARD_PICKLIST_RECONCILED_COUNT,
        )
        self.assertEqual(8, validator.JULY_24_REUSED_LIVE_COUNT)
        self.assertEqual(
            {
                "Contacts": 9,
                "Properties": 8,
                "Units": 15,
                "Rental Applications": 6,
                "Maintenance Requests": 13,
                "Inspections": 18,
                "Leases": 1,
                "Vendors": 1,
                "Tasks": 2,
                "Storage Units": 3,
                "Utilities": 2,
                "Condition Reports": 5,
            },
            {
                "Contacts": len(validator.CONTACTS_RECONCILED_LIVE_MANIFEST),
                "Properties": len(
                    validator.PROPERTIES_RECONCILED_LIVE_MANIFEST
                ),
                "Units": len(validator.UNITS_RECONCILED_LIVE_MANIFEST),
                "Rental Applications": len(
                    validator.DEALS_RECONCILED_LIVE_MANIFEST
                ),
                "Maintenance Requests": len(
                    validator.CASES_RECONCILED_LIVE_MANIFEST
                ),
                "Inspections": len(
                    validator.INSPECTIONS_RECONCILED_LIVE_MANIFEST
                ),
                "Leases": len(validator.LEASE_ADDITIONAL_LIVE_MANIFEST),
                "Vendors": len(validator.VENDORS_RECONCILED_LIVE_MANIFEST),
                "Tasks": len(validator.TASKS_RECONCILED_LIVE_MANIFEST),
                "Storage Units": len(
                    validator.STORAGE_UNITS_RECONCILED_LIVE_MANIFEST
                ),
                "Utilities": len(
                    validator.UTILITIES_RECONCILED_LIVE_MANIFEST
                ),
                "Condition Reports": len(
                    validator.CONDITION_REPORTS_RECONCILED_LIVE_MANIFEST
                ),
            },
        )
        rows = self.load_repository_rows()
        count, digest = validator.governed_live_snapshot_digest(rows)
        self.assertEqual(170, count)
        self.assertEqual(validator.GOVERNED_LIVE_SNAPSHOT_COUNT, count)
        self.assertEqual(validator.GOVERNED_LIVE_SNAPSHOT_SHA256, digest)

    def test_live_manifest_rejects_plausible_api_name_mutations(self) -> None:
        cases = (
            (
                "Rental Applications",
                "Approved Security Deposit",
                "Approved_Security_Deposit_v2",
            ),
            ("Leases", "Lease Type", "Lease_Type_v2"),
            ("Leases", "Lease Status", "Lease_Status_v2"),
            ("Contacts", "Current Unit", "Current_Unit_v2"),
            ("Condition Reports", "Inspection", "Inspection_v2"),
            ("Maintenance Requests", "Case Origin", "Case_Origin_v2"),
        )
        for module_label, field_label, mutated_api_name in cases:
            with self.subTest(module=module_label, field=field_label):
                rows = self.load_repository_rows()
                matching_rows = [
                    row
                    for _, row in rows
                    if row["module_display_label"] == module_label
                    and row["field_label"] == field_label
                ]
                self.assertEqual(1, len(matching_rows))
                matching_rows[0]["api_name"] = mutated_api_name

                errors = validator.validate_rows(rows)

                self.assertTrue(
                    any(
                        f"{module_label}.{field_label}.api_name" in error
                        and mutated_api_name in error
                        for error in errors
                    ),
                    errors,
                )

    def test_live_manifest_rejects_row_deletions(self) -> None:
        cases = (
            ("Rental Applications", "Decision"),
            ("Leases", "Agreement Date"),
            ("Leases", "Lease Name"),
            ("Tasks", "Priority"),
        )
        for module_label, field_label in cases:
            with self.subTest(module=module_label, field=field_label):
                rows = self.load_repository_rows()
                filtered_rows = [
                    (path, row)
                    for path, row in rows
                    if not (
                        row["module_display_label"] == module_label
                        and row["field_label"] == field_label
                    )
                ]
                self.assertEqual(len(rows) - 1, len(filtered_rows))

                errors = validator.validate_rows(filtered_rows)

                self.assertIn(
                    f"2026-07-24 live manifest: {module_label}.{field_label}: "
                    "required catalog row is missing",
                    errors,
                )

    def test_live_manifest_rejects_metadata_and_placement_drift(self) -> None:
        cases = (
            (
                "Rental Applications",
                "Approved Security Deposit",
                "field_type",
                "Double",
                "field_type",
            ),
            (
                "Rental Applications",
                "Decision",
                "picklist_values_and_colors",
                "Pending=#D97706 | Approved=#16A34A",
                "exact live choices/order/colors drifted",
            ),
            (
                "Leases",
                "Lease Type",
                "section",
                "Legacy Details",
                ".section",
            ),
            (
                "Leases",
                "Property",
                "notes",
                "Created and read back as a lookup.",
                "lookup target 'Accounts'",
            ),
            (
                "Storage Units",
                "Property",
                "notes",
                "Created and read back as a lookup.",
                "lookup target 'Accounts'",
            ),
            (
                "Properties",
                "Property Status",
                "picklist_scope",
                "module_local_live_uncolored",
                ".picklist_scope",
            ),
            (
                "Inspections",
                "Status",
                "picklist_values_and_colors",
                "Not Started=UNCOLORED | Completed=UNCOLORED",
                "exact live choices/order/colors drifted",
            ),
            (
                "Maintenance Requests",
                "Priority",
                "notes",
                "All colors are null.",
                "platform-sentinel readback order",
            ),
            (
                "Tasks",
                "Priority",
                "picklist_scope",
                "standard_module_picklist",
                ".picklist_scope",
            ),
        )
        for module_label, field_label, column, value, expected_error in cases:
            with self.subTest(
                module=module_label,
                field=field_label,
                column=column,
            ):
                rows = self.load_repository_rows()
                matching_rows = [
                    row
                    for _, row in rows
                    if row["module_display_label"] == module_label
                    and row["field_label"] == field_label
                ]
                self.assertEqual(1, len(matching_rows))
                matching_rows[0][column] = value

                errors = validator.validate_rows(rows)

                self.assertTrue(
                    any(expected_error in error for error in errors),
                    errors,
                )

    def test_complete_live_snapshot_rejects_any_authoritative_fact_drift(self) -> None:
        cases = (
            (
                "Rental Applications",
                "Approved_Security_Deposit",
                "required",
                "true",
            ),
            (
                "Rental Applications",
                "Approved_Security_Deposit",
                "help_text",
                "Changed tooltip text.",
            ),
            ("Contacts", "Full_Name", "api_name", "Full_Name_v2"),
            (
                "Rental Applications",
                "Stage",
                "picklist_values_and_colors",
                "New Application=UNCOLORED",
            ),
            ("Leases", "Monthly_Rent", "api_name", "Monthly_Rent_v2"),
            (
                "Leases",
                "First_Full_Month_Base_Rent_Amount",
                "help_text",
                "Changed tooltip text.",
            ),
        )
        for module_label, api_name, column, value in cases:
            with self.subTest(
                module=module_label,
                api_name=api_name,
                column=column,
            ):
                rows = self.load_repository_rows()
                matching_rows = [
                    row
                    for _, row in rows
                    if row["module_display_label"] == module_label
                    and row["api_name"] == api_name
                ]
                self.assertEqual(1, len(matching_rows))
                matching_rows[0][column] = value

                errors = validator.validate_rows(rows)

                self.assertTrue(
                    any(
                        "governed live snapshot: canonical CSV facts drifted"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_live_status_requires_live_evidence_source(self) -> None:
        row = {column: "" for column in validator.REQUIRED_COLUMNS}
        row.update(
            {
                "module_display_label": "Leases",
                "module_type": "custom",
                "module_api_name": "Leases",
                "module_api_name_status": "verified_live_mcp",
                "field_label": "Lease Type",
                "field_type": "Single Line",
                "api_name": "Lease_Type",
                "api_name_status": "verified_live_mcp",
                "proposed_api_name": "Lease_Type",
                "disposition": "governed_current",
                "required": "false",
                "help_text": "Verified test field.",
                "source_ids": "MATRIX_2026-07-08",
            }
        )

        errors = validator.validate_rows([(Path("leases.csv"), row)])

        self.assertTrue(
            any(
                "verified_live_mcp requires LIVE_CRM_MCP_2026-07-24" in error
                for error in errors
            )
        )

    def test_uncolored_choices_require_narrow_live_metadata_mode(self) -> None:
        self.assertEqual(
            {
                "global_live_uncolored",
                "module_local_live_uncolored",
                "standard_module_live_uncolored",
            },
            validator.LIVE_UNCOLORED_PICKLIST_SCOPES,
        )
        allowed_errors: list[str] = []
        validator.parse_choices(
            "Kansas=UNCOLORED",
            "state",
            allowed_errors,
            allow_uncolored=True,
        )
        self.assertEqual([], allowed_errors)

        rejected_errors: list[str] = []
        validator.parse_choices(
            "Kansas=UNCOLORED",
            "state",
            rejected_errors,
            allow_uncolored=False,
        )
        self.assertTrue(any("invalid color" in error for error in rejected_errors))

    def test_uncreated_cosigner_target_uses_failure_color(self) -> None:
        rows = self.load_repository_rows()
        matches = [
            row
            for _, row in rows
            if row["module_display_label"] == "Rental Applications"
            and row["proposed_api_name"] == "Cosigner_Required"
        ]
        self.assertEqual(1, len(matches))
        self.assertEqual("proposed_unverified", matches[0]["api_name_status"])
        self.assertIn(
            "Not Approved=#DC2626",
            matches[0]["picklist_values_and_colors"],
        )

    def test_exact_tooltip_and_standard_picklist_sentinel_evidence(self) -> None:
        rows = self.load_repository_rows()
        by_key = {
            (row["module_display_label"], row["api_name"]): row
            for _, row in rows
            if row["api_name_status"] == "verified_live_mcp"
        }

        first_month = by_key[
            ("Leases", "First_Full_Month_Base_Rent_Amount")
        ]
        self.assertEqual(
            "First full-month base-rent input for the due-before-possession "
            "calculation. Reconcile to approved lease terms and Zoho Books "
            "before contract readiness.",
            first_month["help_text"],
        )

        cases_priority = by_key[("Maintenance Requests", "Priority")]
        self.assertNotIn("-None-=", cases_priority["picklist_values_and_colors"])
        self.assertIn(
            "-None-, High, Medium, Low, Emergency, Normal.",
            cases_priority["notes"],
        )
        tasks_priority = by_key[("Tasks", "Priority")]
        self.assertNotIn("Global: GH Priority", tasks_priority["notes"])

        unit_id = by_key[("Units", "Unit_I_D")]
        self.assertEqual("Unit I.D.", unit_id["field_label"])
        self.assertEqual("Auto-Number", unit_id["field_type"])
        self.assertIn("prefix `GH-UNIT-`", unit_id["notes"])
        self.assertIn("start number 1", unit_id["notes"])

        unit_status = by_key[("Units", "Unit_Status")]
        self.assertNotIn("-None-=", unit_status["picklist_values_and_colors"])
        self.assertIn(
            "-None-, Occupied, Vacant - Ready, Vacant - Needs Turnover, "
            "Under Renovation, Reserved, Inactive.",
            unit_status["notes"],
        )

        inspection_name = by_key[("Inspections", "Name")]
        self.assertEqual("Inspection Name", inspection_name["field_label"])
        self.assertEqual("Single Line / Module Name", inspection_name["field_type"])
        self.assertEqual("true", inspection_name["required"])

    def test_duplicate_prone_decisions_cannot_return_to_build_queue(self) -> None:
        rows = self.load_repository_rows()
        matching_rows = [
            row
            for _, row in rows
            if row["module_display_label"] == "Contacts"
            and row["field_label"] == "Secondary Phone"
        ]
        self.assertEqual(1, len(matching_rows))
        matching_rows[0]["api_name_status"] = "proposed_unverified"
        matching_rows[0]["disposition"] = "candidate"

        errors = validator.validate_rows(rows)

        self.assertTrue(
            any(
                "no-duplicate decision: Contacts.Secondary Phone"
                in error
                for error in errors
            ),
            errors,
        )

    def test_policy_warnings_are_governed_live_facts(self) -> None:
        rows = self.load_repository_rows()
        matching_rows = [
            row
            for _, row in rows
            if row["module_display_label"] == "Contacts"
            and row["field_label"] == "Email Operational Consent?"
        ]
        self.assertEqual(1, len(matching_rows))
        matching_rows[0]["notes"] = (
            "Created and read back in production CRM; live required is false."
        )

        errors = validator.validate_rows(rows)

        self.assertTrue(
            any(
                "expected policy warning" in error
                and "Email Operational Consent?" in error
                for error in errors
            ),
            errors,
        )

    def test_global_picklist_scope_matches_production_registry(self) -> None:
        rows = self.load_repository_rows()
        by_key = {
            (row["module_display_label"], row["field_label"]): row
            for _, row in rows
        }
        self.assertEqual(
            {
                ("Properties", "State"): "States",
                ("Properties", "Property Status"): "GH_Lifecycle_Status",
                ("Vendors", "Vendor Status"): "GH_Lifecycle_Status",
            },
            validator.GLOBAL_LIVE_PICKLIST_ASSOCIATIONS,
        )
        state = by_key[("Properties", "State")]
        self.assertEqual("global_live_uncolored", state["picklist_scope"])
        self.assertIn("`States`", state["notes"])

        state["picklist_scope"] = "module_local_live_uncolored"
        errors = validator.validate_rows(rows)
        self.assertTrue(
            any(
                "global live picklist association: Properties.State"
                in error
                for error in errors
            ),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
