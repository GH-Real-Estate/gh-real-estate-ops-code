# Production CRM Global Picklist Registry

This directory is the sanitized, metadata-only registry of global picklists
visible in the GH Real Estate production Zoho CRM organization as of
2026-07-24. The machine-readable source is
[`production-global-picklist-registry.json`](production-global-picklist-registry.json).

The registry contains no Zoho IDs, actor metadata, tenant records, or
credentials. It is an audit snapshot and governance aid; it is not an
authorization to create, update, replace, detach, or delete a live global
picklist.

## Source boundary

The `gh_zoho_crm_audit` MCP verified the organization as **GH Real Estate /
production** and returned ten visible global sets. The bulk endpoint omitted
each requested expansion even when it was requested alone. The direct
single-set endpoint failed with `INVALID_REQUEST` for every set. Therefore:

- top-level set names and settings come from the bulk global-picklist endpoint;
- associations come from the global-picklist association endpoint;
- values, order, used/unused state, and colors are recorded only when they were
  recoverable from associated public-module field metadata;
- an absent value list means **unknown**, never an empty governed list;
- `-None-` is excluded because it is a field-level platform sentinel, not a
  global-picklist value.

## Inventory and decision status

| Display label | API name | Owner | Associations | Values | Decision |
| --- | --- | --- | ---: | --- | --- |
| States | `States` | GH governed | 6 | 50 confirmed; all used; no colors | Keep and govern |
| Countries | `Countries` | GH governed | 6 | 195 confirmed; all used; no colors | Keep and govern |
| Building Entry Type | `Building_Entry_Type` | GH governed | None reported | Unknown | Candidate unused; do not delete |
| Contact Type | `Contact_Type` | GH governed | 1 | 7 confirmed; all used; no colors | Keep and govern |
| Property Type | `Property_Type` | GH governed | 1 | 6 confirmed; 5 used, 1 unused; no colors | Keep; review unused value |
| GH Lifecycle Status | `GH_Lifecycle_Status` | GH governed | 2 | 3 confirmed; all used; no colors | Keep and govern |
| Team Member Role | `team_member_role__s` | Zoho/system | 2 internal | Unknown | Do not mutate |
| Access | `access__s` | Zoho/system | 2 internal | Unknown | Do not mutate |
| Country__s | `Country__s` | Zoho/system | None reported | Unknown | Potential overlap; do not mutate |
| States__s | `States__s` | Zoho/system | None reported | Unknown | Potential overlap; do not mutate |

## Confirmed associations

### States — global picklist

| Module label | Module API | Field label | Field API | Layout label / API |
| --- | --- | --- | --- | --- |
| Contacts | `Contacts` | State | `State` | Standard / `Standard__s` |
| Vendors | `Vendors` | Billing State | `State1` | Standard / `Standard__s` |
| Vendors | `Vendors` | Shipping State | `Shipping_State` | Standard / `Standard__s` |
| Contacts | `Contacts` | Billing State | `Billing_State` | Standard / `Standard__s` |
| Contacts | `Contacts` | Shipping State | `Shipping_State` | Standard / `Standard__s` |
| Properties | `Accounts` | State | `State` | Standard / `Standard__s` |

All six fields returned the same 50-value alphabetical order. All values are
`used`; colors and defaults are null; field color coding and history tracking
are off. See the JSON registry for the exact ordered list.

### Countries — global picklist

| Module label | Module API | Field label | Field API | Layout label / API |
| --- | --- | --- | --- | --- |
| Contacts | `Contacts` | Country | `Country` | Standard / `Standard__s` |
| Vendors | `Vendors` | Billing Country | `Country2` | Standard / `Standard__s` |
| Vendors | `Vendors` | Shipping Country | `Shipping_Country` | Standard / `Standard__s` |
| Contacts | `Contacts` | Billing Country | `Billing_Country` | Standard / `Standard__s` |
| Contacts | `Contacts` | Shipping Country | `Shipping_Country` | Standard / `Standard__s` |
| Properties | `Accounts` | Country | `Country` | Standard / `Standard__s` |

All six fields returned the same 195-value alphabetical order. All values are
`used`; colors and defaults are null; field color coding and history tracking
are off. See the JSON registry for the exact ordered list.

### Contact Type — global picklist

Association: Contacts (`Contacts`) → Contact Type (`Contact_Type`) → Standard
(`Standard__s`).

| Order | Display / reference | Actual value | State | Color |
| ---: | --- | --- | --- | --- |
| 1 | Applicant | Applicant | used | null |
| 2 | Cosigner | Cosigner | used | null |
| 3 | Current Tenant | Tenant | used | null |
| 4 | Occupant | Occupant | used | null |
| 5 | Owner | Owner | used | null |
| 6 | Past Tenant | Past Tenant | used | null |
| 7 | Vendor | Vendor | used | null |

The `Current Tenant` display/reference value maps to the historical actual
value `Tenant`. That mapping is integration-significant and must not be
silently normalized.

### Property Type — global picklist

Association: Properties (`Accounts`) → current field label **Property Type** /
standard display label **Account Type** (`Account_Type`) → Standard
(`Standard__s`).

| Order | Value | State | Color |
| ---: | --- | --- | --- |
| 1 | Apartment | used | null |
| 2 | Apartment Building | **unused** | null |
| 3 | Property Management Building | used | null |
| 4 | Single Family House | used | null |
| 5 | Townhomes | used | null |
| 6 | Trailer | used | null |

`Apartment Building` is the only confirmed unused value. Unused does not mean
safe to delete; historical records may still reference it.

### GH Lifecycle Status — global picklist

| Module label | Module API | Field label | Field API | Layout label / API |
| --- | --- | --- | --- | --- |
| Properties | `Accounts` | Property Status | `Property_Status` | Standard / `Standard__s` |
| Vendors | `Vendors` | Vendor Status | `Vendor_Status` | Standard / `Standard__s` |

| Order | Value | State | Color |
| ---: | --- | --- | --- |
| 1 | Active | used | null |
| 2 | Inactive | used | null |
| 3 | Archived | used | null |

Both fields returned the same exact order, reference values, actual values,
usage state, and null colors. Both defaults are null; field color coding and
history tracking are off. The global set is not lexically sorted, so this
governed order must be preserved.

### Zoho/system team-selling sets

`team_member_role__s` and `access__s` are each associated with the internal
modules `Preferred_Team_Members__s` and `Team_Selling__s`, on the Standard
layout. The field APIs are `Member_Role` and `Access`, respectively. Zoho
rejected field-metadata reads for both internal modules with `INVALID_MODULE`;
their module display labels, field display labels, exact values, defaults,
colors, and history settings remain unknown. These sets are non-customizable
and must be treated as Zoho-owned dependencies.

## Unassociated, overlap, and deletion review

- **Building Entry Type (`Building_Entry_Type`)** is customizable and returned
  no associations, making it a candidate unused GH set. Its values are
  unrecoverable while the single-set endpoint fails. Do not delete or repurpose
  it until a successful value export and a second dependency check confirm the
  absence of associations.
- **Country__s** and **States__s** are non-customizable and returned no
  associations. Their labels suggest semantic overlap with `Countries` and
  `States`, but the audit did not return their values or hidden dependencies.
  They are not confirmed duplicates and must not be changed.

## Operational rules

1. Resolve by exact API name, never label alone.
2. Read associations and values immediately before any future write.
3. Preserve display, reference, and actual values as separate concepts.
4. Treat unused values as historical compatibility state until record and
   integration impact is proven.
5. Never infer unknown system-set values from Zoho documentation or a similarly
   named GH set.
6. Keep Zoho/system-managed sets outside GH mutation plans.
