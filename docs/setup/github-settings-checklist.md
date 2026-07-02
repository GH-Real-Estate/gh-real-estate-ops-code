# GitHub Settings Checklist — GH Real Estate

Use after the repository exists under the organization.

## Organization

- [ ] Personal login remains active and secured with 2FA.
- [ ] Organization owns the repo.
- [ ] Organization base permissions: `No permission` or lowest available.
- [ ] Do not invite vendors, tenants, bookkeepers, attorneys, or property managers.
- [ ] Require 2FA for anyone added later.

## Repository basics

- [ ] Owner: `GH-Real-Estate` organization.
- [ ] Repository name: `gh-real-estate-ops-code`.
- [ ] Visibility: Private.
- [ ] Description: `Private technical source of truth for GH Real Estate Zoho automations, field maps, sanitized samples, and runbooks.`
- [ ] Default branch: `main`.
- [ ] Topics: `zoho`, `deluge`, `catalyst`, `real-estate`, `automation`, `private`.

## General repository settings

Settings → General:

- [ ] Issues: ON.
- [ ] Projects: OFF for now.
- [ ] Wiki: OFF.
- [ ] Discussions: OFF.
- [ ] Pages: OFF.
- [ ] Pull Requests: Allow squash merging ON.
- [ ] Pull Requests: Allow merge commits OFF.
- [ ] Pull Requests: Allow rebase merging OFF.
- [ ] Pull Requests: Automatically delete head branches ON.
- [ ] Auto-merge: OFF for now.

## Branch protection

Settings → Branches → Add branch protection rule:

- [ ] Branch name pattern: `main`.
- [ ] Require a pull request before merging: ON.
- [ ] Require approvals: OFF or 0 while solo.
- [ ] Require conversation resolution before merging: ON.
- [ ] Require status checks before merging: ON after `.github/workflows/repo-checks.yml` is merged.
- [ ] Required status check: `Safety scan`.
- [ ] Required status check: `Returned fee webhook checks`.
- [ ] Require linear history: ON if available.
- [ ] Allow force pushes: OFF.
- [ ] Allow deletions: OFF.

Later, when you add a trusted technical person:

- [ ] Required approvals: 1.
- [ ] Include administrators: ON if practical.

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

- [ ] Connect only this repo.
- [ ] Keep `AGENTS.md` at repo root.
- [ ] Use manual reviews first.
- [ ] Use this review prompt on PRs:

```text
@codex review for duplicate-prevention, dry-run safety, Central Time date handling, Zoho API edge cases, and PII/secrets logging.
```
