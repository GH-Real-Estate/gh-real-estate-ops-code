"""Regression tests for the Residential Lease implementation validator."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    ROOT
    / "src"
    / "zoho-contracts"
    / "scripts"
    / "validate_residential_lease_implementation.py"
)
SPEC = importlib.util.spec_from_file_location(
    "validate_residential_lease_implementation", SCRIPT
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ResidentialLeaseImplementationTests(unittest.TestCase):
    def valid_source_manifest(self, count: int = 59) -> dict:
        return {
            "schema_version": "1.0.0",
            "manifest_id": "ghre-rla-source",
            "contract_type": validator.CONTRACT_TYPE,
            "deployment_status": copy.deepcopy(
                validator.EXPECTED_DEPLOYMENT_STATUS
            ),
            "sources": copy.deepcopy(list(validator.EXPECTED_SOURCE_RECORDS)),
            "source_units": [
                {
                    "source_ref": f"SRC-{number:03d}",
                    "source_heading": f"Source Heading {number}",
                    "source_order": number,
                }
                for number in range(1, count + 1)
            ],
        }

    def valid_gates(self) -> list[dict]:
        return [
            {
                "gate_id": gate_id,
                "status": "open",
                "reason": f"{gate_id} remains unresolved.",
                "blocks": ["publish", "send"],
            }
            for gate_id in sorted(validator.EXPECTED_PRODUCTION_GATE_IDS)
        ]

    def valid_implementation(self) -> dict:
        return {
            "schema_version": "1.0.0",
            "implementation_id": "ghre-rla-contract-type",
            "contract_type": validator.CONTRACT_TYPE,
            "deployment_status": copy.deepcopy(
                validator.EXPECTED_DEPLOYMENT_STATUS
            ),
            "source_manifest_ref": "source-manifest.json",
            "crosswalk_ref": "source-to-clause-crosswalk.json",
            "field_map_ref": "document-field-map.json",
            "template_components_ref": "template-components.json",
            "attachment_requirements_ref": "attachment-requirements.json",
            "clause_records": [
                {
                    "code": code,
                    "path": (
                        "src/zoho-contracts/clauses/residential-lease-agreement/"
                        f"{code.casefold()}-topic-{code[-3:]}.clause.json"
                    ),
                }
                for code in validator.EXPECTED_CODES
            ],
            "recipient_manifests": {
                "one_tenant": (
                    "src/zoho-sign/recipient-manifests/"
                    "residential-lease-one-tenant.recipient-manifest.json"
                ),
                "two_tenants": (
                    "src/zoho-sign/recipient-manifests/"
                    "residential-lease-two-tenants.recipient-manifest.json"
                ),
                "three_tenants": (
                    "src/zoho-sign/recipient-manifests/"
                    "residential-lease-three-tenants.recipient-manifest.json"
                ),
            },
            "ending_text_variants": {
                "one_tenant": (
                    "src/zoho-contracts/contract-types/"
                    "residential-lease-agreement/ending-text/one-tenant.md"
                ),
                "two_tenants": (
                    "src/zoho-contracts/contract-types/"
                    "residential-lease-agreement/ending-text/two-tenants.md"
                ),
                "three_tenants": (
                    "src/zoho-contracts/contract-types/"
                    "residential-lease-agreement/ending-text/three-tenants.md"
                ),
            },
            "addendum_b_variants": {
                "one_tenant": (
                    "src/zoho-contracts/contract-types/"
                    "residential-lease-agreement/addendum-b/one-tenant.md"
                ),
                "two_tenants": (
                    "src/zoho-contracts/contract-types/"
                    "residential-lease-agreement/addendum-b/two-tenants.md"
                ),
                "three_tenants": (
                    "src/zoho-contracts/contract-types/"
                    "residential-lease-agreement/addendum-b/three-tenants.md"
                ),
            },
            "attachments": {
                "attachment_manifest": "attachment-requirements.json"
            },
            "production_gates": self.valid_gates(),
        }

    def valid_crosswalk(self, source_manifest: dict) -> dict:
        entries = []
        for index, unit in enumerate(source_manifest["source_units"]):
            code = validator.EXPECTED_CODES[index % len(validator.EXPECTED_CODES)]
            entries.append(
                {
                    "source_ref": unit["source_ref"],
                    "source_heading": unit["source_heading"],
                    "source_order": index + 1,
                    "target_kind": "clause",
                    "target_ref": code,
                    "target_style": "Heading 2",
                    "coverage_status": "mapped",
                    "gate_id": None,
                }
            )
        return {
            "schema_version": "1.0.0",
            "crosswalk_id": "ghre-rla-crosswalk",
            "source_manifest_ref": (
                "src/zoho-contracts/contract-types/"
                "residential-lease-agreement/source-manifest.json"
            ),
            "entries": entries,
            "source_outline_count": len(entries),
            "unmapped_source_refs": [],
        }

    @staticmethod
    def valid_recipient_manifest(tenant_count: int) -> dict:
        recipients = [
            {
                "role": f"R{number}",
                "business_role": f"Tenant {number}",
                "signing_position": 1,
            }
            for number in range(1, tenant_count + 1)
        ]
        recipients.append(
            {
                "role": f"R{tenant_count + 1}",
                "business_role": validator.LANDLORD_BUSINESS_ROLE,
                "signing_position": 2,
            }
        )
        return {
            "schema_version": "1.0.0",
            "manifest_id": f"rla-{tenant_count}-tenant",
            "document_type": validator.CONTRACT_TYPE,
            "gh_signs": True,
            "recipients": recipients,
            "landlord_role": f"R{tenant_count + 1}",
        }

    def test_expected_clause_codes_are_exactly_010_through_590(self) -> None:
        self.assertEqual(len(validator.EXPECTED_CODES), 59)
        self.assertEqual(validator.EXPECTED_CODES[0], "RLA-010")
        self.assertEqual(validator.EXPECTED_CODES[-1], "RLA-590")

    def test_all_checked_in_schemas_are_valid_json_objects(self) -> None:
        for path in validator._paths(ROOT)["schemas"].values():
            with self.subTest(path=path.name):
                self.assertIsInstance(validator.load_json(path), dict)

    def test_package_schema_references_are_exact_and_locked(self) -> None:
        paths = validator._paths(ROOT)
        for key, path in paths["data"].items():
            with self.subTest(package_file=path.name):
                payload = validator.load_json(path)
                self.assertEqual(
                    validator.validate_schema_reference(payload, key), []
                )
                changed = copy.deepcopy(payload)
                changed["$schema"] = "../../schemas/wrong.schema.json"
                self.assertTrue(
                    validator.validate_schema_reference(changed, key)
                )
                schema = validator.load_json(paths["schemas"][key])
                problems = validator.validate_json_schema(changed, schema)
                self.assertTrue(
                    any("$.$schema" in problem for problem in problems),
                    problems,
                )

    def test_critical_artifact_refs_and_variant_maps_are_required(self) -> None:
        implementation = self.valid_implementation()
        implementation.pop("template_components_ref")
        implementation.pop("attachment_requirements_ref")
        implementation.pop("addendum_b_variants")
        errors = validator.validate_implementation_bindings(implementation)
        self.assertTrue(any("template_components_ref" in error for error in errors))
        self.assertTrue(
            any("attachment_requirements_ref" in error for error in errors)
        )
        self.assertTrue(any("addendum_b_variants" in error for error in errors))

        schema = validator.load_json(
            validator._paths(ROOT)["schemas"]["implementation"]
        )
        problems = validator.validate_json_schema(implementation, schema)
        self.assertTrue(
            any(
                "missing required property template_components_ref" in item
                for item in problems
            )
        )
        self.assertTrue(
            any(
                "missing required property attachment_requirements_ref" in item
                for item in problems
            )
        )
        self.assertTrue(
            any("missing required property addendum_b_variants" in item for item in problems)
        )

    def test_variant_maps_reject_missing_or_unexpected_signer_counts(self) -> None:
        implementation = self.valid_implementation()
        implementation["ending_text_variants"].pop("three_tenants")
        implementation["recipient_manifests"]["four_tenants"] = "wrong.json"
        errors = validator.validate_implementation_bindings(implementation)
        self.assertTrue(
            any("ending_text_variants must contain exactly" in error for error in errors)
        )
        self.assertTrue(
            any("recipient_manifests must contain exactly" in error for error in errors)
        )

    def test_draft_only_state_is_exact_and_fail_closed(self) -> None:
        self.assertEqual(
            validator.validate_deployment_status(
                copy.deepcopy(validator.EXPECTED_DEPLOYMENT_STATUS)
            ),
            [],
        )
        unsafe = copy.deepcopy(validator.EXPECTED_DEPLOYMENT_STATUS)
        unsafe["published"] = True
        errors = validator.validate_deployment_status(unsafe)
        self.assertTrue(any("Draft-only" in error for error in errors), errors)

    def test_source_order_must_be_sequential(self) -> None:
        manifest = self.valid_source_manifest(3)
        manifest["source_units"][1]["source_order"] = 1
        errors = validator.validate_source_manifest(manifest)
        self.assertTrue(any("exact sequential range" in error for error in errors))

    def test_source_identities_hashes_pages_and_excluded_file_are_locked(
        self,
    ) -> None:
        manifest = self.valid_source_manifest(3)
        manifest["sources"][0]["sha256"] = "0" * 64
        manifest["sources"][-1]["page_count"] = 21
        manifest["sources"][-1]["filename"] = "Residential Lease Agreement.docx"
        errors = validator.validate_source_manifest(manifest)
        self.assertTrue(any(".sha256 must exactly match" in error for error in errors))
        self.assertTrue(any(".page_count must exactly match" in error for error in errors))
        self.assertTrue(any(".filename must exactly match" in error for error in errors))

        missing_excluded = self.valid_source_manifest(3)
        missing_excluded["sources"].pop()
        errors = validator.validate_source_manifest(missing_excluded)
        self.assertTrue(any("exact governed source sequence" in error for error in errors))

    def test_crosswalk_requires_complete_exact_source_coverage(self) -> None:
        source = self.valid_source_manifest(3)
        crosswalk = self.valid_crosswalk(source)
        crosswalk["entries"].pop()
        errors = validator.validate_crosswalk(
            crosswalk, source, open_gate_ids=validator.REQUIRED_OPEN_GATES
        )
        self.assertTrue(
            any(
                "exactly one record" in error
                or "sequential source_order" in error
                for error in errors
            )
        )

    def test_crosswalk_identity_heading_and_order_must_match_source_units(
        self,
    ) -> None:
        source = self.valid_source_manifest(3)
        crosswalk = self.valid_crosswalk(source)
        crosswalk["entries"][0]["source_ref"] = "wrong-ref"
        crosswalk["entries"][1]["source_heading"] = "Wrong heading"
        crosswalk["entries"][2]["source_order"] = 2
        errors = validator.validate_crosswalk(
            crosswalk,
            source,
            open_gate_ids=validator.EXPECTED_PRODUCTION_GATE_IDS,
        )
        self.assertTrue(any(".source_ref must exactly match" in error for error in errors))
        self.assertTrue(
            any(".source_heading must exactly match" in error for error in errors)
        )
        self.assertTrue(
            any(".source_order must exactly match" in error for error in errors)
        )

    def test_deferred_crosswalk_entry_requires_open_gate(self) -> None:
        source = self.valid_source_manifest(1)
        crosswalk = self.valid_crosswalk(source)
        entry = crosswalk["entries"][0]
        entry.update(
            {
                "target_kind": "attachment",
                "target_ref": None,
                "target_style": "Attachment",
                "coverage_status": "deferred",
                "gate_id": "closed_or_missing",
            }
        )
        errors = validator.validate_crosswalk(
            crosswalk, source, open_gate_ids=validator.REQUIRED_OPEN_GATES
        )
        self.assertTrue(any("open production gate" in error for error in errors))

    def test_required_production_gates_must_remain_open(self) -> None:
        implementation = self.valid_implementation()
        legal_gate = next(
            gate
            for gate in implementation["production_gates"]
            if gate["gate_id"] == "legal_currentness"
        )
        legal_gate["status"] = "closed"
        errors, _ = validator.validate_production_gates(implementation)
        self.assertTrue(any("must remain open" in error for error in errors))

    def test_production_gate_set_must_be_exact_with_no_extras(self) -> None:
        self.assertEqual(len(validator.EXPECTED_PRODUCTION_GATE_IDS), 29)
        implementation = self.valid_implementation()
        implementation["production_gates"].pop()
        implementation["production_gates"].append(
            {
                "gate_id": "invented_gate",
                "status": "open",
                "reason": "Not governed.",
                "blocks": ["publish"],
            }
        )
        errors, _ = validator.validate_production_gates(implementation)
        self.assertTrue(any("missing exact governed gate IDs" in error for error in errors))
        self.assertTrue(any("unexpected gate IDs" in error for error in errors))

    def test_unverified_api_name_must_remain_null(self) -> None:
        field_map = {
            "mappings": [
                {
                    "source_variable": "lease_number",
                    "business_meaning": "Lease number",
                    "registry_field_id": "lease_number",
                    "zoho_api_name": "leaseNumber",
                    "api_name_status": "tenant_verification_required",
                    "source_system": "Zoho CRM",
                    "snapshot_behavior": "freeze_at_generation",
                    "status": "mapped",
                    "gate_id": None,
                }
            ]
        }
        registry = {
            "fields": [
                {
                    "id": "lease_number",
                    "zoho": {
                        "api_name": None,
                        "type_status": "design_decision",
                    },
                }
            ]
        }
        errors = validator.validate_field_map(
            field_map, registry, open_gate_ids=validator.REQUIRED_OPEN_GATES
        )
        self.assertTrue(any("must remain null" in error for error in errors))

    def test_contract_amount_cannot_stand_in_for_monthly_rent(self) -> None:
        field_map = {
            "mappings": [
                {
                    "source_variable": "monthly_rent",
                    "business_meaning": "Monthly Rent",
                    "registry_field_id": "contract_amount",
                    "zoho_api_name": None,
                    "api_name_status": "tenant_verification_required",
                    "source_system": "Unresolved",
                    "snapshot_behavior": "freeze_at_generation",
                    "status": "deferred",
                    "gate_id": "monthly_rent_source_ownership",
                }
            ]
        }
        registry = {
            "fields": [
                {
                    "id": "contract_amount",
                    "zoho": {
                        "api_name": None,
                        "type_status": "official_system_semantics",
                    },
                }
            ]
        }
        errors = validator.validate_field_map(
            field_map, registry, open_gate_ids=validator.REQUIRED_OPEN_GATES
        )
        self.assertTrue(any("must not map monthly rent" in error for error in errors))

    def test_recipient_manifest_keeps_gh_final(self) -> None:
        manifest = self.valid_recipient_manifest(3)
        self.assertEqual(
            validator.validate_recipient_manifest(
                manifest, tenant_count=3, name="three-tenants"
            ),
            [],
        )
        manifest["recipients"][-1]["business_role"] = "Tenant 4"
        errors = validator.validate_recipient_manifest(
            manifest, tenant_count=3, name="three-tenants"
        )
        self.assertTrue(any("GH landlord role" in error for error in errors))

    def test_ending_text_requires_one_signature_and_date_per_recipient(self) -> None:
        manifest = self.valid_recipient_manifest(2)
        text = "\n".join(
            [
                "{{S:R1}} {{SD:R1}}",
                "{{S:R2}} {{SD:R2}}",
                "{{S:R3}} {{SD:R3}}",
            ]
        )
        self.assertEqual(
            validator.validate_ending_text(text, manifest, name="ending-text"),
            [],
        )
        errors = validator.validate_ending_text(
            text.replace("{{SD:R3}}", ""), manifest, name="ending-text"
        )
        self.assertTrue(any("Sign Date tag for R3" in error for error in errors))

    def test_formatted_sign_date_is_rejected_in_ending_text(self) -> None:
        manifest = self.valid_recipient_manifest(1)
        text = (
            "{{S:R1}} {{SD:R1}} {{S:R2}} "
            '{{SD:R2:(dateformat="MMM dd yyyy")}}'
        )
        errors = validator.validate_ending_text(
            text, manifest, name="ending-text"
        )
        self.assertTrue(any("unsupported Sign tag" in error for error in errors))

    def test_addendum_b_requires_safe_tags_and_two_initials_per_tenant(
        self,
    ) -> None:
        manifest = self.valid_recipient_manifest(2)
        text = "\n".join(
            [
                "<!-- Do not preselect HOA applicability or delivery status -->",
                "# Addendum B. HOA and Tenant Handbook Acknowledgment",
                "{{I:R1}} {{I:R1}} {{I:R2}} {{I:R2}}",
                "{{S:R1}} {{SD:R1}}",
                "{{S:R2}} {{SD:R2}}",
                "{{S:R3}} {{SD:R3}}",
            ]
        )
        self.assertEqual(
            validator.validate_addendum_b(text, manifest, name="addendum-b"),
            [],
        )

        unsafe = text.replace("{{I:R2}}", "", 1).replace(
            "{{SD:R3}}", '{{SD:R3:(dateformat="MMM dd yyyy")}}'
        )
        errors = validator.validate_addendum_b(
            unsafe, manifest, name="addendum-b"
        )
        self.assertTrue(any("exactly 2 initial tag(s) for R2" in item for item in errors))
        self.assertTrue(any("unsupported Sign tag" in item for item in errors))

    def test_mapped_clause_heading_and_body_cannot_be_removed(self) -> None:
        source_headings = ["1.1. Parties", "1.2. Premises"]
        variant = {
            "clause_title": "1.1. Parties",
            "blocks": [
                {"style": "Normal", "text": "Parties body."},
                {"style": "Heading 3", "text": "1.2. Premises"},
                {"style": "Normal", "text": "Premises body."},
            ],
        }
        self.assertEqual(
            validator.validate_mapped_clause_content(
                variant, source_headings, name="RLA-010"
            ),
            [],
        )
        variant["blocks"].pop()
        errors = validator.validate_mapped_clause_content(
            variant, source_headings, name="RLA-010"
        )
        self.assertTrue(
            any("must retain substantive body content" in item for item in errors)
        )

        variant["blocks"].pop()
        errors = validator.validate_mapped_clause_content(
            variant, source_headings, name="RLA-010"
        )
        self.assertTrue(
            any("mapped heading sequence must exactly match" in item for item in errors)
        )

    def test_clause_records_validate_exact_names_files_and_source_mapping(self) -> None:
        paths = validator._paths(ROOT)
        implementation = validator.load_json(
            paths["data"]["implementation"]
        )
        crosswalk = validator.load_json(paths["data"]["crosswalk"])
        standard = validator.load_json(paths["authoring_standard"])
        clause_types = set(standard["clause_type_master_list"])
        self.assertEqual(
            validator.validate_clause_records(
                ROOT, implementation, crosswalk, clause_types
            ),
            [],
        )

        changed = copy.deepcopy(implementation)
        changed["clause_records"][0]["clause_title"] = "Wrong title"
        errors = validator.validate_clause_records(
            ROOT, changed, crosswalk, clause_types
        )
        self.assertTrue(
            any(
                "clause_title must exactly match" in error for error in errors
            ),
            errors,
        )

    def test_template_components_are_loaded_and_crosswalk_targets_exist(
        self,
    ) -> None:
        paths = validator._paths(ROOT)
        implementation = validator.load_json(
            paths["data"]["implementation"]
        )
        crosswalk = validator.load_json(paths["data"]["crosswalk"])
        components = validator.load_json(
            paths["artifacts"]["template_components"]
        )
        self.assertEqual(
            validator.validate_template_components(
                components,
                implementation,
                crosswalk,
                open_gate_ids=set(validator.EXPECTED_PRODUCTION_GATE_IDS),
            ),
            [],
        )

        changed = copy.deepcopy(components)
        changed["components"] = [
            item
            for item in changed["components"]
            if item.get("component_id") != "lease-summary-table"
        ]
        errors = validator.validate_template_components(
            changed,
            implementation,
            crosswalk,
            open_gate_ids=set(validator.EXPECTED_PRODUCTION_GATE_IDS),
        )
        self.assertTrue(
            any("mapped template component does not exist" in item for item in errors)
        )

    def test_attachment_requirements_are_loaded_and_crosswalk_targets_exist(
        self,
    ) -> None:
        paths = validator._paths(ROOT)
        implementation = validator.load_json(
            paths["data"]["implementation"]
        )
        crosswalk = validator.load_json(paths["data"]["crosswalk"])
        attachments = validator.load_json(
            paths["artifacts"]["attachment_requirements"]
        )
        self.assertEqual(
            validator.validate_attachment_requirements(
                attachments,
                implementation,
                crosswalk,
                open_gate_ids=set(validator.EXPECTED_PRODUCTION_GATE_IDS),
            ),
            [],
        )

        changed = copy.deepcopy(attachments)
        changed["requirements"] = [
            item
            for item in changed["requirements"]
            if item.get("requirement_id")
            != "executed-addendum-a-lead-disclosure"
        ]
        errors = validator.validate_attachment_requirements(
            changed,
            implementation,
            crosswalk,
            open_gate_ids=set(validator.EXPECTED_PRODUCTION_GATE_IDS),
        )
        self.assertTrue(
            any(
                "mapped attachment requirement does not exist" in item
                for item in errors
            )
        )
        self.assertTrue(
            any(
                "executed-addendum-a-lead-disclosure requirement is required"
                in item
                for item in errors
            )
        )

    def test_all_checked_in_addendum_b_variants_match_recipient_manifests(
        self,
    ) -> None:
        paths = validator._paths(ROOT)
        implementation = validator.load_json(
            paths["data"]["implementation"]
        )
        self.assertEqual(
            validator.validate_recipient_and_ending_variants(
                ROOT, implementation
            ),
            [],
        )

    def test_missing_package_returns_errors_without_crashing(self) -> None:
        errors = validator.validate_repository(ROOT / "missing-rla-fixture-root")
        self.assertTrue(errors)
        self.assertTrue(any("source-manifest" in error for error in errors))

    def test_checked_in_package_is_valid_when_present(self) -> None:
        package = ROOT / validator.PACKAGE_REL
        if not package.exists():
            self.skipTest("RLA data package is being added by the companion change")
        self.assertEqual(validator.validate_repository(ROOT), [])


if __name__ == "__main__":
    unittest.main()
