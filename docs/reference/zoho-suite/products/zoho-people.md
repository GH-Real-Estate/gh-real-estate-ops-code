# Zoho People HRIS, API, Automation, and Integration Knowledge Base

**Document ID:** GH-ZOHO-PEOPLE-KB
**Research cutoff:** 2026-07-20
**Audience:** ChatGPT, Codex, solution architects, integration engineers, HR administrators, and GH Real Estate / Sylvara system owners
**Evidence policy:** Current official Zoho documentation only. The authorized Zoho People organization, its live metadata, permissions, subscription, data center, and endpoint-specific documentation remain authoritative.

## 1. AI retrieval and execution contract

Use this document to choose a supported Zoho People surface, discover its live schema, and design safe HR workflows. It is a retrieval map and engineering policy, not authorization to view or change employee data.

### Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `[OFFICIAL]` | Directly supported by a linked Zoho source at the research cutoff | Recheck the linked page before implementation |
| `[LIVE-DISCOVERY]` | Organization IDs, form/field names, permissions, policies, or subscription state must come from the authorized tenant | Fetch or inspect in the target environment; never guess |
| `[VOLATILE]` | Plan availability, limits, UI behavior, regional availability, or an integration contract can change | Verify immediately before release |
| `[DOC-DRIFT]` | Official pages expose different generations, names, paths, or scope spellings | Follow the exact page for the exact operation and prove it in a contract test |
| `[DOC-GAP]` | Public documentation does not establish the behavior | Do not invent an endpoint, field, event, retry guarantee, or security property |
| `[DESIGN]` | GH/Sylvara architecture guidance derived from official behavior | Validate with HR, security, legal, and business owners |

### Non-negotiable rules

1. **Zoho People is the employee HR system of record, not the CRM.** Do not model tenants, applicants, owners, vendors, properties, leases, invoices, or customer support cases as employees merely to obtain automation.
2. Treat employee record numbers, Employee IDs, email addresses, form link names, field label names, component IDs, lookup IDs, row IDs, view IDs, leave-type IDs, shift IDs, project/job IDs, and file IDs as distinct, opaque identifiers. Discover and persist their meanings.
3. Run metadata discovery before form integration. A display label may be renamed while the API-facing field label name remains unchanged; a lookup write normally needs the returned record ID rather than its display text.
4. Never infer an endpoint version. Zoho currently documents classic form and service APIs beside v3 leave, attendance, shift, performance, and file APIs. Copy the HTTP method, path, content type, scope, parameter names, date format, response envelope, and threshold from the operation page actually used.
5. Never place OAuth grants, access/refresh tokens, client secrets, connection credentials, payroll or bank data, government identifiers, medical information, performance content, employee documents, or raw HR payloads in Git, prompts, PDFs, fixtures, URLs, or broad logs.
6. OAuth scope does not replace Zoho People authorization. The authorizing user, service permissions, form permissions, field permissions, record visibility, and action permissions still constrain access.
7. Read before mutating; use the narrowest operation; retain a correlation ID and redacted audit evidence; re-read the record. Destructive employee, leave, attendance, performance, or file operations require explicit approval and a recovery plan.
8. Do not call a webhook exactly-once. Authenticate the receiver, deduplicate, queue, retry safely, and reconcile. Zoho's public webhook page does not document a cryptographic signature contract.
9. Published API thresholds are endpoint-specific. Do not convert one page's “requests / lock period” value into a product-wide quota.
10. HR automations must minimize data. ChatGPT/Codex should receive only the fields required for the approved task; consequential employment decisions remain human decisions.

## 2. Product boundary and service map

`[OFFICIAL]` Zoho People combines HR administration with Employee Information, Onboarding, Leave, Attendance, Shifts, Timesheets, Performance, Employee Engagement, Cases, Files, Compensation, and Learning Management. Enabled services and forms depend on the organization and subscription.

| Domain | Appropriate People responsibility | Boundary |
|---|---|---|
| Employee master | Identity within the employer, reporting manager, department, location, designation, employment status, joining/exit data, organization-specific HR fields | Zoho Directory/Mail may own account provisioning; do not assume People is the identity provider |
| Onboarding/offboarding | Candidate-to-employee HR tasks, forms, documents, policies, checklists, e-sign steps, and lifecycle workflows | Recruit owns recruiting; Sign owns signature evidence; WorkDrive may own governed file collaboration |
| Leave | Leave types, balances, requests, grants, approvals, holidays, and reports | Payroll/accounting treatment must be verified in its authoritative product |
| Attendance and shifts | Punches, attendance entries, regularization, schedules, shifts, and device imports | Do not equate a raw punch with approved payable time |
| Timesheets | Clients, projects, jobs, time logs, timers, and timesheet approvals | Books/Projects may receive data but keep their own IDs and posting states |
| Performance | KRAs, goals, competencies, skills, appraisals, feedback, and configured processes | Never automate adverse employment action solely from generated analysis |
| Cases | Internal employee request/case handling | CRM/Desk remains authoritative for customer or tenant cases |
| Files and HR documents | Employee HR files, templates, letters, and configured e-sign flows | Do not duplicate regulated documents across products without a retention/access design |
| LMS and engagement | Courses, learning, surveys, announcements, and employee experience | Confirm which functions expose supported APIs before promising integration |
| Compensation | HR compensation configuration and records | Books/Payroll/bank remain authoritative for actual posting/payment as applicable |

### GH Real Estate and Sylvara authority ladder

Use People for the organizations' actual workforce. Use CRM for leads, applicants, residents, buyers/sellers, owners, vendors, and business relationships; Books/Billing/Payments for financial truth; Contracts and Sign for contract/signature truth; WorkDrive for approved document repositories; Creator for custom operational apps; Catalyst/Flow for governed cross-product orchestration.

`[DESIGN]` GH property staff, leasing staff, maintenance employees, and Sylvara employees can belong in People. Independent contractors may be represented only if HR/legal has defined that operating model. A plumbing vendor company and its contacts belong in CRM/Books vendor records, not the employee form.

## 3. Authentication, regions, environments, and scopes

### OAuth 2.0 lifecycle

`[OFFICIAL]` Zoho People uses OAuth 2.0 authorization-code flows. Register the appropriate client in the Zoho API Console, request organization-specific consent, exchange the one-time grant at the matching regional Zoho Accounts host, and store the refresh token in a secrets manager. Send access tokens as:

```http
Authorization: Zoho-oauthtoken <access_token>
```

The token response includes `access_token`, `refresh_token`, `expires_in`, and `api_domain`. Access tokens are valid for one hour; refresh tokens remain usable until revoked. The current v3 token-validity page also documents issuance limits, including ten grant tokens per ten minutes per client ID, ten access tokens per ten minutes, and twenty refresh tokens per ten minutes per client ID, with older refresh tokens displaced after the stated maximum. Treat these as `[VOLATILE]` and use one controlled refresh process rather than minting tokens per request.

Always use the domain-specific Accounts host and retain the returned `api_domain` as token metadata. Grant, token, organization, production/sandbox environment, and client secret must agree. A refresh token for one organization/environment cannot be reused for a different one. `[DOC-DRIFT]` The OAuth page says to use `api_domain`, while current People operation pages publish regional `people.zoho.*` request hosts. Do not mechanically splice a People path onto a generic Zoho APIs domain: follow the operation's formal regional Request URL, contract-test it in the target DC, and escalate a live conflict to Zoho support.

### People data-center hosts

The current People migration guide lists:

| Data center | People host |
|---|---|
| United States | `people.zoho.com` |
| Europe | `people.zoho.eu` |
| India | `people.zoho.in` |
| Japan | `people.zoho.jp` |
| Canada | `people.zohocloud.ca` |
| China | `people.zoho.com.cn` |
| Australia | `people.zoho.com.au` |

Do not derive the host from an employee's location. Store the organization's verified DC and API base in environment configuration. Do not allow arbitrary user-supplied hosts. Reauthorization and integration reconfiguration may be necessary after a DC migration.

### Scope grammar and documentation drift

The published grammar is `ZOHOPEOPLE.<scope-name>.<operation>`, where operations may include `READ`, `CREATE`, `UPDATE`, `DELETE`, or `ALL`. The v3 scope index currently lists families including:

- `ZOHOPEOPLE.employee.ALL`
- `ZOHOPEOPLE.forms.READ`, `.CREATE`, `.UPDATE`, or `.ALL`
- `ZOHOPEOPLE.dashboard.ALL`
- `ZOHOPEOPLE.automation.ALL`
- `ZOHOPEOPLE.timetracker.ALL`
- `ZOHOPEOPLE.attendance.READ`, `.CREATE`, or `.ALL` as specified by endpoints
- `ZOHOPEOPLE.leave.READ`, `.CREATE`, `.UPDATE`, `.DELETE`, or `.ALL` as specified by endpoints

`[DOC-DRIFT]` The Fetch Forms and Components pages display singular `ZOHOPEOPLE.form.READ`, while the central list and other form operations use plural `ZOHOPEOPLE.forms.*`. Performance and file endpoints can document additional families. Do not normalize these strings from memory. For each route, record the scope printed on that live endpoint page and confirm consent in the target DC.

### Least-privilege client pattern

Prefer separate clients or connections by responsibility: read-only HR reporting, attendance-device ingestion, controlled lifecycle orchestration, and administrative migration should not share a universal token. Bind credentials to a named service owner, rotate/revoke them through change control, alert on failed refreshes, and inventory every enabled scope quarterly.

## 4. Metadata-first data model

Zoho People's generic form APIs make live configuration part of the API contract. Custom forms and fields vary by organization, and even standard forms can be configured.

### Discovery sequence

1. Call `GET /people/api/forms` to enumerate accessible forms and capture each `formLinkName`, display name, component ID, visibility, permissions, and default view details.
2. For each approved form, call `GET /people/api/forms/{formLinkName}/components` to retrieve its field components.
3. Call `GET /people/api/forms/{formLinkName}/views` and, where needed, the default/custom-view API to resolve supported views.
4. Read a small, authorized record sample and record the actual response envelope, field keys, lookup structures, tabular-section representation, null/date behavior, and permission effects.
5. Create a sanitized schema manifest with retrieval date, organization/environment/DC, source URLs, and a hash. Diff it before deployments.

Example manifest shape:

```yaml
verified_at: "2026-07-20T00:00:00Z"
environment: production
dc: us
forms:
  - form_link_name: employee
    component_id: "<opaque-id>"
    fields:
      - api_label_name: EmployeeID
        display_name: "Employee ID"
        type: "<live-type>"
        required: true
        readable: true
        writable: "<live-permission>"
```

This example is a schema pattern, not tenant metadata.

### Identifier taxonomy

| Identifier | Meaning and rule |
|---|---|
| `formLinkName` | Stable link name used in form routes; obtain from form metadata/appendix, never from a translated display name |
| Field label name | API key used in `inputData`; Zoho notes that changing a display name does not change the label name used by the API |
| Employee record number / `erecno` / `employee_zoho_id` | Internal employee record identifier used by many service APIs; do not confuse with the business Employee ID |
| `EmployeeID` / `employee_id` | Organization-assigned employee identifier; formatting and uniqueness are organization policy |
| Employee email | Alternate selector on some endpoints; emails can change and should not be the sole durable join key |
| Record primary key / `pkId` / `record_id` | Opaque form or service record identity returned by the API |
| Component, view, lookup, leave-type, shift, project, job, file IDs | Opaque IDs scoped to an organization/environment; discover, validate, and store with type context |
| `ROWID` | Identity used when updating rows in tabular sections; preserve it when round-tripping existing rows |

Never strip digits into a generic integer when an ID is serialized as a string. Never join objects because two large numeric IDs happen to match across products or environments.

### Field and form behavior

- Lookup writes require the referenced record ID documented by component metadata, not an employee or department display string.
- Insert operations accept `inputData`; tabular-section values must be represented as a JSON array as documented by the insert API.
- Update operations can require row-aware payloads for tabular data. Read the current record and preserve `ROWID` values to avoid accidental row replacement.
- Picklists, multi-select values, date/time formats, required fields, validation rules, and permissions are configuration. Validate against metadata and a nonproduction test.
- The response envelopes differ between classic form APIs (`response.result`, `response.status`) and v3 services (`data`, `message`, `status`). Build route-specific parsers.

## 5. Employee and generic form APIs

### Core operation catalog

| Capability | Documented route pattern or page | Method / scope | Key controls |
|---|---|---|---|
| List forms | `/people/api/forms` | GET; page shows `ZOHOPEOPLE.form.READ` | 30 requests then 5-minute lock on current page |
| Get form components | `/people/api/forms/{formLinkName}/components` | GET; page shows `ZOHOPEOPLE.form.READ` | Capture types, label names, options, and permissions; current page shows 400 requests / 5-minute lock |
| Get form views | `/people/api/forms/{formLinkName}/views` | GET; `ZOHOPEOPLE.forms.READ` | Do not assume a UI view name is a link name; current page shows 30 / 5 minutes |
| Insert record | `/people/api/forms/json/{formLinkName}/insertRecord` | POST; `ZOHOPEOPLE.forms.CREATE` | Form-encoded `inputData`; optional `isDraft`; current page shows 100 / 5 minutes |
| Update record | Generic form update operation | POST as documented; `ZOHOPEOPLE.forms.UPDATE` | Resolve record ID and current fields first; handle tabular rows explicitly |
| Get bulk records | `/people/api/forms/{formLinkName}/getRecords` | GET; `ZOHOPEOPLE.forms.READ` | Maximum 200 records per call; one-based start index; supports `modifiedtime` milliseconds and employee ID/email search; current page shows 400 / 5 minutes |
| Fetch records through a view | Form/view record operation | GET; exact page scope | Respect view filters, indexes, and live permission effects |
| Search form records | Search Record operation | GET; exact page scope | Use documented search syntax; do not synthesize SQL-like criteria |
| Get record count | Record Count operation | GET; exact page scope | Pair with pagination/reconciliation; a count is not an export |
| Get related records | Related/single-record form operation | GET; exact page scope | Resolve form and record IDs; validate relationship direction |

`[DOC-DRIFT]` Some sample URLs omit the extra `/people` segment shown in the formal Request URL. Use the operation's formal request URL, correct regional host, and a contract test; do not combine fragments from two examples.

### Employee creation modes

The employee-add API requires `EmployeeID`, `FirstName`, `LastName`, and `EmailID`. Zoho documents invitation, non-user, and direct-add modes. A user invitation affects access; a non-user employee record does not grant login. Direct add is documented only for standalone Zoho People and is not supported for Zoho One, People Plus, or bundled deployments. Therefore:

1. Detect the subscription/tenant model before choosing a mode.
2. Check whether the email already belongs to a Zoho organization/account.
3. Separate HR record creation from account licensing and application access.
4. Verify manager, department, location, designation, and joining state after creation.
5. Never “fix” a failed bundle provisioning flow by retrying the standalone direct-add API.

The onboarding trigger API can initiate onboarding for selected employees/candidates where configured. Treat this as a consequential workflow start: resolve the person, template/process, due dates, document recipients, and prior onboarding state; create an idempotency key outside People; then confirm the resulting status.

### Incremental synchronization

For eligible forms, `getRecords` accepts `modifiedtime` as epoch milliseconds. A safe pull loop uses a persisted high-water mark with an overlap window, paginates up to 200 records per request, deduplicates by typed record ID plus modified time, and advances the high-water mark only after durable processing. Run a periodic full count/sample reconciliation because deletes, permission changes, and configuration changes may not appear as ordinary modified records.

Do not use employee email as the only deduplication key. Do not interpret absence from a permission-filtered response as deletion. Offboarding usually changes employment status and access across systems; it is not merely a record-delete event.

## 6. Leave API v3

The v3 leave tracker separates requests, grants, compensatory-off records, holidays, settings, and reports. Use the endpoint index rather than assuming that everything is generic form data.

### Leave request contract

| Operation | Route | Method / scope | Important fields |
|---|---|---|---|
| List requests | `/people/api/v3/leave-tracker/leaves` | GET; `ZOHOPEOPLE.leave.READ` | Date/range, employee, department/location, approval filters, data-selection and pagination fields as documented |
| Get one request | `/people/api/v3/leave-tracker/leaves/{record_id}` | GET; `ZOHOPEOPLE.leave.READ` | Returns employee, leave type, dates/day breakdown, approval status, and IDs |
| Add request | `/people/api/v3/leave-tracker/leaves` | POST; `ZOHOPEOPLE.leave.CREATE` | One employee selector, `leave_type_id`, `from_date`, `to_date`, `unit`; optional reason, per-day structure, approver, custom fields |
| Edit request | `/people/api/v3/leave-tracker/leaves/{leave_record_id}` | PUT; `ZOHOPEOPLE.leave.UPDATE` | Page requires employee Zoho ID, leave type, dates, and unit; re-read approval state before edit |
| Delete request | `/people/api/v3/leave-tracker/leaves/{record_id}` | DELETE; `ZOHOPEOPLE.leave.DELETE` | Destructive; confirm person, dates, approval/payroll impact, and policy |
| List/add grant | `/people/api/v3/leave-tracker/grant` | GET/POST; `ZOHOPEOPLE.leave.READ` or `.CREATE` | Grant count, type, effective date, reason, employee ID; supporting file object may reference uploaded file |
| Get a grant | `/people/api/v3/leave-tracker/grant/{record_id}` | GET; `ZOHOPEOPLE.leave.READ` | Do not confuse `grant_id`, employee record ID, and leave-type ID |

At least one of `employee_zoho_id`, `employee_mail_id`, or `employee_id` is required when adding a leave request. Prefer the internal Zoho employee ID once resolved, while retaining the business Employee ID as a human-checkable attribute. Dates follow the organization format unless the endpoint explicitly specifies otherwise. For partial days/hours, preserve the documented `days` object, session/count, and start/end-time semantics.

Approval status is workflow state, not merely a writable label. Do not bypass configured approvers with direct form updates. Before submitting a request, discover the employee's policy, applicable leave type and balance, holiday/weekend/shift context, unit, approver rules, and duplicate requests. After submission, read the returned record and monitor its approval outcome. For payroll exports, use the official loss-of-pay report or approved integration contract; never calculate payroll deductions from unapproved requests alone.

Supporting documents can contain medical or other sensitive information. Upload only when required, retain the returned file identity, prohibit prompt/log content extraction by default, and apply HR retention rules.

## 7. Attendance and shift APIs

Attendance is high-consequence operational data. A device punch, attendance entry, regularization request, approved day, and payroll result are different facts.

### Current v3 surface

| Capability | Route | Method / scope | Current published threshold |
|---|---|---|---|
| List attendance entries | `/people/api/v3/attendance/entries` | GET; `ZOHOPEOPLE.attendance.READ` or `.ALL` | 60 requests, then 5-minute lock |
| Get one entry | `/people/api/v3/attendance/entries/{entry_id}` | GET; `ZOHOPEOPLE.attendance.READ` or `.ALL` | 60 / 5 minutes |
| Bulk add entries | `/people/api/v3/attendance/entries` | POST; `ZOHOPEOPLE.attendance.CREATE` or `.ALL` | 10/minute, 100/hour, 1,500/day |
| Add caller punch | `/people/api/v3/attendance/entries/in` or `/out` | POST; `ZOHOPEOPLE.attendance.CREATE` or `.ALL` | 20 / 5 minutes |
| Edit one entry | `/people/api/v3/attendance/entries/{entry_id}` | PUT; `ZOHOPEOPLE.attendance.UPDATE` or `.ALL` | 20 / 5 minutes |
| Delete one entry | `/people/api/v3/attendance/entries/{entry_id}` | DELETE; `ZOHOPEOPLE.attendance.DELETE` or `.ALL` | 20 / 5 minutes |
| Delete employee's day entries | `/people/api/v3/attendance/entries` | DELETE; `ZOHOPEOPLE.attendance.DELETE` or `.ALL` | 20 / 5 minutes |
| Get shift schedules | `/people/api/v3/shift/schedules` | GET; attendance READ/ALL | 60 / 5 minutes |

`[VOLATILE]` Values above are from the linked operation pages at the cutoff, not a product quota. Implement a central limiter keyed by organization, endpoint family, and credential; honor `429`/lock responses; add jitter; never retry an unverified write blindly.

The v3 attendance list accepts employee email, biometric mapper ID, Employee ID, or Zoho employee ID; date range or `last_modified_within`; grouping flags; and offset. Grouping flags change `data` from a list to nested employee/date maps, so parser tests must cover each selected mode. One-entry reads can require `date` when the origin day is outside the current year.

The bulk-add operation takes `punch_details`, a declared `datetime_format`, and optional entry/storage time zones. It may report total, success, and skipped employee information. A `200` response is not proof every row was accepted. Reconcile input count, success count, skipped identities, and subsequent reads. Make device event IDs/idempotency hashes durable, normalize time zones explicitly, and quarantine ambiguous daylight-saving times.

Classic attendance endpoints remain published for individual check-in/out, bulk import, entries, regularization, shift mapping, and shift configuration. They differ in route, parameters, response, and threshold from v3. A new design should prefer the suitable current v3 operation when it covers the use case, but migration must compare behavior rather than merely rename paths.

### Shift controls

`GET /people/api/v3/shift/schedules` accepts one employee selector plus mandatory `from_date` and `to_date`, returning date-indexed shift data. Specific shift-mapping APIs expose assignments. Before calculating absence, overtime, reminder times, or on-call routing, retrieve the employee's actual schedule, location, holiday calendar, and attendance policy. Do not assume every employee uses the organization's default shift.

## 8. Timesheet API and accounting boundaries

The Timesheet API index documents Clients, Projects, Jobs, Time Logs, Timers, Timesheets, and General Settings. Each is its own resource family with CRUD/status/assignment actions. Follow the child operation page for its route, parameters, scope, and threshold.

A robust hierarchy is:

```text
People client -> People project -> People job -> time log -> submitted/approved timesheet
```

Do not collapse these IDs or substitute a CRM account, Books contact, Projects project, or ToDo task ID. Maintain an explicit cross-product mapping table with source product, organization, object type, source ID, target ID, mapping state, and verified time.

Before adding a time log, resolve employee, project, job, billing flag/rate policy, date/time zone, duration, notes classification, and approval ownership. Detect overlap and duplicate imports. Timer start/pause/resume operations are stateful; read current running timer before changing it. Submitting or approving a timesheet can affect billing/payroll and needs a human-controlled rule.

### Books/Invoice integration semantics

Zoho's native People integration maps People Employees to Books Employees, Clients to Contacts, Projects to Projects, Jobs to Tasks, and Time Logs to Time Entries. Current help states that only approved, nonzero time logs are eligible to push. Once pushed, a log cannot be pushed again; later People edits do not update the Books copy. Only one Books or Invoice organization can be connected.

Consequences for GH/Sylvara:

- treat the push as a controlled posting boundary, not live bidirectional sync;
- store People and Books IDs plus the push result/time;
- prevent edits after posting or run an explicit correction workflow in the destination;
- reconcile approved eligible logs, pushed logs, skipped records, and Books entries;
- do not infer billing or payroll completion merely because the People log is approved.

### Projects integration semantics

The native Projects integration can import projects/tasks and push eligible approved People time logs as Projects timesheets for users present in both products. Official help documents asymmetries: deletions may not propagate; re-import can reset People-side changes; task lists and subtasks are not imported; missing destination projects may be created during push subject to confirmation. Design a named direction and correction process instead of calling this a two-way mirror.

## 9. Performance and file APIs

The v3 Performance reference documents library operations for KRAs, competencies, and skills, with operation-qualified `ZOHOPEOPLE.performance.*` scopes. For example, `/api/v3/performance/kra` supports GET, POST, and PUT; GET defaults to up to 200 records and exposes `is_next`, while create payloads currently allow up to twenty KRA objects. The KRA page publishes 20 requests followed by a five-minute lock. Competency and skill operations have their own contracts.

Library definitions are not employee appraisal results. Before writing, distinguish a reusable KRA/competency/skill definition from an employee assignment, goal, review cycle, feedback entry, rating, or finalized appraisal. Validate minimum/maximum ranges and duplicate names. Never let an AI system silently create rating criteria or change completed appraisals.

The v3 file-upload route `/people/api/v3/time-attendance/file` accepts an attachment and returns a `local_file_id` for later calls such as leave grants. The current page lists a 10 MB maximum and 10 requests per five-minute lock, with scope tied to the consuming Leave, Time Tracker, or Attendance operation. The download API has a separate route/permission contract.

For uploads, validate extension and MIME type, scan content, use a safe generated filename, enforce size, record the intended parent workflow, and discard orphan `local_file_id` values after a failed transaction according to policy. For downloads, stream to an authorized sink and never put binary or extracted HR content in general logs or model context.

## 10. Workflow automation and developer space

### Workflow engine

People workflows can use action-based or date-based triggers, criteria, immediate/time-based actions, email alerts, field updates, checklists/tasks, webhooks, custom functions, e-sign flows, and follow-up/TAT behavior depending on service and configuration. Prefer native field updates/alerts/checklists when they fully express the rule; use a custom function or external integration when procedural logic, cross-product calls, durable queuing, or stronger observability is required.

Prevent loops by recording an automation source/version field or external ledger and excluding self-generated changes in workflow criteria. Date triggers must use the organization's time zone and must define behavior for changed, missing, or historical dates. Criteria should be mutually intelligible to HR administrators, not hidden solely in code.

### Webhooks

The current webhook guide describes workflow-associated callbacks, defaulting to POST while configuration may allow GET or POST. It documents up to ten entity fields and five custom parameters, custom headers/authentication, previewed URLs, and workflow logs.

`[DOC-GAP]` The public page does not establish HMAC signatures, ordered delivery, exactly-once delivery, a universal event envelope, or a retry schedule. A safe receiver therefore:

1. exposes HTTPS through an approved gateway and allowlist where feasible;
2. authenticates with a rotated secret header rather than credentials in the query string;
3. assigns a receipt/correlation ID and stores only a redacted payload fingerprint;
4. validates expected source, service/form, event, IDs, and schema;
5. deduplicates using record/event/change keys in a durable store;
6. responds quickly after queueing, then processes asynchronously;
7. fetches the current People record before consequential work;
8. retries transient failures with bounds and a dead-letter queue;
9. runs periodic reconciliation to recover missed or unordered events.

Do not use GET for payloads containing personal data; URLs leak through logs and intermediaries. Do not map more fields than the receiving workflow needs.

### Custom functions, connections, schedulers, and buttons

Custom functions are Deluge programs mapped to workflows and can update People or call approved external services. Use OAuth **Connections** rather than embedded tokens. A connection has a link name used by `invokeUrl`; record the owner, scopes, service, DC, credential mode, consumers, and rotation plan. Connections can use basic, OAuth 1, or OAuth 2 mechanisms as supported, but OAuth 2 and least privilege should be the normal choice.

Custom schedulers run recurring Deluge logic in the supported settings area. Use them for bounded reconciliation or reminders, not as an unbounded ETL engine. Add a cursor, maximum pages/runtime, lock to prevent overlap, checkpoint, alert, and restart behavior. Custom buttons are human-triggered actions and should present clear context; destructive buttons require confirmation and idempotency.

Automation logs cover workflows, custom buttons, and schedulers for supported services. The current log guide states that failed custom functions can be retried for up to ten days and detailed information logs are retained for sixty days. It also says a custom function must return `String`, not `void`, to support retry. Export essential redacted evidence sooner; do not treat UI logs as permanent audit storage.

## 11. Native integrations and ownership rules

| Integration | Officially documented behavior | Engineering consequence |
|---|---|---|
| Zoho CRM | CRM Leads, Accounts, Contacts, and Deals can be imported as People Clients; current help describes a limited mapping such as name/currency and not a general bidirectional edit sync | CRM remains customer/vendor truth; retain source module/record ID and make refresh direction explicit |
| Zoho Books/Invoice | Employees/Clients/Projects/Jobs/approved Time Logs map to destination objects; push has one-way/posting constraints | Reconcile posting and corrections; never overwrite accounting data from People |
| Zoho Projects | Projects/tasks can be imported and eligible approved time logs pushed for shared users; documented omissions/asymmetries exist | Maintain mappings and a re-import policy; do not promise task-list/subtask parity |
| Zoho Sign | E-sign actions can send configured People documents and return signature progress | Sign is evidence of signature; People stores lifecycle context. Verify completion in Sign before downstream access/provisioning |
| Zoho Recruit | Hired candidates can be pushed into People and onboarding workflows | Use Recruit candidate ID plus People employee ID; deduplicate by more than email and define rehire handling |
| Zoho Mail | User/account synchronization can help provision People users depending on setup | HR record, Zoho account, Mail mailbox, app license, and employment status are separate state machines |
| Zoho Analytics | Advanced People Analytics can synchronize People data into Analytics | Official help warns People permissions do not automatically apply in Analytics; rebuild row/column access there |

Before enabling any native integration, document initiating product, destination, direction, eligible records, mapping keys, frequency/manual action, deletion behavior, update behavior, error visibility, replay semantics, and owner. Test create, update, duplicate, rejected/unauthorized, deleted, renamed, and disconnected cases.

## 12. Security, privacy, retention, and resilience

### Access-control stack

People access is layered: account/user status, service access, role, form permission, field permission, record/data visibility, action permission, and organizational hierarchy can all matter. IP restrictions and Zoho account controls add perimeter constraints. Build integrations under a dedicated, named account with the minimum role and OAuth scopes. Test both allowed and denied cases; an admin-token success proves little about an ordinary user's access.

Classify fields before integration. At minimum separate public/internal workforce directory data, confidential HR data, restricted compensation/identity data, medical/accommodation data, performance/disciplinary content, and authentication secrets. Disable broad model retrieval for the restricted classes. Redact `inputData`, webhook bodies, query parameters, filenames, notes, and exception dumps. Encrypt secrets and exported HR data at rest; restrict operator access; establish deletion and legal-hold rules with counsel.

Zoho's GDPR and HIPAA configuration guides describe relevant controls, but enabling a setting does not make GH/Sylvara compliant by itself. Determine controller/processor responsibilities, lawful purpose, consent/notice, data-subject request procedure, breach response, and business-associate requirements. Do not place ePHI into custom fields, webhooks, Analytics, or AI tools unless the approved configuration and agreement cover that flow.

### Audit, backup, and sandbox

The Activity Log provides administrative/user activity for up to six months under the current help contract. Automation detail has the shorter retention described above. Export required audit evidence to an approved immutable destination with field minimization; maintain correlation IDs across People, Catalyst/Flow, and destination systems.

Automatic Data Backup is currently Enterprise-only, permits at most five backups per month, and leaves the last seven available through emailed links. Critically, automatic backup excludes Time Logs, Timesheets, and Attendance; those require manual export. A recovery plan must therefore test form/file restore procedures and separately export operational time data. An emailed download link is not a durable backup repository.

People Sandbox is intended for configuration testing and is plan-dependent. Current help describes configuration-only or configuration plus the first thirty selected records, with sandbox users given team-member access by default. It is not a full anonymized production clone. Use synthetic employees and scrubbed fixtures, retest permissions, and maintain separate OAuth grants for production and sandbox.

### Data-center migration

DC migration is a project, not a DNS switch. The current migration guide states that integrations need reconfiguration; Books/Invoice must be re-enabled; Zoho Connections, web-form links, Blueprints, historical approval/follow-up/TAT records, feeds, WorkDrive-uploaded files, and kiosk configuration have important nonmigration or rebuild behavior. Attendance-device domain/authentication settings must change. Inventory every token, connection, callback, integration, embedded link, file location, and device before migration; freeze changes; export evidence; migrate; reauthorize; rebuild omitted configuration; and run end-to-end reconciliation.

## 13. Observability, error handling, and reconciliation

Every integration run should record, without sensitive payloads:

- environment/DC, client alias, route template, operation, workflow version, and correlation ID;
- typed source/destination IDs or irreversible hashes where IDs are sensitive;
- start/end time, page/cursor, attempted/succeeded/skipped/failed counts, HTTP/API code, retry count, and terminal disposition;
- metadata-manifest version, redacted response schema version, and the actor/approval reference for consequential actions.

Parse both HTTP status and the route's response envelope. Classic APIs can return numeric response status/error codes; v3 APIs commonly return `status`, `message`, `data`, or structured error codes such as permission/no-data errors. Classify failures as authentication, authorization, validation, duplicate/conflict, threshold/lock, transient service, or permanent business rule. Refresh once on a confirmed expired token; never spin on authorization failures.

Reconciliation jobs should compare active employee rosters to authorized identity/app accounts; leave submissions to approval/balance/payroll outcomes; device rows to accepted attendance entries/skips; approved time logs to destination posting records; onboarding/offboarding instances to required tasks/documents/access actions; and webhooks to current People record state. Alert on age and business impact, not merely exception count.

## 14. Testing and release gates

1. **Schema:** snapshot forms/components/views; test renamed display labels, custom required fields, lookups, picklists, nulls, Unicode, and tabular `ROWID` updates.
2. **Identity:** test Employee ID, Zoho employee ID, email changes, duplicate names, rehires, non-user versus invited user, and wrong-organization IDs.
3. **Permissions:** run allowed and denied tests for service/form/field/record/action permissions and a least-privilege OAuth token.
4. **Time:** test organization date format, time zone, daylight-saving transitions, overnight shifts, holidays, partial leave, missing punches, and historical entry reads.
5. **Pagination/limits:** exercise maximum page size, empty/final pages, overlapping `modifiedtime` windows, grouped response shapes, threshold responses, backoff, and restart checkpoints.
6. **Mutation safety:** test duplicate delivery, timeout-after-write, partial bulk success, stale record, workflow re-entry, and re-read verification.
7. **Integrations:** test missing mappings, disconnected destination, renamed/deleted source, already-pushed time log, destination correction, and user absent from one product.
8. **Privacy:** verify redaction, least-data webhook mapping, attachment scanning, secret storage, audit access, retention, and model/tool restrictions.
9. **Recovery:** test token revocation, dead-letter replay, backup retrieval, required manual time exports, sandbox promotion checklist, and documented rollback.
10. **Human controls:** HR approves templates, leave/attendance correction rules, performance logic, offboarding actions, and any AI-assisted decision boundary.

Release only with a current source registry, live metadata manifest, endpoint/scope matrix, named owner, change ticket, test evidence, monitoring, reconciliation, and rollback plan.

## 15. GH Real Estate and Sylvara reference patterns

### Employee onboarding

Recruit or HR approval creates a candidate/employee handoff. Resolve identity and duplicate/rehire state; create the People employee through the supported tenant mode; start the configured onboarding; send governed documents through Sign; provision accounts through the authorized identity path; write only external IDs/statuses back to the lifecycle ledger. Do not activate financial, CRM, WorkDrive, or property-system access merely because an employee record exists. A human verifies screening, required documents, role, manager, start date, and least-privilege access.

### Role or property assignment change

Treat department/designation/manager/location/assigned portfolio changes as a controlled event. Fetch current People state; obtain required approval; update the minimum HR fields; let a queued orchestrator calculate downstream app/team access; require product-specific confirmation; and reconcile. Do not encode property/unit/customer relationships as free-text HR fields when CRM/Creator owns them.

### Attendance device ingestion

Stage device events with device ID, event ID, employee mapper, timestamp, source timezone, and hash. Resolve mapper to one employee; quarantine unknown/ambiguous rows; batch within the v3 limit; compare total/success/skipped counts; read entries back; and route exceptions to HR. Preserve raw device evidence under the approved retention policy, outside prompts and Git.

### Approved time to Books or Projects

Require People approval, nonzero duration, valid mapping, and destination eligibility. Create one posting ledger entry per source time-log/destination pair, invoke the native or API path once, confirm the destination ID, and mark posted. Corrections create an explicit reversal/adjustment workflow because People edits may not update the destination copy.

### Offboarding

An approved exit initiates a checklist, not an immediate blind cascade. Validate effective date/time and legal holds; secure documents; transfer ownership; revoke sessions/tokens/app access through their authoritative systems; update employee state; preserve audit/retention; and reconcile. A failed downstream action remains visible and owned until resolved. Deleting the People employee is normally not the offboarding mechanism.

### HR self-service assistant

Expose a narrow tool set: retrieve the caller's permitted leave balance/request status, explain published policy, create a draft request, or list the caller's tasks. Do not expose broad employee search, compensation, medical, performance, or document download. Resolve the authenticated person server-side, enforce People permissions, show a confirmation before mutation, and cite the resulting People record ID/status. Generated policy answers must point to the approved policy source and disclose uncertainty.

## 16. Implementation checklist

- [ ] Confirm company/entity, People organization, production/sandbox, subscription, DC, time zone, date format, and HR owner.
- [ ] Define People versus CRM/Books/Projects/Recruit/Sign/WorkDrive/Creator/Catalyst authority boundaries.
- [ ] Inventory services, forms, components, views, workflows, Blueprints, connections, integrations, devices, and custom functions.
- [ ] Build a versioned live metadata manifest; classify every approved field.
- [ ] Register a least-privilege OAuth client/connection and store secrets outside code.
- [ ] Record exact endpoint page, method, content type, scope, response envelope, pagination, and threshold per operation.
- [ ] Implement typed ID mappings, pagination, overlap/deduplication, idempotency, re-read verification, and bounded retries.
- [ ] Authenticate webhooks, minimize fields, queue quickly, reconcile, and test duplicates/out-of-order delivery.
- [ ] Configure redacted operational logs, business reconciliation, alerts, dead-letter handling, and audit export.
- [ ] Test least-privilege permissions, time-zone/date edge cases, partial bulk success, integration asymmetry, and token revocation.
- [ ] Establish backup/manual exports for excluded time data and test recovery.
- [ ] Obtain HR/security/legal approval for sensitive fields, retention, e-sign, AI use, and consequential workflows.

## 17. Known research gaps and verification queue

- `[DOC-DRIFT]` Classic, v2, and v3 APIs coexist; endpoint samples sometimes differ in path prefix or scope singular/plural. Confirm every chosen route in the target DC.
- `[VOLATILE]` Subscription features, API add-ons/daily allowances, service availability, and thresholds vary by edition/region and can change. The live subscription and endpoint/usage UI win.
- `[DOC-GAP]` No general public contract establishes global idempotency keys, ETags/optimistic concurrency, webhook signatures, delivery ordering, or exactly-once behavior for all People operations.
- `[LIVE-DISCOVERY]` GH/Sylvara's actual forms, fields, custom services, workflows, leave policies, shifts, roles, employee types, mappings, connected organizations, retention policy, and integration status are not defined by public docs.
- `[DOC-GAP]` Not every UI service has equivalent public CRUD APIs. Check the current index before designing direct integration for Compensation, Cases, LMS, Engagement, documents, or other UI-only behavior.
- `[VOLATILE]` Zia capabilities and regional availability change. Permission-aware access does not authorize sharing restricted HR data with an AI workflow; review the current Zia/privacy page and company policy.

## 18. Official source registry

### Platform, authentication, metadata, and employee records

- [People API v3 overview](https://www.zoho.com/people/api/v3/overview.html)
- [OAuth concepts](https://www.zoho.com/people/api/oauth.html)
- [OAuth token steps](https://www.zoho.com/people/api/oauth-steps.html)
- [OAuth token validity v3](https://www.zoho.com/people/api/v3/oauth-tokenvalidity.html)
- [OAuth scope index v3](https://www.zoho.com/people/api/v3/scopes.html)
- [People services and features](https://www.zoho.com/people/features.html)
- [Settings and services overview](https://help.zoho.com/portal/en/kb/people/administrator-guide/settings/overview/articles/new-settings)
- [API appendix and identifiers](https://www.zoho.com/people/api/appendix.html)
- [Fetch forms](https://www.zoho.com/people/api/forms-api/fetch-forms.html)
- [Fetch form components](https://www.zoho.com/people/api/forms-api/get-field-forms.html)
- [Fetch form views](https://www.zoho.com/people/api/fetch-view.html)
- [Default and custom views](https://www.zoho.com/people/api/default-custom-views.html)
- [Insert a form record](https://www.zoho.com/people/api/insert-records.html)
- [Update a form record](https://www.zoho.com/people/api/update-records.html)
- [Get bulk form records](https://www.zoho.com/people/api/bulk-records.html)
- [Fetch records](https://www.zoho.com/people/api/fetch-record.html)
- [Search form records](https://www.zoho.com/people/api/forms-api/search-record.html)
- [Get record count](https://www.zoho.com/people/api/get-record-count.html)
- [Get a related/single record](https://www.zoho.com/people/api/forms-api/get-single.html)
- [Add employees](https://www.zoho.com/people/api/adding-employees.html)
- [Trigger onboarding](https://www.zoho.com/people/api/onboarding.html)

### Leave, attendance, shifts, time, performance, and files

- [List leave requests v3](https://www.zoho.com/people/api/v3/leave-tracker/get-leave.html)
- [Add leave request v3](https://www.zoho.com/people/api/v3/leave-tracker/add-leave.html)
- [Get one leave request v3](https://www.zoho.com/people/api/v3/leave-tracker/specificleave.html)
- [Edit leave request v3](https://www.zoho.com/people/api/v3/leave-tracker/edit-leave.html)
- [Delete leave request v3](https://www.zoho.com/people/api/v3/leave-tracker/delete-leave.html)
- [List leave grants v3](https://www.zoho.com/people/api/v3/leave-tracker/grant.html)
- [Add leave grant v3](https://www.zoho.com/people/api/v3/leave-tracker/add.html)
- [Loss-of-pay report](https://www.zoho.com/people/api/leave/reports/loss-of-pay.html)
- [Get attendance entries v3](https://www.zoho.com/people/api/v3/attendance/entries.html)
- [Get one attendance entry v3](https://www.zoho.com/people/api/v3/attendance/entries/get-specific.html)
- [Bulk-add attendance entries v3](https://www.zoho.com/people/api/v3/attendance/entries-bulk-add.html)
- [Classic check-in/check-out](https://www.zoho.com/people/api/attendance-checkin-checkout.html)
- [Get shift schedules v3](https://www.zoho.com/people/api/v3/shift/get-schedules.html)
- [Timesheet API index](https://www.zoho.com/people/api/timesheet.html)
- [Add a Timesheet project](https://www.zoho.com/people/api/timesheet/adding-projects.html)
- [Get KRA library v3](https://www.zoho.com/people/api/v3/performance/kra-get.html)
- [Add KRA library entries v3](https://www.zoho.com/people/api/v3/performance/kra-add.html)
- [Edit KRA library entries v3](https://www.zoho.com/people/api/v3/performance/kra-edit.html)
- [Add competencies v3](https://www.zoho.com/people/api/v3/performance/competency-add.html)
- [Edit skills v3](https://www.zoho.com/people/api/v3/performance/skills-edit.html)
- [Upload time/attendance files v3](https://www.zoho.com/people/api/v3/time-attendance/fileupload.html)
- [Download files v3](https://www.zoho.com/people/api/v3/files/download-file.html)

### Automation, security, administration, and integrations

- [Workflow automation](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/workflow-zoho-people)
- [Webhooks](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/webhooks-zoho-people)
- [Custom functions](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/custom-functions-zoho-people)
- [Connections](https://help.zoho.com/portal/en/kb/people/administrator-guide/settings/developer-space/articles/connections-zoho-people)
- [Custom schedulers](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/custom-schedulers)
- [Custom buttons](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/custom-buttons-in-zoho-people)
- [Automation logs](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/workflow-logs)
- [Developer Space](https://help.zoho.com/portal/en/kb/people/administrator-guide/settings/developer-space/articles/developer-space-zoho-people)
- [User access control](https://help.zoho.com/portal/en/kb/people/administrator-guide/settings/manage-accounts/articles/user-access-control-zoho-people)
- [Permissions](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/setting-up-permissions-zoho-people)
- [IP restrictions](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/ip-restrictions-zoho-people)
- [Activity Log](https://help.zoho.com/portal/en/kb/people/administrator-guide/operations/data-administration/articles/activity-log-zoho-people)
- [Data Backup](https://help.zoho.com/portal/en/kb/people/administrator-guide/operations/data-administration/articles/data-backup-zoho-people)
- [Sandbox](https://help.zoho.com/portal/en/kb/people/administrator-guide/operations/data-administration/articles/sandbox)
- [GDPR compliance guide](https://help.zoho.com/portal/en/kb/people/administrator-guide/compliance/articles/gdpr-compliance-2025)
- [HIPAA configuration guide](https://help.zoho.com/portal/en/kb/people/administrator-guide/common-settings/articles/hipaa-compliance-with-zoho-people-compliance)
- [Data-center migration](https://help.zoho.com/portal/en/kb/people/administrator-guide/compliance/articles/data-center-migration-2025)
- [Books integration](https://help.zoho.com/portal/en/kb/people/administrator-guide/marketplace/zoho-integrations/articles/zoho-books-integration-with-zoho-people)
- [CRM integration](https://help.zoho.com/portal/en/kb/people/administrator-guide/marketplace/zoho-integrations/articles/zoho-crm-integration-with-zoho-people)
- [Projects integration](https://help.zoho.com/portal/en/kb/people/administrator-guide/marketplace/zoho-integrations/articles/zoho-projects-integration-zp)
- [Sign integration](https://help.zoho.com/portal/en/kb/people/administrator-guide/marketplace/zoho-integrations/articles/zoho-sign-integration-with-zoho-people)
- [Mail integration](https://help.zoho.com/portal/en/kb/people/administrator-guide/marketplace/zoho-integrations/articles/zoho-mail-integration-with-zoho-people)
- [Recruit integration](https://help.zoho.com/portal/en/kb/people/administrator-guide/marketplace/zoho-integrations/articles/zoho-people-integration-with-zoho-recruit)
- [Advanced People Analytics](https://help.zoho.com/portal/en/kb/people/administrator-guide/marketplace/zoho-integrations/articles/advanced-people-analytics)
- [Zia chatbot and permission behavior](https://help.zoho.com/portal/en/kb/people/administrator-guide/zia-zoho-people/articles/zia-chat-bot-zoho-people)
