# Deployment Log

Record every production-relevant deployment or Zoho change.

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
