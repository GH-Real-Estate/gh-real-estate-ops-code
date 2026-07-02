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
- Applies credits only to invoices marked eligible by `cf_is_rent_invoice` unless `requireRentInvoiceFlag` is intentionally disabled in code.
- Applies only credits whose `branch_id` matches the invoice `branch_id`.
- Fails closed on blank branch IDs by default; set `allowEmptyBranchMatch=true` only after single-branch behavior is verified in Zoho Books.
- Applies credit notes first, then customer payments, then retainer payments.
- Re-checks invoice balance immediately before applying credits to reduce duplicate-run and concurrent-workflow risk.
- Does not create new invoices, fees, payments, or credit notes.

## Hardening Notes

- Zoho Books API responses are checked for non-zero `code` values before the function continues.
- The function stops on missing invoice context, missing response objects, failed API requests, or unparseable balances.
- Malformed credit entries are skipped with sanitized summary counts.
- The final credit application POST is treated as failed unless Zoho Books returns success.
- Logs intentionally avoid tenant names, emails, bank data, raw payloads, and secrets.

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
- Confirm `cf_is_rent_invoice` exists and is populated for invoices that should receive automatic credit application.
- Confirm branch matching behavior if multi-branch accounting is enabled.
- Confirm the workflow is scoped to Invoice Created, not Estimate Created.
- Do not enable this during historical invoice imports unless automatic credit application is intended.
