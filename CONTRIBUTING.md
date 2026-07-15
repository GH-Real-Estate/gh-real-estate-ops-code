# Contributing and Change Process

This public repository contains operational business code. Unsolicited implementation pull requests are not accepted unless a maintainer approves the work in advance. Sanitized bug reports and private vulnerability reports are welcome.

## Safe contribution boundary

Before opening a pull request:

- Use synthetic data only.
- Do not include credentials, operational IDs, tenant/customer data, private documents, production payloads, raw logs, or licensed non-redistributable material.
- Keep the change focused; do not mix unrelated refactors.
- Preserve fail-closed defaults for financial, tenant, lease, legal, tax, and accounting behavior.
- Pin every external GitHub Action to a full commit SHA and justify any write permission.

Security findings must use [private vulnerability reporting](https://github.com/GH-Real-Estate/gh-real-estate-ops-code/security/advisories/new), never a public issue.

## Controlled workflow

```text
main = stable/current reference
branches = proposed changes
pull requests = review and automated-check checkpoint
manual deployment = controlled production change
```

Use short, descriptive branch names such as `zoho-books/late-fee-duplicate-prevention` or `security/harden-workflow-permissions`. Write commit messages that state the operational outcome.

Open a pull request for every material change. The PR must document purpose and risk, exact tests, deployment status, rollback steps, and any financial, tenant, lease, legal, tax, accounting, security, or permission impact.

Merging to `main` does not mean deployed. Production installation or configuration occurs separately in Zoho/Catalyst and must be recorded in `docs/runbooks/deployment-log.md`.
