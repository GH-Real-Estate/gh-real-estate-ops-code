# GH Real Estate Recipient Manifests

This directory governs recipient indexing, field ownership, and signing order for documents sent from Zoho Contracts to Zoho Sign.

## Canonical policy

`ghre-canonical-recipient-policy.json` is the machine-readable source of truth.

Zoho Sign treats `R<n>` as the **nth actual recipient added to the request**. Recipient numbers must remain contiguous and must not be treated as permanent business-role IDs or signing-order positions.

The invariant is:

> GH Real Estate, LLC is always the final actual recipient and the final signer.

That does **not** mean GH Real Estate is always `R4`. GH is `R4` only when exactly three actual non-landlord recipients precede it.

## Base residential manifests

| Actual signers | Recipient mapping | Signing positions |
|---|---|---|
| One tenant + GH | R1 Tenant 1; R2 GH Real Estate | Tenant 1 = 1; GH = 2 |
| Two tenants + GH | R1 Tenant 1; R2 Tenant 2; R3 GH Real Estate | Tenants = 1; GH = 2 |
| Three tenants + GH | R1 Tenant 1; R2 Tenant 2; R3 Tenant 3; R4 GH Real Estate | Tenants = 1; GH = 2 |

Recipient numbers identify field ownership. Signing positions control routing. Multiple non-landlord signers may share the same earlier signing position and sign in parallel; GH must have the highest position and no recipient may be routed after GH.

## Additional signers

A guarantor, witness, or other governed signer is inserted before GH. GH is then renumbered to the next contiguous recipient slot.

Example with one tenant, one guarantor, and GH:

| Recipient | Role | Signing position |
|---|---|---:|
| R1 | Tenant 1 | 1 |
| R2 | Guarantor | 1, unless the document-specific manifest requires another earlier level |
| R3 | GH Real Estate, LLC authorized representative | 2 — final |

Do not create dummy or placeholder recipients merely to keep GH at a particular R-number.

## Optional signer rule

An optional person is omitted entirely. If Tenant 2, Tenant 3, a guarantor, or another conditional signer does not exist:

1. Remove that recipient.
2. Remove every related text tag.
3. Remove the corresponding signature row.
4. Regenerate the remaining recipient manifest and tags with contiguous R-numbers.

If the person exists and is a named signer, the signature is required.

## Canonical simple tags

### One tenant

```text
Tenant 1: {{S:R1}} and {{SD:R1}}
GH Real Estate: {{S:R2}} and {{SD:R2}}
```

### Two tenants

```text
Tenant 1: {{S:R1}} and {{SD:R1}}
Tenant 2: {{S:R2}} and {{SD:R2}}
GH Real Estate: {{S:R3}} and {{SD:R3}}
```

### Three tenants

```text
Tenant 1: {{S:R1}} and {{SD:R1}}
Tenant 2: {{S:R2}} and {{SD:R2}}
Tenant 3: {{S:R3}} and {{SD:R3}}
GH Real Estate: {{S:R4}} and {{SD:R4}}
```

Use the active text-tag registry for syntax approval. This recipient policy does not approve padded tags, formatted sign-date tags, or other advanced syntax.

## Document-specific manifest files

Any checked-in `*.recipient-manifest.json` file must declare the actual recipients in contiguous order, each recipient's business role and signing position, and the GH landlord recipient when GH signs. The repository validator rejects gaps, placeholder recipients, a landlord that is not last, or any signer routed after the landlord.
