# Zoho Books Accountant MCP Controls

**Verified:** July 25, 2026

**Status:** Current capability captured; read-only acceptance and all production accounting writes remain pending.

## Decision

The three current Books servers provide broad read coverage and most native actions needed for bookkeeping, reconciliation, correction, and close preparation. They are not yet safe for production accounting writes.

Native Zoho-hosted tool selection can support supervised, individually approved work. It cannot by itself enforce a fixed organization, durable idempotency, stale-state protection, draft-only journal creation, payload-field restrictions, or maker/approver separation. Professional-grade automated posting therefore requires a narrow coded enforcement layer with a durable write ledger. Until that layer exists, keep every native Books write human-approved and never run unattended cleanup.

The required changes are:

1. Add `ZohoBooks_get_organization` and `ZohoBooks_get_current_user` to every write-capable Books server as connection identity checks.
2. Add `ZohoBooks_add_journal_attachment` to `gh_zoho_books_bookkeeping_changes`.
3. Move the 25 structural configuration tools listed below from Controller into a normally disconnected `gh_zoho_books_configuration_admin` server.
4. Move the 17 high-risk posting and schedule tools listed below from Bookkeeping into Controller.
5. Remove journal approval, journal publication, and transaction-lock mutation from MCP.
6. Add the verified recurring bill and expense stop/resume lifecycle tools to Controller.
7. Enforce the fixed GH organization, approved payload, immutable plan, stale-state check, idempotency key, returned-ID persistence, and post-write reconciliation in a narrow coded layer before automated posting.
8. Complete organization, identity, scope, read, draft-write, and readback acceptance checks for every Books boundary.

Do not add generic delete tools. Proper accounting correction normally uses a safe update while a record is still editable, a controlled reclassification, a void plus replacement, a credit/refund, or a reversing/compensating journal. Deletion destroys useful audit evidence and is not needed for routine cleanup.

This design can support AI-assisted bookkeeping, reconciliation, close preparation, and evidence-backed adjustment proposals. It does not replace owner/controller approval or a qualified accountant or tax professional for material judgment, tax filings, elections, final year-end close, opening-balance changes, locked-period changes, or actual movement of funds.

## Intended Supervised Native Layout

After the tool-selection changes above, the intended native layout is:

| Server | Intended Tools | Boundary |
|---|---:|---|
| `gh_zoho_books_accounting_audit` | 166 | Read-only accounting, reports, and post-write verification |
| `gh_zoho_books_bookkeeping_changes` | 17 | Routine bounded transaction and bank-classification writes |
| `gh_zoho_books_controller` | 53 | Approval-gated correction, recurring schedule, refund, void, write-off, journal-preparation, and close actions |
| `gh_zoho_books_configuration_admin` | 27 | Normally disconnected structural configuration writes plus two identity reads |

These counts are configuration acceptance checks, not proof of safe automation. Stop and re-audit the selection if the live server builder shows different counts.

The current exact 166/31/58 selection remains recorded in [`configured-servers.md`](configured-servers.md). The sections below define how to transform the two current write selections.

## Evidence Boundary

The current membership is transcribed from a sanitized Codex inventory supplied on July 25, 2026. It proves the names Codex advertised at capture time. It does not prove:

- The target Zoho Books organization.
- The OAuth principal or effective grant for every selected tool.
- Tool availability under the current Books edition, role, or data center.
- Successful reads, writes, pagination, attachment transfer, or retry behavior.
- The correctness of any accounting treatment.

The dated public MCP Tool Manual snapshot did not contain `add_journal_attachment`, but the authenticated Zoho MCP template capture did. Zoho's current Books API separately documents `POST /journals/{journal_id}/attachment` under `ZohoBooks.accountants.CREATE`. Recheck the live Zoho picker before changing the server.

Official references:

- [Zoho Books Journals API](https://www.zoho.com/books/api/v3/journals/)
- [Zoho Books OAuth scopes](https://www.zoho.com/books/api/v3/oauth/)
- [Zoho Books Transaction Locking API](https://www.zoho.com/books/api/v3/transaction-locking/)
- [Captured Zoho MCP tool inventory](tool-inventory.md)
- [Captured preconfigured server inventory](preconfigured-servers.md)
- [GH Zoho Books API and control dossier](../products/zoho-books.md)

## Journal Attachment Finding

`ZohoBooks_add_journal_attachment` is absent from both current write selections:

- `gh_zoho_books_bookkeeping_changes` contains `ZohoBooks_add_journal_comment`, but no journal-attachment tool.
- `gh_zoho_books_controller` contains journal approval, publication, and reversal actions, but no journal-attachment tool.

Add the exact live picker tool to Bookkeeping. It is an evidence operation, not approval to create or publish a journal. Test it with a harmless draft journal and sanitized test attachment, read back the journal metadata through Audit, and review the Zoho MCP execution log.

The captured native Books catalog does not contain a separately named `get_journal_attachment` tool. Treat journal-attachment download/readback as a known limitation unless the current live picker now exposes an exact retrieval tool.

## Supporting-Document Gap

Professional bookkeeping requires source evidence, not only Books transaction fields.

- The dated native Books catalog contains `add_invoice_document`, but the current Bookkeeping selection does not.
- The dated native Books catalog does not contain a Books-scoped `get_invoice_attachment`, generic bill-attachment add/get, expense-receipt add/get, or journal-attachment retrieval tool. The similarly named `get_invoice_attachment` in the full catalog belongs to Zoho POS, not Zoho Books.
- The underlying Books APIs document attachment and receipt operations, but an API operation does not prove that a matching native MCP picker tool exists.

Before claiming complete evidence handling:

1. Recheck the live picker for exact invoice, bill, expense, receipt, and journal attachment tools.
2. Add only verified read tools to Audit and verified add/upload tools to Bookkeeping.
3. If required evidence remains unavailable through native MCP, use user-supplied documents for review or a narrow coded wrapper with file-type, size, fixed-organization, record, malware, duplicate-hash, and audit-log controls.
4. Never add a generic raw-request tool merely to bypass the native allowlist.

## Bookkeeping Final Selection

Bookkeeping should contain these 17 tools:

```text
ZohoBooks_add_bank_reconciliation_attachment
ZohoBooks_add_journal_attachment
ZohoBooks_add_journal_comment
ZohoBooks_categorize_bank_transaction
ZohoBooks_categorize_bank_transaction_as_customer_payment
ZohoBooks_categorize_bank_transaction_as_expense
ZohoBooks_categorize_bank_transaction_as_vendor_payment
ZohoBooks_create_bill
ZohoBooks_create_expense
ZohoBooks_create_invoice
ZohoBooks_get_current_user
ZohoBooks_get_organization
ZohoBooks_match_bank_transaction
ZohoBooks_save_bank_reconciliation_draft
ZohoBooks_update_bill
ZohoBooks_update_expense
ZohoBooks_update_invoice
```

Generic invoice tools must reject late-fee (`LF`), monthly-interest (`INT`), returned-payment-fee (`RF`), recurring-rent, and automatic unused-credit activity owned by existing deterministic automations. Until a coded layer enforces that rule, every invoice create/update requires an exact transaction-class review and explicit approval.

## Controller Moves And Final Selection

Move these 17 tools from Bookkeeping to Controller:

```text
ZohoBooks_categorize_as_credit_note_refunds
ZohoBooks_categorize_as_vendor_credit_refunds
ZohoBooks_categorize_as_vendor_payment_refund
ZohoBooks_create_credit_note
ZohoBooks_create_fixed_asset
ZohoBooks_create_journal
ZohoBooks_create_recurring_bill
ZohoBooks_create_recurring_expense
ZohoBooks_create_sales_receipt
ZohoBooks_create_vendor_credit
ZohoBooks_update_credit_note
ZohoBooks_update_fixed_asset
ZohoBooks_update_journal
ZohoBooks_update_recurring_bill
ZohoBooks_update_recurring_expense
ZohoBooks_update_sales_receipt
ZohoBooks_update_vendor_credit
```

These actions affect refunds, credits, cash/revenue, journals, recurring schedules, or fixed-asset accounting. They are not routine categorization.

Add these six tools to Controller:

```text
ZohoBooks_get_current_user
ZohoBooks_get_organization
ZohoBooks_resume_recurring_bill
ZohoBooks_resume_recurring_expense
ZohoBooks_stop_recurring_bill
ZohoBooks_stop_recurring_expense
```

Remove these three tools from MCP entirely:

```text
ZohoBooks_approve_journal
ZohoBooks_mark_journal_published
ZohoBooks_update_transaction_lock
```

The final Controller selection should contain these 53 tools:

```text
ZohoBooks_apply_credit_note_to_invoice
ZohoBooks_apply_credits_to_bill
ZohoBooks_cancel_write_off_invoice
ZohoBooks_categorize_as_credit_note_refunds
ZohoBooks_categorize_as_vendor_credit_refunds
ZohoBooks_categorize_as_vendor_payment_refund
ZohoBooks_create_bank_reconciliation
ZohoBooks_create_bank_transaction
ZohoBooks_create_base_currency_adjustment
ZohoBooks_create_credit_note
ZohoBooks_create_credit_note_refund
ZohoBooks_create_customer_payment
ZohoBooks_create_customer_payment_refund
ZohoBooks_create_fixed_asset
ZohoBooks_create_journal
ZohoBooks_create_recurring_bill
ZohoBooks_create_recurring_expense
ZohoBooks_create_sales_receipt
ZohoBooks_create_vendor_credit
ZohoBooks_create_vendor_payment
ZohoBooks_exclude_bank_transaction
ZohoBooks_get_current_user
ZohoBooks_get_organization
ZohoBooks_mark_bill_void
ZohoBooks_mark_credit_note_void
ZohoBooks_mark_fixed_asset_active
ZohoBooks_mark_fixed_asset_draft
ZohoBooks_mark_invoice_void
ZohoBooks_mark_vendor_credit_void
ZohoBooks_refund_excess_vendor_payment
ZohoBooks_refund_vendor_credit
ZohoBooks_restore_bank_transaction
ZohoBooks_resume_recurring_bill
ZohoBooks_resume_recurring_expense
ZohoBooks_reverse_journal
ZohoBooks_sell_fixed_asset
ZohoBooks_stop_recurring_bill
ZohoBooks_stop_recurring_expense
ZohoBooks_submit_journal_for_approval
ZohoBooks_uncategorize_bank_transaction
ZohoBooks_unmatch_bank_transaction
ZohoBooks_update_bank_reconciliation
ZohoBooks_update_credit_note
ZohoBooks_update_customer_payment
ZohoBooks_update_fixed_asset
ZohoBooks_update_journal
ZohoBooks_update_recurring_bill
ZohoBooks_update_recurring_expense
ZohoBooks_update_sales_receipt
ZohoBooks_update_vendor_credit
ZohoBooks_update_vendor_payment
ZohoBooks_write_off_fixed_asset
ZohoBooks_write_off_invoice
```

The native `create_journal` operation can accept a published status. In supervised native use, the exact approved payload must state `draft`, and Controller must submit rather than approve its own journal. Before unattended use, replace the generic journal operation with a coded `create_draft_journal` control that hard-codes draft status and rejects publication fields.

Journal approval and publication remain human/qualified-reviewer actions in Zoho. Do not expose them through MCP unless a future independent approver identity, no-self-approval control, verified approval-state precondition, and separate approval policy are implemented.

Transaction-lock updates can potentially reopen a closed period. Keep that tool outside MCP. Controller may read lock state through Audit and must fail closed.

Recurring invoices and recurring journals are intentionally excluded from write authority. Add them only for a separately approved workflow with explicit ownership, lifecycle, duplicate, and stop controls.

## Required Configuration Admin Boundary

Configuration Admin should contain these 27 tools:

```text
ZohoBooks_create_bank_account
ZohoBooks_create_bank_account_rule
ZohoBooks_create_chart_of_account
ZohoBooks_create_contact
ZohoBooks_create_currency
ZohoBooks_create_custom_field
ZohoBooks_create_exchange_rate
ZohoBooks_create_item
ZohoBooks_create_location
ZohoBooks_create_opening_balance
ZohoBooks_create_tag
ZohoBooks_create_tax
ZohoBooks_get_current_user
ZohoBooks_get_organization
ZohoBooks_update_bank_account
ZohoBooks_update_bank_account_rule
ZohoBooks_update_chart_of_account
ZohoBooks_update_contact
ZohoBooks_update_currency
ZohoBooks_update_custom_field
ZohoBooks_update_exchange_rate
ZohoBooks_update_item
ZohoBooks_update_location
ZohoBooks_update_opening_balance
ZohoBooks_update_tag
ZohoBooks_update_tag_options
ZohoBooks_update_tax
```

Keep this server disconnected by default and connect it only for an approved configuration task. This is a safety split, not permission expansion. It prevents a routine correction session from also having standing authority to restructure the Chart of Accounts, taxes, currencies, bank accounts, dimensions, items, contacts, or opening balances.

## Organization, Identity, And Write Enforcement

`ZohoBooks_get_organization` and `ZohoBooks_get_current_user` are detective checks. A successful read does not bind the next write because Books operations accept `organization_id` per request.

Every coded write boundary must:

1. Store the one expected GH organization and Zoho data-center domain in secure server configuration.
2. Reject any caller-supplied organization or any request whose resolved organization differs.
3. Use a distinct OAuth principal for Audit, Bookkeeping, Controller, and Configuration Admin where Zoho supports the required role separation.
4. Prohibit the preparer/controller identity from approving or publishing its own journals.
5. Recheck organization, current user, record state, applications, reconciliation status, and period lock immediately before each write.
6. Abort if `last_modified_time`, an immutable snapshot hash, or any dependent state changed after approval.
7. Require a short-lived immutable plan ID/hash, single-use approval assertion, and idempotency key.
8. Serialize conflicting writes and persist the operation key, request hash, Zoho request identifier, returned record ID, before/after hashes, approver, and outcome in a durable write ledger.
9. Never blindly retry an ambiguous timeout; search/read back by the operation key and source identifiers first.
10. Read back through Audit and reconcile the affected ledger/subledger after success.

If the native Zoho-hosted server cannot enforce the fixed organization and payload fields, its writes remain supervised-only. Do not describe it as autonomous accountant-grade access.

## Correction Policy

| Problem | Approved correction path | Do not do |
|---|---|---|
| Bank line categorized incorrectly | Verify the source line, unmatch or uncategorize once, then apply the correct match or category and read back the result. | Do not exclude it merely to hide the error. |
| Genuine duplicate or out-of-entity feed line | Exclude only with source evidence, explicit approval, and a documented reason; restore if later found valid. | Do not call exclusion “archiving,” and do not use it to remove a real entity transaction. |
| Personal charge in an entity-owned bank/card account | Classify under the approved owner draw/distribution, shareholder receivable, due-from, or other reviewed account. | Do not exclude it simply because it is personal. |
| Editable draft/open expense, bill, invoice, credit, or journal is wrong | Update the exact record after checking links, reconciliations, period status, stale state, and duplicate risk. | Do not recreate it without first preventing duplicate posting. |
| Posted invoice, bill, credit, or payment is materially wrong | Use the module-supported void, credit, refund, or replacement path with explicit approval and readback. | Do not delete the record or detach downstream history. |
| Applied credit/payment must be detached | Prepare the exact exception for human action in Zoho unless a separately audited non-delete tool exists. | Do not add a generic DELETE/unapply tool. |
| Published journal is wrong | Reverse the original and create the corrected, balanced, evidence-backed entry. | Do not delete or overwrite the published journal. |
| Record is in a reconciled or locked period | Stop and prepare an adjusting-entry proposal for controller/CPA review. | Do not unlock or rewrite the prior period through MCP. |
| Opening balance or Chart of Accounts appears wrong | Produce an impact report and require qualified review through disconnected Configuration Admin. | Do not use an unsupported plug account or force a tie. |

`ZohoBooks_exclude_bank_transaction` does not archive a bank transaction and does not correct the general ledger. It is appropriate only for a true duplicate/feed artifact or a line imported from an account outside the entity boundary.

## Why Delete Tools Stay Excluded

No `ZohoBooks_*delete*` tool is present in the current three-server selection, and none should be added.

Deletion can be defensible only for a narrow administrative mistake such as an unposted duplicate draft with no applications, reconciliations, attachments, workflow dependencies, audit requirement, or closed-period effect. Even then:

1. Confirm the exact record and every downstream link.
2. Preserve the before-state and reason.
3. Prefer an update, void, reversal, or compensating entry.
4. If deletion remains necessary, have an authorized human perform that one deletion in Zoho.
5. Read back surrounding ledgers and subledgers afterward.

The absence of delete tools does not make the current Controller low-risk. Void, write-off, reversal, refund, unmatch, uncategorize, exclude, opening-balance, account, tax, and journal actions can materially alter the books.

## Production Acceptance Checklist

Do not begin cleanup writes until every required item passes:

- [ ] Every write-capable server includes the organization and current-user reads.
- [ ] Each boundary returns the one expected GH organization and intended OAuth identity.
- [ ] A fixed server-side organization/data-center allowlist rejects mismatched writes.
- [ ] Distinct preparer/controller roles are documented, and journal approval/publication remain outside MCP.
- [ ] The intended 166/17/53/27 tool counts and exact names match the live builder and Codex.
- [ ] `ZohoBooks_add_journal_attachment` appears in Bookkeeping.
- [ ] Configuration Admin is separated and normally disconnected.
- [ ] Journal approval, journal publication, transaction-lock update, delete, bulk-delete, raw-request, email-send, payment-initiation, credential, user, role, and permission tools are absent.
- [ ] The coded write layer enforces immutable plans, short expiry, stale-state aborts, idempotency, serialization, durable write logging, returned-ID persistence, and ambiguous-timeout readback.
- [ ] Generic invoice writes reject LF, INT, RF, recurring-rent, and automatic-credit workflows owned elsewhere.
- [ ] A closed historical month is reviewed read-only with complete pagination and report-to-ledger tie-outs.
- [ ] A dedicated test organization is used for write acceptance where available. Otherwise use a uniquely marked unposted draft and an exact authorized human cleanup path; do not reverse an unposted test draft.
- [ ] A sanitized journal attachment test succeeds without exposing a private tax or banking document.
- [ ] Locked-period and reconciled-transaction attempts fail closed.
- [ ] The Zoho MCP execution log and durable write ledger record the expected user, server, operation, record ID, and outcome.
- [ ] Existing deterministic automations remain the only owners of late fees, monthly interest, returned-payment fees, recurring rent, and automatic unused-credit workflows.

## Per-Call Posting Standard

Before every financial write, Codex must show:

1. Fixed organization, data center, OAuth identity, and period.
2. Source evidence and its sanitized identifier.
3. Current Zoho record, dependent applications, reconciliation state, and period-lock state.
4. Immutable before-state hash and `last_modified_time`, when available.
5. Proposed tool and exact parameters.
6. Debit/credit or subledger effect.
7. Property, tenant/vendor/customer, tax, location, tag, and account mapping as applicable.
8. Duplicate and automation-ownership checks.
9. Short-lived plan ID/hash, single-use approval, and idempotency key.
10. Expected post-write state.
11. Rollback, reversal, or compensating method.

Immediately before execution, reread the target and abort if anything material changed. After approval, execute only the validated call, persist the returned ID and outcome, read back through Audit, and reconcile the affected ledger/subledger totals. A broad instruction such as “clean up the books” is not approval for multiple production writes.

## Start Sequence

1. Apply the exact native tool additions, moves, and removals in this document.
2. Split Configuration Admin from Controller and keep it disconnected.
3. Implement the fixed-organization, draft-journal, plan, idempotency, stale-state, and write-ledger controls before automated posting.
4. Run organization/user acceptance checks without changing financial records.
5. Audit one account and one closed month at a time.
6. Build a proposed correction register with evidence, materiality, period, book/tax distinction, and recommended action.
7. Complete write acceptance in a test organization or with a uniquely marked unposted draft and human cleanup.
8. Obtain approval for a small first batch of current-period, reversible corrections.
9. Read back and reconcile every result before expanding scope.

Stop immediately if the organization is ambiguous, a tool differs from this inventory, pagination is incomplete, a source document is missing, a period is locked, a transaction is reconciled, the debit/credit effect is unclear, a snapshot changed, an operation outcome is ambiguous, or readback cannot prove the result.
