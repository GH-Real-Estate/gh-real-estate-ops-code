# GH Real Estate chart of accounts

**Current edition:** 2026-07-12 ultimate final cross-examined edition  
**Property:** 9401 Nieman Road, Overland Park, Kansas 66214  
**System:** Zoho Books

This directory is the GitHub-searchable, version-controlled chart-of-accounts source. It was reconciled against the approved accounting/legal authority corpus, the current GH operating and fee policies, and current official Zoho implementation documentation. It is an accounting governance aid—not a CPA opinion, tax return position, legal opinion, or substitute for live authoritative text.

## Files

- `current/final_chart_of_accounts.csv` — 183-row master catalog with exact account codes, parents, statuses, mappings, descriptions, and existing Account IDs.
- `current/conditional_accounts.csv` — 19 trigger-gated accounts: six already in the master catalog plus 13 additional realistic future accounts.
- `current/authority_crosswalk.csv` — authority-to-account cross-examination by operating area.
- `current/manifest.json` — release counts, hashes, and source controls.

The formatted governance workbook is `GH_Real_Estate_Ultimate_Final_Chart_of_Accounts_2026-07-12.xlsx` and is maintained as the user-facing edition. The CSV files are canonical for GitHub search, revision history, and automated comparisons.

## Final decisions

- Keep 183 master catalog rows; 176 are retained/system accounts and seven are new proposals.
- Create now only `7990` Non-Deductible Expenses – Tax Adjustment.
- Treat the other six proposed master accounts as conditional, not automatic creates.
- Stage 13 additional transaction-triggered accounts for collectibility scope, claims, CIP presentation, leasing costs, financing costs, Kansas unclaimed property and personal-property tax, dispositions, and impairment.
- Reconcile rather than force zero balances for A/R, A/P, undeposited funds, processor clearing, tax payable, unearned rent, vendor credits, and retained earnings.
- Use one `2200.03` Zoho Retainer control liability for refundable deposits with tenant/unit/deposit-type detail.
- Classify `4400.03` tenant late-payment interest only after signed-lease and tax review; do not hard-code Schedule B treatment.
- Treat operating-lease collectibility separately from ASC 326 nonlease credit losses; do not use generic bad-debt expense automatically.

## Activation tiers

1. **Create Now – Required** — create during the controlled cutover.
2. **Conditional – ...** — create/activate only after the stated fact, evidence, and review exist.
3. **Keep Active – System / Reconcile** — a legitimate supported balance may exist; reconcile to the named workflow/subledger.
4. **Keep Active – Parent / Do Not Post** — reporting parent only.
5. **Inactivate After Reclass / Locked / Zero** — preserve history, clear supported balances, and retire or leave unmapped as Zoho permits.

## Authority and licensing boundary

Start with `accounting/CURRENT_AUTHORITY_INDEX.md`, `accounting/PROJECT_INSTRUCTIONS.md`, `accounting/FASB_APPLICABILITY_INDEX.md`, `accounting/ACCOUNTING_POLICY_MATRIX.md`, and `legal/CURRENT_AUTHORITY_INDEX.md`. The chart stores ASC locators and original GH analysis only. Do not add FASB Codification text, screenshots, print exports, copied tables/definitions/examples, bulk exports, or reconstructed licensed material.

## Zoho implementation

This XLSX is a governance workbook, not a direct import file. Current Zoho help lists CSV, TSV, or XLS imports and matches duplicates by account name. Update existing accounts by Account ID through controlled manual/API work. Import or create only approved new accounts, parent-first, after a full export/backup.
