'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');

process.env.DRY_RUN = 'true';
process.env.ALLOW_JSON_PAYLOADS = 'false';

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
  isAllowedContentType,
  buildInquiryMessage
} = gateway._test;

test('parses official URL-encoded Zillow payload format', () => {
  const body = Buffer.from([
    'listingId=p01023',
    'name=Rachel%20Lee',
    'email=rachel%40example.com',
    'phone=555-555-8378',
    'movingDate=20160926',
    'numBedroomsSought=3',
    'numBathroomsSought=2',
    'message=Looking%20for%20spacious%203%20bedroom%20apartment%20or%20house',
    'listingStreet=246%20Tennessee%20Avenue',
    'listingUnit=C102',
    'listingCity=Sunnyvale',
    'listingPostalCode=94086',
    'listingState=CA',
    'leadType=tourRequest'
  ].join('&'));

  const parsed = parseInboundPayload(body, 'application/x-www-form-urlencoded; charset=UTF-8');
  assert.equal(parsed.email, 'rachel@example.com');
  assert.equal(parsed.listingUnit, 'C102');
  assert.equal(parsed.leadType, 'tourRequest');
});

test('normalizes official Zillow camelCase fields', () => {
  const lead = normalizeZillowLeadPayload({
    listingId: 'p01023',
    name: 'Rachel Lee',
    email: 'RACHEL@EXAMPLE.COM',
    phone: '555-555-8378',
    movingDate: '20160926',
    numBedroomsSought: '3',
    numBathroomsSought: '2',
    message: 'Looking for spacious 3 bedroom apartment or house',
    listingStreet: '246 Tennessee Avenue',
    listingUnit: 'C102',
    listingCity: 'Sunnyvale',
    listingPostalCode: '94086',
    listingState: 'CA',
    listingContactEmail: 'propertymanager@example.com',
    leadType: 'tourRequest',
    providerModelId: '0'
  }, '2026-07-01T12:00:00.000Z', 'abc123hash');

  assert.equal(lead.firstName, 'Rachel');
  assert.equal(lead.lastName, 'Lee');
  assert.equal(lead.email, 'rachel@example.com');
  assert.equal(lead.phone, '+15555558378');
  assert.equal(lead.desiredMoveInDate, '2016-09-26');
  assert.equal(lead.propertyAddress, '246 Tennessee Avenue, C102, Sunnyvale, CA 94086');
  assert.equal(lead.leadType, 'tourRequest');
  assert.equal(lead.sourcePayloadHash, 'abc123hash');
});

test('rejects lead without email or phone', () => {
  const lead = normalizeZillowLeadPayload({
    name: 'Test Tenant',
    listingId: 'listing-1'
  }, '2026-07-01T12:00:00.000Z');

  const validation = validateNormalizedLead(lead);
  assert.equal(validation.ok, false);
  assert.match(validation.publicErrors.join(' '), /contact method/);
});

test('builds stable hash key when Zillow lead ID is absent', () => {
  const keyA = buildLeadKey({
    email: 'test.tenant@example.com',
    phone: '+19135550100',
    listingId: 'listing-1',
    propertyAddress: '9401 Nieman Rd, Unit 1, Overland Park, KS 66214',
    unit: 'Unit 1',
    leadType: 'tourRequest',
    message: 'Tour request'
  });

  const keyB = buildLeadKey({
    email: 'test.tenant@example.com',
    phone: '+19135550100',
    listingId: 'listing-1',
    propertyAddress: '9401 Nieman Rd, Unit 1, Overland Park, KS 66214',
    unit: 'Unit 1',
    leadType: 'tourRequest',
    message: 'Tour request'
  });

  assert.equal(keyA, keyB);
  assert.match(keyA, /^zillow:hash:[a-f0-9]{40}$/);
});

test('resolves property and unit from listing map', () => {
  const lead = normalizeZillowLeadPayload({
    listingId: 'zpid_test_9401_1',
    name: 'Test Tenant',
    email: 'test.tenant@example.com'
  }, '2026-07-01T12:00:00.000Z');

  const propertyUnit = resolvePropertyUnit(lead, {
    'listing:zpid test 9401 1': {
      propertyId: '1111111111111111111',
      unitId: '2222222222222222222',
      propertyName: '9401 Nieman Rd',
      unitName: 'Unit 1'
    }
  });

  assert.equal(propertyUnit.unitName, 'Unit 1');
  assert.equal(propertyUnit.propertyName, '9401 Nieman Rd');
});

test('builds CRM Lead plan without removed manual-review or rent/deposit fields', () => {
  const lead = normalizeZillowLeadPayload({
    leadId: 'lead_test_123',
    name: 'Test Tenant',
    email: 'test.tenant@example.com',
    phone: '913-555-0100',
    listingId: 'zpid_test_9401_1',
    listingStreet: '9401 Nieman Road',
    listingUnit: 'Unit 3',
    listingCity: 'Overland Park',
    listingState: 'KS',
    listingPostalCode: '66214',
    movingDate: '20260707',
    leadType: 'question',
    message: 'I would like to tour this unit.'
  }, '2026-07-01T12:00:00.000Z', 'payloadhash123');

  const propertyUnit = {
    propertyId: '1111111111111111111',
    unitId: '2222222222222222222',
    propertyName: '9401 Nieman Rd',
    unitName: 'Unit 3'
  };

  const warnings = buildRoutingWarnings(lead, propertyUnit);
  const plan = buildCrmLeadPlan(lead, propertyUnit, warnings);

  assert.equal(plan.leadRecord.Last_Name, 'Tenant');
  assert.equal(plan.leadRecord.Company, '9401 Nieman Rd');
  assert.equal(plan.leadRecord.Email, 'test.tenant@example.com');
  assert.equal(plan.leadRecord.Zillow_Lead_Key, 'zillow:lead_test_123');
  assert.equal(plan.leadRecord.Lead_Source, 'Zillow');
  assert.equal(plan.leadRecord.Lead_Status, 'Not Contacted');
  assert.equal(plan.leadRecord.Requested_Move_In_Date, '2026-07-07');
  assert.equal(plan.leadRecord.Zillow_Property_Address, '9401 Nieman Road, Unit 3, Overland Park, KS 66214');
  assert.equal(plan.leadRecord.Zillow_Source_Payload_Hash, 'payloadhash123');
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Desired_Rent'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Desired_Deposit'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Manual_Review_Required'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Manual_Review_Reason'), false);
});

test('uses URL-encoded body as the default accepted content type', () => {
  assert.equal(isAllowedContentType('application/x-www-form-urlencoded; charset=UTF-8'), true);
  assert.equal(isAllowedContentType('application/json'), false);
});

test('normalizes utility values', () => {
  assert.equal(normalizePhone('(913) 555-0100'), '+19135550100');
  assert.equal(normalizeDate('7/7/2026'), '2026-07-07');
  assert.equal(normalizeDate('20260707'), '2026-07-07');
  assert.equal(normalizeFieldKey('listingContactEmail'), 'listing_contact_email');
  assert.equal(buildInquiryMessage('Hello', 'Intro'), 'Introduction: Intro\n\nMessage: Hello');
});
