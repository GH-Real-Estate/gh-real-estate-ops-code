# GH Real Estate Operations Dashboard

**Specification ID:** GH-ZOHO-CRM-DASH-001

**Version:** 1.0

**Effective date:** July 25, 2026

**Status:** Governed target specification; deployment blocked

**Deployment boundary:** Approved MCP servers only; Browser control is prohibited unless the user separately authorizes it

## Purpose

This specification defines one concise Zoho CRM operations dashboard for GH
Real Estate. It is designed to answer the daily operating questions:

- Which units are occupied, available, or not ready?
- Where are current rental applications in the review funnel?
- Which approved applications are waiting for a Lease?
- Which leases are approaching move-in or expiration?
- Which maintenance requests and inspections require attention?

It is not an accounting dashboard. CRM pipeline amounts and contractual rent
are operational measures. Zoho Books remains authoritative for invoices,
payments, credits, deposits, balances, and actual income.

## Current deployment status

The approved MCP surface used for the July 25 reconciliation does not expose
Zoho CRM report or dashboard create, update, delete, or readback operations.
No live report, component, dashboard, sharing rule, filter, or scheduled
delivery was created.

This file is the controlled build manifest for a later MCP deployment. Do not
substitute Browser control or claim deployment from repository publication.

## Source-of-truth boundaries

| Measure | Owning system/module | Dashboard treatment |
|---|---|---|
| Application volume and progress | Rental Applications — standard Deals module, API `Deals` | CRM operational funnel |
| Potential monthly rent | Rental Applications `Amount`, only after its meaning and dependencies are formally reconciled | Optional pipeline measure; never label as income |
| Contractual recurring rent | Leases, API `Leases`, after a single authoritative monthly-rent definition is approved | Contracted-rent measure; not payment evidence |
| Unit occupancy and market readiness | Units, API `Units` | CRM operating measure |
| Lease dates and lifecycle | Leases, API `Leases` | CRM operating measure |
| Maintenance and inspections | Maintenance Requests, API `Cases`; Inspections, API `Inspections` | CRM operating measure |
| Invoices, payments, credits, deposits, balances, and actual income | Zoho Books | Excluded from this CRM dashboard |

Refundable security deposits and refundable pet deposits are liabilities, not
income. Never include them in a gross-income component.

## Dashboard definition

| Property | Target |
|---|---|
| Dashboard name | `GH Real Estate Operations` |
| Folder | `GH Real Estate Operations` |
| Audience | GH Real Estate administrator/owner and specifically authorized operators |
| Default period | Current month, with report-specific forward windows |
| Refresh | Native CRM refresh; no custom polling |
| Record access | Inherit least-privilege CRM sharing and field permissions |
| Export | Disabled unless separately approved |
| Scheduled email | Disabled by default |

The dashboard must not display applicant or tenant names, contact information,
screening details, protected characteristics, accommodation information,
sensitive notes, documents, or record-level financial data. Aggregate counts
are the default. Any permitted drill-down must inherit the viewer's CRM record
and field permissions.

## Required lifecycle prerequisites

Do not deploy Stage- or Lease-Status-based components until live metadata
readback confirms the following target definitions.

### Rental Applications Stage — standard Stage

Scope: one Deals pipeline named `Rental Applications`

Default: `Application Received`

History tracking: enabled

Sort: entered order

| Order | Stage | Category | Probability | Color |
|---:|---|---|---:|---|
| 1 | Application Received | Open | 10% | `#2563EB` |
| 2 | Screening In Progress | Open | 35% | `#D97706` |
| 3 | Decision Pending | Open | 60% | `#EA580C` |
| 4 | Approved - Lease Pending | Open | 90% | `#16A34A` |
| 5 | Lease Created | Closed Won | 100% | `#16A34A` |
| 6 | Closed - Not Proceeding | Closed Lost | 0% | `#DC2626` |

The verified `Decision` field retains the detailed result: Pending, Approved,
Approved with Conditions, Denied, Withdrawn, Duplicate, or No Response. Stage
must not duplicate those reasons.

### Lease Status — local picklist

API: `Lease_Status`

Default: `Draft`

Required: yes

History tracking: enabled

Sort: entered order

| Order | Value | Color |
|---:|---|---|
| 1 | Draft | `#2563EB` |
| 2 | Ready For Contract | `#7C3AED` |
| 3 | Contract Requested | `#7C3AED` |
| 4 | Sent For Signature | `#7C3AED` |
| 5 | Signed - Pending Move-In | `#D97706` |
| 6 | Active | `#16A34A` |
| 7 | Month-to-Month | `#2563EB` |
| 8 | Ended | `#6B7280` |
| 9 | Terminated | `#DC2626` |
| 10 | Cancelled | `#6B7280` |
| 11 | Archived | `#6B7280` |

Renewal and notice workflows are parallel processes. They must not be encoded
as mutually exclusive Lease Status values.

## Report and component manifest

Create reports first, verify their criteria and totals with sanitized test
records, and then create the dashboard components in the order below.

| Order | Report / component | Source | Type | Exact criteria and measure | Operator use |
|---:|---|---|---|---|---|
| 1 | Occupied Units | `Units` | KPI | Count records where `Unit_Status = Occupied` | Current occupied inventory |
| 2 | Vacant - Ready Units | `Units` | KPI | Count records where `Unit_Status = Vacant - Ready` | Immediately marketable inventory |
| 3 | Open Rental Applications | `Deals` | KPI | Count records where `Stage` is one of the first four target open stages | Current application workload |
| 4 | Open Emergency Maintenance | `Cases` | KPI | Count where `Emergency = true` and `Status` is not Completed, Closed, or Cancelled | Safety/urgency queue |
| 5 | Rental Application Funnel | `Deals` | Funnel | Count by `Stage` in exact target order | Application throughput and bottlenecks |
| 6 | Unit Market Status | `Units` | Donut | Count by `Market_Status` | Listing and leasing readiness |
| 7 | Approved Applications Awaiting Lease | `Deals` | Table/KPI | `Stage = Approved - Lease Pending`; oldest `Application_Received_At` first | Required Lease handoff |
| 8 | Upcoming Move-Ins — 30 Days | `Leases` | Table | `Lease_Status = Signed - Pending Move-In`; `Move_In_Date` from today through today + 30 days | Move-in preparation |
| 9 | Lease Expirations — 90 Days | `Leases` | Table/bar | `Lease_Status` is Active or Month-to-Month; nonblank `Lease_End_Date` from today through today + 90 days | Renewal/nonrenewal planning |
| 10 | Maintenance Queue | `Cases` | Stacked bar | Count open records by `Status`, stacked by `Priority`; exclude Completed, Closed, and Cancelled | Work allocation |
| 11 | Inspections Due or Overdue | `Inspections` | Table/bar | `Status` is not Completed, Cancelled, or Archived; nonblank `Due_Date` through today + 30 days | Inspection follow-up |
| 12 | Lease Lifecycle | `Leases` | Donut | Count by the exact 11-value `Lease_Status` target | Lease operating state |

For tables, show only non-sensitive business fields required to act, such as
record name, Unit, status, due date, and assigned owner. Do not include
applicant contact details, screening facts, payment information, or free-text
notes.

## Monetary component gates

### Potential Monthly Rent — optional, gated

The standard Deals field `Amount` currently has unresolved semantics and an
active-rule dependency. Do not create a dashboard component from it until:

1. the Big Deal rule and all other dependencies are audited;
2. the field is explicitly governed as application-stage monthly rent;
3. blank, zero, changed, approved, denied, duplicate, and withdrawn cases are
   tested; and
4. live metadata and report readback confirm the result.

If approved, label the component `Potential Monthly Rent`, never `Gross
Income`, `Revenue`, or `Rent Collected`.

### Contracted Monthly Rent — optional, gated

Do not sum `Monthly_Rent` or `Current_Base_Rent` today. Their current repository
warnings do not establish a single authoritative contractual-rent measure.

After an approved Lease charge model exists, a component may sum the
authoritative recurring contractual-rent field for Active and Month-to-Month
leases. Label it `Contracted Monthly Rent`. It remains distinct from invoiced,
earned, due, or collected income.

### Actual income — prohibited in this CRM dashboard

Gross rental income, billed rent, collected rent, accounts receivable,
delinquency, credits, refunds, and deposit liability must come from Zoho
Books. Use a Books dashboard for accounting operations or a governed Zoho
Analytics dashboard for a combined executive view. Corrections must return to
the owning system.

## MCP-only deployment procedure

When a supported Zoho CRM reports/dashboard MCP becomes available:

1. Confirm the GH Real Estate production organization and environment.
2. Read back the relevant module and field metadata.
3. Verify the six Stage values, categories, probabilities, default, order, and
   history setting.
4. Verify the 11 Lease Status values, order, default, mandatory flag, colors,
   and history setting.
5. Create the reports in the manifest using exact API names.
6. Read each report definition back and compare filters, groupings, measures,
   and visibility.
7. Create the dashboard and components in manifest order.
8. Apply least-privilege sharing and disable export/scheduled email unless
   separately approved.
9. Read the dashboard and every component back.
10. Compare component totals with the underlying reports using sanitized test
    records.
11. Record the deployment and rollback evidence in the production runbook.

If any required definition cannot be read back exactly, stop and leave the
dashboard undeployed.

## Acceptance checks

- No Browser control was used.
- Every report and dashboard write was performed through an approved MCP.
- Every report and component was read back after creation.
- Stage and Lease Status use exact approved values and order.
- Closed applications are excluded from open-work KPIs.
- Closed maintenance requests are excluded from the emergency and queue KPIs.
- Deposits are not presented as income.
- CRM pipeline value is not presented as actual income.
- No protected or sensitive applicant/tenant fields are exposed.
- A permitted user and a restricted user were each tested with sanitized
  records.

## Rollback

Rollback is a metadata operation, not a record deletion:

1. remove the dashboard components through an approved MCP;
2. remove the dashboard;
3. retire or remove the newly created reports after confirming no other
   dashboard, schedule, or workflow depends on them;
4. preserve CRM records and source fields;
5. read back the absence of the removed artifacts; and
6. revert this repository specification separately if the design itself is
   withdrawn.

The current state requires no live rollback because no dashboard or report was
created.
