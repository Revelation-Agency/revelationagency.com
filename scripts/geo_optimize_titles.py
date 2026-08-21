#!/usr/bin/env python3
"""Put the market into the title tags of the two highest-intent pages.

Audit finding: the homepage title carried no city, state, or region, while
both ranking clients lead their title with the market ("Sign Company Clovis &
Fresno CA", "Solar Installation in Fresno & Clovis, CA"). The contact page --
the highest local-intent page on the site -- was titled "Contact".

Only these two pages are touched. Geo-stamping every title would read as
keyword stuffing; the /locations tree is what carries geo depth.

Rewrites title, og:title, twitter:title, description, og:description and
twitter:description together so the social preview cannot disagree with the
SERP snippet. Idempotent.
"""
from __future__ import annotations
import html, io, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

EDITS = {
    "index.html": {
        "title": "Marketing Agency in Clovis & Fresno, CA | Revelation Agency",
        "desc": ("Marketing agency in Clovis and Fresno, CA. Branding, websites, SEO, "
                 "Google Ads, social, and video built as one system that compounds."),
    },
    "contact.html": {
        "title": "Contact | Marketing Agency in Clovis & Fresno, CA",
        "desc": ("Talk to Revelation Agency in Clovis, CA. Tell us about the business, "
                 "the goal, and the timeline, and we will tell you whether we are the right fit."),
    },
}

PATTERNS = [
    ("title", r"(<title>).*?(</title>)"),
    ("title", r'(<meta property="og:title" content=")[^"]*(")'),
    ("title", r'(<meta name="twitter:title" content=")[^"]*(")'),
    ("desc", r'(<meta name="description" content=")[^"]*(")'),
    ("desc", r'(<meta property="og:description" content=")[^"]*(")'),
    ("desc", r'(<meta name="twitter:description" content=")[^"]*(")'),
]


def main() -> int:
    for name, vals in EDITS.items():
        p = REPO / name
        s = io.open(p, encoding="utf-8").read()
        if vals["title"].replace("&", "&amp;") in s or vals["title"] in s:
            print(f"{name}: already applied")
            continue
        for key, pat in PATTERNS:
            repl = html.escape(vals[key], quote=True)
            s, n = re.subn(pat, lambda m, r=repl: m.group(1) + r + m.group(2),
                           s, count=1, flags=re.S)
            if n == 0:
                print(f"  {name}: pattern not found -> {pat[:44]}")
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        print(f"{name}: title -> {vals['title']} ({len(vals['title'])} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
