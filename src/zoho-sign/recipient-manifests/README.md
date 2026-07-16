# GH Real Estate Recipient Manifests

This directory governs recipient-role numbering and signing order for documents sent from Zoho Contracts to Zoho Sign.

## Canonical policy

`ghre-canonical-recipient-policy.json` is the source of truth for GH Real Estate recipient numbering and routing.

| Recipient | Canonical role | Default signing position |
|---|---|---:|
| R1 | Tenant 1 / primary counterparty signer | 1 |
| R2 | Tenant 2 / additional counterparty signer, when present | 1 |
| R3 | Tenant 3 / additional counterparty signer, when present | 1 |
| R4 | GH Real Estate, LLC authorized representative | 2 — always last |
| R5+ | Guarantor, witness, or other approved additional signer | 1 unless a governed document manifest states otherwise |

Recipient numbers identify field ownership. They do not control routing order by themselves. Configure Zoho Sign signing positions separately and verify that every required non-landlord signer signs before R4. No signer may be routed after R4.

## Optional signer rule

An optional person is omitted entirely. If Tenant 2, Tenant 3, a guarantor, or another conditional signer does not exist, remove that recipient, every related text tag, and the corresponding signature row. If the person exists and is a named signer, the signature is required.

## Canonical simple tags

```text
Tenant 1: {{S:R1}} and {{SD:R1}}
Tenant 2: {{S:R2}} and {{SD:R2}}
Tenant 3: {{S:R3}} and {{SD:R3}}
GH Real Estate: {{S:R4}} and {{SD:R4}}
```

Use the active text-tag registry for syntax approval. This recipient policy does not approve padded tags, formatted sign-date tags, or other advanced syntax.
