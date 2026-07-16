# Zoho CRM

Use this area for CRM functions, field maps, and integration notes.

Zoho CRM owns prospect, applicant, tenant relationship, property/unit, and leasing pipeline records. Do not store real applicant or tenant records in GitHub.

## Contents

```text
field-maps/
  zillow-to-crm-to-contracts.md
integrations/
  zillow-lead-intake/
```

## Rules

- Use fake examples only.
- Do not store actual applications, IDs, pay stubs, employment verification records, landlord references, or tenant documents here.
- Keep live records in Zoho CRM, Zoho Forms, Zoho Creator, or WorkDrive as appropriate.
- Zillow lead intake writes raw Zillow inquiries to CRM `Leads` only. It must not create `Contacts`, rental application pipeline records, leases, Books records, tenant portal access, or WorkDrive folders.
- Convert or promote a Lead only after qualification, application review, owner approval, or the approved business workflow for the tenant stage.

## Zoho Contracts Field Crosswalk

Use `../zoho-contracts/field-maps/contract-field-registry.json` as the governed, machine-readable source for Contracts-to-CRM field planning. Its `proposed_crm` entries document portable CRM field types and proposed API names; they are not proof that those API names exist in the live CRM tenant.

Before creating or syncing CRM fields:

1. Verify the Zoho Contracts field through the contract type `allfields` metadata endpoint.
2. Verify the target CRM module through the CRM Fields Metadata API.
3. Record confirmed API names in a reviewed registry update.
4. Keep fields marked `review_required`, `tenant_api_required`, or `deprecated_alias` out of automated synchronization.

Do not copy contract-party personal data into GitHub while performing that verification.
