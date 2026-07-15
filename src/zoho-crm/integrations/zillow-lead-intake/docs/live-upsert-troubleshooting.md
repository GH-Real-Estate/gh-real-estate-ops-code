# Live Upsert Troubleshooting

Use this when dry-run routing works or the live endpoint is reachable, but live mode returns `502` and Catalyst logs show `zoho_request_failed`.

## Meaning

`zoho_request_failed` means the Catalyst function reached an outbound Zoho HTTP call and Zoho returned a non-2xx HTTP response.

This can happen in any of these places:

1. Zoho Accounts refresh-token exchange.
2. Zoho CRM Units search for dynamic unit routing.
3. Zoho CRM Leads upsert.
4. Optional Zoho CRM intake event upsert if enabled.

It is different from a Catalyst deployment failure. If DevOps logs show a request ID and `zoho_request_failed`, the function is running and the next problem is Zoho OAuth/CRM API configuration.

## Immediate Checks

Confirm the target Catalyst environment has these values:

```text
ZILLOW_WEBHOOK_DRY_RUN=false
DRY_RUN=false
LIVE_MODE_ENABLED=true
LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
ZOHO_CRM_LEADS_MODULE=Leads
ZOHO_CRM_UNITS_MODULE=Units
ENABLE_DYNAMIC_UNIT_ROUTING=true
DYNAMIC_UNIT_ROUTING_REQUIRED=false
UNIT_PROPERTY_LOOKUP_FIELD=Property
PROPERTY_UNIT_MAP_JSON={}
ZOHO_CRM_FIELD_MAP_JSON={}
ENABLE_CRM_INTAKE_EVENT_LOG=false
ENABLE_DRY_RUN_CRM_AUDIT_LOG=false
```

`DYNAMIC_UNIT_ROUTING_REQUIRED` should remain `false` during early live testing. If it is `true`, a Units search failure can reject the entire Zillow callback before the Lead is created.

## PowerShell: Get A Fresh Access Token

Do not paste tokens into ChatGPT or screenshots. Replace the three values locally in PowerShell.

```powershell
$clientId = "PASTE_ZOHO_CLIENT_ID_HERE"
$clientSecret = "PASTE_ZOHO_CLIENT_SECRET_HERE"
$refreshToken = "PASTE_ZOHO_REFRESH_TOKEN_HERE"

try {
  $tokenResponse = Invoke-RestMethod `
    -Method Post `
    -Uri "https://accounts.zoho.com/oauth/v2/token" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body @{
      refresh_token = $refreshToken
      client_id = $clientId
      client_secret = $clientSecret
      grant_type = "refresh_token"
    }

  $accessToken = $tokenResponse.access_token
  "TOKEN_OK length=$($accessToken.Length) expires_in=$($tokenResponse.expires_in)"
} catch {
  "TOKEN_FAILED"
  if ($_.Exception.Response) {
    "STATUS: $([int]$_.Exception.Response.StatusCode)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    "BODY:"
    $reader.ReadToEnd()
  } else {
    $_.Exception.Message
  }
}
```

Expected: `TOKEN_OK ...`.

If this fails, generate a new Zoho grant code and exchange it for a new refresh token before testing CRM writes.

## PowerShell: Minimal Lead Upsert Test

Run only after `$accessToken` exists from the previous step. This verifies that the refresh token can write to the Leads module and that the minimum required fields are accepted.

```powershell
$stamp = Get-Date -Format "yyyyMMddHHmmss"
$leadKey = "manual:zillow:minimal:$stamp"

$minimalLead = @{
  Last_Name = "Tenant"
  Company = "1000 Example Avenue"
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
  "MINIMAL_UPSERT_FAILED"
  if ($_.Exception.Response) {
    "STATUS: $([int]$_.Exception.Response.StatusCode)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    "BODY:"
    $reader.ReadToEnd()
  } else {
    $_.Exception.Message
  }
}
```

Expected: Zoho returns success and creates one minimal diagnostic Lead.

If this fails, the problem is OAuth scope, duplicate field configuration, required Lead field setup, picklist setup, or the `Zillow_Lead_Key` field is not unique/available for API upsert.

## PowerShell: Units Routing Search Test

Run only after the token test succeeds. This checks the Units module and routing field.

```powershell
$unitsModule = "Units"
$criteriaRaw = "(Zillow_Routing_Unit_Key:equals:1000 example avenue|unit 3|sample city|ks|00000)"
$criteriaEncoded = [System.Uri]::EscapeDataString($criteriaRaw)
$unitSearchUrl = "https://www.zohoapis.com/crm/v8/$unitsModule/search?criteria=$criteriaEncoded&per_page=2"

try {
  $unitSearch = Invoke-RestMethod `
    -Method Get `
    -Uri $unitSearchUrl `
    -Headers @{ "Authorization" = "Zoho-oauthtoken $accessToken" }

  $unitSearch | ConvertTo-Json -Depth 10
} catch {
  "UNIT_SEARCH_FAILED"
  if ($_.Exception.Response) {
    "STATUS: $([int]$_.Exception.Response.StatusCode)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    "BODY:"
    $reader.ReadToEnd()
  } else {
    $_.Exception.Message
  }
}
```

Expected: the matching Unit record is returned, or Zoho returns a normal no-data response.

If this fails with invalid module, verify `ZOHO_CRM_UNITS_MODULE=Units` and the actual CRM module API name in Zoho CRM Developer Hub. If it fails with invalid field, verify `Zillow_Routing_Unit_Key` exists on the Units module and is API-accessible.

## PowerShell: Full Lead Upsert Test

Run only after the minimal test succeeds. This mirrors the Zillow test payload more closely.

```powershell
$stamp = Get-Date -Format "yyyyMMddHHmmss"
$leadKey = "manual:zillow:full:$stamp"
$nowIso = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss+00:00")

$fullLead = @{
  First_Name = "Live Test"
  Last_Name = "Tenant"
  Company = "1000 Example Avenue"
  Email = "full.live.test.$stamp@example.com"
  Mobile = "+19135550100"
  Lead_Source = "Zillow"
  Lead_Status = "New Zillow Inquiry"
  Requested_Move_In_Date = "2026-07-07"
  Inquiry_Message = "Message: Live upsert diagnostic only. Delete this CRM Lead."
  Zillow_Renter_Profile_Summary = "Bedrooms sought: 2`nBathrooms sought: 1"
  Zillow_Lead_Key = $leadKey
  Zillow_Listing_ID = "SYNTHETIC-ID-005"
  Zillow_Lead_Type = "tourRequest"
  Zillow_Provider_Model_ID = "0"
  Zillow_Property_Address_Raw = "1000 Example Avenue, Unit 3, Sample City, KS 00000"
  Zillow_Listing_Street = "1000 Example Avenue"
  Zillow_Listing_Unit = "Unit 3"
  Zillow_Listing_City = "Sample City"
  Zillow_Listing_State = "KS"
  Zillow_Listing_Postal_Code = "00000"
  Zillow_Source_Payload_Hash = "manual-full-test-$stamp"
  Zillow_Received_At = $nowIso
  Last_Zillow_Sync_At = $nowIso
  Zillow_Intake_Status = "Routing Unmatched"
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
  "FULL_UPSERT_FAILED"
  if ($_.Exception.Response) {
    "STATUS: $([int]$_.Exception.Response.StatusCode)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    "BODY:"
    $reader.ReadToEnd()
  } else {
    $_.Exception.Message
  }
}
```

Expected: Zoho returns success and creates one full diagnostic Lead.

If minimal succeeds but full fails, use the returned error body to identify the exact rejected field. The full test intentionally omits lookup fields so it isolates non-lookup Zillow fields first.

## Cleanup

Delete diagnostic Leads after testing:

```text
minimal.live.test.*@example.com
full.live.test.*@example.com
```

## Return To Normal Test State

After diagnostics, keep production in live test mode only until the Zillow callback is proven. Then either disable health or rotate the health token.
