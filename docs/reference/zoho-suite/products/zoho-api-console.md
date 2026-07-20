# Zoho API Console and OAuth Engineering Knowledge Base

**Document ID:** GH-ZOHO-API-CONSOLE-KB
**Edition:** 2026.07 Research Edition
**Research cutoff:** 2026-07-20
**Audience:** ChatGPT, Codex, architects, developers, security reviewers, and GH/Sylvara operators
**Scope:** Zoho API Console client registration, Zoho Accounts OAuth 2.0 flows, scopes, data centers, token operations, security, testing, and integration runbooks

> This is a sanitized engineering reference. It contains no client IDs, client secrets, authorization codes, tokens, organization IDs, tenant data, or production callback URLs. The API Console and Zoho Accounts provide authentication and delegated authorization; each target Zoho product's current API documentation controls its resources, scopes, request schema, limits, and behavior.

## API-000 AI retrieval directive

When using this document as project context:

1. Identify the target Zoho product, resource owner, application owner, client type, execution environment, data center, and required operations before choosing an OAuth flow.
2. Treat client type, client ID, redirect URI, JavaScript origin, enabled data centers, per-DC secret model, scopes, token inventory, service organization/portal ID, and service API domain as live configuration. Never infer them from a screenshot, sample, repository name, or another integration.
3. Never output, request in chat, commit, log, screenshot, or store in a PDF a client secret, access token, refresh token, authorization code, device code, SCIM token, or credential-bearing URL.
4. Use the exact current scope documented by the target product endpoint. The API Console does not define product object names, fields, endpoint versions, required organization headers, or API limits.
5. Use the `accounts-server`/location returned by authorization and the `api_domain` returned by token issuance. Do not replace either with a remembered `.com` host.
6. An OAuth token proves that one principal authorized certain scopes. It does not prove that the principal has application-level access to a record, module, organization, portal, team, folder, mailbox, or Catalyst project.
7. Prefer a server-based confidential client for durable backend integrations that require delegated user access. Use PKCE where Zoho documents it. Use a Self Client only for controlled access to the owner's own Zoho resources, not as a shortcut for a multi-user product.
8. Cache and reuse access tokens until shortly before expiry. Do not generate a new token for every API call.
9. Separate Development, test, and Production credentials, callbacks, token stores, consent records, and authorized users. Repository state is not evidence that a credential is active or deployed.
10. Cite the exact Zoho Accounts/OAuth page and the exact product endpoint page used. If current official documentation conflicts with this handbook, follow the current page and flag this handbook for refresh.

### API-001 Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `DOC-VERIFIED` | Confirmed in official Zoho Accounts, Developer, or product documentation at the research cutoff | Cite the controlling page |
| `LIVE-CONSOLE REQUIRED` | Exists only in the authenticated API Console or account | Obtain through an authorized operator; never guess |
| `LIVE-METADATA REQUIRED` | Principal, grant, resource, organization, portal, team, project, or product metadata exists only in an authenticated environment | Inspect the exact target environment with an authorized principal; never infer it |
| `PRODUCT-DOC REQUIRED` | Defined by the target product rather than OAuth | Read that product's current endpoint and scope documentation |
| `RUNTIME TEST REQUIRED` | Exact redirect, token, permission, or resource behavior must be exercised safely | Test in a non-production path with sanitized evidence |
| `SECURITY APPROVAL REQUIRED` | Changes identity, secret, scope, callback, or access policy | Apply change control and least privilege |
| `SOURCE CONFLICT` | Current official pages publish inconsistent values or behavior | Follow the authority ladder, document the conflict, and verify safely before implementation |
| `VOLATILE` | Limit, data-center availability, flow detail, or console UI may change | Revalidate immediately before implementation |

## API-010 Product role and authority boundary

The Zoho API Console is the registration and configuration surface for OAuth clients. Zoho Accounts is the authorization server that authenticates users, obtains consent, issues and refreshes tokens, reports the user's data-center location, and revokes tokens. The protected resource server is the individual Zoho product API.

This distinction prevents a common design error: “Zoho OAuth access” is not one universal API contract.

| Layer | It controls | It does not control |
|---|---|---|
| API Console | Client type, client identity, registered callbacks/origins, client secret, Multi-DC settings | CRM fields, Books organizations, WorkDrive teams, Sign requests, Creator forms, or any business object |
| Zoho Accounts OAuth | Authentication, consent, scope grant, authorization code, access/refresh tokens, token revocation, DC routing | Product record permissions beyond the authorized principal's service permissions |
| Product API | Endpoints, versions, scopes, object schema, organization/portal headers, limits, errors | Client registration or cross-product identity governance |
| Zoho One/Directory | Workforce identity, app assignment, security policy, SSO, provisioning, admin roles | A replacement for each product's public REST API |
| Catalyst/another backend | Secure token use, webhook/API orchestration, idempotency, logging, retry, deployment | Authority to widen scopes or bypass product authorization |

For GH Real Estate and Sylvara, the API Console is credential infrastructure. It must not become a record of business facts, a source-code store, an informal secret-sharing surface, or proof that an integration is healthy.

## API-020 Authority ladder and preflight

Use this order for every implementation:

1. Current official endpoint page for the target Zoho product.
2. Current official Zoho Accounts OAuth page for the selected client type and flow.
3. Authenticated API Console configuration for the client.
4. Authenticated target-product metadata and current principal permissions.
5. Approved architecture, repository manifests, tests, deployment evidence, and monitoring.
6. This handbook as a retrieval and control guide.

Before generating an authorization URL or token request, record a sanitized preflight:

```yaml
integration_alias: "<non-secret stable name>"
business_owner: "<role, not personal credential>"
technical_owner: "<role>"
target_product: "<Zoho product>"
target_environment: "development|test|production"
client_type: "server|client|mobile-desktop|non-browser|self"
authorization_flow: "<documented flow>"
resource_owner_model: "single-owner|delegated-users|instance-admin"
data_center_strategy: "single-DC|multi-DC"
redirect_alias: "<sanitized callback name>"
scope_manifest_version: "<version>"
token_store_alias: "<secret-store reference, never value>"
product_metadata_verified_at: "<timestamp>"
rollback_owner: "<role>"
```

`LIVE-CONSOLE REQUIRED`: The actual client identifier, secret, callback list, DC toggles, token values, consent principal, and application ownership never belong in this manifest.

## API-030 Client types and selection

Zoho's current OAuth introduction routes applications to five documented client models. Select the model from runtime and user-consent requirements, not convenience.

| Client type | Documented model | Flow | Secret posture | Appropriate use |
|---|---|---|---|---|
| Server-based | Browser front end plus trusted backend that can keep credentials confidential | Authorization Code; PKCE optional and recommended by Zoho | Client secret only on server | Production web services and multi-user integrations |
| Client-based | JavaScript application executing in a browser without a trusted backend | Implicit flow in current Zoho documentation | Cannot safely hold a secret | Narrow browser-only use after security review |
| Mobile and desktop | Native public client | Authorization Code with PKCE | Public client; embedded secret is not confidential | Installed applications with system/browser redirect handling |
| Non-browser | Limited-input device such as a TV or printer | Device Authorization Grant | Device obtains codes and polls | Genuine limited-input devices, not ordinary servers |
| Self Client | Owner accesses the owner's own Zoho account or controlled backend-to-backend operation | Console-generated Authorization Code or documented Client Credentials flow | Confidential secret under one owner | Administrative scripts or tightly controlled single-owner services |

### API-031 Server-based client

This is the default architecture for GH/Sylvara backend integrations when a person or administrator must grant durable delegated access. The backend receives a short-lived authorization code at an exactly registered redirect URI, exchanges it for tokens, stores the refresh token in an approved secret store, and supplies access tokens to the product API.

Use a separate client or at least a separately governed token set when environments, owners, scope boundaries, or incident blast radius differ. Do not let a public browser, Zoho Sites page, Creator client script, mobile package, log aggregator, or GitHub workflow receive the client secret.

### API-032 Client-based browser application

Current Zoho documentation describes an implicit flow that returns an access token to the redirect fragment and provides a one-hour token. A browser application cannot safely keep a client secret. The token is exposed to the browser execution environment, history-adjacent tooling, extensions, and any injected script.

For GH/Sylvara, prefer a thin browser client calling an authenticated backend when the backend can safely mediate the Zoho API. Do not place a durable Zoho refresh token in browser storage. If a browser-only architecture is unavoidable, document the exact Zoho-supported flow, constrain scopes, validate `state`, restrict origins/callbacks, implement a strict Content Security Policy, and treat XSS as credential compromise.

### API-033 Mobile and desktop application

Zoho requires PKCE for newly designed mobile/desktop public clients and strongly advises older clients to adopt it. The app creates a high-entropy `code_verifier`, derives a `code_challenge`, sends the challenge with the authorization request, then sends the verifier during code exchange. Zoho documents verifier length as 43–128 unreserved characters and recommends `S256`; when SHA-256 is supported, Zoho says it must be used instead of `plain`.

Use the operating system browser rather than an embedded credential collector. Validate redirect ownership and `state`. Store tokens in the platform's protected credential facility, not a preferences file or general local database.

### API-034 Non-browser application

The Device Authorization Grant is for devices that cannot conduct normal browser input. The device obtains `user_code`, `verification_url`, and `device_code`, displays the first two, and polls with the device code. Zoho currently directs polling at one request per five seconds. The flow can return cross-DC feedback requiring polling to move to the user's actual accounts server.

Do not repurpose device flow to avoid implementing a redirect callback for a normal web/backend service. Bound polling, stop on expiry/denial, never log device codes, and prevent a device reset from leaving an orphaned durable grant.

### API-035 Self Client

A Self Client is appropriate when the client accesses the registering owner's own Zoho data without an end-user authorization UI. It is not a “service account” with automatic access to every Zoho product and organization.

The documented authorization-code path lets an authorized operator enter product scopes in the API Console, choose the code expiry, select an app/portal when prompted, generate a one-time code, and exchange it for access and refresh tokens. The current general Self Client page states a default three-minute code duration; product-specific legacy pages can show different choices, so use the live console.

The documented Self Client Client Credentials flow returns an access token but no refresh token. It requires `scope`, and some products require `soid` in the form `{service}.{instance-id}`. Zoho advises checking the target product documentation; `missing_org_info` indicates the instance selector may be required. Never assume this grant is supported for the desired product operation merely because the API Console exposes a Self Client.

### API-036 Instance-level OAuth

Zoho separately documents instance-level OAuth for integrations where an administrator chooses a specific instance of a Zoho application during consent. It is not a sixth generic client type. Current rules state that the consenting user must administer at least one instance and, generally, one refresh token's scopes are limited to one Zoho app, with listed common-service exceptions.

Use instance-level OAuth only when the target product documents that model. Capture the selected instance's stable ID after authorization, segregate tokens by instance, and never infer the instance from the user's email address.

## API-040 Registration and live-console inventory

### API-041 Registration controls

For a new client, record and verify:

- a stable, purpose-specific client name;
- the exact client type;
- an approved homepage or application domain where required;
- exact redirect URIs, including scheme, host, port, path, and trailing-slash behavior;
- JavaScript domains/origins only for a client type that requires them;
- application owner and at least one recovery/continuity owner under organizational policy;
- environments and enabled data centers;
- whether secrets are distinct per DC or shared, if Multi-DC is enabled;
- the secret-store location by alias, rotation date, and consumers;
- scope baseline and consent workflow;
- retirement and token-revocation procedure.

A redirect URI mismatch is not solved by loosening matching or registering a wildcard. Zoho's OAuth FAQ says the request URI must exactly match a registered URI. Register only deliberate HTTPS callbacks for production. Loopback/custom-scheme patterns for installed clients must follow the current client-type documentation and runtime security model.

### API-042 Sanitized client registry

Keep a repository-safe inventory like this:

```yaml
clients:
  - alias: "gh-crm-intake-prod"
    client_type: "server-based"
    owner_role: "integration administrator"
    environment: "production"
    target_services: ["CRM"]
    enabled_dc_policy: "single-US"
    callback_ids: ["oauth-callback-prod-v1"]
    secret_store_key_alias: "zoho/gh/crm/oauth-client"
    scope_manifest: "oauth/scopes/gh-crm-intake-v1.yaml"
    last_consent_review: "<date>"
    last_rotation_test: "<date>"
    status: "planned|active|retiring|revoked"
```

Never include the client ID merely because it is sometimes called “public.” In this public repository, identifiers create avoidable targeting and configuration-disclosure risk. Preserve real values only in the approved operational system.

## API-050 Authorization Code flow

### API-051 Authorization request

The server-based authorization endpoint is DC-aware:

```http
GET {accounts-server-url}/oauth/v2/auth
```

Core request and recommended security parameters are:

| Parameter | Purpose | Engineering rule |
|---|---|---|
| `client_id` | Identifies registered client | Load from protected configuration; do not expose in repository fixtures |
| `response_type=code` | Requests an authorization code | Fixed for Authorization Code flow |
| `redirect_uri` | Callback receiving code | Exact registered value; verify before launch |
| `scope` | Product permissions requested | Generate from approved manifest; least privilege |
| `access_type` | `online` or `offline` | Use `offline` only when durable unattended access is required |
| `prompt=consent` | Forces consent screen | Use deliberately; can produce another refresh token |
| `state` | Correlates request and mitigates CSRF | Generate cryptographically, bind to session/intent, single-use, expire quickly |
| `code_challenge` | PKCE challenge | Required for mobile/desktop; recommended for server apps |
| `code_challenge_method` | PKCE transform | Prefer `S256` |

Zoho returns a short-lived, one-time authorization code. Current general server documentation says two minutes. Capture and validate returned `state`, `location`, and `accounts-server`; reject an unexpected or replayed callback. Do not log the full callback URL because it contains the code.

### API-052 Code exchange

Exchange the code using `POST` to the accounts server associated with the user's returned location:

```http
POST {accounts-server-url}/oauth/v2/token
Content-Type: application/x-www-form-urlencoded

client_id=<secret-store value>
client_secret=<secret-store value>
grant_type=authorization_code
redirect_uri=<exact registered URI>
code=<single-use code>
code_verifier=<when PKCE is used>
```

Zoho documentation permits token parameters in a query string, request body, and—only for the client credentials pair in documented cases—Basic authentication. Operationally, use a TLS-protected POST body and configure clients, reverse proxies, APM tools, and error middleware not to record it. URL query strings are frequently retained in access logs and telemetry.

The response commonly contains `access_token`, optional `refresh_token`, `api_domain`, `token_type`, and `expires_in`. Treat the whole response as sensitive. Store the refresh token once; maintain the access token in a protected cache with an expiry timestamp; preserve the returned product API domain with the grant.

### API-053 Refresh

```http
POST {accounts-server-url}/oauth/v2/token
Content-Type: application/x-www-form-urlencoded

client_id=<value>
client_secret=<value>
grant_type=refresh_token
refresh_token=<value>
```

The refreshed response normally omits a new refresh token. Replace the cached access token atomically and retain the existing refresh token. Use a single-flight lock so concurrent workers do not create a refresh storm. Refresh shortly before expiry with bounded skew, but reuse a still-valid token. If refresh fails, distinguish transient network failure from revoked/invalid credentials before retrying.

### API-054 Refresh-token issuance and limits

Zoho documents `access_type=offline` as the request for a refresh token. A refresh token is generally returned the first time that grant is created. `prompt=consent` forces the consent page and can be used with offline access when a new refresh token is intentionally required.

Current Zoho Accounts limits include:

- access tokens are valid for one hour;
- at most 10 active access tokens are stored per refresh token; requesting another access token invalidates the oldest;
- up to 10 access-token requests in 10 minutes under the documented throttle;
- a refresh token can create up to 10 access tokens in 10 minutes;
- at most 20 active refresh tokens are stored per client per user, after which the oldest is invalidated;
- at most 10 authorization codes per client/user in 10 minutes, with each general code valid for two minutes;
- device-code/token limits are separately documented and IP-sensitive.

These are `VOLATILE`. They are safety ceilings, not throughput targets. A worker fleet should share a token cache per grant, use locks, and alert on unexpected refresh volume.

`SOURCE CONFLICT`: The dedicated current OAuth token-limits page states a maximum of 10 active access tokens per refresh token. An older Accounts `INVALID_OAUTHTOKEN` FAQ still mentions 15, and some product pages publish other counts. For the general Accounts limit, use the dedicated token-limits page; reconcile any product-specific conflict against that product's current documentation and a safe runtime test before implementation. Never combine the figures.

## API-060 Scopes, principals, and resource authorization

### API-061 Scope construction

Zoho products publish their own scope names and operation suffixes. Common shapes resemble:

```text
Service.resource.READ
Service.resource.CREATE
Service.resource.UPDATE
Service.resource.DELETE
Service.resource.ALL
```

This is a pattern, not a universal grammar. Copy scopes from the exact endpoint page. Product scope namespaces, case, separators, version behavior, and granularity differ. A console accepting a scope string does not prove the principal can perform every operation represented by it.

Scope review must answer:

1. Which endpoint requires each scope?
2. Is a read-only scope sufficient?
3. Can separate read and mutation clients/tokens reduce blast radius?
4. Does the principal's product role/profile permit the intended object and field?
5. Is an organization, portal, team, account, or project selector also required?
6. Does one refresh token cross products, or does the selected OAuth model require one product per grant?
7. What data classes can the scope expose?
8. What exact test proves revocation and least privilege?

### API-062 Incremental authorization

Zoho documents incremental authorization for server-based apps: request basic scopes first, then request additional permission when a feature is used. This improves consent clarity and avoids an unnecessarily broad first grant. Treat a later scope increase as a security change, update the scope manifest, show an accurate consent explanation, and test whether the current refresh-token/grant behavior needs re-consent.

### API-063 Principal permission intersection

Effective access is approximately:

```text
OAuth scopes
INTERSECT authorized user's product membership
INTERSECT product role/profile/field permissions
INTERSECT selected organization/portal/team/project
INTERSECT record sharing and state rules
```

Therefore `invalid_oauthtoken`, `401`, `403`, missing records, or missing fields can reflect different layers. Never “fix” a permission error by immediately asking for full-access scopes. Reconcile data center, token status, target product, organization selector, profile, resource sharing, and endpoint scope in order.

## API-070 Multi-DC routing

### API-071 Current accounts-server map

Zoho's current Multi-DC page lists:

| Location | Accounts server |
|---|---|
| United States | `https://accounts.zoho.com` |
| Europe | `https://accounts.zoho.eu` |
| India | `https://accounts.zoho.in` |
| Australia | `https://accounts.zoho.com.au` |
| Japan | `https://accounts.zoho.jp` |
| Canada | `https://accounts.zohocloud.ca` |
| Saudi Arabia | `https://accounts.zoho.sa` |
| United Kingdom | `https://accounts.zoho.uk` |

This table routes Zoho Accounts. It is not a license to synthesize a product API host. Use `api_domain` and the product's current DC table.

### API-072 Multi-DC client behavior

An API Console client created in one DC needs Multi-DC support enabled to authorize users in enabled other DCs. The client ID is common; the console can use a separate secret per enabled DC or the same credential across enabled DCs. Separate secrets reduce cross-region blast radius but require accurate routing and secret inventory.

For server apps:

1. Start authorization using the documented entry accounts host.
2. Read returned `location` and `accounts-server`.
3. Exchange the code at that accounts server.
4. Store the returned `api_domain` with the token grant.
5. Refresh and revoke at the same correct accounts-server context.
6. Call the product resource at its returned/documented domain.

For device flow, `other_dc` can tell the device to continue polling against the actual user location. Treat every domain value as allowlist-validated Zoho configuration before using it; do not follow an arbitrary callback-supplied host.

### API-073 GH/Sylvara DC rule

Current GH/Sylvara integrations should remain explicitly single-DC unless a real cross-region user or organization requirement is approved. Do not enable every DC “just in case.” If Multi-DC becomes necessary, add regional secrets, callbacks, consent tests, monitoring dimensions, incident response, and data-residency review before enabling it.

## API-080 Product metadata and field discovery

The API Console has no master catalog of CRM modules, Creator forms, Books organization fields, WorkDrive teams, Sign templates, Mail accounts, or Catalyst project components. OAuth grants access; the product API exposes product metadata.

Before coding, create a product-specific discovery checklist:

| Question | Source |
|---|---|
| Correct API version and base path? | Current product API reference |
| Required exact scope? | Endpoint's scope table |
| Organization/portal/team/project identifier? | Authenticated product API/console |
| Object/module/form/report API name? | Product metadata endpoint |
| Field API names, types, required status, picklists? | Product metadata/layout endpoint |
| Principal's permissions and sharing? | Authenticated user/profile and safe probe |
| Limits, pagination, concurrency, idempotency? | Endpoint and limits pages |
| Webhook signature and replay model? | Product webhook documentation |
| Regional endpoint/availability? | Product DC and feature pages |

Store only sanitized metadata in GitHub. Do not store record values, personal data, tokens, live organization identifiers, unredacted errors, or signed URLs. Timestamp the metadata and require refresh when a layout, field, role, plan, environment, or product version changes.

## API-090 Token storage and runtime architecture

### API-091 Secret classification

| Artifact | Classification | Storage rule |
|---|---|---|
| Client secret | Long-lived credential | Managed secret store; server only |
| Refresh token | Long-lived delegated credential | Managed secret store; encrypt, access-log, rotate/revoke |
| Access token | Short-lived bearer credential | Protected memory/cache; never persistent logs |
| Authorization/device code | Short-lived credential | Memory/ephemeral store; single-use; redact |
| Client ID | Identifier with targeting/config value | Protected configuration; omit from public repo |
| Redirect URI | Security configuration | Versioned sanitized alias plus controlled live value |
| Scope set | Authorization policy | Versioned sanitized manifest |

If using Catalyst, store credentials in the approved Catalyst secret/configuration facility and document only variable names. If using GitHub Actions, use environment-scoped secrets and protected environments; do not print them, pass them in command lines captured by logs, or expose them to untrusted pull requests. Zoho Connections can own OAuth on supported Zoho surfaces, but connection names, scopes, owners, and environments remain live metadata and require the same governance.

### API-092 Token broker pattern

A backend token broker should:

1. Resolve grant by integration/environment/DC alias.
2. Read the encrypted refresh token only when refresh is needed.
3. Return a cached access token if valid beyond safety skew.
4. Acquire a distributed single-flight lock before refresh.
5. POST to the stored accounts server.
6. Validate response shape and expected Zoho domain allowlist.
7. Cache token and exact expiry atomically.
8. Emit only sanitized metrics: grant alias, status class, latency, expiry horizon, and correlation ID.
9. Alert on revocation, repeated invalid-client errors, DC mismatch, and abnormal refresh rate.

Do not return refresh tokens to ordinary callers. Restrict which service identities can request each product grant.

## API-100 Error taxonomy and troubleshooting

| Symptom/error | Likely causes | Safe response |
|---|---|---|
| `invalid_client` | Wrong/missing client ID, wrong accounts server, wrong grant type | Reconcile client alias, DC, and flow; do not rotate blindly |
| `invalid_client_secret` | Wrong/missing secret or wrong per-DC secret | Verify secret version and DC in controlled runtime |
| `invalid_redirect_uri` | Request does not exactly match registered callback | Compare exact URI; do not broaden registration |
| `invalid_code` | Missing, expired, reused code; revoked refresh token in refresh context | Restart consent or incident path; never retry the same authorization code |
| `invalid_scope` | Misspelled/unsupported/product-incompatible scope | Read target endpoint scope table |
| `access_denied` | User denied, throttle reached, policy restriction | Preserve sanitized reason; back off; do not loop consent |
| `INVALID_OAUTHTOKEN` from product | Expired/revoked token, DC mismatch, wrong presentation | Refresh once if appropriate; verify product auth scheme and domain |
| 401/403 with valid token | Product membership, role, field, organization, or scope mismatch | Probe identity and metadata with least privilege |
| Missing refresh token | Online access, prior consent, or consent parameters | Do not repeatedly create grants; intentionally re-consent if approved |
| Refresh storm/throttle | No shared cache/lock, new token per request | Stop workers, repair token broker, reuse valid token |

Authorization codes are one-time credentials. Token endpoints support `POST`; entering a token URL in a browser issues a `GET` and can also leak credentials. Never ask an operator to paste a full credential-bearing URL into a ticket or screenshot.

## API-110 Revocation, rotation, and incident response

Zoho supports user revocation from Connected Apps and programmatic `POST {accounts-server-url}/oauth/v2/token/revoke?token=...`. Revoking a refresh token invalidates the access tokens generated from it. Refresh tokens also can disappear when the active-token limit evicts the oldest grant, a user revokes Connected Apps, a registered client is deleted, or relevant account-security choices terminate tokens.

### API-111 Planned rotation

1. Identify every consumer and environment by sanitized client/grant alias.
2. Confirm a rollback owner and maintenance window.
3. Create/rotate the client secret in the authorized console flow if supported.
4. Update secret store without logging the value.
5. Run a token refresh and read-only product smoke test.
6. Test one bounded idempotent write only when the integration requires writes.
7. Monitor old/new credential use.
8. Revoke the superseded token/secret after the cutover window.
9. Preserve sanitized evidence and update rotation date.

### API-112 Suspected compromise

1. Contain the calling workload and prevent repeated mutations.
2. Revoke the exposed access or refresh token at the correct accounts server.
3. Rotate the client secret if exposure includes it; if the client itself is compromised, replace the client under change control.
4. Inspect Zoho Accounts/Connected Apps and target-product audit evidence.
5. Reconcile affected records, messages, payments, documents, and webhooks by stable event IDs.
6. Notify security/business owners according to incident policy.
7. Reauthorize only the minimum scopes after cause is fixed.
8. Add a regression test or control that prevents the exposure path.

Deleting an API Console client is destructive: associated refresh tokens become unusable and every dependent integration can fail. Inventory and migrate all consumers before deletion.

## API-120 Observability and audit evidence

Emit metrics and structured logs that answer “which integration path failed?” without exposing a bearer credential.

Recommended fields:

```json
{
  "event": "zoho_oauth_refresh",
  "integration_alias": "gh-crm-intake-prod",
  "environment": "production",
  "dc": "us",
  "scope_manifest_version": "v1",
  "result": "success|rejected|transport_error",
  "http_status_class": "2xx|4xx|5xx",
  "latency_ms": 0,
  "seconds_to_prior_expiry": 0,
  "correlation_id": "sanitized-random-id"
}
```

Never log headers, request bodies, callback URLs, token responses, Basic authorization, code verifier, `Set-Cookie`, or raw provider error dumps. At the product call layer, log resource type and operation—not tenant names, email addresses, payment data, document contents, or message bodies.

Alert on:

- repeated refresh failure or `invalid_client_secret`;
- token requests approaching documented throttle limits;
- authorization callbacks with bad/missing/replayed `state`;
- unexpected DC or API domain;
- scope-manifest change without approval;
- refresh-token age beyond policy or unknown owner;
- client used from an unexpected environment;
- a sudden rise in 401/403 or mutation volume;
- a token or secret detected by repository/CI secret scanning.

## API-130 Testing strategy

### API-131 Registration tests

- Exact allowed callback succeeds; a path/trailing-slash variation fails.
- Unknown `state`, missing `state`, and replayed `state` are rejected locally.
- PKCE `S256` succeeds; wrong verifier fails.
- Client secret never reaches browser bundle, logs, screenshots, or test artifacts.
- Multi-DC disabled client cannot silently authorize an unsupported location.

### API-132 Token tests

- Code is exchanged once, at the correct accounts server.
- Access token expiry is read from `expires_in`, not hardcoded alone.
- Concurrent callers produce one refresh request.
- Revoked refresh token stops processing and raises an actionable alert.
- A token issued for one service/scope cannot perform a prohibited operation.
- The product call uses the exact authentication prefix documented by that product. Zoho Accounts describes Bearer tokens; several product APIs document `Zoho-oauthtoken`. Follow the resource server.

### API-133 Product authorization tests

- Read-only principal cannot mutate.
- Missing product role/profile permission fails closed even with OAuth scope.
- Wrong organization/portal/team selector cannot cross boundaries.
- Metadata discovery detects renamed/custom fields rather than relying on UI labels.
- Pagination, rate limits, retries, and idempotency are tested at the product layer.

Use synthetic or sanitized records. Never send a real lease, payment, tenant notice, email, SMS, or signature request merely to test OAuth.

## API-140 GH Real Estate and Sylvara patterns

### API-141 Recommended segmentation

| Integration class | Recommended grant boundary |
|---|---|
| Zillow/Catalyst to CRM intake | Dedicated CRM write grant with only required Lead operations and metadata read if needed |
| CRM metadata/reconciliation | Separate read-focused grant where practical |
| Books/Billing/Payments | Finance-specific grant and principal; never reuse CRM token |
| Contracts/Sign | Separate contract and signature grants; sending authority behind manual/idempotent gate |
| Creator tenant portal | Product-specific Creator connection/token; browser never holds broad refresh token |
| WorkDrive document operations | Team/folder-scoped product permissions plus narrow OAuth scopes |
| Mail/Twilio communications | Separate provider credentials, consent policy, suppression and delivery evidence |
| Catalyst deployments | Deployment identity separate from runtime product connections |

### API-142 Source-of-truth rule

OAuth state must never be used as business state. A valid CRM token does not mean a Lead exists; a valid Books token does not mean an invoice posted; a valid Sign token does not mean a request was executed. Every workflow must reconcile the target product's authoritative record and store only stable external IDs/status evidence in the owning system.

### API-143 Safe implementation sequence

1. Approve system-of-record and business action.
2. Read target product KB and exact endpoint page.
3. Discover live object/field/organization metadata.
4. Define least-privilege scope manifest.
5. Choose client type and environment.
6. Register callbacks and client in correct DC.
7. Store credentials in approved secret facility.
8. Complete consent with intended principal.
9. Validate identity, scopes, DC, organization, and read probe.
10. Implement idempotent operation and sanitized observability.
11. Test revocation, retry, duplicate, and partial-failure behavior.
12. Deploy through change control and preserve evidence.

## API-150 Implementation checklist

### Design

- [ ] Target product and exact endpoints identified.
- [ ] System of record and business owner approved.
- [ ] Client type and OAuth flow match runtime.
- [ ] Principal and application role are least privilege.
- [ ] Scope manifest maps each scope to an endpoint.
- [ ] Single-DC/Multi-DC decision documented.
- [ ] Environment separation and callback inventory documented.
- [ ] Secret/token storage, rotation, revocation, and recovery designed.

### Build

- [ ] Authorization callback validates state, expiry, one-time use, and expected Zoho domain.
- [ ] PKCE implemented where required/recommended.
- [ ] Token requests use TLS POST and are excluded from logs.
- [ ] `accounts-server`, `location`, `api_domain`, and expiry are preserved correctly.
- [ ] Shared token cache and single-flight refresh implemented.
- [ ] Product metadata is discovered rather than guessed.
- [ ] Product auth prefix and organization selectors follow endpoint docs.
- [ ] Idempotency and reconciliation protect all mutations.

### Verify and operate

- [ ] Negative permission and wrong-DC tests pass.
- [ ] Revocation drill produces a controlled failure and alert.
- [ ] Secret scanning and log review show no credential exposure.
- [ ] Monitoring covers refresh, 401/403, throttles, and unexpected DC/domain.
- [ ] Deployment evidence identifies commit, environment, scope-manifest version, and smoke test.
- [ ] Retirement runbook inventories consumers before revoking/deleting client.

## API-160 Anti-patterns

- Using one Self Client refresh token for every Zoho product, environment, and workflow.
- Asking an AI agent or support ticket to hold a live token “temporarily.”
- Generating a new access/refresh token for every request or test run.
- Hardcoding `accounts.zoho.com` or `www.zohoapis.com` after receiving different location/domain data.
- Treating client credentials flow as universally supported for every product and action.
- Embedding a confidential client secret in browser/mobile code.
- Adding full-access scopes to mask a product role or organization-selection error.
- Registering broad/uncontrolled callbacks or ignoring `state`.
- Logging token endpoint URLs, headers, bodies, responses, or raw callback queries.
- Treating a successful token exchange as proof that production API calls or automations work.
- Deleting a client before inventorying refresh tokens and dependent jobs.

## API-170 Official source registry

All sources below are official Zoho properties. Endpoint-specific product documentation must be added to an implementation's source manifest.

### Core OAuth and client types

1. [Introduction to OAuth 2.0](https://www.zoho.com/developer/oauth/introduction.html)
2. [Server-based apps overview](https://www.zoho.com/developer/oauth/web-server-apps/overview.html)
3. [Server-based authorization request](https://www.zoho.com/accounts/protocol/oauth/web-apps/authorization.html)
4. [Get access token](https://www.zoho.com/developer/oauth/web-server-apps/get-access-token.html)
5. [Refresh access token](https://www.zoho.com/developer/oauth/web-server-apps/refresh-access-token.html)
6. [Client-based apps overview](https://www.zoho.com/accounts/protocol/oauth/javascript-applications.html)
7. [Mobile and desktop apps / PKCE](https://www.zoho.com/developer/oauth/mobile-and-desktop-apps/overview.html)
8. [Non-browser applications](https://www.zoho.com/developer/oauth/non-browser-apps/overview.html)
9. [Self Client overview](https://www.zoho.com/developer/oauth/self-client/overview.html)
10. [Self Client Authorization Code flow](https://www.zoho.com/developer/oauth/self-client/authorization-code-flow.html)
11. [Self Client Client Credentials flow](https://www.zoho.com/developer/oauth/self-client/client-credentials-flow.html)
12. [Instance-level OAuth overview](https://www.zoho.com/developer/oauth/instance-level-oauth.html)
13. [Instance-level authorization code](https://www.zoho.com/developer/oauth/instance-level-oauth/get-auth-code.html)

### Tokens, routing, and operations

14. [Multi-DC support](https://www.zoho.com/developer/oauth/multi-dc-support.html)
15. [Zoho Accounts server information](https://accounts.zoho.com/oauth/serverinfo)
16. [Token limits](https://www.zoho.com/developer/oauth/token-limits.html)
17. [Revoke OAuth tokens](https://www.zoho.com/accounts/protocol/oauth/revoke-refresh-token.html)
18. [Refresh-token expiry FAQ](https://help.zoho.com/portal/en/kb/accounts/faqs-troubleshooting/faqs/oauth/articles/will-the-refresh-tokens-expire)
19. [Invalid code and redirect URI FAQ](https://help.zoho.com/portal/en/kb/accounts/faqs-troubleshooting/faqs/oauth/articles/invalid-code-redirect-uri)
20. [OAuth FAQ index](https://help.zoho.com/portal/en/kb/accounts/faqs-troubleshooting/faqs/oauth)
21. [Automating OAuth without browser intervention](https://help.zoho.com/portal/en/kb/accounts/faqs-troubleshooting/faqs/oauth/articles/how-to-automate-oauth-token-generation-without-browser-intervention-30-5-2021)
22. [Missing refresh token FAQ](https://help.zoho.com/portal/en/kb/accounts/faqs-troubleshooting/faqs/oauth/articles/i-m-unable-to-find-the-refresh-token-in-the-http-response-i-received)
23. [Invalid OAuth token FAQ (diagnostics; contains a conflicting legacy active-token count)](https://help.zoho.com/portal/en/kb/accounts/faqs-troubleshooting/faqs/oauth/articles/invalid-oauthtoken-on-api-access-30-5-2021)
24. [Token-generation error FAQ](https://help.zoho.com/portal/en/kb/accounts/faqs-troubleshooting/faqs/oauth/articles/error-occurred-during-access-token-generation)

### Product examples used only to illustrate product ownership of scopes/DCs

25. [CRM API v8 OAuth overview](https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html)
26. [Books API OAuth](https://www.zoho.com/books/api/v3/oauth/)
27. [Billing API OAuth](https://www.zoho.com/billing/api/v1/oauth/)
28. [Creator API v2.1 OAuth](https://www.zoho.com/creator/help/api/v2.1/oauth-overview.html)
29. [WorkDrive API OAuth](https://workdrive.zoho.com/apidocs/v1/oauth2authentication)
30. [Sign API OAuth](https://www.zoho.com/sign/api/oauth.html)

## API-180 Explicit research gaps

1. `LIVE-CONSOLE REQUIRED`: The authenticated API Console inventory, owners, client types, callback values, enabled data centers, secret-sharing model, and active/retired clients for GH/Sylvara were not available and are intentionally not inferred.
2. `LIVE-METADATA REQUIRED`: No live OAuth grant, Connected Apps list, principal identity, scope list, product organization/portal/team/project IDs, or current token health was inspected.
3. `PRODUCT-DOC REQUIRED`: There is no single cross-suite scope catalog or object/field registry in API Console. Each product handbook and endpoint reference must control its own APIs.
4. `VOLATILE`: Console labels, supported flows by client type, limits, DC list, and instance-level availability can change. Recheck immediately before registration or migration.
5. `SECURITY APPROVAL REQUIRED`: The preferred organizational client owner, emergency recovery owner, secret manager, rotation interval, and incident-notification policy remain governance decisions.
6. No public official endpoint was found that safely exports a complete API Console client inventory for this use case; plan controlled console review rather than screen scraping.
7. The official Accounts pages describe Bearer presentation while individual product APIs can prescribe `Zoho-oauthtoken`. The resource server's current documentation must decide the header for each integration.
8. `SOURCE CONFLICT`: The dedicated current token-limits page says 10 active access tokens per refresh token, while an older Accounts FAQ says 15 and some product references differ. Use the dedicated page for the general limit and resolve product-specific conflicts before deployment.

---

**Maintenance rule:** Revalidate this handbook after a Zoho Accounts OAuth documentation change, new data center, client-type/PKCE change, token-limit change, API Console redesign, security incident, or any GH/Sylvara authorization architecture change.
