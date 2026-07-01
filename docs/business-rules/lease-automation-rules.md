# Lease Automation Rules

This file summarizes only the lease rules needed by code. It is not the lease. The final signed lease/template in Zoho Contracts or WorkDrive remains the legal source document.

## Required Before Live Automation

- [ ] Confirm this file matches the final signed lease/template.
- [ ] Confirm the late-fee code matches this file.
- [ ] Confirm Zoho Books item/template/custom field IDs are updated.
- [ ] Confirm returned-payment logic is separate from late-fee logic.
- [ ] Confirm every fee/interest value below is enforceable and matches the final lease.

## Current Values Observed In Code

These are code-observed values, not legal verification.

| Rule | Current Code Value | Verification Status |
|---|---:|---|
| Rent due date basis | Source invoice `due_date`; code comments assume monthly rent invoices are due on the 1st | Verify against final lease and Zoho invoice setup |
| Rent due time zone | Central Time behavior required; schedule should run after 5:00 p.m. CT on assessment days | Verify Zoho runtime behavior |
| Late threshold #1 | `D5` = `due_date + 4 days`, after 5:00 p.m. CT | Verify against final lease |
| Late fee #1 | `5%` of unpaid rent balance, subject to cap logic | Verify against final lease |
| Late threshold #2 | `D10` = `due_date + 9 days`, after 5:00 p.m. CT | Verify against final lease |
| Late fee #2 | `5%` of unpaid rent balance, subject to cap logic | Verify against final lease |
| Per-stage fixed cap | Disabled in current code | Confirm intended |
| Total late-fee cap | `10%` of unpaid rent for that month | Verify against final lease |
| Interest start | Day `31` after due date | Verify against final lease |
| Interest rate | `10.00%` APR in current Late Fee Guard | Verify against final lease and applicable law before live use |
| Interest frequency | Every `30` days after first eligible run | Verify intended billing behavior |
| Interest minimum invoice amount | `$1.00` | Verify intended billing behavior |
| Returned-payment fee | Webhook code default is `$30.00` unless environment variable overrides it | Verify against final lease before live use |
| Non-approved payment method admin fee | Not automated in current code | Leave out of automation unless explicitly added |

## Automation Constraints

- Fees must be idempotent.
- No duplicate late-fee or returned-payment fee invoices.
- Zoho Books remains the accounting source of truth.
- All production changes must be documented in `docs/runbooks/deployment-log.md`.
- Do not use this file as legal advice. Use it only as an automation checklist against the final lease.

## Change Log

| Date | Change | Verified By |
|---|---|---|
| 2026-07-01 | Starter placeholder created | Gabriel |
| 2026-07-01 | Updated with values observed in committed Late Fee Guard and Returned Payment Webhook code | Pending verification against final lease |
