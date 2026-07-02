'use strict';

/**
 * GH Real Estate - Zillow Lead Intake
 * Platform: Zoho Catalyst Advanced I/O, Node.js 18+
 *
 * Purpose:
 * - Receive Zillow Rental Network lead callbacks.
 * - Accept Zillow's URL-encoded payload format.
 * - Validate minimum usable lead data before CRM mutation.
 * - Build a stable external key so repeated callbacks update instead of duplicate.
 * - Upsert Contact and Rental Application records in Zoho CRM.
 *
 * Important integration assumption:
 * Zillow's public lead API docs state that lead callbacks are URL-encoded and that
 * Zillow cannot customize the API fields/form. This service therefore normalizes
 * multiple likely field aliases and stores received field names for manual review
 * without logging or persisting raw sensitive payloads.
 */

const crypto = require('crypto');
const https = require('https');
const { URL, URLSearchParams } = require('url');

const DEFAULT_FIELD_MAP = {
  contact: {
    firstName: 'First_Name',
    lastName: 'Last_Name',
    email: 'Email',
    phone: 'Phone',
    mobile: 'Mobile',
    leadSource: 'Lead_Source',
    contactType: 'Contact_Type',
    relatedProperty: 'Related_Property',
    relatedUnit: 'Related_Unit',
    portalAccessStatus: 'Portal_Access_Status',
    description: 'Description'
  },
  application: {
    name: 'Deal_Name',
    stage: 'Stage',
    pipeline: 'Pipeline',
    closingDate: 'Closing_Date',
    amount: 'Amount',
    applicantContact: 'Contact_Name',
    property: 'Property',
    unit: 'Unit',
    zillowLeadKey: 'Zillow_Lead_Key',
    zillowLeadId: 'Zillow_Lead_ID',
    zillowListingId: 'Zillow_Listing_ID',
    zillowListingUrl: 'Zillow_Listing_URL',
    zillowMessage: 'Zillow_Message',
    zillowSource: 'Zillow_Source',
    zillowRawFieldKeys: 'Zillow_Raw_Field_Keys',
    applicationReceivedDate: 'Application_Received_Date',
    desiredMoveInDate: 'Desired_Move_In_Date',
    screeningStatus: 'Screening_Status',
    ownerDecision: 'Owner_Decision',
    approvedRent: 'Approved_Rent',
    approvedDeposit: 'Approved_Deposit',
    workDriveFolderUrl: 'WorkDrive_Folder_URL',
    manualReviewRequired: 'Manual_Review_Required',
    manualReviewReason: 'Manual_Review_Reason',
    notes: 'Description'
  },
  intakeEvent: {
    name: 'Name',
    externalEventKey: 'External_Event_Key',
    leadReference: 'Lead_Reference',
    source: 'Source',
    receivedAt: 'Received_At',
    status: 'Status',
    contactId: 'CRM_Contact_ID',
    applicationId: 'CRM_Application_ID',
    rawFieldKeys: 'Raw_Field_Keys',
    manualReviewRequired: 'Manual_Review_Required',
    manualReviewReason: 'Manual_Review_Reason'
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

    if (method === 'GET' && path === '/health') {
      return handleHealth(req, res);
    }

    if (method !== 'POST') {
      return fail(res, requestId, 405, 'method_not_allowed');
    }

    if (!CONFIG.allowedPaths.includes(path)) {
      return fail(res, requestId, 404, 'path_not_allowed');
    }

    const contentEncoding = String(getHeader(req.headers, 'content-encoding') || '').trim().toLowerCase();
    if (contentEncoding && contentEncoding !== 'identity') {
      return fail(res, requestId, 415, 'unsupported_content_encoding');
    }

    const declaredLength = getDeclaredContentLength(req);
    if (declaredLength !== null && declaredLength > CONFIG.maxBodyBytes) {
      return fail(res, requestId, 413, 'payload_too_large');
    }

    const secretCheck = validateInboundSecret(req);
    if (!secretCheck.ok) {
      return fail(res, requestId, 401, 'inbound_secret_invalid');
    }

    const contentType = String(getHeader(req.headers, 'content-type') || '').toLowerCase();
    if (!isAllowedContentType(contentType)) {
      return fail(res, requestId, 415, 'unsupported_content_type');
    }

    const rawBody = await readRequestBody(req, CONFIG.maxBodyBytes);
    const sourcePayload = parseInboundPayload(rawBody, contentType);
    const normalizedLead = normalizeZillowLeadPayload(sourcePayload, receivedAtIso);
    const validation = validateNormalizedLead(normalizedLead);

    if (!validation.ok) {
      return fail(res, requestId, 422, 'invalid_lead_payload', {
        errors: validation.publicErrors,
        lead_reference: normalizedLead.leadReference
      });
    }

    const propertyUnit = resolvePropertyUnit(normalizedLead, CONFIG.propertyUnitMap);
    const manualReviewReasons = buildManualReviewReasons(normalizedLead, propertyUnit);
    const plan = buildCrmPlan(normalizedLead, propertyUnit, manualReviewReasons);

    if (CONFIG.dryRun) {
      return sendJson(res, 200, {
        ok: true,
        mode: 'dry_run',
        request_id: requestId,
        lead_reference: normalizedLead.leadReference,
        manual_review_required: manualReviewReasons.length > 0,
        manual_review_reasons: manualReviewReasons,
        planned_actions: sanitizePlanForResponse(plan)
      });
    }

    assertLiveModeAllowed();

    const contactResult = await upsertCrmRecord({
      moduleApiName: CONFIG.contactsModule,
      duplicateCheckFields: CONFIG.contactDuplicateCheckFields,
      record: plan.contactRecord
    });
    const contactId = extractZohoRecordId(contactResult, 'contact');

    const applicationRecord = {
      ...plan.applicationRecord,
      [CONFIG.fieldMap.application.applicantContact]: { id: contactId }
    };

    const applicationResult = await upsertCrmRecord({
      moduleApiName: CONFIG.applicationsModule,
      duplicateCheckFields: CONFIG.applicationDuplicateCheckFields,
      record: applicationRecord
    });
    const applicationId = extractZohoRecordId(applicationResult, 'application');

    if (CONFIG.enableCrmIntakeEventLog) {
      const intakeEventRecord = buildIntakeEventRecord(normalizedLead, {
        contactId,
        applicationId,
        manualReviewReasons
      });
      await upsertCrmRecord({
        moduleApiName: CONFIG.intakeEventsModule,
        duplicateCheckFields: CONFIG.intakeEventDuplicateCheckFields,
        record: intakeEventRecord
      });
    }

    return sendJson(res, 200, {
      ok: true,
      mode: 'live',
      request_id: requestId,
      lead_reference: normalizedLead.leadReference,
      contact: summarizeZohoResult(contactResult),
      application: summarizeZohoResult(applicationResult),
      manual_review_required: manualReviewReasons.length > 0,
      manual_review_reasons: manualReviewReasons
    });
  } catch (error) {
    console.error(JSON.stringify({
      level: 'error',
      service: 'gh-zillow-lead-intake',
      request_id: requestId,
      error: error.publicCode || 'internal_error',
      detail: CONFIG.debugErrors ? safeErrorMessage(error) : undefined
    }));

    const status = Number(error.statusCode || error.status || 500);
    return fail(res, requestId, status, error.publicCode || 'internal_error');
  }
}

function buildConfig() {
  const fieldMapOverride = envJson('ZOHO_CRM_FIELD_MAP_JSON', {});
  return {
    version: env('GATEWAY_VERSION', '2026-07-02.v1'),
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

    contactsModule: env('ZOHO_CRM_CONTACTS_MODULE', 'Contacts').trim(),
    applicationsModule: env('ZOHO_CRM_APPLICATIONS_MODULE', 'Deals').trim(),
    intakeEventsModule: env('ZOHO_CRM_INTAKE_EVENTS_MODULE', 'Zillow_Intake_Events').trim(),
    enableCrmIntakeEventLog: envBool('ENABLE_CRM_INTAKE_EVENT_LOG', false),

    contactDuplicateCheckFields: envList('CONTACT_DUPLICATE_CHECK_FIELDS', ['Email', 'Mobile', 'Phone']),
    applicationDuplicateCheckFields: envList('APPLICATION_DUPLICATE_CHECK_FIELDS', ['Zillow_Lead_Key']),
    intakeEventDuplicateCheckFields: envList('INTAKE_EVENT_DUPLICATE_CHECK_FIELDS', ['External_Event_Key']),

    triggerWorkflows: envBool('CRM_TRIGGER_WORKFLOWS', false),
    triggerApprovals: envBool('CRM_TRIGGER_APPROVALS', false),
    triggerBlueprints: envBool('CRM_TRIGGER_BLUEPRINTS', false),
    skipCadencesOnInsert: envBool('SKIP_CADENCES_ON_INSERT', true),
    skipCadencesOnUpdate: envBool('SKIP_CADENCES_ON_UPDATE', false),

    defaultApplicationStage: env('DEFAULT_APPLICATION_STAGE', 'New Inquiry').trim(),
    defaultApplicationPipeline: env('DEFAULT_APPLICATION_PIPELINE', '').trim(),
    defaultLeadSource: env('DEFAULT_LEAD_SOURCE', 'Zillow').trim(),
    defaultContactType: env('DEFAULT_CONTACT_TYPE', 'Applicant').trim(),
    defaultScreeningStatus: env('DEFAULT_SCREENING_STATUS', 'Not Started').trim(),
    defaultOwnerDecision: env('DEFAULT_OWNER_DECISION', 'New Inquiry').trim(),
    defaultPortalAccessStatus: env('DEFAULT_PORTAL_ACCESS_STATUS', 'Not Invited').trim(),
    applicationCloseDaysFromIntake: envNumber('APPLICATION_CLOSE_DAYS_FROM_INTAKE', 14),

    propertyUnitMap: envJson('PROPERTY_UNIT_MAP_JSON', {}),
    fieldMap: deepMerge(DEFAULT_FIELD_MAP, fieldMapOverride),
    debugErrors: envBool('DEBUG_ERRORS', false)
  };
}

function handleHealth(req, res) {
  if (!CONFIG.enableHealth) return fail(res, makeRequestId(), 404, 'health_disabled');

  if (CONFIG.healthToken) {
    const got = getHeader(req.headers, CONFIG.healthHeaderName);
    if (!safeTimingEqualText(got, CONFIG.healthToken)) {
      return fail(res, makeRequestId(), 404, 'not_found');
    }
  }

  return sendJson(res, 200, {
    ok: true,
    service: 'gh-zillow-lead-intake',
    version: CONFIG.version,
    mode: CONFIG.dryRun ? 'dry_run' : 'live'
  });
}

function validateInboundSecret(req) {
  if (!CONFIG.requireInboundSecret) return { ok: true };
  if (!CONFIG.inboundSecretValue) return { ok: false, reason: 'secret_not_configured' };

  const headerValue = getHeader(req.headers, CONFIG.inboundSecretHeaderName);
  if (safeTimingEqualText(headerValue, CONFIG.inboundSecretValue)) return { ok: true };

  if (CONFIG.allowSecretQueryParam) {
    const parsed = safeParseRequestUrl(req);
    const queryValue = parsed.searchParams.get(CONFIG.inboundSecretQueryParam);
    if (safeTimingEqualText(queryValue, CONFIG.inboundSecretValue)) return { ok: true };
  }

  return { ok: false, reason: 'secret_mismatch' };
}

function parseInboundPayload(rawBody, contentType) {
  const bodyText = rawBody.toString('utf8');
  if (contentType.includes('application/json')) {
    try {
      return JSON.parse(bodyText || '{}');
    } catch (error) {
      throw publicError(400, 'invalid_json_body');
    }
  }

  if (contentType.includes('application/x-www-form-urlencoded') || !contentType) {
    const params = new URLSearchParams(bodyText);
    const output = {};
    for (const [key, value] of params.entries()) {
      if (Object.prototype.hasOwnProperty.call(output, key)) {
        output[key] = Array.isArray(output[key]) ? [...output[key], value] : [output[key], value];
      } else {
        output[key] = value;
      }
    }
    return output;
  }

  throw publicError(415, 'unsupported_content_type');
}

function normalizeZillowLeadPayload(payload, receivedAtIso = new Date().toISOString()) {
  const normalizedInput = normalizeInputObject(payload);
  const rawFieldKeys = Object.keys(payload || {}).sort();

  const fullName = firstValue(normalizedInput, [
    'name',
    'full_name',
    'contact_name',
    'prospect_name',
    'applicant_name',
    'lead_name'
  ]);

  const parsedName = splitPersonName(fullName);
  const firstName = firstValue(normalizedInput, ['first_name', 'firstname', 'first']) || parsedName.firstName;
  const lastName = firstValue(normalizedInput, ['last_name', 'lastname', 'last']) || parsedName.lastName;
  const email = normalizeEmail(firstValue(normalizedInput, ['email', 'email_address', 'contact_email', 'applicant_email']));
  const phone = normalizePhone(firstValue(normalizedInput, [
    'phone',
    'phone_number',
    'mobile',
    'cell',
    'contact_phone',
    'applicant_phone'
  ]));

  const leadId = cleanText(firstValue(normalizedInput, [
    'lead_id',
    'zillow_lead_id',
    'zillowleadid',
    'contact_id',
    'id'
  ]));

  const listingId = cleanText(firstValue(normalizedInput, [
    'listing_id',
    'zillow_listing_id',
    'listingid',
    'zpid',
    'property_id',
    'rental_id'
  ]));

  const propertyAddress = cleanText(firstValue(normalizedInput, [
    'property_address',
    'listing_address',
    'address',
    'street_address',
    'property'
  ]));

  const unit = cleanText(firstValue(normalizedInput, [
    'unit',
    'unit_number',
    'apartment',
    'apt',
    'unit_name'
  ]));

  const desiredMoveInDate = normalizeDate(firstValue(normalizedInput, [
    'desired_move_in_date',
    'move_in_date',
    'moveindate',
    'preferred_move_in_date'
  ]));

  const receivedAtDate = normalizeDate(firstValue(normalizedInput, [
    'received_at',
    'created_at',
    'submitted_at',
    'timestamp',
    'date'
  ])) || isoDateOnly(receivedAtIso);

  const source = cleanText(firstValue(normalizedInput, ['source', 'lead_source', 'provider'])) || 'Zillow';
  const message = cleanText(firstValue(normalizedInput, [
    'message',
    'comments',
    'comment',
    'lead_message',
    'description',
    'note'
  ]));

  const listingUrl = cleanUrl(firstValue(normalizedInput, [
    'listing_url',
    'url',
    'property_url',
    'zillow_url'
  ]));

  const rent = normalizeMoney(firstValue(normalizedInput, ['rent', 'monthly_rent', 'price']));
  const deposit = normalizeMoney(firstValue(normalizedInput, ['deposit', 'security_deposit']));
  const bedrooms = cleanText(firstValue(normalizedInput, ['beds', 'bedrooms']));
  const bathrooms = cleanText(firstValue(normalizedInput, ['baths', 'bathrooms']));
  const pets = cleanText(firstValue(normalizedInput, ['pets', 'pet', 'has_pets']));

  const leadKey = buildLeadKey({
    leadId,
    email,
    phone,
    listingId,
    propertyAddress,
    unit,
    message
  });

  return {
    leadKey,
    leadReference: publicLeadReference(leadKey),
    leadId,
    listingId,
    listingUrl,
    source,
    firstName: cleanText(firstName),
    lastName: cleanText(lastName),
    email,
    phone,
    message,
    propertyAddress,
    unit,
    desiredMoveInDate,
    receivedAtDate,
    receivedAtIso,
    rent,
    deposit,
    bedrooms,
    bathrooms,
    pets,
    rawFieldKeys
  };
}

function validateNormalizedLead(lead) {
  const publicErrors = [];

  if (!lead.email && !lead.phone) {
    publicErrors.push('Lead must include at least one contact method: email or phone.');
  }

  if (lead.email && !isLikelyEmail(lead.email)) {
    publicErrors.push('Lead email is not valid.');
  }

  if (lead.phone && lead.phone.replace(/\D/g, '').length < 10) {
    publicErrors.push('Lead phone is too short.');
  }

  return {
    ok: publicErrors.length === 0,
    publicErrors
  };
}

function resolvePropertyUnit(lead, propertyUnitMap) {
  const keys = [];
  if (lead.listingId) keys.push(`listing:${normalizeMapKey(lead.listingId)}`);
  if (lead.propertyAddress || lead.unit) {
    keys.push(`address:${normalizeMapKey(lead.propertyAddress)}|${normalizeMapKey(lead.unit)}`);
  }
  keys.push('default');

  for (const key of keys) {
    if (propertyUnitMap && propertyUnitMap[key]) {
      return {
        matchedKey: key,
        ...propertyUnitMap[key]
      };
    }
  }

  return null;
}

function buildManualReviewReasons(lead, propertyUnit) {
  const reasons = [];
  if (!lead.firstName || !lead.lastName) reasons.push('Missing full applicant name.');
  if (!lead.email) reasons.push('Missing applicant email.');
  if (!lead.phone) reasons.push('Missing applicant phone.');
  if (!lead.propertyAddress && !lead.listingId) reasons.push('Missing listing ID and property address.');
  if (!propertyUnit) reasons.push('No CRM property/unit mapping matched the Zillow lead.');
  if (!lead.desiredMoveInDate) reasons.push('Desired move-in date was not provided.');
  return reasons;
}

function buildCrmPlan(lead, propertyUnit, manualReviewReasons) {
  const manualReviewRequired = manualReviewReasons.length > 0;
  const fieldMap = CONFIG.fieldMap;
  const contactLastName = lead.lastName || lead.firstName || 'Zillow Prospect';
  const contactDescription = [
    'Imported from Zillow lead intake.',
    `Lead reference: ${lead.leadReference}`,
    lead.listingId ? `Listing ID: ${lead.listingId}` : '',
    lead.propertyAddress ? `Property: ${lead.propertyAddress}` : '',
    lead.unit ? `Unit: ${lead.unit}` : '',
    lead.message ? `Message: ${truncate(lead.message, 1500)}` : '',
    manualReviewRequired ? `Manual review: ${manualReviewReasons.join(' ')}` : ''
  ].filter(Boolean).join('\n');

  const contactRecord = compactRecord({
    [fieldMap.contact.firstName]: lead.firstName || undefined,
    [fieldMap.contact.lastName]: contactLastName,
    [fieldMap.contact.email]: lead.email || undefined,
    [fieldMap.contact.phone]: lead.phone || undefined,
    [fieldMap.contact.mobile]: lead.phone || undefined,
    [fieldMap.contact.leadSource]: CONFIG.defaultLeadSource,
    [fieldMap.contact.contactType]: CONFIG.defaultContactType,
    [fieldMap.contact.portalAccessStatus]: CONFIG.defaultPortalAccessStatus,
    [fieldMap.contact.relatedProperty]: propertyUnit && propertyUnit.propertyId ? { id: String(propertyUnit.propertyId) } : undefined,
    [fieldMap.contact.relatedUnit]: propertyUnit && propertyUnit.unitId ? { id: String(propertyUnit.unitId) } : undefined,
    [fieldMap.contact.description]: contactDescription
  });

  const applicationName = buildApplicationName(lead, propertyUnit);
  const closeDate = addDays(lead.receivedAtDate, CONFIG.applicationCloseDaysFromIntake);
  const applicationNotes = [
    'Zillow lead intake created this Rental Application record.',
    'Do not generate lease, Books customer, recurring invoice, or tenant portal access until owner approval.',
    `Lead reference: ${lead.leadReference}`,
    propertyUnit && propertyUnit.matchedKey ? `Property/unit mapping: ${propertyUnit.matchedKey}` : '',
    lead.bedrooms ? `Bedrooms from source: ${lead.bedrooms}` : '',
    lead.bathrooms ? `Bathrooms from source: ${lead.bathrooms}` : '',
    lead.pets ? `Pets from source: ${lead.pets}` : '',
    manualReviewRequired ? `Manual review: ${manualReviewReasons.join(' ')}` : ''
  ].filter(Boolean).join('\n');

  const applicationRecord = compactRecord({
    [fieldMap.application.name]: applicationName,
    [fieldMap.application.stage]: CONFIG.defaultApplicationStage,
    [fieldMap.application.pipeline]: CONFIG.defaultApplicationPipeline || undefined,
    [fieldMap.application.closingDate]: closeDate,
    [fieldMap.application.amount]: lead.rent || (propertyUnit && propertyUnit.approvedRent) || undefined,
    [fieldMap.application.property]: propertyUnit && propertyUnit.propertyId ? { id: String(propertyUnit.propertyId) } : undefined,
    [fieldMap.application.unit]: propertyUnit && propertyUnit.unitId ? { id: String(propertyUnit.unitId) } : undefined,
    [fieldMap.application.zillowLeadKey]: lead.leadKey,
    [fieldMap.application.zillowLeadId]: lead.leadId || undefined,
    [fieldMap.application.zillowListingId]: lead.listingId || undefined,
    [fieldMap.application.zillowListingUrl]: lead.listingUrl || undefined,
    [fieldMap.application.zillowMessage]: lead.message || undefined,
    [fieldMap.application.zillowSource]: lead.source || CONFIG.defaultLeadSource,
    [fieldMap.application.zillowRawFieldKeys]: lead.rawFieldKeys.join(', '),
    [fieldMap.application.applicationReceivedDate]: lead.receivedAtDate,
    [fieldMap.application.desiredMoveInDate]: lead.desiredMoveInDate || undefined,
    [fieldMap.application.screeningStatus]: CONFIG.defaultScreeningStatus,
    [fieldMap.application.ownerDecision]: CONFIG.defaultOwnerDecision,
    [fieldMap.application.approvedRent]: (propertyUnit && propertyUnit.approvedRent) || undefined,
    [fieldMap.application.approvedDeposit]: (propertyUnit && propertyUnit.approvedDeposit) || undefined,
    [fieldMap.application.manualReviewRequired]: manualReviewRequired,
    [fieldMap.application.manualReviewReason]: manualReviewReasons.join('\n') || undefined,
    [fieldMap.application.notes]: applicationNotes
  });

  return { contactRecord, applicationRecord };
}

function buildIntakeEventRecord(lead, result) {
  const fieldMap = CONFIG.fieldMap.intakeEvent;
  return compactRecord({
    [fieldMap.name]: `Zillow Intake - ${lead.leadReference}`,
    [fieldMap.externalEventKey]: lead.leadKey,
    [fieldMap.leadReference]: lead.leadReference,
    [fieldMap.source]: lead.source || CONFIG.defaultLeadSource,
    [fieldMap.receivedAt]: lead.receivedAtIso,
    [fieldMap.status]: 'Processed',
    [fieldMap.contactId]: result.contactId,
    [fieldMap.applicationId]: result.applicationId,
    [fieldMap.rawFieldKeys]: lead.rawFieldKeys.join(', '),
    [fieldMap.manualReviewRequired]: result.manualReviewReasons.length > 0,
    [fieldMap.manualReviewReason]: result.manualReviewReasons.join('\n') || undefined
  });
}

async function upsertCrmRecord({ moduleApiName, duplicateCheckFields, record }) {
  const accessToken = await getZohoAccessToken();
  const url = new URL(`${CONFIG.crmBaseUrl.replace(/\/$/, '')}/crm/${CONFIG.crmApiVersion}/${encodeURIComponent(moduleApiName)}/upsert`);

  const body = {
    data: [record],
    duplicate_check_fields: duplicateCheckFields,
    trigger: buildZohoTriggers()
  };

  const skipFeatureExecution = buildSkipFeatureExecution();
  if (skipFeatureExecution.length > 0) body.skip_feature_execution = skipFeatureExecution;

  const response = await zohoRequest({
    method: 'POST',
    url,
    accessToken,
    body
  });

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
  if (tokenCache.accessToken && tokenCache.expiresAtMs > now + 60000) {
    return tokenCache.accessToken;
  }

  if (!CONFIG.zohoClientId || !CONFIG.zohoClientSecret || !CONFIG.zohoRefreshToken) {
    throw publicError(500, 'zoho_oauth_not_configured');
  }

  const url = new URL(`${CONFIG.accountsBaseUrl.replace(/\/$/, '')}/oauth/v2/token`);
  url.searchParams.set('refresh_token', CONFIG.zohoRefreshToken);
  url.searchParams.set('client_id', CONFIG.zohoClientId);
  url.searchParams.set('client_secret', CONFIG.zohoClientSecret);
  url.searchParams.set('grant_type', 'refresh_token');

  const response = await requestJson({
    method: 'POST',
    url,
    headers: {
      accept: 'application/json'
    }
  });

  if (!response.access_token) {
    throw publicError(502, 'zoho_oauth_failed');
  }

  const expiresInSeconds = Number(response.expires_in || 3600);
  tokenCache.accessToken = response.access_token;
  tokenCache.expiresAtMs = now + Math.max(300, expiresInSeconds - 120) * 1000;
  return tokenCache.accessToken;
}

async function zohoRequest({ method, url, accessToken, body }) {
  return requestJson({
    method,
    url,
    headers: {
      authorization: `Zoho-oauthtoken ${accessToken}`,
      'content-type': 'application/json',
      accept: 'application/json'
    },
    body: JSON.stringify(body)
  });
}

function requestJson({ method, url, headers = {}, body }) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, { method, headers, timeout: 15000 }, (res) => {
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const text = Buffer.concat(chunks).toString('utf8');
        let parsed = {};
        if (text) {
          try {
            parsed = JSON.parse(text);
          } catch (error) {
            const err = publicError(502, 'invalid_zoho_response');
            err.statusCode = 502;
            return reject(err);
          }
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

    req.on('timeout', () => {
      req.destroy(publicError(504, 'zoho_request_timeout'));
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
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
  if (!CONFIG.liveModeEnabled) {
    throw publicError(500, 'live_mode_disabled');
  }

  if (!safeTimingEqualText(CONFIG.liveModeConfirmation, CONFIG.expectedLiveModeConfirmation)) {
    throw publicError(500, 'live_mode_confirmation_missing');
  }
}

function buildLeadKey(parts) {
  if (parts.leadId) return `zillow:${parts.leadId}`;

  const stableText = [
    parts.email || '',
    parts.phone || '',
    parts.listingId || '',
    normalizeMapKey(parts.propertyAddress || ''),
    normalizeMapKey(parts.unit || ''),
    normalizeMapKey(parts.message || '')
  ].join('|');

  return `zillow:hash:${sha256(stableText).slice(0, 40)}`;
}

function publicLeadReference(leadKey) {
  return `zlw_${sha256(leadKey).slice(0, 16)}`;
}

function buildApplicationName(lead, propertyUnit) {
  const applicant = [lead.firstName, lead.lastName].filter(Boolean).join(' ') || 'Zillow Prospect';
  const unitLabel = (propertyUnit && propertyUnit.unitName) || lead.unit || lead.propertyAddress || lead.listingId || 'Unmapped Unit';
  return truncate(`Zillow - ${applicant} - ${unitLabel} - ${lead.receivedAtDate}`, 120);
}

function sanitizePlanForResponse(plan) {
  return {
    contact_module: CONFIG.contactsModule,
    application_module: CONFIG.applicationsModule,
    contact_fields: Object.keys(plan.contactRecord).sort(),
    application_fields: Object.keys(plan.applicationRecord).sort(),
    duplicate_check_fields: {
      contact: CONFIG.contactDuplicateCheckFields,
      application: CONFIG.applicationDuplicateCheckFields
    }
  };
}

function summarizeZohoResult(result) {
  const first = result && Array.isArray(result.data) ? result.data[0] : null;
  return {
    status: first ? first.status : 'unknown',
    code: first ? first.code : undefined,
    action: first && first.action ? first.action : undefined,
    id: first && first.details ? first.details.id : undefined
  };
}

function extractZohoRecordId(result, label) {
  const first = result && Array.isArray(result.data) ? result.data[0] : null;
  const id = first && first.details ? first.details.id : '';
  if (!id) throw publicError(502, `missing_${label}_id`);
  return id;
}

function normalizeInputObject(input) {
  const output = {};
  for (const [key, value] of Object.entries(input || {})) {
    const normalizedKey = normalizeFieldKey(key);
    output[normalizedKey] = Array.isArray(value) ? value.find((item) => cleanText(item)) : value;
  }
  return output;
}

function firstValue(input, keys) {
  for (const key of keys) {
    const normalizedKey = normalizeFieldKey(key);
    const value = cleanText(input[normalizedKey]);
    if (value) return value;
  }
  return '';
}

function normalizeFieldKey(key) {
  return String(key || '')
    .trim()
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase();
}

function cleanText(value) {
  if (value === null || value === undefined) return '';
  return String(value).replace(/\s+/g, ' ').trim();
}

function cleanUrl(value) {
  const text = cleanText(value);
  if (!text) return '';
  if (/^https?:\/\//i.test(text)) return text;
  return '';
}

function normalizeEmail(value) {
  return cleanText(value).toLowerCase();
}

function normalizePhone(value) {
  const text = cleanText(value);
  if (!text) return '';
  const digits = text.replace(/\D/g, '');
  if (digits.length === 10) return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith('1')) return `+${digits}`;
  return text;
}

function normalizeDate(value) {
  const text = cleanText(value);
  if (!text) return '';

  const isoMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (isoMatch) return `${isoMatch[1]}-${isoMatch[2]}-${isoMatch[3]}`;

  const usMatch = text.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (usMatch) {
    return `${usMatch[3]}-${String(usMatch[1]).padStart(2, '0')}-${String(usMatch[2]).padStart(2, '0')}`;
  }

  const parsed = new Date(text);
  if (!Number.isNaN(parsed.getTime())) return isoDateOnly(parsed.toISOString());
  return '';
}

function normalizeMoney(value) {
  const text = cleanText(value);
  if (!text) return undefined;
  const number = Number(text.replace(/[$,]/g, ''));
  return Number.isFinite(number) ? number : undefined;
}

function splitPersonName(fullName) {
  const text = cleanText(fullName);
  if (!text) return { firstName: '', lastName: '' };
  const parts = text.split(' ').filter(Boolean);
  if (parts.length === 1) return { firstName: '', lastName: parts[0] };
  return {
    firstName: parts.slice(0, -1).join(' '),
    lastName: parts[parts.length - 1]
  };
}

function normalizeMapKey(value) {
  return cleanText(value).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function compactRecord(record) {
  const output = {};
  for (const [key, value] of Object.entries(record)) {
    if (!key) continue;
    if (value === undefined || value === null || value === '') continue;
    output[key] = value;
  }
  return output;
}

function deepMerge(base, override) {
  const output = { ...base };
  for (const [key, value] of Object.entries(override || {})) {
    if (value && typeof value === 'object' && !Array.isArray(value) && base[key]) {
      output[key] = deepMerge(base[key], value);
    } else {
      output[key] = value;
    }
  }
  return output;
}

function addDays(yyyyMmDd, days) {
  const base = new Date(`${yyyyMmDd}T00:00:00Z`);
  base.setUTCDate(base.getUTCDate() + Number(days || 0));
  return isoDateOnly(base.toISOString());
}

function isoDateOnly(iso) {
  return String(iso || '').slice(0, 10);
}

function isLikelyEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isAllowedContentType(contentType) {
  return (
    contentType.includes('application/x-www-form-urlencoded') ||
    contentType.includes('application/json') ||
    contentType === ''
  );
}

function readRequestBody(req, maxBytes) {
  if (Buffer.isBuffer(req.rawBody)) return Promise.resolve(req.rawBody);
  if (typeof req.body === 'string') return Promise.resolve(Buffer.from(req.body, 'utf8'));
  if (req.body && typeof req.body === 'object' && typeof req.on !== 'function') {
    return Promise.resolve(Buffer.from(JSON.stringify(req.body), 'utf8'));
  }

  return new Promise((resolve, reject) => {
    const chunks = [];
    let total = 0;

    req.on('data', (chunk) => {
      total += chunk.length;
      if (total > maxBytes) {
        reject(publicError(413, 'payload_too_large'));
        if (typeof req.destroy === 'function') req.destroy();
        return;
      }
      chunks.push(chunk);
    });

    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function getRequestPath(req) {
  return safeParseRequestUrl(req).pathname;
}

function safeParseRequestUrl(req) {
  const raw = req.url || '/';
  return new URL(raw, 'https://gh-real-estate.local');
}

function getDeclaredContentLength(req) {
  const raw = getHeader(req.headers, 'content-length');
  if (!raw) return null;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : null;
}

function getHeader(headers, name) {
  const target = String(name || '').toLowerCase();
  for (const [key, value] of Object.entries(headers || {})) {
    if (String(key).toLowerCase() === target) {
      return Array.isArray(value) ? value[0] : String(value || '');
    }
  }
  return '';
}

function setSecurityHeaders(res) {
  if (!res || typeof res.setHeader !== 'function') return;
  res.setHeader('content-type', 'application/json; charset=utf-8');
  res.setHeader('x-content-type-options', 'nosniff');
  res.setHeader('cache-control', 'no-store');
}

function sendJson(res, statusCode, body) {
  const payload = JSON.stringify(body);
  if (typeof res.writeHead === 'function') res.writeHead(statusCode);
  else res.statusCode = statusCode;
  if (typeof res.end === 'function') return res.end(payload);
  return payload;
}

function fail(res, requestId, statusCode, code, extra = {}) {
  const body = {
    ok: false,
    request_id: requestId,
    error: code,
    ...extra
  };
  return sendJson(res, statusCode, body);
}

function publicError(statusCode, publicCode) {
  const error = new Error(publicCode);
  error.statusCode = statusCode;
  error.publicCode = publicCode;
  return error;
}

function safeErrorMessage(error) {
  return String(error && error.message ? error.message : error).slice(0, 500);
}

function sanitizeZohoError(value) {
  if (!value || typeof value !== 'object') return value;
  const text = JSON.stringify(value);
  return JSON.parse(text.replace(/1000\.[A-Za-z0-9._-]+/g, '[redacted-token]'));
}

function sha256(text) {
  return crypto.createHash('sha256').update(String(text)).digest('hex');
}

function safeTimingEqualText(a, b) {
  const left = Buffer.from(String(a || ''), 'utf8');
  const right = Buffer.from(String(b || ''), 'utf8');
  if (left.length !== right.length) return false;
  return crypto.timingSafeEqual(left, right);
}

function makeRequestId() {
  return crypto.randomBytes(8).toString('hex');
}

function truncate(text, maxLength) {
  const value = cleanText(text);
  if (value.length <= maxLength) return value;
  return `${value.slice(0, Math.max(0, maxLength - 3))}...`;
}

function env(name, fallback = '') {
  return process.env[name] === undefined ? fallback : process.env[name];
}

function envBool(name, fallback = false) {
  const value = env(name, String(fallback)).trim().toLowerCase();
  return ['1', 'true', 'yes', 'y', 'on'].includes(value);
}

function envNumber(name, fallback) {
  const value = Number(env(name, String(fallback)));
  return Number.isFinite(value) ? value : fallback;
}

function envList(name, fallback = []) {
  const value = env(name, '');
  if (!value.trim()) return fallback;
  return value.split(',').map((item) => item.trim()).filter(Boolean);
}

function envJson(name, fallback = {}) {
  const value = env(name, '').trim();
  if (!value) return fallback;
  try {
    return JSON.parse(value);
  } catch (error) {
    throw new Error(`${name} must be valid JSON`);
  }
}

module.exports = handler;
module.exports._test = {
  DEFAULT_FIELD_MAP,
  normalizeZillowLeadPayload,
  validateNormalizedLead,
  resolvePropertyUnit,
  buildManualReviewReasons,
  buildCrmPlan,
  buildLeadKey,
  parseInboundPayload,
  normalizePhone,
  normalizeDate,
  normalizeFieldKey,
  publicLeadReference
};
