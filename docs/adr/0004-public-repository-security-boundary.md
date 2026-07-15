# 2026-07-14 — Public Repository Security Boundary

## Status

Accepted. Supersedes the visibility decision in ADR 0001; the single-repository architecture remains.

## Decision

`GH-Real-Estate/gh-real-estate-ops-code` is a public, sanitized technical reference. Public visibility does not authorize production deployment, disclose private configuration, or make generated legal/accounting material authoritative by itself.

The repository may contain original code, sanitized examples, public government material, authority locators, and governed evidence. It must not contain credentials, tenant/customer PII, private documents, production payloads, raw operational exports, or licensed accounting content that cannot be redistributed.

## Enforcement

- Pull requests and protected `main` are the only normal change path.
- GitHub Actions use immutable commit SHAs, least privilege, hosted runners, and no `pull_request_target`.
- CodeQL, dependency review, the repository safety scan, and workflow-policy checks gate changes.
- GitHub secret scanning, push protection, private vulnerability reporting, read-only default workflow tokens, and a `main` ruleset are repository-setting requirements.
- Financial, tenant, legal, tax, and accounting material remains subject to qualified human review and controlled deployment outside GitHub.

## Consequences

Anything committed must be assumed permanently public, including deleted history and forks. A current-tree deletion is not a substitute for credential rotation or incident handling. Public visibility improves review and portability but requires stricter data minimization and review discipline.
