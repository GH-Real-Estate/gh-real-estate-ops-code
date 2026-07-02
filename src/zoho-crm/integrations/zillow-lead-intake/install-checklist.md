# Install Checklist

- [ ] Create/confirm CRM fields in Leads.
- [ ] Mark Leads field `Zillow_Lead_Key` unique.
- [ ] Confirm Leads mandatory fields: `Last_Name`, `Company`.
- [ ] Confirm Lead Status picklist supports the configured `DEFAULT_LEAD_STATUS`.
- [ ] Create CRM view: Zillow Leads - Manual Review.
- [ ] Create CRM view: Zillow Leads - New Inquiry / Not Contacted.
- [ ] Create Zoho OAuth client and refresh token.
- [ ] Add Catalyst environment variables from `docs/runtime-environment-template.md`.
- [ ] Keep `DRY_RUN=true` for first deployment.
- [ ] Send fake dry-run payload.
- [ ] Configure property/unit map with real CRM record IDs.
- [ ] Ask Zillow to send a test callback.
- [ ] Turn live mode on only after dry-run output matches expected CRM fields.
- [ ] Re-send same fake live payload and confirm no duplicate Lead is created.
- [ ] Record deployment in `docs/runbooks/deployment-log.md`.
