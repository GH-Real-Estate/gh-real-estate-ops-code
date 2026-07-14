# Lease Merge Fields

Map Zoho CRM / Books / Creator fields to Zoho Contracts merge fields.

Do not store signed leases here. Do not store tenant-specific completed merge data here.

| Contract merge field | Source system | Source field API name | Notes |
|---|---|---|---|
| Tenant Legal Name | Zoho CRM | TODO | Fake examples only |
| Unit / Premises | Zoho CRM | TODO | Example: `UNIT_TEST_1` |
| Lease Start Date | Zoho CRM | TODO | `YYYY-MM-DD` |
| Lease End Date | Zoho CRM | TODO | `YYYY-MM-DD` |
| Monthly Rent | Zoho Books/CRM | TODO | Verify source-of-truth decision |
| Security Deposit | Zoho Books/CRM | TODO | Verify source-of-truth decision |
| Late Fee Clause Reference | Lease Template | TODO | Do not duplicate conflicting fee logic |

## Lead-disclosure pre-execution gate

For covered target housing, no named lessee may receive a binding lease-signature action until the matching lead record is complete and the exact completed Addendum A PDF is included in the recipient-visible lease package as Exhibit LD-1. Use the detailed field definitions in [lead-disclosure-merge-fields.md](lead-disclosure-merge-fields.md).

| Lease gate field | Source system | Allowed value for lease release | Validation |
|---|---|---|---|
| Lead Applicability | Compliance / Creator | `Covered` or `Exempt` | Blank or unresolved defaults to Covered |
| Lead Record ID | Compliance / Contracts | Matching transaction record ID | Property, unit, leasing period, and named lessees must match this lease |
| Lead Record Status | Compliance workflow | `Completed` or `Approved Exempt` | All other states block create/send/signature actions |
| Lead Completion Timestamp | Compliance workflow | Nonblank immutable timestamp | Required for Completed |
| Lead Exemption Approval | Legal review | Attorney approval reference | Required only for Approved Exempt |
| Lead Recipient Reconciliation | Sign / Contracts | Exact match | Named lessees, disclosure recipients, acknowledgments, and certifications must be the same set |
| Lead Audit / Archive ID | Sign / WorkDrive | Nonblank immutable record | Required for Completed |
| Completed Addendum A File ID | Sign / WorkDrive | Immutable completed PDF ID | Required for Completed |
| Completed Addendum A SHA-256 | Compliance | Nonblank verified hash | Required for Completed |
| Exhibit LD-1 Attachment ID | Contracts / Sign | Recipient-visible lease attachment ID | Required for covered transactions before release |
| Exhibit LD-1 SHA-256 | Contracts / compliance | Exact hash match | Must equal Completed Addendum A SHA-256 |
| Final Contract Package SHA-256 | Contracts / archive | Nonblank after execution | Archive control; not a pre-signature field |

### Gate expression

```text
lease_signature_enabled =
  (
    lead_record.status == "Completed"
    AND lead_record.draft_lease_contract_id == lease.contract_id
    AND lead_record.property_id == lease.property_id
    AND lead_record.unit_id == lease.unit_id
    AND lead_record.named_lessees == lease.named_lessees
    AND lead_record.completion_timestamp IS NOT BLANK
    AND lead_record.audit_id IS NOT BLANK
    AND lead_record.archive_record_id IS NOT BLANK
    AND lead_record.completed_pdf_file_id IS NOT BLANK
    AND lead_record.completed_pdf_hash IS NOT BLANK
    AND lease.exhibit_ld1_attachment_id IS NOT BLANK
    AND lease.exhibit_ld1_attachment_hash == lead_record.completed_pdf_hash
  )
  OR
  (
    lead_record.status == "Approved Exempt"
    AND lead_record.exemption_evidence_id IS NOT BLANK
    AND lead_record.exemption_counsel_approval IS NOT BLANK
  )
```

After execution, the audit must prove that the disclosure delivery/completion preceded every named lessee's binding lease-signature timestamp and must store the final contract-package hash.

Use two sequential transactions when Zoho cannot enforce the same order in one transaction: complete the standalone lead-disclosure transaction first, then attach its exact completed PDF as Exhibit LD-1 and send the lease. A clause reference, WorkDrive-only file, internal-only attachment, or later lessor countersignature does not satisfy this gate.
