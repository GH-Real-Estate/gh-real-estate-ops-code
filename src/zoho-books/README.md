# Zoho Books

Zoho Books is the financial source of truth for GH Real Estate.

Use this area for code and technical documentation that is owned by, installed in, or directly dependent on Zoho Books.

## Contents

```text
automations/
  apply-unused-credits/
    ApplyUnusedCredits.deluge
    README.md
    install-checklist.md
    test-cases.md
  late-fee-guard/
    Late_Fee_Guard.deluge
    README.md
    install-checklist.md
    test-cases.md
  monthly-interest-billing/
    Monthly_Interest_Billing.deluge
    README.md
    install-checklist.md
    test-cases.md

field-maps/
  books-automation-settings.md
```

## Automations

| Automation | Runtime | Purpose |
|---|---|---|
| Apply Unused Credits | Zoho Books Invoice Created workflow custom function | Applies available matching-branch customer credits to a newly-created invoice |
| Late Fee Guard | Zoho Books scheduled function | Creates lease-aligned D5/D10 late-fee invoices only |
| Monthly Interest Billing | Zoho Books scheduled function | Creates monthly simple-interest invoices for delinquent rent balances only |

## Ownership Boundaries

| Charge / Action | Owner |
|---|---|
| Late fees | `automations/late-fee-guard/Late_Fee_Guard.deluge` |
| Monthly delinquent-rent interest | `automations/monthly-interest-billing/Monthly_Interest_Billing.deluge` |
| Returned-payment / NSF RF invoices | `src/zoho-payments/webhooks/returned-payment-fee/src/index.js` |

Returned-payment / NSF invoices are not a Zoho Books schedule by default because the trigger is a payment failure event from Zoho Payments. The Zoho Payments webhook runs in Zoho Catalyst and writes the resulting RF invoice to Zoho Books.

## Rules

- Do not store rent ledgers, ACH records, bank details, or real payment exports here.
- Keep only code, field maps, sanitized test data, and setup notes.
- Any production-relevant change must be recorded in `docs/runbooks/deployment-log.md`.
