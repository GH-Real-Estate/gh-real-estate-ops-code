# Zoho ToDo Task, API, and AI-Agent Knowledge Base

**Document ID:** GH-ZOHO-TODO-KB
**Research cutoff:** 2026-07-20
**Audience:** ChatGPT, Codex, solution architects, integration engineers, and GH Real Estate / Sylvara system owners
**Evidence policy:** Current official Zoho documentation only. Live Zoho Mail/ToDo configuration, account permissions, IDs, task schemas, subscription entitlements, and regional endpoints remain authoritative.

## 1. AI retrieval and execution contract

Use this document to identify the correct supported surface and design safe task workflows. It is not a substitute for live authorization or metadata discovery.

### Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `[OFFICIAL]` | Directly supported by a linked Zoho source at the research cutoff | Recheck the endpoint page before implementation |
| `[LIVE-DISCOVERY]` | IDs, memberships, settings, or behavior must come from the authorized account | Fetch and validate; never infer |
| `[VOLATILE]` | Plan, availability, limits, UI, AI tooling, or integration behavior can change | Verify immediately before release |
| `[DOC-GAP]` | The public reference does not establish a contract for the capability | Do not invent a field, endpoint, event, or guarantee |
| `[DESIGN]` | GH/Sylvara engineering guidance derived from official behavior | Validate against current business requirements |

### Non-negotiable rules

1. **Zoho ToDo does have a supported programmatic surface.** Its documented REST surface is the **Zoho Mail Tasks API**, under regional `mail.zoho.*` hosts and `ZohoMail.tasks` OAuth scopes. Do not invent a separate `todo.zoho.*` REST base URL or a `ZohoToDo.*` scope.
2. Treat `taskId`, `zgid`, `projectId`, custom-status ID, Zoho user ID (`zuid`), `accountId`, and `messageId` as opaque identifiers. Discover them with the documented read operations.
3. Distinguish native ToDo tasks from CRM, Projects, People, Desk, and Connect tasks shown in **Unified View**. A unified display does not move ownership of those records into ToDo.
4. Never place access tokens, refresh tokens, MCP URLs/API keys, customer information, employee details, tenant data, unpublished business plans, or confidential attachment content in Git, prompts, fixtures, URLs, PDFs, or broad logs.
5. A task is not proof that a lease was signed, rent was paid, a ledger entry posted, a maintenance Case was resolved, or an employee action was approved. Verify the authoritative product before closing consequential work.
6. GET before PUT or DELETE. Confirm group, owner, assignee, current status, and task ID; then change the smallest documented field. Re-read after every mutation.
7. Soft-delete by default. The Tasks API supports moving a task to trash and a separate permanent-delete option. Permanent deletion requires explicit authorization and evidence.
8. Zoho Mail Developer Space documents UI-configured **outgoing webhooks for task activities** and incoming webhooks that can create a task in a selected Streams group. These are Mail webhook surfaces, not Tasks REST subscription endpoints. Do not invent a REST webhook route or delivery guarantee; verify signatures, deduplicate, and reconcile.
9. AI tools may propose or execute task actions only with least-privilege tools, explicit target resolution, idempotency controls, and human confirmation for destructive or externally consequential changes.

## 2. Product boundary and authority ladder

`[OFFICIAL]` Zoho describes Tasks powered by Zoho ToDo as part of the Zoho Mail Suite. Users can work in Zoho Mail's Tasks area or the standalone Zoho ToDo interface. The product supports personal tasks, Streams-group tasks, subtasks, recurring work, reminders, priorities, collaboration, and multiple views.

For GH Real Estate and Sylvara, ToDo is best treated as a lightweight internal action layer, not a universal workflow database.

| Concern | Authoritative system | ToDo's appropriate role |
|---|---|---|
| Leads, applicants, tenants, properties, units, vendors, and leasing pipeline | Zoho CRM | Personal/group follow-up task linking back to the canonical record |
| Maintenance request state and resident-visible status | CRM Cases or the approved Creator workflow | Staff reminder or checklist item; never the ticket master |
| Invoices, payments, balances, credits, refunds, and accounting close | Books/Billing/payment provider | Reminder to review or reconcile, with no financial truth stored in status |
| Contracts and signatures | Contracts/Sign | Follow-up reminder; verify authoritative execution state before completion |
| Employee HR processes | Zoho People | Convenience view or internal task; People remains the HR record |
| Long-running project delivery with dependencies, milestones, timesheets, and formal issue tracking | Zoho Projects or another approved project system | Unified View and small ad hoc actions, not a replacement project engine |
| Files and governed evidence | WorkDrive or the product designated by retention policy | Link or small collaboration attachment only |
| Cross-product integration, secrets, queues, retries, and reconciliation | Catalyst / approved integration layer | Destination or presentation layer for bounded task commands |

### Use ToDo when

- the work is a human-owned action with a clear title, assignee, start/due expectation, priority, reminder, or recurrence;
- collaboration fits a personal scope or an existing Streams group;
- missing the action is operationally inconvenient but the task status does not itself change a legal, accounting, tenant, or employee system of record;
- a user benefits from one Unified View across Zoho task-producing applications.

### Use another product when

- the process needs field-rich intake, row-level external portal access, approvals, SLAs, blueprints, or a durable domain model;
- dependencies, milestones, budgets, issues, time logs, or release planning make it a project rather than a task list;
- the work is a maintenance ticket, HR request, contract, payment, or other regulated record;
- a public customer or tenant needs access. ToDo collaboration is organization/group oriented and is not the GH tenant portal.

## 3. Task model and permissions

### Personal and group namespaces

`[OFFICIAL]` Personal tasks normally belong to the owner and are visible to the owner and assignee. Invitees can be added so they can view, like, and comment. Group tasks require a Streams group; group members can view, track, like, and comment, subject to role and task settings.

REST routes encode this boundary:

```text
Personal: /api/tasks/me
Group:    /api/tasks/groups/{zgid}
```

Never transform one into the other by changing a URL segment without resolving the authorized namespace and membership.

### Main objects

| Object | Documented identity | What must be discovered |
|---|---|---|
| Personal namespace | `me` route | Authorized Zoho account and current task settings |
| Streams task group | `zgid` | Group ID, name, owner, moderators, members, and task availability |
| Task | `taskId` | Namespace, owner, assignee, title, status, project, dates, recurrence, and current version/state |
| Subtask | Its own task ID plus parent relationship | Parent task, group/personal namespace, assignee, and restore behavior |
| Project in Tasks API | `projectId` | Project list for the selected group and current name |
| Custom status | Status ID | Status name, color, position, scope, creator/permissions, and whether still in use |
| Member/assignee | Zoho user ID (`zuid`) | Current user identity and group membership/authorization |
| Email link context | `accountId` and `messageId` | Authorized mail account and message from Mail APIs |

`[DOC-GAP]` The UI documentation refers to **categories**, while the REST reference exposes group **projects** and `projectId`. Do not assume every UI category is interchangeable with an API project. Discover both in the live account and prove mapping in a noncritical test.

### Role behavior

The current UI help documents different edit rights for group admin, task owner, parent-task assignee, subtask assignee, group member, and organization member assignee. Group membership grants visibility and collaboration, not universal edit authority. Invitees can interact with the one shared task but do not thereby receive access to every group task.

`[VOLATILE]` Paid-plan UI documentation currently permits up to five assignees on a task. The public REST create/update reference documents a singular `assignee` user ID. Do not send an undocumented assignee array. If multiple assignees are required, confirm current API support with a live contract test or use the UI.

### UI capabilities that are not automatically API fields

The UI help documents start dates, due dates, priorities, reminders, recurring tasks, subtasks, categories, labels, custom statuses, custom fields, attachments, comments, likes, invitees, task timeline, publishing, board/list views, archives, and multiple assignees. The public task API does not expose all of those in its create/update contract. API clients must implement only fields listed on the operation page.

Particularly:

- custom fields can be created for a personal or group task scope in the UI, but no general custom-field metadata/write contract appears in the public Tasks API index;
- labels are described as personal organization and are not visible to other task viewers; do not treat them as a shared workflow state;
- published task links are view-only and can be scoped internally, to specified users, or publicly to a logged-in Zoho user, with optional expiry. A link is still sensitive access material;
- attachments are visible to group members, assignees, and invitees who can see the task. Do not attach resident, employee, financial, or contract documents merely for convenience.

## 4. Authentication, scopes, regions, and transport

### OAuth

`[OFFICIAL]` Zoho Mail REST APIs require a valid OAuth token and account permissions. Send the access token in the header:

```http
Authorization: Zoho-oauthtoken <access_token>
Accept: application/json
```

Task scopes follow the current operation pattern:

| Scope | Capability |
|---|---|
| `ZohoMail.tasks.READ` | Retrieve tasks, groups, members, projects, and custom statuses |
| `ZohoMail.tasks.CREATE` | Create tasks, projects, or custom statuses |
| `ZohoMail.tasks.UPDATE` | Update and restore tasks; edit projects/statuses |
| `ZohoMail.tasks.DELETE` | Delete tasks, projects, or custom statuses |
| `ZohoMail.tasks.ALL` | Full Tasks API access; avoid unless truly required |

The shorter family name `ZohoMail.tasks` appears in the API index, while endpoint pages specify operation-qualified forms. Use the exact scope shown by the current endpoint and OAuth consent screen.

`accountId`/message-linked tasks can require identifiers obtained from Mail account/message APIs, which have separate scopes such as `ZohoMail.accounts.*` and `ZohoMail.messages.*`. Do not broaden a Tasks-only integration to mailbox read access unless the approved workflow needs it.

### Regional API bases

Use the Mail host corresponding to the authorized account:

| Data center | Base API host |
|---|---|
| United States | `https://mail.zoho.com` |
| Europe | `https://mail.zoho.eu` |
| India | `https://mail.zoho.in` |
| Australia | `https://mail.zoho.com.au` |
| Japan | `https://mail.zoho.jp` |
| Canada | `https://mail.zohocloud.ca` |
| China | `https://mail.zoho.com.cn` |
| United Arab Emirates | `https://mail.zoho.ae` |
| Saudi Arabia | `https://mail.zoho.sa` |

Keep the regional host in environment configuration. Never accept it as an arbitrary user-supplied URL. Zoho's getting-started page directs users to identify the DC from their Mail login URL.

### Request and response conventions

- Task create/update bodies are JSON unless the endpoint says otherwise.
- The delete-task endpoint documents form parameters for `forceDelete`.
- A typical response has `status.code`, `status.description`, and `data`; list responses may include `data.paging.nextPage`.
- Validate the HTTP status **and** the response wrapper. A parseable body is not proof of successful mutation.
- Do not log authorization headers or full task bodies. Task descriptions, linked messages, assignees, and attachments can contain confidential data.

## 5. Live discovery sequence

Before enabling writes, generate a sanitized manifest using documented reads:

1. `GET /api/tasks/groups` to list groups where tasks exist and obtain `zgid` values.
2. `GET /api/tasks/groups/{zgid}/members` to resolve authorized member IDs.
3. `GET /api/tasks/groups/{zgid}/projects` to discover API project IDs.
4. `GET /api/tasks/groups/{zgid}/customStatus` and `GET /api/tasks/me/customStatus` to discover status IDs/names.
5. Read a known non-sensitive task from each approved namespace to capture actual response shape.
6. Confirm the authenticated account, region, scope, group membership, permissions, and subscription features.

Example sanitized manifest:

```yaml
verified_at: "2026-07-20T00:00:00Z"
mail_dc: us
api_host: "https://mail.zoho.com"
authorized_subject: "<service-account-alias>"
groups:
  - purpose: "sylvara-internal-operations"
    zgid: "<opaque-live-id>"
    moderators_verified: true
    projects:
      - purpose: "client-onboarding-actions"
        project_id: "<opaque-live-id>"
    custom_statuses:
      - semantic_key: "waiting_internal"
        status_id: "<opaque-live-id>"
write_policy:
  allow_personal: false
  allowed_group_purposes: ["sylvara-internal-operations"]
  permanent_delete: false
```

Do not store names, email addresses, real task titles/descriptions, message IDs, attachment paths, or tokens in this manifest.

## 6. REST endpoint catalog

All paths are relative to the correct regional Mail host.

### Read operations

| Operation | Method and path | Important parameters/behavior |
|---|---|---|
| List personal tasks | `GET /api/tasks/me` | `limit` 1–499, default 20; `from` pagination |
| List group tasks | `GET /api/tasks/groups/{zgid}` | Same pagination; optional documented status filters |
| Tasks assigned to caller | `GET /api/tasks/?view=assignedtome&action=view` | `from`, `limit`; user-context result |
| Tasks created by caller | `GET /api/tasks/?view=createdbyme&action=view` | `from`, `limit`; user-context result |
| Get one task | `GET /api/tasks/me/{taskId}` or `GET /api/tasks/groups/{zgid}/{taskId}` | Namespace must match the task |
| List subtasks | `GET .../{taskId}/subtasks` | Parent namespace and ID required |
| List task groups | `GET /api/tasks/groups` | Returns group ID, name, owner/moderators, member count |
| List group members | `GET /api/tasks/groups/{zgid}/members` | Use returned IDs for assignee validation |
| List projects | `GET /api/tasks/groups/{zgid}/projects` | Returns project IDs and names |
| List tasks in project | `GET /api/tasks/groups/{zgid}/projects/{projectId}` | Supports documented pagination/status filters |
| List custom statuses | `GET /api/tasks/me/customStatus` or group equivalent | Returns status ID, name, color, and position where present |

Always follow `data.paging.nextPage` or advance the documented `from` cursor until exhausted. Deduplicate by task ID. Preserve `modifiedTime` for reconciliation, but do not assume it is an immutable event sequence.

### Create task

```http
POST /api/tasks/groups/{zgid}
POST /api/tasks/me
Content-Type: application/json
```

The documented payload supports:

- required `title`;
- `description`;
- wire `status`: `inprogress` or `completed`;
- wire `priority`: `high`, `medium`, or `low`;
- `projectId`, `parentTaskId`, and singular `assignee`;
- `dueDate` in `DD/MM/YYYY`;
- `reminderDate` in ISO 8601 plus `emailReminder`/`popupReminder`;
- `accountId` and `messageId` for an email-linked task;
- recurrence fields;
- attachment store-name/path arrays where supported by the linked upload workflow.

The endpoint permits nested `subtask` data, but `[DESIGN]` creating a parent first and then explicit subtasks yields better per-operation evidence and retry control. A retry after a timeout can duplicate a task because the public contract does not document an idempotency key. Keep an application ledger keyed by business event and intended task purpose; search/reconcile before retrying.

### Update task

The same task route accepts `PUT` operations. Official pages document focused changes:

| Change | JSON key | Contract notes |
|---|---|---|
| Title | `title` | Non-empty intended title |
| Description | `description` | Treat content as visible to everyone with task access |
| Priority | `priority` | `high`, `medium`, `low` |
| Status | `status` | Current endpoint documents `inprogress` and `completed` |
| Project | `projectId` | Must belong to the applicable group |
| Assignee | `assignee` | Singular Zoho user ID in current public page |
| Due date | `dueDate` | `DD/MM/YYYY` |
| Absolute reminder | `reminderDate`, `emailReminder`, `popupReminder` | ISO 8601; at least one reminder channel true |
| Due-relative reminder | `reminderDueDate`, channel booleans | Positive number of days before due date |
| Recurrence | `recurringType`, `recurringFrequency`, pattern fields | Daily/Weekly/Monthly/Yearly; coupled fields must be sent together |

Do not use one broad payload merely because the route is shared. Send the minimal documented keys, then GET and compare the resulting state.

### Recurrence rules

The documented model supports:

- `recurringType`: `Daily`, `Weekly`, `Monthly`, or `Yearly`;
- positive `recurringFrequency`;
- optional `recurFrom`, `recurUntil`, or `recurFor`;
- weekday-only daily recurrence;
- weekly day 1–7, with 1 as Sunday;
- monthly day-of-month or week/day combinations;
- yearly day/month or week/day/month combinations, with months 0–11.

Validate calendar edge cases such as the 29th–31st, leap years, daylight-saving transitions, user timezone, and edits after an occurrence exists. The official field constraints do not establish a business catch-up policy.

### Projects and custom statuses

```text
POST   /api/tasks/groups/{zgid}/projects
GET    /api/tasks/groups/{zgid}/projects
PUT    /api/tasks/groups/{zgid}/projects/{projectId}
DELETE /api/tasks/groups/{zgid}/projects/{projectId}

POST   /api/tasks/{me|groups/{zgid}}/customStatus
GET    /api/tasks/{me|groups/{zgid}}/customStatus
PUT    /api/tasks/{me|groups/{zgid}}/customStatus
DELETE /api/tasks/{me|groups/{zgid}}/customStatus
```

Project creation uses `projectName`. Custom-status creation uses `statusName` and optional color. Custom status IDs, not labels alone, are the stable discovery artifact. The documentation says users can delete only custom statuses they created; predefined statuses cannot be deleted.

`[DOC-GAP]` The current project-edit and project-delete child pages contradict their own samples and the Tasks API index: their formal method blocks say `POST`, and the edit block omits `{projectId}`, while the index and sample cURL use the `PUT` and `DELETE` routes shown above. Treat those two project mutations as requiring a target-DC contract test before use; do not silently select one conflicting fragment.

### Delete and restore

```text
DELETE /api/tasks/me/{taskId}
DELETE /api/tasks/groups/{zgid}/{taskId}
PUT    /api/tasks/me/{taskId}/restore
PUT    /api/tasks/groups/{zgid}/{taskId}/restore
```

`forceDelete=false` (and omission) moves the task to trash; `forceDelete=true` permanently deletes it. Restore returns a trashed task to its prior category. Restoring a deleted parent also restores its deleted subtasks, while restoring a subtask alone makes it an independent parent task. Build tests for this behavior before automating cleanup.

## 7. Official MCP surface for ChatGPT and Codex

`[OFFICIAL]` Zoho provides an official Zoho Mail MCP server. Its current tool catalog includes ToDo operations such as:

- `listPersonalTasks`, `addPersonalTask`, `editPersonalTask`, `deletePersonalTask`;
- `addGroupTask`, `editGroupTask`, `deleteGroupTask`;
- `getSubtasksForPersonalTask`, `getSubtasksForGroupTask`;
- personal-task category list/create tools.

The catalog separately marks `getMailAccounts` and `getAccountDetails` as common tools required for all user actions. At the cutoff, its task table does not list a general group-task listing tool; do not invent a `listGroupTasks` MCP tool or treat the REST `GET` route as an MCP tool. Recheck the live catalog before designing target discovery.

This is the preferred supported route when an authorized AI client needs natural-language access and the required tools are available. It is not a reason to grant every Mail tool.

### Safe MCP configuration

1. Create a workflow-specific MCP server and select only required task tools.
2. Prefer read tools first. Add create/update tools only after target-resolution tests.
3. Omit delete tools unless the workflow explicitly requires controlled cleanup.
4. Treat the generated MCP URL/API key as a secret; rotate it if exposed.
5. Review OAuth scopes and user permissions. MCP tools act within the authorized account's permissions.
6. Use separate connections for personal and company contexts when confusion is possible.
7. Require a confirmation summary containing group, task title, assignee, due date, and intended action before writes.
8. Record the tool name, sanitized inputs, result ID, timestamp, and approval reference in an external audit ledger.

Zoho's official documentation says the Mail MCP works with task tools and can be configured with ChatGPT and other MCP clients. Availability in a particular ChatGPT/Codex surface remains `[VOLATILE]`; verify the current client and organization policy before relying on it.

## 8. Automation, integration, and synchronization

### Supported non-API creation paths

The UI can create a task from selected text, an email, Smart Create, or a task-specific email address pattern. These are human conveniences, not guaranteed integration APIs. Email-to-task cheatsheet addresses can create personal/group tasks and encode a due date. Do not expose those addresses publicly or use them as an unauthenticated replacement for the REST API.

`[OFFICIAL]` Zoho Mail Developer Space also documents an incoming-webhook format that can create a task in a selected Streams group. A group owner or moderator configures it and receives a generated URL. Treat that URL as a secret, scope the receiving group deliberately, and do not present this Mail/Streams webhook as a personal-task REST endpoint.

### Unified View

Unified View can show tasks from ToDo, CRM, Projects, People, Desk, and Connect after relevant integrations are enabled. Changes made to an integrated product task can be reflected in that source product. Therefore:

- retain a composite identity of `{source_product, source_org, source_record_id}`;
- never assume a task displayed in ToDo can be mutated through the Zoho Mail Tasks REST route;
- send a CRM task change through CRM APIs, a Projects task change through Projects APIs, and so forth unless an official Unified View contract explicitly supports the operation;
- reconcile task status with the source system after edits.

### Import and migration

The UI supports CSV import and documented imports from Trello, Google Tasks, and Microsoft To Do, with different mapping boundaries. Imports are migration operations, not ongoing two-way synchronization. Test mapping of boards/lists/categories, assignees, dates, recurrence, comments, attachments, statuses, and closed items with synthetic records before migration.

### Outgoing task webhooks and polling

`[OFFICIAL]` Zoho Mail Developer Space can configure an outgoing webhook with **Tasks** as the entity and selected task activities as triggers. The current UI offers two task-selection modes: activities in groups where the configuring user is an owner/moderator, or activities on tasks assigned to or followed by that user. Each configuration can select at most three groups. A limited-data option omits fields such as description, category, priority, parent task, and status name.

This is a UI-configured Mail webhook, not a subscription route in the public Tasks REST API. The official webhook guide says the first setup POST must receive `200`, an unresponsive destination can cause automatic disablement, and requests carry `X-Hook-Signature`. Capture the first request's `X-Hook-Secret` securely and verify the Base64 HMAC-SHA256 signature over the unmodified request body before parsing. The public page does not establish a unique event ID, ordered or exactly-once delivery, or a retry schedule.

For a supported webhook design:

1. Select the smallest approved group/activity set and enable the limited-data payload unless more fields are required.
2. Authenticate the raw request before parsing; never log the hook secret, signature, full description, names, or group details.
3. Deduplicate by a durable fingerprint that includes the task `entityId`, action, and normalized payload; then fetch current task state before consequential work.
4. Queue quickly, return the required success response, and alert if the configuration is disabled or deliveries stop.
5. Run bounded REST polling as reconciliation, or as the primary method when the webhook's group/user selection model does not cover the approved namespace.
6. When polling, paginate fully, store task ID plus normalized `modifiedTime` and a content hash, back off on failures, and alert on paging or permission drift.

## 9. Security, privacy, retention, and observability

### Access and content controls

- Personal tasks are not necessarily private once assigned or invited.
- Group tasks are visible to group members; invitees can gain task-specific visibility.
- Task descriptions and attachments are visible to users with task access.
- Labels are described as owner-private organization, while categories are visible with the task.
- Published links can broaden view access; use expiry and the narrowest audience, and inventory/revoke links.
- A group moderator/admin role can change practical visibility and edit rights. Reconcile membership under joiner/mover/leaver controls.

Never include full Social Security numbers, bank details, payment credentials, medical data, immigration documents, lease packages, identity documents, access codes, or tenant complaints in a task. Store sensitive evidence in the governed authoritative system and put only a minimal reference in ToDo.

### Observability

For every automated mutation, record outside the task body:

```json
{
  "operation_id": "<generated-id>",
  "actor": "<service-principal-alias>",
  "namespace": "group:<purpose>",
  "target_task_id_hash": "<hash>",
  "operation": "update_status",
  "before": {"status": "inprogress"},
  "after": {"status": "completed"},
  "http_status": 200,
  "response_status": "success",
  "verified_by_get": true,
  "timestamp": "<UTC>"
}
```

Do not log task description, attachment paths, email content, access tokens, MCP URLs, or user email addresses. Use request correlation IDs in your integration layer even though the Tasks API does not document accepting them.

### Limits and plan behavior

The current task list endpoints document up to 499 results per call and a default of 20. The UI marks multiple assignees as paid-plan functionality and attachments under 10 MB. The general Mail API reference says plan and user/admin permissions affect API availability.

`[DOC-GAP]` The public Tasks API pages reviewed for this cutoff do not publish a task-specific daily call quota or concurrency budget. Do not interpret that as unlimited. Capture real rate-limit responses, implement bounded concurrency and backoff, and confirm contractual limits with the tenant and Zoho support before high-volume use.

## 10. Testing and release gates

Use a dedicated test group with synthetic users and no customer/employee production data.

### Contract tests

- OAuth READ/CREATE/UPDATE/DELETE scopes independently.
- Every configured regional host.
- Group, member, project, and custom-status discovery.
- Pagination at 20 and near 499, including empty and final pages.
- Personal versus group route isolation.
- Create with minimum fields and with due date/reminder/recurrence.
- Wire values for priority and status, including invalid values.
- Update one field at a time and verify with GET.
- Timezone and `DD/MM/YYYY` date handling.
- Recurrence around month-end, leap year, and DST.
- Soft delete, restore, parent/subtask restore behavior, and explicitly approved permanent delete.
- Duplicate retry after a simulated timeout.
- Revoked token, expired token, removed group membership, nonmember assignee, wrong `zgid`, and wrong DC.
- MCP tool selection, target resolution, user confirmation, and least privilege.
- Outgoing-webhook signature validation, duplicate delivery handling, limited-data mode, receiver outage/disablement, and REST reconciliation.

### Release gates

1. Live discovery manifest reviewed without confidential content.
2. Each write use case has an owner, source event, idempotency key, and rollback/reconciliation procedure.
3. A read-only dry run shows exact proposed group, assignee, title, due date, and source-system link.
4. Task closure logic verifies the authoritative record for financial, legal, resident, or HR work.
5. Alerts cover auth failures, paging failures, repeated retries, unexpected group/member changes, and reconciliation drift.
6. Delete tools and `forceDelete=true` are disabled unless separately approved.

## 11. GH Real Estate and Sylvara patterns

### GH Real Estate

Good ToDo patterns include internal reminders to review a showing follow-up, reconcile an approved repair invoice, prepare a move-in packet, or review a renewal. Each task should link to the canonical CRM/Books/Contracts/Creator record using a non-secret URL or internal reference. Closing the ToDo item must not update authoritative business state without a separate verified workflow.

Avoid creating one ToDo task per tenant event when CRM workflows, Cases, Bookings, or Creator already own the process. Duplicate task swarms create ambiguous completion and expose resident context to group members.

### Sylvara

Use a controlled group for lightweight client-onboarding and founder operations. When work grows into deliverables, dependencies, releases, bugs, or time tracking, move ownership to the repository/issue tracker or Zoho Projects and use Unified View for convenience.

### Recommended task template

```text
Title: <verb> <object> — <non-sensitive reference>
Description:
Purpose: <why this action exists>
Authority: <CRM/Books/Contracts/People/etc. record link>
Completion evidence: <specific check in authoritative system>
Do not include: secrets, full personal data, or document contents
Owner: <resolved Zoho user ID>
Due: <business deadline with timezone>
```

## 12. Implementation checklist

- [ ] Confirm whether the work belongs in ToDo or another system.
- [ ] Confirm Mail/ToDo region and authorized account.
- [ ] Request only required `ZohoMail.tasks.*` scopes.
- [ ] Discover group, members, projects, statuses, and sample response shape.
- [ ] Store a sanitized purpose-to-ID manifest.
- [ ] Build pagination, response-wrapper validation, redaction, backoff, and reconciliation.
- [ ] Add idempotency before create.
- [ ] GET before and after update/delete.
- [ ] Default deletes to trash; disable permanent deletion.
- [ ] Verify authoritative state before completing consequential tasks.
- [ ] If using Mail outgoing webhooks, verify `X-Hook-Signature`, protect `X-Hook-Secret`, minimize the payload, and reconcile through REST reads.
- [ ] Test user/group permission removal and DC mismatch.
- [ ] If using MCP, enable only required tools and protect the MCP URL.
- [ ] Recheck plan and API behavior before production rollout.

## 13. Explicit research gaps

As of the cutoff, the reviewed official public documentation does not establish:

- a separate Zoho ToDo REST hostname or `ZohoToDo.*` OAuth scope;
- a public Tasks REST endpoint for creating webhook subscriptions or a durable change-stream API;
- a documented unique webhook event ID, delivery ordering, exactly-once semantics, or retry schedule for Mail outgoing task webhooks;
- an idempotency-key header for task creation;
- ETag or optimistic-concurrency semantics;
- a task-specific daily API quota/concurrency table;
- a public API contract for every UI feature, including all custom fields, labels, comments, likes, invitees, publishing, timeline, start date, and multiple assignees;
- guaranteed mapping between current UI categories and API `projectId` objects;
- guaranteed event ordering or incremental modified-since feed;
- a complete retention/eDiscovery specification for task bodies and attachments in the Tasks API pages.

Treat each as unknown until current official documentation, live behavior, or Zoho support establishes a contract.

## 14. Official source registry

### Product and UI

- [Zoho ToDo product page](https://www.zoho.com/todo/)
- [Tasks powered by Zoho ToDo](https://www.zoho.com/mail/help/tasks.html)
- [Adding tasks, custom fields, email creation, and imports](https://www.zoho.com/mail/help/adding-tasks.html)
- [Managing, publishing, archiving, and deleting tasks](https://www.zoho.com/mail/help/manage-tasks.html)
- [Import and export tasks](https://www.zoho.com/mail/help/import-tasks.html)
- [Unified View](https://www.zoho.com/mail/help/unified-view.html)
- [Zoho Projects integration](https://www.zoho.com/mail/help/zoho-projects-integration.html)
- [Zoho Mail Streams](https://www.zoho.com/mail/help/streams.html)
- [Zoho Mail incoming and outgoing webhooks, including task activities and signature validation](https://www.zoho.com/mail/help/dev-platform/webhook.html)

### REST API

- [Zoho Mail API index](https://www.zoho.com/mail/help/api/)
- [Tasks API index](https://www.zoho.com/mail/help/api/task-api.html)
- [Mail REST API getting started, regional hosts, and error handling](https://www.zoho.com/mail/help/api/getting-started-with-api.html)
- [Mail REST response codes](https://www.zoho.com/mail/help/api/response-codes.html)
- [Add a group or personal task](https://www.zoho.com/mail/help/api/post-add-new-task.html)
- [Get group or personal tasks](https://www.zoho.com/mail/help/api/get-all-group-or-personal-tasks.html)
- [Get a specific task](https://www.zoho.com/mail/help/api/get-single-task.html)
- [Get subtasks](https://www.zoho.com/mail/help/api/get-subtasks.html)
- [Get assigned tasks](https://www.zoho.com/mail/help/api/get-tasks-assigned-to-me.html)
- [Get tasks created by the caller](https://www.zoho.com/mail/help/api/get-tasks-created-by-me.html)
- [Get task groups](https://www.zoho.com/mail/help/api/get-group-details.html)
- [Get task-group members](https://www.zoho.com/mail/help/api/get-group-member-details.html)
- [Create a group project](https://www.zoho.com/mail/help/api/post-add-new-project.html)
- [Get group projects](https://www.zoho.com/mail/help/api/get-projects-in-group.html)
- [Get project tasks](https://www.zoho.com/mail/help/api/get-tasks-in-project.html)
- [Edit a group project](https://www.zoho.com/mail/help/api/put-edit-tasks-project.html)
- [Delete a group project](https://www.zoho.com/mail/help/api/delete-tasks-project.html)
- [Change task status](https://www.zoho.com/mail/help/api/put-change-task-status.html)
- [Change task assignee](https://www.zoho.com/mail/help/api/put-change-task-assignee.html)
- [Change task priority](https://www.zoho.com/mail/help/api/put-change-task-priority.html)
- [Set a task reminder](https://www.zoho.com/mail/help/api/put-change-task-reminder.html)
- [Set a due-relative reminder](https://www.zoho.com/mail/help/api/put-change-task-reminder-by-due-date.html)
- [Set task recurrence](https://www.zoho.com/mail/help/api/put-change-recurring-task-details.html)
- [Get custom statuses](https://www.zoho.com/mail/help/api/get-custom-status-of-task.html)
- [Add a custom status](https://www.zoho.com/mail/help/api/add-custom-status-to-task.html)
- [Edit a custom status](https://www.zoho.com/mail/help/api/edit-custom-status-of-task.html)
- [Delete a custom status](https://www.zoho.com/mail/help/api/delete-custom-status-of-task.html)
- [Delete a task](https://www.zoho.com/mail/help/api/delete-group-or-personal-task.html)
- [Restore a deleted task](https://www.zoho.com/mail/help/api/restore-deleted-task.html)

### AI-agent access

- [Official Zoho Mail MCP overview](https://www.zoho.com/mail/help/mcp/getting-started.html)
- [Zoho Mail MCP task-tool catalog](https://www.zoho.com/mail/help/mcp/zoho-mail-mcp-tools.html)
- [Configure a Zoho MCP server](https://www.zoho.com/mail/help/mcp/mcp-server-configuration.html)
- [Connect Zoho Mail MCP with ChatGPT](https://www.zoho.com/mail/help/mcp/mcp-chatgpt.html)
- [Use multiple services in one MCP server](https://www.zoho.com/mail/help/mcp/multiple-services-single-server.html)
