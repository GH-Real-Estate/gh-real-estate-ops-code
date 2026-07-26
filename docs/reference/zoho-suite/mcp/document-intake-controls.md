# Zoho MCP Document Intake Controls

**Document ID:** GH-ZOHO-MCP-DOCUMENT-INTAKE

**Verified:** July 25, 2026

**Scope:** Current MCP capability and gap review for GH Real Estate rental applications, inspections, condition reports, leases, WorkDrive filing, CRM projection, and Catalyst-assisted processing.

## Evidence Status

- `LIVE-INVENTORY`: Exact server identifiers, OAuth display, and advertised tool names from the sanitized July 25 Codex MCP snapshot.
- `REPO-VERIFIED`: Current governed CRM module/field maps and system boundaries in this repository.
- `DOC-VERIFIED`: Capability supported by current official Zoho documentation or Zoho's official WorkDrive OpenAPI repository.
- `ACCEPTANCE-PENDING`: Selection is visible, but target identity, effective grant, parameters, binary handoff, or write behavior has not been tested.
- `MISSING-CAPABILITY`: No selected/native tool closes the requirement.
- `MISSING-SELECTION`: A catalog capability exists but is not selected on a current server.
- `CONDITIONAL`: Needed only if the corresponding intake or storage design is chosen.

## Bottom Line

The current CRM, Catalyst, and WorkDrive servers cover the native storage and record-operation surface needed for a supervised document workflow:

- find, inspect, preview, version, permission-audit, and download a WorkDrive file;
- create a folder, upload a file, verify upload status, move, and rename;
- inspect CRM metadata, find exact records, create one record, update one record, and read it back;
- inspect Catalyst functions, routes, deployments, logs, and pipelines; and
- invoke one preverified Catalyst function or controlled release action.

They do **not** by themselves provide reliable full-page OCR, deterministic PDF text extraction, checkbox/table interpretation, page-supported structured field extraction, SHA-256 generation, malware scanning, or an event scheduler. Those are processing/runtime requirements, not missing WorkDrive filing tools.

The current selections are therefore sufficient for attended filing after acceptance, but not yet sufficient for unattended application/lease extraction and CRM updates.

## Current Server Coverage

| Workflow boundary | Current server | Selected tools | Status |
|---|---|---:|---|
| CRM configuration metadata | `gh_zoho_crm_audit` | 18 | Production organization verified |
| CRM record reads/writes | `gh_zoho_crm_changes` | 27 | Production organization verified; document workflow not acceptance-tested |
| Catalyst inspection/readback | `gh_zoho_catalyst_webhook_audit` | 15 | Target organization/project/environment unverified |
| Catalyst release/function invocation | `gh_zoho_catalyst_webhook_release` | 7 | Target and writes unverified |
| Catalyst emergency configuration | `gh_zoho_catalyst_webhook_breakglass` | 5 | Target and writes unverified; keep unavailable by default |
| WorkDrive discovery/download/readback | `gh_zoho_workdrive_audit` | 21 | User/team/Team Folder and current effective grant remain acceptance-pending |
| WorkDrive filing | `gh_zoho_workdrive_changes` | 5 | User/team/Team Folder and writes unverified |

The exact selected names are canonical in [`configured-servers.md`](configured-servers.md).

## Required Native Tool Coverage

### Intake Discovery And File Retrieval

The selected WorkDrive Audit tools provide the required native read surface:

```text
ZohoWorkdrive_Get_User_Info
ZohoWorkdrive_Get_All_Teams_Of_User
ZohoWorkdrive_Get_Current_Team_User
ZohoWorkdrive_Get_All_Team_Folders
ZohoWorkdrive_Get_Team_Folders_Info
ZohoWorkdrive_Get_File_List
ZohoWorkdrive_Fetch_Files_Folders
ZohoWorkdrive_Search_Records
ZohoWorkdrive_File_Property
ZohoWorkdrive_Breadcrumbs_Of_File
ZohoWorkdrive_Get_File_Preview
ZohoWorkdrive_Get_Version
ZohoWorkdrive_Download_Server_File
ZohoWorkdrive_Download_Server_File_Version
ZohoWorkdrive_downloadWorkDriveFile
ZohoWorkdrive_Get_Start_Token
ZohoWorkdrive_Get_List_Of_Recent_Changes
```

`ZohoWorkdrive_downloadWorkDriveFile` is the direct file-handoff operation advertised to Codex. A separate controlled acceptance demonstrated single-file binary handoff and PDF text/render inspection without publishing the source document. That proves an attended file can reach the document-reading toolchain; it does not certify the target user/team/Team Folder, complete all-page OCR for arbitrary files, or unattended processing.

The remaining selected Audit tools inspect Team Folder settings, shared users, and shared links. They are safety reads, not authorization to disclose links or identities.

### Filing And Reorganization

The selected WorkDrive Changes tools are the complete initial write allowlist:

```text
ZohoWorkdrive_Create_Folder
ZohoWorkdrive_Upload_File
ZohoWorkdrive_Upload_Status
ZohoWorkdrive_moveFileOrFolder
ZohoWorkdrive_renameFileOrFolder
```

No copy, overwrite/new-version, generic update, trash, deletion, external-share, Team Folder administration, membership, or role tool is required for the initial workflow.

### CRM Schema, Matching, Projection, And Readback

The required current CRM tools are already selected:

```text
ZohoCRM_getOrganization
ZohoCRM_getModules
ZohoCRM_getModuleByApiName
ZohoCRM_getFields
ZohoCRM_getFieldsWithID
ZohoCRM_getLayouts
ZohoCRM_getLayoutById
ZohoCRM_getLayoutRules
ZohoCRM_searchRecords
ZohoCRM_executeCOQLQuery
ZohoCRM_getRecord
ZohoCRM_getRelatedRecord
ZohoCRM_getRelatedRecords
ZohoCRM_createRecords
ZohoCRM_updateRecord
```

`ZohoCRM_createFields`, `ZohoCRM_updateField`, and `ZohoCRM_updateLayout` are already selected for separately approved one-time schema work. They are not runtime document-ingestion tools.

Routine document intake does not require `ZohoCRM_updateRecords`, `ZohoCRM_massUpdateRecords`, upsert, merge, conversion, delete, or email-send tools. Match exactly one record, write one record, and immediately read it back.

### Catalyst Processing And Release

The current Catalyst servers provide inspection and a generic invocation/release surface. In particular:

```text
CatalystbyZoho_Get_Function
CatalystbyZoho_Get_Deployment
CatalystbyZoho_Get_Logs
CatalystbyZoho_Execute_Automation_Test
CatalystbyZoho_Execute_Function_Via_POST
CatalystbyZoho_Update_Function
CatalystbyZoho_Redeploy_a_deployment
CatalystbyZoho_Rollback_Build
```

`CatalystbyZoho_Execute_Function_Via_POST` is not itself OCR or document understanding. Use it only for one exact, reviewed, allowlisted document-processing function. Do not expose arbitrary project/function selection to an unattended workflow.

## Remaining Capability Gaps

### 1. Full PDF/OCR Processing — `MISSING-CAPABILITY`

The official MCP inventory contains no explicitly named tool that guarantees:

- full-page OCR for image-only PDFs;
- deterministic embedded-text extraction;
- page rendering and visual review;
- checkbox, table, handwriting, or signature observations;
- structured application/lease fields with page evidence and confidence;
- SHA-256 generation; or
- malware/content scanning.

An attended Codex task may use the local governed PDF runtime after WorkDrive download. One controlled text-PDF handoff and text/render inspection succeeded; image-only PDF behavior, arbitrary file types, target identity, complete-page guarantees, and unattended processing remain acceptance-pending.

Unattended processing requires one narrow document processor, such as a reviewed Catalyst function, with an output contract containing:

```text
document_type
source_workdrive_resource_id
source_workdrive_version_id
sha256
page_count
ocr_used
allowlisted_structured_fields
source_page_for_each_field
redacted_evidence_snippet_for_each_field
confidence_for_each_field
pii_redactions_applied
processor_version
warnings
```

Raw OCR text must remain encrypted and transient inside the processor and must not be returned through MCP or written to task/function logs by default. Retain only approved structured fields, page references, and the minimum redacted evidence needed for review. The processor must not make screening, legal-validity, or tenant-eligibility decisions.

The recommended coded MCP boundary is:

```text
Server: gh_document_processor
Tools:
  process_leasing_document
  validate_leasing_document_extraction
```

`process_leasing_document` accepts only an allowlisted WorkDrive resource/version or an already controlled file handoff, performs embedded-text extraction plus all-page OCR/rendering and hashing, and returns the evidence contract above. `validate_leasing_document_extraction` validates the output schema, page citations, confidence thresholds, conflicts, and required-field policy without writing CRM.

Do not add arbitrary URL fetch, generic code execution, applicant-screening decisions, legal-validity decisions, or CRM writes to this server.

### 2. Automatic Arrival — `MISSING-SELECTION` / `CONDITIONAL`

MCP tools do not wake themselves. Use one of:

1. a signed WorkDrive custom-app webhook that queues only the resource/event IDs;
2. a controlled scheduler that persists `Get_Start_Token` and polls `Get_List_Of_Recent_Changes`; or
3. Zoho Forms/Flow depositing a document into a restricted WorkDrive Intake folder.

Zoho's current WorkDrive guidance limits custom-app webhooks to the Business plan and requires a team Admin or Super admin to configure them. Confirm the live plan and role before choosing that route.

The current Catalyst servers do not select the catalog's cron/job-pool tools. If a native Catalyst polling schedule is chosen, verify official parameters and target semantics before adding the smallest applicable split:

```text
Audit candidates:
  CatalystbyZoho_Get_Cron_Job_By_Id
  CatalystbyZoho_List_All_Crons
  CatalystbyZoho_Get_Jobpool_By_Id
  CatalystbyZoho_List_All_Jobpools
  CatalystbyZoho_Get_Job_By_Id

Breakglass/configuration candidates:
  CatalystbyZoho_Create_Job_Pool
  CatalystbyZoho_Update_Job_Pool
  CatalystbyZoho_Create_Cron_Job
  CatalystbyZoho_Update_Cron_Job
  CatalystbyZoho_Update_Cron_Job_Status

Release/test candidate:
  CatalystbyZoho_Submit_Cron_Job
```

Reuse an existing approved Job Pool when possible. Do not add `CatalystbyZoho_Create_Immediate_Job` for recurring intake. Cron can schedule polling, but it does not replace event idempotency, signature validation, change-token persistence, or dead-letter handling.

WorkDrive event retrieval is reconciliation, not proof that a file is complete, safe, final, or correctly classified.

### 3. Catalyst Provisioning And Source Registration — `MISSING-CAPABILITY`

The current Catalyst selection can inspect and release an existing function, but the catalog has no Catalyst create-function tool. Initial function provisioning remains manual, CLI/pipeline, or separately governed API work.

There is also no selected Zoho Payments webhook-registration tool. Registering a source webhook remains outside the current servers. Catalyst scheduling is the conditional missing selection documented above. Breakglass MCP environment-variable tools are nonsecret-only; secret values must be entered directly in Zoho's secret UI or approved vault outside Codex/MCP. The current selection provides no safe secret display, delete, or atomic rollback path.

### 4. CRM WorkDrive Link Fields — `ACCEPTANCE-PENDING`

Repository metadata currently shows:

- Rental Applications use standard module API `Deals`; `WorkDrive_Application_Folder_URL` remains proposed/unverified.
- Leases use custom module API `Leases`; `WorkDrive_Lease_Folder_URL` and `Signed_Lease_PDF_URL` remain proposed/unverified.
- Inspections already have verified `Photos_Folder_URL` and `Signed_Checklist_PDF_URL`.
- Condition Reports currently have verified relationship fields but no governed full-document transcription design.

Before unattended filing, inspect live metadata and separately approve any missing URL/resource-ID fields. Store the immutable WorkDrive resource ID alongside a user-facing internal URL. Never create a public link merely to connect CRM to WorkDrive.

### 5. Native CRM WorkDrive Folder Lookup — `CONDITIONAL`

`ZohoCRM_getRecordWorkdriveFolder` exists in the official tool catalog but is not selected on the current CRM servers.

It is useful only if GH adopts CRM's native record-folder integration. It is not required when the governed design stores WorkDrive resource ID and internal URL fields and verifies them through `ZohoCRM_getRecord`.

### 6. CRM Attachment Intake — `CONDITIONAL`

`ZohoCRM_getAttachments` and `ZohoCRM_getAttachmentById` are not selected. Add them only if PDFs will arrive as CRM attachments.

The preferred design is WorkDrive-first intake. Do not add CRM upload tools merely to duplicate a controlled WorkDrive file.

### 7. WorkDrive AI Summary — `CONDITIONAL`

`ZohoWorkdrive_Generate_File_Summary`, `ZohoWorkdrive_Get_File_Summary`, and `ZohoWorkdrive_File_Query` may be considered only after a Zia/privacy review. They are not deterministic all-page OCR, hashing, or evidence-backed structured extraction and are not required initially.

`ZohoWorkdrive_Download_Progress` is paired with the separate multi-download workflow and is not required for the proposed one-document intake. Do not add it unless a future approved design also adopts `ZohoWorkdrive_Multi_Download`.

### 8. Mail Intake — `CONDITIONAL`

No Zoho Mail MCP server is configured. If approved applications arrive only by email and cannot be routed through Flow into WorkDrive, create a separate read-only Mail intake boundary. Do not mix mailbox access with CRM or WorkDrive writes.

The minimal candidate selection is:

```text
ZohoMail_getMailAccounts
ZohoMail_getAllFolders
ZohoMail_listEmails
ZohoMail_SearchEmails
ZohoMail_getMessageDetails
ZohoMail_getMessageContent
ZohoMail_getMessageAttachmentInfo
ZohoMail_getMessageAttachmentContent
```

Verify the exact live prefixes and picker names before creation. Exclude send, reply, delete, move, archive, spam, flag, label, account-settings, and mailbox-administration tools.

## Governed CRM Routing

| Document | CRM authority | WorkDrive role |
|---|---|---|
| Rental application | `Contacts` plus Rental Applications (`Deals`) | Restricted application folder and source PDF |
| Inspection/checklist | `Inspections`; related `Condition_Reports` when applicable | Signed checklist, photos, and detailed evidence |
| Condition report | Relationships/status in CRM; full report remains controlled evidence | Authoritative PDF/photos |
| Executed lease | `Leases` operational snapshot; Contracts/Sign remain lifecycle/evidence authorities | Controlled executed copy and archive metadata |

Leads, Property Assets (`Equipment`), Pets, and Vehicles (`Tenant_Vehicles`) remain read-only. An application may set aggregate pet/storage request fields on `Deals`; it must not create protected detail records.

Do not automatically populate unresolved rent/proration semantics, infer legal conclusions, authenticate signatures, or treat CRM snapshots as Books payment/accounting truth.

## Idempotent Processing Contract

Use:

```text
operation_key =
  document-intake:<workdrive-resource-id>:<workdrive-version-id>:<sha256>
```

Required sequence:

1. Resolve the expected WorkDrive user, team, Team Folder, parent, resource, and version.
2. Retrieve and validate file type, size, content, permissions, and sharing state.
3. Calculate the content hash and classify/extract every page.
4. Resolve exactly one authorized CRM target by immutable ID or governed unique key.
5. Return the current CRM state, proposed field-level diff, source pages, and warnings.
6. Require approval until field-specific automation acceptance is complete.
7. Create or update one CRM record; set trigger behavior explicitly.
8. Read the CRM record back through `gh_zoho_crm_changes` → `ZohoCRM_getRecord`, and read the WorkDrive resource back through Audit immediately.
9. Move/rename only after the destination and collision policy are approved.
10. Persist the operation/result state outside public GitHub.

Zero matches, multiple matches, stale records, conflicting values, unsupported fields, incomplete OCR, or ambiguous write timeouts must stop for review. Never compensate by deleting a CRM record or WorkDrive resource.

## Required Acceptance Tests

- Exact CRM organization and production/sandbox identity.
- Exact Catalyst organization, project, environment, function, deployment, route, and OAuth principal.
- Exact WorkDrive user, data center, team, Team Folder, role, allowed parent IDs, and effective sharing.
- WorkDrive text-PDF and image-only-PDF binary handoff to the processor.
- Every-page extraction with page evidence, tables, checkboxes, and low-confidence escalation.
- New folder, duplicate folder replay, new upload, duplicate upload replay, move, rename, and readback.
- Same-name/different-content collision without overwrite.
- Existing identical CRM link returns no-op success.
- Zero, one, and multiple CRM target matches.
- Concurrent CRM modification aborts rather than overwrites.
- Protected modules reject writes.
- Public/external sharing remains absent.
- Invalid webhook signature, duplicate/out-of-order event, retry, timeout, and dead-letter handling.
- Partial WorkDrive/CRM failure retains evidence and records an incomplete operation without automatic deletion.

## Explicit Exclusions

Do not add or use for this workflow:

- WorkDrive trash, permanent delete, empty-trash, public/external-share, Team Folder delete/admin, membership, or role tools.
- WorkDrive generic update tools that combine routine and destructive status changes.
- CRM bulk/mass update, delete, merge, conversion, autonomous email, or ungoverned upsert.
- Generic arbitrary HTTP, code-execution, or cross-suite super-server authority.
- Catalyst Breakglass during routine ingestion.
- Applicant screening or legal conclusions generated from document text.

## Change-Control Boundary

This file documents selected capabilities and remaining gates. It does not configure Zoho, grant OAuth access, deploy a Catalyst function, create a webhook, move or upload a file, read tenant documents, or modify CRM records.

## Sources

- [Configured GH MCP servers](configured-servers.md)
- [Full Zoho MCP tool inventory](tool-inventory.md)
- [Zoho WorkDrive engineering reference](../products/zoho-workdrive.md)
- [CRM governed field catalog](../../../../src/zoho-crm/field-maps/crm-module-field-catalog.md)
- [Zoho MCP Tool Manual](https://zoho-mcp-manual-tool-guide.onslate.in/)
- [Zoho WorkDrive OpenAPI repository snapshot (commit `e0b3dd78f6f8789cf5033718fc357cfc47a09029`)](https://github.com/zoho/zohoworkdrive-oas/tree/e0b3dd78f6f8789cf5033718fc357cfc47a09029)
- [Catalyst Cron documentation](https://docs.catalyst.zoho.com/en/job-scheduling/help/cron/introduction/)
- [WorkDrive custom-app webhooks](https://help.zoho.com/portal/en/kb/workdrive/integrations/webhooks/articles/setting-up-webhooks-in-workdrive-using-custom-apps)
