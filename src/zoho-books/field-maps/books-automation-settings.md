# Zoho Books Automation Settings

Document non-secret IDs and API names needed by automation. Do not include tenant PII, payment records, OAuth tokens, refresh tokens, client secrets, passwords, or API keys.

## Current Values Observed In Code

| Setting | Current Value | Status / Notes |
|---|---:|---|
| Zoho Books connection name | `zbooks` | Observed in Late Fee Guard comments. Verify in Zoho before live deployment. |
| Late-fee item ID | `5858793000001596035` | Observed in Late Fee Guard. Non-secret, but verify in Zoho Books. |
| Interest item ID | `5858793000003568001` | Observed in Late Fee Guard. Verify item exists and label is correct. |
| Late-fee invoice template name | `Fee Invoice - Late Fee` | Observed in Late Fee Guard. Verify template exists. |
| Late-fee invoice template ID | `5858793000001838039` | Observed in Late Fee Guard. Verify before live deployment. |
| Late-fee stage ledger field | `cf_late_fee_stages_applied` | Source invoice custom field used for idempotency/history. |
| Rent invoice flag field | `cf_is_rent_invoice` | Source invoice must be marked as rent for fee processing. |
| Do-not-assess invoice field | `cf_do_not_assess_fees` | Optional exclusion flag. |
| Invoice fee-exempt field | `cf_fee_exempt` | Optional exclusion flag. |
| Invoice fee-exempt-until field | `cf_fee_exempt_until` | Optional temporary exclusion field. |
| Customer fee-exempt field | `cf_fee_exempt` | Optional customer-level exclusion flag. |
| Customer fee-exempt-until field | `cf_fee_exempt_until` | Optional customer-level temporary exclusion field. |
| Returned-payment fee item ID | `RETURNED_FEE_ITEM_ID` env var | Must be set before live returned-payment automation. |
| Returned-payment fee amount | Code default is `$30.00` unless env overrides | Verify against final lease before live use. Do not assume the default is correct. |
| Returned-payment ledger field | `cf_returned_payment_fee_events` | Used by webhook to prevent duplicate returned-payment fee events. |
| Optional latest returned-fee invoice field | `cf_returned_fee_invoice_number` | Only updated if enabled by env. |

## Required Before Live Automation

- [ ] Verify every item ID exists in Zoho Books.
- [ ] Verify invoice template ID opens the correct Zoho Books template.
- [ ] Verify all custom fields exist on the correct object: invoice vs customer/contact.
- [ ] Verify returned-payment fee amount against the final lease.
- [ ] Confirm the source of truth for rent invoice identification: `cf_is_rent_invoice`.
- [ ] Confirm test invoices cannot trigger fees unless intentionally marked as rent.

## Field Naming Convention

Use Zoho API names, not display labels, whenever possible.

## Change Log

| Date | Change | Verified By |
|---|---|---|
| 2026-07-01 | Starter placeholder created | Gabriel |
| 2026-07-01 | Updated with non-secret values observed in committed automation code | Pending verification in Zoho |
