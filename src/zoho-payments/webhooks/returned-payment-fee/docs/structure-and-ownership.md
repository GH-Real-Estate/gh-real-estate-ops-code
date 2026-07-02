# Structure And Ownership

This package is intentionally stored under:

```text
src/zoho-payments/webhooks/returned-payment-fee/
```

## Ownership Rule

Organize by the system that owns the event or runtime boundary, not by the accounting record created at the end.

For returned-payment / returned-check fee handling, the ownership chain is:

```text
Zoho Payments event
-> Zoho Catalyst Advanced I/O function
-> Zoho Payments API verification
-> Zoho Books invoice action
```

That means this is a Zoho Payments webhook integration with a Catalyst runtime and a Zoho Books write target.

## Why It Is Not Under `src/zoho-books/`

The function creates a Zoho Books invoice, but Zoho Books is not the trigger source. Placing the package under `src/zoho-books/` would make it look like a Books scheduled/custom function, which it is not.

Zoho Books remains the accounting source of truth for the resulting returned-fee invoice. The code package still belongs under Zoho Payments because a Zoho Payments failure event starts the workflow.

## Runtime Package Boundary

The deployable Catalyst package root is:

```text
src/zoho-payments/webhooks/returned-payment-fee/
```

Runtime files in that package include:

```text
src/index.js
package.json
package-lock.json
catalyst-config.json
```

Supporting documentation and tests stay beside the package because they explain how this exact webhook should be deployed, verified, and recovered.

## Naming

Use `returned-payment-fee` as the repository folder name even when the business phrase is "returned check fee." Zoho Payments can represent ACH, card, or other payment failures, and the code must stay aligned to the payment event source rather than one payment method label.
