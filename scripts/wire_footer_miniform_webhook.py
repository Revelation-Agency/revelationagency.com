"""
Wire the footer mini-form (.ra-footer__miniform) to POST submissions to the
GHL inbound webhook BEFORE redirecting to /booking.

Until now the handler stored name/phone in sessionStorage and redirected, so
leads that didn't complete the booking were silently lost.

This script replaces the inline submit handler in every HTML page (every
canonical footer block) with one that:
  1. Validates name + phone (unchanged)
  2. Fires a keepalive POST to the GHL inbound webhook with the lead
  3. Redirects to booking.html with prefill params 150 ms later — long
     enough for the request to leave the network stack, short enough that
     the user doesn't perceive a wait

Idempotent: matches the existing inline <script>(function(){...})();</script>
that sits immediately before <!-- RA-FOOTER-MINIFORM-END --> and replaces it.
Re-running the script swaps any prior version for the latest.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REPO = Path(__file__).resolve().parents[1]
GHL_WEBHOOK = (
    'https://services.leadconnectorhq.com/hooks/'
    'Jx498vFpyvZUSLnIfT0B/webhook-trigger/'
    'c6d7e341-7e3c-4dbb-a9df-ab8df070bbf4'
)
END_MARKER = '<!-- RA-FOOTER-MINIFORM-END -->'

# Match the inline handler block that lives directly above the END marker.
# Non-greedy across newlines — captures one <script>(function(){...})();</script>.
HANDLER_PATTERN = re.compile(
    r'<script>\(function\(\)\{.*?\}\)\(\);</script>\s*' + re.escape(END_MARKER),
    re.DOTALL,
)

NEW_HANDLER = (
    '<script>(function(){\n'
    "  var WEBHOOK = '" + GHL_WEBHOOK + "';\n"
    "  var forms = document.querySelectorAll('.ra-footer__miniform');\n"
    "  forms.forEach(function(f){\n"
    "    if (f.dataset.bound === '1') return;\n"
    "    f.dataset.bound = '1';\n"
    "    var status = f.querySelector('.ra-footer__miniform-status');\n"
    "    f.addEventListener('submit', function(ev){\n"
    "      ev.preventDefault();\n"
    "      var name = (f.name && f.name.value || '').trim();\n"
    "      var phone = (f.phone && f.phone.value || '').trim();\n"
    "      if (!name || !phone) {\n"
    "        if (status) {\n"
    "          status.textContent = 'Add a name and phone so we can prefill your booking.';\n"
    "          status.classList.add('is-error');\n"
    "        }\n"
    "        return;\n"
    "      }\n"
    "      try {\n"
    "        sessionStorage.setItem('ra_lead_name', name);\n"
    "        sessionStorage.setItem('ra_lead_phone', phone);\n"
    "        sessionStorage.setItem('ra_lead_source', 'footer-miniform');\n"
    "      } catch(e) {}\n"
    "      // Fire the lead at GHL BEFORE redirecting. keepalive: true tells the\n"
    "      // browser to keep the request alive through navigation so the lead\n"
    "      // is never lost if the user closes the tab or the booking page is\n"
    "      // slow to load.\n"
    "      var payload = {\n"
    "        name: name,\n"
    "        phone: phone,\n"
    "        source: 'footer-miniform',\n"
    "        page: (location.pathname || '/') + (location.search || ''),\n"
    "        referrer: document.referrer || '',\n"
    "        timestamp: new Date().toISOString(),\n"
    "        user_agent: navigator.userAgent || ''\n"
    "      };\n"
    "      try {\n"
    "        fetch(WEBHOOK, {\n"
    "          method: 'POST',\n"
    "          mode: 'cors',\n"
    "          headers: { 'Content-Type': 'application/json' },\n"
    "          body: JSON.stringify(payload),\n"
    "          keepalive: true\n"
    "        }).catch(function(err){ console.warn('[ra-footer-miniform] webhook error', err); });\n"
    "      } catch(e) {\n"
    "        console.warn('[ra-footer-miniform] webhook threw', e);\n"
    "      }\n"
    "      if (status) {\n"
    "        status.textContent = 'Got it — taking you to the calendar...';\n"
    "        status.classList.remove('is-error');\n"
    "      }\n"
    "      var base = f.getAttribute('data-booking-url') || 'booking.html';\n"
    "      var url = base + (base.indexOf('?') === -1 ? '?' : '&')\n"
    "        + 'name=' + encodeURIComponent(name)\n"
    "        + '&phone=' + encodeURIComponent(phone)\n"
    "        + '&src=footer-miniform';\n"
    "      // 150 ms is enough to push the keepalive request out of the local\n"
    "      // stack on every browser tested, but is imperceptible to the user.\n"
    "      setTimeout(function(){ window.location.href = url; }, 150);\n"
    "    });\n"
    "  });\n"
    "})();</script>\n"
    + END_MARKER
)


def main():
    written = 0
    unchanged = 0
    skipped = 0
    skipped_files = []
    for root, dirs, files in os.walk(REPO):
        parts = root.split(os.sep)
        if any(p in ('.git', 'node_modules', 'scripts', '.vercel') for p in parts):
            continue
        for fn in files:
            if not fn.endswith('.html'):
                continue
            full = os.path.join(root, fn)
            with open(full, 'r', encoding='utf-8') as f:
                text = f.read()
            if END_MARKER not in text:
                skipped += 1
                skipped_files.append(os.path.relpath(full, REPO).replace(os.sep, '/'))
                continue
            new_text, n_subs = HANDLER_PATTERN.subn(NEW_HANDLER, text, count=1)
            if n_subs == 0:
                # Marker present but our handler shape didn't match (weird).
                skipped += 1
                skipped_files.append(
                    os.path.relpath(full, REPO).replace(os.sep, '/')
                    + ' (no handler block matched)'
                )
                continue
            if new_text == text:
                unchanged += 1
                continue
            with open(full, 'w', encoding='utf-8') as f:
                f.write(new_text)
            written += 1
    print(f'Written: {written}, Unchanged: {unchanged}, Skipped: {skipped}')
    if skipped_files:
        print('Skipped files:')
        for s in skipped_files:
            print(f'  {s}')


if __name__ == '__main__':
    main()
