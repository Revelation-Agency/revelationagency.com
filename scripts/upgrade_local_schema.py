#!/usr/bin/env python3
"""Upgrade the sitewide Organization JSON-LD to a full LocalBusiness entity.

Audit finding (21 Aug 2026): revelationagency.com emitted a bare Organization
node with a postal address and nothing else -- no @id, no geo, no areaServed,
no hours, no service catalogue -- while both ranking clients emit LocalBusiness
with geo and AggregateRating. The agency has a real Clovis address it was not
using as a ranking signal.

This rewrites that node to ProfessionalService (a LocalBusiness subtype, the
accurate type for a marketing agency) and adds:

  @id                        stable entity node so every page references one
                             business rather than asserting a new one
  geo                        GeoCoordinates for the Clovis office
  areaServed                 the four served cities
  openingHoursSpecification  local pack signal
  priceRange                 local pack signal
  hasOfferCatalog            enumerates services, which is what AI answer
                             engines read to state what the business does

Deliberately NOT added: AggregateRating. Review markup must reflect real
collected reviews; inventing one is both a Google penalty and a lie.

Idempotent.
"""
from __future__ import annotations
import io, json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CANON = "https://www.revelationagency.com"
CITIES = ["Clovis, CA", "Fresno, CA", "Madera, CA", "Visalia, CA"]
SERVICES = ["Branding", "Web Design", "SEO", "Google Ads Management",
            "Social Media Marketing", "Video Production"]


def upgraded(old: dict) -> dict:
    node = dict(old)
    node["@type"] = "ProfessionalService"
    node["@id"] = CANON + "/#organization"
    node.setdefault("image", CANON + "/assets/brand/current/ra-social-card.png")
    node["geo"] = {"@type": "GeoCoordinates", "latitude": 36.8252, "longitude": -119.7029}
    node["areaServed"] = [{"@type": "City", "name": c} for c in CITIES]
    node["priceRange"] = "$$"
    node["openingHoursSpecification"] = [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "09:00", "closes": "17:00",
    }]
    node["hasOfferCatalog"] = {
        "@type": "OfferCatalog", "name": "Services",
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}}
            for s in SERVICES
        ],
    }
    return node


def main() -> int:
    changed = skipped = 0
    pat = re.compile(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', re.S)
    for p in sorted(REPO.rglob("*.html")):
        if any(x in {".git", "artifacts", "node_modules"} for x in p.parts):
            continue
        s = io.open(p, encoding="utf-8").read()
        out, hit = [], False
        pos = 0
        for m in pat.finditer(s):
            try:
                node = json.loads(m.group(1))
            except Exception:
                continue
            if node.get("@type") != "Organization" or node.get("name") != "Revelation Agency":
                continue
            new = json.dumps(upgraded(node), indent=2)
            out.append(s[pos:m.start(1)]); out.append(new)
            pos = m.end(1); hit = True
        if not hit:
            skipped += 1
            continue
        out.append(s[pos:])
        io.open(p, "w", encoding="utf-8", newline="").write("".join(out))
        changed += 1
    print(f"upgraded: {changed} pages | untouched: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
