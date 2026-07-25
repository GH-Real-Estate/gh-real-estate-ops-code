#!/usr/bin/env python3
"""Regression tests for the Zoho Contracts field registry."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "src/zoho-contracts/scripts/validate_contract_field_registry.py"
SPEC = importlib.util.spec_from_file_location("contract_field_registry_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ContractFieldRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = validator.load_registry()

    def test_checked_in_registry_is_valid(self) -> None:
        self.assertEqual([], validator.validate_registry(self.registry))

    def test_generated_markdown_matches_registry(self) -> None:
        expected = validator.render_markdown(self.registry)
        actual = validator.MARKDOWN_PATH.read_text(encoding="utf-8")
        self.assertEqual(expected, actual)

    def test_user_confirmed_live_label_evidence_is_exact_and_label_only(self) -> None:
        self.assertEqual(1, len(self.registry["label_evidence"]))
        evidence = self.registry["label_evidence"][0]
        self.assertEqual("user_confirmed_live_label", evidence["evidence_type"])
        self.assertEqual("2026-07-24", evidence["confirmed_on"])
        self.assertEqual("label_only", evidence["scope"])
        self.assertEqual("unverified", evidence["api_name_status"])
        self.assertEqual(37, len(evidence["labels"]))
        self.assertEqual(validator.USER_CONFIRMED_LIVE_LABELS, evidence["labels"])
        self.assertIn("Agreement Effective Date", evidence["labels"])
        self.assertNotIn("Agreement Date", evidence["labels"])

    def test_rejects_drift_in_user_confirmed_label_evidence(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["label_evidence"][0]["labels"][0] = "Agreement Name"
        problems = validator.validate_registry(registry)
        self.assertTrue(
            any("must exactly match the governed 37-label inventory" in problem for problem in problems)
        )

    def test_requested_destinations_have_exact_types_and_governed_crm_decisions(self) -> None:
        by_label = {field["label"]: field for field in self.registry["fields"]}
        self.assertEqual(15, len(validator.REQUESTED_DESTINATION_TYPES))
        for label, expected_type in validator.REQUESTED_DESTINATION_TYPES.items():
            field = by_label[label]
            self.assertEqual("custom", field["classification"])
            self.assertEqual(expected_type, field["zoho"]["ui_type"])
            self.assertIsNone(field["zoho"]["api_name"])
            self.assertEqual("design_decision", field["zoho"]["type_status"])
            if label in validator.VERIFIED_CRM_API_CROSSWALK:
                self.assertEqual(
                    validator.VERIFIED_CRM_API_CROSSWALK[label],
                    field["crm"]["proposed_api_name"],
                )
                self.assertEqual(
                    "verified_live_mcp", field["crm"]["api_name_status"]
                )
            else:
                self.assertIn(label, validator.CRM_FIELDS_WITH_UNDEFINED_SEMANTICS)
                self.assertIsNone(field["crm"]["proposed_api_name"])
                self.assertEqual(
                    "do_not_create_until_defined",
                    field["crm"]["api_name_status"],
                )

    def test_verified_crm_crosswalk_is_exact(self) -> None:
        by_label = {field["label"]: field for field in self.registry["fields"]}
        self.assertEqual(23, len(validator.VERIFIED_CRM_API_CROSSWALK))
        self.assertNotIn("Lease Number", validator.VERIFIED_CRM_API_CROSSWALK)
        for label, expected_api_name in validator.VERIFIED_CRM_API_CROSSWALK.items():
            crm = by_label[label]["crm"]
            self.assertEqual(expected_api_name, crm["proposed_api_name"], label)
            self.assertEqual("verified_live_mcp", crm["api_name_status"], label)

        registry = copy.deepcopy(self.registry)
        agreement_name = next(
            field for field in registry["fields"] if field["label"] == "Agreement Name"
        )
        agreement_name["crm"]["proposed_api_name"] = "Agreement_Name"
        problems = validator.validate_registry(registry)
        self.assertTrue(
            any(
                "Agreement Name must use verified_live_mcp CRM API name Name" in problem
                for problem in problems
            )
        )

    def test_tenant_api_verified_is_reserved_for_contracts_metadata(self) -> None:
        registry = copy.deepcopy(self.registry)
        field = next(
            item for item in registry["fields"] if item["label"] == "Agreement Name"
        )
        field["crm"]["api_name_status"] = "tenant_api_verified"

        problems = validator.validate_registry(registry)

        self.assertNotIn("tenant_api_verified", validator.ALLOWED_CRM_API_STATUSES)
        self.assertIn("tenant_api_verified", validator.ALLOWED_TYPE_STATUSES)
        self.assertTrue(
            any(
                ".crm.api_name_status: value is not in enum" in problem
                for problem in problems
            )
        )

    def test_ambiguous_rent_fields_remain_unmapped(self) -> None:
        by_label = {field["label"]: field for field in self.registry["fields"]}
        self.assertEqual(
            {
                "Base Rent Amount",
                "Total Monthly Rent Amount",
                "Prorated Base Rent Amount",
            },
            validator.CRM_FIELDS_WITH_UNDEFINED_SEMANTICS,
        )
        for label in validator.CRM_FIELDS_WITH_UNDEFINED_SEMANTICS:
            crm = by_label[label]["crm"]
            self.assertIsNone(crm["proposed_api_name"], label)
            self.assertEqual(
                "do_not_create_until_defined", crm["api_name_status"], label
            )

    def test_lease_number_stays_out_of_verified_crosswalk(self) -> None:
        registry = copy.deepcopy(self.registry)
        lease_number = next(
            field for field in registry["fields"] if field["label"] == "Lease Number"
        )
        self.assertIsNone(lease_number["crm"]["proposed_api_name"])
        self.assertEqual(
            "do_not_create_until_defined",
            lease_number["crm"]["api_name_status"],
        )

        lease_number["crm"]["proposed_api_name"] = "Lease_Number"
        lease_number["crm"]["api_name_status"] = "verified_live_mcp"
        problems = validator.validate_registry(registry)
        self.assertIn(
            "Lease Number must remain unmapped until an approved auto-number "
            "prefix and format are defined",
            problems,
        )

    def test_checked_in_contracts_api_names_remain_null_and_unverified(self) -> None:
        for field in self.registry["fields"]:
            self.assertIsNone(field["zoho"]["api_name"], field["label"])
            self.assertNotEqual(
                "tenant_api_verified", field["zoho"]["type_status"], field["label"]
            )

    def test_native_party_fields_prohibit_crm_mirror_proposals(self) -> None:
        party_fields = [
            field
            for field in self.registry["fields"]
            if field["classification"] == "system"
            and (
                field["label"] in {"Party A", "Party B"}
                or field["label"].startswith(("Party A ", "Party B "))
            )
        ]
        self.assertTrue(party_fields)
        for field in party_fields:
            self.assertIsNone(field["crm"]["proposed_api_name"], field["label"])
            self.assertEqual(
                "do_not_create", field["crm"]["api_name_status"], field["label"]
            )

        registry = copy.deepcopy(self.registry)
        party_a = next(field for field in registry["fields"] if field["id"] == "party_a")
        party_a["crm"]["proposed_api_name"] = "Party_A_Account"
        party_a["crm"]["api_name_status"] = "proposed_unverified"
        problems = validator.validate_registry(registry)
        self.assertTrue(
            any("must not have a CRM mirror proposal" in problem for problem in problems)
        )

    def test_party_b_jurisdiction_remains_unresolved(self) -> None:
        field = next(
            item for item in self.registry["fields"] if item["id"] == "party_b_jurisdiction"
        )
        self.assertEqual("review_required", field["status"])
        self.assertEqual("do_not_create", field["crm"]["api_name_status"])
        self.assertIn("Do not map Property State", field["validation"])

    def test_rejects_unknown_custom_type(self) -> None:
        registry = copy.deepcopy(self.registry)
        custom = next(
            field for field in registry["fields"] if field["classification"] == "custom"
        )
        custom["zoho"]["ui_type"] = "Formula"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("ui_type" in problem for problem in problems))

    def test_rejects_duplicate_id(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][1]["id"] = registry["fields"][0]["id"]
        problems = validator.validate_registry(registry)
        self.assertTrue(any("duplicate field id" in problem for problem in problems))

    def test_system_field_cannot_use_custom_menu_type(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["zoho"]["ui_type"] = "Text"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("ui_type" in problem for problem in problems))

    def test_postal_code_must_remain_text(self) -> None:
        registry = copy.deepcopy(self.registry)
        postal = next(
            field for field in registry["fields"] if field["id"] == "property_postal_code_snapshot"
        )
        postal["zoho"]["ui_type"] = "Number"
        postal["portable_type"] = "integer"
        postal["crm"]["recommended_type"] = "Number"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("postal/ZIP identifiers" in problem for problem in problems))

    def test_dropdown_requires_allowed_values(self) -> None:
        registry = copy.deepcopy(self.registry)
        state = next(
            field for field in registry["fields"] if field["id"] == "property_state_code_snapshot"
        )
        state.pop("allowed_values")
        problems = validator.validate_registry(registry)
        self.assertTrue(any("Dropdown fields require allowed_values" in problem for problem in problems))

    def test_unverified_api_name_cannot_be_committed_as_actual(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["zoho"]["api_name"] = "agreementName"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("before tenant API verification" in problem for problem in problems))

    def test_rejects_schema_invalid_portable_type(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["portable_type"] = "blob"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("portable_type" in problem for problem in problems))

    def test_rejects_schema_invalid_sensitivity(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["sensitivity"] = "public"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("sensitivity" in problem for problem in problems))

    def test_rejects_schema_invalid_crm_type(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["crm"]["recommended_type"] = "Formula"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("recommended_type" in problem for problem in problems))

    def test_rejects_unknown_properties(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["unexpected"] = True
        registry["fields"][0]["zoho"]["unexpected"] = True
        problems = validator.validate_registry(registry)
        self.assertTrue(any("unknown property" in problem for problem in problems))

    def test_missing_required_field_returns_errors_without_crashing(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0].pop("label")
        problems = validator.validate_registry(registry)
        self.assertTrue(any("missing required property label" in problem for problem in problems))

    def test_checked_in_schema_rejects_empty_policies(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["policies"] = {}
        problems = validator.validate_registry(registry)
        self.assertTrue(any("minProperties" in problem for problem in problems))

    def test_checked_in_schema_rejects_non_string_schema_reference(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["$schema"] = True
        problems = validator.validate_registry(registry)
        self.assertTrue(any("$.$schema: expected type string" in problem for problem in problems))

    def test_checked_in_schema_rejects_duplicate_aliases(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["aliases"] = ["Agreement Title", "Agreement Title"]
        problems = validator.validate_registry(registry)
        self.assertTrue(any("array items must be unique" in problem for problem in problems))

    def test_checked_in_schema_rejects_non_boolean_allow_decimals(self) -> None:
        registry = copy.deepcopy(self.registry)
        count = next(
            item for item in registry["fields"] if item["id"] == "storage_keys_provided_count"
        )
        count["zoho"]["allow_decimals"] = "false"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("allow_decimals: expected type boolean" in problem for problem in problems))

    def test_checked_in_schema_rejects_boolean_crm_api_name(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"][0]["crm"]["proposed_api_name"] = True
        problems = validator.validate_registry(registry)
        self.assertTrue(any("does not satisfy anyOf" in problem for problem in problems))

    def test_checked_in_schema_rejects_impossible_date(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["as_of_date"] = "2026-02-31"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("invalid ISO date" in problem for problem in problems))

    def test_rejects_empty_tenant_verified_api_name(self) -> None:
        registry = copy.deepcopy(self.registry)
        field = registry["fields"][0]
        field["zoho"]["type_status"] = "tenant_api_verified"
        field["zoho"]["evidence_id"] = "zoho-metadata-api"
        field["zoho"]["api_name"] = ""
        problems = validator.validate_registry(registry)
        self.assertTrue(any("api_name" in problem for problem in problems))

    def test_future_contracts_api_verification_is_supported(self) -> None:
        registry = copy.deepcopy(self.registry)
        field = next(
            item for item in registry["fields"] if item["id"] == "storage_unit_number"
        )
        field["zoho"]["type_status"] = "tenant_api_verified"
        field["zoho"]["evidence_id"] = "zoho-metadata-api"
        field["zoho"]["api_name"] = "storageUnitNumber"
        field["crm"]["api_name_status"] = "verified_live_mcp"
        field["crm"]["proposed_api_name"] = "Storage_Unit_Number"
        self.assertEqual([], validator.validate_registry(registry))

        markdown = validator.render_markdown(registry)
        self.assertIn("Single Line / `Storage_Unit_Number` (verified_live_mcp)", markdown)
        self.assertNotIn("Single Line / `Storage_Unit_Number` (proposed)", markdown)

    def test_future_tenant_only_system_verification_is_supported(self) -> None:
        registry = copy.deepcopy(self.registry)
        field = next(item for item in registry["fields"] if item["id"] == "party_a_time_zone")
        field["status"] = "active"
        field["portable_type"] = "time_zone"
        field["zoho"]["expected_native_type"] = "String"
        field["zoho"]["type_status"] = "tenant_api_verified"
        field["zoho"]["evidence_id"] = "zoho-metadata-api"
        field["zoho"]["api_name"] = "partyATimeZone"
        self.assertEqual([], validator.validate_registry(registry))

    def test_tenant_only_field_must_remain_review_required(self) -> None:
        registry = copy.deepcopy(self.registry)
        time_zone = next(
            field for field in registry["fields"] if field["id"] == "party_a_time_zone"
        )
        time_zone["status"] = "active"
        problems = validator.validate_registry(registry)
        self.assertTrue(any("must be review_required" in problem for problem in problems))

    def test_storage_start_alias_must_point_to_canonical_field(self) -> None:
        registry = copy.deepcopy(self.registry)
        alias = next(
            field for field in registry["fields"] if field["id"] == "storage_term_starts_legacy"
        )
        alias["canonical_id"] = "storage_term_end_date"
        problems = validator.validate_registry(registry)
        self.assertIn("Storage Term Starts must alias Storage Term Begins", problems)

    def test_required_inventory_cannot_drop_a_field(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"].pop()
        system_count = sum(
            field["classification"] == "system" for field in registry["fields"]
        )
        custom_count = sum(
            field["classification"] == "custom" for field in registry["fields"]
        )
        registry["record_counts"] = {
            "system": system_count,
            "custom": custom_count,
            "total": len(registry["fields"]),
        }
        problems = validator.validate_registry(registry)
        self.assertIn(
            "custom field labels/order drifted from the submitted inventory",
            problems,
        )

    def test_record_counts_are_derived_from_current_inventory(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["record_counts"]["custom"] -= 1
        problems = validator.validate_registry(registry)
        self.assertIn(
            "record_counts.custom does not match field inventory",
            problems,
        )


if __name__ == "__main__":
    unittest.main()
