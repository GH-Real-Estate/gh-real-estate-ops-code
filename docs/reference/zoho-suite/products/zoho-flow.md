# Zoho Flow — Automation, Integration, and Governance Knowledge Base

**Document ID:** GH-ZOHO-FLOW-KB  
**Research cutoff:** 2026-07-20  
**Audience:** ChatGPT, Codex, integration architects, implementers, reviewers, and operators for GH Real Estate and Sylvara  
**Source policy:** Official Zoho product, help, pricing, security, and release-note pages only  
**Safety posture:** Examples use placeholders. Never place credentials, tokens, tenant IDs, customer data, or production webhook URLs in source control.

## 1. How an AI should use this document

Treat each statement according to its evidence label:

| Label | Meaning | Required behavior |
|---|---|---|
| **OFFICIAL** | Directly supported by an official source in the registry | May be used, subject to edition and date checks |
| **LIVE-METADATA REQUIRED** | Depends on the organization's data center, plan, connector version, permissions, enabled features, or current field/action metadata | Retrieve and inspect the live tenant metadata before implementation; do not guess |
| **VOLATILE** | Pricing, quotas, polling intervals, UI, or release behavior can change | Recheck the linked official page on the day of design/deployment |
| **INFERENCE** | Recommended architecture derived from official capabilities and GH/Sylvara controls | Present as a design recommendation, not a Zoho guarantee |
| **UNDOCUMENTED** | No authoritative public contract was located | Do not invent an endpoint, scope, retry rule, field, or guarantee |

AI execution rules:

1. Discover the organization data center, plan, roles, connector version, and connection owner before generating a deployable design.
2. Use application metadata and sample payloads from a non-production tenant. Never guess field API names or enum values.
3. Design every automation around a stable business key, replay safety, data minimization, least privilege, and an operator-visible failure path.
4. Do not describe Zoho Flow as a system of record. It orchestrates work; CRM, Books, Contracts/Sign, Creator, WorkDrive, and other domain products own their records.
5. Do not claim there is a documented public REST API for creating, updating, exporting, or deploying Flow definitions. None was located in the official public documentation reviewed for this edition.
6. Recheck the current Flow release notes and plan page because capabilities and limits change frequently.

## 2. Product role and system boundary

**OFFICIAL:** A Flow consists of a trigger followed by one or more actions. A trigger can be an application event, a schedule, an incoming webhook, or a polled URL. Actions can call applications, send webhooks, delay execution, branch on conditions, set variables, or execute Deluge custom functions. A connection authorizes Flow to use a specific external or Zoho account. The builder configures a flow; Summary exposes its configuration; History exposes execution steps, inputs, and outputs for troubleshooting.

**INFERENCE — approved role for GH/Sylvara:** Use Flow for lightweight, observable cross-application orchestration where connector semantics are sufficient. Good uses include intake routing, notifications, non-destructive synchronization, task creation, document-workflow initiation, and reporting handoffs.

**INFERENCE — boundaries:**

- CRM owns leads, contacts, applicants, deals/opportunities, and relationship workflow state.
- Books owns customers/vendors only insofar as needed for accounting, and owns invoices, payments, credits, and ledger truth.
- Contracts and Sign own agreement and signature workflow state.
- WorkDrive owns managed documents and their access controls.
- Creator owns approved custom operational applications and portals.
- Analytics owns derived reporting models, not operational truth.
- Sites and Forms are public entry/intake surfaces, not authoritative transaction stores.
- Catalyst or a controlled service should handle complex, high-risk, high-volume, stateful, or security-sensitive logic that exceeds Flow's observable connector model.

Do not use Flow as a hidden database, an unreviewed financial posting engine, or a two-way synchronization hub without loop prevention and reconciliation.

## 3. Core execution model

### 3.1 Trigger

A trigger starts a new execution. Trigger categories and safe use:

| Trigger type | Official behavior | Design implications |
|---|---|---|
| Application trigger | Starts when a supported app event occurs; exact events depend on connector | Inspect event payload and connector version in a sandbox |
| Scheduled trigger | Starts on configured schedule | Use checkpoint keys and bounded windows; scheduling is not proof that data exists |
| Webhook trigger | Unique Flow URL receives JSON, form data, or plain text; arrays may execute once per element | Authenticate at the source when possible; validate schema; deduplicate |
| URL trigger | Polls a GET endpoint returning JSON or XML; select extraction path and a stable unique key | API should return reverse-chronological items; choose immutable event key; allow overlap |

**OFFICIAL:** A newly activated polling/application flow processes new changes; it does not automatically replay historical records. Polling cadence depends on plan and connector. The official troubleshooting page warns that a flow can be switched off after 20 consecutive failures.

### 3.2 Actions and logic elements

The builder supports app actions and logic elements including:

- **Set Variable:** normalize or derive a value for later steps.
- **Decision:** evaluate conditions; condition groups support AND/OR logic.
- **Delay For / Delay Until:** pause an execution. Do not use a long delay as a durable business-state system; persist meaningful state in the owning application.
- **Send Email:** operational messaging. Prefer the company's governed mail path for regulated or customer-critical communications.
- **Custom Function:** execute Deluge with typed inputs and return value.
- **Outgoing Webhook:** invoke an external HTTP API.

**OFFICIAL:** Successful actions consume tasks. Trigger execution, decisions, and setting variables do not consume tasks. A successful custom-function execution does consume a task. Task allocations reset monthly and do not roll over.

### 3.3 Custom functions

Flow custom functions use Deluge and can be reused across the organization.

| Item | Contract |
|---|---|
| Function name | Starts with a letter or underscore; then letters, numbers, or underscores |
| Input/return types | `int`, `float`, `string`, `bool`, `date`, `map`, `list`, `file`; `void` is a return type, not an input type |
| Lifecycle | Deleting a shared function can break dependent flows; inventory dependencies first |
| Current constraint | Release notes report a 2 MB string-count limit for Deluge function processing; **VOLATILE**—verify live |

Custom-function contract pattern:

```text
Input map:
  source_system: string
  event_id: string
  record_id: string
  event_time_utc: string
  payload: map

Output map:
  outcome: "processed" | "duplicate" | "rejected" | "retryable_error"
  correlation_id: string
  target_record_id: string | null
  reason_code: string | null
```

**INFERENCE:** Keep functions deterministic where possible. Do not embed secrets in source. Use a named connection for authenticated `invokeurl` calls. Validate nulls and types explicitly because connector payloads can omit optional values.

## 4. Connections, authentication, and data centers

### 4.1 Connection lifecycle

**OFFICIAL:** Connections are private by default. Sharing makes a connection available organization-wide. Unsharing does not break flows that already use it. Connections can be tested, reconnected, shared/unshared, transferred, or deleted. Deleting a connection causes dependent flows to fail. If a member is removed without transferring connections, flows using those connections can be disabled.

Operational rules:

- Use service identities where vendor terms and security policy allow; do not anchor production to a departing employee.
- Name connections by environment, system, permission class, and owner role, for example `prod_crm_lead_write_integration_owner`.
- Document granted scopes and the exact flows that use the connection.
- Transfer/re-authorize connections as a controlled change. The recipient may need to reauthorize.
- Rotate credentials or revoke access through the upstream system and reconnect, then test all dependents.
- Never share a broad connection simply to fix a permission error. Reduce the permission to the minimum action set.

### 4.2 Outgoing webhook authentication

**OFFICIAL:** An outgoing webhook can use `GET`, `POST`, `PUT`, `PATCH`, or `DELETE`. Available authentication modes include no authentication, Basic, OAuth 1a, OAuth 2, and API key. Auth Profiles and custom Connections can manage credentials and refresh OAuth tokens. Configuration includes URL, method, content type, headers/parameters/body, and response handling; XML or automatic response parsing can be transformed for downstream steps, and response headers may be included.

Generic request model:

```http
POST https://api.example.invalid/v1/resources
Authorization: <provided by named Flow connection>
Content-Type: application/json
Idempotency-Key: {{source_system}}:{{event_id}}
X-Correlation-Id: {{correlation_id}}

{
  "external_reference": "{{stable_business_key}}",
  "status": "{{validated_status}}",
  "occurred_at": "{{event_time_utc}}"
}
```

The idempotency header above is only valid if the target API documents it. Otherwise implement a lookup-before-create or an integration-ledger pattern. Do not assume Flow itself adds an idempotency key.

### 4.3 Incoming webhook behavior

**OFFICIAL:** Flow generates a unique incoming webhook URL. The trigger accepts JSON, form data, and plain text; XML is treated as plain text. A JSON array can cause an execution per array element. Nested data can be extracted, and request headers may optionally be captured. The designer can configure a custom acknowledgement.

Security design:

- Treat the webhook URL as a secret capability URL, but do not rely on secrecy alone.
- If the sender supports signatures, validate them in a controlled service before forwarding to Flow unless Flow's current trigger provides an explicitly documented verifier.
- Do not claim native webhook-signature verification unless the live connector/trigger documents it.
- Require a timestamp and stable event ID; reject stale events in a controlled validation layer when risk warrants it.
- Return a fast acknowledgement and move stateful/high-latency work to a queue or Catalyst for critical workloads.

### 4.4 Data-center domains

**OFFICIAL / LIVE-METADATA REQUIRED:** Official Flow help lists regional domains including:

| Region | Flow domain |
|---|---|
| United States | `flow.zoho.com` |
| European Union | `flow.zoho.eu` |
| India | `flow.zoho.in` |
| Australia | `flow.zoho.com.au` |
| China | `flow.zoho.com.cn` |
| Japan | `flow.zoho.jp` |
| Canada | `flow.zohocloud.ca` |
| Saudi Arabia | `flow.zoho.sa` |

Use the tenant's actual domain and the service's returned OAuth/API location. Do not mechanically change top-level domains or move tokens across regions. Official IP allowlists are **VOLATILE**; obtain the current list from the linked allowlist page and update firewalls through change control.

## 5. URL triggers and polling design

The URL trigger issues `GET` and can parse JSON or XML. Configure the extraction path to the repeating records and choose a unique key that is stable across polls. A source endpoint should preferably return newest records first.

Recommended source response:

```json
{
  "events": [
    {
      "event_id": "evt_example_0001",
      "event_type": "lease.status.changed",
      "occurred_at": "2026-01-15T18:42:00Z",
      "record_reference": "lease_example_001",
      "version": 7
    }
  ],
  "next_cursor": "opaque_example_cursor"
}
```

Flow's URL-trigger UI—not this example—determines which pagination/cursor options are available. **UNDOCUMENTED:** Do not assert arbitrary cursor pagination support. If a source requires multi-page traversal or complex checkpointing, poll from Catalyst/a controlled worker and emit discrete webhook events to Flow.

## 6. Reliability, errors, retries, and replay

### 6.1 Diagnostics

**OFFICIAL:** Execution History exposes step inputs and outputs. Use it to locate the first failed action. Common categories include:

| Symptom | Likely class | Operator action |
|---|---|---|
| HTTP 400 / mandatory field | Schema or validation | Compare live metadata, payload type, allowed values, and required fields |
| HTTP 401 | Expired/revoked/mis-scoped connection | Test and reconnect; verify identity and scopes |
| Type/date mismatch | Mapping/format | Normalize in a Set Variable/custom function; use ISO timestamps where target permits |
| HTTP 408/504 | Timeout | Let eligible retry policy run; confirm whether target may have committed before timeout |
| HTTP 409 | Conflict | Inspect target semantics; may be duplicate/version conflict, not automatically harmless |
| HTTP 429 | Rate limit | Respect service limits; reduce concurrency/batch; allow retry policy |
| HTTP 500/503 | Service fault | Retry only with replay-safe design; monitor vendor status |

### 6.2 Automatic and manual rerun

**OFFICIAL / VOLATILE:** Professional-plan documentation describes automatic rerun for internal/dependent-service errors and HTTP `408`, `409`, `429`, `500`, `503`, and `504`. The documented schedule is up to eight attempts after approximately 5 minutes, 10 minutes, 30 minutes, 1 hour, 3 hours, 6 hours, 12 hours, and 24 hours. Verify current plan behavior.

Automatic rerun resumes at the failed action; the trigger is not rerun. If configuration is edited before a pending retry, the future retry uses the edited configuration. Manual History controls include **Resume** and **Restart**. Restarting the entire execution can repeat successful side effects and cause duplicates. The official page documents selecting up to 100 executions for manual rerun at once.

Replay-safe sequence:

1. Derive `correlation_id` and `idempotency_key` from the immutable source event.
2. Check a target external-reference field or integration ledger.
3. Create only if absent; otherwise compare version and decide update/no-op.
4. Persist target ID and outcome in the owning system or controlled ledger.
5. Send notification after the committed operation, not before it.
6. On manual restart, verify which prior steps already committed.

### 6.3 Timeout ambiguity

A timeout does not prove the remote operation failed. The server may have committed and lost the response. Therefore:

- Never immediately create again without a stable external-key lookup.
- Use target-supported idempotency keys when explicitly documented.
- For financial or signature actions, query current target state before retry.
- Route ambiguous outcomes to reconciliation rather than silently continuing.

## 7. Limits, editions, and task economics

**VOLATILE:** The official pricing page at the cutoff showed Free, Standard, and Professional capabilities, including these representative limits:

| Capability | Free | Standard | Professional |
|---|---:|---:|---:|
| Included tasks/month | 100 | Starts at 5,000 | Starts at 10,000 |
| Flow count | 5 | Current page lists unlimited | Current page lists unlimited |
| History retention | 30 days | 60 days | 90 days |
| Polling | 15 minutes | 15 minutes | 5 minutes |
| Custom functions | Not shown as included | Included | Included |
| Premium apps/on-premise/auto-rerun | Not shown as included | Not shown as included | Included/listed |

The live pricing selector displayed higher task tiers, including up to millions of tasks per month. Task overages and a daily cap are available in current billing/usage controls. Zoho One documentation at the cutoff described an organization allocation plus a per-employee allocation; this is particularly **VOLATILE** and must be verified in the tenant.

Capacity formula:

```text
monthly_tasks ≈ Σ(event_volume × successful_action_count_per_event)
              + successful_custom_function_executions
              + replay/retry overhead that reaches successful actions
```

Branches change the action count. A trigger firing does not itself equal a task. Measure a representative month in Usage, then reserve headroom for retries, backfills, and seasonal leasing volume.

## 8. Roles, audit, security, and support access

### 8.1 Roles and ownership

Official role descriptions distinguish Owner, Admin, and User capabilities. Owners/admins manage members and audit capabilities. Use least privilege:

- Builder: create/edit assigned flows, not organization-wide connection administration unless required.
- Operator: view History, rerun approved cases, acknowledge incidents.
- Connection owner: reauthorize the integration identity.
- Reviewer/approver: validates production change, mappings, and rollback.

Avoid a single person acting as builder, approver, and production connection owner for financial or legally consequential flows.

### 8.2 Audit and history

Flow settings provide an organization audit trail for owner/admin use. Execution History contains payloads and therefore may contain PII. **OFFICIAL:** Zoho states that data in transit is encrypted and that Flow uses application-layer AES-256 encryption at rest for categories including audit/history, tokens/credentials, and PII; full-disk coverage is described for specified data centers on the official encryption page.

Data-minimization rules:

- Map only necessary fields.
- Do not pass credit reports, government IDs, full bank data, or other highly sensitive artifacts through general-purpose execution history.
- Use WorkDrive or the approved record system for documents; pass a governed reference rather than binary contents where possible.
- Align history retention with policy and available plan controls.
- Redact secrets from request bodies, query parameters, logs, screenshots, and GitHub.

### 8.3 Support Access

**OFFICIAL:** Enabling Support Access can permit Zoho Flow support personnel to use connections and edit/debug flows. Enable it only for an active case, record approval and time window, minimize available sensitive data, and disable it immediately after resolution.

### 8.4 On-premises agent

Professional capabilities include an on-premises agent for supported integrations. An owner/admin generates the installation key. Treat the agent as privileged infrastructure: dedicated host, outbound restrictions, patching, inventory, monitored service identity, key rotation, and removal procedure. The release notes reported a 45-second on-prem endpoint timeout in June 2026; **VOLATILE**, and not a general SLA.

## 9. Change, test, and deployment discipline

**OFFICIAL:** Applying changes to a live flow creates a version. Drafts and version notes support review, and previous configuration can be inspected. There is no official public Flow-as-code deployment API documented in the reviewed sources.

Controlled lifecycle:

1. **Inventory:** trigger, every action, connection owner, field map, downstream side effects, task estimate, alert recipients, data classification.
2. **Contract:** define source event schema, target metadata, stable key, correlation ID, allowed states, and null/default rules.
3. **Sandbox:** use non-production source and target tenants/accounts where available; synthetic data only.
4. **Test matrix:** happy path, missing optional/required field, invalid enum, duplicate event, out-of-order event, connection revocation, 429, timeout-after-commit, partial outage, manual resume, manual restart, and volume burst.
5. **Review:** two-person review for financial, signature, tenant-status, access, or document-sharing effects.
6. **Deploy:** apply changes in an approved window; add a meaningful version note; verify connection and first execution.
7. **Observe:** monitor History, alerts, task use, and target reconciliation.
8. **Rollback:** restore prior logic/version or disable the flow; disabling does not reverse committed downstream changes.

Never test a destructive action against production merely to confirm connectivity.

## 10. GH Real Estate and Sylvara implementation patterns

### 10.1 Public inquiry to CRM

```text
Forms/Sites submission
  -> validate consent + minimum fields
  -> normalize email/phone/address
  -> search CRM by stable dedupe rules
  -> create or update Lead
  -> store source + campaign + submitted_at + external_event_id
  -> assign follow-up task
  -> notify only the responsible queue
```

Controls: do not overwrite a verified CRM value with a blank form field; retain raw intake only as policy allows; consistently apply fair-housing-safe routing criteria.

### 10.2 Approved applicant to contract/signature

Start only from an explicit approved CRM/application state. Re-read the record before creating a contract. Use a unique agreement key such as `applicant_record_id + property_id + lease_version`. Store contract/sign request IDs back in CRM. A webhook retry must look up that key rather than create a second agreement.

### 10.3 Executed lease to Books

Do not post accounting records solely because an intake form or signature request was created. Gate on verified execution status and approved financial terms. Query Books for an existing customer/transaction external reference before create. Route tax, deposit, credit, refund, and ledger ambiguity to accounting review.

### 10.4 WorkDrive document routing

Create/locate a governed folder from a stable property/tenant ID. Validate the destination and permission template before upload/share. Store the WorkDrive resource ID, not just a mutable URL. Never create public links for protected applicant/tenant documents without explicit policy authorization.

### 10.5 Analytics handoff

Send reporting-safe facts after the source transaction commits. Prefer source connectors or a curated dataset with stable source IDs. Flow should not mutate Analytics data as if it were operational truth.

### 10.6 Exception queue

For important workflows, create a structured exception record containing:

```text
correlation_id, source_system, source_event_id, source_record_id,
flow_name, flow_version, failed_step, error_class, retry_count,
first_seen_utc, last_seen_utc, owner_queue, status, resolution_note
```

Exclude payload secrets and sensitive documents. This can live in an approved Creator operations app or another governed system—not only in email.

## 11. Anti-patterns

- Guessing connector field names, module availability, or enumerations.
- Using record names or email addresses as the only dedupe key.
- Creating reciprocal flows without `origin_system`, version, and loop-suppression rules.
- Restarting an execution after partial success without inspecting target state.
- Treating a 2xx acknowledgement as proof that an asynchronous downstream business process completed.
- Writing financial entries from unapproved intake.
- Embedding tokens, webhook URLs, tenant IDs, or PII in GitHub.
- Making every connection organization-wide.
- Leaving connections owned by personal accounts.
- Using long delays as the only representation of lease/application state.
- Assuming polling is real time or will import history.
- Using Flow History as permanent audit storage.
- Enabling Support Access indefinitely.
- Inventing a Flow administration REST API or a stable export/deployment format.

## 12. Implementation checklist

### Discovery

- [ ] Confirm tenant data center and Flow domain.
- [ ] Confirm edition, task allocation, polling interval, history retention, and overage cap.
- [ ] Inventory Owner/Admin/User roles and production connection owners.
- [ ] Identify authoritative source for every field and state transition.
- [ ] Inspect live connector trigger/action metadata and sample payloads.

### Design

- [ ] Define immutable source event ID and stable business key.
- [ ] Define dedupe/replay behavior and timeout reconciliation.
- [ ] Minimize fields and classify PII/documents.
- [ ] Define error taxonomy, exception queue, alert owner, and escalation time.
- [ ] Estimate monthly tasks and peak throughput.
- [ ] Decide whether Flow, Catalyst, or a controlled service is the appropriate runtime.

### Build and test

- [ ] Use least-privilege named connections; record scopes and owner.
- [ ] Validate nulls, formats, allowed values, and target metadata.
- [ ] Test duplicates, out-of-order events, retries, connection failure, and partial commit.
- [ ] Verify both Resume and Restart behavior on synthetic records.
- [ ] Confirm logs/history do not expose unnecessary sensitive values.

### Deploy and operate

- [ ] Obtain required review/approval.
- [ ] Add a meaningful version note and rollback instructions.
- [ ] Observe initial executions and reconcile source-to-target counts.
- [ ] Configure failure and task-usage notifications.
- [ ] Schedule quarterly connection/owner/scope and dormant-flow review.
- [ ] Recheck release notes, plan limits, and official IP/domain documentation.

## 13. Source registry

All sources below are official Zoho pages and were accessed 2026-07-20.

1. **General overview — Zoho Flow Help**  
   https://help.zoho.com/portal/en/kb/flow/user-guide/overview/articles/general-overview
2. **Zoho Flow Help center**  
   https://www.zoho.com/flow/help/
3. **Zoho Flow release notes**  
   https://www.zoho.com/flow/release-notes/
4. **Zoho Flow pricing**  
   https://www.zoho.com/flow/pricing.html
5. **Subscription and usages**  
   https://help.zoho.com/portal/en/kb/flow/user-guide/subscription-and-add-ons/articles/subscription-and-usages
6. **Outgoing webhooks**  
   https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/outgoing-webhooks
7. **Webhook trigger**  
   https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/webhook-trigger
8. **URL trigger**  
   https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/url-trigger
9. **Using custom functions**  
   https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/using-custom-functions
10. **Logic elements**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/logic-elements
11. **Fix errors in flows**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/troubleshooting/articles/fix-errors-in-flows
12. **Rerun**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/troubleshooting/articles/rerun
13. **Versions**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/troubleshooting/articles/versions
14. **Common problems**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/troubleshooting/articles/common-problems
15. **Zoho Flow settings**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/settings/articles/zoho-flow-settings
16. **Encryption in Zoho Flow**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/security-and-privacy/compliance/articles/encryption-in-zoho-flow
17. **HIPAA compliance in Zoho Flow**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/security-and-privacy/compliance/articles/hipaa-compliance-in-zoho-flow
18. **Whitelist IP addresses**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/troubleshooting/articles/whitelist-ip-addresses
19. **Set up and manage the on-prem agent**  
    https://help.zoho.com/portal/en/kb/flow/user-guide/on-premise-app-integrations/articles/setup-and-manage-your-on-prem-agent

## 14. Research gaps that must remain explicit

- **UNDOCUMENTED:** No official public Flow management/deployment REST API or comprehensive OpenAPI specification was located. Do not fabricate endpoints, OAuth scopes, object schemas, or CI/CD commands.
- Connector-specific trigger/action contracts are dynamic. The live connector UI and the connected product's official API are the authoritative discovery surface.
- Generic Flow-wide concurrency, webhook payload-size, request-timeout, and retention guarantees were not found as stable public contracts in the reviewed pages. Check the current tenant/help/support response for the exact design.
- An incoming webhook's signature-verification behavior is not documented as a universal feature. Use a validating edge service for signed high-risk events when the live trigger lacks a verified mechanism.
- Product pricing and task allocations are **VOLATILE**. The current plan/usage screen supersedes this snapshot.

---

**AI stop condition:** If a requested design depends on any research gap above, the AI must say what is unknown, identify the official page or tenant screen to inspect, and refrain from producing deployable assumptions until that evidence is supplied.
