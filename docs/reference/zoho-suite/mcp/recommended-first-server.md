# Recommended First Zoho MCP Server

**Decision:** Create one custom, Zoho-hosted, read-only server named **GH CRM Configuration Audit**.

This is a custom tool selection in the Zoho MCP console. It is not a coded MCP server, new GitHub service, Catalyst deployment, browser bot, or all-Zoho super-agent.

## Why This Wins

The immediate objective is to let Codex inspect GH Real Estate's CRM configuration before proposing controlled changes.

None of the 19 captured preconfigured templates matches that boundary:

- **CRM Data & Metadata Operations** contains 16 displayed tool chips / 15 unique tools. It mixes four production-record writes, record reads, user data, and configuration metadata, while omitting several layout, picklist, and workflow audit tools.
- **CRM Automation & Workflows** contains 17 tools, including rule, field-update, and email-notification creation, updates, reordering, cloning, and deletion.
- **CommandCenter CRM Actions** contains nine tools that can update journeys and stages and add automation functions.
- **Books Financial Overview** contains 12 read tools and is the safest verified preconfigured template, but it addresses accounting review rather than CRM configuration.
- **Mail Reading & Search** exposes message and attachment content and is not strictly read-only because it includes `flagMessages`.

A custom read-only server exposes only the metadata needed for the audit and keeps tenant/applicant records, financial records, communications, and destructive tools out of scope.

## Exact Initial Allowlist

| Tool | Purpose |
|---|---|
| `getOrganization` | Confirm the connected CRM organization before doing any other work. |
| `getModules` | Inventory standard and custom modules and their capabilities. |
| `getModuleByApiName` | Retrieve full metadata for one module. |
| `getFields` | Inventory module fields and field metadata. |
| `getLayouts` | List layouts available for a module. |
| `getLayoutById` | Inspect one layout in detail. |
| `getLayoutRules` | Inspect conditional layout rules. |
| `getBulkGlobalPicklists` | Inventory global picklists. |
| `getSingleGlobalPicklists` | Inspect one global picklist in detail. |
| `getGlobalPickListFieldAssociations` | Identify where a global picklist is used. |
| `getWorkflowRules` | Inventory workflow rules. |
| `getWorkflowRuleById` | Inspect one workflow rule. |
| `getWorkflowConfigurations` | Retrieve workflow configuration metadata. |
| `getWorkflowTasks` | Inventory workflow task actions. |

If Zoho uses a slightly different capitalization or spelling in the live tool picker, the live official tool entry controls. Do not substitute a similarly named write tool.

## Explicit Exclusions

Do not add:

- Any record-read tool, including `getRecords`, `getRecord`, `searchRecords`, `executeCOQLQuery`, or `getRelatedRecords`.
- Any record-create, update, upsert, merge, convert, delete, or bulk tool.
- Any field, module, layout, global-picklist, workflow, Blueprint, role, profile, permission, user, portal-user, or organization write tool.
- Email, notification, call, task, event, note, or attachment tools.
- Zoho Books, WorkDrive, Sign, Payments, Mail, or CommandCenter tools.
- Any tool whose exact behavior is not understood from the official manual.

## First Use

Use the server for one read-only audit:

1. Confirm the connected organization.
2. Inventory modules.
3. Inventory fields and layouts for the GH modules currently under review.
4. Inventory global picklists and workflow rules.
5. Produce a sanitized current-state summary.
6. Produce an exact proposed before-and-after change plan.
7. Identify configuration that MCP cannot inspect or change.
8. Make no Zoho writes.

Do not store organization IDs, user IDs, raw API responses, tenant/applicant records, emails, phone numbers, addresses, or other private data in GitHub.

## Rollout Order

1. **GH CRM Configuration Audit** — custom Zoho-hosted, read-only.
2. **GH CRM Configuration Changes** — separate custom server, only after the audit; add one approved write class at a time.
3. **GH Books Review** — use the verified 12-tool **Books Financial Overview** template only after the CRM pilot.
4. **GH WorkDrive Read** — defer until a concrete recurring document workflow exists and the exact template modal is captured.

Do not convert the read-only audit server into a write-capable server. Keeping read and write servers separate preserves a clear permission boundary and makes the Codex tool list easier to reason about.

## First Preconfigured Server

If the question is limited to preconfigured templates, **Books Financial Overview** is the first one worth creating. Its captured composition contains only 12 `list_*` and `get_*` tools:

- It is still second in the overall rollout because accounting review is not the immediate objective.
- It must remain separate from CRM.
- It may read sensitive contacts, invoices, bank accounts, and transactions.
- It must use the correct GH Real Estate Books organization, Authorization on Demand, and Always Ask in Codex.
- It must not be expanded with invoice, journal, payment, refund, Chart of Accounts, or deletion tools.

Do not use **Accountant Management System** as a shortcut. Its 67 tools include journal and Chart of Accounts creation, updates, and deletions, base-currency adjustments, projects, users, and custom fields.

## Approval and Authorization

- Use **Authorization on Demand** for individual accountability.
- Keep Codex tool approval at **Always Ask** during the pilot.
- Confirm the exact GH Real Estate organization before every first session after authentication changes.
- Prefer a CRM Sandbox if the MCP connection clearly identifies it. If the target environment is ambiguous, stop.
- Review Zoho MCP logs after the audit. Zoho currently retains MCP logs for 30 days.

## Time and Capital Allocation

- Capital: **$0**.
- Connection and read-only audit: **maximum four hours**.
- Any further cataloging or server design: only after the first audit produces a concrete implementation decision.
- MCP work remains subordinate to urgent GH safety, tenant, legal, and cash obligations and to Sylvara customer acquisition.

## Continue Criteria

Continue only if all are true:

- The connected organization is unambiguous.
- The server exposes only the approved 14 read tools.
- No tenant, applicant, accounting, email, file, or contract records are returned.
- The module, field, layout, picklist, and workflow inventory matches the Zoho interface.
- Zoho's MCP log records the expected user and tool calls.
- The audit produces at least one useful configuration decision or removes a material amount of manual UI work.

## Kill Criteria

Stop and do not add write tools if any are true:

- The target organization or environment is ambiguous.
- A supposedly read-only tool returns unnecessary business records or PII.
- Tool approvals or Zoho permissions do not enforce the expected boundary.
- Layout, picklist, or workflow metadata is materially incomplete.
- The first verified audit cannot be completed within four hours.
- The work becomes general Zoho exploration rather than resolving an approved configuration backlog.

## What To Ignore

- A single cross-suite GH Real Estate server.
- A coded MCP wrapper before a native-tool gap is proven.
- Broad Books authority.
- Contact merging or deletion.
- Autonomous emails.
- WorkDrive management.
- Zoho Payments or refund operations.
- Zoho Contracts automation through MCP; Zoho Contracts is not listed in the current Tool Manual.
- Sylvara MCP product development before repeated paid demand.
