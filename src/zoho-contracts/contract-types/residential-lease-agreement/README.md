# Residential Lease Agreement — Draft Implementation Package

This directory governs the Draft Only Zoho Contracts implementation of the July 14, 2026 Lead-First Residential Lease Agreement.

The DOCX controls tenant-facing legal wording and order. The matching 20-page PDF controls visual comparison. Current GitHub standards control clause taxonomy, schema, fields, typography, Zoho Sign tags, recipient routing, validation, and publication gates.

The public repository does not store the source binaries or live addresses, personal contact details, tenant values, signatures, or payment records. The package replaces prohibited instance data with visible blanks and records the exact field location and gate without changing the surrounding operative language.

Nothing here is attorney approval or a live Zoho deployment. The Contract Type must remain Draft, unpublished, blocked from execution, and unsent until every production gate is closed.

[`readable-clause-library.md`](readable-clause-library.md) is the generated professional reading view of the 59 ordered clause records for Articles 1–12. It is not the complete lease and must not be edited directly; update the referenced `.clause.json` files and regenerate it through the validator.

Run:

```powershell
python src/zoho-contracts/scripts/validate_contract_authoring_standard.py
python src/zoho-contracts/scripts/validate_contract_field_registry.py
python src/zoho-contracts/scripts/validate_residential_lease_implementation.py
python src/zoho-sign/recipient-manifests/validate_recipient_policy.py
python -m unittest discover -s src/zoho-contracts/tests -p 'test_*.py' -v
```

To intentionally regenerate the readable clause library after validated JSON changes:

```powershell
python src/zoho-contracts/scripts/validate_residential_lease_implementation.py --write-markdown
```
