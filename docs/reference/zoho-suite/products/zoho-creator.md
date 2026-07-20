# Zoho Creator Engineering, Portal, and Automation Knowledge Base

**Document ID:** GH-ZOHO-CREATOR-KB  
**Verification date:** 2026-07-20  
**Primary audience:** ChatGPT, Codex, solution architects, and maintainers building GH Real Estate and Sylvara systems  
**Evidence policy:** Official Zoho documentation plus the supplied GH application, lifecycle, CRM-module, and change-control maps. Live application metadata and the deployed tenant remain authoritative.

## 1. Retrieval contract for AI agents

### Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `DOC-VERIFIED` | Supported by a cited official Zoho page as of the verification date | Check the endpoint page when coding |
| `LIVE-METADATA REQUIRED` | App/form/report/field identifiers or configuration must come from the running tenant | Query metadata or use a current sanitized export |
| `TENANT-SPECIFIC` | Depends on app version, environment, plan, roles, portals, connections, data, or workflows | Never infer from generic examples |
| `VOLATILE` | Limits, editions, pricing, availability, or early-access behavior can change | Recheck immediately before design/deployment |
| `GH-POLICY` | Required by supplied GH architecture/change-control maps | Treat as a project constraint |
| `DESIGN RECOMMENDATION` | Engineering judgment rather than a platform guarantee | Validate with requirements and tests |

### Non-negotiable rules

1. Never guess the account owner name, app link name, form link name, report link name, field link name, page link name, record ID, environment, custom API link name, connection name, portal name, or portal permission set.
2. Display names are not API contracts. Creator APIs use link names; retrieve and version sanitized metadata.
3. Never expose OAuth tokens, refresh tokens, connection secrets, public keys, tenant PII, lease data, payment information, attachments, or production payloads in source, prompts, PDFs, fixtures, URLs, or logs.
4. Distinguish local Creator Deluge, cross-app Creator integration tasks, REST API v2.1, published APIs, custom APIs, page scripts, widgets, workflows, and batch workflows. Their authentication, trigger, transaction, and limit behavior differs.
5. Treat portal/browser code as untrusted. A hidden field, filtered report, page parameter, record ID, or widget check is not server-side authorization.
6. Repository state is not deployment proof. Environment publication, production smoke tests, evidence, and rollback/reconciliation are separate.
7. For tenant access, money, leases, notices, privacy, or deletion, require dry run, duplicate checks, authorization tests, manual verification, and rollback/reconciliation.

## 2. Creator's role in the GH/Sylvara architecture

`GH-POLICY` Creator is approved for tenant-facing applications and maintenance workflows. It is **not** a universal master database.

- CRM remains the operational system of record for leads, contacts/tenants, properties, units, leasing pipeline, and maintenance Cases under the current map.
- Books/Billing owns accounting transactions and payment state.
- Contracts/Sign owns contract/signature state and authoritative signed artifacts.
- WorkDrive owns governed document storage where designated.
- Creator can own portal-specific preferences, intake drafts, UI state, task orchestration, local workflow records, and carefully defined projections of authoritative data.

### Recommended ownership pattern

| Creator object | Allowed ownership | External authority to reference |
|---|---|---|
| Tenant portal profile projection | Presentation/cache fields, portal preferences | CRM Contact/tenant identity |
| Maintenance intake | Tenant submission, local upload state, portal-visible messages | CRM Case for operational assignment/status under current map |
| Guided move-in checklist | Completion evidence defined by the approved workflow | CRM occupancy state, Contracts/Sign lease state, WorkDrive documents |
| Payment display | Read-only projection/link | Books/Billing/payment provider |
| Lease display | Status/link and permitted copy | Contracts/Sign and governed document repository |
| Portal access mapping | Creator portal identity and local authorization mapping | CRM Contact/external identity IDs as approved |

Every synchronized field needs exactly one write authority, a stable external ID, a conflict rule, and a reconciliation owner.

## 3. Runtime model and component vocabulary

Zoho Creator applications are composed of forms, fields, reports, pages, workflows, functions, approvals, blueprints, schedules, batch workflows, portals, and microservices/connections.

| Component | What it is | API/design implication |
|---|---|---|
| Form | Schema and record-entry surface | Add Record targets a form link name |
| Field | Typed value or relationship inside a form | APIs use field link names; types determine payload shape |
| Report | Record view/query surface | Read/update/delete APIs target a report link name and inherit its access context |
| Page | Composed UI/dashboard | Can contain forms, reports, panels, charts, buttons, and widgets |
| Workflow | Event/time/action automation | API calls can trigger or selectively skip supported workflow categories |
| Function | Reusable Deluge logic | Can be called locally or exposed through a Custom API |
| Approval | Review state/action model | API workflow-skip controls do not bypass approvals in the same way as ordinary form workflows |
| Blueprint | Record state machine | Blueprint behavior cannot be skipped by the documented v2.1 workflow-skip mechanism |
| Batch workflow | Asynchronous sequential batch processing | Partial completion is possible; failed batches do not roll back prior successful batches |
| Portal | External-user surface | Permissions must include component, action, field, and row-level ownership controls |
| Widget | Custom HTML/JS UI | Client-side code is untrusted; sensitive actions require server checks |
| Connection | Managed authorization to Zoho/third-party service | Use least privilege and environment-specific ownership |
| Custom API | HTTP endpoint backed by an existing Deluge function | Separate limits/auth/user scope; design as a public server boundary |

### Creator versions, cloud/on-premise, and environments

Official help pages distinguish Creator 6 features from older experiences. Environment management documentation applies to the supported Creator 6 environment model. Creator API v2.1 documentation also covers Creator cloud and Creator On-Premise, but on-premise uses its own base URL and may not support every cloud feature.

`TENANT-SPECIFIC` Before design, record:

- Creator version and subscription plan;
- cloud data center or on-premise base URL;
- whether development/stage/production environments are enabled;
- enabled portal and user-license model;
- current API and custom-API entitlements;
- application owner and administrators;
- deployed app version and publication status.

Do not use an early-access feature, such as a newly introduced hotfix path, as a core release dependency without explicit acceptance and a fallback.

## 4. OAuth, data centers, scopes, and environment routing

### OAuth 2.0

`DOC-VERIFIED` Creator API v2.1 uses OAuth 2.0. Supported authorization header forms include:

```http
Authorization: Zoho-oauthtoken <access_token>
```

The OAuth page also documents bearer-token usage in applicable flows. Follow the exact endpoint's current example. Use the `api_domain` returned during token exchange and enable Multi-DC support for clients serving organizations in multiple Zoho regions.

Documented cloud API domains include:

| Data center | API domain pattern |
|---|---|
| United States | `www.zohoapis.com` |
| Europe | `www.zohoapis.eu` |
| India | `www.zohoapis.in` |
| Australia | `www.zohoapis.com.au` |
| Japan | `www.zohoapis.jp` |
| Canada | `www.zohoapis.ca` |
| Saudi Arabia | `www.zohoapis.sa` |
| China | `www.zohoapis.com.cn` |
| United Arab Emirates | `www.zohoapis.ae` |

Treat the list as `VOLATILE`; the token's `api_domain` and current OAuth page win.

### Scope map

| Scope | Purpose |
|---|---|
| `ZohoCreator.form.CREATE` | Add form records |
| `ZohoCreator.report.READ` | Read report records and download files |
| `ZohoCreator.report.CREATE` | Upload files to records displayed in reports |
| `ZohoCreator.report.UPDATE` | Update report records |
| `ZohoCreator.report.DELETE` | Delete report records |
| `ZohoCreator.meta.form.READ` | Read form/field metadata |
| `ZohoCreator.meta.application.READ` | Read application/component metadata |
| `ZohoCreator.dashboard.READ` | Read supported dashboard/page information |
| `ZohoCreator.bulk.CREATE` / `.READ` / `.UPDATE` | Bulk job operations as documented by the endpoint |
| `Zohocreator.customapi.EXECUTE` | Execute Creator Custom APIs |

Scope spelling and capitalization are part of the contract; use the exact endpoint page. OAuth scope does not override Creator app/report/portal permissions.

### Environment header

For v2.1 endpoints that support Creator environments, send:

```http
environment: development
```

or:

```http
environment: stage
```

If the header is absent, current endpoint documentation defaults to production. Therefore an omitted header is dangerous during testing. Wrap the base URL, account owner, app link name, and environment header in explicit environment configuration; refuse to run destructive test commands when the environment is blank.

### Connection manifest

Record connection name, owner, scopes, data center, target environment, rotation owner, authorized Creator apps, and dependent functions. Separate portal-read, operational-write, metadata, bulk, and third-party connections where possible.

## 5. API v2.1 topology

The base route is:

```text
https://<base_url>/creator/v2.1/
```

The official API home divides the service into data, publish, file, metadata, bulk, and custom API surfaces.

| Family | Main purpose | Critical boundary |
|---|---|---|
| Data APIs | Add/get/update/delete Creator records | Use app/form/report/field link names and authenticated access |
| Publish APIs | Access records through published components | Production-only published surface; intentionally broader exposure risk |
| File APIs | Upload/download file, image, audio, video, signature fields | One uploaded/downloaded file per call in documented cases; validate type/size/access |
| Metadata APIs | Discover apps, forms, fields, reports, pages, sections | Required before code generation; responses are tenant/environment-specific |
| Bulk Read | Asynchronous export | Cursor/job/download lifecycle and separate rate limits |
| Bulk Insert | Asynchronous CSV import | Workflows do not run; partial/aborted outcomes require reconciliation |
| Custom APIs | User-defined HTTP operation backed by Deluge | Separate auth/user scope/limits and a security boundary |

## 6. Live metadata discovery

### Metadata endpoints

Representative v2.1 routes include:

```http
GET https://<base_url>/creator/v2.1/meta/<account_owner_name>/<app_link_name>/form/<form_link_name>/fields
```

The metadata family also lists applications, applications by workspace, forms, reports, pages, and sections. Use the official OpenAPI specifications exposed on the endpoint pages to generate typed clients and contract tests.

### Required sanitized manifest

```yaml
verified_at: 2026-07-20T00:00:00Z
creator_version: "<live value>"
environment: development
account_owner_name: "<sanitized/live link identifier>"
app:
  display_name: "<sanitized>"
  link_name: "<live value>"
forms:
  - display_name: "<sanitized>"
    link_name: "<live value>"
    fields:
      - display_name: "<sanitized>"
        link_name: "<live value>"
        type: "<live metadata type>"
        required: false
        sensitive: false
        lookup_target: null
reports:
  - display_name: "<sanitized>"
    link_name: "<live value>"
    form_link_name: "<live value>"
pages:
  - display_name: "<sanitized>"
    link_name: "<live value>"
portal:
  roles: []
  permission_sets: []
```

Exclude actual record data, email addresses, tenant names, addresses, documents, and secrets. Diff the manifest before every automation/schema release.

## 7. Data APIs

### Add Records

```http
POST https://<base_url>/creator/v2.1/data/<owner>/<app>/form/<form>
```

Current v2.1 supports up to 200 records per Add Records request. Use field link names in the `data` payload. Form validations still apply. Directly setting file/image/audio/video/signature values is not equivalent to file upload; create/update the record and use the file API for supported fields.

Inspect both the overall response and every record result. Partial record failures must not be collapsed into a single success boolean.

### Get Records

```http
GET https://<base_url>/creator/v2.1/data/<owner>/<app>/report/<report>
```

Current v2.1 behavior:

- default `max_records` is 200;
- supported `max_records` values include 200, 500, and 1,000;
- the response can return a `record_cursor` header; pass it in the next request header for the next consecutive batch;
- `field_config` can select quick view, detail view, custom, or all fields; `fields` selects field link names for custom mode;
- criteria support depends on the report; criteria are not supported on reports based on integration forms in documented cases.

Persist cursor and processed-ID checkpoints only after durable downstream commit. A cursor is not a permanent replication log; implement periodic full/incremental reconciliation.

### Get Record by ID

```http
GET https://<base_url>/creator/v2.1/data/<owner>/<app>/report/<report>/<record_id>
```

Use this route when the record ID is authoritative and when a detail-shaped response is required. Still enforce report/app permissions and portal ownership; possession of the numeric record ID is not authorization.

### Update Records by criteria

```http
PATCH https://<base_url>/creator/v2.1/data/<owner>/<app>/report/<report>
```

Criteria is mandatory. Current processing is limited to 200 matching records per request; documented `process_until_limit=true` controls processing of the first allowed batch. Loop only with a termination condition, immutable selection key, checkpoint, and post-count verification. A broad update is high risk.

### Update Record by ID

```http
PATCH https://<base_url>/creator/v2.1/data/<owner>/<app>/report/<report>/<record_id>
```

Prefer ID updates after an authorized read when changing a single record. Re-read before update for high-value state and verify after update because a workflow/blueprint may change additional fields.

### Delete Records

```http
DELETE https://<base_url>/creator/v2.1/data/<owner>/<app>/report/<report>
DELETE https://<base_url>/creator/v2.1/data/<owner>/<app>/report/<report>/<record_id>
```

Criteria-based delete is limited to the documented processing batch (currently 200) and requires criteria. Deletes are destructive and validations/workflows may apply. Export the target IDs and relevant audit fields, validate count, obtain approval, delete in bounded batches, verify, and preserve recovery evidence. Never use a blank/generated criteria expression.

## 8. Criteria and field-value handling

Creator criteria use **field link names**, not display labels. Current documented rules include:

- combine expressions with `&&` (AND), `||` (OR), and—where documented—`!` (NOT), with parentheses for precedence;
- quote string values with escaped double quotes;
- quote date, time, and datetime values with single quotes in the application's configured format;
- compare a lookup or integration field using its record ID when required;
- multi-select, checkbox, and multi-select lookup expressions accept one comparison value per expression in documented APIs.

Illustrative criteria:

```text
Status=="Open" && External_Request_ID=="gh-evt-123"
```

Never concatenate untrusted portal input directly into criteria. Validate against an allowlist, escape based on field type, and prefer record IDs already authorized by a server-side ownership query.

### Field-type handling matrix

The Fields metadata API is authoritative. Creator field categories include text/name/address, email/phone/URL, numeric/currency/percentage, date/time/datetime, choice fields, lookups/multi-select lookups, subforms, users, formula/aggregate, file/image/audio/video/signature, integration fields, and specialized/AI-backed types.

| Type family | Safe handling |
|---|---|
| Text/contact | Normalize only for comparison; preserve original; classify PII |
| Number/currency | Send numeric JSON values; never localized currency strings |
| Date/time | Use app-defined formats for criteria and documented API format for payloads; preserve timezone explicitly |
| Choice | Use live choice value, not translated/display text; handle retired values |
| Lookup/integration | Use the required record ID/link representation from the endpoint and metadata |
| Subform | Treat as child records with their own IDs and permissions; test add/update/delete semantics |
| Multi-value | Parse v2.1 array/key-value response shapes; do not assume v2's space-delimited strings |
| Formula/aggregate | Usually system-derived; do not attempt to write unless endpoint/type permits it |
| File/media/signature | Use the File API and storage/permission controls; never log contents or public paths |
| Sensitive fields | Restrict metadata/output/logging; apply portal field permissions and encryption policy |

## 9. Workflow trigger control

API v2.1 introduced `skip_workflow` for selected data/file operations. Documented values include:

| Value | Meaning on supported endpoints |
|---|---|
| `form_workflow` | Skip associated form workflows |
| `schedules` | Skip associated schedule workflows where supported |
| `all` | Skip both supported form and schedule workflows |

By default, associated workflows run on v2.1 operations where documented. Administrators/developers can use skip controls subject to endpoint and permission rules. `DOC-VERIFIED` Blueprint and approval behavior is not bypassed by this mechanism in the same way; Blueprints/approvals cannot simply be skipped through the documented option.

**Rule:** Every write design must say whether form workflows and schedules should execute, and must test the exact API action. Never copy a `skip_workflow` setting merely to avoid duplicate effects; fix ownership/idempotency.

## 10. File APIs

Upload targets a particular record and field link name:

```http
POST https://<base_url>/creator/v2.1/data/<owner>/<app>/report/<report>/<record_id>/<field_link_name>/upload
```

Download targets the same record/field with the documented download route. Current behavior includes:

- file APIs support file upload, image, audio, video, or signature fields as documented;
- validation and account storage limits apply;
- multiple-upload fields require one upload call per file;
- one download call returns one file; for multi-file fields, obtain the exact `filepath` from Get Records/Get Record by ID and pass it to download;
- subform file download uses an additional subform link/record ID route.

Security controls:

- permit only approved MIME types/extensions and verify content server-side;
- limit size and scan for malware before trusted downstream use;
- generate storage-safe names; never trust the client filename;
- authorize portal user, parent record, subform record, and field before upload/download;
- store hashes and external document IDs for reconciliation;
- never expose a raw Creator file route as a permanent public document URL.

## 11. Published APIs

Publish APIs operate on published components and current documentation identifies production as the relevant published surface. A published form/report is an intentional exposure boundary, not an authenticated Data API shortcut.

- Publish only the narrowest component required.
- Do not publish internal reports, tenant-wide data, staff notes, accounting data, identity documents, or leases.
- Use unguessable public links only as defense-in-depth, not as identity proof.
- Apply anti-abuse controls, validation, rate limiting, bot protection where available, and post-submission review.
- Prefer authenticated Creator portals or an OAuth Custom API for tenant-specific data.

## 12. Bulk APIs

### Bulk Read

Bulk Read is asynchronous:

```http
POST https://<base_url>/creator/v2.1/bulk/<owner>/<app>/report/<report>/read
GET  https://<base_url>/creator/v2.1/bulk/<owner>/<app>/report/<report>/read/<job_id>
GET  https://<base_url>/creator/v2.1/bulk/<owner>/<app>/report/<report>/read/<job_id>/result
```

The job request can include selected fields, criteria, maximum records, and a record cursor. Status returns count, download URL, and possibly the next cursor. The current documentation says the download URL/cursor is short lived (documented at about 15 minutes), so download promptly to controlled storage.

Current Bulk Read limits are `VOLATILE`:

- create job: 5 per user per minute and 15 per organization per minute;
- download: 10 per user per minute and 30 per organization per minute;
- continuation requests after the first job are constrained to the returned cursor semantics.

### Bulk Insert

The documented lifecycle is create job → upload CSV/ZIP → start → poll → download results, with abort support.

Current limitations include:

- only administrators/developers can run it;
- one active job per form;
- CSV, or a ZIP containing one CSV, with current maximum 100 MB;
- no replace mode;
- start within three hours of creation;
- source and result retention are limited (currently around three days);
- processing uses batches of 200;
- more than 5% failed batches can cause system abort;
- form workflows are not executed;
- formula/barcode updates can be asynchronous;
- Creator On-Premise is not supported by this bulk-insert surface.

Bulk insert is therefore for controlled migration, not business-event processing. Reconcile input row count, accepted/rejected count, created IDs, formula completion, and downstream records. If workflows normally establish invariants, reproduce them in a separately reviewed migration step.

## 13. API limits and capacity

`VOLATILE` Current official API-limit documentation separates Developer API and Custom API limits and resets daily at midnight in the super admin's account timezone.

| Plan (current page) | Developer API | Custom API |
|---|---:|---:|
| Free | 250/day | 100/day |
| Standard | 250/user/day | 100/user/day |
| Professional | 500/user/day | 250/user/day |
| Enterprise | 1,000/user/day | 500/user/day |
| Zoho One | 1,000/user/day | 500/user/day |

The general “Things to know” page currently states 50 requests per minute per API endpoint per public IP and a general maximum of 200 records processed per request. Individual endpoints can override the general record count; Get Records v2.1, for example, documents up to 1,000 returned records.

Creator Deluge integration tasks consume Developer API calls. `invokeurl` calls to Creator Developer APIs consume Developer API limits and external-call capacity; calls to Custom APIs consume Custom API limits and external-call capacity. Capacity plans must count internal automation as well as external clients.

## 14. Custom APIs

Creator Custom APIs expose an **existing Deluge function** as a generated endpoint. Current Creator 6 documentation says Custom APIs can use GET, POST, PUT, or DELETE; only super admins/admins create/manage them, while invocation is governed by configured user scope. Existing Java or Node.js cloud functions cannot currently be exposed directly through this Custom API builder.

Typical endpoint shape:

```text
https://www.zohoapis.com/creator/custom/<account_name>/<custom_api_link_name>
```

Use the exact generated endpoint. Supported authentication includes OAuth 2.0 and a Public Key option. A public key can be used by anyone with the key and URL; treat it as an exposed bearer secret and avoid it for tenant-sensitive operations. OAuth scope is `Zohocreator.customapi.EXECUTE`.

Custom API scopes can be configured for administrators, selected users, portal users, or broader allowed groups. Portal invocation has context restrictions; confirm the exact widget/portal behavior in the current tenant.

`DOC-VERIFIED` With the current `Portal users` user scope, the Custom API can be invoked only from within a widget. The builder supports JSON and multipart/form-data for POST/PUT requests; multipart cannot represent nested data the way JSON can. Choose one explicit request schema and reject unexpected content types.

### Custom API design contract

- Version the link name/path or request schema; do not silently repurpose fields.
- Validate method, content type, body size, types, enums, IDs, and actor permissions.
- Authenticate before resolving record IDs; then enforce row-level ownership.
- Require an idempotency/event key for writes.
- Return stable application codes and an HTTP status consistent with the outcome.
- Redact logs; current Custom API logs show the last 30 days by default and no more than the previous 60 days, so export metrics—not sensitive payloads—to the approved observability system.
- Rate-limit and queue long work; respond with a job/correlation ID when a synchronous function cannot safely complete.
- Maintain a kill switch and reconciliation job.

Custom API counts are separate from standard REST counts. Disabled APIs can produce log behavior that is not equivalent to a successful business response; callers must validate the response contract.

## 15. Deluge in Creator

### Local application DSL

Local Creator Deluge can use form-native statements such as:

```deluge
new_id = insert into Maintenance_Intake
[
    External_Request_ID = input.External_Request_ID
    Status = "Received"
];
```

`LIVE-METADATA REQUIRED` The form/field names above are illustrative. The documented local `insert into` action does not invoke the target form's On Validate or On Success scripts. If those scripts enforce invariants, move reusable validation/business logic into a function and call it explicitly, or route creation through the approved interface with tested workflow behavior.

### Cross-app Creator integration tasks

Common documented signatures include:

```deluge
zoho.creator.createRecord(owner, app_link, form_link, data_map, other_params, connection)
zoho.creator.getRecords(owner, app_link, report_link, criteria, from_index, record_limit, connection)
zoho.creator.getRecordById(owner, app_link, report_link, record_id, connection)
zoho.creator.updateRecord(owner, app_link, report_link, record_id, field_map, other_params, connection)
```

Confirm delete and file-operation signatures on their current task pages/editor. Cross-app tasks wrap Creator APIs, consume Developer API limits, and rely on the named connection. They are not equivalent to local form DSL.

### Defensive local function shape

```deluge
map api_upsert_maintenance(map request_ctx)
{
    response = Map();
    event_id = request_ctx.get("event_id");
    portal_user = zoho.loginuser;

    if(event_id == null || event_id.trim() == "")
    {
        response.put("ok", false);
        response.put("code", "EVENT_ID_REQUIRED");
        return response;
    }

    // Authorize portal_user against a server-side tenant/property mapping.
    // Query by a field link name verified from current metadata.
    // Reject >1 matches; create/update exactly once; do not log request_ctx.

    response.put("ok", true);
    response.put("code", "ACCEPTED");
    return response;
}
```

This is a structural template, not deployable code. Validate compiler syntax in the target Creator version and implement the omitted authorization/idempotency logic from live metadata.

## 16. Workflows, transactions, and batch workflows

Creator workflow families include form workflows, report actions, schedules, payment workflows, approvals, Blueprints, batch workflows, and reusable functions.

### Performance and transaction boundaries

Current performance guidance includes:

- design lookups instead of duplicating data;
- avoid expensive broad `contains` queries where an indexed/exact identifier is available;
- prefer bulk operations for bounded sets;
- a record lock can remain for up to roughly 30 seconds;
- a regular workflow transaction can run up to roughly five minutes;
- a batch transaction has a shorter boundary, roughly one minute;
- external API reads have a documented timeout around 40 seconds;
- update records in a consistent order to reduce deadlock risk.

Treat all limits as `VOLATILE`. Long-running external work should be queued, not held inside a portal request or record lock.

### Workflow action limits

Current workflow-limit documentation includes approximately:

- 120 action calls per minute per public IP;
- 250 calls per minute per application;
- 250 calls per minute per portal;
- Deluge statement allowances that vary by plan, roughly 5,000–50,000;
- special small limits for Blueprint transition scripts/actions.

Check live plan/usage before capacity design.

### Batch workflows

Batch workflows process selected records sequentially in batches. Supported batch-size choices currently include 10, 50, 100, 200, 500, and 1,000. Documentation describes up to 100 batch workflows and only one concurrent batch workflow per account, subject to plan/edition.

Important failure semantics:

- only the failed batch is rolled back;
- previously successful batches remain committed;
- execution continues after isolated failures;
- 15 consecutive failed batches terminate the workflow;
- each batch has its own short execution limit (currently about one minute);
- logs retain only a limited subset/details of failures.

Therefore every batch script must be idempotent, checkpointable, count-reconciled, and safe to resume. Never call partial completion “rolled back.”

## 17. Blueprint and approvals

Creator Blueprint models record states as stages and transitions. Use it when a process requires explicit allowed transitions, required fields, validation, and transition actions—for example maintenance triage or move-in readiness.

Design rules:

- store stable machine state separately from user-facing status text when needed;
- define who can execute each transition;
- keep transition functions short and idempotent;
- do not directly update the state field to bypass a transition;
- test parallel/common transition behavior, failure, rollback, and re-entry;
- synchronize an external state only through an explicit mapping table and reconciliation process.

Approvals are a distinct review mechanism. API workflow-skip controls do not grant permission to bypass an approval. Record the approver, decision, timestamp, before/after values, and downstream event ID without exposing confidential comments.

## 18. Pages, widgets, and client-side security

Creator Pages compose panels, charts, gauges, forms, reports, buttons, embedded content, and widgets. Page scripts and variables can create dynamic experiences, but any value received from a URL, page parameter, browser widget, or embedded component is untrusted.

Widgets can be hosted internally or externally and use JavaScript to extend the app. They are appropriate for a focused tenant experience or operational console when native components are insufficient.

Security contract:

1. Authenticate the user through Creator portal/session or an approved identity provider.
2. Resolve an internal portal-user-to-CRM-Contact/Tenant mapping server-side.
3. Authorize the requested property/unit/maintenance record on every read and write.
4. Return only allowlisted fields; separate staff-private and portal-visible notes.
5. Never embed secrets, OAuth refresh tokens, unrestricted public keys, or privileged connection material in JavaScript.
6. Apply output encoding, CSRF defenses appropriate to the platform, content restrictions, and dependency review.
7. Require confirmation and server-side revalidation for destructive/high-risk actions.

Functional URL patterns are useful for navigation, but a URL that contains a record ID or filter is not an access-control rule.

## 19. Portals and record authorization

Creator portals provide authenticated external-user access and configurable permissions. Current portal permission documentation covers component access, record actions, field-level visibility, and treatment of PII/ePHI fields.

### Required layered model

| Layer | Control |
|---|---|
| Identity | Verified portal user/session and lifecycle (invite, activate, disable) |
| Role/permission set | Access to app components and permitted actions |
| Field permission | Hide staff-only, financial, identity, security, and unrelated tenant fields |
| Row ownership | Server query proves the user belongs to the tenant/property/unit/request |
| Transition authorization | User can perform this action in the current state |
| Audit | Actor, correlation ID, target, action, timestamp, outcome |

Never rely only on “users can view their own records” without testing the exact form/report/lookup relationships for every portal role. Test horizontal access by changing record IDs and vertical access by attempting staff-only actions.

Provision/deprovision portal users idempotently and reconcile against authoritative tenancy/lease status. A lease ending does not automatically prove that every portal access path has been removed.

## 20. Microservices and connections

Creator Microservices includes connections and other integration/model services. Use Connections for OAuth/API credentials, not literal headers in Deluge. Custom connectors may be available in Creator 6 depending on the feature/plan.

Connection governance:

- one declared purpose and least-privileged scope;
- separate development/stage/production authorization;
- named owner and rotation/revocation process;
- dependency inventory for every function/workflow/custom API;
- data-residency review for cross-data-center integrations;
- no tenant PII in connection names or diagnostic messages.

Use `invokeurl` only when a native integration task cannot meet the requirement or when exact HTTP control is necessary. Define connect/read timeout behavior, parse status/body defensively, cap retries, and reconcile ambiguous writes.

## 21. GH/Sylvara implementation patterns

### A. Tenant portal bootstrap

1. Confirm signed/approved tenancy state from authoritative systems.
2. Resolve/create the Creator portal identity idempotently.
3. Store a stable mapping to CRM Contact and approved tenancy/unit IDs.
4. Assign the narrow portal permission set.
5. Validate access with positive and cross-tenant negative tests.
6. Send onboarding through the approved communication system.
7. Reconcile enabled users against active tenancy daily.

Do not make portal provisioning a side effect of a Zillow Lead or unapproved application.

### B. Maintenance intake and CRM Case synchronization

Suggested boundary:

- Creator owns portal submission draft, tenant-visible messages, upload staging, and presentation state.
- CRM `Cases` owns operational case status, triage, assignee, and internal notes under the current GH map.
- WorkDrive or another approved repository owns durable governed documents if designated.

Use a stable `External_Request_ID` unique in both systems. On submit: authorize tenant/unit → validate category/urgency/consent → persist intake once → create/upsert CRM Case once → store CRM Case ID → move to synchronized state. If CRM is unavailable, show “received/pending synchronization,” not “work order created.” A scheduled reconciler repairs missing/mismatched cases.

### C. Tenant-visible payment and lease state

Expose a minimal read-only projection and deep link to the authoritative product. Never calculate balance due from unsynchronized Creator rows or infer a signed lease from a portal checkbox. Include source system, source ID, source timestamp, last synchronized time, and stale-data indicator.

### D. Inspection/checklist workflow

Use a Creator form/subform model only after deciding whether CRM custom modules or another system owns the inspection record. Capture immutable submission/version evidence, media hashes, actor/timestamp, and later amendments separately. Do not silently overwrite signed or compliance evidence.

## 22. Idempotency, synchronization, and reconciliation

Creator Data APIs do not provide a universal idempotency guarantee for create operations.

- Define an immutable external event ID in a unique/logically unique field.
- Before create, query the authorized report by the key; zero → create, one → return existing/update allowed fields, more than one → quarantine.
- Record source system, event ID, payload hash, Creator record ID, external record ID, attempt count, status, and timestamps in an integration ledger.
- Use a state machine (`received`, `validated`, `creator_committed`, `external_committed`, `reconciled`, `failed_review`) instead of one boolean.
- When a timeout occurs after a write, re-query by idempotency key before retrying.
- Run scheduled reconciliation by modified timestamp plus full periodic comparison; compare counts and field-level hashes for allowlisted fields.
- Never use mutable email/phone/address as the sole key for a tenant or request.

For bidirectional synchronization, create an explicit field-ownership matrix. Reject or queue writes to fields owned by the other system instead of “last write wins.”

## 23. Error handling and observability

Creator returns HTTP status plus API response codes/messages. Use the official v2.1 status-code registry.

- Classify authentication/authorization, validation, not-found, limit, lock/conflict, transient service, and unknown failures.
- Retry only transient failures with bounded exponential backoff/jitter.
- Honor daily and per-minute limits; delay work rather than tight-looping.
- Do not retry invalid criteria, unknown link names, permissions, or validation failures without correction.
- For partial/bulk/batch outcomes, record each row/batch status and reconcile totals.
- Log correlation ID, app/form/report alias (sanitized), environment, operation, record hash/ID, actor class, latency, response code, attempt, and disposition.
- Never log access/refresh tokens, cookies, public keys, full request bodies, attachments, PII, lease/payment data, or portal session data.

Monitor daily API consumption, custom API consumption, per-minute throttling, workflow failures, batch termination, queue depth, reconciliation lag, portal-auth failures, metadata drift, stale connections, and production/development routing mistakes.

## 24. Testing and change control

`GH-POLICY` Use requirement gate → development environment/branch → sanitized fixtures → automated tests → app/schema/config diff → reviewed pull request/evidence → publish/deploy separately → production smoke test → evidence → rollback/reconciliation.

### Minimum test suite

- Wrong DC, expired/revoked OAuth, insufficient scope, app/report/field permission failure.
- Missing/incorrect environment header and proof that tests cannot default silently to production.
- Changed form/report/field link names, new required field, choice change, lookup/subform shape change.
- Add 1 and 200 records, partial validation, workflow run/skip modes, Blueprint/approval behavior.
- Cursor sequences at 200/500/1,000, cursor loss/restart, duplicate processing, integration-report criteria limitation.
- Criteria escaping/injection, date/timezone, lookup ID, multi-value fields, empty/null distinctions.
- Update-by-criteria upper bound and termination; delete dry run/count/approval/recovery.
- Upload forbidden type, oversize, multiple files, malicious filename, cross-tenant download, subform file path.
- Custom API auth modes, user scopes, body limits, invalid method, duplicate idempotency key, timeout-after-commit.
- Portal horizontal/vertical authorization across every role; terminated tenant deprovisioning.
- Workflow recursion, record lock, external timeout, API limit, dead letter, reconciliation repair.
- Batch partial success and 15-consecutive-failure termination; resume without duplicating effects.

### Release evidence

Capture approved requirement/ticket, commit/PR, sanitized metadata manifest, exported app/version evidence, environment, test results, publication/deployment timestamp, connection IDs (never secrets), smoke-test IDs (sanitized), observed workflow/function logs, API usage, and rollback/reconciliation result.

## 25. Directive for ChatGPT/Codex

When asked to build with Zoho Creator:

1. Identify authoritative systems and field-level ownership before designing forms.
2. Load the current GH application/lifecycle/module maps.
3. Require current sanitized app/form/report/field/page/portal metadata and environment/version/plan.
4. State the exact surface: local Deluge, Creator integration task, REST v2.1, Publish API, File API, Bulk API, Custom API, workflow, Blueprint, batch workflow, page, widget, or portal.
5. Cite the current official endpoint/help page and verification date.
6. Generate link-name placeholders only from metadata, use explicit environment routing, least-privileged connection, idempotency, pagination/cursor handling, structured errors, safe logs, and reconciliation.
7. Include portal row-level authorization and cross-tenant negative tests for every external surface.
8. State workflow/Blueprint/approval trigger intent explicitly.
9. Include limits/capacity assumptions as `VOLATILE` and provide a live verification step.
10. Provide development/stage tests, publication/deployment instructions, production smoke tests, monitoring, and rollback/reconciliation.
11. Never claim that hidden UI, record ID, report filter, public key, or URL secrecy is authorization.
12. Never claim repository code is deployed or a successful API response proves downstream business completion.

## 26. Official source registry

All sources below are first-party Zoho documentation checked on 2026-07-20.

### GH project context used

- `00_START_HERE.md` — authority order, metadata-first implementation, secret/PII rules, and deployment-evidence boundary.
- `01_GH_Tenant_Lifecycle_Map.md` — tenant lifecycle and system handoffs.
- `02_GH_Zoho_App_Map.md` — Creator's approved tenant-portal/maintenance role and product ownership boundaries.
- `03_GH_CRM_Module_Map.md` — CRM objects that Creator must reference rather than silently duplicate.
- `04_GH_Systems_Change_Control_Standard.md` — development/sandbox, sanitized fixtures, review, production smoke-test, evidence, and rollback requirements.
- `Deluge-Master-Handbook-2025.pdf` and `Deluge Coding.pdf` — comparative Deluge references; current official help/API pages and the live application take precedence.

### API foundations, auth, limits, and metadata

- [Creator API v2.1 home](https://www.zoho.com/creator/help/api/v2.1/)
- [What's new in API v2.1](https://www.zoho.com/creator/help/api/v2.1/what-is-new-in-v2.1.html)
- [OAuth authentication and scopes](https://www.zoho.com/creator/help/api/v2.1/oauth-overview.html)
- [Things to know](https://www.zoho.com/creator/help/api/v2.1/things-to-know.html)
- [API limits](https://www.zoho.com/creator/help/api/v2.1/api-limits.html)
- [API v2.1 status codes](https://www.zoho.com/creator/help/api/v2.1/status-codes.html)
- [OpenAPI specification registry](https://www.zoho.com/creator/help/api/v2.1/openapi-specification.html)
- [Get applications](https://www.zoho.com/creator/help/api/v2.1/get-applications.html)
- [Get workspace applications](https://www.zoho.com/creator/help/api/v2.1/get-workspace-applications.html)
- [Get forms](https://www.zoho.com/creator/help/api/v2.1/get-forms.html)
- [Get fields](https://www.zoho.com/creator/help/api/v2.1/get-fields.html)
- [Get reports](https://www.zoho.com/creator/help/api/v2.1/get-reports.html)
- [Get pages](https://www.zoho.com/creator/help/api/v2.1/get-pages.html)
- [Get sections](https://www.zoho.com/creator/help/api/v2.1/get-sections.html)

### Data and file APIs

- [Add Records](https://www.zoho.com/creator/help/api/v2.1/add-records.html)
- [Get Records](https://www.zoho.com/creator/help/api/v2.1/get-records.html)
- [Get Record by ID](https://www.zoho.com/creator/help/api/v2.1/get-records-by-ID.html)
- [Update Records](https://www.zoho.com/creator/help/api/v2.1/update-records.html)
- [Update Record by ID](https://www.zoho.com/creator/help/api/v2.1/update-specific-record.html)
- [Delete Records](https://www.zoho.com/creator/help/api/v2.1/delete-records.html)
- [Delete Record by ID](https://www.zoho.com/creator/help/api/v2.1/delete-specific-record.html)
- [Upload File](https://www.zoho.com/creator/help/api/v2.1/upload-file.html)
- [Download File](https://www.zoho.com/creator/help/api/v2.1/download-file.html)
- [Download File from a subform](https://www.zoho.com/creator/help/api/v2.1/download-file-from-subform.html)
- [Publish API: Add Records](https://www.zoho.com/creator/help/api/v2.1/publish-api/add-records.html)
- [Publish API: Get Record by ID](https://www.zoho.com/creator/help/api/v2.1/publish-api/get-record-by-id.html)

### Bulk APIs

- [Bulk API overview](https://www.zoho.com/creator/help/api/v2.1/bulk-api/overview.html)
- [Create Bulk Read job](https://www.zoho.com/creator/help/api/v2.1/bulk-api/create-bulk-read-job.html)
- [Get Bulk Read status](https://www.zoho.com/creator/help/api/v2.1/bulk-api/get-the-status-of-the-bulk-read-job.html)
- [Download Bulk Read result](https://www.zoho.com/creator/help/api/v2.1/bulk-api/download-bulk-read-result.html)
- [Bulk Read limitations](https://www.zoho.com/creator/help/api/v2.1/bulk-api/limitations.html)
- [Bulk Insert overview](https://www.zoho.com/creator/help/api/v2.1/bulk-insert-api/overview.html)
- [Create Bulk Insert job](https://www.zoho.com/creator/help/api/v2.1/bulk-insert-api/create-bulk-insert-job.html)
- [Upload Bulk Insert data](https://www.zoho.com/creator/help/api/v2.1/bulk-insert-api/upload-bulk-insert-job.html)
- [Start or abort Bulk Insert](https://www.zoho.com/creator/help/api/v2.1/bulk-insert-api/start-abort-job-status.html)
- [Get Bulk Insert status](https://www.zoho.com/creator/help/api/v2.1/bulk-insert-api/get-job-status.html)
- [Download Bulk Insert result](https://www.zoho.com/creator/help/api/v2.1/bulk-insert-api/download-bulk-insert-result.html)
- [Bulk Insert limitations](https://www.zoho.com/creator/help/api/v2.1/bulk-insert-api/limitations.html)

### Workflows, performance, Blueprint, and environments

- [Understand workflows](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/understand-workflows/articles/understand-workflows)
- [Workflow limitations](https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/workflows-limitations)
- [Platform performance](https://help.zoho.com/portal/en/kb/creator/developer-guide/others/platform-performance/articles/platform-performance)
- [Understand batch workflows](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-batch-workflows/articles/understand-batch-workflows)
- [Create and manage batch workflows](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-batch-workflows/articles/create-and-manage-batch-workflows)
- [Understand Blueprint](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-blueprint/articles/understand-blueprint)
- [Create a Blueprint](https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-blueprint/articles/create-a-blueprint)
- [Understand environments](https://help.zoho.com/portal/en/kb/creator/developer-guide/environments/articles/understand-environments)
- [Manage applications in environments](https://help.zoho.com/portal/en/kb/creator/developer-guide/environments/articles/managing-applications-in-the-environments)
- [Publish applications in environments](https://help.zoho.com/portal/en/kb/creator/developer-guide/environments/articles/publishing-applications-in-environments)

### Custom APIs, microservices, pages, widgets, and portals

- [Understand Custom APIs](https://help.zoho.com/portal/en/kb/creator/developer-guide/microservices/custom-api/articles/understand-custom-apis)
- [Create and manage Custom APIs](https://help.zoho.com/portal/en/kb/creator/developer-guide/microservices/custom-api/articles/create-and-manage-custom-apis)
- [Custom API status codes](https://help.zoho.com/portal/en/kb/creator/developer-guide/microservices/custom-api/articles/custom-api-status-codes)
- [Understand Microservices](https://help.zoho.com/portal/en/kb/creator/developer-guide/microservices/the-concept-of-microservices/articles/understand-microservices)
- [Understand Connections](https://help.zoho.com/portal/en/kb/creator/developer-guide/microservices/understand-connections)
- [Understand Pages](https://help.zoho.com/portal/en/kb/creator/developer-guide/pages/create-and-manage-pages/articles/understand-pages)
- [Understand Page Builder](https://help.zoho.com/portal/en/kb/creator/developer-guide/pages/create-and-manage-pages/articles/understand-page-builder)
- [Page scripts and variables](https://help.zoho.com/portal/en/kb/creator/developer-guide/pages/page-script-and-variables/articles/page-scripts-and-variable)
- [Understand Widgets](https://help.zoho.com/portal/en/kb/creator/developer-guide/application-settings/widgets/articles/understand-widgets)
- [Create your first widget](https://help.zoho.com/portal/en/kb/creator/developer-guide/application-settings/widgets/articles/create-your-first-widget)
- [Functional URL patterns](https://help.zoho.com/portal/en/kb/creator/developer-guide/others/url-patterns/articles/functionality-based-urls)
- [Set up a portal](https://help.zoho.com/portal/en/kb/creator/developer-guide/portal/understand-portal/articles/settingup-portal)
- [Portal user permissions](https://help.zoho.com/portal/en/kb/creator/developer-guide/application-settings/portal-permissions/articles/understand-portal-user-permissions)

### Deluge Creator tasks

- [Creator integration tasks](https://www.zoho.com/deluge/help/creator-tasks.html)
- [Local Add Record task](https://www.zoho.com/deluge/help/data-access/add-record.html)
- [Creator Update Record task](https://www.zoho.com/deluge/help/creator/update-record.html)

---

**End state:** This document defines the stable Creator engineering model and the process for discovering the live application. The deployed app remains authoritative for link names, schemas, permissions, workflow order, portal access, enabled environments, connections, plans, and limits.
