# Recommended Zoho MCP Rollout

**Original decision:** Start with a custom, Zoho-hosted, read-only CRM configuration audit server.  
**Current status:** Implemented and expanded as of July 24, 2026.

The sanitized source of truth for the live server identifiers and exact Codex-advertised tools is [`configured-servers.md`](configured-servers.md).

## Current Implementation

| Order | Codex Server ID | Status | Current Boundary |
|---:|---|---|---|
| 1 | `gh_zoho_crm_audit` | Implemented; production acceptance passed | 18 CRM configuration metadata reads |
| 2 | `gh_zoho_crm_changes` | Implemented; production target confirmed | 15 configuration writes, 7 record reads, 4 record writes, and 1 organization check |
| 3 | `gh_zoho_books_review` | Configured; organization acceptance not evidenced | 12 Books financial/contact reads |
| 4 | GH WorkDrive Read | Deferred | Create only for a concrete recurring document workflow after exact tools are verified |

These are custom or adapted Zoho-hosted server allowlists. They are not coded servers hosted in GitHub or Catalyst.

The Audit acceptance test confirmed GH Real Estate and `type: production`. Its module call succeeded but was transport-truncated, and an advertised field projection returned `PATTERN_NOT_MATCHED`; the reported module pairs are confirmed, but inventory completeness is not certified. The Changes server's production target was confirmed without testing a mutation. The Books organization remains unverified in the supplied evidence.

## Why The Audit Server Still Wins

Codex needs a narrow, reliable way to inspect the current CRM configuration before proposing controlled changes. The audit server keeps tenant/applicant records, financial records, communications, and destructive tools outside its boundary while supporting readback for every configuration class currently writable through the Changes server.

No captured preconfigured CRM template matches that boundary:

- **CRM Data & Metadata Operations** mixes production-record reads and writes with configuration metadata.
- **CRM Automation & Workflows** includes workflow creation, updates, reordering, cloning, and deletion.
- **CommandCenter CRM Actions** can update journeys and stages and add automation functions.
- **Books Financial Overview** is read-only but addresses accounting review rather than CRM configuration.
- **Mail Reading & Search** exposes message and attachment content and includes mailbox state changes.

## Current Audit Allowlist

| Tool | Purpose |
|---|---|
| `ZohoCRM_getOrganization` | Confirm the connected CRM organization before other work. |
| `ZohoCRM_getModules` | Inventory standard and custom modules. |
| `ZohoCRM_getModuleByApiName` | Retrieve metadata for one module. |
| `ZohoCRM_getFields` | Inventory module fields and metadata. |
| `ZohoCRM_getFieldsWithID` | Retrieve field metadata with identifiers for exact readback. |
| `ZohoCRM_getLayouts` | List layouts available for a module. |
| `ZohoCRM_getLayoutById` | Inspect one layout. |
| `ZohoCRM_getLayoutRules` | Inventory conditional layout rules. |
| `ZohoCRM_getLayoutRulesById` | Inspect one layout rule. |
| `ZohoCRM_getBulkGlobalPicklists` | Inventory global picklists. |
| `ZohoCRM_getSingleGlobalPicklists` | Inspect one global picklist. |
| `ZohoCRM_getGlobalPickListFieldAssociations` | Identify where a global picklist is used. |
| `ZohoCRM_getWorkflowRules` | Inventory workflow rules. |
| `ZohoCRM_getWorkflowRuleById` | Inspect one workflow rule. |
| `ZohoCRM_getWorkflowConfigurations` | Retrieve workflow configuration metadata. |
| `ZohoCRM_getFieldUpdates` | Inventory workflow field-update actions. |
| `ZohoCRM_getFieldUpdateById` | Inspect one workflow field-update action. |
| `ZohoCRM_getWorkflowTasks` | Inventory workflow task actions. |

The `ZohoCRM_` prefix is part of the exact name advertised to Codex. Zoho's server builder may display the corresponding picker name without that prefix.

## Changes Server Boundary

The original design limited `gh_zoho_crm_changes` to one organization check and 15 configuration writes. The configured server now also contains 11 record operations:

- Seven production-record reads, including COQL, search, single-record, bulk-record, and related-record retrieval.
- Four production-record writes: create, single update, multi-record update, and mass update.

This is production authority, not a test-only sandbox. The current evidence establishes that the tools are configured, but it does not establish whether the 11 record-tool additions were a deliberate permanent boundary or permission drift. They materially increase PII and operational risk. The server has no delete, upsert, merge, conversion, email-send, permission, role, profile, or user-management tools, but the remaining bulk write tools can still cause widespread changes.

Use this sequence for every production change:

1. Audit the exact current configuration or records.
2. Show the target, current state, proposed state, exact write tool, exact parameters, expected record count, expected effect, and rollback approach.
3. Obtain explicit approval for that one tool call.
4. Apply only the approved change.
5. Read back the result through the narrowest available read tool.
6. Review the Zoho MCP execution log.

Do not treat a broad request such as “clean up CRM” as approval for multiple writes.

## Books Review Boundary

`gh_zoho_books_review` implements the 12-read-tool **Books Financial Overview** template. It can read contacts, invoices, bills, expenses, bank accounts, bank transactions, items, and the Chart of Accounts.

Before its first financial review:

1. Call only the organization tool.
2. Confirm the exact GH Real Estate Books organization.
3. Stop if the organization is ambiguous.
4. Keep per-call approval enabled because the server can return PII and financial data.

Do not expand it with invoice, contact, journal, payment, refund, Chart of Accounts, currency-adjustment, project, user, or deletion writes without a separate approved workflow.

## Explicit Exclusions

Do not add:

- Any delete tool.
- CRM upsert, merge, conversion, email-send, user, role, profile, permission, or portal-user tools.
- Books transaction, journal, payment, refund, currency-adjustment, or Chart of Accounts write tools.
- Direct Zoho Sign send, correct, recall, or deletion authority.
- Mail sending or mailbox-management tools.
- Broad WorkDrive write, sharing, or deletion authority.
- Zoho Payments or refund operations.
- A cross-suite GH Real Estate super-server.
- A coded MCP wrapper before a native-tool or policy-enforcement gap is proven.

## Approval And Authorization

- Use individual OAuth/Authorization on Demand rather than shared credentials.
- Require per-call approval for `gh_zoho_crm_changes` and `gh_zoho_books_review`.
- Verify the exact organization after authentication or server configuration changes.
- Keep MCP URLs, API keys, OAuth tokens, organization IDs, raw responses, tenant records, and accounting records out of GitHub.
- Treat repository documentation as an allowlist reference, not proof of live configuration or deployment.

## Continue Criteria

Continue using the current design only while all are true:

- The target organization is unambiguous.
- `gh_zoho_crm_audit` exposes only the approved 18 metadata-read tools.
- Every production write is previewed, approved, bounded, and verified.
- Bulk record operations have explicit criteria and expected counts.
- Books access is limited to a verified GH Real Estate organization.
- Zoho's MCP logs show only the expected user and calls.
- The servers resolve approved GH configuration or operational work instead of creating general exploration.

## Stop Criteria

Stop the affected workflow if any are true:

- The target organization or environment is ambiguous.
- An advertised tool differs from this inventory.
- A read returns unnecessary PII or financial data.
- A proposed query or write is broader than the approved target.
- The expected record count is unknown or materially different.
- Readback cannot verify the result.
- Tool approvals or Zoho permissions do not enforce the expected boundary.

## Time And Capital Guardrail

The MCP infrastructure is sufficient. Do not create more servers unless a specific approved workflow cannot be completed with the current three-server design. MCP work remains subordinate to urgent safety, tenant, legal, cash, and Sylvara customer-acquisition priorities.
