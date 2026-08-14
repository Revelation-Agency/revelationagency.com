"""Baseline snapshot: capture hashes of load-bearing files and integration snippets.

Runs before any edit so that integration-preservation tests can compare later.
Endpoints are HASHED (16-char sha256), never written in cleartext to artifacts.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def hf(p: str) -> str:
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


TOP_FILES = [
    "index.html",
    "contact.html",
    "booking.html",
    "faq.html",
    "about.html",
    "services.html",
    "portfolio.html",
    "web-hosting.html",
    "404.html",
    "sitemap.xml",
    "robots.txt",
    "vercel.json",
    "assets/js/contact-form.js",
    "assets/js/landing-tracker.js",
    "assets/js/landing-config.js",
    "assets/js/portfolio-data.js",
]


INTEGRATION_PATTERNS = {
    "contact_form_element": r'<form[^>]*id="ra-contact-form"[^>]*>',
    "footer_mini_webhook_line": r"var\s+WEBHOOK\s*=\s*[\"'][^\"'\s]+[\"'];",
    "booking_iframe": r'<iframe[^>]*api\.leadconnectorhq\.com/widget/booking[^>]*></iframe>',
    "booking_embed_script": r'<script[^>]*link\.msgsndr\.com/js/form_embed\.js[^>]*>',
    "chat_widget_loader": r'<script[^>]*widgets\.leadconnectorhq\.com/loader\.js[^>]*></script>',
    "mailto_connect": r"mailto:connect@revelationagency\.com",
    "tel_link": r"tel:\+?15592017039",
}


PAGES_TO_HASH = [
    "index.html", "contact.html", "booking.html", "faq.html", "about.html",
    "services.html", "portfolio.html", "web-hosting.html", "404.html",
]


def snippet_hashes(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    res = {}
    for k, pat in INTEGRATION_PATTERNS.items():
        m = re.search(pat, data)
        if m:
            res[k] = h(m.group(0))
    return res


def main() -> int:
    out = {
        "generated_at": "2026-08-14",
        "base_sha": "4a0b076c37189216a263dfab5c481464cf251a96",
        "branch": "claude/p5-branding-marketing-sales-rebrand",
        "file_sha256": {},
        "integration_snippet_hashes": {},
        "notes": [
            "Endpoint identifiers are hashed with sha256 (first 16 hex). Never printed cleartext.",
            "integration-preservation tests re-run this and compare against baseline.",
        ],
    }
    for p in TOP_FILES:
        if os.path.exists(p):
            out["file_sha256"][p] = hf(p)
    for p in PAGES_TO_HASH:
        if os.path.exists(p):
            out["integration_snippet_hashes"][p] = snippet_hashes(p)
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/baseline-integration-hashes.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("wrote artifacts/baseline-integration-hashes.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
