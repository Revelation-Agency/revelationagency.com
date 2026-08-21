#!/usr/bin/env python3
"""Insert a Locations column into the canonical footer on every page.

Without this the /locations tree is orphaned: it is in the sitemap but nothing
links to it, and orphaned pages do not accrue internal authority. One column,
inserted immediately before the existing Connect column, gives every page a
crawl path to the four city hubs, which in turn link to the 24 service x city
pages.

Two footer variants exist in the tree: a plain `<h5>Connect</h5>` and one
carrying an inline style attribute. The inserted column copies whichever h5
attributes the page already uses, so it matches that page visually instead of
introducing a third variant.

Idempotent: refuses to insert twice.
"""
from __future__ import annotations
import io, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CITIES = [("clovis-ca", "Clovis, CA"), ("fresno-ca", "Fresno, CA"),
          ("madera-ca", "Madera, CA"), ("visalia-ca", "Visalia, CA")]

# Matches the Connect column opener in both variants, capturing the h5's attrs.
PAT = re.compile(
    r'(?P<indent>[ \t]*)<div class="ra-footer__nav">\s*\n'
    r'(?P<h5indent>[ \t]*)<h5(?P<attrs>[^>]*)>Connect</h5>'
)


def block(indent: str, h5indent: str, attrs: str) -> str:
    items = "\n".join(
        f'{h5indent}  <li><a href="/locations/{slug}">{label}</a></li>'
        for slug, label in CITIES
    )
    return (
        f'{indent}<div class="ra-footer__nav">\n'
        f'{h5indent}<h5{attrs}>Locations</h5>\n'
        f'{h5indent}<ul>\n'
        f'{items}\n'
        f'{h5indent}  <li><a href="/locations">All locations</a></li>\n'
        f'{h5indent}</ul>\n'
        f'{indent}</div>\n\n'
    )


def main() -> int:
    changed = skipped = missing = 0
    for p in sorted(REPO.rglob("*.html")):
        if any(part in {".git", "artifacts", "node_modules"} for part in p.parts):
            continue
        s = io.open(p, encoding="utf-8").read()
        if ">Locations</h5>" in s:
            skipped += 1
            continue
        m = PAT.search(s)
        if not m:
            missing += 1
            continue
        ins = block(m.group("indent"), m.group("h5indent"), m.group("attrs"))
        s = s[:m.start()] + ins + s[m.start():]
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        changed += 1
    print(f"inserted: {changed} | already present: {skipped} | no Connect column: {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
