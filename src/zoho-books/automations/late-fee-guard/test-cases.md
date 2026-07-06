# Late Fee Guard Test Cases

Use sanitized records only. These cases are for the Zoho Books scheduled Deluge late-fee function and should be run before live late-fee deployment.

## Late Fee Guard

| Case | Setup | Expected result |
|---|---|---|
| Current invoice, not late | `INV_TEST_CURRENT`, balance due, before fee threshold | No fee created |
| First fee threshold before cutoff | `INV_TEST_D5_1659_CT`, due date + 4 days, run before 5:00 p.m. Central | No D5 fee created |
| First fee threshold at cutoff | `INV_TEST_D5_1700_CT`, due date + 4 days, run at or after 5:00 p.m. Central | Correct D5 fee created once |
| Second fee threshold before cutoff | `INV_TEST_D10_1659_CT`, due date + 9 days, run before 5:00 p.m. Central | No D10 fee created |
| Second fee threshold at cutoff | `INV_TEST_D10_1700_CT`, due date + 9 days, run at or after 5:00 p.m. Central | Correct D10 fee created once |
| Already has first fee | Invoice already marked/linked as D5 applied | No duplicate D5 fee |
| Already has second fee | Invoice already marked/linked as D10 applied | No duplicate D10 fee |
| Overlapping scheduled runs | Start two guarded runs against the same eligible invoice | At most one fee invoice is created for each stage |
| Stage-field persistence failure | Simulate failure updating `cf_late_fee_stages_applied` after fee creation | Warning/alert is logged; duplicate-search fallback prevents repeat creation on next run |
| Paid invoice | Balance is zero | No fee created |
| Partial payment | Balance remains after threshold | Fee behavior matches lease/code rule and total cap |
| Pending ACH/online payment | Latest payment is pending, processing, initiated, or in review | Late-fee stages are suppressed for that run |
| Returned/failed payment | Latest payment is definitively failed/returned | Pending-payment suppression is removed; normal late-fee rules apply; no RF invoice is created here |
| Customer fee exempt | Contact has fee-exempt flag or exemption date through today | No fee created |
| Invoice fee exempt | Invoice has fee-exempt or do-not-assess flag | No fee created |
| Interest invoice overdue | Existing interest invoice is overdue and not marked rent | Excluded from late fees |
| Wrong customer/type | Non-rent invoice or excluded invoice | No fee created |
| API error | Simulated Zoho API failure | Fail safely; do not create partial duplicate records |
| Logs check | Debug disabled during normal run | No tenant PII, bank data, or secrets in logs |

## Manual Smoke Steps

1. Run `Late_Fee_Guard.deluge` against sanitized late-fee test data.
2. Confirm the function creates the expected D5/D10 invoice once.
3. Re-run the same test and confirm idempotency.
4. Confirm the source rent invoice has `cf_late_fee_stages_applied` tokens/logs updated.
5. Confirm no returned-payment / NSF invoice is created by this function.
