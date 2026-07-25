# Recommended Zoho MCP Server Rollout

**Original decision:** Start with a custom, Zoho-hosted, read-only CRM configuration audit server.

**Current status:** The CRM boundary is implemented. The July 25, 2026 inventory also records three Books, three Catalyst, and two WorkDrive servers. The Books, Catalyst, and WorkDrive targets and write behavior remain acceptance-pending.

The sanitized source of truth for current server identifiers and exact Codex-advertised tools is [`configured-servers.md`](configured-servers.md). The Books target architecture, exact selection changes, correction policy, and production gates are maintained in [`books-accountant-controls.md`](books-accountant-controls.md). The WorkDrive/CRM/Catalyst document workflow and remaining capability gaps are maintained in [`document-intake-controls.md`](document-intake-controls.md).

## Current Implementation Status

| Order | Codex Server ID | Status | Current Boundary |
|---:|---|---|---|
| 1 | `gh_zoho_crm_audit` | Implemented; production acceptance passed | 18 CRM configuration metadata reads |
| 2 | `gh_zoho_crm_changes` | Implemented; production target confirmed | 15 configuration writes, 7 record reads, 4 record writes, and 1 organization check |
| 3 | `gh_zoho_books_accounting_audit` | Configured; organization acceptance not evidenced | 166 Books reads and reports |
| 4 | `gh_zoho_books_bookkeeping_changes` | Configured; organization and write acceptance not evidenced | 31 mixed routine and high-risk Books writes |
| 5 | `gh_zoho_books_controller` | Configured; organization and write acceptance not evidenced | 58 high-risk accounting and structural configuration writes |
| 6 | `gh_zoho_catalyst_webhook_audit` | Configured; target and effective-grant acceptance not evidenced | 15 Catalyst project, function, route, deployment, log, pipeline, and configuration reads |
| 7 | `gh_zoho_catalyst_webhook_release` | Configured; target and action acceptance not evidenced | 7 approval-gated function, pipeline, deployment, rollback, test, and build actions |
| 8 | `gh_zoho_catalyst_webhook_breakglass` | Configured; keep unavailable by default | 5 emergency route, environment-variable, and pipeline configuration writes |
| 9 | `gh_zoho_workdrive_audit` | Configured; identity, Team Folder, and binary-handoff acceptance not evidenced | 20 WorkDrive identity, Team Folder, file, version, permission, preview, and download reads |
| 10 | `gh_zoho_workdrive_changes` | Configured; identity, Team Folder, and write acceptance not evidenced | 5 folder, upload/status, move, and rename writes |
| 11 | `gh_zoho_books_configuration_admin` | Required before production accounting; not in current inventory | Normally disconnected structural configuration boundary |

These current servers are custom or adapted Zoho-hosted allowlists, not coded servers hosted in GitHub or Catalyst.

The CRM Audit acceptance test confirmed GH Real Estate and `type: production`. Its module call succeeded but was transport-truncated, and an advertised field projection returned `PATTERN_NOT_MATCHED`; the reported module pairs are confirmed, but inventory completeness is not certified. The CRM Changes production target was confirmed without testing a mutation.

The July 25 evidence confirms all ten current server names, OAuth display, and exact selected tool names. It does not establish the Books target organization; the Catalyst organization/project/environment; the WorkDrive user/team/Team Folder; the non-CRM OAuth identities or effective grants; binary file handoff; or any Books, Catalyst, or WorkDrive write. No sensitive read or write is authorized merely because a tool is selected.

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

Do not convert CRM Audit into a write-capable server. Preserve read/write separation. Use Audit for configuration readback and `gh_zoho_crm_changes` → `ZohoCRM_getRecord` for record-level post-write verification.

## Current Catalyst Boundaries

`gh_zoho_catalyst_webhook_audit` is the inspection and readback boundary. Logs, cache values, routes, deployment data, and environment-variable names can still be sensitive; do not publish raw responses.

`gh_zoho_catalyst_webhook_release` is sufficient for an existing function/pipeline release, bounded POST canary, automation test, redeploy, rollback, and log review after exact target acceptance. Pin the organization, project, environment, function, and sanitized payload. `CatalystbyZoho_Execute_Function_Via_POST` is generic invocation, not a dedicated OCR or webhook tool.

`gh_zoho_catalyst_webhook_breakglass` can alter routes, environment variables, and pipelines. Keep it disconnected or otherwise unavailable during routine operation. MCP environment-variable tools are nonsecret-only. Secret values must be entered directly in Zoho's secret UI or approved vault outside Codex/MCP.

The current catalog has no Catalyst create-function tool and no Zoho Payments webhook-registration tool. Initial function provisioning and payment-webhook registration therefore remain manual, CLI/pipeline, or separately governed API work.

## Current WorkDrive Decision

The 20-tool Audit and 5-tool Changes selections are the complete initial native allowlist for the concrete rental-application, inspection, condition-report, and lease workflow. They support identity/team discovery, file search and metadata, preview/download/version/change reads, permission inspection, folder creation, upload/status, move, and rename.

Do not add copy, overwrite/new-version, generic update, trash/delete, external sharing, Team Folder administration, membership, or role tools. `ZohoWorkdrive_Generate_File_Summary`, `ZohoWorkdrive_Get_File_Summary`, and `ZohoWorkdrive_File_Query` are optional only after a Zia/privacy review and are not substitutes for deterministic OCR. `ZohoWorkdrive_Download_Progress` belongs to the separate multi-download workflow and is not needed for one-document intake.

The WorkDrive servers can organize files after target and write acceptance. Unattended document understanding still requires the narrow processing and event controls in [`document-intake-controls.md`](document-intake-controls.md).

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

## Books Acceptance Order

1. Apply the exact tool additions, moves, and removals in [`books-accountant-controls.md`](books-accountant-controls.md).
2. Create Configuration Admin and keep it disconnected by default.
3. Implement the fixed-organization, draft-journal, plan, idempotency, stale-state, durable-write-ledger, and automation-ownership controls.
4. Confirm each server's expected organization, data center, OAuth identity, role, edition, fiscal year, accounting basis, base currency, and effective grants without changing financial records.
5. Run a read-only review of one closed historical month with complete pagination and ledger/subledger tie-outs.
6. Complete write acceptance in a dedicated test organization where available; otherwise use a uniquely marked unposted draft and an exact authorized human cleanup path.
7. Test a sanitized journal attachment and inspect both the Zoho MCP execution log and durable write ledger.
8. Confirm reconciled and locked-period writes fail closed.
9. Begin with a small, explicitly approved batch of current-period, reversible corrections.

## Catalyst And WorkDrive Acceptance Order

1. Confirm the exact Catalyst organization, project, environment, functions, deployments, routes, OAuth principal, and effective grants through Audit.
2. Confirm the exact WorkDrive user, data center, team, Team Folder, role, allowlisted parent IDs, sharing state, OAuth principal, and effective grants through Audit.
3. Test WorkDrive binary handoff with one sanitized text PDF and one sanitized image-only PDF.
4. Test folder creation, upload/status, move, rename, duplicate replay, same-name/different-content collision, and Audit readback in a dedicated nonproduction Team Folder.
5. Test the exact allowlisted Catalyst function with a sanitized payload and `DRY_RUN=true` where supported; inspect deployment state and logs.
6. Confirm Breakglass is unavailable during routine operation and that release rollback works without exposing secret values.
7. Add the narrow document processor and event source described in [`document-intake-controls.md`](document-intake-controls.md) before unattended extraction or CRM projection.
8. Validate exactly one CRM match, one-record create/update, record readback through `gh_zoho_crm_changes` → `ZohoCRM_getRecord`, WorkDrive readback, and a durable idempotency record.

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
- WorkDrive copy, overwrite/new-version, generic update, sharing, trash/delete, Team Folder administration, membership, or role authority for the initial document workflow.
- Arbitrary Catalyst function invocation, routine Breakglass access, or secret-value entry through Codex/MCP.
- Actual ACH, wire, card, check, refund disbursement, bank-feed credential, or payment-session initiation.
- Autonomous tax return filing, tax elections, tax payments, payroll processing, or statutory filing.
- Opening-balance, final year-end, or material prior-period changes without qualified review.
- A broad coded wrapper; implement only the narrow controls proven necessary for Books write safety and evidence gaps.

## Approval And Authorization

- Use distinct OAuth principals for Audit, Bookkeeping, Controller, and Configuration Admin where supported.
- Keep all write tools approval-gated; keep Controller and Configuration Admin unavailable by default.
- Keep Catalyst Breakglass unavailable by default and bind Release to the exact approved organization, project, environment, function, and payload shape.
- Bind WorkDrive Changes to the approved team, Team Folder, parent IDs, destination policy, and collision rules; verify every write through WorkDrive Audit.
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
- The Catalyst project/environment and WorkDrive user/team/Team Folder are fixed and unambiguous when those services are involved.
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

- The target organization, data center, OAuth identity, Catalyst project/environment, WorkDrive team/Team Folder, or resource is ambiguous.
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
- Broad WorkDrive administration beyond the approved document-intake workflow.
- Treating file preview, WorkDrive/Zia summary, or generic Catalyst invocation as verified all-page OCR.
- Zoho Contracts automation through MCP while Zoho Contracts is absent from the current Tool Manual.
- Sylvara MCP product development before repeated paid demand.
