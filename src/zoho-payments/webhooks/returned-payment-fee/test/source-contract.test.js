'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const packageRoot = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(packageRoot, 'src', 'index.js'), 'utf8');
const readme = fs.readFileSync(path.join(packageRoot, 'README.md'), 'utf8');
const securityModel = fs.readFileSync(path.join(packageRoot, 'docs', 'security-model.md'), 'utf8');

test('webhook source keeps safe production defaults', () => {
  assert.match(source, /requireJson:\s*envBool\('REQUIRE_JSON',\s*true\)/);
  assert.match(source, /requireSignature:\s*envBool\('REQUIRE_SIGNATURE',\s*true\)/);
  assert.match(source, /registrationOnly:\s*envBool\('REGISTRATION_ONLY',\s*false\)/);
  assert.match(source, /dryRun:\s*envBool\('DRY_RUN',\s*true\)/);
  assert.match(source, /genericPublicErrors:\s*envBool\('GENERIC_PUBLIC_ERRORS',\s*true\)/);
});

test('live mode requires more than disabling dry run', () => {
  assert.match(source, /requireLiveModeConfirmation:\s*envBool\('REQUIRE_LIVE_MODE_CONFIRMATION',\s*true\)/);
  assert.match(source, /expectedLiveModeConfirmation:\s*env\('EXPECTED_LIVE_MODE_CONFIRMATION',\s*'GH_RETURNED_FEE_LIVE_APPROVED'\)/);
  assert.match(source, /REQUIRE_SIGNATURE_true_required_for_live/);
  assert.match(source, /ENABLE_REPLAY_DEFENSE_true_required_for_live/);
  assert.match(source, /ENABLE_OAUTH_DIAGNOSTIC_false_required_for_live/);
  assert.match(source, /ENABLE_MOCK_PROCESSING_false_required_for_live/);
});

test('webhook keeps replay and per-payment lock controls', () => {
  assert.match(source, /enableReplayDefense:\s*envBool\('ENABLE_REPLAY_DEFENSE',\s*true\)/);
  assert.match(source, /strictReplayFailure:\s*envBool\('STRICT_REPLAY_FAILURE',\s*true\)/);
  assert.match(source, /makeCacheKey\('evt:',\s*replayKeyMaterial\)/);
  assert.match(source, /makeCacheKey\('lock:',\s*paymentIdFromPayload\)/);
});

test('source-of-truth verification happens before Books invoice creation', () => {
  const paymentLookup = source.indexOf('const payment = await retrieveZohoPayment(paymentId, accessToken);');
  const failedCheck = source.indexOf("normalizeText(payment.status) !== 'failed'");
  const createInvoice = source.indexOf('await createReturnedFeeInvoice(sourceInvoice, payment, attemptToken, accessToken, receivedAtIso)');

  assert.ok(paymentLookup > -1, 'payment lookup is present');
  assert.ok(failedCheck > paymentLookup, 'failed status check follows payment lookup');
  assert.ok(createInvoice > failedCheck, 'invoice creation happens after payment verification');
});

test('returned-fee ownership stays under Zoho Payments with Catalyst runtime documented', () => {
  assert.match(readme, /Event source:\s*Zoho Payments/);
  assert.match(readme, /Execution runtime:\s*Zoho Catalyst Advanced I\/O \/ Node\.js 18/);
  assert.match(readme, /The trigger event originates from Zoho Payments/);
  assert.match(securityModel, /Zoho Payments webhook/);
  assert.match(securityModel, /Catalyst function/);
});
