# Late Fee Guard Test Cases

Use sanitized records only.

| Case | Setup | Expected result |
|---|---|---|
| Current invoice, not late | `INV_TEST_CURRENT`, balance due, before fee threshold | No fee created |
| First fee threshold reached | `INV_TEST_LATE_1`, balance due, after first configured threshold | Correct first fee created once |
| Second fee threshold reached | `INV_TEST_LATE_2`, balance due, after second configured threshold | Correct second fee created once |
| Already has first fee | Invoice already marked/linked as first fee applied | No duplicate first fee |
| Already has second fee | Invoice already marked/linked as second fee applied | No duplicate second fee |
| Paid invoice | Balance is zero | No fee created |
| Partial payment | Balance remains after threshold | Fee behavior matches lease/code rule |
| Wrong customer/type | Non-rent invoice or excluded invoice | No fee created |
| Time-zone edge | Near 5:00 p.m. Central Time | Correct threshold behavior |
| API error | Simulated Zoho API failure | Fail safely; do not create partial duplicate records |
