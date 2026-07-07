'use strict';

/**
 * GH Real Estate - Zillow Rentals Lead Intake
 * Zoho Catalyst Advanced I/O, Node.js 18+
 *
 * Receives Zillow Rentals URL-encoded lead callbacks, authenticates the
 * configured static header, normalizes the official Zillow fields, and upserts
 * only a Zoho CRM Leads record. Contacts, Deals/Rental Applications, leases,
 * Books invoices, tenant portal records, and WorkDrive folders are intentionally
 * outside this intake boundary.
 */

const crypto = require('crypto');
const https = require('https');
const { URL, URLSearchParams } = require('url');

const SERVICE_NAME = 'gh-zillow-lead-intake';

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
    requestedProperty: 'Requested_Property',
    requestedUnit: 'Requested_Unit',
    requestedMoveInDate: 'Requested_Move_In_Date',
    inquiryMessage: 'Inquiry_Message',
    zillowLeadKey: 'Zillow_Lead_Key',
    zillowLeadId: 'Zillow_Lead_ID',
    zillowListingId: 'Zillow_Listing_ID',
    zillowListingUrl: 'Zillow_Listing_URL',
    zillowPropertyAddress: 'Zillow_Property_Address',
    zillowLeadType: 'Zillow_Lead_Type',
    zillowProviderModelId: 'Zillow_Provider_Model_ID',
    zillowSourcePayloadHash: 'Zillow_Source_Payload_Hash',
    zillowRawFieldKeys: 'Zillow_Raw_Field_Keys',
    zillowReceivedAt: 'Zillow_Received_At',
    lastZillowSyncAt: 'Last_Zillow_Sync_At',
    zillowIntakeStatus: 'Zillow_Intake_Status',
    description: 'Description'
  },
  intakeEvent: {
    name: 'Name',
    externalEventKey: 'External_Event_Key',
    leadReference: 'Lead_Reference',
    source: 'Source',
    receivedAt: 'Received_At',
    status: 'Status',
    crmLeadId: 'CRM_Lead_ID',
    rawFieldKeys: 'Raw_Field_Keys',
    sourcePayloadHash: 'Source_Payload_Hash',
    leadType: 'Lead_Type',
    listingId: 'Listing_ID'
  }
};

const CONFIG = buildConfig();
const tokenCache = { accessToken: '', expiresAtMs: 0 };

async function handler(req, res) {
  const requestId = makeRequestId();
  const receivedAtIso = new Date().toISOString();

  try {
    setSecurityHeaders(res);
    const method = String(req.method || '').toUpperCase();
    const path = getRequestPath(req);

    if (method === 'GET' && path === '/health') return handleHealth(req, res, requestId);
    if (method !== 'POST') return fail(res, requestId, 405, 'method_not_allowed');
    if (!CONFIG.allowedPaths.includes(path)) return fail(res, requestId, 404, 'path_not_allowed');

    if (CONFIG.enforceIpAllowlist) {
      const ip = getClientIp(req);
      if (!CONFIG.allowedIps.includes(ip)) return fail(res, requestId, 403, 'source_ip_not_allowed');
    }

    const encoding = String(getHeader(req.headers, 'content-encoding')).toLowerCase().trim();
    if (encoding && encoding !== 'identity') return fail(res, requestId, 415, 'unsupported_content_encoding');

    const declaredLength = getDeclaredContentLength(req);
    if (declaredLength !== null && declaredLength > CONFIG.maxBodyBytes) return fail(res, requestId, 413, 'payload_too_large');

    const secretCheck = validateInboundSecret(req);
    if (!secretCheck.ok) return fail(res, requestId, 401, 'inbound_secret_invalid');

    const contentType = String(getHeader(req.headers, 'content-type')).toLowerCase();
    if (!isAllowedContentType(contentType)) return fail(res, requestId, 415, 'unsupported_content_type');

    const rawBody = await readRequestBody(req, CONFIG.maxBodyBytes, CONFIG.inboundBodyTimeoutMs, contentType);
    const normalizedLead = normalizeZillowLeadPayload(parseInboundPayload(rawBody, contentType), {
      receivedAtIso,
      sourcePayloadHash: sha256(rawBody)
    });

    const validation = validateNormalizedLead(normalizedLead);
    if (!validation.ok) {
      return fail(res, requestId, 400, 'invalid_lead_payload', {
        errors: validation.publicErrors,
        lead_reference: normalizedLead.leadReference
      });
    }

    const propertyUnit = resolvePropertyUnit(normalizedLead, CONFIG.propertyUnitMap);
    const routingWarnings = buildRoutingWarnings(normalizedLead, propertyUnit);
    if (CONFIG.requireRouteMatchForSuccess && !propertyUnit) {
      return fail(res, requestId, 400, 'route_match_required', {
        errors: routingWarnings,
        lead_reference: normalizedLead.leadReference
      });
    }

    const plan = buildCrmLeadPlan(normalizedLead, propertyUnit, routingWarnings);
    if (CONFIG.dryRun) {
      logInfo({ requestId, event: 'zillow_lead_dry_run', leadReference: normalizedLead.leadReference, listingId: normalizedLead.listingId || undefined, leadType: normalizedLead.leadType || undefined, payloadHash: normalizedLead.sourcePayloadHash, routeMatched: Boolean(propertyUnit) });
      return sendJson(res, CONFIG.successStatusCode, {
        ok: true,
        mode: 'dry_run',
        request_id: requestId,
        lead_reference: normalizedLead.leadReference,
        route_matched: Boolean(propertyUnit),
        routing_warnings: routingWarnings,
        planned_actions: sanitizePlanForResponse(plan)
      });
    }

    assertLiveModeAllowed();
    const leadResult = await upsertCrmRecord({ moduleApiName: CONFIG.leadsModule, duplicateCheckFields: CONFIG.leadDuplicateCheckFields, record: plan.leadRecord });
    const crmLeadId = extractZohoRecordId(leadResult, 'lead');

    if (CONFIG.enableCrmIntakeEventLog) {
      await upsertCrmRecord({
        moduleApiName: CONFIG.intakeEventsModule,
        duplicateCheckFields: CONFIG.intakeEventDuplicateCheckFields,
        record: buildIntakeEventRecord(normalizedLead, { crmLeadId, status: 'Processed' })
      });
    }

    return sendJson(res, CONFIG.successStatusCode, {
      ok: true,
      mode: 'live',
      request_id: requestId,
      lead_reference: normalizedLead.leadReference,
      route_matched: Boolean(propertyUnit),
      routing_warnings: routingWarnings,
      lead: summarizeZohoResult(leadResult)
    });
  } catch (error) {
    console.error(JSON.stringify({ level: 'error', service: SERVICE_NAME, request_id: requestId, error: error.publicCode || 'internal_error', detail: CONFIG.debugErrors ? safeErrorMessage(error) : undefined, zoho_status: CONFIG.debugErrors ? error.zohoStatusCode : undefined }));
    return fail(res, requestId, Number(error.statusCode || error.status || 500), error.publicCode || 'internal_error');
  }
}

function buildConfig() {
  const fallbackHeader = env('INBOUND_SECRET_HEADER_NAME', 'x-gh-zillow-webhook-key').trim();
  const fallbackSecret = env('INBOUND_SECRET_VALUE', '').trim();
  return {
    version: env('GATEWAY_VERSION', '2026-07-07.v4'),
    allowedPaths: envList('ALLOWED_PATHS', ['/zillow/leads']),
    maxBodyBytes: envNumber('MAX_BODY_BYTES', 65536),
    inboundBodyTimeoutMs: envNumber('INBOUND_BODY_TIMEOUT_MS', 8000),
    successStatusCode: envNumber('SUCCESS_STATUS_CODE', 202),
    requireInboundSecret: envBool('REQUIRE_INBOUND_SECRET', true),
    inboundSecretHeaderName: env('ZILLOW_WEBHOOK_HEADER_NAME', fallbackHeader).toLowerCase().trim(),
    inboundSecretValue: env('ZILLOW_WEBHOOK_KEY', fallbackSecret).trim(),
    allowSecretQueryParam: envBool('ALLOW_SECRET_QUERY_PARAM', false),
    inboundSecretQueryParam: env('INBOUND_SECRET_QUERY_PARAM', 'key').trim(),
    enforceIpAllowlist: envBool('ENFORCE_IP_ALLOWLIST', false),
    allowedIps: envList('ALLOWED_IPS', []),
    requireUrlEncoded: envBool('REQUIRE_URLENCODED', true),
    allowJsonTestPayloads: envBool('ALLOW_JSON_TEST_PAYLOADS', false),
    enableHealth: envBool('ENABLE_HEALTH', true),
    healthHeaderName: env('HEALTH_HEADER_NAME', 'x-gh-health-token').toLowerCase().trim(),
    healthToken: env('HEALTH_CHECK_TOKEN', '').trim(),
    dryRun: envBool('ZILLOW_WEBHOOK_DRY_RUN', envBool('DRY_RUN', true)),
    liveModeEnabled: envBool('ZILLOW_WEBHOOK_LIVE_MODE_ENABLED', envBool('LIVE_MODE_ENABLED', false)),
    liveModeConfirmation: env('ZILLOW_WEBHOOK_LIVE_CONFIRMATION', env('LIVE_MODE_CONFIRMATION', '')).trim(),
    expectedLiveModeConfirmation: env('EXPECTED_LIVE_MODE_CONFIRMATION', 'GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED').trim(),
    accountsBaseUrl: env('ZOHO_ACCOUNTS_BASE_URL', 'https://accounts.zoho.com').trim(),
    crmBaseUrl: env('ZOHO_CRM_BASE_URL', 'https://www.zohoapis.com').trim(),
    crmApiVersion: env('ZOHO_CRM_API_VERSION', 'v8').trim(),
    accountsAllowedHostSuffixes: envList('ZOHO_ACCOUNTS_ALLOWED_HOST_SUFFIXES', ['accounts.zoho.com']),
    crmAllowedHostSuffixes: envList('ZOHO_CRM_ALLOWED_HOST_SUFFIXES', ['zohoapis.com']),
    outboundTimeoutMs: envNumber('OUTBOUND_TIMEOUT_MS', 15000),
    zohoClientId: env('ZOHO_CLIENT_ID', '').trim(),
    zohoClientSecret: env('ZOHO_CLIENT_SECRET', '').trim(),
    zohoRefreshToken: env('ZOHO_REFRESH_TOKEN', '').trim(),
    leadsModule: env('ZOHO_CRM_LEADS_MODULE', 'Leads').trim(),
    intakeEventsModule: env('ZOHO_CRM_INTAKE_EVENTS_MODULE', 'Zillow_Intake_Events').trim(),
    enableCrmIntakeEventLog: envBool('ENABLE_CRM_INTAKE_EVENT_LOG', false),
    leadDuplicateCheckFields: envList('LEAD_DUPLICATE_CHECK_FIELDS', ['Zillow_Lead_Key']),
    intakeEventDuplicateCheckFields: envList('INTAKE_EVENT_DUPLICATE_CHECK_FIELDS', ['External_Event_Key']),
    triggerWorkflows: envBool('CRM_TRIGGER_WORKFLOWS', false),
    triggerApprovals: envBool('CRM_TRIGGER_APPROVALS', false),
    triggerBlueprints: envBool('CRM_TRIGGER_BLUEPRINTS', false),
    skipCadencesOnInsert: envBool('SKIP_CADENCES_ON_INSERT', true),
    skipCadencesOnUpdate: envBool('SKIP_CADENCES_ON_UPDATE', false),
    defaultLeadSource: env('DEFAULT_LEAD_SOURCE', 'Zillow').trim(),
    defaultLeadStatus: env('DEFAULT_LEAD_STATUS', 'New Zillow Inquiry').trim(),
    defaultZillowIntakeStatus: env('DEFAULT_ZILLOW_INTAKE_STATUS', 'Received').trim(),
    zillowListingUrlTemplate: env('ZILLOW_LISTING_URL_TEMPLATE', '').trim(),
    requireRouteMatchForSuccess: envBool('REQUIRE_ROUTE_MATCH_FOR_SUCCESS', false),
    propertyUnitMap: envJson('PROPERTY_UNIT_MAP_JSON', {}),
    fieldMap: deepMerge(DEFAULT_FIELD_MAP, envJson('ZOHO_CRM_FIELD_MAP_JSON', {})),
    debugErrors: envBool('DEBUG_ERRORS', false)
  };
}

function handleHealth(req, res, requestId) {
  if (!CONFIG.enableHealth) return fail(res, requestId, 404, 'health_disabled');
  if (CONFIG.healthToken && !safeTimingEqualText(getHeader(req.headers, CONFIG.healthHeaderName), CONFIG.healthToken)) return fail(res, requestId, 404, 'not_found');
  return sendJson(res, 200, { ok: true, service: SERVICE_NAME, version: CONFIG.version, mode: CONFIG.dryRun ? 'dry_run' : 'live', endpoint_paths: CONFIG.allowedPaths, crm_target_module: CONFIG.leadsModule });
}

function validateInboundSecret(req) {
  if (!CONFIG.requireInboundSecret) return { ok: true };
  if (!CONFIG.inboundSecretValue) return { ok: false, reason: 'secret_not_configured' };
  if (safeTimingEqualText(getHeader(req.headers, CONFIG.inboundSecretHeaderName), CONFIG.inboundSecretValue)) return { ok: true };
  if (CONFIG.allowSecretQueryParam) {
    const queryValue = safeParseRequestUrl(req).searchParams.get(CONFIG.inboundSecretQueryParam);
    if (safeTimingEqualText(queryValue, CONFIG.inboundSecretValue)) return { ok: true };
  }
  return { ok: false, reason: 'secret_mismatch' };
}

function parseInboundPayload(rawBody, contentType) {
  const bodyText = rawBody.toString('utf8');
  if (contentType.includes('application/json')) return JSON.parse(bodyText || '{}');
  if (!contentType.includes('application/x-www-form-urlencoded') && contentType) throw publicError(415, 'unsupported_content_type');
  const out = {};
  for (const [key, value] of new URLSearchParams(bodyText).entries()) {
    out[key] = Object.prototype.hasOwnProperty.call(out, key) ? (Array.isArray(out[key]) ? [...out[key], value] : [out[key], value]) : value;
  }
  return out;
}

function normalizeZillowLeadPayload(payload, options = {}) {
  const receivedAtIso = options.receivedAtIso || new Date().toISOString();
  const input = normalizeInputObject(payload);
  const fullName = firstValue(input, ['name', 'full_name', 'contact_name', 'prospect_name', 'applicant_name', 'lead_name']);
  const parsedName = splitPersonName(fullName);
  const listingStreet = firstValue(input, ['listing_street', 'listingstreet', 'property_address', 'listing_address', 'address', 'street_address', 'property']);
  const listingUnit = firstValue(input, ['listing_unit', 'listingunit', 'unit', 'unit_number', 'apartment', 'apt', 'unit_name']);
  const listingCity = firstValue(input, ['listing_city', 'listingcity', 'city']);
  const listingState = firstValue(input, ['listing_state', 'listingstate', 'state']).toUpperCase();
  const listingPostalCode = firstValue(input, ['listing_postal_code', 'listingpostalcode', 'listing_zip', 'zip', 'postal_code']);
  const message = firstValue(input, ['message', 'comments', 'comment', 'lead_message', 'description', 'note']);
  const introduction = firstValue(input, ['introduction', 'intro', 'renter_profile_introduction']);
  const leadId = firstValue(input, ['lead_id', 'zillow_lead_id', 'zillowleadid', 'contact_id', 'id']);
  const listingId = firstValue(input, ['listing_id', 'zillow_listing_id', 'listingid', 'zpid', 'property_id', 'rental_id']);
  const providerModelId = firstValue(input, ['provider_model_id', 'providermodelid', 'model_id', 'modelid']);
  const leadType = normalizeLeadType(firstValue(input, ['lead_type', 'leadtype', 'type']));
  const email = normalizeEmail(firstValue(input, ['email', 'email_address', 'contact_email', 'applicant_email']));
  const phone = normalizePhone(firstValue(input, ['phone', 'phone_number', 'mobile', 'cell', 'contact_phone', 'applicant_phone']));
  const propertyAddress = composePropertyAddress({ listingStreet, listingUnit, listingCity, listingState, listingPostalCode });
  const leadKey = buildLeadKey({ leadId, email, phone, listingId, providerModelId, leadType, propertyAddress, listingUnit });

  return {
    leadKey,
    leadReference: publicLeadReference(leadKey),
    leadId,
    listingId,
    listingUrl: cleanUrl(firstValue(input, ['listing_url', 'url', 'property_url', 'zillow_url'])) || buildListingUrl(listingId),
    source: firstValue(input, ['source', 'lead_source', 'provider']) || 'Zillow',
    firstName: firstValue(input, ['first_name', 'firstname', 'first']) || parsedName.firstName,
    lastName: firstValue(input, ['last_name', 'lastname', 'last']) || parsedName.lastName,
    email,
    phone,
    leadType,
    providerModelId,
    message,
    introduction,
    inquiryMessage: [message, introduction ? `Introduction: ${introduction}` : ''].filter(Boolean).join('\n\n'),
    propertyAddress,
    listingStreet,
    listingUnit,
    listingCity,
    listingState,
    listingPostalCode,
    listingContactEmail: normalizeEmail(firstValue(input, ['listing_contact_email', 'listingcontactemail'])),
    movingDate: normalizeDate(firstValue(input, ['moving_date', 'movingdate', 'desired_move_in_date', 'move_in_date', 'moveindate', 'preferred_move_in_date'])),
    moveInTimeframe: normalizeEnum(firstValue(input, ['move_in_timeframe', 'moveintimeframe']), ['asap', 'flexible', 'week', 'month', 'twoWeeks', 'twoMonths']),
    receivedAtDate: normalizeDate(firstValue(input, ['received_at', 'created_at', 'submitted_at', 'timestamp', 'date'])) || isoDateOnly(receivedAtIso),
    receivedAtIso,
    numBedroomsSought: normalizeInteger(firstValue(input, ['num_bedrooms_sought', 'numbedroomssought', 'beds', 'bedrooms'])),
    numBathroomsSought: normalizeNumber(firstValue(input, ['num_bathrooms_sought', 'numbathroomssought', 'baths', 'bathrooms'])),
    neighborhoods: parseMaybeJsonList(firstValue(input, ['neighborhoods'])),
    propertyTypesDesired: parseMaybeJsonList(firstValue(input, ['property_types_desired', 'propertytypesdesired'])),
    leaseLengthMonths: normalizeInteger(firstValue(input, ['lease_length_months', 'leaselengthmonths'])),
    smoker: normalizeBooleanText(firstValue(input, ['smoker'])),
    parkingTypeDesired: normalizeEnum(firstValue(input, ['parking_type_desired', 'parkingtypedesired']), ['required', 'not needed', 'notNeeded']),
    incomeYearly: normalizeMoney(firstValue(input, ['income_yearly', 'incomeyearly'])),
    creditScoreRangeJson: normalizeJsonText(firstValue(input, ['credit_score_range_json', 'creditscorerangejson']), 'object'),
    movingFromCity: firstValue(input, ['moving_from_city', 'movingfromcity']),
    movingFromState: firstValue(input, ['moving_from_state', 'movingfromstate']).toUpperCase(),
    reasonForMoving: firstValue(input, ['reason_for_moving', 'reasonformoving']),
    employmentStatus: normalizeEnum(firstValue(input, ['employment_status', 'employmentstatus']), ['unemployed', 'student', 'retired', 'employed']),
    jobTitle: firstValue(input, ['job_title', 'jobtitle']),
    employer: firstValue(input, ['employer']),
    employmentStartDate: normalizeDate(firstValue(input, ['employment_start_date', 'employmentstartdate'])),
    employmentDetailsJson: normalizeJsonText(firstValue(input, ['employment_details_json', 'employmentdetailsjson']), 'list'),
    petDetailsJson: normalizeJsonText(firstValue(input, ['pet_details_json', 'petdetailsjson']), 'list'),
    rawFieldKeys: Object.keys(payload || {}).sort(),
    sourcePayloadHash: options.sourcePayloadHash || sha256(JSON.stringify(payload || {}))
  };
}

function validateNormalizedLead(lead) {
  const publicErrors = [];
  if (!lead.email && !lead.phone) publicErrors.push('Lead must include at least one contact method: email or phone.');
  if (lead.email && !isLikelyEmail(lead.email)) publicErrors.push('Lead email is not valid.');
  if (lead.phone && lead.phone.replace(/\D/g, '').length < 10) publicErrors.push('Lead phone is too short.');
  if (lead.listingContactEmail && !isLikelyEmail(lead.listingContactEmail)) publicErrors.push('Listing contact email is not valid.');
  return { ok: publicErrors.length === 0, publicErrors };
}

function resolvePropertyUnit(lead, propertyUnitMap) {
  const keys = [];
  if (lead.listingId) keys.push(`listing:${normalizeMapKey(lead.listingId)}`);
  if (lead.providerModelId) keys.push(`model:${normalizeMapKey(lead.providerModelId)}`);
  if (lead.listingContactEmail) keys.push(`contact-email:${normalizeMapKey(lead.listingContactEmail)}`);
  if (lead.propertyAddress || lead.listingUnit) keys.push(`address:${normalizeMapKey(lead.propertyAddress)}|${normalizeMapKey(lead.listingUnit)}`);
  if (lead.listingStreet || lead.listingUnit) keys.push(`address:${normalizeMapKey(lead.listingStreet)}|${normalizeMapKey(lead.listingUnit)}`);
  keys.push('default');
  for (const key of keys) if (propertyUnitMap && propertyUnitMap[key]) return { matchedKey: key, ...propertyUnitMap[key] };
  return null;
}

function buildRoutingWarnings(lead, propertyUnit) {
  const warnings = [];
  if (!lead.firstName || !lead.lastName) warnings.push('Missing full prospect name.');
  if (!lead.email) warnings.push('Missing prospect email.');
  if (!lead.phone) warnings.push('Missing prospect phone.');
  if (!lead.listingId && !lead.propertyAddress) warnings.push('Missing listing ID and property address.');
  if (!propertyUnit) warnings.push('No CRM property/unit mapping matched the Zillow lead.');
  if (!lead.movingDate) warnings.push('Move-in date was not provided.');
  return warnings;
}

function buildCrmLeadPlan(lead, propertyUnit, routingWarnings) {
  const f = CONFIG.fieldMap.lead;
  const summary = [
    'Imported from Zillow lead intake.',
    'Raw inquiry only. Convert to Contact and Rental Application after qualification.',
    `Lead reference: ${lead.leadReference}`,
    lead.leadType ? `Lead type: ${lead.leadType}` : '',
    lead.listingId ? `Listing ID: ${lead.listingId}` : '',
    lead.providerModelId ? `Provider model ID: ${lead.providerModelId}` : '',
    lead.propertyAddress ? `Listing address: ${lead.propertyAddress}` : '',
    lead.numBedroomsSought !== undefined ? `Bedrooms sought: ${lead.numBedroomsSought}` : '',
    lead.numBathroomsSought !== undefined ? `Bathrooms sought: ${lead.numBathroomsSought}` : '',
    lead.leaseLengthMonths ? `Lease length months: ${lead.leaseLengthMonths}` : '',
    lead.moveInTimeframe ? `Move-in timeframe: ${lead.moveInTimeframe}` : '',
    lead.incomeYearly !== undefined ? `Reported yearly income: ${lead.incomeYearly}` : '',
    lead.creditScoreRangeJson ? `Credit score range JSON: ${truncate(lead.creditScoreRangeJson, 400)}` : '',
    lead.employmentStatus ? `Employment status: ${lead.employmentStatus}` : '',
    lead.jobTitle ? `Job title: ${lead.jobTitle}` : '',
    lead.employer ? `Employer: ${lead.employer}` : '',
    lead.petDetailsJson ? `Pet details JSON: ${truncate(lead.petDetailsJson, 700)}` : '',
    lead.inquiryMessage ? `Message: ${truncate(lead.inquiryMessage, 1500)}` : '',
    routingWarnings.length ? `Routing warnings: ${routingWarnings.join(' ')}` : ''
  ].filter(Boolean).join('\n');

  const record = compactRecord({
    [f.firstName]: lead.firstName || undefined,
    [f.lastName]: lead.lastName || lead.firstName || 'Zillow Prospect',
    [f.company]: buildLeadCompany(lead, propertyUnit),
    [f.email]: lead.email || undefined,
    [f.phone]: lead.phone || undefined,
    [f.mobile]: lead.phone || undefined,
    [f.leadSource]: CONFIG.defaultLeadSource,
    [f.leadStatus]: CONFIG.defaultLeadStatus || undefined,
    [f.requestedProperty]: propertyUnit && propertyUnit.propertyId ? { id: String(propertyUnit.propertyId) } : undefined,
    [f.requestedUnit]: propertyUnit && propertyUnit.unitId ? { id: String(propertyUnit.unitId) } : undefined,
    [f.requestedMoveInDate]: lead.movingDate || undefined,
    [f.inquiryMessage]: lead.inquiryMessage || undefined,
    [f.zillowLeadKey]: lead.leadKey,
    [f.zillowLeadId]: lead.leadId || undefined,
    [f.zillowListingId]: lead.listingId || undefined,
    [f.zillowListingUrl]: lead.listingUrl || undefined,
    [f.zillowPropertyAddress]: lead.propertyAddress || undefined,
    [f.zillowLeadType]: lead.leadType || undefined,
    [f.zillowProviderModelId]: lead.providerModelId || undefined,
    [f.zillowSourcePayloadHash]: lead.sourcePayloadHash,
    [f.zillowRawFieldKeys]: lead.rawFieldKeys.join(', '),
    [f.zillowReceivedAt]: lead.receivedAtIso,
    [f.lastZillowSyncAt]: lead.receivedAtIso,
    [f.zillowIntakeStatus]: CONFIG.defaultZillowIntakeStatus,
    [f.description]: summary
  });
  return { leadRecord: record };
}

function buildLeadCompany(lead, propertyUnit) {
  if (propertyUnit && propertyUnit.propertyName) return propertyUnit.propertyName;
  if (lead.propertyAddress) return lead.propertyAddress;
  if (lead.listingId) return `Zillow Listing ${lead.listingId}`;
  return 'GH Real Estate Zillow Lead';
}

function buildIntakeEventRecord(lead, result) {
  const f = CONFIG.fieldMap.intakeEvent;
  return compactRecord({
    [f.name]: `Zillow Intake - ${lead.leadReference}`,
    [f.externalEventKey]: lead.leadKey,
    [f.leadReference]: lead.leadReference,
    [f.source]: lead.source || CONFIG.defaultLeadSource,
    [f.receivedAt]: lead.receivedAtIso,
    [f.status]: result.status || 'Processed',
    [f.crmLeadId]: result.crmLeadId,
    [f.rawFieldKeys]: lead.rawFieldKeys.join(', '),
    [f.sourcePayloadHash]: lead.sourcePayloadHash,
    [f.leadType]: lead.leadType || undefined,
    [f.listingId]: lead.listingId || undefined
  });
}

async function upsertCrmRecord({ moduleApiName, duplicateCheckFields, record }) {
  const accessToken = await getZohoAccessToken();
  const url = new URL(`${CONFIG.crmBaseUrl.replace(/\/$/, '')}/crm/${CONFIG.crmApiVersion}/${encodeURIComponent(moduleApiName)}/upsert`);
  assertAllowedOutboundUrl(url, CONFIG.crmAllowedHostSuffixes, 'crm_host_not_allowed');
  const body = { data: [record], duplicate_check_fields: duplicateCheckFields, trigger: buildZohoTriggers() };
  const skip = buildSkipFeatureExecution();
  if (skip.length) body.skip_feature_execution = skip;
  const response = await requestJson({ method: 'POST', url, accessToken, body });
  const first = response && Array.isArray(response.data) ? response.data[0] : null;
  if (!first || first.status !== 'success') {
    const err = publicError(502, 'zoho_upsert_failed');
    err.zoho = sanitizeZohoError(first || response);
    throw err;
  }
  return response;
}

async function getZohoAccessToken() {
  const now = Date.now();
  if (tokenCache.accessToken && tokenCache.expiresAtMs > now + 60000) return tokenCache.accessToken;
  if (!CONFIG.zohoClientId || !CONFIG.zohoClientSecret || !CONFIG.zohoRefreshToken) throw publicError(500, 'zoho_oauth_not_configured');
  const url = new URL(`${CONFIG.accountsBaseUrl.replace(/\/$/, '')}/oauth/v2/token`);
  assertAllowedOutboundUrl(url, CONFIG.accountsAllowedHostSuffixes, 'accounts_host_not_allowed');
  url.searchParams.set('refresh_token', CONFIG.zohoRefreshToken);
  url.searchParams.set('client_id', CONFIG.zohoClientId);
  url.searchParams.set('client_secret', CONFIG.zohoClientSecret);
  url.searchParams.set('grant_type', 'refresh_token');
  const response = await requestJson({ method: 'POST', url, headers: { accept: 'application/json' } });
  if (!response.access_token) throw publicError(502, 'zoho_oauth_failed');
  tokenCache.accessToken = response.access_token;
  tokenCache.expiresAtMs = now + Math.max(300, Number(response.expires_in || 3600) - 120) * 1000;
  return tokenCache.accessToken;
}

function requestJson({ method, url, headers = {}, accessToken = '', body = undefined }) {
  const finalHeaders = { ...headers };
  if (accessToken) finalHeaders.authorization = `Zoho-oauthtoken ${accessToken}`;
  if (body !== undefined) {
    finalHeaders['content-type'] = 'application/json';
    finalHeaders.accept = 'application/json';
  }
  return new Promise((resolve, reject) => {
    const req = https.request(url, { method, headers: finalHeaders, timeout: CONFIG.outboundTimeoutMs }, (res) => {
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        let parsed = {};
        const text = Buffer.concat(chunks).toString('utf8');
        if (text) {
          try { parsed = JSON.parse(text); } catch (_) { return reject(publicError(502, 'invalid_zoho_response')); }
        }
        if (res.statusCode < 200 || res.statusCode >= 300) {
          const err = publicError(502, 'zoho_request_failed');
          err.zohoStatusCode = res.statusCode;
          err.zoho = sanitizeZohoError(parsed);
          return reject(err);
        }
        resolve(parsed);
      });
    });
    req.on('timeout', () => req.destroy(publicError(504, 'zoho_request_timeout')));
    req.on('error', reject);
    if (body !== undefined) req.write(JSON.stringify(body));
    req.end();
  });
}

function buildZohoTriggers() {
  return [['workflow', CONFIG.triggerWorkflows], ['approval', CONFIG.triggerApprovals], ['blueprint', CONFIG.triggerBlueprints]].filter(([, enabled]) => enabled).map(([name]) => name);
}
function buildSkipFeatureExecution() {
  const skip = [];
  if (CONFIG.skipCadencesOnInsert) skip.push({ name: 'cadences', action: 'insert' });
  if (CONFIG.skipCadencesOnUpdate) skip.push({ name: 'cadences', action: 'update' });
  return skip;
}
function assertLiveModeAllowed() {
  if (!CONFIG.liveModeEnabled) throw publicError(500, 'live_mode_disabled');
  if (!safeTimingEqualText(CONFIG.liveModeConfirmation, CONFIG.expectedLiveModeConfirmation)) throw publicError(500, 'live_mode_confirmation_missing');
}

function buildLeadKey(parts) {
  if (parts.leadId) return `zillow:${parts.leadId}`;
  const contactIdentity = parts.email || parts.phone || 'unknown-contact';
  const addressIdentity = `${normalizeMapKey(parts.propertyAddress || '')}|${normalizeMapKey(parts.listingUnit || '')}`;
  const listingIdentity = parts.listingId || (addressIdentity !== '|' ? addressIdentity : 'unknown-listing');
  return `zillow:hash:${sha256([contactIdentity, listingIdentity, parts.providerModelId || '', parts.leadType || ''].join('|')).slice(0, 40)}`;
}
function publicLeadReference(leadKey) { return `zlw_${sha256(leadKey).slice(0, 16)}`; }
function sanitizePlanForResponse(plan) { return { lead_module: CONFIG.leadsModule, lead_fields: Object.keys(plan.leadRecord).sort(), duplicate_check_fields: { lead: CONFIG.leadDuplicateCheckFields } }; }
function summarizeZohoResult(result) {
  const first = result && Array.isArray(result.data) ? result.data[0] : null;
  return { status: first ? first.status : 'unknown', code: first ? first.code : undefined, action: first && first.action ? first.action : undefined, id: first && first.details ? first.details.id : undefined };
}
function extractZohoRecordId(result, label) {
  const first = result && Array.isArray(result.data) ? result.data[0] : null;
  const id = first && first.details ? first.details.id : '';
  if (!id) throw publicError(502, `missing_${label}_id`);
  return id;
}

function normalizeInputObject(input) {
  const out = {};
  for (const [key, value] of Object.entries(input || {})) out[normalizeFieldKey(key)] = Array.isArray(value) ? value.find((item) => cleanText(item)) : value;
  return out;
}
function firstValue(input, keys) {
  for (const key of keys) {
    const value = cleanText(input[normalizeFieldKey(key)]);
    if (value) return value;
  }
  return '';
}
function normalizeFieldKey(key) { return String(key || '').trim().replace(/([a-z])([A-Z])/g, '$1_$2').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '').toLowerCase(); }
function cleanText(value) { return value === null || value === undefined ? '' : String(value).replace(/\s+/g, ' ').trim(); }
function cleanUrl(value) { const text = cleanText(value); return /^https?:\/\//i.test(text) ? text : ''; }
function normalizeEmail(value) { return cleanText(value).toLowerCase(); }
function normalizePhone(value) { const text = cleanText(value); const digits = text.replace(/\D/g, ''); if (digits.length === 10) return `+1${digits}`; if (digits.length === 11 && digits.startsWith('1')) return `+${digits}`; return text; }
function normalizeDate(value) {
  const text = cleanText(value);
  if (!text) return '';
  const compact = text.match(/^(\d{4})(\d{2})(\d{2})$/);
  if (compact) return `${compact[1]}-${compact[2]}-${compact[3]}`;
  const iso = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (iso) return `${iso[1]}-${iso[2]}-${iso[3]}`;
  const us = text.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (us) return `${us[3]}-${String(us[1]).padStart(2, '0')}-${String(us[2]).padStart(2, '0')}`;
  const parsed = new Date(text);
  return Number.isNaN(parsed.getTime()) ? '' : isoDateOnly(parsed.toISOString());
}
function normalizeMoney(value) { const n = Number(cleanText(value).replace(/[$,]/g, '')); return Number.isFinite(n) ? n : undefined; }
function normalizeInteger(value) { const n = Number(cleanText(value).replace(/,/g, '')); return Number.isInteger(n) ? n : undefined; }
function normalizeNumber(value) { const n = Number(cleanText(value).replace(/,/g, '')); return Number.isFinite(n) ? n : undefined; }
function normalizeBooleanText(value) { const text = cleanText(value).toLowerCase(); if (!text) return ''; if (['true', 'yes', 'y', '1'].includes(text)) return 'true'; if (['false', 'no', 'n', '0'].includes(text)) return 'false'; return text; }
function normalizeEnum(value, allowed) { const text = cleanText(value); if (!text) return ''; return allowed.find((item) => item === text) || allowed.find((item) => String(item).toLowerCase() === text.toLowerCase()) || text; }
function normalizeLeadType(value) { return normalizeEnum(value, ['question', 'tourRequest', 'applicationRequest']); }
function normalizeJsonText(value, expected) {
  const text = cleanText(value);
  if (!text) return '';
  const parsed = parseMaybeJson(text);
  if (expected === 'list' && Array.isArray(parsed)) return stableJson(parsed);
  if (expected === 'object' && parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return stableJson(parsed);
  return text;
}
function parseMaybeJsonList(value) { const parsed = parseMaybeJson(value); if (Array.isArray(parsed)) return parsed.map((item) => typeof item === 'object' ? stableJson(item) : cleanText(item)).filter(Boolean); return cleanText(value).split(',').map(cleanText).filter(Boolean); }
function parseMaybeJson(value) { const text = cleanText(value); if (!/^[\[{]/.test(text)) return null; try { return JSON.parse(text); } catch (_) { return null; } }
function stableJson(value) { return value === null || value === undefined ? '' : JSON.stringify(value); }
function splitPersonName(fullName) { const parts = cleanText(fullName).split(' ').filter(Boolean); if (parts.length <= 1) return { firstName: '', lastName: parts[0] || '' }; return { firstName: parts.slice(0, -1).join(' '), lastName: parts[parts.length - 1] }; }
function composePropertyAddress({ listingStreet, listingUnit, listingCity, listingState, listingPostalCode }) { const street = [listingStreet, listingUnit].filter(Boolean).join(listingStreet && listingUnit ? ', ' : ''); const cityStateZip = [listingCity, [listingState, listingPostalCode].filter(Boolean).join(' ')].filter(Boolean).join(', '); return [street, cityStateZip].filter(Boolean).join(', '); }
function buildListingUrl(listingId) { return CONFIG.zillowListingUrlTemplate && listingId ? CONFIG.zillowListingUrlTemplate.replace('{listingId}', encodeURIComponent(listingId)) : ''; }
function normalizeMapKey(value) { return cleanText(value).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); }
function compactRecord(record) { const out = {}; for (const [key, value] of Object.entries(record)) if (key && value !== undefined && value !== null && value !== '') out[key] = value; return out; }
function deepMerge(base, override) { const out = { ...base }; for (const [key, value] of Object.entries(override || {})) out[key] = value && typeof value === 'object' && !Array.isArray(value) && base[key] ? deepMerge(base[key], value) : value; return out; }
function isoDateOnly(iso) { return String(iso || '').slice(0, 10); }
function isLikelyEmail(email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }
function isAllowedContentType(contentType) { return contentType.includes('application/x-www-form-urlencoded') || (!CONFIG.requireUrlEncoded && contentType === '') || (CONFIG.allowJsonTestPayloads && contentType.includes('application/json')); }

function readRequestBody(req, maxBytes, timeoutMs, contentType) {
  if (Buffer.isBuffer(req.rawBody)) return Promise.resolve(limitExistingBuffer(req.rawBody, maxBytes));
  if (typeof req.body === 'string') return Promise.resolve(limitExistingBuffer(Buffer.from(req.body, 'utf8'), maxBytes));
  if (req.body && typeof req.body === 'object' && typeof req.on !== 'function') {
    const serialized = contentType.includes('application/json') ? JSON.stringify(req.body) : new URLSearchParams(Object.entries(req.body).map(([k, v]) => [k, cleanText(v)])).toString();
    return Promise.resolve(limitExistingBuffer(Buffer.from(serialized, 'utf8'), maxBytes));
  }
  return new Promise((resolve, reject) => {
    const chunks = []; let total = 0; let done = false;
    const timer = setTimeout(() => { if (!done) { done = true; reject(publicError(408, 'request_body_timeout')); if (typeof req.destroy === 'function') req.destroy(); } }, timeoutMs);
    req.on('data', (chunk) => { if (done) return; total += chunk.length; if (total > maxBytes) { done = true; clearTimeout(timer); reject(publicError(413, 'payload_too_large')); if (typeof req.destroy === 'function') req.destroy(); return; } chunks.push(chunk); });
    req.on('end', () => { if (!done) { done = true; clearTimeout(timer); resolve(Buffer.concat(chunks)); } });
    req.on('error', (error) => { if (!done) { done = true; clearTimeout(timer); reject(error); } });
  });
}
function limitExistingBuffer(buffer, maxBytes) { if (buffer.length > maxBytes) throw publicError(413, 'payload_too_large'); return buffer; }
function getRequestPath(req) { return safeParseRequestUrl(req).pathname; }
function safeParseRequestUrl(req) { return new URL(req.url || '/', 'https://gh-real-estate.local'); }
function getDeclaredContentLength(req) { const n = Number(getHeader(req.headers, 'content-length')); return Number.isFinite(n) && n >= 0 ? n : null; }
function getHeader(headers, name) { const target = String(name || '').toLowerCase(); for (const [key, value] of Object.entries(headers || {})) if (String(key).toLowerCase() === target) return Array.isArray(value) ? value[0] : String(value || ''); return ''; }
function getClientIp(req) { return (getHeader(req.headers, 'x-forwarded-for').split(',')[0] || cleanText(req.socket && req.socket.remoteAddress)).trim(); }
function setSecurityHeaders(res) { if (res && typeof res.setHeader === 'function') { res.setHeader('content-type', 'application/json; charset=utf-8'); res.setHeader('x-content-type-options', 'nosniff'); res.setHeader('cache-control', 'no-store'); res.setHeader('referrer-policy', 'no-referrer'); } }
function sendJson(res, statusCode, body) { const payload = JSON.stringify(body); if (typeof res.writeHead === 'function') res.writeHead(statusCode); else res.statusCode = statusCode; return typeof res.end === 'function' ? res.end(payload) : payload; }
function fail(res, requestId, statusCode, code, extra = {}) { return sendJson(res, statusCode, { ok: false, request_id: requestId, error: code, ...extra }); }
function publicError(statusCode, publicCode) { const e = new Error(publicCode); e.statusCode = statusCode; e.publicCode = publicCode; return e; }
function safeErrorMessage(error) { return String(error && error.message ? error.message : error).slice(0, 500); }
function sanitizeZohoError(value) { if (!value || typeof value !== 'object') return value; return JSON.parse(JSON.stringify(value).replace(/1000\.[A-Za-z0-9._-]+/g, '[redacted-token]')); }
function assertAllowedOutboundUrl(url, suffixes, publicCode) { const host = String(url.hostname || '').toLowerCase(); if (!suffixes.some((s) => host === String(s).replace(/^\./, '').toLowerCase() || host.endsWith(`.${String(s).replace(/^\./, '').toLowerCase()}`))) throw publicError(500, publicCode); }
function sha256(value) { return crypto.createHash('sha256').update(value).digest('hex'); }
function safeTimingEqualText(a, b) { const left = Buffer.from(String(a || ''), 'utf8'); const right = Buffer.from(String(b || ''), 'utf8'); return left.length === right.length && crypto.timingSafeEqual(left, right); }
function makeRequestId() { return crypto.randomBytes(8).toString('hex'); }
function truncate(text, maxLength) { const value = cleanText(text); return value.length <= maxLength ? value : `${value.slice(0, Math.max(0, maxLength - 3))}...`; }
function logInfo(payload) { console.log(JSON.stringify({ level: 'info', service: SERVICE_NAME, ...payload })); }
function env(name, fallback = '') { return process.env[name] === undefined ? fallback : process.env[name]; }
function envBool(name, fallback = false) { return ['1', 'true', 'yes', 'y', 'on'].includes(env(name, String(fallback)).trim().toLowerCase()); }
function envNumber(name, fallback) { const n = Number(env(name, String(fallback))); return Number.isFinite(n) ? n : fallback; }
function envList(name, fallback = []) { const v = env(name, ''); return v.trim() ? v.split(',').map((x) => x.trim()).filter(Boolean) : fallback; }
function envJson(name, fallback = {}) { const v = env(name, '').trim(); if (!v) return fallback; try { return JSON.parse(v); } catch (_) { throw new Error(`${name} must be valid JSON`); } }

module.exports = handler;
module.exports._test = { DEFAULT_FIELD_MAP, normalizeZillowLeadPayload, validateNormalizedLead, resolvePropertyUnit, buildRoutingWarnings, buildCrmLeadPlan, buildLeadKey, parseInboundPayload, normalizePhone, normalizeDate, normalizeFieldKey, publicLeadReference, isAllowedContentType, assertLiveModeAllowed };
