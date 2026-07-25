# Zoho MCP Capability Catalog

**Verified:** July 25, 2026

**Purpose:** Sanitized technical source of truth for the Zoho-hosted MCP servers and tools GH Real Estate exposes or may expose to Codex.

## Bottom Line

Zoho MCP exposes a much broader tool surface than GH Real Estate should authorize. The official Tool Manual snapshot contains:

- 51 Zoho services and 9,697 tool rows.
- 8 extended Zoho-family services and 836 tool rows.
- 59 services and 10,533 total tool rows.

The authenticated Zoho MCP portal evidence supplied for this review catalogs 19 preconfigured templates:

- 11 Zoho CRM templates.
- 3 Zoho Books templates.
- 1 Zoho Payments template.
- 3 Zoho Mail templates.
- 1 Zoho WorkDrive template.

Those templates are not the same thing as Zoho CRM's separate product-specific set of four pre-built MCP servers.

GH Real Estate currently has ten configured Zoho server entries with 352 per-server tool memberships:

- `gh_zoho_crm_audit` — 18 CRM configuration metadata reads.
- `gh_zoho_crm_changes` — 27 mixed CRM organization, configuration-write, record-read, and record-write tools.
- `gh_zoho_books_accounting_audit` — 166 Books reads and reports.
- `gh_zoho_books_bookkeeping_changes` — 31 routine and high-risk Books writes pending separation.
- `gh_zoho_books_controller` — 58 high-risk accounting and structural configuration writes.
- `gh_zoho_catalyst_webhook_audit` — 15 Catalyst project, function, route, deployment, log, pipeline, and configuration reads.
- `gh_zoho_catalyst_webhook_breakglass` — 5 emergency Catalyst route, environment-variable, and pipeline configuration writes.
- `gh_zoho_catalyst_webhook_release` — 7 approval-gated function, pipeline, deployment, rollback, test, and build actions.
- `gh_zoho_workdrive_audit` — 20 WorkDrive identity, Team Folder, file, version, permission, preview, and download reads.
- `gh_zoho_workdrive_changes` — 5 WorkDrive folder, upload, move, and rename writes.

The 352 memberships contain 351 distinct advertised names because `ZohoCRM_getOrganization` is selected in both CRM servers.

The exact sanitized current state is recorded in [`configured-servers.md`](configured-servers.md).

## Files

| File | Purpose |
|---|---|
| [`configured-servers.md`](configured-servers.md) | Current GH server identifiers, OAuth status, exact Codex-advertised tools, target-verification status, risks, and operating controls |
| [`books-accountant-controls.md`](books-accountant-controls.md) | Books accountant architecture, missing-tool review, correction policy, configuration split, acceptance gates, and no-delete decision |
| [`document-intake-controls.md`](document-intake-controls.md) | WorkDrive/CRM/Catalyst document-intake coverage, missing OCR/event capabilities, conditional tools, safety boundaries, and acceptance tests |
| [`preconfigured-servers.md`](preconfigured-servers.md) | Verified portal template names, descriptions, exact tool memberships, risk review, and evidence gaps |
| [`tool-inventory.md`](tool-inventory.md) | Searchable inventory of all 10,533 exact tool names grouped across 59 services |
| [`recommended-first-server.md`](recommended-first-server.md) | Implemented rollout decision, current boundaries, exclusions, controls, and stop criteria |

## What Is Verified

### Configured GH Servers

The redacted Codex MCP inventories supplied on July 24 and July 25, 2026 confirm:

- The ten exact server identifiers listed above.
- OAuth authentication displayed for each server.
- All 352 per-server tool memberships using the exact names advertised to Codex.
- The `ZohoCRM_`, `ZohoBooks_`, `CatalystbyZoho_`, and `ZohoWorkdrive_` prefixes used by Codex.

Separate acceptance checks confirmed the GH Real Estate production organization for both CRM servers. The supplied evidence does not confirm the target Books organization for any of the three current Books servers, so all three remain acceptance-pending.

The Audit server's module call succeeded but was transport-truncated, and its advertised field projection returned `PATTERN_NOT_MATCHED`. The reported module pairs are confirmed, but completeness is not certified. The Changes server acceptance test confirmed only its target; it did not test a mutation.

The CRM Changes server is not configuration-only. It contains the original organization/configuration set plus seven production-record reads and four production-record writes. The repository records that expanded boundary explicitly.

The supplied evidence also does not confirm the Catalyst organization, project, environment, function targets, or effective grants; the WorkDrive user, team, Team Folder, or effective grants; successful file-binary handoff; or any Catalyst/WorkDrive write. Those five servers remain acceptance-pending.

### Official Tool Catalog

The tool inventory was extracted from the public JavaScript bundle used by Zoho's official MCP Tool Manual. The snapshot bundle has SHA-256:

```text
4914dee106f4510c045d47c0442470f701c3dc92c20972a10a99f6b07de7982b
```

The inventory records exact tool names and per-service counts. Zoho's official manual remains authoritative for tool purpose, parameters, dependencies, scopes, availability, and behavior.

### Preconfigured Templates

The 19 template names and card descriptions were transcribed from authenticated U.S. Zoho MCP portal evidence supplied on July 24, 2026.

Exact tool membership is captured for all 18 CRM, Books, Payments, and Mail templates:

- 11 Zoho CRM templates.
- 3 Zoho Books templates.
- 1 Zoho Payments template.
- 3 Zoho Mail templates.

The WorkDrive template's name and description are captured, but its exact template membership remains `Not Verified`. The separately captured custom WorkDrive Audit and Changes selections do not prove the preconfigured template's composition.

`CRM Data & Metadata Operations` displays 16 tool chips representing 15 unique names because `getModuleByApiName` appears twice. The repository preserves that observation without treating it as a second capability.

Across the 18 verified templates, the evidence contains 217 displayed tool chips, 216 unique per-template memberships, and 177 unique tool names across templates.

Four exact names in the live templates are not present in the dated public Tool Manual bundle: `cloneWorkflowRule`, `add_journal_attachment`, `getMessageAttachmentContent`, and `uploadAttachments`. They are recorded in a separately labeled live-portal overlay in `tool-inventory.md`; they do not alter the bundle-derived 10,533-tool total.

This repository does not infer missing tool membership from a template title or description.

## Important Distinctions

### Supported Service

A service appearing in the Tool Manual means Zoho exposes one or more tools for that service. It does not mean:

- A preconfigured template exists for that service.
- Gabriel's plan, organization, role, or data center enables every tool.
- The tool is safe or appropriate for GH Real Estate.
- The tool should be added to a server.

### Preconfigured Server

A preconfigured server is a Zoho-hosted starter template containing a selected set of tools. Zoho allows tools to be added or removed after creation.

### Custom Zoho-Hosted Server

A custom server created in the Zoho MCP console is still hosted and authenticated by Zoho. It is a no-code allowlist of Zoho tools. It is not a coded server hosted in GitHub or Catalyst.

### Coded MCP Server

A coded MCP server is custom software that wraps APIs with additional validation, business rules, idempotency, approval gates, and audit behavior. The current native servers are adequate for supervised, individually approved calls after acceptance. Professional-grade automated Books posting requires a narrow coded write layer to bind the organization, enforce immutable plans and allowed payloads, prevent stale/duplicate writes, persist returned IDs in a durable ledger, and resolve ambiguous timeouts. A narrow evidence wrapper is also justified if required bill, expense, receipt, or journal documents remain unavailable through native MCP.

The current WorkDrive, CRM, and Catalyst selections cover supervised document discovery, filing, record matching, single-record updates, link storage, and controlled function invocation. They do not provide deterministic full-PDF/OCR extraction, hashing, malware scanning, or an automatic event scheduler. The catalog does contain conditional Catalyst cron/job-pool tools, but the current servers do not select them. Treat OCR and document validation as a narrow processor gap and scheduling as an explicit design/selection decision rather than adding broad WorkDrive or CRM authority; see [`document-intake-controls.md`](document-intake-controls.md).

## Current Product Gaps

The July 24 Tool Manual snapshot does not list the following GH/Sylvara applications as MCP-ready services:

- Zoho Contracts.
- Zoho Flow.
- Zoho Forms.
- Zoho Sites.
- Zoho Checkout.

Do not assume that a tool exists merely because the underlying product has a REST API.

## Source Hierarchy

1. Current official Zoho MCP Tool Manual and product-specific API/reference documentation for tool behavior and supported capabilities.
2. Current official Zoho help and administration documentation.
3. Authenticated live Codex and Zoho MCP metadata for the exact GH server identifiers, advertised names, selected composition, organization, and environment.
4. Approved GH policy and current repository runtime evidence.
5. These dated catalog documents.

When sources conflict, use the higher-authority source within the fact being evaluated and update the affected reference. For example, official documentation controls tool behavior, while authenticated live metadata establishes which exact prefixed names and selections the current GH servers expose. An official Zoho community announcement says five CRM pre-built servers are available but names only four, while the current CRM developer overview explicitly groups the capability into four. This catalog treats the developer overview as the current product-specific source.

## Official Sources

- [Zoho MCP Tool Guide](https://help.zoho.com/portal/en/kb/mcp/mcp-tool-manual/articles/zoho-mcp-tool-guide)
- [Zoho MCP Tool Manual](https://zoho-mcp-manual-tool-guide.onslate.in/)
- [Zoho MCP Implementation Guide](https://help.zoho.com/portal/en/kb/mcp/implementation-guide/articles/zoho-mcp-implementation-guide)
- [Supported Zoho Services](https://www.zoho.com/mcp/services/zoho-services.html)
- [Zoho CRM MCP Overview](https://www.zoho.com/crm/developer/docs/mcp/overview.html)
- [Zoho CRM MCP FAQ](https://www.zoho.com/crm/developer/docs/mcp/faqs.html)

## Refresh Rule

Recheck this catalog before enabling a new service, after Zoho changes a template or GH changes a server, or at least quarterly while the MCP product is changing rapidly. A refresh must record:

- Review date.
- Manual bundle hash.
- Service and tool counts.
- Current GH server identifiers, OAuth status, and exact Codex-advertised tool names.
- Target-organization acceptance status for every configured server.
- Portal template names and descriptions.
- Exact tool membership from every template modal being considered.
- Any plan, organization, role, scope, or data-center limitation.

Never place an MCP server URL, secure API key, OAuth token, organization ID, tenant record, accounting record, or raw portal response in this public repository.
