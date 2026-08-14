"""Verify that every GHL/mailto/tel/booking snippet hashed at baseline still
exists byte-identically in the current tree.

Exits non-zero on the first divergence.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BASELINE = "artifacts/baseline-integration-hashes.json"

PATTERNS = {
    "contact_form_element": r'<form[^>]*id="ra-contact-form"[^>]*>',
    "footer_mini_webhook_line": r"var\s+WEBHOOK\s*=\s*[\"'][^\"'\s]+[\"'];",
    "booking_iframe": r'<iframe[^>]*api\.leadconnectorhq\.com/widget/booking[^>]*></iframe>',
    "booking_embed_script": r'<script[^>]*link\.msgsndr\.com/js/form_embed\.js[^>]*>',
    "chat_widget_loader": r'<script[^>]*widgets\.leadconnectorhq\.com/loader\.js[^>]*></script>',
    "mailto_connect": r"mailto:connect@revelationagency\.com",
    "tel_link": r"tel:\+?15592017039",
}


def sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def current_hashes(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    return {k: sha16(re.search(pat, data).group(0))
            for k, pat in PATTERNS.items()
            if re.search(pat, data)}


def main() -> int:
    with open(BASELINE, "r", encoding="utf-8") as f:
        baseline = json.load(f)["integration_snippet_hashes"]

    fail = 0
    for page, snips in baseline.items():
        if not os.path.exists(page):
            print(f"[FAIL] {page} disappeared")
            fail += 1
            continue
        now = current_hashes(page)
        for k, h in snips.items():
            got = now.get(k)
            if got != h:
                print(f"[FAIL] {page}:{k} baseline={h} current={got}")
                fail += 1
            else:
                print(f"[OK]   {page}:{k}")
    if fail:
        print(f"\n{fail} integration snippet divergence(s) — refusing to declare preservation.")
        return 2
    print("\nAll baseline integration snippets preserved byte-identically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
