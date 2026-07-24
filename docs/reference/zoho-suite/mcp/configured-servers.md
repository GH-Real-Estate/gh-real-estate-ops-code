# Configured Zoho MCP Servers

**Verified:** July 24, 2026  
**Scope:** Sanitized current-state inventory of the Zoho MCP servers configured for GH Real Estate in Codex.

## Evidence And Status

This inventory is based on:

- A redacted Codex MCP server inventory supplied on July 24, 2026.
- A successful `ZohoCRM_getOrganization` acceptance check against the GH Real Estate production organization.
- A successful read-only CRM module inventory through `gh_zoho_crm_audit`.
- A successful organization-only target check through `gh_zoho_crm_changes`.

The evidence confirms server identifiers, advertised tool names, OAuth status, and the production target for both CRM servers. The supplied evidence does not establish which Zoho Books organization `gh_zoho_books_review` targets; that server still requires an organization-only acceptance check before financial review.

No MCP URL, secure API key, token, organization ID, record payload, tenant information, or accounting data belongs in this repository.

## Current Server Summary

| Codex Server ID | Zoho Service | Auth | Tools | Access Class | Target Status |
|---|---|---:|---:|---|---|
| `gh_zoho_crm_audit` | Zoho CRM | OAuth | 18 | Configuration metadata reads | GH Real Estate production verified |
| `gh_zoho_crm_changes` | Zoho CRM | OAuth | 27 | Configuration writes plus production record reads and writes | GH Real Estate production verified |
| `gh_zoho_books_review` | Zoho Books | OAuth | 12 | Financial and contact reads | Organization not yet verified in supplied evidence |

The three servers expose 57 per-server tool memberships in total. Tool names below are the exact names advertised to Codex. Zoho's server builder may display the same tools without the `ZohoCRM_` or `ZohoBooks_` prefix.

## `gh_zoho_crm_audit`

This server is the read-only CRM configuration inspection boundary. It does not include CRM record retrieval or mutation tools.

```text
ZohoCRM_getBulkGlobalPicklists
ZohoCRM_getFieldUpdateById
ZohoCRM_getFieldUpdates
ZohoCRM_getFields
ZohoCRM_getFieldsWithID
ZohoCRM_getGlobalPickListFieldAssociations
ZohoCRM_getLayoutById
ZohoCRM_getLayoutRules
ZohoCRM_getLayoutRulesById
ZohoCRM_getLayouts
ZohoCRM_getModuleByApiName
ZohoCRM_getModules
ZohoCRM_getOrganization
ZohoCRM_getSingleGlobalPicklists
ZohoCRM_getWorkflowConfigurations
ZohoCRM_getWorkflowRuleById
ZohoCRM_getWorkflowRules
ZohoCRM_getWorkflowTasks
```

The live server expands the original 14-tool audit proposal with four readback tools:

- `ZohoCRM_getFieldsWithID`
- `ZohoCRM_getLayoutRulesById`
- `ZohoCRM_getFieldUpdates`
- `ZohoCRM_getFieldUpdateById`

These additions close readback gaps for fields, layout rules, and workflow field-update actions.

## `gh_zoho_crm_changes`

This server is not configuration-only. It contains the original 16 organization/configuration tools plus 11 production-record tools.

### Organization Check

```text
ZohoCRM_getOrganization
```

### Configuration Writes

```text
ZohoCRM_createFieldUpdates
ZohoCRM_createFields
ZohoCRM_createGlobalPicklist
ZohoCRM_createModules
ZohoCRM_createWorkflowTasks
ZohoCRM_patchLayoutRules
ZohoCRM_postLayoutRules
ZohoCRM_postWorkflowRule
ZohoCRM_updateField
ZohoCRM_updateFieldUpdateById
ZohoCRM_updateGlobalPicklistById
ZohoCRM_updateLayout
ZohoCRM_updateModuleByApiName
ZohoCRM_updateWorkflowRuleById
ZohoCRM_updateWorkflowTaskById
```

### Production Record Reads

```text
ZohoCRM_executeCOQLQuery
ZohoCRM_getRecord
ZohoCRM_getRecords
ZohoCRM_getRelatedRecord
ZohoCRM_getRelatedRecords
ZohoCRM_getRelatedRecordsCount
ZohoCRM_searchRecords
```

### Production Record Writes

```text
ZohoCRM_createRecords
ZohoCRM_massUpdateRecords
ZohoCRM_updateRecord
ZohoCRM_updateRecords
```

The record tools can retrieve or modify tenant, applicant, property, unit, lease, maintenance, and other business records permitted to the authorizing Zoho user. `ZohoCRM_massUpdateRecords` and `ZohoCRM_updateRecords` can affect multiple production records. This server therefore requires an exact proposed diff and explicit approval before every call.

The current server excludes delete, upsert, merge, conversion, email-send, permission, role, profile, and user-management tools.

## `gh_zoho_books_review`

This server matches the 12-read-tool **Books Financial Overview** template.

```text
ZohoBooks_get_contact
ZohoBooks_get_invoice
ZohoBooks_get_organization
ZohoBooks_list_bank_accounts
ZohoBooks_list_bank_transactions
ZohoBooks_list_bills
ZohoBooks_list_chart_of_accounts
ZohoBooks_list_contacts
ZohoBooks_list_expenses
ZohoBooks_list_invoices
ZohoBooks_list_items
ZohoBooks_list_organizations
```

Although this server has no write tools, it can expose sensitive contact, invoice, bill, expense, bank-account, bank-transaction, and Chart of Accounts data. Before any review, call only `ZohoBooks_get_organization` or `ZohoBooks_list_organizations`, confirm the exact GH Real Estate Books organization, and stop if the target is ambiguous.

## Required Operating Controls

1. Use `gh_zoho_crm_audit` for current-state inspection and post-change verification.
2. Use `gh_zoho_crm_changes` only after Codex shows the target, current state, proposed state, exact tool, exact parameters, expected effect, and rollback approach.
3. Require per-call approval for every `gh_zoho_crm_changes` and `gh_zoho_books_review` invocation.
4. Never approve a broad query or multi-record write without an explicit module, criteria, field set, record count expectation, and dry-run/readback plan.
5. Verify the organization again after any MCP URL, authentication, Zoho account, or server configuration change.
6. Review Zoho's MCP execution log after production writes.
7. Keep all MCP URLs and authentication material out of GitHub, screenshots, prompts, and messages.

## Change-Control Boundary

This file records the configured MCP capability surface. It does not prove that a tool call succeeded, authorize an unreviewed production change, or establish that repository code is deployed. Updating this documentation does not alter Zoho CRM, Zoho Books, Codex configuration, OAuth access, or any live record.
