'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');

process.env.DRY_RUN = 'true';

const gateway = require('../src/index');
const {
  normalizeZillowLeadPayload,
  validateNormalizedLead,
  resolvePropertyUnit,
  buildManualReviewReasons,
  buildCrmPlan,
  buildLeadKey,
  parseInboundPayload,
  normalizePhone,
  normalizeDate,
  normalizeFieldKey
} = gateway._test;

test('parses urlencoded Zillow payload', () => {
  const body = Buffer.from([
    'lead_id=lead_test_123',
    'name=Test%20Tenant',
    'email=test.tenant%40example.com',
    'phone=(913)%20555-0100',
    'listing_id=zpid_test_9401_1',
    'property_address=9401%20Nieman%20Rd',
    'unit=Unit%201',
    'message=I%20would%20like%20to%20tour%20this%20unit.'
  ].join('&'));

  const parsed = parseInboundPayload(body, 'application/x-www-form-urlencoded');
  assert.equal(parsed.email, 'test.tenant@example.com');
  assert.equal(parsed.unit, 'Unit 1');
});

test('normalizes likely Zillow field aliases', () => {
  const lead = normalizeZillowLeadPayload({
    LeadID: 'abc123',
    ContactName: 'Test Tenant',
    Email_Address: 'TEST.TENANT@EXAMPLE.COM',
    Phone_Number: '913-555-0100',
    ListingID: 'listing-1',
    MoveInDate: '7/7/2026'
  }, '2026-07-01T12:00:00.000Z');

  assert.equal(lead.leadKey, 'zillow:abc123');
  assert.equal(lead.firstName, 'Test');
  assert.equal(lead.lastName, 'Tenant');
  assert.equal(lead.email, 'test.tenant@example.com');
  assert.equal(lead.phone, '+19135550100');
  assert.equal(lead.desiredMoveInDate, '2026-07-07');
});

test('rejects lead without email or phone', () => {
  const lead = normalizeZillowLeadPayload({
    name: 'Test Tenant',
    listing_id: 'listing-1'
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
    propertyAddress: '9401 Nieman Rd',
    unit: 'Unit 1',
    message: 'Tour request'
  });

  const keyB = buildLeadKey({
    email: 'test.tenant@example.com',
    phone: '+19135550100',
    listingId: 'listing-1',
    propertyAddress: '9401 Nieman Rd',
    unit: 'Unit 1',
    message: 'Tour request'
  });

  assert.equal(keyA, keyB);
  assert.match(keyA, /^zillow:hash:[a-f0-9]{40}$/);
});

test('resolves property and unit from listing map', () => {
  const lead = normalizeZillowLeadPayload({
    listing_id: 'zpid_test_9401_1',
    name: 'Test Tenant',
    email: 'test.tenant@example.com'
  }, '2026-07-01T12:00:00.000Z');

  const propertyUnit = resolvePropertyUnit(lead, {
    'listing:zpid test 9401 1': {
      propertyId: '1111111111111111111',
      unitId: '2222222222222222222',
      unitName: 'Unit 1',
      approvedRent: 1125,
      approvedDeposit: 1125
    }
  });

  assert.equal(propertyUnit.unitName, 'Unit 1');
  assert.equal(propertyUnit.approvedRent, 1125);
});

test('builds CRM plan with duplicate prevention fields', () => {
  const lead = normalizeZillowLeadPayload({
    lead_id: 'lead_test_123',
    name: 'Test Tenant',
    email: 'test.tenant@example.com',
    phone: '913-555-0100',
    listing_id: 'zpid_test_9401_1',
    property_address: '9401 Nieman Rd',
    unit: 'Unit 1',
    desired_move_in_date: '2026-07-07',
    rent: '$1125'
  }, '2026-07-01T12:00:00.000Z');

  const propertyUnit = {
    propertyId: '1111111111111111111',
    unitId: '2222222222222222222',
    unitName: 'Unit 1',
    approvedRent: 1125,
    approvedDeposit: 1125
  };

  const reasons = buildManualReviewReasons(lead, propertyUnit);
  const plan = buildCrmPlan(lead, propertyUnit, reasons);

  assert.equal(plan.contactRecord.Last_Name, 'Tenant');
  assert.equal(plan.contactRecord.Email, 'test.tenant@example.com');
  assert.equal(plan.applicationRecord.Zillow_Lead_Key, 'zillow:lead_test_123');
  assert.equal(plan.applicationRecord.Stage, 'New Inquiry');
  assert.equal(plan.applicationRecord.Amount, 1125);
  assert.equal(plan.applicationRecord.Manual_Review_Required, false);
});

test('normalizes utility values', () => {
  assert.equal(normalizePhone('(913) 555-0100'), '+19135550100');
  assert.equal(normalizeDate('7/7/2026'), '2026-07-07');
  assert.equal(normalizeFieldKey('ContactName'), 'contact_name');
});
