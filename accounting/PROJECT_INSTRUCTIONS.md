# ChatGPT and Codex accounting-source instructions

Use these rules whenever this repository supports a GH Real Estate accounting, bookkeeping, tax, or financial-reporting question.

1. Identify the transaction date or tax year, entity, property/unit, payment method, signed agreement, and reporting basis before reaching a conclusion.
2. State which question is being answered: operational bookkeeping, US GAAP financial statements, federal income tax, Kansas tax, local compliance, or lease/legal treatment.
3. Start with `accounting/FASB_APPLICABILITY_INDEX.md`, `accounting/ACCOUNTING_POLICY_MATRIX.md`, and `accounting/manifests/fasb_topic_registry.json`. For tax questions, first read `accounting/TAX_PROFILE_ASSUMPTIONS.md`, `accounting/TAX_OPPORTUNITY_AND_COMPLIANCE_MATRIX.md`, and `accounting/manifests/tax_authority_registry.json`. For public law, also use `legal/CURRENT_AUTHORITY_INDEX.md` and `legal/manifests/authority_registry.json`.
4. Separate four conclusions when relevant: clean book treatment, federal tax treatment, Kansas/local treatment, and contract/lease treatment.
5. Cite an ASC topic or locator only as a locator. Do not invent paragraph numbers or quote FASB text from memory. Verify exact paragraphs, effective dates, scope exceptions, transition provisions, and private-company alternatives through authorized live access before a material GAAP assertion.
6. Never treat an Accounting Standards Update, exposure draft, FASB project page, IRS publication, FAQ, Zoho account name, GH policy, or retrieved source fingerprint as if it were a binding statute or the Codification itself.
7. When GAAP and tax differ, preserve clean books and identify a book-tax adjustment. Do not force the Zoho ledger to equal the tax return.
8. For household tax questions, treat `married` and `spouse has W-2 wages` as routing facts only. Do not assume MFJ, MFS, a withholding amount, a passive-loss result, QBI eligibility, or NIIT exposure without the complete return facts and CPA review.
9. Do not store spouse/employer names, home address, W-2s, returns, taxpayer identifiers, wage/withholding amounts, or identifiable personal tax workpapers in GitHub.
10. For rent, fees, deposits, refunds, and chargebacks, use the executed lease for that tenant and the applicable Kansas law. A target fee policy or Zoho item does not establish enforceability.
11. For repairs, renovations, appliances, and closing costs, require the invoice, scope, affected building system, unit of property, related work, acquisition date, placed-in-service date, and payment source before classification.
12. For security and holding deposits, require tenant-level liability records, receipt and disposition dates, signed terms, deductions, refund evidence, and unclaimed-property follow-up.
13. For vendor reporting, require a current W-9, payee classification, amount, calendar year, payment method, and card/third-party-network status.
14. Do not use candidate content from an unmerged branch, pull request, monitor report, proposal, draft form, or overdue registry entry as approved current authority.
15. A tax-monitor alert requires a reviewer to identify what changed, its authority weight, effective date, affected tax year, applicability, evidence, election/form impact, book-tax adjustment, and CPA/counsel gate. The automation never updates a tax conclusion itself.
16. Never expose tenant PII, bank credentials, tax identifiers, access tokens, or private documents in repository content, prompts, examples, logs, or reports.
17. End material recommendations with a verification block: sources used, authority weight, assumptions, missing evidence, proposed entry, tax adjustment, effective-date check, and CPA/counsel escalation trigger.

## Required answer labels

Use these labels where applicable:

- **Book treatment** — accrual/GAAP-like operating ledger treatment.
- **US GAAP** — only after scope and effective-date verification.
- **Federal tax** — return treatment and book-tax difference.
- **Kansas/local** — state or local tax, landlord, licensing, or unclaimed-property treatment.
- **Evidence required** — records needed before posting or filing.
- **Review required** — CPA, tax preparer, or Kansas counsel trigger.

## FASB research sequence

For each candidate topic, verify the relevant Codification section types in this order:

1. `15` Scope and Scope Exceptions.
2. `20` Glossary.
3. `25` Recognition.
4. `30` Initial Measurement.
5. `35` Subsequent Measurement.
6. `40` Derecognition.
7. `45` Other Presentation Matters.
8. `50` Disclosure.
9. `55` Implementation Guidance and Illustrations.
10. `65` Transition and Open Effective Date Information.

Also review `00` Status, `05` Overview and Background, `10` Objectives, `60` Relationships, and any SEC or private-company content only when relevant. Not every topic contains every section.

## Baseline prompt for a ChatGPT Project

> Treat the connected `GH-Real-Estate/gh-real-estate-ops-code` repository as a dated internal research and policy-control layer, not as authoritative law, a tax optimizer, or a substitute for the FASB Codification. Start with `accounting/PROJECT_INSTRUCTIONS.md`, `accounting/TAX_PROFILE_ASSUMPTIONS.md`, `accounting/TAX_OPPORTUNITY_AND_COMPLIANCE_MATRIX.md`, `accounting/FASB_APPLICABILITY_INDEX.md`, `accounting/ACCOUNTING_POLICY_MATRIX.md`, `accounting/SOURCE_GAPS.md`, and the accounting manifests. For public law, use the approved `legal/` library. Separate book, GAAP, federal tax, Kansas/local, and lease conclusions. Do not quote or reconstruct copyrighted FASB text, invent ASC paragraphs, or silently apply proposed, superseded, unreviewed, overdue, or monitor-only material. Live official authority and reviewed professional conclusions control.

