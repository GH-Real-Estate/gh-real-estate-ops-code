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

## 2026-07-01 — Repo Cleanup Branch

- System: GitHub
- Repo branch / commit: `cleanup/minimal-setup-2026-07-01` / pending merge
- Files changed: README, Zoho Books settings, lease automation rules, deployment log, removed unused Zoho Contracts templates placeholder
- Business rule changed? no
- Dry-run completed? not applicable
- Smoke test completed? not applicable
- Deployed by: ChatGPT / Codex-style repo cleanup
- Result: pending review and merge
- Rollback plan: close PR without merging, or revert cleanup commit after merge
- Notes: this cleanup documents code-observed settings and removes one unnecessary placeholder folder. It does not deploy anything into Zoho/Catalyst.
