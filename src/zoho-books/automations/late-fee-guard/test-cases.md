# Late Fee Guard Test Cases

Use sanitized records only. These cases are for the Zoho Books scheduled Deluge function and should be run before any live late-fee or delinquent-rent interest deployment.

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
| Interest day 30 | Invoice is 30 days after due date | No interest invoice created |
| Interest day 31 | Invoice is 31 days after due date and meets minimum amount | Interest invoice created once |
| Interest frequency | Interest was already assessed less than 30 days ago | No new interest invoice created |
| Wrong customer/type | Non-rent invoice or excluded invoice | No fee created |
| API error | Simulated Zoho API failure | Fail safely; do not create partial duplicate records |
| Logs check | Debug disabled during normal run | No tenant PII, bank data, or secrets in logs |
