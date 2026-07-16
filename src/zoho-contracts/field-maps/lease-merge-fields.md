# Lease Merge Fields

The canonical field inventory and cross-application type map is [contract-field-registry.md](contract-field-registry.md). Its machine-readable source is `contract-field-registry.json`.

Do not maintain a second competing field catalog in this file. This page records how the legacy starter map resolves into the governed registry.

## Legacy Starter Map Resolution

| Legacy merge concept | Canonical registry field | Current decision |
|---|---|---|
| Tenant Legal Name | `party_b_name` or the reviewed affected-party snapshot | Do not assume Party B is always the tenant; contract-type party roles must control. |
| Unit / Premises | `property_unit_number_snapshot` plus structured property address fields | CRM Property/Unit records own the pre-authoring values. |
| Lease Start Date | `agreement_effective_date` | Use system Agreement Date unless a separately defined lease commencement date is approved. |
| Lease End Date | `term_end_date` | Required for fixed terms; must not precede Agreement Date. |
| Monthly Rent | Not yet included in the submitted 65-field inventory | Add only after source-of-truth and Books synchronization rules are approved. Do not misuse Contract Amount. |
| Security Deposit | Not yet included in the submitted 65-field inventory | Add only after the financial owner, accounting treatment, and duplicate-prevention workflow are approved. |
| Late Fee Clause Reference | Lease template/clause selection, not a free-form transaction field | Do not duplicate lease fee logic in a field map. |

## Source and Sync Rules

- Zoho CRM owns approved pre-authoring party, property, unit, and lease inputs.
- Zoho Contracts owns contract lifecycle state and the resolved agreement snapshot.
- Zoho Books owns invoices, payments, deposits, and accounting truth.
- Use the tenant-returned Contracts `apiName` and verified CRM API field name; proposed names in the registry are not deployable identifiers.
- Prefer one-way CRM-to-Contracts generation. Never overwrite an executed agreement from mutable CRM data.
- Keep signed leases and tenant-specific merged values out of GitHub.

## Production Gate

Before a live mapping is activated:

1. Reconcile the exact contract type through the Contracts `/allfields` metadata endpoint.
2. Reconcile the exact CRM module, layout, field API names, and permissions.
3. Resolve every `review_required` registry entry.
4. Run the validator and sanitized regression tests.
5. Render and manually compare a synthetic contract preview against the approved template.

Merging this documentation does not create fields or deploy a Zoho integration.
