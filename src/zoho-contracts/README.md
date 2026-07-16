# Zoho Contracts

Use this area for sanitized technical merge-field maps, the governed field registry, contract/clause authoring standards, validation tooling, and automation notes.

## Contents

```text
clauses/
  README.md
field-maps/
  animal-addendum-merge-fields.md
  contract-field-registry.json
  contract-field-registry.md
  lease-merge-fields.md
runbooks/
  apply-contract-authoring-standard.md
schemas/
  clause-definition.schema.json
  contract-field-registry.schema.json
scripts/
  validate_contract_authoring_standard.py
  validate_contract_field_registry.py
standards/
  contract-authoring-standard.json
  contract-authoring-standard.md
templates/
  clause-definition.template.json
tests/
  test_validate_contract_authoring_standard.py
  test_validate_contract_field_registry.py
```

## Contract and Clause Authoring Standard

`standards/contract-authoring-standard.json` is the canonical source for the exact Clause Type master list, required clause metadata, Contracts-specific typography, and editor-style hierarchy. Its Markdown file is generated for authors and reviewers.

Create governed clause records only as `clauses/**/*.clause.json` using `templates/clause-definition.template.json`. CI validates every matching file. Zoho's language-variant Clause Title is separate from its Language body: render the title as Heading 2, then label substantive language blocks as Heading 3-5 or Normal without duplicating the title.

Zoho Sign recipient fields are governed separately under `../zoho-sign/`. Use only production-approved canonical syntax; keep officially documented advanced tags blocked until the controlled Contracts-to-Sign smoke test passes.

The live template update, Inter-font gate, synthetic signature test, republish control, and forward-repair rollback are documented in `runbooks/apply-contract-authoring-standard.md`.

## Canonical Field Registry

`field-maps/contract-field-registry.json` is the machine-readable source of truth for the current Zoho Contracts field inventory and proposed CRM crosswalk. The generated Markdown view is for operators and reviewers.

The registry records:

- all 46 submitted Zoho system fields and 19 submitted custom fields;
- the selected Zoho Contracts custom-field type where applicable;
- expected system-field semantics without pretending system fields use the custom menu;
- portable and proposed CRM field types;
- source-of-truth ownership, sensitivity, validation, aliases, and review status;
- tenant-metadata verification gates for exact Contracts and CRM API names.

Do not create integration code from a display label or proposed API name. Confirm the actual Contracts `apiName`, `metaType`, `dataType`, and `displayType` through the authenticated Zoho metadata API, and confirm the exact CRM module/layout field metadata before activation.

## Validation

```powershell
python src/zoho-contracts/scripts/validate_contract_authoring_standard.py
python src/zoho-contracts/scripts/validate_contract_field_registry.py
python -m unittest discover -s src/zoho-contracts/tests -p 'test_*.py' -v
```

To intentionally regenerate generated Markdown after editing either canonical JSON source:

```powershell
python src/zoho-contracts/scripts/validate_contract_authoring_standard.py --write-markdown
python src/zoho-contracts/scripts/validate_contract_field_registry.py --write-markdown
```

## Rules

- Do not store signed leases or tenant-specific merged documents here.
- Do not store real names, addresses, phone numbers, emails, signatures, IDs, payment data, record IDs, tokens, or private documents here.
- Keep actual templates and signed documents in Zoho Contracts, Zoho Sign, and Zoho WorkDrive.
- CRM owns approved pre-authoring party, property, unit, and lease inputs; Zoho Contracts owns lifecycle fields and the resolved agreement snapshot.
- Prefer one-way CRM-to-Contracts authoring. Do not add bidirectional sync without a conflict policy and idempotency controls.
- Treat executed document values as immutable snapshots.
- Keep identifiers and postal codes as text. Do not convert them to numeric fields.
- Do not independently populate deprecated aliases or unresolved tenant-only fields.
- A repository merge documents the design; it does not deploy or alter live Zoho configuration.
