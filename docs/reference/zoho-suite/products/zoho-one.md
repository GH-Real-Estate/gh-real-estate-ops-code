# Zoho One Administration, Directory, and Identity Knowledge Base

**Document ID:** GH-ZOHO-ONE-KB
**Edition:** 2026.07 Research Edition
**Research cutoff:** 2026-07-20
**Audience:** ChatGPT, Codex, identity architects, administrators, security reviewers, and GH/Sylvara operators
**Scope:** Zoho One central administration, Zoho Directory, users, groups, application assignment, SSO, provisioning, security/routing/conditional-access policies, domains, auditability, lifecycle governance, and automation boundaries

> This is a sanitized administrative and engineering reference. It contains no user roster, email addresses, organization IDs, domain-verification values, SCIM tokens, SAML certificates, client secrets, API keys, or production configuration. Current Zoho One/Directory documentation and the authenticated tenant control actual behavior. Each individual Zoho product's API reference remains authoritative for its business objects and REST API.

## ONE-000 AI retrieval directive

When using this document as project context:

1. Decide whether the task concerns workforce identity/access in Zoho One or business data inside a product such as CRM, Books, Creator, Sign, WorkDrive, or Mail. Do not substitute one surface for the other.
2. Treat organization owner, admins, custom roles, service admins, users, groups, smart-group criteria, app assignments, app settings, directory stores, domains, IdPs, security/routing/conditional-access policy versions and priorities, and provisioning connectors as live tenant configuration.
3. Never infer a person's identity, employment state, app role, group membership, license, department, email status, MFA state, or authorization from a repository or a visible product label.
4. Never output, commit, or place in prompts an SCIM token, SAML/JWT secret, signing certificate private key, API credential, recovery code, session artifact, DNS verification value, or user export.
5. Before an access change, resolve the exact user, group, application instance, role/profile, environment, owner, and downstream effect. App assignment in Zoho One can provision an account, but product permissions and data sharing may still require product-specific validation.
6. Use groups and conditional assignment for repeatable access policy. Avoid direct one-off assignment when a lifecycle rule can express the need, but do not automate privileged roles without a review gate.
7. Deactivation is not universal downstream erasure. Current Zoho documentation explicitly warns that some SAML apps may require separate deactivation and that owners/integrations must be transferred.
8. Determine whether the tenant uses legacy Security 1.0 or updated Security 2.0 before evaluating access. Security 1.0 can combine components from multiple policies; Security 2.0 applies one highest-priority security policy and one highest-priority routing policy, while conditional-access policies use separate action and MFA-priority rules. Never transfer a precedence rule between models.
9. An admin-panel change or successful login is not deployment evidence for every application. Preserve approvals, before/after state, tests, audit evidence, exception handling, and rollback/forward-repair notes.
10. Cite the exact official page. If this handbook and a current official page differ, use the current page and flag the handbook for refresh.

### ONE-001 Evidence labels

| Label | Meaning | Required behavior |
|---|---|---|
| `DOC-VERIFIED` | Confirmed in current official Zoho One or Directory documentation | Cite the controlling page |
| `LIVE-DIRECTORY REQUIRED` | Value exists only in the authenticated organization | Inspect with an authorized administrator; never guess |
| `PRODUCT-METADATA REQUIRED` | Setting/role/object belongs to an individual Zoho app | Consult the product's admin/API metadata |
| `PLAN/REGION VOLATILE` | Availability or limit can depend on edition, plan, UI, or DC | Recheck the live tenant and current page |
| `SECURITY-MODEL REQUIRED` | Zoho documents legacy Security 1.0 and updated Security 2.0 policy models | Identify the live model before calculating effective access or following navigation |
| `SECURITY APPROVAL REQUIRED` | Changes privileged access, authentication, provisioning, domain, or recovery | Apply formal change control |
| `BUSINESS APPROVAL REQUIRED` | Depends on employment, contractor, tenant, vendor, or records policy | Obtain accountable owner approval |

## ONE-010 Product role and authority boundary

Zoho One is the suite-level administrative and user experience layer. Its Directory centralizes organizational users, groups, admins, applications, security/routing/conditional-access policies, identity providers, directory stores, domains, and reports. It can assign and provision access to Zoho and supported third-party applications.

Zoho One is **not** one cross-suite business-data API and it does not merge all application databases.

| Concern | Authority |
|---|---|
| Workforce identity, app entitlement, group membership, authentication/access policy | Zoho One / Directory |
| CRM leads, contacts, applications, properties, units, cases | Zoho CRM |
| Accounting, invoices, payments, balances, ledgers | Zoho Books/Billing/Payments |
| Contract lifecycle, clauses, approvals | Zoho Contracts |
| Signature requests, recipients, evidence | Zoho Sign |
| Tenant portal data and app workflows | Zoho Creator under approved architecture |
| Documents and team folders | Zoho WorkDrive |
| Mailbox, messages, routing, retention | Zoho Mail and its Admin Console |
| Serverless integration state | Zoho Catalyst |
| Source code, sanitized manifests, tests, runbooks | GitHub |

An app shown in the Zoho One launcher may be assigned to a user without exposing a public API through Zoho One. To automate CRM, Books, Sign, WorkDrive, Creator, or another service, use that product's documented OAuth scopes, endpoints, organization selectors, and metadata.

## ONE-020 Authority ladder and live preflight

Use this order:

1. Current official Zoho One/Directory page for the exact admin action.
2. Authenticated Zoho One organization state and effective role permissions.
3. Current product administration/API documentation for downstream application behavior.
4. Authenticated downstream product state and audit evidence.
5. Approved GH/Sylvara identity policy, change record, repository manifests, and runbooks.
6. This handbook as a retrieval map.

Before proposing a change, collect a sanitized preflight:

```yaml
change_type: "joiner|mover|leaver|app-assignment|role-change|security-policy|routing-policy|conditional-access|idp|directory-store|domain"
subject_alias: "<non-PII ticket reference>"
subject_class: "employee|contractor|service-admin|external-client|vendor"
authoritative_status_source: "<approved HR/business source>"
target_groups: ["<governed aliases>"]
target_apps: ["<app aliases>"]
privilege_level: "standard|sensitive|admin"
security_model: "1.0|2.0|live-verification-required"
effective_policy_alias: "<live verified>"
effective_routing_policy_alias: "<live verified or not-applicable>"
conditional_access_result: "<live verified or not-applicable>"
downstream_owners: ["<roles>"]
approvals: ["<ticket references>"]
rollback_or_recovery: "<runbook reference>"
```

Do not store a real name, personal email, internal ID, MFA method, application record, or security-policy details in a public repository manifest.

## ONE-030 Organization, interfaces, and administrative roles

### ONE-031 Organization and UI variations

Official Zoho One help currently presents both Spaces UI and Unified UI steps. In Unified UI, many administrative actions begin in **Directory**; Spaces UI often uses a top-right administrative surface. Treat navigation labels as volatile. The underlying action, permission, target, and downstream consequence matter more than click coordinates.

Record the Zoho One organization/DC and selected application instance before changes. Adding an existing or new Zoho application account can be an irreversible association that requires Zoho support to unlink. Zoho specifically warns that selecting an existing versus new app account must be done carefully, and finance apps can require a currency decision while Sites/Mail/Backstage can require domain setup.

### ONE-032 Admin model

The documented role model includes:

| Role | Boundary | Control |
|---|---|---|
| Organization Owner | Highest organization ownership | Maintain continuity and a protected recovery path; do not use for routine operations |
| Organization Admin | Broad organization administration | Limit membership and monitor changes |
| Security Admin | Security 2.0 security, routing, conditional-access, IdP, and related user/group permissions | Migration/model dependent and highly privileged; review separately from general administration |
| Custom admin role | Selected Directory permissions and manageable apps/groups | Preferred for delegated least privilege |
| Service Admin | Manages activities in assigned application | Product-level authority; assigning/removing service-admin status does not necessarily remove app access |
| Application owner | Owner of an added app; also a service admin | Transfer before deactivation/offboarding |
| Creator App Admin/App Member | Custom-app-specific administrative/member model | Distinct from general Zoho One and Creator developer/user roles |

Zoho One lets organization owner/admin assign an admin role and constrain which applications and groups the admin can manage. System roles and custom roles differ; current help states only custom roles can be edited. Build custom roles from task requirements, not job title alone.

### ONE-033 Separation of duties

For GH/Sylvara:

- organization ownership and break-glass recovery should be separate from daily application administration;
- finance, signature, identity, and deployment privileges should not default to one broad role;
- a user who develops Creator apps should not automatically administer all identities or production finance apps;
- runtime OAuth clients/connections should be owned by durable organizational roles, not a departing person's account;
- service-admin assignment must have a reason, owner, expiration/review date, and downstream product validation.

## ONE-040 Identity object and field discovery

### ONE-041 User record

Zoho One user creation includes basic identity data and can include custom fields. A verified-domain email can allow direct addition; without an added/verified domain, the person receives an invitation that must be accepted. Current documentation states the invitation is valid for seven days. Verification status affects high-risk admin operations.

Do not assume email alone is the permanent business identity. Maintain an approved lifecycle key outside public files and inspect live fields such as:

- name/display name;
- primary and secondary email state;
- verified-domain and “Yet to Verify” status;
- active/deactivated status;
- department, location, designation, manager, employee identifier, or custom attributes if configured;
- group/department memberships and roles;
- applications and per-app settings;
- admin/custom roles and service-admin ownership;
- security/routing/conditional-access policies and exclusions, as applicable to the live model;
- directory-store source;
- sessions/account activity;
- license/user class, including any plan-specific user type.

`LIVE-DIRECTORY REQUIRED`: Available fields, required fields, custom field names, and authoritative HR mapping vary by tenant. Exporting or scripting user data is a privacy-sensitive operation.

### ONE-042 Verified domains and critical controls

Zoho documents domain-based restrictions for sensitive admin actions. For a user without a confirmed verified-domain email, admins can be prevented from resetting or enabling/disabling MFA, generating backup codes, creating a mailbox, or performing certain password operations. Adding a verified-domain email may remain pending until the user confirms it.

Never work around verification by changing a user's primary email solely to gain reset authority. Resolve domain ownership and identity proofing under security approval.

### ONE-043 Group types

Zoho One currently documents four useful group categories:

| Type | Behavior | Good use |
|---|---|---|
| Collaboration group | Flexible, ad hoc membership and optional mail/collaboration behavior | Cross-functional teams, controlled cohorts |
| Department | Organization-structure group; a user is generally a member of one department, with follower semantics for others | Primary organizational department |
| Smart group | Criteria-driven automatic membership | Attribute-based lifecycle and security rules |
| System-generated group | Read-only group created for a directory store | Policies/assignment for users sourced from that store |

Groups can provision app access and receive security policies. With Zoho Mail, groups can also have aliases. A moderator can manage membership/settings; a member is non-privileged; departments can include followers for secondary association.

Do not create overlapping groups without documenting purpose and precedence. A user's effective app settings and security components can depend on several assignments and priorities.

## ONE-050 Joiner, mover, and leaver lifecycle

### ONE-051 Joiner

1. Confirm the person's identity, classification, start date, manager, department/location, and authoritative approval.
2. Add/verify the organizational domain and email strategy before bulk onboarding.
3. Create or synchronize the user from the approved identity source.
4. Place the user in governed department/smart/collaboration groups.
5. Let conditional assignment provision standard apps and settings.
6. Manually approve sensitive/admin roles.
7. Apply the effective security/routing/conditional-access controls and require MFA enrollment.
8. Validate login, app access, correct role/profile, and absence of prohibited apps.
9. Record sanitized evidence and schedule access review.

### ONE-052 Mover

A department, job, location, or responsibility change must remove obsolete access as well as add new access.

1. Update authoritative attributes.
2. Preview smart-group and conditional-assignment effects.
3. Identify direct assignments that will not automatically follow group change.
4. Remove old service-admin/custom roles explicitly.
5. Transfer app/integration ownership if responsibility changes.
6. Recalculate effective security, routing, conditional-access, and IdP behavior under the live model.
7. Validate downstream product role, record sharing, folders, mail groups, and subscriptions.

### ONE-053 Leaver/deactivation

Current Zoho documentation says deactivation revokes Zoho One and associated-app access, frees the Zoho One license, and retains data in inactive state. Before deactivation, it directs admins to address admin roles, application ownership, active integrations, SAML apps, and directory-store ownership.

Critical caveat: Zoho explicitly warns that deactivating a user in Zoho One may not automatically deactivate the user in Directory or Non-Directory SAML applications. Those targets may require direct deactivation or working provisioning.

Safe offboarding:

1. Confirm approved effective time and legal/records hold.
2. Inventory owner/admin roles, OAuth connections, integrations, app ownership, directory stores, mailboxes, shared documents, scheduled reports, functions, and third-party SAML apps.
3. Transfer ownership and continuity dependencies first.
4. Revoke active sessions and high-risk credentials under policy.
5. Deactivate in Zoho One.
6. Reconcile every downstream app and third-party service.
7. Preserve/transfer records according to product and legal retention rules.
8. Verify license and access outcomes.
9. Record exceptions and complete a delayed reconciliation check.

Deletion, mailbox removal, document transfer, and legal retention are separate product/policy decisions. Do not interpret “deactivated” as “data erased.”

## ONE-060 Applications and assignment

### ONE-061 Application classes

Zoho One's official overview distinguishes:

- Zoho applications bundled/added to the organization;
- Marketplace/Directory applications with prebuilt SSO;
- Creator custom applications;
- Non-Directory applications configured manually, including SAML, OIDC, bookmarked, and associated/linked-sign-on patterns.

Availability, counts, plan dependencies, and supported provisioning differ. A launcher tile can be only a bookmark; it does not imply SSO, provisioning, or API integration.

### ONE-062 Assignment surfaces

Apps can be assigned to an individual, a group, or Everyone. Conditional assignment can apply rules to a group or the organization and filter users by criteria. Current documentation exposes controls for applying a condition to existing members and for overwriting manually assigned roles; both can cause broad changes and require preview/review.

Per-app settings vary. Zoho documents examples including:

- role;
- profile;
- department, team, or brand;
- department/team/brand role;
- chat access;
- product-specific settings such as WorkDrive role, Desk role/departments, or People role/location/designation/department.

Single-value and multi-value settings behave differently under conditional-assignment priority. `PRODUCT-METADATA REQUIRED`: Never invent a CRM profile, WorkDrive role, Desk department, Creator permission, or Books role from a generic Zoho One example.

### ONE-063 Assignment policy

Use an entitlement matrix:

| Cohort | Standard apps | Sensitive apps | Default product role | Approval |
|---|---|---|---|---|
| Owner/identity admins | Directory and emergency administration | All only when required | Least privilege plus break-glass | Owner + security review |
| GH operations | CRM, WorkDrive, approved operational apps | Books/Sign/Contracts as role requires | Non-admin operational roles | Business owner |
| Sylvara delivery | CRM/project/communication tools as approved | Client tenants and deployment systems by engagement | Project-scoped roles | Engagement owner |
| Developer | GitHub, sandbox/Creator/Catalyst development | Production and finance separated | Developer, not org owner | Technical + product owner |
| Contractor/vendor | Minimum time-bound apps | No default finance/identity admin | Restricted role | Sponsor + expiry |

This is a design template, not a live roster. Real cohorts and roles require approval.

### ONE-064 App requests

Users are not permitted by default to add/access every app; Zoho One supports app access requests for admin approval. Route requests through a purpose, data-classification, cost/license, role, and expiration review. Approval of an app does not automatically approve every role or data set within it.

## ONE-070 Conditional assignment and policy automation

Conditional assignment should derive standard entitlement from stable attributes/groups. Good conditions are understandable, mutually reviewed, and testable. Avoid using frequently edited display fields as hidden authorization policy.

For each rule document:

```yaml
rule_alias: "gh-operations-standard-apps-v1"
target_group: "<governed group alias>"
criteria: "<sanitized attribute logic>"
apps: ["CRM", "WorkDrive"]
app_settings: "<product-verified role aliases>"
apply_to_existing: false
overwrite_manual_roles: false
priority: "<live order>"
owner: "identity administrator"
test_cases: ["new match", "existing match", "no longer matches", "manual exception"]
```

Rules need tests for entry, removal, overlapping rules, existing members, manual overrides, and downstream provisioning failure. A successful Directory assignment is not enough; reconcile the target app account and exact role.

## ONE-080 Security policies

### ONE-081 Components

Zoho currently publishes help for both legacy Security 1.0 and updated Security 2.0. `SECURITY-MODEL REQUIRED`: inspect the authenticated tenant before interpreting a policy name, component, or priority.

| Model and surface | Controls | Priority behavior |
|---|---|---|
| Security 1.0 security policy | Password, MFA, allowed IPs, session management, and lock-period/advanced settings | Applicable policies can contribute different missing components by top-to-bottom priority |
| Security 2.0 security policy | Password policy, lock-period settings, and concurrent-session limit | One highest-priority security policy applies to a user |
| Security 2.0 routing policy | Password/passwordless/IdP authentication modes plus session lifetime and idle timeout | One highest-priority routing policy applies to a user |
| Security 2.0 conditional-access policy | Day/time, platform, routing policy, device-management state, IP, and country conditions with `Allow`, `Allow with MFA`, or `Deny` actions | Action evaluation and MFA-policy priority are separate from security/routing-policy priority |

Authentication and MFA choices also differ by model. Current Security 2.0 pages place passwordless methods and IdPs in routing policies and MFA challenges in conditional access. They document factors including OneAuth, OTP authenticator, security key, passkey, and SMS-based passwordless sign-in in the applicable surface. Prefer phishing-resistant methods for privileged users where operationally supported; SMS should not be the only privileged recovery factor.

In Security 1.0, the allowed-IP page requires static gateway IPs. In Security 2.0, IP address is a conditional-access condition and the current page documents current IP, static IP, and IP-range choices. Test from an alternate admin/recovery path before enforcement to avoid locking out the organization. Do not use an individual's changing home IP as an ungoverned permanent control.

The Security 1.0 session-management page defines web sessions as browser/device sign-ins, excludes native mobile apps from that documented web-session model, and says configured settings apply to sessions created after policy application. Security 2.0 separates concurrent-session limits into security policies and lifetime/idle settings into routing policies. Verify native-app and migration behavior in the live model rather than carrying the 1.0 rule forward.

### ONE-082 Priority and composition

In legacy Security 1.0, the default policy remains lowest priority and cannot be reordered, disabled, or deleted. When multiple policies apply, Zoho evaluates priority from top to bottom. If the highest applicable policy lacks a component, that component can come from the next applicable policy.

That component-wise composition rule is specific to Security 1.0. Under Security 2.0, only the highest-priority applicable security policy and the highest-priority applicable routing policy are assigned. Conditional-access evaluation checks matching `Allow` policies before `Allow with MFA` and then `Deny`; when multiple matching MFA policies apply, the first matching MFA policy by priority supplies the MFA configuration. If nothing matches, the configured default action applies.

Build test personas and record the model-specific result:

```text
security model/version
effective security policy
effective routing policy (Security 2.0)
matching conditional-access policies and resulting action (Security 2.0)
effective component sources (Security 1.0)
```

Removing, deactivating, excluding, migrating, or reordering a policy can change the effective result. Review before/after behavior for every affected cohort using the precedence rules of the live model.

### ONE-083 Privileged-user baseline

Recommended GH/Sylvara policy:

- dedicated admin identities where feasible;
- mandatory strong MFA, favoring OneAuth/hardware security key or TOTP over SMS;
- short/controlled trusted lifetime and sessions for privileged cohorts;
- allowed IP only where stable connectivity and recovery are proven;
- minimal concurrent sessions;
- separate emergency recovery process;
- quarterly privileged-access review and immediate leaver review;
- alert/audit review after MFA reset, policy change, IdP change, or new admin assignment.

These are security recommendations, not claims of current tenant configuration.

## ONE-090 Custom authentication and SSO

### ONE-091 Direction matters

Two different SSO directions exist:

1. **Inbound authentication to Zoho One:** An external identity provider authenticates Zoho One users through the legacy Custom Authentication or current Identity Providers/Routing Policies surface.
2. **Outbound SSO from Zoho One to an application:** Zoho One/Directory acts as identity provider or launcher for a third-party app using a configured Directory/Non-Directory integration.

Do not confuse either with Zoho API OAuth. SSO authenticates a user session; OAuth authorizes API access; SCIM provisions identities.

### ONE-092 Inbound custom authentication

Zoho One documents SAML and JWT inbound authentication in two administrative models. Legacy Security 1.0 calls the surface Custom Authentication and applies IdPs to selected groups or all users with exclusions and priority. Security 2.0 separates Identity Providers from Routing Policies; the routing policy decides which users can use an IdP authentication mode. In either model, users can enter their email at Zoho and be redirected to the applicable IdP, or initiate from the IdP. Determine the live model before following labels or priority rules.

Operational controls:

- verify ACS/entity/audience, sign-in/sign-out URL, NameID/user mapping, and certificate/signing algorithm from current live pages;
- keep a tested organization-owner recovery route before activation;
- use a pilot group, then broaden;
- model IdP/routing-policy priority and exclusions under the live security version;
- monitor certificate expiry and rotate before it lapses;
- test IdP-initiated and service-provider-initiated login, logout, MFA, failure, and deactivated user;
- do not delete/deactivate an IdP until affected users have a proven alternative.

Zoho's IdP guidance says the SSO protocol cannot be switched after creation; replacing SAML with JWT or vice versa requires a controlled replacement path. In legacy Security 1.0, the Default IdP has special behavior and cannot be treated like an ordinary group-scoped IdP.

### ONE-093 Outbound SAML/OIDC and launcher apps

Zoho One can add non-directory SSO apps. Current OIDC guidance describes Zoho One as the OpenID Provider and supplies the third-party relying party with client ID/secret and authorization, token, and user-info endpoints. Treat those credentials as secrets and use the app-specific configuration shown in the live tenant.

Other non-directory patterns include SAML apps, bookmarks, and associated apps inheriting a parent app's linked sign-on. A bookmark provides navigation, not identity federation. Validate SSO and provisioning independently.

## ONE-100 Provisioning and directory stores

### ONE-101 Three separate flows

| Flow | Direction | Purpose |
|---|---|---|
| Directory store import/sync | External directory/HR source → Zoho One | Create/update/status-sync organizational users |
| Application provisioning | Zoho One → third-party/Zoho app | Create/update/deactivate downstream accounts |
| SSO | User ↔ IdP/service provider | Authenticate interactive access |

One can work while another fails. Reconcile all three.

### ONE-102 Directory stores

Zoho One can integrate external directories and sources. Official pages describe SCIM and provider API integrations, field mapping, password/notification behavior, status sync, criteria, manual import, and scheduled sync. System-generated read-only groups identify users from a store.

An inbound SCIM setup exposes a generated Sync Endpoint and SCIM token for the external identity system. Those are credentials. Never place them in GitHub, chat, a PDF, browser screenshots, or a general integration log. Rotate/recreate according to the supported admin flow after exposure.

Before enabling status sync, decide source-of-truth direction. A careless status mapping can deactivate organizational access. Test create, update, rename, disable, re-enable, deletion behavior, duplicate matching, unverified domains, missing attributes, and rollback with synthetic users.

### ONE-103 Outbound application provisioning

Zoho One's provisioning overview states it can manage users for apps that support SCIM or have an API for user management. This does not mean Zoho One exposes a general programming API to all application data. It means configured connectors can call the downstream user-management interface.

For each connector capture:

- app/tenant instance and owner;
- protocol: SCIM or provider-specific API;
- endpoint alias and credential-store owner;
- supported operations (create/update/deactivate/delete/group);
- user matching key and attribute map;
- assignment/role map;
- failure and retry behavior;
- deprovisioning semantics and licensing effect;
- audit/monitoring evidence;
- manual reconciliation path.

Never assume deactivation equals deletion, group push is supported, or all attributes round-trip. Test the exact connector.

### ONE-104 Public API boundary

At this research cutoff, the official sources reviewed for this handbook did not expose a general, public, supported raw REST reference for arbitrary administration of Zoho One users, groups, policies, app assignments, and audit logs. Do not invent `/zohoone/...` endpoints or OAuth scopes, and do not treat an `href` returned by a wrapper as permission to call an undocumented endpoint.

Zoho does publish bounded Deluge integration tasks. For example, `zoho.one.addUser` documents `ZohoOne.Users.CREATE`, and `zoho.one.addUserToGroup` documents `ZohoOne.Groups.CREATE,ZohoOne.Groups.UPDATE`; both require the live organization/user/group data and a Zoho One connection. Their current pages exclude calls from Zoho Creator and say each execution that receives a response consumes an external call from the invoking service according to its plan. Those exact wrappers and scopes are supported only as their current task pages describe. They do not establish a universal REST contract or authorize inference of adjacent endpoints, fields, or scopes.

Zoho separately publishes parallel `zoho.directory.*` wrappers with `ZohoDirectory.*` scopes. For example, the Directory add-user and add-user-to-group tasks require `ZohoDirectory.Users.CREATE` and `ZohoDirectory.Groups.CREATE,ZohoDirectory.Groups.UPDATE`, respectively. Do not mix a `zoho.one` task/connection with a `ZohoDirectory` scope, or a `zoho.directory` task/connection with a `ZohoOne` scope.

Supported automation documented here consists primarily of:

- UI/admin operations;
- conditional assignment and smart groups;
- documented Zoho One/Directory Deluge integration tasks and their exact connection scopes;
- directory-store SCIM/API connectors;
- application provisioning connectors;
- product-specific APIs;
- supported SSO protocols.

If Zoho later publishes a general raw admin API reference, add it only after reviewing official authentication, scopes, schemas, limits, DCs, and audit behavior.

## ONE-110 Domains, email identity, and sender governance

Zoho One can add and verify organization domains, using DNS records or supported DomainConnect flows. Current status concepts include ownership verification and email-authentication status (`VERIFIED`, `AUTHENTICATED`, `PARTIALLY AUTHENTICATED`, and related states). Zoho documents centralized sender email and sync of some domain/DKIM verification information across associated services.

Domain changes are high risk because they can affect:

- verified-user status and admin recovery powers;
- Mail hosting, mailboxes, aliases, and MX routing;
- group email aliases;
- sender addresses, SPF, and DKIM;
- service-level domain/sender validation;
- app access tied to the domain.

Zoho warns that deleting a domain can stop custom addresses/group aliases receiving mail and remove synchronized settings across services; some sender addresses in individual services may not be deleted automatically. Never delete or reverify a domain as a troubleshooting shortcut.

Maintain a controlled DNS/domain registry with owner, registrar/DNS provider, verification state, mail host, SPF/DKIM/DMARC governance, sender use, renewal, and rollback. Store no secret verification values in public GitHub.

## ONE-120 Observability, reports, and access reviews

Zoho One's Audit Logs view records prior account activity by activity type, affected user, and timestamp. Product apps have their own audit/log/report surfaces. A Directory log does not replace CRM setup audit, Books audit trail, Sign evidence, Creator audit/logs, Mail audit, Catalyst logs, or third-party IdP/provisioning logs.

### ONE-121 Evidence model

For every privileged change preserve:

```yaml
change_id: "<ticket>"
change_class: "identity|assignment|admin|policy|idp|provisioning|domain"
actor_role: "<sanitized>"
target_alias: "<sanitized>"
approved_at: "<timestamp>"
executed_at: "<timestamp>"
before_state_hash: "<sanitized manifest hash>"
after_state_hash: "<sanitized manifest hash>"
directory_audit_verified: true
downstream_reconciled: true
exceptions: []
review_due: "<date>"
```

Do not export raw user activity to a public repository. Store sensitive audit evidence in the approved restricted system and link only a non-sensitive ticket/evidence identifier.

### ONE-122 Review cadence

- Monthly: failed provisioning, inactive/duplicate users, unowned apps/integrations, expiring IdP certificates.
- Quarterly: admins, service admins, privileged apps, contractors, direct assignments, security-policy exceptions, OAuth/Connected Apps ownership.
- On every mover/leaver: direct and group-derived access, product role, SAML/third-party account, sessions, tokens, ownership, mailbox/files.
- After policy/rule changes: test personas for every overlap and priority branch.

## ONE-130 Testing strategy

### Identity and groups

- Verified-domain and external invited-user flows behave as documented.
- Duplicate email/identity collision fails safely.
- Smart-group entry and exit follow criteria.
- Department member/follower behavior matches product sync requirements.
- A store-sourced user's status change has the intended direction.

### App assignment and provisioning

- Individual, group, and conditional assignments yield expected downstream accounts.
- Existing-member and overwrite-manual-role options are tested separately.
- Single-value and multi-value app settings resolve correctly under priority.
- Removing a condition removes or retains downstream access exactly as approved.
- Provisioning failure produces alert and reconciliation, not silent partial access.

### Security and authentication

- The live Security 1.0/2.0 model is identified, and effective security, routing, conditional-access, MFA, IP, and session outcomes are calculated under that model.
- Organization owners retain a tested emergency path before IP/IdP enforcement.
- SAML/JWT/OIDC flows test sign-in, logout, deactivation, certificate/secret failure, and wrong user mapping.
- Session rules are tested on new sessions, acknowledging the documented timing behavior.
- MFA reset/disable requires correct role, re-authentication, verification state, and audit evidence.

### Offboarding

- User loses Zoho access at expected time.
- Third-party SAML and non-directory apps are independently verified.
- App/integration/store ownership has moved.
- Mail/files/records follow approved retention and transfer.
- License status and audit records reconcile.

Never test with a real employee termination, tenant portal access, payment authority, or lease/signature action without an approved test plan.

## ONE-140 GH Real Estate and Sylvara operating patterns

### ONE-141 Keep internal identity separate from tenants and clients

Zoho One workforce users should be GH/Sylvara staff, approved contractors, and administrators. Tenants, applicants, and property vendors should not automatically become full Zoho One users merely to access the tenant experience. Use the approved Creator portal/client model, Sites entry point, CRM records, and product-specific external-user mechanism.

Zoho One also documents Portals for external clients and app assignment, but adoption must be an explicit architecture decision. Do not create a second competing tenant identity plane without comparing Creator portal roles, data isolation, lifecycle, license, and support implications.

### ONE-142 Minimum viable governance for current scale

GH currently has a small operating footprint, so avoid elaborate identity bureaucracy. The minimum high-value controls are:

1. Protect organization owner and verify recovery.
2. Require strong MFA.
3. Verify business domains and email authentication.
4. Define a small number of role-based groups: identity admins, GH operations, Sylvara delivery/development, finance/signature privileged, and time-bound contractors if needed.
5. Assign standard apps by group; review privileged apps manually.
6. Keep production OAuth/integration ownership durable.
7. Use a single joiner/mover/leaver checklist and quarterly access review.
8. Record only sanitized policy/runbook material in GitHub.

### ONE-143 App catalog from the current GH/Sylvara suite

The screenshot-supplied suite includes API Console, Billing, Bookings, Books, Catalyst, Calendar, Checkout, Contracts, Creator, CRM, Flow, Forms, Mail, Meeting, Zoho One, Payments, People, Sign, Sites, ToDo, Voice, and WorkDrive. This is an observed desired documentation/app inventory, not proof of tenant assignment, license, configuration, or use.

Zoho One should govern workforce assignment to those apps. Individual handbooks govern product APIs and business-system design. Calendar, Meeting, People, ToDo, and Voice require their own product knowledge bases; this Zoho One document covers only their suite-level entitlement boundary.

## ONE-150 Implementation checklist

### Baseline inventory

- [ ] Organization/DC, owner, admins, custom roles, service admins inventoried privately.
- [ ] Verified domains, sender identity, mail host, and DNS owners documented.
- [ ] Users, user classes, source directory, and verification states reconciled.
- [ ] Groups/departments/smart groups have purpose and owner.
- [ ] Applications, linked instances, owners, roles, assignments, and plan dependencies reviewed.
- [ ] IdPs, security/routing/conditional-access policies, directory stores, provisioning connectors, and certificates inventoried.
- [ ] OAuth clients/connections and integrations have durable owners.

### Secure configuration

- [ ] Strong MFA enforced for all eligible users and stricter for admins.
- [ ] Security 1.0/2.0 is identified, and the applicable component-composition or single-policy/conditional-access priority behavior is tested.
- [ ] Emergency owner/recovery access tested before IP or IdP restriction.
- [ ] Admin/custom/service roles are least privilege.
- [ ] Standard app assignment uses governed groups/conditions.
- [ ] Privileged app roles require manual approval.
- [ ] SCIM/API/SAML/OIDC secrets and certificates are stored securely and monitored.

### Lifecycle and operations

- [ ] Joiner/mover/leaver runbooks cover downstream apps and ownership.
- [ ] SAML/non-directory deactivation is reconciled separately.
- [ ] Direct assignments and exceptions have review/expiry dates.
- [ ] Provisioning failures alert and have a manual repair path.
- [ ] Directory audit and product audit evidence are both preserved appropriately.
- [ ] Quarterly access review and certificate/credential review scheduled.
- [ ] Domain deletion, app unlinking, and organization-owner changes require enhanced change control.

## ONE-160 Anti-patterns

- Treating Zoho One as a universal REST API for all Zoho products.
- Giving every user every app because the suite is licensed.
- Using organization owner for daily development or integration ownership.
- Assigning service admin when a normal product role is enough.
- Building dozens of overlapping groups without priority/purpose documentation.
- Enabling “apply to existing” or “overwrite manual roles” without impact preview.
- Assuming Zoho One deactivation removes every SAML/third-party account.
- Activating custom authentication without a pilot and recovery owner.
- Enforcing IP restrictions before validating network conditions and emergency access.
- Storing SCIM token, IdP secret, certificate private key, DNS value, user export, or audit log in GitHub.
- Treating a launcher bookmark as SSO or provisioning.
- Using tenants/applicants as workforce users by default.
- Deleting a domain or unlinking an app to troubleshoot synchronization.

## ONE-170 Official source registry

All sources below are official Zoho properties.

### Core administration, users, admins, and groups

1. [Zoho One Admin Guide](https://help.zoho.com/portal/en/kb/one/admin-guide)
2. [Users knowledge base](https://help.zoho.com/portal/en/kb/one/admin-guide/users)
3. [Add a user](https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/zohoone-adding-a-user)
4. [Deactivate users](https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/zohoone-deactivate-users)
5. [Manage user email addresses](https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/manage-email-address)
6. [Reset user password and verified-domain restrictions](https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/reset-nonemployee-password)
7. [Admins and roles knowledge base](https://help.zoho.com/portal/en/kb/one/admin-guide/admins)
8. [Assign admins](https://help.zoho.com/portal/en/kb/one/admin-guide/admins/articles/zohoone-assign-admins)
9. [Manage roles for an admin](https://help.zoho.com/portal/en/kb/one/admin-guide/admins/articles/manage-roles-for-an-admin)
10. [Service admins](https://help.zoho.com/portal/en/kb/one/admin-guide/admins/articles/service-admins)
11. [Creator App Admin and App Member](https://help.zoho.com/portal/en/kb/one/admin-guide/admins/articles/app-admin-and-app-member-in-zoho-creator-zoho-one)
12. [Groups overview](https://help.zoho.com/portal/en/kb/one/admin-guide/groups/articles/zohoone-groups-overview)
13. [Add users to a group or department](https://help.zoho.com/portal/en/kb/one/admin-guide/groups/articles/zohoone-add-members)

### Applications, assignment, and provisioning

14. [Applications overview](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/adding-applications/articles/zohoone-adding-apps-overview)
15. [Add a Zoho app](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/adding-applications/articles/zohoone-add-zoho-app)
16. [Assign app to an individual](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/managing-applications/articles/zohoone-assign-app-individually)
17. [Assign app to a group](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/managing-applications/articles/zohoone-assign-app-to-group)
18. [Assign apps using conditions](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/configuring-conditional-assignment/articles/assign-apps-using-conditions)
19. [Application settings](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/managing-applications/articles/application-settings)
20. [Provisioning overview](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/configuring-provisioning/articles/provisioning-overview)
21. [Directory Stores overview](https://help.zoho.com/portal/en/kb/one/admin-guide/directory-stores/cloud-directories-general-guides/articles/directory-stores-overview-zoho-one)
22. [Add Okta directory store](https://help.zoho.com/portal/en/kb/one/admin-guide/directory-stores/cloud-directories-app-specific-configuration-guides/articles/add-okta-to-zoho-one)
23. [Add JumpCloud directory store](https://help.zoho.com/portal/en/kb/one/admin-guide/directory-stores/cloud-directories-app-specific-configuration-guides/articles/add-jumpc)

### Authentication and security

24. [Legacy Security 1.0 policies overview](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-1-0/articles/zohoone-security-policies-overview)
25. [Legacy Security 1.0 policy priority](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-1-0/articles/zohoone-security-policy-priority)
26. [Legacy Security 1.0 password policy](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-1-0/articles/zohoone-configure-password-policy)
27. [Legacy Security 1.0 MFA](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-1-0/articles/zohoone-configure-mfa)
28. [Legacy Security 1.0 allowed IPs](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-1-0/articles/zohoone-allowed-ips)
29. [Legacy Security 1.0 session management](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-1-0/articles/zohoone-configure-session-management)
30. [Legacy Security 1.0 policies for users](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-1-0/articles/zohoone-security-policies-for-users)
31. [Legacy Custom Authentication overview](https://help.zoho.com/portal/en/kb/one/admin-guide/security/custom-authentication/articles/zohoone-customauthentication)
32. [Legacy Custom Authentication IdP details](https://help.zoho.com/portal/en/kb/one/admin-guide/security/custom-authentication/articles/edit-idp-details)
33. [OIDC in Zoho One](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/adding-applications/articles/using-open-id-connect-oidc-in-zoho-one)
34. [Add non-directory OIDC app](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/adding-applications/articles/adding-an-oidc-app)
35. [Bookmarked and associated apps](https://help.zoho.com/portal/en/kb/one/admin-guide/applications/adding-applications/articles/zohoone-add-non-directory-apps)

### Domains and evidence

36. [Domains overview](https://help.zoho.com/portal/en/kb/one/admin-guide/domains/articles/zohoone-domains-overview)
37. [Add and verify domain](https://help.zoho.com/portal/en/kb/one/admin-guide/domains/articles/zohoone-domains-verify-domain)
38. [Sender email overview](https://help.zoho.com/portal/en/kb/one/admin-guide/domains/articles/sender-email-overview)
39. [Domain sync between Zoho services and Zoho One](https://help.zoho.com/portal/en/kb/one/admin-guide/domains/articles/domain-sync-between-zoho-services-and-zoho-one)
40. [Delete domain](https://help.zoho.com/portal/en/kb/one/admin-guide/domains/articles/zohoone-domains-delete-domain)
41. [View audit logs](https://help.zoho.com/portal/en/kb/one/admin-guide/reports/audit-logs/articles/view-audit-logs-zo)

### Current Security 2.0 and bounded automation

42. [Security 2.0 knowledge base](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-2-0)
43. [Security 2.0 policy overview](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-2-0/articles/security-policy-overview-zo)
44. [Security 2.0 security-policy priority](https://help.zoho.com/portal/en/kb/one/admin-guide/managing-security/security-policy-new/articles/reorder-security-policy-zo)
45. [Security 2.0 routing-policy overview](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-2-0/articles/routing-policy-zo)
46. [Security 2.0 routing-policy priority](https://help.zoho.com/portal/en/kb/directory/admin-guide/security/security-2-0/articles/reorder-routing-policy)
47. [Security 2.0 conditional-access overview](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-2-0/articles/conditional-access-overview-one)
48. [Security 2.0 conditional-access and MFA priority](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-2-0/articles/reorder-mfa-policies-zo)
49. [Security 2.0 add an IdP](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-2-0/articles/add-idp-zo)
50. [Security Admin role](https://help.zoho.com/portal/en/kb/one/admin-guide/security/security-2-0-migration/articles/security-admin-zo)
51. [Deluge `zoho.one.addUser`](https://www.zoho.com/deluge/help/one/add-user.html)
52. [Deluge `zoho.one.addUserToGroup`](https://www.zoho.com/deluge/help/one/add-user-to-a-group.html)
53. [Deluge `zoho.directory.addUser`](https://www.zoho.com/deluge/help/directory/add-user.html)
54. [Deluge `zoho.directory.addUserToGroup`](https://www.zoho.com/deluge/help/directory/add-user-to-a-group.html)

### Portals and app-request controls

55. [Unified Client Portal overview](https://help.zoho.com/portal/en/kb/one/admin-guide/portals/overview/articles/unified-client-portal-overview)
56. [Allow users to raise an app request](https://help.zoho.com/portal/en/kb/one/admin-guide/controls/articles/grant-permission-to-raise-app-request)

## ONE-180 Explicit research gaps

1. `LIVE-DIRECTORY REQUIRED`: No authenticated GH/Sylvara Zoho One tenant was inspected. Owner/admin roster, users, groups, departments, smart criteria, app assignments, Security 1.0/2.0 migration state, policies, IdPs, directory stores, domains, and audit events remain unknown.
2. `PLAN/REGION VOLATILE`: Plan, license model, lite/external user options, app availability, directory count, non-Zoho app limits, and UI navigation require live verification.
3. `PRODUCT-METADATA REQUIRED`: Zoho One does not document one universal set of application roles or fields. Each current product tenant controls role/profile/team/department configuration.
4. No general public supported raw Zoho One administration REST reference was found in the official sources reviewed. Bounded `zoho.one.*` and `zoho.directory.*` Deluge tasks exist; use only each task's documented wrapper, connection type, and exact scope, and do not infer raw or adjacent endpoints. Otherwise use documented Directory/provisioning/SSO capabilities and product APIs.
5. The authoritative HR/person lifecycle source for GH/Sylvara, admin recovery owners, privileged-access approval matrix, contractor expiration policy, and records-retention rules remain business/security decisions.
6. External-client Portals exist in Zoho One, but their suitability versus the approved Creator tenant portal is unresolved and requires an architecture/licensing/data-isolation comparison.
7. The desired app screenshot shows Calendar, Meeting, People, ToDo, and Voice, which require separate product/API handbooks; this document covers only central entitlement and identity governance for them.

---

**Maintenance rule:** Revalidate after Zoho One/Directory UI or plan changes, Security 1.0/2.0 migration, identity-provider or certificate changes, a new directory/provisioning connector, domain/mail migration, security-policy redesign, organization-owner change, access incident, or any new public admin API documentation.
