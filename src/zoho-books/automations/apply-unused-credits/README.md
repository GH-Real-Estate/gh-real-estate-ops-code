# Apply Unused Credits

Zoho Books event-based Deluge automation that applies available unused customer credits to a newly-created invoice.

## Runtime

```text
System: Zoho Books
Language: Deluge
Function type: Workflow custom function
Module: Invoice
Trigger: Invoice created
Connection link name: zbooks
Main file: ApplyUnusedCredits.deluge
```

## Why This Lives Under `src/zoho-books/`

This automation belongs here because Zoho Books owns the workflow trigger, invoice lookup, contact unused-credit lookup, and invoice credit application endpoint. It may react to payment and accounting state, but it is not a Zoho Payments webhook or Catalyst runtime.

## Business Rule

- Applies credits only when the invoice has an open balance.
- Reads unused credits from the Zoho Books contact receivables endpoint.
- Includes unused retainer payments.
- Applies only credits whose `branch_id` matches the invoice `branch_id`.
- Applies customer payments and retainer payments through `invoice_payments`.
- Applies credit notes through `apply_creditnotes`.
- Does not create new invoices, fees, payments, or credit notes.

## Related Files

| File | Purpose |
|---|---|
| `ApplyUnusedCredits.deluge` | Production Deluge script source copy |
| `install-checklist.md` | Zoho Books install and verification checklist |
| `test-cases.md` | Sanitized test plan |
| `../../field-maps/books-automation-settings.md` | Shared Zoho Books automation settings |
| `../../../../docs/runbooks/deployment-log.md` | Deployment/change log |
| `../../../../docs/runbooks/smoke-test-checklist.md` | Cross-system smoke test checklist |

## Safety Requirements

- Test with sanitized or controlled Zoho Books records before live use.
- Confirm the `zbooks` connection has the required Books permissions.
- Confirm branch matching behavior if multi-branch accounting is enabled.
- Confirm the workflow is scoped to Invoice Created, not Estimate Created.
- Do not log tenant names, emails, phone numbers, bank data, or raw API payloads.
- Do not enable this during historical invoice imports unless automatic credit application is intended.
