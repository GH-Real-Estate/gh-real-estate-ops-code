'use strict';

/**
 * Returned Payment Webhook
 *
 * Placeholder only. Replace with the current approved runtime code if this
 * automation is used.
 *
 * Required before production:
 * - Webhook authentication / signature verification.
 * - Replay protection.
 * - Duplicate fee prevention.
 * - No PII/secrets logging.
 * - Dry-run or test mode where feasible.
 */

module.exports = async function returnedPaymentWebhookPlaceholder(_request, response) {
  response.statusCode = 501;
  response.setHeader('content-type', 'application/json');
  response.end(JSON.stringify({
    ok: false,
    message: 'Returned payment webhook placeholder. Replace before deployment.'
  }));
};
