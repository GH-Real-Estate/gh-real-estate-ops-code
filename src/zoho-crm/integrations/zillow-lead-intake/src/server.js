'use strict';

/**
 * Catalyst Advanced I/O entry point.
 *
 * Catalyst's Node.js Advanced I/O runtime invokes the exported value as a
 * request handler function with native Node `req` and `res` objects. Keep the
 * business logic in `index.js`; export a plain function here for Catalyst.
 */

const handler = require('./index');

module.exports = function catalystAdvancedIoHandler(req, res) {
  return Promise.resolve(handler(req, res)).catch((error) => {
    console.error(JSON.stringify({
      level: 'error',
      service: 'gh-zillow-lead-intake',
      error: 'unhandled_server_error',
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
