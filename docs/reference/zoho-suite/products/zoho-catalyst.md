# Zoho Catalyst Master Knowledge Base

**Document ID:** GH-ZOHO-CATALYST-KB  
**Edition:** 2026.07 Research Edition  
**Research cutoff:** 2026-07-20  
**Audience:** ChatGPT, Codex, architects, developers, reviewers, and GH/Sylvara operators  
**Scope:** Catalyst platform architecture, APIs, application runtime, integration design, deployment, and operational controls

> This is a sanitized technical reference. It contains no credentials, production identifiers, tenant records, payment data, or private payloads. Official Catalyst documentation controls platform behavior. The deployed project, current console, authenticated metadata, and runtime evidence control tenant-specific behavior.

## CAT-000 AI retrieval directive

When using this document as project context:

1. Identify the exact Catalyst service, project environment, data center, runtime, function type, and target system before proposing code.
2. Treat endpoint paths, scopes, component availability, quotas, supported runtimes, Early Access status, and regional availability as volatile.
3. Never infer project IDs, organization IDs, table or column names, connection names, secrets, domains, function names, webhook secrets, or production URLs.
4. Prefer the provider SDK for backend code when it supplies the needed component operation; use REST when the API contract is required or an SDK is unavailable.
5. Separate Development from Production explicitly. A repository commit or successful local test is not deployment evidence.
6. For money, tenant, lease, signature, authentication, messaging, or document actions, require idempotency, validation, least privilege, sanitized logging, replay protection, a dry-run or manual gate where practical, monitoring, and rollback or forward-repair instructions.
7. Distinguish capability from approval. Catalyst can execute logic, but it is not the source of legal, accounting, leasing, communications, or records-retention policy.
8. Cite the exact official page used. If this document and a current official page differ, use the current official page and flag the handbook for refresh.

### CAT-001 Evidence labels

| Label | Meaning |
|---|---|
| `DOC-VERIFIED` | Confirmed in current official Catalyst documentation at the research cutoff |
| `REPO-OBSERVED` | Confirmed in the sanitized GH GitHub repository |
| `LIVE-METADATA REQUIRED` | Must be obtained from the authenticated tenant/project or runtime |
| `COMPILER/RUNTIME TEST REQUIRED` | Exact behavior must be tested in the target runtime and environment |
| `POLICY INPUT REQUIRED` | Business, legal, accounting, security, or communications approval is required |
| `VOLATILE` | Plan, quota, runtime, regional availability, Early Access status, or product behavior may change |

## CAT-010 Product role and authority boundary

Catalyst is the approved serverless and integration runtime in the GH architecture. It can receive webhooks, validate events, call Zoho and third-party APIs, run scheduled or event-driven jobs, host services, coordinate durable workflows, and expose controlled APIs.

It is not the primary source of truth for:

| Fact or artifact | Owning system |
|---|---|
| Prospects, applicants, tenants, properties, units, leasing relationships | Zoho CRM |
| Invoices, payments, deposits, fees, expenses, balances, accounting reports | Zoho Books |
| Approved contract type, clause, request, approval, and lifecycle | Zoho Contracts |
| Recipient fields, signing sequence, signing evidence, executed-signature status | Zoho Sign |
| Controlled business documents and inspection evidence | Zoho WorkDrive |
| Tenant portal and approved maintenance workflow records | Zoho Creator, when approved |
| Public marketing pages and approved entry points | Zoho Sites |
| Sanitized source code, schemas, tests, runbooks, and deployment evidence | GitHub |
| Secrets and credential values | Approved secret/configuration facility |

Catalyst may keep operational state needed for safe processing, such as an event receipt, idempotency key, retry state, delivery attempt, job status, or sanitized audit fact. It must not silently become a competing CRM, ledger, contract vault, or document repository.

### CAT-011 GH repository observations

The live public repository identifies Catalyst as the runtime for at least these integration responsibilities:

- Zillow-to-CRM lead intake under `src/zoho-crm/integrations/zillow-lead-intake/`.
- Zoho Payments returned-payment webhook handling under `src/zoho-payments/webhooks/returned-payment-fee/`.
- `catalyst-config.json`, environment-variable documentation, security models, operations runbooks, tests, and deployment checklists for those services.

`REPO-OBSERVED`: A repository implementation documents intended code and controls. It does not prove that the same revision is deployed, configured, healthy, or receiving production traffic.

## CAT-020 Platform selection map

| Need | Preferred Catalyst component | Main reason | Important control |
|---|---|---|---|
| Short request/response logic | Basic I/O Function | Managed function with JSON response and REST execution API | Authenticate, validate input, bound work |
| Custom HTTP routing or framework behavior | Advanced I/O Function | Expressive HTTP server behavior | API Gateway, timeouts, no unbounded work |
| Full web service or custom framework | AppSail | Managed Java/Node/Python runtime or OCI container | Health checks, scaling, secrets, rollback |
| Multi-step stateful orchestration | Circuits | JSON-defined workflow across function tasks and conditions | Regional availability, retries, compensation |
| Scheduled or queued work | Job Scheduling | Job pools, jobs, and cron targeting Functions, webhooks, Circuits, or AppSail | Idempotent job keys, duplicate prevention |
| Legacy time trigger | Cloud Scale Cron | Scheduled URL, Cron Function, or Circuit invocation | Treat migration to Job Scheduling as a reviewed change |
| Event-driven integration | Signals or Event Listeners | Event bus or component/custom/Zoho events | Schema versioning, replay safety, dead-letter handling |
| Relational operational state | Data Store + ZCQL | Tables, rows, relations, permissions, bulk operations | Schema registry, indexes, bounded queries |
| Flexible key/document access | NoSQL | Partition-oriented low-latency data | Partition design, index and query validation |
| Object storage | Stratus | Buckets, objects, permissions, CORS, events | Private-by-default permissions and retention |
| Legacy folder-based files | File Store | Folder/file API and role-based access | No subfolders; review Stratus migration |
| Short-lived acceleration | Cache | Segment/key/value storage | Never treat cache as source of truth |
| Search across indexed table columns | Search Integration | Project-wide indexed search | Index only approved columns; paginate |
| Public API mediation | API Gateway | Routing, auth, method rules, throttling | Enabling it changes direct endpoint access |
| Frontend hosting | Slate or Web Client Hosting | Framework deployment or basic client hosting | Keep backend auth and secrets server-side |
| Application authentication | Catalyst Authentication/User Management | Hosted/embedded/third-party auth, roles, users | Identity proofing and authorization are separate |
| CI/CD | Pipelines or Git integration/CLI | Build, test, deploy automation | Production approval and immutable evidence |
| Conversational interface | ConvoKraft | Bots, actions, NLU, Functions/Deluge/webhook logic | No autonomous high-risk action without gate |
| No-code model pipeline | QuickML | Data/ML pipelines and versioned endpoints | Bias, drift, privacy, human review |

## CAT-030 Projects, environments, regions, and identifiers

### CAT-031 Identifier model

Common identifiers include:

| Identifier | Purpose | Rule |
|---|---|---|
| Project ID | Routes API and SDK operations to one Catalyst project | Store as environment configuration; never guess |
| Organization ID / `CATALYST-ORG` | Selects a non-default organization | Omission uses the default organization; make selection explicit in automation |
| ZAID / project application ID | Used by some application-authentication flows | Keep distinct from Project ID and verify in console |
| Function ID and function name | Executes or routes a function | Stable aliasing and deployment manifest required |
| Table ID or table name | Data Store resource selector | Prefer governed names plus verified IDs where required |
| ROWID | Catalyst-generated row identifier | Do not expose as authorization proof |
| Segment ID | Cache namespace | Configuration, not code constant unless governed |
| Folder/file IDs | File Store selectors | Never infer from names alone |
| Job pool, job, cron, circuit IDs/names | Orchestration selectors | Capture returned IDs and environment |

### CAT-032 Development and Production

Catalyst projects separate Development and Production. REST calls can include `Environment: Development`. Current API guidance states that when a project is already deployed to Production, API requests default to Production unless Development is explicitly selected; a project not deployed to Production runs requests in Development.

Operational rule:

- Every script, runbook, smoke test, and incident record must name the environment.
- Never reuse production webhook URLs or credentials in Development fixtures.
- Promotion requires version/commit, environment configuration manifest, deployment result, smoke test, monitoring, and rollback/forward-repair evidence.
- Development success is not proof of Production configuration, permissions, data shape, limits, or connectivity.

### CAT-033 Data centers and API domains

The REST reference uses a DC-specific `{api-domain}`. The CLI command reference currently documents the data-center option values `us`, `eu`, `in`, `jp`, `sa`, `au`, and `ca`. Do not construct a domain from memory. Resolve the account's actual data center and use the official accounts/API domain mapping for that region.

`VOLATILE`: Components are not uniformly available in every region. For example, current Circuits API documentation lists regional exclusions. Recheck the exact target data center before designing around Circuits, Job Scheduling targets, QuickML, Signals, or other newer services.

## CAT-040 Authentication, authorization, and connections

### CAT-041 REST OAuth contract

Typical Catalyst REST calls use:

```http
Authorization: Zoho-oauthtoken {access_token}
Content-Type: application/json
CATALYST-ORG: {org_id}
Environment: Development
```

Only `Authorization` is generally mandatory for OAuth-protected endpoints. `Content-Type` is required when the selected operation expects JSON or form data. Organization and environment headers are contextual. Some application authentication endpoints have different requirements; follow the endpoint page exactly.

Access tokens expire. Refresh tokens remain valid until revoked according to the OAuth contract. Never store a client secret, access token, refresh token, Catalyst CLI token, connection credential, webhook secret, or signed URL in GitHub, logs, PDFs, fixtures, or client-side JavaScript.

### CAT-042 Scope families

The REST reference uses least-privilege scopes, including families such as:

| Resource | Representative scope family |
|---|---|
| Projects/import/export | `ZohoCatalyst.projects.*`, `ZohoCatalyst.project.import.*`, `ZohoCatalyst.project.export.*` |
| Authentication and users | `ZohoCatalyst.authentication.*`, `ZohoCatalyst.projects.users.*` |
| Tables, columns, rows, bulk | `ZohoCatalyst.tables.*`, `ZohoCatalyst.tables.columns.*`, `ZohoCatalyst.tables.rows.*`, `ZohoCatalyst.tables.bulk.*` |
| NoSQL | `ZohoCatalyst.nosql.*`, `ZohoCatalyst.nosql.item.*` |
| Files | `ZohoCatalyst.files.*` |
| Cache | `ZohoCatalyst.cache.*` |
| Functions | `ZohoCatalyst.functions.EXECUTE` |
| Circuits | `ZohoCatalyst.circuits.EXECUTE` |
| Search | `ZohoCatalyst.search.READ` |
| Email | `ZohoCatalyst.email.CREATE` |
| Notifications | `ZohoCatalyst.notifications.web`, `ZohoCatalyst.notifications.mobile` |
| ML Kit | `ZohoCatalyst.mlkit.READ` |
| SmartBrowz | `ZohoCatalyst.pdfshot.execute`, `ZohoCatalyst.dataverse.execute` |
| Pipelines | `ZohoCatalyst.pipeline.READ`, `ZohoCatalyst.pipeline.execution.CREATE` |
| Cron / Job Scheduling | `ZohoCatalyst.cron.*` and operation-specific scopes |

This is a family index, not a substitute for the exact endpoint page. Use the minimum operation scope and separate read-only monitoring identities from deployment or mutation identities.

### CAT-043 Catalyst Connections

Connections provide governed OAuth access to default Zoho services or custom services. Use them when Catalyst logic must call CRM, Books, Creator, WorkDrive, Sign, Mail, Twilio, or another protected API.

Connection controls:

- One connection should have a named business purpose and least-privilege scopes.
- Document owner, service, scopes, data center, environment, renewal/reauthorization plan, consumers, and revocation procedure without storing secret values.
- Separate Development and Production authorization.
- A connection name is tenant-specific and `LIVE-METADATA REQUIRED`.
- If Signals or another service can employ a connection directly, the event rule must still restrict the target and payload.
- Reauthorization is an operational dependency. Alert before business-critical credentials expire or are revoked where the provider exposes such evidence.

## CAT-050 REST API conventions and error handling

### CAT-051 Base route and response shape

Many Cloud Scale REST endpoints use:

```text
{api-domain}/baas/v1/project/{project_id}/...
```

Success responses commonly contain `status: "success"` and `data`. Do not assume every endpoint returns the same shape: downloads can stream bytes, some calls return no body, long-running jobs return status handles, and authentication endpoints differ.

### CAT-052 Error classes

Current REST documentation includes these representative conditions:

| HTTP/status | Error example | Handling rule |
|---|---|---|
| 400 | `MISSING_VALUE`, `MISMATCH`, `ZCQL_QUERY_ERROR` | Validate schema; do not retry unchanged input |
| 401 | `UNAUTHORISED`, `NO_ACCESS` | Refresh/re-authorize only through approved credential flow; check scope and identity |
| 403 | `API_LIMIT_REACHED`, `INVALID_OPERATION`, `VERIFICATION_NEEDED` | Stop, inspect quota/permission/account state |
| 404 | invalid resource/name variants | Reconcile environment and metadata; do not create a replacement blindly |
| 409 | `CONFLICT`, `DUPLICATE_ENTRY`, `DUPLICATE_OPERATION`, `DUPLICATE_VALUE` | Treat as possible idempotent replay or state conflict; reconcile |
| 410 | `EXPIRED`, `EXPIRED_LOG` | Recreate or re-fetch only when safe |
| 429 | `TOO_MANY_REQUESTS` | Exponential backoff with jitter and a bounded retry budget |
| 500/202 function error | `EMAIL_ERROR`, `FUNCTION_ERROR` | Capture correlation metadata, retry only if action is idempotent |

Never log full request bodies containing tenant data, tokens, signed URLs, document contents, or payment details. Log an event/correlation ID, sanitized operation name, target alias, attempt count, status class, latency, and outcome.

## CAT-100 Serverless Functions

### CAT-101 Function types

Catalyst's current Functions overview documents five general server-side function types:

| Type | Invocation model | Typical GH use |
|---|---|---|
| Basic I/O | Direct API/SDK execution with JSON output | Small authenticated service operation |
| Advanced I/O | HTTP application behavior | Webhook receiver or routed API |
| Cron Function | Triggered by a configured cron schedule | Bounded reconciliation or maintenance job |
| Event Function | Triggered by Event Listeners or Signals | Decoupled event processing |
| Integration Function | Invoked by supported Zoho/Catalyst integration | ConvoKraft or service integration logic |

All five general types support Java, Node.js, and Python. Current documentation marks Integration Functions unavailable in the EU, AU, IN, and CA data centers; recheck the target region before selecting them.

The documentation navigation also provides separate pages for Browser Logic Functions and Job Functions. Browser Logic is a specialized SmartBrowz function type that currently supports Java and Node.js. A Job Function is a specialized, non-HTTPS target for the separate Job Scheduling service and currently supports Java, Node.js, and Python. Do not count either as a sixth general server-side type or treat a Job Function as interchangeable with a Cron Function. Revalidate regional availability and the exact creation/invocation page before choosing either capability.

Only Basic I/O functions are directly executable through the general function execution REST API:

```text
GET|POST|PUT|DELETE {api-domain}/baas/v1/project/{project_id}/function/{function_id}/execute
Scope: ZohoCatalyst.functions.EXECUTE
```

The current API page lists GET, POST, PUT, and DELETE. API Gateway can expose GET, PUT, POST, DELETE, PATCH, or `ANY` routes to eligible targets.

### CAT-102 Function design contract

Every production function should define:

- input schema, maximum accepted body/file size, and content types;
- authentication and authorization requirements;
- stable idempotency key and replay window for externally triggered mutations;
- upstream and downstream timeouts;
- bounded retry policy with classification of retryable statuses;
- sanitized logging and correlation identifiers;
- response schema and error taxonomy;
- runtime/memory configuration and expected execution duration;
- environment variables/configuration keys without their values;
- tests, health/smoke check, alert, rollback or forward-repair procedure;
- system-of-record ownership for every written fact.

### CAT-103 Function anti-patterns

- Doing unbounded pagination or bulk processing inside one synchronous invocation.
- Returning success before a required durable handoff is stored.
- Treating a retry as a new business event.
- Relying on function memory or local disk as durable state.
- Placing secrets or tenant data in source, exception messages, or console logs.
- Calling a financial, Sign send, Mail send, or Twilio send endpoint before writing an idempotent intent record.
- Letting one function own unrelated CRM, accounting, contract, and communications policies.

## CAT-110 AppSail and hosted services

AppSail is the managed web-service platform. It supports Catalyst-managed Java, Node.js, and Python runtimes and custom OCI-compliant Linux AMD64 images from supported registries. Unlike Catalyst Functions, an AppSail service can use a conventional web framework and is not required to follow a Catalyst function template. Catalyst SDK components remain available inside the service.

Use AppSail when the workload needs:

- a framework/router, multiple endpoints, middleware, or a conventional service lifecycle;
- a runtime or dependency model better suited to an application than a short function;
- custom container packaging;
- explicit health behavior and service-level scaling configuration.

Do not move a simple webhook to AppSail merely because it is available. Additional runtime flexibility also creates more dependency, image, health, patching, and startup responsibilities.

AppSail production checklist:

1. Pin and scan dependencies/container base images.
2. Define startup command, port, memory, disk, environment variables, and health endpoint.
3. Validate graceful shutdown and request timeout behavior.
4. Keep secrets outside source and container layers.
5. Enforce authentication at API Gateway/service middleware.
6. Log only sanitized metadata.
7. Test cold start, retry, duplicate event, downstream outage, and partial failure.
8. Record deployed version and a verified rollback path.

## CAT-120 API Gateway

API Gateway routes client requests to Basic I/O Functions, Advanced I/O Functions, and the Web Client. It supports route/method mapping, optional authentication, and throttling.

### CAT-121 Critical enablement behavior

> Enabling API Gateway disables Security Rules and makes direct function/web-client URLs inaccessible until APIs are configured. Inventory every exposed target and prepare the complete route set before enabling it.

Current documented behavior:

| Capability | Security Rules | API Gateway |
|---|---|---|
| Route customization | Basic target access | Separate request and target paths |
| Methods | GET, PUT, POST, DELETE, PATCH | Same methods plus `ANY` for eligible function targets |
| Authentication | Catalyst User or OAuth | API Key, Catalyst User, or OAuth |
| Throttling | Not available | General and IP-based throttling |
| Web client routes | Not configurable | GET routes supported |

For OAuth-authenticated gateway calls made as a project administrator or collaborator, current key-concepts documentation requires `ZC-OAUTH-USER: ADMIN`. Ordinary authenticated application users do not send that administrator selector. Treat caller class and required headers as part of each route's contract.

API Gateway returns `429 Too Many Requests` when a configured throttle is exceeded. The current hard limit documented for APIs is 1,000 APIs per project; treat all limits as `VOLATILE`.

### CAT-122 Gateway migration plan

1. Export/inventory current Security Rules and every public URL consumer.
2. Define route, method, target, authentication, throttle, request size, and owner.
3. Create synthetic contract tests for every route.
4. Configure all required APIs before switching clients.
5. Enable in Development and verify negative authorization tests.
6. Promote through controlled deployment.
7. Monitor 401/403/404/429/5xx and latency.
8. Retain the prior configuration and a tested recovery procedure.

## CAT-200 Storage and query services

### CAT-201 Data Store

Data Store is Catalyst's relational persistent store. Tables and their schemas are created in the console; APIs/SDKs manage rows, inspect tables/columns, and perform bulk operations. ZCQL provides SQL-like DML. The service also documents an OLAP database for analytical queries.

Representative REST contract:

| Operation | Method and route | Scope |
|---|---|---|
| Insert row(s) | `POST .../table/{tableIdentifier}/row` | `ZohoCatalyst.tables.rows.CREATE` |
| List rows | `GET .../table/{tableIdentifier}/row?next_token=...&max_rows=...` | `ZohoCatalyst.tables.rows.READ` |
| Update row(s) | `PUT .../table/{tableIdentifier}/row` with `ROWID` | `ZohoCatalyst.tables.rows.UPDATE` |
| Delete row | `DELETE .../table/{tableIdentifier}/row/{row_id}` | `ZohoCatalyst.tables.rows.DELETE` |
| Truncate table | `DELETE .../table/{tableIdentifier}/truncate` | `ZohoCatalyst.tables.rows.DELETE` |
| Execute ZCQL | `POST .../query` | `ZohoCatalyst.zcql.CREATE` |
| Search indexed data | `POST .../search` | `ZohoCatalyst.search.READ` |
| Create bulk read job | `POST .../bulk/read` | `ZohoCatalyst.tables.bulk.READ` |

The row-list API uses a returned `next_token`. Current documentation states a default page of 200 rows when `max_rows` is omitted. Bulk Read can produce CSV pages and supports asynchronous status and callback handling; the current page describes 200,000 rows per result page. Treat counts and quotas as volatile and recheck before implementation.

`DANGER`: Truncate deletes all rows while retaining schema. It is outside normal GH automation scope and requires an explicit destructive-operation approval, backup/recovery proof, exact environment confirmation, and post-action reconciliation.

### CAT-202 ZCQL

ZCQL supports SELECT, INSERT, UPDATE, DELETE, WHERE, HAVING, JOIN, GROUP BY, ORDER BY, LIMIT, and numeric functions subject to documented syntax. The current service has a V2 parser with features unavailable in V1.

Safe query rules:

- Pin/test the parser version in both Development and Production.
- Never concatenate untrusted input into a query. Use the SDK's supported parameterization or strict allowlisted construction.
- Select only needed columns and always bound list queries.
- Index fields used for stable lookup; verify query plans/metrics where available.
- Use an immutable external event ID or business key with a unique constraint for deduplication.
- Do not use ZCQL deletion/truncation as a cleanup shortcut.

### CAT-203 NoSQL

NoSQL provides a non-relational table/item model with indexing, query/search, and batch-oriented operations. Use it when access is naturally partition/key oriented and relational joins are not required. The API scope families include `ZohoCatalyst.nosql.*` and `ZohoCatalyst.nosql.item.*`.

Before selection, document:

- partition/key and item identity;
- maximum item shape and growth;
- required access patterns and secondary indexes;
- consistency expectations;
- expiration/retention behavior;
- batch and pagination strategy;
- tenant/data separation and permission model.

### CAT-204 Cache

Cache stores key/value items in segments. The REST reference documents read, create/update, and delete operations. A representative read is:

```text
GET {api-domain}/baas/v1/project/{project_id}/segment/{segment_id}/cache?cacheKey={cache_key}
```

Current documentation states that the default and maximum cache-item validity is two days. `VOLATILE`: Recheck before depending on it.

Never use Cache as proof that a webhook was processed, a payment was posted, a signature completed, or a notice was sent. Durable idempotency and audit facts belong in a persistent approved store.

### CAT-205 Search Integration

Search executes over indexed Data Store columns:

```text
POST {api-domain}/baas/v1/project/{project_id}/search
Scope: ZohoCatalyst.search.READ
```

The request can select table/columns, set ordering, and use start/end offsets. The current reference lists defaults of `start: 0` and `end: 500`. Index only fields approved for search. Do not index sensitive values merely for convenience, and enforce authorization after search—not only at the UI.

### CAT-206 File Store and Stratus

File Store is the older folder-based object component. It supports folders, file upload/download/details/list/delete, and role permissions. Current documentation notes:

- no subfolders inside File Store folders;
- a 100 MB maximum file upload through the documented API;
- 1 GB of File Store space per project in Development;
- no stated upper storage limit in Production.

Treat these as volatile plan/platform statements rather than a storage design guarantee.

Stratus is the newer object storage service with buckets, objects, bucket/object permissions, event triggers, CORS, and third-party migration paths. Official pages previously described it as Early Access; the current console and region determine availability.

Storage choice rules:

- WorkDrive remains the controlled business-document repository in the GH architecture.
- Catalyst storage may hold transient integration artifacts, deployable assets, or runtime objects only under an approved retention and access model.
- Default private; grant the smallest action (`GetObject`, `PutObject`, `DeleteObject`) over the narrowest paths.
- A deny rule overrides allows in the documented Stratus permission model.
- Validate content type, extension, size, malware policy, object key, and authorization before upload.
- Never expose raw tenant, lease, signature, ID, payment, or maintenance-photo objects through a public bucket.
- Prefer short-lived, audience-bound access rather than permanent public URLs.

## CAT-300 Identity and application security

### CAT-301 Authentication options

Catalyst Authentication documents:

- native hosted authentication;
- native embedded authentication;
- third-party authentication;
- multiple authentication types;
- public signup controls;
- social login options;
- users, roles, whitelisting, custom user validation, and authorized domains;
- authentication email templates;
- cross-domain access patterns.

Authentication proves an identity/session. Authorization must still evaluate role, object ownership, organization/tenant boundary, operation, and current business state.

### CAT-302 User API families

The REST API covers signup/addition, current or specific user details, listing users, update/delete, password reset, and sign-out behavior. Representative routes include:

```text
DELETE {api-domain}/baas/v1/project/{project_id}/project-user/{user_id}
POST   {api-domain}/baas/v1/project/{project_id}/project-user/forgotpassword
GET    {application_domain}/baas/logout?logout=true&PROJECT_ID={project_id}
```

Follow each endpoint's distinct authentication requirements. The password-reset endpoint is documented without OAuth and relies on project/application context; protect it with abuse controls, generic responses where supported, rate limiting, and monitoring.

### CAT-303 Portal/user safety for GH and Sylvara

- Do not automatically create a tenant portal identity from an unqualified lead.
- Separate CRM relationship status, Creator portal status, and Catalyst authentication status.
- Require verified email/identity workflow and an approved lifecycle gate.
- Disable access promptly when the business relationship ends, without deleting required business records.
- Do not use email address, `user_id`, `zuid`, or display role alone as authorization proof for a property/unit.
- A user may access only records related through an approved server-side relationship check.
- Log access decisions as sanitized facts, not full document or record payloads.

## CAT-400 Orchestration and eventing

### CAT-401 Circuits

Circuits are JSON-defined workflows that sequence tasks, conditions, data, and paths and can execute Basic I/O functions. Use a Circuit for an observable multi-step operation where branching, retries, and state transitions are clearer than a single long function.

Before choosing Circuits, verify regional availability. Define compensation rather than pretending downstream SaaS calls form one database transaction.

Example safe conceptual flow:

```text
Validate event -> claim idempotency key -> fetch authoritative record
-> perform one approved mutation -> persist result
-> enqueue downstream reconciliation -> mark complete
```

### CAT-402 Cloud Scale Cron and Job Scheduling

Cloud Scale Cron can schedule a third-party URL, Cron Function, or Circuit. Newer Job Scheduling introduces:

- Job Pools as queues for one target type;
- Jobs as executable work items;
- Cron as submission scheduling;
- targets for Job Functions, webhooks, Circuits, and AppSail;
- instant, predefined-cron, dynamic-cron, and Jobs-component submission patterns.

The current Quick Start states that the shortest interval is one minute. Treat intervals, targets, quotas, and regional availability as volatile.

Every job payload should carry:

| Field | Purpose |
|---|---|
| `schema_version` | Allows compatible parsing |
| `event_id` or `job_key` | Stable idempotency and trace key |
| `event_type` | Routes behavior without guessing payload shape |
| `occurred_at` | Business event time |
| `received_at` | Runtime receipt time |
| `source_system` | Establishes authority |
| sanitized source record ID | Re-fetches current data without embedding PII |
| `attempt` | Bounded retry visibility |
| `correlation_id` | Cross-system trace |

### CAT-403 Event Listeners and Signals

Cloud Scale Event Listeners support component events, custom events, and Zoho events. Documented component examples include Data Store insert/update/delete, Cache put, Authentication signup/delete, File Store upload, and GitHub deployment success/failure. Rules can target Event Functions or Circuits.

Signals is the newer event bus for event-driven architectures and decoupled services. Use versioned event schemas and consumer contracts. Acknowledge only after a durable handoff or successful idempotent completion, according to the service's delivery contract.

Event safety checklist:

1. Verify authenticity and source.
2. Preserve raw bytes only as long as needed for signature verification and only in approved secure memory/storage.
3. Parse against a versioned schema.
4. Claim an idempotency record atomically.
5. Re-fetch authoritative state before money, lease, document, or messaging mutations.
6. Treat duplicate/out-of-order events as normal.
7. Bound retries; route persistent failures to an operator queue.
8. Record sanitized receipt/outcome and correlation ID.

## CAT-500 Mail, notifications, and conversational services

### CAT-501 Catalyst Mail and push

Catalyst Mail supports email configuration, SMTP configuration, domains, and sending. Push Notifications covers iOS, Android, and web.

Do not confuse Catalyst Mail with Zoho Mail's mailbox APIs. Catalyst Mail is an application notification capability; Zoho Mail manages organizational mailboxes, folders, and messages.

For every outbound notification:

- select an approved template/version;
- verify recipient authorization and current contact preference;
- prevent duplicates with a stable communication intent key;
- avoid sensitive content in subject, preview text, push body, or logs;
- store provider message/delivery identifiers where policy permits;
- handle bounce, failure, unsubscribe, and suppression events;
- never represent provider acceptance as confirmed receipt or legal delivery.

### CAT-502 ConvoKraft

ConvoKraft builds NLU-driven conversational bots using bots, actions, parameters, responses, and business logic. Action logic can use Catalyst Integration Functions, Deluge Functions, or webhooks. SmartTrain can ingest custom training data.

For GH/Sylvara:

- A bot may answer approved public or authenticated operational questions.
- It must not determine applicant qualification, legal rights, accounting treatment, deposit deductions, fees, or enforcement actions.
- High-risk actions require explicit confirmation and server-side authorization; prefer a handoff rather than autonomous execution.
- Training sources must be approved, current, non-privileged, and appropriate for the bot's audience.
- Never train on raw tenant records, signed documents, payment details, credentials, production logs, or unrestricted mailbox content.
- Treat generated text as untrusted until validated against the owning record/policy.

## CAT-600 DevOps, deployment, and observability

### CAT-601 CLI resource lifecycle

The Catalyst CLI supports project selection, initialization, local serve, pull, deploy, functions, AppSail, client, API Gateway, Data Store bulk import/export, configuration, events, and infrastructure-as-code export/import.

Representative commands:

```text
catalyst project:list
catalyst project:use {project_id_or_name}
catalyst serve
catalyst deploy
catalyst deploy --only functions:FunctionName
catalyst deploy --only appsail:ServiceName
catalyst pull
catalyst ds:export
catalyst ds:import {csv_path}
catalyst apig:status
catalyst event:generate {source} {action}
```

Never place CLI tokens in repository configuration or command history pasted into issues. Use short-lived CI credentials where supported and separate read/test/deploy permissions.

### CAT-602 GitHub integration and Pipelines

Catalyst can integrate with GitHub and deploy a repository with a valid Catalyst project structure and `catalyst.json`. Catalyst Pipelines uses `catalyst-pipelines.yaml`, visual or code editing, stages/jobs/runners, variables, artifacts, and manual or version-control triggers.

GH repository rule:

- GitHub `main` stores reviewed sanitized code and expected configuration names.
- A commit does not deploy automatically unless an approved pipeline explicitly does so.
- No pipeline should deploy a pull-request revision to Production with write-capable secrets before review.
- Build artifacts must be tied to source commit and integrity evidence.
- Production promotion must be human-gated for tenant, payment, invoice, contract, Sign, Mail, Twilio, or authorization changes.

### CAT-603 Deployment evidence contract

For each production change record:

| Evidence | Required value |
|---|---|
| Repository | `GH-Real-Estate/gh-real-estate-ops-code` |
| Commit/release | Exact immutable SHA/tag |
| Catalyst project alias | Sanitized alias; no public operational ID |
| Environment and data center | Exact target |
| Resource | Function/AppSail/API Gateway/Circuit/job/event rule/client |
| Configuration manifest | Names only; secret values excluded |
| Deployed version/time/operator | Runtime evidence |
| Smoke-test result | Positive and negative paths |
| Monitoring/alert | Query/dashboard/alert owner |
| Rollback/forward repair | Exact procedure and trigger |

### CAT-604 Monitoring and alert design

Use Catalyst logs, metrics, Application Alerts, function/job/event statistics, API Gateway status, and downstream provider evidence as applicable. Monitor:

- invocation count, success/failure, timeout, latency, and concurrency/throttle events;
- job queued/running/succeeded/failed/expired state;
- event queued/processed/failed/retried state;
- downstream 401/403/409/429/5xx by sanitized target;
- idempotency conflicts and duplicate suppression count;
- reconciliation mismatch count;
- deployment version and configuration drift;
- alert delivery health.

Alerts should be actionable and contain correlation metadata, not tenant PII or full payloads.

## CAT-700 GH and Sylvara production patterns

### CAT-701 Zillow or form intake to CRM Leads

Approved boundary:

```text
External intake -> Catalyst validation/normalization -> CRM Leads only
```

The intake function must not automatically create Contacts, Rental Applications/Deals, leases, Books customers/invoices, portal users, WorkDrive folders, or Sign requests. It should validate allowed fields, normalize phone/email cautiously, apply a stable source-event deduplication key, call CRM with a least-privilege connection, store sanitized outcome evidence, and return an appropriate retry-safe response.

### CAT-702 Zoho Payments returned-payment event

Approved boundary:

```text
Payments webhook -> verify -> deduplicate -> re-fetch payment state
-> approved policy gate -> one Books RF invoice -> reconcile
```

Requirements:

- Verify current webhook authenticity using the exact provider mechanism.
- Store a durable event/idempotency record before the Books mutation.
- Do not trust the event body alone for balance, customer, or status.
- Do not combine returned-payment fees with the Books late-fee or delinquent-interest automations.
- Obtain approved accounting/legal policy for charge amount, timing, account/item/tax handling, and reversals.
- Record Books invoice ID and provider event ID; a retry must return/reconcile the same result.

### CAT-703 Zoho Sign callback reconciliation

```text
Sign callback -> authenticate -> deduplicate -> fetch current request/document
-> validate expected state transition -> update approved CRM/Contracts status
-> place executed output in approved WorkDrive location -> reconcile
```

Never log the signed document, signatures, recipient authentication codes, or full callback payload. A callback alone is not authority to change a financial ledger or tenant lifecycle without the approved state machine.

### CAT-704 Scheduled reconciliation

Use Job Scheduling/Cron for a bounded, paginated reconciliation—not a blind replay. Select one ownership direction per fact, compare stable IDs/status/version, classify mismatches, auto-repair only low-risk approved cases, and route material mismatches for review.

### CAT-705 Twilio communications gateway

Catalyst may host Twilio webhook and send orchestration. The service must validate Twilio request signatures, normalize E.164 destinations, enforce consent and quiet-hour/campaign policy, use a stable outbound intent key, store only sanitized delivery identifiers/status, process callbacks idempotently, and prevent inbound content from becoming executable instructions.

### CAT-706 Creator portal backend

Creator remains the portal/workflow owner where approved. Catalyst can provide secure middleware when Creator needs a validated external integration or computation. Avoid duplicating Creator forms/reports in Data Store without a written ownership, retention, and reconciliation contract.

## CAT-800 Security and reliability patterns

### CAT-801 Canonical webhook state machine

| State | Meaning | Allowed next state |
|---|---|---|
| `received` | Authenticated transport received | `claimed`, `rejected` |
| `claimed` | Durable idempotency key acquired | `validated`, `failed_retryable` |
| `validated` | Schema and business preconditions pass | `applied`, `manual_review` |
| `applied` | One approved mutation completed | `reconciled`, `failed_retryable` |
| `reconciled` | Owning system confirms expected outcome | terminal |
| `rejected` | Invalid auth/schema/nonpermitted event | terminal |
| `manual_review` | Policy/data ambiguity | approved operator action only |
| `failed_retryable` | Transient failure within retry budget | `claimed`, `dead_letter` |
| `dead_letter` | Budget exhausted | operator disposition |

### CAT-802 Idempotency record

```json
{
  "schema_version": "1",
  "source_system": "provider_alias",
  "event_id": "opaque-stable-event-id",
  "event_type": "approved.event.type",
  "payload_digest": "sha256-of-canonical-approved-input",
  "state": "received",
  "attempt_count": 1,
  "correlation_id": "generated-trace-id",
  "result_system": null,
  "result_id": null,
  "received_at": "RFC3339 timestamp",
  "updated_at": "RFC3339 timestamp"
}
```

Use a unique compound key on `(source_system, event_id)`. Do not store sensitive payloads merely to calculate idempotency. If the provider lacks an event ID, derive a versioned digest only from stable, approved, non-secret fields.

### CAT-803 Outbound API wrapper contract

```text
callProvider(operation, targetAlias, idempotencyKey, request)
  validate request schema
  obtain least-privilege connection/credential
  set connect/read deadline
  send correlation and provider idempotency header when supported
  classify response
  retry only transient and idempotent operations
  redact response before logging
  persist stable provider result ID/status
  reconcile from provider on ambiguous timeout
```

### CAT-804 Threat model checklist

- Broken authentication or authorization
- Forged/replayed webhook
- Cross-tenant record access
- Server-side request forgery through user-supplied URL
- SQL/ZCQL or command injection
- Malicious file upload or content-type confusion
- Secret leakage through source, logs, error pages, artifacts, or client bundles
- Duplicate financial/document/message action
- Out-of-order provider event
- Dependency or container compromise
- Denial of service and retry storm
- Public bucket/object exposure
- Privilege accumulation in OAuth scopes or connections
- Stale production deployment/configuration drift

## CAT-900 Testing, change control, and AI answer template

### CAT-901 Minimum test matrix

1. Valid authenticated request.
2. Missing/invalid authentication.
3. Authorized user without object permission.
4. Invalid schema/type/oversized input.
5. Duplicate identical event.
6. Same ID with conflicting digest.
7. Out-of-order event.
8. Downstream timeout before response.
9. Downstream 409/429/5xx.
10. Partial success followed by retry.
11. Pagination boundary and empty page.
12. Development/Production configuration separation.
13. Secret and PII log-redaction test.
14. Alert delivery and dead-letter/manual-review path.
15. Rollback or forward-repair smoke test.

### CAT-902 AI answer template

When asked to design or change a Catalyst workflow, answer in this order:

1. **Owning system and allowed boundary.**
2. **Verified Catalyst component and why it fits.**
3. **Unknown live metadata/configuration to retrieve.**
4. **Auth, scopes, environment, data center, and connection plan.**
5. **Versioned input/output/event schema.**
6. **Idempotency, retries, timeouts, and reconciliation.**
7. **Security/privacy/logging controls.**
8. **Implementation outline and exact official references.**
9. **Tests, deployment evidence, monitoring, and rollback.**
10. **Policy or human approvals still required.**

Do not output deploy-ready mutation code until exact project metadata, field/resource names, connection aliases, and policy gates are provided or explicitly represented as placeholders.

## Appendix A - Official source registry

All entries were reviewed against current official Catalyst documentation on 2026-07-20. Page contents, plans, regions, runtimes, and limits remain volatile.

### A-001 Core API and SDK

- REST API overview, prerequisites, scopes, endpoints, and errors: https://docs.catalyst.zoho.com/en/api/introduction/overview-and-prerequisites/
- CLI command reference: https://docs.catalyst.zoho.com/en/cli/v1/cli-command-reference/
- CLI serve resources: https://docs.catalyst.zoho.com/en/cli/v1/serve-resources/introduction/
- CLI deploy resources: https://docs.catalyst.zoho.com/en/cli/v1/deploy-resources/introduction/
- CLI deployment options: https://docs.catalyst.zoho.com/en/cli/v1/deploy-resources/deploy-options/
- CLI pull resources: https://docs.catalyst.zoho.com/en/cli/v1/pull-resources/pull-all-resources/

### A-002 Compute and routing

- Functions: https://docs.catalyst.zoho.com/en/serverless/help/functions/introduction/
- Function deployment: https://docs.catalyst.zoho.com/en/cli/v1/deploy-resources/deploy-functions/
- AppSail: https://docs.catalyst.zoho.com/en/serverless/help/appsail/introduction/
- Add AppSail: https://docs.catalyst.zoho.com/en/cli/v1/add-appsail/
- Deploy AppSail: https://docs.catalyst.zoho.com/en/cli/v1/deploy-resources/deploy-appsail/
- Circuits: https://docs.catalyst.zoho.com/en/serverless/help/circuits/introduction/
- API Gateway: https://docs.catalyst.zoho.com/en/cloud-scale/help/api-gateway/introduction/
- API Gateway key concepts: https://docs.catalyst.zoho.com/en/cloud-scale/help/api-gateway/key-concepts/
- Connections: https://docs.catalyst.zoho.com/en/cloud-scale/help/connections/introduction/

### A-003 Storage and query

- Data Store: https://docs.catalyst.zoho.com/en/cloud-scale/help/data-store/introduction/
- NoSQL: https://docs.catalyst.zoho.com/en/cloud-scale/help/nosql/introduction/
- ZCQL: https://docs.catalyst.zoho.com/en/cloud-scale/help/zcql/introduction/
- ZCQL V2 syntax/exceptions: https://docs.catalyst.zoho.com/en/cloud-scale/help/zcql/syntax-exceptions/
- File Store: https://docs.catalyst.zoho.com/en/cloud-scale/help/file-store/introduction/
- File Store features: https://docs.catalyst.zoho.com/en/cloud-scale/help/file-store/key-features/
- Stratus: https://docs.catalyst.zoho.com/en/cloud-scale/help/stratus/introduction/
- Stratus permissions: https://docs.catalyst.zoho.com/en/cloud-scale/help/stratus/stratus-permissions/
- Stratus CORS: https://docs.catalyst.zoho.com/en/cloud-scale/help/stratus/stratus-config/bucket-cors/
- Cache: https://docs.catalyst.zoho.com/en/cloud-scale/help/cache/introduction/

### A-004 Identity, triggers, and notifications

- Authentication: https://docs.catalyst.zoho.com/en/cloud-scale/help/authentication/introduction/
- User Management: https://docs.catalyst.zoho.com/en/cloud-scale/help/authentication/user-management/introduction/
- Cross-domain access: https://docs.catalyst.zoho.com/en/cloud-scale/help/authentication/cross-domain-access/
- Cloud Scale Cron: https://docs.catalyst.zoho.com/en/cloud-scale/help/cron/introduction/
- Event Listeners: https://docs.catalyst.zoho.com/en/cloud-scale/help/event-listeners/introduction/
- Component Event Listeners: https://docs.catalyst.zoho.com/en/cloud-scale/help/event-listeners/component-event-listeners/
- Catalyst Mail: https://docs.catalyst.zoho.com/en/cloud-scale/help/mail/introduction/
- Web Client Hosting: https://docs.catalyst.zoho.com/en/cloud-scale/help/web-client-hosting/introduction/

### A-005 Newer services and DevOps

- Job Scheduling: https://docs.catalyst.zoho.com/en/job-scheduling/getting-started/introduction/
- Job Scheduling components: https://docs.catalyst.zoho.com/en/job-scheduling/getting-started/components-of-job-scheduling/
- Job Pool: https://docs.catalyst.zoho.com/en/job-scheduling/help/jobpool/introduction/
- Jobs: https://docs.catalyst.zoho.com/en/job-scheduling/help/job/introduction/
- Job Scheduling Cron: https://docs.catalyst.zoho.com/en/job-scheduling/help/cron/introduction/
- Signals: https://docs.catalyst.zoho.com/en/signals/getting-started/introduction/
- Pipelines: https://docs.catalyst.zoho.com/en/pipelines/getting-started/introduction/
- Pipeline model: https://docs.catalyst.zoho.com/en/pipelines/help/pipelines/introduction/
- Pipeline YAML: https://docs.catalyst.zoho.com/en/pipelines/help/catalyst-pipelines.yaml/introduction/
- GitHub integration: https://docs.catalyst.zoho.com/en/devops/help/github-integration/implementation/
- Slate: https://docs.catalyst.zoho.com/en/slate/help/introduction/
- Slate Git integration: https://docs.catalyst.zoho.com/en/slate/help/git-integration/deploy-from-private-repository/
- Slate rollback: https://docs.catalyst.zoho.com/en/slate/help/rollback-deployment/

### A-006 AI and conversational services

- QuickML: https://docs.catalyst.zoho.com/en/quickml/getting-started/introduction/
- QuickML endpoints: https://docs.catalyst.zoho.com/en/quickml/help/pipeline-endpoints/
- ConvoKraft: https://docs.catalyst.zoho.com/en/convokraft/getting-started/introduction/
- ConvoKraft bots: https://docs.catalyst.zoho.com/en/convokraft/help/bots/introduction/
- ConvoKraft action models: https://docs.catalyst.zoho.com/en/convokraft/help/actions/overview/models/
- ConvoKraft Catalyst Integration Functions: https://docs.catalyst.zoho.com/en/convokraft/help/actions/bot-logic/catalyst-integration-functions/
- ConvoKraft SmartTrain: https://docs.catalyst.zoho.com/en/convokraft/help/smarttrain/

## Appendix B - Maintenance manifest

Refresh this knowledge base when any of these changes occur:

- REST API version, base route, OAuth scope, or response/error contract changes.
- New or retired Catalyst service, function type, runtime, data center, or regional restriction.
- API Gateway enablement/migration behavior or authentication/throttling changes.
- Stratus, Signals, Job Scheduling, Pipelines, Slate, QuickML, or ConvoKraft Early Access/general-availability change.
- CLI command, project structure, `catalyst.json`, or deployment behavior changes.
- GH repository ownership map, security rule, automation responsibility, or production integration changes.
- Live project metadata, table schema, connection, webhook contract, domain, or deployment configuration changes.

The refresh owner must update the verification date, exact source URL, affected section IDs, migration impact, tests, and release notes. A documentation update does not deploy or modify a live Catalyst project.
