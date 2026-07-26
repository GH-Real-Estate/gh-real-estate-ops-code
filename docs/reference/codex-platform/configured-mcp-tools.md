# Codex Runtime Capability Snapshot

**Verified:** July 25, 2026

**Purpose:** Sanitized, dated inventory of the MCP server and app-tool names advertised to Codex for GH Real Estate.

**Source snapshot SHA-256:** `DFB188041F0AE00DF5EFB84C11EAF2AD23F7693405CA046C2F97D92EE4A4CB16`

## Scope And Interpretation

The supplied runtime snapshot contains 11 server entries with 495 per-server tool memberships and 493 distinct advertised names:

| Runtime boundary | Server entries | Memberships | Distinct names |
|---|---:|---:|---:|
| Platform-managed `codex_apps` gateway | 1 | 134 | 134 |
| GH-configured Zoho-hosted servers | 10 | 361 | 359 |
| **Total** | **11** | **495** | **493** |

The two cross-server duplicates are:

- `ZohoCRM_getOrganization`, selected in both CRM servers.
- `ZohoBooks_get_unused_retainer_payments`, selected in Books Audit and Controller.

An advertised tool name proves only that the runtime exposed that operation at capture time. It does not prove that the backing app is connected, the caller has permission, the target is correct, an OAuth scope is effective, or a read/write will succeed. State-changing tools still require the repository's approval, validation, readback, and rollback controls.

The source snapshot identified the authentication mechanism but contained no credential value, MCP URL, organization ID, production payload, tenant record, accounting record, or private document. Do not commit the raw runtime inventory or any future authentication material.

## Platform-Managed `codex_apps`

`codex_apps` is a shared Codex app gateway, not a GH-configured Zoho-hosted server. Its 134 advertised tools are grouped as follows:

| Provider namespace | Tools | Capability summary |
|---|---:|---|
| `codex_document_control` | 3 | Discover connected document sessions, inspect their schemas, and execute a supported document command |
| `github` | 89 | Repository, branch, commit, pull request, issue, review, reaction, workflow, artifact, and status operations |
| `hotline` | 1 | Resolve local hotline information through the approved provider |
| `plugin_management` | 4 | Inspect dependencies/permissions and change or remove installed app access |
| `sites` | 28 | Create, version, configure, deploy, secure, and inspect hosted sites |
| `zillow` | 9 | Property search/details, Zestimate/rent data, neighborhood data, and affordability/payment calculations |

### Document Control

```text
codex_document_control.execute_document_command
codex_document_control.get_document_tool_schemas
codex_document_control.list_document_sessions
```

Document Control works only against an explicitly connected document session and the operations that session advertises. Tool exposure does not imply access to an arbitrary local or cloud document.

### GitHub

```text
github.add_comment_to_issue
github.add_issue_assignees
github.add_issue_labels
github.add_reaction_to_issue_comment
github.add_reaction_to_pr
github.add_reaction_to_pr_review_comment
github.add_review_to_pr
github.compare_commits
github.convert_pull_request_to_draft
github.create_blob
github.create_branch
github.create_commit
github.create_file
github.create_issue
github.create_pull_request
github.create_tree
github.delete_file
github.dismiss_pull_request_review
github.download_user_content
github.download_workflow_artifact
github.enable_auto_merge
github.fetch
github.fetch_blob
github.fetch_commit
github.fetch_commit_workflow_runs
github.fetch_file
github.fetch_issue
github.fetch_issue_comments
github.fetch_pr
github.fetch_pr_comments
github.fetch_pr_file_patch
github.fetch_pr_patch
github.fetch_workflow_job_logs
github.fetch_workflow_job_steps
github.fetch_workflow_run_artifacts
github.fetch_workflow_run_jobs
github.get_commit_combined_status
github.get_issue_comment_reactions
github.get_pr_diff
github.get_pr_info
github.get_pr_reactions
github.get_pr_review_comment_reactions
github.get_profile
github.get_repo
github.get_repo_collaborator_permission
github.get_user_login
github.get_users_recent_prs_in_repo
github.label_pr
github.list_installations
github.list_installed_accounts
github.list_pr_changed_filenames
github.list_pull_request_review_threads
github.list_pull_request_reviews
github.list_recent_issues
github.list_repositories
github.list_repositories_by_affiliation
github.list_repositories_by_installation
github.list_user_org_memberships
github.list_user_orgs
github.lock_issue_conversation
github.mark_pull_request_ready_for_review
github.merge_pull_request
github.remove_issue_assignees
github.remove_issue_label
github.remove_pull_request_reviewers
github.remove_reaction_from_issue_comment
github.remove_reaction_from_pr
github.remove_reaction_from_pr_review_comment
github.reply_to_review_comment
github.request_pull_request_reviewers
github.rerun_failed_workflow_run_jobs
github.rerun_workflow_job
github.resolve_review_thread
github.search
github.search_branches
github.search_commits
github.search_installed_repositories_streaming
github.search_installed_repositories_v2
github.search_issues
github.search_prs
github.search_repositories
github.unlock_issue_conversation
github.unresolve_review_thread
github.update_file
github.update_issue
github.update_issue_comment
github.update_pull_request
github.update_ref
github.update_review_comment
```

These names include destructive or externally visible actions such as file deletion, branch/ref mutation, merging, review dismissal, issue/comment changes, and workflow reruns. Repository access, branch protection, review state, and explicit task authority continue to control execution.

### Hotline

```text
hotline.get_local_hotline
```

Use the provider to resolve current local information; do not guess a hotline number.

### Plugin Management

```text
plugin_management.get_app_permissions
plugin_management.get_plugin_dependencies
plugin_management.uninstall_app
plugin_management.update_app_permissions
```

Permission changes and removal affect installed app access. They require an exact target and explicit user direction.

### Sites

```text
sites.add_custom_domain
sites.create_site
sites.create_source_repository_write_credential
sites.deploy_private_site_version
sites.deploy_site_version
sites.generate_siwc_bypass_token
sites.get_deployment_status
sites.get_environment
sites.get_environment_variables
sites.get_project
sites.get_site
sites.get_site_analytics_overview
sites.get_site_version
sites.get_site_worker_logs
sites.list_custom_domains
sites.list_projects
sites.list_site_analytics_events
sites.list_site_versions
sites.list_sites
sites.query_site_analytics_event
sites.refresh_custom_domain_status
sites.remove_custom_domain
sites.save_site_version
sites.update_access
sites.update_environment
sites.update_environment_variables
sites.update_site_access
sites.update_site_metadata
```

Every Sites deployment URL is production. Domain, access, environment-variable, credential, and deployment operations require exact project/version identity and secret-safe handling.

### Zillow

```text
zillow.calculateHomeAffordability
zillow.get_rent_zestimate
zillow.get_zestimate
zillow.get_zestimate_history
zillow.get_zestimate_info
zillow.interestRateMortgagePaymentSimulator
zillow.zillow_city_neighborhood_real_estate_information
zillow.zillow_property_details_by_address_or_name
zillow.zillow_property_search
```

Zillow estimates and calculators are informational inputs, not appraisals, lending decisions, accounting records, or authority to publish or modify a listing.

## GH-Configured Zoho Servers

The ten Zoho-hosted server entries expose:

| Codex server ID | Tools |
|---|---:|
| `gh_zoho_books_accounting_audit` | 167 |
| `gh_zoho_books_bookkeeping_changes` | 31 |
| `gh_zoho_books_controller` | 65 |
| `gh_zoho_catalyst_webhook_audit` | 15 |
| `gh_zoho_catalyst_webhook_breakglass` | 5 |
| `gh_zoho_catalyst_webhook_release` | 7 |
| `gh_zoho_crm_audit` | 18 |
| `gh_zoho_crm_changes` | 27 |
| `gh_zoho_workdrive_audit` | 21 |
| `gh_zoho_workdrive_changes` | 5 |

The exact 361 per-server Zoho memberships, current-state risks, and operating controls are maintained in the [Zoho MCP configured-server inventory](../zoho-suite/mcp/configured-servers.md). Keep the platform-managed `codex_apps` gateway out of Zoho server totals.

## Refresh Procedure

1. Obtain a new sanitized runtime inventory without URLs, tokens, secrets, organization IDs, payloads, or private records.
2. Compare server IDs and exact advertised tool names as sets; do not infer capability from a server title.
3. Recalculate memberships, distinct names, and cross-server duplicates.
4. Update this snapshot and the owning product-specific inventory in one focused change.
5. Treat every new write, delete, deployment, permission, payment, accounting, tenant, or document operation as untrusted until its schema, target, authorization, validation behavior, readback, and rollback path are reviewed.
6. Do not rewrite historical deployment-log entries. Add a new dated evidence entry.

Updating this file records capability metadata only. It does not connect an app, alter a server, change permissions, deploy a site, modify GitHub, access Zillow data, or read/write any Zoho record.
