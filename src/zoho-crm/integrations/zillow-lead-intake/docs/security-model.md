# Security Model

Zillow lead callbacks contain applicant contact information. Treat this endpoint as sensitive even though it does not handle SSNs, bank records, or screening reports.

## Controls

- POST-only allowlisted route.
- URL-encoded and JSON body parsing only.
- Body size cap.
- Compression rejected.
- Shared-secret gate before parsing/mutation.
- Dry-run mode by default.
- Live-mode double circuit breaker.
- No raw payload logging by default.
- No secrets in source code.
- Zoho CRM writes use OAuth refresh-token flow.
- Duplicate prevention uses CRM upsert with a unique `Zillow_Lead_Key` field.

## Zillow Signature Limitation

The public Zillow Rentals Lead API page documents HTTP POST callback delivery and URL-encoded payloads, but does not document a standard webhook signature. Because of that, this service uses a shared-secret gate.

Recommended order:

1. Ask Zillow Rentals Support whether they can send a custom secret header.
2. If yes, use `INBOUND_SECRET_HEADER_NAME` and keep query secrets disabled.
3. If no, use an unguessable Catalyst route or enable query secret fallback only for this endpoint.
4. Rotate the secret if the endpoint URL is exposed.

## Data Minimization

The service stores only CRM Lead fields needed for inquiry follow-up. It does not store raw Zillow payloads, screening reports, IDs, pay stubs, lease documents, or payment data.

## Live-Mode Guard

CRM writes require all of these:

```text
DRY_RUN=false
LIVE_MODE_ENABLED=true
LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
```

This is intentional. A single mis-set environment variable should not create live CRM records.
