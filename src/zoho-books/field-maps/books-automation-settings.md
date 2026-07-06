# Zoho Books Automation Settings

Document non-secret IDs and API names needed by automation. Do not include tenant PII, payment records, OAuth tokens, refresh tokens, client secrets, passwords, or API keys.

## Current Values Observed In Code

| Setting | Current Value | Status / Notes |
|---|---:|---|
| Zoho Books connection name | `zbooks` | Observed in Deluge automation code. Verify in Zoho before live deployment. |
| Apply-unused-credits workflow module | `Invoice` | Must be an Invoice workflow, not an Estimate workflow. |
| Apply-unused-credits trigger | Event Based / Created | Runs when a new invoice is created. Do not enable during bulk historical imports unless intentional. |
| Apply-unused-credits eligibility field | `cf_is_rent_invoice` | Required by default through `requireRentInvoiceFlag=true`; prevents accidental credit application to non-rent/miscellaneous invoices. |
| Apply-unused-credits unused-credit source | `/contacts/{customer_id}/receivables/unusedcredits` | Reads unused customer credits from Zoho Books contact receivables. |
| Apply-unused-credits retainer option | `include_unused_retainer_payments=true` | Includes unused retainer payments in the credit list. |
| Apply-unused-credits branch rule | Invoice `branch_id` must match credit `branch_id` | Prevents cross-branch credit application. Blank branch values fail closed unless `allowEmptyBranchMatch=true` after verification. |
| Apply-unused-credits order | credit notes, customer payments, retainer payments | Explicit order in code; Zoho's returned order is preserved within each type. |
| Apply-unused-credits duplicate guard | Pre-apply invoice balance recheck | Stops if the invoice balance was paid or reduced below the selected credit amount before POST. |
| Apply-unused-credits API handling | Non-zero Zoho response `code` fails the run | Applies to invoice lookup, unused-credit lookup, pre-apply lookup, and credit-application POST. |
| Apply-unused-credits write endpoint | `/invoices/{invoice_id}/credits` | Applies selected credits back to the invoice. |
| Late-fee item ID | `5858793000001596035` | Observed in Late Fee Guard. Non-secret, but verify in Zoho Books. |
| Interest item ID | `5858793000003568001` | Used by monthly interest billing. Verify item exists and supports line name `Monthly Interest Charge`. |
| Late-fee invoice template name | `Fee Invoice - Late Fee` | Observed in Late Fee Guard. Verify template exists. |
| Late-fee invoice template ID | `5858793000001838039` | Observed in Late Fee Guard. Verify before live deployment. |
| Late-fee stage ledger field | `cf_late_fee_stages_applied` | Source invoice custom field used for late-fee idempotency/history. |
| Rent invoice flag field | `cf_is_rent_invoice` | Source invoice must be marked as rent for fee and default monthly-interest processing. |
| Do-not-assess invoice field | `cf_do_not_assess_fees` | Optional exclusion flag. |
| Invoice fee-exempt field | `cf_fee_exempt` | Optional exclusion flag. |
| Invoice fee-exempt-until field | `cf_fee_exempt_until` | Optional temporary exclusion field. |
| Customer fee-exempt field | `cf_fee_exempt` | Optional customer-level exclusion flag. |
| Customer fee-exempt-until field | `cf_fee_exempt_until` | Optional customer-level temporary exclusion field. |
| Monthly interest default dry run | `DRY_RUN=true` | No interest invoice creation unless explicitly changed. This does not disable D5/D10 late-fee processing in the combined function. |
| Monthly interest posting flag | `POST_INTEREST_INVOICES=false` | Must be true with `DRY_RUN=false` before invoices can be created. |
| Monthly interest send flag | `SEND_INTEREST_INVOICES=false` | Draft-first rollout. Set true only after Draft output is reviewed. |
| Monthly interest manual override | `MANUAL_INTEREST_RUN_OVERRIDE=false` | Allows controlled non-window dry runs/posting; keep false for normal schedule. |
| Monthly interest annual rate | `INTEREST_ANNUAL_RATE=10.00` | Configurable simple annual interest rate. Do not hardcode 12%. |
| Monthly interest minimum posting amount | `$10.00` | Below-threshold amounts are logged and skipped. No durable carry-forward storage exists today. |
| Monthly interest idempotency key | `GHRE_INT_{customer_id}_{YYYYMM}` | Stored in invoice reference number by default. Optional custom field can be configured with `interestIdempotencyFieldApiName`. |
| Monthly interest line item name | `Monthly Interest Charge` | Required line item label for monthly interest invoices. |
| Monthly interest schedule | Last day after close of business or first day of following month | Mid-month runs require `MANUAL_INTEREST_RUN_OVERRIDE=true`. |
| Returned-payment fee item ID | `RETURNED_FEE_ITEM_ID` env var | Must be set before live returned-payment automation. |
| Returned-payment fee amount | Code default is `$30.00` unless env overrides | Verify against final lease before live use. Do not assume the default is correct. |
| Returned-payment ledger field | `cf_returned_payment_fee_events` | Used by webhook to prevent duplicate returned-payment fee events. |
| Optional latest returned-fee invoice field | `cf_returned_fee_invoice_number` | Only updated if enabled by env. |

## Required Before Live Automation

- [ ] Verify every item ID exists in Zoho Books.
- [ ] Verify invoice template ID opens the correct Zoho Books template.
- [ ] Verify all custom fields exist on the correct object: invoice vs customer/contact.
- [ ] Verify `Late_Fee_Guard.deluge` has daily interest disabled with `enableInterestOnDelinquentRent=false` and contains the combined monthly interest section.
- [ ] Verify monthly interest invoices will not be marked as rent.
- [ ] Verify `GHRE_INT_{customer_id}_{YYYYMM}` can be found through invoice reference-number search.
- [ ] Verify returned-payment fee amount against the final lease.
- [ ] Confirm the source of truth for rent invoice identification: `cf_is_rent_invoice`.
- [ ] Confirm test invoices cannot trigger fees unless intentionally marked as rent.
- [ ] Confirm the `zbooks` connection can read invoices, read contact unused credits, and apply credits to invoices.
- [ ] Confirm the `zbooks` connection can create/update Draft invoices for monthly interest before posting is enabled.
- [ ] Confirm Apply Unused Credits is configured as an Invoice Created workflow, not an Estimate workflow.
- [ ] Confirm Apply Unused Credits should run for every new invoice or add a Zoho Books workflow filter.
- [ ] Confirm `cf_is_rent_invoice` is present and populated before keeping `requireRentInvoiceFlag=true`.
- [ ] Confirm multi-branch credit behavior before enabling Apply Unused Credits in production.
- [ ] Confirm blank branch handling before changing `allowEmptyBranchMatch`.
- [ ] Confirm the credit-source order matches accounting preference.

## Field Naming Convention

Use Zoho API names, not display labels, whenever possible.

## Change Log

| Date | Change | Verified By |
|---|---|---|
| 2026-07-06 | Documented monthly consolidated simple-interest settings, idempotency key, threshold, schedule, and dry-run/posting defaults | Pending verification in Zoho |
| 2026-07-02 | Documented hardened Apply Unused Credits settings for invoice eligibility, branch fail-closed behavior, credit order, response-code handling, and pre-apply balance recheck | Pending verification in Zoho |
| 2026-07-02 | Added Apply Unused Credits workflow settings observed in committed Deluge code | Pending verification in Zoho |
| 2026-07-01 | Starter placeholder created | Gabriel |
| 2026-07-01 | Updated with non-secret values observed in committed automation code | Pending verification in Zoho |
