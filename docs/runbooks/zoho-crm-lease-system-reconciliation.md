# Zoho CRM Lease-System Production Reconciliation

**As of:** July 24, 2026

**Scope:** Sanitized Zoho CRM configuration evidence and remaining manual handoff

**Organization gate:** `GH Real Estate` / `production`

**Record-data boundary:** No CRM records or tenant/applicant PII were read, created, updated, or backfilled

## Outcome

The production CRM now has the bounded Rental Application and Lease configuration that could be created and verified safely through the approved metadata/configuration tools. This is not an end-to-end deployment.

| Workstream | Status | Evidence boundary |
|---|---|---|
| Production organization gate | Passed | Both approved CRM connectors returned `GH Real Estate` and `production` before configuration work. |
| Rental Application fields | Applied and read back | 15 fields created in `Deals`; actual API names, types, lookups, tooltips, choices, and placement were verified. |
| Lease fields and sections | Applied and read back | 33 fields and eight sections created in `Leases`; 40 reconciled fields were placed and read back. |
| Lease Status | Values/colors/history applied; order/default/required partial | History tracking was enabled and target choices/colors were added without deleting legacy values. Live label `Ready For Contract` remains capitalized, but live order interleaves target/legacy values and places new `Draft` last because the current tool cannot set order. Default remains null and the field remains optional. |
| Required/default/readiness controls | Blocked | The current configuration tool cannot express and verify the complete requirement safely. |
| Approved Application to Lease automation | Unsupported | No reusable workflow task was verified, and the approved connectors cannot enumerate or create the required durable custom function/button. |
| Zoho Contracts extension and signer routing | Manual | No Contracts extension, button, related-list, field-mapping, contract-type, or signer configuration was changed. |
| Residential Lease Agreement | Blocked | It remains Draft only, unpublished, execution-blocked, attorney-review-required, and has 29 open production gates. |

This document intentionally contains no organization, module, layout, section, field, workflow, or record IDs.

## Architecture and ownership

```text
Zillow inquiry
-> CRM Lead
-> Contact + Rental Application (Deals)
-> approved Rental Application
-> separate Lease (Leases)
-> manual Request Contract handoff
-> Zoho Contracts
-> Zoho Sign
-> signed status/PDF related back to Lease
-> Books and portal activation as later, separate workflows
```

- Zillow/Catalyst writes raw inquiries to `Leads` only.
- `Contacts` owns people.
- Rental Applications, display-renamed from standard Deals and using API `Deals`, owns screening and approval.
- Leases, using verified custom-module API `Leases`, owns approved relationships and frozen contract-request inputs.
- Zoho Contracts owns drafting, approvals, lifecycle, and the final agreement snapshot.
- Zoho Sign owns signatures and signing evidence.
- Zoho Books owns invoices, payments, balances, deposits, and accounting truth.
- GitHub owns sanitized technical governance, not production records or proof of Contracts deployment.

## Manifest evidence and controls

Every target below uses exactly one Phase 2 classification. When a verified existing field also had a distinct requested metadata action, the field identity and that separable action are classified independently (for example, `Stage` reuse versus its unsupported value mutation). Field-specific metadata is split between this reconciliation and the governed CSV row:

- this document records actual API, type, lookup, applied/blocked state, workflow conflict, and rollback class;
- the governed CSV records the field's business `required` condition, exact live-readback `help_text`, section, choice definition, intended Contracts destination, notes, and source evidence; and
- [`zillow-to-crm-to-contracts.md`](../../src/zoho-crm/field-maps/zillow-to-crm-to-contracts.md), [`lease-merge-fields.md`](../../src/zoho-contracts/field-maps/lease-merge-fields.md), and the [manual Contracts runbook](../../src/zoho-contracts/runbooks/crm-leases-extension-manual-deployment.md) provide the approved cross-system destination/control detail.

The CSV `required` value records live enforcement/readback: all 48 created fields are optional with default null. Intended stage/conditional requirements are recorded in `help_text` and notes but are not currently enforced; the complete conditional mandatory/default/readiness rules remain unsupported.

No unique constraint was authorized or applied to any of the 48 created fields, and none may be used as an idempotency key without a later verified uniqueness design.

| Classification | Live action and dependency | Common rollback |
|---|---|---|
| `create` | Field was absent, created, and read back. No pre-existing workflow could depend on an absent field, and no new workflow was created. Intended downstream use is documented but inactive. | After a dependency audit, remove from active layouts and retire; do not delete records or backfill/clear values. |
| `reuse_verified` | Compatible live field/API was read back and reused. Preserve its dependencies and do not create an alias. | Restore only metadata changed by this task after a workflow/report dependency audit; never delete the field. |
| `update_metadata` | Compatible live field was preserved while explicitly approved metadata was changed/read back. | Restore captured prior metadata only after a dependency/audit-history review; preserve field/value IDs and record data. |
| `superseded_do_not_create` | Candidate conflicts with the approved architecture or a verified field. No live delete or create. | None; preserve any legacy live field until separately audited. |
| `blocked_ambiguous` | No target create/reuse decision or semantic change was made. Existing field meaning, format, or equation must be resolved first. | None; no target write occurred. |
| `unsupported_by_current_mcp` | Requested action cannot be expressed and read back completely with the approved tools. No partial substitute is allowed. | Revert only the separately identified partial metadata, if any; otherwise none. |
| `manual_contracts_mapping` | Contracts extension/field/signer action is outside the approved CRM tool surface and remains unperformed. | Follow the before-state/rollback steps in the manual runbook only after a later authorized manual deployment. |

Sensitivity is determined by business meaning, not by this metadata-only audit:

- person lookups, legal names, email fields, application dates, and decisions are confidential applicant/tenant data;
- rent, deposit, credit, and amount fields are confidential financial/lease data;
- premises and lease-term snapshots are confidential tenancy data; and
- addenda, nonstandard-term, attorney-review, status, and workflow controls are confidential operational/legal data.

No field values were accessed during verification.

## Applied production CRM configuration

### Rental Applications -- API `Deals`

All 15 fields below were created in the `Rental Application Information` section and read back through the audit connector. Their API-name status is `verified_live_mcp`. All created-field defaults were read back as null and history tracking as disabled. Conditional business requirements remain process requirements unless a complete enforceable rule is later deployed.

| Field label | Actual API name | CRM type | Lookup target | Classification |
|---|---|---|---|---|
| Unit | `Unit` | Lookup | `Units` | `create` |
| Source Lead | `Source_Lead` | Lookup | `Leads` | `create` |
| Co-Applicant 1 | `Co_Applicant_1` | Lookup | `Contacts` | `create` |
| Co-Applicant 2 | `Co_Applicant_2` | Lookup | `Contacts` | `create` |
| Application Received At | `Application_Received_At` | Date/Time | -- | `create` |
| Decision | `Decision` | Pick List | -- | `create` |
| Decision Date | `Decision_Date` | Date | -- | `create` |
| Approved Security Deposit | `Approved_Security_Deposit` | Currency | -- | `create` |
| Approved Lease Commencement Date | `Approved_Lease_Commencement_Date` | Date | -- | `create` |
| Approved Lease Term End Date | `Approved_Lease_Term_End_Date` | Date | -- | `create` |
| Approved Possession Date | `Approved_Possession_Date` | Date | -- | `create` |
| Addenda Required | `Addenda_Required` | Multi-Select Pick List | -- | `create` |
| Nonstandard Terms? | `Nonstandard_Terms` | Checkbox | -- | `create` |
| Nonstandard Terms Notes | `Nonstandard_Terms_Notes` | Multi-Line, 2,000 characters | -- | `create` |
| Attorney Review Required? | `Attorney_Review_Required` | Checkbox | -- | `create` |

The governed [`rental-applications.csv`](../../src/zoho-crm/field-maps/crm-module-fields/rental-applications.csv) preserves the exact tooltip text, choice values, and colors returned by live readback. The submitted creation payload used normalized/paraphrased wording for some tooltips instead of the user-supplied prose, including Unit, Application Received At, and Addenda Required; the tool stored and read that submitted text back exactly. The CSV is evidence of the live result, not proof of verbatim prompt-text equality.

`Decision` was verified with these local ordered values:

| Value | Color |
|---|---|
| Pending | `#D97706` |
| Approved | `#16A34A` |
| Approved with Conditions | `#EA580C` |
| Denied | `#DC2626` |
| Withdrawn | `#6B7280` |
| Duplicate | `#6B7280` |
| No Response | `#6B7280` |

The standard `Stage` field was not changed, and the requested target Stage list is not claimed to exist live. Final audit found 18 live display options, all uncolored, with default null and history tracking enabled. Their underlying actual values are stale or semantically misaligned; for example, display `New Application` resolves to actual value `On Hold - Holding Deposit Received`, and display `Screening Review` resolves to `Rejected`. The governed Stage row in [`rental-applications.csv`](../../src/zoho-crm/field-maps/crm-module-fields/rental-applications.csv) preserves the exact display-to-actual pairs. An additive write was unsafe because the current tool could not reconcile those pairs with pipeline/probability semantics. The standard `Amount` field was also left unchanged because the active Big Deal Rule depends on `Amount >= 1000` together with `Probability = 100`.

The targeted standard Deals fields were classified separately from the 15 creates:

| Field/action | Actual API | Classification | Live requirement/default and dependency |
|---|---|---|---|
| Primary Applicant relationship | `Contact_Name` | `reuse_verified` | Required standard lookup to `Contacts`; copied to the Lease `Tenant` relationship only through a later approved workflow. |
| Property relationship | `Account_Name` | `reuse_verified` | Optional standard lookup to `Accounts`; copied to Lease `Property` only through a later approved workflow. |
| Stage field identity | `Stage` | `reuse_verified` | Required, default null, history enabled. Existing field remains authoritative; requested value mutation is separately `unsupported_by_current_mcp`. |
| Approved Base Rent use of Amount | `Amount` | `blocked_ambiguous` | Active Big Deal Rule dependency prevents repurposing until meaning/reporting/workflow impact is approved. |

### Leases -- API `Leases`

The live custom-module API name `Leases` was verified before configuration. The following 33 fields were created and read back; every API name below has status `verified_live_mcp`.

| Field label | Actual API name | CRM type | Lookup target | Classification |
|---|---|---|---|---|
| Lease Type | `Lease_Type` | Pick List | -- | `create` |
| Rental Application | `Rental_Application` | Lookup | `Deals` | `create` |
| Previous Lease | `Previous_Lease` | Lookup | `Leases` | `create` |
| Property | `Property` | Lookup | `Accounts` | `create` |
| Unit | `Unit` | Lookup | `Units` | `create` |
| Tenant 2 | `Tenant_2` | Lookup | `Contacts` | `create` |
| Tenant 3 | `Tenant_3` | Lookup | `Contacts` | `create` |
| Guarantor | `Guarantor` | Lookup | `Contacts` | `create` |
| Agreement Date | `Agreement_Date` | Date | -- | `create` |
| Premises Street Line 1 | `Premises_Street_Line_1` | Single Line | -- | `create` |
| Premises Apartment Number | `Premises_Apartment_Number` | Single Line | -- | `create` |
| Premises City | `Premises_City` | Single Line | -- | `create` |
| Premises State | `Premises_State` | Single Line | -- | `create` |
| Premises ZIP Code | `Premises_ZIP_Code` | Single Line | -- | `create` |
| Total Monthly Pet Rent Amount | `Total_Monthly_Pet_Rent_Amount` | Currency | -- | `create` |
| Base Storage Unit Rent Amount | `Base_Storage_Unit_Rent_Amount` | Currency | -- | `create` |
| Total Monthly Storage Rent Amount | `Total_Monthly_Storage_Rent_Amount` | Currency | -- | `create` |
| Next Total Monthly Rent Due Date | `Next_Total_Monthly_Rent_Due_Date` | Date | -- | `create` |
| Prorated Rent Start Date | `Prorated_Rent_Start_Date` | Date | -- | `create` |
| Prorated Rent End Date | `Prorated_Rent_End_Date` | Date | -- | `create` |
| Pet Security Deposit Amount | `Pet_Security_Deposit_Amount` | Currency | -- | `create` |
| Prorated Pet Rent Amount | `Prorated_Pet_Rent_Amount` | Currency | -- | `create` |
| Prorated Storage Unit Rent Amount | `Prorated_Storage_Unit_Rent_Amount` | Currency | -- | `create` |
| Holding Deposit Credit Applied | `Holding_Deposit_Credit_Applied` | Currency | -- | `create` |
| Total Due Before Possession | `Total_Due_Before_Possession` | Currency | -- | `create` |
| Tenant 2 Legal Name Snapshot | `Tenant_2_Legal_Name_Snapshot` | Single Line | -- | `create` |
| Tenant 2 Email Snapshot | `Tenant_2_Email_Snapshot` | Email | -- | `create` |
| Tenant 3 Legal Name Snapshot | `Tenant_3_Legal_Name_Snapshot` | Single Line | -- | `create` |
| Tenant 3 Email Snapshot | `Tenant_3_Email_Snapshot` | Email | -- | `create` |
| Addenda Required | `Addenda_Required` | Multi-Select Pick List | -- | `create` |
| Nonstandard Terms? | `Nonstandard_Terms` | Checkbox | -- | `create` |
| Nonstandard Terms Notes | `Nonstandard_Terms_Notes` | Multi-Line, 2,000 characters | -- | `create` |
| Attorney Review Required? | `Attorney_Review_Required` | Checkbox | -- | `create` |

The governed `leases-01.csv` through `leases-06.csv` files under [`crm-module-fields`](../../src/zoho-crm/field-maps/crm-module-fields/) preserve the exact tooltip text, choice values, and colors returned by live readback. The submitted creation payload used normalized/paraphrased wording for some tooltip text instead of the user-supplied prose, and the tool stored/read the submitted text exactly. These rows describe the live result and must not be treated as verbatim prompt-text equality.

No Lease workflow rule or field-update action was returned by the supported audit calls. The tool cannot enumerate custom functions/buttons, so absence of a returned workflow is not proof that no external dependency exists; rollback still requires a dependency audit.

These seven compatible live fields were reused rather than duplicated:

| Live field label | Actual API name | Classification | Governed use | Important variance |
|---|---|---|---|---|
| Lease Name | `Name` | `reuse_verified` | Readable record name | Existing module-name field. |
| Tenant | `Tenant` | `reuse_verified` | Primary tenant relationship and intended Party B counterparty | The live label is `Tenant`, not `Primary Tenant`. |
| Lease Start Date | `Lease_Start_Date` | `reuse_verified` | Lease commencement snapshot | Distinct from `Agreement_Date`. |
| Lease End Date | `Lease_End_Date` | `reuse_verified` | Fixed-term end-date snapshot | Contracts destination remains manual/unverified. |
| Move-In Date | `Move_In_Date` | `reuse_verified` | Possession-date snapshot | Not automatically a Contracts destination. |
| Security Deposit | `Security_Deposit` | `reuse_verified` | Approved refundable security-deposit snapshot | Zoho Books remains accounting truth. |
| Lease Status | `Lease_Status` | `update_metadata` | Lease workflow state | Values/colors/history updated; order/default/required remain unenforced. |

The following sections were created in this order after protected or legacy sections, and 40 created/reused fields were moved into them with final placement/order read back:

1. Lease Identity and Status
2. Relationships
3. Lease Dates
4. Premises Snapshot
5. Monthly Charges
6. Initial Amounts
7. Additional Tenants
8. Contract Controls

`Lease Type` was verified with local values `Original` (`#2563EB`) and `Renewal` (`#16A34A`).

`Lease Status` history tracking was enabled. Target values and colors were added without removing any legacy value:

| Governed target | Live result | Color |
|---|---|---|
| Draft | Draft | `#2563EB` |
| Ready for Contract | Ready For Contract | `#7C3AED` |
| Contract in Progress | Contract in Progress | `#7C3AED` |
| Signed - Future | Signed - Future | `#16A34A` |
| Active | Active | `#16A34A` |
| Month-to-Month | Month-to-Month | `#2563EB` |
| Renewal Pending | Renewal Pending | `#D97706` |
| Non-Renewing | Non-Renewing | `#EA580C` |
| Terminated | Terminated | `#DC2626` |
| Expired | Expired | `#92400E` |
| Moved Out | Moved Out | `#6B7280` |
| Archived | Archived | `#6B7280` |

The table above is a target-to-live presence/color comparison, not the live order. Post-write order does not match the requested order: target and legacy values interleave, and the new `Draft` value is last. The current tool cannot set picklist order. The case-only `Ready for Contract` rename was not forced because Zoho rejected it as a duplicate. The existing live value and all other legacy values were preserved. The current default remains null and the field remains optional because the approved configuration tool could not set and verify those controls.

### Related source fields verified for the manual handoff

| Module | Live label | Actual API name | Classification | Type/use |
|---|---|---|---|---|
| Contacts | Full Name | `Full_Name` | `reuse_verified` | Text; Contracts Contact Name source |
| Contacts | Email | `Email` | `reuse_verified` | Email; Contracts Contact Email Address source |
| Properties (`Accounts`) | Property Name | `Account_Name` | `reuse_verified` | Record name |
| Properties (`Accounts`) | Street Line 1 | `Street_Line_1` | `reuse_verified` | Premises source |
| Properties (`Accounts`) | City | `City` | `reuse_verified` | Premises source |
| Properties (`Accounts`) | State | `State` | `reuse_verified` | Live-uncolored Pick List; premises source only |
| Properties (`Accounts`) | Zip Code | `Zip_Code1` | `reuse_verified` | Premises source |
| Units | Unit Name | `Name` | `reuse_verified` | Record name |
| Units | Unit Number | `Unit_Number` | `reuse_verified` | Integer; apartment-number source |
| Units | Property | `Property` | `reuse_verified` | Lookup to `Accounts` |

`First_Name` and `Last_Name` also exist on Contacts, but the extension contact-name mapping should use `Full_Name`.

## Blocked, superseded, and manual work

| Item | Classification | Reason and required next action |
|---|---|---|
| Lease Number | `blocked_ambiguous` | The module had an available auto-number slot, but no approved prefix/format was supplied. Approve the human-readable format before creation. |
| Base Rent Amount | `blocked_ambiguous` | Existing `Monthly_Rent` may already represent base or total monthly rent. Determine semantics and dependencies before reuse or new-field approval. |
| Total Monthly Rent Amount | `blocked_ambiguous` | Same `Monthly_Rent` ambiguity; do not create a duplicate. |
| Prorated Base Rent Amount | `blocked_ambiguous` | Existing `Prorated_Rent` semantics are unverified. Reconcile before reuse or creation. |
| First Full Month Base Rent Amount | `verified_live_mcp` input; equation blocked | `First_Full_Month_Base_Rent_Amount` now exists and was read back as Currency(2). Do not duplicate it. The complete initial-amount equation, copy automation, Books reconciliation, readiness gate, Contracts mapping, and controlled Contracts/Sign canary remain unresolved. |
| Rental Application `Stage` values | `unsupported_by_current_mcp` | The tool cannot safely reconcile pipeline and probability semantics; no Stage value was added or removed. |
| Conditional required/default/readiness behavior | `unsupported_by_current_mcp` | The available configuration schema cannot express and verify the complete rule. Do not deploy a partial rule. |
| Lease Status order/default/required controls | `unsupported_by_current_mcp` | Values/colors/history were applied, but the MCP cannot set target order, default `Draft`, or required behavior. Complete these controls manually through a supported admin path and read them back. |
| Supplied tooltip prose remediation | `unsupported_by_current_mcp` | Live readback verified the submitted normalized/paraphrased tooltip payload exactly, not verbatim equality to all 48 user-supplied strings. The current update schema cannot change tooltips; use a later supported update path, then read back each exact supplied string. |
| Approved Application to Create Lease automation | `unsupported_by_current_mcp` | No reusable workflow task was found, and custom functions/buttons cannot be enumerated or created through the approved connectors. |
| Application Stage custom field | `superseded_do_not_create` | Standard `Stage` remains the governed application-stage field. |
| Create Lease Ready? | `superseded_do_not_create` | Durable readiness belongs in validated Lease creation criteria, not a duplicate application flag. No live field was deleted. |
| Lease Created? | `superseded_do_not_create` | The durable Lease relationship, not a checkbox, proves creation. No live field was deleted. |
| Reciprocal Lease Record | `superseded_do_not_create` | The approved architecture uses Lease `Rental_Application`; a reciprocal application field is not created. |
| Zoho Contracts Request ID on Rental Applications | `superseded_do_not_create` | Contracts lifecycle belongs to the separate Lease/Contracts relationship, not the screening record. |
| Zoho Books Customer ID on Rental Applications | `superseded_do_not_create` | Books activation is a later workflow and accounting identifiers do not belong on the screening record. |
| Lease-signing, possession, or active-tenancy Stage values on Rental Applications | `superseded_do_not_create` | Those states belong to Lease/Contracts/Sign; no target Stage value was added. |
| Zoho Contracts extension, Request Contract button, related list, field mappings, Party A/B configuration, and signer routing | `manual_contracts_mapping` | The approved CRM connectors do not expose these Contracts settings. Follow the manual runbook; do not claim completion until read back in the live UI. |

## Final readback

The final metadata readback established:

- 15 created Rental Application fields with expected API names, types, lookup targets, choices/colors, section placement, and the exact submitted tooltip payload returned after creation;
- 33 created Lease fields with expected API names, types, lookup targets, choices/colors, placement, and the exact submitted tooltip payload returned after creation;
- eight Lease sections in the approved order after protected/legacy content;
- all 40 reconciled Lease fields placed in the approved sections;
- Lease Status history tracking enabled, target values/colors present, all legacy values preserved, and the documented capitalization/order/default/required variances;
- no change to Deals Stage, Deals Amount, protected fields, legacy picklist values, CRM records, or `zohocontracts__Contracts`; and
- no Zoho Contracts extension, template, contract request, signature request, or communication action.

## Rollback

Rollback must preserve records and dependency evidence. Do not delete fields or picklist values under this scope.

1. **Created fields:** remove them from active layouts and retire their APIs only after a dependency audit. Do not delete fields or record values.
2. **Section moves:** the sanitized repository evidence does not retain the exact pre-change section/order for the seven reused fields. Do not guess a prior placement or claim an exact layout rollback from this repository. First recover the before-state from Zoho Setup Audit Log, an authorized configuration export, or separately retained session evidence; if no authoritative before-state is available, leave the current placements in place. Keep the eight new sections until a separate approved cleanup verifies they are unused.
3. **Lease Status:** after a workflow/report dependency audit, deactivate only values introduced by this change, including the new `Draft`; restore `Ready For Contract` to `#168AEF` and `Renewal Pending` to `#F5C72F`; restore history tracking to disabled only if audit requirements allow it. Preserve every pre-existing value, including `Draft Lease Data` at `#AF38FA`.
4. **Repository documentation:** revert the focused documentation/catalog commit. A Git revert does not undo live CRM configuration.
5. **Contracts handoff:** no live Contracts setting was changed in this work, so there is no Contracts rollback to perform.

The missing pre-change placement evidence is a rollback limitation, not permission to reconstruct state from the planning catalog. The current verified placements are Lease Identity and Status (`Name`, `Lease_Status`), Relationships (`Tenant`), Lease Dates (`Lease_Start_Date`, `Lease_End_Date`, `Move_In_Date`), and Initial Amounts (`Security_Deposit`).

The sanitized pre-change Lease Status readback is sufficient to identify the value rollback without storing value IDs. Before this change the field was optional, its default was null, history tracking was disabled, and it contained:

| Pre-change value | Pre-change color |
|---|---|
| Draft Lease Data | `#AF38FA` |
| Ready For Contract | `#168AEF` |
| Contract Requested | `#F8E199` |
| Contract Drafting | `#90A9FD` |
| Sent For Signature | `#F5C72F` |
| Signed - Pending Move-In | `#F5C72F` |
| Lease Active | `#67C480` |
| Renewal Pending | `#F5C72F` |
| Notice Given | `#EB4D4D` |
| Ended | `#666666` |
| Cancelled | `#666666` |

Accordingly, the values introduced by this change are `Contract in Progress`, `Signed - Future`, `Active`, `Month-to-Month`, `Non-Renewing`, `Terminated`, `Expired`, `Moved Out`, `Archived`, and `Draft`. Deactivate only those values after the dependency audit; the two retained values whose colors changed are `Ready For Contract` and `Renewal Pending`.

## Remaining deployment gates

1. Reconcile the four blocked financial concepts and approve the Lease Number format.
2. Remediate the normalized/paraphrased tooltips to the supplied exact prose through a supported administrative path and read every tooltip back.
3. Implement and read back complete required/default/readiness rules and Lease Status order through a supported administrative path.
4. Design a durable, idempotent Approved Application to Lease automation; do not substitute one-time record creation.
5. Complete the [manual Zoho Contracts extension handoff](../../src/zoho-contracts/runbooks/crm-leases-extension-manual-deployment.md).
6. Recover and retain authoritative pre-change layout placement evidence before attempting any exact section-move rollback.
7. Keep the Residential Lease Agreement Draft only and unsent until all 29 production gates are closed through their required evidence.
