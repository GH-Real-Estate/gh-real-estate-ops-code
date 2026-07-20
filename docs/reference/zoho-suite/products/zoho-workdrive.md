# Zoho WorkDrive Engineering and Automation Knowledge Base

**Document ID:** GH-ZOHO-WORKDRIVE-KB  
**Program:** GH Real Estate / Sylvara systems knowledge base  
**Research cutoff:** 2026-07-20  
**Primary audience:** ChatGPT, Codex, architects, records/security administrators, and maintainers  
**Source policy:** Official Zoho WorkDrive API, help, pricing, and release documentation plus supplied GH system maps  
**Evidence labels:** `DOC-VERIFIED`, `LIVE-METADATA REQUIRED`, `TENANT-SPECIFIC`, `VOLATILE`, `GH-POLICY`, `DESIGN RECOMMENDATION`, `DOC-GAP`

> **AI ingestion directive.** Zoho WorkDrive is GH/Sylvara's controlled content and collaboration layer—not CRM, a contract lifecycle manager, a signature authority, an accounting ledger, or GitHub. Use immutable WorkDrive resource IDs, team/team-folder identity, exact live permissions, version/checksum evidence, and data-center-aware OAuth. Never route or deduplicate by filename/folder label alone. Never place tenant documents, signed agreements, identity records, exports, external-share links, OAuth credentials, custom-app secrets, or production webhook payloads in GitHub, prompts, or logs. Before every write, resolve legal entity, WorkDrive team, space/team folder, parent resource ID, classification, owner, allowed membership/share policy, duplicate/version behavior, retention, and source-system operation key.

## 1. Retrieval contract for AI agents

### 1.1 Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `DOC-VERIFIED` | Supported by an official source in the registry | Revalidate critical implementation details in the live API Explorer |
| `LIVE-METADATA REQUIRED` | ID, capability, permission, custom field, template, team, or folder is tenant generated | Retrieve it from the intended account/DC and preserve exact value |
| `TENANT-SPECIFIC` | Depends on plan, team, role, policy, classification, workflow, or source system | Resolve before design and code |
| `VOLATILE` | Plan storage, file size, API/webhook/function quota, feature availability | Verify immediately before implementation/procurement |
| `GH-POLICY` | Constraint from the supplied GH architecture/change-control documents | Treat as binding until approved change |
| `DESIGN RECOMMENDATION` | Engineering/records-control guidance inferred from behavior | Confirm with security, legal, records, and business owners |
| `DOC-GAP` | Not published as one stable universal contract in reviewed docs | Do not guess; use the current explorer, controlled test, response headers, or Zoho support |

### 1.2 Non-negotiable rules

1. Resolve the WorkDrive team and legal entity before a file/folder/share operation; reject ambiguous or user-supplied routing.
2. Persist resource IDs and relationships. Names and paths can change and are not unique.
3. Define overwrite/version/keep-both/skip behavior explicitly. Never let a default silently replace controlled evidence.
4. Treat every upload/download/share/webhook payload as untrusted. Validate type, size, signature, checksum, malware status, classification, and authorization.
5. Do not use GitHub as a document repository. Git may contain only sanitized schemas, automation source, tests, manifests, and checksums that reveal no tenant data.
6. External sharing is an access grant, not merely a URL. Require approved recipient/scope/expiry/password/download policy and revocation owner.
7. Webhook receipt is not proof that a file is final, complete, safe, or archived. Verify signature, deduplicate, retrieve state, and reconcile.

## 2. System boundary and content ownership

`GH-POLICY` WorkDrive owns controlled business documents and evidence such as property records, approved leases/signature packets, inspection evidence, maintenance attachments, operational policies, and retained exports. It should not own a second editable copy of facts whose authority belongs elsewhere.

| Information/artifact | Authority | WorkDrive representation |
|---|---|---|
| Lead/contact/property/unit/application/status | CRM | Folder/file IDs and links, not duplicate operational database |
| Contract clauses, negotiation, lifecycle, executed status | Contracts | Controlled final/approved file copy; Contracts remains lifecycle authority |
| Signing status and completion certificate | Sign | Completed PDF/certificate archived with Sign IDs/checksum |
| Invoices/payments/credits/ledger | Books/Billing | Approved rendered/export evidence; finance system remains accounting truth |
| Tenant portal/UI | Creator/Sites | Authorized view/download through backend; no raw broad share |
| Source code/configuration | GitHub | No controlled tenant documents or credentials |

### 2.1 Space selection

WorkDrive includes private/user space and team/shared structures. Business automation should use an approved Team Folder/controlled shared location, not an employee's personal folder. Team Folder roles generally determine whether a user can organize, edit/upload, comment/view, or administer. Exact names and privileges are `LIVE-METADATA REQUIRED`.

`DESIGN RECOMMENDATION` A Team Folder should align to durable governance (legal entity or controlled function), while property/unit/tenant records live underneath. Do not create a new Team Folder for every record unless membership/policy boundaries genuinely require it.

## 3. Plans, storage, and volatile entitlements

`VOLATILE` The public pricing page at the cutoff lists Starter, Team, and Business, with a minimum of three users and plan-dependent shared storage, upload size, recovery, workflows, data templates/custom fields, DLP/classification, audit, external sharing, custom apps, APIs, and integrations.

The reviewed snapshot advertised:

| Plan | Shared storage example | Added storage/user example | Team maximum example | Max file upload example |
|---|---:|---:|---:|---:|
| Starter | 1 TB/team up to 10 users | 100 GB | 20 TB | 10 GB |
| Team | 3 TB/team up to 10 users | 300 GB | 60 TB | 50 GB |
| Business | 5 TB/team up to 10 users | 500 GB | 100 TB | 250 GB |

These are current commercial figures, not permanent API constants. A product plan's maximum file size is distinct from the single-request API upload threshold. The official API explorer describes ordinary single-request upload for files up to 250 MB, while chunked/resumable upload supports larger files subject to current plan/API rules. Verify both limits and current storage before every large-file design.

The individual plan is not a substitute for a governed business team because ownership, continuity, controls, shared policy, and administrative audit matter.

## 4. OAuth, data centers, scopes, and principals

### 4.1 Authentication

WorkDrive APIs use Zoho OAuth 2.0 and the header:

```http
Authorization: Zoho-oauthtoken <access_token>
```

Use a managed server-side OAuth client or Zoho Connection. Record owner, scopes, team, region, environment, rotation/revocation, and dependent automation. A token acts with the authorized user's effective permissions; scope does not bypass team-folder membership or role.

### 4.2 API domain

Official examples use:

```text
https://www.zohoapis.com/workdrive/api/v1
```

`TENANT-SPECIFIC` Use the OAuth response's current `api_domain` and correct regional Accounts domain. Zoho services operate in multiple DCs, and the exact WorkDrive API host suffix must be resolved rather than synthesized. Do not hardcode `.com`, or guess `.ca` versus `zohocloud.ca`.

### 4.3 Scope model

Official API/help examples include granular scopes such as:

```text
WorkDrive.users.READ
WorkDrive.files.READ
WorkDrive.files.CREATE
WorkDrive.files.UPDATE
WorkDrive.files.DELETE
WorkDrive.teamfolders.READ
WorkDrive.teamfolders.CREATE
WorkDrive.teamfolders.UPDATE
```

The exact scope names and operations must come from the current endpoint in the official API Explorer. Separate read/indexing, upload, metadata/classification, sharing, and administrative connections where practical. Never grant broad delete/team-folder administration merely because an upload example uses it.

### 4.4 Principal and ownership hazard

Automation run by an individual can fail or lose access when that user is deactivated, removed from a Team Folder, or changes role. Use an approved durable integration owner, document business ownership, and test access after personnel/role changes. Do not transfer ownership based on email string without resolving the live WorkDrive member identity.

## 5. Resource and identifier model

| Resource | Identifiers/relationships | Implementation rule |
|---|---|---|
| User | ZUID/user ID, team-member ID, team relationship | Distinguish Zoho user identity from membership record |
| Team | team ID, name, role/membership | Legal-entity and governance boundary |
| Team Folder | resource ID, team ID, name, status, membership/role | Controlled shared root; route by ID |
| Folder | resource ID, parent ID, team/team-folder relationship | Path is presentation; parent relationship is authority |
| File | resource ID, parent, name/extension, version, size, timestamps, creator/modifier | Persist ID, checksum/version and authoritative source references |
| Version | version ID/number, creator/time/size | Do not confuse latest version with original evidence |
| Permission/share | permission/share ID, target, role, expiry/settings | Revoke/update by ID; review external scope |
| External link | link ID/token, access settings, expiry | Sensitive bearer capability; never log or store in GitHub |
| Comment/activity | resource/user/timestamp/action identity | Operational collaboration/audit, not necessarily legal record |
| Custom field/data template | generated field/template IDs, type/options | Discover live schema; do not infer from label |

`DESIGN RECOMMENDATION` Maintain a cross-reference:

```text
legal_entity | source_system | source_record_id | document_kind/version
workdrive_team_id | team_folder_id | parent_folder_id | resource_id
content_sha256 | workdrive_version_id | classification | archive_state
created_at | last_verified_at
```

Names/paths may be included for supportability but never as the primary key.

## 6. API response and request conventions

WorkDrive v1 responses use a JSON:API-like resource model, commonly:

```json
{
  "data": {
    "type": "<resource-type>",
    "id": "<resource-id>",
    "attributes": {},
    "relationships": {},
    "links": {}
  }
}
```

Collection responses use a `data` array. Attributes and relationships are endpoint-specific; never assume an attribute is present because another resource returned it. Preserve string IDs exactly—do not coerce large numeric-looking identifiers into floating-point numbers.

The Explorer uses query conventions including bracketed pagination such as `page[limit]` for some operations. `DOC-GAP` There is not one safely inferred paging/search contract across all endpoints. Follow each operation's current parameter table and returned navigation/meta/links.

## 7. Verified endpoint anchors and API capability map

### 7.1 Exact anchors verified in official material

The API Explorer and official CRM-integration guidance document the following patterns:

| Operation | Method/path | Notes |
|---|---|---|
| Current WorkDrive user | `GET /workdrive/api/v1/users/me` | Returns authorized user identity |
| User's teams | `GET /workdrive/api/v1/users/{zuid}/teams` | Resolve team IDs before routing |
| Create Team Folder | `POST /workdrive/api/v1/teamfolders` | Privileged; scope `WorkDrive.teamfolders.CREATE` in example |
| Create folder | `POST /workdrive/api/v1/files` | Parent resource supplied; scope/role required |
| Upload file | `POST /workdrive/api/v1/upload` | Multipart; documented query includes filename, parent ID, duplicate behavior |
| Download server file | documented under `/apidocs/v1/filesfolders/downloadserverfile` | Retrieve exact request path/parameters from live Explorer |
| Get Team Folder info | documented under `/apidocs/v1/teamfolder/getteamfoldersinfo` | Retrieve exact operation contract from Explorer |

Official upload examples use parameters such as:

```text
filename=<encoded-name>
parent_id=<resolved-resource-id>
override-name-exist=true
```

Do not copy `override-name-exist=true` casually: it can update/replace/version an existing name depending on current API semantics. Use an explicit per-document-kind collision policy and compare existing resource/source/checksum first.

### 7.2 API capability families

The official API Explorer organizes operations for:

- users, teams, members, and groups;
- Team Folders and membership/roles;
- files and folders: create, list/detail, upload, download, copy, move, rename/update, trash/restore/delete;
- versions and content replacement;
- sharing, permissions, collaborators, and external links;
- comments/activity and search/listing;
- large-file chunk upload.

`LIVE-METADATA REQUIRED` Exact method/path, arguments, scope, role, response attributes, and availability must be copied from the current Explorer at implementation time. This dossier intentionally does not invent endpoints that the dynamic official documentation did not expose reliably in static retrieval.

### 7.3 Discovery sequence

1. Call `/users/me`; retain ZUID and verify expected integration principal.
2. List teams and select an allowlisted team ID for the legal entity.
3. Retrieve Team Folder information and membership/role.
4. Resolve the intended root/team-folder and parent folder IDs.
5. Inspect existing child resources by ID/name and source cross-reference.
6. Retrieve applicable data template/custom-field/classification/share policy.
7. Perform the least-privilege operation.
8. Retrieve the resource and verify parent, version/checksum/size/classification/access.

## 8. Folder creation and deterministic hierarchy

Folder provisioning must be idempotent:

1. acquire `folder_operation_key = <entity>:<source-system>:<source-record-id>:<folder-role>`;
2. check the cross-reference for an existing resource ID;
3. retrieve it and verify team, parent, type, and nontrashed state;
4. if absent, list/search only within the approved parent, matching the governed source key—not merely display name;
5. create once and persist returned ID;
6. apply approved classification/metadata/membership;
7. retrieve and reconcile.

Suggested hierarchy, adjusted for privacy and legal-entity boundaries:

```text
<Legal Entity Team Folder>/
  Properties/<CRM Property ID>/
    Governance/
    Units/<CRM Unit ID>/
      Applications/<Application ID>/
      Leases/<Contract ID>/
      Inspections/<Inspection ID>/
      Maintenance/<Case ID>/
```

Do not put full tenant names, SSNs, bank details, allegations, health/disability data, or access codes in folder/file names because names leak into search, sync, notifications, audit, and links. Use opaque source IDs plus a user-facing title inside authorized systems.

## 9. Upload, chunk upload, versions, and download

### 9.1 Ordinary upload

Official API material describes `/upload` for a single-request upload and notes only members with sufficient Team Folder roles—such as admins, organizers, and editors—can upload. Validate:

- allowed parent/team and caller role;
- filename normalization and extension allowlist;
- declared and detected MIME type;
- file signature/magic bytes;
- size and decompression/archive policy;
- checksum before and after upload;
- malware/quarantine result;
- existing resource/collision policy;
- classification, custom fields, retention, and share state.

`DESIGN RECOMMENDATION` Upload untrusted intake into a quarantined restricted folder, scan/inspect it, then move or copy the approved resource into its controlled final parent.

### 9.2 Chunk/resumable upload

Official 2025 WorkDrive release material describes chunked uploads as resumable and suitable for very large files up to the account's plan cap, which can be as high as 250 GB in the current Business pricing snapshot. Follow the Explorer's live protocol for initiating, uploading ordered chunks, completing/committing, aborting, and resuming.

Persist upload-session ID, resource/parent, total size, chunk size/count, completed part indexes/checksums, source checksum, expiry, attempts, and final resource ID. Never create parallel sessions for the same operation without reconciliation. On completion, retrieve size/version/checksum metadata and compare.

### 9.3 Versions and duplicate names

Current WorkDrive release notes describe duplicate handling choices: update existing with a newer version, keep both, or skip. Select by document class:

| Artifact | Default recommendation |
|---|---|
| Executed lease/sign certificate | Create immutable versioned artifact; never overwrite original evidence |
| Working policy/template | Update as new WorkDrive version after approval |
| Identical integration replay | Skip after matching source ID + SHA-256 |
| Different content under same name | Block/review or keep both with governed version label |

### 9.4 Download

Authorize against resource ID and current user/business purpose, then stream server-to-server. Validate content type, length, checksum, and malware handling. Avoid buffering huge files in constrained Deluge functions. Do not expose OAuth-backed raw download URLs to a browser; use the product's authorized share/download surface or a short-lived application proxy permitted by architecture.

## 10. Sharing, permissions, and external links

Treat access changes as high-risk writes. Resolve the target user/group/member ID and current resource inheritance before adding/removing/updating a permission.

Minimum share record:

```text
resource_id | permission/share_id | principal_type/id
role | external/internal | download_allowed | expiry
password/auth policy | business purpose | approver | revoked_at
```

Controls:

- Prefer internal groups/Team Folder membership over ad hoc per-file shares.
- Apply least privilege and shortest practical expiry.
- Disable public/anonymous links for tenant, applicant, contract, identification, finance, and property-access records unless explicitly approved.
- Do not embed static external links in Sites, CRM email templates, source code, or long-lived messages.
- Periodically enumerate external shares and orphaned permissions; revoke when case/lease/vendor relationship ends.
- Test inherited permissions before placing sensitive content in a folder.
- Moving a file can change its effective access; re-evaluate permissions/classification after move/copy.

`VOLATILE` Advanced external-sharing controls, whitelisted domains, DLP, classification, device/app management, and audit features depend on current plan/edition.

## 11. Webhooks and custom apps

### 11.1 Availability and quotas

Official help currently describes custom-app webhooks for Business plan, with administrators/super administrators able to configure them. The reviewed snapshot publishes:

| Item | Current documented value |
|---|---:|
| Custom apps per team | 10 |
| Webhooks per custom app | 10 |
| Webhook calls per day | 50,000 |
| Trial | 1 custom app / 2 webhooks |

`VOLATILE` Verify current account/plan and whether the daily limit is team/app-wide before capacity design.

### 11.2 Events and payload

Documented trigger families cover file events (view, download, trash/restore/delete, move, rename, comments, internal/external sharing changes) and folder events (create, copy, move, upload/download, rename, trash/restore/delete, share/external-link changes and file events within), plus Team Folder/team events.

Payload `data[]` items include documented structures/fields such as:

- `resource_info`, `share_info`, `association_info`;
- `event_id`, `event_type`, `event_time`, `event_by`;
- `app_key`, `webhook_id`, `portal_id`, `team_id`, and `type`.

Use `event_id` for deduplication when present and preserve resource/team IDs. Unknown event types must route to observation/review, not a destructive default.

### 11.3 Signature verification

WorkDrive sends `X-ZWDWebhook-Signature`. Official help describes an HMAC-SHA256, JWS-like value composed of encoded header, payload, and signature segments. Verify the exact current algorithm/encoding example from the setup article and:

1. capture raw body and signature header before parsing;
2. enforce body/content-type/size limits;
3. reconstruct exactly as documented with the custom-app secret;
4. compare in constant time;
5. reject invalid signature without processing;
6. deduplicate `event_id`, enqueue, then retrieve authoritative resource state.

All webhooks in a custom app share the app secret according to current help. Rotate with coordinated dual/controlled deployment and test every dependent webhook. Never put the secret or signed raw payload in logs/GitHub.

### 11.4 Reconciliation architecture

Webhook events can be duplicate, delayed, reordered, omitted after quota/configuration failure, or report transient state. Maintain periodic API reconciliation for critical archive/share states, and alert on webhook silence, invalid HMAC, unknown event, disabled app, quota exhaustion, retrieval failure, unapproved external share, deletion, or parent move.

## 12. Workflows, custom functions, and connections

`DOC-VERIFIED` WorkDrive custom functions use Deluge, are created by administrators, run as workflow actions, and use Connections for OAuth-backed external services. Current help documents:

- maximum 50 custom functions per team;
- `void` functions only;
- arguments of string/integer types;
- execution with the workflow creator/configured connection's permissions;
- approximately one-minute execution time;
- 10 MB response size;
- 200,000 executed statements/lines;
- 1,000 email sends/day;
- 50,000 webhook GET/POST calls/day;
- 5 MB file download/process limit.

`VOLATILE` Verify all limits and plan access; release material currently describes custom functions/connections for Business and Zoho One.

### 12.1 Safe function design

- Keep the workflow action small: validate event/resource IDs, write a durable operation record, call a queue/service, and exit.
- Do not process large PDFs/images/ZIPs inside the 5 MB/one-minute function boundary.
- Use named Connections, not embedded tokens.
- Pass only IDs and non-sensitive classification, not full document content.
- Make functions idempotent by event/resource/version/operation key.
- Retrieve resource state before write and after it.
- Fail closed and route to review if permissions, team, classification, or parent differ.

## 13. Rate limits, errors, retries, and concurrency

`DOC-GAP` The reviewed official public API Explorer/help does not publish one global WorkDrive REST request-per-minute or concurrency budget. Do not borrow limits from CRM/Sign/Creator. Inspect current operation documentation, response headers, plan/admin material, and obtain Zoho confirmation for high-volume jobs.

- Handle `401` by controlled refresh once; persistent auth errors require reauthorization.
- Treat `403` as scope/membership/role/policy failure, not transient retry.
- Treat `404` cautiously: wrong team/DC/ID, inaccessible resource, or deletion may be indistinguishable; reconcile authorization and audit.
- Treat `409`/duplicate/collision as a branch requiring explicit version/keep/skip policy.
- Retry `429`, transport failure, and selected `5xx` with capped exponential backoff/jitter and `Retry-After`.
- Do not retry create folder, upload commit, share, move, delete, or restore after ambiguous timeout until retrieving/reconciling.
- Serialize writes to one resource/parent/operation key and use version/precondition data when the endpoint supports it.

No universal API idempotency header was identified. Use operation records, content hashes, source cross-references, and retrieve-before-retry.

## 14. Security, privacy, audit, recovery, and retention

Official product material advertises encryption at rest using 256-bit AES, TLS/SSL with PFS in transit, 2FA, administrative audit, DLP/classification, external/whitelisted-domain controls, device/app management, and certifications/compliance claims. These are plan/configuration claims, not proof that GH/Sylvara's tenant is configured correctly.

- Enforce MFA, least privilege, group-based membership, separate legal-entity teams where required, and periodic access reviews.
- Define classification for public, internal, confidential, restricted, legal-record, and sensitive-personal content.
- Configure DLP/external sharing/download/sync policy by class and verify it with tests.
- Inventory desktop/mobile sync and unmanaged devices; local synchronized copies affect deletion/retention risk.
- Preserve WorkDrive activity/admin audit and application integration evidence; alert on destructive/share changes.
- Current Business material advertises recovery up to 120 days; `VOLATILE`. Recovery window is not backup, legal hold, or guaranteed immutable retention.
- Define retention, record freeze/legal hold, deletion authority, restoration testing, export portability, and incident response.
- Encrypt and access-control any backup/export; never place it in GitHub or an AI knowledge PDF.

## 15. GH Real Estate and Sylvara patterns

### 15.1 Property/unit hierarchy provisioning

On approved CRM property/unit creation, a backend resolves legal entity -> WorkDrive team/team folder, locks source ID, creates/finds the opaque-ID folder, applies classification/custom fields, persists WorkDrive ID to the cross-reference/CRM, and retrieves to verify. Renaming a property changes display metadata, not the WorkDrive identity.

### 15.2 Signed agreement archive

1. Verified Sign/Contracts completion provides request/contract IDs and authenticated download.
2. Download to quarantined processing; validate PDF/ZIP, size, checksum, document count, certificate, malware.
3. Resolve the contract's approved property/unit/tenant archive folder by IDs.
4. Upload as an immutable governed artifact; collision requires source ID + checksum comparison.
5. Apply legal-record classification/retention and no external share by default.
6. Persist WorkDrive resource/version/checksum in Contracts/CRM integration record.
7. Reconcile access and archive completeness; delete temporary processing copy under policy.

### 15.3 Maintenance/inspection intake

Creator/CRM stores case/inspection authority; attachments enter a restricted quarantine folder with source case/inspection ID. Scan/classify, then move to controlled location. Avoid public anonymous WorkDrive links in Sites. When a vendor needs access, share the minimum specific folder/file to the resolved vendor principal with expiry and audit.

### 15.4 Finance exports

Books/Billing remains authoritative. Store approved close/report exports in a finance-restricted Team Folder with period, organization ID, report definition, generated timestamp, checksum, approver, and retention. Do not treat the static export as the live ledger.

## 16. Testing and change control

### 16.1 Minimum test matrix

- OAuth wrong DC, token refresh/revocation, scope, team membership/role;
- `/users/me`, teams, team-folder selection, ambiguous same-name resources;
- folder get-or-create, concurrent duplicate, rename/move/trash/restore;
- upload new/update version/keep both/skip and ambiguous timeout;
- 250 MB single-request boundary, chunk resume/out-of-order/duplicate/expired session, plan max;
- filename/MIME/signature/path characters, malware, archive bomb, zero-byte, checksum mismatch;
- classifications/custom fields/data templates and inheritance;
- internal group share, external user/link, expiry/password/download, revocation and move inheritance;
- webhook valid/invalid HMAC, duplicate/out-of-order/unknown event, quota/silence, resource retrieval;
- custom function timeout/5 MB/permission/connection/retry behavior;
- deleted/renamed/deactivated user, orphaned connection, Team Folder owner change;
- final archive/download/restore and cross-system reconciliation.

### 16.2 Deployment packet

Include legal-entity/team/folder map, sanitized IDs and metadata hash, classification/retention/access decisions, OAuth scopes/principal, workflow/function/webhook configuration, source and tests, canary, observability, collision/retry policy, recovery/rollback, and post-deploy evidence. A Git commit does not prove WorkDrive configuration is deployed.

Rollback must avoid deleting user content. Prefer disabling automation/webhooks, revoking new share grants, restoring prior configuration/version, quarantining misrouted files, and reconciling impacted resource IDs. Deletion requires explicit authority and recovery evidence.

## 17. Anti-patterns

- Using a filename or path as immutable identity.
- Creating business archives in an employee's private folder.
- Hardcoding the US `zohoapis.com` host.
- Assuming scopes override Team Folder role.
- Always setting `override-name-exist=true`.
- Processing huge documents in a one-minute/5 MB Deluge function.
- Uploading directly from public intake into the final trusted folder.
- Exposing external links in Sites/GitHub/logs or leaving them without expiry.
- Treating a webhook as authoritative without HMAC/API retrieval.
- Retrying move/share/upload commit/delete blindly after timeout.
- Assuming 120-day recovery is backup/legal hold.
- Storing signed agreements or tenant records in GitHub.

## 18. Preflight checklist

- [ ] Legal entity, WorkDrive DC, team, Team Folder, parent resource, plan/storage verified.
- [ ] Durable OAuth principal, exact least-privilege scopes, connection rotation/revocation tested.
- [ ] Immutable source/operation key and WorkDrive cross-reference exist.
- [ ] Filename/path minimization, document class, classification, retention, legal hold, archive owner approved.
- [ ] Duplicate/version/collision policy and content-hash verification defined.
- [ ] Upload/chunk limits, malware/quarantine, downloads and temporary-file deletion tested.
- [ ] Membership/inheritance/internal/external share policy and periodic review configured.
- [ ] Webhook custom app, HMAC secret, event dedupe, queue, reconciliation, quotas and health alerts tested.
- [ ] Custom function limits/connections and failure queue tested.
- [ ] Rollout/canary, recovery/rollback, incident response and post-deployment evidence approved.

## 19. Unknowns and live-verification requirements

The following are intentionally unresolved rather than guessed:

- one global REST API rate/concurrency budget;
- one pagination/search/error schema for every resource family;
- a universal idempotency or ETag/precondition header;
- exact current regional API domains—use OAuth `api_domain`;
- all resource `type`, attribute, relationship, and role enum values;
- account-generated team, team-folder, file/folder, user/member, permission/share, custom-field/template IDs;
- exact chunk-session protocol, expiry, part sizing, and current maximum;
- plan-specific recovery, DLP, workflow, custom-app, external-share, audit, and retention behavior;
- whether a webhook includes every event necessary for a given control.

Use the current official API Explorer, live sanitized metadata, controlled tests, response headers, and Zoho support.

## 20. Official source registry

All sources accessed and verified 2026-07-20.

### API documentation

- WorkDrive API Overview / Explorer — https://workdrive.zoho.com/apidocs/v1/overview
- File and Folder Sharing / Upload — https://workdrive.zoho.com/apidocs/v1/filefoldersharing
- Chunk Upload — https://workdrive.zoho.com/apidocs/v1/chunkupload
- Download Server File — https://workdrive.zoho.com/apidocs/v1/filesfolders/downloadserverfile
- Get Team Folder Info — https://workdrive.zoho.com/apidocs/v1/teamfolder/getteamfoldersinfo
- Official CRM–WorkDrive Extension Pointers (OAuth scopes and endpoint examples) — https://help.zoho.com/portal/en/community/topic/extension-pointers-for-integrating-zoho-crm-with-zoho-products-8-upload-and-manage-zoho-workdrive-folders-and-files-from-within-zoho-crm

### Webhooks, functions, and automation

- Setting Up Webhooks Using Custom Apps — https://help.zoho.com/portal/en/kb/workdrive/integrations/webhooks/articles/setting-up-webhooks-in-workdrive-using-custom-apps
- Webhook Trigger Events — https://help.zoho.com/portal/en/kb/workdrive/integrations/webhooks/articles/webhooks-trigger-events-available-in-workdrive
- Working with Custom Functions — https://help.zoho.com/portal/en/kb/workdrive/custom-functions-connections/articles/working-with-custom-functions-in-workdrive
- Custom Apps — https://www.zoho.com/workdrive/custom-apps.html
- Workflows in WorkDrive — https://www.zoho.com/workdrive/digest/workflows-in-workdrive.html
- What's New in WorkDrive — https://www.zoho.com/workdrive/whats-new.html
- Introducing Chunk Uploads — https://www.zoho.com/workdrive/digest/introducing-chunk-uploads-in-zoho-workdrive.html

### Plans and security

- WorkDrive Pricing — https://www.zoho.com/workdrive/pricing.html
- WorkDrive Plan Comparison — https://www.zoho.com/workdrive/plan-comparison.html
- WorkDrive Individual Plan — https://www.zoho.com/workdrive/individual-plan.html
- WorkDrive Cloud Storage / Security and Recovery — https://www.zoho.com/workdrive/cloud-storage.html
- WorkDrive 6.0 Enterprise Content Management — https://www.zoho.com/workdrive/intelligent-enterprise-content-management-6.html
