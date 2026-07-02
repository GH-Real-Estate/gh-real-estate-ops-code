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
