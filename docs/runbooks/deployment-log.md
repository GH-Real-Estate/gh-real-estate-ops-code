# Deployment Log

Record every production-relevant deployment or Zoho change.

## 2026-07-25 - Production CRM Second-Pass Layout and Intake Reconciliation

- System: Zoho CRM / GitHub
- Repo branch / change: live configuration through the approved CRM MCP servers; sanitized repository reconciliation on `agent/crm-second-pass-reconciliation`
- Scope: reversible active-layout cleanup for Contacts and Properties; two Rental Application intake count fields and two conditional layout rules; architecture and dashboard documentation
- Protected boundary: Leads, Property Assets (`Equipment`), Pets, and Vehicles (`Tenant_Vehicles`) were not modified; no CRM records or PII were read; no Browser control was used
- Result: seven redundant Contact fields and standard `Parent_Account` on Properties were removed from active layouts with `permanent: false`; no field or stored value was deleted. Properties sections were renamed to `Property Address & Legal Notice` and `Owner & Emergency Contact`.
- Rental Applications: `Requested_Pet_Count` and `Requested_Storage_Unit_Count` were created as Integer fields, placed beside their request controls, and independently read back. Active layout rules show and require each count only when its corresponding request checkbox is true.
- Verification: the affected Contacts, Properties, and Deals layouts, both created fields, and both layout rules were read back through `gh_zoho_crm_audit`; repository validation and tests are required before publication
- Intentionally unchanged: Deals Stage/Pipeline, Lease Status, Properties tenant subforms, Zillow/listing fields, `Total_Due_Before_Possession`, Contacts/Properties field definitions, dashboards, Contracts, Sign, Books, and all CRM records
- Rollback: add retired fields back to their former sections, restore the two prior section labels, deactivate the two conditional rules, remove the two count fields non-permanently from the Deals layout, and retire rather than delete them after dependency review
- Remaining blockers: pipeline CRUD and probability/category control; Lease Status order/default/required control; deployable idempotent calculation function; Formula-to-Contracts mapping proof; dashboard/report-component CRUD; Contracts/Sign canary
- Evidence: [`zoho-crm-second-pass-reconciliation-2026-07-25.md`](zoho-crm-second-pass-reconciliation-2026-07-25.md)

## 2026-07-24 — Production CRM Full Metadata Reconciliation

- System: Zoho CRM / Zoho Books review / GitHub
- Repo branch / change: live configuration through the approved CRM MCP servers; sanitized repository reconciliation on `agent/full-crm-reconciliation`
- Scope: all 72 returned CRM modules were enumerated (49 visible, 15 user-hidden, 8 system-hidden); field/layout metadata was attempted for all 51 modules flagged API-supported, with exact successes, rejections, and truncated layout responses recorded in the sanitized module ledgers; Leads, Property Assets (`Equipment`), Pets, and Vehicles (`Tenant_Vehicles`) were read-only and remained unchanged
- Result: 83 optional custom fields were created and read back across 12 modules; `GH_Lifecycle_Status` was created with Active, Inactive, and Archived and associated with Properties and Vendors; maintenance and task choices were extended additively; affected layouts were organized into governed sections
- Security: Vendors `Username` and `Password` were hidden for Administrator and Standard profiles and removed non-permanently from the active layout; no credential values or CRM records were read
- Lease financial state: `First_Full_Month_Base_Rent_Amount` now exists as Currency(2), but no total-due formula, snapshot-copy automation, Books reconciliation gate, Contracts mapping, contract request, or signature request was created
- Verification: all 83 fields, lookup targets, tooltips, optional state, profile permissions, final placements, global associations, additive choices, and credential containment were read back through the audit MCP; repository validators and tests are required before publication
- Rollback: remove new fields from active layouts and retire them only after dependency review; reverse section moves from the recorded pre-state; detach global associations before retiring the set; never delete fields or clear record data without a separate value/dependency audit
- Remaining blockers: Deals Stage/Pipeline actual-value corruption; Lease Number format; `Monthly_Rent` and `Prorated_Rent` semantics; complete initial-amount equation; Lease Status default/required controls; historical tooltip remediation; Books ownership; Contracts/Sign canary; RLA publication and attorney approval
- Evidence: [`zoho-crm-production-reconciliation-2026-07-24.md`](zoho-crm-production-reconciliation-2026-07-24.md)

## 2026-07-24 — Production CRM Lease-System Core Reconciled (Earlier Phase)

This earlier phase is retained as historical evidence. The full metadata
reconciliation entry above supersedes its field-gap and current-state summary.

- System: Zoho CRM / GitHub
- Repo branch / change: live configuration performed through the approved CRM connectors; sanitized repository reconciliation prepared on `agent/production-crm-lease-system`
- Files changed: production metadata/configuration for Rental Applications (`Deals`) and Leases (`Leases`); sanitized CRM/Contracts catalogs, crosswalks, RLA gate reasons, manual handoff, changelog, and this log
- Business rule changed? yes; the bounded production CRM schema, Lease layout, and Lease Status configuration now support a separate approved Lease record, but no record workflow or Contracts behavior was activated
- Dry-run completed? not applicable; writes were metadata/configuration-only and were gated by current-state inspection
- Smoke test completed? yes for configuration metadata; each created field and the final sections/placements/choices were read back. No record-data, contract-request, or signature smoke test was authorized or performed.
- Deployed by: Codex through the user-authorized `gh_zoho_crm_changes` connector, with readback through `gh_zoho_crm_audit`
- Result: 15 Rental Application fields and 33 Lease fields created/read back; seven Lease fields reused; eight Lease sections created; 40 Lease fields placed; Lease Status history enabled and target choices/colors added without removing legacy values. No CRM record or PII was read or modified.
- Rollback plan: after dependency review, remove created fields from active layouts and retire rather than delete them; recover the seven reused fields' exact pre-change placements from an authorized Zoho audit/export before any section rollback because this sanitized repository does not retain that before-state; deactivate only newly added Lease Status values, restore `Ready For Contract` to `#168AEF` and `Renewal Pending` to `#F5C72F`, preserve legacy `Draft Lease Data` at `#AF38FA`, and restore prior history setting where safe; revert repository documentation separately
- Notes: Deals Stage/Amount, ambiguous rent/proration fields, Lease Number, First Full Month Base Rent, required/default/readiness rules, exact supplied-tooltip remediation, Lease Status ordering, Create Lease automation, and exact section-placement rollback remain blocked/unsupported. Lease Status target/legacy values interleave and new `Draft` is last; default remains null and the field remains optional. No `zohocontracts__Contracts`, extension, button, related list, field mapping, Party configuration, signer route, template, contract request, signature request, or communication changed. The Residential Lease Agreement remains Draft only, unpublished, execution-blocked, attorney-review-required, and unsent with all 29 gates open. See [`zoho-crm-lease-system-reconciliation.md`](zoho-crm-lease-system-reconciliation.md).

## 2026-07-24 — Zillow Lifecycle and Listing Publication Documentation

- System: GitHub / Zoho CRM / Zoho Catalyst / Zillow
- Repo branch / commit: `agent/document-zillow-listing-publication` / pending merge
- Files changed: CRM overview, Zillow-to-CRM-to-Contracts lifecycle map, new outbound Zillow listing-publication architecture, changelog, and this log
- Business rule changed? no live behavior; the governed design now distinguishes the operating inbound Lead webhook from a possible future outbound feed and places Contact, Application, Lease, and Contract creation at their correct lifecycle gates
- Dry-run completed? documentation and source inspection only; current repository behavior and official Zillow/Zoho guidance were reconciled
- Smoke test completed? repository and GitHub checks required; no live CRM, Catalyst, Zillow, or Contracts smoke test was authorized
- Deployed by: ChatGPT / GitHub documentation update
- Result: documentation only; no CRM record/field, Catalyst function, Zillow feed, credential, or live listing was created or changed
- Rollback plan: revert the documentation merge; no live-system rollback is required
- Notes: continue manual Zillow Rental Manager publishing for the fourplex. Do not implement a feed until Zillow confirms eligibility, schema, property type, and test onboarding in writing.

## 2026-07-24 — Zoho MCP Production Servers Configured

- System: Zoho CRM / Zoho Books / Codex
- Repo branch / commit: live setup performed outside the repository; sanitized documentation added through `agent/document-configured-zoho-mcp-servers`
- Files changed: live Zoho-hosted MCP server selections and local Codex MCP configuration; no server URL, credential, identifier, or raw response recorded
- Business rule changed? no
- Dry-run completed? not applicable; Gabriel explicitly selected the GH Real Estate production CRM organization
- Smoke test completed? partial; Audit confirmed GH Real Estate and `type: production`, and its module call succeeded but was transport-truncated with an advertised projection returning `PATTERN_NOT_MATCHED`; Changes production target was confirmed without testing a mutation; Books organization acceptance is not evidenced
- Deployed by: Gabriel
- Result: `gh_zoho_crm_audit` exposes 18 CRM metadata reads, `gh_zoho_crm_changes` exposes 27 mixed configuration/record tools, and `gh_zoho_books_review` exposes 12 Books reads
- Rollback plan: disable the affected Codex server entry, remove or narrow its Zoho tool selection, and revoke its authorization if compromise or unintended access is suspected
- Notes: the Changes server includes 11 record/COQL tools beyond its original 16 organization/configuration tools. This entry documents the reported live capability surface; it does not prove that any CRM mutation or Books data read succeeded.

## 2026-07-17 — Partial-Payment Preservation Source Correction

- System: GitHub / Zoho Books / Zoho Payments / Zoho Catalyst
- Repo branch / commit: `agent/preserve-zoho-partial-payments` / PR #67
- Files changed: LF and monthly-interest Deluge functions; returned-payment webhook and source-contract test; Books settings; install/test checklists
- Business rule changed? no; new fee invoices now inherit or deterministically resolve the existing top-level `allow_partial_payments` setting, while source-ledger updates leave payment behavior untouched
- Dry-run completed? not applicable for source-control update
- Smoke test completed? repository, authority-refresh, and security checks passed on PR #67; live Zoho smoke test required after deployment
- Deployed by: ChatGPT / GitHub update
- Result: source corrected; no existing recurring profile, generated invoice, payment, or live Zoho function changed
- Rollback plan: revert the merge commit; if deployed later, restore the prior saved function/webhook versions and rerun the payment smoke tests
- Notes: verify the actual generated rent invoice under Sales > Invoices. A checked recurring-profile setting does not retroactively prove that an already-generated invoice allows partial payment.

## 2026-07-14 — CI Failure Response Queue And Publisher Verification

- System: GitHub / Codex
- Repo branch / commit: `codex/ci-response-queue-smoke` / PR #53; queue/publisher fix merged in PR #52
- Files changed: `docs/setup/github-settings-checklist.md`, `docs/runbooks/ci-failure-response.md`, `docs/runbooks/deployment-log.md`
- Business rule changed? no; repository incident-response controls changed without modifying legal, accounting, payment, lease, tenant, or live-system rules
- Dry-run completed? not applicable
- Smoke test completed? yes; bot-created issue #54 preserved the distinct push/PR failures in one record, then closed from green recovery run `29361402852`; PR recovery run `29361405235` also passed
- Deployed by: Codex / GitHub Actions
- Result: `queue: max` active, publisher identity enforced, one bounded incident, one newer-failure comment, one recovery comment, no duplicate/reopened issue, no raw logs/PII/secrets, and no sentinel in the final diff
- Rollback plan: revert the documentation merge if the record is incorrect; revert PR #52 through a normal reviewed PR if the queue or publisher controls must be rolled back
- Notes: Historical pre-change verification only. PR #55 disables the automatic `workflow_run` response path to reduce Actions usage; normal GitHub notifications become the default alert, and the external `GH Repo CI Auto-Repair` Codex task must be paused or disabled separately. Repository auto-merge remains off and governed/high-risk changes remain human-gated.

## 2026-07-06 - Monthly Interest Lease Accrual Alignment

- System: GitHub / Zoho Books
- Repo branch / commit: `lease-final-alignment` / pending merge
- Files changed: `src/zoho-books/automations/monthly-interest-billing/Monthly_Interest_Billing.deluge`, monthly interest docs/tests, `docs/business-rules/lease-automation-rules.md`, `src/zoho-books/field-maps/books-automation-settings.md`, `docs/runbooks/deployment-log.md`
- Business rule changed? yes; monthly interest eligibility remains day 31, but once eligible, accrual now starts from the original rent due date to match Lease Section 3.6
- Dry-run completed? not yet; required in Zoho Books before live posting
- Smoke test completed? GitHub checks required; live Zoho Books smoke test still required
- Deployed by: ChatGPT / GitHub update
- Result: source copy and docs aligned to the final lease-template rule
- Rollback plan: revert the merge commit; if already deployed in Zoho Books, reinstall the prior saved schedule body and rerun smoke tests
- Notes: this entry does not prove the revised function has been pasted into Zoho Books or saved in the Zoho editor.

## 2026-07-06 - Lease-Aligned RF Fee And Monthly Interest Repo Structure

- System: GitHub / Zoho Books / Zoho Payments / Zoho Catalyst
- Repo branch / commit: `chatgpt-rf-lease-and-interest-structure` / pending merge
- Files changed: `src/zoho-books/automations/monthly-interest-billing/`, `src/zoho-books/automations/late-fee-guard/`, `src/zoho-payments/webhooks/returned-payment-fee/`, `src/zoho-books/README.md`, `README.md`, `docs/business-rules/lease-automation-rules.md`, `src/zoho-books/field-maps/books-automation-settings.md`, `docs/runbooks/deployment-log.md`
- Business rule changed? no live lease rule changed; repo documentation now verifies the uploaded lease template says returned-payment fee is `$30.00 or the maximum amount allowed by law, whichever is less`
- Dry-run completed? not yet; required in Zoho Books/Catalyst before live posting
- Smoke test completed? GitHub checks required; live Zoho/Catalyst smoke tests still required
- Deployed by: ChatGPT / GitHub update
- Result: monthly interest source moved to its own Zoho Books automation folder; RF webhook docs/tests aligned to the $30.00 lease value
- Rollback plan: revert the merge commit; if already deployed in Zoho/Catalyst, restore prior runtime source/config and rerun smoke tests
- Notes: returned-payment / NSF RF invoices remain owned by the Zoho Payments returned-payment webhook. Do not add a separate Books RF schedule unless a later reconciliation gap is proven.

## 2026-07-06 - Split Late Fee Guard And Monthly Interest Source

- System: GitHub / Zoho Books
- Repo branch / commit: `codex/split-late-fee-monthly-interest` / pending merge
- Files changed: `src/zoho-books/automations/late-fee-guard/`, `src/zoho-books/field-maps/books-automation-settings.md`, `src/zoho-books/README.md`, `README.md`, `docs/runbooks/deployment-log.md`
- Business rule changed? source-control deployment model changed from combined late-fee/interest function back to separate daily late-fee and monthly interest scheduled functions
- Dry-run completed? not yet; required in Zoho Books before live posting
- Smoke test completed? not yet; required in Zoho Books after installing both scheduled functions
- Deployed by: ChatGPT / Codex-style repo update
- Result: source copy and operator docs updated; this entry does not prove the functions are installed in Zoho Books
- Rollback plan: revert the merge commit or reinstall the prior source copy if Zoho deployment has not yet been updated
- Notes: returned-payment / NSF fees remain owned by the Zoho Payments returned-payment webhook. Add a separate Books reconciliation schedule only if manual paper checks or missed webhook events need coverage after source fields are verified.

## Template

```md
## YYYY-MM-DD — Change Title

- System: Zoho Books / Zoho CRM / Zoho Creator / Zoho Catalyst / GitHub / Other
- Repo branch / commit:
- Files changed:
- Business rule changed? yes/no
- Dry-run completed? yes/no/not applicable
- Smoke test completed? yes/no
- Deployed by:
- Result:
- Rollback plan:
- Notes:
```

## 2026-07-02 — Codex Default Merge Workflow Documented

- System: GitHub / Codex
- Repo branch / commit: `codex/update-agent-merge-defaults` / pending merge
- Files changed: `AGENTS.md`, `README.md`, `docs/setup/github-settings-checklist.md`, `docs/runbooks/deployment-log.md`
- Business rule changed? no business automation rule changed
- Dry-run completed? not applicable
- Smoke test completed? not applicable
- Deployed by: ChatGPT / Codex-style repo update
- Result: Codex/ChatGPT default behavior now documents branch, PR, check-fix, merge-to-main, final verification, and branch cleanup expectations for repo edits
- Rollback plan: revert the merge commit or restore the previous repo workflow wording
- Notes: this is a source-control operating policy. It does not deploy code into Zoho/Catalyst.

## 2026-07-02 — Apply Unused Credits Hardening Source Updated

- System: GitHub / Zoho Books
- Repo branch / commit: `main` / PR #7 merged as `b9668f7f1c746261ebc073e1f125d16bec75b04d`
- Files changed: `src/zoho-books/automations/apply-unused-credits/`, `src/zoho-books/field-maps/books-automation-settings.md`, `docs/runbooks/smoke-test-checklist.md`, `docs/runbooks/deployment-log.md`
- Business rule changed? source-control default behavior changed to require invoice eligibility and fail closed on blank branch IDs
- Dry-run completed? not applicable for source-control update
- Smoke test completed? not yet; required before Zoho Books deployment
- Deployed by: ChatGPT / Codex-style repo update
- Result: hardened source copy and operational documentation added to GitHub
- Rollback plan: revert the merge commit or disable/remove the Zoho Books workflow custom function if installed later
- Notes: this entry does not prove the hardened function is installed in Zoho Books. After live installation, add a second entry with the deployed commit and smoke-test result.

## 2026-07-02 — Apply Unused Credits Source Added

- System: GitHub / Zoho Books
- Repo branch / commit: `main` / PR #6 merged as `2dbe4ba23110ef6c9dc5f473e4ae7af64cf461bb`
- Files changed: `src/zoho-books/automations/apply-unused-credits/`, `src/zoho-books/README.md`, `src/zoho-books/field-maps/books-automation-settings.md`, `docs/runbooks/smoke-test-checklist.md`, `README.md`
- Business rule changed? no live rule changed by this repo update
- Dry-run completed? not applicable for source-control import
- Smoke test completed? not yet; required before Zoho Books deployment
- Deployed by: ChatGPT / Codex-style repo update
- Result: source copy, install checklist, test cases, and settings documentation added to GitHub
- Rollback plan: revert the merge commit or remove the Zoho Books workflow custom function if installed later
- Notes: this entry does not prove the function is installed in Zoho Books. After live installation, add a second entry with the deployed commit and smoke-test result.

## 2026-07-01 — Starter Repo Created

- System: GitHub
- Repo branch / commit: `main` / initial
- Files changed: starter structure plus current automation code
- Business rule changed? no
- Dry-run completed? not applicable
- Smoke test completed? not applicable
- Deployed by: Gabriel
- Result: repository created under `GH-Real-Estate/gh-real-estate-ops-code`
- Rollback plan: revert initial commit or revert individual files if needed
- Notes: this log records GitHub repository setup only. It does not prove the committed code is currently installed in Zoho/Catalyst.

## 2026-07-01 — Repo Cleanup Merged

- System: GitHub
- Repo branch / commit: `main` / PR #1 merged
- Files changed: README, Zoho Books settings, lease automation rules, deployment log, `.gitignore`, `.env.example`, returned-payment webhook package manifest, removed unused Zoho Contracts templates placeholder
- Business rule changed? no
- Dry-run completed? not applicable
- Smoke test completed? not applicable
- Deployed by: ChatGPT / Codex-style repo cleanup
- Result: merged into `main`
- Rollback plan: revert PR #1 or revert individual cleanup commit if needed
- Notes: this cleanup documents code-observed settings and removes one unnecessary placeholder folder. It does not deploy anything into Zoho/Catalyst.

## 2026-07-01 — System-Based Repo Structure Merged

- System: GitHub
- Repo branch / commit: `main` / PR #2 merged
- Files changed: moved runtime-owned code and docs under `src/<system>/`, moved decision log to `docs/adr/`, moved samples under source-system folders, restored repo hygiene docs/tools, restored webhook package metadata/lockfile, added sanitized webhook operations/security docs
- Business rule changed? no
- Dry-run completed? not applicable
- Smoke test completed? not applicable
- Deployed by: ChatGPT / Codex-style repo structure cleanup
- Result: merged into `main`
- Rollback plan: revert PR #2 or revert individual files if needed
- Notes: no production automation logic was changed. This is a repository organization change only. Returned-payment webhook operational docs were sanitized to avoid storing live endpoint/payment/invoice identifiers.
