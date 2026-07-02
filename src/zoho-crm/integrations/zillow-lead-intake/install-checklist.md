# Install Checklist

- [ ] Create/confirm CRM fields in Contacts.
- [ ] Create/confirm CRM fields in Deals/Rental Applications.
- [ ] Mark `Zillow_Lead_Key` unique.
- [ ] Confirm Deals mandatory fields: `Deal_Name`, `Stage`, `Closing_Date`.
- [ ] Confirm Rental Application stages include `New Inquiry`.
- [ ] Create CRM view: Zillow Leads - Manual Review.
- [ ] Create CRM view: Zillow Leads - New Inquiry.
- [ ] Create Zoho OAuth client and refresh token.
- [ ] Add Catalyst environment variables from `.env.example`.
- [ ] Keep `DRY_RUN=true` for first deployment.
- [ ] Send fake dry-run payload.
- [ ] Configure property/unit map with real CRM record IDs.
- [ ] Ask Zillow to send a test callback.
- [ ] Turn live mode on only after dry-run output matches expected CRM fields.
- [ ] Re-send same fake live payload and confirm no duplicate Rental Application is created.
- [ ] Record deployment in `docs/runbooks/deployment-log.md`.
