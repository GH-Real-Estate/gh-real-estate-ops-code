# File Manifest

## Function Package Files

The returned-payment webhook package lives at:

```text
src/zoho-payments/webhooks/returned-payment-fee/
```

This is the deployable Zoho Catalyst package for a Zoho Payments event source. It writes approved returned-fee invoices to Zoho Books, but the package is organized under Zoho Payments because the payment failure event starts the workflow.

| File | Purpose |
|---|---|
| `src/index.js` | Main runtime code. Handles webhook verification, OAuth2 API calls, idempotency, and invoice creation. |
| `package.json` | Declares Node dependencies, package metadata, and local/CI scripts. |
| `package-lock.json` | Locks dependency versions for reproducible deployments. |
| `catalyst-config.json` | Catalyst deployment metadata. Must not contain real environment variables or secrets. |
| `README.md` | High-level explanation of the function. |
| `test/source-contract.test.js` | Automated checks for safe defaults, replay/lock controls, source-of-truth verification, and ownership documentation. |
| `docs/environment-variables.md` | Explains required environment variables and safe live values. |
| `docs/security-model.md` | Explains the security architecture and why HMAC + OAuth2 are both used. |
| `docs/operations-runbook.md` | Practical operating procedures for dry runs, live mode, duplicate handling, and troubleshooting. |
| `docs/structure-and-ownership.md` | Documents why this returned-fee package belongs under Zoho Payments even though it runs in Catalyst and writes to Books. |
| `docs/file-manifest.md` | This file. |
| `docs/changelog.md` | Human-readable record of major function changes. |
| `install-checklist.md` | Installation checklist. |
| `test-cases.md` | Sanitized manual/runtime test plan. |

## Do Not Commit

Do not commit:

```text
node_modules/
.env
real webhook signing keys
OAuth secrets
raw webhook logs
real payment IDs
real invoice IDs
tenant names/emails/phones
```

## Rule

Production packages should contain runtime files plus clear documentation and tests. They should not contain patch notes, temporary migration files, token examples using real IDs, or old setup debris.
