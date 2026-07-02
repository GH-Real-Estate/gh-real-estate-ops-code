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
- [X] Auto-merge: OFF for now.

## Branch protection

Settings → Branches → Add branch protection rule:

- [X] Branch name pattern: `main`.
- [ ] Require a pull request before merging: ON.
- [ ] Require approvals: OFF or 0 while solo.
- [ ] Require conversation resolution before merging: ON.
- [ ] Require status checks before merging: ON after `.github/workflows/repo-checks.yml` is merged.
- [ ] Required status check: `Safety scan`.
- [ ] Required status check: `Returned fee webhook checks`.
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
- [ ] Allow GitHub Actions to create and approve pull requests: OFF.
- [ ] No deploy workflows yet.

## Codex / ChatGPT

- [X] Connect only this repo.
- [X] Keep `AGENTS.md` at repo root.
- [X] Use manual reviews first.
- [X] Use this review prompt on PRs:

```text
@codex review for duplicate-prevention, dry-run safety, Central Time date handling, Zoho API edge cases, and PII/secrets logging.
```
