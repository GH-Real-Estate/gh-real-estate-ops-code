# Legal authority library changelog

## 2026-07-14 - Record Kansas Article 25 user document as intake evidence

- Audited a user-provided DOCX that self-reports a September 16, 2024 update and found it to be an incomplete Article 25 extract rather than all of Kansas Statutes Chapter 58.
- Recorded its SHA-256, scope, official-index comparison, omissions, and disposition in a metadata-only intake record without storing the binary.
- Confirmed that all 68 populated operative sections in the document were already represented in the approved repository release; the document added no operative authority and omitted 29 sections present in the observed official index and repository release.
- Added a strict intake schema, fail-closed validator, regression tests, and CI enforcement that prohibit binary storage or silent promotion into approved current law.
- Added the Kansas Legislature's stable current Chapter 58 Article 25 index as the fourteenth governed legal discovery source, with an exact section-link filter, a 90–150 item boundary, and review-only metadata handling.

This intake audit does not modify, reapprove, or advance the July 12, 2026 legal release. Live official source text and qualified legal review remain required for reliance or a future release change.

## 2026-07-13 - Add governed official-index discovery

- Added a daily, allowlisted discovery layer covering 13 legal publisher indexes to complement the existing weekly approved-source hash monitor.
- Added fail-closed `current`, `review_required`, and `degraded` discovery states, rolling-window feed semantics, draft candidate pull requests, structured review evidence, and a protected evidence-promotion gate.
- Documented the optional noncritical Congress API key, the Kansas Secretary of State linked-rules manual gap, and the City Clerk control over the City-linked Overland Park electronic-code copy.
- Required qualified legal review, official evidence, effective-date analysis, and a complete dated release before any discovered change can affect approved legal material or operations.

This automation change does not modify, reapprove, or advance the July 12, 2026 legal release.

## 2026-07-13 - Repair official-source monitoring semantics

- Corrected the monitor to compare official archived payloads with `source_archive_sha256` instead of comparing XML/HTML bytes with rendered-PDF hashes.
- Added the required enCodePlus export-token flow and semantic fingerprints of hash-verified approved bundle pages for Overland Park code PDFs so regenerated containers and layout reflow do not masquerade as ordinance changes.
- Added current eCFR date resolution, duplicate-URL suppression, per-host throttling, bounded retries, and payload-type validation.
- Added explicit availability-only policies for five non-byte-comparable derived sources without changing any approved legal-release hash or authority status.
- Added source-monitor regression tests and live pull-request verification for future monitor changes.
- Hardened failure publication with explicit repository targeting, default-branch-only issue writes, serialized runs, atomic report replacement, bounded issue summaries, and fallback reports for pre-monitor or missing-artifact failures.
- Restricted monitor requests and redirects to exact governed HTTPS/443 hosts, rejected credentials and HTTPS downgrades before following redirects, and revalidated every final response URL before reading content.
- Stopped fetching the two exact legacy KHRC HTTP sources; they remain explicit offline manual gaps without making every scheduled run fail, while any other insecure URL fails closed.
- Added retry handling for incomplete HTTP responses and corrected reported attempt counts for permanent failures.
- Made connector-text size validation independent of Windows CRLF checkout conversion without changing committed source text.
- Documented that fixed official URLs verify registered payloads but do not discover new editions, superseding sources, or later case history.

This technical repair does not approve a source change or advance the July 12, 2026 legal-release verification date.

## 2026-07-12 — Initial approved source-pack release

- Added eight searchable and bookmarked project-source PDFs.
- Added connector-searchable text extracted from each PDF.
- Added a machine-readable registry covering 447 source documents and exact bundle page locations.
- Added Kansas 2026 session-law addenda for Sub. HB 2357 and SB 391, effective July 1, 2026.
- Preserved conditional HUD/HCV/VAWA/Section 504 authorities separately from generally applicable law.
- Excluded withdrawn HUD guidance from the active source set and retained proposed rules as monitoring-only material where identified.
- Added release validation and scheduled official-source change monitoring.

This entry records a research release, not a legal opinion or a representation that no authority changed after the verification date.
