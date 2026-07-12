# 2026-07-12 — Version the GH accounting authority library in GitHub

## Decision

Store GH-authored accounting policy, tax/GAAP sourcebooks, FASB topic locators, applicability metadata, review dates, and searchable extracts under `accounting/` in the private GH Real Estate repository.

Do not store FASB Codification text, screenshots, print exports, scraped content, or licensed commercial guidance unless explicit written permission covers the repository and intended generative-AI use.

## Reason

GitHub provides reviewable history, hashes, automated validation, review reminders, and connector search. Dated PDFs provide a stable ChatGPT Project baseline. Machine-readable locators allow systematic scoping without creating an unauthorized substitute for the Codification.

## Controls

- Live authoritative source and effective-date research control over the registry.
- GAAP, federal tax, Kansas/local law, contract terms, internal policy, and Zoho configuration remain separately labeled.
- Automation validates and opens review issues; it does not interpret FASB changes or revise policy.
- Material conclusions require exact locator verification and CPA review.
- The `legal/` corpus remains the source for public housing and landlord law.
- No tenant records, signed leases, banking records, credentials, tax identifiers, or PII belong in the accounting library.

## Update model

1. Official notification or scheduled review creates a review item.
2. A reviewer checks authorized live sources and transaction facts.
3. A pull request updates locators, dates, original GH analysis, sourcebooks, and changelog.
4. Validation confirms registry integrity and sourcebook hashes.
5. Approved files are merged and refreshed in the ChatGPT Project as a single dated release.

