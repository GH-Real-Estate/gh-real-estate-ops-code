# Deployment Log

Record every production-relevant deployment or Zoho change.

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
