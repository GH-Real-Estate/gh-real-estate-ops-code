# Zoho Books Master Research Dossier

**Document ID:** GH-ZOHO-BOOKS-KB  
**Program:** GH Real Estate / Sylvara systems knowledge base  
**Research cutoff:** 2026-07-20  
**Source policy:** Current official Zoho API, Deluge, help, and release documentation only  
**Primary API generation:** Zoho Books REST API v3  
**Evidence labels:** `DOC-VERIFIED`, `LIVE-METADATA REQUIRED`, `VOLATILE`, `POLICY INPUT REQUIRED`, `RESEARCH INFERENCE`, `DOC-GAP`

> **AI ingestion directive.** Treat this dossier as an architectural and API navigation source, not as live tenant metadata or accounting advice. Before producing executable code, resolve the legal entity, Zoho data center, Books `organization_id`, connection link name, OAuth scopes, current API page, and live IDs for contacts, accounts, items, taxes, currencies, locations, templates, custom fields, reporting tags, and payment gateways. Never invent field/API names, IDs, account mappings, tax treatment, journal entries, revenue recognition, deposit treatment, rent rules, or write-off policy. Money-changing operations require an approved proposed-write set, duplicate prevention, dry run where possible, human approval, reconciliation, and rollback or compensating procedure.

## 1. System boundary and role

`DOC-VERIFIED` Zoho Books is a full accounting system. The official v3 introduction says its API is intended to perform operations available in the web client. In the GH/Sylvara architecture, Books owns the accounting record: customers/vendors as accounting parties, items used on financial transactions, estimates, sales orders, invoices, payments received, credit notes/refunds, expenses, purchase orders, bills, vendor credits/payments, bank transactions and reconciliation, chart of accounts, journals, fixed assets, opening balances, transaction locks, and financial reporting dimensions.

Books does **not** own the leasing/application pipeline, property/unit operational relationship graph, approved contract policy, signature evidence, controlled document repository, portal workflow, source code, or production secrets. CRM may originate approved operational data, but a Books record becomes the accounting system of record for the financial fact it represents.

`POLICY INPUT REQUIRED` Never infer that an operational event should create an invoice, payment, credit, refund, deposit liability, fee, expense, bill, journal, or write-off. The accounting treatment, posting date, account, tax, location/entity, customer/vendor, item, reporting tags, approval path, and reversal method must come from GH/Sylvara finance and legal requirements.

### 1.1 Books versus Billing, Checkout, and Payments

| Product | Proper role | Boundary rule |
|---|---|---|
| Zoho Books | General ledger and end-to-end accounting, including receivables, payables, banking, reconciliation, taxes, and financial statements | Financial posting authority for GH/Sylvara unless an approved finance design says otherwise |
| Zoho Billing | Billing automation and subscription/customer revenue lifecycle | Do not run a competing invoice/payment ledger without an approved Books–Billing integration and ownership map |
| Zoho Checkout | Declarative hosted payment pages | A collection surface, not the accounting ledger or processor |
| Zoho Payments | Payment processor/gateway, transaction and payout evidence | Processor status is not automatically the Books posting; reconcile processor, gateway fees, refunds, payouts, and Books entries |

`DOC-VERIFIED` Zoho's current comparison describes Billing as specialized billing automation and Books as comprehensive accounting that also includes billing. `POLICY INPUT REQUIRED` Choose one owner for invoice numbering, receivable state, credits, and payment application; never let parallel products independently create the same financial event.

## 2. API identity, data centers, and authentication

### 2.1 Root and tenant selector

- `DOC-VERIFIED` US API root: `https://www.zohoapis.com/books/v3`.
- `DOC-VERIFIED` Every organization is independent and has its own base currency, time zone, language, contacts, reports, and `organization_id`.
- `DOC-VERIFIED` Send `organization_id` as a query parameter on organization-scoped calls. Resolve it with `GET /organizations` using `ZohoBooks.settings.READ`, or from the authenticated admin console.
- `LIVE-METADATA REQUIRED` Maintain an explicit registry: legal entity -> Zoho account -> DC -> Books organization name -> `organization_id` -> base currency -> environment -> connection. Never choose an organization from display name alone.

### 2.2 Data-center hosts

| Data center | API host and prefix |
|---|---|
| United States | `https://www.zohoapis.com/books/` |
| Europe | `https://www.zohoapis.eu/books/` |
| India | `https://www.zohoapis.in/books/` |
| Australia | `https://www.zohoapis.com.au/books/` |
| Japan | `https://www.zohoapis.jp/books/` |
| Canada | `https://www.zohoapis.ca/books/` |
| China | `https://www.zohoapis.com.cn/books/` |
| Saudi Arabia | `https://www.zohoapis.sa/books/` |

`VOLATILE` Confirm the tenant's current DC from the Books web-app URL and current official API introduction. The Zoho Accounts authorization/token host must use the corresponding DC.

### 2.3 OAuth 2.0

- Authorization and token operations use the DC-specific Zoho Accounts endpoints, including `/oauth/v2/auth`, `/oauth/v2/token`, and `/oauth/v2/token/revoke`.
- API header: `Authorization: Zoho-oauthtoken {access_token}`.
- Access tokens are documented as valid for one hour. Offline consent returns a refresh token; refresh tokens remain valid until revoked, subject to Zoho account controls.
- Use server-based authorization-code flow or a controlled self-client only where appropriate. Never put client secrets or refresh/access tokens in browser code, Deluge source, GitHub, PDFs, WorkDrive project documentation, logs, or test fixtures.

### 2.4 Scope model

Scope format is `ZohoBooks.{scope}.{operation}`, where operation is `CREATE`, `READ`, `UPDATE`, `DELETE`, or `ALL`. The official OAuth page documents these principal families:

| Scope family | Resources |
|---|---|
| `contacts` | Customers and vendors |
| `settings` | Organizations, items, users, taxes, currencies, opening balances, and other settings resources |
| `estimates` | Quotes/estimates |
| `invoices` | Invoices and invoice actions |
| `customerpayments` | Payments received |
| `creditnotes` | Customer credits and refunds |
| `projects` | Projects/tasks/time data under supported endpoints |
| `expenses` | Expenses |
| `salesorders` | Sales orders |
| `purchaseorders` | Purchase orders |
| `bills` | Vendor bills |
| `debitnotes` | Vendor credits |
| `vendorpayments` | Payments made |
| `banking` | Bank accounts, statements, transactions, rules, and reconciliation |
| `accountants` | Chart of accounts, journals, and accountant operations |

`DOC-VERIFIED` Endpoint pages display the exact scope for each action. Use the smallest action scopes required; do not rely on broad `ALL` in production. Re-consent is a controlled security change.

## 3. Protocol, response, pagination, limits, and errors

### 3.1 Request and response contract

- REST methods are primarily `GET`, `POST`, `PUT`, and `DELETE`. Action endpoints often use `POST`.
- Typical JSON response: `{ "code": 0, "message": "success", "<resource>": {...} }`. `code` is zero for success and non-zero for an application error.
- Some APIs return PDF or CSV when requested with `Accept` or the documented `accept` parameter.
- Timestamps are documented in ISO-8601 form. Treat time zone and posting date separately; never derive an accounting date from server time without policy.
- Validate both HTTP status and the Zoho `code`. Record Zoho request/correlation data if present, but redact tokens and tenant payloads.

### 3.2 Pagination and filtering

- List APIs use `page` and `per_page` and return `page_context` with `page`, `per_page`, and `has_more_page`.
- Official pagination documentation says list APIs are paginated to 200 items by default. Individual endpoint pages can impose their own maximum; invoice docs explicitly state `per_page` maximum 200.
- Do not stop because a page contains fewer than an assumed size; continue according to `has_more_page`.
- Filters are resource-specific. Common shapes include exact fields, `*_startswith`, `*_contains`, date ranges, `filter_by`, `search_text`, `sort_column`, and custom-view IDs. Copy allowed values from the current endpoint page.
- For syncs, persist a watermark plus immutable Zoho IDs, overlap the time window, paginate deterministically, and reconcile deletes/inactivations. Do not use a display name as a cursor.

### 3.3 Rate limits

`DOC-VERIFIED` Current v3 introduction:

- 100 requests per minute per organization.
- Daily plan totals: Free 1,000; Standard 2,000; Professional 5,000; Premium 10,000; Elite 10,000; Ultimate 10,000.
- Concurrent calls: Free 5; paid plans 10 (documented as a soft limit).
- Exceeding daily, per-minute, or concurrent limits returns HTTP 429. Examples include Zoho codes `45`, `44`, and `1070` respectively.

`VOLATILE` Plans and limits can change. Read the introduction immediately before a capacity design. Centralize throttling per `organization_id`, cap concurrency, and apply bounded exponential backoff with jitter for 429/transient 5xx. Do not blindly retry an ambiguous financial `POST`.

### 3.4 Error handling and idempotency gap

`DOC-GAP` Current official Books API pages reviewed do not document a universal idempotency-key header for financial creates. Therefore:

1. Generate an immutable operation key in the owning workflow before a write.
2. Store it in a sanitized integration write ledger and, only where approved and supported, in a Books reference/custom field.
3. Search or read the mapped Books record before creating.
4. Serialize writes by entity + business event.
5. After timeout, treat the result as unknown. Reconcile Books, webhook history, and the local mapping before retry.
6. Store returned `*_id` immediately and make subsequent processing update/read by ID.
7. Require separate dedupe for payments, credits, refunds, bank categorization, journals, and emails.

`LIVE-METADATA REQUIRED` A `reference_number` or custom field is not automatically unique. Use a Books custom field configured as unique only after confirming the module, field ID/API behavior, and tenant validation; still retain the integration ledger.

## 4. Complete major API resource-family map

The v3 navigation/OpenAPI surface exposes the following families. Collection routes below are canonical examples; action routes and edition-specific operations must be copied from the linked current page.

### 4.1 Tenant, sales, receivables, and customer data

| Family | Canonical route(s) | Major operations and uses |
|---|---|---|
| Organizations | `/organizations` | Create/list/update/get organizations; list accessible orgs; addresses; copy settings; activation/product transitions |
| Contacts | `/contacts`, `/contacts/{contact_id}` | Customer/vendor CRUD; active state; portal/reminders; addresses; statements; comments; attachments; tags; tax info; bank/card references; merge; CRM reference retrieval |
| Contact persons | `/contacts/{contact_id}/contactpersons` and documented contact-person routes | CRUD, primary contact, portal invite, SMS preferences |
| Estimates | `/estimates` | CRUD, send/accept/decline, templates, comments, conversion and approval actions |
| Sales orders | `/salesorders` | CRUD, statuses, email, templates, conversion/linkage to invoices/packages where supported |
| Sales receipts | `/salesreceipts` | Sales-receipt lifecycle and related actions |
| Invoices | `/invoices`, `/invoices/{invoice_id}` | CRUD; draft/sent/void/approval; email/reminders/SMS; payments and credits; attachments; payment links; write-off; signatures; project/estimate conversion; sub-status and edition-specific e-invoice actions |
| Delivery challans | `/deliverychallans` | Delivery-document lifecycle where enabled/edition-supported |
| Recurring invoices | `/recurringinvoices` | CRUD; stop/resume; child invoices; schedules and history |
| Credit notes | `/creditnotes` | CRUD; open/void/approval/email; apply to invoices; refunds; attachments; signatures; edition e-invoice actions |
| Customer debit notes | Documented customer-debit-note family | Customer debit adjustments where enabled; finance approval required |
| Customer payments | `/customerpayments` | Create/list/get/update/delete; apply amounts to invoices; excess-payment refunds; custom fields |
| Retainer invoices | `/retainerinvoices` | Retainer lifecycle, payments, application/refund behavior per current page and accounting policy |

### 4.2 Purchasing, payables, and expenses

| Family | Canonical route(s) | Major operations and uses |
|---|---|---|
| Expenses | `/expenses` | CRUD; billable/customer/project linkage; mileage; receipts and attachments; employees; comments/history |
| Recurring expenses | `/recurringexpenses` | CRUD; stop/resume; child expenses and history |
| Purchase orders | `/purchaseorders` | CRUD; statuses, approvals, email, templates, conversion to bills |
| Bills | `/bills` | CRUD; open/void; approvals; address; payments; applied credits; attachments/comments; PO conversion |
| Recurring bills | `/recurringbills` | CRUD; stop/resume; child bills/history |
| Vendor credits | `/vendorcredits` | Vendor-credit lifecycle, apply/refund actions per endpoint and accounting policy |
| Vendor payments | `/vendorpayments` | Create/list/get/update/delete; apply to bills; excess-payment refunds; remittance email |

### 4.3 Banking and accountant controls

| Family | Canonical route(s) | Major operations and uses |
|---|---|---|
| Bank accounts | `/bankaccounts` | Create/list/get/update/delete/activate/deactivate; statement import; balances/overview/preferences |
| Bank reconciliation | Bank-account reconciliation subroutes | Create/list/get/update/delete; save draft; attach/retrieve/delete reconciliation documents |
| Bank transactions | `/banktransactions` | CRUD; match/unmatch; exclude/restore; categorize/uncategorize as expense, customer/vendor payment, or refund |
| Bank rules | `/bankrules` | CRUD/bulk/reorder; match filters; suggested-rule controls |
| Chart of accounts | `/chartofaccounts` | CRUD; active/inactive; bulk actions; account transactions/balances |
| Registers | `/registers` family | Register transactions, bulk action history, budget-vs-actual and controlled bulk actions |
| Journals | `/journals` | CRUD; publish/reverse; attachments/comments; approvals; recurring journals; credit applications |
| Fixed assets | `/fixedassets` family | Asset/type CRUD; activate/draft/cancel/write-off/sell; history and depreciation forecast |
| Base-currency adjustment | Documented adjustment family | Create/list/get/delete/reevaluate; account/contact details |
| Opening balance | `/settings/openingbalances` family | Create/update/get/delete; account details/transactions; write-off/cancel write-off |
| Transaction locking | `/settings/transactionlocking` family | Update/get/delete locks; period locks; partial-unlock settings |

`POLICY INPUT REQUIRED` Bank matching, categorization, reconciliation, account creation, journals, fixed-asset events, currency adjustments, opening balances, locks, write-offs, and reversals must never be automated from API availability alone.

### 4.4 Catalog, dimensions, configuration, and extensibility

| Family | Canonical route(s) | Major operations and uses |
|---|---|---|
| Items | `/items` | CRUD; active state; portal publication; inventory/service fields; per-item taxes/accounts/custom fields |
| Price lists | `/pricebooks` | CRUD/status; items and bulk fetch |
| Locations | `/locations` | Enable, CRUD, active state, primary location |
| Currencies | `/settings/currencies` | Currency CRUD; exchange rates under `/settings/currencies/{currency_id}/exchangerates` |
| Taxes | `/settings/taxes` | Taxes, tax groups, US/CA authorities, US exemptions; edition-dependent |
| Reporting tags | `/settings/reportingtags` family | Tag/option CRUD/status/default/reorder/visibility; analytics dimensions |
| Users | `/users` | User lifecycle, invite, status, current-user lookup |
| Projects, tasks, time entries | `/projects`, `/projects/{id}/tasks`, `/timeentries` families | Project/member/task/time CRUD, comments, attachments, timers, invoice linkage |
| Custom modules | `/settings/custommodules` and record routes | Define modules/fields and CRUD records; do not use to compete with CRM/Creator ownership |
| CRM integration | `/integration` family | Import Books customer/vendor/item from CRM identifiers using documented integration endpoints |
| Custom views | `/customviews` | Saved filters/columns; do not treat a view as a durable data contract |
| Related lists | `/settings/relatedlists` | External/custom data alongside entity pages |
| Module renaming | Settings module-label routes | Display-label management; API routes/IDs still require metadata verification |
| Workflows/custom triggers/functions/buttons/actions/blueprints | Settings automation families | Configure automation artifacts, histories, failures, deployment/execution where supported |
| Webhooks | `/settings/webhooks` | CRUD; edit metadata; histories; detail; resend and bulk resend |
| Sandbox | `/settings/sandboxes` family | Create/manage sandbox; inspect changes; validate/push; deployment logs; plan/edition dependent |

## 5. Core schemas and field maps

All fields below are official API request fields, but availability, requiredness, allowed values, tax fields, and behavior vary by edition, plan, enabled features, and operation. `LIVE-METADATA REQUIRED` means fetch the current record/settings and inspect the endpoint's current request schema before writing.

### 5.1 Contacts: customers and vendors

Important create/update fields include:

- Identity: `contact_name`, `company_name`, `contact_type` (`customer`/`vendor` where accepted), `customer_sub_type`, `contact_number`, owner/tags.
- Communications: `website`, `language_code`, `phone`, `mobile`, `email` on contact persons, `communication_preference`, portal/SMS/WhatsApp flags.
- Credit/pricing: `credit_limit`, `pricebook_id`, `currency_id`, `payment_terms`, `payment_terms_label`.
- Addresses: `billing_address`, `shipping_address` with attention, address/street2, city, state/state_code, zip, country, fax, phone.
- Contact persons: salutation, first/last name, email, mobile, designation, department, primary flag.
- Templates: invoice, estimate, credit-note, PO, SO, retainer, statement, thank-you, and email template IDs as enabled.
- Accounting/tax: opening balances/location/exchange rate and many edition-specific fields (`tax_treatment`, `tax_regime`, `tax_id`, exemptions, GST/VAT/1099/TDS fields).
- Extension: `custom_fields`, tags, social fields, notes.

`POLICY INPUT REQUIRED` Contact identity is not enough to determine customer/vendor role, legal name, terms, credit limit, currency, tax treatment, portal access, or opening balance. Store CRM<->Books mappings by immutable IDs.

### 5.2 Items

Important fields: `name`, `sku`, `description`, `rate`, `unit`, `product_type`, `item_type`, sales `account_id`, `purchase_account_id`, `inventory_account_id`, `purchase_rate`, vendor, reorder/stock fields, location stock/rates, tax IDs/rules/exemptions, jurisdictional codes, `custom_fields` (`customfield_id` + `value` on current create schema).

`POLICY INPUT REQUIRED` Do not select revenue, expense, inventory, asset, liability, or tax accounts from an item name. Item and account IDs must come from an approved finance-owned catalog.

### 5.3 Invoices

Important request fields:

- Parties and document identity: `customer_id`, `contact_persons`, `invoice_number`, `reference_number`, `template_id`, `date`, `due_date`, `payment_terms`.
- Currency/dimensions: `currency_id`, `exchange_rate`, `location_id`, `salesperson_name`, tags, `custom_fields` (`customfield_id` + `value` in the current schema).
- Totals/tax: document discount and type, inclusive-tax flag, shipping charge, adjustment/reason, tax authority/exemption and edition-specific GST/VAT fields.
- Lines: `line_items[]` with `item_id` or documented free-form attributes, description, rate, quantity, unit, discount, `tax_id`, project/time/expense/bill links, order and jurisdictional codes.
- Collection/display: `payment_options.payment_gateways`, partial-payment flag, notes, terms, custom email subject/body, send/auto-number options.

Important actions include status transitions, approval submission/approval/rejection, email/reminders/SMS, payment-link generation, list payments/credits, apply/delete credits, attachment/document operations, write-off/cancel, signatures, and edition-specific e-invoicing.

`POLICY INPUT REQUIRED` Creating or marking an invoice sent does not prove delivery, payment, or revenue recognition. Do not write off or void automatically without approved reason, authority, and compensating/reconciliation steps.

### 5.4 Payments received and refunds

Payment create fields include `customer_id`, `payment_mode`, `amount`, `date`, `reference_number`, `description`, `account_id`, `exchange_rate`, bank charges, location/tags/custom fields, and `invoices[]` with `invoice_id`, `amount_applied`, and tax withheld where applicable. APIs support excess-payment refunds and retrieving/updating/deleting refund details.

`POLICY INPUT REQUIRED` A processor success, bank deposit, or CRM status does not by itself determine payment date, payment account, amount applied, fees, withholding, exchange rate, or refund account. Reconcile amount, currency, customer, invoice applications, gateway transaction ID, fees, refund, and payout before marking complete.

### 5.5 Credit notes

Credit-note payloads mirror customer/line/tax/currency dimensions. APIs cover draft/open/void and approvals, applying credit to invoices, listing/removing applied credits, refunds, email, documents, digital signatures, and jurisdiction-specific e-invoicing.

`POLICY INPUT REQUIRED` A cancellation is not automatically a credit; a credit is not automatically cash-refunded; a processor refund is not automatically the proper Books credit-note/refund sequence.

### 5.6 Bills, vendor payments, and expenses

- Bills: `vendor_id`, currency/exchange rate, bill/reference number, dates/terms, location, PO/document links, custom fields/tags, and line items with item/account, quantity/rate, tax, project/customer billable context, serials and approvals.
- Vendor payments: vendor, mode, date, amount, paid-through account, references, bill applications, bank charges, exchange rate, tags/custom fields; excess-payment refunds.
- Expenses: expense `account_id`, paid-through account, date/amount, currency/exchange rate, vendor, reference, tax, project/customer/billable flags, location/tags/custom fields, mileage/employee fields, receipt/attachment.

`POLICY INPUT REQUIRED` Vendor, expense account, paid-through account, billable status, project/customer, tax, and posting period are finance inputs. Never derive them solely from memo text or an uploaded receipt.

## 6. Taxes, multi-currency, locations, and reporting dimensions

### 6.1 Taxes

- The API provides taxes and tax groups, plus edition-specific authorities and exemptions.
- Contact, item, and transaction schemas expose different jurisdiction fields. US, Canada, India, Mexico, GCC, EU/VAT and other editions are not interchangeable.
- `LIVE-METADATA REQUIRED` Fetch active tax configuration and allowed values from the tenant and current edition-specific API page.
- `POLICY INPUT REQUIRED` Do not calculate nexus, taxability, exemptions, source/place of supply, withholding, reverse charge, or filing treatment from API documentation.
- Preserve historical transaction evidence. Changing or deleting tax configuration can affect future behavior; use approved effective-date/version procedures.

### 6.2 Currency and exchange rates

- Organization has a base currency. Contacts and transactions may use configured currencies.
- Currency APIs manage configuration; exchange-rate APIs live under `/settings/currencies/{currency_id}/exchangerates`.
- Transaction schemas may accept `currency_id` and `exchange_rate`; behavior depends on resource and organization settings.
- `POLICY INPUT REQUIRED` Do not infer transaction currency, rate source, rate date, rounding, realized/unrealized gain/loss, or base-currency adjustment policy.

### 6.3 Locations and reporting tags

- Locations can represent business locations/branches where enabled. Reporting tags are analytic dimensions with managed options.
- Persist IDs, not labels. Verify mandatory tags/options and visibility conditions.
- `POLICY INPUT REQUIRED` A property, unit, company, cost center, fund, or owner is not automatically a Books location, reporting tag, project, or custom field. Finance must approve the dimensional model.

## 7. Banking, matching, and reconciliation

The API can create/manage bank accounts; import statements; retrieve balances, statements and insights; create/draft/manage reconciliation; match/unmatch; exclude/restore; categorize/uncategorize transactions; and manage bank rules/match filters.

Safe design:

1. Treat bank feeds/statements and payment-processor payouts as external evidence, not automatic classification authority.
2. Match on multiple controls: amount/currency/date window, account, processor payout, customer/vendor, and immutable external reference.
3. Never auto-create a balancing transaction simply because no match exists.
4. Keep unmatched/ambiguous items in an exception queue.
5. Require reviewer identity and evidence for categorization, reconciliation close, and later changes.
6. Reconcile gross payments, fees, refunds, disputes/chargebacks, net payout, and timing separately.
7. Do not store bank credentials, full account numbers, raw statements with sensitive data, or tenant payloads in GitHub.

## 8. Automation, webhooks, sandbox, and audit

### 8.1 Workflows and custom functions

Books supports workflow rules and actions including field updates, email, webhooks, and custom functions; the v3 API also exposes configuration and history resources for workflows, custom triggers/functions/buttons/actions, blueprints, and failures/upcoming actions where available.

`VOLATILE` Exact availability depends on plan/edition and current settings API. Treat automation definitions as deployable configuration: source a sanitized specification, review diffs, test in an approved sandbox or isolated organization, validate push, and retain deployment logs.

### 8.2 Outbound webhooks

`DOC-VERIFIED` `/settings/webhooks` supports create/list/update/get/delete; edit-page metadata; execution histories/detail; resend; and bulk resend. Create fields include entity/events, name/description, method (`POST`, `PUT`, `DELETE`), URL, entity/additional/query/form parameters, custom headers, body format/raw body, a `secret` for signature verification, and optional connection link name.

Receiver rules:

- HTTPS only by GH/Sylvara policy; authenticate and verify the current documented signature scheme. The API documents a secret but the reviewed page does not fully specify an algorithm/header—`DOC-GAP`: obtain current live documentation/test evidence before implementing verification.
- Store raw payload hash, immutable event/dedupe key, entity ID, received time, processing status, and result; redact data.
- Return quickly and process asynchronously. Assume retries and duplicates; make the consumer idempotent.
- Re-read the Books record before irreversible action. A webhook is a notification, not a complete/current record guarantee.
- Use history/resend endpoints for controlled recovery, not as proof the downstream side effect succeeded.

### 8.3 Sandbox and change control

Current v3 settings navigation exposes sandbox management, production/sandbox change lists, validate/push, deployment logs, activation, rebuild, and review markers. `VOLATILE` Verify that the GH/Sylvara plan and feature set expose these APIs. Never treat a sandbox push as production smoke-test evidence.

## 9. Deluge and integration patterns

### 9.1 Native Books tasks

Official Deluge Books tasks include:

- `zoho.books.getOrganizations(...)`
- `zoho.books.createRecord(module, organization_id, data_map, connection)`
- `zoho.books.updateRecord(module, organization_id, record_id, data_map, connection)`
- record list and record-by-ID tasks
- template retrieval
- `zoho.books.markStatus(...)`

`DOC-VERIFIED` Each execution consumes an external/API call in the host's applicable limits. New tasks require an OAuth connection with correct scopes. Module spellings, argument order, supported actions, and response wrappers must be copied from current Deluge task documentation/editor autocomplete.

### 9.2 When to use `invokeUrl`

Native tasks wrap a selected subset of the REST API. Use `invokeUrl` with a named OAuth connection for unsupported action, banking, settings, webhook, sandbox, or specialized endpoints. Build the DC-specific root from the tenant registry; append `organization_id`; send JSON; and validate HTTP plus `code`.

```deluge
// Illustrative skeleton only. Resolve all placeholders from approved metadata.
org_id = "<BOOKS_ORGANIZATION_ID>";
invoice_id = "<BOOKS_INVOICE_ID>";
response = invokeUrl
[
    url: "https://www.zohoapis.com/books/v3/invoices/" + invoice_id + "?organization_id=" + org_id
    type: GET
    connection: "<BOOKS_OAUTH_CONNECTION>"
];
if(response.get("code") != 0)
{
    // Return a redacted structured error; do not continue to a write.
}
```

Never hard-code an OAuth token in `headers` when a connection can manage it. Never log response payloads containing tenant, bank, contact, or financial data.

### 9.3 Controlled create pattern

1. Resolve legal entity and organization mapping.
2. Validate approved business event and proposed write.
3. Resolve CRM/customer/vendor/item/account/tax/currency/location/tag mappings by immutable IDs.
4. Check the integration write ledger and Books for an existing mapping.
5. Construct payload from allowlisted fields; reject unknown keys.
6. In dry run, calculate/display payload and affected records without calling write endpoint.
7. With approval, make one create call; persist returned Books ID and response code.
8. Re-read by ID and compare critical fields.
9. Reconcile downstream status separately; do not chain an email/payment/refund until the prior state is verified.

## 10. GH/Sylvara-safe workflow patterns

### 10.1 Approved CRM party to Books contact

- Trigger only from an approved CRM lifecycle state, not arbitrary lead creation.
- Resolve existing CRM<->Books mapping first; then search by approved unique Books custom field if configured.
- Create the minimum accounting contact fields. Finance supplies type, currency, terms, tax, templates, and portal access.
- Store Books `contact_id` back in the approved CRM integration field and the technical mapping ledger.
- Never copy sensitive application/tenant data that Books does not need.

### 10.2 Approved charge to invoice

- The charge catalog maps approved business-event code -> Books organization/customer/item/account/tax/currency/location/tags/template and approval class.
- Draft first when supported. Human-review customer, dates, lines, amount, tax, terms, references, and delivery recipients.
- Transition/send only through an approved action. Marking `sent` is a status action; it does not itself prove email delivery or customer receipt.
- Reconcile payments and credits by IDs and amounts; never infer paid from CRM stage.

### 10.3 Processor payment/refund to Books

- Ingest verified processor webhook and retrieve current processor object.
- Deduplicate by processor account + payment/refund ID + event/action.
- Match the Books customer/invoice and approved clearing/bank account.
- Record/apply the payment once; separately reconcile fee and payout.
- For refund, determine approved credit-note/refund/accounting sequence; never call both processor refund and Books cash refund without a single orchestration owner.

### 10.4 Deposit or tenant money

`POLICY INPUT REQUIRED` No API design may determine whether funds are income, liability, escrow/trust, refundable deposit, advance, retainer, or other treatment. Require jurisdiction/legal/accounting handoff, dedicated account mappings, restricted roles, reconciliation, and auditable refund/application process.

## 11. Security, privacy, and observability

- Separate GH and Sylvara organizations/connections/secrets where they are distinct legal entities. Never route from a user-supplied organization ID.
- Least-privilege OAuth and Zoho roles; MFA for admins; periodic access review.
- Secret manager for OAuth clients/tokens, webhook secrets, gateway credentials, and bank-feed credentials.
- Allowlist egress host/DC; validate redirects; TLS; no secrets or PII in URLs.
- Log operation key, environment, legal entity, organization ID, endpoint class, object IDs, sanitized status/code, duration, attempt, actor/approver, and payload hash—not raw payloads.
- Mask contact data, bank data, tax IDs, documents, invoices, and payment details in tests/logs/GitHub.
- Use sanitized deterministic fixtures. Never clone live tenant data into a developer repository.
- Monitor rate-limit headroom, unknown outcomes, duplicate blocks, webhook lag/failures, unmapped IDs, reconciliation exceptions, and privilege/configuration drift.

## 12. Testing, approval, deployment, and rollback

For every financial integration change:

1. Name requirement owner, source of truth, legal entity, accounting/legal approver, and affected Books organization.
2. Capture current API/DC/scopes and live metadata snapshots with no sensitive data.
3. Define data contract, allowed fields, immutable operation key, duplicate check, failure states, reconciliation, and compensating action.
4. Use a short-lived branch and sanitized fixtures; unit-test transforms, decimal/currency handling, time zones, pagination, 429/5xx, timeout-after-commit, and duplicate delivery.
5. Exercise read-only calls and approved sandbox/isolation. Use the Books sandbox API only if verified available.
6. Produce proposed-write set: current state, proposed state, records/users, immediate effect, reversal, and approval.
7. Deploy separately after merge; confirm environment and version.
8. Smoke test with approved records; re-read and reconcile.
9. Record PR, merge commit, deploy version, operator, test evidence, smoke result, limitations, and rollback/compensation status.

Rollback is normally a controlled compensating financial transaction or approved status reversal—not record deletion. Deletions, voids, write-offs, credit deletion, bank recategorization, journal reversal, and transaction unlocking require explicit authority.

## 13. Live-metadata checklist

Before Codex/ChatGPT writes Books code, supply a sanitized snapshot of:

- legal entity, DC, `organization_id`, environment, plan/edition, base currency/time zone;
- OAuth connection link name and exact scopes (never secret values);
- active contacts and CRM mapping field IDs/API behavior;
- chart-of-account IDs/types and approved account-purpose map;
- item IDs and approved sales/purchase/inventory/tax mappings;
- currencies/exchange-rate policy, locations/branches, reporting tags/options;
- tax edition, active tax IDs/groups/authorities/exemptions and approved decision table;
- invoice/bill/payment/credit templates, number series, statuses, approvals, custom fields and validation;
- bank/clearing accounts, gateway/processor mappings, reconciliation procedure;
- enabled workflows, webhooks, functions, retry behavior, sandbox availability;
- roles/permissions, retention, monitoring, and rollback owner.

## 14. Official source registry

All links verified 2026-07-20. Pages are volatile; prefer the current OpenAPI download and endpoint-level page at implementation time.

### Core protocol

- Zoho Books v3 introduction, organization ID, DCs, rate/concurrency limits: https://www.zoho.com/books/api/v3/introduction/
- OAuth and scopes: https://www.zoho.com/books/api/v3/oauth/
- HTTP methods: https://www.zoho.com/books/api/v3/http-methods/
- Response format: https://www.zoho.com/books/api/v3/response/
- Errors: https://www.zoho.com/books/api/v3/errors/
- Pagination: https://www.zoho.com/books/api/v3/pagination/
- Organizations: https://www.zoho.com/books/api/v3/organizations/

### Sales and receivables

- Contacts: https://www.zoho.com/books/api/v3/contacts/
- Contact persons: https://www.zoho.com/books/api/v3/contact-persons/
- Estimates: https://www.zoho.com/books/api/v3/estimates/
- Sales orders: https://www.zoho.com/books/api/v3/sales-order/
- Sales receipts: https://www.zoho.com/books/api/v3/sales-receipt/
- Invoices: https://www.zoho.com/books/api/v3/invoices/
- Recurring invoices: https://www.zoho.com/books/api/v3/recurring-invoices/
- Credit notes: https://www.zoho.com/books/api/v3/credit-notes/
- Customer payments: https://www.zoho.com/books/api/v3/customer-payments/
- Retainer invoices: https://www.zoho.com/books/api/v3/retainer-invoices/

### Purchasing and accounting

- Expenses: https://www.zoho.com/books/api/v3/expenses/
- Purchase orders: https://www.zoho.com/books/api/v3/purchase-order/
- Bills: https://www.zoho.com/books/api/v3/bills/
- Vendor credits: https://www.zoho.com/books/api/v3/vendor-credits/
- Vendor payments: https://www.zoho.com/books/api/v3/vendor-payments/
- Bank accounts and reconciliation: https://www.zoho.com/books/api/v3/bank-accounts/
- Bank transactions: https://www.zoho.com/books/api/v3/bank-transactions/
- Bank rules: https://www.zoho.com/books/api/v3/bank-rules/
- Chart of accounts: https://www.zoho.com/books/api/v3/chart-of-accounts/
- Journals: https://www.zoho.com/books/api/v3/journals/
- Fixed assets: https://www.zoho.com/books/api/v3/fixed-assets/
- Transaction locking: https://www.zoho.com/books/api/v3/transaction-locking/

### Catalog, dimensions, and automation

- Items: https://www.zoho.com/books/api/v3/items/
- Price lists: https://www.zoho.com/books/api/v3/pricelists/
- Locations: https://www.zoho.com/books/api/v3/locations/
- Currencies/exchange rates: https://www.zoho.com/books/api/v3/currency/
- Taxes: https://www.zoho.com/books/api/v3/taxes/
- Reporting tags: https://www.zoho.com/books/api/v3/reporting-tags/
- Projects: https://www.zoho.com/books/api/v3/projects/
- Custom fields/settings navigation: https://www.zoho.com/books/api/v3/custom-fields/
- Workflows: https://www.zoho.com/books/api/v3/workflows/
- Webhooks and execution history: https://www.zoho.com/books/api/v3/webhooks/
- Custom functions: https://www.zoho.com/books/api/v3/custom-functions/
- Sandbox: https://www.zoho.com/books/api/v3/sandbox/
- CRM integration endpoints: https://www.zoho.com/books/api/v3/integration/

### Deluge and product boundary

- Zoho Books Deluge tasks index: https://www.zoho.com/deluge/help/books-tasks.html
- Create record task: https://www.zoho.com/deluge/help/books/create-record.html
- Fetch records task: https://www.zoho.com/deluge/help/books/fetch-records.html
- Fetch record by ID: https://www.zoho.com/deluge/help/books/fetch-record-by-id.html
- Update record task: https://www.zoho.com/deluge/help/books/update-record.html
- Mark status task: https://www.zoho.com/deluge/help/books/mark-status.html
- First-party Zoho Books-vs-Billing product comparison (context only; API/help references control implementation): https://help.zoho.com/portal/en/community/topic/zoho-billing-vs-zoho-books-which-one-should-i-choose-html
