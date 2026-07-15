# Returned Payment Fee Webhook

Node.js webhook gateway for Zoho Payments returned/failed payment events. The webhook verifies inbound events, performs replay protection, checks Zoho as source of truth, and creates returned-payment fee records in Zoho Books when approved.

## Runtime

```text
Event source: Zoho Payments
Execution runtime: Zoho Catalyst Advanced I/O / Node.js 24
Accounting write target: Zoho Books
Main file: src/index.js
Package file: package.json
```

## Why This Lives Under `src/zoho-payments/`

The trigger event originates from Zoho Payments. The webhook then runs in Zoho Catalyst and writes to Zoho Books. That makes this a Zoho Payments integration with a Catalyst runtime and a Zoho Books dependency, not a generic top-level automation and not a Zoho Books scheduled function.

Use `returned-payment-fee` for the folder name even when the business phrase is "returned check fee." The code reacts to payment failure events from Zoho Payments, which can cover ACH/check-style returns and other failed payment methods.

## Related Files

| File | Purpose |
|---|---|
| `src/index.js` | Webhook source code |
| `package.json` | Node package/runtime manifest |
| `package-lock.json` | Locked dependency versions |
| `catalyst-config.json` | Catalyst deployment metadata |
| `install-checklist.md` | Install and verification checklist |
| `test-cases.md` | Sanitized manual/runtime test plan |
| `test/source-contract.test.js` | Automated source-contract checks for safe defaults and ownership rules |
| `docs/environment-variables.md` | Runtime configuration guide |
| `docs/security-model.md` | Webhook security model |
| `docs/operations-runbook.md` | Live/dry-run/recovery runbook |
| `docs/file-manifest.md` | Function package contents |
| `docs/structure-and-ownership.md` | Why this package lives under Zoho Payments even though it runs in Catalyst and writes to Books |
| `docs/changelog.md` | Function-level changelog |
| `../../../zoho-books/field-maps/books-automation-settings.md` | Related Books item/custom-field settings |
| `../../../../docs/business-rules/lease-automation-rules.md` | Lease fee rule verification |
| `../../../../samples/zoho-payments/returned-payment.sample.json` | Sanitized sample event |

## Local / CI Checks

```text
npm run ci
```

This runs the syntax check and the automated source-contract tests. GitHub Actions also runs this package check and the repository safety scanner on pull requests.

## Safety Requirements

- Must verify webhook signature before live use.
- Must use replay protection.
- Must default to dry-run unless explicitly approved for live mode.
- Must not log tenant PII, bank details, or secrets.
- Returned-payment fee amount must be verified against the final lease and runtime environment.
