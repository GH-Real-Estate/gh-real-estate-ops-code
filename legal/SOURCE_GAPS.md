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
- Two KHRC PDF sources are published through plain HTTP. Exact hashes detect different bytes, but the transport cannot prove freshness against replay of the approved payload; recheck KHRC through an independently trusted channel before material reliance.

Record a resolved exception in `CHANGELOG.md`, update the registry and hashes, and regenerate the complete release rather than silently replacing a file.
