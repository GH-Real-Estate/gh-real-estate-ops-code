# GH Real Estate Document Drafting and Typography Standard

**Standard ID:** GH-DOC-001  
**Version:** 1.1  
**Effective date:** July 15, 2026  
**Scope:** All user-facing documents and reusable drafting artifacts created for GH Real Estate by ChatGPT, Codex, repository generators, or connected applications  
**Machine-readable profile:** [document-style-profile.json](document-style-profile.json)  
**Zoho Contracts authoring profile:** [contract-authoring-standard.md](../../src/zoho-contracts/standards/contract-authoring-standard.md)

## 1. Purpose and priority

This standard creates one consistent, professional drafting system for legal documents, business documents, notices, letters, policies, checklists, reports, forms, DOCX files, PDFs, and reusable templates.

Apply rules in this order:

1. Binding law, court rule, agency instruction, mandatory form, or required disclosure.
2. Signed agreement or attorney-approved language and formatting.
3. Application limitations and accessibility requirements.
4. This standard.
5. A document-specific design choice approved for that document.

Never change mandatory wording or invalidate an official form merely to match this style.

## 2. Font policy

### 2.1 Brand preference

GH Real Estate prefers the appearance of Apple's San Francisco typeface.

Use San Francisco only when it is supplied by the Apple operating system or application as its native system font, or when a separate license expressly permits the specific use. Do not download, bundle, upload, redistribute, or embed Apple's font files in GH documents, templates, websites, applications, PDFs, or this repository.

Apple's published San Francisco font-package license limits the downloaded font to Apple-platform user-interface mockups and states that it may not be used to create or distribute documentation, artwork, website content, or other work products outside that permission. See [Apple Fonts and license](https://developer.apple.com/fonts/).

### 2.2 Production document font

**Inter is the required production font for ordinary GH Real Estate documents.**

Use Inter for:

- leases, addenda, disclosures, notices, letters, policies, and forms;
- DOCX and PDF output;
- Zoho Contracts and Zoho Sign templates when Inter is available;
- reports, checklists, operating procedures, and presentations;
- websites and applications when San Francisco is not being supplied natively by an Apple platform;
- any cross-platform artifact that must render consistently.

Inter is licensed under the SIL Open Font License 1.1, which permits document use and embedding. See the [official Inter license](https://github.com/rsms/inter/blob/master/LICENSE.txt).

### 2.3 Exact implementation order

| Environment | Required implementation |
|---|---|
| Apple-native interface | Use the operating system's system-font API; do not package an SF font file |
| HTML/CSS | Load Inter; use `-apple-system, BlinkMacSystemFont, "Inter", sans-serif` |
| DOCX / Word | Use `Inter` in document styles and applicable run-level font properties |
| PDF | Render with Inter and embed or subset it when the PDF tool permits |
| Zoho Contracts / Zoho Sign | Select Inter when available; do not upload SF font files |
| Plain-text chat or Markdown | The viewing application controls the display font; any downloadable artifact created from the text must follow this standard |
| Locked application without SF or Inter | Record a platform exception; use the closest neutral sans-serif only as a temporary editing preview, then produce the final deliverable in Inter |

A document is not font-compliant merely because the authoring computer has SF installed. The final artifact must be legally licensed, portable, and visually verified.

## 3. Core page and type specifications

### 3.1 Page setup

| Element | Standard |
|---|---|
| Page size | U.S. Letter, 8.5 × 11 inches |
| Top margin | 0.80 inch |
| Bottom margin | 0.78 inch |
| Left margin | 1.00 inch |
| Right margin | 1.00 inch |
| Header distance | 0.35 inch |
| Footer distance | 0.34 inch |
| Body alignment | Left aligned; use justified text only when spacing remains visually clean |
| Widow/orphan control | Enabled |
| Heading pagination | Keep heading with the next paragraph; never leave a heading alone at page bottom |

### 3.2 Type scale

| Use | Inter size and treatment |
|---|---|
| Document title | 18 pt, bold |
| Title kicker / status | 8.3 pt, bold, uppercase |
| Subtitle | 9.2 pt, semibold or bold |
| Heading 1 | 15 pt, bold |
| Heading 2 | 12 pt, bold |
| Heading 3 | 10.5 pt, bold |
| Normal body | 10 pt, regular |
| Dense agreement body | 9–10 pt; substantive terms must not be smaller than 9 pt |
| Tables | Normally 7.5–8.8 pt; use the largest size that fits without crowding |
| Running header | 7.6 pt, semibold or bold |
| Running footer | 7.2 pt, regular |
| Footnote / administrative note | At least 7.2 pt |

Normal body paragraphs use 1.08 line spacing, zero space before, and 5 pt after. Use paragraph spacing rather than empty paragraphs.

### 3.3 Color palette

| Token | Hex | Use |
|---|---|---|
| Ink | `#17212B` | Main text |
| GH blue | `#1F4E79` | Headings and restrained accents |
| Muted | `#5C6670` | Headers, footers, metadata |
| Light blue | `#E8EEF5` | Table headers and neutral callouts |
| Light gray | `#F2F4F7` | Secondary fills |
| Pale gold | `#FFF4D6` | Important operational callouts |
| Risk red | `#9B1C1C` | Draft, warning, and risk labels |
| Border | `#AAB4BE` | Rules and table borders |

Legal documents should remain predominantly black/ink on white. Color must never be the only way information is conveyed.

## 4. Branding, logo, headers, and footers

### 4.1 Logo

- Use the GH Real Estate logo, not a HUD, EPA, government, association, or equal-housing logo, unless an official form or applicable rule specifically requires that mark.
- On legal documents, place the GH logo on the first page only unless a document-specific template requires otherwise.
- Preserve aspect ratio and use a transparent-background source when available.
- Preferred maximum size is 1.25–1.60 inches wide and 0.45 inch high.
- When an editor requires pixels, use approximately 150 × 45 px at 96 ppi, or 300 × 90 px for a higher-density source.
- Never stretch, distort, recolor, or use the logo as a watermark behind legal text.

### 4.2 Running header

Default centered form:

`GH Real Estate, LLC | [Short Document Name]`

When the application supports left, center, and right zones:

- **Left:** GH Real Estate, LLC or the small GH logo.
- **Center:** Short document name.
- **Right:** Optional auto-generated document/contract ID; otherwise blank.

Do not put a manually maintained lease number in a global template. Use a merge field only when the system creates and maintains it automatically.

### 4.3 Running footer

Default centered form:

`[Status] | Rev. YYYY-MM-DD | [Execution restriction, if any] | Page X of Y`

When the application supports three zones:

- **Left:** Status, such as `Attorney Review Draft — Not for Execution`.
- **Center:** Revision date or approved template version.
- **Right:** `Page X of Y`.

Final executed versions must remove obsolete draft warnings while preserving the approved template version and page numbering.

## 5. Legal-document drafting standard

### 5.1 Hierarchy and numbering

Use this hierarchy unless a mandatory form controls:

1. Document title.
2. Introductory identification and effective date.
3. Recitals only when they serve a legal purpose.
4. Numbered articles or sections.
5. Numbered clauses.
6. Lettered subsections.
7. Roman-numeral subparts only when needed.
8. Exhibits, schedules, appendices, and addenda.
9. Signature and acknowledgment blocks.

Preferred numbering:

```text
2. PARTIES, PREMISES AND TERM
2.1 Lease Term
2.2 Move-In and Delivery of Possession
2.3 Renewal
2.4 Early Termination
2.5 Holdover
(a) First subordinate provision
(i) Second subordinate provision
```

For Zoho Contracts:

- A **Clause Type** is the top-level subject family. Use only the exact values in the governed 16-item master list under `src/zoho-contracts/standards/`.
- Each independently selectable legal provision is its own **Clause**, such as `2.1 Lease Term` or `2.2 Move-In and Delivery of Possession`.
- Keep Clause Name, library Question, language-variant Clause Title, and Language as distinct governed values.
- The Question must identify the factual decision that helps the contract owner select the standard language or an approved alternative.
- Exactly one language variant is standard. Approved alternatives may have different Clause Titles.
- Do not repeat Clause Title text inside Language merely to simulate the separate Zoho title field.
- Do not place unrelated subjects in one oversized clause merely to reduce the clause count.
- Numbering must be generated or reconciled automatically; never maintain duplicate numbering manually in multiple systems.

### 5.2 Drafting quality

- Use defined terms consistently and capitalize them only when defined.
- Prefer direct sentences, active voice, and concrete duties.
- State who must act, what must occur, when it must occur, and the consequence of nonperformance.
- Separate obligations, permissions, conditions, remedies, and notices when combining them would create ambiguity.
- Avoid `and/or`, unnecessary archaic language, circular cross-references, and vague catch-all language.
- Do not use `etc.` in operative legal text.
- Keep dates, money, notice periods, fees, party names, premises, and signature roles as controlled merge fields when possible.
- Cross-references must resolve to the final numbered provision.
- Mandatory federal, Kansas, Overland Park, or program-specific wording must remain exact when the authority requires exact text.
- Never present attorney-review language as approved law or production-ready legal advice.

### 5.3 Table of contents

Use an automatic table of contents when the agreement is approximately 10 pages or longer, contains at least six top-level sections, or materially benefits from navigation.

- Use live heading styles and generated page numbers.
- Do not type page numbers manually.
- If the contract platform cannot refresh page numbers after merging, use a section list without page numbers or create the TOC only in the final stable PDF.
- Verify every entry after final pagination.

### 5.4 Signatures and attachments

- Keep each signature block together when possible.
- Clearly identify printed name, legal capacity, signature, and date.
- Provide one signature/certification line for every required signer.
- Distinguish an addendum, exhibit, schedule, and appendix by function and reference it consistently in the main agreement.
- Recipient-visible required attachments must travel with the final executed contract; an internal file link alone is insufficient when the law or agreement requires attachment or delivery.
- Do not use duplicate competing forms for the same disclosure or obligation.

### 5.5 Attorney-review status

Attorney-review drafts must display:

- `Attorney Review Draft`;
- the revision date;
- `Not for Tenant Execution` or the appropriate restriction;
- unresolved blanks and decisions in a visible, controlled manner; and
- a clean final version only after counsel approves the language and workflow.

## 6. General business-document standard

For nonlegal letters, reports, checklists, instructions, emails converted to documents, and presentations:

- use Inter as the production font unless San Francisco is being supplied natively and lawfully by the Apple platform;
- use the same restrained palette and heading hierarchy;
- lead with the outcome or requested action;
- use plain language and short paragraphs;
- use tables only when they materially improve comparison;
- include document owner, revision date, and status when the item will be reused;
- avoid excessive decoration, stock imagery, or inconsistent icon systems;
- preserve accessibility, searchable text, and meaningful link labels.

## 7. Application-specific controls

### 7.1 Word and DOCX generators

- Set Inter in document styles and at run level where a generator may otherwise substitute fonts.
- Set the Word `ascii`, `hAnsi`, and applicable complex-script/east-Asian font mappings.
- Use true heading styles, list numbering, page fields, and table-header repetition.
- Do not simulate spacing with blank lines or repeated spaces.
- Preserve editable fields and accessible reading order.

### 7.2 PDF output

- Export from the verified source rather than printing screenshots.
- Embed or subset Inter when permitted by the PDF tool.
- Preserve selectable/searchable text, bookmarks for long documents, working links, and tagged structure when supported.
- Confirm fonts did not substitute during export.

### 7.3 Zoho Contracts and Zoho Sign

The Contracts-specific profile at `src/zoho-contracts/standards/contract-authoring-standard.json` overrides the general page and type defaults only for Zoho Contracts templates and clauses.

- Confirm Inter Regular and Bold are available organization-wide. If absent, install approved Inter TTF files through Zoho Writer organization font settings before publication; request a documented exception only if installation is impossible.
- Do not upload or embed Apple's SF font package.
- Use Heading 1 for the Clause Type/article heading in the template, Heading 2 for the language-variant Clause Title, Heading 3-5 for nested clause subheadings, and Normal for operative Language.
- Use only the governed Clause Type master list and store checked-in clause definitions in the CI-scanned `src/zoho-contracts/clauses/` path.
- Use Contracts merge fields for transaction data and the separate Zoho Sign registry for recipient fields.
- Treat Sign Date as the date the recipient actually signs; it is expected to be blank before signing.
- Keep formatted and choice-field text tags blocked until a synthetic Contracts-to-Sign test proves both field conversion in preview and final value behavior after signing.
- Test the final merged contract, not only the blank template.
- Preserve signature order, required attachments, audit records, final PDF pagination, and the last approved export needed for a forward-repair rollback.
- Republishing affects new contracts only. Repository changes do not restyle existing contracts or deploy live Zoho configuration.

### 7.4 Web and application interfaces

Load Inter as the non-Apple font and use:

```css
font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
```

This allows Apple devices to use their native system typography without distributing Apple's font files and uses Inter elsewhere.

## 8. Required QA before delivery

Every final DOCX or PDF must pass:

1. Content comparison against the current source of truth.
2. Defined-term, numbering, cross-reference, and attachment reconciliation.
3. Merge-field and unresolved-placeholder check.
4. Signature-role and date-field check.
5. Header, footer, revision, and page-number check.
6. Font check: lawful SF system rendering or Inter; no silent substitution.
7. Render every page and visually inspect it.
8. Check for clipping, overflow, blank pages, orphan headings, split signature blocks, broken tables, and unreadably small text.
9. Confirm TOC entries and PDF bookmarks when applicable.
10. Confirm selectable/searchable text and accessibility where supported.
11. Confirm the correct draft/final execution status.
12. Record the final filename, version, and hash when the document is legally or operationally material.

A document is not complete merely because it opens successfully.

## 9. Exceptions

An exception must identify:

- the application or mandatory form creating the limitation;
- the exact rule that cannot be followed;
- the temporary substitute used;
- whether the final tenant-facing or external artifact remains affected; and
- the remediation owner.

Do not silently substitute Roboto, Arial, Calibri, Times New Roman, or another font and describe it as compliant. Inter is the ordinary production fallback.

## 10. Repository rule

This repository stores this standard, style metadata, templates, and sanitized implementation notes. It must not store:

- Apple SF font binaries;
- tenant-specific completed legal documents;
- signatures or private tenant information;
- government logos copied for decorative use; or
- attorney-client privileged documents unless a separate approved repository and access policy expressly permits them.

All future repository-aware ChatGPT/Codex drafting tasks must read this standard before creating or materially revising a user-facing document.
