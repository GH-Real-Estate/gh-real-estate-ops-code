# Zoho Suite Reference Instructions

These instructions apply to `docs/reference/zoho-suite/`.

## Purpose

Maintain a public, sanitized, official-source-anchored knowledge layer that ChatGPT, Codex, and the GitHub connector can retrieve when designing or reviewing GH Real Estate and Sylvara systems.

## Authority Order

1. Current official provider API/reference documentation.
2. Current official provider help/administration documentation.
3. Authenticated live metadata from the exact target environment.
4. Approved GH/Sylvara policy and the repository's current runtime evidence.
5. These dated reference documents.

When sources disagree, use the higher-authority source and update the affected reference. Do not infer that repository presence proves production deployment.

## Research and Editing Rules

- Use primary official Zoho or Twilio sources for technical claims. A community post or search snippet may identify a lead but must not control an implementation.
- Keep the document ID and established section IDs stable. Add new IDs; do not casually renumber existing retrieval anchors.
- State the research cutoff and source access date.
- Distinguish documented facts, repository observations, live-metadata requirements, compiler/runtime tests, policy inputs, volatility, and inference.
- Record exact source-page titles and URLs in the product source registry.
- Describe endpoints and fields precisely, but do not copy large provider-document passages or store licensed/non-redistributable content.
- Treat API versions, scopes, base domains, editions, quotas, limits, regional availability, preview status, and product names as volatile.
- Never invent module API names, field link names, record IDs, organization IDs, portal/project/workspace names, connection aliases, template IDs, folder IDs, phone numbers, or webhook secrets.
- Keep examples synthetic and visibly non-live.

## Security Boundary

Never add credentials, tokens, secrets, private keys, connection exports, signed URLs, real identifiers, tenant/customer/applicant/employee records, financial data, signed documents, message bodies, raw production payloads, or private configuration screenshots.

This is a public repository. Treat every committed byte as permanently disclosed.

## AI Retrieval Requirements

Each product reference should remain standalone and include:

- Product role and system-of-record boundary.
- AI usage directive and evidence labels.
- Authentication, data-center, environment, and scope model.
- Identifiers and live metadata discovery.
- API/resource/field coverage appropriate to the product.
- Pagination, limits, errors, retries, idempotency, concurrency, and reconciliation.
- Events, webhooks, workflows, custom functions, and integration options.
- Security, privacy, audit, testing, deployment, monitoring, and recovery.
- GH/Sylvara patterns, anti-patterns, and implementation checklist.
- Official source registry and maintenance triggers.

## PDF Companion Workflow

The PDFs are generated distribution artifacts and are not committed here. Markdown is the canonical GitHub retrieval source.

After a substantive update:

1. Regenerate the matching PDF from the same Markdown.
2. Preserve searchable text, bookmarks, table of contents, hyperlinks, US Letter page size, and repository typography rules.
3. Render and visually inspect every page.
4. Run source and PDF structural QA.
5. Update `source-manifest.json`, checksums, research edition, and change notes as needed.

## Implementation Boundary

Editing this reference does not authorize or deploy a live Zoho, Catalyst, or Twilio change. Runtime changes remain subject to the root and source-system `AGENTS.md` files, tests, review gates, deployment records, smoke tests, monitoring, and rollback requirements.
