#!/usr/bin/env python3
"""Verify the Revelation Agency portfolio taxonomy v2 without mutating files."""

from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "data" / "portfolio-taxonomy-2026.json"

EXPECTED_TAXONOMY = {
    "B1": "Websites",
    "B2": "Apps",
    "B3": "Brand Identity",
    "B4": "Design",
    "B5": "Video",
    "M1": "SEO / AI Answers",
    "M2": "Social Media",
    "M3": "Digital Advertising",
    "M4": "Customer Nurture",
    "S1": "Outreach",
    "S2": "Lead Gen Ads",
    "S3": "CRMs / Sales Tools",
    "S4": "AI Automation Systems",
}

DISCIPLINE_LINKS = {
    "B1": "/services/branding/websites-landing-pages",
    "B2": "/services/branding/apps-digital-products",
    "B3": "/services/branding/brand-strategy-identity",
    "B4": "/services/branding/design",
    "B5": "/services/branding/video-visual-content",
    "M1": "/services/marketing/seo-ai-visibility",
    "M2": "/services/marketing/social-media",
    "M3": "/services/marketing/digital-ads",
    "M4": "/services/marketing/email-lifecycle-marketing",
    "S1": "/services/sales/lead-generation-outreach",
    "S2": "/services/sales/lead-gen-ads",
    "S3": "/services/sales/crm-sales-infrastructure",
    "S4": "/services/sales/ai-automation-systems",
}

EXPECTED_CASE_COUNTS = {
    "B1": 20, "B2": 8, "B3": 21, "B4": 13, "B5": 21,
    "M1": 7, "M2": 6, "M3": 14, "M4": 12,
    "S1": 0, "S2": 8, "S3": 17, "S4": 14,
}
EXPECTED_MASTER_COUNTS = {
    "B1": 12, "B2": 5, "B3": 10, "B4": 6, "B5": 12,
    "M1": 6, "M2": 3, "M3": 8, "M4": 7,
    "S1": 0, "S2": 8, "S3": 10, "S4": 8,
}
EXPECTED_PILLAR_COUNTS = {"Branding": 21, "Marketing": 13, "Sales": 11}
PUBLIC_PILLAR_LABEL = {"Branding": "Branding", "Marketing": "Marketing", "Sales": "Sales Systems"}
EXPECTED_PILLAR_DESCRIPTIONS = {
    "Branding": "Websites, Apps, Brand Identity, Design, and Video — the surfaces where the market meets the business.",
    "Marketing": "SEO / AI Answers, Social Media, Digital Advertising, and Customer Nurture connected to a measurable next step.",
    "Sales": "Outreach, Lead Gen Ads, CRMs / Sales Tools, and AI Automation Systems — built so demand has somewhere disciplined to go.",
}
EXPECTED_DESIGN_CASES = {
    "/portfolio/case-studies/ams-energy-solutions-branding.html",
    "/portfolio/case-studies/ams-energy-solutions.html",
    "/portfolio/case-studies/hope-now-for-youth-branding.html",
    "/portfolio/case-studies/hope-now-for-youth-video.html",
    "/portfolio/case-studies/hope-now-for-youth.html",
    "/portfolio/case-studies/infinite-heating-cooling-branding.html",
    "/portfolio/case-studies/infinite-heating-cooling.html",
    "/portfolio/case-studies/infinite-roofing-solutions-branding.html",
    "/portfolio/case-studies/infinite-roofing-solutions.html",
    "/portfolio/case-studies/ivory-pools-branding.html",
    "/portfolio/case-studies/ivory-pools.html",
    "/portfolio/case-studies/risen-sun-solar-roofing-branding.html",
    "/portfolio/case-studies/risen-sun-solar-roofing.html",
}
PILLAR_BY_PREFIX = {"B": "Branding", "M": "Marketing", "S": "Sales"}
PILLAR_ORDER = ("Branding", "Marketing", "Sales")


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self._active: dict[str, str] | None = None
        self._text: list[str] = []
        self._active_tag = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "a" and "pf-card" in values.get("class", "").split():
            self.anchors.append(values)
        if tag == "button" and "pf-filter-btn" in values.get("class", "").split():
            self._active = values
            self._text = []
            self._active_tag = tag

    def handle_data(self, data: str) -> None:
        if self._active is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._active is not None and tag == self._active_tag:
            self._active["_text"] = " ".join(" ".join(self._text).split())
            self.buttons.append(self._active)
            self._active = None
            self._text = []
            self._active_tag = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def route_from_href(href: str) -> str:
    route = urlsplit(href).path
    if not route.endswith(".html"):
        route += ".html"
    return route


def parse_attrs(opening: str) -> dict[str, str]:
    return {
        key.lower(): html.unescape(value)
        for key, _, value in re.findall(r'([\w:-]+)\s*=\s*(["\'])(.*?)\2', opening, re.S)
    }


def strip_shared_chrome(text: str) -> str:
    return re.sub(r'<(?:nav|footer)\b.*?</(?:nav|footer)>', "", text, flags=re.I | re.S)


def taxonomy_block(text: str, marker: str, tag_pattern: str) -> str | None:
    match = re.search(
        rf'<!-- {re.escape(marker)} -->\s*({tag_pattern})',
        text,
        re.I | re.S,
    )
    return match.group(1) if match else None


def check_manifest(data: dict, errors: list[str]) -> tuple[dict, dict]:
    if data.get("schemaVersion") != "2026-08-17-v2":
        errors.append(f"manifest schemaVersion is {data.get('schemaVersion')!r}")
    if data.get("taxonomy") != EXPECTED_TAXONOMY:
        errors.append("manifest taxonomy/order does not exactly match the corrected 5/4/4 contract")
    architecture = str(data.get("summary", {}).get("architecture", ""))
    for title in EXPECTED_TAXONOMY.values():
        if title not in architecture:
            errors.append(f"manifest architecture omits exact title {title!r}")
    if re.search(r"cross[- ]?cut", architecture, re.I):
        errors.append("manifest architecture still calls AI cross-cutting")

    cases = data.get("caseStudiesByRoute", {})
    masters = data.get("masterCardsByRoute", {})
    if len(cases) != 68:
        errors.append(f"manifest has {len(cases)} case records, expected 68")
    if len(masters) != 21:
        errors.append(f"manifest has {len(masters)} master records, expected 21")
    physical = {"/" + path.relative_to(ROOT).as_posix() for path in (ROOT / "portfolio/case-studies").glob("*.html")}
    if set(cases) != physical:
        errors.append(f"manifest/physical case route mismatch: missing={sorted(physical-set(cases))}, extra={sorted(set(cases)-physical)}")

    for kind, records in (("case", cases), ("master", masters)):
        for route, record in records.items():
            if record.get("route") != route:
                errors.append(f"{route}: embedded route mismatch")
            disciplines = record.get("disciplines")
            if not isinstance(disciplines, list) or not disciplines:
                errors.append(f"{route}: disciplines must be a nonempty list")
                continue
            if disciplines != [code for code in EXPECTED_TAXONOMY if code in disciplines]:
                errors.append(f"{route}: disciplines are not unique and in canonical order")
            unknown = sorted(set(disciplines) - set(EXPECTED_TAXONOMY))
            if unknown:
                errors.append(f"{route}: unknown disciplines {unknown}")
            if record.get("primaryDiscipline") not in disciplines:
                errors.append(f"{route}: primaryDiscipline is not in disciplines")
            expected_pillars = [
                pillar for pillar in PILLAR_ORDER
                if any(PILLAR_BY_PREFIX.get(code[0]) == pillar for code in disciplines)
            ]
            if record.get("pillars") != expected_pillars:
                errors.append(f"{route}: pillars {record.get('pillars')} do not derive from disciplines {disciplines}")
            if not isinstance(record.get("aiAutomation"), bool):
                errors.append(f"{route}: aiAutomation is not boolean")
            if "S4" in disciplines and not record.get("aiAutomation"):
                errors.append(f"{route}: S4 requires delivered automation metadata")
            rationale = str(record.get("mappingRationale", ""))
            if not rationale:
                errors.append(f"{route}: missing mappingRationale")
            if re.search(r"cross[- ]?cut", rationale, re.I):
                errors.append(f"{route}: rationale calls AI cross-cutting")

    case_counts = Counter(code for record in cases.values() for code in record["disciplines"])
    master_counts = Counter(code for record in masters.values() for code in record["disciplines"])
    if {code: case_counts[code] for code in EXPECTED_TAXONOMY} != EXPECTED_CASE_COUNTS:
        errors.append(f"case discipline counts drifted: {dict(case_counts)}")
    if {code: master_counts[code] for code in EXPECTED_TAXONOMY} != EXPECTED_MASTER_COUNTS:
        errors.append(f"master discipline counts drifted: {dict(master_counts)}")
    design_cases = {route for route, record in cases.items() if "B4" in record["disciplines"]}
    if design_cases != EXPECTED_DESIGN_CASES:
        errors.append(f"Design evidence set drifted: missing={sorted(EXPECTED_DESIGN_CASES-design_cases)}, extra={sorted(design_cases-EXPECTED_DESIGN_CASES)}")
    if any("S1" in record["disciplines"] for record in (*cases.values(), *masters.values())):
        errors.append("Outreach has an assignment despite no audited outbound-delivery evidence")
    return cases, masters


def check_case_pages(cases: dict, errors: list[str]) -> None:
    old_generated_labels = (
        "Brand Strategy &amp; Identity", "Websites &amp; Landing Pages",
        "Apps &amp; Digital Products", "Video &amp; Visual Content",
        "SEO &amp; AI Visibility", "Positioning, Content &amp; Authority",
        "Email &amp; Lifecycle Marketing", "Lead Generation &amp; Personalized Outreach",
        "CRM &amp; Sales Infrastructure", "Follow-up &amp; Nurture", "Conversion Advertising",
    )
    for route, record in cases.items():
        text = read(ROOT / route.lstrip("/"))
        body_match = re.search(r"<body\b[^>]*>", text, re.I)
        if not body_match:
            errors.append(f"{route}: missing body")
            continue
        attrs = parse_attrs(body_match.group(0))
        expected_attrs = {
            "data-ra-page-kind": record["pageKind"],
            "data-ra-project": record["project"],
            "data-ra-pillars": " ".join(pillar.lower() for pillar in record["pillars"]),
            "data-ra-disciplines": " ".join(record["disciplines"]),
            "data-ra-ai": str(record["aiAutomation"]).lower(),
        }
        for key, value in expected_attrs.items():
            if attrs.get(key) != value:
                errors.append(f"{route}: {key}={attrs.get(key)!r}, expected {value!r}")

        if text.count("<!-- RA-PORTFOLIO-TAXONOMY:visible -->") != 1:
            errors.append(f"{route}: visible taxonomy marker count is not 1")
        visible = taxonomy_block(
            text,
            "RA-PORTFOLIO-TAXONOMY:visible",
            r'<div class="ra-case-taxonomy".*?</div>',
        )
        if visible is None:
            errors.append(f"{route}: visible taxonomy block is missing")
        else:
            chips = re.findall(
                r'<a href="([^"]+)" class="ra-case-taxonomy__chip" title="([^"]+)"><span>([^<]+)</span>([^<]+)</a>',
                visible,
                re.S,
            )
            expected_chips = [
                (DISCIPLINE_LINKS[code], f"{code} · {EXPECTED_TAXONOMY[code]}", code, EXPECTED_TAXONOMY[code])
                for code in record["disciplines"]
            ]
            decoded = [tuple(html.unescape(value) for value in chip) for chip in chips]
            if decoded != expected_chips:
                errors.append(f"{route}: visible chips do not exactly match manifest: {decoded}")
            if "Cross-cutting" in visible or "ra-case-taxonomy__chip--ai" in visible:
                errors.append(f"{route}: old cross-cutting AI chip remains")
            for old in old_generated_labels:
                if old in visible:
                    errors.append(f"{route}: old taxonomy label remains in generated chips: {old}")

        if text.count("<!-- RA-PORTFOLIO-TAXONOMY:jsonld -->") != 1:
            errors.append(f"{route}: taxonomy JSON-LD marker count is not 1")
        json_block = taxonomy_block(
            text,
            "RA-PORTFOLIO-TAXONOMY:jsonld",
            r'<script type="application/ld\+json">.*?</script>',
        )
        if json_block is None:
            errors.append(f"{route}: taxonomy JSON-LD is missing")
        else:
            raw = re.search(r">(.*)</script>", json_block, re.S).group(1)
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{route}: invalid taxonomy JSON-LD: {exc}")
            else:
                expected_about = [EXPECTED_TAXONOMY[code] for code in record["disciplines"]]
                if payload.get("about") != expected_about:
                    errors.append(f"{route}: JSON-LD about={payload.get('about')}, expected {expected_about}")
                expected_keywords = [PUBLIC_PILLAR_LABEL[pillar] for pillar in record["pillars"]]
                expected_keywords += (["AI-enabled"] if record["aiAutomation"] else [])
                if payload.get("keywords") != expected_keywords:
                    errors.append(f"{route}: JSON-LD keywords={payload.get('keywords')}, expected {expected_keywords}")

        if re.search(r"cross[- ]?cut", strip_shared_chrome(text), re.I):
            errors.append(f"{route}: case-owned content still calls AI cross-cutting")


def check_card_attrs(route: str, attrs: dict[str, str], record: dict, label: str, errors: list[str]) -> None:
    expected = {
        "data-cat": " ".join(pillar.lower() for pillar in record["pillars"]),
        "data-pillars": " ".join(pillar.lower() for pillar in record["pillars"]),
        "data-disciplines": " ".join(record["disciplines"]),
        "data-ai": str(record["aiAutomation"]).lower(),
    }
    for key, value in expected.items():
        if attrs.get(key) != value:
            errors.append(f"{label} {route}: {key}={attrs.get(key)!r}, expected {value!r}")


def check_portfolio_hub(masters: dict, errors: list[str]) -> None:
    text = read(ROOT / "portfolio.html")
    parser = AnchorParser()
    parser.feed(text)
    routes = [route_from_href(attrs.get("href", "")) for attrs in parser.anchors]
    if len(routes) != len(set(routes)) or set(routes) != set(masters):
        errors.append(f"portfolio.html card membership differs from manifest: {routes}")
    for route, attrs in zip(routes, parser.anchors):
        if route in masters:
            check_card_attrs(route, attrs, masters[route], "portfolio.html", errors)

    expected_filters = ["all", "branding", "marketing", "sales"] + [code.lower() for code in EXPECTED_TAXONOMY]
    actual_filters = [button.get("data-filter") for button in parser.buttons]
    if actual_filters != expected_filters:
        errors.append(f"portfolio filter order is {actual_filters}, expected {expected_filters}")
    master_counts = Counter(code for record in masters.values() for code in record["disciplines"])
    pillar_counts = Counter(pillar for record in masters.values() for pillar in record["pillars"])
    expected_button_values = {
        "all": ("All Work", len(masters)),
        **{pillar.lower(): (PUBLIC_PILLAR_LABEL[pillar], pillar_counts[pillar]) for pillar in PILLAR_ORDER},
        **{code.lower(): (title, master_counts[code]) for code, title in EXPECTED_TAXONOMY.items()},
    }
    for button in parser.buttons:
        key = button.get("data-filter", "")
        label, count = expected_button_values.get(key, ("", -1))
        if button.get("_text") != f"{label} {count}":
            errors.append(f"portfolio filter {key!r} text is {button.get('_text')!r}, expected {label!r} + {count}")

    for token in (
        "/* RA-PORTFOLIO-SERVICE-FILTERS:START */",
        "/* RA-PORTFOLIO-SERVICE-FILTERS:END */",
        "// RA-PORTFOLIO-FILTERS:START",
        "// RA-PORTFOLIO-FILTERS:END",
        "function portfolioFilterMatches(card, filter)",
        "data-disciplines",
        "id=\"pf-filter-status\" aria-live=\"polite\"",
    ):
        if text.count(token) != 1 and token != "data-disciplines":
            errors.append(f"portfolio.html: expected one {token!r}, found {text.count(token)}")
        elif token == "data-disciplines" and text.count(token) < len(masters):
            errors.append("portfolio.html: discipline filtering is not wired to every card")
    if re.search(r"cross[- ]?cut", strip_shared_chrome(text), re.I):
        errors.append("portfolio.html: portfolio-owned content calls AI cross-cutting")

    for route, record in masters.items():
        pattern = re.compile(
            rf'<a\b[^>]*class="[^"]*\bpf-card\b[^"]*"[^>]*href="{re.escape(route.removesuffix(".html"))}"[^>]*>.*?</a>',
            re.I | re.S,
        )
        match = pattern.search(text)
        if not match:
            errors.append(f"portfolio.html: cannot inspect card block for {route}")
            continue
        block = match.group(0)
        expected_label = " · ".join(PUBLIC_PILLAR_LABEL[pillar] for pillar in record["pillars"])
        label_match = re.search(r'<span class="pf-card__label">(.*?)</span>', block, re.S)
        if not label_match or html.unescape(label_match.group(1)) != expected_label:
            errors.append(f"portfolio.html: {route} public card label is not {expected_label!r}")
        tax_match = re.search(r'data-taxonomy="([^"]+)"', block)
        expected_taxonomy = expected_label.upper()
        if not tax_match or html.unescape(tax_match.group(1)) != expected_taxonomy:
            errors.append(f"portfolio.html: {route} thumbnail taxonomy is not {expected_taxonomy!r}")


def check_shelves(masters: dict, errors: list[str]) -> None:
    for pillar in PILLAR_ORDER:
        path = ROOT / "portfolio" / f"{pillar.lower()}.html"
        text = read(path)
        parser = AnchorParser()
        parser.feed(text)
        expected_routes = [route for route, record in masters.items() if pillar in record["pillars"]]
        actual_routes = [route_from_href(attrs.get("href", "")) for attrs in parser.anchors]
        if actual_routes != expected_routes:
            errors.append(f"{path.relative_to(ROOT)} shelf differs from manifest: {actual_routes}")
        if text.count(f'data-ra-portfolio-shelf="{pillar.lower()}"') != 1:
            errors.append(f"{path.relative_to(ROOT)}: missing unique shelf marker")
        description = EXPECTED_PILLAR_DESCRIPTIONS[pillar]
        if text.count(description) != 2:
            errors.append(
                f"{path.relative_to(ROOT)}: exact service description must appear in both hero and shelf"
            )
        if pillar == "Sales":
            for label in ("Sales Systems Work", "Sales Systems work.", "Sales Systems Proof"):
                if label not in text:
                    errors.append(f"{path.relative_to(ROOT)}: missing public pillar label {label!r}")
        for route, attrs in zip(actual_routes, parser.anchors):
            if route in masters:
                check_card_attrs(route, attrs, masters[route], path.relative_to(ROOT).as_posix(), errors)


def check_proof_safety(errors: list[str]) -> None:
    checks = (
        ("net-metering-systems", [r"\$50", r"25%\s+lead-to-appointment", r"5x.{0,30}(?:ROAS|return)", r"positive return on ad spend", r"\b12\s+management automations?\b"]),
        ("trust-energy", [r"\$25", r"\$40\s*[-–]\s*\$50", r"1-in-4|1:4", r"\b4\s+years?\b|\bfour years\b", r"half-industry\s+CPL"]),
        ("highlands-energy", [r"\$9", r"3\s*[-–]\s*5x"]),
    )
    for prefix, patterns in checks:
        for path in sorted((ROOT / "portfolio/case-studies").glob(prefix + "*.html")):
            text = read(path)
            for pattern in patterns:
                if re.search(pattern, text, re.I | re.S):
                    errors.append(f"{path.relative_to(ROOT)}: proof-safety blocker matched {pattern}")


def main() -> int:
    errors: list[str] = []
    try:
        data = json.loads(read(MANIFEST_PATH))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot load portfolio manifest: {exc}")
        return 2
    cases, masters = check_manifest(data, errors)
    check_case_pages(cases, errors)
    check_portfolio_hub(masters, errors)
    check_shelves(masters, errors)
    check_proof_safety(errors)
    if errors:
        print(f"Portfolio taxonomy verification FAILED ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Portfolio taxonomy verification PASSED")
    print("- exact taxonomy: 5 Branding / 4 Marketing / 4 Sales Systems services")
    print("- manifest: 68 case records / 21 master records")
    print(f"- case discipline counts: {EXPECTED_CASE_COUNTS}")
    print(f"- master discipline counts: {EXPECTED_MASTER_COUNTS}")
    print(f"- pillar shelves: {EXPECTED_PILLAR_COUNTS}; multi-pillar cards: 14")
    print("- evidence gates: Design 13 case routes / 6 master cards; Outreach 0")
    print("- generated metadata, chips, JSON-LD, filters, shelves, and proof quarantine verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
