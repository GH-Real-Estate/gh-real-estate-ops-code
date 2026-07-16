# GH Real Estate Zoho CRM Working Field-Type Catalog

**Standard:** GH-ZOHO-CRM-001  
**Version:** 1.0  
**Effective date:** July 16, 2026  
**Status:** Working catalog pending a complete tenant-specific Zoho CRM metadata export

## Purpose

This document gives ChatGPT, Codex, and implementers a controlled vocabulary for GH Real Estate CRM field discussions.

It is intentionally not labeled a complete list of every field type available in every Zoho CRM edition, data center, feature rollout, module, or layout. The live tenant and current official documentation control.

## Required distinction

- **Zoho UI field type:** what an administrator selects in the layout editor.
- **API metadata `data_type`:** what Zoho returns from the Fields Metadata API.
- **Formula return type or subtype:** additional detail that may control storage and API behavior.

Do not use these terms interchangeably.

## Working type map

| Zoho UI / GH working type | Expected API metadata | Status | GH use |
|---|---|---|---|
| Single Line | `text` | Confirmed pattern | Short text, identifiers, codes, labels, and text-formatted postal codes. |
| Multi-Line | `textarea` | Confirmed pattern | Plain small/large or rich text; choose subtype and length deliberately. |
| Email | `email` | Confirmed pattern | Validated email address. |
| Phone | `phone` | Confirmed pattern | Phone number; do not treat as arithmetic data. |
| URL | `website` | Confirmed pattern | Web address. |
| Pick List | `picklist` | Confirmed pattern | Single choice; document ordered values, default, scope, history, and colors. |
| Multi-Select Pick List | `multiselectpicklist` | Confirmed pattern | Multiple choices; use sparingly because automation/reporting is more complex. |
| Checkbox | `boolean` | Confirmed pattern | True/false indicator. |
| Number | `integer` | Confirmed pattern | Whole number such as Unit Number or Household Size. |
| Long Integer | `bigint` | Confirmed pattern | Large whole number; identifiers are usually better stored as text. |
| Decimal | `double` | Confirmed pattern | Decimal measurement such as bathrooms or quantities. |
| Currency | `currency` | Confirmed pattern | Monetary amount with configured decimal places. |
| Percent | Expected numeric; verify live | Working mapping | Percentage value; confirm live metadata before automation. |
| Date | Expected `date`; verify live | Working mapping | Calendar date without time. |
| Date/Time | `datetime` | Confirmed pattern | Timestamp when time and zone matter. |
| Lookup | `lookup` | Confirmed pattern | Single-record relationship; specify target module and related-list behavior. |
| User | TBD from live metadata | Needs verification | User lookup/owner assignment; distinguish record Owner from a custom user lookup. |
| Auto-Number | TBD plus `auto_number` metadata | Needs verification | System-generated sequence; specify prefix, start number, and reset behavior. |
| Formula | Depends on return type | Needs formula design | Read-only calculated field; document expression, return type, decimals, and dependencies. |
| Rollup Summary | TBD plus `rollup_summary` metadata | Edition/availability dependent | Aggregates related records; document relationship, function, criteria, and limits. |
| Image Upload | TBD from live metadata | Official UI type | Image upload field; confirm edition limits, portal access, count, size, and retention. |
| File Upload | TBD from live metadata | Official UI type | File upload field; confirm edition limits, allowed files, size, and retention. |
| Address | Not assumed to be one custom API field | Design pattern | Prefer explicit street/city/state/postal/country fields unless live CRM exposes the intended address construct. |
| Subform | `subform` | Confirmed metadata type | Child line-item structure; requires a separate subform field catalog. |
| Multi-Select Lookup | `multiselectlookup` | Confirmed metadata type | Many-to-many relationship; specify linking module and related lists. |
| Owner Lookup | `ownerlookup` | Confirmed metadata type | System owner field, not interchangeable with every User field. |
| Profile Image | `profileimage` | Confirmed metadata type | System/profile image behavior; not the same as a custom image upload field. |

## Standard-field suffixes in the GH catalog

The field registry may use a more specific display such as:

- `Single Line / Standard First Name`;
- `Single Line / Standard Last Name`;
- `Single Line / Standard Account Name`;
- `Single Line / Standard Deal Name`;
- `Single Line / Standard Subject`;
- `Single Line / Module Name`;
- `Email / Standard`;
- `Phone / Standard`;
- `Pick List / Standard`;
- `Pick List / Standard Stage`;
- `Multi-Line / Standard Description`.

The suffix describes the existing Zoho field's role. It does not create a new Zoho field type.

## Multi-line subtype rule

When proposing Multi-Line, also specify one of:

| Subtype | Publicly documented capacity | Recommended use |
|---|---:|---|
| Plain Text Small | Up to 2,000 characters | Short operational notes |
| Plain Text Large | Up to 32,000 characters | Detailed plain-text summaries |
| Rich Text | Up to 50,000 characters | Formatted content only when its limitations are acceptable |

Do not default to Rich Text. Integration, view, search, mobile, formula, export, and rendering behavior may differ.

## Choice-field rule

For Pick List and Multi-Select Pick List, always specify:

- values in exact entered order;
- local, global, or standard-module scope;
- default;
- history tracking;
- color-coding recommendation;
- a six-digit hex value for each choice;
- retired or replacement values when revising an existing field.

The Fields Metadata response includes picklist values, sequence numbers, color-code support, and per-value `colour_code` values.

## Complex-type rule

The following require more than a label and type:

### Lookup

Document:

- target module display label;
- verified target module API name;
- relationship direction;
- related-list label/API name when used by automation;
- delete behavior;
- whether one-to-many or many-to-many is intended.

### Formula

Document:

- exact expression;
- return type;
- decimal places;
- null handling;
- referenced field API names;
- recalculation expectations;
- whether workflows can trigger from changes.

### Auto-Number

Document:

- prefix/suffix;
- starting number;
- digit length;
- reset behavior;
- uniqueness/business use;
- whether the number is stable enough for external references.

### Rollup Summary

Document:

- parent and related module;
- lookup relationship;
- aggregation function;
- target field;
- criteria;
- empty-set behavior;
- edition/rollout availability;
- workflow-loop risk.

### File or Image Upload

Document:

- maximum files/images;
- maximum size;
- extensions;
- portal permissions;
- PII classification;
- retention;
- whether WorkDrive or Contracts/Sign is the better source of truth.

### Subform or multi-select lookup

Create a separate child/linking field table. Do not hide the child schema inside one parent-row description.

## Current workbook vocabulary

The current supplied GH field matrix uses these field-type labels:

```text
Address
Auto-Number
Checkbox
Currency
Date
Date / Formula
Date/Time
Decimal
Email
Email / Standard
Formula
Image Upload
Long Integer
Lookup
Multi-Line
Multi-Select
Number
Number / Formula
Percent
Phone
Phone / Standard
Pick List
Pick List / Standard
Pick List / Standard Stage
Single Line
Single Line / Module Name
Single Line / Standard Account Name
Single Line / Standard Deal Name
Single Line / Standard First Name
Single Line / Standard Last Name
Single Line / Standard Subject
Single Line / Standard Vendor Name
URL
User
```

Compound entries such as `Date / Formula` and `Number / Formula` are unresolved design choices, not final field types. Before creation, select one actual Zoho field type and document the formula if Formula is chosen.

## Official-source facts used by this working catalog

- Zoho's Fields Metadata endpoint returns field label, API name, `data_type`, tooltip, picklist details, color coding, lookup/formula/auto-number objects, and other metadata.
- Zoho documents that custom field type cannot be changed after creation.
- Zoho documents Plain Text Small, Plain Text Large, and Rich Text multi-line formats.
- Zoho documents picklist color coding across modules.
- Zoho documents File Upload, Image Upload, and Rollup Summary fields, subject to edition and rollout limits.

Official sources:

- https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html
- https://help.zoho.com/portal/en/kb/crm/customize-crm-account/customizing-fields/articles/types-of-fields

## Update gate

When the user supplies a complete field-type catalog or a live metadata export:

1. preserve exact official UI names;
2. add edition/feature availability;
3. add actual `data_type`, JSON type, length/precision, and subtype behavior;
4. remove uncertain mappings only after evidence;
5. update the machine-readable CRM catalog;
6. rerun the catalog validator.
