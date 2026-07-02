# Apply Unused Credits Test Cases

Use sanitized or controlled Zoho Books records only. These cases are for the Invoice Created workflow custom function and should be run before live deployment.

| Case | Setup | Expected result |
|---|---|---|
| Missing context | Function run without invoice or organization context | Error logged; no API write attempted |
| Paid invoice | New invoice has zero balance | No credits applied |
| No unused credits | Customer has no unused receivable credits | No credits applied |
| Customer-payment credit exact match | Invoice balance equals unused customer-payment balance on same branch | Full balance covered once |
| Customer-payment credit partial | Invoice balance exceeds unused customer-payment balance on same branch | Available credit applied; remaining invoice balance stays open |
| Customer-payment credit larger than invoice | Unused customer-payment balance exceeds invoice balance on same branch | Only invoice balance is applied |
| Credit note | Customer has unused credit note on same branch | Credit note applied through `apply_creditnotes` |
| Retainer payment | Customer has unused retainer payment on same branch | Retainer credit applied through `invoice_payments` |
| Multiple credit sources | Customer has credit note plus customer/retainer credits | Credits apply until invoice balance is covered or available credits are exhausted |
| Branch mismatch | Credit exists on a different branch than the invoice | Credit is skipped |
| Empty branch on both records | Invoice and credit both have empty branch values | Credit applies, matching current single-branch behavior |
| Unknown credit entity type | Unused credit payload contains unsupported `entity_name` | Unsupported credit is skipped |
| Duplicate/manual re-run | Function is run again after credits were already applied | No over-application; Zoho Books remaining credit balance is the source of truth |
| API failure loading invoice | Invoice lookup fails or returns no invoice object | Error logged; no credit-application POST attempted |
| API failure loading credits | Unused-credit lookup fails or returns no credits object | Safe stop; no credit-application POST attempted |
| Logs check | Normal run with debug not added | Logs contain no tenant PII, bank data, raw payloads, or secrets |
