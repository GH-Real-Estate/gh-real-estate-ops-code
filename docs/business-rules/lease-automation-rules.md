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
| Interest start | More than 30 days after original due date; first eligible day is day 31 | Matches lease template Section 3.6 |
| Interest rate | `10.00%` APR in `Monthly_Interest_Billing.deluge` | Matches lease template Section 3.6 |
| Interest frequency | Separate monthly scheduled billing; simple interest only | Operational design; lease allows simple interest until paid |
| Interest minimum invoice amount | `$10.00` | Operational threshold, not a lease value |
| Returned-payment fee | `RETURNED_FEE_AMOUNT=30.00` / source default `$30.00` | Matches lease template Section 3.7: `$30.00 or maximum lawful amount, whichever is less` |
| Non-approved payment method admin fee | Not automated in current code | Lease template Section 3.3 allows `$25.00`; leave out of automation unless explicitly added |

## Automation Constraints

- Fees must be idempotent.
- No duplicate late-fee, monthly-interest, or returned-payment fee invoices.
- Zoho Books remains the accounting source of truth.
- Late Fee Guard owns only late fees.
- Monthly Interest Billing owns only delinquent-rent interest.
- Returned-payment / NSF RF invoices are owned by the Zoho Payments webhook running in Zoho Catalyst.
- All production changes must be documented in `docs/runbooks/deployment-log.md`.
- Do not use this file as legal advice. Use it only as an automation checklist against the final lease.

## Change Log

| Date | Change | Verified By |
|---|---|---|
| 2026-07-06 | Verified late-fee, interest, and returned-payment fee values against the uploaded 2026-06-30 lease template; confirmed RF fee is $30.00, not $35.00 | ChatGPT review of lease template |
| 2026-07-01 | Starter placeholder created | Gabriel |
| 2026-07-01 | Updated with values observed in committed Late Fee Guard and Returned Payment Webhook code | Pending verification against final lease |
