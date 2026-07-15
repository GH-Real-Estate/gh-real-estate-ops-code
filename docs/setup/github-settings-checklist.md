# GitHub Public Repository Security Checklist

A checked item means it was verified, not merely recommended.

## Confirmed repository state

- [x] Public repository; default branch `main`.
- [x] Squash-only merging; merge commits, rebase merging, and auto-merge disabled.
- [x] Workflows default to `contents: read`, pin external Actions to full commit SHAs, use pinned GitHub-hosted runners, and prohibit `pull_request_target`, self-hosted runners, floating Action tags, and OIDC write permission.
- [x] Read-only checkouts discard persisted Git credentials.
- [x] CodeQL, dependency review, safety, and workflow-policy checks are defined.
- [x] Repository-wide CODEOWNERS, GitHub Actions/npm Dependabot coverage, private security routing, contribution templates, public data classification, and rights notice are committed.

## Main ruleset

- [ ] Require pull requests and all currently green CI/security checks.
- [ ] Require the branch to be current and all conversations resolved.
- [ ] Dismiss stale approvals and require approval after the latest push.
- [ ] Block force pushes and deletion; require linear history.
- [ ] Limit bypass to an audited emergency administrator path.
- [ ] Protect release tags such as `v*`.

Do not require CODEOWNER approval or prevent environment self-review until a second trusted reviewer exists; either setting would deadlock a single maintainer. Add the reviewer first.

## Actions

- [ ] Allow only GitHub-owned Actions plus the exact pinned third-party Actions in this repository.
- [ ] Default `GITHUB_TOKEN` permission is **Read repository contents**.
- [ ] Fork pull requests never receive write tokens or repository secrets.
- [ ] Require approval for workflows from all outside collaborators.
- [ ] Keep artifact/log retention to the shortest useful period.

## Code security

- [ ] Dependency graph, Dependabot alerts, and security updates enabled.
- [ ] Secret scanning and push protection enabled; bypass requires a documented reason.
- [ ] Private vulnerability reporting enabled.
- [ ] CodeQL results appear for Actions, JavaScript/TypeScript, and Python.

## Environments and access

- [ ] `authority-production` allows only trusted refs and, after a second reviewer exists, requires independent review and prevents self-review.
- [ ] Organization requires 2FA/passkeys and grants no broad write base permission.
- [ ] Collaborators, teams, Apps, deploy keys, PATs, environment secrets, and stale invitations are reviewed quarterly.
- [ ] Audit-log alerts cover ruleset/secret-scanning bypass, workflow/access changes, and visibility changes.
- [ ] Forks, traffic, Actions usage, and security alerts are reviewed monthly.

## Public data boundary

- [ ] No private alias crosswalk, credential, PII, private document, production payload, raw export, or operational ID is stored here.
- [ ] Generated legal/accounting PDFs match approved hash manifests.
- [ ] FASB/licensed material remains locators and GH-authored analysis only.
- [ ] A one-time credential-focused full-history scan is completed on a trusted machine; rotate any verified credential.
- [ ] Public draft pull requests are reviewed for unnecessary operational detail.
