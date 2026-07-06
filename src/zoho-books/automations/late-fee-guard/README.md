# Late Fee Guard

Zoho Books scheduled Deluge automations for GH Real Estate rent late-fee and delinquent-rent interest handling.

## Runtime

```text
System: Zoho Books
Language: Deluge
Function type: Scheduled functions
Late-fee file: Late_Fee_Guard.deluge
Monthly interest file: Monthly_Interest_Billing.deluge
```

## Why This Lives Under `src/zoho-books/`

These automations belong here because they are installed in Zoho Books and create/update Zoho Books invoices and custom fields. The old generic `automations/` location made the repo feel scattered because it grouped code by workflow label instead of by the system that owns the runtime.

## Related Files

| File | Purpose |
|---|---|
| `Late_Fee_Guard.deluge` | Production Deluge script source copy for D5/D10 late-fee milestones |
| `Monthly_Interest_Billing.deluge` | Monthly consolidated simple-interest billing script |
| `disable-daily-interest.patch` | Targeted patch to disable the old daily/source-invoice interest path in `Late_Fee_Guard.deluge` |
| `install-checklist.md` | Install and verification checklist |
| `test-cases.md` | Sanitized test plan |
| `../../field-maps/books-automation-settings.md` | Zoho Books item/template/custom-field settings |
| `../../../../docs/business-rules/lease-automation-rules.md` | Lease rules the code must match |
| `../../../../docs/runbooks/deployment-log.md` | Deployment/change log |

## Late-Fee Policy

- Keep D5 and D10 milestone late-fee logic in `Late_Fee_Guard.deluge`.
- Do not apply late fees to prior late-fee invoices, returned-fee invoices, or interest invoices.
- Source invoices must be intentionally marked as rent with `cf_is_rent_invoice` unless a future approved non-fee charge configuration is added and reviewed.
- Pending ACH/online payment suppression remains part of the late-fee guard.

## Monthly Interest Policy

- Interest is simple annual interest calculated by day, not a flat monthly fee.
- Default rate is `INTEREST_ANNUAL_RATE = 10.00`.
- Interest eligibility starts only when an eligible source invoice is more than 30 days past due, using `daysPastDue > 30`.
- Formula: `eligibleOutstandingPrincipal * annualRate * eligibleDaysInBillingPeriod / 365`.
- No compounding.
- Create at most one monthly interest invoice per tenant per billing month.
- The line item name is `Monthly Interest Charge`.
- The invoice reference/idempotency key is `GHRE_INT_{customer_id}_{YYYYMM}`.
- Minimum posting threshold is `$10.00`. Below-threshold amounts are logged and skipped. No durable carry-forward storage exists in this repo today.

## Interest Exclusions

Do not charge interest on:

- prior interest invoices
- late fee invoices
- online payment or processing fee invoices
- NSF or returned payment fee invoices
- application fees
- security deposits
- fee-only invoices
- voided, disputed, written-off, draft, deleted, or zero-balance invoices

`Monthly_Interest_Billing.deluge` defaults to excluding mixed fee/non-fee invoices because Zoho Books invoice-level balances do not reliably identify whether a partial payment left rent principal or a fee balance outstanding.

## Required Interest Config

| Variable | Default | Purpose |
|---|---:|---|
| `DRY_RUN` | `true` | Prints the report without creating/updating invoices |
| `POST_INTEREST_INVOICES` | `false` | Must be `true` with `DRY_RUN=false` before any invoice is posted |
| `SEND_INTEREST_INVOICES` | `false` | Sends interest invoices only after creation; otherwise invoices remain Draft |
| `MANUAL_INTEREST_RUN_OVERRIDE` | `false` | Allows a controlled mid-month run; keep off for normal schedule |
| `INTEREST_ANNUAL_RATE` | `10.00` | Annual simple interest rate percentage |
| `interestMinimumPostingAmount` | `10.00` | Minimum tenant monthly interest amount required before posting |
| `interestIdempotencyFieldApiName` | blank | Optional Books invoice custom field for the idempotency key; reference number is always used |

## Schedule

Run `Monthly_Interest_Billing.deluge` only:

- on the last day of the month after close of business, or
- on the first day of the following month for the prior month.

Normal rollout should run with `DRY_RUN=true` first. Invoice creation requires both `DRY_RUN=false` and `POST_INTEREST_INVOICES=true`. Created invoices remain Draft unless `SEND_INTEREST_INVOICES=true`.

## Safety Requirements

- Must be idempotent.
- Must not create duplicate fees or interest invoices.
- Must only process invoices intentionally marked as rent or approved non-fee tenant charges.
- Must suppress fee creation while ACH/online payments are still pending or processing.
- Must not log tenant PII.
- Must match the verified final lease before live use.
