#!/usr/bin/env python3
"""Register the new SEO case studies in the portfolio taxonomy and grid.

Adds three routes to assets/data/portfolio-taxonomy-2026.json and one master
card to portfolio.html for Shepherd Cleaning Solutions, which had no portfolio
presence at all. Idempotent.
"""
from __future__ import annotations
import io, json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TAX = REPO / "assets" / "data" / "portfolio-taxonomy-2026.json"
GRID = REPO / "portfolio.html"

NEW_CASES = {
    "/portfolio/case-studies/shepherd-cleaning-solutions-seo.html": {
        "project": "Shepherd Cleaning Solutions",
        "pageKind": "caseStudyDiscipline",
        "primaryDiscipline": "M1",
        "disciplines": ["M1"],
        "pillars": ["Marketing"],
        "aiAutomation": False,
        "mappingRationale": "Audited route evidence maps this case study to M1 SEO / AI Answers.",
    },
    "/portfolio/case-studies/excel-sign-company-seo.html": {
        "project": "Excel Sign Company",
        "pageKind": "caseStudyDiscipline",
        "primaryDiscipline": "M1",
        "disciplines": ["M1"],
        "pillars": ["Marketing"],
        "aiAutomation": False,
        "mappingRationale": "Audited route evidence maps this case study to M1 SEO / AI Answers.",
    },
}
# The master page lives in portfolio/case-studies/, so it is BOTH a case-study
# file (needs a caseStudiesByRoute record) and a portfolio grid card (needs a
# masterCardsByRoute record). Existing master projects follow the same pattern.
NEW_CASES["/portfolio/case-studies/shepherd-cleaning-solutions.html"] = {
    "project": "Shepherd Cleaning Solutions",
    "pageKind": "masterPortfolioCard",
    "primaryDiscipline": "B3",
    "disciplines": ["B1", "B3", "M1"],
    "pillars": ["Branding", "Marketing"],
    "aiAutomation": False,
    "mappingRationale": "Master card inherits audited project evidence for B3 Brand Identity, B1 Websites, and M1 SEO / AI Answers.",
}

NEW_MASTER = {
    "/portfolio/case-studies/shepherd-cleaning-solutions.html": {
        "project": "Shepherd Cleaning Solutions",
        "pageKind": "masterPortfolioCard",
        "primaryDiscipline": "B3",
        "disciplines": ["B1", "B3", "M1"],
        "pillars": ["Branding", "Marketing"],
        "aiAutomation": False,
        "mappingRationale": "Master card inherits audited project evidence for B3 Brand Identity, B1 Websites, and M1 SEO / AI Answers.",
    },
}

CARD = '''        <a class="pf-card fade-up" data-cat="branding marketing" href="/portfolio/case-studies/shepherd-cleaning-solutions" data-pillars="branding marketing" data-disciplines="B1 B3 M1" data-ai="false">
          <div class="pf-card__bg" style="background:url('/assets/img/portfolio/shepherd-cleaning-solutions/thumbnail.png') center/cover no-repeat;opacity:1;" data-taxonomy="BRANDING &middot; MARKETING"></div>
          <span class="pf-card__label">Branding &middot; Marketing</span>
          <span class="pf-card__status">Case Study</span>
          <div class="pf-card__body">
            <h3 class="pf-card__title">Shepherd Cleaning Solutions</h3>
            <p class="pf-card__desc">Premium B2B commercial cleaning brand built from zero &mdash; identity, website, and the AI answer visibility that gets it named in Clovis.</p>
          </div>
        </a>
'''


def main() -> int:
    d = json.loads(io.open(TAX, encoding="utf-8").read())
    added = 0
    for route, rec in NEW_CASES.items():
        if route not in d["caseStudiesByRoute"]:
            d["caseStudiesByRoute"][route] = {"route": route, **rec}
            added += 1
    for route, rec in NEW_MASTER.items():
        if route not in d["masterCardsByRoute"]:
            d["masterCardsByRoute"][route] = {"route": route, **rec}
            added += 1
    d["caseStudiesByRoute"] = dict(sorted(d["caseStudiesByRoute"].items()))
    d["masterCardsByRoute"] = dict(sorted(d["masterCardsByRoute"].items()))
    d["summary"]["caseStudyRecords"] = len(d["caseStudiesByRoute"])
    d["summary"]["masterPortfolioCardRecords"] = len(d["masterCardsByRoute"])
    d["summary"]["totalRecords"] = (d["summary"]["caseStudyRecords"]
                                    + d["summary"]["masterPortfolioCardRecords"])
    io.open(TAX, "w", encoding="utf-8", newline="").write(json.dumps(d, indent=2) + "\n")
    print(f"taxonomy: +{added} records -> cases={d['summary']['caseStudyRecords']} "
          f"masters={d['summary']['masterPortfolioCardRecords']}")

    g = io.open(GRID, encoding="utf-8").read()
    if "shepherd-cleaning-solutions" in g:
        print("portfolio.html: Shepherd card already present")
    else:
        m = re.search(r'[ \t]*<a class="pf-card fade-up"', g)
        if not m:
            print("ERROR: no pf-card anchor found in portfolio.html")
            return 1
        g = g[:m.start()] + CARD + g[m.start():]
        io.open(GRID, "w", encoding="utf-8", newline="").write(g)
        print("portfolio.html: Shepherd master card inserted")
    for shelf in ("portfolio/branding.html", "portfolio/marketing.html"):
        sp = REPO / shelf
        t = io.open(sp, encoding="utf-8").read()
        if "shepherd-cleaning-solutions" in t:
            print(f"{shelf}: already present")
            continue
        mm = re.search(r'[ 	]*<a class="pf-card fade-up"', t)
        if not mm:
            print(f"ERROR: no pf-card anchor in {shelf}")
            return 1
        t = t[:mm.start()] + CARD + t[mm.start():]
        io.open(sp, "w", encoding="utf-8", newline="").write(t)
        print(f"{shelf}: Shepherd card inserted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
