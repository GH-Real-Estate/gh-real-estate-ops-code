# Live Upsert Troubleshooting

Use this when dry-run routing works but live mode returns `502` with `zoho_request_failed`.

## Meaning

`zoho_request_failed` during live mode means the function reached Zoho CRM and Zoho rejected the live `Leads/upsert` request. This is different from dry-run routing failure.

Most likely causes:

1. OAuth token lacks Leads write scope.
2. A required Lead field is missing.
3. A picklist value is not available in the CRM layout.
4. A lookup field is pointed at the wrong module/record ID.
5. A field API name or field type does not match the current CRM schema.

## Immediate Safety Step

Switch production back to dry-run before troubleshooting:

```text
ZILLOW_WEBHOOK_DRY_RUN=true
DRY_RUN=true
LIVE_MODE_ENABLED=false
LIVE_MODE_CONFIRMATION=
```

Redeploy production after saving variable changes.

## PowerShell: Minimal Lead Upsert Test

This verifies that the refresh token can write to the Leads module and that the minimum required fields are accepted.

```powershell
$stamp = Get-Date -Format "yyyyMMddHHmmss"
$leadKey = "manual:zillow:minimal:$stamp"

$minimalLead = @{
  Last_Name = "Tenant"
  Company = "9401 Nieman Road"
  Email = "minimal.live.test.$stamp@example.com"
  Lead_Source = "Zillow"
  Lead_Status = "New Zillow Inquiry"
  Zillow_Lead_Key = $leadKey
}

$upsertBody = @{
  data = @($minimalLead)
  duplicate_check_fields = @("Zillow_Lead_Key")
  trigger = @()
} | ConvertTo-Json -Depth 10

try {
  $minimalUpsert = Invoke-RestMethod `
    -Method Post `
    -Uri "https://www.zohoapis.com/crm/v8/Leads/upsert" `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Zoho-oauthtoken $accessToken" } `
    -Body $upsertBody

  $minimalUpsert | ConvertTo-Json -Depth 10
} catch {
  $status = $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  $bodyText = $reader.ReadToEnd()

  "STATUS: $status"
  "BODY:"
  $bodyText
}
```

Expected: Zoho returns success and creates one minimal test Lead.

If this fails, the problem is OAuth scope, duplicate field configuration, or required Lead field setup.

## PowerShell: Full Lead Upsert Test

Run only after the minimal test succeeds. This mirrors the Zillow test payload more closely.

```powershell
$stamp = Get-Date -Format "yyyyMMddHHmmss"
$leadKey = "manual:zillow:full:$stamp"
$nowIso = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss+00:00")

$fullLead = @{
  First_Name = "Live Test"
  Last_Name = "Tenant"
  Company = "9401 Nieman Road"
  Email = "full.live.test.$stamp@example.com"
  Mobile = "+19135550100"
  Lead_Source = "Zillow"
  Lead_Status = "New Zillow Inquiry"
  Requested_Property = @{ id = "6543229000000811002" }
  Requested_Unit = @{ id = "6543229000003667005" }
  Requested_Move_In_Date = "2026-07-07"
  Inquiry_Message = "Message: Live upsert diagnostic only. Delete this CRM Lead."
  Zillow_Renter_Profile_Summary = "Bedrooms sought: 2`nBathrooms sought: 1"
  Zillow_Lead_Key = $leadKey
  Zillow_Listing_ID = "2097508172"
  Zillow_Lead_Type = "tourRequest"
  Zillow_Provider_Model_ID = "0"
  Zillow_Property_Address_Raw = "9401 Nieman Road, Unit 3, Overland Park, KS 66214"
  Zillow_Listing_Street = "9401 Nieman Road"
  Zillow_Listing_Unit = "Unit 3"
  Zillow_Listing_City = "Overland Park"
  Zillow_Listing_State = "KS"
  Zillow_Listing_Postal_Code = "66214"
  Zillow_Listing_Contact_Email = "leasing@example.com"
  Zillow_Source_Payload_Hash = "manual-full-test-$stamp"
  Zillow_Received_At = $nowIso
  Last_Zillow_Sync_At = $nowIso
  Zillow_Intake_Status = "Routing Matched"
  Zillow_Raw_Field_Keys = "manual diagnostic"
  Zillow_Raw_Payload_Stored = $false
  Description = "Manual full Zillow upsert diagnostic. Delete after test."
}

$upsertBody = @{
  data = @($fullLead)
  duplicate_check_fields = @("Zillow_Lead_Key")
  trigger = @()
} | ConvertTo-Json -Depth 20

try {
  $fullUpsert = Invoke-RestMethod `
    -Method Post `
    -Uri "https://www.zohoapis.com/crm/v8/Leads/upsert" `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Zoho-oauthtoken $accessToken" } `
    -Body $upsertBody

  $fullUpsert | ConvertTo-Json -Depth 20
} catch {
  $status = $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  $bodyText = $reader.ReadToEnd()

  "STATUS: $status"
  "BODY:"
  $bodyText
}
```

Expected: Zoho returns success and creates one full diagnostic Lead.

If minimal succeeds but full fails, use the returned error body to identify the exact rejected field.

## Cleanup

Delete diagnostic Leads after testing:

```text
minimal.live.test.*@example.com
full.live.test.*@example.com
```

## Return To Normal Test State

After diagnostics, keep production in dry-run until Zillow sends an official test callback:

```text
ZILLOW_WEBHOOK_DRY_RUN=true
DRY_RUN=true
LIVE_MODE_ENABLED=false
LIVE_MODE_CONFIRMATION=
```
