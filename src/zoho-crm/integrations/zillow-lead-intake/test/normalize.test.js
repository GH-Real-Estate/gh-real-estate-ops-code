'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const { Readable } = require('node:stream');

process.env.ZILLOW_WEBHOOK_DRY_RUN = 'true';
process.env.ZILLOW_WEBHOOK_KEY = 'test-secret';
process.env.INBOUND_BODY_TIMEOUT_MS = '1000';
process.env.DEFAULT_LEAD_STATUS = 'New Zillow Inquiry';
process.env.REQUIRE_URLENCODED = 'true';
process.env.ALLOW_JSON_TEST_PAYLOADS = 'false';
process.env.ENABLE_HEALTH = 'false';

const gateway = require('../src/index');
const {
  normalizeZillowLeadPayload,
  validateNormalizedLead,
  resolvePropertyUnit,
  buildRoutingWarnings,
  buildCrmLeadPlan,
  buildLeadKey,
  parseInboundPayload,
  normalizePhone,
  normalizeDate,
  normalizeFieldKey,
  isAllowedContentType
} = gateway._test;

function officialPayload() {
  return new URLSearchParams({
    listingId: '2097508172',
    name: 'Rachel Lee',
    email: 'rachel@example.com',
    phone: '555-555-8378',
    movingDate: '20260926',
    numBedroomsSought: '3',
    numBathroomsSought: '2',
    message: 'Looking for a spacious apartment.',
    listingStreet: '9401 Nieman Road',
    listingUnit: 'Unit 3',
    listingCity: 'Overland Park',
    listingPostalCode: '66214',
    listingState: 'KS',
    listingContactEmail: 'leasing@gabrielhrealestate.com',
    neighborhoods: JSON.stringify(['Overland Park', 'Nieman']),
    propertyTypesDesired: JSON.stringify(['apartment']),
    leaseLengthMonths: '12',
    introduction: 'Hello my name is Rachel.',
    smoker: 'false',
    parkingTypeDesired: 'required',
    incomeYearly: '150000',
    creditScoreRangeJson: JSON.stringify({ creditScoreMin: 675, creditScoreMax: 690 }),
    movingFromCity: 'Kansas City',
    movingFromState: 'MO',
    moveInTimeframe: 'asap',
    reasonForMoving: 'closer to work',
    employmentStatus: 'employed',
    jobTitle: 'Software Engineer',
    employer: 'Example Co',
    employmentStartDate: '2020-09-27',
    employmentDetailsJson: JSON.stringify([{ jobTitle: 'Engineer', employer: 'Example Co', startDate: '2020-09-27' }]),
    petDetailsJson: JSON.stringify([{ type: 'dog', breed: 'Lab', size: 'medium', weightPounds: 50 }]),
    leadType: 'tourRequest',
    providerModelId: '0'
  }).toString();
}

function makeReq({ method = 'POST', url = '/zillow/leads', headers = {}, body = '' } = {}) {
  const req = Readable.from([Buffer.from(body, 'utf8')]);
  req.method = method;
  req.url = url;
  req.headers = headers;
  return req;
}

function makeRes() {
  return {
    headers: {},
    statusCode: 0,
    body: '',
    setHeader(name, value) {
      this.headers[String(name).toLowerCase()] = value;
    },
    writeHead(statusCode) {
      this.statusCode = statusCode;
    },
    end(payload) {
      this.body += payload || '';
    }
  };
}

test('parses official URL-encoded Zillow payload', () => {
  const parsed = parseInboundPayload(Buffer.from(officialPayload()), 'application/x-www-form-urlencoded; charset=UTF-8');
  assert.equal(parsed.email, 'rachel@example.com');
  assert.equal(parsed.listingUnit, 'Unit 3');
  assert.equal(parsed.leadType, 'tourRequest');
});

test('normalizes official Zillow fields and compact YYYYMMDD dates', () => {
  const parsed = parseInboundPayload(Buffer.from(officialPayload()), 'application/x-www-form-urlencoded');
  const lead = normalizeZillowLeadPayload(parsed, {
    receivedAtIso: '2026-07-07T12:00:00.000Z',
    sourcePayloadHash: 'payloadhash'
  });

  assert.equal(lead.leadType, 'tourRequest');
  assert.equal(lead.providerModelId, '0');
  assert.equal(lead.firstName, 'Rachel');
  assert.equal(lead.lastName, 'Lee');
  assert.equal(lead.email, 'rachel@example.com');
  assert.equal(lead.phone, '+15555558378');
  assert.equal(lead.movingDate, '2026-09-26');
  assert.equal(lead.propertyAddress, '9401 Nieman Road, Unit 3, Overland Park, KS 66214');
  assert.deepEqual(lead.neighborhoods, ['Overland Park', 'Nieman']);
  assert.equal(lead.creditScoreRangeJson, '{"creditScoreMin":675,"creditScoreMax":690}');
  assert.equal(lead.sourcePayloadHash, 'payloadhash');
});

test('rejects lead without email or phone', () => {
  const lead = normalizeZillowLeadPayload({
    name: 'Test Tenant',
    listingId: 'listing-1'
  }, { receivedAtIso: '2026-07-01T12:00:00.000Z' });

  const validation = validateNormalizedLead(lead);
  assert.equal(validation.ok, false);
  assert.match(validation.publicErrors.join(' '), /contact method/);
});

test('builds stable duplicate key without using mutable message text', () => {
  const keyA = buildLeadKey({
    email: 'test.tenant@example.com',
    phone: '+19135550100',
    listingId: 'listing-1',
    propertyAddress: '9401 Nieman Rd',
    listingUnit: 'Unit 1',
    leadType: 'tourRequest',
    providerModelId: '0',
    message: 'First message'
  });

  const keyB = buildLeadKey({
    email: 'test.tenant@example.com',
    phone: '+19135550100',
    listingId: 'listing-1',
    propertyAddress: '9401 Nieman Rd',
    listingUnit: 'Unit 1',
    leadType: 'tourRequest',
    providerModelId: '0',
    message: 'Changed message'
  });

  assert.equal(keyA, keyB);
  assert.match(keyA, /^zillow:hash:[a-f0-9]{40}$/);
});

test('resolves property and unit from listing map', () => {
  const lead = normalizeZillowLeadPayload({
    listingId: '2097508172',
    name: 'Test Tenant',
    email: 'test.tenant@example.com'
  }, { receivedAtIso: '2026-07-01T12:00:00.000Z' });

  const propertyUnit = resolvePropertyUnit(lead, {
    'listing:2097508172': {
      propertyId: '1111111111111111111',
      unitId: '2222222222222222222',
      propertyName: '9401 Nieman Road',
      unitName: 'Unit 3'
    }
  });

  assert.equal(propertyUnit.unitName, 'Unit 3');
  assert.equal(propertyUnit.propertyName, '9401 Nieman Road');
});

test('builds CRM Lead plan without deleted rent/deposit/manual review fields', () => {
  const parsed = parseInboundPayload(Buffer.from(officialPayload()), 'application/x-www-form-urlencoded');
  const lead = normalizeZillowLeadPayload(parsed, {
    receivedAtIso: '2026-07-07T12:00:00.000Z',
    sourcePayloadHash: 'payloadhash'
  });

  const propertyUnit = {
    propertyId: '1111111111111111111',
    unitId: '2222222222222222222',
    propertyName: '9401 Nieman Road',
    unitName: 'Unit 3'
  };

  const warnings = buildRoutingWarnings(lead, propertyUnit);
  const plan = buildCrmLeadPlan(lead, propertyUnit, warnings);

  assert.equal(plan.leadRecord.Last_Name, 'Lee');
  assert.equal(plan.leadRecord.Company, '9401 Nieman Road');
  assert.equal(plan.leadRecord.Email, 'rachel@example.com');
  assert.equal(plan.leadRecord.Zillow_Listing_ID, '2097508172');
  assert.equal(plan.leadRecord.Zillow_Lead_Type, 'tourRequest');
  assert.equal(plan.leadRecord.Zillow_Provider_Model_ID, '0');
  assert.equal(plan.leadRecord.Requested_Move_In_Date, '2026-09-26');
  assert.equal(plan.leadRecord.Zillow_Source_Payload_Hash, 'payloadhash');
  assert.equal(plan.leadRecord.Lead_Source, 'Zillow');
  assert.equal(plan.leadRecord.Lead_Status, 'New Zillow Inquiry');
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Desired_Rent'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Desired_Deposit'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Manual_Review_Required'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Manual_Review_Reason'), false);
});

test('strict content-type rejects JSON unless explicitly enabled', () => {
  assert.equal(isAllowedContentType('application/x-www-form-urlencoded; charset=UTF-8'), true);
  assert.equal(isAllowedContentType('application/json'), false);
});

test('handler rejects missing security header before parsing', async () => {
  const req = makeReq({
    headers: { 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8' },
    body: officialPayload()
  });
  const res = makeRes();
  await gateway(req, res);
  assert.equal(res.statusCode, 401);
  assert.equal(JSON.parse(res.body).error, 'inbound_secret_invalid');
});

test('handler accepts authenticated dry-run URL-encoded payload', async () => {
  const req = makeReq({
    headers: {
      'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'x-gh-zillow-webhook-key': 'test-secret'
    },
    body: officialPayload()
  });
  const res = makeRes();
  await gateway(req, res);
  const body = JSON.parse(res.body);
  assert.equal(res.statusCode, 202);
  assert.equal(body.ok, true);
  assert.equal(body.mode, 'dry_run');
  assert.equal(body.planned_actions.lead_module, 'Leads');
});

test('normalizes utility values', () => {
  assert.equal(normalizePhone('(913) 555-0100'), '+19135550100');
  assert.equal(normalizeDate('20260707'), '2026-07-07');
  assert.equal(normalizeDate('7/7/2026'), '2026-07-07');
  assert.equal(normalizeFieldKey('ContactName'), 'contact_name');
});
