# Recommended Zoho MCP Server Rollout

**Original decision:** Start with a custom, Zoho-hosted, read-only CRM configuration audit server.

**Current status:** The CRM boundary is implemented. The July 25, 2026 inventory also records a three-server Books accounting expansion that remains acceptance-pending.

The sanitized source of truth for current server identifiers and exact Codex-advertised tools is [`configured-servers.md`](configured-servers.md). The Books target architecture, exact selection changes, correction policy, and production gates are maintained in [`books-accountant-controls.md`](books-accountant-controls.md).

## Current Implementation Status

| Order | Codex Server ID | Status | Current Boundary |
|---:|---|---|---|
| 1 | `gh_zoho_crm_audit` | Implemented; production acceptance passed | 18 CRM configuration metadata reads |
| 2 | `gh_zoho_crm_changes` | Implemented; production target confirmed | 15 configuration writes, 7 record reads, 4 record writes, and 1 organization check |
| 3 | `gh_zoho_books_accounting_audit` | Configured; organization acceptance not evidenced | 166 Books reads and reports |
| 4 | `gh_zoho_books_bookkeeping_changes` | Configured; organization and write acceptance not evidenced | 31 mixed routine and high-risk Books writes |
| 5 | `gh_zoho_books_controller` | Configured; organization and write acceptance not evidenced | 58 high-risk accounting and structural configuration writes |
| 6 | `gh_zoho_books_configuration_admin` | Required before production accounting | Normally disconnected structural configuration boundary |
| 7 | GH WorkDrive Read | Deferred | Create only for a concrete recurring document workflow after exact tools are verified |

These current servers are custom or adapted Zoho-hosted allowlists, not coded servers hosted in GitHub or Catalyst.

The CRM Audit acceptance test confirmed GH Real Estate and `type: production`. Its module call succeeded but was transport-truncated, and an advertised field projection returned `PATTERN_NOT_MATCHED`; the reported module pairs are confirmed, but inventory completeness is not certified. The CRM Changes production target was confirmed without testing a mutation.

The July 25 evidence confirms the three Books server names, OAuth display, and exact selected tool names. It does not establish their target organization, OAuth identity, effective grant, or successful operation. No Books financial write is authorized merely because a tool is selected.

## Why Separate Servers And A Narrow Write Layer Win

The operational boundaries should match risk:

- Audit establishes current state and verifies results.
- Bookkeeping handles bounded ordinary transactions and bank classification.
- Controller handles credits, refunds, corrections, recurring schedules, fixed assets, draft-journal preparation, voids, write-offs, and other high-risk actions.
- Configuration Admin handles Chart of Accounts, bank-account setup, taxes, currencies, items, dimensions, custom fields, contacts, and opening balances, and remains disconnected by default.
- Journal approval/publication and transaction unlocking remain human/qualified-reviewer actions outside MCP.

OAuth scopes are broader than individual tools, and native tool selection cannot guarantee fixed-organization routing, draft-only journals, idempotency, stale-state protection, or payload-field restrictions. A narrow coded write layer is therefore required before unattended accounting writes. It must enforce the approved organization, immutable plan, exact fields, duplicate and automation-ownership rules, stale-state abort, durable operation ledger, ambiguous-timeout readback, and returned-record-ID persistence.

## Current CRM Boundaries

`gh_zoho_crm_audit` is the read-only CRM configuration inspection boundary. It excludes production-record retrieval and mutation. Its 18 tools cover organization, modules, fields, layouts, layout rules, global picklists, workflows, field updates, and workflow tasks.

`gh_zoho_crm_changes` is not configuration-only. It also contains seven production-record reads and four production-record writes. The record additions can retrieve or modify tenant, applicant, property, unit, lease, maintenance, and other records permitted to the authorizing user. Every call requires a bounded proposal and explicit approval.

Do not convert CRM Audit into a write-capable server. Preserve read/write separation and use Audit for post-change verification.

## Current Books Decision

The former `gh_zoho_books_review` server is absent from the July 25 inventory. Its narrow 12-read **Books Financial Overview** template has been superseded by Audit, Bookkeeping, and Controller.

The broader objective justifies expanded accounting capability, but the current 166/31/58 selection is not the final safe boundary. Transform it to:

| Server | Target Tools |
|---|---:|
| Audit | 166 |
| Bookkeeping | 17 |
| Controller | 53 |
| Configuration Admin | 27 |

The transformation must:

- Add organization and current-user reads to every write-capable boundary.
- Add `ZohoBooks_add_journal_attachment` to Bookkeeping.
- Move 25 structural tools from Controller to Configuration Admin.
- Move 17 credit, refund, sales-receipt, recurring-schedule, fixed-asset, and journal-preparation tools from Bookkeeping to Controller.
- Add recurring bill/expense stop and resume tools to Controller.
- Remove `ZohoBooks_approve_journal`, `ZohoBooks_mark_journal_published`, and `ZohoBooks_update_transaction_lock` from MCP.

Do not add delete tools. Corrections should preserve the accounting audit trail through an approved update, controlled reclassification, void/replacement, credit/refund, or reversal/compensating entry. Bank-feed exclusion is not archival.

## Acceptance Order

1. Apply the exact tool additions, moves, and removals in [`books-accountant-controls.md`](books-accountant-controls.md).
2. Create Configuration Admin and keep it disconnected by default.
3. Implement the fixed-organization, draft-journal, plan, idempotency, stale-state, durable-write-ledger, and automation-ownership controls.
4. Confirm each server's expected organization, data center, OAuth identity, role, edition, fiscal year, accounting basis, base currency, and effective grants without changing financial records.
5. Run a read-only review of one closed historical month with complete pagination and ledger/subledger tie-outs.
6. Complete write acceptance in a dedicated test organization where available; otherwise use a uniquely marked unposted draft and an exact authorized human cleanup path.
7. Test a sanitized journal attachment and inspect both the Zoho MCP execution log and durable write ledger.
8. Confirm reconciled and locked-period writes fail closed.
9. Begin with a small, explicitly approved batch of current-period, reversible corrections.

## Production Change Sequence

Use this sequence for every production change:

1. Audit the exact organization, OAuth identity, transaction, applications, ledger, reconciliation, and period-lock state.
2. Create a short-lived immutable plan containing source evidence, current-state hash, exact tool/parameters, accounting effect, duplicate and automation-owner checks, expected result, and reversal or compensating method.
3. Obtain explicit single-use approval for that plan.
4. Immediately reread and abort if the target, dependencies, or period state changed.
5. Apply only the validated call and persist its operation key, request hash, returned record ID, and outcome.
6. Read back through Audit and reconcile the affected ledger, bank account, AR/AP subledger, fixed-asset register, or other control total.
7. Review the Zoho MCP execution log and durable write ledger.

A broad request such as “clean up CRM” or “fix the books” is not approval for multiple writes. Do not store organization IDs, user IDs, raw responses, tenant/applicant records, financial records, tax documents, or private source evidence in GitHub.

## Explicit Exclusions

Do not add or authorize:

- Any Books or CRM delete or bulk-delete tool.
- A raw or generic Zoho request tool.
- A cross-suite GH Real Estate super-server.
- Journal approval, journal publication, or transaction-lock mutation through MCP.
- CRM upsert, merge, conversion, autonomous email-send, user, role, profile, permission, or portal-user tools.
- Direct Zoho Sign send, correct, recall, or deletion authority.
- Broad WorkDrive write, sharing, or deletion authority.
- Actual ACH, wire, card, check, refund disbursement, bank-feed credential, or payment-session initiation.
- Autonomous tax return filing, tax elections, tax payments, payroll processing, or statutory filing.
- Opening-balance, final year-end, or material prior-period changes without qualified review.
- A broad coded wrapper; implement only the narrow controls proven necessary for Books write safety and evidence gaps.

## Approval And Authorization

- Use distinct OAuth principals for Audit, Bookkeeping, Controller, and Configuration Admin where supported.
- Keep all write tools approval-gated; keep Controller and Configuration Admin unavailable by default.
- Bind the coded layer to the one expected GH organization and data-center domain; reject caller-supplied or mismatched organization values.
- Keep journal approval/publication outside the preparer/controller identity and prohibit self-approval.
- Require complete pagination before accounting conclusions.
- Use exact-decimal or integer-cent arithmetic.
- Never blindly retry an ambiguous financial write; search and read back by operation key and source identifiers first.
- Reject generic invoice writes for LF, INT, RF, recurring-rent, automatic-credit, and other automation-owned transactions.
- Keep MCP URLs, API keys, OAuth tokens, organization IDs, raw responses, tenant records, accounting records, and source documents out of GitHub.
- Treat repository documentation as an allowlist and policy reference, not proof of live configuration, deployment, or accounting authority.

## Continue Criteria

Continue only while all are true:

- The target organization and environment are fixed and unambiguous.
- Each server exposes only its approved tool boundary.
- Every production write is previewed, single-use approved, idempotent, bounded, logged, and verified.
- Controller and Configuration Admin require explicit activation and approval.
- Source evidence supports the accounting treatment.
- Complete pagination and readback are available.
- Stale state, reconciliation, or period locks cause a fail-closed stop.
- Zoho's MCP log and the durable write ledger show only the expected user, operation, record, and result.
- Existing deterministic automations retain ownership of late fees, monthly interest, returned-payment fees, recurring rent, and automatic credit application.

## Kill Criteria

Stop the affected workflow if any are true:

- The target organization, data center, OAuth identity, or environment is ambiguous.
- An advertised tool or count differs from the current approved inventory.
- A server exposes delete, raw-request, payment-initiation, journal-approval/publication, period-unlock, or unexpected administration tools.
- Pagination, source evidence, period status, current-state hash, or accounting effect is incomplete.
- A proposed query or write is broader than the approved target.
- The expected record count or operation outcome is unknown or materially different.
- A transaction is reconciled or the period is locked.
- The target changed after approval.
- Readback cannot verify the result.
- Tool approvals, organization binding, or write-ledger controls do not enforce the expected boundary.

## What To Ignore

- A single all-powerful Zoho server.
- Delete authority as a cleanup shortcut.
- Bank-feed exclusion as “archiving.”
- Autonomous payments, refunds, tax filing, payroll, journal approval, or year-end sign-off.
- WorkDrive management without a concrete workflow.
- Zoho Contracts automation through MCP while Zoho Contracts is absent from the current Tool Manual.
- Sylvara MCP product development before repeated paid demand.
