# Authority refresh governance

This directory is the control layer between automated source discovery and the approved legal or accounting libraries. It makes changes visible and reviewable; it does not let a crawler declare law, GAAP applicability, tax treatment, contract enforceability, or operational compliance.

## Trust model

The repository has three distinct layers:

1. **Discovery evidence** records what an allowlisted official publisher exposed at a particular time. New records always begin as `discovered`.
2. **Review candidates** preserve provenance, dates, diffs, licensing limits, impact mappings, and reviewer decisions. Candidate content stays outside approved current paths.
3. **Approved dated releases** are complete, human-reviewed snapshots. A monitor result never silently modifies one.

Official source material controls over repository extracts, summaries, classifications, machine output, and internal policy. A green workflow proves only the checks that workflow actually performed.

## Governed files

| File | Purpose |
|---|---|
| `legal/schemas/authority-record.schema.json` | Draft 2020-12 record contract for legal authority provenance, currentness, dates, rights, storage, review, and release state. |
| `accounting/schemas/accounting-authority-record.schema.json` | Draft 2020-12 record contract for accounting and tax authority metadata, applicability, currentness, rights, review, and implementation state. |
| `legal/CURRENT_STATUS.json` | Machine-readable status and limitations for the approved legal baseline. |
| `accounting/CURRENT_STATUS.json` | Machine-readable status and limitations for the approved accounting baseline. |
| `authority/impact_crosswalk.json` | Maps authority-domain signals to existing repository artifacts that require review or testing. |
| `authority/schemas/impact-crosswalk.schema.json` | Draft 2020-12 contract for the impact crosswalk. |
| `authority/schemas/promotion-validation-context.schema.json` | Contract for the immutable catalog, crosswalk, source revision, and reviewed-path evidence captured with each promoted discovery release. |
| `authority/schemas/promotion-release.schema.json` | Contract for the immutable promotion release record and its validation-context binding. |
| `.github/CODEOWNERS` | Requests GH Real Estate ownership review for authority content and related workflows. |

The existing July 12, 2026 registries remain the approved dated baselines. The new record schemas govern normalized refresh records; they do not retroactively imply that the older registry formats contain fields that were never collected.

## Currentness states

Legal records use bounded states:

- `discovered`
- `candidate`
- `change-detected`
- `awaiting-legal-review`
- `approved-current-through-date`
- `approved-historical`
- `superseded`
- `withdrawn`
- `source-unavailable`
- `review-overdue`
- `rejected`

Accounting records use bounded states:

- `discovered`
- `locator-mapped-dated-baseline`
- `official-change-detected`
- `awaiting-cpa-review`
- `reviewed-applicable`
- `reviewed-not-applicable`
- `effective-pending`
- `implemented`
- `source-unavailable`
- `review-overdue`
- `superseded`
- `rejected`

These states intentionally separate source discovery, currentness, applicability, reviewer approval, effective date, and implementation. There is no global `compliant` flag.

These are record-level governance states. The top-level result of each discovery run is separately limited to `current`, `review_required`, or `degraded`; none of those run states is a legal, GAAP, tax, or compliance conclusion.

## Promotion workflow

1. Poll only allowlisted official sources and preserve publisher identifiers and raw publisher status in metadata.
2. Record final URL, retrieval time, content type, hash or semantic comparison evidence, and any transport or parsing limitation.
3. Apply the most restrictive storage policy until licensing review is complete. Unknown rights mean metadata/link-only storage.
4. Compare the discovery candidate with the approved dated baseline. Preserve both versions; do not patch text into a synthetic consolidated authority.
5. Use `impact_crosswalk.json` to identify code, configuration, policy, document, and test surfaces requiring review.
6. Open a bounded pull request. Legal-effect and applicability decisions require qualified legal review; GAAP decisions require a CPA or qualified accounting reviewer using authorized FASB access; tax decisions require tax-year-specific professional review.
7. Record the effective-date analysis, applicability facts, licensing decision, reviewer decision, tests, any production configuration check, and one evidence-backed disposition for every conservative potential-impact route.
8. Merge the bounded candidate evidence and a separate structured approval record to `main`, then use the protected workflow to archive reviewed discovery evidence, its exact validation context, and the discovery snapshot. Each release binds the source revision, source catalog, impact crosswalk, and hashes of reviewed repository paths so CI can replay the original gate without trusting later configuration; full-history CI also verifies those inputs against the recorded commit immediately preceding the release's unique first-parent introduction. Stale source revisions, partial introductions, removal/re-addition, and later mutation fail closed. This evidence promotion does not update approved authority content and is never auto-merged.
9. When the review requires a legal/accounting currentness change, publish a separate complete dated release only after required professional review. Never auto-merge that release.
10. Downstream production systems consume only an approved legal/accounting release commit or tag. Candidate branches, discovery artifacts, and reviewed discovery snapshots are never production authority inputs.

If retrieval, comparison, review, or licensing fails, preserve the approved baseline, mark the affected area degraded, and require live official verification before high-risk reliance.

## Licensing and storage

Storage permission is evaluated independently from authority weight:

- Public US government material may often be stored when the particular source and included third-party content permit it.
- State and local public records require a source-specific reproduction and terms review.
- Copyrighted model codes and commercial guidance normally remain link/hash/metadata-only unless permission covers repository and generative-AI use.
- FASB Codification text, screenshots, print exports, and scraped content are not stored. The accounting schema permits topic locators, official links, metadata, and original GH analysis; exact requirements require authorized live access.
- A public URL does not by itself grant redistribution rights.

The allowed discovery-stage `storage_policy` values are `redistributable`, `metadata-only`, `licensed-no-store`, and `manual-review`. Current FASB indexes are configured `metadata-only`; `licensed-no-store` is available for a source that may be consulted under license but whose payload may not be retained. Reviewed release control comes from the more specific `licensing.storage_class` and `redistribution_status` fields.

## Impact crosswalk rules

The crosswalk is an alert router, not a rules engine. Each mapping:

- cites only existing legal registry groups, signed-evidence classes, official-source families, internal policies, or three-digit ASC topic locators;
- points to repository paths that actually exist;
- requires a documented human review or no-change conclusion;
- prohibits automatic changes; and
- defines a fail-closed action.

No ASC paragraph appears in the crosswalk. Paragraphs, effective dates, scope exceptions, transition provisions, and private-company alternatives must be verified through authorized FASB research for the actual entity and reporting period.

## Consumption rules

- For research, start with `legal/CURRENT_STATUS.json` or `accounting/CURRENT_STATUS.json`, then the applicable approved index and official source.
- For production code, pin the approved release commit or tag. Do not follow a mutable `latest` pointer without checking state.
- Reject or visibly degrade claims of currentness when a relevant source is changed, unavailable, overdue, or awaiting review.
- Recheck signed leases, property facts, financing, entity structure, reporting period, elections, and transaction evidence. The repository cannot infer them.
- Never use repository content as a substitute for counsel, a CPA, a tax professional, authorized Codification access, or a tenant-specific executed agreement.

## GitHub enforcement requirement

`CODEOWNERS` requests review but does not enforce it by itself. The repository ruleset must require pull requests, code-owner approval, passing authority checks, resolved review threads, and no direct pushes to the protected release branch. The `@GHRealEstate` owner must resolve to a GitHub user or team with repository access; otherwise GitHub will not treat the ownership rule as enforceable.

## Rollback

Authority updates are append-only dated releases. If a promoted release is defective, restore the last approved tag or commit for consumers, mark the defective release superseded or rejected, preserve its evidence for audit, and open a corrective pull request. Never erase the review history or silently rewrite a dated baseline.
