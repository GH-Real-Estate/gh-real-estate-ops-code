# Lease Automation Rules

This file summarizes only the lease rules needed by code. It is not the lease. The final signed lease/template in Zoho Contracts or WorkDrive remains the legal source document.

## Required Before Live Automation

- [ ] Confirm this file matches the final signed lease/template.
- [ ] Confirm the late-fee code matches this file.
- [ ] Confirm monthly interest code matches this file.
- [ ] Confirm Zoho Books item/template/custom field IDs are updated.
- [ ] Confirm returned-payment logic is separate from late-fee logic.
- [ ] Confirm every fee/interest value below is enforceable and matches the final lease.

## Current Values Verified Against 2026-06-30 Lease Template

| Rule | Current Code / Runtime Value | Verification Status |
|---|---:|---|
| Rent due date basis | Source invoice `due_date`; monthly rent invoices should be due on the 1st | Matches lease template Section 3.1 subject to invoice setup |
| Rent due time zone | Central Time behavior required; schedule should run after 5:00 p.m. CT on assessment days | Matches lease template Sections 3.1 and 3.5 subject to Zoho runtime behavior |
| Late threshold #1 | `D5` = `due_date + 4 days`, after 5:00 p.m. CT | Matches lease template Section 3.5 |
| Late fee #1 | `5%` of unpaid rent balance | Matches lease template Section 3.5 |
| Late threshold #2 | `D10` = `due_date + 9 days`, after 5:00 p.m. CT | Matches lease template Section 3.5 |
| Late fee #2 | Additional `5%` of unpaid rent balance | Matches lease template Section 3.5 |
| Total late-fee cap | `10%` of unpaid rent for that monthly rent charge | Matches lease template Section 3.5 |
| Interest eligibility | First eligible day is day 31 after original due date | Matches lease template Section 3.6: unpaid Rent must remain unpaid more than 30 days |
| Interest accrual start | `interestStartsDaysAfterDue = 0`; once eligible, interest accrues from the original due date | Matches lease template Section 3.6 |
| Interest rate | `10.00%` APR in `Monthly_Interest_Billing.deluge` | Matches lease template Section 3.6 |
| Interest frequency | Separate monthly scheduled billing; simple interest only | Operational design; lease allows simple interest until paid |
| Interest minimum invoice amount | `$10.00` | Operational threshold, not a lease value |
| Returned-payment fee | `RETURNED_FEE_AMOUNT=30.00` / source default `$30.00` | Matches lease template Section 3.7: `$30.00 or maximum lawful amount, whichever is less` |
| Non-approved payment method admin fee | Not automated in current code | Lease template Section 3.3 allows `$25.00`; leave out of automation unless explicitly added |

## Prospective Ordinary-Pet Administration Fee — Not Production Authorized

The proposed one-time Ordinary-Pet Administration Fee is `$50.00` per household for the continuous tenancy. It is cost-linked to actual ordinary-pet approval-processing work and remains blocked from production because it has not been verified against the 2026-06-30 Lease Template.

Required behavior:

- Assess the fee only after at least one Ordinary Pet is approved and the final Lease/addendum or signed prospective amendment containing the charge is executed and effective.
- Treat the fee as ordinarily nonrefundable once earned, subject to the controlled assistance-animal void/refund/credit rule below and any controlling law.
- Charge it once per household for the continuous tenancy. Do not charge it again at renewal, extension, holdover, replacement-pet approval, additional-pet approval, or a later animal-addendum update.
- Treat it as an `Other Charge`, not `Base Rent` or a security deposit. It is not held for, credited toward, or used to pay damage, cleaning, pest treatment, wear, performance, or breach.
- Do not create a separate late-fee, interest, collection-cost, or payment-allocation formula for it.
- Do not add it unilaterally during an existing tenancy. A material mid-tenancy addition requires a signed prospective amendment.
- Use `$0.00` / not applicable for an Approved or Interim Assistance Animal. Pause an unassessed charge while an accommodation request concerning the fee-triggering animal is pending.
- If the sole animal that triggered the charge is later approved as an assistance animal, void an unpaid invoice or promptly issue a traceable `$50.00` refund/credit. If an approved Ordinary Pet remains, route the fee to individualized manual review.
- Use a stable idempotency key derived from the parent lease/continuous-tenancy identifier and fee type; never include tenant or animal names in the key or logs.
- Keep an internal, non-PII cost rationale for the approval-processing work. Do not describe the fee as reimbursement for animal damage or risk.

Do not configure or invoice the charge until qualified Kansas counsel approves the final Lease/addendum language and signed-adoption method, the full current Lease has been reconciled, and CPA/accounting review approves the Zoho Books item, revenue account, recognition, refund/credit workflow, and audit treatment. An account or item name never authorizes the charge.

## Automation Constraints

- Fees must be idempotent.
- No duplicate late-fee, monthly-interest, returned-payment-fee, or Ordinary-Pet Administration Fee invoices.
- Zoho Books remains the accounting source of truth.
- Late Fee Guard owns only late fees.
- Monthly Interest Billing owns only delinquent-rent interest.
- Returned-payment fee invoices are owned by the Zoho Payments webhook running in Zoho Catalyst.
- No runtime owner exists yet for the prospective Ordinary-Pet Administration Fee; do not implement one until all production gates above are approved.
- All production changes must be documented in `docs/runbooks/deployment-log.md`.
- Do not use this file as legal advice. Use it only as an automation checklist against the final lease.

## Change Log

| Date | Change | Verified By |
|---|---|---|
| 2026-07-13 | Documented the prospective `$50.00` one-time Ordinary-Pet Administration Fee and its legal, accounting, accommodation, and idempotency gates; not production authorized | Attorney, CPA/accounting, and full-lease review pending |
| 2026-07-06 | Aligned monthly interest accrual start with Lease Section 3.6: eligible after day 30, accrues from original due date once eligible | ChatGPT / GitHub update |
| 2026-07-06 | Verified late-fee, interest, and returned-payment fee values against the uploaded 2026-06-30 lease template; confirmed RF fee is $30.00, not $35.00 | ChatGPT review of lease template |
| 2026-07-01 | Starter placeholder created | Gabriel |
| 2026-07-01 | Updated with values observed in committed Late Fee Guard and Returned Payment Webhook code | Pending verification against final lease |
