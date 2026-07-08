'use strict';

/**
 * Root Catalyst Advanced I/O entrypoint.
 *
 * Catalyst's Node.js function directory expects the main function file at the
 * function root. Keep the real Zillow intake implementation in `src/index.js`,
 * and expose it here through the root-level main file declared in
 * `catalyst-config.json`.
 */

// GH Real Estate verified the Zoho CRM Units module API name as `Units`.
// Set the safe runtime default before loading src/index.js because that module
// builds its CONFIG object at require-time.
process.env.ZOHO_CRM_UNITS_MODULE = process.env.ZOHO_CRM_UNITS_MODULE || 'Units';

let cachedHandler;

module.exports = function zillowLeadIntakeRootHandler(req, res) {
  normalizeCatalystFunctionUrl(req);
  normalizeCatalystHealthMethod(req);

  let handler;
  try {
    handler = getHandler();
  } catch (error) {
    return writeStartupError(res, error);
  }

  return Promise.resolve(handler(req, res)).catch((error) => {
    console.error(JSON.stringify({
      level: 'error',
      service: 'gh-zillow-lead-intake',
      error: 'unhandled_root_error',
      detail: safeErrorDetail(error)
    }));

    return writeJson(res, 500, { ok: false, error: 'internal_error' });
  });
};

function getHandler() {
  if (!cachedHandler) cachedHandler = require('./src/index');
  return cachedHandler;
}

function normalizeCatalystFunctionUrl(req) {
  if (!req || typeof req.url !== 'string') return;

  const functionName = String(process.env.CATALYST_FUNCTION_NAME || 'Zillow-Lead-Intake').trim();
  const basePath = `/server/${functionName}`;

  if (req.url === basePath || req.url === `${basePath}/`) {
    req.url = '/';
    return;
  }

  if (req.url.startsWith(`${basePath}/`)) {
    req.url = req.url.slice(basePath.length) || '/';
  }
}

function normalizeCatalystHealthMethod(req) {
  if (!req || typeof req.url !== 'string') return;

  // Some Catalyst function invocation URLs reject GET before the Advanced I/O
  // handler is reached. Accept a POST health probe from PowerShell and map it
  // back to the implementation's protected GET /health route.
  if (String(req.method || '').toUpperCase() === 'POST' && req.url === '/health') {
    req.method = 'GET';
  }
}

function writeStartupError(res, error) {
  console.error(JSON.stringify({
    level: 'error',
    service: 'gh-zillow-lead-intake',
    error: 'startup_error',
    detail: safeErrorDetail(error)
  }));

  return writeJson(res, 500, {
    ok: false,
    error: 'startup_error',
    detail: safeErrorDetail(error)
  });
}

function writeJson(res, statusCode, body) {
  const payload = JSON.stringify(body);

  if (res && typeof res.setHeader === 'function') {
    res.setHeader('content-type', 'application/json; charset=utf-8');
    res.setHeader('x-content-type-options', 'nosniff');
    res.setHeader('cache-control', 'no-store');
  }

  if (res && typeof res.writeHead === 'function' && !res.headersSent) {
    res.writeHead(statusCode);
  } else if (res) {
    res.statusCode = statusCode;
  }

  if (res && typeof res.end === 'function') return res.end(payload);
  return payload;
}

function safeErrorDetail(error) {
  return String(error && error.message ? error.message : error).slice(0, 500);
}
