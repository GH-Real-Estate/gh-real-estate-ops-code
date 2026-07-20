# GH Real Estate & Sylvara Zoho Suite and Twilio Knowledge Collection

**Document ID:** GH-ZOHO-SUITE-KB-INDEX  
**Edition:** 2026.07 Research Edition  
**Research cutoff:** 2026-07-20  
**Audience:** ChatGPT, Codex, architects, developers, reviewers, and GH/Sylvara operators  
**Scope:** Cross-suite authority, system boundaries, integration design, retrieval strategy, and knowledge-base catalog

> This collection is a sanitized technical reference. It contains no credentials, production identifiers, tenant records, payment data, signed documents, or private payloads. Official provider documentation, approved business policy, live authenticated metadata, and runtime evidence control implementation.

## IDX-000 How an AI agent must use this collection

1. Start here to identify the owning system and the relevant product handbook.
2. Open the Deluge handbook when the requested implementation uses a Zoho custom function, workflow, button, schedule, or Creator script.
3. Open every product handbook crossed by the workflow. A CRM-to-Books automation requires both handbooks; a Catalyst webhook that mutates CRM and sends Twilio messages requires all three.
4. Treat API versions, OAuth scopes, data-center domains, editions, quotas, field schemas, event payloads, and feature availability as volatile.
5. Obtain live metadata before writing deployable field mappings. Never invent an API name, module, organization ID, portal name, connection alias, custom-field ID, template ID, folder ID, or webhook secret.
6. Identify the source of truth. Do not let an integration runtime or reporting product become a competing ledger, CRM, contract vault, or document store.
7. Separate capability from authorization. A documented API can be technically available while the proposed action still requires business, legal, accounting, privacy, or communications approval.
8. For tenant, lease, money, signature, identity, document, or messaging actions, require idempotency, least privilege, validated inputs, replay resistance, sanitized observability, bounded retries, reconciliation, tests, monitoring, and rollback or forward-repair instructions.
9. Cite the exact official source page and the handbook section used. If an official page conflicts with a handbook, the current official page controls and the handbook must be flagged for refresh.
10. Do not treat repository contents, a generated PDF, or a successful development test as proof of live deployment or production configuration.

### IDX-001 Evidence labels used throughout

| Label | Meaning |
|---|---|
| `DOC-VERIFIED` | Confirmed in an official provider document at the stated research cutoff |
| `REPO-OBSERVED` | Confirmed in the sanitized GH repository, not necessarily deployed |
| `LIVE-METADATA REQUIRED` | Must be read from the authenticated tenant, organization, portal, project, or account |
| `COMPILER/RUNTIME TEST REQUIRED` | Exact behavior must be verified in the target runtime or sandbox |
| `POLICY INPUT REQUIRED` | Approved business, legal, accounting, privacy, security, or communications policy is required |
| `VOLATILE` | Edition, region, limit, scope, endpoint, runtime, or feature availability may change |
| `INFERENCE` | A design recommendation derived from documented facts rather than a provider guarantee |

## IDX-010 Collection catalog

The collection is deliberately split into product-specific, searchable handbooks. Each PDF has a matching Markdown source in GitHub so ChatGPT, Codex, and the GitHub connector can retrieve exact sections without extracting a binary PDF.

| Handbook | Primary retrieval use |
|---|---|
| Deluge Master Knowledge Base | Language syntax, task grammar, functions, execution contexts, error handling, testing, and cross-product Deluge patterns |
| Zoho CRM Master Knowledge Base | Modules, fields, metadata, records, queries, workflows, Blueprints, functions, bulk APIs, notifications, and relationship authority |
| Zoho Books Master Knowledge Base | Organizations, contacts, invoices, payments, credits, expenses, banking/accounting automation, webhooks, custom functions, and ledger controls |
| Zoho Creator Master Knowledge Base | Applications, forms, reports, pages, workflows, Deluge, environments, portals, APIs, SDKs, and tenant/maintenance portal patterns |
| Zoho Catalyst Master Knowledge Base | Functions, AppSail, API Gateway, storage, identity, events, jobs, Circuits, deployment, and integration runtime controls |
| Zoho Contracts Master Knowledge Base | Contract types, templates, clauses, merge fields, approvals, lifecycle, counterparties, APIs, and audit controls |
| Zoho Sign Master Knowledge Base | Requests, recipients, fields, templates, signing sequence, webhooks, embedded signing, evidence, and API controls |
| Zoho WorkDrive Master Knowledge Base | Teams, workspaces, folders, files, permissions, sharing, uploads/downloads, events, and governed document storage |
| Zoho Sites Master Knowledge Base | Sites, pages, forms, domains, publishing, scripts, analytics, member access, and safe marketing/intake patterns |
| Zoho Flow Master Knowledge Base | Triggers, actions, decisions, custom functions, webhooks, connections, history, error handling, and orchestration boundaries |
| Zoho Analytics Master Knowledge Base | Workspaces, tables, imports, query tables, reports, dashboards, embeds, APIs, synchronization, governance, and BI boundaries |
| Zoho Forms Master Knowledge Base | Form design, fields, validation, approvals, webhooks, integrations, prefill, attachments, and intake controls |
| Zoho Billing Master Knowledge Base | Customers, products, plans, subscriptions, invoices, hosted pages, payments, webhooks, lifecycle, and recurring-revenue controls |
| Zoho Checkout Master Knowledge Base | Payment pages, pricing modes, field collection, URL prefill, notifications, integrations, and documented platform boundary |
| Zoho Payments Master Knowledge Base | Payment sessions, methods, customers, refunds, payouts, disputes/events, webhooks, and payment safety controls |
| Zoho Bookings Master Knowledge Base | Services, staff, workspaces, availability, appointments, customers, notifications, APIs, and scheduling workflows |
| Zoho Mail Master Knowledge Base | Organizations, domains, users, mailboxes, messages, folders, APIs, OAuth, retention, and transactional-use boundaries |
| Twilio Master Knowledge Base | Messaging, voice, phone numbers, Conversations, Verify, webhooks, status callbacks, compliance, and Zoho integration patterns |

## IDX-020 System-of-record and responsibility matrix

| Information or action | Authoritative system | Supporting systems | Boundary rule |
|---|---|---|---|
| Prospect, applicant, tenant, owner, vendor, property, unit, leasing relationship | Zoho CRM | Forms, Creator, Catalyst, Analytics | Downstream systems keep only the identifier and fields needed for their responsibility |
| Invoice, payment, credit, deposit accounting, expense, balance, financial report | Zoho Books | Payments, Checkout, Billing, Analytics, Catalyst | Only Books posts or corrects accounting truth unless an approved subsystem is explicitly authoritative |
| Subscription and recurring product lifecycle | Zoho Billing when adopted for that business line | Payments, Books, Checkout | Define whether Billing or Books owns invoices before implementation; never dual-create silently |
| Payment processing event | Zoho Payments or configured payment gateway | Checkout, Billing, Books, Catalyst | Gateway events do not become ledger truth until verified and reconciled in Books |
| Contract draft, approved language, clause and contract lifecycle | Zoho Contracts | CRM, Sign, WorkDrive | Approved templates and policy govern content; CRM fields supply verified merge data |
| Recipient, signature order, field completion, signing status and evidence | Zoho Sign | Contracts, CRM, WorkDrive | A request is not executed merely because an API call succeeded; final evidence and status control |
| Controlled business file and signed artifact | Zoho WorkDrive or approved product-native vault | Contracts, Sign, Creator | GitHub stores no private executed documents or tenant files |
| Tenant portal and approved maintenance workflow | Zoho Creator | CRM, WorkDrive, Books, Catalyst | Creator is the interaction/workflow layer, not a shadow ledger or ungoverned master CRM |
| Public site content and approved public entry point | Zoho Sites | Forms, Bookings, Checkout | A public form or page must minimize collection and route data into the authoritative workflow |
| Appointment availability and booking status | Zoho Bookings | CRM, Mail, Twilio, Calendar integration | Synchronize the business result to CRM only through an explicit mapping and duplicate rule |
| Email mailbox record | Zoho Mail | CRM, Catalyst, Flow | Email delivery does not prove consent, legal notice, or CRM-state transition |
| SMS/voice delivery event | Twilio | CRM, Catalyst, Flow | Messaging requires approved consent, quiet-hour, opt-out, template, and retention rules |
| Cross-system event processing and custom runtime state | Zoho Catalyst | All connected systems | Store only operational state such as receipt, idempotency, retry, and sanitized audit facts |
| Low-code SaaS orchestration | Zoho Flow | All connected systems | Use for bounded, observable flows; move complex or high-risk durable logic to governed code/runtime |
| Analytics model and dashboard | Zoho Analytics | CRM, Books, Creator, other approved sources | Reports are derivative; corrections return to the owning operational system |
| Source code, sanitized schemas, tests, runbooks, and dated research | GitHub | ChatGPT/Codex | GitHub is public and never holds secrets, live payloads, private records, or licensed content |

## IDX-030 Canonical business event sequence

The normal GH leasing path is a governed state transition, not a chain of blind copies:

1. A public source such as Zillow, Zoho Forms, Zoho Sites, or an approved referral captures the minimum permitted intake data.
2. The intake layer normalizes data, applies a deterministic duplicate key, records provenance and consent facts, and upserts the correct CRM record or creates a manual-review candidate.
3. CRM owns qualification, relationship linking, unit/property selection, applicant status, and approval prerequisites.
4. A contract-generation gate verifies required CRM metadata, the approved contract type/template revision, parties, unit, dates, rent, deposit, addenda, and policy approvals.
5. Zoho Contracts generates and approves the controlled draft. Zoho Sign creates the signing request with explicit recipient roles, sequence, field/tag mapping, expiration, reminders, and callback correlation.
6. A verified signing completion event updates CRM state and files the executed artifact in its approved document location. A status callback alone cannot substitute for evidence validation.
7. Books creates the appropriate customer and financial records from an approved mapping. External IDs preserve the CRM relationship without making CRM the ledger.
8. Payments, Checkout, or Billing events are authenticated, deduplicated, reconciled against the correct Books record, and sent to manual review when amounts, currency, organization, or status do not match.
9. Creator exposes only the portal/workflow data needed by the authenticated user. WorkDrive holds approved files under governed permissions.
10. Analytics consumes approved data for decisions and reporting. Corrections flow back to the system of record.

Any alternative sequence must explicitly document why the ownership, validation, and rollback model remains safe.

## IDX-040 Cross-system identifier contract

### IDX-041 Never use display labels as joins

Names, email addresses, phone numbers, addresses, invoice numbers, filenames, and human-readable labels can change or collide. Persist the provider-generated immutable identifier and the owning product alongside any friendly label.

| Required mapping field | Example purpose |
|---|---|
| `source_system` | Identifies CRM, Books, Contracts, Sign, Creator, Catalyst, Twilio, or another provider |
| `source_record_id` | Immutable identifier from the owning system |
| `target_system` and `target_record_id` | Explicit cross-system link |
| `mapping_type` | Applicant-to-contact, tenant-to-customer, contract-to-sign-request, payment-to-invoice, etc. |
| `environment` | Development, sandbox, test, or production |
| `organization_or_portal_alias` | Sanitized configuration alias; never infer from a numeric ID |
| `schema_version` | Mapping and event-contract version |
| `created_at`, `updated_at` | Traceability timestamps |
| `correlation_id` | End-to-end event tracing without exposing personal data |

### IDX-042 Idempotency identity

Every mutating integration needs a deterministic operation identity. Prefer an upstream immutable event ID. If none exists, derive a versioned key from stable business inputs such as provider, event type, source ID, target intent, and effective date. Store the receipt and terminal outcome before acknowledging a webhook where the platform permits.

Do not assume that a provider honors an idempotency header unless the exact API page documents it. Application-level duplicate protection remains required for money, documents, signatures, CRM creation, and messaging.

## IDX-050 API discovery and authentication baseline

### IDX-051 Live discovery before code generation

Retrieve and preserve a sanitized snapshot of the exact live configuration needed by the workflow:

- Account data center and regional base domains.
- Organization, portal, project, workspace, team, or account aliases and IDs.
- CRM modules, API names, field metadata, layouts, related lists, picklists, currencies, and Blueprint constraints.
- Books/Billing organization settings, taxes, currencies, custom fields, templates, payment gateways, chart-of-accounts references, and webhook configuration.
- Creator application owner/link name, form/report link names, field link names, environments, portal, permissions, and published-component settings.
- Contracts contract types, templates, fields, clauses, approval rules, counterparties, and lifecycle states.
- Sign templates, recipients/roles, field definitions/tags, webhook subscriptions, and storage behavior.
- WorkDrive team/workspace/folder identifiers, permissions, sharing restrictions, and retention requirements.
- Catalyst project/environment, API Gateway, functions, connections, tables, jobs, signals, secrets/config aliases, and deployed revision.
- Flow connection ownership, trigger/action versions, custom functions, flow history, error policy, and enabled state.
- Forms/Sites/Bookings/Mail/Twilio identifiers, configured fields, routing, notification, consent, and webhook state.

Record discovery time, environment, source, and hash where useful. Do not commit sensitive snapshots to the public repository.

### IDX-052 OAuth and connection rules

- Use the least-privilege operation-specific scopes documented for the exact endpoint.
- Keep development/sandbox and production clients, tokens, connections, callback URLs, and data separate.
- Resolve the account's data center and official base domain; do not hard-code `.com` for every organization.
- Store secrets only in an approved secret/configuration facility. GitHub, PDFs, source maps, sample payloads, browser code, and logs must contain placeholders only.
- Establish a credential owner, reauthorization/rotation procedure, revocation response, and alerting path.
- Reject unexpected issuers, accounts, organizations, portals, projects, and environments even when a token is syntactically valid.

## IDX-060 Integration selection guide

| Situation | Preferred approach | Escalate when |
|---|---|---|
| Small same-product record action | Native workflow/custom function or Deluge task | It spans systems, needs durable state, or exceeds execution limits |
| Bounded cross-product SaaS flow | Zoho Flow or Deluge with named connections | Complex branching, high volume, replay, durable orchestration, or strict observability is required |
| Public webhook or third-party API | Catalyst function/AppSail behind controlled routing | The provider offers a verified native connector that fully satisfies controls |
| Long multi-step process | Catalyst Circuits/job/event design or a deliberately persisted state machine | Component/region support is unavailable or compensation cannot be defined |
| Bulk synchronization | Product bulk/query/export APIs plus checkpointed worker | Near-real-time semantics or per-record side effects make bulk unsafe |
| Human approval | Product approval/Blueprint/Contracts/Sign workflow | Approval evidence cannot be captured or role separation is inadequate |
| Reporting | Analytics or product-native reports | The report attempts to mutate or redefine operational truth |
| Public intake | Forms/Sites/Bookings/Checkout configured for minimum collection | Sensitive evidence or identity proofing requires an authenticated portal |

`INFERENCE`: Simplicity is a control only when it preserves traceability, error handling, replay safety, and ownership. A short custom function can be riskier than a larger governed service if it performs irreversible work without receipts or recovery.

## IDX-070 Standard event-processing contract

For every webhook, callback, scheduled poll, or event-driven automation:

1. Accept only the documented method, content type, path, and bounded payload size.
2. Capture a correlation identifier and receive timestamp.
3. Authenticate the sender using the exact documented signature, token, certificate, IP, or OAuth mechanism. Never invent signature verification.
4. Parse with a versioned schema; quarantine unknown versions or material shape changes.
5. Check the expected account, organization, project, portal, currency, and environment.
6. Claim a deterministic idempotency key atomically.
7. Load current target state from the system of record rather than trusting a stale event snapshot.
8. Validate prerequisites, permissions, status transitions, amounts, parties, and policy gates.
9. Execute the minimum mutation with bounded timeout and retry behavior.
10. Persist a sanitized outcome and provider response identifiers.
11. Acknowledge according to the provider's retry contract.
12. Reconcile asynchronous completion and route ambiguous or terminal failures to manual review.

### IDX-071 Retry classification

| Failure class | Default action |
|---|---|
| Validation, missing required field, invalid transition | No unchanged retry; correct data or policy |
| Authentication or authorization | Stop; repair approved credential/scope; do not loop refresh blindly |
| Rate limit or documented temporary service condition | Honor provider guidance; exponential backoff with jitter and bounded attempts |
| Network timeout with unknown commit state | Reconcile by idempotency key or provider lookup before retrying |
| Conflict or duplicate | Treat as possible replay; load current state and compare intended outcome |
| Provider 5xx | Retry only if the operation is replay-safe; otherwise reconcile/manual review |
| Schema or signature verification failure | Quarantine and alert; never process permissively |

## IDX-080 Data and field governance

### IDX-081 Field registry minimum

Each governed integration should maintain a sanitized registry with:

- Owning product and module/resource.
- Display label and exact API/link name.
- Immutable field/resource ID when exposed and appropriate.
- Data type, format, maximum length, precision, allowed values, and nullability.
- Layout/edition/region applicability.
- Read, create, update, filter, search, bulk, and webhook visibility.
- Source of truth and allowed downstream consumers.
- Sensitivity/classification and log/analytics restrictions.
- Default, transformation, validation, and duplicate behavior.
- Deprecation/replacement state and verification date.

### IDX-082 Null, absent, empty, and cleared are different

An omitted property, explicit `null`, empty string, empty collection, zero, `false`, and an API-specific clear operation may have different meanings. Each product mapping must define them. An AI agent must not normalize these states without the endpoint contract and business rule.

### IDX-083 Time, money, and locale

- Preserve documented ISO/RFC formats and offsets; store the business timezone where scheduling or legal deadlines depend on it.
- Never use floating-point arithmetic for money. Preserve currency, precision, rounding rule, tax treatment, organization, and effective date.
- Normalize phone numbers only for approved messaging/calling use and retain consent/opt-out facts separately.
- Treat addresses as structured business data, not reliable record keys.

## IDX-090 Security, privacy, and public-repository boundary

Never place these in GitHub or the handbooks:

- OAuth access/refresh tokens, API keys, auth tokens, Twilio credentials, webhook secrets, passwords, private keys, connection exports, or signed URLs.
- Live tenant/applicant/owner/vendor names, emails, phone numbers, addresses tied to people, IDs, SSNs, bank/card data, payment tokens, signed contracts, maintenance photos, or message bodies.
- Raw production webhook/request/response bodies or logs.
- Production organization, portal, project, module, template, folder, account, or phone-number identifiers when disclosure increases risk.
- Licensed or non-redistributable documentation content beyond permitted short factual summaries and links.

Use synthetic fixtures with obviously fictional identities, reserved domains/numbers where practical, non-live identifiers, and no copied production payload structure that reveals private data. Automated secret/PII scanning supplements, but does not replace, human review.

## IDX-100 Testing and release evidence

Every production-capable automation needs proportionate evidence:

1. Source-page and live-metadata verification.
2. Schema/contract tests for valid, missing, null, malformed, oversized, and version-changed inputs.
3. Authentication/signature tests including invalid, expired, wrong-account, and replay cases.
4. Idempotency tests: duplicate before completion, duplicate after completion, and concurrent duplicate.
5. Pagination tests including empty, single-page, boundary, next-page, and rate-limited cases.
6. State-transition tests including already-complete, invalid-state, partial-success, and compensation paths.
7. Least-privilege and negative-permission tests.
8. Log-redaction tests for tokens, personal data, financial data, and document content.
9. Development/sandbox smoke test with synthetic data.
10. Production promotion record naming commit/version, environment, configuration aliases, approver, timestamp, and result.
11. Monitoring, alert delivery, dead-letter/manual-review, reconciliation, and rollback/forward-repair drills.

For financial, contractual, signature, access-control, or external-communication changes, require explicit human approval before production mutation.

## IDX-110 GH/Sylvara implementation priorities

### IDX-111 Foundation

1. Confirm the live application inventory, account data centers, environments, owners, licenses, and connection owners.
2. Establish a cross-system identifier and field registry using sanitized aliases in GitHub.
3. Create a service catalog for every active automation: trigger, owner, systems touched, auth, fields, risks, idempotency, alerts, runbook, test suite, deployed revision, and retirement plan.
4. Standardize correlation IDs, event receipts, error classes, redacted logging, and manual-review queues.
5. Document consent, notice, retention, accounting, leasing, and approval policies separately from technical capability.

### IDX-112 Leasing and onboarding

1. Govern Zillow/Forms/Sites intake into CRM with deterministic duplicate handling and provenance.
2. Define CRM relationship models for applicant, tenant, property, unit, lease, owner, vendor, and household.
3. Gate Contracts generation on complete live metadata and approved policy.
4. Version Sign recipient manifests, tag/field maps, and callback reconciliation.
5. Link executed artifacts to controlled WorkDrive locations without exposing files in GitHub.
6. Create Books customer/invoice/deposit mappings only after accounting review.
7. Expose approved portal functions through Creator with role-based record rules.

### IDX-113 Payments and recurring revenue

1. Decide which product owns each commercial model: Books receivables, Billing subscriptions, Checkout payment pages, or another approved gateway.
2. Establish one ledger-posting route and a reconciliation key for each payment/refund/chargeback event.
3. Authenticate and deduplicate Payments/gateway webhooks in Catalyst.
4. Require currency, amount, organization, customer, invoice/subscription, and terminal-status validation.
5. Separate failed-payment communication from fee assessment; each needs approved policy, timing, and audit evidence.

### IDX-114 Communications and scheduling

1. Centralize consent, opt-out, channel preference, quiet hours, sender identity, message purpose, and policy version.
2. Use Bookings as scheduling authority for enabled services and CRM as relationship authority.
3. Use Mail/Twilio delivery callbacks as communication evidence, not business-state authorization.
4. Suppress duplicate reminders across Bookings, Mail, CRM, Flow, and Twilio.
5. Route replies, STOP/HELP events, bounces, failures, and staff escalations to an owned queue.

## IDX-120 AI implementation answer contract

When ChatGPT or Codex is asked to design or change a GH/Sylvara workflow, the answer should contain:

1. **Goal and owning system.**
2. **Products and exact handbook sections used.**
3. **Verified facts versus volatile/live metadata.**
4. **Required metadata discovery.**
5. **Data model and field mapping with null/clear semantics.**
6. **Auth, scopes, data center, environment, and connection plan.**
7. **Trigger/event contract and versioning.**
8. **Idempotency, concurrency, retry, timeout, and reconciliation design.**
9. **Security, privacy, consent, audit, and policy gates.**
10. **Implementation outline with placeholders for unresolved metadata.**
11. **Tests, deployment, monitoring, and rollback/forward repair.**
12. **Exact official sources and revalidation date.**

Do not output production-ready mutation code when mandatory live metadata or policy decisions remain unresolved. A safe scaffold with explicit placeholders is acceptable.

## Appendix A - Source hierarchy

Use sources in this order:

1. Current official product API/reference documentation for technical behavior.
2. Current official help/administration documentation for product configuration and feature behavior.
3. Authenticated live metadata from the target GH/Sylvara environment.
4. The current sanitized GitHub repository for approved architecture, field-map intent, schemas, tests, and runbooks.
5. This dated knowledge collection for retrieval, explanation, and design context.

Provider blog posts, forum answers, marketplace listings, community examples, and search snippets may identify a research lead but must not control a production implementation when a primary source is available.

## Appendix B - Collection maintenance manifest

Refresh an affected handbook and this index when:

- A provider publishes a new API version, scope model, data center, authentication requirement, webhook contract, runtime, edition, quota, or retirement notice.
- Live modules, fields, templates, applications, organizations, portals, connections, flows, webhooks, phone numbers, or ownership change.
- A GH/Sylvara policy changes system ownership, allowed automation, consent, accounting treatment, contract language, approval, retention, or incident response.
- Repository architecture, runtime code, schemas, or deployment practices materially change.
- A handbook reaches its scheduled review date or an implementation discovers a mismatch.

The refresh record must identify the affected document ID and section IDs, old and new verified facts, exact source URLs, access date, migration impact, tests, and reviewer. Updating documentation does not deploy or modify a live system.

## Appendix C - Local project-source inputs

The cross-suite architecture was reconciled with these user-provided, sanitized project sources:

- `00_START_HERE.md`
- `01_GH_Tenant_Lifecycle_Map.md`
- `02_GH_Zoho_App_Map.md`
- `03_GH_CRM_Module_Map.md`
- `04_GH_Systems_Change_Control_Standard.md`
- `06_GH_GitHub_Repository_Source_Index.md`
- `Deluge-Master-Handbook-2025.pdf`
- `Deluge Coding.pdf`

The public repository and official provider documentation control over any stale statement in a local source. Live tenant configuration remains `LIVE-METADATA REQUIRED`.
