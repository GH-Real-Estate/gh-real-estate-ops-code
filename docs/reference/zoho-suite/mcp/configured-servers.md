# Configured Zoho MCP Servers

**Verified:** July 25, 2026

**Scope:** Sanitized current-state inventory of the Zoho MCP servers configured for GH Real Estate in Codex.

## Evidence And Status

This inventory is based on:

- Redacted Codex MCP server inventories supplied on July 24 and July 25, 2026, including the current ten-server Zoho snapshot.
- A successful `ZohoCRM_getOrganization` acceptance check against the GH Real Estate production organization.
- A successful read-only CRM module inventory through `gh_zoho_crm_audit`.
- A successful organization-only target check through `gh_zoho_crm_changes`.

The July 25 inventory supersedes the earlier 12-tool `gh_zoho_books_review` capture. It shows three custom Books servers with 255 selected tool memberships. The evidence confirms server identifiers, advertised tool names, and OAuth status, but it does not prove which Books organization any of the three servers targets, that every OAuth grant succeeded, or that a write works. Each Books server therefore remains acceptance-pending.

The current July 25 snapshot also adds three Catalyst webhook-administration servers with 27 selected tool memberships and two WorkDrive servers with 25 selected tool memberships. Their identifiers, exact advertised tool names, counts, and OAuth display are captured. The evidence does not prove the target Catalyst organization/project/environment, the target WorkDrive team/Team Folder, effective OAuth grants, binary file handoff, or successful read/write execution. All five new servers remain acceptance-pending.

The CRM Audit server's `ZohoCRM_getModules` call succeeded, but the response was transport-truncated and an advertised field projection returned `PATTERN_NOT_MATCHED`; the captured module pairs are confirmed, but completeness is not certified. The CRM Changes target check did not test a mutation.

No MCP URL, secure API key, token, organization ID, record payload, tenant information, accounting data, or private document belongs in this repository.

## Current Server Summary

| Codex Server ID | Zoho Service | Auth | Tools | Access Class | Target Status |
|---|---|---:|---:|---|---|
| `gh_zoho_crm_audit` | Zoho CRM | OAuth | 18 | Configuration metadata reads | GH Real Estate production verified |
| `gh_zoho_crm_changes` | Zoho CRM | OAuth | 27 | Configuration writes plus production record reads and writes | GH Real Estate production verified |
| `gh_zoho_books_accounting_audit` | Zoho Books | OAuth | 166 | Financial, subledger, bank, report, automation, and configuration reads | Organization not verified in supplied evidence |
| `gh_zoho_books_bookkeeping_changes` | Zoho Books | OAuth | 31 | Routine writes mixed with credits, refunds, journals, recurring schedules, sales receipts, and fixed assets | Organization not verified in supplied evidence |
| `gh_zoho_books_controller` | Zoho Books | OAuth | 58 | High-risk accounting actions mixed with structural configuration writes | Organization not verified in supplied evidence |
| `gh_zoho_catalyst_webhook_audit` | Catalyst by Zoho | OAuth | 15 | Project, function, deployment, route, environment-name, pipeline, log, cache, and segment reads | Organization/project/environment not verified in supplied evidence |
| `gh_zoho_catalyst_webhook_breakglass` | Catalyst by Zoho | OAuth | 5 | API Gateway, environment-variable, and pipeline configuration writes | Organization/project/environment and writes not acceptance-tested |
| `gh_zoho_catalyst_webhook_release` | Catalyst by Zoho | OAuth | 7 | Function update/invocation, pipeline execution, deployment, rollback, test, and build-cancel actions | Organization/project/environment and writes not acceptance-tested |
| `gh_zoho_workdrive_audit` | Zoho WorkDrive | OAuth | 20 | Identity, team, Team Folder, file, version, change-feed, permission, preview, and download reads | User/team/Team Folder and binary handoff not verified in supplied evidence |
| `gh_zoho_workdrive_changes` | Zoho WorkDrive | OAuth | 5 | Folder creation, upload/status, move, and rename writes | User/team/Team Folder and writes not acceptance-tested |

The ten Zoho servers expose 352 per-server tool memberships in total and 351 distinct advertised names; `ZohoCRM_getOrganization` is selected in both CRM servers. Tool names below are the exact names advertised to Codex. Zoho's server builder may display the same tools without the `ZohoCRM_`, `ZohoBooks_`, `CatalystbyZoho_`, or `ZohoWorkdrive_` prefix.

The operating decision, missing-tool review, correction policy, and production acceptance gates for the Books servers are maintained in [`books-accountant-controls.md`](books-accountant-controls.md).

The WorkDrive/CRM/Catalyst document-intake coverage, remaining OCR and event-trigger gaps, deliberate exclusions, and acceptance tests are maintained in [`document-intake-controls.md`](document-intake-controls.md).

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

## `gh_zoho_catalyst_webhook_audit`

This is the read-only Catalyst project, API Gateway, function, deployment, pipeline, log, environment-name, cache, and segment inspection boundary.

```text
CatalystbyZoho_Get_API_route
CatalystbyZoho_Get_Cache_Item_Value
CatalystbyZoho_Get_Deployment
CatalystbyZoho_Get_Function
CatalystbyZoho_Get_Logs
CatalystbyZoho_Get_Pipeline_By_Id
CatalystbyZoho_Get_Project_By_Id
CatalystbyZoho_List_All_API_route
CatalystbyZoho_List_All_Deployments
CatalystbyZoho_List_All_Env_Variables
CatalystbyZoho_List_All_Functions
CatalystbyZoho_List_All_Organizations
CatalystbyZoho_List_All_Pipelines
CatalystbyZoho_List_All_Projects
CatalystbyZoho_List_All_Segments
```

Environment-variable reads can reveal names and deployment structure even when values are not returned. Keep raw responses, project identifiers, routes, logs, and configuration out of GitHub.

## `gh_zoho_catalyst_webhook_breakglass`

This is an emergency configuration boundary for API Gateway routes, environment variables, and pipelines. It must remain disconnected or otherwise unavailable during routine operation.

```text
CatalystbyZoho_Configure_API_Gateway_Route
CatalystbyZoho_Create_Env_Variables
CatalystbyZoho_Create_Pipeline
CatalystbyZoho_Update_Environment_Variable
CatalystbyZoho_Update_Pipeline
```

These tools can change authentication/routing, runtime configuration, and release orchestration. MCP environment-variable calls are nonsecret-only; enter secret values directly in Zoho's secret UI or approved vault outside Codex/MCP. Every call requires exact target readback, a reviewed replacement payload, a secret-safe rollback plan, explicit approval, and immediate Audit verification.

## `gh_zoho_catalyst_webhook_release`

This is the approval-gated Catalyst release and function-execution boundary.

```text
CatalystbyZoho_Cancel_Build
CatalystbyZoho_Execute_Automation_Test
CatalystbyZoho_Execute_Function_Via_POST
CatalystbyZoho_Execute_Pipeline_Manually
CatalystbyZoho_Redeploy_a_deployment
CatalystbyZoho_Rollback_Build
CatalystbyZoho_Update_Function
```

`CatalystbyZoho_Execute_Function_Via_POST` is generic function invocation, not a dedicated OCR, webhook, or document-validation tool. Invoke only a preverified allowlisted function with a bounded sanitized payload. Release and rollback tools require exact project/environment/deployment identity, current-state inspection, expected revision, post-action logs, and readback.

## `gh_zoho_workdrive_audit`

This is the read-only WorkDrive identity, routing, file, version, permission, preview, change-feed, and download boundary.

```text
ZohoWorkdrive_Breadcrumbs_Of_File
ZohoWorkdrive_Download_Server_File
ZohoWorkdrive_Download_Server_File_Version
ZohoWorkdrive_Fetch_Files_Folders
ZohoWorkdrive_File_Property
ZohoWorkdrive_Get_All_Team_Folders
ZohoWorkdrive_Get_All_Teams_Of_User
ZohoWorkdrive_Get_Current_Team_User
ZohoWorkdrive_Get_File_List
ZohoWorkdrive_Get_File_Preview
ZohoWorkdrive_Get_List_Of_Recent_Changes
ZohoWorkdrive_Get_Shared_Links
ZohoWorkdrive_Get_Shared_Users
ZohoWorkdrive_Get_Start_Token
ZohoWorkdrive_Get_Team_Folder_Setting
ZohoWorkdrive_Get_Team_Folder_Shared_Users
ZohoWorkdrive_Get_Team_Folders_Info
ZohoWorkdrive_Get_User_Info
ZohoWorkdrive_Get_Version
ZohoWorkdrive_Search_Records
```

This selection covers the complete read side of the proposed application, inspection, condition-report, and lease filing workflow. Before retrieving any private file, verify the integration user, team, Team Folder, resource ID, version, business purpose, and effective sharing. A successful binary download tool call is not yet evidence that Codex receives a usable PDF artifact; that handoff requires a controlled acceptance test.

## `gh_zoho_workdrive_changes`

This is the narrow WorkDrive filing boundary for folder creation, file upload, upload-status verification, move, and rename.

```text
ZohoWorkdrive_Create_Folder
ZohoWorkdrive_Upload_File
ZohoWorkdrive_Upload_Status
ZohoWorkdrive_moveFileOrFolder
ZohoWorkdrive_renameFileOrFolder
```

The server intentionally excludes copy, new-version upload, generic file update, trash, permanent deletion, external-share creation/update, Team Folder administration, and membership/role changes. Restrict its OAuth principal to the approved GH Real Estate intake and leasing Team Folder. Require explicit parent/resource IDs, collision policy, source/resource operation key, expected destination, and Audit readback for every write.

## `gh_zoho_books_accounting_audit`

This is the Books read-only analysis boundary. Its 166 selected tools cover core ledgers, subledgers, bank activity and reconciliations, fixed assets, financial reports, automation history, and configuration metadata.

```text
ZohoBooks_get_account_transactions_report
ZohoBooks_get_account_type_summary_report
ZohoBooks_get_account_type_transactions_report
ZohoBooks_get_accounting_period_transaction_lock
ZohoBooks_get_activity_logs_report
ZohoBooks_get_all_tag_options
ZohoBooks_get_ap_aging_details_report
ZohoBooks_get_ap_aging_summary_report
ZohoBooks_get_ar_aging_details_report
ZohoBooks_get_ar_aging_summary_report
ZohoBooks_get_balance_sheet_report
ZohoBooks_get_bank_account
ZohoBooks_get_bank_account_balance
ZohoBooks_get_bank_account_balances
ZohoBooks_get_bank_account_rule
ZohoBooks_get_bank_account_statement_summary
ZohoBooks_get_bank_charges_report
ZohoBooks_get_bank_reconciliation
ZohoBooks_get_bank_reconciliation_document
ZohoBooks_get_bank_transaction
ZohoBooks_get_base_currency_adjustment
ZohoBooks_get_bill
ZohoBooks_get_bill_comments
ZohoBooks_get_bill_details_report
ZohoBooks_get_budget_vs_actuals_report
ZohoBooks_get_cash_flow_forecast_report
ZohoBooks_get_cash_flow_report
ZohoBooks_get_chart_of_account
ZohoBooks_get_contact
ZohoBooks_get_contact_unused_credits
ZohoBooks_get_credit_note
ZohoBooks_get_credit_note_refund
ZohoBooks_get_current_user
ZohoBooks_get_custom_function
ZohoBooks_get_custom_function_history
ZohoBooks_get_customer_balance_summary_report
ZohoBooks_get_customer_payment
ZohoBooks_get_customer_payment_refund
ZohoBooks_get_customer_payments_report
ZohoBooks_get_day_book_report
ZohoBooks_get_estimate
ZohoBooks_get_exception_report
ZohoBooks_get_expense
ZohoBooks_get_expense_details_report
ZohoBooks_get_expenses_by_category_report
ZohoBooks_get_fields_meta
ZohoBooks_get_fixed_asset
ZohoBooks_get_fixed_asset_forecast
ZohoBooks_get_fixed_asset_history
ZohoBooks_get_fixed_asset_register_report
ZohoBooks_get_fixed_asset_type_list
ZohoBooks_get_general_ledger_details_report
ZohoBooks_get_general_ledger_report
ZohoBooks_get_invoice
ZohoBooks_get_invoice_details_report
ZohoBooks_get_item
ZohoBooks_get_journal
ZohoBooks_get_journal_report
ZohoBooks_get_last_imported_bank_statement
ZohoBooks_get_matching_bank_transactions
ZohoBooks_get_movement_of_equity_report
ZohoBooks_get_opening_balance
ZohoBooks_get_organization
ZohoBooks_get_payable_details_report
ZohoBooks_get_payable_summary_report
ZohoBooks_get_profit_and_loss_report
ZohoBooks_get_purchase_order
ZohoBooks_get_purchases_by_vendor_report
ZohoBooks_get_ratio_analysis_report
ZohoBooks_get_realized_gain_or_loss_report
ZohoBooks_get_receivable_details_report
ZohoBooks_get_receivable_summary_report
ZohoBooks_get_recurring_bill
ZohoBooks_get_recurring_expense
ZohoBooks_get_recurring_invoice
ZohoBooks_get_recurring_journal
ZohoBooks_get_register_bulk_action_history
ZohoBooks_get_report_1099_vendor_payments_report
ZohoBooks_get_reports_metadata
ZohoBooks_get_retainer_invoice
ZohoBooks_get_sales_order
ZohoBooks_get_sales_receipt
ZohoBooks_get_sales_summary_report
ZohoBooks_get_tags
ZohoBooks_get_transaction_journal_view
ZohoBooks_get_transaction_lock
ZohoBooks_get_trial_balance_report
ZohoBooks_get_unrealized_gain_or_loss_report
ZohoBooks_get_vendor_balance_summary_report
ZohoBooks_get_vendor_credit
ZohoBooks_get_vendor_credit_refund
ZohoBooks_get_vendor_payment
ZohoBooks_get_vendor_payment_refund
ZohoBooks_get_vendor_payments_report
ZohoBooks_get_webhook
ZohoBooks_get_webhook_history
ZohoBooks_get_workflow
ZohoBooks_get_workflow_log_details
ZohoBooks_get_workflow_logs_report
ZohoBooks_list_bank_account_balances
ZohoBooks_list_bank_account_match_filters
ZohoBooks_list_bank_account_rules
ZohoBooks_list_bank_account_statements
ZohoBooks_list_bank_account_transactions
ZohoBooks_list_bank_accounts
ZohoBooks_list_bank_reconciliations
ZohoBooks_list_bank_transactions
ZohoBooks_list_base_currency_adjustment_accounts
ZohoBooks_list_base_currency_adjustments
ZohoBooks_list_bill_payments
ZohoBooks_list_bills
ZohoBooks_list_chart_of_account_transactions
ZohoBooks_list_chart_of_accounts
ZohoBooks_list_child_expenses_of_recurring_expense
ZohoBooks_list_child_journals
ZohoBooks_list_contacts
ZohoBooks_list_credit_note_refunds_of_all_credit_notes
ZohoBooks_list_credit_notes
ZohoBooks_list_currencies
ZohoBooks_list_custom_fields_simple
ZohoBooks_list_custom_function_histories
ZohoBooks_list_custom_functions
ZohoBooks_list_customer_payment_refunds
ZohoBooks_list_customer_payments
ZohoBooks_list_customers
ZohoBooks_list_estimates
ZohoBooks_list_exchange_rates
ZohoBooks_list_expense_comments
ZohoBooks_list_expenses
ZohoBooks_list_fixed_assets
ZohoBooks_list_invoice_credits_applied
ZohoBooks_list_invoice_payments
ZohoBooks_list_invoices
ZohoBooks_list_items
ZohoBooks_list_journals
ZohoBooks_list_locations
ZohoBooks_list_opening_balance_details
ZohoBooks_list_opening_balance_transactions
ZohoBooks_list_organizations
ZohoBooks_list_purchase_orders
ZohoBooks_list_recurring_bill_history
ZohoBooks_list_recurring_bills
ZohoBooks_list_recurring_expense_history
ZohoBooks_list_recurring_expenses
ZohoBooks_list_recurring_invoice_child_invoices
ZohoBooks_list_recurring_invoice_history
ZohoBooks_list_recurring_invoices
ZohoBooks_list_recurring_journals
ZohoBooks_list_register_transactions
ZohoBooks_list_retainer_invoices
ZohoBooks_list_sales_orders
ZohoBooks_list_sales_receipts
ZohoBooks_list_tax_authorities
ZohoBooks_list_tax_exemptions
ZohoBooks_list_taxes
ZohoBooks_list_transaction_locks
ZohoBooks_list_unreviewed_bank_statements
ZohoBooks_list_vendor_credit_refunds_of_all_vendor_credits
ZohoBooks_list_vendor_credits
ZohoBooks_list_vendor_payment_refunds
ZohoBooks_list_vendor_payments
ZohoBooks_list_vendors
ZohoBooks_list_webhook_histories
ZohoBooks_list_webhooks
ZohoBooks_list_workflow_logs
ZohoBooks_list_workflows
```

The selection is broad enough for ledger and subledger review, but selection alone does not establish complete pagination, attachment access, a correct organization target, or accounting correctness.

## `gh_zoho_books_bookkeeping_changes`

This is the intended routine Books write boundary, but its current 31-tool selection also contains high-risk credits, refund classifications, sales receipts, journals, recurring schedules, and fixed-asset writes.

```text
ZohoBooks_add_bank_reconciliation_attachment
ZohoBooks_add_journal_comment
ZohoBooks_categorize_as_credit_note_refunds
ZohoBooks_categorize_as_vendor_credit_refunds
ZohoBooks_categorize_as_vendor_payment_refund
ZohoBooks_categorize_bank_transaction
ZohoBooks_categorize_bank_transaction_as_customer_payment
ZohoBooks_categorize_bank_transaction_as_expense
ZohoBooks_categorize_bank_transaction_as_vendor_payment
ZohoBooks_create_bill
ZohoBooks_create_credit_note
ZohoBooks_create_expense
ZohoBooks_create_fixed_asset
ZohoBooks_create_invoice
ZohoBooks_create_journal
ZohoBooks_create_recurring_bill
ZohoBooks_create_recurring_expense
ZohoBooks_create_sales_receipt
ZohoBooks_create_vendor_credit
ZohoBooks_match_bank_transaction
ZohoBooks_save_bank_reconciliation_draft
ZohoBooks_update_bill
ZohoBooks_update_credit_note
ZohoBooks_update_expense
ZohoBooks_update_fixed_asset
ZohoBooks_update_invoice
ZohoBooks_update_journal
ZohoBooks_update_recurring_bill
ZohoBooks_update_recurring_expense
ZohoBooks_update_sales_receipt
ZohoBooks_update_vendor_credit
```

`ZohoBooks_add_journal_attachment`, `ZohoBooks_get_organization`, and `ZohoBooks_get_current_user` are not in this selection. Confirm the exact live picker entries and add all three. Move the 17 high-risk tools enumerated in [`books-accountant-controls.md`](books-accountant-controls.md) to Controller. The intended final Bookkeeping selection contains 17 tools.

## `gh_zoho_books_controller`

This server contains 58 selected tools. It currently mixes high-risk accounting corrections and close actions with structural organization configuration. That composition is functional but too broad for routine availability.

```text
ZohoBooks_apply_credit_note_to_invoice
ZohoBooks_apply_credits_to_bill
ZohoBooks_approve_journal
ZohoBooks_cancel_write_off_invoice
ZohoBooks_create_bank_account
ZohoBooks_create_bank_account_rule
ZohoBooks_create_bank_reconciliation
ZohoBooks_create_bank_transaction
ZohoBooks_create_base_currency_adjustment
ZohoBooks_create_chart_of_account
ZohoBooks_create_contact
ZohoBooks_create_credit_note_refund
ZohoBooks_create_currency
ZohoBooks_create_custom_field
ZohoBooks_create_customer_payment
ZohoBooks_create_customer_payment_refund
ZohoBooks_create_exchange_rate
ZohoBooks_create_item
ZohoBooks_create_location
ZohoBooks_create_opening_balance
ZohoBooks_create_tag
ZohoBooks_create_tax
ZohoBooks_create_vendor_payment
ZohoBooks_exclude_bank_transaction
ZohoBooks_mark_bill_void
ZohoBooks_mark_credit_note_void
ZohoBooks_mark_fixed_asset_active
ZohoBooks_mark_fixed_asset_draft
ZohoBooks_mark_invoice_void
ZohoBooks_mark_journal_published
ZohoBooks_mark_vendor_credit_void
ZohoBooks_refund_excess_vendor_payment
ZohoBooks_refund_vendor_credit
ZohoBooks_restore_bank_transaction
ZohoBooks_reverse_journal
ZohoBooks_sell_fixed_asset
ZohoBooks_submit_journal_for_approval
ZohoBooks_uncategorize_bank_transaction
ZohoBooks_unmatch_bank_transaction
ZohoBooks_update_bank_account
ZohoBooks_update_bank_account_rule
ZohoBooks_update_bank_reconciliation
ZohoBooks_update_chart_of_account
ZohoBooks_update_contact
ZohoBooks_update_currency
ZohoBooks_update_custom_field
ZohoBooks_update_customer_payment
ZohoBooks_update_exchange_rate
ZohoBooks_update_item
ZohoBooks_update_location
ZohoBooks_update_opening_balance
ZohoBooks_update_tag
ZohoBooks_update_tag_options
ZohoBooks_update_tax
ZohoBooks_update_transaction_lock
ZohoBooks_update_vendor_payment
ZohoBooks_write_off_fixed_asset
ZohoBooks_write_off_invoice
```

The server has no named delete tool. It also lacks `ZohoBooks_get_organization` and `ZohoBooks_get_current_user`; add those two read-only safety tools before using it. Move structural configuration into Configuration Admin, move the high-risk Bookkeeping tools into Controller, add recurring stop/resume tools, and remove journal approval, journal publication, and transaction-lock updates from MCP. The intended final Controller selection contains 53 tools.

The current write selection nevertheless contains actions with deletion-like accounting effect or material blast radius, including voiding, write-off, reversal, unmatching, uncategorizing, excluding, opening-balance changes, Chart of Accounts changes, and transaction-lock changes. Selection of those tools is not accounting approval.

## Required Operating Controls

1. Apply the exact 166/17/53/27 target selections in [`books-accountant-controls.md`](books-accountant-controls.md) before production accounting.
2. Use `gh_zoho_books_accounting_audit`, `gh_zoho_catalyst_webhook_audit`, `gh_zoho_crm_audit`, and `gh_zoho_workdrive_audit` for system/configuration current-state inspection and supported readback. CRM record-level post-write verification must use `gh_zoho_crm_changes` → `ZohoCRM_getRecord`; CRM Audit has metadata tools only.
3. Treat organization/current-user/project/team reads as detective checks only. Bind each write path to the expected organization, data center, project/environment, and Team Folder; reject mismatched caller-supplied targets.
4. Require an immutable short-lived plan, single-use approval, stale-state reread, idempotency key, durable write ledger, returned-ID persistence, ambiguous-timeout readback, and post-write reconciliation.
5. Keep all native writes supervised until the documented controls exist. Keep Books Controller/Configuration Admin and Catalyst Breakglass unavailable by default.
6. Keep journal approval, journal publication, transaction-lock mutation, public WorkDrive sharing, WorkDrive deletion, and unrestricted Catalyst function invocation outside routine MCP operation.
7. Never approve a broad query, bulk action, or write without an explicit entity/resource, period where applicable, criteria, field set, expected count, and readback plan.
8. Do not treat bank-feed exclusion as archival or as a substitute for correcting the general ledger.
9. Verify the organization, OAuth identity, project/environment, WorkDrive user/team/Team Folder, and effective grants after any MCP URL, authentication, account, role, or server-configuration change.
10. Review Zoho's MCP execution logs and the workflow's durable write ledger after production writes.
11. Keep MCP URLs, authentication material, organization/project/team/resource IDs, raw financial or tenant responses, private documents, and source evidence out of GitHub.

## Change-Control Boundary

This file records the configured MCP capability surface. It does not prove that a tool call succeeded, authorize an unreviewed production change, or establish that repository code is deployed. Updating this documentation does not alter Zoho CRM, Zoho Books, Codex configuration, OAuth access, or any live record.
