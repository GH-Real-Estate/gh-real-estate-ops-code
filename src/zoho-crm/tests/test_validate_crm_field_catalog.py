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
        rows = self.load_repository_rows()
        count, digest = validator.governed_live_snapshot_digest(rows)
        self.assertEqual(75, count)
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


if __name__ == "__main__":
    unittest.main()
