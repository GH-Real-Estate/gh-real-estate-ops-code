# 2026-07-01 — Use One Private Repo For GH Real Estate

## Decision

Use one private repository for GH Real Estate technical assets:

```text
GH-Real-Estate/gh-real-estate-ops-code
```

## Reason

GH Real Estate has a small number of related automation systems. Keeping late fees, returned-payment webhook code, Zoho field maps, Creator exports, and runbooks in one repo gives Codex/ChatGPT enough context to understand how everything works together.

## Scope

Included:

- Deluge scripts.
- Zoho Catalyst / webhook code.
- Zoho Books and CRM field maps.
- Zoho Creator `.ds` exports if sanitized.
- Sanitized test payloads.
- Setup and deployment runbooks.

Excluded:

- Tenant files.
- Signed leases.
- Real payment records.
- PII.
- Raw production logs.
- Bank data.
