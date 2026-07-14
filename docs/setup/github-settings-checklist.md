# GitHub Settings Checklist — GH Real Estate

Use after the repository exists under the organization.

## Organization

- [X] Personal login remains active and secured with 2FA.
- [X] Organization owns the repo.
- [X] Organization base permissions: `No permission` or lowest available.
- [X] Do not invite vendors, tenants, bookkeepers, attorneys, or property managers.
- [X] Require 2FA for anyone added later.

## Repository basics

- [X] Owner: `GH-Real-Estate` organization.
- [X] Repository name: `gh-real-estate-ops-code`.
- [X] Visibility: Private.
- [X] Description: `Private technical source of truth for GH Real Estate Zoho automations, field maps, sanitized samples, and runbooks.`
- [X] Default branch: `main`.
- [ ] Topics: `zoho`, `deluge`, `catalyst`, `real-estate`, `automation`, `private`.

## General repository settings

Settings → General:

- [X] Issues: ON.
- [X] Projects: OFF for now.
- [X] Wiki: OFF.
- [X] Discussions: OFF.
- [X] Pages: OFF.
- [X] Pull Requests: Allow squash merging ON.
- [X] Pull Requests: Allow merge commits OFF.
- [X] Pull Requests: Allow rebase merging OFF.
- [X] Pull Requests: Automatically delete head branches ON.
- [X] Auto-merge: OFF; Codex/ChatGPT should merge intentionally after checks pass instead of relying on unattended GitHub auto-merge.

## Branch protection

Settings → Branches → Add branch protection rule:

- [X] Branch name pattern: `main`.
- [ ] Require a pull request before merging: ON.
- [ ] Require approvals: OFF or 0 while solo.
- [ ] Require conversation resolution before merging: ON.
- [ ] Require status checks before merging: ON after `.github/workflows/repo-checks.yml` is merged.
- [ ] Require branches to be up to date before merging: ON. This prevents an open authority-promotion PR from replacing a newer reviewed snapshot.
- [ ] Required status check: `Safety scan`.
- [ ] Required status check: `Returned fee webhook checks`.
- [ ] Required status check: `Validate authority refresh controls`. Its workflow must continue to run on every pull request so unrelated PRs are not blocked by a skipped required check.
- [ ] Require review from Code Owners: ON for changes under `legal/`, `accounting/`, `authority/`, and the authority workflow paths.
- [ ] Confirm `@GHRealEstate` in `.github/CODEOWNERS` resolves to a user or team with repository access; replace it before enabling enforcement if it does not.
- [ ] Require linear history: ON if available.
- [X] Allow force pushes: OFF.
- [ ] Allow deletions: OFF.

Later, when you add a trusted technical person:

- [X] Required approvals: 1.
- [X] Include administrators: ON if practical.

## Code security

Settings → Code security and analysis:

- [ ] Dependency graph: ON.
- [ ] Dependabot alerts: ON.
- [ ] Dependabot security updates: ON.
- [ ] Secret scanning: ON if available.
- [ ] Push protection: ON if available.

## GitHub Actions

Settings → Actions → General:

- [ ] Actions permissions: restricted; avoid marketplace sprawl.
- [ ] Workflow permissions: read repository contents by default.
- [ ] Allow GitHub Actions to create and approve pull requests: ON. The authority workflows need pull-request creation; they do not approve or merge their own pull requests.
- [ ] No live-system deployment workflows. `authority-production` gates repository evidence promotion only; it does not deploy to Zoho or another runtime.

## Authority refresh controls

Settings -> Environments -> New environment:

- [ ] Environment name: `authority-production`.
- [ ] Required reviewer: repository owner or another qualified operator who is not relying only on the workflow output.
- [ ] Prevent self-review: ON when GitHub plan and reviewer staffing permit it.
- [ ] Confirm a second trusted GitHub operator exists before claiming enforced non-self review. Repository approval is an operational gate, not proof of legal, CPA, tax, or licensing qualification.
- [ ] Deployment branches/tags: protect the `main` branch only.
- [ ] Do not store FASB credentials, licensed exports, legal client material, tenant data, or accounting records in the environment.

Settings -> Secrets and variables -> Actions:

- [ ] Optional repository secret: `CONGRESS_API_KEY` for Library of Congress metadata discovery.
- [ ] Leave the secret absent if the API is not needed. That source will report `configuration_required` without blocking critical enacted-law coverage through GovInfo.

Verify after merge:

- [ ] `Authority Discovery` is enabled and scheduled daily at `11:17 UTC`.
- [ ] `Legal Source Monitor` remains enabled weekly at `12:27 UTC` Monday.
- [ ] `Accounting Authority Review Calendar` remains enabled monthly at `13:41 UTC` on day 1.
- [ ] `Authority Release Promotion` requires the `authority-production` approval gate and exact confirmation `PROMOTE_REVIEWED_AUTHORITY_RELEASE`.
- [ ] Promotion runs only from a clean default-branch checkout and archives `validation-context.json`; confirm its release-record hash and the exact release-plus-snapshot file scope in the resulting PR.
- [ ] Candidate and promotion workflows create draft pull requests only; repository auto-merge remains OFF.
- [ ] On the first generated candidate PR and the first generated promotion PR, select **Approve workflows to run** if GitHub shows the approval banner, then verify the required PR-event checks pass on the test-merge commit. Repeat this approval on later bot PRs whenever GitHub requests it; the explicitly dispatched branch-head runs do not necessarily satisfy a pending PR-event check.
- [ ] Keep bot PRs on `GITHUB_TOKEN` while a human approval click is acceptable. If zero-click bot checks become necessary, provision a narrowly scoped GitHub App installation token; do not add a long-lived PAT.
- [ ] Branch protection blocks direct pushes and requires the authority check plus CODEOWNERS review for governed paths.

## CI failure response

- [X] `.github/workflows/ci-failure-response.yml` uses default-branch trusted code, immutable Action SHAs, `persist-credentials: false`, and only `contents: read`, `actions: read`, plus job-scoped `issues: write`.
- [X] Incident issues use `ci-incident` and `codex-attention` labels and contain links plus bounded metadata, not raw logs or artifacts.
- [X] The GitHub workflow stores no OpenAI API key; recurring remediation uses the connected Codex desktop automation.
- [X] Confirmed July 14, 2026: live non-sensitive failure/recovery test opened one incident (#51), kept distinct push/PR runs in that incident, closed it from a newer green run, and created no duplicate issue.
- [X] Confirmed July 14, 2026: the `GH Repo CI Auto-Repair` Codex automation is active and limited to draft-PR remediation under `docs/runbooks/ci-failure-response.md`.
- [ ] Complete the unchecked branch-protection, required-check, CODEOWNERS, secret-scanning, push-protection, restricted-Actions, and authority-environment controls before considering unattended merge behavior.
- [X] Repository auto-merge remains OFF. Legal, accounting, authority, payment, lease, tenant, security, PII, and workflow-control changes remain human-gated.

## Codex / ChatGPT

- [X] Connect only this repo.
- [X] Keep `AGENTS.md` at repo root.
- [X] Default code-editing workflow: create a short-lived branch, open a PR, resolve code/issues/check failures, merge to `main` after checks pass, and verify final `main` state.
- [X] Default branch cleanup: rely on GitHub automatic head-branch deletion after merge; delete the branch manually only when available tooling supports it.
- [X] Do not leave open PRs or short-lived branches after normal code-editing tasks unless blocked by checks, permissions, tooling, security/PII concerns, live deployment risk, or explicit user instruction.
- [X] Use this review prompt on PRs when an additional review is useful:

```text
@codex review for duplicate-prevention, dry-run safety, Central Time date handling, Zoho API edge cases, and PII/secrets logging.
```
