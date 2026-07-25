# Zoho Contracts Field Registry

> **Status:** Sanitized technical source of truth for field definitions and cross-application mapping. It contains no contract values or tenant records and does not deploy fields to Zoho.

- **Registry:** `GHRE-ZC-FIELDS` v1.3.0
- **As of:** 2026-07-24
- **Inventory:** 46 system fields + 35 custom fields = 81 total

## Operating Rules

- `contract-field-registry.json` is canonical; this Markdown file is generated and checked for drift.
- Built-in system fields are platform-managed and are not forced into the custom-field type menu.
- User-confirmed live labels are label-only evidence and cannot populate a Contracts `apiName`; authenticated metadata is required.
- CRM API names marked `verified_live_mcp` are bounded to the governed 2026-07-24 production metadata readback. Other names remain unverified design targets.
- `Base Rent Amount`, `Total Monthly Rent Amount`, and `Prorated Base Rent Amount` stay unmapped until their CRM semantics are explicitly defined.
- Native Party A fields come from Organization Info and native Party B fields from counterparty/contact configuration; do not create CRM Lease mirrors.
- CRM owns approved pre-authoring party, property, unit, and lease inputs. Zoho Contracts owns lifecycle fields and the resolved agreement snapshot.
- Prefer one-way CRM-to-Contracts authoring. Executed document values are immutable snapshots.
- Never commit live names, addresses, phone numbers, emails, amounts, record IDs, tokens, or merged contracts.

## Label-Only Tenant Evidence

- **Evidence:** `user-confirmed-live-labels-2026-07-24`
- **Type:** `user_confirmed_live_label`
- **Confirmed:** 2026-07-24
- **Scope:** `label_only`
- **Contracts API names:** `unverified`
- **Confirmed labels:** 37

This evidence confirms display labels only. It does not verify Contracts API names, field IDs, data types, template publication, or deployability.

- Base Rent Amount
- Security Deposit Amount
- Total Monthly Pet Rent Amount
- Base Storage Unit Rent Amount
- Total Storage Unit Rent Amount
- Total Monthly Rent Amount
- Next Total Monthly Rent Due Date
- Prorated Rent Start Date
- Prorated Rent End Date
- Prorated Base Rent Amount
- Pet Security Deposit Amount
- Prorated Pet Rent Amount
- Prorated Storage Unit Rent Amount
- Holding Deposit Amount
- Total Due Before Possession
- Agreement Effective Date
- Lease Agreement Effective Date
- Term End Date
- Property Street Line 1
- Property Apartment Number
- Property City
- Property State
- Property Zip Code
- Party C Contact Name
- Party D Contact Name
- Party A
- Party A Name
- Party A Jurisdiction
- Party A Address
- Party A Contact Name
- Party A Contact Phone Number
- Party A Contact Email Address
- Party B
- Party B Name
- Party B Jurisdiction
- Party B Address
- Party B Contact Name

## Zoho Custom Field Types

The tenant UI exposes: `Text`, `Date`, `Number`, `Currency`, `Dropdown`, `Single Checkbox`, `Percent`, `Phone`, `Email`.

None of the current custom fields needs `Single Checkbox` or `Percent`. `Property State` uses `Dropdown`; identifiers and postal codes stay `Text`.

## System Fields

System-field types below are expected native/logical types from Zoho's published semantics. The authenticated `/allfields` metadata response remains controlling for exact tenant `apiName`, `metaType`, `dataType`, and `displayType`.

| Field | Registry ID | Expected Zoho type | Portable / CRM design | Status | Validation / distinction |
|---|---|---|---|---|---|
| Agreement Name | `agreement_name` | String | text / Single Line / `Name` (verified_live_mcp) | active | Required; use a stable human-readable agreement title, not as a cross-system join key. |
| Party A Jurisdiction | `party_a_jurisdiction` | String | text / Pick List / do_not_create | active | Use a controlled legal-jurisdiction code and label; do not treat postal state as jurisdiction automatically. |
| Party A | `party_a` | Index | entity_reference / Lookup / do_not_create | active | Entity/short-name context; keep distinct from Party A Name and never use the display value as a join key. |
| Party A Time Zone Name | `party_a_time_zone_name` | Unknown | time_zone / Pick List / do_not_create | review_required | Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation. |
| Party B Time Zone Name | `party_b_time_zone_name` | Unknown | time_zone / Pick List / do_not_create | review_required | Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation. |
| Party A Time Zone | `party_a_time_zone` | Unknown | unknown / Unresolved / do_not_create | review_required | Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes. |
| Party B Time Zone | `party_b_time_zone` | Unknown | unknown / Unresolved / do_not_create | review_required | Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes. |
| Party B Jurisdiction | `party_b_jurisdiction` | String | text / Pick List / do_not_create | review_required | Leave unresolved until its intended legal meaning is explicitly approved. Do not map Property State, Premises State, or another postal state into this field. |
| Term Period | `term_period` | Term | duration / Composite / design_required | active | Represent as positive integer value plus explicit Months/Years unit; never convert months to 30 days or years to 365 days. |
| Condition / Event / Fulfilment of Order / Completion of Services | `term_end_trigger` | Text | multiline_text / Multi Line / `Term_End_Trigger_Description` (proposed) | active | Required when the contract ends by condition, event, order fulfillment, or service completion instead of a fixed end date. |
| Term End Date | `term_end_date` | Date | date / Date / `Lease_End_Date` (verified_live_mcp) | active | ISO YYYY-MM-DD in integrations; required for a fixed term and must not precede Agreement Date. |
| Party B | `party_b` | Index | entity_reference / Lookup / do_not_create | active | Entity/short-name context; keep distinct from Party B Name and never use the display value as a join key. |
| Non-renewal Notice Period | `nonrenewal_notice_period` | Term | integer / Number / `Nonrenewal_Notice_Days` (proposed) | active | Whole days, minimum zero; calculate deadline dates from the controlling end date. |
| Renewal Notice Days | `renewal_notice_days_tenant` | Number | unknown / Unresolved / tenant_api_required | review_required | Do not sync until apiName proves whether this is the legal renewal notice or the operational expiration-reminder lead. |
| Termination Notice Period | `termination_notice_period` | Term | integer / Number / `Termination_Notice_Days` (proposed) | active | Whole days, minimum zero; calculate the deadline from the controlling termination date. |
| Termination Fee | `termination_fee` | Currency | currency / Currency / `Termination_Fee` (proposed) | active | Nonnegative, two decimals, and paired with the applicable ISO currency code outside a single-currency tenant. |
| Party A Name | `party_a_name` | String | text / Single Line / do_not_create | active | Name snapshot; do not label as legal name unless the source record is verified as the legal name. |
| Party A Address | `party_a_full_address` | Text | multiline_text / Multi Line / do_not_create | active | Derived read-only snapshot, maximum 2000 characters; structured components remain authoritative. |
| Party B Address | `party_b_full_address` | Text | multiline_text / Multi Line / do_not_create | active | Derived read-only snapshot, maximum 2000 characters; structured components remain authoritative. |
| Agreement Date | `agreement_effective_date` | Date | date / Date / `Agreement_Date` (verified_live_mcp) | active | This is the date the contract becomes active; do not treat it as signature date. |
| Renewal Term Period | `renewal_term_period` | Term | duration / Composite / design_required | active | Represent as positive integer value plus explicit Months/Years unit; use calendar-aware date arithmetic. |
| Renewal Notice Period | `renewal_notice_period` | Term | integer / Number / `Renewal_Notice_Days` (proposed) | active | Whole days, minimum zero; keep distinct from any operational reminder lead time. |
| Party B Name | `party_b_name` | String | text / Single Line / do_not_create | active | Name snapshot; do not label as legal name unless the source record is verified as the legal name. |
| Party A Phone Number | `party_a_phone` | Phone | phone / Phone / do_not_create | active | Organization-level phone, distinct from contact phone; normalize to E.164 where possible. |
| Party A Apartment/Suite/Building | `party_a_address_line_2` | String | text / Single Line / do_not_create | active | US-address component; preserve letters and punctuation. |
| Party A Street Address | `party_a_address_line_1` | String | text / Single Line / do_not_create | active | Street-address component; no tenant values belong in repository fixtures. |
| Party A City | `party_a_city` | String | text / Single Line / do_not_create | active | Trim whitespace; preserve official spelling. |
| Party A State | `party_a_state` | String | text / Pick List / do_not_create | active | Prefer a controlled state/province code while preserving the Zoho system value losslessly. |
| Party A Zip Code | `party_a_postal_code` | String | text / Single Line / do_not_create | active | Text, never Number; preserve leading zeros and ZIP+4. |
| Party A Country | `party_a_country` | String | text / Pick List / do_not_create | active | Prefer ISO 3166-1 alpha-2 plus display label. |
| Party A Contact Name | `party_a_primary_contact_name` | String | text / Single Line / do_not_create | active | Individual contact snapshot; pair with a CRM Contact lookup where available. |
| Party A Contact Email Address | `party_a_primary_contact_email` | Email | email / Email / do_not_create | active | Trim and lowercase for comparison; never place real addresses in repository fixtures. |
| Party A Contact Phone Number | `party_a_primary_contact_phone` | Phone | phone / Phone / do_not_create | active | Individual contact phone, distinct from organization phone; normalize to E.164 where possible. |
| Party A Contact Job Title | `party_a_primary_contact_job_title` | String | text / Single Line / do_not_create | active | Optional contact-role snapshot; do not use as authorization proof. |
| Party B Phone Number | `party_b_phone` | Phone | phone / Phone / do_not_create | active | Organization-level phone, distinct from contact phone; normalize to E.164 where possible. |
| Party B Apartment/Suite/Building | `party_b_address_line_2` | String | text / Single Line / do_not_create | active | US-address component; preserve letters and punctuation. |
| Party B Street Address | `party_b_address_line_1` | String | text / Single Line / do_not_create | active | Street-address component; no tenant values belong in repository fixtures. |
| Party B City | `party_b_city` | String | text / Single Line / do_not_create | active | Trim whitespace; preserve official spelling. |
| Party B State | `party_b_state` | String | text / Pick List / do_not_create | active | Prefer a controlled state/province code while preserving the Zoho system value losslessly. |
| Party B Zip Code | `party_b_postal_code` | String | text / Single Line / do_not_create | active | Text, never Number; preserve leading zeros and ZIP+4. |
| Party B Country | `party_b_country` | String | text / Pick List / do_not_create | active | Prefer ISO 3166-1 alpha-2 plus display label. |
| Party B Contact Name | `party_b_primary_contact_name` | String | text / Single Line / do_not_create | active | Individual contact snapshot; pair with a CRM Contact lookup where available. |
| Party B Contact Email Address | `party_b_primary_contact_email` | Email | email / Email / do_not_create | active | Trim and lowercase for comparison; never place real addresses in repository fixtures. |
| Party B Contact Phone Number | `party_b_primary_contact_phone` | Phone | phone / Phone / do_not_create | active | Individual contact phone, distinct from organization phone; normalize to E.164 where possible. |
| Party B Contact Job Title | `party_b_primary_contact_job_title` | String | text / Single Line / do_not_create | active | Optional contact-role snapshot; do not use as authorization proof. |
| Contract Amount | `contract_amount` | Currency | currency / Currency / `Contract_Amount` (proposed) | active | Nonnegative, two decimals, and paired with the applicable ISO currency code outside a single-currency tenant. |

## Custom Fields

These are the approved design types to use when configuring the custom fields. Existing tenant fields must still be reconciled through metadata before automation uses them.

| Field | Registry ID | Zoho Contracts type | CRM design | Status | Validation / alias rule |
|---|---|---|---|---|---|
| Lease Number | `lease_number` | Text | Single Line / do_not_create_until_defined | active | Do not create until an approved auto-number prefix and format are defined. Once approved, generate centrally, enforce case-insensitive uniqueness, and preserve letters, hyphens, and leading zeros. |
| Property Street Line 1 | `property_address_line_1_snapshot` | Text | Single Line / `Premises_Street_Line_1` (verified_live_mcp) | active | Required for property-specific agreements; freeze as an execution snapshot. |
| Property City | `property_city_snapshot` | Text | Single Line / `Premises_City` (verified_live_mcp) | active | Required with a property address; freeze as an execution snapshot. |
| Property State | `property_state_code_snapshot` | Dropdown | Pick List / `Premises_State` (verified_live_mcp) | active | Required two-letter USPS state code; do not accept free-text variants. |
| Property Zip Code | `property_postal_code_snapshot` | Text | Single Line / `Premises_ZIP_Code` (verified_live_mcp) | active | Text, never Number; match five-digit ZIP or ZIP+4 and preserve leading zeros. |
| Storage Unit Number | `storage_unit_number` | Text | Single Line / `Storage_Unit_Number` (proposed) | active | Required for a storage agreement; preserve letters, separators, and leading zeros. |
| Number of Storage Unit Keys Provided | `storage_keys_provided_count` | Number | Number / `Storage_Keys_Provided_Count` (proposed) | active | Whole number, minimum zero; do not infer possession solely from this count. |
| Storage Term Begins | `storage_term_start_date` | Date | Date / `Storage_Term_Start_Date` (proposed) | active | ISO YYYY-MM-DD; canonical storage start date and must not follow Storage Term Ends. |
| Storage Unit Rent | `storage_unit_rent_amount` | Currency | Currency / `Storage_Unit_Rent` (proposed) | active | Nonnegative, two decimals, organization currency; this field must not directly create an invoice. |
| Storage Term Ends | `storage_term_end_date` | Date | Date / `Storage_Term_End_Date` (proposed) | active | ISO YYYY-MM-DD; when present, must not precede the canonical storage start date. |
| Storage Term Starts | `storage_term_starts_legacy` | Date | Date / do_not_create | deprecated_alias | Do not create or independently populate. Migrate templates to Storage Term Begins unless a reviewed definition distinguishes access start from billing start. |
| Party C Contact Name | `party_c_primary_contact_name` | Text | Single Line / `Tenant_2_Legal_Name_Snapshot` (verified_live_mcp) | active | Party C is the approved Tenant 2 legal-name snapshot for this lease workflow; do not substitute a mutable contact display name. |
| Party D Contact Name | `party_d_primary_contact_name` | Text | Single Line / `Tenant_3_Legal_Name_Snapshot` (verified_live_mcp) | active | Party D is the approved Tenant 3 legal-name snapshot for this lease workflow; do not substitute a mutable contact display name. |
| Party C Contact Phone Number | `party_c_primary_contact_phone` | Phone | Phone / `Party_C_Contact_Phone` (proposed) | active | Normalize to E.164 where possible; never include real values in repository fixtures. |
| Party D Contact Phone Number | `party_d_primary_contact_phone` | Phone | Phone / `Party_D_Contact_Phone` (proposed) | active | Normalize to E.164 where possible; never include real values in repository fixtures. |
| Party C Contact Email Address | `party_c_primary_contact_email` | Email | Email / `Party_C_Contact_Email` (proposed) | active | Trim and lowercase for comparison; never include real values in repository fixtures. |
| Party D Contact Email Address | `party_d_primary_contact_email` | Email | Email / `Party_D_Contact_Email` (proposed) | active | Trim and lowercase for comparison; never include real values in repository fixtures. |
| Lease Agreement Effective Date | `lease_agreement_effective_date_custom` | Date | Date / `Lease_Start_Date` (verified_live_mcp) | review_required | Map only from the verified CRM Lease_Start_Date field; retain review-required status until counsel or approved business rules define its relationship to system Agreement Date. |
| Property Apartment Number | `property_unit_number_snapshot` | Text | Single Line / `Premises_Apartment_Number` (verified_live_mcp) | active | Text, not Number; preserve letters, separators, and leading zeros. Prefer the display label Property Unit Number. |
| Base Rent Amount | `base_rent_amount` | Currency | Currency / do_not_create_until_defined | active | Nonnegative, two decimals, and frozen before contract request. This field must not directly create an invoice or establish a paid balance. |
| Security Deposit Amount | `security_deposit_amount` | Currency | Currency / `Security_Deposit` (verified_live_mcp) | active | Refundable general security-deposit amount; nonnegative and two decimals. Do not treat this contract value as proof of receipt or deposit liability. |
| Total Monthly Pet Rent Amount | `total_monthly_pet_rent_amount` | Currency | Currency / `Total_Monthly_Pet_Rent_Amount` (verified_live_mcp) | active | Aggregate ordinary-pet monthly rent only; nonnegative and two decimals. Keep distinct from pet deposits, nonrefundable fees, and assistance animals. |
| Base Storage Unit Rent Amount | `base_storage_unit_rent_amount` | Currency | Currency / `Base_Storage_Unit_Rent_Amount` (verified_live_mcp) | active | Per-unit monthly storage rate; nonnegative and two decimals. Keep distinct from the aggregate storage amount. |
| Total Storage Unit Rent Amount | `total_storage_unit_rent_amount` | Currency | Currency / `Total_Monthly_Storage_Rent_Amount` (verified_live_mcp) | active | Aggregate monthly storage rent; nonnegative and two decimals. Reconcile assigned units and rates before contract request. |
| Total Monthly Rent Amount | `total_monthly_rent_amount` | Currency | Currency / do_not_create_until_defined | active | Total approved recurring monthly rent; nonnegative and two decimals. Reconcile the component equation before automation uses this value. |
| Next Total Monthly Rent Due Date | `next_total_monthly_rent_due_date` | Date | Date / `Next_Total_Monthly_Rent_Due_Date` (verified_live_mcp) | active | ISO YYYY-MM-DD; the first regular monthly-rent due date after the initial amounts. Do not treat it as proof that an invoice exists. |
| Prorated Rent Start Date | `prorated_rent_start_date` | Date | Date / `Prorated_Rent_Start_Date` (verified_live_mcp) | active | ISO YYYY-MM-DD; first date covered by prorated rent. When present, it must not follow Prorated Rent End Date. |
| Prorated Rent End Date | `prorated_rent_end_date` | Date | Date / `Prorated_Rent_End_Date` (verified_live_mcp) | active | ISO YYYY-MM-DD; last date covered by prorated rent. When present, it must not precede Prorated Rent Start Date. |
| Prorated Base Rent Amount | `prorated_base_rent_amount` | Currency | Currency / do_not_create_until_defined | active | Base rent for the approved prorated period; nonnegative and two decimals. Use only the governed proration and rounding rule. |
| Pet Security Deposit Amount | `pet_security_deposit_amount` | Currency | Currency / `Pet_Security_Deposit_Amount` (verified_live_mcp) | active | Refundable ordinary-pet security deposit, not a nonrefundable pet fee; nonnegative and two decimals. |
| Prorated Pet Rent Amount | `prorated_pet_rent_amount` | Currency | Currency / `Prorated_Pet_Rent_Amount` (verified_live_mcp) | active | Ordinary-pet rent for the approved prorated period; nonnegative and two decimals. Keep separate from deposits and fees. |
| Prorated Storage Unit Rent Amount | `prorated_storage_unit_rent_amount` | Currency | Currency / `Prorated_Storage_Unit_Rent_Amount` (verified_live_mcp) | active | Storage rent for the approved prorated period; nonnegative and two decimals. Reconcile assigned units and the governed proration rule. |
| Holding Deposit Amount | `holding_deposit_amount` | Currency | Currency / `Holding_Deposit_Credit_Applied` (verified_live_mcp) | active | Holding-deposit credit applied to initial amounts; nonnegative and two decimals. This snapshot is not proof of payment. |
| First Full Month Base Rent Amount | `first_full_month_base_rent_amount` | Currency | Currency / `First_Full_Month_Base_Rent_Amount` (verified_live_mcp) | review_required | First full month of Base Rent due before possession; nonnegative and two decimals. Do not map or automate until the complete initial-amount equation, Books reconciliation, readiness gate, and controlled Contracts canary pass. |
| Total Due Before Possession | `total_due_before_possession` | Currency | Currency / `Total_Due_Before_Possession` (verified_live_mcp) | review_required | Do not automate until the full equation, first-full-month amount, fee treatment, holding-deposit credit, proration rounding, and pet or storage charges are reconciled. |

## Required Reconciliation Before Live Mapping

- **Party A Time Zone Name:** Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation.
- **Party B Time Zone Name:** Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation.
- **Party A Time Zone:** Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes.
- **Party B Time Zone:** Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes.
- **Party B Jurisdiction:** Leave unresolved until its intended legal meaning is explicitly approved. Do not map Property State, Premises State, or another postal state into this field.
- **Renewal Notice Days:** Do not sync until apiName proves whether this is the legal renewal notice or the operational expiration-reminder lead.
- **Lease Agreement Effective Date:** Map only from the verified CRM Lease_Start_Date field; retain review-required status until counsel or approved business rules define its relationship to system Agreement Date.
- **First Full Month Base Rent Amount:** First full month of Base Rent due before possession; nonnegative and two decimals. Do not map or automate until the complete initial-amount equation, Books reconciliation, readiness gate, and controlled Contracts canary pass.
- **Total Due Before Possession:** Do not automate until the full equation, first-full-month amount, fee treatment, holding-deposit credit, proration rounding, and pet or storage charges are reconciled.
- **Storage Term Starts:** deprecated alias of `storage_term_start_date`; do not create or independently populate it.
- **Party C/D:** this workflow maps them only to the verified Tenant 2 and Tenant 3 legal-name snapshots; do not reuse the labels for arbitrary party roles.

## Tenant Metadata Verification

1. Call `GET /api/v1/admin/contracttypes/{contract-type-api-name}/allfields` with `contracts.meta.READ`.
2. Match by returned stable `apiName`, not display text.
3. Record `metaType` (`1` system, `3` custom), `dataType`, and `displayType`.
4. Query CRM fields with `GET /crm/v8/settings/fields?module=...`; confirm every `verified_live_mcp` crosswalk name still exists in the exact module/layout before deployment.
5. Run the registry validator and sanitized merge tests before activating any sync.

Zoho Contracts `dataType` codes: `1` Boolean, `2` Number, `3` String, `4` Date, `5` Index, `6` Text, `7` Currency, `8` Term, `9` Percent, `10` Phone, `11` Email.

## Official References

- [zoho-system-fields](https://help.zoho.com/portal/en/kb/contracts/admin-guide/clause-library/articles/adding-and-managing-clauses)
- [zoho-metadata-api](https://www.zoho.com/contracts/api/contract-type/get-contract-type-template-all-fields.html)
- [zoho-contract-create-api](https://www.zoho.com/contracts/api/contract/create-contract.html)
- [zoho-template-mapping](https://help.zoho.com/portal/en/kb/contracts/admin-guide/contract-types/creation-and-management/articles/managing-contract-types)
- [zoho-crm-field-metadata](https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html)
- [zoho-crm-custom-fields](https://www.zoho.com/crm/developer/docs/api/v8/create-custom-field.html)

## Validation

```powershell
python src/zoho-contracts/scripts/validate_contract_field_registry.py
python -m unittest discover -s src/zoho-contracts/tests -p 'test_*.py' -v
```

Merging this registry does not create, rename, or update any live Zoho field.
