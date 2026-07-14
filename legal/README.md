# GH Real Estate Legal Authority Library

This directory is the version-controlled legal research corpus for GH Real Estate operations at **9401 Nieman Road, Overland Park, Kansas 66214**.

The approved release in this directory is current through **July 12, 2026** and contains:

- 8 searchable, bookmarked PDF files.
- 447 canonical source documents: 377 Kansas, 41 federal, and 29 Overland Park authorities.
- 1,718 compiled pages.
- Kansas landlord–tenant, eviction, fair-housing, screening, privacy, safety, electronic-transaction, and related authorities.
- Federal fair-housing, HUD, lead, screening, military, foreclosure, electronic-transaction, and conditional housing-program authorities.
- Overland Park rental, civil-rights, property-maintenance, building, fire, systems, and zoning provisions.

This is an internal research and retrieval aid, not legal advice. It is scoped to the property and operations described above; it is not a representation that every law that could apply to every real-estate transaction or factual scenario has been collected. Verify live official law and consult Kansas counsel before enforcement, filing, denial, accommodation, deposit deduction, eviction, or a material lease or policy change.

## Where to start

1. Read [`CURRENT_AUTHORITY_INDEX.md`](CURRENT_AUTHORITY_INDEX.md).
2. Apply the rules in [`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md).
3. Search `text/current/authorities/` for one-source-per-file connector text.
4. Confirm the result against the corresponding file in `generated/project-sources/current/` and the official URL in `manifests/authority_registry.json`.

Official source text controls over extracted text, summaries, applicability notes, and AI-generated analysis.

## Directory map

```text
legal/
  README.md
  PROJECT_INSTRUCTIONS.md
  CURRENT_AUTHORITY_INDEX.md
  CHANGELOG.md
  SOURCE_GAPS.md
  context/
  generated/project-sources/current/
  manifests/
  scripts/
  text/current/
```

- `generated/project-sources/current/` contains the eight approved PDFs to pin in a ChatGPT Project.
- `text/current/authorities/` contains 463 search-sized Markdown files representing the 447 canonical sources; long sources are split into numbered parts. `text/current/full/` and `chunks/` preserve bundle-level text.
- `manifests/authority_registry.json` records citations, official URLs, source hashes, authority labels, and bundle page locations.
- `manifests/releases/2026-07-12.json` is the machine-readable build record.
- `context/` documents the boundary between legal authority and operational facts. Internal policy files are intentionally excluded from this legal release and never override a statute, regulation, ordinance, court order, or signed agreement.
- `scripts/` validates releases and checks official sources for possible changes.

Known access exceptions and corpus limitations are recorded in [`SOURCE_GAPS.md`](SOURCE_GAPS.md), including two HUD 403 responses and one HUD memorandum recovered through a public mirror.

## Version rules

- `CURRENT` means approved for the dated release, not guaranteed current forever.
- Binding, conditional, guidance, proposed, and withdrawn materials must remain separately labeled.
- An enacted amendment that is not yet incorporated into a consolidated code is stored and applied as a dated addendum only to the provisions it changes.
- Historical text must be date-scoped. Never patch old wording into current text to create a synthetic statute.
- A source-monitor alert is a review candidate, not automatically current law.

## Unresolved applicability facts

Confirm these facts before relying on conditional authorities:

- Official construction year; public sources report 1963.
- Whether any mortgage is Fannie Mae, Freddie Mac, FHA, VA, USDA, or otherwise federally backed.
- Whether any unit participates in HCV or another HUD/federal-assistance program.
- Current Overland Park rental license, parcel zoning, occupancy classification, and lawful-nonconforming status.
- Whether an owner actually occupies a unit before analyzing any owner-occupied four-unit fair-housing exemption.

## Update process

The scheduled monitor compares official payloads with the matching release fingerprint and opens a `LEGAL REVIEW REQUIRED` issue when a comparable source changes or cannot be verified. Direct files use their artifact hash. Rendered eCFR sources use the archived XML hash and the latest completely processed date reported by the official eCFR title metadata endpoint. Overland Park enCodePlus exports are generated through the required temporary file-token flow, then their page-scoped text, page geometry, and embedded graphics are compared with the hash-verified approved bundle pages. Regenerated PDF container bytes, whitespace reflow, and line-wrap hyphenation are retained for audit but do not create false legal-change alerts. Duplicate URLs are fetched once, and transient rate-limit/server failures receive bounded retries.

Five derived sources are explicitly availability-only in `manifests/source_monitor_overrides.json`: the FTC HTML rendering, the mirror-derived/normalized HUD memorandum, and three exact-page Kansas case extracts. Their official URLs are checked for reachability and payload type, but their bytes are not compared with a non-equivalent derived artifact. They require purpose-built or qualified manual comparison. This exception is visible in every monitor report and documented in `SOURCE_GAPS.md`.

The full JSON and Markdown reports are retained as workflow artifacts. When changed fingerprints, retrieval errors, or a technical workflow failure require review, the default-branch workflow posts a bounded issue summary linked to the full artifact. Feature-branch manual runs cannot modify the production legal-review issue, and scheduled/manual runs for the same ref are serialized.

A green monitor run means the registered comparable payloads matched and the five availability-only sources were reachable. It does not prove complete legal currentness: fixed, dated URLs do not discover later editions, new amendments, superseding notices, later case history, or guidance published at a new URL. Those discovery and manual-comparison checks remain part of the qualified release-review process.

The monitor never silently promotes changed text, rewrites effective dates, or merges a legal update. After human review, regenerate the complete release, update the registry and changelog, replace all eight current PDFs and their text extracts together, and record the review date.
