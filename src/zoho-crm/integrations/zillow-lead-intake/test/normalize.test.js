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
  buildRoutingUnitKey,
  buildRoutingWarnings,
  buildCrmLeadPlan,
  buildLeadKey,
  parseInboundPayload,
  normalizePhone,
  normalizeDate,
  normalizeFieldKey,
  isAllowedContentType,
  buildInquiryMessage,
  buildRenterProfileSummary
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
  assert.equal(lead.secondaryPhone, '');
  assert.equal(lead.desiredMoveInDate, '2016-09-26');
  assert.equal(lead.propertyAddress, '246 Tennessee Avenue, C102, Sunnyvale, CA 94086');
  assert.equal(lead.routingUnitKey, '246 tennessee avenue|c102|sunnyvale|ca|94086');
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
    propertyAddress: '1000 Example Avenue, Unit 1, Sample City, KS 00000',
    unit: 'Unit 1',
    leadType: 'tourRequest',
    message: 'Tour request'
  });

  const keyB = buildLeadKey({
    email: 'test.tenant@example.com',
    phone: '+19135550100',
    listingId: 'listing-1',
    propertyAddress: '1000 Example Avenue, Unit 1, Sample City, KS 00000',
    unit: 'Unit 1',
    leadType: 'tourRequest',
    message: 'Tour request'
  });

  assert.equal(keyA, keyB);
  assert.match(keyA, /^zillow:hash:[a-f0-9]{40}$/);
});

test('resolves property and unit from static map before CRM Unit lookup', async () => {
  const lead = normalizeZillowLeadPayload({
    listingId: 'zpid_example_1000_1',
    name: 'Test Tenant',
    email: 'test.tenant@example.com'
  }, '2026-07-01T12:00:00.000Z');

  const propertyUnit = await resolvePropertyUnit(lead, {
    'listing:zpid example 1000 1': {
      propertyId: 'SYNTHETIC-ID-001',
      unitId: 'SYNTHETIC-ID-006',
      propertyName: '1000 Example Avenue',
      unitName: 'Unit 1'
    }
  });

  assert.equal(propertyUnit.unitName, 'Unit 1');
  assert.equal(propertyUnit.propertyName, '1000 Example Avenue');
  assert.equal(propertyUnit.matchedBy, 'runtime_map');
});

test('builds routing unit key from Zillow listing address components', () => {
  assert.equal(
    buildRoutingUnitKey({
      listingStreet: '1000 Example Avenue',
      listingUnit: 'Unit 3',
      listingCity: 'Sample City',
      listingState: 'KS',
      listingPostalCode: '00000'
    }),
    '1000 example avenue|unit 3|sample city|ks|00000'
  );
});

test('builds CRM Lead plan with primary Zillow phone mapped to Mobile only', () => {
  const lead = normalizeZillowLeadPayload({
    leadId: 'lead_test_123',
    name: 'Test Tenant',
    email: 'test.tenant@example.com',
    phone: '913-555-0100',
    listingId: 'zpid_example_1000_1',
    listingStreet: '1000 Example Avenue',
    listingUnit: 'Unit 3',
    listingCity: 'Sample City',
    listingState: 'KS',
    listingPostalCode: '00000',
    movingDate: '20260707',
    leadType: 'question',
    moveInTimeframe: 'month',
    message: 'I would like to tour this unit.',
    numBedroomsSought: '2'
  }, '2026-07-01T12:00:00.000Z', 'payloadhash123');

  const propertyUnit = {
    propertyId: 'SYNTHETIC-ID-001',
    unitId: 'SYNTHETIC-ID-006',
    propertyName: '1000 Example Avenue',
    unitName: 'Unit 3'
  };

  const plan = buildCrmLeadPlan(lead, propertyUnit, buildRoutingWarnings(lead, propertyUnit));

  assert.equal(plan.leadRecord.Last_Name, 'Tenant');
  assert.equal(plan.leadRecord.Company, '1000 Example Avenue');
  assert.equal(plan.leadRecord.Email, 'test.tenant@example.com');
  assert.equal(plan.leadRecord.Mobile, '+19135550100');
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Phone'), false);
  assert.equal(plan.leadRecord.Zillow_Lead_Key, 'zillow:lead_test_123');
  assert.equal(plan.leadRecord.Lead_Source, 'Zillow');
  assert.equal(plan.leadRecord.Lead_Status, 'New Zillow Inquiry');
  assert.equal(plan.leadRecord.Requested_Move_In_Date, '2026-07-07');
  assert.equal(plan.leadRecord.Zillow_Property_Address_Raw, '1000 Example Avenue, Unit 3, Sample City, KS 00000');
  assert.equal(plan.leadRecord.Zillow_Lead_Type, 'question');
  assert.equal(plan.leadRecord.Zillow_Move_In_Timeframe, 'month');
  assert.equal(plan.leadRecord.Zillow_Listing_Street, '1000 Example Avenue');
  assert.equal(plan.leadRecord.Zillow_Listing_Unit, 'Unit 3');
  assert.equal(plan.leadRecord.Zillow_Listing_City, 'Sample City');
  assert.equal(plan.leadRecord.Zillow_Listing_State, 'KS');
  assert.equal(plan.leadRecord.Zillow_Listing_Postal_Code, '00000');
  assert.equal(plan.leadRecord.Zillow_Source_Payload_Hash, 'payloadhash123');
  assert.equal(plan.leadRecord.Zillow_Intake_Status, 'Routing Matched');
  assert.equal(plan.leadRecord.Zillow_Raw_Payload_Stored, false);
  assert.match(plan.leadRecord.Zillow_Renter_Profile_Summary, /Bedrooms sought: 2/);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Desired_Rent'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Desired_Deposit'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Manual_Review_Required'), false);
  assert.equal(Object.prototype.hasOwnProperty.call(plan.leadRecord, 'Manual_Review_Reason'), false);
});

test('maps secondary phone aliases to standard Phone when present', () => {
  const lead = normalizeZillowLeadPayload({
    name: 'Test Tenant',
    email: 'test.tenant@example.com',
    phone: '913-555-0100',
    secondaryPhone: '913-555-0101',
    listingId: 'zpid_example_1000_1'
  }, '2026-07-01T12:00:00.000Z');

  const plan = buildCrmLeadPlan(lead, null, buildRoutingWarnings(lead, null));
  assert.equal(plan.leadRecord.Mobile, '+19135550100');
  assert.equal(plan.leadRecord.Phone, '+19135550101');
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
  assert.match(buildRenterProfileSummary({ numBedroomsSought: '2' }), /Bedrooms sought: 2/);
});
