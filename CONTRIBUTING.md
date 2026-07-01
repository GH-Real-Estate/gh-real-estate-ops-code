# Contributing / Change Process

This is currently a solo-operator repo. Still use a controlled workflow for material changes.

## Simple workflow

```text
main = stable/current reference
branches = proposed changes
pull requests = review checkpoint
manual deployment = controlled production change
```

## Branch names

Use short, descriptive names:

```text
late-fee/fix-duplicate-prevention
late-fee/update-install-checklist
returned-payment/add-replay-check
books/update-field-map
creator/add-sanitized-export
contracts/update-merge-map
docs/update-github-settings
```

## Commit messages

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

## Pull request standard

Open a pull request for any change that affects:

- Fees.
- Invoices.
- Payments.
- Tenant communication.
- Webhooks.
- API credentials/configuration.
- Zoho field mappings.
- Lease/business-rule logic.

## Deployment rule

Merging to `main` does not mean deployed. Production deployment happens only after manually installing/updating the code in Zoho/Catalyst and recording it in:

```text
docs/runbooks/deployment-log.md
```
