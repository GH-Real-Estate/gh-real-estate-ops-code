# Smoke Test Checklist

Use before and after any live automation change.

## General

- [ ] Code in GitHub matches code installed in Zoho/runtime.
- [ ] Change is documented in deployment log.
- [ ] No secrets committed.
- [ ] No real tenant PII committed.
- [ ] Dry-run completed or not applicable.
- [ ] One controlled test completed.

## Apply Unused Credits

- [ ] New invoice with no unused credits does not apply anything.
- [ ] New invoice with matching-branch customer-payment credit applies the correct amount.
- [ ] New invoice with matching-branch credit note applies the correct amount.
- [ ] New invoice with matching-branch retainer payment applies the correct amount.
- [ ] Non-matching-branch credit is skipped.
- [ ] Running the function twice does not over-apply credits.
- [ ] Logs contain no PII, bank data, raw payloads, or secrets.

## Late Fee Guard

- [ ] Test invoice below threshold does not create a fee.
- [ ] Test invoice above threshold creates correct fee.
- [ ] Running the function twice does not duplicate the fee.
- [ ] Invoice template is correct.
- [ ] Time-zone behavior is correct.
- [ ] Logs contain no PII.

## Returned Payment Webhook

- [ ] Valid event accepted.
- [ ] Invalid signature rejected.
- [ ] Replayed event rejected or ignored.
- [ ] Duplicate returned-payment fee not created.
- [ ] Logs contain no bank data, PII, or secrets.

## Field maps

- [ ] Zoho Books item IDs verified.
- [ ] Zoho Books custom-field API names verified.
- [ ] Zoho CRM field names verified.
- [ ] Zoho Contracts merge fields verified.
