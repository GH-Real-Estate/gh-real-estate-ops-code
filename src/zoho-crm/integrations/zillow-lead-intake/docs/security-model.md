# Security Model

Zillow lead callbacks contain prospect contact information and possible applicant-profile details. Treat this endpoint as sensitive even though it does not handle SSNs, bank records, screening reports, IDs, or pay stubs.

## Controls

- POST-only allowlisted route.
- `application/x-www-form-urlencoded` body handling by default.
- JSON disabled by default; enable only for internal testing.
- Body size cap.
- Inbound body timeout.
- Compression rejected.
- Shared-secret header gate before parsing or mutation.
- Query-string secrets disabled by default.
- Optional IP allowlist after real Zillow source IPs are confirmed.
- Optional Catalyst Cache replay/duplicate guard.
- Zoho outbound host allowlist.
- Dry-run mode by default.
- Live-mode double circuit breaker.
- No raw payload logging by default.
- No raw payload values stored in CRM; only a SHA-256 payload hash and sanitized summary.
- No secrets in source code.
- Zoho CRM writes use OAuth refresh-token flow.
- Duplicate prevention uses CRM upsert with a unique `Zillow_Lead_Key` field.

## Zillow Signature Limitation

Zillow Rentals lead delivery supports static security headers/tokens, but the guide does not document a standard HMAC signature or OAuth framework for lead delivery. Because of that, this service uses a static shared-secret header and compensating controls.

Recommended order:

1. Keep `REQUIRE_INBOUND_SECRET=true`.
2. Use `INBOUND_SECRET_HEADER_NAME=x-gh-zillow-webhook-key`.
3. Put the actual secret only in `ZILLOW_WEBHOOK_KEY` inside Zoho Catalyst.
4. Send the secret to Zillow through a one-time secret link or another secured channel.
5. Keep `ALLOW_SECRET_QUERY_PARAM=false` unless Zillow cannot send headers.
6. Rotate the secret if the endpoint URL or secret is exposed.

## Data Minimization

The service stores only CRM Lead fields needed for inquiry follow-up and routing. It does not store raw Zillow payload values as a blob, screening reports, IDs, pay stubs, lease documents, or payment data.

`Description` may include a sanitized summary of Zillow-supplied profile fields such as move-in timeframe, pets, employment status, self-reported income, and self-reported credit range. These are inquiry/application signals only. They are not approved lease terms and must not drive Books invoices.

## Live-Mode Guard

CRM Lead writes require all of these:

```text
ZILLOW_WEBHOOK_DRY_RUN=false
DRY_RUN=false
LIVE_MODE_ENABLED=true
LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
```

This is intentional. A single mis-set environment variable should not create live CRM records.
