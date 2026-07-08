# CRM Units Routing Setup

Zillow intake routes leads to CRM Units through the `Units` module. The preferred routing source is CRM data, not a large Catalyst environment variable.

## Required Catalyst Settings

```text
ZOHO_CRM_UNITS_MODULE=Units
ENABLE_DYNAMIC_UNIT_ROUTING=true
DYNAMIC_UNIT_ROUTING_REQUIRED=false
UNIT_PROPERTY_LOOKUP_FIELD=Property
PROPERTY_UNIT_MAP_JSON={}
ZOHO_CRM_FIELD_MAP_JSON={}
```

`ZOHO_CRM_UNITS_MODULE` must use the module API name from Zoho CRM Developer Hub. For GH Real Estate, the verified API name is `Units`.

## Required Unit Fields

| Field Label | API Name | Field Type | Purpose |
|---|---|---|---|
| Property | `Property` | Lookup | Links each Unit to its parent Property record. |
| Unit Number | `Unit_Number` | Number | Numeric unit only, for sorting/reporting. |
| Zillow Listing ID | `Zillow_Listing_ID` | Single Line | Strongest Zillow routing key once Zillow provides real listing IDs. |
| Zillow Provider Model ID | `Zillow_Provider_Model_ID` | Single Line | Optional multifamily/floorplan key if Zillow provides a meaningful model ID. |
| Zillow Listing Contact Prefix | `Zillow_Listing_Contact_Prefix` | Single Line | Optional prefix before `@` in listing contact email. |
| Zillow Routing Unit Key | `Zillow_Routing_Unit_Key` | Single Line | Address/unit fallback key used before real listing IDs are known. |

## Unit Number Rule

Use numbers only:

```text
1
2
3
4
```

Do not use `Apt. 1` or `Unit 1` in `Unit_Number` because it is a Number field.

## Unit Name Rule

Keep the readable display name in the standard `Name` field:

```text
9401 Nieman Road - Apt. 1
9401 Nieman Road - Apt. 2
9401 Nieman Road - Apt. 3
9401 Nieman Road - Apt. 4
```

## Property Lookup Rule

Set every Unit's `Property` lookup to its parent property:

```text
9401 Nieman Road
```

This lets the intake populate both `Requested Unit` and `Requested Property` on the CRM Lead.

## Zillow Routing Unit Key Values

Use lowercase plain text. No backticks. No quotation marks.

| Unit | Zillow Routing Unit Key |
|---|---|
| 9401 Nieman Road - Apt. 1 | `9401 nieman road|unit 1|overland park|ks|66214` |
| 9401 Nieman Road - Apt. 2 | `9401 nieman road|unit 2|overland park|ks|66214` |
| 9401 Nieman Road - Apt. 3 | `9401 nieman road|unit 3|overland park|ks|66214` |
| 9401 Nieman Road - Apt. 4 | `9401 nieman road|unit 4|overland park|ks|66214` |

These values match the current internal test payload format:

```text
listingStreet=9401 Nieman Road
listingUnit=Unit 3
listingCity=Overland Park
listingState=KS
listingPostalCode=66214
```

The runtime normalizes that into:

```text
9401 nieman road|unit 3|overland park|ks|66214
```

## Fields To Leave Blank Until Zillow Sends Real Data

Leave these blank until Zillow test callback provides real values:

```text
Zillow Listing ID
Zillow Provider Model ID
Zillow Listing Contact Prefix
```

After Zillow sends the real test callback, copy the actual `listingId` to `Zillow Listing ID` on the matching Unit. That becomes the strongest routing key.

## Search Test

After saving `Zillow_Routing_Unit_Key` on a Unit, test CRM search:

```powershell
$unitsModule = "Units"
$criteriaRaw = "(Zillow_Routing_Unit_Key:equals:9401 nieman road|unit 3|overland park|ks|66214)"
$criteriaEncoded = [System.Uri]::EscapeDataString($criteriaRaw)
$unitSearchUrl = "https://www.zohoapis.com/crm/v8/$unitsModule/search?criteria=$criteriaEncoded&per_page=2"

$unitSearch = Invoke-RestMethod `
  -Method Get `
  -Uri $unitSearchUrl `
  -Headers @{ "Authorization" = "Zoho-oauthtoken $accessToken" }

$unitSearch | ConvertTo-Json -Depth 10
```

Expected result: the matching Unit record is returned.

## Routing Priority

The runtime attempts routing in this order:

1. Runtime map fallback, if configured.
2. Unit `Zillow_Listing_ID`.
3. Unit `Zillow_Provider_Model_ID`.
4. Unit `Zillow_Listing_Contact_Prefix`.
5. Unit `Zillow_Routing_Unit_Key`.

If a Unit matches but `Requested Property` is not populated, confirm that `UNIT_PROPERTY_LOOKUP_FIELD=Property` and the Unit's `Property` lookup is filled.
