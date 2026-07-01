# Returned Payment Fee Webhook

Node.js webhook gateway for Zoho Payments returned/failed payment events. The webhook verifies inbound events, performs replay protection, checks Zoho as source of truth, and creates returned-payment fee records in Zoho Books when approved.

## Runtime

```text
Event source: Zoho Payments
Execution runtime: Zoho Catalyst Advanced I/O / Node.js 18
Main file: src/index.js
Package file: package.json
```

## Why This Lives Under `src/zoho-payments/`

The trigger event originates from Zoho Payments. The webhook then writes to Zoho Books. That makes this a Zoho Payments integration with a Zoho Books dependency, not a generic top-level automation.

## Related Files

| File | Purpose |
|---|---|
| `src/index.js` | Webhook source code |
| `package.json` | Node package/runtime manifest |
| `install-checklist.md` | Install and verification checklist |
| `test-cases.md` | Sanitized test plan |
| `../../../zoho-books/field-maps/books-automation-settings.md` | Related Books item/custom-field settings |
| `../../../../docs/business-rules/lease-automation-rules.md` | Lease fee rule verification |
| `../../../../samples/zoho-payments/returned-payment.sample.json` | Sanitized sample event |

## Safety Requirements

- Must verify webhook signature before live use.
- Must use replay protection.
- Must default to dry-run unless explicitly approved for live mode.
- Must not log tenant PII, bank details, or secrets.
- Returned-payment fee amount must be verified against the final lease and runtime environment.
