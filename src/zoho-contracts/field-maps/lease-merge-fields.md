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

For covered target housing, no named lessee may receive a binding lease-signature action until the matching lead record is complete. Use the detailed field definitions in [lead-disclosure-merge-fields.md](lead-disclosure-merge-fields.md).

| Lease gate field | Source system | Allowed value for lease release | Validation |
|---|---|---|---|
| Lead Applicability | Compliance / Creator | `Covered` or `Exempt` | Blank or unresolved defaults to Covered |
| Lead Record ID | Compliance / Contracts | Matching transaction record ID | Property, unit, leasing period, and named lessees must match this lease |
| Lead Record Status | Compliance workflow | `Completed` or `Approved Exempt` | All other states block create/send/signature actions |
| Lead Completion Timestamp | Compliance workflow | Nonblank immutable timestamp | Signature action remains disabled until present; audit later confirms it precedes each binding lease signature |
| Lead Exemption Approval | Legal review | Attorney approval reference | Required only for Approved Exempt |
| Lead Recipient Reconciliation | Sign / Contracts | Exact match | Named lessees, disclosure recipients, acknowledgments, and certifications must be the same set |
| Lead Audit / Archive ID | Sign / WorkDrive | Nonblank immutable record | Required before release |

### Gate expression

```text
lease_signature_enabled =
  (
    lead_record.status == "Completed"
    AND lead_record.transaction_id == lease.transaction_id
    AND lead_record.property_id == lease.property_id
    AND lead_record.unit_id == lease.unit_id
    AND lead_record.named_lessees == lease.named_lessees
    AND lead_record.completion_timestamp IS NOT BLANK
    AND lead_record.audit_id IS NOT BLANK
  )
  OR
  (
    lead_record.status == "Approved Exempt"
    AND lead_record.exemption_evidence_id IS NOT BLANK
    AND lead_record.exemption_counsel_approval IS NOT BLANK
  )
```

After execution, the audit must prove that `lead_record.completion_timestamp` preceded every named lessee's binding lease-signature timestamp.

If Zoho cannot enforce field and document order inside a single transaction, complete a standalone lead-disclosure transaction first and create/send the lease transaction only after the first transaction passes this gate. Do not rely on a later lessor countersignature to cure late disclosure.
