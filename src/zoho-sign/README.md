# Zoho Sign

This directory governs Zoho Sign-specific configuration that is consumed by contracts and other business systems. It is deliberately separate from `src/zoho-contracts/`: Zoho Contracts owns contract content, while Zoho Sign owns recipient fields and signing behavior.

## Recipient manifests

- `recipient-manifests/ghre-canonical-recipient-policy.json` is the canonical, machine-readable source of truth for recipient indexing and final-signer routing.
- `recipient-manifests/README.md` is the operator reference.
- Zoho Sign `R<n>` values are contiguous indexes for the actual recipients added to an envelope. They are not permanent Party A/Party B identifiers and they do not determine signing order.
- GH Real Estate, LLC must be the final actual recipient and must have the final signing position in every document GH signs.
- In a base residential document, GH is R2 with one tenant, R3 with two tenants, and R4 with three tenants.
- `residential-lease-one-tenant.recipient-manifest.json`, `residential-lease-two-tenants.recipient-manifest.json`, and `residential-lease-three-tenants.recipient-manifest.json` govern the supported Residential Lease signer sets.
- Guarantors, witnesses, and other governed non-landlord signers are inserted before GH, which moves GH to the next contiguous R-number.
- Do not create dummy recipients to preserve a fixed R-number. No signer may be routed after GH.
- `recipient-manifests/validate_recipient_policy.py` validates the canonical policy and all checked-in `*.recipient-manifest.json` files.

## Field-tag registry

- `field-tags/zoho-contracts-text-tag-registry.json` is the canonical, machine-readable policy for text-tag grammar carried from Zoho Contracts into Zoho Sign.
- `field-tags/zoho-contracts-text-tag-registry.md` is generated documentation for operators and contract authors.
- `../zoho-contracts/scripts/validate_contract_authoring_standard.py` validates the Contracts authoring standard and Sign field-tag registry.

Only entries classified as `production_safe_simple_tags` may be committed to production contract content without a new tenant smoke test. Officially documented formatted or choice-field tags remain fail-closed until the exact Contracts-to-Sign path is proven in an isolated sample document.

The field catalog distinguishes between fields available in the Zoho Sign editor and fields with published text-tag grammar. Do not invent a tag merely because a corresponding editor field exists.

The field-tag registry governs syntax. The recipient-manifest policy governs which actual recipient owns each R-number and when each signer is routed. Generic R1 examples in the syntax registry are syntax examples only and do not override a document-specific recipient manifest.
