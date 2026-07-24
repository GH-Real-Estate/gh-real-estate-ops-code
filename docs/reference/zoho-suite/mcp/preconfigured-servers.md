# Zoho MCP Preconfigured Server Catalog

**Portal Snapshot:** U.S. data center, July 24, 2026  
**Evidence:** Authenticated Zoho MCP portal captures and modal transcriptions supplied by Gabriel, plus current official Zoho MCP documentation.

## Evidence Status

The captured portal evidence catalogs 19 preconfigured templates:

- 11 Zoho CRM templates.
- 3 Zoho Books templates.
- 1 Zoho Payments template.
- 3 Zoho Mail templates.
- 1 Zoho WorkDrive template.

Exact tool membership is verified for all 18 captured CRM, Books, Payments, and Mail templates. The WorkDrive template's name and description are verified, but its exact tools remain `Not Verified`.

`CRM Data & Metadata Operations` displays 16 tool chips but only 15 unique tool names because `getModuleByApiName` appears twice. The duplicate is preserved as a portal observation and is not treated as a second capability.

Across the 18 verified templates, the capture contains 217 displayed tool chips, 216 unique per-template memberships, and 177 unique tool names across templates. Four live-portal names are not present in the dated public Tool Manual bundle and are preserved in a separate overlay in [`tool-inventory.md`](tool-inventory.md).

This is a dated account-specific portal snapshot. Recheck the live modal before creating or authorizing a server because Zoho can change template composition.

## Decision Summary

| Preconfigured Server | Service | Tool Count | Risk | GH Real Estate Decision |
|---|---|---:|---|---|
| CRM Data & Metadata Operations | Zoho CRM | 16 chips / 15 unique | High | Do not use unchanged; it mixes metadata reads with production-record reads and writes. |
| CRM Activities & Engagement | Zoho CRM | 12 | Critical | Defer; it can create, update, and delete tasks or notes and send mail. |
| CRM Automation & Workflows | Zoho CRM | 17 | Critical | Defer; it can create, clone, reorder, update, and delete automation and notifications. |
| Lead Management System | Zoho CRM | 5 | High | Defer; it creates, updates, and converts production leads. |
| Contact Hub & Merging | Zoho CRM | 5 | Critical | Do not authorize initially; it includes record deletion. |
| Deal Lifecycle Tracker | Zoho CRM | 3 | High | Defer; record updates can change live leasing-pipeline state. |
| Account & Relationship Manager | Zoho CRM | 4 | High | Defer; it creates and updates production account/property records. |
| Activity & Communication Center | Zoho CRM | 5 | High | Defer; it creates records and tasks and updates tasks. |
| Notes & Contextual Collaboration | Zoho CRM | 3 | High | Defer; it creates notes that may contain tenant or applicant context. |
| Email Automation & Follow-up | Zoho CRM | 1 | Critical | Do not authorize initially; its sole tool sends external mail. |
| CommandCenter CRM Actions | Zoho CRM and Zoho CommandCenter | 9 | Critical | Defer; it mutates journeys/stages and can attach automation functions. |
| Accountant Management System | Zoho Books | 67 | Critical | Do not authorize; it exposes Chart of Accounts, journal, project, custom-field, and deletion operations. |
| Books Financial Overview | Zoho Books | 12 | Medium-High | First preconfigured candidate after the CRM audit; all captured tools are reads, but they expose sensitive financial data. |
| Books Transactions & Creation | Zoho Books | 9 | Critical | Defer; it can create invoices and contacts. |
| Payments Management | Zoho Payments | 15 | Critical | Do not authorize initially; it creates payment sessions, links, customers, and refunds. |
| Mail Reading & Search | Zoho Mail | 13 | High | Defer; it exposes message and attachment contents and includes `flagMessages`, which changes state. |
| Mail Sending & Replies | Zoho Mail | 5 | Critical | Do not authorize initially; it sends external mail and uploads attachments. |
| Mail Organization & Management | Zoho Mail | 16 | Critical | Do not authorize initially; it moves, archives, deletes, labels, and marks mail as spam. |
| WorkDrive File Management | Zoho WorkDrive | Not Verified | High | Defer until the exact modal is captured and a concrete document workflow exists. |

Risk labels evaluate the template unchanged. They do not mean every tool has the same severity.

## Zoho CRM Templates

### CRM Data & Metadata Operations

**Server Name:** `CRM-Data-Metadata`  
**Service Name:** Zoho CRM  
**Description:** Access and manage Zoho CRM records across modules with tools for searching, retrieving, creating, and updating data. The template also provides metadata access for modules, fields, users, and organization details. Agents can run advanced COQL queries, retrieve record counts, and navigate related records.  
**Tools:** 16 displayed chips / 15 unique tools

```text
getRecords
getRecord
searchRecords
createRecords
updateRecord
updateRecords
upsertRecords
getRelatedRecords
getModules
getModuleByApiName
getModuleByApiName
getFields
getUsers
getOrganization
executeCOQLQuery
getRecordCount
```

The template combines configuration metadata with production-record reads and four write tools: `createRecords`, `updateRecord`, `updateRecords`, and `upsertRecords`. It also lacks dedicated layout, layout-rule, global-picklist, and workflow-read tools required for the intended CRM configuration audit.

### CRM Activities & Engagement

**Server Name:** `CRM-Activities-Engagement`  
**Service Name:** Zoho CRM  
**Description:** Manage CRM activities such as tasks, notes, and communication history linked to records. Agents can create follow-up tasks, attach notes, track engagement timelines, and manage activity updates.  
**Tools:** 12

```text
createWorkflowTasks
getTaskById
getWorkflowTasks
updateWorkflowTaskById
deleteTaskById
createNotesModule
getNoteById
updateNoteById
deleteNoteById
deleteNotesModule
getTimelines
sendMail
```

### CRM Automation & Workflows

**Server Name:** `CRM-Automation-Workflow`  
**Service Name:** Zoho CRM  
**Description:** Configure and manage CRM workflow automation including workflow rules, field updates, and email notifications.  
**Tools:** 17

```text
postWorkflowRule
updateWorkflowRuleById
deleteWorkflowRuleById
deleteWorkflowRules
cloneWorkflowRule
getWorkflowRules
getWorkflowRuleById
reorderWorkflowRules
createFieldUpdates
updateFieldUpdateById
deleteFieldUpdateById
deleteFieldUpdates
postEmailNotifications
updateEmailNotification
deleteEmailNotificationById
deleteEmailNotifications
getEmailNotifications
```

### Lead Management System

**Server Name:** `Lead-Management`  
**Service Name:** Zoho CRM  
**Description:** A specialized MCP server for managing the end-to-end lead lifecycle, including creation, searching, updates, and lead conversion.  
**Tools:** 5

```text
getRecords
createRecords
updateRecords
searchRecords
convertInventory
```

`convertInventory` is recorded exactly as displayed in the supplied portal transcription. Verify the live tool manual entry and behavior before any authorization; the name does not match the template's lead-conversion wording.

### Contact Hub & Merging

**Server Name:** `Contact-Hub`  
**Service Name:** Zoho CRM  
**Description:** Centralized contact management server designed to handle contact synchronization, deletion, and advanced merging operations.  
**Tools:** 5

```text
getRecords
createRecords
updateRecords
deleteRecords
searchRecords
```

The captured composition includes deletion but does not display a separately named merge tool. Do not infer merge behavior beyond the live tool definitions.

### Deal Lifecycle Tracker

**Server Name:** `Deal-Lifecycle`  
**Service Name:** Zoho CRM  
**Description:** Automate and track sales deal progression, search for existing opportunities, and manage Blueprint transitions.  
**Tools:** 3

```text
getRecords
updateRecords
searchRecords
```

### Account & Relationship Manager

**Server Name:** `Account-Management`  
**Service Name:** Zoho CRM  
**Description:** Manage corporate accounts and their associated contacts to maintain a clean hierarchical view of customer data.  
**Tools:** 4

```text
getRecords
createRecords
updateRecords
getRelatedRecords
```

### Activity & Communication Center

**Server Name:** `Activity-Center`  
**Service Name:** Zoho CRM  
**Description:** Unified server for managing daily operations including tasks, calls, and events to ensure follow-up consistency.  
**Tools:** 5

```text
getTaskById
createWorkflowTasks
updateWorkflowTaskById
getRecords
createRecords
```

### Notes & Contextual Collaboration

**Server Name:** `Notes-Collaboration`  
**Service Name:** Zoho CRM  
**Description:** Capture and retrieve internal notes across various CRM modules to maintain context during the sales process.  
**Tools:** 3

```text
getNoteById
createNotesModule
getRelatedRecords
```

### Email Automation & Follow-up

**Server Name:** `Email-Followup`  
**Service Name:** Zoho CRM  
**Description:** Automate outbound communication and follow-up emails directly from CRM records.  
**Tools:** 1

```text
sendMail
```

### CommandCenter CRM Actions

**Server Name:** `cc-crm-all-actions-unified-stage-flow-MCP-Server`  
**Service Name:** Zoho CRM and Zoho CommandCenter  
**Description:** Unified template for configuring all CRM stage actions and journey deadlines in CommandCenter, including add/remove tags, create record, convert, webhooks, field updates, tasks, functions, and email notifications.  
**Tools:** 9

```text
putStagesByStageid
updateJourney
getModules
getFields
getUsers
getLayouts
getTags
getEmailTemplates
postAutomationFunctions
```

The description claims a broader action set than the nine displayed tool names. Treat the tools' live definitions and required parameters as authoritative; do not infer undeclared standalone capabilities.

## Zoho Books Templates

### Accountant Management System

**Server Name:** `Accountant`  
**Service Name:** Zoho Books  
**Description:** A specialized MCP server for managing end-to-end accounting operations including Chart of Accounts, journals, projects, currencies, taxes, and financial configurations.  
**Tools:** 67

```text
list_organizations
get_organization
create_chart_of_account
list_chart_of_accounts
get_chart_of_account
update_chart_of_account
delete_chart_of_account
mark_chart_of_account_active
mark_chart_of_account_inactive
list_chart_of_account_transactions
delete_chart_of_account_transaction
list_currencies
create_journal
list_journals
update_journal
get_journal
delete_journal
add_journal_attachment
add_journal_comment
delete_journal_comment
mark_journal_published
list_locations
list_contacts
list_taxes
list_tax_exemptions
list_tax_authorities
get_tags
create_project
list_projects
update_projects_using_custom_field
update_project
get_project
delete_project
mark_project_active
mark_project_inactive
clone_project
add_project_user
list_project_users
invite_project_user
update_project_user
get_project_user
delete_project_user
add_project_comment
list_project_comments
delete_project_comment
list_project_invoices
add_project_task
list_project_tasks
update_project_task
get_project_task
delete_project_task
list_users
list_invoices
create_base_currency_adjustment
list_base_currency_adjustments
get_base_currency_adjustment
delete_base_currency_adjustment
list_base_currency_adjustment_accounts
create_custom_field
list_custom_fields
update_custom_field
delete_custom_field
update_field_dropdown_options
bulk_fetch_fields
check_formula_syntax
list_custom_fields_simple
get_fields_meta
```

This template includes destructive accounting and configuration operations. It is not appropriate for an AI pilot or routine GH Real Estate review.

### Books Financial Overview

**Server Name:** `Books-Financial-Overview`  
**Service Name:** Zoho Books  
**Description:** View invoices, bills, expenses, bank transactions, and Chart of Accounts. Core financial-data retrieval for accounting workflows.  
**Tools:** 12

```text
list_organizations
get_organization
list_invoices
get_invoice
list_contacts
get_contact
list_bills
list_expenses
list_items
list_bank_accounts
list_bank_transactions
list_chart_of_accounts
```

All captured tools are named reads. This is the best verified preconfigured candidate, but it exposes sensitive financial and contact data and does not advance the current CRM configuration objective.

### Books Transactions & Creation

**Server Name:** `Books-Transactions`  
**Service Name:** Zoho Books  
**Description:** Create invoices and contacts and manage financial transactions. Intended for agents that need write access to accounting data.  
**Tools:** 9

```text
list_organizations
list_contacts
list_items
create_invoice
create_contact
list_customer_payments
list_vendor_payments
list_sales_orders
get_estimate
```

## Zoho Payments Template

### Payments Management

**Server Name:** `Payments-Management`  
**Service Name:** Zoho Payments  
**Description:** Manage end-to-end payment operations, including payment sessions, refunds, customers, payouts, and payment links. Agents can track payments, issue refunds, generate shareable payment links, and drill into payout transactions for reconciliation.  
**Tools:** 15

```text
createPaymentSession
getPaymentSession
createPaymentLink
getPaymentLink
updatePaymentLink
cancelPaymentLink
listPayments
getPayment
createCustomer
getCustomer
createRefund
getRefund
listPayouts
getPayout
getPayoutTransactions
```

Do not expose payment creation, refund, or payment-link authority to the initial operator. Financial actions belong in deterministic, reviewed payment workflows.

The public Tool Manual snapshot lists `listMerchantAccounts` as a sixteenth Zoho Payments tool, but it is not included in this 15-tool preconfigured template. This is normal evidence that a preconfigured template is only a subset of a service's total tool catalog.

## Zoho Mail Templates

### Mail Reading & Search

**Server Name:** `Mail-Reading-Search`  
**Service Name:** Zoho Mail  
**Description:** Read, search, and browse emails including message content, attachments, and folder structure. Core template for any mail-related agent workflow.  
**Tools:** 13

```text
getMailAccounts
listEmails
SearchEmails
getAllFolders
getMessageContent
getAccountDetails
getMessageAttachmentInfo
getMessageAttachmentContent
getMessageDetails
getFolder
getOriginalMessage
readMessages
flagMessages
```

This template is not strictly read-only because `flagMessages` changes mailbox state. It also exposes sensitive message and attachment contents.

### Mail Sending & Replies

**Server Name:** `Mail-Sending-Replies`  
**Service Name:** Zoho Mail  
**Description:** Compose and send new emails, reply to existing threads, and manage attachments for outgoing mail.  
**Tools:** 5

```text
getMailAccounts
getAllFolders
sendEmail
sendReplyEmail
uploadAttachments
```

### Mail Organization & Management

**Server Name:** `Mail-Organization`  
**Service Name:** Zoho Mail  
**Description:** Organize the mailbox by moving, archiving, labeling, and managing emails and folders. Includes task management within Mail.  
**Tools:** 16

```text
getMailAccounts
getAllFolders
moveMessages
archiveMessage
unArchiveMessage
deleteEmail
spamMessage
unSpamMessage
unreadMessage
applyLabelToMessages
removeLabelFromMessage
createFolder
renameFolder
createLabel
getAllLabelDetails
listPersonalTasks
```

## Zoho WorkDrive Template

### WorkDrive File Management

**Server Name:** Not captured  
**Service Name:** Zoho WorkDrive  
**Description:** Browse, search, download, and manage files and folders in Zoho WorkDrive.  
**Tools:** `Not Verified`

Do not create this template until its complete live modal is captured. If a future workflow requires it, keep only the minimum search/read/download tools and exclude upload, move, rename, share, and delete operations.

## Separate Zoho CRM Product-Specific Pre-Built Servers

Zoho CRM's developer documentation separately describes four product-specific pre-built CRM MCP servers. These are not the same 11 templates shown in the general Zoho MCP portal.

| Product-Specific Server | Official Capability |
|---|---|
| Data Insights | Read-only record queries, COQL, module discovery, and field schemas. |
| Data Operations | Record create, read, update, delete, bulk operations, related records, COQL, modules, and fields. |
| Module Customization | Custom modules, module properties, fields, page layouts, and layout activation or deactivation. |
| Workflow & Process Automation | Workflow rules, workflow ordering, workflow task actions, and workflow configuration reads. |

The current [Zoho CRM MCP overview](https://www.zoho.com/crm/developer/docs/mcp/overview.html) explicitly says four. An official community announcement says five but names only four; do not treat an unnamed fifth server as available.

## First-Server Decision

Create **GH CRM Configuration Audit** first as a custom, Zoho-hosted, read-only tool selection. Do not custom-code an MCP server.

None of the verified preconfigured templates matches the required boundary:

- `CRM Data & Metadata Operations` includes production-record reads and writes but omits several configuration-audit reads.
- `CRM Automation & Workflows` includes destructive workflow and notification writes.
- `CommandCenter CRM Actions` changes journeys and stage actions.
- `Books Financial Overview` is the safest verified preconfigured template, but it is accounting scope and does not solve the first CRM objective.

The exact 14-tool read-only allowlist, rollout, and kill criteria are maintained in [`recommended-first-server.md`](recommended-first-server.md).

If Gabriel later wants the first preconfigured template after the CRM audit, use **Books Financial Overview** unchanged only after confirming the live modal still contains the same 12 read tools and the correct GH Real Estate Books organization.

## Required Recheck Before Creation

1. Open the candidate's complete live modal.
2. Compare the description and every tool chip with this dated snapshot.
3. Match every selected tool to the current official Tool Manual.
4. Classify the tool as read, write, destructive, external communication, financial, access-control, or unknown.
5. Confirm the exact organization and environment.
6. Use Authorization on Demand and keep Codex approval at Always Ask.
7. Stop if the server exposes any unapproved tool or the target is ambiguous.

Do not create a template merely to inspect its tools when the modal exposes the list before the **Create** action.
