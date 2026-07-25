# Zillow Listing Publication

**Status:** Research and architecture only. No outbound Zillow feed, credentials, scheduled job, publication button, or live listing was created or deployed by this work.

This integration is intentionally separate from [Zillow lead intake](../zillow-lead-intake/README.md). Lead intake receives Zillow callbacks and writes CRM Leads. Listing publication would read approved marketing data from CRM and send it to Zillow only after Zillow approves GH Real Estate for a feed.

## Decision

For GH Real Estate's current fourplex:

1. Continue authoring and publishing listings manually in Zillow Rental Manager.
2. Ask Zillow whether GH Real Estate is eligible for Rentals Feed Integration before writing code.
3. Do not use undocumented endpoints or browser automation.
4. Treat the Unit as the operational source of market readiness, asking rent, availability, and unit facts.
5. Treat the related Property as the source of building address, shared description, shared amenities, and building photos.
6. If Zillow approves a multifamily feed, emit one Zillow property listing with nested unit or floorplan models. Zillow must confirm the correct property-type enum during onboarding.
7. Do not create a Rental Listings custom CRM module yet. Add it only when an approved feed, multiple advertising channels, or publication-history requirements justify the extra records.

There is no general public Zillow Rentals CRUD API for creating a listing directly. Zillow's documented automation path is an approval-gated XML feed that Zillow pulls from an HTTP, HTTPS, FTPS, or SFTP location. Zillow says testing typically takes four to six weeks. See [Rentals Feed Integrations](https://www.zillowgroup.com/developers/api/rentals/rentals-feed-integrations/) and the [Rental Listing Bulk Feed Guide](https://s3.amazonaws.com/files.hotpads.com/+guides/Rental+Listing+Bulk+Feed+Guide.pdf).

The current Bulk Feed Guide directs small owners and property managers to Zillow Rental Manager or a third-party syndicator instead of maintaining a custom feed. That recommendation and GH Real Estate's present scale are why the no-code decision is the default, even if the eligibility inquiry is worth making.

## Why the source is Property plus Unit

| Choice | Result |
|---|---|
| Property only | Wrong operational granularity. One vacant unit cannot safely make the whole fourplex active or change every unit's rent. |
| Unit only | Missing shared address, building facts, common amenities, and property-level photos. |
| Unit trigger plus Property inheritance | Recommended now. The marketable unit starts review; publication combines its data with its related Property. |
| Rental Listings custom module | Defer. It becomes useful for one immutable Unit × channel × marketing-cycle snapshot, retries, errors, and publication history. |

The external Zillow object can still be property-shaped even though the CRM review begins from a Unit. For an approved multifamily feed, the Property becomes the listing container and available Units become nested models.

## Current state

- The existing Catalyst Zillow integration is inbound only.
- It creates or updates CRM Leads and reads Units only to resolve inbound routing.
- It does not publish, update, deactivate, or delete Zillow listings.
- The repository has no outbound Zillow feed endpoint, scheduled job, credential, schema fixture, test, or deployment.
- Existing Zillow IDs on Units support inbound matching. They are not evidence of an outbound publishing integration.
- Existing Property and Unit listing fields in the CRM catalog are candidates unless their API names are already verified by live metadata or the operating inbound integration.

## System ownership

| Data | Source of truth | Publication role |
|---|---|---|
| Property address and building identity | Properties — standard Accounts module, API `Accounts` | Zillow property/listing container |
| Unit identity and rentable characteristics | Units — custom module, verified API `Units` | Nested unit/floorplan model |
| Market readiness and asking terms | Unit, after operator review | Starts listing preparation |
| Executed lease and tenant status | Leases | Determines occupancy; does not author marketing copy |
| Listing publication state | Zillow Rental Manager today | Record Zillow ID and URL back in CRM manually |
| Future feed snapshot/history | Deferred Rental Listings module | Add only after approval or multichannel need |
| Financial truth | Zoho Books | Never infer paid amounts or balances from the listing feed |
| Integration code and sanitized docs | GitHub/Catalyst | No credentials, private feed payloads, or tenant data |

## Zillow minimum and practical data

Zillow's current feed material requires a full address, listing contact email and phone, price, bedrooms, bathrooms, and a high-quality photo. Multifamily data separates property-level facts from unit or floorplan models. The onboarding schema and Zillow's validator control if they differ from this planning map.

### Feed and company configuration

| Zillow value | CRM/runtime source | Requirement |
|---|---|---|
| Feed version | Code constant approved during onboarding | Required |
| Company ID | Zillow-issued/configured secret-safe value | Required; do not commit production value |
| Company city and state | Approved organization configuration | Required by the current bulk guide |
| Feed location and authentication | Catalyst/secret manager configuration | Required for approved transport |
| Last updated timestamp | Generated in UTC by the publisher | Required per listing |
| Listing ID | Stable non-PII business identifier | Required and immutable for the listing lifecycle |

### Property-level data

| Zillow value | CRM source | Requirement / rule |
|---|---|---|
| Property type | Property plus Zillow onboarding decision | Required; do not guess the fourplex enum |
| Street, city, state, ZIP | Property | Required; ZIP is text |
| Property name | Property | Recommended |
| Number of units | Property | Required for current multifamily onboarding guidance |
| Property description | Property | Recommended, operator-approved |
| Shared amenities | Property | Recommended |
| Shared photo URLs | Approved public image host | At least one high-quality photo is required overall |
| Listing contact email and phone | Approved property/organization contact | Required; never use an applicant or tenant |
| Lease term and shared policies | Approved business configuration | Include when applicable |
| Property-level fees | Approved fee policy | Include only from reconciled, reviewed data |

### Unit or model data

| Zillow value | CRM source | Requirement / rule |
|---|---|---|
| Model ID | Stable Unit/feed identifier | Required |
| Model type | Onboarding-approved floorplan or unit value | Required |
| Parent model ID | Floorplan relationship, when used | Conditional |
| Unit number | Unit | Required for an individual unit model |
| Model name | Unit/floorplan display name | Required |
| Asking rent / low price | Unit Target Market Rent or approved equivalent | Required |
| High price | Approved range, when range pricing is used | Conditional |
| Bedrooms | Unit | Required |
| Full bathrooms | Unit | Required |
| Half bathrooms | Unit | Optional but recommended when applicable |
| Square feet | Unit | Recommended |
| Available date | Unit | Recommended |
| Security deposit | Unit/approved policy | Recommended |
| Unit description and amenities | Unit | Recommended, operator-approved |
| Unit photo URLs | Approved public image host | Recommended |
| Pet, parking, storage, utility, and lease terms | Unit plus approved policies | Include when applicable |
| Mandatory fees | Approved structured fee data | Include under the current onboarding schema |

Do not place Zillow feed credentials, production paths, private photo links, feed samples containing real listing identifiers, or unpublished listing data in GitHub.

## CRM preparation fields

Do not create fields from this document. First audit live CRM metadata and reconcile the governed [Properties catalog](../../field-maps/crm-module-fields/properties.csv) and [Units catalog](../../field-maps/crm-module-fields/units.csv). Proposed names are not production API names.

Reuse before adding fields:

- Property address components, Number of Units, building description, shared amenities, approved listing contact, and shared photo references.
- Unit Property lookup, Unit Number, Bedrooms, Bathrooms, Square Feet, Available Date, Target Market Rent, Security Deposit Default, occupancy/market status, and unit photo references.
- Verified inbound-routing fields `Zillow_Listing_ID`, `Zillow_Provider_Model_ID`, and `Zillow_Routing_Unit_Key`.

The Property-level `Active on Zillow?` candidate is too ambiguous to control publication when only one unit is available. Treat any future property flag as a read-only summary. A Unit market status can start preparation, but it must never publish without a separate human approval.

If Zillow approves a feed and CRM lacks an approval control, propose this field only after live metadata review:

| Field Label — Field Type | API name | Required | Default | Help text |
|---|---|---:|---|---|
| Zillow Publication Approval — Pick List | `TBD_FROM_ZOHO_METADATA` | Conditional before feed inclusion | Draft | Controls whether this unit may enter an approved Zillow feed. Source: authorized listing review. Edit: authorized users only. Vacancy alone never publishes. |

Picklist planning details:

- Scope: local Unit-module picklist
- Sort: entered order
- History tracking: recommended
- Draft — `#2563EB`
- Ready for Review — `#D97706`
- Approved to Publish — `#16A34A`
- Hold — `#EA580C`
- Withdrawn — `#6B7280`

This is a design proposal, not proof that the field exists.

## Publication workflow

### Current manual workflow

1. A vacancy, nonrenewal, or approved marketing decision sets the Unit to a reviewable market state.
2. CRM users verify Property address/building facts and Unit rent, availability, bedrooms, bathrooms, size, fees, contact data, descriptions, and photos.
3. Gabriel explicitly approves the listing packet.
4. An authorized user publishes through Zillow Rental Manager.
5. Record the resulting Zillow listing ID and URL on the Unit using live-verified fields.
6. Keep the listing active through inquiries and application review.
7. Deactivate it only when leased, withdrawn, or otherwise intentionally removed—not merely when an application arrives.

### Future approved feed

1. A scheduled Catalyst job reads only approved Properties and Units.
2. It validates required fields and rejects incomplete records without publishing.
3. It generates a complete UTF-8 Zillow/HotPads XML snapshot using the onboarding-approved schema.
4. It exposes the snapshot at the static, authenticated location approved by Zillow.
5. Zillow pulls and validates the feed.
6. The integration records sanitized success/failure state without storing tenant data or secrets.
7. An optional real-time layer may call Zillow's update-notification endpoint only after the bulk feed is operating; the bulk feed remains the reconciliation source.

Zillow treats a bulk feed as a complete snapshot: omitting a listing can remove it. Zillow also holds listing-count changes greater than 20 percent for confirmation. A four-unit design with four independent listing records could trigger that threshold whenever one record appears or disappears. The proposed multifamily container with nested unit models avoids using feed record count as the unit-availability mechanism, subject to Zillow approval.

## Feed scope recommendation

Use a hybrid feed first if Zillow approves it: keep rich listing content in Zillow Rental Manager and automate only the high-change pricing and availability values Zillow permits for that arrangement. Expand to full listing authoring only if the reduced manual work justifies the operational burden.

Do not add the optional Real-Time Listing API first. It is a notification layer: the provider marks a listing for update and Zillow retrieves the complete XML from the provider endpoint. It requires separate test and production keys, and the bulk feed remains the backstop. See the [Real-Time Listing API Guide](https://s3.amazonaws.com/files.hotpads.com/+guides/Rental+Listing+Real-Time+Listing+Guide.pdf).

## Approval and implementation gates

No implementation or production publication until all gates pass:

- [ ] Zillow confirms GH Real Estate eligibility in writing.
- [ ] Zillow supplies or confirms the current bulk-feed schema and fourplex property-type enum.
- [ ] Zillow confirms whether one multifamily listing with nested unit models is accepted for this property.
- [ ] GH chooses full or hybrid feed ownership.
- [ ] Live CRM metadata verifies every source module, field API name, type, and lookup.
- [ ] Listing contact data and public photo hosting are approved.
- [ ] Required fee data and calculation semantics are reconciled.
- [ ] Human approval behavior and authorized roles are configured.
- [ ] Sanitized fixtures cover create, change, withdraw, duplicate-source, missing-field, and feed-count scenarios.
- [ ] Zillow test validation succeeds before production access.
- [ ] Monitoring, rollback, and manual Zillow Rental Manager fallback are documented.

## Safeguards

- Never publish solely because occupancy becomes Vacant.
- Never deactivate solely because a lead or application is received.
- Prevent duplicate publication from Zillow Rental Manager and a feed at the same time.
- Use stable listing/model identifiers and idempotent generation.
- Fail closed on missing price, contact, address, bedroom, bathroom, or photo data.
- Require an authorized review after material rent, fee, availability, description, or photo changes.
- Store credentials only in approved runtime secret configuration.
- Keep feed logs free of tenant, applicant, or lead data.
- Provide a kill switch that stops outbound generation without changing CRM business records.
- Preserve the manual Zillow Rental Manager path as rollback.

## Rollback

This research-only design changes no CRM or Zillow behavior. Revert the repository commit to remove the documentation.

For a future deployment, rollback means disable the outbound job, restore manual Zillow Rental Manager ownership, verify live listing state directly in Zillow, and do not delete CRM source records.

## Official sources

Reviewed July 24, 2026:

- [Zillow Rentals Feed Integrations](https://www.zillowgroup.com/developers/api/rentals/rentals-feed-integrations/)
- [Rental Listing Bulk Feed Guide, revised June 30, 2026](https://s3.amazonaws.com/files.hotpads.com/+guides/Rental+Listing+Bulk+Feed+Guide.pdf)
- [Real-Time Listing API Guide, revised May 27, 2026](https://s3.amazonaws.com/files.hotpads.com/+guides/Rental+Listing+Real-Time+Listing+Guide.pdf)
- [Zillow multifamily new-feed requirements](https://zillow.zendesk.com/hc/en-us/articles/32915953493267-Multifamily-New-Feeds)
- [Zillow listing requirements](https://help.zillowrentalmanager.com/hc/en-us/articles/21542196327571--Zillow-Listing-Requirements)
- [Zillow listing data overview](https://help.zillowrentalmanager.com/hc/en-us/articles/21542731223827-Listing-Data-Overview)
- [Zillow fee-data guidance](https://zillow.zendesk.com/hc/en-us/articles/43429008094227-Sharing-Fee-Data-with-Zillow)
