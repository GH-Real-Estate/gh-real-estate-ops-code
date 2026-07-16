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

    def test_future_custom_tenant_verification_is_supported(self) -> None:
        registry = copy.deepcopy(self.registry)
        field = next(item for item in registry["fields"] if item["id"] == "lease_number")
        field["zoho"]["type_status"] = "tenant_api_verified"
        field["zoho"]["evidence_id"] = "zoho-metadata-api"
        field["zoho"]["api_name"] = "leaseNumber"
        field["crm"]["api_name_status"] = "tenant_api_verified"
        field["crm"]["proposed_api_name"] = "Lease_Number"
        self.assertEqual([], validator.validate_registry(registry))

        markdown = validator.render_markdown(registry)
        self.assertIn("Single Line / `Lease_Number` (tenant-verified)", markdown)
        self.assertNotIn("Single Line / `Lease_Number` (proposed)", markdown)

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

    def test_submitted_inventory_counts_are_fixed(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["fields"].pop()
        problems = validator.validate_registry(registry)
        self.assertTrue(any("46 system + 19 custom = 65" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
