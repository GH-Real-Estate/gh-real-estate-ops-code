from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = (
    ROOT
    / "src"
    / "zoho-sign"
    / "recipient-manifests"
    / "validate_recipient_policy.py"
)
POLICY_PATH = VALIDATOR_PATH.with_name("ghre-canonical-recipient-policy.json")

SPEC = importlib.util.spec_from_file_location("validate_recipient_policy", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load recipient policy validator")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RecipientPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_checked_in_policy_is_valid(self) -> None:
        self.assertEqual(VALIDATOR.validate_policy(self.policy), [])

    def test_repository_validation_is_clean(self) -> None:
        self.assertEqual(VALIDATOR.validate_repository(ROOT), [])

    def test_one_tenant_manifest_places_gh_at_r2_and_last(self) -> None:
        manifest = {
            "schema_version": "1.0.0",
            "manifest_id": "residential-lease-one-tenant",
            "document_type": "Residential Lease Agreement",
            "gh_signs": True,
            "recipients": copy.deepcopy(
                self.policy["base_residential_manifests"]["one_tenant"]["recipients"]
            ),
            "landlord_role": "R2",
        }
        self.assertEqual(VALIDATOR.validate_document_manifest(manifest), [])

    def test_three_tenant_manifest_places_gh_at_r4_and_last(self) -> None:
        manifest = {
            "schema_version": "1.0.0",
            "manifest_id": "residential-lease-three-tenants",
            "document_type": "Residential Lease Agreement",
            "gh_signs": True,
            "recipients": copy.deepcopy(
                self.policy["base_residential_manifests"]["three_tenants"]["recipients"]
            ),
            "landlord_role": "R4",
        }
        self.assertEqual(VALIDATOR.validate_document_manifest(manifest), [])

    def test_gap_in_recipient_numbers_is_rejected(self) -> None:
        manifest = {
            "schema_version": "1.0.0",
            "manifest_id": "invalid-gap",
            "document_type": "Residential Lease Agreement",
            "gh_signs": True,
            "recipients": [
                {
                    "role": "R1",
                    "business_role": "Tenant 1",
                    "signing_position": 1,
                },
                {
                    "role": "R4",
                    "business_role": VALIDATOR.LANDLORD_ROLE,
                    "signing_position": 2,
                },
            ],
            "landlord_role": "R4",
        }
        errors = VALIDATOR.validate_document_manifest(manifest)
        self.assertTrue(any("contiguous" in error for error in errors), errors)

    def test_landlord_not_last_is_rejected(self) -> None:
        manifest = {
            "schema_version": "1.0.0",
            "manifest_id": "invalid-landlord-order",
            "document_type": "Residential Lease Agreement",
            "gh_signs": True,
            "recipients": [
                {
                    "role": "R1",
                    "business_role": VALIDATOR.LANDLORD_ROLE,
                    "signing_position": 2,
                },
                {
                    "role": "R2",
                    "business_role": "Tenant 1",
                    "signing_position": 1,
                },
            ],
            "landlord_role": "R1",
        }
        errors = VALIDATOR.validate_document_manifest(manifest)
        self.assertTrue(any("final actual recipient" in error for error in errors), errors)

    def test_landlord_not_final_signing_position_is_rejected(self) -> None:
        manifest = {
            "schema_version": "1.0.0",
            "manifest_id": "invalid-signing-position",
            "document_type": "Residential Lease Agreement",
            "gh_signs": True,
            "recipients": [
                {
                    "role": "R1",
                    "business_role": "Tenant 1",
                    "signing_position": 2,
                },
                {
                    "role": "R2",
                    "business_role": VALIDATOR.LANDLORD_ROLE,
                    "signing_position": 2,
                },
            ],
            "landlord_role": "R2",
        }
        errors = VALIDATOR.validate_document_manifest(manifest)
        self.assertTrue(any("after every other signer" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
