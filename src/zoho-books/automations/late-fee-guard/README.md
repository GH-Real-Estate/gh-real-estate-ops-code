# Late Fee Guard

Zoho Books scheduled Deluge automation for GH Real Estate rent late-fee and delinquent-rent interest handling.

## Runtime

```text
System: Zoho Books
Language: Deluge
Function type: Scheduled function
Main file: Late_Fee_Guard.deluge
```

## Why This Lives Under `src/zoho-books/`

This automation belongs here because it is installed in Zoho Books and creates/updates Zoho Books invoices and custom fields. The old generic `automations/` location made the repo feel scattered because it grouped code by workflow label instead of by the system that owns the runtime.

## Related Files

| File | Purpose |
|---|---|
| `Late_Fee_Guard.deluge` | Production Deluge script source copy |
| `install-checklist.md` | Install and verification checklist |
| `test-cases.md` | Sanitized test plan |
| `../../field-maps/books-automation-settings.md` | Zoho Books item/template/custom-field settings |
| `../../../../docs/business-rules/lease-automation-rules.md` | Lease rules the code must match |
| `../../../../docs/runbooks/deployment-log.md` | Deployment/change log |

## Safety Requirements

- Must be idempotent.
- Must not create duplicate fees.
- Must only process rent invoices intentionally marked as rent.
- Must suppress fee creation while ACH/online payments are still pending or processing.
- Must not log tenant PII.
- Must match the verified final lease before live use.
