# Zoho CRM Engineering and Automation Knowledge Base

**Document ID:** GH-ZOHO-CRM-KB  
**Verification date:** 2026-07-20  
**Primary audience:** ChatGPT, Codex, solution architects, and maintainers building GH Real Estate and Sylvara systems  
**Evidence policy:** This dossier uses official Zoho documentation and the supplied GH system maps. It is an engineering reference, not a substitute for live tenant metadata, current edition entitlements, legal review, or deployment evidence.

## 1. Retrieval contract for AI agents

Read this section before generating code or proposing a CRM change.

### Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `DOC-VERIFIED` | Supported by a cited official Zoho page as of the verification date | Still check the changelog for high-risk work |
| `LIVE-METADATA REQUIRED` | The value is organization-specific or can change without the code changing | Query CRM metadata or use a sanitized export before coding |
| `TENANT-SPECIFIC` | Depends on GH/Sylvara layouts, profiles, editions, portals, connections, or naming | Do not infer from examples or UI labels |
| `VOLATILE` | Limits, editions, credits, or early-access behavior can change | Recheck the cited live page immediately before implementation |
| `GH-POLICY` | Required by the supplied GH architecture or change-control documents | Treat as a project constraint unless an approved decision supersedes it |
| `DESIGN RECOMMENDATION` | Engineering judgment, not a Zoho guarantee | Validate against requirements and tenant behavior |

### Non-negotiable rules

1. Never invent a module API name, field API name, layout ID, related-list API name, picklist value, portal user type, function name, connection name, or organization ID.
2. UI labels are not API contracts. Resolve identifiers from the live metadata APIs and preserve IDs/API names in a versioned sanitized manifest.
3. Never place OAuth client secrets, refresh tokens, connection secrets, tenant PII, lease documents, bank data, or production payloads in prompts, repositories, PDFs, logs, or test fixtures.
4. Treat CRM REST APIs, CRM Deluge integration tasks, functions, workflows, and widgets as different execution interfaces. Trigger defaults and limits may differ by interface.
5. Repository state is not proof of deployment. Preserve test output, deployment evidence, smoke-test results, and rollback notes separately.
6. For money, leases, notices, tenant records, access/privacy controls, or deletion, require a dry run, duplicate checks, manual verification, and a tested rollback/reconciliation path.

## 2. CRM's role in the GH/Sylvara architecture

`GH-POLICY` Zoho CRM owns the operational relationship and pipeline records for:

- leads and rental inquiries;
- applicants and contacts;
- properties and units;
- rental applications and leasing pipeline stages;
- maintenance cases and other operational relationship records.

CRM does **not** own accounting ledgers, posted invoices, payment settlement, or signed-contract truth. Those belong to the appropriate finance and contract/signature systems. CRM may store external IDs, status projections, links, and reconciliation timestamps, but it must not become a second ledger or a second signed-document repository.

### Current module map

| Business object | Current CRM mapping | Status and implementation rule |
|---|---|---|
| Lead / inquiry | `Leads` | Known API name; live fields/layouts still required |
| Property | `Accounts` with a renamed display label | Use `Accounts` in API calls; never use the renamed UI label as the API name |
| Unit | Custom module, previously observed as `Units` | `LIVE-METADATA REQUIRED`; reverify before every new integration |
| Person / tenant / applicant | `Contacts` | Separate role/state semantics from the person record itself |
| Rental application | `Deals` | Pipeline, stage, layout, required fields, and blueprint are tenant-specific |
| Maintenance request | `Cases` | Status, priority, assignment, SLA, and portal visibility are tenant-specific |
| Inspection | Custom module | API name and schema unresolved |
| Equipment / asset | Custom module | API name and schema unresolved |
| Pets / animals | Design unresolved | Do not implement as a subform, custom module, or multi-select lookup without an approved data-model decision |
| Storage units | Design/API unresolved | Discover and document before automation |

`GH-POLICY` The Zillow boundary writes inquiry data to CRM `Leads` only. It does not create Contacts, applications, leases, Books transactions, portal users, or WorkDrive documents without a separately approved workflow.

### Tenant lifecycle placement

1. Inquiry enters CRM as a Lead.
2. Showing and qualification activity remains operational CRM state.
3. Application is represented in the approved application object/pipeline.
4. Approved lease terms flow to Contracts/Sign; CRM stores reference/status, not the signed-document authority.
5. Books/Billing owns invoices, rent, payments, and accounting events; CRM receives projections or links when useful.
6. Creator/Sites provides the approved tenant experience; maintenance state may synchronize with CRM Cases.
7. Move-out/renewal state is coordinated through explicit status transitions and reconciled external IDs.

## 3. Platform and execution model

Zoho CRM is simultaneously a configurable database, a workflow engine, a UI platform, and an API service. Design must identify which layer owns each rule.

| Surface | Best use | Important caveat |
|---|---|---|
| REST API v8 | External services, metadata discovery, high-control integrations | OAuth, credits, concurrency, rate limits, DC-aware base URL |
| Deluge CRM v8 tasks | Short operations from Zoho functions/workflows | Wrapper signatures and automation defaults are interface-specific |
| Workflow rules | Declarative event/time-based automation | Re-entry and trigger behavior must be tested |
| Blueprint | Enforced state machine and transition validation | Not a substitute for record authorization or external reconciliation |
| CRM Functions | Server-side Deluge business logic and endpoints | Synchronous; execution time, line count, response, and credit limits apply |
| Widgets / JS SDK | Embedded custom UI | Browser input is untrusted; enforce authorization server-side |
| CRM Portals | Controlled CRM record access for external users | Current GH map approves Creator for the tenant portal; CRM portal adoption requires an explicit architecture decision |
| Sandbox | Configuration and automation testing | Sandbox behavior and data are not production proof; deployment is a separate controlled step |

Edition availability, per-user entitlements, optional features, and API credits are `VOLATILE` and `TENANT-SPECIFIC`. Check the current account and the cited limits pages before committing to an architecture.

## 4. Authentication, data centers, and scopes

### OAuth 2.0

`DOC-VERIFIED` CRM API v8 uses OAuth 2.0. Send the access token as:

```http
Authorization: Zoho-oauthtoken <access_token>
```

Use the `api_domain` returned with the token response. Do not hardcode `www.zohoapis.com`; the organization and OAuth client may reside in another Zoho data center. Refresh access tokens through the configured OAuth client and store refresh/client credentials in a managed secret store or Zoho Connection, never in Deluge source.

### Scope strategy

Use least privilege and separate read, write, metadata, notification, and administrative connections where practical. Examples of the documented scope families include:

```text
ZohoCRM.modules.<module>.READ
ZohoCRM.modules.<module>.CREATE
ZohoCRM.modules.<module>.UPDATE
ZohoCRM.modules.<module>.DELETE
ZohoCRM.settings.fields.READ
ZohoCRM.apis.READ
ZohoSearch.securesearch.READ
```

The exact scope needed depends on the endpoint. Follow the endpoint's scope table, not a broad remembered scope. `TENANT-SPECIFIC` Profile/module/field permissions still constrain what the authenticated user can see or change. Metadata responses can therefore differ by principal.

### Connection design

- Give connections purpose-specific names such as `crm_ops_read_v1` or `crm_case_write_v1`; never assume a connection exists from an example.
- Record connection owner, authorized scopes, environment, DC, rotation owner, and dependent functions in a sanitized manifest.
- Prefer OAuth connections over legacy API-key patterns.
- Rotate/revoke credentials through change control and run dependency smoke tests afterward.

## 5. Live metadata discovery: required preflight

The safe sequence for every new module integration is:

1. List available REST APIs for the authorized principal.
2. Fetch module metadata and resolve the module API name and supported operations.
3. Fetch fields metadata for data types, API names, lookups, uniqueness, encryption, and permissions.
4. Fetch layout metadata for layout-specific required fields and picklist values.
5. Fetch related-list metadata for related-list API names and returned `href` patterns.
6. Fetch pipeline, blueprint, assignment-rule, portal, and other settings metadata only when the workflow uses them.
7. Save a sanitized, timestamped manifest and review its diff before code changes.

### Core discovery endpoints

```http
GET {api-domain}/crm/v8/__apis
GET {api-domain}/crm/v8/settings/modules/{module_api_name}
GET {api-domain}/crm/v8/settings/fields?module={module_api_name}
GET {api-domain}/crm/v8/settings/fields/{field_id}?module={module_api_name}
GET {api-domain}/crm/v8/settings/layouts?module={module_api_name}
GET {api-domain}/crm/v8/settings/layouts/{layout_id}?module={module_api_name}
GET {api-domain}/crm/v8/settings/related_lists?module={module_api_name}&layout_id={layout_id}
```

`DOC-VERIFIED` Module metadata exposes capability and access information. Field metadata returns fields across layouts; it is not sufficient for layout-specific mandatory state or picklist values. Layout metadata is therefore mandatory when inserting or transitioning records in a known layout. Related-list API calls must use the API name/URL from metadata, not a visible label.

### Sanitized metadata manifest

At minimum, capture:

```yaml
verified_at: 2026-07-20T00:00:00Z
environment: sandbox
module:
  display_label: "<sanitized>"
  api_name: "<live value>"
  id: "<live metadata id>"
  generated_type: "default|custom|linking|subform|web"
  api_supported: true
layouts:
  - id: "<layout id>"
    name: "<sanitized>"
fields:
  - label: "<sanitized>"
    api_name: "<live value>"
    data_type: "<live value>"
    required_by_layout: false
    unique: false
    encrypted: false
    lookup_target: null
    picklist_values: []
related_lists:
  - label: "<sanitized>"
    api_name: "<live value>"
    href: "<returned path>"
```

Never include real record values. Treat the manifest as a cache with an explicit verification date, not eternal truth.

## 6. API v8 family map

The official API reference is the authoritative inventory. This table is a retrieval map, not an exhaustive substitute for endpoint pages.

| Family | Major capabilities | GH/Sylvara relevance |
|---|---|---|
| Metadata | Modules, fields, layouts, related lists, custom views, templates, tags, wizards, pipelines, blueprint, assignment rules, scoring, portals, company settings, currencies, variables, Zia | Schema discovery, safe code generation, lifecycle configuration |
| Records | List/get/create/update/upsert/delete, search, clone, timeline, deleted records, count | Core operational synchronization |
| Relationships | Related records, linking modules, subforms, multi-select lookup, contact roles | Property-unit-contact-application relations; do not guess representation |
| Record actions | Lock/unlock, change owner, convert lead, merge, share, mass actions | Controlled lifecycle operations; high-risk actions require audit and idempotency |
| Content | Attachments, photos, files, mail merge, notes, emails, drafts | Store references carefully; WorkDrive/Sign may remain authoritative document systems |
| Query | Search API and COQL | Incremental reads, reconciliation, cross-module reporting |
| Bulk | Bulk read, bulk write, data backup | Migration/export; workflows and supported field types differ from ordinary record APIs |
| Composite | Multiple dependent/parallel subrequests | Reduce round trips; understand rollback and timeout ambiguity |
| Notifications | Enable/update/get/disable watches | Event-driven integrations with renewal and reconciliation |
| Users/org/security | Organization, users, profiles, roles, territories, groups, sharing | Permission-aware behavior and audit context |
| Portals | Portals, user types, invite/bulk invite/remove users | External CRM access only if architecture explicitly approves it |
| Specialized | Services, appointments, cadences, scoring, assignment thresholds, unsubscribe, recycle bin | Use only after availability and ownership are confirmed |

## 7. Core record operations

### REST patterns

```http
GET    {api-domain}/crm/v8/{module_api_name}
GET    {api-domain}/crm/v8/{module_api_name}/{record_id}
POST   {api-domain}/crm/v8/{module_api_name}
PUT    {api-domain}/crm/v8/{module_api_name}/{record_id}
DELETE {api-domain}/crm/v8/{module_api_name}/{record_id}
POST   {api-domain}/crm/v8/{module_api_name}/upsert
```

Insert/update/upsert accept up to 100 records per ordinary API call. A multi-record response may use HTTP `207 Multi-Status`; inspect every item rather than treating the HTTP status alone as success.

Use field API names in payloads. Common system-required fields documented by Zoho include `Last_Name` for Leads/Contacts, `Account_Name` for Accounts, `Deal_Name` and `Stage` for Deals (and `Pipeline` when enabled), and `Case_Origin`, `Status`, and `Subject` for Cases. `LIVE-METADATA REQUIRED` Layout rules, custom required fields, validation rules, blueprints, and profiles can add more requirements.

Use `yyyy-MM-dd` for date fields and ISO 8601 with the appropriate user/organization offset for datetimes. Do not serialize money as a localized string. Do not send UI labels where IDs or API names are required.

### Automation trigger semantics

For REST record APIs, the documented `trigger` array can control workflow, approval, blueprint, pathfinder, and orchestration behavior on supported operations. The omission/default behavior is defined by the endpoint page and can differ from Deluge task wrappers. For the current CRM v8 Deluge Create Record task, omitting `options_map` executes approval, Blueprint, and orchestration by default, while workflow must be selected explicitly; setting `trigger` to an empty list suppresses all of those CRM automations. An omitted options map and an empty trigger list therefore do not mean the same thing.

**Rule:** decide and document trigger intent for every write. Test the exact interface and operation in sandbox. Never generalize the REST default to a Deluge wrapper or bulk job.

### Concurrency-safe updates

`DOC-VERIFIED` Update and upsert support `If-Unmodified-Since`; stale writes can return `412 ALREADY_MODIFIED`. Use optimistic concurrency for high-value lifecycle fields:

1. read record and authoritative timestamp/version evidence;
2. validate the intended transition;
3. update with `If-Unmodified-Since`;
4. on 412, re-read and reconcile instead of blind retry.

### Idempotency pattern

CRM's ordinary create call should not be treated as automatically idempotent.

- Assign a stable source-event ID and/or source-system ID to a truly unique CRM field.
- Prefer upsert using a deliberately selected unique field when the business semantics are correct.
- Verify uniqueness in metadata and in existing data before relying on it.
- Record external ID, event ID, payload hash, first/last attempt, status, and CRM record ID in an integration ledger.
- Before retrying an ambiguous timeout, search by the idempotency key.
- Do not upsert on a field that can legitimately change, be blank, or contain duplicates.

Zoho documents that duplicate matching can select a matching record; if data contains duplicates, the result may not be the business record intended. Unique constraints and reconciliation are therefore required.

### External ID APIs

CRM v8 also provides an External ID API family. An External ID is a custom single-line CRM field intended to hold a unique identifier from another system. The family supports documented get, insert, update, upsert, search, and related-record operations using the external value; some routes require the documented `X-EXTERNAL` header to identify the external-ID field.

Use this surface when GH/Sylvara has a genuine stable source identifier and the target module supports the operation. Verify the field's External ID/uniqueness configuration and existing data first. An External ID is an integration key, not permission evidence, and it must not contain a secret or sensitive human identifier.

## 8. Reading, searching, pagination, and query

### Get Records

`GET /{module}` supports field selection and pagination. Current documented behavior includes:

- up to 200 records per page;
- selected `fields` are required for list retrieval and capped at 50;
- ordinary `page` pagination covers the first 2,000 records;
- `page_token` supports deeper traversal, documented up to 100,000 records;
- page tokens are user-specific, parameter-bound, and expire after 24 hours;
- `If-Modified-Since` can reduce unchanged reads;
- ordinary list retrieval can truncate rich-text content; retrieve a specific record when full content matters.

Persist a checkpoint only after processing a complete page. Do not reuse a token with altered filters/fields/sort parameters.

### Search API

```http
GET {api-domain}/crm/v8/{module_api_name}/search?criteria=<encoded criteria>
```

The current search API documents a maximum of ten criteria. Search can also use email, phone, or word parameters. `equals` has contains-like behavior in documented cases; do not use it as a uniqueness guarantee. Searching subform or many-to-many data may require the subform/linking module rather than the parent module. The secure-search scope may be required in addition to module read scope.

### Related records

```http
GET {api-domain}/crm/v8/{module}/{record_id}/{related_list_api_name}
```

Use the related-list metadata response to obtain the API name and `href`. Paginate and field-select like other reads. For many-to-many relationships, inspect the linking module and its fields rather than assuming an array embedded in the parent.

### COQL

COQL is CRM's structured query endpoint (`POST /crm/v8/coql`). It uses module and field API names and supports cross-module joins through lookup relationships.

Current documented boundaries include:

- up to 500 fields in `SELECT`;
- up to 25 criteria in `WHERE`;
- up to 2,000 rows per request;
- offset pagination for the same query up to a documented 100,000 rows, followed by keyset-style continuation for larger extraction;
- default ordering by record ID when no explicit order is supplied.

Not all field/relationship types are queryable. The official limitations page lists exclusions including territories, multi-select lookups, some multiline criteria, attachments/file-upload data, and other specialized fields. Build query capability from metadata and test the exact query.

Example shape:

```json
{
  "select_query": "select id, Last_Name, Modified_Time from Leads where Modified_Time >= '2026-07-01T00:00:00-05:00' order by Modified_Time asc limit 0, 2000"
}
```

The example is illustrative; validate datetime literal syntax, field availability, and escape rules against the current COQL page/editor.

## 9. Bulk and composite APIs

### Bulk Read

Use bulk read for large asynchronous exports. The documented job flow is create job, poll job status, and download result. The API reference currently describes export capacities up to 200,000 records for CSV and lower limits for specialized formats. `VOLATILE` Confirm the job and format limits before each migration/export.

### Bulk Write

Bulk write is a migration/import surface, not a drop-in replacement for record APIs.

- Current reference capacity is up to 25,000 records per job.
- Input is a CSV (often inside the expected ZIP/job workflow).
- Attachments, notes, file upload/image fields, and some special data are unsupported.
- Workflows are not supported in the same way as ordinary record writes.
- A current bulk-write initiation cost is 500 API credits.

Validate every result row, preserve the job ID and source file hash, and reconcile success/failure counts to source counts. Never infer business-process completion from “job completed.”

### Composite API

Composite requests can contain up to five subrequests and support parallel/dependent execution and reference substitution. `rollback_on_fail` can provide rollback behavior for supported cases, but external side effects and asynchronous automations still need separate reconciliation. The documented five-minute timeout creates an ambiguity: a timed-out caller must re-query state before retrying.

## 10. API credits, concurrency, and failures

`VOLATILE` The official API limits page is the only authoritative current table. As verified, daily credits use a rolling 24-hour window and differ by edition and licensed-user count. Examples in the current table range from 5,000 for Free to formulas/caps for Standard, Professional, Enterprise/Zoho One, Ultimate, and CRM Plus. Do not bake these numbers into capacity plans without rechecking the account.

Some current credit weights include:

- ordinary insert/update/upsert: one API credit per batch of up to ten records;
- query calls: credit weight varies with requested limit;
- convert lead: five credits;
- send mail: twenty credits;
- bulk read initialization: fifty credits;
- bulk write initialization: five hundred credits.

Current primary concurrency ranges by edition from 5 through 25 requests per organization/app. A separate sub-concurrency pool of 10 applies to specified expensive operations. CRM Deluge integration tasks now consume API credits and have edition-based concurrency, although their concurrency treatment differs from REST sub-concurrency.

### Retry policy

- Classify HTTP status and Zoho response code before retrying.
- Retry only transient errors (`429`, selected `5xx`, network timeout) with bounded exponential backoff and jitter.
- Honor `Retry-After` when present.
- Do not blindly retry validation, permission, duplicate, lock, or stale-update errors.
- Re-read state before retrying an ambiguous write.
- Use a dead-letter/review queue after the maximum attempt count.
- Emit correlation ID, endpoint family, module, sanitized record ID/hash, attempt, latency, Zoho code, and final disposition—never tokens or full PII payloads.

## 11. Notifications and webhooks

CRM Notification APIs manage watches at:

```http
POST   {api-domain}/crm/v8/actions/watch
PUT    {api-domain}/crm/v8/actions/watch
GET    {api-domain}/crm/v8/actions/watch
DELETE {api-domain}/crm/v8/actions/watch
```

Subscriptions identify module events such as create/edit/delete/all, a unique `channel_id`, a `notify_url`, and optionally a correlation `token` and field selection. Current documentation limits field selection to ten fields. `channel_expiry` is no more than one week; absent or excessive expiry defaults to a much shorter documented window (currently one hour). Renewal is therefore an operational requirement.

### Safe receiver design

1. Terminate TLS and reject unexpected methods/content types.
2. Treat the echoed token as correlation material, not as a complete cryptographic signature system.
3. Rate-limit and enqueue quickly; acknowledge only after durable acceptance.
4. Deduplicate by channel/event/record/version evidence.
5. Re-fetch the authoritative CRM record using a least-privileged server connection.
6. Detect out-of-order delivery and compare `Modified_Time` or a domain version.
7. Run scheduled reconciliation because subscription expiry, delivery failure, or downstream outages can create gaps.
8. Monitor renewal time, last notification, fetch failures, dead letters, and drift.

Never make an irreversible rent, lease, access, or deletion decision solely from an unauthenticated webhook body.

## 12. Automation surfaces

### Workflow rules

Use declarative workflows for clear event/time conditions and lightweight field updates, notifications, or function calls. Document:

- triggering operation and entry condition;
- whether repeat edits can re-enter;
- order/interaction with validation, approvals, blueprint, orchestration, and external writes;
- recursion guard;
- retry/failure owner;
- fields written and expected downstream events.

Avoid cycles such as CRM workflow → external update → CRM write → same workflow. Use source markers, version checks, and explicit terminal states.

### Blueprint

Blueprint represents an enforced record state machine. The v8 API exposes Blueprint discovery and transition execution for a record under the module record action path. Before an API transition:

1. fetch available transitions for the actual record and principal;
2. identify the transition by returned ID, not visible text alone;
3. validate mandatory fields/checklists/notes in that transition;
4. execute with optimistic concurrency/reconciliation;
5. record the transition ID, before/after state, actor, and result.

Do not bypass Blueprint by directly editing a state field unless the approved design explicitly allows it and tests prove invariant preservation.

### CRM Functions

CRM Functions are synchronous server-side Deluge programs. They can be associated with buttons, related lists, validation rules, workflow/automation, schedules, and REST-style endpoints. `crmAPIRequest` can expose parameters, body, file content, headers, user information, method, and auth type; `crmAPIResponse` can set status, content type, headers, and body.

Current documented limits include:

- 200,000 executed lines;
- 10 MB response;
- 10 seconds for button, related-list, validation, and REST executions;
- 30 seconds for automation executions;
- 15 minutes for schedules.

Function-credit documentation contains edition-dependent tables and a note whose wording may conflict with the table. Treat all credit quantities as `VOLATILE`; check live usage and the current page. Function analytics update on a delay (documented around five minutes) and retain logs for a limited window (currently 30 days). Export durable operational metrics without exposing sensitive inputs.

Functions are synchronous. For long or asynchronous work, use a queue or an approved asynchronous platform such as Catalyst, then reconcile completion back to CRM.

### Widgets

CRM widgets use the CRM JavaScript SDK/ZRC and embed a custom web UI in supported CRM locations. Good uses include guided maintenance triage, contextual property/unit panels, or a narrowly scoped reconciliation console. Security rules:

- never put client secrets in widget code;
- regard record IDs and widget input as attacker-controlled;
- perform authorization and sensitive writes server-side;
- use Content Security Policy and dependency pinning where the packaging model permits;
- log privileged actions and show explicit confirmation for destructive or financial effects.

### CRM Portals

CRM portal APIs expose portal configuration, user types, invitations/bulk invitations, and removal. A portal can allow external contacts/vendors/partners to view or modify authorized CRM records, notes, or attachments. Portal permissions and record-sharing behavior are `TENANT-SPECIFIC`.

`GH-POLICY` The current GH application map assigns the tenant experience to Creator/Sites. Do not create a parallel CRM tenant portal, invite users, or duplicate authorization rules without an approved architecture change.

### Sandbox and deployment

Use CRM Sandbox for configuration/function/workflow tests. Deployment from sandbox is a controlled action; it does not prove production data compatibility. Maintain a dependency inventory for layouts, fields, functions, workflows, connections, profiles, portals, and integrations. Deploy configuration and code in reviewed units, then smoke-test with sanitized/nonproduction records.

## 13. Deluge CRM v8 integration tasks

The following signatures are retrieval aids. Confirm the current task page and editor before production use because supported parameters and option behavior can change.

```deluge
zoho.crm.v8.createRecord(module, record_details, options_map, connection)
zoho.crm.v8.getRecords(module, query_value, page, per_page, connection)
zoho.crm.v8.searchRecords(module, criteria, page, per_page, search_value, connection)
zoho.crm.v8.getRecordById(module, record_id, query_value, connection)
zoho.crm.v8.updateRecord(module, record_id, record_values, options_map, connection)
zoho.crm.v8.bulkCreate(module, records_value, options_map, connection)
zoho.crm.v8.bulkUpdate(module, records_value, options_map, connection)
zoho.crm.v8.getRelatedRecords(relation_name, parent_module, record_id, query_value, page, per_page, connection)
zoho.crm.v8.updateRelatedRecord(sub_module, sub_id, parent_module, parent_id, values, connection)
zoho.crm.v8.convertLead(lead_id, values, connection)
zoho.crm.v8.upsert(module, values, duplicate_check, connection)
zoho.crm.v8.attachFile(module, record_id, file, connection)
zoho.crm.v8.getFields(module, connection)
```

Bulk create/update tasks currently accept no more than 100 records per call, and each bulk-update item needs its record ID. Search criteria are currently capped at ten conditions. A documented `not_equal` search does not include null values, so a separate null strategy may be needed.

### Defensive Deluge write pattern

```deluge
// Illustrative only: replace every identifier from live metadata/configuration.
module_api = config.get("module_api");
source_event_id = input.get("event_id");

if(module_api == null || source_event_id == null)
{
    return {"ok":false,"code":"CONFIG_OR_ID_MISSING"};
}

criteria = "(External_Event_ID:equals:" + source_event_id + ")";
existing = zoho.crm.v8.searchRecords(module_api, criteria, 1, 2, Map(), "crm_ops_read_v1");

if(existing.size() > 1)
{
    return {"ok":false,"code":"DUPLICATE_IDEMPOTENCY_KEY"};
}

payload = Map();
payload.put("External_Event_ID", source_event_id);
// Add only validated API-name fields.

no_triggers = List();
options = Map();
options.put("trigger", no_triggers); // Explicitly suppresses supported CRM automations here.
result = zoho.crm.v8.createRecord(module_api, payload, options, "crm_ops_write_v1");
return {"ok":true,"result":result};
```

The snippet deliberately omits business fields and is not copy-paste production code. Verify syntax in the target editor, use a unique field for the event ID, sanitize logs, and decide whether creation or upsert is correct.

## 14. GH/Sylvara automation blueprints

### A. Inquiry ingestion

**Source:** Zillow or another approved lead source.  
**Target:** CRM `Leads` only.  
**Keys:** source + source lead/event ID; secondary normalized email/phone for review, not silent merge.  
**Flow:** validate → dedupe/upsert by approved unique key → store consent/source/timestamps → assign through approved rule → emit audit result.  
**Guardrails:** do not create Contact, Deal/application, lease, portal user, Books transaction, or WorkDrive folder automatically unless a later approved workflow owns that transition.

### B. Lead conversion / application creation

Use the CRM conversion API or the approved workflow only after qualification. Fetch conversion requirements, layout/pipeline/owner rules, and existing Contact/Account candidates. Prevent duplicate person/property records. Application creation in `Deals` must set live required fields and approved pipeline/stage. Store the originating Lead ID and conversion result.

### C. Maintenance synchronization

CRM `Cases` is the operational system of record under the current map, while Creator may expose tenant intake/status.

- Assign a stable cross-system request ID.
- Define field-level ownership: e.g., tenant-submitted description/attachments, CRM triage/status/assignee, Creator projection.
- Synchronize permitted transitions, not every field blindly.
- Detect conflicts and out-of-order updates.
- Keep private staff notes separate from portal-visible text.
- Reconcile open requests and attachment references on a schedule.

### D. Lease/sign/accounting handoff

When an application is approved, send only the approved contract data snapshot to Contracts/Sign. Store the external envelope/contract ID and status in CRM. After signature, verify authoritative signed status before changing occupancy. Send accounting events to Books/Billing through a separate idempotent handoff. Never infer payment from a CRM stage.

### E. Property/unit model

Resolve current `Accounts`, custom Unit module, lookups, related lists, and uniqueness rules from metadata. Property display-label renaming does not change the `Accounts` API name. Unit automation must not ship until the custom module API name and property lookup API name are reverified.

## 15. Security, privacy, and observability

- Apply least-privileged OAuth scopes, CRM profiles, roles, sharing rules, field permissions, and portal permissions together.
- Treat field encryption metadata and sensitivity classifications as deployment gates.
- Avoid logging request/response bodies by default. Redact tokens, cookies, names, email, phone, addresses, application data, SSNs/tax IDs, bank/payment information, leases, and attachments.
- Use immutable correlation IDs and sanitized record identifiers for traceability.
- Maintain an allowlist of fields each integration may read/write; fail closed on unknown fields.
- Validate webhook and widget input server-side.
- Separate production, sandbox, and development credentials and endpoints.
- Monitor API-credit headroom, concurrency, function failures/timeouts, notification expiry, dead letters, duplicate keys, reconciliation lag, and metadata drift.
- Define retention/deletion policies across CRM, Creator, WorkDrive, Contracts/Sign, and Books; deletion in one system does not prove deletion elsewhere.

## 16. Testing and change-control checklist

`GH-POLICY` Follow requirement gate → sandbox/branch → sanitized fixtures → automated tests → metadata/config diff review → pull request → separate deployment → production smoke test → evidence → rollback readiness.

### Minimum tests

- OAuth expiration/refresh, revoked scope, wrong DC, and insufficient profile permission.
- Metadata drift: renamed label, changed API name for custom field/module, removed picklist, new required field, layout change.
- Create/update/upsert success, 207 partial success, validation failure, duplicate data, stale `If-Unmodified-Since`, record lock.
- Pagination boundaries (200, 2,000, token continuation), token expiry, and restart checkpoint.
- Search criteria encoding and null semantics; COQL escaping, joins, limits, and unsupported fields.
- Workflow/blueprint/approval trigger-on and trigger-off cases using the exact interface.
- Webhook duplicate, out-of-order, expired channel, endpoint outage, replay, and reconciliation repair.
- Function timeout, API-credit exhaustion, `429`, `5xx`, network timeout after server commit, bounded retry, dead-letter handling.
- Permission tests for staff roles and every external portal role.
- Rollback/reconciliation for every money, lease, access, PII, or delete pathway.

### Deployment evidence

Record release/commit, approved ticket/PR, metadata manifest version, sandbox tests, deployed components, connection IDs (not secrets), production smoke-test record IDs (sanitized), timestamps, owner, observed function/workflow logs, and rollback result/readiness.

## 17. Directive for ChatGPT/Codex

When asked to design or write Zoho CRM automation:

1. Identify the business owner and authoritative system for every field/state.
2. Load the current GH module/app/lifecycle maps.
3. Request or query live sanitized module, field, layout, related-list, pipeline, blueprint, and permission metadata.
4. State the exact execution context: REST, Deluge integration task, CRM function, workflow, Blueprint, widget, or portal.
5. Cite the current official endpoint/task page and verification date.
6. Generate code with configuration placeholders, explicit trigger intent, least-privileged connection, idempotency key, pagination, structured error handling, safe logging, and reconciliation.
7. Mark every unverified identifier `LIVE-METADATA REQUIRED`; never fill it by guesswork.
8. Provide sandbox tests, production smoke tests, monitoring, and rollback steps.
9. Never claim that a Git commit proves deployment, or that a successful API call proves downstream workflow/business completion.
10. For high-risk effects, pause at a review gate unless the approved runbook explicitly authorizes automatic execution.

## 18. Official source registry

All sources below are first-party Zoho documentation and were checked on 2026-07-20. Recheck `VOLATILE` pages before implementation.

### GH project context used

- `00_START_HERE.md` — authority order, metadata-first implementation, secret/PII rules, and deployment-evidence boundary.
- `01_GH_Tenant_Lifecycle_Map.md` — inquiry through occupancy, maintenance, renewal, and move-out system boundaries.
- `02_GH_Zoho_App_Map.md` — product-level record ownership and Creator/CRM/finance/document boundaries.
- `03_GH_CRM_Module_Map.md` — known and unresolved CRM module mappings, including the Zillow-to-Leads boundary.
- `04_GH_Systems_Change_Control_Standard.md` — sandbox, sanitized fixtures, review, smoke-test, evidence, and rollback requirements.
- `Deluge-Master-Handbook-2025.pdf` and `Deluge Coding.pdf` — comparative Deluge references; current official endpoint/task documentation and live metadata take precedence.

### CRM API v8 foundations

- [CRM API v8 home](https://www.zoho.com/crm/developer/docs/api/v8/)
- [Complete API reference inventory](https://www.zoho.com/crm/developer/docs/api/v8/api-references.html)
- [What's new in API v8](https://www.zoho.com/crm/developer/docs/api/v8/whats-new.html)
- [API v8 change log](https://www.zoho.com/crm/developer/docs/api/v8/change-log.html)
- [API collection / Postman](https://www.zoho.com/crm/developer/docs/api/v8/api-collection.html)
- [List available REST APIs](https://www.zoho.com/crm/developer/docs/api/v8/list-available-rest-apis.html)
- [API limits and concurrency](https://www.zoho.com/crm/developer/docs/api/v8/api-limits.html)
- [Status codes](https://www.zoho.com/crm/developer/docs/api/v8/status-codes.html)

### Authentication

- [OAuth overview](https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html)
- [Authorization request](https://www.zoho.com/crm/developer/docs/api/v8/auth-request.html)
- [Access and refresh tokens](https://www.zoho.com/crm/developer/docs/api/v8/access-refresh.html)
- [CRM OAuth scopes](https://www.zoho.com/crm/developer/docs/api/v8/scopes.html)
- [Client credentials](https://www.zoho.com/crm/developer/docs/api/v8/client-credentials.html)

### Metadata and records

- [Module metadata](https://www.zoho.com/crm/developer/docs/api/v8/module-meta.html)
- [Field metadata](https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html)
- [Layout metadata](https://www.zoho.com/crm/developer/docs/api/v8/layouts-meta.html)
- [Related-list metadata](https://www.zoho.com/crm/developer/docs/api/v8/related-list-meta.html)
- [Get records](https://www.zoho.com/crm/developer/docs/api/v8/get-records.html)
- [Insert records](https://www.zoho.com/crm/developer/docs/api/v8/insert-records.html)
- [Update records](https://www.zoho.com/crm/developer/docs/api/v8/update-records.html)
- [Upsert records](https://www.zoho.com/crm/developer/docs/api/v8/upsert-records.html)
- [Search records](https://www.zoho.com/crm/developer/docs/api/v8/search-records.html)
- [Get related records](https://www.zoho.com/crm/developer/docs/api/v8/get-related-records.html)

### Query, bulk, composite, and notifications

- [COQL overview](https://www.zoho.com/crm/developer/docs/api/v8/COQL-Overview.html)
- [Execute COQL](https://www.zoho.com/crm/developer/docs/api/v8/Get-Records-through-COQL-Query.html)
- [COQL joins](https://www.zoho.com/crm/developer/docs/api/v8/COQL-Joins.html)
- [COQL subqueries](https://www.zoho.com/crm/developer/docs/api/v8/COQL-subquery.html)
- [COQL limitations](https://www.zoho.com/crm/developer/docs/api/v8/COQL-Limitations.html)
- [Bulk Read overview](https://www.zoho.com/crm/developer/docs/api/v8/bulk-read/overview.html)
- [Bulk Write overview](https://www.zoho.com/crm/developer/docs/api/v8/bulk-write/overview.html)
- [Bulk Write limitations](https://www.zoho.com/crm/developer/docs/api/v8/bulk-write/limitations.html)
- [Composite API](https://www.zoho.com/crm/developer/docs/api/v8/composite-api.html)
- [Notification API overview](https://www.zoho.com/crm/developer/docs/api/v8/notifications/overview.html)
- [Enable notifications](https://www.zoho.com/crm/developer/docs/api/v8/notifications/enable.html)
- [Update notifications](https://www.zoho.com/crm/developer/docs/api/v8/notifications/update-details.html)
- [Get notification details](https://www.zoho.com/crm/developer/docs/api/v8/notifications/get-details.html)
- [External ID API overview](https://www.zoho.com/crm/developer/docs/api/v8/records-api-ext-id-overview.html)
- [Get records using External ID](https://www.zoho.com/crm/developer/docs/api/v8/get-records-ext.html)
- [Upsert records using External ID](https://www.zoho.com/crm/developer/docs/api/v8/upsert-records-ext.html)

### Functions, widgets, portals, and sandbox

- [CRM Functions overview](https://www.zoho.com/crm/developer/docs/functions/)
- [Set up functions](https://www.zoho.com/crm/developer/docs/functions/set-up-functions.html)
- [Function input types](https://www.zoho.com/crm/developer/docs/functions/input-type.html)
- [Function request and response](https://www.zoho.com/crm/developer/docs/functions/request-response.html)
- [Function authentication](https://www.zoho.com/crm/developer/docs/functions/auth-method.html)
- [Functions IDE](https://www.zoho.com/crm/developer/docs/functions/functions-ide.html)
- [Function limits](https://www.zoho.com/crm/developer/docs/functions/functions-limits.html)
- [Function analytics](https://www.zoho.com/crm/developer/docs/functions/function-analytics.html)
- [Call a function from a function](https://www.zoho.com/crm/developer/docs/functions/calling_func_within_func.html)
- [Functions FAQ](https://www.zoho.com/crm/developer/docs/functions/faqs-of-functions.html)
- [CRM Widgets](https://www.zoho.com/crm/developer/docs/widgets/)
- [Widget CLI](https://www.zoho.com/crm/developer/docs/widgets/install-cli.html)
- [Get CRM portals](https://www.zoho.com/crm/developer/docs/api/v8/get-portals.html)
- [Create a CRM portal](https://www.zoho.com/crm/developer/docs/api/v8/create-portal.html)
- [Get portal user types](https://www.zoho.com/crm/developer/docs/api/v8/get-user-types.html)
- [Invite portal user](https://www.zoho.com/crm/developer/docs/api/v8/invite-user.html)
- [Bulk invite portal users](https://www.zoho.com/crm/developer/docs/api/v8/portal-bulk-invite-users.html)
- [Remove portal user](https://www.zoho.com/crm/developer/docs/api/v8/delete-user-from-portal.html)
- [CRM Sandbox overview](https://help.zoho.com/portal/en/kb/crm/data-administration/sandbox/articles/sandbox-overview)
- [Deploy from CRM Sandbox](https://help.zoho.com/portal/en/kb/crm/data-administration/sandbox/articles/deploy-sandbox)
- [Creator integration in CRM Sandbox](https://help.zoho.com/portal/en/kb/crm/data-administration/sandbox/articles/zoho-creator-integration-in-crm-sandbox)

### Deluge CRM v8 tasks

- [CRM v8 integration tasks](https://www.zoho.com/deluge/help/crm-integration-tasks-V8.html)
- [Create record v8](https://www.zoho.com/deluge/help/crm/create-record-V8.html)
- [Get records v8](https://www.zoho.com/deluge/help/crm/get-records-V8.html)
- [Search records v8](https://www.zoho.com/deluge/help/crm/search-records-V8.html)
- [Update record v8](https://www.zoho.com/deluge/help/crm/update-record-V8.html)
- [Bulk update records v8](https://www.zoho.com/deluge/help/crm/bulk-update-records-V8.html)
- [Upsert record v8](https://www.zoho.com/deluge/help/crm/upsert-record-V8.html)

---

**End state:** This document explains the stable engineering model and the discovery process. The live CRM tenant remains authoritative for identifiers, permissions, layouts, picklists, enabled features, credits, and runtime behavior.
