# Monthly Interest Billing

Zoho Books scheduled Deluge automation for GH Real Estate delinquent-rent interest only.

## Runtime

```text
System: Zoho Books
Language: Deluge
Function type: Scheduled function
Deployable file: Monthly_Interest_Billing.deluge
```

## Why This Is Separate

Monthly interest is period-based. Late fees are milestone-based. Returned-payment fees are payment-event based.

Keeping this file in its own automation folder makes the repo match the production architecture:

| Charge / Action | Owner |
|---|---|
| D5/D10 late fees | `../late-fee-guard/Late_Fee_Guard.deluge` |
| Monthly delinquent-rent interest | `Monthly_Interest_Billing.deluge` |
| Returned-payment fee invoices | `src/zoho-payments/webhooks/returned-payment-fee/src/index.js` |

## Current Policy

- Interest applies to unpaid Rent only.
- Interest is eligible only if unpaid Rent remains unpaid more than thirty (30) days after the original due date.
- Once eligible, interest accrues from the original rent due date.
- The current lease template states ten percent (10%) simple annual interest, or the maximum lawful rate if lower.
- No compounding.
- No interest on late fees, returned-payment fees, processing fees, security deposits, application fees, or other fee-only invoices.
- The saved Zoho Books code uses `interestAprPct = 10.00`.
- The saved Zoho Books code uses `interestFirstEligibleDaysAfterDue = 31` and `interestStartsDaysAfterDue = 0`.

## Saved-Code Notes

The current source copy is the Zoho Books editor-safe, lease-aligned version:

```text
VERSION: v1.6_LEASE_ALIGNED_ORIGINAL_DUE_DATE_INTEREST
```

This version avoids `for each` loops directly over `response.get(...)` expressions because the Zoho Books schedule editor rejected that pattern during save. It also separates interest eligibility from interest accrual so the code matches Lease Section 3.6.

## Schedule

Recommended production schedule:

```text
Schedule Name: GHRE Monthly Interest Billing
Frequency: Monthly
Time: 17:30 Central or later
```

Daily frequency is acceptable only for save/run smoke testing.

## Safety Requirements

- Must only process invoices marked `cf_is_rent_invoice == true`.
- Must skip fee-only invoices and deposit invoices.
- Must use customer-period duplicate protection.
- Must write interest tokens back to `cf_late_fee_stages_applied` on source rent invoices.
- Must not create returned-payment fee invoices.
- Must not log tenant PII.
