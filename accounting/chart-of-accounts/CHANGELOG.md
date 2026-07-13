# Chart of accounts changelog

## 2026-07-13 revision 2 — Revised live Zoho reconciliation

- Reconciled `COA Final Revised.xlsx` to the repository without committing its banking identifiers.
- Removed the duplicate Lease Termination Fee Income account and retained `4000.10.03 Early Termination / Lease Buyout Income`.
- Re-coded the remaining tenant-fee children to a unique, contiguous `4000.10.01`–`.07` sequence.
- Renamed `6130.02` to Building Improvement Depreciation, added live conditional `6130.03 Land Improvement Depreciation`, and moved appliance/furniture/equipment depreciation to `6130.04`.
- Retained the unresolved controls for entity segregation, Account-ID history, `1590.02` building-only scoping, system/workflow descriptions, and post-recode item/automation verification.

## 2026-07-13 — Live Zoho reconciliation

- Reconciled the repository to the uploaded 185-account Zoho export: 182 active and three inactive accounts.
- Added an exact sanitized live snapshot while excluding the raw workbook and `Account #` field.
- Replaced stale proposed codes/IDs with live values, including `2200.04`, `4000.20`, `4400.03`, `6990.15`, `7990`, `7990.01`, and `1590.04`.
- Restored the live contiguous tenant-fee sequence `4000.10.01` through `.08` and documented the `.03/.05` termination-income overlap.
- Added governance corrections for maintenance supplies, tenant-fee parent wording, system/adjustment controls, debt classification, repairs-versus-capitalization, leasing costs, gifts, and legacy deposit income.
- Preserved conditional `6130.04 Land Improvement Depreciation` and the broader event-triggered account watchlist.
- Flagged owner personal feeds/card, the inactive Sylvara feed, and repurposed Account IDs for immediate live-Zoho verification.

## 2026-07-12 — Ultimate-final governance edition

- Published the initial 183-row governance master, conditional-account register, authority crosswalk, and manifest.
