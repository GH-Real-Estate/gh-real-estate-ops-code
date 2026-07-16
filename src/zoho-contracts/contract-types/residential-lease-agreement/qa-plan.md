# Residential Lease Draft QA Plan

This package is Draft Only and Attorney Review Required. A repository merge does not publish or deploy the lease.

## Repository checks

- Validate all 59 clause records and complete crosswalk coverage.
- Confirm `article-13-body` immediately follows `article-13` in both the 161-unit source manifest and crosswalk.
- Validate the canonical field registry and recipient manifests.
- Confirm all live API names remain null until authenticated verification.
- Confirm no source binary, local path, address, phone, email, tenant value, signature, or payment data is committed.
- Confirm every unresolved field or conditional workflow points to an open production gate.
- Confirm the exact 29 production gates remain open and the deployment status remains Draft Only, unpublished, execution blocked, and unsent.
- Confirm no production-ready hardcoded value remains for lease-end time, parking count or assignment, storage rent or terms, pet charges or status, appliance inventory, landlord representative or title, required contact data, or municipality applicability.
- Confirm the source's Overland Park and OPMC wording remains unchanged but is bound to `municipality_jurisdiction_applicability`.
- Confirm every Section 14.2 initials cell and each Addendum B delivery row uses only the actual tenants' `{{I:Rn}}` tags in the matching signer-count fragment.

## Live Zoho Draft checks

1. Reuse the existing `Residential Lease Agreement` Contract Type only after publication-history and agreement-association review.
2. Preserve a reconstructable copy of the prior published version.
3. Keep the working version Draft, unpublished, and unsent.
4. Verify Inter is available; do not substitute Roboto or upload font binaries.
5. Build with native Title, Intro Text, Heading 1 article headings, governed clauses, native tables, Ending Text, and controlled attachments.
6. Use the one-, two-, or three-tenant Ending Text and Addendum B fragment matching the actual signer set.
7. Leave every value governed by `parking_terms`, `storage_terms`, `lease_end_time`, `initial_amounts_due`, `pet_terms`, `appliance_inventory`, `landlord_authorized_representative`, `required_contact_fields`, or `municipality_jurisdiction_applicability` visibly blank while its gate is open.
8. Verify the selected Ending Text and Addendum B fragments contain initials only for actual tenant recipients and contain no initials field for GH.
9. Verify GH Real Estate is the final actual recipient and final signer.
10. Update the dynamic Table of Contents after all components are present.
11. Confirm the organization header does not expose literal `Document Name`; do not change global header/footer settings in this run.

## Twenty-page visual comparison

Compare every live Draft preview page against the controlling 20-page PDF. Verify the cover, warning, TOC, fourteen articles, Article 13 operative paragraph before Article 14, clause and subsection order, tables, defined terms, citations, Addendum A treatment, Addendum B, Ending Text, required initials locations, headers, footers, page numbers, and all visible blanks or fields.

Fail the preview if it contains Roboto, an RLA code, an internal question, an API name, `TODO`, `Document Name`, a raw unsupported tag, duplicate numbering, clipping, overflow, an unintended blank page, legacy lease text, storage-addendum text, or unauthorized fee language.

## Signature smoke-test gate

Use only a short fictitious `TEST — DO NOT SEND TO TENANT` document and controlled GH-owned test mailboxes. Test preview field conversion separately from post-signature value population for every signer-count variant. Verify every required `{{I:Rn}}` converts for the intended tenant, GH receives no initials field, and the one-, two-, or three-tenant fragment is selected exactly. Do not send even a synthetic request without explicit user approval.
