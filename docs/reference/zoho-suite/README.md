# Zoho Suite and Twilio AI Reference Library

This directory is the public, sanitized, text-first research baseline for designing and reviewing GH Real Estate and Sylvara business systems with ChatGPT, Codex, and the GitHub connector.

The matching PDFs are distributed as project-source artifacts. GitHub stores Markdown because it is searchable, diffable, reviewable, and substantially easier for an AI agent to retrieve precisely than a binary PDF.

## Start Here

1. Read [`products/collection-index.md`](products/collection-index.md) to identify the owning system and cross-system boundaries.
2. Open every product reference crossed by the workflow.
3. Open [`products/deluge-master-knowledge-base.md`](products/deluge-master-knowledge-base.md) whenever the implementation uses Deluge or a Zoho custom function.
4. Revalidate volatile facts against the exact official URL in the product's source registry.
5. Retrieve live authenticated metadata before generating deployable code or field maps.
6. Apply repository security, testing, approval, deployment, and rollback rules before changing runtime behavior.

## Product References

| Product | Markdown reference | System responsibility |
|---|---|---|
| Cross-suite collection | [`collection-index.md`](products/collection-index.md) | Ownership, identifiers, event processing, integration selection, safety, and AI answer contract |
| Deluge | [`deluge-master-knowledge-base.md`](products/deluge-master-knowledge-base.md) | Language syntax, tasks, runtime contexts, functions, patterns, and testing |
| Zoho CRM | [`zoho-crm.md`](products/zoho-crm.md) | Relationship and leasing-pipeline authority |
| Zoho Books | [`zoho-books.md`](products/zoho-books.md) | Accounting, receivables, payments, credits, and financial reports |
| Zoho Creator | [`zoho-creator.md`](products/zoho-creator.md) | Approved portal and low-code workflow layer |
| Zoho Catalyst | [`zoho-catalyst.md`](products/zoho-catalyst.md) | Serverless runtime, APIs, event processing, storage, identity, and deployment |
| Zoho Contracts | [`zoho-contracts.md`](products/zoho-contracts.md) | Contract type, clause, approval, merge, and lifecycle control |
| Zoho Sign | [`zoho-sign.md`](products/zoho-sign.md) | Recipients, signing fields/order, signature status, and evidence |
| Zoho WorkDrive | [`zoho-workdrive.md`](products/zoho-workdrive.md) | Governed business-document storage and sharing |
| Zoho Sites | [`zoho-sites.md`](products/zoho-sites.md) | Public sites and approved public entry points |
| Zoho Flow | [`zoho-flow.md`](products/zoho-flow.md) | Bounded low-code cross-system orchestration |
| Zoho Analytics | [`zoho-analytics.md`](products/zoho-analytics.md) | Derivative analytics, reports, dashboards, and embeds |
| Zoho Forms | [`zoho-forms.md`](products/zoho-forms.md) | Public/internal intake forms and controlled routing |
| Zoho Billing | [`zoho-billing.md`](products/zoho-billing.md) | Subscription and recurring-revenue lifecycle when adopted |
| Zoho Checkout | [`zoho-checkout.md`](products/zoho-checkout.md) | Hosted payment pages and configured collection flows |
| Zoho Payments | [`zoho-payments.md`](products/zoho-payments.md) | Payment processing events, refunds, payouts, and reconciliation inputs |
| Zoho Bookings | [`zoho-bookings.md`](products/zoho-bookings.md) | Services, staff availability, appointments, and scheduling notifications |
| Zoho Mail | [`zoho-mail.md`](products/zoho-mail.md) | Organization mailboxes, messages, folders, and mail administration |
| Twilio | [`twilio.md`](products/twilio.md) | Approved SMS, voice, Verify, Conversations, and delivery callbacks |

[`source-manifest.json`](source-manifest.json) records the research edition, product document IDs, matching PDF filenames, checksums, and repository paths after the collection is generated.

## Retrieval Contract for ChatGPT and Codex

Every product document uses a stable document ID and section IDs. Search first for the product plus the capability, endpoint family, or evidence label. Examples:

```text
Zoho CRM metadata fields API name LIVE-METADATA REQUIRED
Zoho Books payments webhook idempotency
Zoho Creator portal record permissions
Zoho Catalyst Circuits regional availability
Zoho Sign recipient order webhook
Twilio status callback signature validation
```

When answering or implementing:

- State which product owns the underlying record or decision.
- Separate `DOC-VERIFIED`, `REPO-OBSERVED`, `LIVE-METADATA REQUIRED`, `COMPILER/RUNTIME TEST REQUIRED`, `POLICY INPUT REQUIRED`, `VOLATILE`, and `INFERENCE` facts.
- Cite the exact official source URL and the relevant section ID.
- Name unknown account, organization, portal, project, module, field, template, folder, connection, webhook, and policy inputs explicitly.
- Use placeholders for unresolved live metadata; never invent it.
- Do not output production-ready mutation code when mandatory metadata, permissions, or policy are unresolved.
- Include authentication, least-privilege scopes, data center, environment, pagination, idempotency, retry, concurrency, reconciliation, logging, testing, deployment, monitoring, and rollback considerations in proportion to risk.

## Authority and Currentness

This reference library is dated research, not a substitute for live documentation or configuration. Use this order of authority:

1. Current official provider API/reference documentation.
2. Current official provider help/administration documentation.
3. Authenticated metadata from the exact target environment.
4. Approved GH/Sylvara business, accounting, legal, privacy, security, consent, and communications policy.
5. The current runtime code, schemas, tests, runbooks, and deployment evidence in this repository.
6. This dated reference collection.

If a handbook conflicts with a current primary source or live metadata, stop, use the higher-authority source, and open a focused documentation update.

## Public-Repository Boundary

This library must never contain:

- Credentials, tokens, secrets, API keys, private keys, connection exports, signed URLs, or real environment files.
- Live organization, portal, project, account, phone-number, template, folder, or webhook identifiers when disclosure increases risk.
- Tenant, applicant, owner, vendor, employee, or customer records.
- Real names, email addresses, phone numbers, addresses tied to people, IDs, financial data, signed documents, photos, message bodies, or raw payloads.
- Production logs or screenshots containing private configuration.
- Licensed or non-redistributable provider documentation text.

The documents summarize and link to primary sources. Synthetic examples must remain obviously fictional and non-live.

## Maintenance Workflow

Refresh a product reference when an API version, OAuth scope, endpoint, data-center rule, edition, limit, event contract, runtime, feature state, or live integration materially changes.

1. Identify affected section IDs and exact source URLs.
2. Recheck the current official page and capture the access date.
3. Compare authenticated live metadata without committing sensitive output.
4. Update the Markdown source and matching source manifest.
5. Regenerate the PDF from the same Markdown source.
6. Render and inspect every PDF page; run text, bookmark, link, and boundary QA.
7. Run repository checks and obtain the approvals required by the affected risk domain.
8. Record deployment separately when runtime behavior changes. A documentation merge is not deployment evidence.

## Scope Boundary

The library documents technical possibilities and safe system-design patterns. It does not authorize a live Zoho/Twilio change, determine legal compliance, approve contract language, establish accounting treatment, prove consent, or replace qualified legal/accounting/security review.
