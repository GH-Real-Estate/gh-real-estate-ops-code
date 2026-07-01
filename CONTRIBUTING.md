# Contributing / Change Process

This is currently a solo-operator repo. Still use a controlled workflow for material changes.

## Simple Workflow

```text
main = stable/current reference
branches = proposed changes
pull requests = review checkpoint
manual deployment = controlled production change
```

## Branch Names

Use short, descriptive names that include the affected system:

```text
zoho-books/late-fee-duplicate-prevention
zoho-books/update-field-map
zoho-payments/returned-fee-replay-check
zoho-crm/update-application-map
zoho-creator/add-sanitized-export
zoho-contracts/update-merge-map
docs/update-github-settings
```

## Commit Messages

Good:

```text
Document Zoho Books late fee item IDs
Add late fee duplicate-prevention test cases
Update returned payment webhook install notes
```

Bad:

```text
final
fix stuff
new code
asdf
```

## Pull Request Standard

Open a pull request for any change that affects:

- Fees.
- Invoices.
- Payments.
- Tenant communication.
- Webhooks.
- API credentials/configuration.
- Zoho field mappings.
- Lease/business-rule logic.

## Deployment Rule

Merging to `main` does not mean deployed. Production deployment happens only after manually installing/updating the code in Zoho/Catalyst and recording it in:

```text
docs/runbooks/deployment-log.md
```
