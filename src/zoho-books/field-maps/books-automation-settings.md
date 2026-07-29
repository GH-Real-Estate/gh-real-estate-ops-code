# Zoho Books Automation Settings

Document non-secret IDs and API names needed by automation. Do not include tenant PII, payment records, OAuth tokens, refresh tokens, client secrets, passwords, or API keys.

## Current Values Observed In Code

| Setting | Current Value | Status / Notes |
|---|---:|---|
| Zoho Books organization ID | `[PRIVATE CONFIGURATION REQUIRED]` | Observed in saved Deluge source; schedule context can override when present. |
| Zoho Books connection name | `zbooks` | Observed in Deluge automation code. Verify in Zoho before live deployment. |
| Apply-unused-credits workflow module | `Invoice` | Must be an Invoice workflow, not an Estimate workflow. |
| Apply-unused-credits trigger | Event Based / Created | Runs when a new invoice is created. Do not enable during bulk historical imports unless intentional. |
| Apply-unused-credits eligibility field | `cf_is_rent_invoice` | Prevents accidental credit application to non-rent/miscellaneous invoices. |
| Apply-unused-credits unused-credit source | `/contacts/{customer_id}/receivables/unusedcredits` | Reads unused customer credits from Zoho Books contact receivables. |
| Apply-unused-credits retainer option | `include_unused_retainer_payments=false` | Retainers are excluded and defensively skipped because they may represent refundable tenant deposits. |
| Apply-unused-credits branch rule | Invoice `branch_id` must match credit `branch_id` | Prevents cross-branch credit application. Blank branch values fail closed unless explicitly changed after verification. |
| Late-fee item ID | `[PRIVATE CONFIGURATION REQUIRED]` | Observed in Late Fee Guard. Non-secret, but verify in Zoho Books. |
| Interest item ID | `[PRIVATE CONFIGURATION REQUIRED]` | Used by monthly interest billing. Verify item exists and maps to delinquent-rent interest. |
| Late-fee invoice template name | `Fee Invoice - Late Fee` | Observed in Late Fee Guard. Verify template exists. |
| Late-fee invoice template ID | `[PRIVATE CONFIGURATION REQUIRED]` | Observed in Late Fee Guard. Verify before live deployment. |
| Late-fee / interest source ledger field | `cf_late_fee_stages_applied` | Source invoice custom field used for late-fee and monthly-interest idempotency/history. |
| Rent invoice flag field | `cf_is_rent_invoice` | Source invoice must be marked as rent for fee and monthly-interest processing. |
| Do-not-assess invoice field | `cf_do_not_assess_fees` | Optional exclusion flag. |
| Invoice fee-exempt field | `cf_fee_exempt` | Optional exclusion flag. |
| Invoice fee-exempt-until field | `cf_fee_exempt_until` | Optional temporary exclusion field. |
| Customer fee-exempt field | `cf_fee_exempt` | Optional customer-level exclusion flag. |
| Customer fee-exempt-until field | `cf_fee_exempt_until` | Optional customer-level temporary exclusion field. |
| Monthly interest APR | `interestAprPct = 10.00` | Matches uploaded lease template Section 3.6. |
| Monthly interest eligibility | `interestFirstEligibleDaysAfterDue = 31` | No assessment until unpaid Rent is more than 30 days delinquent. |
| Monthly interest accrual start | `interestStartsDaysAfterDue = 0` | Once eligible, interest accrues from the original rent due date. |
| Monthly interest minimum invoice amount | `$10.00` | Operational threshold; not a lease value. |
| Monthly interest invoice prefix | `INT-` | Manual invoice-number series. |
| Monthly interest period token | `INTPERIOD_YYYYMM` | Written to source rent invoice ledger field. |
| Monthly interest invoice token | `INTINV_YYYYMM=<invoice_id>` | Written to source rent invoice ledger field. |
| Monthly interest reference | `GHRE_INT_YYYYMM_customerId` | Customer-period duplicate protection. |
| Monthly interest schedule | Monthly after close of business | Daily frequency should be used only for testing save/run behavior. |
| Returned-payment fee item ID | `RETURNED_FEE_ITEM_ID` env var | Must be set before live returned-payment automation. |
| Returned-payment fee amount | `RETURNED_FEE_AMOUNT=30.00` | Matches uploaded lease template Section 3.7. Do not set to $35 unless the lease is amended. |
| Returned-payment ledger field | `cf_returned_payment_fee_events` | Used by webhook to prevent duplicate returned-payment fee events. |
| Optional latest returned-fee invoice field | `cf_returned_fee_invoice_number` | Only updated if enabled by env. |
| Partial-payment source field | Top-level `allow_partial_payments` | Preserve or explicitly resolve the source value on newly created LF, INT, and RF invoices. Source-ledger updates must write custom fields only. Do not nest this field inside `payment_options`. |

## Required Before Live Automation

- [ ] Verify every item ID exists in Zoho Books.
- [ ] Verify invoice template ID opens the correct Zoho Books template.
- [ ] Verify all custom fields exist on the correct object: invoice vs customer/contact.
- [ ] Verify `Late_Fee_Guard.deluge` has daily interest disabled with `enableInterestOnDelinquentRent=false`.
- [ ] Verify `Monthly_Interest_Billing.deluge` is installed as a separate Zoho Books scheduled function from `src/zoho-books/automations/monthly-interest-billing/`.
- [ ] Verify monthly interest invoices will not be marked as rent.
- [ ] Verify `GHRE_INT_YYYYMM_customerId` can be found through invoice reference-number search.
- [ ] Verify returned-payment fee amount is `$30.00` in Catalyst runtime unless law requires a lower amount.
- [ ] Confirm the source of truth for rent invoice identification: `cf_is_rent_invoice`.
- [ ] Confirm test invoices cannot trigger fees unless intentionally marked as rent.
- [ ] Confirm the `zbooks` connection can read invoices, read contacts, create invoices, update invoices, and send invoices where configured.
- [ ] Inspect the actual generated rent invoice under Sales > Invoices and verify its top-level `allow_partial_payments` value; the recurring profile checkbox alone does not verify an already-generated invoice.
- [ ] If a saved bank account is associated with the recurring profile, verify whether auto-charge is intended before promising the tenant control over a partial payment amount.
- [ ] Confirm Apply Unused Credits is configured as an Invoice Created workflow, not an Estimate workflow.
- [ ] Confirm Apply Unused Credits should run for every new invoice or add a Zoho Books workflow filter.
- [ ] Confirm the installed function excludes all retainer payments; any future true-rent-advance workflow requires a separate explicit allowlist.

## Field Naming Convention

Use Zoho API names, not display labels, whenever possible.

## Change Log

| Date | Change | Verified By |
|---|---|---|
| 2026-07-25 | Excluded all retainer payments from Apply Unused Credits and added a fail-closed unexpected-retainer guard | Repository review; live Zoho deployment pending |
| 2026-07-17 | Corrected LF/INT/RF partial-payment inheritance to use and preserve the top-level `allow_partial_payments` invoice field | Repository review; live Zoho verification pending |
| 2026-07-06 | Updated Monthly Interest Billing to accrue from the original due date once eligible after 30 days | ChatGPT / GitHub update |
| 2026-07-06 | Moved Monthly Interest Billing into its own Zoho Books automation folder and aligned settings with saved v1.5 code | ChatGPT / GitHub update |
| 2026-07-06 | Verified RF fee amount should be `$30.00` under the uploaded lease template | ChatGPT review of lease template |
| 2026-07-06 | Split daily late-fee guard and monthly interest billing into separate Zoho Books scheduled functions | Pending verification in Zoho |
| 2026-07-02 | Documented hardened Apply Unused Credits settings for invoice eligibility, branch fail-closed behavior, credit order, response-code handling, and pre-apply balance recheck | Pending verification in Zoho |
| 2026-07-02 | Added Apply Unused Credits workflow settings observed in committed Deluge code | Pending verification in Zoho |
| 2026-07-01 | Starter placeholder created | Gabriel |
| 2026-07-01 | Updated with non-secret values observed in committed automation code | Pending verification in Zoho |
