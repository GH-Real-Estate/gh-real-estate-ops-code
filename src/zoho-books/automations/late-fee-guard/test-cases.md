# Late Fee Guard And Monthly Interest Test Cases

Use sanitized records only. These cases are for the combined Zoho Books scheduled Deluge function and should be run before any live late-fee or delinquent-rent interest deployment.

## Late Fee Guard

| Case | Setup | Expected result |
|---|---|---|
| Current invoice, not late | `INV_TEST_CURRENT`, balance due, before fee threshold | No fee created |
| First fee threshold before cutoff | `INV_TEST_D5_1659_CT`, due date + 4 days, run at 4:59 p.m. Central | No D5 fee created |
| First fee threshold at cutoff | `INV_TEST_D5_1700_CT`, due date + 4 days, run at or after 5:00 p.m. Central | Correct D5 fee created once |
| Second fee threshold before cutoff | `INV_TEST_D10_1659_CT`, due date + 9 days, run at 4:59 p.m. Central | No D10 fee created |
| Second fee threshold at cutoff | `INV_TEST_D10_1700_CT`, due date + 9 days, run at or after 5:00 p.m. Central | Correct D10 fee created once |
| Already has first fee | Invoice already marked/linked as D5 applied | No duplicate D5 fee |
| Already has second fee | Invoice already marked/linked as D10 applied | No duplicate D10 fee |
| Overlapping scheduled runs | Start two guarded runs against the same eligible invoice | At most one fee invoice is created for each stage |
| Stage-field persistence failure | Simulate failure updating `cf_late_fee_stages_applied` after fee creation | Warning/alert is logged; duplicate-search fallback prevents repeat creation on next run |
| Paid invoice | Balance is zero | No fee created |
| Partial payment | Balance remains after threshold | Fee behavior matches lease/code rule and total cap |
| Pending ACH/online payment | Latest payment is pending, processing, initiated, or in review | Late-fee stages are suppressed for that run |
| Returned/failed payment | Latest payment is definitively failed/returned | Pending-payment suppression is removed; normal late-fee rules apply |
| Customer fee exempt | Contact has fee-exempt flag or exemption date through today | No fee or interest created |
| Invoice fee exempt | Invoice has fee-exempt or do-not-assess flag | No fee or interest created |
| Interest invoice overdue | Existing interest invoice is overdue and not marked rent | Excluded from late fees and excluded from interest source invoices |
| Wrong customer/type | Non-rent invoice or excluded invoice | No fee created |
| API error | Simulated Zoho API failure | Fail safely; do not create partial duplicate records |
| Logs check | Debug disabled during normal run | No tenant PII, bank data, or secrets in logs |

## Monthly Interest Billing

| Case | Setup | Expected result |
|---|---|---|
| Rent invoice 4 days overdue | `INV_INT_004`, rent invoice, balance due, run during monthly billing window | No interest; dry-run report shows `daysPastDue=4` exclusion |
| Rent invoice 31+ days overdue mid-month | `INV_INT_031_MID`, rent invoice, 31+ days overdue, run mid-month with `MANUAL_INTEREST_RUN_OVERRIDE=false` | No invoice; job exits with monthly-window skip |
| Manual mid-month override | Same as above with `MANUAL_INTEREST_RUN_OVERRIDE=true` and `DRY_RUN=true` | No posting; dry-run report shows calculated interest and would-create decision if threshold is met |
| Multiple eligible rent invoices for one tenant | One customer has `INV_INT_A` and `INV_INT_B`, both eligible, both unpaid | One consolidated monthly interest invoice would be created for that customer/month |
| Interest below threshold | Eligible calculated interest totals `$9.99` or less for a tenant | No invoice created; log says skipped below `$10.00`; no carry-forward unless durable storage is later added |
| Existing idempotency key | Existing invoice has reference `GHRE_INT_{customer_id}_{YYYYMM}` | No duplicate. Draft can be updated when posting is enabled; Sent/Paid/Partially Paid/Void is left alone |
| Late fee invoice overdue | Source invoice number starts `LF-` or reference/header indicates late fee | Excluded from interest |
| Interest invoice overdue | Source invoice has `GHRE_INT_`, `INT-`, `Interest (` or `Monthly Interest` in header/reference | Excluded from interest and not eligible for late fees |
| Processing fee invoice | Source invoice/header/line indicates processing fee, online payment fee, or payment processing | Excluded from interest |
| NSF / returned payment fee invoice | Source invoice/header/line indicates NSF, returned payment, or returned check | Excluded from interest |
| Security deposit invoice | Source invoice/header/line indicates security deposit | Excluded from interest |
| Application fee invoice | Source invoice/header/line indicates application fee | Excluded from interest |
| Fee-only invoice | Invoice has only excluded fee/deposit lines and no approved non-fee principal | Excluded from interest |
| Partial payment | Original rent invoice total is higher than current balance | Interest uses current outstanding balance, not original invoice total |
| Voided invoice | Status is void/voided/deleted | Excluded from interest |
| Written-off invoice | Status indicates written off/write-off | Excluded from interest |
| Disputed invoice | Status indicates dispute/disputed | Excluded from interest |
| Dry-run safety | `DRY_RUN=true`, `POST_INTEREST_INVOICES=true` | No invoice created because dry run wins |
| Posting disabled safety | `DRY_RUN=false`, `POST_INTEREST_INVOICES=false` | No invoice created; report says invoice would be created |
| Draft-first posting | `DRY_RUN=false`, `POST_INTEREST_INVOICES=true`, `SEND_INTEREST_INVOICES=false` | Draft invoice created only |
| Send explicitly enabled | `DRY_RUN=false`, `POST_INTEREST_INVOICES=true`, `SEND_INTEREST_INVOICES=true` | Invoice is marked sent and email is attempted using Books invoice email recipients |

## Manual Smoke Steps

1. Run `Late_Fee_Guard.deluge` with monthly interest `DRY_RUN=true` against sanitized test data.
2. Confirm report includes tenants checked, invoices checked, exclusions and reasons, eligible principal, eligible days, calculated interest, threshold skips, and would-create decisions.
3. Re-run the dry run and confirm the report is stable.
4. For one sanitized tenant above threshold, create a Draft using `DRY_RUN=false` and `POST_INTEREST_INVOICES=true` with `SEND_INTEREST_INVOICES=false`.
5. Re-run posting for the same billing month and confirm the existing `GHRE_INT_{customer_id}_{YYYYMM}` invoice is found and no duplicate is created.
6. Inspect the Draft invoice line item: it must be named `Monthly Interest Charge` and the description must include billing period, source invoice numbers, source due dates, outstanding principal, eligible days, annual rate, and formula.
