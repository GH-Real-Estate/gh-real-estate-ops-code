# Pet and Assistance Animal Addendum Merge Fields

> **Status:** Proposed sanitized technical map. Field/API names must be created or confirmed in Zoho before use. This file contains no tenant data and is not the addendum, an accommodation record, or legal advice. The actual template remains an attorney-review draft outside this repository.

## Scope

This map supports one consolidated Pet and Assistance Animal Addendum with up to three animals plus a controlled continuation page. It is designed to keep ordinary-pet financial terms separate from assistance-animal accommodations and to prevent confidential disability information from entering the signed Lease packet or this repository.

The listed API/link names are proposed names, not a representation that the fields already exist. Treat every proposed name as `TBD` until it is confirmed against the live Zoho configuration. Do not deploy a mapping that points to a guessed field.

## Source and Ownership Rules

| Data group | Intended source of truth | Notes |
|---|---|---|
| Lease, premises, and tenant identity | Zoho CRM / approved lease record | Confirm the live module and API names |
| Ordinary-pet approval and descriptive data | Zoho CRM or approved animal subform | Use a repeatable animal record if supported; never use live data in repository tests |
| Accommodation decision and operational conditions | Restricted accommodation workflow | Merge only decision status and operational terms needed to implement it; keep support material private |
| Pet deposit and recurring pet rent | Approved lease record, synchronized with Zoho Books as designed | The final source-of-truth and invoicing owner require business approval |
| Signatures and signing dates | Zoho Sign / Zoho Contracts | Do not merge stored signature images |
| Final executed document | Zoho Contracts / Zoho Sign / Zoho WorkDrive | Never store a signed or tenant-specific merged document in GitHub |

## Document and Lease Fields

| Contract merge field | Intended source | Proposed source field / API name | Type / format | Validation |
|---|---|---|---|---|
| Lease Number | Lease record | `Lease_Number` | Text | Required; match the parent Lease |
| Lease Date | Lease record | `Lease_Date` | Date, `YYYY-MM-DD` | Required |
| Addendum Effective Date | Lease/addendum record | `Animal_Addendum_Effective_Date` | Date, `YYYY-MM-DD` | Required; do not precede an approval/interim date without review |
| Premises Street Address | Property record | `Property_Street_Address` | Text | Required; use the authoritative property record |
| Premises Unit | Lease record | `Unit_Number` | Text | Required |
| Premises City | Property record | `Property_City` | Text | Required |
| Premises State | Property record | `Property_State` | Two-letter code | Required; expected `KS` for the current property |
| Premises ZIP | Property record | `Property_ZIP` | Text | Required; preserve leading zero if ever applicable |
| Landlord Legal Name | Configuration | `Landlord_Legal_Name` | Text | Required; approved controlled value, not free text |
| Tenant 1 Printed Name | Lease record | `Tenant_1_Legal_Name` | Text | Required |
| Tenant 2 Printed Name | Lease record | `Tenant_2_Legal_Name` | Text | Optional only when no second affected tenant exists |
| Tenant 3 Printed Name | Lease record | `Tenant_3_Legal_Name` | Text | Optional only when no third affected tenant exists |

Do not add disability, diagnosis, medical-provider, support-document, immigration, banking, government-ID, or other unnecessary sensitive fields to this map.

## Derived Household-Status Fields

These fields should be calculated from the animal schedule, not independently entered.

| Contract merge field | Proposed API/link name | Type | Derivation / validation |
|---|---|---|---|
| No Ordinary Pet Approved | `No_Ordinary_Pet_Approved` | Boolean | `true` only when Ordinary-Pet count is zero |
| One or More Ordinary Pets Approved | `Has_Ordinary_Pet` | Boolean | `true` when Ordinary-Pet count is at least one |
| Approved Assistance Animal Confirmed | `Has_Approved_Assistance_Animal` | Boolean | `true` when an animal classification is `Approved Assistance Animal` |
| Interim Arrangement Stated | `Has_Interim_Assistance_Animal` | Boolean | `true` when an animal classification is `Interim Assistance Animal` |
| Ordinary-Pet Count | `Ordinary_Pet_Count` | Integer | Count only animals classified `Ordinary Pet`; range `0-3` unless a signed continuation page is used |
| Approved Assistance-Animal Count | `Approved_Assistance_Animal_Count` | Integer | Count only approved assistance animals |
| Interim Assistance-Animal Count | `Interim_Assistance_Animal_Count` | Integer | Count only interim assistance animals |

Reject generation when a checkbox disagrees with the schedule or when all status fields are false while an animal row is populated.

## Per-Animal Fields

Use `n = 1, 2, 3`. Each populated animal row must have exactly one classification. Do not leave partially populated rows.

| Contract merge field pattern | Intended source | Proposed API/link pattern | Type / allowed values | Validation |
|---|---|---|---|---|
| Animal `n` Name / Identifier | Animal record | `Animal_{n}_Name` | Text | Required for a populated row |
| Animal `n` Classification | Animal/accommodation decision | `Animal_{n}_Classification` | Picklist: `Ordinary Pet`, `Approved Assistance Animal`, `Interim Assistance Animal` | Exactly one value required |
| Animal `n` Species / Type | Animal record | `Animal_{n}_Species_Type` | Text | Required; do not use as a categorical accommodation denial rule |
| Animal `n` Color / Identifying Description | Animal record | `Animal_{n}_Description` | Text | Required; operational identification only |
| Animal `n` Approval or Interim Effective Date | Decision/addendum record | `Animal_{n}_Effective_Date` | Date, `YYYY-MM-DD` | Required |
| Animal `n` Breed / Mix | Ordinary-pet record | `Animal_{n}_Breed_Mix` | Text | Required only for `Ordinary Pet`; otherwise suppress / not applicable |
| Animal `n` Age | Ordinary-pet record | `Animal_{n}_Age` | Text or decimal years | Required only for `Ordinary Pet`; otherwise suppress / not applicable |
| Animal `n` Approximate Adult Weight | Ordinary-pet record | `Animal_{n}_Adult_Weight_Lb` | Decimal pounds | Required only for `Ordinary Pet`; nonnegative |
| Animal `n` Photo Received | Ordinary-pet record | `Animal_{n}_Photo_Received` | Boolean / N/A | `N/A` for approved or interim assistance animals unless counsel approves a lawful need |
| Animal `n` Municipal License / Expiration | Animal record | `Animal_{n}_License_Expiration` | Date or `Not Applicable` | Populate only when legally applicable; current requirement must be checked |
| Animal `n` Required Vaccination Proof | Animal record | `Animal_{n}_Vaccination_Proof_Status` | Picklist: `Received`, `Not Applicable`, `Pending Lawful Update` | Never use this field to store a medical document |

If more than three animals are involved, generate a signed continuation page that repeats the same fields and classifications. Do not overwrite or concatenate animal records into an unstructured text field.

## Emergency and Interim Fields

| Contract merge field | Intended source | Proposed API/link name | Type / format | Validation |
|---|---|---|---|---|
| Emergency Caregiver Name | Animal/addendum record | `Animal_Emergency_Caregiver_Name` | Text | Optional; obtain consent and limit access |
| Emergency Caregiver Phone | Animal/addendum record | `Animal_Emergency_Caregiver_Phone` | Phone | Required when caregiver name is populated; do not place in repository fixtures |
| Interim Arrangement Terms | Restricted accommodation workflow | `Animal_Interim_Operational_Terms` | Long text | Required when an interim animal exists; operational terms only, no disability details |
| Interim Arrangement Expiration | Restricted accommodation workflow | `Animal_Interim_Expiration_Date` | Date, `YYYY-MM-DD` | Required when an interim animal exists; route for review before expiration |
| Accommodation Decision Date | Restricted accommodation workflow | `Animal_Accommodation_Decision_Date` | Date, `YYYY-MM-DD` | Required for each approved assistance-animal decision; may be validation-only rather than merged |
| Restricted Accommodation Record ID | Restricted accommodation workflow | `Animal_Accommodation_Private_Record_ID` | Internal identifier | Validation/reference only; **never merge into the document or repository payloads** |

## Ordinary-Pet Financial Fields

These fields apply only to animals classified `Ordinary Pet`. Approved and interim assistance animals must be excluded from count and charge calculations.

| Contract merge field | Intended source | Proposed API/link name | Type / format | Validation |
|---|---|---|---|---|
| Aggregate Refundable Additional Pet Security Deposit | Approved lease/financial record | `Pet_Deposit_Amount` | Currency, two decimals | Required as `0.00` or approved amount; aggregate for all Ordinary Pets; must be `<= 0.5 x Periodic Rent` |
| Pet Deposit Due Date | Lease/addendum record | `Pet_Deposit_Due_Date` | Date, `YYYY-MM-DD` | Required when deposit amount is greater than zero |
| Pet Deposit Not Applicable | Lease/addendum record | `Pet_Deposit_Not_Applicable` | Boolean | Must be `true` when no Ordinary Pet exists; mutually exclusive with positive deposit |
| Monthly Pet Rent Rate | Approved lease/financial record | `Pet_Rent_Rate_Per_Ordinary_Pet` | Currency, two decimals | Required as `0.00` or approved rate |
| Chargeable Ordinary-Pet Count | Derived | `Pet_Rent_Chargeable_Count` | Integer | Must equal the approved chargeable Ordinary-Pet count; assistance animals excluded |
| Total Monthly Pet Rent | Derived / approved override | `Pet_Rent_Total_Monthly` | Currency, two decimals | Normally rate multiplied by count; require documented approval for any exception |
| First Monthly Pet Rent Due Date | Lease/addendum record | `Pet_Rent_First_Due_Date` | Date, `YYYY-MM-DD` | Required when total monthly pet rent is greater than zero |
| First Partial-Month Pet Rent | Approved lease/financial record | `Pet_Rent_First_Partial_Amount` | Currency, two decimals | Populate only under an attorney-approved proration rule; otherwise `0.00` and N/A |
| First Partial-Month Pet Rent N/A | Lease/addendum record | `Pet_Rent_First_Partial_Not_Applicable` | Boolean | Required when no partial amount is charged |
| Periodic Rent for Deposit-Cap Validation | Lease record | `Periodic_Rent_For_Pet_Deposit_Cap` | Currency, two decimals | Validation-only; do not display as a new addendum charge |

Financial guardrails:

- Fail generation if a charge field is blank. Use `0.00` plus the corresponding not-applicable flag where no charge applies.
- The aggregate refundable additional pet deposit may not exceed one-half of one month's periodic rent under K.S.A. 58-2550.
- Do not create a per-animal deposit, nonrefundable pet administration fee, assistance-animal charge, duplicate late-fee formula, or duplicate interest formula.
- Label monthly pet rent as an `Other Charge`, not `Base Rent`.
- Do not create a Zoho Books invoice, recurring charge, or deposit entry until the final lease/addendum, source-of-truth system, accounting treatment, item IDs, and duplicate-prevention method are approved.

## Signer and Audit Fields

| Contract / workflow field | Intended source | Proposed API/link name | Type / format | Validation |
|---|---|---|---|---|
| Tenant 1 Signer Email | Lease record | `Tenant_1_Signer_Email` | Email | Workflow-only; never include in repository fixtures |
| Tenant 2 Signer Email | Lease record | `Tenant_2_Signer_Email` | Email | Optional when no second affected tenant exists |
| Tenant 3 Signer Email | Lease record | `Tenant_3_Signer_Email` | Email | Optional when no third affected tenant exists |
| Landlord Representative Printed Name | Authorized-user record | `Landlord_Representative_Name` | Text | Required |
| Landlord Representative Signer Email | Authorized-user record | `Landlord_Representative_Signer_Email` | Email | Workflow-only; approved authorized signer |
| Tenant Signature / Date | Zoho Sign | Platform-managed | Signature/date | Use the governed [Zoho Sign text-tag registry](../../zoho-sign/field-tags/zoho-contracts-text-tag-registry.md); never merge a stored signature image; for accommodation terms, do not make tenant signature a condition of an otherwise required accommodation |
| Landlord Signature / Date | Zoho Sign | Platform-managed | Signature/date | Use the governed [Zoho Sign text-tag registry](../../zoho-sign/field-tags/zoho-contracts-text-tag-registry.md); required to confirm the stated approval or interim arrangement |
| Template Version | Controlled configuration | `Animal_Addendum_Template_Version` | Text/date | Required; must identify the attorney-approved production version |
| Generation Timestamp | Workflow | `Animal_Addendum_Generated_At` | ISO 8601 timestamp | Audit only; Central Time display if shown to operators |
| Generated By | Workflow | `Animal_Addendum_Generated_By` | User ID | Audit only; avoid unnecessary personal data in logs |
| Parent Lease Record ID | Lease record | `Parent_Lease_Record_ID` | Internal identifier | Workflow-only; do not display in the contract |

## Required Validation Logic

Before document generation:

1. Confirm the template version is marked attorney-approved and production-active.
2. Confirm all document/lease fields are populated and match the parent Lease.
3. Confirm every populated animal row is complete and has exactly one classification.
4. Recalculate household-status booleans and all classification counts from the animal rows.
5. Suppress ordinary-pet-only descriptive fields for approved/interim assistance animals unless an approved legal rule requires them.
6. Force all pet charges to `0.00` / not applicable when there is no Ordinary Pet.
7. Exclude approved/interim assistance animals from deposit and pet-rent calculations.
8. Enforce the aggregate pet-deposit cap using the current periodic-rent value.
9. Recalculate monthly pet rent and reject an unexplained mismatch.
10. Require interim operational terms and expiration when any animal is interim.
11. Scan merged values and attachments for medical information, accommodation support documents, signature images, tenant PII not needed in the contract, and secrets.
12. Create an immutable audit event without logging tenant names, animal names, phone numbers, emails, accommodation evidence, or document contents.

After generation, a human reviewer must compare the preview against the approved template and parent Lease before sending it for signature.

## Sanitized Test Matrix

Use synthetic values only.

| Test | Expected result |
|---|---|
| One Ordinary Pet with completed deposit and monthly pet rent | Generates; charges reconcile; deposit cap passes |
| Two Ordinary Pets with one aggregate deposit | Generates; no duplicate/per-animal deposit |
| One Approved Assistance Animal and no Ordinary Pet | Generates with all pet charges `0.00` / N/A; no ordinary-pet fields or medical information |
| One Interim Assistance Animal | Generates only when interim terms and expiration are present; no pet charges |
| Mixed household: one Ordinary Pet plus one Approved Assistance Animal | Generates; only the Ordinary Pet is included in charge counts |
| Blank classification or partially populated animal row | Blocked |
| Blank charge field | Blocked even though the template would treat blank as `$0.00` |
| Aggregate pet deposit greater than one-half month's periodic rent | Blocked |
| Assistance animal included in pet-rent count | Blocked |
| Accommodation support document or diagnosis included in merge payload | Blocked and routed to privacy review |
| Tenant signature missing for an already granted accommodation | Do not treat the accommodation as denied or void; route for lawful workflow handling |

## Production Gate and Rollback

Do not activate this map until:

- Kansas counsel approves the final addendum and assistance-animal decision workflow.
- The full current lease has been reconciled.
- Every live Zoho module, field/API name, picklist value, permission, signature role, financial owner, and validation rule has been verified.
- Sanitized tests pass and a rendered preview is manually reviewed.
- The legacy templates remain available for rollback until the consolidated workflow is accepted.

Merging this file does not deploy the template. Roll back the documentation by reverting this file and `docs/business-rules/animal-addendum-rules.md`; roll back a live template only through the approved Zoho Contracts/WorkDrive document-control process.
