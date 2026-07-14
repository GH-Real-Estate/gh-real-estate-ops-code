# Lead-Based Paint Disclosure Merge Fields

Map approved Zoho CRM, Creator, Contracts, and Sign data to a property- and transaction-specific lead disclosure record.

**Status:** Attorney review required before production use  
**Privacy:** Store only sanitized field definitions here. Never store tenant values, signatures, reports, or completed disclosure records in GitHub.

## Control objective

The lease-signature action must remain disabled until:

- the lead record is `Completed`, and the exact completed Addendum A is attached to the lease as recipient-visible Exhibit LD-1; or
- a documented, attorney-approved exemption is `Approved Exempt`.

Coverage defaults to `Covered` whenever verified construction-year evidence or exemption evidence is missing.

## Field map

| Business key | Source / owner | Required data | Validation |
|---|---|---|---|
| `lead.property_id` | CRM / property record | Stable property identifier | Required; must resolve to exactly one property |
| `lead.premises_address` | CRM / property record | Street, city, state, ZIP | Required; must match lease |
| `lead.unit_id` | CRM / unit record | Unit/apartment identifier | Required; must match lease |
| `lead.construction_year` | Verified property source | Four-digit year | No unverified default |
| `lead.construction_year_source` | Compliance record | Source, date retrieved, attachment ID | Required before a post-1977 determination |
| `lead.draft_lease_contract_id` | Contracts / lease record | Nonbinding draft lease ID | Required; lease must not yet be released |
| `lead.transaction_id` | Contracts / compliance record | Lead transaction identifier | Required; unique |
| `lead.leasing_period_start` | Contracts / lease record | Date | Must match lease |
| `lead.leasing_period_end` | Contracts / lease record | Date or approved open-ended value | Must match lease |
| `lead.contract_language` | Contracts | Controlled language value | Required; disclosure content must use same language |
| `lead.named_lessees[]` | CRM / Contracts | Stable ID and legal name for every actual lessee | Required; exact match to lease signers |
| `lead.coverage_status` | Compliance decision | `Covered` or `Exempt` | Default `Covered`; no blank/free text |
| `lead.exemption_type` | Compliance decision | Controlled exemption value | Required only when exempt |
| `lead.exemption_evidence_id` | WorkDrive / compliance record | Evidence attachment ID | Required when exempt |
| `lead.exemption_counsel_approval` | Legal review | Approver, date, matter/reference ID | Required when exempt |
| `lead.knowledge_selection` | Lessor | `Known present` or `No knowledge` | Exactly one; no global template default |
| `lead.known_hazard_basis` | Lessor | Basis/evidence | Required when known present |
| `lead.known_hazard_location` | Lessor | Unit/common-area location | Required when known present |
| `lead.known_hazard_condition` | Lessor | Condition/details | Required when known present |
| `lead.records_selection` | Lessor | `All available provided` or `No records` | Exactly one; no global template default |
| `lead.records_search_scope` | Compliance record | Unit, common area, building-wide files checked | All three scopes must be resolved |
| `lead.records_attachment_ids[]` | WorkDrive / Sign package | Every disclosed report/record ID | Required when records exist; recipient-visible |
| `lead.records_index` | Compliance record | Title, date, scope, ID for each attachment | Must reconcile to attachments |
| `lead.warning_statement_version` | Template | Federal warning statement version | Locked production text |
| `lead.pamphlet_title` | Template / compliance | Protect Your Family From Lead in Your Home | Locked |
| `lead.pamphlet_edition` | Compliance | January 2026 | Required |
| `lead.pamphlet_publication_id` | Compliance | EPA-747-K-26-001 | Required |
| `lead.pamphlet_language` | Compliance | Controlled language value | Must match approved contract-language package |
| `lead.pamphlet_source_url` | Compliance | Official EPA URL | Required |
| `lead.pamphlet_file_hash` | Compliance | SHA-256 of delivered file | Required; validate against approved asset |
| `lead.delivery_recipients[]` | Sign / delivery audit | Every named lessee recipient ID | Must equal named-lessee set |
| `lead.delivery_method` | Sign / delivery audit | Paper, electronic, or mixed | Required |
| `lead.delivery_timestamp` | Sign / delivery audit | Immutable timestamp | Must precede each lessee's binding lease signature |
| `lead.paper_fallback_status` | Sign / compliance | Offered/used and evidence ID | Required for electronic workflow |
| `lead.esign_consent_id` | Sign / compliance | Consumer-consent record ID | Required for electronic-only delivery |
| `lead.esign_access_proof_id` | Sign / compliance | Proof recipient can access/retain records | Required for electronic-only delivery |
| `lead.lessee_acknowledgments[]` | Sign | Separate disclosure/records and pamphlet acknowledgment for every named lessee | Complete set; exclude non-lessee occupants |
| `lead.lessor_certification` | Sign | Signer ID, capacity, signature/date | Required |
| `lead.lessor_agent_role` | CRM / legal | Applicable or N/A | No silent blank |
| `lead.lessor_agent_certification` | Sign | Signer ID, signature/date | Required when applicable |
| `lead.lessee_agent_role` | CRM / legal | Applicable compensated role or N/A | No silent blank |
| `lead.lessee_agent_certification` | Sign | Signer ID, signature/date | Required when applicable |
| `lead.lessee_certifications[]` | Sign | Signer ID, signature/date for every named lessee | Complete set |
| `lead.status` | Compliance workflow | Draft, Delivered, In Progress, Completed, Approved Exempt, Blocked | Lease gate accepts only Completed or Approved Exempt |
| `lead.completion_timestamp` | Compliance workflow | Immutable timestamp | Required for Completed |
| `lead.audit_id` | Sign / Contracts | Immutable audit trail ID | Required for Completed |
| `lead.completed_pdf_file_id` | Sign / WorkDrive | Immutable completed Addendum A file ID | Required for Completed |
| `lead.completed_pdf_hash` | Compliance | SHA-256 of completed Addendum A PDF | Required for Completed |
| `lead.archive_record_id` | Compliance / WorkDrive | Internal completion/archive record ID | Required for Completed |
| `lead.final_lease_contract_id` | Contracts | Matching lease contract ID | Required before lease release |
| `lead.final_lease_attachment_id` | Contracts / Sign | Recipient-visible Exhibit LD-1 attachment ID | Required before lease release |
| `lead.final_lease_attachment_hash` | Contracts / compliance | SHA-256 of Exhibit LD-1 | Must equal `lead.completed_pdf_hash` |
| `lead.final_contract_package_hash` | Contracts / archive | SHA-256 of fully executed contract package | Required after final execution |
| `lead.retention_through` | Records management | Retention date | At least three years from leasing-period commencement |
| `lead.attorney_review_version` | Legal / template registry | Approved template version and approval date | Required for production |

## Derived validations

1. `named_lessees == delivery_recipients == lessee_acknowledgments == lessee_certifications`.
2. `delivery_timestamp < earliest_binding_lease_signature_timestamp`.
3. `coverage_status == Exempt` requires exemption type, evidence, attorney approval, and status `Approved Exempt`.
4. `knowledge_selection == Known present` requires basis, location, and condition.
5. `records_selection == All available provided` requires a reconciled recipient-visible attachment index.
6. Electronic-only delivery requires consumer consent, paper-rights/fallback evidence, access proof, and retention instructions.
7. The pamphlet hash must match the approved January 2026 asset for the selected language.
8. No required selection, explanation, signature, date, recipient, or attachment may remain blank.
9. Covered transactions require `final_lease_attachment_hash == completed_pdf_hash` before lease release.
10. Exhibit LD-1 must be included in the recipient-visible lease/signature package; a reference, WorkDrive-only file, or generic internal attachment does not pass the gate.
11. The final archived contract must preserve the Exhibit LD-1 attachment ID/hash and final package hash.

## Zoho implementation note

Use two sequential contract transactions:

1. **Residential Lead-Based Paint Disclosure:** admin prefill; lessor/applicable agents sign; all named lessees sign; the current pamphlet and responsive records are recipient-visible attachments.
2. **Residential Lease Agreement:** remove the former embedded disclosure, retain the incorporation clause, and append the exact completed standalone Addendum A PDF as recipient-visible Exhibit LD-1 before sending the lease.

Do not use the disclosure form twice. Keep delivery/archive fields in the internal completion record rather than on the tenant-signed form. Do not create or enable the lease signature request until the lead transaction and Exhibit LD-1 hash validation pass.
