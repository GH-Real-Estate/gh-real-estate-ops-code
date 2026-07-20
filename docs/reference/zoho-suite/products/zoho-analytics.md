# Zoho Analytics — Data, API, Modeling, Sharing, and Governance Knowledge Base

**Document ID:** GH-ZOHO-ANALYTICS-KB  
**Research cutoff:** 2026-07-20  
**Audience:** ChatGPT, Codex, data architects, integration developers, report builders, reviewers, and operators for GH Real Estate and Sylvara  
**Source policy:** Official Zoho documentation and Zoho's official Analytics OpenAPI repository only  
**Safety posture:** All examples are synthetic placeholders. Never commit access/refresh tokens, organization/workspace/view IDs, secret keys, customer data, export files, or private-link URLs.

## 1. AI execution contract

Evidence labels:

| Label | Meaning | AI behavior |
|---|---|---|
| **OFFICIAL** | Supported by an official page or Zoho-maintained OpenAPI file | May be used within its exact endpoint and edition context |
| **LIVE-METADATA REQUIRED** | Must be retrieved from the live organization, metadata, plan, region, source connection, or current API response | Do not guess; call/read metadata or ask for an authorized tenant export |
| **VOLATILE** | Pricing, API-unit allocation, connector limits, UI, or feature availability can change | Verify the current official page and tenant subscription |
| **INFERENCE** | Recommended GH/Sylvara architecture or control | State as a recommendation |
| **UNDOCUMENTED** | No official guarantee was found | Do not invent behavior |

Rules for ChatGPT/Codex:

1. Analytics is a reporting/analytical system, not the operational source of truth for CRM, lease, contract, payment, accounting, or document state.
2. Discover organization, workspace, view, column, formula, datasource, and permission metadata before generating code. Names are mutable; use returned IDs.
3. Select the tenant's real data center and OAuth account server. Tokens and API hosts are region-bound.
4. Use the least OAuth scope that covers the exact operation. Do not default to `ZohoAnalytics.fullaccess.all`.
5. Never construct a `criteria` string by concatenating untrusted user input. Validate identifiers against metadata and encode `CONFIG` correctly.
6. Build imports and row writes around stable source IDs, reconciliation, and replay safety. The reviewed API does not document a universal idempotency-key header.
7. Treat public publishing, no-login private links, embed URLs, exports, emails, and workspace secret keys as data-exfiltration surfaces.
8. The Zoho-maintained OpenAPI repository is the machine-readable endpoint authority for this snapshot; consult the current repository before implementation.

## 2. Product role and architecture boundary

Zoho Analytics provides data ingestion, preparation/modeling, reporting, dashboards, sharing, publishing/embedding, scheduled delivery, source connectors, and an API. Its REST API covers row data, synchronous/asynchronous bulk import/export, metadata, modeling, sharing, embedding, and user management.

**INFERENCE — GH/Sylvara ownership map:**

- Zoho CRM owns leads, contacts, applicant/customer relationships, deals, and business workflow state.
- Zoho Books owns accounting transactions and ledger truth.
- Contracts/Sign own agreement and signature state.
- Creator owns approved custom operational applications.
- WorkDrive owns governed documents.
- Forms/Sites collect public intake.
- Flow/Catalyst orchestrate or compute.
- Analytics receives curated facts and produces metrics, trends, forecasts, and read-only decision support.

Never “fix” an operational error only in Analytics. Correct it in the source system, then resynchronize/reimport and reconcile.

## 3. REST protocol, regional hosts, and headers

### 3.1 API shape

**OFFICIAL:** Zoho Analytics API v2 uses HTTPS and paths under `/restapi/v2` for most resources. The request commonly carries a URL-encoded JSON object in a parameter named `CONFIG`. File imports use multipart upload where specified. JSON is the normal API response; exports can return formats including CSV, JSON, XML, XLS, PDF, HTML, and image depending on endpoint/configuration.

Canonical request pattern:

```http
POST https://analyticsapi.zoho.example/restapi/v2/workspaces/{workspace-id}/views/{view-id}/rows
Authorization: Zoho-oauthtoken <access-token>
ZANALYTICS-ORGID: <organization-id>
Content-Type: application/x-www-form-urlencoded

CONFIG=<percent-encoded-json>
```

The organization header is required for most organization-scoped operations. Follow each OpenAPI operation rather than assuming all endpoints have identical parameters.

### 3.2 Data-center matrix

**OFFICIAL / LIVE-METADATA REQUIRED:**

| Region | Analytics API host | Accounts host |
|---|---|---|
| United States | `analyticsapi.zoho.com` | `accounts.zoho.com` |
| European Union | `analyticsapi.zoho.eu` | `accounts.zoho.eu` |
| India | `analyticsapi.zoho.in` | `accounts.zoho.in` |
| Australia | `analyticsapi.zoho.com.au` | `accounts.zoho.com.au` |
| China | `analyticsapi.zoho.com.cn` | `accounts.zoho.com.cn` |
| Japan | `analyticsapi.zoho.jp` | `accounts.zoho.jp` |
| Saudi Arabia | `analyticsapi.zoho.sa` | `accounts.zoho.sa` |
| Canada | `analyticsapi.zohocloud.ca` | `accounts.zohocloud.ca` |

The OAuth authorization response can identify the accounts server/location. Persist the region as configuration, never infer it from a user's email, and never send a token to another region.

## 4. OAuth 2.0 and scope design

### 4.1 Client and token lifecycle

**OFFICIAL:** Register an OAuth client appropriate to the application type (browser, server, mobile, non-browser, or self client). The authorization-code flow uses the regional accounts server. Zoho's Analytics guide states that a grant code is short lived (60 seconds for the described flow), an access token is valid for one hour, and offline access can yield a refresh token.

Token endpoints:

```text
POST https://{regional-accounts-host}/oauth/v2/token
POST https://{regional-accounts-host}/oauth/v2/token/revoke
```

**OFFICIAL / VOLATILE:** The guide says a refresh token remains usable until revoked, subject to limits; a user can have at most 20 refresh tokens, with the oldest removed when exceeded. A refresh token can generate at most 10 access tokens in 10 minutes, after which token creation is blocked for 10 minutes. Recheck the live OAuth page.

Security rules:

- Store client secrets and refresh tokens in a secrets manager, never GitHub or Analytics tables.
- Encrypt at rest, restrict read access, and log rotation/revocation events without token contents.
- Refresh centrally; avoid concurrent workers generating redundant access tokens.
- Revoke tokens on decommission, suspected exposure, employee departure, or scope reduction.
- Use separate clients/credentials for development, test, and production.

### 4.2 Scope families

Official scope families include:

| Domain | Representative scopes | Purpose |
|---|---|---|
| Data | `ZohoAnalytics.data.read`, `.create`, `.update`, `.delete`, `.all` | Rows, imports, exports |
| Modeling | `ZohoAnalytics.modeling.create`, `.update`, `.delete`, `.all` | Workspaces, tables, reports, formulas, folders, tags |
| Metadata | `ZohoAnalytics.metadata.read`, `.all` | Discover org/workspace/view/schema/dependencies; current OAS may define operation-specific variants |
| Share | `ZohoAnalytics.share.read`, `.create`, `.update`, `.delete`, `.all` as specified | Workspace/view sharing and groups |
| Embed | `ZohoAnalytics.embed.read`, `.create`, `.update`, `.delete`, `.all` as specified | Publish/embed/private-link/slide operations |
| User management | `ZohoAnalytics.usermanagement.read`, `.create`, `.update`, `.delete`, `.all` | Organization/workspace users and roles |
| Full access | `ZohoAnalytics.fullaccess.all` | Broad access; avoid unless formally justified |

The high-level prerequisites page can lag the operation-level OpenAPI. For a deployment, read the `security` section of the exact current operation and request the narrowest listed scope.

## 5. Discovery-first resource model

The API is ID-oriented:

```text
Organization
  └─ Workspace
      ├─ Folder
      ├─ View
      │   ├─ Table or Query Table
      │   ├─ Report or Dashboard
      │   ├─ Columns
      │   ├─ Custom/Aggregate formulas
      │   └─ Datasource/import metadata
      ├─ Variables and Tags
      ├─ Users, Admins, Groups, Shares
      └─ Email schedules / publishing configuration
```

Minimum discovery sequence:

1. `GET /restapi/v2/orgs` and select the authorized organization.
2. `GET /restapi/v2/workspaces` (or `/owned`/`/shared`).
3. `GET /restapi/v2/workspaces/{workspace-id}` for details.
4. `GET /restapi/v2/workspaces/{workspace-id}/views`.
5. `GET /restapi/v2/workspaces/{workspace-id}/views/{view-id}/metadata`.
6. Inspect dependencies, formulas, datasource/import details, and permissions before changes.

Cache IDs as environment configuration with provenance and refresh on a controlled cadence. If a view/column disappears, stop and raise schema drift; do not fall back to the first similarly named object.

## 6. Criteria language, field typing, and safe filters

**OFFICIAL:** The `criteria` expression resembles a SQL `WHERE` condition. Double-quote column names, single-quote literal strings, and use dates such as `yyyy-mm-dd` or `yyyy-mm-dd hh:mm:ss`. Supported categories include arithmetic (`+`, `-`, `*`, `/`), relational (`=`, `!=`, `<`, `>`, `<=`, `>=`), pattern/set/range operators (`LIKE`, `NOT LIKE`, `IN`, `NOT IN`, `BETWEEN`), and logical `AND`/`OR` with parentheses.

Example:

```text
"Source_Record_ID" = 'crm_example_001'
AND "Lifecycle_Status" IN ('Approved','Active')
AND "Effective_Date" >= '2026-01-01'
```

Safe construction rules:

- Validate every column against live view metadata.
- Maintain an allowlist of allowed operators per caller/use case.
- Escape or reject quotes/control characters in literal values using a tested builder; do not accept a raw criteria fragment from a public request.
- Normalize timezone before formatting timestamps.
- Parenthesize mixed `AND`/`OR` explicitly.
- Run a read/export preview with a narrow criterion before update/delete.
- Never set `updateAllRows` or an equivalent all-row option based on untrusted input.

## 7. Data API

### 7.1 Row endpoints

| Method | Path | Scope | Core purpose |
|---|---|---|---|
| `POST` | `/restapi/v2/workspaces/{workspace-id}/views/{view-id}/rows` | `ZohoAnalytics.data.create` | Add one row |
| `PUT` | same path | `ZohoAnalytics.data.update` | Update rows selected by criteria or explicit all-row option |
| `DELETE` | same path | `ZohoAnalytics.data.delete` | Delete selected rows |

`CONFIG` for row creation contains a `columns` map and can specify date parsing such as `dateFormat` or per-column date formats where documented. Update supports mapped columns, a `criteria` selector (or explicit all-row behavior), date formatting, and an `addIfNotExist` option described by the official update guide. Do not interpret `addIfNotExist` as a transactional, universal idempotent upsert without testing exact matching behavior.

Synthetic add-row configuration:

```json
{
  "columns": {
    "Source_System": "Zoho CRM",
    "Source_Record_ID": "crm_example_001",
    "Metric_Date": "2026-01-15",
    "Lifecycle_Status": "Approved"
  },
  "dateFormat": "yyyy-MM-dd"
}
```

Replay pattern:

1. Stable source record/event ID must be represented in a dedicated column.
2. Export/query by that key or use a verified update criterion.
3. Compare a source version/hash or `modified_time`.
4. Insert, update, or no-op deterministically.
5. Reconcile counts and hashes after the batch.

### 7.2 Pagination

Pagination options vary by metadata/list endpoint and are specified in each operation's `CONFIG` schema. Do not assume a single global `page`/`per_page` contract. Follow the exact OpenAPI properties and continue until the documented termination condition. For large row export, use the bulk async export workflow rather than emulating page loops when the official export API is appropriate.

## 8. Bulk API

### 8.1 Complete bulk endpoint inventory

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/restapi/v2/workspaces/{workspace-id}/data` | Synchronous import to a new table |
| `POST` | `/restapi/v2/workspaces/{workspace-id}/views/{view-id}/data` | Synchronous import to an existing table |
| `GET` | same existing-view path | Synchronous export |
| `POST` | `/restapi/v2/bulk/workspaces/{workspace-id}/data/batch` | Batch import creating a new table |
| `POST` | `/restapi/v2/bulk/workspaces/{workspace-id}/views/{view-id}/data/batch` | Batch import to existing table |
| `POST` | `/restapi/v2/bulk/workspaces/{workspace-id}/data` | Async import creating a new table |
| `GET` | same workspace bulk-data path | Async export using SQL/configuration |
| `POST` | `/restapi/v2/bulk/workspaces/{workspace-id}/views/{view-id}/data` | Async import to existing table |
| `GET` | same view bulk-data path | Async export by view |
| `GET` | `/restapi/v2/bulk/workspaces/{workspace-id}/importjobs/{job-id}` | Import job status |
| `GET` | `/restapi/v2/bulk/workspaces/{workspace-id}/exportjobs/{job-id}` | Export job status |
| `GET` | `/restapi/v2/bulk/workspaces/{workspace-id}/exportjobs/{job-id}/data` | Download completed export |

### 8.2 Async jobs

**OFFICIAL / VOLATILE:** The async guides state a maximum 100 MB import file, up to five simultaneous import/export jobs per organization, and one-hour retention for job summary or completed export data. Documented job codes include `1001` not initiated, `1002` in progress, `1003` error, `1004` completed, and `1005` not found. The example polling interval is approximately 10 seconds; implement bounded backoff and honor any current response guidance.

Async algorithm:

```text
submit job -> persist job-id + source batch-id
poll status with bounded backoff
if completed -> download/parse summary -> reconcile accepted/rejected rows
if error -> preserve sanitized error + quarantine input batch
if not found/expired -> reconcile target before resubmitting
```

Do not resubmit blindly after an ambiguous timeout; the job may exist.

### 8.3 Batch import

**OFFICIAL:** Each chunk can be up to 100 MB. The first request uses a batch start marker; later requests use the returned batch key; the final request sets the final-batch flag. Order is preserved. With Append or UpdateAdd, batches can be committed individually; with TruncateAdd, the replacement is applied only after the final batch. Exact `CONFIG` property casing/values must come from the live/current OpenAPI and batch-import page.

TruncateAdd is destructive. Require a snapshot/export, row-count controls, approval, test import, and rollback plan.

### 8.4 Export configuration

Official synchronous export options include response format, `criteria`, password protection where applicable, selected columns, and switches controlling hidden/personal columns. The defaults described for hidden and personal columns are false. Dashboard exports have format-specific configuration.

**OFFICIAL:** The synchronous export guide restricts some cases, including tables exceeding one million rows, live-connected data sources, and certain dashboards/query tables. Use asynchronous export for large/complex workloads.

Export security:

- Request only required columns; explicitly keep hidden/personal columns excluded.
- Prefer machine-readable CSV/JSON for pipelines and verify encoding/delimiters.
- Encrypt exports, set short retention, log access, and delete temporary artifacts.
- Never use a public/private published URL as an ETL credential substitute.

## 9. Complete API family catalog

This catalog is derived from Zoho's official `analytics-oas` v2.0 files. Paths are exact for the snapshot. Re-read the current repository before building. The Share OAS contains several group/permission paths without the `/restapi/v2` prefix; do not “correct” or normalize them without checking the current operation/server definition.

### 9.1 Metadata

| Area | Official methods and paths |
|---|---|
| Organizations/workspaces | `GET /restapi/v2/orgs`; `GET /restapi/v2/workspaces`; `/workspaces/owned`; `/workspaces/shared`; `GET /workspaces/{workspace-id}` |
| Views/folders/recent/trash/dashboards | `GET /workspaces/{id}/views`; `/folders`; `/trash`; `GET /recentviews`; `GET /dashboards`, `/dashboards/owned`, `/dashboards/shared` |
| Object detail | `GET /views/{view-id}`; `/workspaces/{id}/views/{view-id}/metadata`; `/dependents`; `/columns/{column-id}/dependents` |
| Query tables | `GET /workspaces/{id}/querytables`; `/querytables/{query-table-id}` |
| Tags | `GET /workspaces/{id}/tags`; `/tags/{tag-id}/views`; `/views/{view-id}/tags` |
| Favorites/defaults | `POST`/`DELETE /workspaces/{id}/favorite`; `/default`; `/views/{view-id}/favorite` |
| Formulas | `GET /views/{id}/customformulas`; `/aggregateformulas`; workspace formulas; aggregate formula dependents/value |
| Datasources/import | `GET /views/{id}/datasources`; `/importdetails`; `POST /datasource/{id}/sync`; `POST /views/{id}/sync`; `PUT /datasource/{id}` |
| Schedules/config | `GET /workspaces/{id}/emailschedules`; `GET /metadetails`; `GET /workspaces/{id}/template/data` |
| White label | `POST`/`DELETE /workspaces/{id}/wlaccess` |
| AutoML metadata | `GET /automl/analysis`; workspace analyses/details/model deployments |
| Workspace secret | `GET /workspaces/{id}/secretkey` — highly sensitive; avoid unless required |

### 9.2 Modeling

| Area | Official operation set |
|---|---|
| Workspaces | Create, copy, rename/update, delete: `POST /workspaces`, `POST`/`PUT`/`DELETE /workspaces/{id}` |
| Tables/query tables/reports | Create table; create/update query table; create/update report |
| Views | Save As, move to folder, rename/update, delete, restore/delete from trash |
| Folders | Create, rename, delete, set default, move, reorder |
| Columns/data design | Sort data; add/rename/delete column; add/delete lookup; hide/show/reorder columns |
| Copy/analyze | Copy views/formulas; create similar views; auto-analyze view/column |
| Variables | `GET`/`POST /variables`; `GET`/`PUT`/`DELETE /variables/{variable-id}` |
| Custom/aggregate formulas | Create, update, delete per view |
| Email schedules | Create, update, delete, trigger, enable/disable status |
| Tags | Create/update/delete; assign/remove tags to/from views |
| AutoML | Create/delete analyses/models; deploy/delete deployment; what-if; execute deployment |

Modeling changes can break reports, formulas, schedules, APIs, and downstream exports. Inspect dependency endpoints first and treat deletions/renames as governed schema migrations.

### 9.3 Embed and publishing

| Method(s) | Path | Purpose |
|---|---|---|
| `GET` | `/restapi/v2/workspaces/{workspace-id}/views/{view-id}/publish` | Publishing information |
| `GET` | `.../publish/embed` | Generate/retrieve embed URL/config response |
| `GET`/`POST`/`DELETE` | `.../publish/privatelink` | List/create/remove private link |
| `POST`/`DELETE` | `.../publish/public` | Publish/unpublish publicly |
| `GET`/`PUT` | `.../publish/config` | Read/update publish configuration |
| `GET`/`POST` | `/restapi/v2/workspaces/{workspace-id}/slides` | List/create slides |
| `GET`/`PUT`/`DELETE` | `.../slides/{slide-id}` | Slide lifecycle |
| `GET` | `.../slides/{slide-id}/publish` | Slide publish result |

The embed URL guide describes short-lived, no-login access for embedded-analytics customers. Its `CONFIG` can carry criteria, display controls, validity period (documented default 3600 seconds), and permissions such as export, View Underlying Data, drilldown, and insight; sensitive permissions default false in the described contract. Generate on a trusted server after authorizing the viewer. Bind criteria to server-side tenant identity; never accept client-provided tenant criteria.

Private links can include password, expiry, and permissions. For applicant, tenant, owner, lease, or financial data, prefer authenticated per-user access. Public publishing is prohibited unless the dataset is explicitly classified public and approved.

### 9.4 Sharing

| Area | Operations |
|---|---|
| Organization/workspace admins | Get org admins; get/add/remove workspace admins |
| Workspace/view shares | Get workspace sharing; share/unshare/update views |
| Effective access | Get current user's view permissions; get shared details |
| Groups | List/create/get/update/delete groups; add/remove members |

Recheck the exact OAS path/server definitions for group and permission endpoints because several official paths omit `/restapi/v2` in the repository snapshot.

### 9.5 User management

| Area | Operations |
|---|---|
| Organization users | List/add/remove; activate/deactivate; change role |
| Subscription/resources | Read subscription and resource details |
| Workspace users | List/add/remove; change status/role |
| Custom organization roles | List/create/update/delete |

These operations are high impact. Use separate administrative credentials, approval, and post-change access review.

## 10. Response, error, retry, and concurrency model

**OFFICIAL:** Failures use HTTP 4xx/5xx and a JSON failure envelope containing status/summary/data with fields such as `errorCode` and `errorMessage`. Parse both HTTP status and API status; do not treat an HTTP transport success as business success without inspecting the body.

The API-unit page identifies over-limit error codes including `6043` and `6044`; consult the current error catalog for exact interpretation. Error handling:

| Class | Response |
|---|---|
| Authentication/authorization | Stop, refresh only when appropriate, verify region/scopes/org header; do not retry invalid permission indefinitely |
| Validation/criteria/schema | Quarantine request; refresh metadata; require correction |
| Rate/API-unit limit | Delay until documented reset; reduce request cost; do not fan out retries |
| 5xx/network timeout | Retry with exponential backoff+jitter only after checking replay safety |
| Async job error | Read job summary, isolate rejected data, correct and submit a new controlled batch |
| Not found | Refresh IDs/metadata; distinguish deleted/moved object from wrong organization/region |

**UNDOCUMENTED:** No universal idempotency header, ETag/optimistic concurrency contract, or global retry-after guarantee was found for all v2 operations. Use stable source keys, source version columns, lookup-before-write, serialized mutations to the same resource, and post-write reconciliation.

## 11. API units and capacity

**VOLATILE:** At the cutoff, the official API-unit page listed daily plan allocations of approximately: Free 1,000; Basic 4,000; Standard 10,000; Premium 30,000; Enterprise 100,000. Verify subscription and current allocation in the tenant.

Representative costs from that page included:

| Operation | Documented unit example |
|---|---:|
| Append/TruncateAdd import | 10 units per 1,000 rows |
| UpdateAdd import | 15 units per 1,000 rows |
| Add row | 0.1 unit |
| Update row | 0.3 unit |
| Delete row | 0.1 unit |

Modeling, metadata, sharing, and other operations have their own costs. Compute capacity from the current table, not these examples. Batch where safe, cache metadata briefly, avoid polling too fast, and reserve capacity for reconciliation/recovery.

## 12. Connectors, refresh, and live connection

### 12.1 Zoho CRM and Books

Official connector guides support importing CRM and Books data with configurable modules/fields and scheduled sync, plus prebuilt reporting content. Connector setup generally requires an appropriately privileged administrator. Initial synchronization can take from minutes to hours based on volume.

Design rules:

- Preserve source record IDs in Analytics.
- Include source modified time and load/sync time.
- Do not infer that every operational field/module is available; inspect selection metadata.
- Reconcile record counts and expected mandatory fields after first and subsequent syncs.
- Treat Analytics reports as lagged according to schedule, not current transactional state.

### 12.2 Multiple sync schedules

The source-management help describes immediate/manual sync constraints and up to five sync schedules per connection for supported scenarios. This is connector/edition dependent and **VOLATILE**. Avoid aggressive refresh when the source API or Analytics units cannot sustain it.

### 12.3 Live Connect

**OFFICIAL / VOLATILE:** Live Connect is described for Premium/Enterprise. Queries execute against the source in real time while Analytics stores metadata rather than imported data. Connections can use SSL/SSH for supported databases. Schema changes require Sync Design/manual mapping. Lookups are limited to the same live source, while dashboards can combine sources; Query Table capabilities vary by selected database/source.

Live Connect is not automatically lower risk: it increases dependency on source availability, query performance, network allowlists, credentials, and least-privilege database access. Use a read-only account and test load.

### 12.4 Events and webhooks

Analytics API v2 is primarily request/job/sync oriented. No general record-change webhook/event bus is documented in the reviewed API. For event-driven operational automation, use the source product's webhook/Flow/Catalyst, then load a curated analytical fact. Email schedules and data-source sync/refresh endpoints are not substitutes for source-of-truth events.

## 13. Security, audit, and data governance

### 13.1 Workspace controls

Official security controls include organization/workspace IP restrictions, restrictions on sharing to trusted domains (the guide describes up to 100), controls for public views, and an option to disable no-login private links. Exact edition availability must be checked.

Minimum policy:

- Separate public, internal, confidential, and restricted workspaces/datasets.
- Disable public/no-login publishing by default.
- Use role/group-based access and quarterly recertification.
- Restrict exports, underlying-data access, and email scheduling.
- Separate developer/modeler from production sharing administrator for sensitive datasets.
- Never expose workspace secret keys or private/embed URLs in client logs or GitHub.

### 13.2 Activity Logs

Official Activity Logs can record date/time, performer, action/category, workspace/view, details/remarks, IP, and user agent for activities including imports, workspace/view/table/user/share/publish/export/email, and white-label changes. Availability/configuration is plan dependent.

Activity logs complement—not replace—source-system audit. Export/retain them according to policy, monitor high-risk actions, and alert on public publishing, bulk export, privilege changes, and deleted data models.

### 13.3 Data minimization

- Do not import SSNs, full bank/payment credentials, raw background reports, secret keys, or unneeded applicant documents.
- Use pseudonymous stable IDs for cross-system joins when identities are unnecessary.
- Keep protected-class or fair-housing-sensitive information out of broad operational dashboards unless a documented lawful purpose and access control exists.
- Aggregate where detail is unnecessary; suppress small cohorts where re-identification is possible.
- Give every column an owner, source, definition, sensitivity, refresh expectation, and retention rule.

## 14. GH Real Estate and Sylvara analytical patterns

### 14.1 Curated lifecycle mart

Recommended fact grain: one immutable event or one daily snapshot per applicant/lease/property, never a mixture.

Core lineage columns:

```text
source_system, source_object, source_record_id, source_event_id,
source_modified_at_utc, loaded_at_utc, schema_version,
property_id, lifecycle_stage, effective_date, metric_value
```

Use dimensions for property, market, channel, and calendar. Do not join by mutable property name, email, or phone.

### 14.2 Funnel metrics

Forms/Sites submission -> CRM lead -> application -> approval -> contract -> signature -> move-in. Define numerator, denominator, exclusion reasons, date basis, and source for each stage. Snapshot late-arriving changes and disclose synchronization lag.

### 14.3 Financial reporting

Books remains authoritative. Import invoice/payment/credit IDs, status, dates, currency, and approved dimensional keys. Reconcile totals to Books by period/org/currency before publishing. Do not calculate a replacement ledger in Analytics.

### 14.4 Tenant/owner portals

Generate short-lived embed access server-side only after authenticating/authorizing the viewer. Bind the row-level criterion to the server-held tenant/owner ID. Disable export and underlying-data access unless approved. Never trust a tenant ID supplied by browser JavaScript.

### 14.5 Operational alerts

Analytics can highlight trends and exceptions, but a scheduled dashboard/email is not a transactional workflow guarantee. Critical rent/payment, lease, safety, or compliance actions should originate from the owning application/controlled workflow, with Analytics as reconciliation and oversight.

## 15. Modeling and deployment controls

1. **Inventory:** current workspaces, views, datasources, schedules, shares, embeds, formulas, variables, tags, users, and dependencies.
2. **Define:** grain, keys, lineage columns, source ownership, time zone/currency, metric formulas, classification, and retention.
3. **Prototype:** non-production workspace with synthetic/de-identified data.
4. **Validate:** schema, row counts, uniqueness, nulls, referential integrity, aggregates vs source, criteria escaping, API-unit cost, and role access.
5. **Review:** dependency impact for rename/delete/formula/lookup changes; privacy review for sharing/embed/export.
6. **Deploy:** controlled migration using supported modeling APIs/manual process; log IDs/config/version externally without credentials.
7. **Observe:** job status, sync failures, API units, activity log, public/private links, schedule recipients, query/load performance.
8. **Rollback:** retain model definitions/source queries and a data reload path; API delete/TruncateAdd can be irreversible without backup.

The OpenAPI catalog exposes create/update/delete capabilities but does not by itself constitute a complete environment-promotion mechanism. Build an explicit manifest of logical objects, live IDs, dependencies, scopes, and validation queries.

## 16. Anti-patterns

- Using Analytics as CRM, Books, lease, or payment truth.
- Hardcoding workspace/view/column IDs copied from another environment without discovery.
- Concatenating raw user input into `criteria`.
- Broad `fullaccess` OAuth when read/metadata scopes suffice.
- Blind retry of an import/update after a timeout.
- TruncateAdd without backup, approval, and row-count guard.
- Public/no-login links for confidential tenant, owner, applicant, or financial data.
- Client-side generation of embed criteria or URL.
- Importing all columns “just in case.”
- Assuming scheduled sync is real time.
- Ignoring rejected-row summaries or timezone/currency normalization.
- Renaming/deleting a view/column without dependency analysis.
- Committing exports, IDs, tokens, secret keys, or private URLs to GitHub.
- Treating AutoML output as an autonomous housing, credit, applicant, pricing, or legal decision.

## 17. Implementation checklist

### Tenant and authorization

- [ ] Confirm region, API/account hosts, organization ID, edition, and API-unit allocation.
- [ ] Register environment-specific OAuth client and minimal scopes.
- [ ] Store/revoke/rotate tokens through a secrets manager.
- [ ] Discover all object IDs and metadata from the target organization.

### Data contract

- [ ] Define source system/record/event IDs, grain, schema version, modified/load times.
- [ ] Define column types, date/time zone, currency, allowed nulls and enums.
- [ ] Define dedupe/update behavior and reconciliation queries.
- [ ] Classify and minimize every field.

### API build

- [ ] Use correct regional host, authorization header, org header, and URL-encoded `CONFIG`.
- [ ] Validate criteria identifiers/values; prevent all-row mutation by default.
- [ ] Choose row, sync bulk, async bulk, or connector based on volume/latency.
- [ ] Poll jobs with bounded backoff; persist job IDs and parse row summaries.
- [ ] Budget API units and concurrent jobs.

### Modeling/share/deploy

- [ ] Query dependents before schema/formula deletion or rename.
- [ ] Test source reconciliation and access with each intended role.
- [ ] Review shares, groups, private/public links, embed permissions, export, and email schedules.
- [ ] Record rollback/reload instructions.
- [ ] Monitor activity logs and public-publishing/privilege-change events.

## 18. Official source registry

All sources were accessed 2026-07-20.

### API fundamentals and OAuth

1. **API v2 Introduction — Zoho Analytics**  
   https://www.zoho.com/analytics/api/v2/introduction.html
2. **API Specification**  
   https://www.zoho.com/analytics/api/v2/api-specification.html
3. **Prerequisites, scopes, and criteria**  
   https://www.zoho.com/analytics/api/v2/prerequisites.html
4. **Authentication overview**  
   https://www.zoho.com/analytics/api/v2/authentication.html
5. **Register a new OAuth client**  
   https://www.zoho.com/analytics/api/v2/authentication/reg-new-client.html
6. **Generate authorization code**  
   https://www.zoho.com/analytics/api/v2/authentication/generating-code.html
7. **Generate access and refresh token**  
   https://www.zoho.com/analytics/api/v2/authentication/generating-token.html
8. **Refresh access token**  
   https://www.zoho.com/analytics/api/v2/authentication/refresh-token.html
9. **Revoke token**  
   https://www.zoho.com/analytics/api/v2/authentication/revoke-token.html
10. **Official OpenAPI specification page**  
    https://www.zoho.com/analytics/api/v2/open-api-specification.html
11. **Zoho official Analytics OpenAPI repository**  
    https://github.com/zoho/analytics-oas

### Data and bulk operations

12. **Add row**  
    https://www.zoho.com/analytics/api/v2/data-api/add-row.html
13. **Update row(s)**  
    https://www.zoho.com/analytics/api/v2/data-api/update-row.html
14. **Delete row(s)**  
    https://www.zoho.com/analytics/api/v2/data-api/delete-row.html
15. **Bulk API overview**  
    https://www.zoho.com/analytics/api/v2/bulk-api.html
16. **Asynchronous import**  
    https://www.zoho.com/analytics/api/v2/bulk-api/import-data-async.html
17. **Asynchronous export**  
    https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async.html
18. **Batch import**  
    https://www.zoho.com/analytics/api/v2/bulk-api/batch-import.html
19. **Synchronous export**  
    https://www.zoho.com/analytics/api/v2/bulk-api/export-data.html
20. **API units**  
    https://www.zoho.com/analytics/api/v2/api-limits-pricing/api-units.html

### Embed, sources, and governance

21. **Generate embed URL**  
    https://www.zoho.com/analytics/api/v2/embed-api/embed-url.html
22. **Create private URL**  
    https://www.zoho.com/analytics/api/v2/embed-api/create-private-url.html
23. **Security controls**  
    https://www.zoho.com/analytics/help/connectors/security-controls.html
24. **Activity Logs**  
    https://www.zoho.com/analytics/help/accounts/audit-logs/activity-logs.html
25. **Live Connect**  
    https://www.zoho.com/analytics/help/datasources/live-connect.html
26. **Zoho CRM connector**  
    https://www.zoho.com/analytics/help/connectors/zoho-crm.html
27. **Zoho Books connector**  
    https://www.zoho.com/analytics/help/connectors/zohobooks.html
28. **Manage data sources**  
    https://www.zoho.com/analytics/help/managing-datasources.html
29. **Multiple sync schedules**  
    https://www.zoho.com/analytics/help/import-data/multiple-sync-schedule.html

## 19. Explicit research gaps

- **UNDOCUMENTED:** A universal API idempotency-key header and cross-resource optimistic-concurrency/ETag contract were not found. Design stable keys, serialized changes, and reconciliation.
- Pagination, maximum results, and specific `CONFIG` properties are operation-specific. Do not apply one endpoint's arguments globally.
- Connector field coverage, refresh interval, historical depth, and plan eligibility must be inspected in the live tenant.
- API unit allocations/costs and async concurrency/retention are **VOLATILE**; current pages and tenant resources supersede this snapshot.
- AutoML is documented as an API family but requires separate model-governance, fairness, explainability, monitoring, and human-review controls. It must not autonomously make protected/high-impact real-estate decisions.
- Analytics does not document a generalized source-record event webhook. Use the source application's official event mechanism.

---

**AI stop condition:** If a request requires unknown live IDs, fields, scopes, permissions, plan features, or operation-specific arguments, return a discovery plan and a non-deployable template. Do not fabricate a working request.
