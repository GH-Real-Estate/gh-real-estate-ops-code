# Security Model

Zillow lead callbacks contain applicant contact information. Treat this endpoint as sensitive even though it does not handle SSNs, bank records, screening reports, or lease documents.

## Controls

- POST-only allowlisted route.
- Strict `application/x-www-form-urlencoded` parsing by default.
- JSON disabled by default; only enable `ALLOW_JSON_TEST_PAYLOADS=true` for internal tests.
- Body size cap and inbound body timeout.
- Compressed request bodies rejected.
- Static shared-secret header gate before parsing or mutation.
- Timing-safe secret comparison.
- Query-string secret fallback disabled by default.
- Optional IP allowlist after the real Zillow source IP path is confirmed.
- Dry-run mode by default.
- Live-mode double circuit breaker.
- Outbound Zoho host allowlists.
- No raw payload logging by default.
- No secrets in source code, docs, screenshots, or Git history.
- Zoho CRM writes use OAuth refresh-token flow.
- Duplicate prevention uses CRM upsert with a unique `Zillow_Lead_Key` field.

## Zillow Signature Limitation

The Zillow Rentals Lead Delivery API supports a static security header/token but does not support OAuth for lead delivery. Because the guide does not document an HMAC signature with timestamped replay protection, this service uses a strong static header value and treats the endpoint URL and secret as sensitive.

Recommended order:

1. Deploy in `ZILLOW_WEBHOOK_DRY_RUN=true`.
2. Configure `ZILLOW_WEBHOOK_KEY` as a long random secret in Zoho Catalyst.
3. Give Zillow the endpoint URL and the header name.
4. Send the header value through a one-time secure secret link, not normal email text.
5. Rotate the secret if the endpoint URL or header value is exposed.

## Data Minimization

The service stores only CRM Lead fields needed for inquiry follow-up. It stores a raw payload hash and the raw field names received, but it does not store full raw payload values by default.

Do not add fields for `Manual_Review_Required`, `Manual_Review_Reason`, `Desired_Rent`, or `Desired_Deposit` to this intake. Manual review is operational, and approved rent/deposit should come from GH Real Estate property/unit/application records.

## Live-Mode Guard

CRM writes require all of these:

```text
ZILLOW_WEBHOOK_DRY_RUN=false
ZILLOW_WEBHOOK_LIVE_MODE_ENABLED=true
ZILLOW_WEBHOOK_LIVE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
```

This is intentional. A single mis-set environment variable should not create live CRM records.
