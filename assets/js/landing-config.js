/*
 * Revelation Agency — landing-page tracking config
 *
 * Two values, both expected to be set by Blaine before launch.
 * Until they are set, the tracker is a no-op (guards check the values
 * before firing anything). Nothing is invented.
 *
 *   LANDING_GA4_ID     — GA4 Measurement ID, format "G-XXXXXXXXXX".
 *                        Get it from Google Analytics → Admin → Data Streams →
 *                        Web → Measurement ID.
 *
 *   LANDING_WEBHOOK_URL — Full HTTPS endpoint that accepts a JSON POST of
 *                        {cid, page, event, timestamp}. Typically a GHL inbound
 *                        webhook or a Cloudflare Worker.
 *
 * TODO(Blaine): set both values below. Leave them as null to keep the
 * tracker disabled.
 */
(function (w) {
  w.LANDING_GA4_ID = null;          // TODO: set to "G-XXXXXXXXXX" when GA4 stream is created
  w.LANDING_WEBHOOK_URL = null;     // TODO: set to "https://..." when webhook endpoint is provisioned
})(window);
