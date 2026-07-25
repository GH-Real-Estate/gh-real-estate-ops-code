# CRM Leases to Zoho Contracts Manual Deployment

**Applies to:** GH Real Estate production

**CRM source module:** Leases -- custom module -- verified API `Leases`

**Contract type:** Residential Lease Agreement

**Status:** Manual and not yet performed

**Last official-source review:** July 24, 2026

## Safety gate

This runbook covers work that the approved CRM connectors cannot perform. Completing this document in GitHub does not change Zoho Contracts.

Every target action and field mapping in this runbook is classified `manual_contracts_mapping` until it is performed and read back through the authorized live administrative surface.

Do not begin unless the operator has separately confirmed:

- the live organization is GH Real Estate production;
- the Residential Lease Agreement remains Draft only, unpublished, execution-blocked, and attorney-review-required;
- all 29 production gates remain open unless separately closed with governed evidence;
- no real contract request or signature request will be sent during this configuration pass; and
- before-state screenshots or an equivalent sanitized configuration record are available for rollback.

Stop on any mismatched organization, ambiguous field, missing counterparty type, unverified button token, or request to publish/send.

## Official operating boundary

Zoho's current instructions require a custom CRM module to be enabled in the Contracts extension and to have both a Request Contract button and a Zoho Contracts related-list widget. The extension separately configures counterparties, Contact-field mappings, and module-wise template-field mappings.

Use these current official references:

- [Setting Up Zoho Contracts Extension in Zoho CRM](https://help.zoho.com/portal/en/kb/contracts/admin-guide/integrations/zoho-crm/articles/setting-up-zoho-contracts-extension-in-zoho-crm)
- [Initiating Contract Requests from Zoho CRM](https://help.zoho.com/portal/en/kb/contracts/user-guide/integrations/zoho-crm/articles/initiating-contract-requests-from-zoho-crm)
- [Managing Contracts in Zoho CRM](https://help.zoho.com/portal/en/kb/contracts/user-guide/integrations/zoho-crm/articles/managing-contracts-in-zoho-crm)
- [Managing Contract Types](https://help.zoho.com/portal/en/kb/contracts/admin-guide/contract-types/creation-and-management/articles/managing-contract-types)

The official custom-button example uses a different module. Do not replace its module or record tokens by inference. The exact Leases-specific URL and record-name variable must come from the current Zoho extension UI, current official Leases-specific instruction, or Zoho Support.

## Before-state capture

Record screenshots or a sanitized checklist of:

1. Connected Contracts organization.
2. Enabled CRM modules and allowed contract types.
3. Existing Leases counterparty settings, if any.
4. Counterparty Contact field mappings.
5. Existing module-wise Leases mappings.
6. Leases buttons, profiles, page location, and target.
7. Leases detail-view related lists/widgets.
8. Residential Lease Agreement status and Party A Organization Info.

Do not capture organization IDs, record IDs, user emails, tenant values, OAuth material, or request URLs containing identifiers.

## 1. Enable the Leases custom module

1. In Zoho CRM, open **Setup > Marketplace > Zoho > Zoho Contracts > Settings**.
2. Confirm the connected organization is GH Real Estate production.
3. Open **Modules**, choose **Add Custom Module**, and select the live **Leases** module.
4. Enable only **Residential Lease Agreement** for this module.
5. If the Draft/unpublished Residential Lease Agreement is not offered by the selector, stop. Do not publish or republish it merely to expose it to the extension.
6. Save, navigate away, return to Modules, and verify:
   - Leases remains enabled;
   - no unrelated module was enabled; and
   - Residential Lease Agreement is the only allowed contract type.

Do not publish or republish the contract type.

## 2. Configure the counterparty

1. Open the extension **Counterparty** settings for Leases.
2. Choose the **Always** counterparty rule.
3. Use the live Lease lookup **Tenant** (API `Tenant`) as the primary-tenant counterparty source.
4. The requirement calls this role **Primary Tenant**, but the verified live field label is **Tenant**. Do not create or guess a second lookup merely to match the role label.
5. Select the existing **Tenant** counterparty type only if that exact type is visible and its intended use is verified.
6. If the Tenant counterparty type is absent or ambiguous, stop. Do not create or substitute a type under this runbook.
7. Save and read the Always rule and both selections back.

Party B is the primary tenant counterparty. Party B Address is the counterparty's address, not the rental premises. Leave Party B Jurisdiction unresolved; never map `Premises_State` or Property State to it.

## 3. Map Contact identity fields

In **Field Mapping > Counterparty Contact Fields**, configure:

| Contracts field | CRM Contacts field | Verified CRM API |
|---|---|---|
| Contact Name | Full Name | `Full_Name` |
| Contact Email Address | Email | `Email` |

Save, return to the page, and verify both mappings. Do not use a tenant snapshot or concatenate names when the verified standard Contact fields are available.

## 4. Add the Request Contract button without guessing tokens

1. Go to **Setup > Customization > Modules and Fields > Leases > Buttons**.
2. Create or reuse a button named **Request Contract** only after checking for a duplicate.
3. Use the official placement:
   - page: **In Record**;
   - position: **Details**;
   - action: **Invoke a URL**;
   - target: **New Window**; and
   - profiles: only the approved lease/contract operators.
4. Obtain the exact current Leases-specific URL from Zoho's live extension instruction or Zoho Support.
5. Verify that its module token is for the live `Leases` API and that its record token is the exact Zoho-provided Lease variable.
6. Do not adapt the official Purchases example, guess `${Leases...}`, or insert an organization/record ID.
7. If the exact URL or token cannot be verified, stop and leave the button uncreated.
8. Save and reopen the button to read back its placement, action, target, and profiles. Do not click it while the implementation is blocked.

## 5. Add the Zoho Contracts related list

1. Go to **Setup > Customization > Modules and Fields > Leases** and open the production Lease layout.
2. In **Detail View**, choose **Add Related List > Widgets > Create New Widget**.
3. Configure:
   - name: **Zoho Contracts**;
   - hosting: **External**; and
   - Base URL: `https://extensions.zoho.com/jsp/zcrmcontracts/details.jsp`
4. Save, install the widget, and name the custom related list **Zoho Contracts**.
5. Return to a sanitized/non-record layout preview or configuration view and verify the related list is installed. Do not open tenant records for this handoff.

The static Base URL above is the value in Zoho's official custom-module setup article as reviewed on July 24, 2026.

## 6. Configure module-wise document-field mappings

Open **Field Mapping > Module-wise Fields Mapping > Leases > Residential Lease Agreement**. Use only verified CRM APIs and visible Contracts destination labels. Contracts API names remain unverified until the contract type `/allfields` metadata is reconciled.

### Mappings eligible for manual configuration

| CRM Lease source | Verified CRM API | Intended Contracts destination label | Manual control |
|---|---|---|---|
| Lease Name | `Name` | Agreement Name, if the visible field has that meaning | Confirm the destination label and preview behavior. |
| Agreement Date | `Agreement_Date` | Agreement Effective Date | Exact label-only evidence uses `Agreement Effective Date`; keep it distinct from lease commencement and stop if the live UI differs. |
| Lease Start Date | `Lease_Start_Date` | Lease Agreement Effective Date | Confirm this is the approved lease-commencement destination. |
| Lease End Date | `Lease_End_Date` | Term End Date | Required for a fixed term. |
| Premises Street Line 1 | `Premises_Street_Line_1` | Property Street Line 1 | Premises snapshot, not Party B address. |
| Premises Apartment Number | `Premises_Apartment_Number` | Property Apartment Number | Text snapshot. |
| Premises City | `Premises_City` | Property City | Premises snapshot. |
| Premises State | `Premises_State` | Property State | Never Party B Jurisdiction. |
| Premises ZIP Code | `Premises_ZIP_Code` | Property Zip Code | Preserve as text. |
| Security Deposit | `Security_Deposit` | Security Deposit Amount | Snapshot only; Books remains accounting truth. |
| Total Monthly Pet Rent Amount | `Total_Monthly_Pet_Rent_Amount` | Total Monthly Pet Rent Amount | Use only when approved pet terms exist. |
| Base Storage Unit Rent Amount | `Base_Storage_Unit_Rent_Amount` | Base Storage Unit Rent Amount | Use only when approved storage terms exist. |
| Total Monthly Storage Rent Amount | `Total_Monthly_Storage_Rent_Amount` | Total Storage Unit Rent Amount | Confirm destination label in the live contract type. |
| Next Total Monthly Rent Due Date | `Next_Total_Monthly_Rent_Due_Date` | Next Total Monthly Rent Due Date | Confirm the initial-amount equation first. |
| Prorated Rent Start Date | `Prorated_Rent_Start_Date` | Prorated Rent Start Date | Use only when prorating. |
| Prorated Rent End Date | `Prorated_Rent_End_Date` | Prorated Rent End Date | Use only when prorating. |
| Pet Security Deposit Amount | `Pet_Security_Deposit_Amount` | Pet Security Deposit Amount | Refundable deposit, not a fee. |
| Prorated Pet Rent Amount | `Prorated_Pet_Rent_Amount` | Prorated Pet Rent Amount | Confirm proration rule and rounding. |
| Prorated Storage Unit Rent Amount | `Prorated_Storage_Unit_Rent_Amount` | Prorated Storage Unit Rent Amount | Confirm storage applicability and proration. |
| Holding Deposit Credit Applied | `Holding_Deposit_Credit_Applied` | Holding Deposit Amount | Confirm credit semantics and Books evidence. |
| Total Due Before Possession | `Total_Due_Before_Possession` | Total Due Before Possession | Do not map/use until the complete equation is approved. |
| Tenant 2 Legal Name Snapshot | `Tenant_2_Legal_Name_Snapshot` | Party C Contact Name | Document field only; does not create a signer. |
| Tenant 3 Legal Name Snapshot | `Tenant_3_Legal_Name_Snapshot` | Party D Contact Name | Document field only; does not create a signer. |

Save only mappings whose visible live destination label and meaning match. Reopen the settings and read each mapping back.

### Do not map yet

- Lease Number: no approved CRM auto-number field exists.
- Base Rent Amount or Total Monthly Rent Amount: existing CRM `Monthly_Rent` semantics are ambiguous.
- Prorated Base Rent Amount: existing CRM `Prorated_Rent` semantics are ambiguous.
- First Full Month Base Rent Amount: the CRM field and reconciled equation are missing.
- Party B Jurisdiction: legal meaning remains unresolved.
- Tenant 2/3 email snapshots: signer-routing inputs, not document fields unless a later approved design says otherwise.
- `Addenda_Required`, `Nonstandard_Terms`, `Nonstandard_Terms_Notes`, or `Attorney_Review_Required`: workflow controls, not automatic legal-text merge values.

An empty mapped CRM source produces an empty value in the generated contract according to Zoho's current initiation guidance. Therefore, a saved mapping is not evidence that the Lease record is contract-ready.

## 7. Verify Party A Organization Info

In Zoho Contracts, verify that Party A Organization Info resolves to **GH Real Estate, LLC** and that the approved organization address/contact fields are current.

Do not copy Party A system fields into CRM. Stop if the legal entity, address, authorized representative, or signer authority is ambiguous.

## 8. Configure signer routing separately

Document fields do not create Zoho Sign recipients. GH uses these fixed process-role labels:

- R1 = Primary Tenant
- R2 = Tenant 2, when present
- R3 = Tenant 3, when present
- R4 = GH Real Estate landlord representative and final signer

R1-R4 are GH process labels, not documented Zoho recipient tokens or permanent numeric slots. Configure Zoho's actual signing order contiguously for the people present:

| Variant | Actual Zoho signing order |
|---|---|
| One tenant | R1 Primary Tenant = order 1; R4 GH landlord = order 2 and last |
| Two tenants | R1 Primary Tenant = order 1; R2 Tenant 2 = order 2; R4 GH landlord = order 3 and last |
| Three tenants | R1 Primary Tenant = order 1; R2 Tenant 2 = order 2; R3 Tenant 3 = order 3; R4 GH landlord = order 4 and last |

- Only the counterparty primary contact can be the default counterparty-representative signer at contract-type level.
- The landlord may be the default organization representative, but must remain last.
- Tenant 2 and Tenant 3 must be added manually at the contract's **Add Signers** step when later authorized; do not represent them as conditional contract-type defaults.
- Do not open Add Signers or send an envelope during this blocked configuration pass.
- Actual Zoho signing orders must be contiguous, with no placeholder recipient and no gap.
- Tenant 2 and Tenant 3 emails come from `Tenant_2_Email_Snapshot` and `Tenant_3_Email_Snapshot` only after the snapshots are verified.
- Party C Contact Name and Party D Contact Name are document fields only. They do not create R2/R3 recipients.
- Do not route a guarantor through the Residential Lease signer manifest unless a separately governed guaranty workflow is approved.

## 9. Readback without requesting a contract

After saving, verify configuration only:

1. Leases is enabled for Residential Lease Agreement and no unrelated contract type.
2. Counterparty source is live Lease field **Tenant** and counterparty type is the verified existing **Tenant** type.
3. Contact Name maps to `Full_Name`; Contact Email Address maps to `Email`.
4. The Request Contract button has the verified Leases-specific URL/tokens, approved profiles, Details placement, and New Window target.
5. The Zoho Contracts related list/widget is installed on the Lease detail view.
6. Every saved module-wise mapping points to the intended CRM API and visible Contracts destination label.
7. Party A is GH Real Estate, LLC.
8. Party B Jurisdiction remains unmapped.
9. Fixed GH process-role labels are preserved, actual Zoho signing orders are contiguous, only the primary tenant is the default counterparty representative, optional tenants are reserved for later manual Add Signers, and GH signs last.
10. Residential Lease Agreement remains Draft only/unpublished and no contract or signature request was sent.

Do not use **Request Contract** as a smoke test while any production gate remains open.

## Rollback

If this manual configuration is later applied and must be reversed:

1. Disable Leases in the Contracts extension or remove Residential Lease Agreement from its allowed types.
2. Disable/remove only the Request Contract button and related-list widget created by this change after confirming no other workflow depends on them.
3. Restore prior counterparty, Contact-field, and module-wise mappings from the captured before-state.
4. Preserve existing contracts, CRM records, attachments, and audit history. Do not delete them.
5. Do not disconnect the entire Contracts organization unless a separately approved incident response requires that broader action.
6. Reopen every affected settings page and verify the prior state.

No Contracts configuration was changed when this runbook was authored, so no live rollback is currently required.
