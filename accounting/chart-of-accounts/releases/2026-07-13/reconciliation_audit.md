# GH chart of accounts reconciliation audit — 2026-07-13

## Outcome

The uploaded Zoho export is structurally sound but is **not unconditionally approved as final**. It contains 185 unique accounts (182 active, three inactive), 182 unique nonblank codes, no duplicate IDs/names/codes, no orphan parents, and no formula errors. The exact live state is preserved in `zoho_live_chart_of_accounts_sanitized.csv`; the governance-corrected view is `final_chart_of_accounts.csv`.

The raw workbook is intentionally excluded because its `Account #` column contains unmasked banking identifiers.

## Immediate actions required in Zoho

1. **Entity segregation:** review active `2100 Personal Credit Card – Owner`, uncoded `Owner - Checking`, and uncoded `Owner - Savings`. If personal or mixed-use, reclassify supported GH activity through the appropriate due-to/from-member or equity account, clear the balances, disconnect feeds, and inactivate. Keep `Sylvara.ai - Checking` inactive, zero, disconnected, and outside GH reports.
2. **Account-ID verification:** inspect transaction history and workflow/system mappings for IDs `PUBLIC-ACCT-0028`, `PUBLIC-ACCT-0017`, `PUBLIC-ACCT-0012`, `PUBLIC-ACCT-0013`, `PUBLIC-ACCT-0011`, and `PUBLIC-ACCT-0175`. Several visible names/codes differ materially from the prior ID registry. If an ID has history or a locked system role, do not repurpose it merely by renaming.
3. **Termination income overlap:** define a non-overlapping signed-lease distinction between `4000.10.03` and `4000.10.05`, or remap/clear/inactivate the duplicate. `4000.10.03` had no live description.
4. **Land-improvement depreciation:** scope `1590.02` and `6130.02` to building improvements. Create `6130.04 Land Improvement Depreciation` only when separately depreciable land-improvement basis exists.
5. **Description/workflow cleanup:** correct `4000.10`, `4903`, `4906`, `6100.02`, `6990.11`, `6990.13`, `2700`, repair-capitalization warnings, leasing-cost scope, and current-versus-long-term debt descriptions. The governance master contains proposed corrected wording.
6. **Legacy deposit income:** keep `4300.02` and `4300.03` inactive, zero, and unmapped; use `2200.03` for refundable deposits and `4000.13` only when amounts are legally and finally retained.

## Correct as structured

- `2200.03 Tenant Deposits Held` and `2600 Unearned Rent Revenue` are correctly separate.
- `2200.04` current mortgage portion is correct in substance when it is reclassified out of `2800.01` rather than duplicated.
- `4000.11`, `4000.13`, `4000.20`, `1300.03`, `3000.01`, `3000.02`, `4400.03`, and `7990/7990.01` are appropriate subject to their stated controls.
- One combined refundable-deposit control is permissible when tenant, unit, lease, and deposit type are maintained in the subledger.

## Conditional watchlist

The conditional register retains accounts for nonlease credit losses, insurance claims, deferred leasing costs, Kansas unclaimed property, financing costs, lease collectibility adjustments, dispositions, personal-property tax, and impairment. These are not missing merely because no triggering event presently exists.
