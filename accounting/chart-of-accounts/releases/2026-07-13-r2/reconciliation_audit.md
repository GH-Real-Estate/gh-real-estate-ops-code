# GH chart of accounts reconciliation audit — 2026-07-13 revision 2

## Outcome

The revised Zoho export is structurally sound and materially improved. It contains 185 unique accounts (182 active, three inactive), 182 unique nonblank codes, no duplicate IDs/names/codes, no orphan parents, and no formula errors. The exact live state is preserved in `zoho_live_chart_of_accounts_sanitized.csv`; the governance-corrected view is `final_chart_of_accounts.csv`.

The raw workbook is intentionally excluded because its `Account #` column still contains unmasked banking identifiers.

## Improvements confirmed

- Removed the overlapping `Lease Termination Fee Income` account and retained one clear `4000.10.03 Early Termination / Lease Buyout Income` account.
- Added `6130.03 Land Improvement Depreciation`, renamed `6130.02` to Building Improvement Depreciation, and moved appliance/furniture/equipment depreciation to `6130.04`.
- Preserved unique, contiguous tenant-fee codes `4000.10.01` through `.07`.

## Immediate actions still required in Zoho

1. **Entity segregation:** review active `2100 Personal Credit Card – Owner`, uncoded `Owner - Checking`, and uncoded `Owner - Savings`. If personal or mixed-use, reclassify supported GH activity through the appropriate due-to/from-member or equity account, clear the balances, disconnect feeds, and inactivate. Keep `Sylvara.ai - Checking` inactive, zero, disconnected, and outside GH reports.
2. **Account-ID verification:** inspect transaction history and workflow/system mappings for IDs `PUBLIC-ACCT-0028`, `PUBLIC-ACCT-0017`, `PUBLIC-ACCT-0012`, `PUBLIC-ACCT-0013`, `PUBLIC-ACCT-0011`, and `PUBLIC-ACCT-0175`. Several visible names/codes differ materially from the prior ID registry. If an ID has history or a locked system role, do not repurpose it merely by renaming.
3. **Description/workflow cleanup:** apply the governance wording for `4000.10`, `4000.10.06`, `4903`, `4906`, `6100.02`, `6990.11`, `6990.13`, `2700`, repairs-versus-capitalization, leasing-cost scope, and current-versus-long-term debt. Rename `1590.02` to Accumulated Depreciation - Building Improvements when Zoho permits.
4. **Item and automation remapping:** confirm every Zoho item, recurring invoice, workflow, bank rule, integration, and report follows the revised `4000.10.03`–`.07` and `6130.03`–`.04` codes.
5. **Legacy deposit income:** keep `4300.02` and `4300.03` inactive, zero, and unmapped; use `2200.03` for refundable deposits and `4000.13` only when amounts are legally and finally retained.

## Correct as structured

- `2200.03 Tenant Deposits Held` and `2600 Unearned Rent Revenue` are correctly separate.
- `2200.04` current mortgage portion is correct in substance when reclassified out of `2800.01` rather than duplicated.
- `6130.02`, `6130.03`, and `6130.04` now provide a clean depreciation-expense split.
- The chosen `6130.03` land / `6130.04` appliance code order is acceptable. Swapping them would align with the existing `1590.04` land / `1590.03` equipment contra-asset sequence, but consistency and correct mapping matter more than the digits.
- `4000.11`, `4000.13`, `4000.20`, `1300.03`, `3000.01`, `3000.02`, `4400.03`, and `7990/7990.01` are appropriate subject to their stated controls.
- One combined refundable-deposit control is permissible when tenant, unit, lease, and deposit type are maintained in the subledger.

## Professional-standard assessment

The chart design and repository governance exceed what is typical for a single fourplex and are suitable for professional bookkeeping and scalable portfolio reporting. The live Zoho implementation is **near professional standard but not yet fully audit-ready** until entity segregation and Account-ID/workflow verification are completed. Granularity alone does not establish GAAP compliance; reconciliations, subledgers, fixed-asset schedules, source documents, close controls, and reviewed posting practices remain essential.

## Conditional watchlist

The conditional register retains accounts for nonlease credit losses, insurance claims, deferred leasing costs, Kansas unclaimed property, financing costs, lease collectibility adjustments, dispositions, personal-property tax, and impairment. These are not missing merely because no triggering event presently exists.
