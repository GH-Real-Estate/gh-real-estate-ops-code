"""Regression checks for the sanitized production CRM module inventory."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


CRM_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = (
    CRM_ROOT
    / "field-maps"
    / "production-module-inventory-2026-07-24.csv"
)
METADATA_AUDIT_PATH = (
    CRM_ROOT
    / "field-maps"
    / "production-module-metadata-audit-2026-07-24.csv"
)
EXPECTED_CANONICAL_SHA256 = (
    "f6d5bc2e8f24d57e84ac64d93dcb06069fe7e93996ccd4d2526e92b4f5acbf38"
)
EXPECTED_AUDIT_CANONICAL_SHA256 = (
    "23f7a6f5fc5f4857f235a60b73edae54ff9e9c6f48acd334d78ea954c3845f90"
)
EXPECTED_COLUMNS = [
    "inventory_order",
    "display_label",
    "singular_label",
    "api_name",
    "api_supported",
    "status",
    "show_as_tab",
    "viewable",
    "generated_type",
    "parent_module_api_name",
]


class ProductionModuleInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with INVENTORY_PATH.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            cls.columns = reader.fieldnames
            cls.rows = list(reader)

    def test_exact_snapshot_digest_and_shape(self) -> None:
        self.assertEqual(EXPECTED_COLUMNS, self.columns)
        payload = json.dumps(
            self.rows,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(EXPECTED_CANONICAL_SHA256, hashlib.sha256(payload).hexdigest())
        self.assertEqual(72, len(self.rows))
        self.assertEqual(
            list(range(1, 73)),
            [int(row["inventory_order"]) for row in self.rows],
        )

    def test_counts_match_production_module_metadata(self) -> None:
        self.assertEqual(
            Counter({"true": 51, "false": 21}),
            Counter(row["api_supported"] for row in self.rows),
        )
        self.assertEqual(
            Counter({"visible": 49, "user_hidden": 15, "system_hidden": 8}),
            Counter(row["status"] for row in self.rows),
        )
        self.assertEqual(
            Counter({"default": 53, "custom": 11, "subform": 5, "field_tracker": 3}),
            Counter(row["generated_type"] for row in self.rows),
        )

    def test_module_api_names_are_unique_and_protected_identities_are_exact(self) -> None:
        by_api = {row["api_name"]: row for row in self.rows}
        self.assertEqual(len(self.rows), len(by_api))
        self.assertEqual("Leads", by_api["Leads"]["display_label"])
        self.assertEqual("Property Assets", by_api["Equipment"]["display_label"])
        self.assertEqual("Pets", by_api["Pets"]["display_label"])
        self.assertEqual("Vehicles", by_api["Tenant_Vehicles"]["display_label"])
        for api_name in ("Leads", "Equipment", "Pets", "Tenant_Vehicles"):
            self.assertEqual("true", by_api[api_name]["api_supported"])

    def test_values_are_sanitized_metadata_only(self) -> None:
        allowed_booleans = {"true", "false"}
        allowed_statuses = {"visible", "user_hidden", "system_hidden"}
        for row in self.rows:
            self.assertTrue(row["display_label"])
            self.assertTrue(row["singular_label"])
            self.assertTrue(row["api_name"])
            self.assertIn(row["api_supported"], allowed_booleans)
            self.assertIn(row["show_as_tab"], allowed_booleans)
            self.assertIn(row["viewable"], allowed_booleans)
            self.assertIn(row["status"], allowed_statuses)
            self.assertNotIn("id", row)
            self.assertNotIn("modified_by", row)
            self.assertNotIn("profiles", row)


class ProductionModuleMetadataAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with INVENTORY_PATH.open(encoding="utf-8-sig", newline="") as handle:
            cls.inventory_rows = list(csv.DictReader(handle))
        with METADATA_AUDIT_PATH.open(
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            cls.audit_rows = list(csv.DictReader(handle))

    def test_exact_audit_digest_and_supported_module_coverage(self) -> None:
        payload = json.dumps(
            self.audit_rows,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            EXPECTED_AUDIT_CANONICAL_SHA256,
            hashlib.sha256(payload).hexdigest(),
        )
        self.assertEqual(51, len(self.audit_rows))
        supported_apis = {
            row["api_name"]
            for row in self.inventory_rows
            if row["api_supported"] == "true"
        }
        self.assertEqual(
            supported_apis,
            {row["api_name"] for row in self.audit_rows},
        )

    def test_metadata_outcome_counts_are_explicit(self) -> None:
        self.assertEqual(
            Counter({"success": 43, "rejected": 8}),
            Counter(row["fields_result"] for row in self.audit_rows),
        )
        self.assertEqual(
            Counter({"success": 30, "rejected": 17, "response_truncated": 4}),
            Counter(row["layouts_result"] for row in self.audit_rows),
        )
        allowed_details = {
            "",
            "NO_PERMISSION",
            "EMPTY_RESPONSE",
            "NOT_SUPPORTED",
            "RESPONSE_TRUNCATED",
        }
        for row in self.audit_rows:
            self.assertIn(row["fields_detail"], allowed_details)
            self.assertIn(row["layouts_detail"], allowed_details)
            if row["fields_result"] == "success":
                self.assertGreater(int(row["field_count"]), 0)
                self.assertEqual("", row["fields_detail"])
            else:
                self.assertEqual("", row["field_count"])
                self.assertTrue(row["fields_detail"])
            if row["layouts_result"] == "success":
                self.assertGreater(int(row["layout_count"]), 0)
                self.assertEqual("", row["layouts_detail"])
            else:
                self.assertEqual("", row["layout_count"])
                self.assertTrue(row["layouts_detail"])


if __name__ == "__main__":
    unittest.main()
