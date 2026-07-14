# Accounting authority library changelog

## 2026-07-13 - Add governed official-index discovery

- Added daily discovery across 9 configured FASB, IRS, Treasury, and Kansas Department of Revenue publication indexes while retaining the separate monthly stored-review-date calendar.
- Restricted all FASB discovery to metadata-only storage and required authorized live research plus CPA or qualified accounting review for exact GAAP conclusions.
- Added fail-closed `current`, `review_required`, and `degraded` discovery states, rolling-window feed semantics, draft candidate pull requests, structured review evidence, and protected evidence promotion.
- Prohibited automatic changes to accounting policy, tax treatment, books, chart of accounts, or runtime automations from discovery output.

This automation change does not modify, reapprove, or advance the July 12, 2026 accounting release.

## 2026-07-12 — Initial approved release

- Added four dated accounting, federal tax, Kansas, and local sourcebooks totaling 33 pages and 114 source-register records.
- Added searchable text counterparts for GitHub connector retrieval.
- Added a 54-topic FASB applicability registry covering current GAAP reporting and realistic future GH triggers.
- Added transaction-policy and evidence matrices for rent, deposits, fees, repairs, improvements, assets, debt, escrow, owner equity, vendors, casualty, sale, payroll, grants, and software.
- Added explicit FAF/FASB licensing controls; no Codification text, print exports, screenshots, or scraped content are stored.
- Added release validation and a monthly human-review calendar that opens an issue without changing accounting policy.

This entry records a research baseline, not a CPA opinion, tax return position, or representation that no authority changed after the verification date.

