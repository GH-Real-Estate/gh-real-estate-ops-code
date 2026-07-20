# Zoho Payments Master Research Dossier

**Document ID:** GH-ZOHO-PAYMENTS-KB  
**Program:** GH Real Estate / Sylvara systems knowledge base  
**Research cutoff:** 2026-07-20  
**Edition researched:** Current official United States Zoho Payments documentation  
**Primary API generation:** Zoho Payments REST API v1  
**Evidence labels:** `DOC-VERIFIED`, `LIVE-METADATA REQUIRED`, `VOLATILE`, `POLICY INPUT REQUIRED`, `RESEARCH INFERENCE`, `DOC-GAP`, `DOC-DRIFT`

> **AI ingestion directive.** Zoho Payments is a payment processor/gateway, not Zoho Books' ledger, Billing's subscription policy engine, Checkout's page configuration, or CRM/Creator's operational system. Every REST call requires a verified Payments `account_id`; never infer it from a payer or let a client select it. Keep OAuth, API/widget keys, webhook and return-signing keys server-side or in their explicitly documented widget context. Never store raw card/bank data. Never fulfill from a browser redirect alone. A verified webhook plus server-side retrieval must match legal entity, account, object ID, amount, currency, reference and expected status. The current API documents no universal idempotency header: never blindly retry a financial `POST` after an uncertain outcome.

## 1. System boundary and current availability

Zoho Payments provides:

- customer and saved payment-method references;
- payment-method collection sessions;
- payment sessions for hosted checkout/embedded flows;
- server-created payments with saved methods;
- payment links;
- full/partial refunds;
- webhooks;
- payout and payout-transaction reads;
- hosted checkout, payment widget and payment-method widget.

It does not decide:

- whether a rent, fee, deposit, contribution, invoice, subscription or refund is lawful/approved;
- tax amount or accounting classification;
- Billing subscription schedule/proration/dunning;
- Books invoice/payment/credit/journal/reconciliation treatment;
- customer/tenant operational fulfillment.

### 1.1 US capability boundary

`DOC-VERIFIED` Current US help says the business must be registered in the United States. US documentation supports card and ACH debit. It can accept more than 135 currencies while payouts are in USD; exact currency/method/account eligibility must be verified.

`VOLATILE` Zoho Payments has region-specific sites, onboarding, methods and sandbox behavior. This dossier must not be used as India/other-region documentation. Build a separate edition dossier before non-US implementation.

## 2. API root, account identity, OAuth, and keys

### 2.1 API root and mandatory account selector

- `DOC-VERIFIED` US root: `https://payments.zoho.com/api/v1`.
- Every REST request requires `account_id` as a query parameter.
- `account_id` identifies the processor account/legal entity. Store it in a server-side tenant registry with payout bank, currencies, methods and environment.
- Treat IDs as opaque strings.

Example route form: `GET https://payments.zoho.com/api/v1/payments/{payment_id}?account_id={account_id}`.

### 2.2 Organization OAuth

Current org OAuth flow:

- authorization: `GET https://accounts.zoho.com/oauth/v2/org/auth`;
- token exchange/refresh: `POST https://accounts.zoho.com/oauth/v2/token`;
- revoke: `/oauth/v2/token/revoke`;
- service organization selector: `soid=zohopay.{account_id}`;
- API header: `Authorization: Zoho-oauthtoken {access_token}`.

Owner/Admin grants org access. Authorization code lifetime is one minute; access token is approximately one hour; offline access yields a refresh token. The current guide states a maximum of 20 refresh tokens, with oldest removal after the limit.

### 2.3 Scopes

| Family | Current scope patterns |
|---|---|
| Customers | `ZohoPay.customers.CREATE`, `.READ`, `.DELETE` |
| Payment methods/sessions | `ZohoPay.paymentmethods.CREATE`, `.READ`, `.UPDATE`, `.DELETE` |
| Payments/sessions/links | `ZohoPay.payments.CREATE`, `.READ`, `.UPDATE` |
| Refunds | `ZohoPay.refunds.CREATE`, `.READ` |
| Payouts | `ZohoPay.payouts.READ` |
| Webhook configuration | `ZohoPay.settings.CREATE`, `.READ`, `.UPDATE`, `.DELETE` |

`DOC-DRIFT` An older self-client authentication page differs/incompletely lists scopes. Use the current org OAuth and exact endpoint page, least privilege, separate app/consent per company/environment, and record granted scopes.

### 2.4 Browser API/widget key

The API key is generated under Payments > Settings > Developer Space and is used by documented browser widgets. Only Owner/Admin/Developer can generate/view it. Official guidance simultaneously warns not to share/post the key while widget examples expose the necessary browser artifact.

Safe interpretation:

- Use it only in the exact documented widget integration.
- Treat it as restricted, rotatable and domain/context-bound—not as a server REST credential.
- Never commit it to GitHub, put it in PDFs/logs, or use it instead of OAuth.
- Server creates sessions/intents; browser receives only the documented widget/session material.

## 3. Response, errors, pagination, limits, and safe retry

### 3.1 Response/errors

Responses generally use `{ "code": 0, "message": "...", "<resource>": ... }`. Current docs list HTTP 200/201, 400, 401, 404, 405, 429 and 500. Validate both HTTP and Zoho code; redact payloads.

Retry 429 and transient 5xx with bounded exponential backoff and jitter only when operation safety is established. A network timeout after request send is an unknown outcome, not a failure.

### 3.2 Pagination/filtering

- List endpoints commonly use `page` and `per_page`; default 25, maximum 200 on documented resources.
- Continue until the API indicates no additional data; persist watermarks and overlap for reconciliation.
- Dates/status/search/method filters are endpoint-specific.

### 3.3 Rate limits

`DOC-VERIFIED` Current category limits:

| API category | Limit |
|---|---|
| Customers | 600 requests/minute |
| Payment methods | 600/minute |
| Payments | 600/minute |
| Refunds | 60/minute |

`DOC-GAP` Do not assume undocumented category limits. Centralize limiter per `account_id`, cap concurrency and ask Zoho support about capacity changes.

### 3.4 Idempotency gap and operation ledger

`DOC-GAP` No official Payments idempotency key/header was found in current docs. Therefore:

1. Create a non-PII immutable operation key before customer/session/link/payment/refund creation.
2. Store account, operation type, expected IDs/amount/currency/reference, request hash and state in a server write ledger.
3. Use `reference_number`, `reference_id` or approved metadata only where supported; they correlate but are not assumed unique.
4. Serialize payments/refunds by source/payment and operation.
5. After timeout, reconcile webhook, GET endpoint and local mappings before retry. Do not issue a second create/refund merely because no response arrived.
6. Retain `customer_id`, session IDs, `payment_id`, `refund_id`, `payout_id` and Books/Billing cross-references.

There is no documented customer lookup-by-email guarantee. Persist the customer mapping locally to avoid duplicates.

## 4. API resource inventory and schemas

## 4.1 Customers

Routes:

- `POST /customers`
- `GET /customers`
- `GET /customers/{customer_id}`
- `DELETE /customers/{customer_id}`

Create requires `name` and `email`; phone is optional. Returned fields include `customer_id`, name/email/phone, `meta_data`, created and modified time.

Metadata controls: maximum five entries; key max 20 characters; value max 500. Official docs prohibit sensitive/card/bank data and PII such as phone/email in metadata. Use only non-sensitive opaque correlation keys.

List filters:

- `filter_by` with documented date presets (`Date.Today`, `ThisMonth`, `ThisYear`, `PreviousMonth`, `PreviousYear`, `CustomDate`, `Last_30_Days`);
- `from_date`, `to_date`;
- `page`, `per_page` (default 25/max 200).

`POLICY INPUT REQUIRED` A Payments customer is a processor object, not the master CRM/Billing/Books party. Create once per account and persist cross-references.

## 4.2 Payment-method sessions

Routes:

- `POST /paymentmethodsessions`
- `GET /paymentmethodsessions/{payment_method_session_id}`

This creates a temporary secure collection/tokenization session; it does **not** charge. Use the documented payment-method widget/flow. Store the resulting opaque payment-method ID, not raw inputs.

## 4.3 Payment methods

Routes:

- `PUT /paymentmethods/{payment_method_id}`
- `GET /paymentmethods/{payment_method_id}`
- `DELETE /paymentmethods/{payment_method_id}`

`DOC-GAP` No general list endpoint is documented. Types include `card` and `ach_debit`. Returned details are masked (brand/holder/last four/expiry/funding/country or ACH bank/routing/account-holder/type/last four). Never reconstruct/store full credentials.

Deleting a method can affect recurring/off-session collection; verify Billing/customer impact and approvals.

## 4.4 Payment sessions

Routes:

- `POST /paymentsessions`
- `GET /paymentsessions/{payments_session_id}`

Create requires amount, currency and description. Important optional fields include invoice/reference number, metadata, allowed methods, success/failure URLs and hosted-checkout/widget parameters.

- Default/maximum lifetime: 15 minutes; `expires_in` accepts 300–900 seconds.
- `max_retry_count`: 1–5.
- First successful payment closes the session.
- Success/failure URLs must be HTTPS.
- Hosted URL: `https://payments.zoho.com/hostedcheckout/{access_key}`.
- Result can be `succeeded`, `failed`, or `in_progress` for ACH/asynchronous processing.
- Result contains object IDs, amount, user-defined fields and signature.

`DOC-DRIFT` REST docs use `allowed_payment_methods` values `card`/`ach_debit`, while a hosted-checkout example uses `card`/`ach`. Verify the current OpenAPI/live endpoint before deployment.

Never fulfill from return parameters. Verify the return signature, then GET current server-side session/payment; `in_progress` is not paid.

## 4.5 Payments

Routes:

- `POST /payments`
- `GET /payments`
- `GET /payments/{payment_id}`

Create with a saved method requires `customer_id`, `payment_method_id`, amount and currency. It supports on-session/off-session context, browser information required for on-session, statement descriptor, description, shipping and metadata.

Off-session attempts can fail if 3DS/customer action is required. Do not assume a saved card guarantees success.

Documented API statuses include `initiated`, `succeeded`, `failed`, `incomplete`, `refunded`, `partially_refunded`, `blocked`, and `disputed`; ACH/UI can add pending semantics. Always use the current returned state.

List filters include:

- status (`Status.All`, `Failed`, `Succeeded`, `Canceled`, `Refunded`, `Disputed`); current docs say Canceled groups failed plus customer-canceled/abandoned;
- `search_text`;
- date preset/from/to;
- `payment_method_type` (`card`, `ach_debit`);
- page/per-page default 25/max 200.

Returned financial fields include session/customer/method IDs, amount/currency, captured/refunded amount, fees/net/exchange data, status, receipt email, invoice/reference numbers and descriptor. Use these for reconciliation, not as authority to invent accounting entries.

## 4.6 Payment links

Routes:

- `POST /paymentlinks`
- `PUT /paymentlinks/{payment_link_id}`
- `GET /paymentlinks/{payment_link_id}`
- `PUT /paymentlinks/{payment_link_id}/cancel`

`DOC-GAP` No list endpoint is documented.

Create requires amount, currency and description. Optional fields include email, phone, `reference_id` (max 100), expiry (default 30 days), `notify_customer.email`, return URL and allowed card/ACH methods. Statuses: `active`, `paid`, `canceled`, `expired`. `notify_user` is deprecated.

The return-signature message uses payment-link ID, payment ID, amount, status and payment-link reference with the signing key. Verify it server-side and retrieve the resource. A `paid` redirect without valid signature/server state is untrusted.

## 4.7 Refunds

Routes:

- `POST /payments/{payment_id}/refunds`
- `GET /refunds/{refund_id}`

Full or partial refund is controlled by amount. Required fields include amount, reason and type. Documented reasons: `duplicate`, `fraudulent`, `requested_by_customer`, `others`. Status: `initiated`, `succeeded`, `failed`, `canceled`, `pending`.

`DOC-GAP` No refund-list endpoint is documented. Refund rate limit is 60/minute.

Before refund:

- retrieve payment/account/legal entity and amount already refunded;
- validate approved reason and remaining refundable amount;
- lock by operation key and serialize;
- submit once, then wait for verified webhook/GET state;
- reconcile Billing/Books credit/refund and customer state.

Never refund using only a customer-supplied `payment_id`.

## 4.8 Payouts

Routes:

- `GET /payouts`
- `GET /payouts/{payout_id}`
- `GET /payouts/{payout_id}/transactions`

Read-only. List filters include status, date and payout method plus page/per-page default 25/max 200. Payout arrival is settlement evidence, not individual payment finality. Reconcile gross payments, fees, refunds/disputes and net payout to Books clearing/bank accounts.

## 5. Webhooks

### 5.1 Configuration API

Routes:

- `POST /webhooks`
- `GET /webhooks`
- `PUT /webhooks/{webhook_url_id}`
- `GET /webhooks/{webhook_url_id}`
- `DELETE /webhooks/{webhook_url_id}`

Endpoint URL must be HTTPS. Maximum five webhook endpoints per account. Fields include name (max 50), URL, description, status (`active`, `inactive`, `disabled`), enabled events and timestamps. Signing key is returned only on API creation and can be viewed in app; store it immediately in the secret manager.

### 5.2 Events

Current US event types:

- `payment.succeeded`, `payment.failed`, `payment.pending`
- `payment_link.paid`, `.expired`, `.canceled`
- `refund.succeeded`, `refund.failed`
- `payout.initiated`, `.paid`, `.failed`

`VOLATILE` Subscribe only to required events and compare against current event catalog.

### 5.3 Signature verification

- Header: `X-Zoho-Webhook-Signature` containing timestamp `t` and signature `v`.
- Message: `{t}.{raw_request_payload}`.
- Algorithm: HMAC SHA-256 with signing key.
- Preserve raw request bytes; compute and constant-time compare before JSON parsing/processing.
- Add application replay control: reject timestamps outside documented local tolerance and cache `event_id`/delivery evidence.
- Never log signature key or raw payment payload.

### 5.4 Delivery behavior

- At-least-once; duplicates are possible. Persist/deduplicate `event_id`.
- `payment.failed` can occur for every failed attempt; retrieve current session/payment before irreversible “final failure” logic.
- Return 2xx within 15 seconds; enqueue and process asynchronously.
- Retries continue up to two days: hourly during day one and every two hours during day two.
- Warning emails occur after roughly six hours and one day; endpoint is disabled after two days of failure.
- Signatures are unique per delivery attempt.

Receiver sequence:

1. Read raw body and signature header.
2. Resolve account/endpoint signing secret without using payload-controlled routing.
3. Verify HMAC and replay window.
4. Record/dedupe event; return 2xx after durable enqueue.
5. Retrieve the API object with the correct `account_id`.
6. Compare expected amount/currency/reference/legal entity/state.
7. Apply one idempotent downstream transition; retain reconciliation evidence.

## 6. Hosted checkout, widget, and browser/server boundary

### 6.1 Server responsibilities

- Resolve legal entity/account and approved charge.
- Create customer/method session/payment session/link/payment/refund.
- Hold OAuth/client/webhook/return-signing keys.
- Maintain operation ledger and ID mappings.
- Verify signatures and retrieve final state.

### 6.2 Browser responsibilities

- Render documented widget or navigate to hosted checkout/payment link.
- Receive opaque session/access artifacts and public configuration only.
- Collect payment details solely through Zoho's documented secure surface.
- Display pending/success/failure UI without granting business fulfillment.

Never pass raw card/bank details through CRM, Creator, Catalyst logs or application servers unless a separately approved PCI design explicitly requires it.

## 7. Security, compliance, and sandbox reality

Official security documentation states PCI DSS Level 1, ISO 27001:2022, TLS 1.3, mandatory MFA, reauthentication for sensitive actions, RBAC and encrypted payment payloads.

Operational controls:

- separate Payments accounts/OAuth clients/secrets/webhooks/payout banks for GH and Sylvara legal entities;
- least scopes and roles; admin MFA; access review and token/key rotation;
- secret manager for all OAuth, API/widget, webhook and signing material;
- no secrets, raw financial payload PII or full bank/card data in GitHub, WorkDrive project docs, logs, analytics or custom metadata;
- HTTPS only, strict return/redirect allowlist, content security policy and dependency review;
- mask IDs as policy requires while retaining immutable cross-references in controlled systems.

### 7.1 No US sandbox

`DOC-VERIFIED` Current US FAQ says Zoho Payments does **not** provide a sandbox/test environment; it provides a demo account. India has a sandbox, but it is not a substitute for a US account.

For GH/Sylvara US:

- Use demo only for orientation.
- Ask Zoho support for an approved test approach/isolated account.
- If no nonproduction processor is available, use explicitly approved low-value live tests with limits, identified testers, refund/cleanup and Books/payout reconciliation.
- Never claim “sandbox-tested” from an India environment or demo.

## 8. GH/Sylvara-safe workflow patterns

### 8.1 Approved one-time payment

1. CRM/Creator supplies approved immutable business event, legal entity, amount/currency and payer mapping.
2. Backend resolves `account_id`, reuses/creates customer, then creates payment session/link.
3. Persist operation + session/link IDs and expected values.
4. Browser uses hosted/widget flow.
5. Verified webhook + server GET must show expected success. ACH pending/in-progress remains pending.
6. Books creates/links approved invoice/payment/clearing entry and later payout reconciliation.
7. CRM/Creator receives only a verified status/cross-reference; no payment credentials.

### 8.2 Saved method/off-session

- Collect through payment-method session/widget with clear consent.
- Store opaque method ID against the correct Payments customer/account.
- Off-session charge only under approved mandate/notice and amount rules.
- Handle 3DS/customer-action failures by returning to an on-session flow; no repeated silent retries.

### 8.3 Billing recurring collection

Billing owns schedule, plan, invoice, proration, amendments and dunning. Payments processes. Books is ledger. Store Billing customer/subscription/invoice -> Payments account/customer/method/payment -> Books IDs. Do not create a second schedule in Checkout or custom cron.

### 8.4 Refund

- Approved request/ticket, payment retrieval, remaining amount and dual approval above threshold.
- Operation lock; one refund `POST`.
- Verified refund event + GET result.
- Books/Billing credit/refund linkage and customer notification through approved owner.
- Exception queue for pending/failed/unknown; no duplicate refund retry.

### 8.5 Reconciliation

Nightly:

- page through payments and payouts;
- join processor IDs/reference/operation key to Billing/Books and CRM/Creator mappings;
- compare gross, fees, refunds/disputes, net and payout bank timing;
- exception queue for unmatched/duplicate, amount/currency mismatch, pending/failed/disputed/refunded and payout variance;
- no automated journal entry without finance-owned rules.

## 9. Tax, currency, and accounting boundary

Zoho Payments accepts a gross amount/currency; it is not the tax engine. Tax is calculated/snapshotted in the approved Books/Billing/Checkout workflow. Persist jurisdiction/rate/source with the financial transaction, not in sensitive processor metadata.

Use integer minor units or an exact decimal library internally; validate currency decimal rules; compare exact amount/currency at every boundary. Payout USD does not eliminate foreign-currency charge/exchange/fee accounting.

## 10. Deluge and Catalyst integration pattern

`DOC-GAP` The current Deluge integration-task catalog reviewed does not list a native Zoho Payments task family. Use a server-side Catalyst function or Deluge `invokeUrl` with a properly configured OAuth/custom connection after confirming org OAuth and `ZohoPay.*` scope support in the current connection editor.

```deluge
// Illustrative read-only skeleton only.
account_id = "<ZOHO_PAYMENTS_ACCOUNT_ID>";
payment_id = "<ZOHO_PAYMENT_ID>";
response = invokeUrl
[
    url: "https://payments.zoho.com/api/v1/payments/" + payment_id + "?account_id=" + account_id
    type: GET
    connection: "<ZOHO_PAYMENTS_OAUTH_CONNECTION>"
];
if(response.get("code") != 0)
{
    // Fail closed; redact error details.
}
```

`LIVE-METADATA REQUIRED` Compile/test the connection and scope in the host. Never put OAuth token in source. For webhooks, Catalyst/another backend should preserve raw bytes for HMAC verification before parsing.

## 11. Testing and change control

Preflight:

- legal entity, US eligibility, `account_id`, owner/admin, OAuth client/consent/scopes;
- payout bank, currencies and methods;
- webhook URLs/events/signing keys;
- Books/Billing/Checkout/CRM mappings and approved charge/refund policy.

Test matrix:

- card and ACH success/fail/pending; abandonment; customer action/3DS;
- session expiry/retry count and link expiry/cancel;
- return-signature failure and replay;
- webhook valid/invalid signature, duplicate, out of order, 15-second acknowledgement and disabled/retry recovery;
- token expiry/revocation, 429/5xx and timeout-after-commit;
- full/partial/duplicate/pending/failed refund;
- amount/currency/reference/account mismatch;
- fees/refunds/disputes/payout reconciliation.

Because US has no sandbox, every live test needs named approval, low limits, test identity, cleanup/refund, customer-communication suppression where allowed, and end-to-end Books/bank reconciliation.

Every change requires short-lived branch, sanitized fixtures, focused PR, deployment evidence, webhook canary, kill switch, smoke test and rollback/compensation. Secret/key changes occur outside Git and require rotation evidence.

## 12. Live-metadata checklist

- legal entity, account ID, region/edition, environment/demo/live and owner;
- OAuth client/connection/scopes and rotation owner;
- supported payment methods/currencies, payout bank/currency/schedule;
- customers and cross-system mappings;
- hosted checkout/widget/link configuration and allowlisted domains;
- webhook endpoints/events/signing-key version/replay tolerance/queue/DLQ;
- Books/Billing/Checkout account, invoice, subscription, tax and reconciliation mapping;
- refund authority/thresholds and dispute/chargeback owner;
- monitoring, retention, redaction and incident plan.

## 13. Official source registry

All links verified 2026-07-20.

### API and authentication

- API introduction: https://www.zoho.com/us/payments/api/v1/introduction/
- Organization OAuth: https://www.zoho.com/us/payments/developerdocs/web-integration/org-oauth/
- Authentication/self-client reference: https://www.zoho.com/us/payments/developerdocs/web-integration/authentication/
- Customers: https://www.zoho.com/us/payments/api/v1/customers/
- Payment-method sessions: https://www.zoho.com/us/payments/api/v1/payment-method-session/
- Payment methods: https://www.zoho.com/us/payments/api/v1/payment-methods/
- Payment sessions: https://www.zoho.com/us/payments/api/v1/payment-session/
- Payments: https://www.zoho.com/us/payments/api/v1/payments/
- Payment links: https://www.zoho.com/us/payments/api/v1/payment-links/
- Refunds: https://www.zoho.com/us/payments/api/v1/refunds/
- Payouts: https://www.zoho.com/us/payments/api/v1/payouts/
- API errors: https://www.zoho.com/us/payments/api/v1/errors/

### Webhooks and signatures

- Webhooks API: https://www.zoho.com/us/payments/api/v1/webhooks/
- Webhook events: https://www.zoho.com/us/payments/api/v1/webhooks-events/
- Return signature verification: https://www.zoho.com/us/payments/developerdocs/signature-verification/
- Webhook verification: https://www.zoho.com/us/payments/developerdocs/webhooks/verification/
- Webhook best practices/retries: https://www.zoho.com/us/payments/developerdocs/webhooks/best-practices/

### Browser flows, limits, security, and operations

- Hosted checkout: https://www.zoho.com/us/payments/developerdocs/web-integration/hosted-checkout/
- Payment widget: https://www.zoho.com/us/payments/developerdocs/web-integration/integrate-widget/
- Payment-method widget: https://www.zoho.com/us/payments/developerdocs/web-integration/payment-method/
- Go live: https://www.zoho.com/us/payments/developerdocs/go-live/
- Rate limits: https://www.zoho.com/us/payments/developerdocs/rate-limits/
- Security: https://www.zoho.com/us/payments/developerdocs/security/
- Developer errors: https://www.zoho.com/us/payments/developerdocs/errors/
- US sandbox FAQ: https://www.zoho.com/us/payments/faq/general/sandbox/
- Account setup: https://www.zoho.com/us/payments/help/getting-started/setup/
- Product overview: https://www.zoho.com/us/payments/help/overview/introduction/
- Getting paid: https://www.zoho.com/us/payments/help/payments/getting-paid/
- View/manage payments: https://www.zoho.com/us/payments/help/payments/view/
- Generate payment links: https://www.zoho.com/us/payments/help/payment-links/generating-links/
