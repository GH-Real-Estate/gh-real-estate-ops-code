# Zoho Sites Engineering and Automation Knowledge Base

**Document ID:** GH-ZOHO-SITES-KB  
**Program:** GH Real Estate / Sylvara systems knowledge base  
**Research cutoff:** 2026-07-20  
**Primary audience:** ChatGPT, Codex, web architects, administrators, security reviewers, and maintainers  
**Source policy:** Official Zoho Sites help/pricing documentation and the supplied GH system maps  
**Evidence labels:** `DOC-VERIFIED`, `LIVE-METADATA REQUIRED`, `TENANT-SPECIFIC`, `VOLATILE`, `GH-POLICY`, `DESIGN RECOMMENDATION`, `DOC-GAP`, `DEPRECATED/LEGACY`

> **AI ingestion directive.** Zoho Sites is the public website, controlled content-publishing surface, form/embed host, and optional member-content shell. It is not CRM, Creator, Contracts, Sign, Books, WorkDrive, or a general backend. No supported public REST API for site/page CRUD or deployment was found in the official public material reviewed as of 2026-07-20; never invent `/sites`, `/pages`, or private builder endpoints. Supported programmability is Dynamic Content (Face views, Deluge functions, stylesheets, RequireJS JavaScript, `$DX` calls), Connections, header/footer code, CSS, forms, embeds, member portal/access controls, and the builder's publish/version functions. Server-side authorization must protect every private record; hiding a page, client-side JavaScript, an opaque URL, or a cached view is not authorization.

## 1. Retrieval contract for AI agents

### 1.1 Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `DOC-VERIFIED` | Supported by an official source in the registry | Recheck plan/tenant UI before a production change |
| `LIVE-METADATA REQUIRED` | Site, page, form, Dynamic Content, connection, member/group, domain, or integration value is tenant generated | Retrieve the exact live value; never infer from label |
| `TENANT-SPECIFIC` | Depends on plan, data center, site, domain, theme, member auth, cache, or integration | Resolve and test in target site |
| `VOLATILE` | Page/member/form/storage/bandwidth/function/invoke/email quota or plan capability | Verify current pricing/account immediately before design |
| `GH-POLICY` | Constraint from supplied GH architecture and change-control material | Follow until an approved change supersedes it |
| `DESIGN RECOMMENDATION` | Defensive web/security/architecture guidance | Validate with owners and tenant behavior |
| `DOC-GAP` | No supported official interface or universal contract was identified | Do not reverse engineer or guess |
| `DEPRECATED/LEGACY` | Official material indicates discontinued or incompatible behavior | Do not start new designs on it; plan migration |

### 1.2 Non-negotiable rules

1. Public Sites pages accept only public/approved content and minimum intake data. Tenant/applicant documents, ledgers, signed agreements, access codes, internal notes, and raw system IDs stay behind authorized systems.
2. Never place OAuth tokens, connection credentials, API keys, webhook secrets, PII, or signing/payment URLs in header/footer JavaScript, dynamic-content client code, HTML, GitHub, analytics, or page source.
3. Dynamic Content views that depend on `user` or `request_object` must have caching disabled and must authorize the resource server-side on every request.
4. URL/form/cookie/header data is untrusted. Validate type, length, allowlist, encoding, authorization, CSRF, and abuse controls before calls or writes.
5. Public inquiry intake creates a CRM Lead under the GH boundary. It does not directly create a Contact, tenant, lease, invoice, portal user, or WorkDrive share.
6. Publish is a production deployment. Preserve review, page/version evidence, link/form/SEO/security tests, rollback/unpublish plan, and post-publish verification.

## 2. System boundary and selection rule

`GH-POLICY` Sites owns the public website and approved portal entry points. Creator is the preferred tenant operational portal; CRM owns relationships/pipeline; WorkDrive owns controlled documents; Contracts/Sign own agreements/evidence; Books/Billing own money.

| Requirement | Preferred system | Sites role |
|---|---|---|
| Public brand, property/service information, public SEO pages | Sites | Author/publish approved content |
| Public inquiry/application-start form | Sites + CRM/Zoho Forms/Creator | Host form/entry; validated backend creates Lead/intake record |
| Booking widget | Zoho Bookings | Embed approved booking surface |
| Tenant/applicant workflow, authenticated records, maintenance | Creator | Sites may link or provide member-content shell, not own state |
| Controlled document download | WorkDrive/authorized backend | Do not publish raw link/ID publicly |
| E-signature | Sign/Contracts | Launch approved protected workflow, never expose tokens statically |
| Payment | Checkout/Billing/Payments | Embed/link hosted PCI-aware experience; Sites is not payment authority |
| Full application backend/API | Creator/Catalyst/service | Sites Dynamic Content is suited to bounded presentation/integration logic |

### 2.1 Public REST API gap

`DOC-GAP` The official Sites help, Dynamic Content, integrations, and product material reviewed did not document a supported public REST API for programmatic site, page, theme, form, member, domain, or publish CRUD. Do not:

- invent `https://sites.zoho.../api/v1/pages` or similar paths;
- automate undocumented builder network calls/cookies;
- screen-scrape the authenticated builder;
- treat a Dynamic Content function URL as a site-management API;
- assume Zoho Sites uses CRM/Creator API scopes.

If Zoho publishes an API later, add it only after official endpoint/scope/DC/auth/rate-limit verification and controlled testing. Until then, site changes are governed builder/configuration changes, while business automation uses documented integrations and Dynamic Content.

## 3. Plans, editions, and quotas

`VOLATILE` The public pricing page reviewed at the cutoff lists Starter and Pro with plan-dependent pages, storage, bandwidth, forms, upload size, galleries, contributors, menus, page versions, member portal, access control, Dynamic Content and publishing capabilities.

The snapshot advertises examples:

| Capability | Starter example | Pro example |
|---|---:|---:|
| Pages | 5 | 50 |
| Storage | 500 MB | 100 GB |
| Bandwidth/month | 10 GB | Unmetered |
| Forms | 5 | 50 |
| Form file upload | 10 MB | 100 MB |
| Galleries | plan-limited | 200 |
| Contributors | plan-limited | 3 |
| Menus | plan-limited | 5 |

Current Pro Dynamic Content quotas shown on pricing include approximately 10 email sends/day, 200 `invokeUrl` calls/day, and 1,000 function executions/month. A Dynamic Content add-on is shown increasing them to about 500 emails/day, 5,000 `invokeUrl` calls/day, and 50,000 function executions/month. A member-portal add-on is shown at 1,000 members, while base portal membership can be much smaller.

These are pricing snapshots, not constants. Verify the site's current plan/add-ons, usage meters, region, and whether limits are per site/account/function before architecture. Design graceful degradation and alerts before quota exhaustion.

## 4. Sites programmability model

### 4.1 Supported layers

| Layer | Technology | Intended use | Security boundary |
|---|---|---|---|
| Builder/page elements | Zoho Sites UI | Static content/layout, forms, embeds | Published public/member content |
| Dynamic Content view | Face template + HTML | Server-rendered dynamic presentation | Must authorize and control cache |
| Dynamic Content function | Deluge/Dynamic Runtime Environment | Server-side data/service calls and transformations | Connections and function logic protect credentials/data |
| Dynamic Content style | `style.css` | Scoped presentation | No secrets/data logic |
| Dynamic Content client | RequireJS `main.js`, `$DX` | Interaction and view/function calls | Browser is untrusted; no secrets/authorization |
| Header/footer code | HTML/JavaScript | Approved analytics, tags, site-wide scripts | Executes across pages; high blast radius |
| Custom CSS | Sites CSS editor | Theme/layout adjustment | Test accessibility/responsiveness |
| Native/embed integrations | CRM forms, Zoho Forms, Bookings, etc. | Supported specialized UX/data capture | Owning app controls business state |

### 4.2 Dynamic Content composition

Official help defines four components:

1. **Functions** — Deluge functions that call Zoho or external services, including through `invokeUrl`/Connections.
2. **Views** — Face templates that call functions and render HTML.
3. **Stylesheets** — CSS in `style.css`.
4. **JavaScript** — `main.js`, loaded dynamically through RequireJS and following the module/closure model.

The view is not a trusted database, and client JavaScript is not a secret-bearing backend.

## 5. Dynamic Content server functions and Connections

### 5.1 Function invocation

Face views invoke a function with:

```text
{% records = functions.execute("<function_name>", param1, param2) %}
```

The function name is the required first argument. Functions can call supported Deluge integration tasks or `invokeUrl`, subject to current Sites/Deluge/target API limits and the configured Connection.

Safe function sequence:

1. validate parameter presence/type/length/format;
2. resolve authenticated `user` and approved group/role, when private;
3. map public opaque reference to an authorized internal record server-side;
4. authorize action/resource/fields;
5. call the owning API with least-privilege Connection;
6. allowlist the returned fields;
7. HTML/JSON encode for output context;
8. avoid sensitive logging and return generic errors.

### 5.2 Connections

Official Sites Connections support default and custom services, including OAuth and other custom authentication. The documented link-name rules are lower-case start, lower-case letters/numbers/underscores, and up to 50 characters. OAuth scope delimiters can be comma, space, or plus depending on service configuration.

Maintain a sanitized connection registry:

```text
connection_link_name | environment/site | service/DC | purpose
scopes | owner | authorized principal | rotation/revoke date | dependent functions
```

Never infer a connection name from code examples. Never put client secrets/tokens in Deluge source, Face, JavaScript, GitHub, or PDF. Test expiration/revocation and owner deactivation.

### 5.3 API calls to other Zoho products

For CRM/Creator/Bookings/Books/WorkDrive/Sign/Contracts/Catalyst, use the target product's official endpoint, OAuth/DC, metadata, limits, and ownership rules. A Sites Connection is authentication plumbing; it does not normalize target APIs or grant authority. Validate live IDs/API names and preserve target idempotency keys.

## 6. Face views, request/user objects, response controls, and caching

### 6.1 Available objects/functions

Official Dynamic Content help documents:

| Object/function | Documented values/use |
|---|---|
| `user` | `display_name`, `email_address`, `groups` for the logged-in member |
| `request_object` | `domain_name`, `uri`, `parameters`, `headers`, `cookies` |
| `functions.execute(...)` | Runs a Dynamic Content function |
| `response_object.setStatus(code)` | Sets valid HTTP response status |
| `response_object.setCookie(name,value,path,max_age)` | Sets a response cookie |

`user.groups` contains display names, which are configuration labels and can change. If authorization depends on a group, maintain an approved exact group registry and fail closed on missing/unknown/multiple ambiguous state. Do not return the user's email or groups to public HTML unless necessary and approved.

### 6.2 Cache rule

`DOC-VERIFIED` Views are cached by default. Official help explicitly advises disabling cache for user- or request-specific views; `user` and `request_object` behavior will not work correctly with cache enabled.

For any tenant/applicant/vendor/private view:

- disable Dynamic Content cache;
- set appropriate response/cache headers where supported;
- authorize every request server-side;
- never embed PII in page source, shared caches, static assets, or analytics;
- test logged-in A -> log-out -> logged-in B on the same browser/device and across groups;
- fail closed if user context is missing.

Public catalog content may be cacheable only if it contains no user/request-specific data and staleness is acceptable.

### 6.3 Safe Face pattern

```text
{% if user %}
  {% result = functions.execute("authorized_summary", request_object.parameters.ref) %}
  {% if result.allowed %}
    <!-- Render only allowlisted, encoded fields -->
  {% else %}
    {% response_object.setStatus(403) %}
  {% endif %}
{% else %}
  {% response_object.setStatus(401) %}
{% endif %}
```

This is a design skeleton, not tested production syntax for every return type. Authorization belongs inside `authorized_summary` too; template branching alone is insufficient.

## 7. Dynamic Content client API

Official help documents `$DX.get` and `$DX.post`. The request object accepts:

| Property | Purpose |
|---|---|
| `url` | Dynamic Content view/function URL |
| `params` | JSON parameters sent to the view |
| `handler` | success callback with XHR as `this` |
| `headers` | request headers |
| `args` | JSON arguments passed to the handler |

Supported URL patterns shown in official examples include:

```text
/dcapp/<dc_name>/<view_name>
/dcapp/<dc_name>/function/<function_name>
```

`main.js` should use a RequireJS `define(...)` module. The Dynamic Content root exposes information such as `data-dc-name` and home page used by the documented `init(context, params)` pattern.

### 7.1 Declarative view navigation

Face/HTML can use `dc-*` attributes:

| Attribute | Meaning |
|---|---|
| `dc-container` | Named target container |
| `dc-bind-click` | Bind default or named callback |
| `dc-view` | View loaded on click |
| `dc-target` | Target container name |
| `dc-param-<name>` | Parameter sent and available under `request_object.parameters` |

All client parameters remain attacker-controlled even if generated from a prior server response.

### 7.2 Client-side rules

- Never place tokens/secrets/credentials in JavaScript, DOM, local storage, URLs, or headers generated from static code.
- Use same-origin documented Dynamic Content routes and server-side Connections.
- Protect state-changing `$DX.post` functions with authenticated authorization, origin/CSRF strategy available to the platform, idempotency key, validation, and rate/abuse controls.
- Do not inject `responseText` containing untrusted HTML without server-side allowlisting/encoding.
- Handle non-2xx, timeout, network failure, unauthorized, quota exhaustion, and retry UI explicitly.
- Retry only idempotent reads automatically; a POST retry requires operation-key reconciliation.

## 8. Forms and intake integrations

### 8.1 CRM webforms

Official Sites integration supports embedding Zoho CRM webforms for Web-to-Lead, Web-to-Contact, and Web-to-Case after the CRM form is created.

`GH-POLICY` Public property/rental inquiry must use Web-to-Lead or an approved intake service that creates `Leads`. Do not select Web-to-Contact merely because it is available. Contacts represent qualified/approved people under the current architecture.

Controls:

- retrieve current CRM form/module/field API mapping and layout/required rules;
- use approved consent/source/campaign/property reference fields;
- CAPTCHA/spam trap, server validation, rate/velocity controls, duplicate policy;
- minimize fields; do not collect SSN, banking, IDs, health/disability detail, full application documents, or credentials in a public lead form;
- confirm lead creation through CRM API/reconciliation, not a thank-you screen.

### 8.2 Zoho Forms

Official integration embeds a published Zoho Form. Zoho warns not to collect passwords or CVV. Use Forms/Creator when richer intake, conditional logic, workflow, upload quarantine, or approvals are needed. Form publication, permissions, owning organization, data residency, integrations, and notification recipients are `TENANT-SPECIFIC`.

### 8.3 Native Sites forms

Native Sites forms store submissions in the Sites forms module and can perform documented submission outcomes such as a thank-you message, redirect to page/URL, file download, or blog action. These presentation outcomes do not prove a downstream CRM/Creator write. Define data owner, export/backup, notification, spam, access, retention, deletion, and reconciliation.

### 8.4 Legacy form migration

`DEPRECATED/LEGACY` Official migration help says the old Sites form version is discontinued/incompatible with the new form version. The new version may lack prior elements/features such as Notes, Formula, Auto Number, Deluge actions, and No Duplicate. Old forms can continue receiving submissions while customization is disabled/incompatible.

Inventory every old form immediately. Do not assume visual presence means maintainability. Export/retain records securely, rebuild missing logic in a supported owner such as Zoho Forms/Creator/CRM, test field/consent/redirect/integration behavior, and replace embeds under change control.

## 9. Member portal, access control, and contributors

### 9.1 Member portal

Paid Sites plans can support member sign-up/invitation, restricted pages/files, groups, and a default portal or SAML sign-in. Current social-login help documents Facebook and Google. Availability and member counts are `VOLATILE`.

The portal is suitable for controlled content access, but the current GH architecture prefers Creator for tenant operational workflows. Sites membership must not become the authoritative tenant/contact record.

Controls:

- establish invite/self-signup policy, identity verification, group assignment, approval, suspension, deletion, and support ownership;
- restrict pages/files by explicit member/group access and test negative cases;
- require SAML configuration and claims/group mapping review if used;
- never trust `user.email_address` alone to authorize a CRM/WorkDrive record; resolve a server-side membership-to-record mapping;
- revalidate access on lease/relationship termination.

### 9.2 CRM member sync hazard

Official member sync can create/synchronize new signups into CRM Contacts or Leads. `GH-POLICY` Configure Lead destination for unqualified public signups, or disable sync and use an approved intake flow. Do not let a website signup silently create a Contact, tenant, portal entitlement, lease party, or marketing consent.

### 9.3 Access modes and contributors

Official access controls include organization-public, organization-private, public, and member/group-restricted content. Contributor roles include Guest, Author, Admin, and Developer, with page-level editing controls.

- Separate content author, developer, administrator, domain/DNS owner, analytics owner, and publisher/approver where possible.
- Limit header/footer code and Dynamic Content/connection access to developers/admins.
- Review contributors after staff/vendor changes.
- Password protection is a supplemental control, not a substitute for member identity and resource authorization.

## 10. Domains, SSL, DNS, and data centers

Official domain mapping uses a verification TXT record and a `www` CNAME pointed to the appropriate Zoho Sites host. Examples are data-center specific, including forms such as `zhs.zohosites.com`, `.eu`, `.in`, `.au`, `.jp`, `.ca`, `.sa`, and `.com.cn`. Copy the exact target displayed for the site's DC; do not reuse a US record.

Official root-domain help notes the root/apex cannot be made primary directly in the same way and describes forwarding/third-party DNS approaches such as Cloudflare. Validate HTTPS for apex and `www`, redirect chains, canonical host, HSTS/certificate renewal, email DNS separation, and outage/rollback.

DNS change packet:

```text
domain | owner/registrar/DNS provider | Sites DC/site
current TXT/CNAME/A/forwarding | proposed records | TTL
verification token (controlled) | certificate status
canonical/redirect policy | rollback records | test evidence
```

Never delete unrelated MX, SPF, DKIM, DMARC, verification, or service records while editing Sites DNS.

## 11. Header/footer code, JavaScript, CSS, analytics, and embeds

Header/footer code executes widely and can access/rendered page data. Treat it like privileged production code:

- approved source/vendor, integrity/version and privacy/legal review;
- minimum third-party trackers; consent behavior and data-transfer inventory;
- no secrets, internal IDs, portal data, or sensitive query-string capture;
- avoid `document.write`, unsafe `innerHTML`, dynamic script URLs, and global namespace collision;
- Content Security Policy and subresource-integrity options should be assessed, subject to Sites capabilities;
- test mobile, keyboard, screen reader, forms, Dynamic Content, portal, performance, and error isolation;
- maintain a kill switch/removal plan.

Custom CSS must preserve responsive layout, focus indicators, contrast, zoom/text reflow, error messaging, and reduced-motion needs. JavaScript events such as click/double-click/mouseover/out/enter/leave are documented, but do not make hover/mouse the only route to essential content.

For Bookings, CRM, Forms, Checkout/Payments, and other embeds, the embedded product owns the transaction. Configure exact trusted domains/origins, minimize passed URL data, and confirm outcomes server-side where consequential.

## 12. Publishing, versions, debug access, backup, and rollback

Official publish options support individual page/file publication and draft states. Pro material includes page versions; official help says versions are automatically backed up, filterable, and restorable with user/time context.

`DOC-VERIFIED` Official controls also include unpublishing a site and downloading the published site as a password-protected ZIP representing the last published state. Debug access is temporary and current help says it is automatically revoked after one week.

### 12.1 Release workflow

1. Create/modify in draft and record requirement/owner.
2. Review content, legal claims, privacy/consent, SEO, links, forms, embeds, member access, Dynamic Content, scripts/CSS, analytics, accessibility, and performance.
3. Capture current page version/export and screenshots; inventory impacted URLs.
4. Test negative authorization and user-specific cache isolation.
5. Publish approved pages in a controlled window/canary where feasible.
6. Verify canonical domain/HTTPS, desktop/mobile, metadata/schema/sitemap/robots, form writes, dynamic calls, portal access, analytics consent, and error pages.
7. Roll back through page-version restore/unpublish/script removal/config restore when needed; reconcile external writes caused during the incident.

A downloaded site ZIP is not a complete backup of CRM/Form/Creator data, member accounts, Connections, Dynamic Content secrets, or all builder configuration. Protect the ZIP and password separately; never commit it to GitHub if it contains production content/data.

## 13. SEO and public-content controls

Official Sites SEO features include page metadata and robots configuration; pricing lists automatic sitemap, schema, and redirect capabilities by plan. Verify generated output after publish.

- Use canonical URLs and one HTTPS host; test `www`/apex redirects.
- Do not put private/member/draft/parameterized personal pages in sitemap, schema, social metadata, or indexable cache.
- `robots.txt` is crawler guidance, not access control.
- Use approved 301 redirects for changed URLs and monitor broken links.
- Validate structured data against actual public content and fair-housing/advertising/legal policy.
- Avoid exposing internal IDs, email addresses, storage links, or form values in page titles, URLs, schema, Open Graph, analytics, or error pages.

## 14. Errors, retries, idempotency, and observability

### 14.1 Dynamic Content failure model

Handle OAuth/connection failure, target API `4xx/5xx`, Sites quota exhaustion, function error/timeout, invalid response, view rendering error, `$DX` XHR failure, and stale/unavailable cache.

- Return correct generic HTTP status through `response_object.setStatus` where appropriate.
- Do not disclose stack traces, tokens, target payloads, member email/groups, or record existence.
- Retry idempotent reads only with capped backoff.
- A state-changing `$DX.post`/function uses an immutable operation key and target-system reconciliation before retry.
- Fail closed for private content: an API failure must never fall back to a public cached/full dataset.

### 14.2 Logging and monitoring

Record sanitized site/DC/dynamic-content/function/view, correlation ID, opaque operation/resource key, response category, duration, quota/retry, and outcome. Do not log request cookies, auth headers, form bodies, emails, addresses, documents, or target response payloads.

Monitor uptime/HTTPS/certificate, broken links, form success/reconciliation, spam rate, Dynamic Content errors/latency/quota, Connection expiration, access-denied anomalies, cache leakage tests, page changes/publishes, contributor/admin changes, external scripts, SEO indexation, and member lifecycle.

## 15. GH Real Estate and Sylvara patterns

### 15.1 Public property inquiry

1. Sites renders approved public listing/service content from a sanitized source; no WorkDrive/CRM raw IDs.
2. Form collects minimum contact/inquiry/consent/property reference with CAPTCHA/abuse controls.
3. Owning integration validates and creates or deduplicates a CRM `Lead` using an immutable intake operation ID.
4. Thank-you page states receipt only; background reconciliation confirms CRM write and alerts failures.
5. Qualification, application, Contact conversion, documents, payments, and leasing happen in their owning systems.

### 15.2 Public listing Dynamic Content

Use a server-side function with least-privilege CRM/Creator connection, fixed approved query, strict field allowlist, output encoding, and public cache only if no personalization/sensitive data. Never expose owner/tenant contact, access instructions, internal notes, unapproved availability, screening criteria, or private WorkDrive links.

### 15.3 Tenant/member entry

Sites may provide branded entry/authentication, but Creator should own operational portal state. After member authentication, a Sites server function maps the member to an approved CRM/Creator identity and returns only allowed summary/action links. Disable cache. Generate document/sign/payment access through authorized backend, not static links.

### 15.4 Booking

Embed the approved Zoho Bookings widget/service. Map service/staff/location/calendar, availability/time zone, confirmation/reminder, cancellation/reschedule, CRM linkage, spam/no-show and privacy. Sites only hosts the UI; Bookings owns appointment truth.

### 15.5 Cross-entity routing

Maintain explicit domain/site -> legal entity -> CRM/Creator/Bookings/Checkout connection mapping. Reject unknown host/domain and never route GH versus Sylvara by a browser-supplied `company` parameter.

## 16. Testing matrix

- Draft/publish/unpublish/restore/version and last-published ZIP;
- apex/`www`, HTTPS/certificate, redirects, wrong DC DNS, DNS rollback;
- desktop/mobile/tablet, keyboard/screen reader/zoom/contrast/performance;
- header/footer/CSS/third-party-script failure and removal kill switch;
- public/static versus member/dynamic cache, user A -> user B isolation;
- unauthenticated/wrong group/wrong record/direct URL/parameter tampering;
- `request_object` query/header/cookie type/length/XSS/injection/CSRF/IDOR;
- `$DX.get/post` success, non-2xx, timeout, double-click, replay, quota;
- Connection expiry/revocation/wrong scopes/DC and target API errors;
- CRM Lead form duplicate/spam/consent/reconciliation and negative Contact creation test;
- Zoho Forms/native/legacy form required/upload/redirect/notification/export;
- member signup/invite/SAML/social/group removal/deactivation;
- Bookings/payment/sign embeds with abandoned/tampered callback and server confirmation;
- robots/sitemap/schema/canonical/social metadata/noindex private content.

## 17. Anti-patterns

- Inventing a Sites REST API or automating private builder endpoints.
- Using client-side JavaScript to authorize private data.
- Leaving cache enabled for a `user`/request-specific view.
- Passing OAuth/API credentials in JavaScript, URLs, header/footer, or GitHub.
- Trusting a member email, group display name, query parameter, or hidden field as record authorization.
- Creating CRM Contacts from unqualified website signups.
- Treating thank-you/redirect as proof of CRM/payment/signature/booking success.
- Publishing tenant documents or durable WorkDrive external links.
- Relying on `robots.txt` or password protection as the only privacy control.
- Assuming a site ZIP backs up external app data/configuration.
- Continuing to build on legacy Sites forms with discontinued features.
- Publishing without accessibility, cache-isolation, negative authorization, and rollback tests.

## 18. Preflight checklist

- [ ] Site, legal entity, plan/add-ons/quotas, DC, owner/contributors verified.
- [ ] Public/Creator/member boundary and authoritative system for every form/action defined.
- [ ] Domain/DNS/SSL/canonical/rollback map approved.
- [ ] Dynamic Content app/views/functions/cache settings and exact Connections/scopes inventoried.
- [ ] Every private view performs server-side identity-to-record authorization with cache disabled.
- [ ] Forms map to CRM Leads/approved owner with consent, spam, duplicate and reconciliation controls.
- [ ] Header/footer/CSS/embeds/analytics privacy, security, accessibility and kill switch reviewed.
- [ ] Member signup/auth/group/suspension/deletion and negative-access tests passed.
- [ ] Draft/version/export, publish evidence, monitoring, unpublish/restore rollback ready.
- [ ] No secrets, PII, tenant docs, system IDs, or durable access links in source/page/logs.

## 19. Unknowns and required live verification

Do not invent or assume:

- a public Sites management REST API, OAuth scopes, webhooks, or CI/CD deployment endpoint;
- account-generated site/page/form/Dynamic Content/connection/member/group IDs or link names;
- plan/add-on quotas, member count, bandwidth/storage, or Dynamic Content allowance;
- all Deluge functions/tasks available in the Sites Dynamic Runtime Environment;
- target-app API behavior through a Connection;
- cache TTL/invalidation, cookie/security-header control, CSP, or session behavior beyond tested/current docs;
- native form integration/retry/export retention behavior;
- exact SAML/social-login claims and member sync behavior;
- complete backup/restore of builder, members, Connections, or external data.

Use current tenant UI, official help/pricing, controlled tests, target-product documentation, or Zoho support.

## 20. Official source registry

All sources accessed and verified 2026-07-20.

### Dynamic Content and customization

- Dynamic Content — https://help.zoho.com/portal/en/kb/zohosites/help-guide/manage/dynamic-content/articles/dynamic-content
- Zoho Sites Connections — https://help.zoho.com/portal/en/kb/zohosites/help-guide/manage/dynamic-content/articles/zoho-sites-connections
- Header and Footer Code — https://help.zoho.com/portal/en/kb/zohosites/help-guide/customization/code/articles/zoho-sites-header-and-footer-code
- Custom CSS Editor — https://help.zoho.com/portal/en/kb/zohosites/help-guide/customization/code/articles/zoho-sites-custom-css-editor
- JavaScript Events — https://help.zoho.com/portal/en/kb/zohosites/help-guide/edit-website/style-editor/articles/javascript-events

### Forms and integrations

- Zoho CRM Forms — https://help.zoho.com/portal/en/kb/zohosites/help-guide/edit-website/forms/articles/zoho-crm-forms
- Integrating Zoho Forms — https://help.zoho.com/portal/en/kb/zohosites/help-guide/edit-website/forms/articles/zoho-sites-integrating-zoho-forms
- Zoho Sites Forms — https://help.zoho.com/portal/en/kb/zohosites/help-guide/forms/articles/zoho-sites-forms
- Sites Form Migration — https://help.zoho.com/portal/en/kb/zohosites/help-guide/website-migration/articles/zoho-sites-form-migration
- Zoho Bookings for Sites — https://help.zoho.com/portal/en/kb/zohosites/help-guide/sites-integrations/articles/zoho-bookings-for-site
- CRM Member Sync — https://help.zoho.com/portal/en/kb/zohosites/help-guide/sites-integrations/articles/member-sync-in-zoho-crm

### Members, access, and contributors

- Member Portal — https://help.zoho.com/portal/en/kb/zohosites/help-guide/roles-and-permissions/member-portal/articles/member-portal-sites
- SAML Sign-in Method — https://help.zoho.com/portal/en/kb/zohosites/help-guide/roles-and-permissions/member-portal/articles/saml-sign-in-method
- Social Login — https://help.zoho.com/portal/en/kb/zohosites/help-guide/roles-and-permissions/member-portal/articles/social-login-sites
- Access Restriction — https://help.zoho.com/portal/en/kb/zohosites/help-guide/roles-and-permissions/access-control/articles/access-restriction
- Member Portal Restriction — https://help.zoho.com/portal/en/kb/zohosites/help-guide/roles-and-permissions/access-control/articles/zoho-sites-member-portal-restriction
- Contributors — https://help.zoho.com/portal/en/kb/zohosites/help-guide/roles-and-permissions/contributors/articles/contributors-for-sites
- Password Protection — https://help.zoho.com/portal/en/kb/zohosites/help-guide/roles-and-permissions/password-protection/articles/password-protection

### Domains, SEO, publishing, and recovery

- Domain Mapping — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/domain-ssl/articles/zoho-sites-domain-mapping
- Domain and SSL Hosting — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/domain-ssl/articles/domain-and-ssl-hosting
- Root Domain — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/domain-ssl/articles/root-domain
- SEO — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/seo/articles/seo
- Publish Options — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/site-options/articles/publish-options
- Page Versions — https://help.zoho.com/portal/en/kb/zohosites/help-guide/pages/articles/page-versions
- Unpublish Site — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/site-options/articles/unpublish-site
- Download Site — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/site-options/articles/zoho-sites-download-site
- Page Status in Builder — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/site-options/articles/page-status-in-builder
- Debug Access — https://help.zoho.com/portal/en/kb/zohosites/help-guide/configuration/site-options/articles/deb
- Zoho Sites Pricing — https://www.zoho.com/sites/pricing.html
