# Zoho Sign

This directory governs Zoho Sign-specific configuration that is consumed by contracts and other business systems. It is deliberately separate from `src/zoho-contracts/`: Zoho Contracts owns contract content, while Zoho Sign owns recipient fields and signing behavior.

## Recipient manifests

- `recipient-manifests/ghre-canonical-recipient-policy.json` is the canonical, machine-readable source of truth for recipient numbering and signing order.
- `recipient-manifests/README.md` is the operator reference.
- R1 is Tenant 1, R2 is conditional Tenant 2, R3 is conditional Tenant 3, and R4 is always the GH Real Estate, LLC authorized representative.
- Configure routing separately so all tenants, guarantors, and other required non-landlord signers complete signing before R4. No signer may be routed after R4.
- R5 and higher are reserved for additional governed roles such as guarantors or witnesses; they still sign before R4 unless a later approved policy explicitly changes the rule.

## Field-tag registry

- `field-tags/zoho-contracts-text-tag-registry.json` is the canonical, machine-readable policy for text-tag grammar carried from Zoho Contracts into Zoho Sign.
- `field-tags/zoho-contracts-text-tag-registry.md` is generated documentation for operators and contract authors.
- `../zoho-contracts/scripts/validate_contract_authoring_standard.py` validates both the Contracts authoring standard and this Sign registry.

Only entries classified as `production_safe_simple_tags` may be committed to production contract content without a new tenant smoke test. Officially documented formatted or choice-field tags remain fail-closed until the exact Contracts-to-Sign path is proven in an isolated sample document.

The field catalog distinguishes between fields available in the Zoho Sign editor and fields with published text-tag grammar. Do not invent a tag merely because a corresponding editor field exists.

The field-tag registry governs syntax; the recipient-manifest policy governs who owns each R-number and when that signer is routed. Generic R1 examples in the syntax registry are examples only and do not override the canonical GH recipient assignment.
