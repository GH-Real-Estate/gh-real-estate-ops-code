# GH Real Estate Accounting Authority Library

This directory is the version-controlled accounting research and policy-control layer for **GH Real Estate, LLC** and its fourplex at **9401 Nieman Road, Overland Park, Kansas 66214**.

The approved authority baseline is checked through **July 12, 2026**. The sanitized household/business tax profile is checked through **July 13, 2026**. The library is designed for GitHub history, pull-request review, ChatGPT connector retrieval, and generation of dated Project Source PDFs.

## What this library does

- Separates US GAAP, federal tax, Kansas tax and landlord rules, local administration, signed agreements, and GH internal policy.
- Maps all FASB topics that are presently relevant or could become relevant through a realistic GH transaction or growth trigger.
- Provides transaction-level accounting controls and evidence requirements.
- Preserves dated sourcebooks, machine-readable manifests, review dates, and change history.
- Maintains a sanitized tax operating profile and a prioritized tax opportunity/compliance decision register.
- Retrieves focused official federal, Kansas, Johnson County, Overland Park, and Mission tax sources on a semiannual review calendar.
- Automates validation and review reminders without silently changing an accounting or tax conclusion.

## What this library does not do

- It does not reproduce the FASB Accounting Standards Codification.
- It does not make ChatGPT output authoritative, legally binding, GAAP-compliant, or tax-return ready by itself.
- It does not ingest every tax law, calculate the maximum lawful deduction, make an election, file a return, or replace a CPA.
- It does not replace live-source verification, the signed lease, loan documents, a CPA engagement, or legal advice.
- It is not a tenant ledger, lease vault, bank-record archive, personal tax vault, or tax workpaper repository.

## Start here

1. Read [`CURRENT_AUTHORITY_INDEX.md`](CURRENT_AUTHORITY_INDEX.md).
2. Read [`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md).
3. For tax questions, read [`TAX_PROFILE_ASSUMPTIONS.md`](TAX_PROFILE_ASSUMPTIONS.md) and [`TAX_OPPORTUNITY_AND_COMPLIANCE_MATRIX.md`](TAX_OPPORTUNITY_AND_COMPLIANCE_MATRIX.md).
4. Use [`FASB_APPLICABILITY_INDEX.md`](FASB_APPLICABILITY_INDEX.md) to identify candidate GAAP topics.
5. Use [`ACCOUNTING_POLICY_MATRIX.md`](ACCOUNTING_POLICY_MATRIX.md) for transaction treatment and evidence.
6. Check [`SOURCE_GAPS.md`](SOURCE_GAPS.md) before reaching a material conclusion.
7. Read `manifests/fasb_topic_registry.json` for machine-readable GAAP applicability and review metadata.
8. Read `manifests/tax_authority_registry.json` for the focused official tax-source review universe.
9. For public law, search the existing [`../legal/`](../legal/) authority library; live official law controls.

## Authority hierarchy

1. Current statutes, regulations, municipal code, and controlling decisions within their scope.
2. Signed leases, loan documents, filed elections, contracts, and court or agency orders.
3. FASB Accounting Standards Codification when US GAAP financial statements are required or elected.
4. Published administrative guidance, forms, instructions, and official explanations according to their legal weight.
5. CPA-approved GH accounting and tax policies that do not conflict with higher authority.
6. Zoho configuration, automation, examples, and AI-generated analysis.

US GAAP and federal income-tax accounting are different frameworks. A clean book entry may require a tax adjustment, and a tax rule must not be mislabeled as GAAP.

## Directory map

```text
accounting/
  README.md
  CURRENT_AUTHORITY_INDEX.md
  PROJECT_INSTRUCTIONS.md
  FASB_APPLICABILITY_INDEX.md
  ACCOUNTING_POLICY_MATRIX.md
  TAX_PROFILE_ASSUMPTIONS.md
  TAX_OPPORTUNITY_AND_COMPLIANCE_MATRIX.md
  CHANGELOG.md
  SOURCE_GAPS.md
  policies/
    FASB_RESEARCH_AND_LICENSING_POLICY.md
  manifests/
    fasb_topic_registry.json
    sourcebook_release.json
    tax_authority_registry.json
  generated/project-sources/current/
  text/current/
  scripts/
    validate_authority_registry.py
    review_due.py
    check_tax_sources.py
  tests/
    test_check_tax_sources.py
```

## Version and review rules

- `CURRENT` means approved for the dated release, not guaranteed current forever.
- An automated alert, URL fingerprint, or retrieval error is a review candidate, not an accounting or tax conclusion.
- The tax monitor never promotes a retrieved source, changes a policy, rewrites a sourcebook, modifies the chart of accounts, or posts to Zoho.
- FASB topic locators and GH-authored summaries may be stored; copied Codification text may not be stored without explicit written permission covering the intended AI use.
- Exact paragraph citations, effective dates, transition provisions, scope exceptions, and private-company alternatives require live verification before a material GAAP assertion.
- Tax-year forms, indexed amounts, elections, and filing positions require the final product for the applicable year and CPA review.
- Proposed standards, draft forms, and exposure drafts are monitoring-only until issued and effective for GH's reporting basis and period.
- Do not auto-merge accounting- or tax-authority currentness changes.

## Current working scope

- Kansas single-member LLC; federal disregarded-entity treatment is assumed but must be verified from the latest return and elections.
- One long-term residential fourplex; all units are treated as rental operations for current workflows, with historical personal-use conversion dates still requiring asset-level documentation.
- The owner is married and both spouses reside in Mission, Kansas; the spouse has W-2 wages. MFJ versus MFS remains a return-level decision.
- No employees, short-term lodging, federal housing program, REIT election, outside investor, or GAAP lender covenant is assumed unless verified.
- Zoho Books is the operating ledger. It does not determine legal, tax, or GAAP treatment.

## FASB source restriction

The Financial Accounting Foundation and FASB impose copyright and access restrictions, including restrictions on using site content with generative AI. See the official [FAF Terms of Use](https://accountingfoundation.org/page/detail?pageId=%2Fterms-of-use.html) and [FASB copyright information](https://www.fasb.org/copyright-information). This repository therefore stores locators, original summaries, applicability notes, and review evidence—not Codification text, screenshots, or print exports.
