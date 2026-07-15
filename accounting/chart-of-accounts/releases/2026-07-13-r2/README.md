# GH Real Estate chart of accounts

**Current reconciliation:** 2026-07-13 revision 2  
**Property:** 9401 Nieman Road, Overland Park, Kansas 66214  
**System:** Zoho Books

This directory separates **what is currently in Zoho** from **what GH should treat as the accounting-governance master**:

- `current/zoho_live_chart_of_accounts_sanitized.csv` — 185-row sanitized live snapshot with deterministic public Account-ID aliases, excluding bank-account numbers and mileage/import-only fields.
- `current/final_chart_of_accounts.csv` — the same 185 live accounts and public aliases with governance roles, recommended statuses, reporting mappings, and corrected control descriptions.
- `current/conditional_accounts.csv` — accounts that are live-but-gated or should be created only after a documented transaction trigger.
- `current/authority_crosswalk.csv` — accounting, tax, legal, and workflow cross-checks.
- `current/reconciliation_audit.md` — unresolved live-Zoho actions and substantive audit findings.
- `current/manifest.json` — counts, hashes, provenance, and security controls.
- `CHANGELOG.md` — release history.
- `releases/2026-07-13/` — immutable first reconciliation.
- `releases/2026-07-13-r2/` — immutable revised snapshot, governance master, audit, and manifest.

The raw workbook is not committed because it contains banking identifiers in its `Account #` column. The sanitized live CSV is the current-tree repository record for codes, names, types, statuses, parents, descriptions, and public Account-ID aliases. Live Zoho Account IDs existed in this repository before public redaction, so the alias mapping remains recoverable from public Git history and PR diffs. Treat those IDs and aliases as public, non-secret identifiers; private runtime configuration must remain outside GitHub and must never rely on identifier secrecy for authorization.

## Current status

- 185 live accounts: 182 active, three inactive.
- No duplicate IDs, names, or nonblank codes; no orphan parents or formula errors.
- The duplicate termination-income account is resolved and depreciation expense is now separated among building improvements, land improvements, and appliances/equipment.
- Immediate review remains required for personal/other-entity feeds, repurposed Zoho Account IDs, `1590.02` building-only scoping, and item/automation remapping after the live code changes.
- `2200.03 Tenant Deposits Held` remains the single refundable-deposit liability control; tenant/unit/deposit-type subledger detail is mandatory.

## Authority boundary

Start with `accounting/CURRENT_AUTHORITY_INDEX.md`, `accounting/PROJECT_INSTRUCTIONS.md`, `accounting/FASB_APPLICABILITY_INDEX.md`, `accounting/ACCOUNTING_POLICY_MATRIX.md`, and `legal/CURRENT_AUTHORITY_INDEX.md`. The repository stores ASC locators and original GH analysis, not copied FASB Codification text. Transaction facts, signed agreements, current law, and professional review control material conclusions.
