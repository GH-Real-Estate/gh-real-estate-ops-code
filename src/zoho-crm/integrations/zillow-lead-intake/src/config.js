'use strict';

const DEFAULT_FIELD_MAP = {
  lead: {
    firstName: 'First_Name',
    lastName: 'Last_Name',
    company: 'Company',
    email: 'Email',
    phone: 'Phone',
    mobile: 'Mobile',
    leadSource: 'Lead_Source',
    leadStatus: 'Lead_Status',
    property: 'Requested_Property',
    unit: 'Requested_Unit',
    requestedMoveInDate: 'Requested_Move_In_Date',
    inquiryMessage: 'Inquiry_Message',
    zillowLeadKey: 'Zillow_Lead_Key',
    zillowLeadId: 'Zillow_Lead_ID',
    zillowListingId: 'Zillow_Listing_ID',
    zillowListingUrl: 'Zillow_Listing_URL',
    zillowPropertyAddress: 'Zillow_Property_Address',
    zillowSourcePayloadHash: 'Zillow_Source_Payload_Hash',
    zillowReceivedAt: 'Zillow_Received_At',
    lastZillowSyncAt: 'Last_Zillow_Sync_At',
    zillowIntakeStatus: 'Zillow_Intake_Status',
    zillowRawPayloadStored: 'Zillow_Raw_Payload',
    description: 'Description'
  }
};

function env(name, fallback = '') {
  return process.env[name] === undefined ? fallback : process.env[name];
}

function envBool(name, fallback = false) {
  return ['1', 'true', 'yes', 'y', 'on'].includes(env(name, String(fallback)).trim().toLowerCase());
}

function envNumber(name, fallback) {
  const value = Number(env(name, String(fallback)));
  return Number.isFinite(value) ? value : fallback;
}

function envList(name, fallback = []) {
  const value = env(name, '');
  return value.trim() ? value.split(',').map((item) => item.trim()).filter(Boolean) : fallback;
}

function envJson(name, fallback = {}) {
  const value = env(name, '').trim();
  if (!value) return fallback;
  try {
    return JSON.parse(value);
  } catch {
    throw new Error(`${name} must be valid JSON`);
  }
}

function deepMerge(base, override) {
  const output = { ...base };
  for (const [key, value] of Object.entries(override || {})) {
    output[key] = value && typeof value === 'object' && !Array.isArray(value) && base[key]
      ? deepMerge(base[key], value)
      : value;
  }
  return output;
}

function buildConfig() {
  return {
    version: env('GATEWAY_VERSION', '2026-07-07.v3'),
    allowedPaths: envList('ALLOWED_PATHS', ['/zillow/leads']),
    maxBodyBytes: envNumber('MAX_BODY_BYTES', 65536),
    requireInboundSecret: envBool('REQUIRE_INBOUND_SECRET', true),
    inboundSecretHeaderName: env('INBOUND_SECRET_HEADER_NAME', 'x-gh-zillow-webhook-key').toLowerCase().trim(),
    inboundSecretValue: env('INBOUND_SECRET_VALUE', '').trim(),
    allowSecretQueryParam: envBool('ALLOW_SECRET_QUERY_PARAM', false),
    inboundSecretQueryParam: env('INBOUND_SECRET_QUERY_PARAM', 'key').trim(),
    enableHealth: envBool('ENABLE_HEALTH', true),
    healthHeaderName: env('HEALTH_HEADER_NAME', 'x-gh-health-token').toLowerCase().trim(),
    healthToken: env('HEALTH_CHECK_TOKEN', '').trim(),
    dryRun: envBool('DRY_RUN', true),
    liveModeEnabled: envBool('LIVE_MODE_ENABLED', false),
    liveModeConfirmation: env('LIVE_MODE_CONFIRMATION', '').trim(),
    expectedLiveModeConfirmation: env('EXPECTED_LIVE_MODE_CONFIRMATION', 'GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED').trim(),
    accountsBaseUrl: env('ZOHO_ACCOUNTS_BASE_URL', 'https://accounts.zoho.com').trim(),
    crmBaseUrl: env('ZOHO_CRM_BASE_URL', 'https://www.zohoapis.com').trim(),
    crmApiVersion: env('ZOHO_CRM_API_VERSION', 'v8').trim(),
    zohoClientId: env('ZOHO_CLIENT_ID', '').trim(),
    zohoClientSecret: env('ZOHO_CLIENT_SECRET', '').trim(),
    zohoRefreshToken: env('ZOHO_REFRESH_TOKEN', '').trim(),
    leadsModule: env('ZOHO_CRM_LEADS_MODULE', 'Leads').trim(),
    leadDuplicateCheckFields: envList('LEAD_DUPLICATE_CHECK_FIELDS', ['Zillow_Lead_Key']),
    defaultLeadSource: env('DEFAULT_LEAD_SOURCE', 'Zillow').trim(),
    defaultLeadStatus: env('DEFAULT_LEAD_STATUS', 'Not Contacted').trim(),
    defaultIntakeStatus: env('DEFAULT_ZILLOW_INTAKE_STATUS', 'Received').trim(),
    propertyUnitMap: envJson('PROPERTY_UNIT_MAP_JSON', {}),
    fieldMap: deepMerge(DEFAULT_FIELD_MAP, envJson('ZOHO_CRM_FIELD_MAP_JSON', {})),
    debugErrors: envBool('DEBUG_ERRORS', false)
  };
}

module.exports = { DEFAULT_FIELD_MAP, buildConfig, envBool };
