# Lead-Based Paint Disclosure and Pre-Execution Gate

**Status:** Attorney review required before production use  
**Last checked:** July 14, 2026  
**Property context:** GH Real Estate, LLC; 9401 Nieman Road, Overland Park, Kansas

## Rule in one sentence

For covered target housing, GH must give every person or entity who will actually become a named lessee the completed lead disclosure, all available lead records and reports, and the current federally approved pamphlet, and collect the required acknowledgments and certifications **before that lessee becomes contractually obligated**.

This does **not** require a disclosure signature from every inquiry, applicant, possible occupant, minor, or adult occupant who will not be a lessee.

## Fail-closed coverage decision

Public sources in the GH legal source pack indicate a 1963 construction year, but the repository does not yet contain an official county-record construction-year source. Until reliable year evidence or a Kansas-attorney-approved exemption is stored in the property file:

- treat every apartment at 9401 Nieman Road as pre-1978 target housing;
- do not allow a blank, free-text-only, or assumed exemption;
- require the lead gate for each new lease and incoming lessee.

Potential exemptions include post-1977 construction, certified lead-free housing, qualifying short-term leases of 100 days or less without renewal or extension, certain zero-bedroom or elderly/disability housing, and certain renewals where a complete prior disclosure was made and no new information exists. The exact exemption and supporting evidence must be documented and approved before use.

## Required pre-obligation package

1. A property- and transaction-specific disclosure containing the exact federal Lead Warning Statement.
2. Lessor's completed selection regarding known lead-based paint or hazards, with details when known.
3. Lessor's completed selection regarding available records and reports.
4. Every available dwelling-unit, common-area, and relevant building-wide lead record or report.
5. The current approved pamphlet, **Protect Your Family From Lead in Your Home**, January 2026 English edition, EPA-747-K-26-001, or the matching approved translation when the contract is in another language.
6. Lessee acknowledgments for disclosure/records and pamphlet receipt.
7. Certifications and dates for the lessor, each named lessee, and applicable agents.
8. Delivery, electronic-consent, completion, audit, and retention evidence.

The pamphlet itself is delivered but is not a separate tenant-signature form. There is no additional generic private-rental “HUD lead notice” beyond a compliant disclosure and the joint EPA/CPSC/HUD pamphlet. Program-specific HUD forms are used only when the relevant program actually applies.

## Required Lead Warning Statement

> Housing built before 1978 may contain lead-based paint. Lead from paint, paint chips, and dust can pose health hazards if not managed properly. Lead exposure is especially harmful to young children and pregnant women. Before renting pre-1978 housing, lessors must disclose the presence of known lead-based paint and/or lead-based paint hazards in the dwelling. Lessees must also receive a federally approved pamphlet on lead poisoning prevention.

Do not edit, shorten, or paraphrase this statement in the production disclosure.

## Who completes or signs

- **Lessor:** completes the knowledge and records selections and signs the certification.
- **Every actual named lessee:** acknowledges disclosure/records and pamphlet receipt and signs the certification before becoming obligated.
- **Lessor's agent:** completes the required agent acknowledgment/certification when the role exists.
- **Lessee's agent paid by the lessor:** completes the applicable acknowledgment/certification.
- **Not federal signatories solely by status:** mere applicants, potential occupants, minors who are not lessees, and adult occupants who are not lessees.

If a GH application, holding deposit, reservation, acceptance, or other instrument can itself create a contractual obligation, counsel must classify it and move the disclosure gate before GH accepts that obligation.

## Mandatory two-stage system sequence

1. Admin creates a nonbinding draft lease/transaction ID but does not release the lease for signature.
2. Admin identifies the property/unit, contract language, leasing period, named lessees, and applicable agent roles.
3. Admin documents covered/exempt status; covered is the default until approved evidence supports an exemption.
4. Lessor completes the knowledge and records selections. Never prefill “no knowledge” or “no records” as a global template default.
5. Admin checks unit, common-area, and building-wide lead files and attaches every available responsive record.
6. GH sends the completed standalone Addendum A, responsive records, and exact current pamphlet to every named lessee.
7. Each named lessee completes both acknowledgments and the certification; lessor and applicable agents complete their fields.
8. The system validates required choices, details, recipients, signatures, dates, attachments, electronic-delivery evidence, and the signing audit.
9. The completed lead PDF becomes immutable with status `Completed`; store its file ID, SHA-256 hash, completion timestamp, audit ID, archive-record ID, and retention date.
10. Attach the **exact completed Addendum A PDF** to the matching lease as recipient-visible **Exhibit LD-1**; verify the attachment hash equals the completed disclosure hash.
11. Only after Exhibit LD-1 is part of the lease package may the lease be released for a binding lessee signature.
12. After final execution, archive the final contract-package hash and attachment/audit identifiers.

Use two sequential Zoho transactions unless counsel confirms that one transaction can technically enforce the same order. A WorkDrive link, an internal-only Contracts attachment, or a lease clause that merely references the disclosure does not replace inclusion of the exact completed disclosure in or as an attachment to the final contract. A later landlord countersignature does not cure a lessee who was already bound before disclosure.

## Electronic delivery

Electronic delivery must preserve legally sufficient E-SIGN evidence, including the consumer's affirmative consent, paper-copy option, withdrawal procedures and consequences, access/retention instructions, hardware/software requirements, and proof the recipient can access the electronic records. Fall back to paper when valid electronic delivery cannot be established.

Do not use a delivery link that omits attachments, expires before reasonable access, or prevents the lessee from retaining the disclosure, records, pamphlet, or final lease package.

## Language

The required disclosure content must be provided in the language used for the contract. Deliver the matching approved pamphlet translation when available. Escalate unavailable-language or accessibility issues to counsel; do not treat them as a routine bypass.

## Renewals and incoming lessees

- A renewal generally does not require repeat disclosure when a complete disclosure was previously made and the lessor has no new information; preserve the prior record.
- Provide newly obtained information and complete any required renewed disclosure before the renewal becomes binding.
- Treat an incoming lessee or sublessee as a new recipient and complete the lead gate before that person becomes obligated.
- Preserve the exact prior and current pamphlet editions and delivery evidence.

## Records and retention

Retain the completed disclosure for at least three years from commencement of the leasing period. GH's operational archive should also retain:

- all disclosed reports and attachments;
- the exact pamphlet edition, source URL, file hash, and language;
- delivery recipients, method, and timestamps;
- electronic-consent or paper-fallback evidence;
- all signatures, initials, and platform audit data;
- completed-disclosure PDF file ID and SHA-256 hash;
- Exhibit LD-1 attachment ID and hash;
- final lease contract ID and final contract-package hash;
- the internal completion/archive record;
- exemption evidence and attorney approval, when used.

A three-year federal minimum is not a deletion instruction. Counsel should approve a longer retention schedule that fits other claims, contract, and records-management requirements.

## Current lease reconciliation

The revised lead-first attorney-review lease uses one production method:

- the former embedded disclosure form has been removed;
- the standalone disclosure is **Addendum A** and is completed first;
- the lease contains an incorporation clause; and
- the exact executed Addendum A PDF must be attached to the lease package as **Exhibit LD-1** before the lease is sent for signature.

Do not restore the former embedded form or send two competing disclosure forms with duplicate or inconsistent selections. The lease's separate lead-safe renovation restriction remains in place.

## Primary authorities and official materials

- [42 U.S.C. § 4852d](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section4852d&num=0&edition=prelim)
- [40 C.F.R. part 745, subpart F](https://www.ecfr.gov/current/title-40/chapter-I/subchapter-R/part-745/subpart-F)
- [24 C.F.R. part 35, subpart A](https://www.ecfr.gov/current/title-24/subtitle-A/part-35/subpart-A)
- [EPA real-estate disclosure guidance](https://www.epa.gov/lead/real-estate-disclosures-about-potential-lead-hazards)
- [January 2026 approved pamphlet](https://www.epa.gov/system/files/documents/2026-02/protectyourfamily_pamphlet_2026_3.pdf)
- [EPA sample lessor disclosure](https://www.epa.gov/sites/default/files/documents/lesr_eng.pdf)

This document is an operational control for attorney review, not legal advice or a substitute for property-specific counsel.
