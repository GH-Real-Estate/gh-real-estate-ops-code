# Legal authority library changelog

## 2026-07-13 - Repair official-source monitoring semantics

- Corrected the monitor to compare official archived payloads with `source_archive_sha256` instead of comparing XML/HTML bytes with rendered-PDF hashes.
- Added the required enCodePlus export-token flow and semantic fingerprints of hash-verified approved bundle pages for Overland Park code PDFs so regenerated containers and layout reflow do not masquerade as ordinance changes.
- Added current eCFR date resolution, duplicate-URL suppression, per-host throttling, bounded retries, and payload-type validation.
- Added explicit availability-only policies for five non-byte-comparable derived sources without changing any approved legal-release hash or authority status.
- Added source-monitor regression tests and live pull-request verification for future monitor changes.

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
