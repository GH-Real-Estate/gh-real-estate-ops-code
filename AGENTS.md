# AGENTS.md — GH Real Estate Ops Code

Codex/ChatGPT instructions for this repository.

## Business Context

GH Real Estate uses Zoho as the live business operating system.

- Zoho CRM: applicants, tenant relationship records, leasing pipeline.
- Zoho Books: invoices, rent, payments, deposits, fees, financial source of truth.
- Zoho Contracts / Zoho Sign / Zoho WorkDrive: leases and signed/legal documents.
- Zoho Creator: tenant portal / maintenance workflows when deployed.
- GitHub: technical source of truth for code, field maps, sanitized samples, runbooks, and tests.

## Repository Layout Rule

Organize code by source system / runtime:

- `src/zoho-books/` contains code and field maps owned by Zoho Books.
- `src/zoho-payments/` contains webhook handling for Zoho Payments events.
- `src/zoho-crm/` contains CRM functions and CRM field maps.
- `src/zoho-creator/` contains sanitized Creator exports and import notes.
- `src/zoho-contracts/` contains Contracts merge-field maps only.
- `docs/` contains cross-system architecture, business rules, runbooks, security notes, and ADRs.
- `samples/` contains sanitized payload examples grouped by source system.

Do not recreate a generic top-level `automations/` folder. Automations belong under the system that owns or runs them.

## Primary Rule

Do not turn this repository into a tenant file cabinet or accounting database. It is a technical code and documentation repository only.

## Security Rules

Never add:

- Real tenant names, phone numbers, emails, IDs, SSNs, bank details, pay stubs, immigration records, signed leases, actual payment IDs, raw production logs, or unredacted webhook payloads.
- OAuth tokens, API keys, refresh tokens, client secrets, private keys, passwords, webhook secrets, or live credentials.
- Raw Zoho exports that include real customers, invoices, payment data, leases, or uploaded documents.

Always use:

- Environment variable names and `.env.example` only.
- Sanitized test records such as `TENANT_TEST_001`, `INV_TEST_001`, `PAYMENT_TEST_001`, and `UNIT_TEST_1`.
- Minimal logging that avoids PII and secrets.

## Automation Rules

- Zoho Books is the financial source of truth.
- Late-fee code must be idempotent. Running it twice must not create duplicate fees.
- Returned-payment handling must be separate from late-fee handling unless explicitly changed.
- Default to dry-run mode for automation that creates, updates, deletes, invoices, charges, emails, or texts.
- Live mode must be explicit, documented, and smoke-tested.
- Any fee amount, date threshold, interest rule, item ID, template ID, or custom-field API name must be documented in the relevant README and field map.
- Any change to business logic must update `docs/business-rules/`, `docs/adr/`, and the relevant test cases.

## Review Priorities

When reviewing code, prioritize:

1. Duplicate fee prevention / idempotency.
2. Date/time-zone handling, especially Central Time and 5:00 p.m. deadlines.
3. Dry-run safety.
4. Authentication and webhook signature verification.
5. Replay protection for webhook endpoints.
6. Error handling and retry behavior.
7. No PII/secrets in logs.
8. Zoho API pagination, rate limits, and response handling.
9. Alignment with documented lease/business rules.
10. Clear install/deploy/rollback instructions.

## Coding Conventions

- Deluge files use `.deluge` extension.
- JavaScript/Node code uses clear function names and defensive input checks.
- Keep config in environment variables or documented Zoho connection names, not hardcoded secrets.
- Prefer small functions over large unstructured scripts.
- Add comments where business logic could be misunderstood.
- Do not add dependencies without a reason.

## Do Not Do

- Do not replace Zoho Books, Zoho CRM, or Zoho Contracts with this repo.
- Do not introduce a custom tenant database unless explicitly requested.
- Do not store real business records here.
- Do not deploy automatically unless a deploy workflow has been reviewed and approved.
