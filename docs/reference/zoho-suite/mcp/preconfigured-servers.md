# Zoho MCP Preconfigured Server Catalog

**Portal Snapshot:** U.S. data center, July 24, 2026  
**Evidence:** Authenticated portal captures supplied by Gabriel plus current official Zoho MCP documentation.

## Evidence Status

The portal captures directly verify 15 preconfigured templates across Zoho CRM, Zoho Books, and Zoho WorkDrive.

The portal reveals exact tool membership only after opening a template modal. The supplied evidence includes that modal for **CRM Data & Metadata Operations** only. Tool membership for the other 14 templates remains a live-portal fact that must be captured before any server is authorized.

This is deliberate fail-closed documentation:

- Template names and descriptions are recorded.
- Known tools are recorded exactly.
- Unknown tool membership remains `Not Verified`.
- No tool is inferred from a template title or description.

## Zoho CRM Templates

| Preconfigured Server | Portal Description | Services | Exact Tool Membership | Initial Risk | Recommendation |
|---|---|---|---|---|---|
| CRM Data & Metadata Operations | Access and manage Zoho CRM records across modules with tools for searching, retrieving, creating, and updating data. It also provides metadata access for modules, fields, users, and organization details, COQL queries, record counts, and related records. | Zoho CRM | Verified below | High | Do not use unchanged; it exposes tenant-record reads and four write tools but omits several configuration-audit tools. |
| CRM Activities & Engagement | Manages CRM activities such as tasks, notes, and record-linked communication history. The visible portal card also indicates follow-up-task and attachment capabilities, but its text is truncated in the supplied capture. | Zoho CRM | Not Verified | High | Defer until a recurring activity workflow is proven and its modal is captured. |
| CRM Automation & Workflows | Configure and manage CRM workflow automation including workflow rules, field updates, and email notifications. | Zoho CRM | Not Verified | High | Defer until after the read-only CRM configuration audit. |
| Lead Management System | A specialized MCP server for managing the end-to-end lead lifecycle, including creation, searching, updates, and lead conversion. | Zoho CRM | Not Verified | High | Defer; GH has no need for autonomous lead conversion during the first pilot. |
| Contact Hub & Merging | Centralized contact management server designed to handle contact synchronization, deletion, and advanced merging operations. | Zoho CRM | Not Verified | Critical | Do not authorize initially; deletion and merging create unnecessary data-loss risk. |
| Deal Lifecycle Tracker | Automate and track sales deal progression, search for existing opportunities, and manage blueprint transitions. | Zoho CRM | Not Verified | High | Defer; stage and Blueprint transitions are consequential production changes. |
| Account & Relationship Manager | Manage corporate accounts and their associated contacts to maintain a clean hierarchical view of customer data. | Zoho CRM | Not Verified | High | Defer; it is record-management scope rather than configuration-audit scope. |
| Activity & Communication Center | Unified server for managing daily operations including tasks, calls, and events to ensure follow-up consistency. | Zoho CRM | Not Verified | High | Defer; it can create operational side effects and communications. |
| Notes & Contextual Collaboration | Capture and retrieve internal notes across various CRM modules to maintain context during the sales process. | Zoho CRM | Not Verified | Medium–High | Defer; notes may contain tenant or applicant information and do not solve the current configuration objective. |
| Email Automation & Follow-up | Automate outbound communication and follow-up emails directly from CRM records. | Zoho CRM | Not Verified | Critical | Do not authorize initially; this can communicate externally. |
| CommandCenter CRM Actions | Single MCP template for all CRM stage actions in CommandCenter. | Zoho CRM and Zoho CommandCenter | Not Verified | Critical | Defer; broad stage-action authority is not needed for the pilot. |

## Verified Tool Composition: CRM Data & Metadata Operations

The modal displays 16 chips but only 15 unique tools. `getModuleByApiName` appears twice in the portal.

| Tool | Function | Class |
|---|---|---|
| `getRecords` | Lists records from a selected CRM module. | Record Read |
| `getRecord` | Retrieves one record by module and record ID. | Record Read |
| `searchRecords` | Searches module records using supported search parameters or criteria. | Record Read |
| `createRecords` | Creates CRM records in a selected module. | Record Write |
| `updateRecord` | Updates one record by record ID. | Record Write |
| `updateRecords` | Updates multiple CRM records. | Record Write |
| `upsertRecords` | Creates or updates records using duplicate-check fields. | Record Write |
| `getRelatedRecords` | Retrieves records from a related list for a parent record. | Record Read |
| `getModules` | Retrieves CRM module metadata and capabilities. | Configuration Read |
| `getModuleByApiName` | Retrieves complete metadata for one module, including fields, layouts, profiles, related lists, and capabilities. | Configuration Read |
| `getFields` | Retrieves field metadata for a module. | Configuration Read |
| `getUsers` | Retrieves CRM users. | Identity Read |
| `getOrganization` | Retrieves CRM organization details. | Organization Read |
| `executeCOQLQuery` | Runs a COQL query against CRM record data. | Record Read |
| `getRecordCount` | Counts records in a module, optionally using a custom view or supported search filter. | Record Read |

### Why This Template Is Not the First Choice

It combines three scopes that should not be combined for the first pilot:

1. CRM configuration metadata.
2. Tenant/applicant/business record reads.
3. CRM record writes.

It also does not show dedicated tools for listing layouts, layout rules, global picklists, or workflows. A narrowly scoped custom Zoho-hosted server is a better fit for the current objective.

## Zoho Books Templates

| Preconfigured Server | Portal Description | Services | Exact Tool Membership | Initial Risk | Recommendation |
|---|---|---|---|---|---|
| Accountant Management System | A specialized MCP server for managing accounting operations in Zoho Books. | Zoho Books | Not Verified | Critical | Do not authorize; the description is broad and does not establish read-only behavior. |
| Books Financial Overview | View invoices, bills, expenses, bank transactions, and chart of accounts. | Zoho Books | Not Verified | Medium–High | Best Books starting template only after its modal confirms every included tool is read-only. |
| Books Transactions & Creation | Create invoices, contacts, and manage financial transactions. | Zoho Books | Not Verified | Critical | Defer; it can create financial records and may expose broader transaction authority. |

The official Tool Manual contains 1,090 distinct Zoho Books tools. A preconfigured template includes only a subset; the template title is not evidence of which subset.

## Zoho WorkDrive Templates

| Preconfigured Server | Portal Description | Services | Exact Tool Membership | Initial Risk | Recommendation |
|---|---|---|---|---|---|
| WorkDrive File Management | Browse, search, download, and manage files and folders in Zoho WorkDrive. | Zoho WorkDrive | Not Verified | High | Defer. If later needed, remove upload, move, rename, share, and delete tools and keep search/read/download only. |

The official Tool Manual contains 178 distinct Zoho WorkDrive tools. The word `manage` does not establish a safe permission boundary.

## Separate Zoho CRM Product-Specific Pre-Built Servers

Zoho CRM's developer documentation separately describes four pre-built CRM MCP servers. These are not the same 11 templates shown in the general Zoho MCP portal.

| Product-Specific Server | Official Capability |
|---|---|
| Data Insights | Read-only record queries, COQL, module discovery, and field schemas. |
| Data Operations | Record create, read, update, delete, bulk operations, related records, COQL, modules, and fields. |
| Module Customization | Custom modules, module properties, fields, page layouts, and layout activation or deactivation. |
| Workflow & Process Automation | Workflow rules, workflow ordering, workflow task actions, and workflow configuration reads. |

The current [Zoho CRM MCP overview](https://www.zoho.com/crm/developer/docs/mcp/overview.html) explicitly says four. An official community announcement says five but names only four; do not treat an unnamed fifth server as available.

## Required Capture Before Creating Any Unverified Template

For each candidate template:

1. Open the template card.
2. Capture the complete modal showing server name, service tags, full description, and every tool chip.
3. Record the number of displayed chips and unique tools.
4. Match every tool against the official Tool Manual.
5. Classify each tool as read, write, delete/destructive, external communication, financial, access-control, or unknown.
6. Remove every tool outside the approved workflow before connecting the server to Codex.

Do not create a template merely to discover its tools if the modal provides the list before the **Create** action.
