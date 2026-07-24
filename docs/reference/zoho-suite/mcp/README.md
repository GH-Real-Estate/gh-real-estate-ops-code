# Zoho MCP Capability Catalog

**Verified:** July 24, 2026  
**Purpose:** Sanitized technical source of truth for deciding which Zoho-hosted MCP servers and tools GH Real Estate should expose to Codex.

## Bottom Line

Zoho MCP currently exposes a much broader tool surface than GH Real Estate should authorize. The official Tool Manual snapshot contains:

- 51 Zoho services and 9,697 tool rows.
- 8 extended Zoho-family services and 836 tool rows.
- 59 services and 10,533 total tool rows.

The authenticated Zoho MCP portal captures supplied for this review directly show 15 preconfigured templates:

- 11 Zoho CRM templates.
- 3 Zoho Books templates.
- 1 Zoho WorkDrive template.

Those 15 templates are not the same thing as Zoho CRM's separate product-specific set of four pre-built MCP servers.

## Files

| File | Purpose |
|---|---|
| [`preconfigured-servers.md`](preconfigured-servers.md) | Verified portal template names, descriptions, tool-membership evidence, and risk review |
| [`tool-inventory.md`](tool-inventory.md) | Searchable inventory of all 10,533 exact tool names grouped across 59 services |
| [`recommended-first-server.md`](recommended-first-server.md) | Exact first-server decision, allowlist, exclusions, rollout, and kill criteria |

## What Is Verified

### Official Tool Catalog

The tool inventory was extracted from the public JavaScript bundle used by Zoho's official MCP Tool Manual. The snapshot bundle has SHA-256:

```text
4914dee106f4510c045d47c0442470f701c3dc92c20972a10a99f6b07de7982b
```

The inventory records exact tool names and per-service counts. Zoho's official manual remains authoritative for tool purpose, parameters, dependencies, scopes, availability, and behavior.

### Preconfigured Templates

The 15 template names and card descriptions were transcribed from the authenticated U.S. Zoho MCP portal captures supplied on July 24, 2026.

Only **CRM Data & Metadata Operations** had its tool modal captured. It shows 16 tool chips representing 15 unique tools because `getModuleByApiName` appears twice. Exact tool membership for the other 14 templates is not published in the indexed official documentation and was not visible in the supplied captures.

This repository labels that gap explicitly. It does not reverse-engineer or invent template membership.

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

A coded MCP server is custom software that wraps APIs with additional validation, business rules, idempotency, approval gates, and audit behavior. GH Real Estate does not currently need one.

## Current Product Gaps

The July 24 Tool Manual snapshot does not list the following GH/Sylvara applications as MCP-ready services:

- Zoho Contracts.
- Zoho Flow.
- Zoho Forms.
- Zoho Sites.
- Zoho Checkout.

Do not assume that a tool exists merely because the underlying product has a REST API.

## Source Hierarchy

1. Live authenticated Zoho MCP portal modal for the exact template composition.
2. Official Zoho MCP Tool Manual for service and tool definitions.
3. Official product-specific MCP or API documentation.
4. This repository's security, risk, and implementation recommendations.

When sources conflict, the live portal and current product developer documentation control. For example, an official Zoho community announcement says five CRM pre-built servers are available but names only four, while the current CRM developer overview explicitly groups the capability into four. This catalog treats the developer overview as the current product-specific source.

## Official Sources

- [Zoho MCP Tool Guide](https://help.zoho.com/portal/en/kb/mcp/mcp-tool-manual/articles/zoho-mcp-tool-guide)
- [Zoho MCP Tool Manual](https://zoho-mcp-manual-tool-guide.onslate.in/)
- [Zoho MCP Implementation Guide](https://help.zoho.com/portal/en/kb/mcp/implementation-guide/articles/zoho-mcp-implementation-guide)
- [Supported Zoho Services](https://www.zoho.com/mcp/services/zoho-services.html)
- [Zoho CRM MCP Overview](https://www.zoho.com/crm/developer/docs/mcp/overview.html)
- [Zoho CRM MCP FAQ](https://www.zoho.com/crm/developer/docs/mcp/faqs.html)

## Refresh Rule

Recheck this catalog before enabling a new service, after Zoho changes a template, or at least quarterly while the MCP product is changing rapidly. A refresh must record:

- Review date.
- Manual bundle hash.
- Service and tool counts.
- Portal template names and descriptions.
- Exact tool membership from every template modal being considered.
- Any plan, organization, role, scope, or data-center limitation.

Never place an MCP server URL, API key, OAuth token, organization ID, tenant record, accounting record, or raw portal response in this public repository.
