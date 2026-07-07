'use strict';

/**
 * Catalyst Advanced I/O blank-template entry point.
 *
 * Zoho Catalyst's blank Advanced I/O Node.js runtime expects a native HTTP
 * server export. The business logic remains in `index.js` so tests can import
 * and exercise the handler directly.
 */

const http = require('http');
const handler = require('./index');

const server = http.createServer((req, res) => {
  Promise.resolve(handler(req, res)).catch((error) => {
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
});

module.exports = server;
