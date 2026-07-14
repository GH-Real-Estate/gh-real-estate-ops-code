# Source gaps and verification exceptions

The July 12, 2026 release is a strong current operational corpus for a residential fourplex in Overland Park. It is not a complete historical archive of every Kansas, federal, HUD, or municipal real-estate authority, every case, or every copyrighted technical code incorporated by reference.

## Known retrieval exceptions

- HUD's September 17, 2025 withdrawal memorandum returned HTTP 403 during automated retrieval. The official controlling 2026 Federal Register withdrawal notice, 91 Fed. Reg. 17291, is included.
- HUD Form 928.1, the Fair Housing poster, returned HTTP 403. The binding text of 24 C.F.R. part 110 is included; the poster remains a link-only record where noted.
- HUD's May 22, 2026 assistance-animal enforcement memorandum was recovered from a public mirror because HUD blocked automated retrieval. Treat it as nonbinding guidance and compare it with an official HUD copy before legal reliance.

## Scope limitations

- No claim is made that the repository contains every historical version of every collected law.
- Historical session laws and ordinances are included where needed to understand identified current addenda; the archive is not exhaustive.
- Case-law coverage is curated for direct operational relevance, not exhaustive.
- Copyrighted model building, fire, electrical, plumbing, mechanical, fuel-gas, and energy codes incorporated by reference may not be reproduced in full. Local amendments and official adoption provisions are included; consult licensed code text where required.
- Federal program rules are conditional on facts such as HCV participation, federal financial assistance, or mortgage status.

## Automated monitor comparison limits

- Overland Park's enCodePlus source URLs are stable references, not direct PDF downloads. The monitor requests a temporary export token and compares page-scoped text, page geometry, and embedded graphics with the hash-verified approved bundle slice. This ignores regenerated PDF-container and text-layout bytes while still detecting text, page, and embedded-image changes; unreadable or non-extractable content fails closed for review.
- The official FTC landlord-guidance page contains changing site chrome around a stable rendered guidance body. The monitor verifies reachability and HTML payload type; substantive comparison remains manual.
- The approved May 22, 2026 HUD memorandum was normalized from a public-mirror copy, so its artifact hash cannot be compared with the official HUD PDF bytes. The monitor verifies official-PDF reachability; compare content manually before reliance.
- The McConnell, Schutt, and Washburn South case artifacts are exact-page extracts from official advance sheets, while their official URLs serve full opinion PDFs. The monitor verifies those PDFs are reachable; opinion/currentness comparison remains manual.
- These availability-only exceptions are technical monitoring limits, not approval of later source content and not permission to treat an unreviewed change as current law.
- Availability-only records do not fail an otherwise successful scheduled run. A green result means those URLs were reachable with the expected payload type, not that their substance was compared; manually review them before a new approved release and before high-risk reliance.
- Registered, dated GovInfo and other version-specific URLs verify the integrity of the collected edition. They cannot discover a newer U.S. Code edition, later Federal Register notice, superseding guidance, later case history, or a replacement published at a new URL. Qualified currentness review must perform that discovery separately.
- The Overland Park semantic PDF check compares extracted text, page order/geometry, and embedded XObjects. It is not a rendered-page visual diff and may not detect a vector- or annotation-only change that leaves those signals unchanged.
- Two KHRC PDF sources are published only through plain HTTP. The monitor intentionally does not fetch them, records the exact two URLs as acknowledged offline manual gaps, and does not treat them as a changed/error result by themselves. Recheck KHRC through an independently trusted channel before material reliance; every other HTTP source remains a failing monitor error.

## Discovery coverage limits

- Daily discovery covers 14 configured publisher indexes; it is not a complete citator, docket service, legislative-history service, or proof that every relevant source family is configured.
- A `current` discovery result means no new, modified, or comparison-eligible missing item was detected under the configured comparison policies and no degradation condition occurred. It does not advance the July 12, 2026 legal release or establish that the approved library remains complete or legally current.
- Recent-item feeds and APIs use `rolling-window` missing semantics. They report new and modified observations, but do not treat an older item disappearing from a limited window as repeal, withdrawal, supersession, or deletion.
- The Library of Congress legislation API is an optional, noncritical metadata source. Without `CONGRESS_API_KEY`, it reports `configuration_required`; GovInfo remains the critical enacted-law discovery route, but its presence does not eliminate legislative-status review.
- The Kansas Secretary of State links to the `rules.ks.gov` rules portal. The current automation records portal and index metadata only; rule text, adoption status, effective date, amendment history, and applicability require manual official-source review.
- `codes.opkansas.org` is the City-linked electronic copy of the Overland Park code. The City Clerk's master copy controls, and discovery from the electronic copy is always a manual-review candidate.
- Any source retrieval or parser `error` makes discovery `degraded`, even when the catalog marks that source noncritical; missing configuration degrades the domain only when the affected source is critical. A degraded result does not mean that no authority changed and does not permit continued high-risk reliance without live verification.
- Candidate branches and workflow artifacts are unapproved evidence. They are not production inputs and must not be cited as current law before qualified legal review and a complete dated release.

## User-provided document intake limits

- A DOCX received on July 14, 2026 self-reports a September 16, 2024 update and is an incomplete Kansas Statutes Chapter 58, Article 25 extract. It contains 68 populated operative sections already present in the approved repository release and omits 29 operative sections listed by both the observed official Article 25 index and the repository release.
- The document binary is not stored because its compilation provenance and redistribution rights were not established. Its hash, bounded scope findings, and comparison evidence are retained under `manifests/intake/`.
- The live Article 25 page labeled itself `2026 Kansas Statutes` and listed 97 operative sections on July 14, 2026. The 2025 Kansas Revisor composite amendment listing contains no `58-25xx` entry, and the reviewed 2026 official pages did not identify an enacted Article 25 amendment. These checks support the intake disposition but do not authenticate the online text or advance the approved release date.
- The Kansas Revisor describes the online K.S.A. as unofficial. The printed bound K.S.A. and current Cumulative Supplement are the authenticated source; high-risk reliance still requires live verification and qualified Kansas legal review.
- The daily Article 25 index monitor detects section-link additions, removals, and catchline changes. It does not by itself prove that body text behind an unchanged section link is unchanged; the weekly registered-source comparison, legislative-measure discovery, live official review, and authenticated print source remain complementary controls.
- The intake comparison does not advance the July 12, 2026 release verification date, establish continuing legal currentness, or substitute for live official-source and qualified legal review. Do not cite the user document as authority or copy its text into the approved current path.

Record a resolved exception in `CHANGELOG.md`, update the registry and hashes, and regenerate the complete release rather than silently replacing a file.
