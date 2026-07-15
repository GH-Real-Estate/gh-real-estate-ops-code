## Purpose

Describe the operational problem and the smallest safe change that solves it.

## Risk classification

- [ ] Documentation only
- [ ] Application or integration code
- [ ] Financial, payment, tenant, lease, legal, tax, or accounting behavior
- [ ] GitHub Actions, permissions, security controls, or deployment behavior

## Safety checklist

- [ ] I verified that this change contains no credentials, secrets, tenant PII, private documents, production logs, or unsanitized exports.
- [ ] Tests, linting, validation, or a reproducible manual check are documented below.
- [ ] The rollback path and any deployment step are documented below.
- [ ] New or changed Actions use full immutable commit SHAs and the least possible permissions.
- [ ] Financial/legal/accounting changes retain fail-closed defaults and require qualified human review before production use.
- [ ] Merging this PR alone does not imply that a Zoho/Catalyst production deployment occurred.

## Verification

List exact commands and results.

## Deployment and rollback

State `Not deployed` when no external system was changed.
