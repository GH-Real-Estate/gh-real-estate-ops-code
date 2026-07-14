# Zoho Contracts

Use this area only for technical merge-field maps and sanitized automation notes.

## Contents

```text
field-maps/
  animal-addendum-merge-fields.md
  lead-disclosure-merge-fields.md
  lease-merge-fields.md
```

Related business rules:

- [Animal addendum rules](../../docs/business-rules/animal-addendum-rules.md)
- [Lead-based paint disclosure and pre-execution gate](../../docs/business-rules/lead-based-paint-disclosure-rules.md)

## Rules

- Do not store signed leases here.
- Do not store tenant-specific merged documents here.
- Do not store real tenant names, signatures, IDs, payment data, lead reports, or private documents here.
- Keep actual templates and signed documents in Zoho Contracts, Zoho Sign, and Zoho WorkDrive.
- Treat merge-field maps as implementation specifications only; obtain attorney approval before production use.
- Use fail-closed validations for legal applicability, required attachments, signing order, and exemption evidence.
