# Zoho Contracts Field Registry

> **Status:** Sanitized technical source of truth for field definitions and cross-application mapping. It contains no contract values or tenant records and does not deploy fields to Zoho.

**Registry:** `GHRE-ZC-FIELDS` v1.0.0  
**As of:** 2026-07-15  
**Inventory:** 46 system fields + 19 custom fields = 65 total

## Operating Rules

- `contract-field-registry.json` is canonical; this Markdown file is generated and checked for drift.
- Built-in system fields are platform-managed and are not forced into the custom-field type menu.
- A proposed CRM API name is a design target only. Fetch the actual Contracts `apiName` and CRM API name from authenticated metadata before integration.
- CRM owns approved pre-authoring party, property, unit, and lease inputs. Zoho Contracts owns lifecycle fields and the resolved agreement snapshot.
- Prefer one-way CRM-to-Contracts authoring. Executed document values are immutable snapshots.
- Never commit live names, addresses, phone numbers, emails, amounts, record IDs, tokens, or merged contracts.

## Zoho Custom Field Types

The tenant UI exposes: `Text`, `Date`, `Number`, `Currency`, `Dropdown`, `Single Checkbox`, `Percent`, `Phone`, `Email`.

None of the current custom fields needs `Single Checkbox` or `Percent`. `Property State` uses `Dropdown`; identifiers and postal codes stay `Text`.

## System Fields

System-field types below are expected native/logical types from Zoho's published semantics. The authenticated `/allfields` metadata response remains controlling for exact tenant `apiName`, `metaType`, `dataType`, and `displayType`.

| Field | Registry ID | Expected Zoho type | Portable / CRM design | Status | Validation / distinction |
|---|---|---|---|---|---|
| Agreement Name | `agreement_name` | String | text / Single Line / `Agreement_Name` (proposed) | active | Required; use a stable human-readable agreement title, not as a cross-system join key. |
| Party A Jurisdiction | `party_a_jurisdiction` | String | text / Pick List / `Party_A_Jurisdiction` (proposed) | active | Use a controlled legal-jurisdiction code and label; do not treat postal state as jurisdiction automatically. |
| Party A | `party_a` | Index | entity_reference / Lookup / `Party_A_Account` (proposed) | active | Entity/short-name context; keep distinct from Party A Name and never use the display value as a join key. |
| Party A Time Zone Name | `party_a_time_zone_name` | Unknown | time_zone / Pick List / `Party_A_Time_Zone_Name` (proposed) | review_required | Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation. |
| Party B Time Zone Name | `party_b_time_zone_name` | Unknown | time_zone / Pick List / `Party_B_Time_Zone_Name` (proposed) | review_required | Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation. |
| Party A Time Zone | `party_a_time_zone` | Unknown | unknown / Unresolved / tenant_api_required | review_required | Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes. |
| Party B Time Zone | `party_b_time_zone` | Unknown | unknown / Unresolved / tenant_api_required | review_required | Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes. |
| Party B Jurisdiction | `party_b_jurisdiction` | String | text / Pick List / `Party_B_Jurisdiction` (proposed) | active | Use a controlled legal-jurisdiction code and label; do not treat postal state as jurisdiction automatically. |
| Term Period | `term_period` | Term | duration / Composite / design_required | active | Represent as positive integer value plus explicit Months/Years unit; never convert months to 30 days or years to 365 days. |
| Condition / Event / Fulfilment of Order / Completion of Services | `term_end_trigger` | Text | multiline_text / Multi Line / `Term_End_Trigger_Description` (proposed) | active | Required when the contract ends by condition, event, order fulfillment, or service completion instead of a fixed end date. |
| Term End Date | `term_end_date` | Date | date / Date / `Term_End_Date` (proposed) | active | ISO YYYY-MM-DD in integrations; required for a fixed term and must not precede Agreement Date. |
| Party B | `party_b` | Index | entity_reference / Lookup / `Party_B_Account` (proposed) | active | Entity/short-name context; keep distinct from Party B Name and never use the display value as a join key. |
| Non-renewal Notice Period | `nonrenewal_notice_period` | Term | integer / Number / `Nonrenewal_Notice_Days` (proposed) | active | Whole days, minimum zero; calculate deadline dates from the controlling end date. |
| Renewal Notice Days | `renewal_notice_days_tenant` | Number | unknown / Unresolved / tenant_api_required | review_required | Do not sync until apiName proves whether this is the legal renewal notice or the operational expiration-reminder lead. |
| Termination Notice Period | `termination_notice_period` | Term | integer / Number / `Termination_Notice_Days` (proposed) | active | Whole days, minimum zero; calculate the deadline from the controlling termination date. |
| Termination Fee | `termination_fee` | Currency | currency / Currency / `Termination_Fee` (proposed) | active | Nonnegative, two decimals, and paired with the applicable ISO currency code outside a single-currency tenant. |
| Party A Name | `party_a_name` | String | text / Single Line / `Party_A_Name_Snapshot` (proposed) | active | Name snapshot; do not label as legal name unless the source record is verified as the legal name. |
| Party A Address | `party_a_full_address` | Text | multiline_text / Multi Line / `Party_A_Full_Address_Snapshot` (proposed) | active | Derived read-only snapshot, maximum 2000 characters; structured components remain authoritative. |
| Party B Address | `party_b_full_address` | Text | multiline_text / Multi Line / `Party_B_Full_Address_Snapshot` (proposed) | active | Derived read-only snapshot, maximum 2000 characters; structured components remain authoritative. |
| Agreement Date | `agreement_effective_date` | Date | date / Date / `Agreement_Effective_Date` (proposed) | active | This is the date the contract becomes active; do not treat it as signature date. |
| Renewal Term Period | `renewal_term_period` | Term | duration / Composite / design_required | active | Represent as positive integer value plus explicit Months/Years unit; use calendar-aware date arithmetic. |
| Renewal Notice Period | `renewal_notice_period` | Term | integer / Number / `Renewal_Notice_Days` (proposed) | active | Whole days, minimum zero; keep distinct from any operational reminder lead time. |
| Party B Name | `party_b_name` | String | text / Single Line / `Party_B_Name_Snapshot` (proposed) | active | Name snapshot; do not label as legal name unless the source record is verified as the legal name. |
| Party A Phone Number | `party_a_phone` | Phone | phone / Phone / `Party_A_Phone` (proposed) | active | Organization-level phone, distinct from contact phone; normalize to E.164 where possible. |
| Party A Apartment/Suite/Building | `party_a_address_line_2` | String | text / Single Line / `Party_A_Address_Line_2` (proposed) | active | US-address component; preserve letters and punctuation. |
| Party A Street Address | `party_a_address_line_1` | String | text / Single Line / `Party_A_Address_Line_1` (proposed) | active | Street-address component; no tenant values belong in repository fixtures. |
| Party A City | `party_a_city` | String | text / Single Line / `Party_A_City` (proposed) | active | Trim whitespace; preserve official spelling. |
| Party A State | `party_a_state` | String | text / Pick List / `Party_A_State` (proposed) | active | Prefer a controlled state/province code while preserving the Zoho system value losslessly. |
| Party A Zip Code | `party_a_postal_code` | String | text / Single Line / `Party_A_Postal_Code` (proposed) | active | Text, never Number; preserve leading zeros and ZIP+4. |
| Party A Country | `party_a_country` | String | text / Pick List / `Party_A_Country` (proposed) | active | Prefer ISO 3166-1 alpha-2 plus display label. |
| Party A Contact Name | `party_a_primary_contact_name` | String | text / Single Line / `Party_A_Primary_Contact_Name` (proposed) | active | Individual contact snapshot; pair with a CRM Contact lookup where available. |
| Party A Contact Email Address | `party_a_primary_contact_email` | Email | email / Email / `Party_A_Primary_Contact_Email` (proposed) | active | Trim and lowercase for comparison; never place real addresses in repository fixtures. |
| Party A Contact Phone Number | `party_a_primary_contact_phone` | Phone | phone / Phone / `Party_A_Primary_Contact_Phone` (proposed) | active | Individual contact phone, distinct from organization phone; normalize to E.164 where possible. |
| Party A Contact Job Title | `party_a_primary_contact_job_title` | String | text / Single Line / `Party_A_Primary_Contact_Job_Title` (proposed) | active | Optional contact-role snapshot; do not use as authorization proof. |
| Party B Phone Number | `party_b_phone` | Phone | phone / Phone / `Party_B_Phone` (proposed) | active | Organization-level phone, distinct from contact phone; normalize to E.164 where possible. |
| Party B Apartment/Suite/Building | `party_b_address_line_2` | String | text / Single Line / `Party_B_Address_Line_2` (proposed) | active | US-address component; preserve letters and punctuation. |
| Party B Street Address | `party_b_address_line_1` | String | text / Single Line / `Party_B_Address_Line_1` (proposed) | active | Street-address component; no tenant values belong in repository fixtures. |
| Party B City | `party_b_city` | String | text / Single Line / `Party_B_City` (proposed) | active | Trim whitespace; preserve official spelling. |
| Party B State | `party_b_state` | String | text / Pick List / `Party_B_State` (proposed) | active | Prefer a controlled state/province code while preserving the Zoho system value losslessly. |
| Party B Zip Code | `party_b_postal_code` | String | text / Single Line / `Party_B_Postal_Code` (proposed) | active | Text, never Number; preserve leading zeros and ZIP+4. |
| Party B Country | `party_b_country` | String | text / Pick List / `Party_B_Country` (proposed) | active | Prefer ISO 3166-1 alpha-2 plus display label. |
| Party B Contact Name | `party_b_primary_contact_name` | String | text / Single Line / `Party_B_Primary_Contact_Name` (proposed) | active | Individual contact snapshot; pair with a CRM Contact lookup where available. |
| Party B Contact Email Address | `party_b_primary_contact_email` | Email | email / Email / `Party_B_Primary_Contact_Email` (proposed) | active | Trim and lowercase for comparison; never place real addresses in repository fixtures. |
| Party B Contact Phone Number | `party_b_primary_contact_phone` | Phone | phone / Phone / `Party_B_Primary_Contact_Phone` (proposed) | active | Individual contact phone, distinct from organization phone; normalize to E.164 where possible. |
| Party B Contact Job Title | `party_b_primary_contact_job_title` | String | text / Single Line / `Party_B_Primary_Contact_Job_Title` (proposed) | active | Optional contact-role snapshot; do not use as authorization proof. |
| Contract Amount | `contract_amount` | Currency | currency / Currency / `Contract_Amount` (proposed) | active | Nonnegative, two decimals, and paired with the applicable ISO currency code outside a single-currency tenant. |

## Custom Fields

These are the approved design types to use when configuring the custom fields. Existing tenant fields must still be reconciled through metadata before automation uses them.

| Field | Registry ID | Zoho Contracts type | CRM design | Status | Validation / alias rule |
|---|---|---|---|---|---|
| Lease Number | `lease_number` | Text | Single Line / `Lease_Number` (proposed) | active | Required, case-insensitive unique, centrally generated; preserve letters, hyphens, and leading zeros. |
| Property Street Line 1 | `property_address_line_1_snapshot` | Text | Single Line / `Property_Street_Line_1` (proposed) | active | Required for property-specific agreements; freeze as an execution snapshot. |
| Property City | `property_city_snapshot` | Text | Single Line / `Property_City` (proposed) | active | Required with a property address; freeze as an execution snapshot. |
| Property State | `property_state_code_snapshot` | Dropdown | Pick List / `Property_State` (proposed) | active | Required two-letter USPS state code; do not accept free-text variants. |
| Property Zip Code | `property_postal_code_snapshot` | Text | Single Line / `Property_Zip_Code` (proposed) | active | Text, never Number; match five-digit ZIP or ZIP+4 and preserve leading zeros. |
| Storage Unit Number | `storage_unit_number` | Text | Single Line / `Storage_Unit_Number` (proposed) | active | Required for a storage agreement; preserve letters, separators, and leading zeros. |
| Number of Storage Unit Keys Provided | `storage_keys_provided_count` | Number | Number / `Storage_Keys_Provided_Count` (proposed) | active | Whole number, minimum zero; do not infer possession solely from this count. |
| Storage Term Begins | `storage_term_start_date` | Date | Date / `Storage_Term_Start_Date` (proposed) | active | ISO YYYY-MM-DD; canonical storage start date and must not follow Storage Term Ends. |
| Storage Unit Rent | `storage_unit_rent_amount` | Currency | Currency / `Storage_Unit_Rent` (proposed) | active | Nonnegative, two decimals, organization currency; this field must not directly create an invoice. |
| Storage Term Ends | `storage_term_end_date` | Date | Date / `Storage_Term_End_Date` (proposed) | active | ISO YYYY-MM-DD; when present, must not precede the canonical storage start date. |
| Storage Term Starts | `storage_term_starts_legacy` | Date | Date / do_not_create | deprecated_alias | Do not create or independently populate. Migrate templates to Storage Term Begins unless a reviewed definition distinguishes access start from billing start. |
| Party C Contact Name | `party_c_primary_contact_name` | Text | Single Line / `Party_C_Contact_Name` (proposed) | active | Require an explicit Party C role before use; prefer a related Contract Party record over permanent ordinal fields. |
| Party D Contact Name | `party_d_primary_contact_name` | Text | Single Line / `Party_D_Contact_Name` (proposed) | active | Require an explicit Party D role before use; prefer a related Contract Party record over permanent ordinal fields. |
| Party C Contact Phone Number | `party_c_primary_contact_phone` | Phone | Phone / `Party_C_Contact_Phone` (proposed) | active | Normalize to E.164 where possible; never include real values in repository fixtures. |
| Party D Contact Phone Number | `party_d_primary_contact_phone` | Phone | Phone / `Party_D_Contact_Phone` (proposed) | active | Normalize to E.164 where possible; never include real values in repository fixtures. |
| Party C Contact Email Address | `party_c_primary_contact_email` | Email | Email / `Party_C_Contact_Email` (proposed) | active | Trim and lowercase for comparison; never include real values in repository fixtures. |
| Party D Contact Email Address | `party_d_primary_contact_email` | Email | Email / `Party_D_Contact_Email` (proposed) | active | Trim and lowercase for comparison; never include real values in repository fixtures. |
| Lease Agreement Effective Date | `lease_agreement_effective_date_custom` | Date | Date / do_not_create_until_defined | review_required | Do not create a duplicate CRM field unless counsel/business rules document how this differs from system Agreement Date. |
| Property Apartment Number | `property_unit_number_snapshot` | Text | Single Line / `Property_Unit_Number` (proposed) | active | Text, not Number; preserve letters, separators, and leading zeros. Prefer the display label Property Unit Number. |

## Required Reconciliation Before Live Mapping

- **Party A Time Zone Name:** Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation.
- **Party B Time Zone Name:** Fetch tenant metadata before mapping; if this is a zone name, store an IANA identifier rather than an abbreviation.
- **Party A Time Zone:** Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes.
- **Party B Time Zone:** Do not create a CRM field until metadata establishes whether this is an offset, ID, or display value; derive offsets because of daylight-saving changes.
- **Renewal Notice Days:** Do not sync until apiName proves whether this is the legal renewal notice or the operational expiration-reminder lead.
- **Lease Agreement Effective Date:** Do not create a duplicate CRM field unless counsel/business rules document how this differs from system Agreement Date.
- **Storage Term Starts:** deprecated alias of `storage_term_start_date`; do not create or independently populate it.
- **Party C/D:** add an explicit role field or use a Contract Party related record before relying on ordinal party labels.

## Tenant Metadata Verification

1. Call `GET /api/v1/admin/contracttypes/{contract-type-api-name}/allfields` with `contracts.meta.READ`.
2. Match by returned stable `apiName`, not display text.
3. Record `metaType` (`1` system, `3` custom), `dataType`, and `displayType`.
4. Query CRM fields with `GET /crm/v8/settings/fields?module=...` and replace proposed names only after exact module/layout verification.
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
