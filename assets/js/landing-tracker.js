/*
 * Revelation Agency — landing-page tracker
 *
 * Reads `?cid=...` (recipient id) from the URL, stores it in sessionStorage,
 * and fires:
 *
 *   On load:
 *     - GA4 page_view + custom "landing_view" event carrying { cid, page }
 *       (only if window.LANDING_GA4_ID is set)
 *     - POST { cid, page, event:"view", timestamp } to LANDING_WEBHOOK_URL
 *       (only if set)
 *
 *   On click of any element matching `.landing-cta` (the booking buttons):
 *     - GA4 "landing_cta_click" event with { cid, page, cta }
 *     - POST { cid, page, event:"cta_click", cta, timestamp } to webhook
 *
 * No third-party pixels. No fallbacks. If env values are unset the tracker
 * is a silent no-op. Failures (network, blocked by privacy extension, etc.)
 * are swallowed — the page is the priority, not the metric.
 */
(function () {
  'use strict';

  var GA4_ID = window.LANDING_GA4_ID || null;
  var WEBHOOK = window.LANDING_WEBHOOK_URL || null;

  // -- cid: read from URL, persist for the session so CTA clicks carry it ---
  var sp = new URLSearchParams(window.location.search);
  var cid = sp.get('cid');
  try {
    if (cid) {
      sessionStorage.setItem('ra_landing_cid', cid);
    } else {
      cid = sessionStorage.getItem('ra_landing_cid');
    }
  } catch (e) { /* sessionStorage might be blocked */ }

  var page = window.location.pathname.replace(/\/$/, '') || '/';

  // -- GA4 (gtag) lazy-loader ----------------------------------------------
  if (GA4_ID) {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_ID);
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA4_ID, {
      send_page_view: true,
      page_path: page,
    });
    window.gtag('event', 'landing_view', {
      cid: cid || '',
      page: page,
    });
  }

  // -- Webhook POST helper -------------------------------------------------
  function postWebhook(eventName, extra) {
    if (!WEBHOOK) return;
    var payload = {
      cid: cid || '',
      page: page,
      event: eventName,
      timestamp: new Date().toISOString(),
    };
    if (extra) Object.assign(payload, extra);
    try {
      // sendBeacon is fire-and-forget — survives page navigation (important
      // when a CTA click navigates immediately to /booking).
      if (navigator.sendBeacon) {
        var blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
        navigator.sendBeacon(WEBHOOK, blob);
        return;
      }
      fetch(WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true,
        mode: 'cors',
      }).catch(function () { /* swallow */ });
    } catch (e) { /* swallow */ }
  }

  // -- Fire page-view webhook now ------------------------------------------
  postWebhook('view');

  // -- CTA click wiring ----------------------------------------------------
  document.addEventListener('click', function (ev) {
    var target = ev.target && ev.target.closest ? ev.target.closest('.landing-cta') : null;
    if (!target) return;
    var ctaName = target.getAttribute('data-cta') || 'unknown';
    if (GA4_ID && window.gtag) {
      window.gtag('event', 'landing_cta_click', {
        cid: cid || '',
        page: page,
        cta: ctaName,
      });
    }
    postWebhook('cta_click', { cta: ctaName });
  }, true);

})();
