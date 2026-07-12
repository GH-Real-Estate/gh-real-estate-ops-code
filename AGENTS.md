# AGENTS.md

## Repository Purpose

This repository supports GH Real Estate operational systems, Zoho automations, Deluge scripts, documentation, validation scripts, and related implementation notes.

This is a business-operations repo. Treat rent, invoice, payment, lease, tenant, security deposit, and accounting logic as high-risk.

## Business Priorities

1. Reliability
2. Auditability
3. Payment accuracy
4. Tenant-operation clarity
5. Compliance awareness
6. Minimal manual admin
7. Low support burden

## Legal Authority Library Rules

- The `legal/` subtree contains public legal authorities and audited extracts, not legal advice, signed leases, tenant records, or internal policy targets.
- Start with `legal/CURRENT_AUTHORITY_INDEX.md`, `legal/PROJECT_INSTRUCTIONS.md`, `legal/SOURCE_GAPS.md`, and `legal/manifests/authority_registry.json`.
- Official source text controls over Markdown extraction, summaries, applicability notes, and AI output.
- Distinguish binding law, conditional law, published case law, guidance, official notices, proposals, withdrawn material, and internal GH policy.
- Never mark a changed source current merely because an automated hash check detected it. Legal status, effective dates, supersession, and applicability require human review.
- Never patch old and new wording into a synthetic statute. Keep current consolidated text, effective addenda, and historical versions separately labeled.
- Keep proposed, withdrawn, monitoring, candidate-branch, and unreviewed material out of the approved current-law path.
- Run `python legal/scripts/validate_release.py` after changing an approved release.
- Do not auto-merge a legal-source currentness change. Preserve the approved baseline until a qualified reviewer resolves the change.

## Working Rules

- Make small, focused, reversible changes.
- Inspect the current repo state and relevant files before editing.
- Do not broadly reorganize folders unless explicitly requested.
- Do not add production dependencies without explaining why they are necessary.
- Do not hardcode secrets, tokens, credentials, tenant PII, banking data, EIN/SSN data, live customer data, or private documents.
- Use environment variables or secure configuration patterns.
- Prefer examples, fixtures, and sanitized sample data.
- Keep documentation practical and operator-friendly.
- Preserve existing naming conventions unless a rename is specifically requested.
- Before changing automation behavior, identify what system it affects and what could break.
- Write professional, production-quality, maintainable code.
- Keep the codebase understandable for future maintainers.
- Use professional comments where they improve clarity.
- Comment non-obvious business rules, edge cases, payment logic, tenant logic, lease logic, and integration assumptions.
- Avoid comments that merely repeat the code.
- Do not create duplicate automation paths.
- Do not double-charge, double-send, double-update, or duplicate records.
- Keep Zoho Books, Zoho CRM, Zoho Creator, Zoho Forms, Zoho Contracts, and Zoho Sign logic separated unless integration code requires otherwise.
- Use clear folder structure by business domain and integration.
- Keep payment, invoice, lease, tenant, notice, and deposit workflows especially clear and auditable.
- Prefer small, testable scripts and functions.
- Prefer idempotent automations where possible.
- Add guardrails for missing fields, bad dates, failed API responses, duplicate tenants, duplicate invoices, partial payments, and stale records.
- Do not make cosmetic-only changes unless requested.
- Do not introduce unnecessary frameworks, services, or abstractions.

## Default GitHub Code-Change Workflow

When Codex/ChatGPT changes code, scripts, workflow files, configuration, tests, or production-relevant operational docs in this GitHub repo, the default is end-to-end completion:

1. Inspect the current repo state and relevant files before editing.
2. Make focused changes on a short-lived branch.
3. Open a pull request into `main`.
4. Run or wait for all relevant local and GitHub checks.
5. Inspect failures, fix code or documentation issues, and rerun checks until they pass or a real external blocker is found.
6. Merge the pull request into `main` after checks pass and no blocking review, security, merge-conflict, or production-risk issue remains.
7. Verify `main` contains the final merged commit.
8. Ensure the short-lived branch is gone after merge when GitHub automatic branch deletion or the available tooling supports it.

Do not leave an unmerged branch or open PR at the end of a normal code-editing task unless one of these blockers applies:

- The user explicitly asks to stop before merge.
- GitHub permissions, branch protection, missing checks, or connector/tool limits prevent merge or branch cleanup.
- Checks fail for an external reason that cannot be fixed from the repo.
- The change exposes a security, PII, financial, payment, lease, tenant, or destructive-production risk that requires human approval.
- A live Zoho/Catalyst deployment step is required before claiming production completion.

Never merge when required checks are failing, unresolved requested changes remain, secrets or PII are suspected, or the diff includes unrelated work.

## Folder Structure Guidance

Prefer organizing by business system and integration, for example:

- `zoho-books/`
- `zoho-crm/`
- `zoho-creator/`
- `zoho-forms/`
- `zoho-contracts/`
- `zoho-sign/`
- `automations/`
- `scripts/`
- `docs/`
- `tests/`

Use `automations/` only for workflows that span multiple systems or do not naturally belong to a single Zoho product. If a workflow is primarily owned by Zoho Books, Zoho CRM, or Zoho Creator, place it under that system's folder.

## Zoho / Deluge Rules

- Use valid Deluge syntax.
- Statements end with semicolons.
- Use `ifNull()` and `isNull()` guards where records or API responses may be missing.
- Use `try/catch` for integration and record-update workflows.
- Use pagination and small batches for record loops.
- Do not use while-loop patterns; Deluge work should use supported loops, pagination, or bounded batches.
- Use Zoho Connections for external API calls. Never hardcode secrets in `invokeurl`.
- Do not assume field link names, module API names, organization IDs, or connection names. Inspect repo docs/schema files first or ask.

## Automation Safety

For automations involving money, rent, invoices, fees, deposits, leases, notices, or tenant records:

- Make the process idempotent where practical.
- Prevent duplicate charges, duplicate invoices, duplicate customer records, and duplicate emails.
- Include a dry-run mode or clear manual verification step when practical.
- Log counts and outcomes without exposing sensitive tenant data.
- Fail safely if required fields are missing.
- Add validation.
- Avoid destructive changes.
- Include rollback notes when relevant.
- Make duplicate prevention explicit.
- Do not assume balances or payment status unless the source data supports it.
- Do not claim a financial workflow is fixed unless it was tested or carefully verified.

## Review Guidelines

Flag issues involving:

- Duplicate rent charges or duplicate tenant/customer records
- Incorrect proration, late fee, payment, or invoice logic
- Missing null checks
- Missing pagination
- Hardcoded secrets or live tenant data
- Unclear deployment steps
- Broad refactors unrelated to the task
- Code that cannot be validated manually or automatically

Also follow `code_review.md` when reviewing pull requests.

## Done When

A task is complete only when:

- The diff is focused.
- The changed files are summarized.
- Relevant checks were run, or the reason they could not be run is stated.
- Remaining manual steps are listed.
- Deployment risk is called out when production Zoho behavior could be affected.

After changes, provide:

1. What changed
2. Why it changed
3. Files touched
4. Business behavior changed
5. How to test or smoke-test
6. Risks
7. Rollback steps if relevant
8. Comments or documentation added, and why
9. GitHub checks run and final merge status
