'use strict';

const crypto = require('crypto');
const https = require('https');
const { URL, URLSearchParams } = require('url');
const { TextDecoder: UtilTextDecoder } = require('util');

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
    zillowRenterProfileSummary: 'Zillow_Renter_Profile_Summary',
    zillowLeadKey: 'Zillow_Lead_Key',
    zillowLeadId: 'Zillow_Lead_ID',
    zillowListingId: 'Zillow_Listing_ID',
    zillowListingUrl: 'Zillow_Listing_URL',
    zillowLeadType: 'Zillow_Lead_Type',
    zillowProviderModelId: 'Zillow_Provider_Model_ID',
    zillowMoveInTimeframe: 'Zillow_Move_In_Timeframe',
    zillowPropertyAddressRaw: 'Zillow_Property_Address_Raw',
    zillowListingStreet: 'Zillow_Listing_Street',
    zillowListingUnit: 'Zillow_Listing_Unit',
    zillowListingCity: 'Zillow_Listing_City',
    zillowListingState: 'Zillow_Listing_State',
    zillowListingPostalCode: 'Zillow_Listing_Postal_Code',
    zillowListingContactEmail: 'Zillow_Listing_Contact_Email',
    zillowReceivedAt: 'Zillow_Received_At',
    lastZillowSyncAt: 'Last_Zillow_Sync_At',
    zillowIntakeStatus: 'Zillow_Intake_Status',
    zillowSourcePayloadHash: 'Zillow_Source_Payload_Hash',
    zillowRawFieldKeys: 'Zillow_Raw_Field_Keys',
    zillowRawPayloadStored: 'Zillow_Raw_Payload_Stored',
    description: 'Description'
  },
  unit: {
    name: 'Name',
    unitId: 'Unit_I_D',
    unitNumber: 'Unit_Number',
    unitStatus: 'Unit_Status',
    zillowListingId: 'Zillow_Listing_ID',
    zillowProviderModelId: 'Zillow_Provider_Model_ID',
    zillowRoutingUnitKey: 'Zillow_Routing_Unit_Key',
    zillowListingContactPrefix: 'Zillow_Listing_Contact_Prefix',
    propertyLookup: ''
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
    payloadHash: 'Payload_Hash',
    routingWarnings: 'Routing_Warnings'
  }
};

const CACHE_KEY_MAX_LEN = 50;
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
    if (!validateAllowedPath(path).ok) return fail(res, requestId, 404, 'path_not_allowed');

    if (CONFIG.enforceIpAllowlist) {
      const clientIp = getClientIp(req);
      if (!CONFIG.allowedIps.includes(clientIp)) return fail(res, requestId, 403, 'source_ip_not_allowed');
    }

    const contentEncoding = String(getHeader(req.headers, 'content-encoding') || '').trim().toLowerCase();
    if (contentEncoding && contentEncoding !== 'identity') return fail(res, requestId, 415, 'unsupported_content_encoding');

    const declaredLength = getDeclaredContentLength(req);
    if (declaredLength !== null && declaredLength > CONFIG.maxBodyBytes) return fail(res, requestId, 413, 'payload_too_large');
    if (!validateInboundKey(req).ok) return fail(res, requestId, 401, 'inbound_header_invalid');

    const contentType = String(getHeader(req.headers, 'content-type') || '').toLowerCase();
    if (!isAllowedContentType(contentType)) return fail(res, requestId, 415, 'unsupported_content_type');

    const rawBody = await readRequestBody(req, CONFIG.maxBodyBytes, CONFIG.inboundBodyTimeoutMs);
    const rawBodyText = decodeUtf8Strict(rawBody);
    const sourcePayloadHash = sha256(rawBody);
    const sourcePayload = parseInboundPayload(Buffer.from(rawBodyText, 'utf8'), contentType);
    const normalizedLead = normalizeZillowLeadPayload(sourcePayload, receivedAtIso, sourcePayloadHash);
    const validation = validateNormalizedLead(normalizedLead);

    if (!validation.ok) {
      return fail(res, requestId, 400, 'invalid_lead_payload', {
        errors: validation.publicErrors,
        lead_reference: normalizedLead.leadReference
      });
    }

    const propertyUnit = await resolvePropertyUnit(normalizedLead, CONFIG.propertyUnitMap);
    const routingWarnings = buildRoutingWarnings(normalizedLead, propertyUnit);
    const plan = buildCrmLeadPlan(normalizedLead, propertyUnit, routingWarnings);

    if (CONFIG.enableCacheReplayDefense) {
      const replayKey = makeCacheKey('zlw:', normalizedLead.leadKey || sourcePayloadHash);
      const replayResult = await replaySeenAndMarkBestEffort(req, replayKey, CONFIG.replayWindowSeconds);
      if (replayResult.seen) {
        return sendJson(res, 202, {
          ok: true,
          mode: CONFIG.dryRun ? 'dry_run' : 'live',
          request_id: requestId,
          lead_reference: normalizedLead.leadReference,
          action: 'ignored',
          reason: 'recent_duplicate_cache_hit'
        });
      }
    }

    if (CONFIG.dryRun) {
      if (CONFIG.enableCrmIntakeEventLog && CONFIG.enableDryRunCrmAuditLog) {
        await upsertCrmRecord({
          moduleApiName: CONFIG.intakeEventsModule,
          duplicateCheckFields: CONFIG.intakeEventDuplicateCheckFields,
          record: buildIntakeEventRecord(normalizedLead, {
            crmLeadId: '',
            status: 'Dry Run Accepted',
            routingWarnings
          })
        });
      }

      return sendJson(res, 202, {
        ok: true,
        mode: 'dry_run',
        request_id: requestId,
        lead_reference: normalizedLead.leadReference,
        source_payload_hash: normalizedLead.sourcePayloadHash,
        routing_match: propertyUnit ? sanitizePropertyUnitForResponse(propertyUnit) : null,
        routing_warnings: routingWarnings,
        planned_actions: sanitizePlanForResponse(plan)
      });
    }

    assertLiveModeAllowed();
    const leadResult = await upsertCrmRecord({
      moduleApiName: CONFIG.leadsModule,
      duplicateCheckFields: CONFIG.leadDuplicateCheckFields,
      record: plan.leadRecord
    });
    const crmLeadId = extractZohoRecordId(leadResult, 'lead');

    if (CONFIG.enableCrmIntakeEventLog) {
      await upsertCrmRecord({
        moduleApiName: CONFIG.intakeEventsModule,
        duplicateCheckFields: CONFIG.intakeEventDuplicateCheckFields,
        record: buildIntakeEventRecord(normalizedLead, {
          crmLeadId,
          status: 'Processed',
          routingWarnings
        })
      });
    }

    return sendJson(res, 202, {
      ok: true,
      mode: 'live',
      request_id: requestId,
      lead_reference: normalizedLead.leadReference,
      source_payload_hash: normalizedLead.sourcePayloadHash,
      routing_match: propertyUnit ? sanitizePropertyUnitForResponse(propertyUnit) : null,
      lead: summarizeZohoResult(leadResult),
      routing_warnings: routingWarnings
    });
  } catch (error) {
    const status = Number(error.statusCode || error.status || 500);
    console.error(JSON.stringify({
      level: 'error',
      service: 'gh-zillow-lead-intake',
      request_id: requestId,
      status,
      error: error.publicCode || 'internal_error',
      detail: CONFIG.debugErrors ? safeErrorMessage(error) : undefined
    }));

    const publicCode = CONFIG.genericPublicErrors && status >= 500
      ? 'internal_error'
      : (error.publicCode || 'internal_error');
    return fail(res, requestId, status, publicCode);
  }
}

function buildConfig() {
  const fieldMapOverride = envJson('ZOHO_CRM_FIELD_MAP_JSON', {});
  const fieldMap = deepMerge(DEFAULT_FIELD_MAP, fieldMapOverride);
  return {
    version: env('GATEWAY_VERSION', '2026-07-07.v7'),
    allowedPaths: envList('ALLOWED_PATHS', ['/zillow/leads']),
    maxBodyBytes: envNumber('MAX_BODY_BYTES', 65536),
    inboundBodyTimeoutMs: envNumber('INBOUND_BODY_TIMEOUT_MS', 8000),
    requireInboundKey: envBool('REQUIRE_INBOUND_SECRET', true),
    inboundHeaderName: env('INBOUND_SECRET_HEADER_NAME', 'x-gh-zillow-webhook-key').toLowerCase().trim(),
    inboundHeaderValue: firstNonEmpty(env('ZILLOW_WEBHOOK_KEY', ''), env('INBOUND_SECRET_VALUE', '')).trim(),
    allowQueryKey: envBool('ALLOW_SECRET_QUERY_PARAM', false),
    queryKeyName: env('INBOUND_SECRET_QUERY_PARAM', 'key').trim(),
    enforceIpAllowlist: envBool('ENFORCE_IP_ALLOWLIST', false),
    allowedIps: envList('ALLOWED_IPS', []),
    enableHealth: envBool('ENABLE_HEALTH', false),
    healthHeaderName: env('HEALTH_HEADER_NAME', 'x-gh-health-token').toLowerCase().trim(),
    healthToken: env('HEALTH_CHECK_TOKEN', '').trim(),
    dryRun: envBoolAny(['ZILLOW_WEBHOOK_DRY_RUN', 'DRY_RUN'], true),
    liveModeEnabled: envBool('LIVE_MODE_ENABLED', false),
    liveModeConfirmation: env('LIVE_MODE_CONFIRMATION', '').trim(),
    expectedLiveModeConfirmation: env('EXPECTED_LIVE_MODE_CONFIRMATION', 'GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED').trim(),
    allowJsonPayloads: envBool('ALLOW_JSON_PAYLOADS', false),
    genericPublicErrors: envBool('GENERIC_PUBLIC_ERRORS', true),
    outboundTimeoutMs: envNumber('OUTBOUND_TIMEOUT_MS', 15000),
    enableCacheReplayDefense: envBool('ENABLE_CACHE_REPLAY_DEFENSE', false),
    strictReplayFailure: envBool('STRICT_REPLAY_FAILURE', false),
    replayCacheSegmentId: env('REPLAY_CACHE_SEGMENT_ID', ''),
    replayWindowSeconds: envNumber('REPLAY_WINDOW_SECONDS', 300),
    accountsBaseUrl: env('ZOHO_ACCOUNTS_BASE_URL', 'https://accounts.zoho.com').trim(),
    crmBaseUrl: env('ZOHO_CRM_BASE_URL', 'https://www.zohoapis.com').trim(),
    crmApiVersion: env('ZOHO_CRM_API_VERSION', 'v8').trim(),
    accountsAllowedHostSuffixes: envList('ACCOUNTS_ALLOWED_HOST_SUFFIXES', ['accounts.zoho.com']),
    crmAllowedHostSuffixes: envList('CRM_ALLOWED_HOST_SUFFIXES', ['zohoapis.com']),
    zohoClientId: env('ZOHO_CLIENT_ID', '').trim(),
    zohoClientSecret: env('ZOHO_CLIENT_SECRET', '').trim(),
    zohoRefreshToken: env('ZOHO_REFRESH_TOKEN', '').trim(),
    leadsModule: env('ZOHO_CRM_LEADS_MODULE', 'Leads').trim(),
    unitsModule: env('ZOHO_CRM_UNITS_MODULE', 'Units').trim() || 'Units',
    unitPropertyLookupField: env('UNIT_PROPERTY_LOOKUP_FIELD', '').trim(),
    enableDynamicUnitRouting: envBool('ENABLE_DYNAMIC_UNIT_ROUTING', true),
    dynamicUnitRoutingRequired: envBool('DYNAMIC_UNIT_ROUTING_REQUIRED', false),
    intakeEventsModule: env('ZOHO_CRM_INTAKE_EVENTS_MODULE', 'Zillow_Intake_Events').trim(),
    enableCrmIntakeEventLog: envBool('ENABLE_CRM_INTAKE_EVENT_LOG', false),
    enableDryRunCrmAuditLog: envBool('ENABLE_DRY_RUN_CRM_AUDIT_LOG', false),
    leadDuplicateCheckFields: envList('LEAD_DUPLICATE_CHECK_FIELDS', ['Zillow_Lead_Key']),
    intakeEventDuplicateCheckFields: envList('INTAKE_EVENT_DUPLICATE_CHECK_FIELDS', ['External_Event_Key']),
    triggerWorkflows: envBool('CRM_TRIGGER_WORKFLOWS', false),
    triggerApprovals: envBool('CRM_TRIGGER_APPROVALS', false),
    triggerBlueprints: envBool('CRM_TRIGGER_BLUEPRINTS', false),
    skipCadencesOnInsert: envBool('SKIP_CADENCES_ON_INSERT', true),
    skipCadencesOnUpdate: envBool('SKIP_CADENCES_ON_UPDATE', false),
    defaultLeadSource: env('DEFAULT_LEAD_SOURCE', 'Zillow').trim(),
    defaultLeadStatus: env('DEFAULT_LEAD_STATUS', 'New Zillow Inquiry').trim(),
    propertyUnitMap: envJson('PROPERTY_UNIT_MAP_JSON', {}),
    fieldMap,
    debugErrors: envBool('DEBUG_ERRORS', false)
  };
}

function handleHealth(req, res, requestId) {
  if (!CONFIG.enableHealth || !CONFIG.healthToken) return fail(res, requestId, 404, 'not_found');
  if (!safeTimingEqualText(getHeader(req.headers, CONFIG.healthHeaderName), CONFIG.healthToken)) return fail(res, requestId, 404, 'not_found');
  return sendJson(res, 200, {
    ok: true,
    service: 'gh-zillow-lead-intake',
    version: CONFIG.version,
    mode: CONFIG.dryRun ? 'dry_run' : 'live',
    crm_target_module: CONFIG.leadsModule
  });
}

function validateInboundKey(req) {
  if (!CONFIG.requireInboundKey) return { ok: true };
  if (!CONFIG.inboundHeaderValue) return { ok: false, reason: 'header_not_configured' };
  if (safeTimingEqualText(getHeader(req.headers, CONFIG.inboundHeaderName), CONFIG.inboundHeaderValue)) return { ok: true };
  if (CONFIG.allowQueryKey) {
    const queryValue = safeParseRequestUrl(req).searchParams.get(CONFIG.queryKeyName);
    if (safeTimingEqualText(queryValue, CONFIG.inboundHeaderValue)) return { ok: true };
  }
  return { ok: false, reason: 'header_mismatch' };
}

function parseInboundPayload(rawBody, contentType) {
  const bodyText = rawBody.toString('utf8');
  const normalizedContentType = String(contentType || '').toLowerCase();
  if (CONFIG.allowJsonPayloads && normalizedContentType.includes('application/json')) {
    try { return JSON.parse(bodyText || '{}'); }
    catch (_) { throw publicError(400, 'invalid_json_body'); }
  }
  if (normalizedContentType.includes('application/x-www-form-urlencoded') || !normalizedContentType) {
    const params = new URLSearchParams(bodyText);
    const output = {};
    for (const [key, value] of params.entries()) {
      output[key] = Object.prototype.hasOwnProperty.call(output, key)
        ? (Array.isArray(output[key]) ? [...output[key], value] : [output[key], value])
        : value;
    }
    return output;
  }
  throw publicError(415, 'unsupported_content_type');
}

function normalizeZillowLeadPayload(payload, receivedAtIso = new Date().toISOString(), sourcePayloadHash = '') {
  const input = normalizeInputObject(payload);
  const rawFieldKeys = Object.keys(payload || {}).sort();
  const fullName = firstValue(input, ['name', 'full_name', 'contact_name', 'prospect_name', 'applicant_name', 'lead_name']);
  const parsedName = splitPersonName(fullName);
  const firstName = firstValue(input, ['first_name', 'firstname', 'first']) || parsedName.firstName;
  const lastName = firstValue(input, ['last_name', 'lastname', 'last']) || parsedName.lastName;
  const email = normalizeEmail(firstValue(input, ['email', 'email_address', 'contact_email', 'applicant_email']));
  const phone = normalizePhone(firstValue(input, ['phone', 'phone_number', 'mobile', 'cell', 'contact_phone', 'applicant_phone']));
  const secondaryPhone = normalizePhone(firstValue(input, ['secondary_phone', 'secondaryphone', 'alternate_phone', 'alternatephone', 'other_phone', 'phone_2', 'phone2', 'home_phone', 'work_phone', 'secondary_mobile']));
  const leadId = cleanText(firstValue(input, ['lead_id', 'zillow_lead_id', 'zillowleadid', 'contact_id', 'id']));
  const listingId = cleanText(firstValue(input, ['listing_id', 'zillow_listing_id', 'listingid', 'zpid', 'property_id', 'rental_id']));
  const listingUrl = cleanUrl(firstValue(input, ['listing_url', 'url', 'property_url', 'zillow_url']));
  const leadType = normalizeEnum(firstValue(input, ['lead_type', 'leadtype']));
  const providerModelId = cleanText(firstValue(input, ['provider_model_id', 'provider_modelid', 'providermodelid']));
  const listingStreet = cleanText(firstValue(input, ['listing_street', 'listingstreet', 'street_address', 'property_address', 'listing_address', 'address', 'property']));
  const listingUnit = cleanText(firstValue(input, ['listing_unit', 'listingunit', 'unit', 'unit_number', 'apartment', 'apt', 'unit_name']));
  const listingCity = cleanText(firstValue(input, ['listing_city', 'listingcity', 'city', 'property_city']));
  const listingState = cleanText(firstValue(input, ['listing_state', 'listingstate', 'state', 'property_state'])).toUpperCase();
  const listingPostalCode = cleanText(firstValue(input, ['listing_postal_code', 'listingpostalcode', 'listing_zip', 'postal_code', 'zip', 'zipcode', 'property_zip']));
  const listingContactEmail = normalizeEmail(firstValue(input, ['listing_contact_email', 'listingcontactemail']));
  const listingContactPrefix = listingContactEmail ? listingContactEmail.split('@')[0] : '';
  const propertyAddress = composeListingAddress({ street: listingStreet, unit: listingUnit, city: listingCity, state: listingState, postalCode: listingPostalCode });
  const routingUnitKey = buildRoutingUnitKey({ listingStreet, listingUnit, listingCity, listingState, listingPostalCode });
  const desiredMoveInDate = normalizeDate(firstValue(input, ['moving_date', 'movingdate', 'desired_move_in_date', 'move_in_date', 'moveindate', 'preferred_move_in_date']));
  const message = cleanText(firstValue(input, ['message', 'comments', 'comment', 'lead_message', 'description', 'note']));
  const introduction = cleanText(firstValue(input, ['introduction', 'intro', 'renter_introduction']));
  const moveInTimeframe = normalizeEnum(firstValue(input, ['move_in_timeframe', 'moveintimeframe']));
  const profile = buildRenterProfile(input, moveInTimeframe);
  const leadKey = buildLeadKey({ leadId, email, phone: phone || secondaryPhone, listingId, propertyAddress, unit: listingUnit, leadType, message, introduction });

  return {
    leadKey,
    leadReference: publicLeadReference(leadKey),
    leadId,
    listingId,
    listingUrl,
    source: 'Zillow',
    firstName: cleanText(firstName),
    lastName: cleanText(lastName),
    fullName: cleanText(fullName),
    email,
    phone,
    secondaryPhone,
    message,
    introduction,
    inquiryMessage: buildInquiryMessage(message, introduction),
    propertyAddress,
    listingStreet,
    unit: listingUnit,
    listingCity,
    listingState,
    listingPostalCode,
    listingContactEmail,
    listingContactPrefix,
    routingUnitKey,
    desiredMoveInDate,
    receivedAtIso,
    sourcePayloadHash,
    leadType,
    providerModelId,
    moveInTimeframe,
    renterProfileSummary: buildRenterProfileSummary(profile),
    rawFieldKeys
  };
}

function buildRenterProfile(input, moveInTimeframe) {
  return {
    numBedroomsSought: cleanText(firstValue(input, ['num_bedrooms_sought', 'numbedroomssought', 'beds', 'bedrooms'])),
    numBathroomsSought: cleanText(firstValue(input, ['num_bathrooms_sought', 'numbathroomssought', 'baths', 'bathrooms'])),
    neighborhoods: cleanText(firstValue(input, ['neighborhoods'])),
    propertyTypesDesired: cleanText(firstValue(input, ['property_types_desired', 'propertytypesdesired'])),
    leaseLengthMonths: cleanText(firstValue(input, ['lease_length_months', 'leaselengthmonths'])),
    smoker: normalizeBooleanText(firstValue(input, ['smoker'])),
    parkingTypeDesired: normalizeEnum(firstValue(input, ['parking_type_desired', 'parkingtypedesired'])),
    incomeYearly: normalizeMoney(firstValue(input, ['income_yearly', 'incomeyearly'])),
    creditScoreRangeJson: cleanText(firstValue(input, ['credit_score_range_json', 'creditscorerangejson'])),
    movingFromCity: cleanText(firstValue(input, ['moving_from_city', 'movingfromcity'])),
    movingFromState: cleanText(firstValue(input, ['moving_from_state', 'movingfromstate'])).toUpperCase(),
    moveInTimeframe,
    reasonForMoving: cleanText(firstValue(input, ['reason_for_moving', 'reasonformoving'])),
    employmentStatus: normalizeEnum(firstValue(input, ['employment_status', 'employmentstatus'])),
    jobTitle: cleanText(firstValue(input, ['job_title', 'jobtitle'])),
    employer: cleanText(firstValue(input, ['employer'])),
    employmentStartDate: normalizeDate(firstValue(input, ['employment_start_date', 'employmentstartdate'])),
    employmentDetailsJson: cleanText(firstValue(input, ['employment_details_json', 'employmentdetailsjson'])),
    petDetailsJson: cleanText(firstValue(input, ['pet_details_json', 'petdetailsjson']))
  };
}

function validateNormalizedLead(lead) {
  const publicErrors = [];
  if (!lead.email && !lead.phone && !lead.secondaryPhone) publicErrors.push('Lead must include at least one contact method: email or phone.');
  if (lead.email && !isLikelyEmail(lead.email)) publicErrors.push('Lead email is not valid.');
  if (lead.phone && lead.phone.replace(/\D/g, '').length < 10) publicErrors.push('Lead phone is too short.');
  if (lead.secondaryPhone && lead.secondaryPhone.replace(/\D/g, '').length < 10) publicErrors.push('Lead secondary phone is too short.');
  return { ok: publicErrors.length === 0, publicErrors };
}

async function resolvePropertyUnit(lead, propertyUnitMap) {
  const staticMatch = resolvePropertyUnitFromMap(lead, propertyUnitMap);
  if (staticMatch) return staticMatch;

  if (!CONFIG.enableDynamicUnitRouting) return null;

  try {
    return await resolvePropertyUnitFromCrmUnits(lead);
  } catch (error) {
    if (CONFIG.dynamicUnitRoutingRequired) throw error;
    console.error(JSON.stringify({
      level: 'warn',
      service: 'gh-zillow-lead-intake',
      warning: 'dynamic_unit_routing_failed',
      detail: safeErrorMessage(error)
    }));
    return null;
  }
}

function resolvePropertyUnitFromMap(lead, propertyUnitMap) {
  const keys = buildRoutingCandidateKeys(lead);
  for (const key of uniqueNonEmpty([...keys, 'default'])) {
    if (propertyUnitMap && propertyUnitMap[key]) return { matchedKey: key, matchedBy: 'runtime_map', ...propertyUnitMap[key] };
  }
  return null;
}

async function resolvePropertyUnitFromCrmUnits(lead) {
  const unitFieldMap = CONFIG.fieldMap.unit;
  const criteriaCandidates = buildUnitSearchCriteriaCandidates(lead, unitFieldMap);
  for (const candidate of criteriaCandidates) {
    const records = await searchCrmRecords({ moduleApiName: CONFIG.unitsModule, criteria: candidate.criteria, perPage: 2 });
    if (records.length > 0) return buildPropertyUnitFromCrmUnitRecord(records[0], candidate);
  }
  return null;
}

function buildUnitSearchCriteriaCandidates(lead, unitFieldMap) {
  const candidates = [];
  if (lead.listingId && unitFieldMap.zillowListingId) {
    candidates.push({ matchedBy: 'unit_zillow_listing_id', matchedKey: `listing:${normalizeMapKey(lead.listingId)}`, criteria: crmEquals(unitFieldMap.zillowListingId, lead.listingId) });
  }
  if (lead.providerModelId && lead.providerModelId !== '0' && unitFieldMap.zillowProviderModelId) {
    candidates.push({ matchedBy: 'unit_zillow_provider_model_id', matchedKey: `provider_model:${normalizeMapKey(lead.providerModelId)}`, criteria: crmEquals(unitFieldMap.zillowProviderModelId, lead.providerModelId) });
  }
  if (lead.listingContactPrefix && unitFieldMap.zillowListingContactPrefix) {
    candidates.push({ matchedBy: 'unit_zillow_listing_contact_prefix', matchedKey: `listing_contact_prefix:${normalizeMapKey(lead.listingContactPrefix)}`, criteria: crmEquals(unitFieldMap.zillowListingContactPrefix, lead.listingContactPrefix) });
  }
  if (lead.routingUnitKey && unitFieldMap.zillowRoutingUnitKey) {
    candidates.push({ matchedBy: 'unit_zillow_routing_unit_key', matchedKey: `routing_unit_key:${lead.routingUnitKey}`, criteria: crmEquals(unitFieldMap.zillowRoutingUnitKey, lead.routingUnitKey) });
  }
  return candidates;
}

function buildPropertyUnitFromCrmUnitRecord(unitRecord, candidate) {
  const unitFieldMap = CONFIG.fieldMap.unit;
  const property = extractLookup(unitRecord, CONFIG.unitPropertyLookupField, ['Property', 'Property_Name', 'Related_Property', 'Parent_Property', 'Account_Name']);
  return {
    matchedKey: candidate.matchedKey,
    matchedBy: candidate.matchedBy,
    unitId: String(unitRecord.id || ''),
    unitName: cleanText(unitRecord[unitFieldMap.name]) || cleanText(unitRecord.Name),
    propertyId: property.id || undefined,
    propertyName: property.name || undefined
  };
}

function extractLookup(record, preferredField, fallbackFields) {
  const candidates = uniqueNonEmpty([preferredField, ...fallbackFields]);
  for (const field of candidates) {
    const value = record[field];
    if (value && typeof value === 'object') {
      return { id: value.id ? String(value.id) : '', name: cleanText(value.name || value.Name) };
    }
    if (typeof value === 'string' && value) return { id: '', name: value };
  }
  return { id: '', name: '' };
}

function buildRoutingCandidateKeys(lead) {
  const keys = [];
  if (lead.listingId) keys.push(`listing:${normalizeMapKey(lead.listingId)}`);
  if (lead.providerModelId && lead.providerModelId !== '0') keys.push(`provider_model:${normalizeMapKey(lead.providerModelId)}`);
  if (lead.listingContactEmail) keys.push(`listing_contact_email:${normalizeMapKey(lead.listingContactEmail)}`);
  if (lead.listingContactPrefix) keys.push(`listing_contact_prefix:${normalizeMapKey(lead.listingContactPrefix)}`);
  if (lead.routingUnitKey) keys.push(`routing_unit_key:${lead.routingUnitKey}`);
  if (lead.listingStreet || lead.unit || lead.listingCity || lead.listingState || lead.listingPostalCode) {
    keys.push(`address:${buildRoutingUnitKey({ listingStreet: lead.listingStreet, listingUnit: lead.unit, listingCity: lead.listingCity, listingState: lead.listingState, listingPostalCode: lead.listingPostalCode })}`);
  }
  return keys;
}

function buildRoutingWarnings(lead, propertyUnit) {
  const warnings = [];
  if (!lead.firstName || !lead.lastName) warnings.push('Missing full prospect name.');
  if (!lead.email) warnings.push('Missing prospect email.');
  if (!lead.phone && !lead.secondaryPhone) warnings.push('Missing prospect phone.');
  if (!lead.listingId) warnings.push('Missing Zillow listingId.');
  if (!lead.propertyAddress) warnings.push('Missing Zillow listing address.');
  if (!propertyUnit) warnings.push('No CRM Unit routing match found for this Zillow lead.');
  if (propertyUnit && !propertyUnit.propertyId) warnings.push('CRM Unit matched, but no Property lookup was available for Requested Property.');
  if (!lead.desiredMoveInDate && !lead.moveInTimeframe) warnings.push('No move-in date or timeframe was provided.');
  return warnings;
}

function buildCrmLeadPlan(lead, propertyUnit, routingWarnings) {
  const fieldMap = CONFIG.fieldMap.lead;
  const lastName = lead.lastName || lead.firstName || 'Zillow Prospect';
  const company = buildLeadCompany(lead, propertyUnit);
  const intakeStatus = propertyUnit ? 'Routing Matched' : 'Routing Unmatched';

  const leadRecord = compactRecord({
    [fieldMap.firstName]: lead.firstName || undefined,
    [fieldMap.lastName]: lastName,
    [fieldMap.company]: company,
    [fieldMap.email]: lead.email || undefined,
    [fieldMap.phone]: lead.secondaryPhone || undefined,
    [fieldMap.mobile]: lead.phone || undefined,
    [fieldMap.leadSource]: CONFIG.defaultLeadSource,
    [fieldMap.leadStatus]: CONFIG.defaultLeadStatus || undefined,
    [fieldMap.property]: propertyUnit && propertyUnit.propertyId ? { id: String(propertyUnit.propertyId) } : undefined,
    [fieldMap.unit]: propertyUnit && propertyUnit.unitId ? { id: String(propertyUnit.unitId) } : undefined,
    [fieldMap.requestedMoveInDate]: lead.desiredMoveInDate || undefined,
    [fieldMap.inquiryMessage]: lead.inquiryMessage || undefined,
    [fieldMap.zillowRenterProfileSummary]: lead.renterProfileSummary || undefined,
    [fieldMap.zillowLeadKey]: lead.leadKey,
    [fieldMap.zillowLeadId]: lead.leadId || undefined,
    [fieldMap.zillowListingId]: lead.listingId || undefined,
    [fieldMap.zillowListingUrl]: lead.listingUrl || undefined,
    [fieldMap.zillowLeadType]: lead.leadType || undefined,
    [fieldMap.zillowProviderModelId]: lead.providerModelId || undefined,
    [fieldMap.zillowMoveInTimeframe]: lead.moveInTimeframe || undefined,
    [fieldMap.zillowPropertyAddressRaw]: lead.propertyAddress || undefined,
    [fieldMap.zillowListingStreet]: lead.listingStreet || undefined,
    [fieldMap.zillowListingUnit]: lead.unit || undefined,
    [fieldMap.zillowListingCity]: lead.listingCity || undefined,
    [fieldMap.zillowListingState]: lead.listingState || undefined,
    [fieldMap.zillowListingPostalCode]: lead.listingPostalCode || undefined,
    [fieldMap.zillowListingContactEmail]: lead.listingContactEmail || undefined,
    [fieldMap.zillowSourcePayloadHash]: lead.sourcePayloadHash || undefined,
    [fieldMap.zillowReceivedAt]: lead.receivedAtIso,
    [fieldMap.lastZillowSyncAt]: lead.receivedAtIso,
    [fieldMap.zillowIntakeStatus]: intakeStatus,
    [fieldMap.zillowRawFieldKeys]: lead.rawFieldKeys.join(', '),
    [fieldMap.zillowRawPayloadStored]: false,
    [fieldMap.description]: buildLeadDescription(lead, propertyUnit, routingWarnings)
  });
  return { leadRecord };
}

function buildLeadCompany(lead, propertyUnit) {
  if (propertyUnit && propertyUnit.propertyName) return propertyUnit.propertyName;
  if (lead.propertyAddress) return lead.propertyAddress;
  if (lead.listingId) return `Zillow Listing ${lead.listingId}`;
  return 'GH Real Estate Zillow Lead';
}

function buildLeadDescription(lead, propertyUnit, routingWarnings) {
  return [
    'Imported from Zillow Rentals Lead Delivery API.',
    'Raw inquiry only. Do not convert to Contact, Rental Application, lease, Books invoice, tenant portal access, or WorkDrive folder until qualification and approval.',
    `Lead reference: ${lead.leadReference}`,
    lead.leadType ? `Lead type: ${lead.leadType}` : '',
    lead.listingId ? `Listing ID: ${lead.listingId}` : '',
    lead.providerModelId ? `Provider model ID: ${lead.providerModelId}` : '',
    lead.routingUnitKey ? `Routing unit key: ${lead.routingUnitKey}` : '',
    lead.listingContactPrefix ? `Listing contact prefix: ${lead.listingContactPrefix}` : '',
    lead.propertyAddress ? `Zillow listing address: ${lead.propertyAddress}` : '',
    propertyUnit && propertyUnit.matchedKey ? `Matched CRM route: ${propertyUnit.matchedKey}` : '',
    propertyUnit && propertyUnit.matchedBy ? `Matched by: ${propertyUnit.matchedBy}` : '',
    lead.desiredMoveInDate ? `Requested move-in date: ${lead.desiredMoveInDate}` : '',
    lead.moveInTimeframe ? `Move-in timeframe: ${lead.moveInTimeframe}` : '',
    lead.inquiryMessage ? `Inquiry message: ${truncate(lead.inquiryMessage, 1500)}` : '',
    lead.renterProfileSummary ? `Renter profile summary:\n${truncate(lead.renterProfileSummary, 2500)}` : '',
    routingWarnings && routingWarnings.length ? `Routing warnings: ${routingWarnings.join(' ')}` : '',
    lead.sourcePayloadHash ? `Source payload hash: ${lead.sourcePayloadHash}` : ''
  ].filter(Boolean).join('\n');
}

function buildIntakeEventRecord(lead, result) {
  const fieldMap = CONFIG.fieldMap.intakeEvent;
  return compactRecord({
    [fieldMap.name]: `Zillow Intake - ${lead.leadReference}`,
    [fieldMap.externalEventKey]: lead.leadKey,
    [fieldMap.leadReference]: lead.leadReference,
    [fieldMap.source]: lead.source || CONFIG.defaultLeadSource,
    [fieldMap.receivedAt]: lead.receivedAtIso,
    [fieldMap.status]: result.status || 'Processed',
    [fieldMap.crmLeadId]: result.crmLeadId || undefined,
    [fieldMap.rawFieldKeys]: lead.rawFieldKeys.join(', '),
    [fieldMap.payloadHash]: lead.sourcePayloadHash || undefined,
    [fieldMap.routingWarnings]: (result.routingWarnings || []).join('\n') || undefined
  });
}

async function upsertCrmRecord({ moduleApiName, duplicateCheckFields, record }) {
  const accessToken = await getZohoAccessToken();
  const url = new URL(`${CONFIG.crmBaseUrl.replace(/\/$/, '')}/crm/${CONFIG.crmApiVersion}/${encodeURIComponent(moduleApiName)}/upsert`);
  assertAllowedHost(url, CONFIG.crmAllowedHostSuffixes, 'crm_host_not_allowed');
  const body = { data: [record], duplicate_check_fields: duplicateCheckFields, trigger: buildZohoTriggers() };
  const skipFeatureExecution = buildSkipFeatureExecution();
  if (skipFeatureExecution.length > 0) body.skip_feature_execution = skipFeatureExecution;
  const response = await zohoRequest({ method: 'POST', url, accessToken, body });
  const first = response && Array.isArray(response.data) ? response.data[0] : null;
  if (!first || first.status !== 'success') {
    const err = publicError(502, 'zoho_upsert_failed');
    err.zoho = sanitizeZohoError(first || response);
    throw err;
  }
  return response;
}

async function searchCrmRecords({ moduleApiName, criteria, perPage = 2 }) {
  const accessToken = await getZohoAccessToken();
  const url = new URL(`${CONFIG.crmBaseUrl.replace(/\/$/, '')}/crm/${CONFIG.crmApiVersion}/${encodeURIComponent(moduleApiName)}/search`);
  assertAllowedHost(url, CONFIG.crmAllowedHostSuffixes, 'crm_host_not_allowed');
  url.searchParams.set('criteria', criteria);
  url.searchParams.set('per_page', String(perPage));
  const response = await zohoRequest({ method: 'GET', url, accessToken });
  return Array.isArray(response.data) ? response.data : [];
}

async function getZohoAccessToken() {
  const now = Date.now();
  if (tokenCache.accessToken && tokenCache.expiresAtMs > now + 60000) return tokenCache.accessToken;
  if (!CONFIG.zohoClientId || !CONFIG.zohoClientSecret || !CONFIG.zohoRefreshToken) throw publicError(500, 'zoho_oauth_not_configured');
  const url = new URL(`${CONFIG.accountsBaseUrl.replace(/\/$/, '')}/oauth/v2/token`);
  assertAllowedHost(url, CONFIG.accountsAllowedHostSuffixes, 'accounts_host_not_allowed');
  url.searchParams.set('refresh_token', CONFIG.zohoRefreshToken);
  url.searchParams.set('client_id', CONFIG.zohoClientId);
  url.searchParams.set('client_secret', CONFIG.zohoClientSecret);
  url.searchParams.set('grant_type', 'refresh_token');
  const response = await requestJson({ method: 'POST', url, headers: { accept: 'application/json' }, timeoutMs: CONFIG.outboundTimeoutMs });
  if (!response.access_token) throw publicError(502, 'zoho_oauth_failed');
  const expiresInSeconds = Number(response.expires_in || 3600);
  tokenCache.accessToken = response.access_token;
  tokenCache.expiresAtMs = now + Math.max(300, expiresInSeconds - 120) * 1000;
  return tokenCache.accessToken;
}

async function zohoRequest({ method, url, accessToken, body }) {
  assertAllowedHost(url, CONFIG.crmAllowedHostSuffixes, 'crm_host_not_allowed');
  return requestJson({
    method,
    url,
    headers: { authorization: `Zoho-oauthtoken ${accessToken}`, 'content-type': 'application/json', accept: 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
    timeoutMs: CONFIG.outboundTimeoutMs
  });
}

function requestJson({ method, url, headers = {}, body, timeoutMs = 15000 }) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, { method, headers, timeout: timeoutMs }, (res) => {
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const text = Buffer.concat(chunks).toString('utf8');
        let parsed = {};
        if (text) {
          try { parsed = JSON.parse(text); }
          catch (_) { return reject(publicError(502, 'invalid_zoho_response')); }
        }
        if (res.statusCode < 200 || res.statusCode >= 300) {
          const err = publicError(502, 'zoho_request_failed');
          err.statusCode = 502;
          err.zohoStatusCode = res.statusCode;
          err.zoho = sanitizeZohoError(parsed);
          return reject(err);
        }
        resolve(parsed);
      });
    });
    req.on('timeout', () => req.destroy(publicError(504, 'zoho_request_timeout')));
    req.on('error', reject);
    if (body !== undefined) req.write(body);
    req.end();
  });
}

function crmEquals(fieldApiName, value) {
  return `(${fieldApiName}:equals:${escapeCrmCriteriaValue(value)})`;
}

function escapeCrmCriteriaValue(value) {
  return cleanText(value).replace(/\\/g, '\\\\').replace(/,/g, '\\,').replace(/\)/g, '\\)').replace(/\(/g, '\\(');
}

function buildZohoTriggers() {
  const triggers = [];
  if (CONFIG.triggerWorkflows) triggers.push('workflow');
  if (CONFIG.triggerApprovals) triggers.push('approval');
  if (CONFIG.triggerBlueprints) triggers.push('blueprint');
  return triggers;
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
  return `zillow:hash:${sha256([normalizeEmail(parts.email || ''), normalizePhone(parts.phone || ''), cleanText(parts.listingId || ''), normalizeMapKey(parts.propertyAddress || ''), normalizeMapKey(parts.unit || ''), normalizeMapKey(parts.leadType || ''), normalizeMapKey(parts.message || ''), normalizeMapKey(parts.introduction || '')].join('|')).slice(0, 40)}`;
}

function publicLeadReference(leadKey) { return `zlw_${sha256(leadKey).slice(0, 16)}`; }
function sanitizePlanForResponse(plan) { return { lead_module: CONFIG.leadsModule, lead_fields: Object.keys(plan.leadRecord).sort(), duplicate_check_fields: { lead: CONFIG.leadDuplicateCheckFields } }; }
function sanitizePropertyUnitForResponse(propertyUnit) { return { matched_key: propertyUnit.matchedKey, matched_by: propertyUnit.matchedBy, property_id_present: Boolean(propertyUnit.propertyId), unit_id_present: Boolean(propertyUnit.unitId), property_name: propertyUnit.propertyName, unit_name: propertyUnit.unitName }; }
function summarizeZohoResult(result) { const first = result && Array.isArray(result.data) ? result.data[0] : null; return { status: first ? first.status : 'unknown', code: first ? first.code : undefined, action: first && first.action ? first.action : undefined, id: first && first.details ? first.details.id : undefined }; }
function extractZohoRecordId(result, label) { const first = result && Array.isArray(result.data) ? result.data[0] : null; const id = first && first.details ? first.details.id : ''; if (!id) throw publicError(502, `missing_${label}_id`); return id; }
function normalizeInputObject(input) { const output = {}; for (const [key, value] of Object.entries(input || {})) output[normalizeFieldKey(key)] = Array.isArray(value) ? value.find((item) => cleanText(item)) : value; return output; }
function firstValue(input, keys) { for (const key of keys) { const value = cleanText(input[normalizeFieldKey(key)]); if (value) return value; } return ''; }
function firstNonEmpty(...values) { for (const value of values) { const cleaned = cleanText(value); if (cleaned) return cleaned; } return ''; }
function normalizeFieldKey(key) { return String(key || '').trim().replace(/([a-z])([A-Z])/g, '$1_$2').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '').toLowerCase(); }
function cleanText(value) { return value === null || value === undefined ? '' : String(value).replace(/\s+/g, ' ').trim(); }
function cleanUrl(value) { const text = cleanText(value); return /^https?:\/\//i.test(text) ? text : ''; }
function normalizeEmail(value) { return cleanText(value).toLowerCase(); }
function normalizePhone(value) { const text = cleanText(value); if (!text) return ''; const digits = text.replace(/\D/g, ''); if (digits.length === 10) return `+1${digits}`; if (digits.length === 11 && digits.startsWith('1')) return `+${digits}`; return text; }
function normalizeDate(value) { const text = cleanText(value); if (!text) return ''; const yyyymmdd = text.match(/^(\d{4})(\d{2})(\d{2})$/); if (yyyymmdd) return `${yyyymmdd[1]}-${yyyymmdd[2]}-${yyyymmdd[3]}`; const isoMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})/); if (isoMatch) return `${isoMatch[1]}-${isoMatch[2]}-${isoMatch[3]}`; const usMatch = text.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/); if (usMatch) return `${usMatch[3]}-${String(usMatch[1]).padStart(2, '0')}-${String(usMatch[2]).padStart(2, '0')}`; const parsed = new Date(text); return Number.isNaN(parsed.getTime()) ? '' : isoDateOnly(parsed.toISOString()); }
function normalizeMoney(value) { const text = cleanText(value); if (!text) return undefined; const number = Number(text.replace(/[$,]/g, '')); return Number.isFinite(number) ? number : undefined; }
function normalizeEnum(value) { return cleanText(value); }
function normalizeBooleanText(value) { const text = cleanText(value).toLowerCase(); if (!text) return ''; if (['true', '1', 'yes', 'y'].includes(text)) return 'true'; if (['false', '0', 'no', 'n'].includes(text)) return 'false'; return cleanText(value); }
function splitPersonName(fullName) { const text = cleanText(fullName); if (!text) return { firstName: '', lastName: '' }; const parts = text.split(' ').filter(Boolean); if (parts.length === 1) return { firstName: '', lastName: parts[0] }; return { firstName: parts.slice(0, -1).join(' '), lastName: parts[parts.length - 1] }; }
function composeListingAddress({ street, unit, city, state, postalCode }) { const line1 = [cleanText(street), cleanText(unit)].filter(Boolean).join(', '); const line2 = [cleanText(city), [cleanText(state), cleanText(postalCode)].filter(Boolean).join(' ')].filter(Boolean).join(', '); return [line1, line2].filter(Boolean).join(', '); }
function buildRoutingUnitKey({ listingStreet, listingUnit, listingCity, listingState, listingPostalCode }) { return [listingStreet, listingUnit, listingCity, listingState, listingPostalCode].map(normalizeMapKey).join('|'); }
function buildInquiryMessage(message, introduction) { return [introduction ? `Introduction: ${introduction}` : '', message ? `Message: ${message}` : ''].filter(Boolean).join('\n\n'); }
function buildRenterProfileSummary(profile) { return [['Bedrooms sought', profile.numBedroomsSought], ['Bathrooms sought', profile.numBathroomsSought], ['Neighborhoods', formatPossiblyJson(profile.neighborhoods)], ['Property types desired', formatPossiblyJson(profile.propertyTypesDesired)], ['Lease length months', profile.leaseLengthMonths], ['Smoker', profile.smoker], ['Parking desired', profile.parkingTypeDesired], ['Income yearly', profile.incomeYearly === undefined ? '' : String(profile.incomeYearly)], ['Credit score range', formatPossiblyJson(profile.creditScoreRangeJson)], ['Moving from city', profile.movingFromCity], ['Moving from state', profile.movingFromState], ['Move-in timeframe', profile.moveInTimeframe], ['Reason for moving', profile.reasonForMoving], ['Employment status', profile.employmentStatus], ['Job title', profile.jobTitle], ['Employer', profile.employer], ['Employment start date', profile.employmentStartDate], ['Employment details', formatPossiblyJson(profile.employmentDetailsJson)], ['Pet details', formatPossiblyJson(profile.petDetailsJson)]].filter(([, value]) => cleanText(value)).map(([label, value]) => `${label}: ${truncate(value, 700)}`).join('\n'); }
function formatPossiblyJson(value) { const text = cleanText(value); if (!text) return ''; try { return JSON.stringify(JSON.parse(text)); } catch (_) { return text; } }
function normalizeMapKey(value) { return cleanText(value).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); }
function compactRecord(record) { const output = {}; for (const [key, value] of Object.entries(record)) { if (!key) continue; if (value === undefined || value === null || value === '') continue; output[key] = value; } return output; }
function deepMerge(base, override) { const output = { ...base }; for (const [key, value] of Object.entries(override || {})) output[key] = value && typeof value === 'object' && !Array.isArray(value) && base[key] ? deepMerge(base[key], value) : value; return output; }
function uniqueNonEmpty(values) { return [...new Set(values.filter(Boolean))]; }
function isoDateOnly(iso) { return String(iso || '').slice(0, 10); }
function isLikelyEmail(email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }
function isAllowedContentType(contentType) { const value = String(contentType || '').toLowerCase(); if (value.includes('application/x-www-form-urlencoded')) return true; if (CONFIG.allowJsonPayloads && value.includes('application/json')) return true; return value === ''; }
function readRequestBody(req, maxBytes, timeoutMs) { if (Buffer.isBuffer(req.rawBody)) return req.rawBody.length > maxBytes ? Promise.reject(publicError(413, 'payload_too_large')) : Promise.resolve(req.rawBody); if (typeof req.body === 'string') { const buf = Buffer.from(req.body, 'utf8'); return buf.length > maxBytes ? Promise.reject(publicError(413, 'payload_too_large')) : Promise.resolve(buf); } if (Buffer.isBuffer(req.body)) return req.body.length > maxBytes ? Promise.reject(publicError(413, 'payload_too_large')) : Promise.resolve(req.body); if (req.body && typeof req.body === 'object' && typeof req.on !== 'function') return Promise.resolve(Buffer.from(new URLSearchParams(req.body).toString(), 'utf8')); return new Promise((resolve, reject) => { const chunks = []; let total = 0; let done = false; const timer = setTimeout(() => { if (done) return; done = true; reject(publicError(408, 'request_body_timeout')); if (typeof req.destroy === 'function') req.destroy(); }, Math.max(1000, Number(timeoutMs || 8000))); req.on('data', (chunk) => { if (done) return; total += chunk.length; if (total > maxBytes) { done = true; clearTimeout(timer); reject(publicError(413, 'payload_too_large')); if (typeof req.destroy === 'function') req.destroy(); return; } chunks.push(chunk); }); req.on('end', () => { if (done) return; done = true; clearTimeout(timer); resolve(Buffer.concat(chunks)); }); req.on('error', (err) => { if (done) return; done = true; clearTimeout(timer); reject(err); }); }); }
function decodeUtf8Strict(rawBody) { try { return new UtilTextDecoder('utf-8', { fatal: true }).decode(rawBody); } catch (_) { throw publicError(400, 'invalid_utf8_body'); } }
function getRequestPath(req) { try { return normalizePath(safeParseRequestUrl(req).pathname); } catch (_) { return '/'; } }
function safeParseRequestUrl(req) { return new URL(req.url || '/', 'https://gh-real-estate.local'); }
function normalizePath(path) { let p = String(path || '').trim(); if (!p) p = '/'; if (!p.startsWith('/')) p = `/${p}`; if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1); return p; }
function validateAllowedPath(path) { const normalized = normalizePath(path); const allowed = CONFIG.allowedPaths.map(normalizePath); const rootAliasAllowed = normalized === '/' && allowed.length === 1 && allowed[0] !== '/'; return { ok: allowed.includes(normalized) || rootAliasAllowed }; }
function getDeclaredContentLength(req) { const raw = getHeader(req.headers, 'content-length'); if (!raw) return null; const parsed = Number(raw); return Number.isFinite(parsed) ? parsed : null; }
function getHeader(headers, name) { const target = String(name || '').toLowerCase(); for (const [key, value] of Object.entries(headers || {})) if (String(key).toLowerCase() === target) return Array.isArray(value) ? value[0] : String(value || ''); return ''; }
function getClientIp(req) { const forwarded = getHeader(req.headers, 'x-forwarded-for'); if (forwarded) return forwarded.split(',')[0].trim(); return cleanText(req.ip || req.socket?.remoteAddress || req.connection?.remoteAddress || ''); }
function setSecurityHeaders(res) { if (!res || typeof res.setHeader !== 'function') return; res.setHeader('content-type', 'application/json; charset=utf-8'); res.setHeader('x-content-type-options', 'nosniff'); res.setHeader('cache-control', 'no-store'); }
function sendJson(res, statusCode, body) { const payload = JSON.stringify(body); if (typeof res.writeHead === 'function') res.writeHead(statusCode); else res.statusCode = statusCode; if (typeof res.end === 'function') return res.end(payload); return payload; }
function fail(res, requestId, statusCode, code, extra = {}) { return sendJson(res, statusCode, { ok: false, request_id: requestId, error: code, ...extra }); }
function publicError(statusCode, publicCode) { const error = new Error(publicCode); error.statusCode = statusCode; error.publicCode = publicCode; return error; }
function safeErrorMessage(error) { return String(error && error.message ? error.message : error).slice(0, 500); }
function sanitizeZohoError(value) { if (!value || typeof value !== 'object') return value; const text = JSON.stringify(value); return JSON.parse(text.replace(/1000\.[A-Za-z0-9._-]+/g, '[redacted-token]')); }
function sha256(value) { return crypto.createHash('sha256').update(value).digest('hex'); }
function safeTimingEqualText(a, b) { const left = Buffer.from(String(a || ''), 'utf8'); const right = Buffer.from(String(b || ''), 'utf8'); if (left.length !== right.length) return false; return crypto.timingSafeEqual(left, right); }
function makeRequestId() { return crypto.randomBytes(8).toString('hex'); }
function truncate(text, maxLength) { const value = cleanText(text); return value.length <= maxLength ? value : `${value.slice(0, Math.max(0, maxLength - 3))}...`; }
function env(name, fallback = '') { return process.env[name] === undefined ? fallback : process.env[name]; }
function envBool(name, fallback = false) { return ['1', 'true', 'yes', 'y', 'on'].includes(env(name, String(fallback)).trim().toLowerCase()); }
function envBoolAny(names, fallback = false) { for (const name of names) if (process.env[name] !== undefined) return envBool(name, fallback); return fallback; }
function envNumber(name, fallback) { const value = Number(env(name, String(fallback))); return Number.isFinite(value) ? value : fallback; }
function envList(name, fallback = []) { const value = env(name, ''); return value.trim() ? value.split(',').map((item) => item.trim()).filter(Boolean) : fallback; }
function envJson(name, fallback = {}) { const value = env(name, '').trim(); if (!value) return fallback; try { return JSON.parse(value); } catch (_) { throw new Error(`${name} must be valid JSON`); } }
function assertAllowedHost(url, allowedSuffixes, code) { const host = String(url.hostname || '').toLowerCase(); const allowed = (allowedSuffixes || []).map((item) => String(item).toLowerCase()); if (!allowed.some((suffix) => host === suffix || host.endsWith(`.${suffix}`))) throw publicError(500, code); }
async function replaySeenAndMarkBestEffort(req, key, ttlSeconds) { try { const catalyst = req.catalyst || global.catalyst; if (!catalyst || typeof catalyst.cache !== 'function') return { seen: false, skipped: true }; const segment = catalyst.cache().segment(CONFIG.replayCacheSegmentId || 'default'); const existing = await segment.get(key); if (existing && existing.cache_value) return { seen: true }; await segment.put(key, '1', Number(ttlSeconds || 300)); return { seen: false }; } catch (_) { if (CONFIG.strictReplayFailure) throw publicError(503, 'replay_cache_failed'); return { seen: false, skipped: true }; } }
function makeCacheKey(prefix, value) { return `${prefix}${sha256(String(value || '')).slice(0, CACHE_KEY_MAX_LEN - prefix.length)}`; }

module.exports = handler;
module.exports._test = { DEFAULT_FIELD_MAP, buildConfig, normalizeZillowLeadPayload, validateNormalizedLead, resolvePropertyUnit, resolvePropertyUnitFromMap, buildRoutingCandidateKeys, buildRoutingUnitKey, buildRoutingWarnings, buildCrmLeadPlan, buildLeadKey, buildInquiryMessage, buildRenterProfileSummary, parseInboundPayload, normalizePhone, normalizeDate, normalizeFieldKey, isAllowedContentType, publicLeadReference };
