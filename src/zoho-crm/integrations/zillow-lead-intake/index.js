'use strict';

/**
 * Root Catalyst Advanced I/O entrypoint.
 *
 * Catalyst's Node.js function directory expects the main function file at the
 * function root. Keep the real Zillow intake implementation in `src/index.js`,
 * and expose it here through the root-level main file declared in
 * `catalyst-config.json`.
 */

const handler = require('./src/index');

module.exports = function zillowLeadIntakeRootHandler(req, res) {
  return Promise.resolve(handler(req, res)).catch((error) => {
    console.error(JSON.stringify({
      level: 'error',
      service: 'gh-zillow-lead-intake',
      error: 'unhandled_root_error',
      detail: String(error && error.message ? error.message : error).slice(0, 500)
    }));

    if (!res.headersSent) {
      res.writeHead(500, {
        'content-type': 'application/json; charset=utf-8',
        'x-content-type-options': 'nosniff',
        'cache-control': 'no-store'
      });
    }

    res.end(JSON.stringify({ ok: false, error: 'internal_error' }));
  });
};
