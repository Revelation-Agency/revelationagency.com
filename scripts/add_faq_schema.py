#!/usr/bin/env python3
"""Emit FAQPage JSON-LD on faq.html from the questions actually on the page.

The FAQ page carried no structured data at all. FAQPage markup is the single
highest-leverage schema for AI answer engines, which quote answer text
directly -- but only when the markup matches what a visitor can see. This
extracts the rendered Q/A pairs rather than authoring a parallel set, so the
schema cannot drift from the page or misrepresent it.

Idempotent.
"""
from __future__ import annotations
import html, io, json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAGE = REPO / "faq.html"

Q_PAT = re.compile(
    r'<button class="faq-item__q".*?<span style="flex:1;">(?P<q>.*?)</span>'
    r'.*?<div class="faq-item__a-inner">(?P<a>.*?)</div>', re.S)


def clean(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    s = io.open(PAGE, encoding="utf-8").read()
    if '"@type": "FAQPage"' in s:
        print("FAQPage schema already present; nothing to do")
        return 0
    pairs = [(clean(m.group("q")), clean(m.group("a"))) for m in Q_PAT.finditer(s)]
    pairs = [(q, a) for q, a in pairs if q and a]
    if not pairs:
        print("ERROR: no Q/A pairs found - refusing to emit empty schema")
        return 1
    node = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }
    block = ('<script type="application/ld+json">\n'
             + json.dumps(node, indent=2) + "\n</script>\n")
    s = s.replace("</head>", block + "</head>", 1)
    io.open(PAGE, "w", encoding="utf-8", newline="").write(s)
    print(f"emitted FAQPage with {len(pairs)} questions")
    for q, _ in pairs:
        print("   ", q[:78])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
