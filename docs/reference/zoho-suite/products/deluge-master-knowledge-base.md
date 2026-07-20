# Deluge Master Knowledge Base

**Document ID:** GH-DELUGE-MASTER-KB  
**Edition:** 2026.07 Research Edition  
**Research cutoff:** 2026-07-20  
**Audience:** ChatGPT, Codex, architects, developers, reviewers, and GH/Sylvara operators

> This is the canonical searchable Markdown companion to `GH_Deluge_Master_Knowledge_Base_2026.pdf`. Official Zoho documentation controls language and task behavior; live tenant metadata and runtime/compiler tests control deployment.

# Part 0 — Retrieval contract and authority model

## KB-000 Purpose, scope, and non-goals

This is a searchable, bookmarked master reference for reasoning about **Deluge**, Zoho’s scripting language, in the Zoho products used by GH. It is optimized for ChatGPT and Codex retrieval: stable entry IDs, explicit host context, exact task signatures where verified, source URLs, volatility labels, safety constraints, and copy-oriented examples using straight ASCII quotes.

The handbook covers the shared language, Creator-native data access, HTTP and Connections, current CRM V8 integration tasks, Books, Sign, WorkDrive, Contracts, Flow, Catalyst, Sites, and the GH system-ownership overlay. It does not contain credentials, production identifiers, tenant data, legal policy, accounting policy, or evidence that any repository file is deployed.

> DANGER — A PDF cannot make Deluge “timeless” or guarantee perfect runtime behavior. Zoho changes task signatures, limits, API versions, permissions, and product support. For a live change, current editor autocomplete, live module/field metadata, current official API documentation, and a sandbox/compiler test outrank this handbook.

**Edition:** 2026.07  
**Research and verification date:** July 20, 2026  
**Primary language authority:** current official Zoho Deluge documentation  
**Deployment authority:** sanitized live tenant metadata and current runtime evidence  
**Audience:** ChatGPT, Codex, developers, system administrators, reviewers, and change approvers

## KB-001 Mandatory AI preflight

Before generating or reviewing Deluge, resolve all of the following. If any answer affects syntax or writes and is unknown, ask for it or mark the code as a non-deployable reference pattern.

| Field | Required resolution | Why it changes the answer |
|---|---|---|
| Host | Creator, CRM, Books, Flow, WorkDrive, Sites, or other | Deluge is one language across non-uniform runtimes. |
| Trigger | Workflow event, schedule, button, validation, API, related list, custom function, batch | Context objects, time limits, permissions, and return contracts differ. |
| Edition and data center | Current plan/edition and account DC | Limits, features, domains, and callback URLs vary. |
| API generation | CRM V8, legacy wrapper, or REST API version | Names, signatures, envelopes, and trigger behavior cannot be mixed. |
| Schema | Exact module, field, form, report, and relation API/link names | Display labels are not safe identifiers. |
| Identity | Owner/system/login user and connection owner | Determines access and audit behavior. |
| Connection | Exact link name, authentication type, and least scopes | The connection argument is positional and product-specific. |
| Side effects | Creates, updates, deletes, sends, signs, charges, posts, or uploads | Controls dry-run, idempotency, approval, and rollback requirements. |
| Limits | Current account/runtime/API limits | Static values in old examples are frequently stale. |
| Evidence | Compiler/sandbox result and expected response fixture | Documentation examples alone are not deployment proof. |

### Canonical generation directive

> Never generate Deluge from syntax alone. Identify the host, trigger, current API version, schema identifiers, connection, scopes, execution identity, side effects, and current limits. Prefer a current native task, then supported `invokeAPI`, then `invokeUrl` with a Connection. Never mix Creator-only data syntax or legacy CRM signatures into another runtime. Validate nulls, types, response status, and nested keys; test in the product editor or sandbox before deployment.

## KB-002 Entry evidence labels

| Label | Meaning | Deployment implication |
|---|---|---|
| DOC-VERIFIED | Signature or behavior was checked against an official Zoho page on the verification date. | Still compiler-test in the target host. |
| API-VERIFIED | REST contract was checked against the current official product API page. | Confirm data center, scopes, edition, and live response. |
| REPO-OBSERVED | Pattern exists on the connected repository’s current `main`. | Repository presence is not live deployment proof. |
| COMPILER-TEST REQUIRED | Plausible/current source pattern, but not run in the user’s Zoho editor. | Do not deploy until it compiles with sanitized inputs. |
| LIVE-METADATA REQUIRED | Exact module, field, form, report, relation, template, folder, or connection name is tenant-specific. | Retrieve metadata; never infer from the UI label. |
| POLICY INPUT REQUIRED | Legal, accounting, communications, or business behavior must be approved outside code. | Stop before implementation if the requirement is absent. |
| VOLATILE | Pricing, limits, supported services, API versions, or UI details can change quickly. | Recheck the official page and live account immediately before work. |
| DEPRECATED | Kept only to recognize or migrate older code. | Do not select for new implementation. |

## KB-003 Authority ladder for GH work

Use the first applicable source; do not average conflicting sources.

1. Approved business, legal, and accounting implementation requirement.
2. Sanitized live Zoho metadata and current runtime evidence.
3. Connected `GH-Real-Estate/gh-real-estate-ops-code` repository on `main` and the applicable `AGENTS.md`.
4. Current official Zoho or provider documentation.
5. Dated project maps and working checklists.

The code repository is the sanitized technical source of truth for code, tests, schemas, field maps, runbooks, and controls. It is not a production secret store, tenant file cabinet, accounting ledger, live runtime, or proof of deployment.

## KB-004 Supplied-source audit

The two uploaded PDFs were inspected rather than merged blindly.

| Source | Finding | Treatment in this edition |
|---|---|---|
| `Deluge-Master-Handbook-2025.pdf` | Nine pages, about 1,500 extracted words, no usable citations/bookmarks, corrupted code glyphs, incomplete Creator signatures, incorrect CRM response assumptions, and unsupported constructs such as `throws`. | Rejected as a coding authority; useful only as a gap checklist. |
| `Deluge Coding.pdf` | Sixty-four-page 2018 Creator beginner e-book. It teaches obsolete UI, incomplete data types, a fixed-type claim contradicted by current docs, and multiple broken examples. | Retained only for its beginner teaching sequence; all technical content rewritten. |
| GH Markdown maps | Consistent system ownership, lifecycle, schema cautions, and change control. | Treated as the normative GH overlay, not language documentation. |
| Connected repository `main` | Current sanitized Books patterns, CRM/Creator boundaries, security guidance, and PDF standards. | Marked REPO-OBSERVED and separated from deployment proof. |

## KB-005 Research provenance and refresh policy

This edition uses official Zoho pages as primary technical sources. Key roots:

- Deluge overview: https://www.zoho.com/deluge/help/
- Release notes: https://www.zoho.com/deluge/help/release-notes.html
- Data types: https://www.zoho.com/deluge/help/datatypes.html
- Built-in functions: https://www.zoho.com/deluge/help/built-in-functions.html
- Deluge tasks: https://www.zoho.com/deluge/help/deluge-tasks.html
- Integration tasks: https://www.zoho.com/deluge/help/integration-tasks.html
- `invokeUrl`: https://www.zoho.com/deluge/help/webhook/invokeurl-api-task.html
- `invokeAPI`: https://www.zoho.com/deluge/help/webhook/invokeapitask.html
- Connections: https://www.zoho.com/deluge/help/connections.html
- CRM V8 tasks: https://www.zoho.com/deluge/help/crm-integration-tasks-V8.html
- Books tasks: https://www.zoho.com/deluge/help/books-tasks.html
- Creator tasks: https://www.zoho.com/deluge/help/creator-tasks.html
- Sign tasks: https://www.zoho.com/deluge/help/sign-tasks.html
- WorkDrive tasks: https://www.zoho.com/deluge/help/workdrive-tasks.html

Refresh at least quarterly and before a risky implementation. Review release notes; re-open each task/API page used by the change; export sanitized live metadata; confirm connections and scopes; inspect the current repository; rerun compiler and sandbox tests; update the verified date and change log.

<!-- PAGEBREAK -->

# Part I — The Deluge runtime model

## KB-100 Deluge is a language family embedded in products

Deluge is a dynamically typed scripting language embedded in multiple Zoho products. The common syntax creates a dangerous illusion: code that is valid in Creator may be unknown in CRM or Books; task availability and response shapes vary; runtime limits and logs are product-specific; connection requirements change by host; event contexts expose different variables.

The correct mental model is **shared expressions and data operations plus a host-specific task surface**.

| Layer | Usually shared | Host-specific examples |
|---|---|---|
| Language core | Variables, expressions, `if`, `for each`, `try/catch`, lists, maps, conversions | Some operator/criteria behavior and function availability still vary. |
| Runtime variables | `zoho.currentdate`, `zoho.currenttime` | `zoho.appname` and environment attributes are Creator-oriented; login/admin behavior varies. |
| Native data DSL | None universally | `insert into`, `Form[criteria]`, `input`, and `old` are Creator-native. |
| Integration wrappers | Namespaced `zoho.*` tasks | CRM V8, Books, Sign, Creator, and WorkDrive have distinct signatures. |
| Function contract | Arguments and return statement concept | Available declared types, namespaces, request/response objects, and invocation syntax vary. |
| Limits/logging | All executions are bounded | CRM credits/timeouts, Creator action rates, Flow tasks, Books workflow logs, and WorkDrive limits differ. |

Source: https://www.zoho.com/deluge/help/ and each product’s runtime documentation. Status: DOC-VERIFIED; product availability remains VOLATILE.

## KB-101 Host compatibility matrix

| Host | Deluge role | Native context | Preferred integration route | Major caution |
|---|---|---|---|---|
| Zoho Creator | Workflows, functions, pages, portal logic, batch workflows | Forms, reports, records, `input`, `old`, UI tasks | Native Creator DSL inside app; Creator tasks/API across apps | Never export Creator-only syntax to another host. |
| Zoho CRM | Functions tied to workflow, schedules, buttons, related lists, validation, or standalone/API use | CRM arguments and sometimes `crmAPIRequest`/`crmAPIResponse` | CRM V8 native tasks; CRM REST through supported `invokeAPI`/`invokeUrl` | System/elevated behavior, trigger recursion, API-name drift. |
| Zoho Books | Workflow custom functions and schedules | Context maps such as `invoice` and `organization` depend on rule/module | Books native tasks or REST via `invokeAPI`/`invokeUrl` | Financial writes require fail-closed controls and full-list update caution. |
| Zoho Flow | Custom functions inside flows | Function inputs/outputs and flow execution | Flow app actions; inside custom function, Connections currently pair with `invokeUrl` | Function/task limits and retry behavior are Flow-specific. |
| Zoho Sign | Usually called from another Deluge host | No assumption of a Sign-hosted Deluge runtime | Native Sign integration tasks or Sign REST via `invokeUrl` | Sending for signature is an external communication and legal workflow side effect. |
| Zoho WorkDrive | Cross-app integration tasks and WorkDrive workflow custom functions | WorkDrive workflow context is separate from cross-app wrappers | Upload/create-folder wrappers; REST for broader coverage | Duplicate names, overwrite flag, sharing/retention, and strict workflow limits. |
| Zoho Contracts | Product automation plus REST API access | Do not assume a native Deluge task | Scoped Connection plus REST; proxy unsupported methods via controlled runtime | Contract policy/template authority is outside code. |
| Zoho Sites | Deluge in Dynamic Content | Dynamic content view/request context | Read-oriented service calls where approved | Views cache by default; never cache user-specific private data. |
| Zoho Catalyst | External serverless/integration runtime | Java, Node.js, or Python functions; Deluge is not the core Functions runtime | HTTP endpoint/webhook called with a Connection | Runtime, not business policy or permanent record. |
| Zoho Analytics | Reporting and analysis | Analytics automation varies | Native task/API if needed | Never treat a replica/report as original system of record. |

## KB-102 Execution identity and authorization

Do not assume the visible user’s permissions govern every function. A Connection may run as its owner. CRM functions can operate with system/elevated behavior. Creator may distinguish app owner, portal user, and login user. The same script can therefore produce different access outcomes depending on where it was created, who owns the Connection, and how it was invoked.

For every write, record the expected execution principal, connection owner, OAuth scopes, target organization/account, and audit trail. Use least privilege. Never place access tokens, refresh tokens, passwords, API keys, Authorization headers, or private URLs in the script or logs.

Source: https://www.zoho.com/deluge/help/connections.html and https://www.zoho.com/crm/developer/docs/functions/ . Status: DOC-VERIFIED; account configuration is LIVE-METADATA REQUIRED.

## KB-103 Volatile limits: lookup, do not memorize

These values summarize pages current on the verification date. They are not a promise for a particular subscription.

| Runtime | Current documented signals | Operational rule |
|---|---|---|
| CRM Functions | Up to 200,000 executed lines and 10 MB response. Typical duration categories include 10 seconds for buttons/related lists/validation/API, 30 seconds for automation, and 15 minutes for schedules. | Check the current Functions Limits page and account analytics before design. |
| Creator | Current documentation includes 120 workflow action calls/minute/IP; 250 action calls/minute/app and per portal; ordinary workflow transaction timeout around 5 minutes; batch around 1 minute; external API read 40 seconds. | Use batch workflows and page/chunk controls where appropriate; confirm plan. |
| Flow | Current FAQ includes 300 app-trigger executions/minute and 100 webhook-trigger executions/minute, subject to plan and third-party limits. | Model Flow tasks and downstream API quotas separately. |
| Generic `invokeUrl`/`invokeAPI` | Socket response over 40 seconds fails. File/response limits vary by host and target domain. | Keep calls bounded and fail with correlation-safe diagnostics. |
| Books | Schedules, workflow component usage, logs, and retry settings are product-account controlled. | Never import CRM or Creator limits into Books. |

Sources: https://www.zoho.com/crm/developer/docs/functions/functions-limits.html ; https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/workflows-limitations ; https://help.zoho.com/portal/en/kb/creator/developer-guide/others/platform-performance/articles/platform-performance ; https://www.zoho.com/flow/help/faq.html . Status: VOLATILE.

<!-- PAGEBREAK -->

# Part II — Language core

## KB-200 Lexical rules and statements

Variables are dynamically typed and local to the action script. There are no conventional global variables. Identifiers are case-sensitive, start with a letter or underscore, and then use letters, numbers, or underscores. Avoid keywords and avoid names that differ only by case.

Text literals use ordinary double quotes. Official examples show `//` line comments and `/* ... */` block comments. Statements normally end with a semicolon. Blocks use braces. Code copied from word processors must be normalized to ASCII quotes before compiling.

```deluge
// Straight quotes, explicit semicolons, and descriptive names.
record_id = 1234567890;
dry_run = true;
status_label = "Ready";

/* Deluge variables can later hold a value of another type,
   but intentional code should keep a stable meaning. */
candidate = "42";
candidate = candidate.toLong();
```

Sources: https://www.zoho.com/deluge/help/variables.html and https://www.zoho.com/deluge/help/error-messages.html . Status: DOC-VERIFIED; example COMPILER-TEST REQUIRED in the target host.

## KB-201 Data types

| Type | Canonical role | Construction/example | Critical caution |
|---|---|---|---|
| Text | Strings and serialized payloads | `name = "Avery";` | Use straight double quotes. Encoding and API format matter. |
| Number | Integer-like numeric values and IDs | `count = 12;` | Large Zoho IDs should not be treated as arithmetic quantities. Preserve exactness. |
| Decimal | Fractional numeric values | `rate = 3.25;` | For money, use approved rounding and source policy; do not use binary-float assumptions. |
| Boolean | `true` or `false` | `dry_run = true;` | Do not substitute text `"true"` unless the API contract requires text. |
| Date-Time | Date and timestamp | Application/date functions or supported literal | Parsing/format is controlled by host/application settings and API contracts. |
| Time | Creator-only time-of-day value | Creator literal such as `'19:00:00'` | Supported only in Creator; literal uses single quotes and all hour/minute/second components. Time without zone/date is not an instant. |
| List | Ordered, zero-indexed values; mixed types allowed | `ids = List(); ids.add(10);` | Check size before `get(index)`. |
| Key-Value / Map | Unique keys mapped to values | `payload = Map(); payload.put("Name","Sample");` | Duplicate key assignment replaces the old value. Use exact API keys. |
| Collection | Index-value or key-value container | `Collection()` | One Collection instance cannot mix both models. Method names differ from Map/List. |
| File | Runtime file object | Result of download/file conversion or host field | A Creator upload field is not universally interchangeable with FILE. Size limits vary. |
| `null` | Absence constant | `value = null;` | `null` is not a data type; it differs from blank text and empty containers. |

Sources: https://www.zoho.com/deluge/help/datatypes.html ; https://www.zoho.com/deluge/help/datatypes/collection.html ; https://www.zoho.com/deluge/help/datatypes/file-data-type.html . Status: DOC-VERIFIED.

## KB-202 List, Map, and Collection are not synonyms

Use `List` for ordered values, `Map` for API objects, and `Collection` only when the receiving Deluge task expects Collection semantics or legacy/native code uses it. Similar-looking methods are not identical.

```deluge
names = List();
names.add("Avery");
names.add("Jordan");

person = Map();
person.put("Name","Avery");
person.put("Active",true);

legacy_indexed = Collection("Avery","Jordan");
legacy_keyed = Collection("Name":"Avery","Active":true);
```

Spelling trap: the Collection index documents `containsKey` and `containsValue`; the Map index documents `containKey` and `containValue`. Zoho’s documented misspellings such as `getOccurenceCount` and `removeFirstOccurence` must not be silently corrected.

## KB-203 Null, blank, empty, missing, and false

These states are distinct:

- `null`: no value.
- `""`: text with zero characters.
- whitespace text: non-empty text that may become blank after trimming.
- empty List/Map/Collection: a container with zero members.
- missing Map key: key not present; treat separately from a present key mapped to null.
- `false`: a Boolean value, not absence.
- `0`: a number, not absence.

The states are conceptually distinct, but the three convenience functions do **not** map to them uniformly. Current official behavior:

| Input | Other services: `isBlank` / `isNull` / `isEmpty` | Creator: `isBlank` / `isNull` / `isEmpty` |
|---|---|---|
| whitespace text `" "` | `true / false / true` | `true / false / false` |
| empty text `""` | `true / true / null` | `true / true / true` |
| `null` | `false / true / null` | `true / true / true` |
| empty List `{}` | `true / false / true` | `true / false / true` |
| List containing blank text | `false / false / false` | `false / false / false` |
| Map with blank key/value | `false / false / false` | `null / null / false` |

Receiver-style `.isNull()` is unavailable in Creator; global `isNull(expression)` works across services. `isNull` does not support form objects. Use the documented matrix for the named host, receiver/key-existence methods when omission matters, and do not call a receiver method on a potentially null value.

```deluge
safe_name = ifNull(input_name,"").trim();
if(isBlank(safe_name))
{
    safe_name = "Unnamed";
}

if(payload != null)
{
    if(payload.containKey("records"))
    {
        records = payload.get("records");
    }
}
```

Sources: https://www.zoho.com/deluge/help/functions/common/isnull-isblank-isempty-difference.html and https://www.zoho.com/deluge/help/functions/common/isnull.html . Status: DOC-VERIFIED matrix. `containKey` is the Map spelling; confirm method availability in the target host.

## KB-204 Operators and precedence

| Family | Operators | Notes |
|---|---|---|
| Arithmetic | `+ - * / %` | `+` also concatenates text. Division by zero is a runtime error. |
| Assignment | `= += -= *= /= %=` | `=` assigns; `==` compares. This is a frequent defect in old examples. |
| Relational | `< > <= >= == !=` | Official generic docs restrict some text comparisons; criteria contexts add their own operators. |
| Logical | `&& || !` | Always parenthesize mixed logical expressions. |
| Criteria-specific | `is`, `is not`, `in`, `not in`, functions/predicates | Validity depends on field type and the Creator/product criteria grammar. |

Important documented inconsistency: logical precedence is normally NOT → AND → OR, while the official page calls out a Creator ordering difference. Parentheses eliminate dependence on host precedence and make intent reviewable.

```deluge
// Correct bounded window; the old PDF's OR version was effectively always true.
if((hour_value >= 12) && (hour_value <= 18))
{
    window_label = "afternoon";
}
```

Sources: https://www.zoho.com/deluge/help/operators.html and https://www.zoho.com/deluge/help/criteria-conditional-statements.html . Status: DOC-VERIFIED.

## KB-205 Conditions

Statement form:

```deluge
if(criteria)
{
    // statements
}
else if(other_criteria)
{
    // statements
}
else
{
    // statements
}
```

Expression forms:

```deluge
label = if(is_active,"Active","Inactive");
fallback = ifNull(possibly_null,"Default");
```

Do not assume short-circuit behavior protects unsafe expressions without checking the host; write explicit outer guards when a nested call can fail. Keep side effects out of conditional expressions.

Source: https://www.zoho.com/deluge/help/conditional-statements/condition.html . Status: DOC-VERIFIED.

## KB-206 Iteration

General List/CSV element iteration:

```deluge
for each item in items
{
    info item;
}
```

Index iteration:

```deluge
for each index position in items
{
    item = items.get(position);
}
```

Creator record iteration uses a separate native grammar and may add criteria/sort:

```deluge
for each record_row in Maintenance_Requests[Status == "Open"] sort by Added_Time
{
    info record_row.ID;
}
```

`break;` exits the current loop. `continue;` skips the rest of the current iteration. There is no general `while` construct in the official task model; use API pagination with a bounded page sequence, schedule/batch continuation, or a controlled external runtime. Never invent `{1..N}` range syntax.

Sources: https://www.zoho.com/deluge/help/list-manipulations/for-each-element.html ; https://www.zoho.com/deluge/help/list-manipulations/for-each-index.html ; https://www.zoho.com/deluge/help/data-access/for-each-record.html . Status: DOC-VERIFIED; Creator example LIVE-METADATA REQUIRED and COMPILER-TEST REQUIRED.

## KB-207 Custom functions and return values

Custom functions have declared parameter and return types, but the editor’s supported types, namespace/category prefix, request objects, and invocation form vary by host. Flow documents void/int/float/string/bool/date/map/list/file; CRM’s function IDE presents its own set. Do not paste one product’s declaration header into another.

Core rules:

- Parameter count, order, and declared types must match the call.
- A value-returning function must return the declared type on every reachable path.
- A function with no return value must not be assigned to a variable.
- Some products invoke functions through a namespace/category prefix.
- Treat the header produced by the target editor as canonical.

Sources: https://www.zoho.com/deluge/help/misc-statements/call-function.html ; https://www.zoho.com/deluge/help/misc-statements/return-statement.html ; https://www.zoho.com/crm/developer/docs/functions/functions-ide.html ; https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/using-custom-functions . Status: DOC-VERIFIED; declaration syntax is host-specific.

## KB-208 Errors, `try/catch`, and diagnostics

`try/catch` handles runtime failures, not compile/save errors. Current official guidance exposes exception attributes including `message` and `lineNo`. The language documentation does not establish a general `throw`/`throws` statement; do not generate one.

```deluge
try
{
    result = 10 / divisor;
}
catch (error_value)
{
    // Log only a correlation-safe summary. Never dump credentials or personal payloads.
    info "calculation_failed line=" + error_value.lineNo + " message=" + error_value.message;
    result = null;
}
```

Compile/save errors include missing semicolons, undefined variables, missing returns, and argument count/type mismatches. Runtime errors include divide by zero, invalid JSON, index out of bounds, null operations, invalid casts, network timeouts, permission failures, and API error bodies.

`info expression;` writes debug output, but visibility, retention, and size vary. CRM Function Analytics currently exposes execution status, inputs/request information, duration, and logs, commonly for a limited retention window. Log a generated correlation ID, operation name, sanitized record ID suffix/hash, page number, status code, and error class—not the whole request or response.

Sources: https://www.zoho.com/deluge/help/misc-statements/try-catch.html ; https://www.zoho.com/deluge/help/error-messages.html ; https://www.zoho.com/deluge/help/debug/info.html ; https://www.zoho.com/crm/developer/docs/functions/function-analytics.html . Status: DOC-VERIFIED.

## KB-209 Date, time, timezone, and money discipline

Date/time literals and parsing depend on application settings and API formats. `zoho.currentdate` and `zoho.currenttime` are runtime variables, not universal UTC guarantees. Store/transport timestamps in the target API’s documented format with an explicit zone or offset. Convert deliberately at system boundaries. Never compare a formatted date string when a Date-Time comparison is available.

For money, obtain the currency, precision, rounding mode, effective date, and approved rule from Finance/Accounting. Re-fetch authoritative balances before a write. Never derive a ledger posting from UI-formatted text. Avoid silent truncation and do not assume a Decimal operation reproduces an external accounting system’s policy.

Source roots: https://www.zoho.com/deluge/help/functions/date-time.html and https://www.zoho.com/deluge/help/zoho-variables.html . Status: language facts DOC-VERIFIED; accounting behavior POLICY INPUT REQUIRED.

## KB-210 Runtime variables

Current documented read-only variables include `zoho.currentdate`, `zoho.currenttime`, `zoho.loginuser`, `zoho.loginuserid`, `zoho.adminuser`, `zoho.adminuserid`, `zoho.appname`, `zoho.appuri`, `zoho.ipaddress`, and `zoho.device.type`. Availability varies by host. Creator also documents `thisapp.environment.type` and `thisapp.environment.linkname` for environment guards.

Never assume `loginuser` is a safe sender address, a permanent identifier, or the person whose credentials the Connection uses.

Sources: https://www.zoho.com/deluge/help/zoho-variables.html and https://www.zoho.com/deluge/help/environment-attributes.html . Status: DOC-VERIFIED; product availability must be checked.

<!-- PAGEBREAK -->

# Part III — Built-in function catalog

## KB-300 How to read this catalog

Built-ins are organized by receiver/input type, but Zoho documentation sometimes shows both receiver-style and function-style calls. The name, category, and behavior family below were checked against the current category indexes. This edition is a complete **selection index**, not a claim that every built-in overload and error contract has been frozen into the PDF. For exact arity, optional parameters, accepted date formats, regular-expression behavior, return type, and host exceptions, follow the category URL to the individual function page and confirm in the target editor.

This is deliberate: inventing an “exact” signature from a similar function is more dangerous than requiring the official per-function page. Exact task signatures for GH’s principal apps are cataloged in Parts IV–V; the built-in tables select candidates. An AI must resolve the individual function entry before producing deployable code.

## KB-301 Logical and type predicates

| Name | Intent | Distinction/caution |
|---|---|---|
| `isNull(value)` / receiver equivalent | Host-sensitive absence test | Empty text also returns true; receiver form is unavailable in Creator; form objects unsupported. See KB-203. |
| `isBlank(value)` | Host/type-sensitive blank test | `null` and blank maps differ between Creator and other services. Use the matrix in KB-203. |
| `isEmpty()` / `isEmpty(value)` | Host/type-sensitive empty test | Empty text can return `null` outside Creator; whitespace differs by host. |
| `isDate(value)` | Date-Time recognition with hazardous edge cases | Invalid date-like Text can throw; List/Map can return `null`. Use deliberate validation or `try/catch`. |
| `isFile(value)` | Tests FILE runtime object | Upload-field values can be context-specific. |
| `isNumber(value)` | Tests numeric convertibility/type under documented rules | Do not use this alone to validate money or IDs. |
| `isText(value)` | Tests Text | Serialized JSON is still Text until parsed. |

Sources: https://www.zoho.com/deluge/help/functions/logical.html ; https://www.zoho.com/deluge/help/functions/type-check.html ; https://www.zoho.com/deluge/help/functions-returning-boolean.html ; https://www.zoho.com/deluge/help/functions/common/isdate.html . Status: DOC-VERIFIED inventory and caveats.

## KB-302 Text functions — current documented name inventory

### Search, membership, and comparison

| Function | Typical input pattern | Result/use |
|---|---|---|
| `contains` | text + search text | Boolean membership, case-sensitive. |
| `notContains` | text + search text | Boolean inverse membership. |
| `containsIgnoreCase` | text + search text | Boolean case-insensitive membership. |
| `isEmpty` | text | Host-sensitive empty test; outside Creator an empty text can produce `null`. See KB-203. |
| `getAlpha` | text | Returns alphabetic characters under the documented function contract. |
| `getAlphaNumeric` | text | Returns alphanumeric characters under the documented function contract. |
| `equalsIgnoreCase` | two text values | Boolean case-insensitive equality. |
| `startsWith` / `startsWithIgnoreCase` | text + prefix | Prefix test. |
| `endsWith` / `endsWithIgnoreCase` | text + suffix | Suffix test. |
| `indexOf` / `lastIndexOf` | text + search text | Position; handle “not found” per the function page. |
| `find` | text + search expression | Search/position operation; verify argument order. |
| `matches` | text + regular expression | Boolean regex match; validate regex and escaping. |
| `getOccurenceCount` | text + search text | Count; preserve Zoho’s spelling `Occurence`. |
| `getPrefix` / `getPrefixIgnoreCase` | text + delimiter/marker | Text before the documented match. |
| `getSuffix` / `getSuffixIgnoreCase` | text + delimiter/marker | Text after the documented match. |

### Length, slicing, padding, and order

| Function | Typical input pattern | Result/use |
|---|---|---|
| `len` / `length` | text | Character length under documented semantics. |
| `left` / `right` | text + count | Leading/trailing segment; guard bounds. |
| `mid` | text + start/count | Middle segment; confirm zero-based boundaries. |
| `subText` / `substring` | text + start and optional end/count | Slice; out-of-bounds raises runtime errors. |
| `leftpad` / `rightpad` | text + target/pad arguments | Padded text; verify optional pad character/string. |
| `repeat` | text + count | Repeated text; bound output size. |
| `reverse` | text | Reversed text. |
| `concat` | text values | Concatenated text; `+` also concatenates but explicit conversion is safer. |

### Case, whitespace, cleanup, replace

| Function | Typical input pattern | Result/use |
|---|---|---|
| `toLowerCase` / `toUpperCase` | text | Case-normalized text. Do not use display-normalization as a unique identity key without policy. |
| `proper` | text | Proper/title-like case per documented implementation. |
| `trim` / `ltrim` / `rtrim` | text | Whitespace trimming. |
| `remove` | text + target | Removes according to the specific page’s semantics. |
| `removeAllAlpha` | text | Removes alphabetic characters. |
| `removeAllAlphaNumeric` | text | Removes alphanumeric characters. |
| `removeFirstOccurence` / `removeLastOccurence` | text + target | Removes one occurrence; preserve Zoho’s spelling. |
| `replaceAll` / `replaceAllIgnoreCase` | search + replacement and documented options | Replaces all matches; verify regex/literal behavior. |
| `replaceFirst` / `replaceFirstIgnoreCase` | search + replacement and documented options | Replaces first match. |
| `isAscii` | text | Boolean ASCII test. Useful before constrained external systems, not as a blanket validation rule. |

### Text conversions and encoding helpers

| Function | Result | Primary caution |
|---|---|---|
| `toList` | List | Separator/format rules vary by overload. |
| `toMap` | Map | Input must follow documented key/value structure or valid JSON as applicable. |
| `toJSONList` | List from JSON text/data | Invalid JSON is a runtime error. |
| `toListString` | Text representation of list-like data | Do not confuse display serialization with API JSON. |
| `toLong` / `toNumber` | Number | Validate before conversion; IDs should remain exact. |
| `toDecimal` | Decimal | Apply approved rounding after conversion. |
| `toString` / `toText` | Text | Format arguments can be type-specific. |
| `text` | value plus documented format arguments | Produces formatted Text; resolve exact overload from its individual page. |
| `toDate` / `toTime` | Date-Time/Time | Provide explicit source format and timezone contract. |
| `textToHex` / `hexToText` | Encoded/decoded text | Encoding is not encryption. |

Complete category source: https://www.zoho.com/deluge/help/functions/text.html . Status: DOC-VERIFIED name inventory; per-function argument contract must be re-opened.

## KB-303 Number functions — current documented name inventory

| Family | Functions | Argument/result model |
|---|---|---|
| Absolute/rounding | `abs`, `ceil`, `floor`, `frac`, `round` | Numeric input; `round` accepts documented precision. Confirm negative rounding behavior. |
| Powers/logs | `exp`, `log`, `log10`, `power`, `sqrt` | Domain errors are possible; do not pass invalid/negative domains blindly. |
| Trigonometry | `sin`, `asin`, `sinh`, `asinh`, `cos`, `acos`, `cosh`, `acosh`, `tan`, `atan`, `tanh`, `atanh`, `atan2` | Verify units (normally radians) and `atan2` argument order from the individual page. |
| Aggregate/ranking | `average`, `max`, `min`, `median`, `largest`, `smallest`, `nthLargest`, `nthSmallest` | Numeric list/collection inputs; empty or mixed inputs require guards. |
| Random | `randomNumber` | Not a cryptographic or unique identifier generator. |
| Conversion | `toHex`, `toDecimal`, `toLong`, `toWords` | Locale/format and truncation/rounding behavior are function-specific. |
| Predicate | `isNumber` | Checks numeric status/convertibility under documented semantics. |

Source: https://www.zoho.com/deluge/help/functions/number.html . Status: DOC-VERIFIED name inventory.

## KB-304 Date-Time functions — current documented name inventory

| Family | Functions | Use/caution |
|---|---|---|
| Add | `addBusinessDay`, `addDay`, `addHour`, `addMinutes`, `addMonth`, `addSeconds`, `addWeek`, `addYear` | Returns adjusted value under calendar/application rules. Business-day holidays may need explicit configuration/policy. |
| Subtract | `subBusinessDay`, `subDay`, `subHour`, `subMinutes`, `subMonth`, `subSeconds`, `subWeek`, `subYear` | Same timezone/calendar cautions. |
| Components | `day`, `getDay`, `getDayOfYear`, `getHour`, `getMinutes`, `getMonth`, `getSeconds`, `getWeekOfYear`, `getYear`, `hour`, `minute`, `month`, `second`, `weekday` | Similar names may return different representations; open individual page. |
| Boundaries | `toStartOfMonth`, `toStartOfWeek`, `edate`, `eomonth`, `nextWeekDay`, `previousWeekDay`, `workday` | Start-of-week and business-day assumptions are configuration-sensitive. |
| Differences | `daysBetween`, `hoursBetween`, `monthsBetween`, `yearsBetween`, `days360`, `totalMonth`, `totalYear` | Inclusive/exclusive and partial-unit behavior must be read per function. |
| Current values | `today`, `now` | Use host/application timezone; do not label UTC without conversion. |
| Conversion/format | `toString`, `toTime`, `toDate`, `toDateTimeString`, `unixEpoch`, `isDate` | Supply explicit expected format at system boundaries. Unix unit/epoch semantics must be verified. |

Source: https://www.zoho.com/deluge/help/functions/date-time.html . Status: DOC-VERIFIED name inventory.

## KB-305 Time functions — Creator only

Time is currently supported only in Zoho Creator. A literal must use single quotes and all three components, for example `'19:00:00'` or `'06:00:00 PM'`. The current Time index includes `addHour`, `addMinutes`, `addSeconds`, `subHour`, `subMinutes`, `subSeconds`, `getHour`, `getMinutes`, `getSeconds`, and `toString`. Operations that cross the 24-hour range error. Treat Time as time-of-day; combine it with an explicit date and zone before representing an instant.

Sources: https://www.zoho.com/deluge/help/datatypes/time.html and https://www.zoho.com/deluge/help/functions/time.html . Status: DOC-VERIFIED category inventory.

## KB-306 List functions — current documented name inventory

| Family | Functions | Key behavior |
|---|---|---|
| Add/clear | `add`, `addAll`, `clear` | Mutates list. `addAll` expects compatible list input. |
| Membership/search | `contains`, `notContains`, `indexOf`, `lastIndexOf` | Handle not-found values explicitly. |
| Set-like | `distinct`, `intersect`, `removeAll` | Ordering/duplicate semantics should be tested before relying on them. |
| Access/slice | `get`, `subList`, `size` | Lists are zero-indexed; guard bounds. |
| Remove | `remove`, `removeElement` | Index removal versus value removal is easy to confuse. Read the specific page. |
| Order | `sort` | Mutating/return behavior and direction syntax are documented per page. |
| Numeric summary | `average`, `largest`, `median`, `nthLargest`, `nthSmallest`, `smallest` | Validate non-empty numeric values. |
| Conversion | `toJSONList`, `toList` | Serialization is not an API success check. |
| State | `isEmpty` | Empty differs from null. |

Source: https://www.zoho.com/deluge/help/functions/list.html . Status: DOC-VERIFIED name inventory.

## KB-307 Map functions — current documented name inventory

| Function | Common form | Behavior/caution |
|---|---|---|
| `put` | `map.put(key,value)` | Inserts or replaces a key. Return behavior is not a success contract for the external system. |
| `putAll` | `map.putAll(other_map)` | Merges; duplicate keys are overwritten. |
| `get` | `map.get(key)` | Returns mapped value; guard absent/null/nested shapes. |
| `containKey` | `map.containKey(key)` | Documented Map spelling is singular `contain`. |
| `containValue` | `map.containValue(value)` | Value membership. |
| `notContains` | receiver + value/key per documented variant | Read the individual page; do not infer from Collection/List. |
| `keys` | `map.keys()` | Returns keys. API key order should not be treated as meaningful. |
| `remove` | `map.remove(key)` | Mutates map. |
| `clear` | `map.clear()` | Removes all entries. |
| `size` / `isEmpty` | map | Container state. |
| `toMap` / `toJSONList` | value/map conversion | Requires valid documented input shape. |

Source: https://www.zoho.com/deluge/help/functions/key-value.html . Status: DOC-VERIFIED name inventory.

## KB-308 Collection functions — current documented name inventory

`clear`, `containsKey`, `containsValue`, `delete`, `deleteAll`, `deleteKey`, `deleteKeys`, `distinct`, `duplicate`, `get`, `getKey`, `getLastKey`, `insert`, `insertAll`, `intersect`, `isEmpty`, `keys`, `size`, `sort`, `sortKey`, `update`, `values`, and `notContains`.

Collection can be index-value or key-value, never both in one instance. Select methods that match the constructed model. Do not substitute Map’s `containKey` for Collection’s documented `containsKey`.

Source: https://www.zoho.com/deluge/help/functions/collection.html . Status: DOC-VERIFIED name inventory.

## KB-309 Conversion, JSON, XML, and URL utilities

| Category | Current names | Safety rule |
|---|---|---|
| General conversion | `toDate`, `toDecimal`, `toJSONList`, `toLong`, `toString`, `toTime`, `toList`, `toMap` | Conversion can fail at runtime; validate inputs and formats. |
| JSON/XML | `toXml`, `toXmlList`, `getJSON`, `toJSONList`, `toMap` | Confirm whether the receiver is Text, XML, Map, or List. Validate external payload schema before nested reads. |
| Utilities | `encodeUrl`, `getJSON` | URL encoding is required for values, not an excuse to concatenate untrusted paths. |

Sources: https://www.zoho.com/deluge/help/functions/conversion.html ; https://www.zoho.com/deluge/help/functions/xml.html ; https://www.zoho.com/deluge/help/functions/utilities.html . Status: DOC-VERIFIED inventory.

## KB-310 File methods

| Function | Purpose | Risk/control |
|---|---|---|
| `getFileContent` | Read file content | Size/encoding and sensitive-data exposure. Avoid logging content. |
| `getFileName`, `getFileSize`, `getFileType` | Metadata | Validate both declared and actual content where security matters. |
| `isFile` | Type check | Host upload fields can differ from FILE. |
| `setCharset`, `setFileName`, `setFileType` | Adjust metadata/interpretation | Does not prove content safety. Sanitize names and prevent path semantics. |
| `setFilePassword` | Protect supported file | Added in 2026; password delivery and secret storage require a separate approved channel. |
| `compress`, `extract` | Archive operation | Zip bombs/path traversal/content type require external security controls where applicable. |
| `toFile` | Convert supported value to FILE | Confirm encoding/name/type and size. |
| `convertToPDF` | Convert supported source to PDF | Options expanded in 2026; visual render-and-verify is still required. |

Source: https://www.zoho.com/deluge/help/file-methods.html . Status: DOC-VERIFIED inventory; capability and options are VOLATILE.

## KB-311 Encoding, hashing, and encryption tasks

The current encryption index includes Base64 encode/decode/decode-to-file, Base32 encode/decode, AES variants, HMAC SHA-1/SHA-256/SHA-512, MD5, SHA-1/SHA-256/SHA-512, URL encode/decode, and HTML encode/decode. Base32 and expanded Base64 charset support were added in 2026.

Encoding is not encryption. Hashing is not encryption. MD5 and SHA-1 are not appropriate for new security-sensitive integrity/password designs. AES/HMAC usage requires an approved key-management design; never hardcode keys or log them. Prefer platform-managed authentication and standard API signatures over inventing cryptography in Deluge.

Source: https://www.zoho.com/deluge/help/encryption-tasks.html and https://www.zoho.com/deluge/help/release-notes.html . Status: DOC-VERIFIED inventory.

## KB-312 Function selection algorithm

1. Identify the input’s actual runtime type; do not infer from how it prints.
2. Choose the type/category index.
3. Select the candidate function by behavior.
4. Open its individual current official page.
5. Record exact call form, argument order/types, optional defaults, return type, host exceptions, and error cases.
6. Guard null/empty/bounds/conversion.
7. Compile with a sanitized normal case and boundary cases.
8. If the output crosses a system boundary, validate the receiving API’s schema separately.

<!-- PAGEBREAK -->

# Part IV — Tasks, HTTP, and Connections

## KB-400 Task taxonomy

Deluge “tasks” are statements or namespaced service operations. The master task index currently groups data access, list/map/subform manipulation, file attributes, client/UI operations, miscellaneous actions, notifications, XML, Creator Blueprint, user roles/properties, AI tasks, FTP/SFTP, and integrations.

Important categories:

- Creator-native data access: add/fetch/update/delete records, aggregate values, record iteration, `input`, and `old`.
- List/Map manipulation and subform row operations.
- File upload field attributes and FILE methods.
- `sendmail`, SMS, push notifications, `openUrl`, and product UI/client functions.
- `invokeUrl`, `invokeAPI`, webhooks, FTP, and SFTP.
- Namespaced integration tasks such as `zoho.crm.v8.*`, `zoho.books.*`, `zoho.creator.*`, `zoho.sign.*`, and `zoho.workdrive.*`.

Source index: https://www.zoho.com/deluge/help/deluge-tasks.html . Status: DOC-VERIFIED category model; each task remains host-specific.

## KB-401 Creator-native data DSL

These constructs are **Creator-only** and operate on the local application’s forms/reports. They are not generic database syntax.

### Add a record

```deluge
new_id = insert into Maintenance_Requests
[
    External_Request_ID = external_request_id
    Status = "Received"
];
```

The task returns the created numeric ID when assigned. Field/form link names are LIVE-METADATA REQUIRED. Critical behavior: local `insert into` does not run the target form’s On Validate or On Success scripts. Shared post-processing must be called explicitly where required. Date-based schedules can still apply to the inserted record.

### Fetch a collection of records

```deluge
open_records = Maintenance_Requests[Status == "Open"];
matching_records = Maintenance_Requests[ID == target_id];
```

Creator fetch syntax always returns a collection of records, even for a unique ID criterion. Before accessing one record, require exactly one match; handle zero and multiple matches explicitly. Fetched records use Creator record/collection semantics, not a generic REST `{data:[...]}` envelope. Criteria operators depend on field type and Creator’s grammar. Order is not guaranteed unless a documented sort is specified.

### Update and delete

```deluge
for each record_row in Maintenance_Requests[External_Request_ID == external_id]
{
    record_row.Status = "Acknowledged";
}

// Destructive; require approved criteria, preview count, and rollback plan.
delete from Maintenance_Requests[ID == approved_record_id];
```

Never run an unbounded delete. Pre-fetch and report the exact write set. Creator integration forms have additional restrictions: local tasks may not add/modify/delete integration-form records, and system fields are not supported as ordinary fields.

Sources: https://www.zoho.com/deluge/help/data-access.html ; https://www.zoho.com/deluge/help/data-access/add-record.html ; https://www.zoho.com/deluge/help/fetch-records/fetch-collection-records.html ; https://www.zoho.com/deluge/help/data-access/delete-records.html . Status: DOC-VERIFIED grammar; examples COMPILER-TEST REQUIRED.

## KB-402 `input`, `old`, subforms, and UI tasks

`input.Field_Link_Name` refers to the current form/input value in supported Creator workflow events. `old.Field_Link_Name` provides the previous value only in documented events. Availability is event-specific; do not assume either in schedules, CRM, or Books.

Subform row creation uses generated row objects and a Collection. Transaction behavior differs by event: official documentation notes partial rows may remain in some On Load/On User Input failures, whereas On Validate/On Success can be all-or-none for the insertion. Model it as event-specific and test rollback behavior.

Client functions such as show/hide/enable/disable/focus are Creator UI operations and should not contain authoritative business state. They are not access controls; server-side validation must enforce rules.

Sources: https://www.zoho.com/deluge/help/subform-tasks.html ; https://www.zoho.com/deluge/help/client-functions.html ; https://www.zoho.com/deluge/help/data-access/accessing-form-fields.html ; https://www.zoho.com/deluge/help/data-access/old.html . Status: DOC-VERIFIED concepts.

## KB-403 Notifications and externally visible effects

`sendmail`, SMS, push notifications, document submission, signing, and `openUrl` produce user-visible effects. A successful API call may be irreversible even if the surrounding Creator transaction later rolls back.

The `sendmail` task is a bracketed statement with required sender, recipient, subject, and message plus documented optional fields/attachments. Sender restrictions, verified addresses, recipient limits, attachment formats, and daily quotas are host/account-specific. Build recipients from approved data, prevent duplicates, provide a dry-run preview, and never log message bodies or private addresses.

```deluge
if(dry_run)
{
    info "notification_preview template=maintenance_ack recipient_count=1";
}
else
{
    sendmail
    [
        from: zoho.adminuserid
        to: approved_recipient
        subject: approved_subject
        message: approved_message
    ];
}
```

Source: https://www.zoho.com/deluge/help/misc-statements/send-mail.html and https://www.zoho.com/deluge/help/notifications-using-deluge.html . Status: DOC-VERIFIED structure; sender policy and values LIVE-METADATA/POLICY INPUT REQUIRED.

## KB-404 Integration route selection

1. Use a current native integration task when it covers the operation and its response/trigger behavior is acceptable.
2. For a service in the current supported list, consider `invokeAPI`; it resolves the data-center domain.
3. Otherwise use `invokeUrl` with a scoped Connection.
4. Use Catalyst or another governed service for unsupported methods, long-running work, large files, stronger transaction/retry needs, or complex signing/security.
5. Never embed an access/refresh token, password, API key, or client secret in source.

Every native integration task execution is a backend API call and consumes the host’s External Call allowance. A task inside five loop iterations consumes five calls. Failed responses that reach the service can still count.

Source: https://www.zoho.com/deluge/help/integration-tasks.html . Status: DOC-VERIFIED.

## KB-405 `invokeUrl` exact attribute contract

Current syntax supports these attributes: `url`, `type`, `headers`, `body`, `parameters`, `files`, `connection`, `detailed`, `response-format`, and `response-decoding`.

```deluge
headers_map = Map();
headers_map.put("Accept","application/json");

response = invokeurl
[
    url: approved_url
    type: GET
    headers: headers_map
    connection: "approved_connection"
    detailed: true
];
```

### Methods and mutually exclusive payloads

- Current methods: GET, POST, PUT, PATCH, DELETE, OPTIONS. GET is the default.
- Do not specify both `body` and `parameters` in the same call.
- GET parameters become query parameters.
- A Text body defaults to `text/plain`; Key-Value body commonly becomes `multipart/form-data`; FILE defaults to `application/octet-stream`. Set `Content-Type` to the API’s required value.
- Serialize JSON explicitly when required, commonly with `payload.toString()` and `Content-Type: application/json`.
- `detailed:true` exposes response content, headers, and status code. Always inspect the documented structure rather than assuming the ordinary response envelope remains unchanged.
- `response-format` includes NONE, STRING, and FILE under current docs, with host exceptions; STRING/FILE are not applicable in Creator according to the current page.
- `response-decoding` controls supported decoding behavior; use only when the API contract requires it.

### Current timeout and file limits

A response taking more than 40 seconds causes a socket-timeout failure. Current download limits documented on the task page are 5 MB in Creator; in other services, up to 15 MB for Zoho-domain files and 5 MB for other domains. Permitted ports vary by product/data center. Enforce the smallest limit across host, integration task, and target app.

Source: https://www.zoho.com/deluge/help/webhook/invokeurl-api-task.html and https://www.zoho.com/deluge/help/web-data/invokeurl-task/limitations.html . Status: DOC-VERIFIED on 2026-07-20; VOLATILE.

## KB-406 `invokeAPI` exact service boundary

`invokeAPI` uses a service identifier plus a relative API path and resolves the correct Zoho data-center domain. On the verification date, the documented service list is exactly:

- `zohocrm`
- `zohobooks`
- `zohoinvoice`
- `zohobilling`
- `zohoinventory`
- `zohobookings`
- `zohocreator`
- `zohoworkdrive`

It is not a universal Zoho client: Sign and Contracts are not on this list. Current methods are GET, POST, PUT, PATCH, DELETE, and OPTIONS. JSON bodies should be serialized to Text where the API expects JSON. Current timeouts include a 40-second socket response, 10-second connection establishment, and 5-second connection-request wait.

Use the current page’s exact block syntax in the target editor; do not transform an `invokeUrl` block by guesswork.

Source: https://www.zoho.com/deluge/help/webhook/invokeapitask.html . Status: DOC-VERIFIED on 2026-07-20; supported services VOLATILE.

## KB-407 Connections

Connections currently support default/custom services and authentication patterns including API key, Basic, OAuth 1, OAuth 2 Authorization Code, OAuth 2 PKCE, OAuth 2 Client Credentials, and AWS Signature V4. Callback URLs and authorization domains vary by data center.

Production checklist:

- Use OAuth or the provider’s current recommended method.
- Request the minimum scopes for the exact endpoints.
- Use a dedicated, controlled service identity where continuity matters.
- Record the connection link name, owner, scopes, target organization, expiration/revocation behavior, and reauthorization procedure.
- Treat link names as configuration identifiers; they are not secrets, but they are tenant-specific.
- Never log tokens or Connection-injected headers.
- Understand whether the runtime uses the login user or Connection owner.
- Deleting/editing a custom service can revoke dependent Connections.
- In some embedded task contexts, the `connection` value must be a literal link name; do not assume a variable is accepted.

Source: https://www.zoho.com/deluge/help/connections.html . Status: DOC-VERIFIED; all actual connection values LIVE-METADATA REQUIRED.

## KB-408 Ordered optional arguments

Integration task parameters are positional. To supply a later optional parameter, supply every preceding parameter in the documented order. Use `Map()` or `null` only where the specific task permits it.

```deluge
options_map = Map();
response = zoho.crm.v8.createRecord(
    "Leads",
    record_map,
    options_map,
    "crm_connection"
);
```

Omitting `options_map` while passing a connection would shift arguments and fail or misbehave. This rule applies across current integration documentation.

## KB-409 Response validation ladder

Never equate “not null” with success.

1. Did the Deluge task execute without a runtime exception?
2. If detailed HTTP: is the status code in the endpoint’s success set?
3. Does the service-level status/code indicate success? Books commonly uses `code == 0`; Sign commonly returns `code`, `status`, and nested `requests`; CRM V8 wrapper shapes differ by task.
4. Does the expected object/list/key exist and have the expected type?
5. Does the returned identifier match the requested operation?
6. For writes, re-fetch the authoritative record and compare critical fields.
7. Record a sanitized correlation/evidence entry.

```deluge
operation_ok = true;
if(response == null)
{
    info "operation_failed reason=null_response";
    operation_ok = false;
}
else
{
    if(response.containKey("code"))
    {
        if(response.get("code") != 0)
        {
            info "operation_failed service_code=" + response.get("code");
            operation_ok = false;
        }
    }
}
```

Status: reference pattern; Map spelling is DOC-VERIFIED, but return syntax and task envelope are host-specific. COMPILER-TEST REQUIRED.

## KB-410 Retry and timeout discipline

Deluge provides no universal sleep/backoff primitive in the core documented task model. Do not write a fast loop that hammers an endpoint. For a transient failure:

- Retry reads only within a small explicit bound and current quota, or defer to a later schedule/queue.
- Retry idempotent PUT/PATCH only if the endpoint contract and idempotency design allow it.
- Never blindly retry a create, payment, invoice, signature send, notification, folder creation, or contract action.
- Before any retry, search/re-fetch by a stable external/idempotency key.
- Persist an operation state such as `planned`, `attempted`, `confirmed`, `needs_reconciliation` in the owning approved system.
- Use Catalyst/queue infrastructure for delayed exponential backoff, long-running work, or robust dead-letter handling.

<!-- PAGEBREAK -->

# Part V — Product-specific reference

# Part V-A — Zoho CRM

## KB-500 CRM execution contexts

CRM supports functions in six placements: standalone, workflow rule, schedule, custom button, related list, and validation rule. A function’s available arguments, return contract, timeout, and intended behavior depend on its placement; a function created for one placement is not automatically reusable in another.

Standalone functions can be exposed via GET/POST. Prefer OAuth. CRM also documents a static function API key, but it is shared across exposed functions and persists until revoked; it is unsuitable as a GH production default. CRM-hosted native tasks can use CRM’s system connection behavior; cross-product/other-host code needs the documented Connection.

Functions can run with elevated/system scope and may bypass ordinary user permission assumptions. Restrict “Manage Extensibility,” use CRM Sandbox, and perform an authorization test with representative least-privileged identities.

Sources: https://www.zoho.com/crm/developer/docs/functions/ and https://www.zoho.com/crm/developer/docs/functions/set-up-functions.html . Status: DOC-VERIFIED.

## KB-501 CRM V8 task signature catalog

Prefer `zoho.crm.v8.*` for new code. Legacy unversioned pages still exist; do not mix them with V8 arguments or response expectations.

| Task | Current documented signature pattern | Key return/constraint |
|---|---|---|
| Create | `zoho.crm.v8.createRecord(module, record_details, options_map, connection)` | Creates one; options and connection are positional/optional by host. |
| Get records | `zoho.crm.v8.getRecords(module, query_value, page, per_page, connection)` | Page defaults 1; current max/default `per_page` documented as 200. |
| Search | `zoho.crm.v8.searchRecords(module, criteria, page, per_page, search_value, connection)` | Up to 10 criteria; null behavior differs for `not_equal`. |
| Get by ID | `zoho.crm.v8.getRecordById(module, record_id, query_value, connection)` | Query map selects fields/related options per current page. |
| Update | `zoho.crm.v8.updateRecord(module, record_id, record_values, options_map, connection)` | Make trigger behavior explicit. |
| Bulk create | `zoho.crm.v8.bulkCreate(module, records_value, options_map, connection)` | Maximum 100 record maps/call. |
| Bulk update | `zoho.crm.v8.bulkUpdate(module, records_value, options_map, connection)` | Maximum 100; every map needs `id`. |
| Get related | `zoho.crm.v8.getRelatedRecords(relation_name, parent_module, record_id, query_value, page, per_page, connection)` | Relation API name and pagination are required knowledge. |
| Update related | `zoho.crm.v8.updateRelatedRecord(sub_module, sub_id, parent_module, parent_id, values, connection)` | Confirm relationship direction and IDs. |
| Convert lead | `zoho.crm.v8.convertLead(lead_id, values, connection)` | Conversion mapping and downstream automations are business-critical. |
| Upsert | `zoho.crm.v8.upsert(module, values, duplicate_check, connection)` | Duplicate-check map contains a list of truly unique field API names. |
| Attach file | `zoho.crm.v8.attachFile(module, record_id, file, connection)` | FILE and size/type limits apply. |
| Get fields | `zoho.crm.v8.getFields(module, connection)` | Use to inspect field metadata; still sanitize exports. |

Root: https://www.zoho.com/deluge/help/crm-integration-tasks-V8.html . Status: DOC-VERIFIED on 2026-07-20; exact optionality/return shape must be checked per task page.

## KB-502 CRM automation trigger contract

For current V8 create/update/bulk writes:

- If `options_map` is omitted, **workflow does not run by default**, while approval, blueprint, and orchestration run under the documented default behavior.
- If `options_map` supplies `trigger`, only the listed types run.
- `{"trigger":[]}` suppresses workflow, approval, blueprint, and orchestration.
- Supported current trigger values include `workflow`, `approval`, `blueprint`, and `orchestration`.

Never inherit the default silently. Record why each automation is enabled/suppressed and prevent recursion.

```deluge
changes = Map();
changes.put("Lead_Status","Contacted");

triggers = List();
triggers.add("workflow");

options = Map();
options.put("trigger",triggers);

if(dry_run)
{
    info "crm_update_preview module=Leads fields=Lead_Status trigger=workflow";
}
else
{
    response = zoho.crm.v8.updateRecord("Leads",lead_id.toLong(),changes,options);
    if(response == null)
    {
        info "crm_update_failed reason=null_response";
    }
    else if(response.get("id") == null)
    {
        info "crm_update_failed code=" + ifNull(response.get("code"),"unknown");
    }
}
```

Source: https://www.zoho.com/deluge/help/crm/update-record-V8.html and create/bulk V8 pages. Status: DOC-VERIFIED behavior; example COMPILER-TEST REQUIRED and LIVE-METADATA REQUIRED.

## KB-503 CRM retrieval, search, and pagination

Get/search functions are paginated. A single page is never evidence that all records were processed. Current V8 task docs use page/per-page values up to 200. Implement a bounded page list or external continuation, stop on an empty/short page or documented `more_records`, and record the last confirmed page.

Search currently supports up to 10 criteria. The `not_equal` operator does not include records where the field is null. Documentation wording about “field label” conflicts with API conventions/examples; use live field API names and sandbox-test the criterion.

```deluge
pages = {1,2,3,4,5};
for each page_number in pages
{
    query = Map();
    query.put("fields","id,Lead_Status,GH_External_ID");
    page_records = zoho.crm.v8.getRecords("Leads",query,page_number,200);
    if(page_records == null)
    {
        break;
    }
    if(page_records.isEmpty())
    {
        break;
    }
    for each crm_record in page_records
    {
        // Read-only processing or build a proposed write set.
    }
    if(page_records.size() < 200)
    {
        break;
    }
}
```

This finite-list pattern avoids invented range/while syntax, but its maximum page count must be derived from the operation’s approved bound. Confirm the current V8 return type and `fields` query key in the target editor because official wording contains `field`/`fields` inconsistencies.

## KB-504 CRM upsert and duplicate safety

Upsert is safe only when the duplicate-check field is truly unique, populated, normalized consistently, and protected against duplicate values. Current documentation warns that if multiple records share the match value, an arbitrary match may be updated; if the payload omits the configured duplicate-check value, duplicate checking may not happen and a new record may be created.

Before upsert:

1. Read the module metadata and uniqueness setting.
2. Normalize the stable external ID at ingestion.
3. Search and fail closed if more than one match exists.
4. Include the duplicate-check field in the payload.
5. Re-fetch by returned ID and external ID.
6. Alert on ambiguity; never “pick the first.”

Source: https://www.zoho.com/deluge/help/crm/upsert-record-V8.html . Status: DOC-VERIFIED.

## KB-505 GH CRM module contract

| Display name | Known underlying/API context | Rule |
|---|---|---|
| Leads | `Leads` | Zillow/approved intake writes here only. |
| Properties | `Accounts` | Renamed display label; never generate `Properties` without live evidence. |
| Units | Previously verified `Units` | Recheck current metadata before every implementation. |
| Contacts | `Contacts` | Approved people/tenant/vendor relationships; protect PII. |
| Rental Applications | `Deals` | Renamed pipeline module. |
| Maintenance Requests | `Cases` | CRM operational record; define Creator-facing data contract before dual-system writes. |
| Inspections | Custom, unresolved here | LIVE-METADATA REQUIRED. |
| Equipment | Custom, unresolved here | LIVE-METADATA REQUIRED. |
| Pets / Animals | Design/API name unresolved | Do not store unnecessary medical detail. |
| Storage Units | Design/API name unresolved | LIVE-METADATA REQUIRED. |

Zillow boundary: create/update Leads only. It must not directly create Contacts, Rental Applications, leases, Books records, portal users, or WorkDrive folders.

## KB-506 CRM current limit and conflict notes

Current Functions Limits documentation includes 200,000 executed lines, 10 MB response, and timeout categories of roughly 10 seconds (button/related list/validation/API), 30 seconds (automation), and 15 minutes (schedule). One workflow can have up to six functions under the documented instant/time-based distribution. REST function arguments have current URL/body character limits.

The official credit page currently contains conflicting Enterprise/Zoho One figures between a table and note. Do not choose either as universal. Check the live usage panel/calculator for the account.

Source: https://www.zoho.com/crm/developer/docs/functions/functions-limits.html . Status: VOLATILE and documentation-conflicted.

<!-- PAGEBREAK -->

# Part V-B — Zoho Books / Finance

## KB-520 Books ownership and surfaces

Books owns invoices, payments, deposits, fees, expenses, assets, liabilities, and financial reporting. Deluge appears in workflow functions, schedules, custom buttons, and related lists. Never make a Books write merely because CRM or Creator changed; the approved accounting requirement and Books’ authoritative state must drive it.

Current native task families are only `getOrganizations`, `createRecord`, `updateRecord`, `getRecords`, `getRecordsByID`, `markStatus`, and `getTemplates`. Payments, refunds, deletes, journals, credits, specialized actions, and many reports require the Books REST API.

## KB-521 Books native signatures

| Task | Current documented signature | Critical behavior |
|---|---|---|
| Organizations | `zoho.books.getOrganizations(connection)` | Returns organizations visible to the Connection. Never select the first by assumption. |
| Create | `zoho.books.createRecord(module_name, organization_id, data_map, connection)` | Validate `code == 0` and expected object/ID. |
| Update | `zoho.books.updateRecord(module_name, organization_id, record_id, data_map, connection)` | Omitted list elements such as line items may be deleted/replaced. Re-fetch/reconstruct full list. |
| List | `zoho.books.getRecords(module_name, organization_id, search, connection)` | Search is a Map except documented Creator variation; inspect `page_context`. |
| Get by ID | `zoho.books.getRecordsByID(module_name, organization_id, record_id, connection)` | Official pages/examples conflict on `ID` versus `Id` casing; current editor autocomplete is final. |
| Mark status | `zoho.books.markStatus(module_name, organization_id, record_id, status, connection)` | Selected Estimate/Invoice states only. A `sent` status changes the field; it does not email the document. Email is a separate action/API. |
| Templates | `zoho.books.getTemplates(module_name, organization_id, connection)` | Use returned template identifiers; do not infer from names. |

Source: https://www.zoho.com/deluge/help/books-tasks.html . Status: DOC-VERIFIED with casing conflict explicitly unresolved.

## KB-522 Books response and pagination contract

Books responses commonly include a numeric `code`, `message`, the expected singular/plural resource, and `page_context`. Success generally requires `code == 0`; a non-null Map is not enough. For list endpoints, continue while the live response reports `page_context.has_more_page`, and pass the next page through the REST task/endpoint design actually in use.

```deluge
invoice_record = null;
invoice_response = zoho.books.getRecordsByID(
    "Invoices",
    organization_id,
    invoice_id,
    "books_connection"
);

if(invoice_response == null)
{
    info "books_read_failed reason=null_response";
}
else if(invoice_response.get("code") != 0)
{
    info "books_read_failed code=" + invoice_response.get("code");
}
else
{
    invoice_record = invoice_response.get("invoice");
    if(invoice_record == null)
    {
        info "books_read_failed reason=missing_invoice";
    }
}
```

Status: signature casing must be confirmed in the target editor; response key must match the current module/endpoint. COMPILER-TEST REQUIRED.

## KB-523 Books replace-all update hazard

The current update task page warns that records/items not supplied in the update payload can be deleted. Treat nested lists such as line items as replace-all unless the exact endpoint documents a patch/partial behavior.

Safe sequence:

1. GET the authoritative record immediately before update.
2. Verify status, balance, version/modified time where available, currency, and organization.
3. Copy every nested list element that must remain.
4. Apply the smallest approved modification.
5. Produce a proposed write set/dry-run payload summary.
6. Update once with idempotency/duplicate protection.
7. Re-fetch and reconcile totals, line count, balance, and changed field.
8. If mismatch, stop and execute the approved compensating/rollback procedure.

Source: https://www.zoho.com/deluge/help/books/update-record.html . Status: DOC-VERIFIED; high-risk control REQUIRED.

## KB-524 Books workflow context and custom status

Current Books documentation defines default function input maps for Users, Organization, Quotes, Invoices, Sales Orders, Purchase Orders, Customers, Recurring Invoices, Expenses, Bills, Recurring Bills, and Items. Examples show some dates/amounts as Text, so normalize types explicitly instead of assuming Decimal/Date-Time.

The Organization map can expose identifiers, name, time zone, language/date format, currency identifiers/code/symbol, addresses, contact information, and portal name. Invoice context examples include invoice ID/number, customer/currency fields, status, dates, exchange rate, subtotal/tax/total/balance, addresses, notes/terms, custom fields, and salesperson. Exact keys depend on the product’s current template/context; inspect a sanitized test log or editor argument schema.

Books currently documents function execution status codes 1000–1009 for success, failure, cancellation, invalid input, validation failure, external service error, permission denial, missing record, limit exceeded, and unknown error. Use the editor’s return template/contract; do not invent key names.

Source: https://www.zoho.com/us/books/help/settings/automation/workflow-actions/functions.html . Status: DOC-VERIFIED categories; context keys LIVE-METADATA REQUIRED.

## KB-525 Books related lists and schedules

Books-related-list Deluge must return `header_context` and `data`; optional `page_context` communicates page, per-page, and `has_more_page`. This is a presentation contract, not an accounting write API.

Current product docs allow a limited number of schedules, buttons, and related lists; schedules/logs have retention and retry controls in the UI. Values are VOLATILE. Check the live account rather than importing generic Deluge limits.

Sources: https://www.zoho.com/us/books/help/settings/customization/related-lists.html ; https://www.zoho.com/us/books/help/settings/automation/schedules.html ; https://www.zoho.com/us/books/help/settings/automation/workflow-logs.html .

## KB-526 GH Books pattern

The connected repository’s current sanitized Books automations use workflow context maps such as `invoice` and `organization`, inspect response `code`, use Connections, re-fetch balances, and separate planned/live behavior. The literal connection link name currently observed is `"zbooks"`; this is REPO-OBSERVED configuration, not a universal name. Verify the live account before deployment.

For every invoice, credit, fee, interest, deposit, payment, or status change require: approved accounting rule; stable external ID; dry run; duplicate prevention; current-balance recheck; explicit write set; manual verification threshold; reconciliation; and rollback/compensating action.

<!-- PAGEBREAK -->

# Part V-C — Zoho Creator

## KB-540 Creator runtime model

Creator supports form/report workflows, schedules, approvals, Blueprints, payment workflows, batch workflows, reusable functions, custom APIs, pages, and portal experiences. It is GH’s approved tenant-portal/maintenance experience—not the default master source for CRM relationships, Books accounting, Contracts lifecycle, or signed documents.

Separate local Creator data syntax from cross-app integration tasks. Local `Form[criteria]`, `insert into`, `input`, and `old` work only inside Creator contexts. `zoho.creator.*` wrappers call another Creator app/account through API/link names.

## KB-541 Creator cross-app task patterns

| Operation | Current signature pattern | Identifier rule |
|---|---|---|
| Create | `zoho.creator.createRecord(owner, app_link, form_link, data_map, other_params, connection)` | Form link name, field link names, required preceding optional map. |
| Get records | `zoho.creator.getRecords(owner, app_link, report_link, criteria, from_index, record_limit, connection)` | Report link name, Creator criteria, bounded paging. |
| Get by ID | `zoho.creator.getRecordById(owner, app_link, report_link, record_id, connection)` | Report—not form—link name in current docs. |
| Update | `zoho.creator.updateRecord(owner, app_link, report_link, record_id, field_map, other_params, connection)` | Report and field link names. |
| Delete | Use the current `zoho.creator.deleteRecord` page/editor contract | Destructive; exact current signature and permissions must be re-opened. |

Root: https://www.zoho.com/deluge/help/creator-tasks.html . Status: current create/get/update signatures DOC-VERIFIED at root/per-task pages; all tenant identifiers LIVE-METADATA REQUIRED.

## KB-542 Creator local insert side effect gap

Local `insert into` returns a record ID but does not invoke the target form’s On Validate/On Success scripts. Therefore:

- Put reusable invariant logic in an explicit function that both the form workflow and programmatic insert call.
- Do not rely on a target workflow to assign security-sensitive defaults.
- Validate mandatory/business fields before insert.
- Use a stable external ID and pre-fetch to prevent duplicates.
- Confirm date-based schedules and other downstream automation separately.

## KB-543 Creator workflow, batch, and transaction limits

Current official documentation includes:

- 120 applicable workflow action calls/minute/IP.
- 250 action calls/minute/application and 250/minute/portal.
- Approximate statement allowances from 5,000 to 50,000 by plan for ordinary functions.
- 30-second record-lock timeout.
- Five-minute ordinary workflow transaction timeout.
- One-minute batch workflow transaction timeout.
- 40-second external API read timeout.
- Batch sizes of 10, 50, 100, 200, 500, or 1,000.
- Up to 100 configured batch workflows; one concurrent batch workflow per account; others queue.
- Fifteen consecutive batch failures terminate processing.

A failed/rolled-back Creator transaction cannot reverse a successful external API call. Any external write inside a Creator transaction needs its own idempotency key, operation state, and reconciliation path.

Sources: https://help.zoho.com/portal/en/kb/creator/developer-guide/limitations/articles/workflows-limitations ; https://help.zoho.com/portal/en/kb/creator/developer-guide/others/platform-performance/articles/platform-performance ; https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/create-and-manage-batch-workflows/articles/understand-batch-workflows . Status: VOLATILE.

## KB-544 Creator environments and portal authorization

Use Creator development/stage/production environments and `thisapp.environment.*` guards where supported. Environment guards reduce accidental writes; they do not replace permissions or an approval gate.

For portal operations, authenticate the user, map them to an approved CRM/Creator relationship, authorize the specific record, and then return only minimum fields. Never authorize by a record ID or URL parameter alone. Do not put credit/background reports, raw identity documents, banking details, or unnecessary medical data in app logs or project sources.

Source: https://help.zoho.com/portal/en/kb/creator/developer-guide/environments/articles/managing-applications-in-the-environments . Status: DOC-VERIFIED concept; actual environment names LIVE-METADATA REQUIRED.

<!-- PAGEBREAK -->

# Part V-D — Zoho Sign

## KB-560 Sign task signature catalog

Every Sign integration task is an external API call. Current task families and signatures:

| Task | Current documented signature | Return/constraint |
|---|---|---|
| Create document | `zoho.sign.createDocument(files, data_map, connection)` | FILE or List of FILE; empty `Map()` may skip optional data. Returns request/document metadata. |
| Get document | `zoho.sign.getDocumentById(request_id, connection)` | Returns Key-Value request/document/actions/status. Official examples vary `Id`/`ID`; use editor spelling. |
| Update document | `zoho.sign.updateDocument(document_id, values_map, connection)` | Only draft documents can be updated. |
| Get field IDs | `zoho.sign.getFieldIds(connection)` | Connection optional/required varies by host; returns field type IDs. |
| Download | `zoho.sign.downloadDocument(request_id, connection)` | Returns FILE. Sensitive signed output. |
| Submit | `zoho.sign.submitRequest(request_id, params, connection)` | Inserts required fields and sends to recipients—externally visible. |
| List templates | `zoho.sign.getTemplates(query_value, connection)` | Both query/connection positional optional; pass an empty map/null as permitted. |
| Get template | `zoho.sign.getTemplateById(template_id, connection)` | Returns roles/actions/field metadata. |
| Create from template | `zoho.sign.createUsingTemplate(template_id, params, connection)` | Creates and sends documents using mapped roles/field data. |

Source root: https://www.zoho.com/deluge/help/sign-tasks.html . Status: DOC-VERIFIED on 2026-07-20.

## KB-561 Safe Sign lifecycle

1. Create/instantiate a draft.
2. Capture `request_id`, each `document_id`, action IDs, and template version/evidence.
3. Validate recipient identity, email, role, action type, signing order, field mapping, and delivery policy.
4. Show a dry-run send manifest with recipient count and document/template IDs—not PII content.
5. Obtain the approved lifecycle/send gate.
6. Call `submitRequest` or the explicitly approved send operation once.
7. Reconcile status with an authenticated/deduplicated webhook or scheduled read.
8. Store completion evidence/signed output in the approved WorkDrive/record location; update Contracts/CRM through the approved data contract.

```deluge
draft = zoho.sign.createDocument(pdf_file,Map(),"sign_oauth_connection");
if(draft == null)
{
    info "sign_draft_failed reason=null_response";
}
else if(draft.get("code") != 0)
{
    info "sign_draft_failed code=" + draft.get("code");
}
else
{
    request_info = draft.get("requests");
    request_id = request_info.get("request_id");
    info "sign_draft_created request_suffix=" + request_id.toString().right(6);
    // Stop here until the separate approved send gate.
}
```

Source: https://www.zoho.com/deluge/help/sign/create-document.html . Status: DOC-VERIFIED signature/shape; COMPILER-TEST REQUIRED.

## KB-562 Sign constraints and webhook safety

- Current task docs note Creator `createDocument` inputs can be individually up to 50 MB, while Sign’s UI request constraints can be tighter (current guidance includes 40 files, 25 MB each, 40 MB overall). Enforce the tightest layer.
- Current index uses `createDocument`; older guides use `uploadDocument`. Prefer the current index/editor.
- Automated requests can consume Sign credits. Read the live plan before bulk sends.
- Draft update works only before sending.
- A Sign workflow may not update CRM automatically; implement an approved callback/reconciliation.
- Validate webhook authenticity by the current Sign mechanism, deduplicate events by a stable event/request key, enforce expected state transitions, and return quickly.
- Never log full webhook payloads, recipient PII, authentication codes, documents, or signatures.

Sources: https://www.zoho.com/deluge/help/sign/update-document.html ; https://help.zoho.com/portal/en/kb/zoho-sign/user-guide/sending-a-document/articles/send-for-signatures ; https://help.zoho.com/portal/en/kb/zoho-sign/solutions-guide/zoho-deluge-integration/articles/how-to-set-up-a-callback-function-in-crm-to-add-zoho-sign-document-details-that-is-triggered-by-the-zoho-sign-webhook . Status: VOLATILE constraints.

<!-- PAGEBREAK -->

# Part V-E — Zoho WorkDrive

## KB-580 Cross-app native task signatures

Only three native cross-app task families are currently documented:

| Task | Exact current signature | Key control |
|---|---|---|
| Upload | `zoho.workdrive.uploadFile(file, folder_id, file_name, override_name_exist, connection)` | File name must be URL encoded; `true` replaces same-name file. Prefer `false` unless replacement approved. |
| Create folder | `zoho.workdrive.createFolder(folder_name, parent_id, connection)` | Parent folder ID is tenant-specific. Search/deduplicate before create. |
| Create team folder | `zoho.workdrive.createTeamFolder(folder_name, parent_id, description, is_public_within_team, connection)` | `parent_id` is team ID; public/private choice is access control. |

Listing, downloading, moving, copying, renaming, sharing, deleting, versioning, and broader metadata operations require the WorkDrive REST API.

Sources: https://www.zoho.com/deluge/help/workdrive-tasks.html ; https://www.zoho.com/deluge/help/workdrive/upload-file.html ; create-folder pages. Status: DOC-VERIFIED.

## KB-581 Upload pattern and overwrite hazard

```deluge
encoded_name = encodeUrl(file_name);
upload_response = zoho.workdrive.uploadFile(
    file_object,
    approved_folder_id,
    encoded_name,
    false,
    "workdrive_connection"
);
```

Before upload: validate destination ownership/retention; sanitize the name; calculate/check an approved digest if needed; check existing external ID/name/version; choose create versus replace explicitly; enforce file limits and malware/content controls; record the returned WorkDrive ID; re-fetch metadata; never print file content.

`override_name_exist=true` is destructive replacement, not harmless idempotency. Use versioning or a stable external-ID manifest when retention matters.

## KB-582 WorkDrive-hosted custom functions

WorkDrive now supports Deluge custom functions attached to workflow rules, separate from cross-app tasks. Current documented constraints include Team Admin configuration, up to 50 custom functions/team, `void` return only, Automation category, string/int parameters, one-minute execution, 10 MB response, 200,000 executed lines, email/webhook quotas, and a 5 MB file download/processing limit inside a function.

Workflow actions run with the Workflow Creator’s permissions; function calls/Connections use the configuring user’s permissions. Use a controlled least-privileged service identity and document ownership transfer/reauthorization.

Sources: https://help.zoho.com/portal/en/kb/workdrive/custom-functions-connections/articles/working-with-custom-functions-in-workdrive and Connections companion. Status: DOC-VERIFIED; limits VOLATILE.

## KB-583 Large files and system ownership

WorkDrive’s REST API recommends standard upload below its current threshold and large-file upload above it, but Creator/native Deluge file transport limits may be lower. Use Catalyst or an SDK for large, resumable, or integrity-critical transfer.

WorkDrive owns controlled documents and evidence, not contract lifecycle state, signature state, code, or accounting. Store the WorkDrive resource ID in the owning business record; do not turn folder names into the only relationship key.

<!-- PAGEBREAK -->

# Part V-F — Zoho Contracts

## KB-600 No current native Contracts Deluge task

The current Deluge integration-task catalog does not list Zoho Contracts, and Contracts is absent from the current `invokeAPI` supported-service list. Use the Contracts REST API through `invokeUrl` with a scoped OAuth Connection, Zoho Flow where a supported action exists, or a governed Catalyst proxy.

Contracts owns approved templates, clauses, requests, approvals, negotiation, and lifecycle. Code may implement an approved transition; it must not invent contract policy, clauses, recipients, or authority.

Sources: https://www.zoho.com/deluge/help/integration-tasks.html ; https://www.zoho.com/contracts/api/introduction.html . Status: DOC/API-VERIFIED.

## KB-601 Contracts REST areas and create pattern

Current official APIs cover create/get/update/list contracts, collaborators, negotiation, and multi-step import. Create uses `POST /api/v1/contracts` with documented fields including source, input fields by API name, and optional clause overrides.

```deluge
headers = Map();
headers.put("Content-Type","application/json");

response = invokeurl
[
    url: contracts_api_base + "/api/v1/contracts"
    type: POST
    headers: headers
    body: contract_payload.toString()
    connection: "contracts_oauth"
    detailed: true
];
```

The base URL is data-center-specific and should come from approved configuration. The API’s examples may display literal OAuth tokens for illustration; never copy them. Before create, search/reconcile by a stable CRM/application external reference and store both returned Contracts ID and API name/version evidence.

Sources: https://www.zoho.com/contracts/api/contract/create-contract.html and OAuth page. Status: API-VERIFIED; example COMPILER-TEST REQUIRED.

## KB-602 Unsupported `UPDATE` method conflict

The published Contracts Update Contract endpoint uses the nonstandard HTTP method `UPDATE`. Current Deluge `invokeUrl` supports only GET, POST, PUT, PATCH, DELETE, and OPTIONS.

> DANGER — Do not substitute PUT or PATCH by analogy. Direct Deluge update is unverified. Confirm a supported alternate endpoint/method with Zoho in a sandbox or proxy the documented request through a governed Catalyst/other HTTP client that supports the required method.

Source: https://www.zoho.com/contracts/api/contract/update-contract.html and current `invokeUrl` page. Status: DOCUMENTATION CONFLICT; direct Deluge operation unsupported until verified.

## KB-603 Negotiation and import hazards

Current negotiation docs require Contracts scopes and Zoho Writer editor scope. Supplying a negotiator list overwrites existing negotiators, and the first becomes primary. A send-for-negotiation is externally visible and must follow an approved lifecycle gate.

Import is multi-step upload/import. Persist the operation ID/state, do not blindly restart after timeout, and reconcile by the stable external reference.

Sources: https://www.zoho.com/contracts/api/negotiation/send-for-negotiation.html ; https://www.zoho.com/contracts/api/contract/import-contract.html . Status: API-VERIFIED.

<!-- PAGEBREAK -->

# Part V-G — Zoho Flow

## KB-620 Flow custom functions

Flow custom functions are organization-wide reusable Deluge functions. Current documented return types include void, int, float, string, bool, date, map, list, and file; inputs cannot be void. Return a stable Map schema and run a sanitized sample so downstream mapping exposes keys.

Any organization member may be able to edit/delete a custom function, and deletion affects all consuming flows. Keep the sanitized source, interface schema, tests, version, and consumer list in GitHub; deploy/change under approval.

Source: https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/using-custom-functions . Status: DOC-VERIFIED.

## KB-621 Flow Connections restriction

Current Flow documentation states that app Connections in Flow custom functions work through `invokeURL`, not predefined integration tasks.

```deluge
api_response = invokeurl
[
    url: approved_api_url
    type: GET
    connection: "approved_flow_connection"
];
```

Do not generate `zoho.crm.v8.*(...,"flow_connection")` merely because it is valid elsewhere. Use Flow’s native app action outside the function or `invokeUrl` under the current documented restriction.

Use Flow for routing/light transformations. Keep high-risk financial, legal, signing, deletion, access-control, or multi-step reconciliation logic in the owning app or Catalyst.

## KB-622 Flow rate and failure design

Current FAQ values include 300 app-trigger executions/minute and 100 webhook-trigger executions/minute, plus plan and third-party limits. These do not replace per-flow task quotas or downstream API limits. Define retry/alert behavior, avoid self-trigger cycles, correlate each flow run, and route unreconciled high-risk operations to a human queue.

Source: https://www.zoho.com/flow/help/faq.html . Status: VOLATILE.

<!-- PAGEBREAK -->

# Part V-H — Catalyst, Sites, and Analytics boundaries

## KB-640 Catalyst is not a general Deluge host

Catalyst core serverless Functions currently use Java, Node.js, or Python, with Basic I/O, Advanced I/O, Cron, Event, and Integration types. Advanced I/O exposes HTTP request/response handling and currently has a 30-second maximum. API Gateway should provide authentication/throttling for externally reachable endpoints.

Deluge can call a Catalyst HTTPS endpoint via a Connection. Catalyst is appropriate for GH’s Zillow/intake endpoint, unsupported HTTP methods, large files, secure webhook verification, queues, and robust retry/reconciliation. It is an integration runtime, not business policy or permanent record.

Exception: Catalyst ConvoKraft bot actions/handlers have a separate Deluge facility. That does not make Deluge a supported language for general Catalyst Functions.

Sources: https://docs.catalyst.zoho.com/en/serverless/help/functions/runtime-support/ ; https://docs.catalyst.zoho.com/en/serverless/help/functions/advanced-io/ ; https://docs.catalyst.zoho.com/en/convokraft/help/actions/bot-logic/deluge-functions/defining-deluge-functions/ . Status: DOC-VERIFIED.

## KB-641 Zoho Sites Dynamic Content

Sites has two distinct code surfaces:

- Code Snippets: HTML, CSS, and JavaScript—not Deluge.
- Dynamic Content: Deluge functions plus Face views/CSS/JavaScript.

Dynamic Content views are cached by default. Current docs say `user` and `request_object` do not work while caching is enabled. For authenticated/request-specific tenant content, disable caching, verify login, check role/group, authorize that the requested record belongs to that user, and return minimum fields. Never trust URL/request parameters as authorization.

> DANGER — Caching user-specific tenant output can expose one user’s data to another. Prefer Creator for private tenant workflows unless Sites Dynamic Content has an explicit, tested authorization and cache design.

Sources: https://help.zoho.com/portal/en/kb/zohosites/help-guide/manage/dynamic-content/articles/dynamic-content ; Sites Connections and Code Snippets pages. Status: DOC-VERIFIED.

## KB-642 Zoho Analytics

Analytics is a reporting/analysis consumer, not the original source of operational or accounting records. Deluge/API automation may refresh or query analytics under a defined contract, but an Analytics row must not drive a destructive CRM/Books correction without reconciliation to the owning source.

Status: GH architecture rule; any Analytics task/API signature must be researched from its current official page when selected.

## KB-643 Zoho Forms / approved intake

Zoho Forms is an intake surface, not a general Deluge host in the current task catalog. Current Forms documentation supports native integrations and HTTP POST webhooks using JSON, URL-encoded, or multipart content with different attachment/subform coverage. Forms Connections can authorize webhooks on supported paid plans. Payment status can arrive asynchronously from the form submission.

For GH, normalize and validate the submission at an authenticated Catalyst/approved endpoint, assign a stable source submission ID, deduplicate, and create/update **CRM Leads only**. Do not let a form webhook directly create Contacts, applications, leases, Books transactions, portal users, or folders. Treat attachments and payment fields as separate high-risk flows, not ordinary lead fields.

Sources: https://help.zoho.com/portal/en/kb/forms/integrations/webhooks/articles/webhook-configuration and https://help.zoho.com/portal/en/kb/forms/adminguide/articles/connections-control-panel . Status: DOC-VERIFIED on 2026-07-20; exact form mapping LIVE-METADATA REQUIRED.

<!-- PAGEBREAK -->

# Part VI — GH architecture and production engineering

## KB-700 GH system-of-record matrix

| System | Approved role | Must not become |
|---|---|---|
| Zillow / approved forms | Inquiry and application intake | Accounting, lease generation, tenant portal provisioning |
| CRM | Leads, applicants, contacts, tenants, properties, units, leasing pipeline, operational relationships | Ledger or signed-document vault |
| Books | Invoices, payments, deposits, fees, expenses, assets/liabilities, financial reports | Leasing pipeline or maintenance master |
| Contracts | Approved templates, clauses, requests, approvals, lifecycle | Public form or general statutory-notice library |
| Sign | Recipient roles, fields, signature workflow/evidence | Contract policy source |
| WorkDrive | Controlled documents, property records, inspection evidence | Code repository or contract lifecycle authority |
| Creator | Approved tenant portal and maintenance experience | Universal master database |
| Sites | Public website and approved portal entry | Tenant ledger/private document store |
| Catalyst | Serverless functions, webhooks, integration runtime | Policy source or permanent business record |
| Flow | Lightweight approved cross-app routing | Complex uncontrolled financial/legal logic |
| Analytics | Reporting and analysis | Source of original records |
| GitHub | Sanitized code, schemas, tests, runbooks, controls | Tenant file cabinet, ledger, secret store, runtime proof |

Integration copies only necessary identifiers/fields. Each business fact has one owner. A replicated value carries the owner’s ID and last-synchronized/evidence metadata; it does not create a competing authority.

## KB-701 Tenant lifecycle control points

| Stage | Owning transition | Automation boundary |
|---|---|---|
| Inquiry | Zillow/approved input → CRM Lead | Deduplicate by stable source ID. Zillow writes Leads only. |
| Contact/showing | CRM Lead status/pipeline | Communications require approved templates and opt-out/contact rules. |
| Application | Approved application source → CRM application relationship | Fair-housing consistency; protect reports and identity data. |
| Review | CRM process | Human/legal/business approval; code does not decide policy. |
| Lease preparation | Contracts lifecycle, then Sign | Approved template/clauses/roles; separate draft and send gates. |
| Move-in | CRM relationships plus Books approved initial accounting | Portal access, payments, utilities, condition evidence each have separate authority. |
| Occupancy | Books rent accounting; CRM/Creator maintenance; WorkDrive evidence | Define maintenance data contract; no dual-master. |
| Renewal/nonrenewal | Approved legal/business process across owning systems | No automatic notice/rent decision without approved requirement. |
| Move-out | CRM/WorkDrive operational evidence plus Books final accounting | Deposit/legal/accounting controls and reconciliation. |

## KB-702 Maintenance ownership ambiguity

GH maps identify CRM `Cases` as Maintenance Requests while Creator provides the tenant-facing maintenance workflow. Before any write implementation, approve a data contract specifying:

- Which system creates the canonical request ID.
- Which fields are mastered in CRM versus Creator.
- Allowed state transitions and who can perform them.
- One-way or two-way synchronization and conflict resolution.
- Attachment/evidence storage in WorkDrive.
- Tenant-visible versus internal fields.
- Retry, duplicate, and reconciliation behavior.
- Retention, privacy, and audit evidence.

Until approved, provide read-only mapping/design examples only. Status: POLICY/DATA CONTRACT REQUIRED.

## KB-703 Requirement gate

Every change must name requirement owner, approved behavior, affected systems, source of truth, data contract, security/privacy impact, legal/accounting approval if applicable, tests, rollout, rollback, and operator evidence.

High-risk domains include money, rent, invoices, fees, credits, deposits, leases, notices, tenant records, access control, privacy/retention, external communications, and deletion. These require dry run, duplicate prevention, manual verification, and rollback/compensating actions.

## KB-704 Proposed write set

Before a risky live run, produce this table from sanitized identifiers:

| Item | Current state | Proposed state | Record/user count | Live immediately? | Reversal/compensation | Approval |
|---|---|---|---|---|---|---|
| Operation ID | Current authoritative values/hash | Exact changed fields/action | Exact bounded count | Yes/No and trigger effects | Tested procedure | Named approved handoff |

Do not show full tenant names, emails, addresses, documents, bank data, or payloads. Use internal test IDs, record suffixes, or approved hashes.

## KB-705 Change workflow and deployment evidence

1. Inspect current repository and sanitized live state.
2. Select the smallest change and current official signature.
3. Create a short-lived branch.
4. Add sanitized fixtures and tests.
5. Run narrow tests, then applicable suite/compiler/sandbox tests.
6. Review the diff for unrelated changes, secrets, PII, duplicates, and unsafe behavior.
7. Open focused PR; resolve checks/review; merge under current repo instructions.
8. Deploy separately with required approval.
9. Smoke test live behavior at bounded scope.
10. Record PR, merge commit, deployed version, environment, tests, smoke result, operator/date, known limitations, monitoring, and rollback status.

A merged PR is not a deployment. A saved Zoho function is not proof its workflow is enabled. A successful HTTP response is not business reconciliation.

<!-- PAGEBREAK -->

# Part VII — Production patterns and recipes

## KB-720 Stable external identifiers

Use a source-issued immutable ID or a GH-generated UUID/correlation key. Never use name, email, address display text, folder name, invoice number format, or mutable status as the sole cross-system identity.

Store:

- `external_id` from the source.
- Owning-system record ID.
- Downstream record IDs where copying is approved.
- Operation/idempotency key for each side effect.
- Version/modified time or digest when available.
- Sync state and last successful reconciliation time.

On duplicate ambiguity, fail closed and create a review item. Never select `get(0)` from multiple matches.

## KB-721 Idempotent write state machine

| State | Meaning | Allowed next action |
|---|---|---|
| `planned` | Validated dry-run proposal exists | Approve or cancel. |
| `approved` | Required human/policy gate recorded | Preflight authoritative systems again. |
| `attempted` | One request sent with operation key | Re-query; do not resend blindly. |
| `confirmed` | Response and authoritative re-fetch agree | Record evidence and downstream reconciliation. |
| `needs_reconciliation` | Timeout/ambiguous/mismatch | Human/system query by external key; compensate if approved. |
| `compensated` | Approved reversal/correction completed | Preserve both original and corrective evidence. |

Use a unique operation key per intended business action, not per HTTP attempt. External APIs are not part of a Deluge transaction.

## KB-722 Dry-run switch pattern

```deluge
operation = Map();
execute_write = !dry_run;
operation.put("operation_key",operation_key);
operation.put("system","Zoho CRM");
operation.put("module","Leads");
operation.put("record_id_suffix",lead_id.toString().right(6));
operation.put("fields",{"Lead_Status"});

if(dry_run)
{
    info "DRY_RUN " + operation.toString();
}

// Continue to the write only when execute_write is true.
// Immediately re-fetch and verify preconditions before the single write.
```

Do not include actual values when sensitive. Dry run must execute validation, target selection, and proposed write-set generation, while suppressing writes/sends/uploads/status transitions. Status: reference pattern; COMPILER-TEST REQUIRED.

## KB-723 Trigger recursion guard

Possible cycle: CRM workflow updates a record → function calls CRM update → workflow fires again. Controls:

- Explicit trigger options.
- A stable processed-version/operation key, not a transient Boolean alone.
- Compare current and desired values; do nothing if already equal.
- Record source/system and correlation ID.
- Bound any re-entry count and fail closed.
- Test with real workflow/blueprint/orchestration configuration in Sandbox.

Never suppress all automation merely to “make the loop stop” without understanding required approval/blueprint behavior.

## KB-724 Read–validate–write–re-read

```deluge
// Pseudocode-shaped Deluge: replace read/write tasks with the current host signatures.
current = read_authoritative_record(record_id);
preflight_ok = true;
if(current == null)
{
    info "preflight_failed missing_record";
    preflight_ok = false;
}
else if(current.get("status") != expected_status)
{
    info "preflight_failed stale_state";
    preflight_ok = false;
}

if(preflight_ok && !dry_run)
{
    write_response = perform_one_approved_write(record_id,changes,operation_key);
    confirmed = read_authoritative_record(record_id);
    if(confirmed.get("status") != desired_status)
    {
        info "reconciliation_required operation=" + operation_key;
    }
}
```

This block is intentionally not copy-valid Deluge because custom function headers/calls are host-specific. It is an algorithm. Replace every placeholder with a DOC-VERIFIED task and test it.

## KB-725 Pagination patterns

### Native page argument

Use a finite approved page List and stop when empty/short or when current response metadata says no more. This prevents an unbounded loop in a language without a general documented `while`.

### API cursor/token

Persist the next token after each confirmed page. If a run stops, resume from the confirmed token. Never mix results from two filters/orderings under one cursor.

### Changing datasets

Use stable sort keys and, where the API supports it, modified-time/version filters or cursors. Processing page numbers while records are inserted/deleted can skip/duplicate records. Idempotency is still required.

## KB-726 Batch write pattern

For CRM V8 bulk create/update, max 100 current records/call. Validate every record map, include `id` on updates, and split into deterministic batches. Treat a bulk response as record-by-record results; reconcile each failure instead of assuming all-or-none.

For Creator batch workflows, use documented sizes and one-account concurrency. Fifteen consecutive failures can terminate the workflow. Store last confirmed key/batch and avoid external calls inside large per-record loops where a bulk endpoint or Catalyst job is safer.

## KB-727 Multi-system saga

Deluge cannot make CRM, Books, Contracts, Sign, Creator, and WorkDrive one atomic transaction.

| Step | Example | Compensation/reconciliation |
|---|---|---|
| 1 | Create approved CRM relationship | Mark integration state; delete only if approved and safe. |
| 2 | Create Contracts draft | Cancel/archive draft or flag orphan. |
| 3 | Instantiate Sign draft | Delete/cancel draft before send if supported/approved. |
| 4 | Send signature request | Generally cannot “unsend” safely; revoke under approved process and notify. |
| 5 | Create Books customer/invoice | Void/credit/correct under accounting policy; do not delete history casually. |
| 6 | Upload controlled document | Move/version/restrict under retention policy. |

Persist each step and downstream ID. Never proceed to the next irreversible step unless prior state is confirmed and the gate is approved.

## KB-728 Privacy-safe logging

Allowed examples: operation name; correlation ID; system/module; record ID suffix/hash; page/batch; count; HTTP/service code; elapsed time; error class; retry/reconciliation state.

Do not log: Authorization headers/tokens; Connection material; full request/response; names/emails/phones/addresses; lease/document content; signatures; background/credit data; bank/payment data; portal auth codes; signed URLs; raw webhook bodies.

Sanitization is not simply replacing an email with `***`; nested payloads may contain hidden PII. Build logs from an allowlist of fields.

## KB-729 Input and response schema validation

Before a task call:

- Required keys present.
- No unknown high-risk keys.
- Correct runtime types after explicit conversion.
- IDs numeric/text as the endpoint expects.
- Picklist/status values from live metadata.
- Currency/date/time format and zone explicit.
- Lists within documented size.
- Text lengths and file sizes/types bounded.
- External ID normalized and unique.

After response:

- Status/code success.
- Expected object/key type.
- Identifier present.
- No partial-record errors hidden in list.
- Pagination metadata captured.
- Authoritative re-read matches critical fields.

## KB-730 Configuration versus secrets

Safe configuration includes module API names, form/report link names, organization IDs, Connection link names, template IDs, folder IDs, endpoint bases, feature flags, and limits—but some may still be sensitive operational metadata. Store them in approved environment/configuration mechanisms and sanitized field maps, not scattered literals.

Secrets include tokens, passwords, client secrets, API keys, private signing material, and authentication codes. Keep them in Connections/secret management only. Never upload them to this project, GitHub, logs, fixtures, or the PDF.

## KB-731 External communication gate

Before email/SMS/Sign/Contracts negotiation/notice:

1. Approved template and legal/business authority.
2. Current recipient identity, role, address/phone, consent/opt-out rules.
3. Deduplication key and prior-send search.
4. Dry-run manifest with counts and sanitized IDs.
5. Approval for bulk or high-impact send.
6. Single send attempt; ambiguous timeout → reconcile, do not resend.
7. Delivery/signing callback with authenticity and deduplication.
8. Retain evidence in the owning system under policy.

## KB-732 File/document safety

Validate file size/type/content, source, destination permissions, retention, naming, checksum/version, and whether the operation replaces an existing file. Avoid signed/public URLs in logs. For signed leases, Contracts owns lifecycle, Sign owns signing evidence, and WorkDrive may own controlled stored output—the same PDF’s copies do not change those authorities.

<!-- PAGEBREAK -->

# Part VIII — Testing, debugging, and anti-patterns

## KB-800 Minimum verification ladder

| Level | Evidence | What it proves | What it does not prove |
|---|---|---|---|
| Static review | Straight quotes, semicolons, balanced blocks, exact task page, correct host | Obvious syntax/source errors reduced | Compilation, permissions, response shape |
| Editor compile/save | Target product accepts code/header | Grammar and available task/function in that context | Runtime data/permissions/side effects |
| Unit-like function test | Sanitized deterministic inputs/expected outputs | Pure transforms and guards | Workflow context or external integration |
| Sandbox task test | Scoped Connection, test records, captured response fixture | Endpoint, scope, shape, trigger behavior | Production data/config equality |
| Negative/failure test | Null, empty, duplicates, 4xx/5xx, timeout, permission, partial result | Fail-closed behavior and safe logging | All provider outages/races |
| Dry run | Live target selection and proposed write set, no side effects | Current targeting/schema/preconditions | Actual write permission/result |
| Canary | One approved low-risk live record | Production integration at small scope | Bulk behavior |
| Reconciliation | Authoritative re-read and cross-system IDs/totals | Business state matches intent | Long-term drift without monitoring |
| Rollback drill | Tested reversal/compensation | Recoverability under defined case | Irreversible communication/signature effects |

## KB-801 Test case matrix

Every reusable function/task wrapper should cover:

- Normal valid input.
- Null and missing Map key.
- Blank/whitespace text.
- Empty list/map/collection.
- Wrong type and failed conversion.
- Minimum/maximum text/list/file size.
- Duplicate external ID: zero, one, and multiple matches.
- Stale status/version between read and write.
- Permission denied/expired Connection.
- HTTP 400/401/403/404/409/429/500 and Deluge timeout.
- Success HTTP with service-level failure code.
- Partial bulk success.
- Pagination first/middle/last page and changing dataset.
- Repeated webhook/event/retry.
- Dry-run path produces no writes.
- Workflow trigger enabled and suppressed cases.
- Privacy check: logs contain no prohibited fields.

## KB-802 Sanitized fixtures

Use fictional names such as Avery Example and test domains like `example.invalid`; generated non-production IDs; invented addresses that cannot be confused with tenants; fake amounts clearly marked; and minimal response objects containing only required keys.

Never copy a production payload and “redact a few fields.” Nested custom fields, notes, URLs, file names, tokens, and metadata can still identify people or systems.

## KB-803 Debug decision tree

### Save/compile error

Check semicolons, braces, straight quotes, undefined/case-mismatched variable, reserved keyword, function return path, argument count/type/order, host availability, and optional-argument placeholders.

### Null/index/cast runtime error

Check actual response type; absent key versus null; empty list; zero-based index; conversion input; REST envelope versus native task return; and whether an error response replaced the expected success object.

### HTTP/auth failure

Check data-center domain, endpoint/method, Connection owner/status, scopes, organization/account ID, resource permission, content type/body serialization, query encoding, and rate limit. Do not expose the Authorization header while debugging.

### “Success” but wrong business state

Check service-level code, nested per-record errors, workflow/approval/blueprint/orchestration trigger behavior, eventual indexing, stale read, wrong organization/module ID, partial update/replace-all lists, and authoritative re-read.

### Duplicate side effect

Stop retries. Query by external/operation key. Determine whether the original call completed despite timeout. Reconcile and use approved compensation. Fix state persistence before resuming.

## KB-804 Common compiler/runtime messages

The current error catalog includes missing semicolons, undefined variables, missing return statements, “function needs to be assigned,” invalid assignment of void functions, argument count/type mismatch, invalid JSON, divide by zero, substring/list index out of bounds, null operation, modulo type mismatch, invalid nonnumeric comparison, and failed casts such as Number to Map.

Source: https://www.zoho.com/deluge/help/error-messages.html . Status: DOC-VERIFIED categories; exact wording can change.

## KB-805 Hallucination and anti-pattern checklist

Reject code containing any of the following unless a current official page proves it in the named host:

- `throws`/`throw` as if Deluge were Java.
- `while`, `do while`, or invented range syntax such as `{1..N}`.
- Generic SQL (`SELECT`, `INSERT INTO ... VALUES`) instead of Creator’s DSL/API task.
- Creator `Form[criteria]`, `input`, `old`, or `insert into` inside CRM/Books/Flow.
- Legacy `zoho.crm.*` signature mixed with `zoho.crm.v8.*` arguments/response.
- REST `{data:[...]}` envelope assumed for a native Deluge wrapper that returns a List/Map.
- Display labels used as CRM API names or Creator link names.
- `Properties` emitted when the known underlying CRM module is `Accounts`.
- `Rental_Applications` emitted when the known context is renamed `Deals` without metadata.
- Map `containsKey` or Collection `containKey` silently swapped.
- Corrected spelling `Occurrence` when the documented function contains `Occurence`.
- Optional connection passed without preceding optional maps/arguments.
- Variable substituted for a Connection where the task requires a literal.
- Embedded OAuth token/API key/client secret.
- `response != null` treated as success.
- A Books update that omits existing line items.
- Bulk update without per-record result reconciliation.
- Upsert on a non-unique/missing match field.
- First-search-result selection when multiple records match.
- Unbounded loop/page count or external call inside large record loop.
- Blind retry of create/payment/invoice/sign/send/folder/contract operation.
- Sign draft creation and send combined without an approval gate.
- Contracts `UPDATE` silently changed to PUT/PATCH.
- WorkDrive overwrite flag `true` without explicit replacement approval.
- Sites user-specific Dynamic Content left cached.
- Catalyst described as a general Deluge serverless runtime.
- Flow Connection passed to a predefined integration task inside a custom function despite current restriction.
- Full payload/PII/token/document logged with `info`.
- Merge/save described as deployed/live.
- Legal/accounting/fair-housing behavior invented by code.

## KB-806 Legacy recognition and migration

Legacy pages/code may contain unversioned CRM tasks, `uploadDocument` for Sign, old `invokeURL` function/getURL/postURL forms, authtokens in query/header values, 2018 Creator UI paths, incomplete data types, and old limits. Recognize them for migration only.

Migration procedure:

1. Identify the exact current host/trigger.
2. Inventory every side effect and existing automation dependency.
3. Replace credentials with a Connection and least scopes.
4. Map legacy task to current native V8/task or REST endpoint.
5. Export live schema/API/link names.
6. Rewrite response parsing from a captured current fixture.
7. Make trigger behavior explicit.
8. Add idempotency, pagination, safe logging, dry run, and reconciliation.
9. Compiler/sandbox test both success and failure.
10. Deploy canary with rollback; retain migration evidence.

Sources: https://www.zoho.com/deluge/help/old-to-new-framework.html and release notes. Status: DOC-VERIFIED migration rationale.

<!-- PAGEBREAK -->

# Part IX — Quick-reference grammar and templates

## KB-900 Core syntax sheet

```deluge
// Assignment and containers
name = "Sample";
count = 0;
dry_run = true;
items = List();
payload = Map();
items.add("one");
payload.put("items",items);

// Condition
if(payload != null)
{
    if(payload.containKey("items"))
    {
        items = payload.get("items");
    }
}
if(items == null)
{
    items = List();
}

// Iteration
for each item in items
{
    if(item == null)
    {
        continue;
    }
    info item;
}

// Runtime error handling
try
{
    number_value = candidate.toLong();
}
catch (error_value)
{
    info "conversion_failed line=" + error_value.lineNo;
    number_value = null;
}
```

Status: language-level reference; compiler test in target host.

## KB-901 Safe native-task template

```deluge
// 1. Validate input and tenant-specific identifiers.
// 2. Read authoritative current state.
// 3. Detect duplicate/stale state.
// 4. Build minimal changes and explicit options.
// 5. Emit sanitized dry-run write set.
// 6. Execute once if approved.
// 7. Validate response code/shape/ID.
// 8. Re-read and reconcile.
// 9. Record sanitized evidence or reconciliation state.
```

## KB-902 Safe HTTP JSON template

```deluge
headers = Map();
headers.put("Accept","application/json");
headers.put("Content-Type","application/json");

response = invokeurl
[
    url: approved_url
    type: POST
    headers: headers
    body: payload.toString()
    connection: "approved_connection"
    detailed: true
];

// Inspect the documented detailed-response status/content keys in this host.
// Validate both HTTP status and service-level code before nested reads.
```

Status: DOC-VERIFIED attributes; detailed response shape and endpoint COMPILER/API TEST REQUIRED.

## KB-903 CRM V8 explicit-trigger template

```deluge
record_map = Map();
record_map.put("Last_Name","Example");
record_map.put("GH_External_ID",external_id);

trigger_list = List();
// Add only approved values: workflow, approval, blueprint, orchestration.

options_map = Map();
options_map.put("trigger",trigger_list);

response = zoho.crm.v8.createRecord(
    "Leads",
    record_map,
    options_map,
    "crm_connection"
);
```

Do not deploy this exact snippet until live field names, mandatory fields, connection behavior, triggers, and duplicate strategy are confirmed.

## KB-904 Creator local insert template

```deluge
existing = Maintenance_Requests[External_Request_ID == external_request_id];
if(existing.isEmpty())
{
    if(!dry_run)
    {
        new_id = insert into Maintenance_Requests
        [
            External_Request_ID = external_request_id
            Status = "Received"
        ];
        thisapp.after_maintenance_insert(new_id);
    }
}
else
{
    info "duplicate_prevented external_key_hash=" + external_key_hash;
}
```

All form/field/function link names are placeholders. The explicit post-insert call compensates for local `insert into` not running target On Validate/On Success. COMPILER-TEST REQUIRED.

## KB-905 Books controlled-write template

```deluge
// Pseudocode comments define the mandatory production gates.
// - Resolve exact organization from approved configuration.
// - Read by stable external ID; fail on 0-or-many mismatch as required.
// - Re-fetch current balance/status/line items.
// - Build complete update payload; do not omit retained nested items.
// - If dry_run, output only sanitized field/count summary.
// - Execute once through "zbooks" only after live connection verification.
// - Require response.get("code") == 0 and expected resource ID.
// - Re-fetch and reconcile monetary totals.
```

## KB-906 Sign draft-only template

```deluge
draft = zoho.sign.createDocument(pdf_file,Map(),"sign_oauth_connection");
if(draft != null)
{
    if(draft.get("code") == 0)
    {
        request_id = draft.get("requests").get("request_id");
        // Persist draft ID and STOP. Sending requires a separate approved gate.
    }
}
```

## KB-907 WorkDrive no-overwrite template

```deluge
result = zoho.workdrive.uploadFile(
    file_object,
    approved_folder_id,
    encodeUrl(approved_file_name),
    false,
    "workdrive_connection"
);
```

## KB-908 AI answer template

When ChatGPT/Codex responds to a Deluge implementation request, use this structure:

1. **Resolved context:** host, trigger, API version, owning system, execution identity.
2. **Required live inputs:** module/field/link names, connection, scopes, plan/DC, approved behavior.
3. **Chosen interface:** native task / `invokeAPI` / `invokeUrl` / Catalyst, with official URL.
4. **Side effects:** writes, triggers, communications, money, sharing, deletion.
5. **Code status:** DOC-VERIFIED signature; COMPILER-TEST REQUIRED unless evidence exists.
6. **Code:** ASCII quotes, semicolons, null/type/response guards, bounded paging.
7. **Safety:** dry run, duplicate/idempotency key, proposed write set, reconciliation, rollback.
8. **Test matrix:** success, boundary, failure, permission, repeat, trigger, privacy.
9. **Deployment evidence:** PR/version/environment/smoke/monitoring/rollback—not merely “saved.”

<!-- PAGEBREAK -->

# Appendix A — Official source registry

## A-001 Language core

- Overview: https://www.zoho.com/deluge/help/
- Release notes: https://www.zoho.com/deluge/help/release-notes.html
- Variables: https://www.zoho.com/deluge/help/variables.html
- Zoho variables: https://www.zoho.com/deluge/help/zoho-variables.html
- Data types: https://www.zoho.com/deluge/help/datatypes.html
- Expressions: https://www.zoho.com/deluge/help/expression.html
- Operators: https://www.zoho.com/deluge/help/operators.html
- Criteria: https://www.zoho.com/deluge/help/criteria-conditional-statements.html
- Conditions: https://www.zoho.com/deluge/help/conditional-statements/condition.html
- Try/catch: https://www.zoho.com/deluge/help/misc-statements/try-catch.html
- Error catalog: https://www.zoho.com/deluge/help/error-messages.html
- Keywords: https://www.zoho.com/deluge/help/keywords.html
- Generic limitations: https://www.zoho.com/deluge/help/limitations.html
- Old/new Creator framework: https://www.zoho.com/deluge/help/old-to-new-framework.html

## A-002 Functions and tasks

- Built-ins root: https://www.zoho.com/deluge/help/built-in-functions.html
- Text: https://www.zoho.com/deluge/help/functions/text.html
- Number: https://www.zoho.com/deluge/help/functions/number.html
- Date-Time: https://www.zoho.com/deluge/help/functions/date-time.html
- Time: https://www.zoho.com/deluge/help/functions/time.html
- List: https://www.zoho.com/deluge/help/functions/list.html
- Map: https://www.zoho.com/deluge/help/functions/key-value.html
- Collection: https://www.zoho.com/deluge/help/functions/collection.html
- Conversion: https://www.zoho.com/deluge/help/functions/conversion.html
- Logical: https://www.zoho.com/deluge/help/functions/logical.html
- Type checks: https://www.zoho.com/deluge/help/functions/type-check.html
- XML/JSON: https://www.zoho.com/deluge/help/functions/xml.html
- Utilities: https://www.zoho.com/deluge/help/functions/utilities.html
- File methods: https://www.zoho.com/deluge/help/file-methods.html
- Encryption: https://www.zoho.com/deluge/help/encryption-tasks.html
- Tasks root: https://www.zoho.com/deluge/help/deluge-tasks.html
- Data access: https://www.zoho.com/deluge/help/data-access.html
- List manipulation: https://www.zoho.com/deluge/help/list-manipulations.html
- Map manipulation: https://www.zoho.com/deluge/help/map-manipulations.html
- Subforms: https://www.zoho.com/deluge/help/subform-tasks.html
- Client functions: https://www.zoho.com/deluge/help/client-functions.html
- Notifications: https://www.zoho.com/deluge/help/notifications-using-deluge.html
- FTP: https://www.zoho.com/deluge/help/ftp-task.html
- SFTP: https://www.zoho.com/deluge/help/sftp-task.html

## A-003 HTTP and security

- Integration tasks: https://www.zoho.com/deluge/help/integration-tasks.html
- `invokeUrl`: https://www.zoho.com/deluge/help/webhook/invokeurl-api-task.html
- `invokeUrl` limits: https://www.zoho.com/deluge/help/web-data/invokeurl-task/limitations.html
- `invokeAPI`: https://www.zoho.com/deluge/help/webhook/invokeapitask.html
- Connections: https://www.zoho.com/deluge/help/connections.html

## A-004 CRM

- Functions: https://www.zoho.com/crm/developer/docs/functions/
- Setup contexts: https://www.zoho.com/crm/developer/docs/functions/set-up-functions.html
- Functions limits: https://www.zoho.com/crm/developer/docs/functions/functions-limits.html
- Function analytics: https://www.zoho.com/crm/developer/docs/functions/function-analytics.html
- CRM V8 task root: https://www.zoho.com/deluge/help/crm-integration-tasks-V8.html
- Create: https://www.zoho.com/deluge/help/crm/create-record-V8.html
- Get records: https://www.zoho.com/deluge/help/crm/get-records-V8.html
- Search: https://www.zoho.com/deluge/help/crm/search-records-V8.html
- Update: https://www.zoho.com/deluge/help/crm/update-record-V8.html
- Bulk update: https://www.zoho.com/deluge/help/crm/bulk-update-records-V8.html
- Upsert: https://www.zoho.com/deluge/help/crm/upsert-record-V8.html

## A-005 Books and Creator

- Books task root: https://www.zoho.com/deluge/help/books-tasks.html
- Books mark status: https://www.zoho.com/deluge/help/books/mark-status.html
- Books OAuth/API: https://www.zoho.com/books/api/v3/oauth/
- Books functions: https://www.zoho.com/us/books/help/settings/automation/workflow-actions/functions.html
- Books schedules: https://www.zoho.com/us/books/help/settings/automation/schedules.html
- Books buttons: https://www.zoho.com/us/books/help/settings/customization/custom-buttons.html
- Books related lists: https://www.zoho.com/us/books/help/settings/customization/related-lists.html
- Books Connections: https://www.zoho.com/us/books/help/settings/connections.html
- Creator task root: https://www.zoho.com/deluge/help/creator-tasks.html
- Creator add: https://www.zoho.com/deluge/help/data-access/add-record.html
- Creator update wrapper: https://www.zoho.com/deluge/help/creator/update-record.html
- Creator workflows: https://help.zoho.com/portal/en/kb/creator/developer-guide/workflows/understand-workflows/articles/understand-workflows
- Creator performance: https://help.zoho.com/portal/en/kb/creator/developer-guide/others/platform-performance/articles/platform-performance
- Creator environments: https://help.zoho.com/portal/en/kb/creator/developer-guide/environments/articles/managing-applications-in-the-environments
- Creator custom APIs: https://help.zoho.com/portal/en/kb/creator/developer-guide/microservices/custom-api/articles/understand-custom-apis

## A-006 Contracts, Sign, WorkDrive, Flow

- Contracts API: https://www.zoho.com/contracts/api/introduction.html
- Contracts OAuth: https://www.zoho.com/contracts/api/understanding-the-basics/oauth-authentication.html
- Contracts create: https://www.zoho.com/contracts/api/contract/create-contract.html
- Contracts update: https://www.zoho.com/contracts/api/contract/update-contract.html
- Contracts import: https://www.zoho.com/contracts/api/contract/import-contract.html
- Contracts negotiation: https://www.zoho.com/contracts/api/negotiation/send-for-negotiation.html
- Sign task root: https://www.zoho.com/deluge/help/sign-tasks.html
- Sign create: https://www.zoho.com/deluge/help/sign/create-document.html
- Sign update: https://www.zoho.com/deluge/help/sign/update-document.html
- Sign submit: https://www.zoho.com/deluge/help/sign/submit-request.html
- Sign templates: https://www.zoho.com/deluge/help/sign/get-templates.html
- Sign CRM callback guide: https://help.zoho.com/portal/en/kb/zoho-sign/solutions-guide/zoho-deluge-integration/articles/how-to-set-up-a-callback-function-in-crm-to-add-zoho-sign-document-details-that-is-triggered-by-the-zoho-sign-webhook
- WorkDrive task root: https://www.zoho.com/deluge/help/workdrive-tasks.html
- WorkDrive upload: https://www.zoho.com/deluge/help/workdrive/upload-file.html
- WorkDrive functions: https://help.zoho.com/portal/en/kb/workdrive/custom-functions-connections/articles/working-with-custom-functions-in-workdrive
- Flow functions: https://help.zoho.com/portal/en/kb/flow/user-guide/create-a-flow/articles/using-custom-functions
- Flow FAQ: https://www.zoho.com/flow/help/faq.html

## A-007 Catalyst, Sites, and Forms

- Catalyst Functions: https://docs.catalyst.zoho.com/en/serverless/help/functions/implementation/
- Catalyst runtime support: https://docs.catalyst.zoho.com/en/serverless/help/functions/runtime-support/
- Catalyst Advanced I/O: https://docs.catalyst.zoho.com/en/serverless/help/functions/advanced-io/
- Catalyst API Gateway: https://docs.catalyst.zoho.com/en/cloud-scale/help/api-gateway/key-concepts/
- Catalyst ConvoKraft Deluge exception: https://docs.catalyst.zoho.com/en/convokraft/help/actions/bot-logic/deluge-functions/defining-deluge-functions/
- Sites Dynamic Content: https://help.zoho.com/portal/en/kb/zohosites/help-guide/manage/dynamic-content/articles/dynamic-content
- Sites Connections: https://help.zoho.com/portal/en/kb/zohosites/help-guide/manage/dynamic-content/articles/zoho-sites-connections
- Sites Code Snippets: https://help.zoho.com/portal/en/kb/zohosites/help-guide/manage/code-snippets/articles/code-snippets-24-3-2022
- Forms webhooks: https://help.zoho.com/portal/en/kb/forms/integrations/webhooks/articles/webhook-configuration
- Forms Connections: https://help.zoho.com/portal/en/kb/forms/adminguide/articles/connections-control-panel

<!-- PAGEBREAK -->

# Appendix B — Maintenance manifest

## B-001 Quarterly update checklist

- Review Deluge release notes since 2026-07-20.
- Compare CRM task root for API generation after V8.
- Re-verify all signatures used in active repository code.
- Re-check `invokeAPI` supported service list and all time/file limits.
- Re-check embedded-credential deprecation/security changes.
- Re-check Creator/CRM/Flow/WorkDrive limits and Books workflow component usage.
- Re-check Contracts method compatibility and native-task availability.
- Re-check Flow Connection restriction.
- Re-check Catalyst supported runtimes and Sites cache behavior.
- Export sanitized CRM modules/fields and Creator form/report link metadata.
- Verify Books organization/context maps and Connections.
- Verify Sign templates/actions/roles and WorkDrive folders/permissions.
- Run compiler/sandbox regression fixtures and update evidence labels.
- Regenerate searchable PDF; render every page; inspect fonts, tables, links, code, and page numbers.

## B-002 Release-note highlights affecting this edition

Current Deluge release notes include 2026 additions such as CRM V8 integration tasks, Base32 functions, expanded Base64 charset behavior, file-password support, and expanded `convertToPDF` options. Recent 2025 changes include OPTIONS support, broader HTTP body handling, and deprecation of credentials embedded directly in `invokeUrl`; Connections are the required design direction.

Source: https://www.zoho.com/deluge/help/release-notes.html . Status: DOC-VERIFIED summary; always open the current page.

## B-003 Known documentation conflicts retained intentionally

| Conflict | Handbook rule |
|---|---|
| CRM search criterion says field label while API conventions/examples use API-style name | Use live metadata/API name and sandbox test. |
| CRM V8 get records mentions `field` while examples/current API use `fields` | Use current per-task API schema/editor; do not guess. |
| Books uses `getRecordsByID` in task name but `getRecordsById` in examples | Editor autocomplete/compiler decides exact casing. |
| Books prose says label names while examples align with API parameters | Use current API request schema and live test. |
| Older Sign pages use `uploadDocument`; current task index uses `createDocument` | Prefer current index/editor. |
| Contracts update method is `UPDATE`, absent from `invokeUrl` methods | Direct Deluge update unsupported until verified; proxy/confirm. |
| CRM current credit table and note disagree | Inspect live account calculator/usage. |
| File limits differ across host/task/target | Enforce smallest applicable limit. |
| Generic Deluge limits differ from product-specific pages | Product/trigger/current plan page wins. |

## B-004 AI ingestion metadata

```text
DOCUMENT_ID: GH-DELUGE-KB-2026-07
VERIFIED_DATE: 2026-07-20
PRIMARY_AUTHORITY: OFFICIAL_ZOHO_DOCS
DEPLOYMENT_AUTHORITY: LIVE_SANITIZED_METADATA_AND_RUNTIME_EVIDENCE
DEFAULT_CODE_STATUS: COMPILER_TEST_REQUIRED
DEFAULT_SCHEMA_STATUS: LIVE_METADATA_REQUIRED
HIGH_RISK_DEFAULT: FAIL_CLOSED
PREFERRED_INTERFACE_ORDER: NATIVE_CURRENT_TASK > INVOKEAPI_SUPPORTED > INVOKEURL_CONNECTION > CATALYST
PROHIBITED: SECRETS, PII_LOGS, INVENTED_API_NAMES, BLIND_RETRIES, UNBOUNDED_LOOPS, POLICY_IN_CODE
GH_CRM_KNOWN: Leads=Leads; Properties=Accounts; RentalApplications=Deals; MaintenanceRequests=Cases; Units=verify Units
GH_BOOKS_CONNECTION_REPO_OBSERVED: zbooks
```

## B-005 Final usage note

Use this handbook as a high-recall map and safety contract. For a concrete script, cite the exact current task/function/API page, retrieve tenant metadata, compile in the named product, test with sanitized fixtures, run dry mode, and reconcile the owning system after execution. That process—not any static PDF—is what turns Deluge knowledge into dependable automation.
