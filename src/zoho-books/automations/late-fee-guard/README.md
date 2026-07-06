# Late Fee Guard

Zoho Books scheduled Deluge automation for GH Real Estate rent late fees only.

## Runtime

```text
System: Zoho Books
Language: Deluge
Function type: Scheduled function
Deployable file: Late_Fee_Guard.deluge
```

## Why This Lives Under `src/zoho-books/automations/late-fee-guard/`

This automation is installed in Zoho Books and creates or updates Zoho Books late-fee invoices and source-invoice custom fields. It owns late-fee milestones only.

Monthly interest used to be stored beside this file, but it is now stored in its own automation folder because it has a different schedule, idempotency model, and business rule.

## Related Files

| File | Purpose |
|---|---|
| `Late_Fee_Guard.deluge` | Production Deluge script source copy for D5/D10 late-fee milestones only |
| `install-checklist.md` | Install and verification checklist for the late-fee schedule |
| `test-cases.md` | Sanitized late-fee test plan |
| `../monthly-interest-billing/Monthly_Interest_Billing.deluge` | Separate monthly scheduled function for delinquent-rent interest |
| `../../field-maps/books-automation-settings.md` | Zoho Books item/template/custom-field settings |
| `../../../../docs/business-rules/lease-automation-rules.md` | Lease rules the code must match |
| `../../../../docs/runbooks/deployment-log.md` | Deployment/change log |

## Late-Fee Policy

- Keep D5 and D10 milestone late-fee logic in `Late_Fee_Guard.deluge`.
- Do not apply late fees to prior late-fee invoices, returned-fee invoices, or interest invoices.
- Source invoices must be intentionally marked as rent with `cf_is_rent_invoice`.
- Pending ACH/online payment suppression remains part of the late-fee guard.
- Keep `enableInterestOnDelinquentRent = false`; monthly interest is owned by `../monthly-interest-billing/Monthly_Interest_Billing.deluge`.

## Returned-Payment / NSF Fees

Returned-payment and NSF fees should not live inside the late-fee guard. The existing Zoho Payments returned-payment webhook under `src/zoho-payments/webhooks/returned-payment-fee/` owns event-driven ACH/card/payment-return fee handling. Add a separate Zoho Books reconciliation schedule only if manual paper checks or missed payment events need coverage after the source-of-truth fields are verified.

## Safety Requirements

- Must be idempotent.
- Must not create duplicate late-fee invoices.
- Must only process invoices intentionally marked as rent.
- Must suppress late-fee creation while ACH/online payments are still pending or processing.
- Must not log tenant PII.
- Must match the verified final lease before live use.
