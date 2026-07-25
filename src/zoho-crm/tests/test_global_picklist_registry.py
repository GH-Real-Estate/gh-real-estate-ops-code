"""Regression checks for the sanitized production global-picklist registry."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


CRM_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    CRM_ROOT
    / "field-maps"
    / "global-picklists"
    / "production-global-picklist-registry.json"
)


def walk(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class GlobalPicklistRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.picklists = {
            row["api_name"]: row for row in cls.registry["global_picklists"]
        }

    def test_production_gate_and_exact_inventory(self) -> None:
        self.assertEqual(
            {
                "company_name": "GH Real Estate",
                "environment_type": "production",
            },
            self.registry["snapshot"]["organization_gate"],
        )
        self.assertEqual(
            {
                "States",
                "Countries",
                "Building_Entry_Type",
                "Contact_Type",
                "Property_Type",
                "GH_Lifecycle_Status",
                "team_member_role__s",
                "access__s",
                "Country__s",
                "States__s",
            },
            set(self.picklists),
        )
        self.assertEqual(10, len(self.registry["global_picklists"]))

    def test_known_value_counts_and_order(self) -> None:
        expected_counts = {
            "States": 50,
            "Countries": 195,
            "Contact_Type": 7,
            "Property_Type": 6,
            "GH_Lifecycle_Status": 3,
        }
        for api_name, count in expected_counts.items():
            with self.subTest(api_name=api_name):
                values = self.picklists[api_name]["values"]
                self.assertEqual("recovered_from_associated_field_metadata", values["status"])
                self.assertEqual(count, values["count"])
                self.assertEqual(count, len(values["items"]))

        self.assertEqual(
            ["Alabama", "Alaska", "Arizona"],
            self.picklists["States"]["values"]["items"][:3],
        )
        self.assertEqual(
            ["West Virginia", "Wisconsin", "Wyoming"],
            self.picklists["States"]["values"]["items"][-3:],
        )
        self.assertEqual(
            ["Afghanistan", "Albania", "Algeria"],
            self.picklists["Countries"]["values"]["items"][:3],
        )
        self.assertEqual(
            ["Yemen", "Zambia", "Zimbabwe"],
            self.picklists["Countries"]["values"]["items"][-3:],
        )
        self.assertEqual(
            ["Active", "Inactive", "Archived"],
            self.picklists["GH_Lifecycle_Status"]["values"]["items"],
        )

    def test_lifecycle_set_associations_are_exact_and_uncolored(self) -> None:
        lifecycle = self.picklists["GH_Lifecycle_Status"]
        self.assertFalse(lifecycle["values_sorted_lexically"])
        self.assertEqual(
            {
                ("Accounts", "Property_Status"),
                ("Vendors", "Vendor_Status"),
            },
            {
                (row["module_api_name"], row["field_api_name"])
                for row in lifecycle["associations"]
            },
        )
        for association in lifecycle["associations"]:
            self.assertEqual("Standard", association["layout_display_label"])
            self.assertEqual("Standard__s", association["layout_api_name"])
            self.assertIsNone(association["field_default"])
            self.assertFalse(association["field_history_tracking_enabled"])
            self.assertFalse(association["field_color_coding_enabled"])
        self.assertEqual(
            {
                "type": "used",
                "color": None,
                "reference_value_equals_display_value": True,
                "actual_value_equals_display_value": True,
            },
            lifecycle["values"]["common_attributes"],
        )

    def test_compatibility_significant_value_state_is_preserved(self) -> None:
        contact_values = self.picklists["Contact_Type"]["values"]["items"]
        current_tenant = next(
            row for row in contact_values if row["display_value"] == "Current Tenant"
        )
        self.assertEqual("Current Tenant", current_tenant["reference_value"])
        self.assertEqual("Tenant", current_tenant["actual_value"])

        property_values = self.picklists["Property_Type"]["values"]["items"]
        apartment_building = next(
            row
            for row in property_values
            if row["display_value"] == "Apartment Building"
        )
        self.assertEqual("unused", apartment_building["type"])

    def test_unknowns_are_not_encoded_as_empty_values(self) -> None:
        for api_name in (
            "Building_Entry_Type",
            "team_member_role__s",
            "access__s",
            "Country__s",
            "States__s",
        ):
            with self.subTest(api_name=api_name):
                values = self.picklists[api_name]["values"]
                self.assertEqual("unknown", values["status"])
                self.assertIsNone(values["count"])
                self.assertIsNone(values["items"])
                self.assertTrue(values["reason"])

    def test_system_sets_remain_noncustomizable_and_outside_gh_governance(self) -> None:
        for api_name in (
            "team_member_role__s",
            "access__s",
            "Country__s",
            "States__s",
        ):
            with self.subTest(api_name=api_name):
                picklist = self.picklists[api_name]
                self.assertFalse(picklist["customizable"])
                self.assertEqual(
                    "zoho_system_managed",
                    picklist["governance_class"],
                )

    def test_registry_contains_no_live_metadata_ids_or_actor_keys(self) -> None:
        forbidden = {
            "id",
            "created_by",
            "modified_by",
            "primary_email",
            "phone",
            "street",
            "zip",
        }
        for key, _ in walk(self.registry):
            self.assertNotIn(key.casefold(), forbidden)
            self.assertFalse(key.casefold().endswith("_id"))


if __name__ == "__main__":
    unittest.main()
