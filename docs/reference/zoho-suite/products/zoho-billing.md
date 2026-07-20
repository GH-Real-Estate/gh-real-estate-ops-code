# Zoho Billing Master Research Dossier

**Document ID:** GH-ZOHO-BILLING-KB  
**Program:** GH Real Estate / Sylvara systems knowledge base  
**Research cutoff:** 2026-07-20  
**Source policy:** Current official Zoho API, Deluge, help, and release documentation only  
**Primary API generation:** Zoho Billing REST API v1  
**Evidence labels:** `DOC-VERIFIED`, `LIVE-METADATA REQUIRED`, `VOLATILE`, `EARLY ACCESS`, `POLICY INPUT REQUIRED`, `RESEARCH INFERENCE`, `DOC-GAP`, `DOC-DRIFT`

> **AI ingestion directive.** Identify the legal entity, Zoho data center, Billing/Books organization, `organization_id`, environment, plan/edition, product owner, OAuth connection and exact endpoint scope before generating code. Zoho Billing's current brand coexists with legacy technical names: the v1 API still uses `ZohoSubscriptions.*` scopes and the header `X-com-zoho-subscriptions-organizationid`. Do not “correct” those identifiers. Never invent product/plan/addon/coupon codes, customer IDs, tax fields, gateway names, price, frequency, trial, proration, dunning, revenue-recognition, or accounting policy. Any subscription, invoice, charge, payment, credit, refund, write-off, or customer communication is a controlled financial/customer action requiring duplicate prevention, approval, reconciliation, and a compensating procedure.

## 1. Product role, evolution, and system boundary

`DOC-VERIFIED` Zoho Billing is the product that evolved from Zoho Subscriptions. Zoho's announcement says it expanded the former subscription product into an end-to-end billing platform for both recurring and one-time sales. Existing Zoho Subscriptions organization data remained intact while the interface/domain changed to Billing; additional capabilities can depend on a Billing plan.

Billing is designed for:

- product, plan, addon, coupon, and price-list catalogs;
- one-time, recurring, usage/metered, project, and hybrid billing;
- customer, contact person, payment-method reference, quote, invoice, subscription, unbilled-charge, payment, payment-link, credit-note and refund workflows;
- hosted payment pages, online/offline subscriptions, trials, renewals, plan/addon/coupon changes, pause/resume/cancel/reactivate;
- proration, dunning/retry/revenue-recovery, customer portal, reporting tags, MRR/ARR/churn and revenue reporting;
- workflows, outgoing webhooks, custom functions, incoming webhook functions, events, and integrations.

Billing does **not** replace CRM's operating relationship/pipeline, Contracts' policy-controlled agreement lifecycle, Sign's signature evidence, Creator's custom operational portal, WorkDrive's controlled documents, Catalyst's integration runtime, or GitHub's sanitized technical implementation.

### 1.1 Relationship to Zoho Books

`DOC-VERIFIED` The current Billing help states that Books and Billing are seamlessly integrated for a shared organization: changes in Books are reflected in Billing and vice versa, and Billing-created customers/transactions appear in Books. A Books user can see Books organizations from Billing and initially gets a free test organization to explore Billing without polluting Books data; joining a Books organization starts read-only until made live.

This means the correct design is not “sync two independent invoice ledgers” when the same Zoho Finance organization is joined. Instead:

- Resolve whether Billing is using a standalone/test organization or the same live Finance organization as Books.
- Keep one approved owner for customer billing lifecycle, invoice creation/numbering, payment application, credits, tax, and accounting posting.
- Treat making a joined organization live as a production activation change.
- `POLICY INPUT REQUIRED` Books remains the full accounting authority for chart of accounts, payables, banking, reconciliation, and financial statements. Billing specializes in billing/subscription automation.

### 1.2 Relationship to Checkout and Payments

| Product | Role | Boundary |
|---|---|---|
| Billing | Billing schedule, product/price/subscription lifecycle, invoices, dunning, customer portal and revenue analytics | Use for complex recurring or hybrid billing |
| Checkout | Reusable declarative hosted payment pages | Simpler collection surface; not a substitute for proration, metering, amendments, and dunning |
| Payments | Processor/gateway API, payment methods, payments, refunds, webhooks and payouts | Processor state must be verified and reconciled to Billing/Books |

`POLICY INPUT REQUIRED` A lease or service contract does not automatically map to a Billing subscription. Legal/accounting owners must define whether Billing is appropriate, the billed unit, start/end/renewal behavior, proration, grace, retry, cancellation, refund, deposit and revenue treatment.

## 2. API root, tenant identity, data centers, and OAuth

### 2.1 Root and organization header

- `DOC-VERIFIED` US root: `https://www.zohoapis.com/billing/v1`.
- `DOC-VERIFIED` Every scoped call requires header `X-com-zoho-subscriptions-organizationid: {organization_id}`.
- Resolve the ID from `GET /organizations` or authenticated Manage Organizations UI. The organization lookup uses `ZohoSubscriptions.settings.READ`.
- `LIVE-METADATA REQUIRED` Maintain legal entity -> Zoho account -> DC -> Billing/Books organization -> `organization_id` -> live/test/read-only state -> base currency -> OAuth connection mapping. Reject any caller-supplied organization selector that conflicts with this registry.

### 2.2 Data-center API hosts

| Data center | Base API prefix |
|---|---|
| United States | `https://www.zohoapis.com/billing/` |
| Europe | `https://www.zohoapis.eu/billing/` |
| India | `https://www.zohoapis.in/billing/` |
| Australia | `https://www.zohoapis.com.au/billing/` |
| Japan | `https://www.zohoapis.jp/billing/` |
| Canada | `https://www.zohoapis.ca/billing/` |
| China | `https://www.zohoapis.com.cn/billing/` |
| Saudi Arabia | `https://www.zohoapis.sa/billing/` |

Accounts hosts documented on the OAuth page include `.com`, `.eu`, `.in`, `.com.au`, `.jp`, and Canadian `accounts.zohocloud.ca`; `VOLATILE` verify the current DC table before implementing consent/token exchange.

### 2.3 OAuth lifecycle

- Register a server-based or controlled self-client in Zoho API Console.
- Authorization: DC-specific `/oauth/v2/auth`; exchange/refresh: `/oauth/v2/token`; revoke: `/oauth/v2/token/revoke`.
- Header: `Authorization: Zoho-oauthtoken {access_token}`.
- Authorization code is documented as valid for 60 seconds. Access tokens generally expire in one hour. `access_type=offline` returns a refresh token.
- Current page says no more than 20 refresh tokens per user; the oldest is removed when exceeded.
- Never store client secrets, tokens, gateway credentials or customer payment details in source, GitHub, WorkDrive documentation, Creator records, logs, or PDFs.

### 2.4 Scopes

The technical scope service name remains `ZohoSubscriptions`.

| Family | Current documented scope pattern |
|---|---|
| Customers | `ZohoSubscriptions.customers.{CREATE|UPDATE|READ|DELETE}` |
| Subscriptions | `ZohoSubscriptions.subscriptions.{CREATE|UPDATE|READ|DELETE}` |
| Invoices/unbilled charges | `ZohoSubscriptions.invoices.{CREATE|UPDATE|READ|DELETE}` |
| Credit notes | `ZohoSubscriptions.creditnotes.{CREATE|READ|DELETE}` plus endpoint-specific actions |
| Products | `ZohoSubscriptions.products.{CREATE|UPDATE|READ|DELETE}` |
| Plans | `ZohoSubscriptions.plans.{CREATE|UPDATE|READ|DELETE}` |
| Addons | `ZohoSubscriptions.addons.{CREATE|UPDATE|READ|DELETE}` |
| Coupons | `ZohoSubscriptions.coupons.{CREATE|UPDATE|READ|DELETE}` |
| Hosted pages | `ZohoSubscriptions.hostedpages.{CREATE|READ}` |
| Payments/payment links | `ZohoSubscriptions.payments.{CREATE|UPDATE|READ|DELETE}` |
| Settings | `ZohoSubscriptions.settings.READ` and endpoint-level settings scopes where documented |
| Events | `ZohoSubscriptions.webhooks.READ` |

`DOC-DRIFT` The OAuth overview's summary is not exhaustive for every newer API family; endpoint pages show additional scopes such as quotes and settings write operations. Always copy the scope printed on the exact endpoint. Use least privilege, separate connections per company/environment, and treat added scope/re-consent as a reviewed access change.

## 3. Protocol, responses, pagination, limits, and uncertain writes

### 3.1 Request/response

- JSON responses generally use `{ "code": 0, "message": "success", "<resource>": ... }`.
- Validate HTTP status and Zoho `code`; don't continue on a nonzero application code.
- IDs are opaque strings, even where examples are numeric.
- Use decimal-safe money handling and exact ISO currency codes. Avoid binary floating-point math.
- Status/action allowed values are endpoint-specific and can change by feature/edition.

### 3.2 Pagination/filtering

- List APIs use `page` and `per_page`, return `page_context`, and are documented as paginated to 200 records by default.
- Iterate based on `has_more_page`; preserve deterministic checkpoints and overlap windows for sync.
- Filters differ by family (status, customer, product/plan, date, search, sort, custom view). Copy exact parameter and allowed value from the current page.
- Events are accessible through the API only for the last 180 days. Persist sanitized event IDs and processing evidence if longer audit is required.

### 3.3 Rate/concurrency limits and documentation ambiguity

The current introduction states:

- Standard plan: 1,000 API requests/day.
- Premium plan: 5,000 API requests/day.
- 100 requests per minute per organization, while the same section also says “A threshold of 30 API requests per minute applies for all the APIs.”
- Concurrent calls: Free 5; paid plans 10 (soft limit).
- HTTP 429 for daily, minute, or concurrent excess; example Zoho codes `45`, `44`, and `1070`.

`DOC-DRIFT / VOLATILE` The 30-versus-100-minute language is internally ambiguous, and plans have expanded since the page's examples. Design to the stricter 30/minute until current tenant/API support confirms otherwise; centralize rate control per organization and limit concurrency.

### 3.4 Idempotency gap

`DOC-GAP` No universal Billing v1 idempotency header is documented in the official pages reviewed. `reference_id`, plan/addon/coupon codes, invoice references, and custom fields help correlation but are not assumed unique unless tenant metadata enforces it.

For any create/charge/refund/action:

1. Create an immutable application operation key.
2. Persist intended legal entity, organization, resource/action, amount/currency and approved input hash in a write ledger.
3. Resolve an existing mapped Billing ID before write.
4. Serialize by customer/subscription/invoice/payment and action class.
5. Do not blindly retry a timed-out `POST`. Reconcile by API reads, event/webhook evidence, and local mappings first.
6. Store returned IDs immediately; re-read by ID and validate critical state.
7. Make emails, charge collection, subscription transitions, credits and refunds separate controlled steps.

## 4. Complete major API resource-family map

### 4.1 Organization and catalog

| Family | Canonical routes | Major operations |
|---|---|---|
| Organizations | `/organizations` | Create/list/update/get; identify independent tenant and base configuration |
| Items | `/items`, `/items/{item_id}` | CRUD, bulk fetch, active/inactive; one-time catalog items |
| Products | `/products`, `/products/{product_id}` | CRUD/status; email-template updates; parent of subscription plans/addons |
| Plans | `/plans`, `/plans/{plan_code}` | CRUD/status/free/non-free; pricing/frequency/trial/setup fee/tax; comments |
| Addons | `/addons`, `/addons/{addon_code}` | CRUD/status; recurring or one-time pricing, brackets, applicable plans; comments |
| Coupons | `/coupons`, `/coupons/{coupon_code}` | CRUD/status; coupon-set actions; discount type/duration/product/plan/addon applicability |
| Price books | `/pricebooks` family | Create/list/get/delete; item and line-item price updates/removal |
| Settings | `/settings/...` | Read taxes, exemptions, authorities and churn preferences |
| Reporting tags | settings reporting-tag routes | Tag/option CRUD/status/default/visibility/reorder |

### 4.2 Customers and payment method references

| Family | Canonical routes | Major operations |
|---|---|---|
| Customers | `/customers`, `/customers/{customer_id}` | CRUD/status; retrieve by CRM reference; transaction list |
| Contact persons | Customer/contact-person routes | CRUD and customer association |
| Cards | Card/customer routes | Retrieve/delete/list active cards; token/reference data only |
| Bank accounts | Bank-account routes | Retrieve stored bank-account reference |

Never store or process raw card/bank credentials through these general business APIs. Use a supported gateway/hosted page/widget and retain opaque IDs/masked fields only.

### 4.3 Sales, billing, subscriptions, and collections

| Family | Exact important routes | Major operations |
|---|---|---|
| Quotes | `/estimates` family | CRUD; sent/accepted/declined; email/export/print/templates/comments |
| Invoices | `POST/GET /invoices`; `PUT/GET/DELETE /invoices/{invoice_id}` | Invoice lifecycle plus custom fields, open/void/email/collect/write-off/address/credits/line items/attachment/cancel write-off |
| Subscriptions | `POST/GET /subscriptions`; `PUT/GET/DELETE /subscriptions/{subscription_id}` | Create/list/update/get/delete; lifecycle/action routes detailed below |
| Unbilled charges | `/unbilledcharges/{id}` family | Retrieve/delete/convert to invoice |
| Payments | `POST/GET /payments`; `PUT/GET/DELETE /payments/{payment_id}` | Record/manage payments received and invoice applications |
| Payment links | `POST/GET /paymentlinks`; `PUT/GET/DELETE /paymentlinks/{payment_id}`; `POST .../cancel` | Generate and manage customer payment links |
| Credit notes | `/creditnotes` family | Create/get/delete; email; void/open; apply credit to invoices |
| Refunds | `POST /creditnotes/{creditnote_id}/refunds`; `POST /payments/{payment_id}/refunds`; `GET /creditnotes/refunds/{refund_id}` | Credit-note or excess-payment refund and retrieval |
| Hosted pages | `/hostedpages` family | Hosted page read/list and server-created checkout flows |

### 4.4 Expenses, projects, events, and extensibility

| Family | Routes | Major operations |
|---|---|---|
| Expenses | `/expenses` | CRUD |
| Recurring expenses | `/recurringexpenses` | CRUD; stop/resume; child/history |
| Projects | `/projects` family | CRUD/status/clone/users/comments/invoices/project tasks |
| Tasks | project/task routes | Bulk/list/CRUD/status/completion/comments/attachments |
| Time entries | `/timeentries` family | Log/list/CRUD; timer start/stop/get |
| Events | `GET /events`, `GET /events/{event_id}` | Event feed, payload, event type, outbound-webhook delivery status; 180-day access |
| Custom modules | settings module/record routes | Define modules/fields/permissions; record CRUD/bulk operations |

`RESEARCH INFERENCE` Billing includes expense and project/time APIs, but this does not make it the approved owner of GH property maintenance, operational projects, payroll, or general accounting. Preserve the app-ownership map.

## 5. Catalog schemas

### 5.1 Items and products

- Items: `name`, `rate`, `description`, `sku`, `product_type`, taxability/tax/exemption and jurisdictional codes, item-tax preferences, `custom_fields` (`customfield_id`, `value`).
- Products: `name`, `description`, notification `email_ids`, `redirect_url`. Products group recurring plans/addons.

`POLICY INPUT REQUIRED` Decide whether a charge is a one-time item, subscription product/plan, addon, usage charge, or external Books item through an approved catalog model. Do not duplicate the same charge across item and plan families.

### 5.2 Plans

Important create fields include `plan_code`, `name`, `recurring_price`, `unit`, `interval`, `interval_unit`, `billing_cycles`, `trial_period`, `setup_fee`, setup-fee account, product ID/type, tax fields, tags/custom fields, and whether setup fee can be charged immediately.

`LIVE-METADATA REQUIRED` Plan codes are durable integration keys only if governance makes them immutable. Price, interval, trial, setup fee, tax, free-plan behavior and plan changes affect customer charges; use versioning and approval, not in-place mutation without impact analysis.

### 5.3 Addons and coupons

- Addons: `addon_code`, name/unit, `pricing_scheme`, `price_brackets[]` (start/end quantity/price), type, interval, product, applicability to all or selected plans, taxes, tags/custom fields.
- Coupons: `coupon_code`, name/description, type, duration, discount basis/value, product, maximum redemption, expiry, plans/addons applicability.
- Current help describes coupon redemption as one-time, forever, or limited cycles; percentage or flat; product applicability; expiry and maximum redemptions. Advanced Coupons and per-customer controls can be `EARLY ACCESS` and one-way to enable.

`POLICY INPUT REQUIRED` Never decide eligibility, discount, free period, concession, late-fee waiver, or renewal pricing from technical capability.

## 6. Customer and transaction schemas

### 6.1 Customers

Important fields include `display_name`, salutation/first/last/email/company, phone/mobile, department/designation/website, billing/shipping address, payment terms, currency code, portal flag, tags/custom fields, notes, templates, and extensive edition-specific GST/VAT/TDS/tax authority/exemption attributes.

Customer creation with a subscription can occur inline through the subscription payload or hosted page. `DOC-VERIFIED` Billing automation help warns that customer-creation workflows/actions do not fire for customers created via hosted payment pages or created along with subscriptions via API. Never assume a generic customer-created workflow completed; explicitly verify downstream requirements.

### 6.2 Invoices

Important fields include customer/contact persons, number/reference, template, dates/terms, currency/exchange, discount/tax/adjustment, custom fields, project, and `invoice_items[]` with product/time/expense linkage, price/rate/quantity/unit/tax and description. Payment gateway options, partial payments, notes/terms, custom subject/body and `send` are supported.

Exact action routes include:

- `POST /invoices/{invoice_id}/converttoopen`
- `POST /invoices/{invoice_id}/void`
- `POST /invoices/{invoice_id}/email`
- `POST /invoices/{invoice_id}/collect`
- `POST /invoices/{invoice_id}/writeoff` and `/cancelwriteoff`
- `POST /invoices/{invoice_id}/credits`
- add/delete pending invoice line items and attachments.

`POLICY INPUT REQUIRED` Collect, void, credit and write-off actions are irreversible/high-risk business events; availability is not authorization.

### 6.3 Payments, links, credits, and refunds

- Payment fields: customer, mode, amount/date/reference/description, invoice allocations, exchange rate, bank charges, tax/account IDs, custom fields.
- Payment links require customer, amount, description and optional expiry; returned object contains link ID/number/URL, amount, customer, status and custom fields.
- Refund API accepts credit-note or payment context and refund amount/details.

`POLICY INPUT REQUIRED` A Billing payment record, gateway payment, Books payment, refund, credit note and processor payout are different evidence. Assign one orchestration owner, use cross-reference IDs, and reconcile amount/currency/state before fulfillment or accounting completion.

## 7. Subscription model and lifecycle

### 7.1 Create/update schema

Subscription create can accept:

- existing `customer_id` or an inline `customer` object with identity/address/tax/custom fields;
- contact person and communication preferences;
- `card_id`/gateway references, `auto_collect`, and payment gateways;
- `starts_at`, `exchange_rate`, place of supply and tax fields;
- `plan` with `plan_code`, price/description, quantity, setup fee/tax, tags and item custom fields;
- `addons[]`, `coupon_code`, billing cycles/trial overrides, exclude trial/setup-fee flags;
- reference/salesperson, invoice/template options, partial payments, account ID, backdated invoice controls.

Do not accept customer-controlled price, tax, plan, coupon, start date, trial, billing cycle or gateway values without server-side allowlisting.

### 7.2 Statuses and dates

Current API docs list subscription statuses including `live`, `trial`, `dunning`, `unpaid`, `non_renewing`, `cancelled`, `creation_failed`, `cancelled_from_dunning`, `expired`, `trial_expired`, and `future`. Date fields include created/activated, current term start/end, last/next billing, expiry, trial start/end, pause/resume/cancel times.

- `auto_collect=true` denotes online recurring collection; false is offline/manual.
- `end_of_term` governs whether eligible changes take effect immediately or at term end.
- Metered billing can hold renewal invoices pending while usage line items finalize.
- Never interpret `dunning`, `pending`, future changes, or an asynchronous bank payment as settled.

### 7.3 Exact lifecycle/action routes

- Cancel/reactivate: `POST /subscriptions/{id}/cancel`, `/reactivate`.
- Scheduled changes: `GET`/`DELETE /subscriptions/{id}/scheduledchanges`.
- Activity: `GET /subscriptions/{id}/recentactivities`.
- One-time addon: `POST /subscriptions/{id}/buyonetimeaddon`.
- Coupon: `POST /subscriptions/{id}/coupons/{coupon_code}`; remove with `DELETE /subscriptions/{id}/coupons`.
- Card: `POST`/`DELETE /subscriptions/{id}/card`.
- Charge: `POST /subscriptions/{id}/charge`.
- Postpone: `POST /subscriptions/{id}/postpone`.
- Auto-collect: `POST /subscriptions/{id}/autocollect`.
- Reference/salesperson/custom fields/notes: subresource action routes.
- Extend cycles: `POST /subscriptions/{id}/extend`.
- Metered billing enable/disable: `POST /subscriptions/{id}/meteredbilling/{enable|disable}`.
- Pause/resume: `POST /subscriptions/{id}/{pause|resume}`.

Each route's current body controls timing/proration and must be verified before use.

### 7.4 Current/volatile features

Official 2026 release notes describe:

- subscriptions for items on certain plans;
- day-based billing frequency as `EARLY ACCESS`;
- renewal payment links for manual/offline renewals;
- regeneration of invoices for usage subscriptions and usage line-item custom fields as `EARLY ACCESS`;
- drawdown/prepaid billing and overage restriction; location price-list association; service-period fields in selected editions.

`VOLATILE` Release notes are discovery signals, not API contracts. Confirm plan, tenant UI, API route/schema, and support availability before design.

## 8. Hosted pages and customer-facing flows

REST hosted-page routes:

- `GET /hostedpages/{hostedpage_id}` and `GET /hostedpages`.
- `POST /hostedpages/newsubscription`.
- `POST /hostedpages/updatesubscription`.
- `POST /hostedpages/updatecard`.
- `POST /hostedpages/buyonetimeaddon`.
- `POST /hostedpages/addpaymentmethod`.
- `POST /hostedpages/invoicepayment`.
- `POST /hostedpages/updatepaymentmethod`.

Payloads can include customer, plan, addon, coupon, redirect URL, gateway, currency/exchange, template, tax, price book, address IDs and custom fields. Returned hosted-page URL is an ephemeral customer flow, not payment/activation proof.

Security rules:

- Create hosted pages server-side with a least-privilege connection.
- Use opaque operation/customer references; minimize PII in URLs/browser state.
- Allowlist plan/addon/coupon/price and redirect URLs.
- Treat browser return as UX only. Verify Billing subscription/invoice/payment state and the processor event server-side.
- Expire/abandon local intent and prevent repeated fulfillment.

## 9. Events, outgoing webhooks, incoming webhooks, and automation

### 9.1 Event feed and outgoing webhooks

`GET /events` and `GET /events/{event_id}` return `event_id`, type/time, payload, and webhook delivery entries with webhook ID/URL/status/last update. Examples include subscription and payment events; event types must be retrieved from the current Event Types catalog. API access is limited to 180 days.

Workflow automation can trigger email alerts, field updates, outgoing webhooks, custom functions and notifications. Build webhook receivers for duplicates, retries and out-of-order events. Re-read the resource before irreversible action.

`DOC-GAP` The reviewed v1 public API documents event reads but not a complete outbound-webhook CRUD/signature API. Configure and verify current webhook authentication/retry behavior in the tenant UI and official automation help; do not invent a signature header.

### 9.2 Incoming webhooks

Billing's “Incoming Webhooks” feature is an externally callable URL that runs a Deluge function inside Billing. Zoho generates OAuth and ZAPI-key URLs; requests expose header, params and body to the function; execution logs are available.

- Treat the URL/key as a secret bearer credential. Official help warns that anyone with the exposed URL can access data.
- Prefer OAuth where supported, rotate/regenerate URLs, restrict caller/egress, validate a second application signature where possible, and reject replay/duplicates.
- Parse into an allowlisted schema; no arbitrary module/action from request input.
- An incoming webhook must not directly perform an unapproved financial write. Enqueue/validate/approve first for high-risk events.

### 9.3 Automation gotchas

- Customer-created actions are not triggered for hosted-page signups or customers created inline with subscriptions through API.
- Date/time, event criteria, immediate/time-based action, and custom-function context maps are host-specific.
- Official help examples can lag current API generations (one current automation example contains a Billing web-app `/api/v3/quotes` URL while the official public API is `/billing/v1`); `DOC-DRIFT`: always use current v1 endpoint docs, not copied legacy snippets.

## 10. Taxes, currencies, revenue, and dunning

### 10.1 Taxes/currency

- Settings APIs expose tax, exemption and authority lists; transaction/customer/catalog schemas contain edition-specific tax fields.
- Organization has a base currency; customers/transactions can use supported currencies and exchange rates.
- `POLICY INPUT REQUIRED` Tax jurisdiction, exemption, withholding, source/place of supply, inclusive/exclusive calculation, rate, exchange source/date, rounding, and accounting treatment come from approved policy.
- Store the IDs and values used on each transaction; do not infer current configuration equals historical treatment.

### 10.2 Dunning, proration, usage, and revenue recognition

Billing help exposes proration, multiple dunning rules, metered/usage billing, unbilled charges, advance/prepaid billing, renewal pricing and revenue recognition. These are powerful policy engines.

Before configuring:

- define retry count/interval, customer communication, final action, pause/cancel/free fallback and invoice disposition;
- define immediate versus term-end plan/addon/quantity changes and proration credit/charge;
- define usage source, cutoff, corrections, late usage and invoice finalization;
- define service period, deferred/recognized revenue and Books posting with finance;
- test timezone, daylight saving, month end/leap day, failed/pending bank methods and backdating.

No AI should create these policies from generic best practice.

## 11. Deluge and API integration patterns

### 11.1 Native Billing tasks

Official Deluge tasks include:

- `zoho.billing.getOrganizations(...)`
- `zoho.billing.getRecords(...)`
- `zoho.billing.retrieve(...)`
- `zoho.billing.create(...)`
- `zoho.billing.update(...)`

Example documented shape: `zoho.billing.update("Subscriptions", organization_id, record_id, values, "billing_connection")`. `LIVE-METADATA REQUIRED` Confirm module name and exact argument order in current task page/editor. Each execution consumes an external/API call; loops multiply usage.

### 11.2 `invokeUrl` for full v1

Use a named OAuth connection for lifecycle actions, hosted pages, refunds, events, or resources not covered by tasks.

```deluge
// Illustrative read-only skeleton. Resolve placeholders from the tenant registry.
headers_map = Map();
headers_map.put("X-com-zoho-subscriptions-organizationid", "<BILLING_ORG_ID>");
response = invokeUrl
[
    url: "https://www.zohoapis.com/billing/v1/subscriptions/<SUBSCRIPTION_ID>"
    type: GET
    headers: headers_map
    connection: "<BILLING_OAUTH_CONNECTION>"
];
if(response.get("code") != 0)
{
    // Fail closed and return a redacted structured error.
}
```

Do not also hard-code an Authorization token when using the connection. Build the root from the DC registry. Never log full customers, invoices, subscriptions, payment methods or webhook bodies.

## 12. GH/Sylvara-safe workflow patterns

### 12.1 Approved customer/subscription provisioning

1. CRM/Creator holds an approved operational/customer event and immutable operation key.
2. Resolve legal entity, joined Billing/Books organization, existing customer mapping, product/plan/addons/coupon, currency/tax, start date, trial/billing cycles and collection mode from approved catalogs.
3. Create/reuse customer with minimum fields. Do not depend on customer-created workflow firing for an inline API customer.
4. In dry run, show proposed first invoice, renewal date, proration/setup fee, tax, gateway, communications and cancellation/dunning behavior.
5. Create subscription once; store customer/subscription/invoice IDs and re-read.
6. Do not mark operational access/occupancy fulfilled until required contract/signature and verified payment conditions are separately satisfied.

### 12.2 Subscription change

- Retrieve current subscription and scheduled changes.
- Calculate/display immediate and term-end effects using Billing preview/current UI where available; no independent AI arithmetic as billing authority.
- Require approval for price, quantity, plan, addon, coupon, cycle, start/renewal, pause/cancel/reactivate, proration or credit.
- Post one action with operation lock; retrieve new state and generated invoice/credit; reconcile Books.
- Compensation is an approved reverse change/credit, not deletion.

### 12.3 Dunning/failure

- Processor pending or Billing dunning is not final failure.
- Consume verified events; re-read subscription/invoice/payment.
- Customer notices and service/tenant consequences must be approved legal/business policy, not hard-coded from status names.
- Preserve attempt/event timeline, communication evidence and human exceptions.

### 12.4 Payment/refund

- Verify processor webhook/signature and API state; match amount/currency/customer/invoice/subscription.
- Deduplicate processor payment/refund ID and Billing action.
- Do not call `/collect` or create a payment record if the gateway integration already records it without confirming behavior.
- Refund requires approved remaining-refundable amount, reason, operator and Books credit/refund treatment; serialize and reconcile after uncertain result.

### 12.5 Multi-company isolation

Separate GH and Sylvara organizations, OAuth clients/connections, products/plans, number series, gateways, bank accounts, taxes and documents when they are distinct legal entities. A common user account does not authorize cross-entity routing. Reject organization/customer/gateway mismatches before the API call.

## 13. Security, observability, and data governance

- Least-privilege Zoho roles and OAuth scopes; MFA; access review; rotate/revoke unused clients/tokens/incoming webhook URLs.
- Secret manager only for OAuth clients/tokens, gateway credentials, incoming URLs/keys and webhook secrets.
- Never store raw card/bank data; use gateway-hosted tokenization and opaque IDs.
- Avoid sensitive PII in custom fields, references, metadata, URLs, logs, events and GitHub fixtures.
- Log operation key, legal entity, environment, organization/resource IDs, endpoint/action, sanitized code/status, attempt, actor/approver, duration and payload hash.
- Monitor 429/concurrency, unknown write outcomes, duplicate blocks, event/webhook lag, `creation_failed`, dunning/unpaid, failed refunds, unmapped customers, scheduled-change drift and Books reconciliation exceptions.
- Retain event data needed for audit before the 180-day API window expires, subject to privacy/retention policy.

## 14. Testing, approvals, deployment, and rollback

Minimum matrix:

- customer reuse/create, inline-customer workflow gap, portal invitation;
- subscription trial/live/future, online/offline, immediate/term-end change, pause/resume/cancel/reactivate;
- setup fee, addon/coupon, tax, currency/exchange, partial payment;
- proration, renewal, usage late/correction, unbilled conversion, dunning/pending/failure;
- hosted-page success/abandon/return tampering;
- duplicate/out-of-order events, invalid webhook/auth, token expiry;
- pagination, 30/100-minute uncertainty, daily/concurrent 429, 5xx and timeout-after-commit;
- full/partial/duplicate refund, Books shared-org posting and reconciliation.

Use the free Billing test organization offered to Books users for exploration, but `LIVE-METADATA REQUIRED`: prove which capabilities/gateways differ from live. Never assume test-org results prove production tax, payment, workflow, roles, number series, or joined-Books behavior.

Every production change must include approved proposed-write set, sanitized tests, focused PR, environment/deployment evidence, canary, kill switch, smoke test, reconciliation, and rollback/compensation. Configuration activation, joining/making an org live, catalog price changes, workflow/webhook changes, and gateway changes are production changes even when no code is deployed.

## 15. Live-metadata checklist

Before implementation, provide sanitized evidence for:

- legal entity, DC, organization ID, test/live/read-only/joined-Books state, plan/edition, base currency/time zone;
- exact OAuth connection and scopes;
- customer mapping and custom fields/validation/unique constraints;
- items/products/plans/addons/coupons/price books, codes/IDs and approved immutability/version rules;
- tax/currency/location/reporting-tag configuration;
- invoice/payment/credit/refund number series, templates, statuses, approvals and gateway behavior;
- subscription/proration/dunning/revenue/usage policy and current feature flags;
- hosted-page templates/redirect allowlist, portal and notification settings;
- workflows/functions/incoming/outgoing webhooks, event types, retry/log evidence;
- Books organization/account/item/tax/payment reconciliation mapping;
- roles, secrets, monitoring, retention and compensating-action owners.

## 16. Official source registry

All links verified 2026-07-20.

### API protocol and identity

- Billing v1 introduction, DCs, organization header, limits: https://www.zoho.com/billing/api/v1/introduction/
- OAuth and scopes: https://www.zoho.com/billing/api/v1/oauth/
- Response: https://www.zoho.com/billing/api/v1/response/
- Errors: https://www.zoho.com/billing/api/v1/errors/
- Pagination: https://www.zoho.com/billing/api/v1/pagination/
- Organizations: https://www.zoho.com/billing/api/v1/organizations/

### Catalog and customers

- Items: https://www.zoho.com/billing/api/v1/items/
- Products: https://www.zoho.com/billing/api/v1/products/
- Plans: https://www.zoho.com/billing/api/v1/plans/
- Addons: https://www.zoho.com/billing/api/v1/addons/
- Coupons: https://www.zoho.com/billing/api/v1/coupons/
- Customers: https://www.zoho.com/billing/api/v1/customers/
- Contact persons: https://www.zoho.com/billing/api/v1/contact-persons/
- Cards: https://www.zoho.com/billing/api/v1/cards/
- Bank account reference: https://www.zoho.com/billing/api/v1/bank-account/
- Price books: https://www.zoho.com/billing/api/v1/pricebooks/
- Reporting tags: https://www.zoho.com/billing/api/v1/reporting-tags/

### Billing and collection resources

- Quotes: https://www.zoho.com/billing/api/v1/quotes/
- Invoices: https://www.zoho.com/billing/api/v1/invoices/
- Subscriptions: https://www.zoho.com/billing/api/v1/subscription/
- Unbilled charges: https://www.zoho.com/billing/api/v1/unbilled-charges/
- Payments: https://www.zoho.com/billing/api/v1/payments/
- Payment links: https://www.zoho.com/billing/api/v1/payment-links/
- Credit notes: https://www.zoho.com/billing/api/v1/credit-notes/
- Refunds: https://www.zoho.com/billing/api/v1/refunds/
- Hosted pages: https://www.zoho.com/billing/api/v1/hosted-pages/
- Events and event types: https://www.zoho.com/billing/api/v1/events/
- Settings/tax lists: https://www.zoho.com/billing/api/v1/settings/
- Custom modules: https://www.zoho.com/billing/api/v1/custom-modules/

### Help, integrations, and first-party product announcements

The community-hosted links in this subsection are Zoho product announcements or comparisons used for product-state context. They are not endpoint contracts; current API and help references control implementation.

- Billing automation/workflows/webhooks/functions (including workflow trigger caveat): https://www.zoho.com/us/billing/help/settings/automation.html
- Incoming webhooks: https://www.zoho.com/us/billing/help/settings/developer-space/incoming-webhooks.html
- Books integration and test organization: https://www.zoho.com/us/billing/help/integrations/zoho-books.html
- Subscription preferences/proration/dunning navigation: https://www.zoho.com/billing/help/
- Plans: https://www.zoho.com/billing/help/product-catalog/subscription-items/plans.html
- Coupons/advanced coupons: https://www.zoho.com/billing/help/product-catalog/subscription-items/coupons.html
- Billing evolution from Zoho Subscriptions: https://help.zoho.com/portal/en/community/topic/zoho-billing-the-all-new-end-to-end-billing-solution-for-smes
- First-party Zoho Books-vs-Billing product comparison: https://help.zoho.com/portal/en/community/topic/zoho-billing-vs-zoho-books-which-one-should-i-choose-html
- February 2026 updates: https://help.zoho.com/portal/en/community/topic/whats-new-in-zoho-billing-february-2026
- May 2026 updates/early access: https://help.zoho.com/portal/en/community/topic/whats-new-in-zoho-billing-may-2026

### Deluge

- Billing tasks index: https://www.zoho.com/deluge/help/billing-tasks.html
- Get organizations: https://www.zoho.com/deluge/help/billing/get-organization.html
- Fetch records: https://www.zoho.com/deluge/help/billing/fetch-records.html
- Fetch record by ID: https://www.zoho.com/deluge/help/billing/fetch-record-by-id.html
- Create record: https://www.zoho.com/deluge/help/billing/create-record.html
- Update record: https://www.zoho.com/deluge/help/billing/update-record.html
- General integration-task wrapper model and `invokeUrl` fallback: https://www.zoho.com/deluge/help/integration-tasks.html
