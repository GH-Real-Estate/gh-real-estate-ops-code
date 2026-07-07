'use strict';

const crypto = require('crypto');

function sha256(text) {
  return crypto.createHash('sha256').update(String(text)).digest('hex');
}

function makeRequestId() {
  return crypto.randomBytes(8).toString('hex');
}

function cleanText(value) {
  if (value === null || value === undefined) return '';
  return String(value).replace(/\s+/g, ' ').trim();
}

function cleanUrl(value) {
  const text = cleanText(value);
  return /^https?:\/\//i.test(text) ? text : '';
}

function normalizeEmail(value) {
  return cleanText(value).toLowerCase();
}

function normalizePhone(value) {
  const text = cleanText(value);
  if (!text) return '';
  const digits = text.replace(/\D/g, '');
  if (digits.length === 10) return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith('1')) return `+${digits}`;
  return text;
}

function normalizeDate(value) {
  const text = cleanText(value);
  if (!text) return '';
  const yyyymmdd = text.match(/^(\d{4})(\d{2})(\d{2})$/);
  if (yyyymmdd) return `${yyyymmdd[1]}-${yyyymmdd[2]}-${yyyymmdd[3]}`;
  const iso = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (iso) return `${iso[1]}-${iso[2]}-${iso[3]}`;
  const us = text.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (us) return `${us[3]}-${String(us[1]).padStart(2, '0')}-${String(us[2]).padStart(2, '0')}`;
  const parsed = new Date(text);
  return Number.isNaN(parsed.getTime()) ? '' : String(parsed.toISOString()).slice(0, 10);
}

function normalizeFieldKey(key) {
  return String(key || '')
    .trim()
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase();
}

function normalizeMapKey(value) {
  return cleanText(value).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function firstValue(input, keys) {
  for (const key of keys) {
    const value = cleanText(input[normalizeFieldKey(key)]);
    if (value) return value;
  }
  return '';
}

function splitPersonName(fullName) {
  const parts = cleanText(fullName).split(' ').filter(Boolean);
  if (!parts.length) return { firstName: '', lastName: '' };
  if (parts.length === 1) return { firstName: '', lastName: parts[0] };
  return { firstName: parts.slice(0, -1).join(' '), lastName: parts.at(-1) };
}

function isLikelyEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function truncate(text, maxLength) {
  const value = cleanText(text);
  return value.length <= maxLength ? value : `${value.slice(0, Math.max(0, maxLength - 3))}...`;
}

function publicError(statusCode, publicCode) {
  const error = new Error(publicCode);
  error.statusCode = statusCode;
  error.publicCode = publicCode;
  return error;
}

function safeTimingEqualText(a, b) {
  const left = Buffer.from(String(a || ''), 'utf8');
  const right = Buffer.from(String(b || ''), 'utf8');
  return left.length === right.length && crypto.timingSafeEqual(left, right);
}

module.exports = {
  sha256,
  makeRequestId,
  cleanText,
  cleanUrl,
  normalizeEmail,
  normalizePhone,
  normalizeDate,
  normalizeFieldKey,
  normalizeMapKey,
  firstValue,
  splitPersonName,
  isLikelyEmail,
  truncate,
  publicError,
  safeTimingEqualText
};
