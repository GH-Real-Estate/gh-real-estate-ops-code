# Apply Unused Credits Test Cases

Use sanitized or controlled Zoho Books records only. These cases are for the Invoice Created workflow custom function and should be run before live deployment.

| Case | Setup | Expected result |
|---|---|---|
| Missing context | Function run without invoice or organization context | Error logged; no API write attempted |
| Failed invoice lookup | Zoho Books invoice GET returns non-zero `code` or request error | Error logged; no credit lookup or write attempted |
| Invoice not eligible | `requireRentInvoiceFlag=true` and `cf_is_rent_invoice` is false/missing | No credits applied |
| Paid invoice | New invoice has zero balance | No credits applied |
| No unused credits | Customer has no unused receivable credits | No credits applied |
| Customer-payment credit exact match | Invoice balance equals unused customer-payment balance on same branch | Full balance covered once |
| Customer-payment credit partial | Invoice balance exceeds unused customer-payment balance on same branch | Available credit applied; remaining invoice balance stays open |
| Customer-payment credit larger than invoice | Unused customer-payment balance exceeds invoice balance on same branch | Only invoice balance is applied |
| Credit note | Customer has unused credit note on same branch | Credit note applied through `apply_creditnotes` before payment/retainer credits |
| Retainer payment | Customer has unused retainer payment on same branch | Retainer credit applied through `invoice_payments` after credit notes and customer-payment credits |
| Multiple credit sources | Customer has credit note plus customer/retainer credits | Credits apply in configured order until invoice balance is covered or available credits are exhausted |
| Branch mismatch | Credit exists on a different branch than the invoice | Credit is skipped |
| Blank branch fail-closed | Invoice or credit has blank branch and `allowEmptyBranchMatch=false` | Function stops or skips credit to avoid unverified branch application |
| Blank branch allowed | Invoice and credit both have blank branch and `allowEmptyBranchMatch=true` | Credit applies only after single-branch behavior is verified |
| Unknown credit entity type | Unused credit payload contains unsupported `entity_name` | Unsupported credit is skipped |
| Malformed credit balance | Credit payload has blank/non-decimal balance | Credit is skipped; function continues with other eligible credits |
| Duplicate/manual re-run | Function is run again after credits were already applied | No over-application; Zoho Books remaining credit balance and pre-apply balance recheck are the guardrails |
| Balance changes before POST | Invoice balance decreases after payload selection and before credit apply | Function stops so a later run can recalculate |
| API failure loading credits | Unused-credit lookup fails or returns non-zero `code` | Error logged; no credit-application POST attempted |
| API failure applying credits | Credit apply POST fails or returns non-zero `code` | Error logged; function does not report success |
| Logs check | Normal run with debug not added | Logs contain no tenant PII, bank data, raw payloads, or secrets |
