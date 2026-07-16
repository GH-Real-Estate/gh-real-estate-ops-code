# Zoho Sign

This directory governs Zoho Sign-specific configuration that is consumed by contracts and other business systems. It is deliberately separate from `src/zoho-contracts/`: Zoho Contracts owns contract content, while Zoho Sign owns recipient fields and signing behavior.

## Field-tag registry

- `field-tags/zoho-contracts-text-tag-registry.json` is the canonical, machine-readable policy for text tags carried from Zoho Contracts into Zoho Sign.
- `field-tags/zoho-contracts-text-tag-registry.md` is generated documentation for operators and contract authors.
- `../zoho-contracts/scripts/validate_contract_authoring_standard.py` validates both the Contracts authoring standard and this Sign registry.

Only entries classified as `production_safe_simple_tags` may be committed to production contract content without a new tenant smoke test. Officially documented formatted or choice-field tags remain fail-closed until the exact Contracts-to-Sign path is proven in an isolated sample document.

The field catalog distinguishes between fields available in the Zoho Sign editor and fields with published text-tag grammar. Do not invent a tag merely because a corresponding editor field exists.
