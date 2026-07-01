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
