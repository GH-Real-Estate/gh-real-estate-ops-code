# GH Real Estate chart of accounts

**Current reconciliation:** 2026-07-13  
**Property:** 9401 Nieman Road, Overland Park, Kansas 66214  
**System:** Zoho Books

This directory separates **what is currently in Zoho** from **what GH should treat as the accounting-governance master**:

- `current/zoho_live_chart_of_accounts_sanitized.csv` — exact 185-row live snapshot from the uploaded export, excluding bank-account numbers and mileage/import-only fields.
- `current/final_chart_of_accounts.csv` — the same 185 live accounts and IDs with governance roles, recommended statuses, reporting mappings, and corrected control descriptions.
- `current/conditional_accounts.csv` — accounts that are live-but-gated or should be created only after a documented transaction trigger.
- `current/authority_crosswalk.csv` — accounting, tax, legal, and workflow cross-checks.
- `current/reconciliation_audit.md` — unresolved live-Zoho actions and substantive audit findings.
- `current/manifest.json` — counts, hashes, provenance, and security controls.
- `CHANGELOG.md` — release history.
- `releases/2026-07-13/` — immutable copy of the reconciled live snapshot, governance master, audit, and manifest.

The raw workbook is not committed because it contains banking identifiers in its `Account #` column. The sanitized live CSV is the exact repository record for codes, names, types, statuses, parents, descriptions, and Account IDs.

## Current status

- 185 live accounts: 182 active, three inactive.
- No duplicate IDs, names, or nonblank codes; no orphan parents or formula errors.
- Immediate review remains required for personal/other-entity feeds, repurposed Zoho Account IDs, overlapping termination-income accounts, and land-improvement depreciation structure.
- `2200.03 Tenant Deposits Held` remains the single refundable-deposit liability control; tenant/unit/deposit-type subledger detail is mandatory.

## Authority boundary

Start with `accounting/CURRENT_AUTHORITY_INDEX.md`, `accounting/PROJECT_INSTRUCTIONS.md`, `accounting/FASB_APPLICABILITY_INDEX.md`, `accounting/ACCOUNTING_POLICY_MATRIX.md`, and `legal/CURRENT_AUTHORITY_INDEX.md`. The repository stores ASC locators and original GH analysis, not copied FASB Codification text. Transaction facts, signed agreements, current law, and professional review control material conclusions.
