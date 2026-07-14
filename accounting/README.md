# GH Real Estate Accounting Authority Library

This directory is the version-controlled accounting research and policy-control layer for **GH Real Estate, LLC** and its fourplex at **9401 Nieman Road, Overland Park, Kansas 66214**.

The approved baseline is checked through **July 12, 2026**. It is designed for GitHub history, pull-request review, ChatGPT connector retrieval, and generation of dated Project Source PDFs.

## What this library does

- Separates US GAAP, federal tax, Kansas tax and landlord rules, local administration, signed agreements, and GH internal policy.
- Maps all FASB topics that are presently relevant or could become relevant through a realistic GH transaction or growth trigger.
- Provides transaction-level accounting controls and evidence requirements.
- Preserves dated sourcebooks, machine-readable manifests, review dates, and change history.
- Automates validation and review reminders without silently changing an approved accounting conclusion.

## What this library does not do

- It does not reproduce the FASB Accounting Standards Codification.
- It does not make ChatGPT output authoritative, legally binding, GAAP-compliant, or tax-return ready by itself.
- It does not replace live-source verification, the signed lease, loan documents, a CPA engagement, or legal advice.
- It is not a tenant ledger, lease vault, bank-record archive, or tax workpaper repository.

## Start here

1. Read [`CURRENT_AUTHORITY_INDEX.md`](CURRENT_AUTHORITY_INDEX.md).
2. Read [`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md).
3. Use [`FASB_APPLICABILITY_INDEX.md`](FASB_APPLICABILITY_INDEX.md) to identify candidate GAAP topics.
4. Use [`ACCOUNTING_POLICY_MATRIX.md`](ACCOUNTING_POLICY_MATRIX.md) for transaction treatment and evidence.
5. Check [`SOURCE_GAPS.md`](SOURCE_GAPS.md) before reaching a material conclusion.
6. Read `manifests/fasb_topic_registry.json` for machine-readable applicability, review, and monitoring metadata.
7. For public law, search the existing [`../legal/`](../legal/) authority library; live official law controls.

## Authority hierarchy

1. Current statutes, regulations, municipal code, and controlling decisions within their scope.
2. Signed leases, loan documents, filed elections, contracts, and court or agency orders.
3. FASB Accounting Standards Codification when US GAAP financial statements are required or elected.
4. Published administrative guidance, forms, instructions, and official explanations according to their legal weight.
5. CPA-approved GH accounting policies that do not conflict with higher authority.
6. Zoho configuration, automation, examples, and AI-generated analysis.

US GAAP and federal income-tax accounting are different frameworks. A clean book entry may require a tax adjustment, and a tax rule must not be mislabeled as GAAP.

## Directory map

```text
accounting/
  README.md
  CURRENT_AUTHORITY_INDEX.md
  PROJECT_INSTRUCTIONS.md
  CURRENT_STATUS.json
  FASB_APPLICABILITY_INDEX.md
  ACCOUNTING_POLICY_MATRIX.md
  CHANGELOG.md
  SOURCE_GAPS.md
  policies/
    FASB_RESEARCH_AND_LICENSING_POLICY.md
  manifests/
    fasb_topic_registry.json
    sourcebook_release.json
  generated/project-sources/current/
  text/current/
  scripts/
    validate_authority_registry.py
    review_due.py
```

## Version and review rules

- `CURRENT` means approved for the dated release, not guaranteed current forever.
- An automated alert is a review candidate, not an accounting conclusion.
- FASB topic locators and GH-authored summaries may be stored; copied Codification text may not be stored without explicit written permission covering the intended AI use.
- Exact paragraph citations, effective dates, transition provisions, scope exceptions, and private-company alternatives require live verification before a material GAAP assertion.
- Proposed standards and exposure drafts are monitoring-only until issued and effective for GH's reporting basis and period.
- Do not auto-merge accounting-authority currentness changes.

## Automated discovery and review

`Authority Discovery` runs daily at `11:17 UTC` (and on manual dispatch) against 9 configured accounting official-source indexes: four public FASB publication/project/taxonomy indexes, IRS Internal Revenue Bulletins, Treasury releases, and three Kansas Department of Revenue indexes. It reports `current`, `review_required`, or `degraded`. These are discovery-run states only; they do not establish GAAP applicability, tax treatment, effective dates, or compliance.

FASB collection is strictly metadata-only: official locators, titles, identifiers, dates, and publisher status may be retained, but Codification text, screenshots, print exports, and scraped licensed content are prohibited. A CPA or qualified accounting reviewer must use authorized live FASB access to verify exact scope, paragraphs, effective dates, transition, elections, and implementation. Tax changes require tax-year-specific professional review.

`Accounting Authority Review Calendar` remains a separate monthly control at `13:41 UTC` on day 1. It checks stored review dates; it does not query or validate live Codification content. Daily discovery writes only candidate evidence under `authority/candidates/accounting/` and may open a draft pull request or degraded-source issue. It never edits this approved library, changes the books or automation, promotes a conclusion, or merges a pull request.

Recent-item sources marked `rolling-window` do not treat an item falling out of a publisher's limited recent-results page as withdrawn or missing. Any source retrieval or parser `error`, or missing configuration for a critical source, makes the run `degraded`, preserves the July 12, 2026 baseline, and requires live verification before a material GAAP or tax assertion. Review and promotion procedures are in [`../docs/runbooks/authority-refresh.md`](../docs/runbooks/authority-refresh.md).

## Current working scope

- Kansas single-member LLC; federal disregarded-entity treatment is assumed but must be verified from the latest return and elections.
- One long-term residential fourplex; all units are treated as rental operations for current workflows, with historical personal-use conversion dates still requiring asset-level documentation.
- No employees, short-term lodging, federal housing program, REIT election, outside investor, or GAAP lender covenant is assumed unless verified.
- Zoho Books is the operating ledger. It does not determine legal, tax, or GAAP treatment.

## FASB source restriction

The Financial Accounting Foundation and FASB impose copyright and access restrictions, including restrictions on using site content with generative AI. See the official [FAF Terms of Use](https://accountingfoundation.org/page/detail?pageId=%2Fterms-of-use.html) and [FASB copyright information](https://www.fasb.org/copyright-information). This repository therefore stores locators, original summaries, applicability notes, and review evidence—not Codification text, screenshots, or print exports.
