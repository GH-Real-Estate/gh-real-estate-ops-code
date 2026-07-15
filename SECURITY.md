# Security Policy

## Supported code

Only the current `main` branch is supported. Merging code does not deploy it to Zoho, Catalyst, or another production system.

## Report vulnerabilities privately

Do not open a public issue, pull request, discussion, or commit containing a vulnerability, credential, exploit detail, tenant/customer data, or production payload.

Use [GitHub private vulnerability reporting](https://github.com/GH-Real-Estate/gh-real-estate-ops-code/security/advisories/new). Include the smallest sanitized reproduction, affected path, impact, and suggested remediation. If that form is unavailable, contact the repository owner through an established private business channel without posting details publicly.

GH Real Estate will acknowledge a credible report as promptly as practical, investigate privately, rotate exposed credentials immediately when indicated, and coordinate disclosure after a fix. No response-time or bounty commitment is made.

## Public repository boundary

Allowed:

- Original code and documentation.
- Synthetic or irreversibly sanitized examples.
- Public government authority material and source locators.
- GH-authored legal/accounting analysis that does not reproduce restricted licensed content.
- Public aliases for operational identifiers.

Never commit:

- Passwords, API keys, OAuth secrets/tokens, refresh tokens, private keys, webhook secrets, session cookies, or credentialed URLs.
- Real tenant, applicant, customer, employee, or vendor PII.
- Signed leases, applications, pay stubs, identity/immigration documents, bank data, payment records, or private photos.
- Raw production logs, payloads, exports, backups, database files, configuration files, or operational account IDs.
- FASB Codification text, screenshots, print exports, or other non-redistributable licensed material.

Every commit and fork must be assumed permanently public. Deleting a file from the current branch does not remove it from history.

## Incident response

If a credential is committed:

1. Revoke or rotate it in the source system immediately; repository cleanup alone is insufficient.
2. Disable affected integrations while exposure is assessed.
3. Remove it from the current tree and evaluate Git history, Actions logs, artifacts, forks, and caches.
4. Add a sanitized entry to `docs/security/security-incidents.md`.
5. Add a preventive scanner, configuration, or review control.

If PII or a private document is committed, stop further distribution, remove access where possible, preserve a sanitized incident record, assess notification obligations with qualified counsel, and return the data to its approved system of record.

## Security controls

Repository workflows use immutable Action commit SHAs, least-privilege permissions, GitHub-hosted runners, CodeQL, dependency review, fail-closed file controls, and workflow-policy tests. Repository settings must also enforce a protected `main` ruleset, read-only default workflow tokens, secret scanning with push protection, private vulnerability reporting, and outside-contributor approval.
