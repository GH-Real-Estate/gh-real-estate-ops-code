# Monthly Interest Billing Test Cases

Use sanitized records only. These cases are for the separate Zoho Books scheduled Deluge function that bills monthly delinquent-rent interest.

## Monthly Interest Billing

| Case | Setup | Expected result |
|---|---|---|
| Rent invoice 4 days overdue | `INV_INT_004`, rent invoice, balance due | No interest |
| Rent invoice 31+ days overdue | `INV_INT_031`, rent invoice, balance due | Eligible for interest calculation |
| First eligible period starts at due date | `INV_INT_031`, due date on day 0, run on day 31 or later | Interest period begins at the original due date, not day 31 |
| Multiple eligible rent invoices for one tenant | One customer has `INV_INT_A` and `INV_INT_B`, both eligible, both unpaid | One consolidated monthly interest invoice for that customer/month |
| Interest below threshold | Eligible calculated interest totals below `$10.00` for a tenant | No invoice created |
| Existing customer-period invoice | Existing invoice has reference `GHRE_INT_YYYYMM_customerId` | No duplicate |
| Source already tokened | Source rent invoice has `INTPERIOD_YYYYMM` or `INTINV_YYYYMM=...` | No duplicate |
| Late fee invoice overdue | Source invoice number starts `LF-` or reference/header indicates late fee | Excluded from interest |
| Returned-payment invoice overdue | Source invoice/header/line indicates returned payment or returned check | Excluded from interest |
| Processing fee invoice | Source invoice/header/line indicates processing fee, online payment fee, or payment processing | Excluded from interest |
| Security deposit invoice | Source invoice/header/line indicates security deposit | Excluded from interest |
| Application fee invoice | Source invoice/header/line indicates application fee | Excluded from interest |
| Fee-only invoice | Invoice has only excluded fee/deposit lines | Excluded from interest |
| Partial payment | Original rent invoice total is higher than current balance | Interest uses current outstanding balance |
| Voided/deleted invoice | Status is void or deleted | Excluded from interest |
| ACH initiated | Source invoice has `ach_payment_initiated=true` | Interest skipped for that invoice in this run |
| Logs check | Debug disabled during normal run | No tenant PII, bank data, or secrets in logs |

## Manual Smoke Steps

1. Run `Monthly_Interest_Billing.deluge` against sanitized monthly-interest test data.
2. Confirm no invoice is created for non-rent or excluded invoices.
3. Confirm one eligible customer produces one monthly interest invoice, not one invoice per source rent invoice.
4. Confirm the first eligible invoice line uses an interest period beginning on the original rent due date.
5. Re-run for the same billing month and confirm no duplicate invoice is created.
6. Inspect the created invoice line descriptions: they must include source invoice number, APR, interest period, and days.
7. Inspect each source rent invoice: it must receive the interest period and invoice ID tokens.
8. Confirm no returned-payment invoice is created by this function.
