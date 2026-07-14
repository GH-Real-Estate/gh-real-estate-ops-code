# GH accounting authority release — current index

**Authority baseline current through:** July 12, 2026  
**Sanitized tax profile checked through:** July 13, 2026  
**Property:** 9401 Nieman Road, Overland Park, Kansas 66214  
**Release status:** Approved dated sourcebook baseline with a governed tax-review extension

> Internal accounting and tax research aid. Live official authority, signed agreements, filed elections, complete return facts, and reviewed professional conclusions control.

## Approved sourcebook release

- 4 searchable Project Source PDFs.
- 33 compiled pages.
- 114 federal, GAAP-locator, Kansas, Overland Park, and Johnson County source-register records.
- 54 FASB topics classified as baseline, transaction-triggered, future-structure, or currently not applicable.
- Machine-readable review dates and licensing controls.
- Automated validation and monthly human-review reminders.

## Governed tax-review extension

- `TAX_PROFILE_ASSUMPTIONS.md` stores sanitized routing facts only; no taxpayer identifiers, employer identity, wage amounts, returns, or workpapers.
- `TAX_OPPORTUNITY_AND_COMPLIANCE_MATRIX.md` ranks practical tax decisions, evidence, CPA gates, and kill criteria.
- `manifests/tax_authority_registry.json` identifies the focused official federal, Kansas, Johnson County, Overland Park, and Mission sources that require recurring review.
- `scripts/check_tax_sources.py` validates the registry, retrieves official sources, records fingerprints and availability, and reports due reviews.
- `.github/workflows/tax-authority-review.yml` runs January 15 and July 15 and opens or updates one review issue when a source changed, failed retrieval, or is due.

The extension does not change the approved July 12 sourcebook text. Any substantive sourcebook or tax-policy update requires reviewed effective dates, affected tax years, a changelog entry, and a pull request.

## Project Source upload order

| Order | File | Pages | SHA-256 |
|---:|---|---:|---|
| 0 | `00_GH_Accounting_Authority_Map_and_Project_Protocol_2026-07-12.pdf` | 8 | `2a3f74d4db36c5280cef3cfba2f2f9c7b48fb5f2a537a17ec59624f38b96041e` |
| 1 | `01_GH_Federal_Rental_Tax_and_US_GAAP_Sourcebook_2026-07-12.pdf` | 12 | `22e0cd7b2359269d224d4ebd4edda99b7f458b793525f4d547ec1bad3ff8df14` |
| 2 | `02_GH_Kansas_Rental_Accounting_and_Tax_Law_Sourcebook_2026-07-12.pdf` | 8 | `4ab54c5531dc1d7925a8f2d50bff037d0d33b0e94ff45e448f9069abda1b5782` |
| 3 | `03_GH_Overland_Park_and_Johnson_County_Compliance_Sourcebook_2026-07-12.pdf` | 5 | `d9add335d77ffb0d42e23db43ea09c75d0d54f3c3c8bb827c20e1fe67b9297ed` |

Upload or replace the four files together. A repository change does not silently refresh a PDF already pinned in a ChatGPT Project.

## Retrieval order

1. `accounting/PROJECT_INSTRUCTIONS.md`
2. `accounting/TAX_PROFILE_ASSUMPTIONS.md` for tax questions
3. `accounting/TAX_OPPORTUNITY_AND_COMPLIANCE_MATRIX.md` for tax planning and CPA gates
4. `accounting/FASB_APPLICABILITY_INDEX.md`
5. `accounting/ACCOUNTING_POLICY_MATRIX.md`
6. `accounting/manifests/tax_authority_registry.json` and applicable live official source
7. `accounting/manifests/fasb_topic_registry.json`
8. Applicable `accounting/text/current/` sourcebook text
9. `legal/CURRENT_AUTHORITY_INDEX.md` and official public-law source
10. Authorized live Codification access for exact FASB requirements

## Status rules

- **Baseline:** review whenever GAAP financial statements are prepared or claimed.
- **Transaction-triggered:** activate only when the stated fact exists.
- **Future-structure:** reassess after a significant ownership, financing, or business-model change.
- **Currently not applicable:** do not apply under present facts; retain the trigger.
- **Review due:** retrieve and compare the current official source, identify effective dates and affected tax years, and obtain the required reviewer approval.
- **Overdue:** locator may remain useful, but no material currentness assertion may rely on it until reviewed.

## FASB content boundary

The repository contains no Codification text. It stores only topic locators, original GH analysis, review metadata, and dated sourcebooks that summarize relevant areas. See `accounting/policies/FASB_RESEARCH_AND_LICENSING_POLICY.md`.

