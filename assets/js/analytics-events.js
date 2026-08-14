/*
 * Revelation Agency — provider-neutral local analytics event contract.
 *
 * This file is a LOCAL-ONLY event layer used to prove the contract shape.
 * It installs no third-party pixel and posts to no production destination.
 *
 * Contract (Canon 9487 / P5 packet):
 *   - service_view, proof_view, primary_cta_click, secondary_cta_click,
 *     form_start, form_submit_attempt, booking_open, phone_click, email_click,
 *     outbound_portfolio_click
 *   - Every event carries { page, pillar, service, cta_placement,
 *     utm: {source, medium, campaign, term, content}, referrer_hostname }
 *   - No form field value, email, phone, name, or free-text input may ever
 *     enter the payload. The sanitizer below strips PII.
 *
 * Production activation requires a separate analytics destination, consent,
 * privacy, retention, and read-back decision (see IMPLEMENTATION_REPORT.md).
 */
(function () {
  'use strict';

  var PILLAR_BY_PATH = [
    { rx: /^\/services\/branding\//,   pillar: 'branding' },
    { rx: /^\/services\/marketing\//,  pillar: 'marketing' },
    { rx: /^\/services\/sales\//,      pillar: 'sales' },
    { rx: /^\/services\/ai-automation(\.html)?$/, pillar: 'crosscut-ai' },
    { rx: /^\/portfolio\/branding\//,  pillar: 'branding' },
    { rx: /^\/portfolio\/marketing\//, pillar: 'marketing' },
    { rx: /^\/portfolio\/sales\//,     pillar: 'sales' },
    { rx: /^\/portfolio\//,            pillar: 'portfolio' },
    { rx: /^\/the-reveal\//,           pillar: 'reveal' },
    { rx: /^\/(services|services\.html)$/, pillar: 'services-hub' },
    { rx: /^\/(index\.html)?$/,        pillar: 'home' }
  ];

  function pillarForPath(p) {
    for (var i = 0; i < PILLAR_BY_PATH.length; i++) {
      if (PILLAR_BY_PATH[i].rx.test(p)) return PILLAR_BY_PATH[i].pillar;
    }
    return 'other';
  }

  function serviceForPath(p) {
    var m = p.match(/^\/services\/([^/]+)\/([^/.]+)/);
    if (m) return m[2];
    m = p.match(/^\/services\/([^/]+)\/?$/);
    if (m) return m[1] + '-hub';
    return null;
  }

  function safeUtm() {
    var params = new URLSearchParams(window.location.search || '');
    function clean(k) {
      var v = params.get(k);
      if (v == null) return null;
      return String(v).replace(/[^A-Za-z0-9._-]/g, '').slice(0, 64) || null;
    }
    return {
      source:   clean('utm_source'),
      medium:   clean('utm_medium'),
      campaign: clean('utm_campaign'),
      term:     clean('utm_term'),
      content:  clean('utm_content')
    };
  }

  function referrerHost() {
    try {
      if (!document.referrer) return null;
      var u = new URL(document.referrer);
      return u.hostname.replace(/[^a-z0-9.-]/gi, '').slice(0, 128);
    } catch (_) { return null; }
  }

  var PII_KEYS = /^(email|phone|tel|name|first|last|first_name|last_name|message|note|company|address|city|state|zip|postal|country|password|token|contact|mobile|dob)$/i;

  function sanitize(obj) {
    if (!obj || typeof obj !== 'object') return obj;
    var out = {};
    Object.keys(obj).forEach(function (k) {
      if (PII_KEYS.test(k)) { out[k] = '[REDACTED]'; return; }
      var v = obj[k];
      if (v && typeof v === 'object' && !Array.isArray(v)) {
        out[k] = sanitize(v);
      } else if (typeof v === 'string') {
        out[k] = v.length > 200 ? '[TRUNCATED]' : v;
      } else {
        out[k] = v;
      }
    });
    return out;
  }

  var ALLOWED_EVENTS = [
    'service_view', 'proof_view', 'primary_cta_click', 'secondary_cta_click',
    'form_start', 'form_submit_attempt', 'booking_open', 'phone_click',
    'email_click', 'outbound_portfolio_click'
  ];

  function emit(name, extra) {
    if (ALLOWED_EVENTS.indexOf(name) === -1) return;
    var path = window.location.pathname || '/';
    var payload = sanitize({
      event: name,
      page: path,
      pillar: pillarForPath(path),
      service: serviceForPath(path),
      cta_placement: (extra && extra.cta_placement) || null,
      utm: safeUtm(),
      referrer_hostname: referrerHost(),
      ts: Date.now()
    });
    if (extra) {
      Object.keys(extra).forEach(function (k) {
        if (k === 'cta_placement') return;
        if (PII_KEYS.test(k)) return;
        payload[k] = extra[k];
      });
    }
    // LOCAL SINK ONLY. Push to a window buffer + console. Never network.
    window.__RA_EVENTS__ = window.__RA_EVENTS__ || [];
    window.__RA_EVENTS__.push(payload);
    try { if (window.console && console.debug) console.debug('[ra.analytics]', payload); } catch (_) { /* noop */ }
  }

  // Auto-bind: mark service_view on load for /services/ + /portfolio/ pages.
  function autoBind() {
    var path = window.location.pathname || '/';
    if (/^\/services\//.test(path)) emit('service_view');
    if (/^\/portfolio\//.test(path)) emit('proof_view');

    document.querySelectorAll('a[data-cta="primary"]').forEach(function (el) {
      el.addEventListener('click', function () {
        emit('primary_cta_click', { cta_placement: el.getAttribute('data-cta-placement') || null });
      });
    });
    document.querySelectorAll('a[data-cta="secondary"]').forEach(function (el) {
      el.addEventListener('click', function () {
        emit('secondary_cta_click', { cta_placement: el.getAttribute('data-cta-placement') || null });
      });
    });
    document.querySelectorAll('a[href^="tel:"]').forEach(function (el) {
      el.addEventListener('click', function () { emit('phone_click'); });
    });
    document.querySelectorAll('a[href^="mailto:"]').forEach(function (el) {
      el.addEventListener('click', function () { emit('email_click'); });
    });
    document.querySelectorAll('a[data-booking-open="1"], a[href*="booking.html"]').forEach(function (el) {
      el.addEventListener('click', function () { emit('booking_open'); });
    });
    document.querySelectorAll('form[data-webhook], form.ra-form').forEach(function (form) {
      var started = false;
      form.addEventListener('focusin', function () {
        if (started) return;
        started = true;
        emit('form_start');
      });
      form.addEventListener('submit', function () {
        emit('form_submit_attempt');
      });
    });
    document.querySelectorAll('a[data-outbound-portfolio], a[data-portfolio-live]').forEach(function (el) {
      el.addEventListener('click', function () {
        emit('outbound_portfolio_click', { destination_host: (el.hostname || null) });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoBind);
  } else {
    autoBind();
  }

  // Public handle for tests + manual emits from templates.
  window.RA_ANALYTICS = { emit: emit, allowed: ALLOWED_EVENTS.slice(), sanitize: sanitize };
})();
