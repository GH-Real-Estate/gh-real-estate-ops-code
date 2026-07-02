# AGENTS.md

## Purpose

This repo contains GH Real Estate operational systems, Zoho automation code, scripts, configuration, documentation, and related business workflows.

## Business Priorities

1. Reliability
2. Auditability
3. Payment accuracy
4. Tenant-operation clarity
5. Compliance awareness
6. Minimal manual admin
7. Low support burden

## Working Rules

- Write professional, production-quality, industry-grade code.
- Keep the codebase understandable for future maintainers.
- Use professional comments where they improve clarity.
- Comment non-obvious business rules, edge cases, payment logic, tenant logic, lease logic, and integration assumptions.
- Avoid comments that merely repeat the code.
- Do not create duplicate automation paths.
- Do not double-charge, double-send, double-update, or duplicate records.
- Keep Zoho Books, Zoho CRM, Zoho Creator, Zoho Forms, Zoho Contracts, and Zoho Sign logic separated unless integration code requires otherwise.
- Use clear folder structure by business domain and integration.
- Keep payment, invoice, lease, tenant, notice, and deposit workflows especially clear and auditable.
- Do not store secrets, tenant PII, banking data, or private documents in source code.
- Use environment variables or secure configuration patterns.
- Prefer small, testable scripts and functions.
- Prefer idempotent automations where possible.
- Add guardrails for missing fields, bad dates, failed API responses, duplicate tenants, duplicate invoices, partial payments, and stale records.
- Do not make cosmetic-only changes unless requested.
- Do not introduce unnecessary frameworks, services, or abstractions.

## Folder Structure Guidance

Prefer organizing by business system and integration, for example:

- `zoho-books/`
- `zoho-crm/`
- `zoho-creator/`
- `zoho-forms/`
- `zoho-contracts/`
- `zoho-sign/`
- `automations/`
- `scripts/`
- `docs/`
- `tests/`

Use `automations/` only for workflows that span multiple systems or do not naturally belong to a single Zoho product. If a workflow is primarily owned by Zoho Books, Zoho CRM, or Zoho Creator, place it under that system’s folder.

## High-Risk Workflow Rules

For anything involving rent, deposits, invoices, payments, late fees, notices, leases, or tenant records:

- Add validation.
- Avoid destructive changes.
- Prefer dry-run or smoke-test modes where practical.
- Include rollback notes when relevant.
- Make duplicate prevention explicit.
- Do not assume balances or payment status unless the source data supports it.
- Do not claim a financial workflow is fixed unless it was tested or carefully verified.

## Verification

After changes, provide:

1. What changed
2. Why it changed
3. Files touched
4. Business behavior changed
5. How to test or smoke-test
6. Risks
7. Rollback steps if relevant
8. Comments or documentation added, and why
