'use strict';

/**
 * GH Real Estate — Zoho Payments Returned Payment Fee Webhook Gateway
 * Platform: Zoho Catalyst Advanced I/O, Node.js 24
 * Entry: module.exports = async (req, res) => { ... }
 *
 * Purpose
 * - Receive Zoho Payments payment.failed webhooks.
 * - Verify X-Zoho-Webhook-Signature using the Zoho Payments webhook signing key.
 * - Enforce request hardening: method, path allowlist, JSON content type, size limits,
 *   no compressed payloads, optional shared/admin header, optional IP allowlist.
 * - Enforce replay controls with timestamp validation and Catalyst Cache best-effort dedupe.
 * - Retrieve the payment from Zoho Payments as source of truth.
 * - Verify the payment is actually failed and that the payment session is no longer active.
 * - Resolve the related Zoho Books invoice.
 * - Create a returned-payment fee invoice in Zoho Books.
 * - Update the source invoice ledger field to prevent duplicate RF invoices.
 *
 * Important production rule
 * - Deploy first in REGISTRATION_ONLY=true and REQUIRE_SIGNATURE=false so Zoho Payments can
 *   register/ping the endpoint before you have the signing key. After registration, copy the
 *   signing key into ZPAYMENTS_WEBHOOK_SIGNING_KEY, set REQUIRE_SIGNATURE=true and
 *   REGISTRATION_ONLY=false, then redeploy.
 */

const crypto = require('crypto');
const https = require('https');
const { URL, URLSearchParams } = require('url');
const { TextDecoder: UtilTextDecoder } = require('util');

const catalystSdk = require('zcatalyst-sdk-node');

// =============================================================================
// Configuration
// =============================================================================
const CONFIG = {
  version: env('GATEWAY_VERSION', '2026-05-13.v1'),

  // Inbound route/security
  allowedPaths: envList('ALLOWED_PATHS', ['/zpayments/payment-failed']),
  requireJson: envBool('REQUIRE_JSON', true),
  maxBodyBytes: envNumber('MAX_BODY_BYTES', 262144),
  inboundBodyTimeoutMs: envNumber('INBOUND_BODY_TIMEOUT_MS', 8000),
  requireSignature: envBool('REQUIRE_SIGNATURE', true),
  registrationOnly: envBool('REGISTRATION_ONLY', false),
  dryRun: envBool('DRY_RUN', true),

  // Public response / health hardening.
  // Keep public health disabled in production unless you protect it with HEALTH_CHECK_TOKEN.
  genericPublicErrors: envBool('GENERIC_PUBLIC_ERRORS', true),
  enableHealth: envBool('ENABLE_HEALTH', false),
  healthHeaderName: env('HEALTH_HEADER_NAME', 'x-gh-health-token').toLowerCase().trim(),
  healthToken: env('HEALTH_CHECK_TOKEN', '').trim(),

  // Live-mode circuit breaker. This prevents accidental invoice creation if DRY_RUN is
  // flipped to false without an explicit production approval flag.
  requireLiveModeConfirmation: envBool('REQUIRE_LIVE_MODE_CONFIRMATION', true),
  liveModeConfirmation: env('LIVE_MODE_CONFIRMATION', '').trim(),
  expectedLiveModeConfirmation: env('EXPECTED_LIVE_MODE_CONFIRMATION', 'GH_RETURNED_FEE_LIVE_APPROVED').trim(),

  // Optional shared-header gate. Keep false for normal Zoho webhook traffic unless Zoho lets
  // you configure custom headers. This is useful for private/admin routes.
  requireSharedHeader: envBool('REQUIRE_SHARED_HEADER', false),
  sharedHeaderName: env('SHARED_HEADER_NAME', 'x-gh-webhook-key').toLowerCase().trim(),
  sharedHeaderValue: env('SHARED_HEADER_VALUE', '').trim(),

  // Optional IP allowlist. Only enable after confirming what IP reaches Catalyst in logs.
  enforceIpAllowlist: envBool('ENFORCE_IP_ALLOWLIST', false),
  allowedIps: envList('ALLOWED_IPS', []),

  // Signature / replay
  webhookSigningKey: env('ZPAYMENTS_WEBHOOK_SIGNING_KEY', '').trim(),
  webhookSigningKeyPrevious: env('ZPAYMENTS_WEBHOOK_SIGNING_KEY_PREVIOUS', '').trim(),
  signatureToleranceSeconds: envNumber('SIGNATURE_TOLERANCE_SECONDS', 900),
  allowMissingTimestampWhenSignatureOff: envBool('ALLOW_MISSING_TIMESTAMP_WHEN_SIGNATURE_OFF', true),
  enableReplayDefense: envBool('ENABLE_REPLAY_DEFENSE', true),
  strictReplayFailure: envBool('STRICT_REPLAY_FAILURE', true),
  replayCacheSegmentId: env('REPLAY_CACHE_SEGMENT_ID', ''),
  replayKeyPrefix: env('REPLAY_KEY_PREFIX', 'zpr:'),
  replayWindowSeconds: envNumber('REPLAY_WINDOW_SECONDS', 86400),
  lockWindowSeconds: envNumber('PAYMENT_LOCK_SECONDS', 300),

  // Manual admin processing route for testing one failed payment ID.
  enableAdminProcessPayment: envBool('ENABLE_ADMIN_PROCESS_PAYMENT', false),
  adminHeaderName: env('ADMIN_HEADER_NAME', 'x-gh-admin-key').toLowerCase().trim(),
  adminHeaderValue: env('ADMIN_HEADER_VALUE', '').trim(),

  // Zoho API roots. Use US defaults for GH Real Estate.
  accountsBaseUrl: env('ZOHO_ACCOUNTS_BASE_URL', 'https://accounts.zoho.com').trim(),
  paymentsBaseUrl: env('ZOHO_PAYMENTS_BASE_URL', 'https://payments.zoho.com').trim(),
  booksBaseUrl: env('ZOHO_BOOKS_BASE_URL', 'https://www.zohoapis.com/books/v3').trim(),
  accountsAllowedHostSuffixes: envList('ACCOUNTS_ALLOWED_HOST_SUFFIXES', ['accounts.zoho.com']),
  paymentsAllowedHostSuffixes: envList('PAYMENTS_ALLOWED_HOST_SUFFIXES', ['payments.zoho.com']),
  booksAllowedHostSuffixes: envList('BOOKS_ALLOWED_HOST_SUFFIXES', ['zohoapis.com']),

  // OAuth
  zohoClientId: env('ZOHO_CLIENT_ID', '').trim(),
  zohoClientSecret: env('ZOHO_CLIENT_SECRET', '').trim(),
  zohoRefreshToken: env('ZOHO_REFRESH_TOKEN', '').trim(),

  // App IDs
  zohoPaymentsAccountId: env('ZOHO_PAYMENTS_ACCOUNT_ID', '').trim(),
  zohoBooksOrgId: env('ZOHO_BOOKS_ORG_ID', '').trim(),

  // Returned-payment fee configuration
  returnedFeeItemId: env('RETURNED_FEE_ITEM_ID', '').trim(),
  returnedFeeAmount: envNumber('RETURNED_FEE_AMOUNT', 30.00),
  returnedFeeInvoicePrefix: env('RETURNED_FEE_INVOICE_PREFIX', 'RF').trim(),
  returnedFeeLedgerFieldApiName: env('RETURNED_FEE_LEDGER_FIELD_API_NAME', 'cf_returned_payment_fee_events'),
  optionalLatestRfInvoiceFieldApiName: env('OPTIONAL_LATEST_RF_INVOICE_FIELD_API_NAME', 'cf_returned_fee_invoice_number'),
  updateOptionalLatestRfInvoiceField: envBool('UPDATE_OPTIONAL_LATEST_RF_INVOICE_FIELD', false),
  maxLedgerLength: envNumber('MAX_LEDGER_LENGTH', 32000),
  sendInvoiceOnCreate: envBool('SEND_INVOICE_ON_CREATE', false),
  booksPaymentOptionsEnabled: envBool('BOOKS_PAYMENT_OPTIONS_ENABLED', true),
  booksPaymentGatewaysCsv: env('BOOKS_PAYMENT_GATEWAYS_CSV', ''),

  // Policy controls
  skipCustomerCanceledOrAbandoned: envBool('SKIP_CUSTOMER_CANCELED_OR_ABANDONED', true),
  deferIfPaymentSessionActive: envBool('DEFER_IF_PAYMENT_SESSION_ACTIVE', true),
  skipNonFinalFailureKeywords: envList('SKIP_FAILURE_REASON_KEYWORDS', [
    'widget_closed',
    'abandoned',
    'customer_canceled',
    'customer_cancelled',
    'customer canceled',
    'customer cancelled'
  ]),

  // Diagnostics
  debugPayloadLogging: envBool('DEBUG_PAYLOAD_LOGGING', false),
  debugSafeZohoBodies: envBool('DEBUG_SAFE_ZOHO_BODIES', false),
  outboundTimeoutMs: envNumber('OUTBOUND_TIMEOUT_MS', 15000),

  // Temporary OAuth diagnostic route. Disable after OAuth is confirmed.
  enableOAuthDiagnostic: envBool('ENABLE_OAUTH_DIAGNOSTIC', false),
  oauthDiagnosticHeaderName: env('OAUTH_DIAGNOSTIC_HEADER_NAME', 'x-gh-oauth-diagnostic-token').toLowerCase().trim(),
  oauthDiagnosticToken: env('OAUTH_DIAGNOSTIC_TOKEN', '').trim(),

  // Protected mock-processing route. Dry-run only; never creates invoices.
  enableMockProcessing: envBool('ENABLE_MOCK_PROCESSING', false),
  mockProcessingHeaderName: env('MOCK_PROCESSING_HEADER_NAME', 'x-gh-mock-processing-token').toLowerCase().trim(),
  mockProcessingToken: env('MOCK_PROCESSING_TOKEN', '').trim(),
};

const CACHE_KEY_MAX_LEN = 50;
const tokenCache = { accessToken: '', expiresAtMs: 0 };

// =============================================================================
// Main Advanced I/O Handler
// =============================================================================
module.exports = async (req, res) => {
  const requestId = makeRequestId();
  const receivedAtIso = new Date().toISOString();

  try {
    setSecurityHeaders(res);

    const method = String(req.method || '').toUpperCase();
    const path = getRequestPath(req);

    if (method === 'GET' && path === '/health') {
      if (!CONFIG.enableHealth) return fail(res, requestId, 404, 'health_disabled');

      if (CONFIG.healthToken) {
        const got = getHeader(req.headers, CONFIG.healthHeaderName);
        if (!safeTimingEqualText(got, CONFIG.healthToken)) return fail(res, requestId, 404, 'not_found');
      }

      return sendJson(res, 200, {
        ok: true,
        service: 'gh-zpayments-returned-fee-webhook',
        version: CONFIG.version,
        mode: CONFIG.registrationOnly ? 'registration_only' : (CONFIG.dryRun ? 'dry_run' : 'live')
      });
    }

    if (method === 'POST' && path === '/admin/process-payment') {
      return await handleAdminProcessPayment(req, res, requestId, receivedAtIso);
    }

    if (method === 'GET' && path === '/oauth/diagnostic') {
      return await handleOAuthDiagnostic(req, res, requestId);
    }

    if (method === 'POST' && path === '/test/simulate-payment-failed') {
      return await handleMockProcessFailedPayment(req, res, requestId, receivedAtIso);
    }

    if (method !== 'POST') return fail(res, requestId, 405, 'method_not_allowed');

    const pathCheck = validateAllowedPath(path);
    if (!pathCheck.ok) return fail(res, requestId, 404, 'path_not_allowed', { path, allowed: CONFIG.allowedPaths });

    if (CONFIG.enforceIpAllowlist) {
      const ip = getClientIp(req);
      if (!CONFIG.allowedIps.includes(ip)) return fail(res, requestId, 403, 'source_ip_not_allowed', { ip });
    }

    const contentEncoding = String(req.headers['content-encoding'] || '').trim().toLowerCase();
    if (contentEncoding && contentEncoding !== 'identity') {
      return fail(res, requestId, 415, 'unsupported_content_encoding', { contentEncoding });
    }

    const declaredLen = getDeclaredContentLength(req);
    if (declaredLen !== null && declaredLen > CONFIG.maxBodyBytes) {
      return fail(res, requestId, 413, 'payload_too_large', { declaredLen, maxBodyBytes: CONFIG.maxBodyBytes });
    }

    if (CONFIG.requireSharedHeader) {
      const got = getHeader(req.headers, CONFIG.sharedHeaderName);
      if (!CONFIG.sharedHeaderValue || !safeTimingEqualText(got, CONFIG.sharedHeaderValue)) {
        return fail(res, requestId, 401, 'shared_header_invalid');
      }
    }

    const contentTypeRaw = String(req.headers['content-type'] || '');
    if (CONFIG.requireJson && !isAllowedJsonContentType(contentTypeRaw)) {
      return fail(res, requestId, 415, 'bad_content_type', { contentType: contentTypeRaw });
    }

    const rawBody = await readRawBodyLimited(req, CONFIG.maxBodyBytes, CONFIG.inboundBodyTimeoutMs);
    const rawBodyString = decodeUtf8Strict(rawBody);
    const payloadSha256 = crypto.createHash('sha256').update(rawBody).digest('hex');

    let signatureInfo = { verified: false, timestamp: 0, ageSeconds: null, signature: '', replayKeyMaterial: payloadSha256 };
    if (CONFIG.requireSignature) {
      signatureInfo = verifyZohoPaymentsWebhookSignature(req, rawBodyString);
      if (!signatureInfo.verified) return fail(res, requestId, 401, 'signature_invalid');
    } else if (!CONFIG.allowMissingTimestampWhenSignatureOff) {
      const sig = parseZohoSignatureHeader(getHeader(req.headers, 'x-zoho-webhook-signature'));
      if (!sig.timestamp) return fail(res, requestId, 401, 'missing_signature_timestamp');
    }

    let payload;
    try { payload = JSON.parse(rawBodyString || '{}'); }
    catch (_) { return fail(res, requestId, 400, 'json_parse_failed'); }

    if (CONFIG.debugPayloadLogging) {
      logInfo({ requestId, event: 'raw_payload', payload });
    }

    const eventInfo = extractEventInfo(payload);
    const eventTypeNorm = normalizeText(eventInfo.eventType);
    const paymentIdFromPayload = eventInfo.paymentId;
    const eventId = eventInfo.eventId || '';

    if (eventTypeNorm && eventTypeNorm !== 'payment.failed') {
      return ok(res, requestId, {
        action: 'ignored',
        reason: 'event_not_payment_failed',
        event_type: eventInfo.eventType,
        event_id: eventId || null
      });
    }

    if (!paymentIdFromPayload) {
      return fail(res, requestId, 400, 'payment_id_not_found');
    }

    if (CONFIG.registrationOnly) {
      return ok(res, requestId, {
        action: 'registration_only_ack',
        event_type: eventInfo.eventType || null,
        payment_id_present: Boolean(paymentIdFromPayload),
        note: 'No invoice creation attempted because REGISTRATION_ONLY=true.'
      });
    }

    // Replay/dedupe cache. Ledger idempotency is still the source of truth.
    const replayKeyMaterial = eventId || paymentIdFromPayload || signatureInfo.replayKeyMaterial || payloadSha256;
    const replayResult = await replaySeenAndMarkBestEffort(req, makeCacheKey('evt:', replayKeyMaterial), CONFIG.replayWindowSeconds);
    if (replayResult.seen) {
      return ok(res, requestId, {
        action: 'ignored',
        reason: 'replay_or_duplicate_event_cache_hit',
        event_id: eventId || null,
        payment_id: paymentIdFromPayload
      });
    }

    const lockKey = makeCacheKey('lock:', paymentIdFromPayload);
    const lockResult = await replaySeenAndMarkBestEffort(req, lockKey, CONFIG.lockWindowSeconds);
    if (lockResult.seen) {
      return ok(res, requestId, {
        action: 'ignored',
        reason: 'payment_processing_lock_active',
        payment_id: paymentIdFromPayload
      });
    }

    let result;
    try {
      result = await processFailedPayment(paymentIdFromPayload, requestId, receivedAtIso);
    } catch (processErr) {
      // Let Zoho retry on processing failures by removing cache marks where possible.
      await cacheDeleteBestEffort(req, replayResult.key);
      await cacheDeleteBestEffort(req, lockResult.key);
      throw processErr;
    }

    return ok(res, requestId, {
      action: result.action,
      result,
      verified_hmac: CONFIG.requireSignature ? true : false,
      signature_age_seconds: signatureInfo.ageSeconds,
      event_id: eventId || null
    });
  } catch (err) {
    const status = Number(err.statusCode || 500);
    logInfo({ requestId, ok: false, reason: 'unhandled_error', status, error: safeError(err) });
    return sendJson(res, status, {
      ok: false,
      request_id: requestId,
      error: CONFIG.genericPublicErrors
        ? (status >= 500 ? 'Internal webhook error.' : 'Webhook rejected.')
        : (status >= 500 ? 'Internal webhook error.' : (err.publicMessage || 'Webhook rejected.'))
    });
  }
};

// =============================================================================
// OAuth Diagnostic Route: safe read-only test of Zoho OAuth + Books access
// =============================================================================
async function handleOAuthDiagnostic(req, res, requestId) {
  if (!CONFIG.enableOAuthDiagnostic) return fail(res, requestId, 404, 'oauth_diagnostic_disabled');
  if (!CONFIG.oauthDiagnosticToken) return fail(res, requestId, 500, 'oauth_diagnostic_token_misconfigured');

  const got = getHeader(req.headers, CONFIG.oauthDiagnosticHeaderName);
  if (!safeTimingEqualText(got, CONFIG.oauthDiagnosticToken)) {
    return fail(res, requestId, 404, 'not_found');
  }

  const missing = [];
  if (!CONFIG.zohoClientId) missing.push('ZOHO_CLIENT_ID');
  if (!CONFIG.zohoClientSecret) missing.push('ZOHO_CLIENT_SECRET');
  if (!CONFIG.zohoRefreshToken) missing.push('ZOHO_REFRESH_TOKEN');
  if (missing.length) return fail(res, requestId, 500, 'missing_oauth_env', { missing });

  try {
    const accessToken = await getZohoAccessToken();
    const url = booksUrl('/organizations');
    const data = await zohoGetJson(url, accessToken);

    const organizations = Array.isArray(data.organizations) ? data.organizations : [];
    const matchedOrg = CONFIG.zohoBooksOrgId
      ? organizations.find((o) => String(o.organization_id) === String(CONFIG.zohoBooksOrgId))
      : null;

    return sendJson(res, 200, {
      ok: true,
      request_id: requestId,
      oauth_refresh_ok: true,
      books_call_status: 200,
      organization_count: organizations.length,
      expected_organization_id_present: CONFIG.zohoBooksOrgId ? Boolean(matchedOrg) : null,
      expected_organization_name: matchedOrg ? matchedOrg.name : null,
      api_domain: CONFIG.booksBaseUrl,
      dry_run: CONFIG.dryRun,
      registration_only: CONFIG.registrationOnly
    });
  } catch (err) {
    logInfo({ requestId, ok: false, reason: 'oauth_diagnostic_failed', error: safeError(err) });
    return sendJson(res, Number(err.statusCode || 502), {
      ok: false,
      request_id: requestId,
      oauth_refresh_ok: false,
      error: String(err.publicMessage || err.message || err)
    });
  }
}

// =============================================================================
// Admin Route: process a known Zoho Payments payment_id manually
// =============================================================================
async function handleAdminProcessPayment(req, res, requestId, receivedAtIso) {
  if (!CONFIG.enableAdminProcessPayment) return fail(res, requestId, 404, 'admin_route_disabled');
  if (!CONFIG.adminHeaderValue) return fail(res, requestId, 500, 'admin_header_misconfigured');

  const got = getHeader(req.headers, CONFIG.adminHeaderName);
  if (!safeTimingEqualText(got, CONFIG.adminHeaderValue)) return fail(res, requestId, 401, 'admin_header_invalid');

  const rawBody = await readRawBodyLimited(req, CONFIG.maxBodyBytes, CONFIG.inboundBodyTimeoutMs);
  const rawBodyString = decodeUtf8Strict(rawBody);
  let body;
  try { body = JSON.parse(rawBodyString || '{}'); }
  catch (_) { return fail(res, requestId, 400, 'json_parse_failed'); }

  const paymentId = firstNonEmpty(body.payment_id, body.paymentId);
  if (!paymentId) return fail(res, requestId, 400, 'payment_id_required');

  validateStaticConfigForProcessing();
  const result = await processFailedPayment(paymentId, requestId, receivedAtIso);
  return ok(res, requestId, { action: result.action, result, admin: true });
}


// =============================================================================
// Mock Route: simulate a failed payment against a real Books invoice
// =============================================================================
async function handleMockProcessFailedPayment(req, res, requestId, receivedAtIso) {
  if (!CONFIG.enableMockProcessing) return fail(res, requestId, 404, 'mock_processing_disabled');
  if (!CONFIG.mockProcessingToken) return fail(res, requestId, 500, 'mock_processing_token_misconfigured');

  const got = getHeader(req.headers, CONFIG.mockProcessingHeaderName);
  if (!safeTimingEqualText(got, CONFIG.mockProcessingToken)) return fail(res, requestId, 404, 'not_found');

  const contentTypeRaw = String(req.headers['content-type'] || '');
  if (CONFIG.requireJson && !isAllowedJsonContentType(contentTypeRaw)) {
    return fail(res, requestId, 415, 'bad_content_type', { contentType: contentTypeRaw });
  }

  const rawBody = await readRawBodyLimited(req, CONFIG.maxBodyBytes, CONFIG.inboundBodyTimeoutMs);
  const rawBodyString = decodeUtf8Strict(rawBody);

  let body;
  try { body = JSON.parse(rawBodyString || '{}'); }
  catch (_) { return fail(res, requestId, 400, 'json_parse_failed'); }

  if (!CONFIG.dryRun) {
    return fail(res, requestId, 409, 'mock_processing_requires_dry_run_true');
  }

  const invoiceId = firstNonEmpty(body.invoice_id, body.invoiceId, body.source_invoice_id, body.sourceInvoiceId);
  const invoiceNumber = firstNonEmpty(body.invoice_number, body.invoiceNumber, body.source_invoice_number, body.sourceInvoiceNumber);
  if (!invoiceId && !invoiceNumber) {
    return fail(res, requestId, 400, 'invoice_id_or_invoice_number_required');
  }

  validateStaticConfigForMockProcessing();

  const mockPaymentId = sanitizeMockPaymentId(firstNonEmpty(body.payment_id, body.paymentId, `mock_${Date.now()}`));
  const mockPayment = {
    payment_id: mockPaymentId,
    status: 'failed',
    failure_reason: firstNonEmpty(body.failure_reason, body.failureReason, 'Mock returned-payment failure'),
    payment_method_type: firstNonEmpty(body.payment_method, body.paymentMethod, 'ach'),
    amount: firstNonEmpty(body.amount, '')
  };

  const invoiceRef = {
    invoiceId: invoiceId ? String(invoiceId).trim() : '',
    invoiceNumber: invoiceNumber ? String(invoiceNumber).trim() : '',
    candidates: {
      invoice_ids: invoiceId ? [String(invoiceId).trim()] : [],
      invoice_numbers: invoiceNumber ? [String(invoiceNumber).trim()] : []
    }
  };

  const result = await processMockFailedPayment(invoiceRef, mockPayment, requestId, receivedAtIso);
  return ok(res, requestId, { action: result.action, result, mock: true });
}

async function processMockFailedPayment(invoiceRef, payment, requestId, receivedAtIso) {
  validateStaticConfigForMockProcessing();

  const accessToken = await getZohoAccessToken();
  const sourceInvoice = await resolveBooksInvoice(invoiceRef, accessToken);

  if (!sourceInvoice || !sourceInvoice.invoice_id) {
    return {
      action: 'needs_review',
      reason: 'books_invoice_not_found',
      payment_id: payment.payment_id,
      invoice_number: invoiceRef.invoiceNumber || null,
      invoice_id: invoiceRef.invoiceId || null
    };
  }

  if (isRfOrLfInvoice(sourceInvoice)) {
    return {
      action: 'ignored',
      reason: 'source_invoice_is_fee_invoice',
      payment_id: payment.payment_id,
      source_invoice_id: sourceInvoice.invoice_id,
      source_invoice_number: sourceInvoice.invoice_number || null
    };
  }

  const attemptToken = `MOCK_ZPAY_${payment.payment_id}`;
  const existingLedger = getCustomFieldValue(sourceInvoice, CONFIG.returnedFeeLedgerFieldApiName);
  if (containsLedgerToken(existingLedger, attemptToken)) {
    return {
      action: 'ignored',
      reason: 'attempt_already_recorded_on_source_invoice',
      payment_id: payment.payment_id,
      source_invoice_id: sourceInvoice.invoice_id,
      source_invoice_number: sourceInvoice.invoice_number || null
    };
  }

  const duplicate = await findDuplicateReturnedFeeInvoice(sourceInvoice, payment, attemptToken, accessToken);
  if (duplicate && duplicate.invoice_id) {
    return {
      action: 'ignored',
      reason: 'duplicate_returned_fee_invoice_exists',
      payment_id: payment.payment_id,
      existing_returned_fee_invoice_id: duplicate.invoice_id,
      existing_returned_fee_invoice_number: duplicate.invoice_number || null
    };
  }

  return {
    action: 'mock_dry_run_would_create_returned_fee_invoice',
    payment_id: payment.payment_id,
    source_invoice_id: sourceInvoice.invoice_id,
    source_invoice_number: sourceInvoice.invoice_number || null,
    customer_id: sourceInvoice.customer_id || null,
    fee_amount: CONFIG.returnedFeeAmount,
    returned_fee_item_id: CONFIG.returnedFeeItemId,
    attempt_token: attemptToken,
    failure_reason: extractFailureReason(payment) || null,
    payment_method: extractPaymentMethodType(payment) || null,
    dry_run: true,
    note: 'Mock route bypassed Zoho Payments retrieval and did not create or update any Zoho Books record.'
  };
}

// =============================================================================
// Core Processing
// =============================================================================
async function processFailedPayment(paymentId, requestId, receivedAtIso) {
  validateStaticConfigForProcessing();

  const accessToken = await getZohoAccessToken();
  const payment = await retrieveZohoPayment(paymentId, accessToken);

  if (normalizeText(payment.status) !== 'failed') {
    return {
      action: 'ignored',
      reason: 'payment_not_failed_after_api_verification',
      payment_id: paymentId,
      status: payment.status || null
    };
  }

  if (CONFIG.skipCustomerCanceledOrAbandoned && isCustomerCanceledOrAbandoned(payment)) {
    return {
      action: 'ignored',
      reason: 'customer_canceled_or_abandoned_or_non_chargeable_failure',
      payment_id: paymentId,
      failure_reason: extractFailureReason(payment) || null
    };
  }

  const paymentSessionId = firstNonEmpty(payment.payments_session_id, deepFindFirst(payment, ['payments_session_id']));
  let paymentSession = null;
  if (paymentSessionId) {
    paymentSession = await safeRetrievePaymentSession(paymentSessionId, accessToken);
    if (CONFIG.deferIfPaymentSessionActive && paymentSession && isPaymentSessionStillActive(paymentSession)) {
      return {
        action: 'deferred',
        reason: 'payment_session_still_active',
        payment_id: paymentId,
        payments_session_id: paymentSessionId
      };
    }
  }

  const invoiceRef = extractInvoiceReference(payment, paymentSession);
  if (!invoiceRef.invoiceNumber && !invoiceRef.invoiceId) {
    return {
      action: 'needs_review',
      reason: 'unable_to_resolve_books_invoice_from_payment',
      payment_id: paymentId,
      invoice_reference_candidates: invoiceRef.candidates
    };
  }

  const sourceInvoice = await resolveBooksInvoice(invoiceRef, accessToken);
  if (!sourceInvoice || !sourceInvoice.invoice_id) {
    return {
      action: 'needs_review',
      reason: 'books_invoice_not_found',
      payment_id: paymentId,
      invoice_number: invoiceRef.invoiceNumber || null,
      invoice_id: invoiceRef.invoiceId || null
    };
  }

  if (isRfOrLfInvoice(sourceInvoice)) {
    return {
      action: 'ignored',
      reason: 'source_invoice_is_fee_invoice',
      payment_id: paymentId,
      source_invoice_id: sourceInvoice.invoice_id,
      source_invoice_number: sourceInvoice.invoice_number || null
    };
  }

  const attemptToken = `ZPAY_${paymentId}`;
  const existingLedger = getCustomFieldValue(sourceInvoice, CONFIG.returnedFeeLedgerFieldApiName);
  if (containsLedgerToken(existingLedger, attemptToken)) {
    return {
      action: 'ignored',
      reason: 'attempt_already_recorded_on_source_invoice',
      payment_id: paymentId,
      source_invoice_id: sourceInvoice.invoice_id,
      source_invoice_number: sourceInvoice.invoice_number || null
    };
  }

  const duplicate = await findDuplicateReturnedFeeInvoice(sourceInvoice, payment, attemptToken, accessToken);
  if (duplicate && duplicate.invoice_id) {
    await appendLedgerToken(sourceInvoice, attemptToken, duplicate.invoice_id, duplicate.invoice_number || '', accessToken, receivedAtIso);
    return {
      action: 'ignored',
      reason: 'duplicate_returned_fee_invoice_exists',
      payment_id: paymentId,
      existing_returned_fee_invoice_id: duplicate.invoice_id,
      existing_returned_fee_invoice_number: duplicate.invoice_number || null
    };
  }

  if (CONFIG.dryRun) {
    return {
      action: 'dry_run_would_create_returned_fee_invoice',
      payment_id: paymentId,
      source_invoice_id: sourceInvoice.invoice_id,
      source_invoice_number: sourceInvoice.invoice_number || null,
      customer_id: sourceInvoice.customer_id || null,
      fee_amount: CONFIG.returnedFeeAmount,
      attempt_token: attemptToken,
      failure_reason: extractFailureReason(payment) || null,
      payment_method: extractPaymentMethodType(payment) || null
    };
  }

  const rfInvoice = await createReturnedFeeInvoice(sourceInvoice, payment, attemptToken, accessToken, receivedAtIso);
  await appendLedgerToken(sourceInvoice, attemptToken, rfInvoice.invoice_id, rfInvoice.invoice_number || '', accessToken, receivedAtIso);

  const emailResult = CONFIG.sendInvoiceOnCreate
    ? await sendReturnedFeeInvoiceEmail(rfInvoice, sourceInvoice, accessToken)
    : { sent: false, reason: 'SEND_INVOICE_ON_CREATE=false' };

  return {
    action: 'created_returned_fee_invoice',
    payment_id: paymentId,
    source_invoice_id: sourceInvoice.invoice_id,
    source_invoice_number: sourceInvoice.invoice_number || null,
    returned_fee_invoice_id: rfInvoice.invoice_id,
    returned_fee_invoice_number: rfInvoice.invoice_number || null,
    sent_on_create: Boolean(emailResult.sent),
    email_send_result: emailResult
  };
}

// =============================================================================
// Zoho API: OAuth + HTTP helpers
// =============================================================================
async function getZohoAccessToken() {
  const now = Date.now();
  if (tokenCache.accessToken && now < tokenCache.expiresAtMs - 60000) return tokenCache.accessToken;

  const accountsOrigin = new URL(validateUrlHostSuffix(CONFIG.accountsBaseUrl, CONFIG.accountsAllowedHostSuffixes)).origin;
  const tokenUrl = `${accountsOrigin}/oauth/v2/token`;

  const body = new URLSearchParams({
    refresh_token: CONFIG.zohoRefreshToken,
    client_id: CONFIG.zohoClientId,
    client_secret: CONFIG.zohoClientSecret,
    grant_type: 'refresh_token'
  }).toString();

  const resp = await httpsRequest({ method: 'POST', url: tokenUrl, body, headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
  if (resp.status < 200 || resp.status >= 300) {
    throw publicError(502, 'Zoho OAuth refresh failed.', { status: resp.status, body: safeTruncate(resp.body, 600) });
  }

  let parsed;
  try { parsed = JSON.parse(resp.body || '{}'); }
  catch (_) { throw publicError(502, 'Zoho OAuth refresh returned invalid JSON.'); }

  if (!parsed.access_token) throw publicError(502, 'Zoho OAuth refresh did not return access_token.');

  tokenCache.accessToken = parsed.access_token;
  tokenCache.expiresAtMs = Date.now() + Number(parsed.expires_in || 3600) * 1000;
  return tokenCache.accessToken;
}

async function retrieveZohoPayment(paymentId, accessToken) {
  const url = apiUrl(CONFIG.paymentsBaseUrl, CONFIG.paymentsAllowedHostSuffixes, `/api/v1/payments/${encodeURIComponent(paymentId)}`, {
    account_id: CONFIG.zohoPaymentsAccountId
  });
  const data = await zohoGetJson(url, accessToken);
  const payment = data.payment || data.data?.payment || data.data || null;
  if (!payment || typeof payment !== 'object') throw publicError(502, 'Zoho Payments did not return a payment object.');
  return payment;
}

async function safeRetrievePaymentSession(paymentSessionId, accessToken) {
  try {
    const url = apiUrl(CONFIG.paymentsBaseUrl, CONFIG.paymentsAllowedHostSuffixes, `/api/v1/paymentsessions/${encodeURIComponent(paymentSessionId)}`, {
      account_id: CONFIG.zohoPaymentsAccountId
    });
    const data = await zohoGetJson(url, accessToken);
    return data.payments_session || data.payment_session || data.data?.payments_session || null;
  } catch (err) {
    logInfo({ event: 'payment_session_lookup_failed', paymentSessionId, error: safeError(err) });
    return null;
  }
}

async function resolveBooksInvoice(invoiceRef, accessToken) {
  if (invoiceRef.invoiceId) {
    const inv = await retrieveBooksInvoice(invoiceRef.invoiceId, accessToken);
    if (inv) return inv;
  }
  if (invoiceRef.invoiceNumber) {
    const inv = await findBooksInvoiceByNumber(invoiceRef.invoiceNumber, accessToken);
    if (inv) return inv;
  }
  return null;
}

async function retrieveBooksInvoice(invoiceId, accessToken) {
  const url = booksUrl(`/invoices/${encodeURIComponent(invoiceId)}`, { organization_id: CONFIG.zohoBooksOrgId });
  const data = await zohoGetJson(url, accessToken);
  return data.invoice || null;
}

async function findBooksInvoiceByNumber(invoiceNumber, accessToken) {
  const exactUrl = booksUrl('/invoices', {
    organization_id: CONFIG.zohoBooksOrgId,
    filter_by: 'Status.All',
    invoice_number: invoiceNumber
  });
  const exact = await zohoGetJson(exactUrl, accessToken);
  const exactMatch = (exact.invoices || []).find((inv) => normalizeText(inv.invoice_number) === normalizeText(invoiceNumber));
  if (exactMatch) return retrieveBooksInvoice(exactMatch.invoice_id, accessToken);

  const searchUrl = booksUrl('/invoices', {
    organization_id: CONFIG.zohoBooksOrgId,
    filter_by: 'Status.All',
    search_text: invoiceNumber
  });
  const searched = await zohoGetJson(searchUrl, accessToken);
  const searchMatch = (searched.invoices || []).find((inv) => normalizeText(inv.invoice_number) === normalizeText(invoiceNumber));
  if (searchMatch) return retrieveBooksInvoice(searchMatch.invoice_id, accessToken);

  return null;
}

async function findDuplicateReturnedFeeInvoice(sourceInvoice, payment, attemptToken, accessToken) {
  const terms = [attemptToken, payment.payment_id, sourceInvoice.invoice_number].filter(Boolean).slice(0, 3);
  for (const term of terms) {
    const url = booksUrl('/invoices', {
      organization_id: CONFIG.zohoBooksOrgId,
      filter_by: 'Status.All',
      search_text: term
    });
    const data = await zohoGetJson(url, accessToken);
    const invoices = data.invoices || [];
    const found = invoices.find((inv) => {
      const num = String(inv.invoice_number || '');
      const hay = JSON.stringify(inv).toLowerCase();
      return num.startsWith(`${CONFIG.returnedFeeInvoicePrefix}-`) &&
        (hay.includes(attemptToken.toLowerCase()) || hay.includes(String(payment.payment_id || '').toLowerCase()) || hay.includes(String(sourceInvoice.invoice_number || '').toLowerCase()));
    });
    if (found) return found;
  }
  return null;
}

async function createReturnedFeeInvoice(sourceInvoice, payment, attemptToken, accessToken, receivedAtIso) {
  if (!sourceInvoice.customer_id) throw publicError(500, 'Source invoice missing customer_id.');
  if (!CONFIG.returnedFeeItemId) throw publicError(500, 'RETURNED_FEE_ITEM_ID is required.');

  const today = new Date().toISOString().slice(0, 10);
  const sourceNumber = sanitizeInvoiceNumber(sourceInvoice.invoice_number || sourceInvoice.invoice_id);
  const paymentTail = String(payment.payment_id || '').slice(-8);
  const rfInvoiceNumber = `${CONFIG.returnedFeeInvoicePrefix}-${sourceNumber}-${paymentTail}`.slice(0, 100);
  const paymentMethod = extractPaymentMethodType(payment) || 'unknown';
  const failureReason = extractFailureReason(payment) || 'N/A';

  const notes = [
    'Returned Payment Fee',
    `Source Invoice: ${sourceInvoice.invoice_number || sourceInvoice.invoice_id}`,
    `Source Invoice ID: ${sourceInvoice.invoice_id}`,
    `Zoho Payments Payment ID: ${payment.payment_id}`,
    `Payment Session ID: ${payment.payments_session_id || 'N/A'}`,
    `Payment Method: ${paymentMethod}`,
    `Failure Reason: ${failureReason}`,
    `Idempotency Token: ${attemptToken}`,
    `Processed At: ${receivedAtIso}`
  ].join('\n');

  const invoiceBody = {
    customer_id: sourceInvoice.customer_id,
    invoice_number: rfInvoiceNumber,
    date: today,
    due_date: today,
    reference_number: attemptToken,
    line_items: [
      {
        item_id: CONFIG.returnedFeeItemId,
        rate: CONFIG.returnedFeeAmount,
        quantity: 1,
        description: `Returned payment fee for failed payment on invoice ${sourceInvoice.invoice_number || sourceInvoice.invoice_id}. Payment ID: ${payment.payment_id}.`
      }
    ],
    notes,
    terms: 'Due upon receipt.'
  };

  if (typeof sourceInvoice.allow_partial_payments === 'boolean') {
    invoiceBody.allow_partial_payments = sourceInvoice.allow_partial_payments;
  }

  const contactPersonIds = extractInvoiceContactPersonIds(sourceInvoice);
  if (contactPersonIds.length > 0) {
    invoiceBody.contact_persons = contactPersonIds;
  }

  const gateways = buildBooksPaymentGateways();
  if (CONFIG.booksPaymentOptionsEnabled && gateways.length > 0) {
    invoiceBody.payment_options = { payment_gateways: gateways };
  }

  // Do not rely on the create-invoice `send` flag alone. Zoho Books can create
  // the invoice successfully while not delivering email if contact persons are
  // missing or not associated. We create first, record the idempotency ledger,
  // then explicitly call the invoice email endpoint.
  const url = booksUrl('/invoices', {
    organization_id: CONFIG.zohoBooksOrgId,
    ignore_auto_number_generation: 'true'
  });

  const data = await zohoRequestJson('POST', url, invoiceBody, accessToken);
  const invoice = data.invoice || null;
  if (!invoice || !invoice.invoice_id) throw publicError(502, 'Zoho Books did not return created RF invoice.');
  return invoice;
}


async function sendReturnedFeeInvoiceEmail(rfInvoice, sourceInvoice, accessToken) {
  if (!rfInvoice || !rfInvoice.invoice_id) {
    return { sent: false, reason: 'missing_returned_fee_invoice_id' };
  }

  const toMailIds = extractInvoiceRecipientEmails(rfInvoice, sourceInvoice);
  if (toMailIds.length === 0) {
    return {
      sent: false,
      reason: 'no_recipient_email_found',
      invoice_id: rfInvoice.invoice_id,
      invoice_number: rfInvoice.invoice_number || null
    };
  }

  const emailBody = {
    to_mail_ids: toMailIds,
    send_from_org_email_id: true
  };

  const url = booksUrl(`/invoices/${encodeURIComponent(rfInvoice.invoice_id)}/email`, {
    organization_id: CONFIG.zohoBooksOrgId
  });

  try {
    const data = await zohoRequestJson('POST', url, emailBody, accessToken);
    const okCode = Number(data.code) === 0 || normalizeText(data.message) === 'success';
    return {
      sent: okCode,
      reason: okCode ? 'email_endpoint_success' : 'email_endpoint_nonzero_response',
      invoice_id: rfInvoice.invoice_id,
      invoice_number: rfInvoice.invoice_number || null,
      to_mail_ids: toMailIds,
      zoho_code: data.code,
      zoho_message: data.message || null
    };
  } catch (e) {
    const safe = safeError(e);
    return {
      sent: false,
      reason: 'email_endpoint_error',
      invoice_id: rfInvoice.invoice_id,
      invoice_number: rfInvoice.invoice_number || null,
      to_mail_ids: toMailIds,
      error: safe.message || String(e)
    };
  }
}

async function appendLedgerToken(sourceInvoice, attemptToken, rfInvoiceId, rfInvoiceNumber, accessToken, receivedAtIso) {
  const current = String(getCustomFieldValue(sourceInvoice, CONFIG.returnedFeeLedgerFieldApiName) || '').trim();
  if (containsLedgerToken(current, attemptToken)) return;

  const compactTimestamp = receivedAtIso.replace('T', ' ').replace('Z', ' UTC');
  const newLine = `${attemptToken}|${rfInvoiceNumber || rfInvoiceId}|${compactTimestamp}`;
  let nextLedger = current ? `${current}\n${newLine}` : newLine;

  if (nextLedger.length > CONFIG.maxLedgerLength) {
    const lines = nextLedger.split(/\r?\n/).filter(Boolean);
    while (lines.join('\n').length > CONFIG.maxLedgerLength && lines.length > 1) lines.shift();
    nextLedger = lines.join('\n');
  }

  let nextCustomFields = mergeCustomField(sourceInvoice.custom_fields || [], CONFIG.returnedFeeLedgerFieldApiName, nextLedger);

  if (CONFIG.updateOptionalLatestRfInvoiceField && CONFIG.optionalLatestRfInvoiceFieldApiName) {
    nextCustomFields = mergeCustomField(nextCustomFields, CONFIG.optionalLatestRfInvoiceFieldApiName, rfInvoiceNumber || rfInvoiceId || '');
  }

  const url = booksUrl(`/invoices/${encodeURIComponent(sourceInvoice.invoice_id)}`, { organization_id: CONFIG.zohoBooksOrgId });
  await zohoRequestJson('PUT', url, { custom_fields: nextCustomFields }, accessToken);
}

async function zohoGetJson(url, accessToken) {
  return zohoRequestJson('GET', url, null, accessToken);
}

async function zohoRequestJson(method, url, bodyObj, accessToken) {
  const body = bodyObj ? JSON.stringify(bodyObj) : '';
  const resp = await httpsRequest({
    method,
    url,
    body,
    headers: {
      Authorization: `Zoho-oauthtoken ${accessToken}`,
      ...(body ? { 'Content-Type': 'application/json' } : {})
    }
  });

  if (resp.status < 200 || resp.status >= 300) {
    throw publicError(502, `Zoho API HTTP ${resp.status}.`, {
      status: resp.status,
      body: CONFIG.debugSafeZohoBodies ? safeTruncate(resp.body, 1200) : undefined
    });
  }

  try { return JSON.parse(resp.body || '{}'); }
  catch (_) { throw publicError(502, 'Zoho API returned invalid JSON.'); }
}

function httpsRequest({ method, url, body = '', headers = {} }) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const requestHeaders = { ...headers };
    if (body) requestHeaders['Content-Length'] = Buffer.byteLength(body);

    const req = https.request({
      method,
      hostname: u.hostname,
      path: u.pathname + u.search,
      headers: requestHeaders,
      timeout: CONFIG.outboundTimeoutMs
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve({ status: res.statusCode || 0, headers: res.headers, body: data }));
    });

    req.on('timeout', () => req.destroy(new Error('outbound_timeout')));
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

// =============================================================================
// Signature Verification + Inbound Hardening
// =============================================================================
function verifyZohoPaymentsWebhookSignature(req, rawBodyString) {
  const header = getHeader(req.headers, 'x-zoho-webhook-signature');
  if (!header) throw publicError(401, 'Missing X-Zoho-Webhook-Signature header.');

  const parsed = parseZohoSignatureHeader(header);
  if (!parsed.timestamp || !parsed.signature) throw publicError(401, 'Invalid X-Zoho-Webhook-Signature header.');

  const timestampNum = Number(parsed.timestamp);
  if (!Number.isFinite(timestampNum) || timestampNum <= 0) throw publicError(401, 'Invalid webhook signature timestamp.');

  // Zoho Payments webhook signatures use millisecond timestamps in the `t` value.
  // Accept seconds defensively, but preserve the original `t` string for HMAC input.
  const timestampMs = timestampNum > 100000000000 ? timestampNum : timestampNum * 1000;
  const ageSeconds = Math.abs(Date.now() - timestampMs) / 1000;
  if (CONFIG.signatureToleranceSeconds > 0 && ageSeconds > CONFIG.signatureToleranceSeconds) {
    throw publicError(401, 'Webhook signature timestamp outside tolerance.');
  }

  const signedPayload = `${parsed.timestamp}.${rawBodyString}`;
  const secrets = [CONFIG.webhookSigningKey, CONFIG.webhookSigningKeyPrevious].filter(Boolean);
  if (!secrets.length) throw publicError(500, 'Missing Zoho Payments webhook signing key.');

  for (const secret of secrets) {
    const expectedHex = crypto.createHmac('sha256', secret).update(signedPayload, 'utf8').digest('hex');
    if (safeTimingEqualHex(expectedHex, parsed.signature)) {
      return {
        verified: true,
        encoding: 'hex',
        timestamp: timestampNum,
        ageSeconds,
        signature: parsed.signature,
        replayKeyMaterial: `${parsed.timestamp}:${parsed.signature}`
      };
    }

    const expectedBase64 = crypto.createHmac('sha256', secret).update(signedPayload, 'utf8').digest('base64');
    if (safeTimingEqualBase64(expectedBase64, parsed.signature)) {
      return {
        verified: true,
        encoding: 'base64',
        timestamp: timestampNum,
        ageSeconds,
        signature: parsed.signature,
        replayKeyMaterial: `${parsed.timestamp}:${parsed.signature}`
      };
    }
  }

  throw publicError(401, 'Webhook signature verification failed.');
}

function parseZohoSignatureHeader(headerValue) {
  const out = { timestamp: '', signature: '' };
  const raw = String(headerValue || '').trim();
  if (!raw) return out;

  for (const part of raw.split(',')) {
    const idx = part.indexOf('=');
    if (idx === -1) continue;
    const k = part.slice(0, idx).trim().toLowerCase();
    const v = part.slice(idx + 1).trim();
    if (k === 't') out.timestamp = v;
    if (k === 'v') out.signature = v.replace(/^sha256=/i, '').replace(/\s+/g, '');
  }
  return out;
}

function isAllowedJsonContentType(ctRaw) {
  const s = String(ctRaw || '').trim().toLowerCase();
  if (!s || s.includes('\r') || s.includes('\n') || s.includes(',')) return false;
  if (!s.startsWith('application/json')) return false;
  let rest = s.slice('application/json'.length).trim();
  if (!rest) return true;
  if (rest.startsWith(';')) rest = rest.slice(1).trim();
  if (!rest.startsWith('charset=')) return false;
  return rest.slice('charset='.length).trim() === 'utf-8';
}

function readRawBodyLimited(req, maxBytes, timeoutMs) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let total = 0;
    let done = false;

    const timer = setTimeout(() => {
      if (done) return;
      done = true;
      try { req.destroy(new Error('inbound_timeout')); } catch (_) {}
      reject(publicError(400, 'Inbound body read timeout.'));
    }, timeoutMs);

    function finish(err, buffer) {
      if (done) return;
      done = true;
      clearTimeout(timer);
      if (err) return reject(err);
      resolve(buffer);
    }

    req.on('aborted', () => finish(publicError(400, 'Client aborted request.')));
    req.on('error', (err) => finish(err));
    req.on('data', (chunk) => {
      total += chunk.length;
      if (total > maxBytes) {
        try { req.destroy(); } catch (_) {}
        return finish(publicError(413, 'Payload too large.'));
      }
      chunks.push(chunk);
    });
    req.on('end', () => finish(null, Buffer.concat(chunks)));
  });
}

function decodeUtf8Strict(buf) {
  const TD = typeof global.TextDecoder === 'function' ? global.TextDecoder : UtilTextDecoder;
  return new TD('utf-8', { fatal: true }).decode(buf);
}

function getDeclaredContentLength(req) {
  const h = req.headers['content-length'];
  if (!h) return null;
  const n = Number(h);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

function validateAllowedPath(path) {
  const normalized = normalizePath(path);
  const allowed = CONFIG.allowedPaths.map(normalizePath);

  // Catalyst can surface the routed path as `/` in some Advanced I/O/API Gateway contexts.
  // If there is exactly one configured webhook path, allow `/` as an alias for that route.
  const rootAliasAllowed = normalized === '/' && allowed.length === 1 && allowed[0] !== '/';

  return { ok: allowed.includes(normalized) || rootAliasAllowed, path: rootAliasAllowed ? allowed[0] : normalized };
}

function getRequestPath(req) {
  try { return normalizePath(new URL(req.url || '/', 'https://example.com').pathname); }
  catch (_) { return '/'; }
}

function normalizePath(path) {
  let p = String(path || '').trim();
  if (!p) p = '/';
  if (!p.startsWith('/')) p = `/${p}`;
  if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1);
  return p;
}

// =============================================================================
// Catalyst Cache Replay/Lock Helpers
// =============================================================================
async function replaySeenAndMarkBestEffort(req, key, ttlSeconds) {
  if (!CONFIG.enableReplayDefense) return { seen: false, key, disabled: true };
  try {
    const app = catalystSdk.initialize(req);
    const segment = getCacheSegment(app);
    const now = Date.now();
    const existing = await segment.getValue(key).catch(() => null);
    if (existing) {
      const firstSeenMs = Number(String(existing).trim());
      const ageMs = Number.isFinite(firstSeenMs) ? now - firstSeenMs : 0;
      if (ageMs >= 0 && ageMs <= Math.max(1, ttlSeconds) * 1000) {
        return { seen: true, key, ageMs };
      }
    }
    await segment.put(key, String(now), secondsToCacheHoursInteger(ttlSeconds));
    return { seen: false, key, marked: true };
  } catch (err) {
    logInfo({ event: 'cache_replay_defense_error', key, error: safeError(err) });
    if (CONFIG.strictReplayFailure) throw publicError(503, 'Replay defense unavailable.');
    return { seen: false, key, cacheError: true };
  }
}

async function cacheDeleteBestEffort(req, key) {
  if (!key) return;
  try {
    const app = catalystSdk.initialize(req);
    const segment = getCacheSegment(app);
    if (typeof segment.deleteValue === 'function') await segment.deleteValue(key);
    else if (typeof segment.delete === 'function') await segment.delete(key);
    else if (typeof segment.remove === 'function') await segment.remove(key);
  } catch (_) {}
}

function getCacheSegment(app) {
  const cache = app.cache();
  if (CONFIG.replayCacheSegmentId) return cache.segment(CONFIG.replayCacheSegmentId);
  return cache.segment();
}

function makeCacheKey(prefix, material) {
  const digest = crypto.createHash('sha256').update(String(material || '')).digest('base64url');
  let key = `${prefix}${digest}`;
  if (key.length <= CACHE_KEY_MAX_LEN) return key;
  const p = String(prefix || '').slice(0, 5);
  return `${p}${digest}`.slice(0, CACHE_KEY_MAX_LEN);
}

function secondsToCacheHoursInteger(seconds) {
  const h = Math.ceil(Math.max(1, Number(seconds || 1)) / 3600);
  return Math.max(1, Math.min(48, h));
}

// =============================================================================
// Extraction + Business Rules
// =============================================================================
function extractEventInfo(payload) {
  const eventType = firstNonEmpty(
    payload.event_type,
    payload.event,
    payload.type,
    payload.notification_type,
    payload.data?.event_type,
    payload.data?.event,
    payload.data?.type,
    deepFindFirst(payload, ['event_type', 'event', 'type'])
  );

  const eventId = firstNonEmpty(
    payload.event_id,
    payload.eventId,
    payload.id,
    payload.notification_id,
    payload.data?.event_id,
    payload.data?.id,
    deepFindFirst(payload, ['event_id', 'eventId', 'notification_id'])
  );

  const paymentId = firstNonEmpty(
    payload.payment_id,
    payload.payment?.payment_id,
    payload.data?.payment_id,
    payload.data?.payment?.payment_id,
    payload.payload?.payment_id,
    deepFindFirst(payload, ['payment_id'])
  );

  return { eventType, eventId, paymentId };
}

function extractInvoiceReference(payment, session) {
  const paymentMeta = metadataToMap(payment.meta_data || payment.metadata || []);
  const sessionMeta = metadataToMap(session?.meta_data || session?.metadata || []);

  const searchableText = [
    payment.description,
    payment.statement_descriptor,
    payment.reference_number,
    session?.description,
    session?.reference_number,
    JSON.stringify(payment.meta_data || payment.metadata || []),
    JSON.stringify(session?.meta_data || session?.metadata || [])
  ].filter((v) => isUsefulZohoValue(v)).join(' ');

  const parsedFromText = parseInvoiceNumberFromText(searchableText);

  const invoiceIdCandidates = compactUsefulValues([
    payment.books_invoice_id,
    payment.invoice_id,
    payment.source_invoice_id,
    paymentMeta.books_invoice_id,
    paymentMeta.invoice_id,
    paymentMeta.source_invoice_id,
    session?.books_invoice_id,
    session?.invoice_id,
    sessionMeta.books_invoice_id,
    sessionMeta.invoice_id,
    sessionMeta.source_invoice_id
  ]);

  // Zoho Payments can return invoice_number as the literal string "null" on failed payments,
  // while the real Books invoice number is still present in description text such as:
  // "Zoho :: GH Real Estate :: INV-000142". Filter null-like values and prioritize parsed invoice numbers.
  const invoiceNumberCandidates = compactUsefulValues([
    parsedFromText,
    payment.invoice_number,
    payment.books_invoice_number,
    payment.source_invoice_number,
    payment.reference_number,
    paymentMeta.invoice_number,
    paymentMeta.books_invoice_number,
    paymentMeta.source_invoice_number,
    session?.invoice_number,
    session?.reference_number,
    sessionMeta.invoice_number,
    sessionMeta.books_invoice_number,
    sessionMeta.source_invoice_number
  ]).map(normalizeInvoiceNumberCandidate);

  return {
    invoiceId: invoiceIdCandidates[0] || '',
    invoiceNumber: invoiceNumberCandidates[0] || '',
    candidates: {
      invoice_ids: uniqueNonEmpty(invoiceIdCandidates).slice(0, 5),
      invoice_numbers: uniqueNonEmpty(invoiceNumberCandidates).slice(0, 5)
    }
  };
}

function parseInvoiceNumberFromText(text) {
  const patterns = [
    /\b(INV[-_ ]?\d{3,})\b/i,
    /\b(INVOICE[-_ ]?\d{3,})\b/i,
    /\b([A-Z]{1,10}[-_]\d{3,})\b/i
  ];
  for (const pattern of patterns) {
    const m = String(text || '').match(pattern);
    if (m && m[1]) return normalizeInvoiceNumberCandidate(m[1]);
  }
  return '';
}

function isUsefulZohoValue(value) {
  if (value === null || value === undefined) return false;
  const s = String(value).trim();
  if (!s) return false;
  const n = s.toLowerCase();
  return !['null', 'undefined', 'none', 'n/a', 'na', '-', '--'].includes(n);
}

function compactUsefulValues(values) {
  return values
    .filter((v) => isUsefulZohoValue(v))
    .map((v) => String(v).trim())
    .filter(Boolean);
}

function normalizeInvoiceNumberCandidate(value) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/_/g, '-')
    .toUpperCase();
}

function uniqueNonEmpty(values) {
  const out = [];
  const seen = new Set();
  for (const value of values || []) {
    const s = String(value || '').trim();
    if (!s) continue;
    const key = s.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(s);
  }
  return out;
}

function metadataToMap(metaData) {
  const out = {};
  if (!Array.isArray(metaData)) return out;
  for (const row of metaData) {
    if (!row || typeof row !== 'object') continue;
    const key = normalizeText(row.key || row.name || row.api_name || '');
    if (key) out[key] = firstNonEmpty(row.value, row.val, '');
  }
  return out;
}

function isCustomerCanceledOrAbandoned(payment) {
  const text = normalizeText([
    extractFailureReason(payment),
    payment.failure_code,
    payment.error_code,
    payment.code,
    payment.status_message,
    JSON.stringify(payment.error || {}),
    JSON.stringify(payment.processor_response || {})
  ].join(' '));

  return CONFIG.skipNonFinalFailureKeywords.some((kw) => text.includes(normalizeText(kw)));
}

function isPaymentSessionStillActive(session) {
  const statusText = normalizeText([
    session.status,
    session.payment_status,
    session.payment_session_status,
    session.session_status,
    JSON.stringify(session.status_detail || {})
  ].join(' '));

  if (statusText.includes('succeeded') || statusText.includes('paid') || statusText.includes('completed')) return false;
  if (statusText.includes('failed') || statusText.includes('expired') || statusText.includes('cancel')) return false;

  const expiryRaw = Number(firstNonEmpty(session.expiry_time, session.expires_at, session.expires_on, 0));
  if (!expiryRaw) return false;
  const expiryMs = expiryRaw < 10000000000 ? expiryRaw * 1000 : expiryRaw;
  return expiryMs > Date.now();
}

function extractFailureReason(payment) {
  return firstNonEmpty(
    payment.failure_reason,
    payment.failure_message,
    payment.reason,
    payment.error_message,
    payment.message,
    payment.error?.message,
    payment.processor_response?.message,
    payment.processor_response?.reason,
    ''
  );
}

function extractPaymentMethodType(payment) {
  return firstNonEmpty(
    payment.payment_method?.type,
    payment.payment_method_type,
    payment.method,
    payment.payment_method,
    payment.payment_mode,
    ''
  );
}

function isRfOrLfInvoice(invoice) {
  const num = String(invoice.invoice_number || '').toUpperCase();
  return num.startsWith(`${CONFIG.returnedFeeInvoicePrefix.toUpperCase()}-`) || num.startsWith('LF-');
}

function buildBooksPaymentGateways() {
  if (!CONFIG.booksPaymentGatewaysCsv) return [];
  return CONFIG.booksPaymentGatewaysCsv.split(',').map((name) => name.trim()).filter(Boolean).map((gateway_name) => ({ gateway_name }));
}


// =============================================================================
// Zoho Books Email Recipient Helpers
// =============================================================================
function extractInvoiceContactPersonIds(invoice) {
  const ids = [];

  const addId = (value) => {
    if (value === undefined || value === null) return;
    if (typeof value === 'string' || typeof value === 'number') {
      const text = String(value).trim();
      if (/^\d{6,}$/.test(text)) ids.push(text);
      return;
    }
    if (typeof value === 'object') {
      addId(firstNonEmpty(
        value.contact_person_id,
        value.contactperson_id,
        value.contact_persons_id,
        value.id
      ));
    }
  };

  const addArray = (value) => {
    if (Array.isArray(value)) value.forEach(addId);
    else addId(value);
  };

  addArray(invoice.contact_persons);
  addArray(invoice.contact_persons_details);
  addArray(invoice.contact_person_details);
  addArray(invoice.contact_person_id);

  return uniqueNonEmpty(ids);
}

function extractInvoiceRecipientEmails(...records) {
  const emails = [];

  const addEmail = (value) => {
    if (value === undefined || value === null) return;
    const text = String(value).trim();
    if (/^[^\s@<>"']+@[^\s@<>"']+\.[^\s@<>"']+$/.test(text)) emails.push(text);
  };

  const visit = (value, key = '', depth = 0) => {
    if (depth > 6 || value === undefined || value === null) return;

    if (Array.isArray(value)) {
      value.forEach((item) => visit(item, key, depth + 1));
      return;
    }

    if (typeof value === 'object') {
      for (const [childKey, childValue] of Object.entries(value)) {
        visit(childValue, childKey, depth + 1);
      }
      return;
    }

    const normalizedKey = normalizeText(key);
    if (
      normalizedKey === 'email' ||
      normalizedKey.endsWith('_email') ||
      normalizedKey.includes('mail_id') ||
      normalizedKey.includes('email_id')
    ) {
      addEmail(value);
    }
  };

  records.filter(Boolean).forEach((record) => visit(record));
  return uniqueNonEmpty(emails).slice(0, 10);
}

// =============================================================================
// Zoho Books Custom Field Helpers
// =============================================================================
function getCustomFieldValue(invoice, apiName) {
  const fields = invoice.custom_fields || [];
  const target = normalizeText(apiName);
  const match = fields.find((field) => {
    return normalizeText(field.api_name) === target ||
      normalizeText(field.placeholder) === target ||
      normalizeText(field.label) === target;
  });
  return match ? firstNonEmpty(match.value, match.show_value, '') : '';
}

function mergeCustomField(customFields, apiName, value) {
  const target = normalizeText(apiName);
  let found = false;

  const next = (customFields || []).map((field) => {
    const isTarget = normalizeText(field.api_name) === target || normalizeText(field.placeholder) === target || normalizeText(field.label) === target;
    if (isTarget) {
      found = true;
      return { api_name: apiName, value };
    }
    if (field.api_name) return { api_name: field.api_name, value: firstNonEmpty(field.value, '') };
    if (field.placeholder) return { api_name: field.placeholder, value: firstNonEmpty(field.value, '') };
    return field;
  });

  if (!found) next.push({ api_name: apiName, value });
  return next;
}

function containsLedgerToken(ledger, token) {
  const target = normalizeText(token);
  return String(ledger || '').split(/\r?\n/).some((line) => normalizeText(line).includes(target));
}

// =============================================================================
// URL + HTTP Utility Helpers
// =============================================================================
function apiUrl(base, allowedSuffixes, path, query = {}) {
  const baseValidated = validateUrlHostSuffix(base, allowedSuffixes);
  const baseUrl = new URL(baseValidated);

  const basePath = String(baseUrl.pathname || '').replace(/\/+$|^\/$/g, '');
  const relativePath = String(path || '').startsWith('/') ? String(path || '') : `/${String(path || '')}`;
  const fullPath = `${basePath}${relativePath}`.replace(/\/{2,}/g, '/');

  const u = new URL(`${baseUrl.origin}${fullPath}`);
  for (const [k, v] of Object.entries(query || {})) {
    if (v !== undefined && v !== null && String(v) !== '') u.searchParams.set(k, String(v));
  }
  return u.toString();
}

function booksUrl(path, query = {}) {
  return apiUrl(CONFIG.booksBaseUrl, CONFIG.booksAllowedHostSuffixes, path, query);
}

function validateUrlHostSuffix(urlString, allowedSuffixes) {
  const u = new URL(String(urlString || ''));
  if (u.protocol !== 'https:') throw new Error('url_must_be_https');
  const host = String(u.hostname || '').toLowerCase();
  const ok = allowedSuffixes.some((suffix) => host === suffix || host.endsWith(`.${suffix}`));
  if (!ok) throw new Error(`host_not_allowed:${host}`);
  return u.toString();
}

// =============================================================================
// Config Validation
// =============================================================================
function validateStaticConfigForMockProcessing() {
  const missing = [];
  for (const key of [
    'zohoClientId',
    'zohoClientSecret',
    'zohoRefreshToken',
    'zohoBooksOrgId',
    'returnedFeeItemId'
  ]) {
    if (!CONFIG[key]) missing.push(key);
  }
  if (CONFIG.returnedFeeAmount <= 0) missing.push('returnedFeeAmount_positive_number');
  if (missing.length) throw publicError(500, `Missing or invalid mock config: ${missing.join(', ')}`);
}

function validateStaticConfigForProcessing() {
  const missing = [];
  for (const key of [
    'zohoClientId',
    'zohoClientSecret',
    'zohoRefreshToken',
    'zohoPaymentsAccountId',
    'zohoBooksOrgId',
    'returnedFeeItemId'
  ]) {
    if (!CONFIG[key]) missing.push(key);
  }
  if (CONFIG.requireSignature && !CONFIG.webhookSigningKey) missing.push('webhookSigningKey');
  if (CONFIG.returnedFeeAmount <= 0) missing.push('returnedFeeAmount_positive_number');

  if (!CONFIG.dryRun && CONFIG.requireLiveModeConfirmation) {
    if (!CONFIG.liveModeConfirmation || CONFIG.liveModeConfirmation !== CONFIG.expectedLiveModeConfirmation) {
      missing.push('LIVE_MODE_CONFIRMATION');
    }
    if (!CONFIG.requireSignature) missing.push('REQUIRE_SIGNATURE_true_required_for_live');
    if (!CONFIG.requireJson) missing.push('REQUIRE_JSON_true_required_for_live');
    if (!CONFIG.enableReplayDefense) missing.push('ENABLE_REPLAY_DEFENSE_true_required_for_live');
    if (!CONFIG.strictReplayFailure) missing.push('STRICT_REPLAY_FAILURE_true_required_for_live');
    if (CONFIG.registrationOnly) missing.push('REGISTRATION_ONLY_false_required_for_live');
    if (CONFIG.enableOAuthDiagnostic) missing.push('ENABLE_OAUTH_DIAGNOSTIC_false_required_for_live');
    if (CONFIG.enableMockProcessing) missing.push('ENABLE_MOCK_PROCESSING_false_required_for_live');
    if (CONFIG.debugPayloadLogging) missing.push('DEBUG_PAYLOAD_LOGGING_false_required_for_live');
    if (CONFIG.debugSafeZohoBodies) missing.push('DEBUG_SAFE_ZOHO_BODIES_false_required_for_live');
  }

  if (missing.length) throw publicError(500, `Missing or invalid config: ${missing.join(', ')}`);
}

// =============================================================================
// Generic Helpers
// =============================================================================
function sendJson(res, status, obj) {
  const body = JSON.stringify(obj || { ok: false });
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Content-Length', Buffer.byteLength(body));
  res.end(body);
}

function ok(res, requestId, extra = {}) {
  logInfo({ requestId, ok: true, ...redactForLogs(extra) });
  return sendJson(res, 200, { ok: true, request_id: requestId, ...extra });
}

function fail(res, requestId, status, reason, extra = {}) {
  logInfo({ requestId, ok: false, status, reason, ...redactForLogs(extra) });

  const publicReason = CONFIG.genericPublicErrors
    ? (status === 404 ? 'not_found' : (status >= 500 ? 'Internal webhook error.' : 'Webhook rejected.'))
    : reason;

  return sendJson(res, status, { ok: false, request_id: requestId, error: publicReason });
}

function setSecurityHeaders(res) {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Referrer-Policy', 'no-referrer');
}

function makeRequestId() {
  return typeof crypto.randomUUID === 'function' ? crypto.randomUUID() : crypto.randomBytes(16).toString('hex');
}

function logInfo(obj) {
  try { console.log(JSON.stringify(obj)); }
  catch (_) { console.log(String(obj)); }
}

function safeTimingEqualHex(a, b) {
  const aa = String(a || '').trim().toLowerCase();
  const bb = String(b || '').trim().toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(aa) || !/^[0-9a-f]{64}$/.test(bb)) return false;
  return crypto.timingSafeEqual(Buffer.from(aa, 'hex'), Buffer.from(bb, 'hex'));
}

function safeTimingEqualBase64(a, b) {
  const normalize = (value) => String(value || '').trim().replace(/^sha256=/i, '').replace(/\s+/g, '').replace(/=+$/g, '');
  const aa = normalize(a);
  const bb = normalize(b);
  if (!/^[A-Za-z0-9+/_-]{40,128}$/.test(aa) || !/^[A-Za-z0-9+/_-]{40,128}$/.test(bb)) return false;
  const ab = Buffer.from(aa.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
  const bbuff = Buffer.from(bb.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
  return ab.length === bbuff.length && crypto.timingSafeEqual(ab, bbuff);
}

function safeTimingEqualText(a, b) {
  const aa = Buffer.from(String(a || ''), 'utf8');
  const bb = Buffer.from(String(b || ''), 'utf8');
  return aa.length === bb.length && crypto.timingSafeEqual(aa, bb);
}

function getHeader(headers, name) {
  const wanted = String(name || '').toLowerCase();
  for (const [k, v] of Object.entries(headers || {})) {
    if (String(k).toLowerCase() === wanted) return Array.isArray(v) ? String(v[0] || '') : String(v || '');
  }
  return '';
}

function getClientIp(req) {
  const xf = getHeader(req.headers, 'x-forwarded-for');
  if (xf) return xf.split(',')[0].trim();
  return String(req.socket?.remoteAddress || req.connection?.remoteAddress || '').trim();
}

function deepFindFirst(obj, keys) {
  const wanted = new Set(keys.map((k) => normalizeText(k)));
  const seen = new Set();
  function walk(v) {
    if (!v || typeof v !== 'object') return '';
    if (seen.has(v)) return '';
    seen.add(v);
    for (const [k, child] of Object.entries(v)) {
      if (wanted.has(normalizeText(k)) && child !== null && child !== undefined && String(child).trim() !== '') return child;
      const nested = walk(child);
      if (nested !== '') return nested;
    }
    return '';
  }
  return walk(obj);
}

function firstNonEmpty(...values) {
  for (const v of values) {
    if (v !== null && v !== undefined && String(v).trim() !== '') return v;
  }
  return '';
}

function normalizeText(value) {
  return String(value || '').trim().toLowerCase();
}

function sanitizeMockPaymentId(value) {
  return String(value || '')
    .replace(/[^A-Za-z0-9_-]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 80) || `mock_${Date.now()}`;
}

function sanitizeInvoiceNumber(value) {
  return String(value || '')
    .replace(/[^A-Za-z0-9_-]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 70);
}

function safeTruncate(value, max) {
  const s = String(value || '');
  return s.length > max ? `${s.slice(0, max)}...` : s;
}

function publicError(statusCode, publicMessage, details = {}) {
  const err = new Error(publicMessage);
  err.statusCode = statusCode;
  err.publicMessage = publicMessage;
  err.details = details;
  return err;
}

function safeError(err) {
  if (!err) return {};
  return {
    message: err.message,
    statusCode: err.statusCode,
    details: redactForLogs(err.details || {})
  };
}

function redactForLogs(obj) {
  const json = JSON.stringify(obj || {});
  return JSON.parse(json, (key, value) => {
    const k = String(key || '').toLowerCase();
    if (k.includes('token') || k.includes('secret') || k.includes('authorization') || k.includes('key')) {
      if (typeof value === 'string') return value ? '[REDACTED]' : '';
    }
    return value;
  });
}

function env(name, fallback = '') {
  return process.env[name] !== undefined ? String(process.env[name]) : fallback;
}

function envBool(name, fallback = false) {
  const value = process.env[name];
  if (value === undefined || value === '') return fallback;
  return ['true', '1', 'yes', 'y', 'on'].includes(String(value).toLowerCase());
}

function envNumber(name, fallback) {
  const value = Number(process.env[name]);
  return Number.isFinite(value) ? value : fallback;
}

function envList(name, fallback) {
  const value = process.env[name];
  if (value === undefined || String(value).trim() === '') return Array.isArray(fallback) ? fallback : [];
  return String(value).split(',').map((s) => s.trim()).filter(Boolean);
}
