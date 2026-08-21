#!/usr/bin/env python3
"""Offline, read-only verification for the Revelation Agency 2026 refresh.

This verifier intentionally performs no network requests and writes no files.
It exits 0 only when every refresh invariant passes, exits 1 for verification
failures, and exits 2 for an unexpected verifier error.

Usage:
    python scripts/verify_2026_refresh.py
    python scripts/verify_2026_refresh.py --root D:\\Codex\\revelation-agency-site-rebrand-p5
"""

from __future__ import annotations

import argparse
import hashlib
import html as html_module
import json
import os
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Optional
from urllib.parse import unquote, urljoin, urlsplit


EXPECTED_HTML_COUNT = 173
EXPECTED_CASE_COUNT = 68
EXPECTED_MASTER_COUNT = 21
REFRESH_CSS = "/assets/css/ra-refresh-2026.css?v=20260817g"
REFRESH_JS = "/assets/js/ra-refresh-2026.js?v=20260817g"
PORTFOLIO_MANIFEST = "assets/data/portfolio-taxonomy-2026.json"

EXPECTED_SOURCE_HASHES = {
    "assets/brand/current/source/revelation-logo-no-text.png":
        "452413d4ef652d26f4ac75392bacb889148bca59e1ef94155a85202763a2b200",
    "assets/brand/current/source/revelation-logo-with-text.png":
        "441045281d05747bd1fc231217348d44324ff5819144207d2755120f829199f4",
}

SERVICE_VISUAL_PATHS = (
    "assets/brand/visuals/2026/service-v2/websites-responsive-system.webp",
    "assets/brand/visuals/2026/service-v2/apps-product-system.webp",
    "assets/brand/visuals/2026/service-v2/brand-identity-system.webp",
    "assets/brand/visuals/2026/service-v2/design-production-system.webp",
    "assets/brand/visuals/2026/service-v2/video-production-system.webp",
    "assets/brand/visuals/2026/service-v2/seo-ai-answers-system.webp",
    "assets/brand/visuals/2026/service-v2/social-content-system.webp",
    "assets/brand/visuals/2026/service-v2/digital-advertising-system.webp",
    "assets/brand/visuals/2026/service-v2/customer-nurture-system.webp",
    "assets/brand/visuals/2026/service-v2/outreach-system.webp",
    "assets/brand/visuals/2026/service-v2/lead-gen-ads-system.webp",
    "assets/brand/visuals/2026/service-v2/crm-sales-tools-system.webp",
    "assets/brand/visuals/2026/service-v2/ai-automation-systems-system.webp",
)

REQUIRED_REFRESH_ASSETS = (
    "assets/css/ra-refresh-2026.css",
    "assets/js/ra-refresh-2026.js",
    "assets/brand/current/manifest.json",
    "assets/brand/current/ra-mark-red.png",
    "assets/brand/current/ra-lockup-red.png",
    "assets/brand/visuals/2026/manifest.json",
    "assets/brand/visuals/2026/branding-signal.webp",
    "assets/brand/visuals/2026/marketing-signal.webp",
    "assets/brand/visuals/2026/sales-signal.webp",
    "assets/brand/visuals/2026/ai-automation-signal.webp",
    *SERVICE_VISUAL_PATHS,
    "assets/brand/visuals/2026/reveal-straight-answers.webp",
    "assets/brand/visuals/2026/reveal-video-infrastructure.webp",
    "assets/revelation-logo.png",
    "favicon-32.png",
    "apple-touch-icon.png",
    "favicon.ico",
    "icon-192.png",
    "icon-512.png",
)

EXPECTED_VISUAL_ASSIGNMENTS = {
    "services/branding/index.html": "branding",
    "services/branding/apps-digital-products.html": "branding",
    "services/branding/brand-strategy-identity.html": "branding",
    "services/branding/design.html": "branding",
    "services/branding/video-visual-content.html": "branding",
    "services/branding/websites-landing-pages.html": "branding",
    "services/marketing/index.html": "marketing",
    "services/marketing/email-lifecycle-marketing.html": "marketing",
    "services/marketing/digital-ads.html": "marketing",
    "services/marketing/seo-ai-visibility.html": "marketing",
    "services/marketing/social-media.html": "marketing",
    "services/sales/index.html": "sales",
    "services/sales/ai-automation-systems.html": "sales",
    "services/sales/crm-sales-infrastructure.html": "sales",
    "services/sales/lead-gen-ads.html": "sales",
    "services/sales/lead-generation-outreach.html": "sales",
    "the-reveal/straight-answers.html": "reveal-straight-answers",
    "the-reveal/video-is-no-longer-optional-its-infrastructure.html":
        "reveal-video-infrastructure",
}

EXPECTED_SERVICE_VISUAL_ASSIGNMENTS = {
    "services/branding/websites-landing-pages.html": (
        "websites-landing-pages", SERVICE_VISUAL_PATHS[0]),
    "services/branding/apps-digital-products.html": (
        "apps-digital-products", SERVICE_VISUAL_PATHS[1]),
    "services/branding/brand-strategy-identity.html": (
        "brand-strategy-identity", SERVICE_VISUAL_PATHS[2]),
    "services/branding/design.html": ("design", SERVICE_VISUAL_PATHS[3]),
    "services/branding/video-visual-content.html": (
        "video-visual-content", SERVICE_VISUAL_PATHS[4]),
    "services/marketing/seo-ai-visibility.html": (
        "seo-ai-visibility", SERVICE_VISUAL_PATHS[5]),
    "services/marketing/social-media.html": ("social-media", SERVICE_VISUAL_PATHS[6]),
    "services/marketing/digital-ads.html": ("digital-ads", SERVICE_VISUAL_PATHS[7]),
    "services/marketing/email-lifecycle-marketing.html": (
        "email-lifecycle-marketing", SERVICE_VISUAL_PATHS[8]),
    "services/sales/lead-generation-outreach.html": (
        "lead-generation-outreach", SERVICE_VISUAL_PATHS[9]),
    "services/sales/lead-gen-ads.html": ("lead-gen-ads", SERVICE_VISUAL_PATHS[10]),
    "services/sales/crm-sales-infrastructure.html": (
        "crm-sales-infrastructure", SERVICE_VISUAL_PATHS[11]),
    "services/sales/ai-automation-systems.html": (
        "ai-automation-systems", SERVICE_VISUAL_PATHS[12]),
}

VALID_PILLARS = {"branding", "marketing", "sales"}
VALID_DISCIPLINES = {
    "B1", "B2", "B3", "B4", "B5",
    "M1", "M2", "M3", "M4",
    "S1", "S2", "S3", "S4",
}
DISCIPLINE_TO_PILLAR = {"B": "branding", "M": "marketing", "S": "sales"}

OLD_LOGO_PATTERNS = (
    re.compile(r"assets/brand/approved/ra-landscape-black-updated\.png", re.I),
    re.compile(r"assets/brand/approved/[^\"'<>\s]*phoenix[^\"'<>\s]*", re.I),
    re.compile(r"assets/[^\"'<>\s]*phoenix[^\"'<>\s]*\.(?:png|webp|svg|jpe?g)", re.I),
)

LEGACY_FOOTER_LABELS = {
    "systems",
    "creative",
    "brand systems",
    "digital presence",
    "sales infrastructure",
    "video production",
    "website development",
    "app development",
    "search rankings",
    "outsource marketing",
    "positioning, content & authority",
    "follow-up & nurture",
    "conversion advertising",
}

LEGACY_FOOTER_ROUTE_PREFIXES = (
    "/services/systems",
    "/services/creative",
    "/services/marketing/search-rankings",
    "/services/marketing/outsource-marketing",
    "/services/marketing/positioning-content-authority",
    "/services/sales/follow-up-nurture",
    "/services/sales/conversion-advertising",
    "/services/ai-automation",
)

EXPECTED_SERVICE_CANONICAL_PATHS = {
    "/services/branding",
    "/services/branding/apps-digital-products",
    "/services/branding/brand-strategy-identity",
    "/services/branding/design",
    "/services/branding/video-visual-content",
    "/services/branding/websites-landing-pages",
    "/services/marketing",
    "/services/marketing/digital-ads",
    "/services/marketing/email-lifecycle-marketing",
    "/services/marketing/seo-ai-visibility",
    "/services/marketing/social-media",
    "/services/sales",
    "/services/sales/ai-automation-systems",
    "/services/sales/crm-sales-infrastructure",
    "/services/sales/lead-gen-ads",
    "/services/sales/lead-generation-outreach",
}

EXPECTED_SERVICE_LEAVES = {
    "B1": "services/branding/websites-landing-pages.html",
    "B2": "services/branding/apps-digital-products.html",
    "B3": "services/branding/brand-strategy-identity.html",
    "B4": "services/branding/design.html",
    "B5": "services/branding/video-visual-content.html",
    "M1": "services/marketing/seo-ai-visibility.html",
    "M2": "services/marketing/social-media.html",
    "M3": "services/marketing/digital-ads.html",
    "M4": "services/marketing/email-lifecycle-marketing.html",
    "S1": "services/sales/lead-generation-outreach.html",
    "S2": "services/sales/lead-gen-ads.html",
    "S3": "services/sales/crm-sales-infrastructure.html",
    "S4": "services/sales/ai-automation-systems.html",
}

EXPECTED_PORTFOLIO_NAV_LINKS = {
    "/portfolio?filter=b1": "Websites",
    "/portfolio?filter=b2": "Apps",
    "/portfolio?filter=b3": "Brand Identity",
    "/portfolio?filter=b4": "Design",
    "/portfolio?filter=b5": "Video",
    "/portfolio?filter=m1": "SEO / AI Answers",
    "/portfolio?filter=m2": "Social Media",
    "/portfolio?filter=m3": "Digital Advertising",
    "/portfolio?filter=m4": "Customer Nurture",
    "/portfolio?filter=s1": "Outreach",
    "/portfolio?filter=s2": "Lead Gen Ads",
    "/portfolio?filter=s3": "CRMs / Sales Tools",
    "/portfolio?filter=s4": "AI Automation Systems",
}

EXPECTED_CORRECTED_ROUTE_REDIRECTS = {
    "/services/marketing/positioning-content-authority":
        "/services/marketing/seo-ai-visibility",
    "/services/sales/follow-up-nurture":
        "/services/marketing/email-lifecycle-marketing",
    "/services/sales/conversion-advertising":
        "/services/marketing/digital-ads",
    "/services/ai-automation":
        "/services/sales/ai-automation-systems",
    "/services/systems/ai-automation":
        "/services/sales/ai-automation-systems",
    "/portfolio/creative/branding": "/portfolio?filter=b3",
    "/portfolio/creative/website-development": "/portfolio?filter=b1",
    "/portfolio/creative/app-development": "/portfolio?filter=b2",
    "/portfolio/creative/video-production": "/portfolio?filter=b5",
    "/portfolio/systems/brand-systems": "/portfolio?filter=b3",
    "/portfolio/systems/digital-presence": "/portfolio?filter=b1",
    "/portfolio/systems/sales-infrastructure": "/portfolio?filter=s3",
    "/portfolio/systems/ai-automation": "/portfolio?filter=s4",
    "/portfolio/marketing/search-rankings": "/portfolio?filter=m1",
    "/portfolio/marketing/social-media": "/portfolio?filter=m2",
    "/portfolio/marketing/outsource-marketing": "/portfolio?filter=marketing",
    "/portfolio/marketing/digital-ads": "/portfolio?filter=m3",
}


@dataclass
class CheckResult:
    name: str
    summary: str
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def attr_tokens(value: Optional[str], *, lower: bool = False) -> list[str]:
    if value is None:
        return []
    tokens = [token for token in re.split(r"[\s,|]+", value.strip()) if token]
    return [token.lower() for token in tokens] if lower else tokens


def normalize_text(value: str) -> str:
    value = html_module.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def posix_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


class BodyAttributeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attrs: Optional[dict[str, Optional[str]]] = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if self.attrs is None and tag.lower() == "body":
            self.attrs = {key.lower(): value for key, value in attrs}


class PortfolioParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[tuple[int, dict[str, Optional[str]]]] = []
        self.filters: list[tuple[int, dict[str, Optional[str]]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attr_map = {key.lower(): value for key, value in attrs}
        classes = set(attr_tokens(attr_map.get("class")))
        if tag.lower() == "a" and "pf-card" in classes:
            self.cards.append((self.getpos()[0], attr_map))
        if tag.lower() == "button" and "pf-filter-btn" in classes:
            self.filters.append((self.getpos()[0], attr_map))


class FooterServiceParser(HTMLParser):
    """Collect service-footer anchor labels and hrefs without CSS/comment noise."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.footer_depths: list[int] = []
        self.service_depths: list[int] = []
        self.anchor: Optional[dict[str, Any]] = None
        self.links: list[tuple[int, str, str, set[str]]] = []

    @property
    def in_footer(self) -> bool:
        return bool(self.footer_depths)

    @property
    def in_services(self) -> bool:
        return bool(self.service_depths)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self.depth += 1
        attr_map = {key.lower(): value for key, value in attrs}
        classes = set(attr_tokens(attr_map.get("class")))
        tag = tag.lower()

        if tag == "footer":
            self.footer_depths.append(self.depth)
        if self.in_footer and tag == "ul" and "ra-footer__svc" in classes:
            self.service_depths.append(self.depth)
        if self.in_footer and self.in_services and tag == "a":
            self.anchor = {
                "line": self.getpos()[0],
                "href": attr_map.get("href") or "",
                "classes": classes,
                "text": [],
            }

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        # No relevant footer service element is expected to be self-closing.
        return

    def handle_data(self, data: str) -> None:
        if self.anchor is not None:
            self.anchor["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "a" and self.anchor is not None:
            self.links.append((
                int(self.anchor["line"]),
                normalize_text("".join(self.anchor["text"])),
                str(self.anchor["href"]),
                set(self.anchor["classes"]),
            ))
            self.anchor = None

        if tag == "ul" and self.service_depths and self.depth == self.service_depths[-1]:
            self.service_depths.pop()
        if tag == "footer" and self.footer_depths and self.depth == self.footer_depths[-1]:
            self.footer_depths.pop()
        self.depth = max(0, self.depth - 1)


class RootLinkParser(HTMLParser):
    LINK_ATTRS = {
        "a": ("href",),
        "area": ("href",),
        "form": ("action",),
        "iframe": ("src",),
        "img": ("src",),
        "link": ("href",),
        "script": ("src",),
        "source": ("src", "srcset"),
        "track": ("src",),
        "video": ("src", "poster"),
        "audio": ("src",),
        "use": ("href", "xlink:href"),
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._collect(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._collect(tag, attrs)

    def _collect(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        wanted = self.LINK_ATTRS.get(tag, ())
        if not wanted:
            return
        attr_map = {key.lower(): value for key, value in attrs}
        for attr in wanted:
            value = attr_map.get(attr)
            if not value:
                continue
            if attr == "srcset":
                candidates = [part.strip().split()[0] for part in value.split(",") if part.strip()]
            else:
                candidates = [value.strip()]
            for candidate in candidates:
                if candidate.startswith("/") and not candidate.startswith("//"):
                    self.links.append((self.getpos()[0], tag, attr, candidate))


def check_global_includes(root: Path, html_files: list[Path]) -> CheckResult:
    errors: list[str] = []
    css_re = re.compile(
        r"<link\b[^>]*\bhref\s*=\s*([\"'])" + re.escape(REFRESH_CSS) + r"\1[^>]*>",
        re.I,
    )
    js_re = re.compile(
        r"<script\b[^>]*\bsrc\s*=\s*([\"'])" + re.escape(REFRESH_JS) + r"\1[^>]*>",
        re.I,
    )

    if len(html_files) != EXPECTED_HTML_COUNT:
        errors.append(
            f"expected {EXPECTED_HTML_COUNT} HTML files, found {len(html_files)}; "
            "confirm the migration did not omit or accidentally create pages"
        )

    for path in html_files:
        text = read_text(path)
        css_count = len(css_re.findall(text))
        js_count = len(js_re.findall(text))
        rel = posix_rel(path, root)
        if css_count != 1:
            errors.append(f"{rel}: expected exactly 1 {REFRESH_CSS} <link>, found {css_count}")
        if js_count != 1:
            errors.append(f"{rel}: expected exactly 1 {REFRESH_JS} <script>, found {js_count}")

    return CheckResult(
        "global-refresh-includes",
        f"{len(html_files)} HTML files; CSS and JS must each appear exactly once per file",
        errors,
    )


def check_old_logo_references(root: Path, html_files: list[Path]) -> CheckResult:
    errors: list[str] = []
    for path in html_files:
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in OLD_LOGO_PATTERNS:
                match = pattern.search(line)
                if match:
                    errors.append(
                        f"{posix_rel(path, root)}:{line_no}: old phoenix/approved logo reference "
                        f"{match.group(0)!r}; use /assets/brand/current/ra-mark-red.png or ra-lockup-red.png"
                    )
                    break
    return CheckResult(
        "old-logo-references",
        "no HTML may reference the retired approved phoenix identity",
        errors,
    )


def validate_taxonomy_attrs(
    *,
    label: str,
    pillars_value: Optional[str],
    disciplines_value: Optional[str],
    ai_value: Optional[str],
) -> list[str]:
    errors: list[str] = []
    pillars = set(attr_tokens(pillars_value, lower=True))
    disciplines = set(attr_tokens(disciplines_value))

    if not pillars:
        errors.append(f"{label}: data-ra-pillars is missing or empty")
    invalid_pillars = sorted(pillars - VALID_PILLARS)
    if invalid_pillars:
        errors.append(f"{label}: invalid pillar values {invalid_pillars}; allowed={sorted(VALID_PILLARS)}")

    if not disciplines:
        errors.append(f"{label}: data-ra-disciplines is missing or empty")
    invalid_disciplines = sorted(disciplines - VALID_DISCIPLINES)
    if invalid_disciplines:
        errors.append(
            f"{label}: invalid discipline codes {invalid_disciplines}; "
            f"allowed={sorted(VALID_DISCIPLINES)}"
        )

    implied = {DISCIPLINE_TO_PILLAR[code[0]] for code in disciplines if code in VALID_DISCIPLINES}
    missing_implied = sorted(implied - pillars)
    if missing_implied:
        errors.append(
            f"{label}: disciplines imply pillars {missing_implied}, but data-ra-pillars={sorted(pillars)}"
        )

    if ai_value is None:
        errors.append(f"{label}: data-ra-ai is missing")
    elif ai_value.strip().lower() not in {"true", "false"}:
        errors.append(f"{label}: data-ra-ai must be 'true' or 'false', found {ai_value!r}")
    return errors


def check_case_page_metadata(root: Path) -> CheckResult:
    case_dir = root / "portfolio" / "case-studies"
    case_files = sorted(case_dir.glob("*.html")) if case_dir.is_dir() else []
    errors: list[str] = []

    if len(case_files) != EXPECTED_CASE_COUNT:
        errors.append(
            f"expected {EXPECTED_CASE_COUNT} case-study HTML files in portfolio/case-studies, "
            f"found {len(case_files)}"
        )

    for path in case_files:
        parser = BodyAttributeParser()
        text = read_text(path)
        parser.feed(text)
        rel = posix_rel(path, root)
        if parser.attrs is None:
            errors.append(f"{rel}: no <body> start tag found")
            continue
        attrs = parser.attrs
        errors.extend(validate_taxonomy_attrs(
            label=rel,
            pillars_value=attrs.get("data-ra-pillars"),
            disciplines_value=attrs.get("data-ra-disciplines"),
            ai_value=attrs.get("data-ra-ai"),
        ))

        body_tag = re.search(r"<body\b[^>]*>", text, re.I | re.S)
        if body_tag:
            for attr_name in ("data-ra-pillars", "data-ra-disciplines", "data-ra-ai"):
                count = len(re.findall(r"\b" + re.escape(attr_name) + r"\s*=", body_tag.group(0), re.I))
                if count != 1:
                    errors.append(f"{rel}: <body> must contain {attr_name} exactly once, found {count}")

    return CheckResult(
        "case-study-taxonomy-metadata",
        f"{len(case_files)} case-study pages checked for pillars, disciplines, and AI flag",
        errors,
    )


def records_from_container(container: Any) -> list[Any]:
    if isinstance(container, list):
        return container
    if not isinstance(container, dict):
        return []

    recordish_keys = {
        "route", "href", "path", "url", "slug", "projectSlug", "masterSlug",
        "pillars", "disciplines", "pageKind", "kind", "type",
    }
    if recordish_keys.intersection(container):
        return [container]

    records: list[Any] = []
    for key, value in container.items():
        if isinstance(value, dict):
            record = dict(value)
            record.setdefault("_key", key)
            records.append(record)
        elif isinstance(value, str):
            records.append({"_key": key, "value": value})
    return records


def first_value(record: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        value = record.get(key)
        if value is not None and value != "":
            return value
    return None


def record_route(record: Any) -> Optional[str]:
    if isinstance(record, str):
        value = record
    elif isinstance(record, dict):
        value = first_value(record, ("route", "href", "path", "url", "caseStudyRoute"))
        if value is None:
            key = record.get("_key")
            if isinstance(key, str) and ("/" in key or key.endswith(".html")):
                value = key
        if value is None and isinstance(record.get("value"), str):
            value = record["value"]
    else:
        return None
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value)
    path = unquote(parsed.path).replace("\\", "/")
    if not path.startswith("/"):
        path = "/" + path
    path = re.sub(r"/{2,}", "/", path)
    if path.startswith("/case-studies/"):
        path = "/portfolio" + path
    if path.startswith("/portfolio/case-studies/") and not path.endswith(".html"):
        path += ".html"
    return path


def record_master_id(record: Any) -> Optional[str]:
    if isinstance(record, str):
        return record.strip() or None
    if not isinstance(record, dict):
        return None
    value = first_value(record, (
        "masterSlug", "projectSlug", "masterProject", "master", "projectId",
        "project", "slug", "id", "name", "_key",
    ))
    if isinstance(value, dict):
        value = first_value(value, ("slug", "id", "name", "route", "href"))
    if value is None:
        return None
    return str(value).strip().lower() or None


def record_kind(record: Any) -> str:
    if not isinstance(record, dict):
        return ""
    value = first_value(record, ("pageKind", "kind", "type", "recordType"))
    return str(value).strip().lower() if value is not None else ""


def metadata_values(record: dict[str, Any]) -> tuple[Any, Any, Any]:
    taxonomy = record.get("taxonomy") if isinstance(record.get("taxonomy"), dict) else {}
    pillars = first_value(record, ("pillars", "pillar"))
    disciplines = first_value(record, ("disciplines", "disciplineCodes", "discipline"))
    ai_value = first_value(record, ("aiAutomation", "ai", "usesAiAutomation"))
    if pillars is None:
        pillars = first_value(taxonomy, ("pillars", "pillar"))
    if disciplines is None:
        disciplines = first_value(taxonomy, ("disciplines", "disciplineCodes", "discipline"))
    if ai_value is None:
        ai_value = first_value(taxonomy, ("aiAutomation", "ai", "usesAiAutomation"))
    return pillars, disciplines, ai_value


def values_as_tokens(value: Any, *, lower: bool = False) -> list[str]:
    if isinstance(value, list):
        tokens = [str(item).strip() for item in value if str(item).strip()]
    elif isinstance(value, str):
        tokens = attr_tokens(value)
    elif value is None:
        tokens = []
    else:
        tokens = [str(value).strip()]
    return [token.lower() for token in tokens] if lower else tokens


def validate_manifest_record(record: Any, label: str) -> list[str]:
    if not isinstance(record, dict):
        return [f"{label}: record must be an object with taxonomy fields"]
    pillars_value, disciplines_value, ai_value = metadata_values(record)
    pillars = set(values_as_tokens(pillars_value, lower=True))
    disciplines = set(values_as_tokens(disciplines_value))
    errors: list[str] = []
    if not pillars:
        errors.append(f"{label}: manifest pillars are missing or empty")
    elif pillars - VALID_PILLARS:
        errors.append(f"{label}: invalid manifest pillars {sorted(pillars - VALID_PILLARS)}")
    if not disciplines:
        errors.append(f"{label}: manifest disciplines are missing or empty")
    elif disciplines - VALID_DISCIPLINES:
        errors.append(f"{label}: invalid manifest disciplines {sorted(disciplines - VALID_DISCIPLINES)}")
    if not isinstance(ai_value, bool):
        errors.append(f"{label}: manifest aiAutomation/ai flag must be boolean")
    implied = {DISCIPLINE_TO_PILLAR[code[0]] for code in disciplines if code in VALID_DISCIPLINES}
    if implied - pillars:
        errors.append(
            f"{label}: disciplines imply pillars {sorted(implied - pillars)} absent from manifest pillars"
        )
    return errors


def check_portfolio_manifest(root: Path) -> CheckResult:
    manifest_path = root / PORTFOLIO_MANIFEST
    errors: list[str] = []
    if not manifest_path.is_file():
        return CheckResult(
            "portfolio-taxonomy-manifest",
            f"canonical manifest expected at {PORTFOLIO_MANIFEST}",
            [
                f"missing {PORTFOLIO_MANIFEST}; create one mapping all 68 case pages and 21 master projects"
            ],
        )

    try:
        data = load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            "portfolio-taxonomy-manifest",
            f"canonical manifest expected at {PORTFOLIO_MANIFEST}",
            [f"{PORTFOLIO_MANIFEST}: invalid JSON: {exc}"],
        )

    if not isinstance(data, dict):
        return CheckResult(
            "portfolio-taxonomy-manifest",
            "manifest must be a JSON object",
            [f"{PORTFOLIO_MANIFEST}: top-level value is {type(data).__name__}, expected object"],
        )

    case_container = first_value(data, ("caseStudies", "case_studies", "cases", "caseStudiesByRoute"))
    master_container = first_value(data, ("masterProjects", "master_projects", "masters", "masterCardsByRoute"))
    flat_container = first_value(data, ("records", "projects", "entries", "items"))
    flat_records = records_from_container(flat_container)

    if case_container is not None:
        case_records = records_from_container(case_container)
    else:
        explicitly_typed = [record for record in flat_records if record_kind(record) in {"case", "case-study", "case_study", "detail"}]
        case_records = explicitly_typed or [
            record for record in flat_records
            if (record_route(record) or "").startswith("/portfolio/case-studies/")
        ]

    if master_container is not None:
        master_records = records_from_container(master_container)
    else:
        master_records = [
            record for record in flat_records
            if record_kind(record) in {"master", "master-project", "master_project", "portfolio-card", "portfolio_card"}
        ]

    expected_case_routes = {
        "/" + path.relative_to(root).as_posix()
        for path in (root / "portfolio" / "case-studies").glob("*.html")
    }
    case_routes: list[str] = []
    for index, record in enumerate(case_records, start=1):
        route = record_route(record)
        label = f"case record #{index}"
        if route is None:
            errors.append(f"{label}: missing route/href/path/url")
        else:
            case_routes.append(route)
            label = route
        errors.extend(validate_manifest_record(record, label))

    route_set = set(case_routes)
    if len(case_records) != EXPECTED_CASE_COUNT:
        errors.append(f"manifest must contain exactly {EXPECTED_CASE_COUNT} case records, found {len(case_records)}")
    if len(route_set) != len(case_routes):
        duplicates = sorted({route for route in case_routes if case_routes.count(route) > 1})
        errors.append(f"manifest has duplicate case routes: {duplicates}")
    missing_routes = sorted(expected_case_routes - route_set)
    extra_routes = sorted(route_set - expected_case_routes)
    if missing_routes:
        errors.append(f"manifest is missing case routes: {missing_routes}")
    if extra_routes:
        errors.append(f"manifest has non-case or nonexistent case routes: {extra_routes}")

    if master_records:
        master_ids = [record_master_id(record) for record in master_records]
        for index, (record, master_id) in enumerate(zip(master_records, master_ids), start=1):
            label = master_id or f"master record #{index}"
            if master_id is None:
                errors.append(f"master record #{index}: missing slug/id/name")
            errors.extend(validate_manifest_record(record, label))
        unique_master_ids = {value for value in master_ids if value}
        if len(master_records) != EXPECTED_MASTER_COUNT:
            errors.append(
                f"manifest must contain exactly {EXPECTED_MASTER_COUNT} master records, found {len(master_records)}"
            )
        if len(unique_master_ids) != len(master_records):
            errors.append(
                f"master records require {EXPECTED_MASTER_COUNT} unique identifiers; "
                f"found {len(unique_master_ids)} unique"
            )
    else:
        derived_master_ids = {record_master_id(record) for record in case_records}
        derived_master_ids.discard(None)
        if len(derived_master_ids) != EXPECTED_MASTER_COUNT:
            errors.append(
                "manifest has no explicit masterProjects/masters array and case records yield "
                f"{len(derived_master_ids)} distinct masterSlug/projectSlug values; expected {EXPECTED_MASTER_COUNT}"
            )

    master_count = len(master_records) if master_records else len({
        value for value in (record_master_id(record) for record in case_records) if value
    })
    return CheckResult(
        "portfolio-taxonomy-manifest",
        f"{len(case_records)} case records and {master_count} master projects in {PORTFOLIO_MANIFEST}",
        errors,
    )


def check_portfolio_cards(root: Path) -> CheckResult:
    path = root / "portfolio.html"
    if not path.is_file():
        return CheckResult("portfolio-card-taxonomy", "portfolio.html card/filter audit", ["portfolio.html is missing"])

    text = read_text(path)
    parser = PortfolioParser()
    parser.feed(text)
    errors: list[str] = []
    if len(parser.cards) != EXPECTED_MASTER_COUNT:
        errors.append(f"portfolio.html: expected {EXPECTED_MASTER_COUNT} .pf-card anchors, found {len(parser.cards)}")

    pillar_counts = {pillar: 0 for pillar in sorted(VALID_PILLARS)}
    multi_pillar_count = 0
    for line, attrs in parser.cards:
        label = f"portfolio.html:{line}"
        errors.extend(validate_taxonomy_attrs(
            label=label,
            pillars_value=attrs.get("data-pillars"),
            disciplines_value=attrs.get("data-disciplines"),
            ai_value=attrs.get("data-ai"),
        ))
        pillars = set(attr_tokens(attrs.get("data-pillars"), lower=True))
        if len(pillars) > 1:
            multi_pillar_count += 1
        for pillar in VALID_PILLARS:
            if pillar in pillars:
                pillar_counts[pillar] += 1

    if parser.cards and multi_pillar_count == 0:
        errors.append("portfolio.html: no card has more than one data-pillars value; multi-pillar work is not represented")
    for required_empty_state_token in (
        'id="pf-empty-state"',
        'id="pf-empty-label"',
        "emptyState.hidden = shown !== 0",
        "There is no public case study in this filter yet.",
        "function findFilterButton(filter)",
    ):
        if required_empty_state_token not in text:
            errors.append(f"portfolio.html: zero-result filters need an intentional empty state ({required_empty_state_token})")
    if "querySelector('.pf-filter-btn[data-filter=\"' +" in text:
        errors.append("portfolio.html: URL filter values must not be interpolated into a CSS selector")

    thumbnail_labels = re.findall(
        r'<div\b[^>]*class=["\'][^"\']*\bpf-card__bg\b[^"\']*["\'][^>]*\bdata-taxonomy=["\']([^"\']+)["\']',
        text,
        re.I,
    )
    if len(thumbnail_labels) != EXPECTED_MASTER_COUNT:
        errors.append(
            f"portfolio.html: expected {EXPECTED_MASTER_COUNT} canonical thumbnail taxonomy overlays, "
            f"found {len(thumbnail_labels)}"
        )
    for thumbnail_label in thumbnail_labels:
        if re.search(r"\b(?:Creative|Strategy)\b|(?<!Sales )\bSystems\b", thumbnail_label, re.I):
            errors.append(f"portfolio.html: retired thumbnail taxonomy remains: {thumbnail_label!r}")
    if "/assets/img/portfolio/revelation-portal/thumbnail.png" in text:
        errors.append("portfolio.html: Revelation Portal card still exposes the retired agency identity")
    if "/assets/brand/current/ra-mark-red.png" not in text:
        errors.append("portfolio.html: Revelation Portal card does not use the supplied current mark")

    for pillar, count in pillar_counts.items():
        if count == 0:
            errors.append(f"portfolio.html: {pillar.title()} filter would return zero cards")

    # Pillar shelves are generated from the same canonical manifest as the
    # filter index. Verify the exact membership and taxonomy so a project
    # cannot silently disappear from a pillar-specific proof page.
    try:
        manifest = load_json(root / PORTFOLIO_MANIFEST)
        master_records = manifest["masterCardsByRoute"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        errors.append(f"{PORTFOLIO_MANIFEST}: cannot verify pillar shelves: {exc}")
        master_records = {}

    shelf_counts: dict[str, int] = {}
    if isinstance(master_records, dict):
        for pillar in sorted(VALID_PILLARS):
            shelf_path = root / "portfolio" / f"{pillar}.html"
            if not shelf_path.is_file():
                errors.append(f"portfolio/{pillar}.html: pillar shelf page is missing")
                continue
            shelf_parser = PortfolioParser()
            shelf_parser.feed(read_text(shelf_path))
            shelf_counts[pillar] = len(shelf_parser.cards)

            expected = {
                str(route): record
                for route, record in master_records.items()
                if isinstance(record, dict)
                and pillar in {str(value).lower() for value in record.get("pillars", [])}
            }
            actual: dict[str, tuple[int, dict[str, Optional[str]]]] = {}
            for line, attrs in shelf_parser.cards:
                href = str(attrs.get("href") or "")
                route = urlsplit(href).path
                if route and not route.endswith(".html"):
                    route += ".html"
                if route in actual:
                    errors.append(f"portfolio/{pillar}.html:{line}: duplicate project card {route}")
                actual[route] = (line, attrs)

            missing = sorted(set(expected) - set(actual))
            extra = sorted(set(actual) - set(expected))
            if missing:
                errors.append(f"portfolio/{pillar}.html: missing manifest project cards {missing}")
            if extra:
                errors.append(f"portfolio/{pillar}.html: unexpected project cards {extra}")

            for route in sorted(set(expected) & set(actual)):
                line, attrs = actual[route]
                record = expected[route]
                label = f"portfolio/{pillar}.html:{line} ({route})"
                errors.extend(validate_taxonomy_attrs(
                    label=label,
                    pillars_value=attrs.get("data-pillars"),
                    disciplines_value=attrs.get("data-disciplines"),
                    ai_value=attrs.get("data-ai"),
                ))
                actual_pillars = set(attr_tokens(attrs.get("data-pillars"), lower=True))
                expected_pillars = {str(value).lower() for value in record.get("pillars", [])}
                if actual_pillars != expected_pillars:
                    errors.append(
                        f"{label}: data-pillars {sorted(actual_pillars)} does not match manifest "
                        f"{sorted(expected_pillars)}"
                    )
                actual_disciplines = set(attr_tokens(attrs.get("data-disciplines")))
                expected_disciplines = {str(value) for value in record.get("disciplines", [])}
                if actual_disciplines != expected_disciplines:
                    errors.append(
                        f"{label}: data-disciplines {sorted(actual_disciplines)} does not match manifest "
                        f"{sorted(expected_disciplines)}"
                    )
                expected_ai = str(bool(record.get("aiAutomation"))).lower()
                if str(attrs.get("data-ai") or "").lower() != expected_ai:
                    errors.append(
                        f"{label}: data-ai={attrs.get('data-ai')!r} does not match manifest {expected_ai!r}"
                    )

    filters = {str(attrs.get("data-filter") or "").strip().lower() for _, attrs in parser.filters}
    missing_filters = sorted(({"all"} | VALID_PILLARS) - filters)
    if missing_filters:
        errors.append(f"portfolio.html: missing filter buttons for {missing_filters}")

    return CheckResult(
        "portfolio-card-taxonomy",
        f"{len(parser.cards)} cards; filter counts={pillar_counts}; "
        f"pillar shelves={shelf_counts}; multi-pillar cards={multi_pillar_count}",
        errors,
    )


def redirect_source_matches(source: str, route: str) -> bool:
    escaped = re.escape(source).replace(re.escape(":path*"), r".*")
    return re.fullmatch(escaped, route) is not None


def candidate_routes_for_html(rel: str) -> set[str]:
    pure = PurePosixPath(rel)
    file_route = "/" + pure.as_posix()
    routes = {file_route}
    if pure.name.lower() == "index.html":
        parent = pure.parent.as_posix()
        routes.add("/" if parent == "." else "/" + parent + "/")
        routes.add("/" if parent == "." else "/" + parent)
        routes.add("/index.html" if parent == "." else "/" + parent + "/index")
    else:
        routes.add("/" + pure.with_suffix("").as_posix())
    return routes


def page_is_redirected(rel: str, redirect_sources: list[str]) -> bool:
    return any(
        redirect_source_matches(source, route)
        for source in redirect_sources
        for route in candidate_routes_for_html(rel)
    )


def route_for_source_page(rel: str) -> str:
    pure = PurePosixPath(rel)
    if pure.name.lower() == "index.html":
        parent = pure.parent.as_posix()
        return "/" if parent == "." else "/" + parent + "/"
    return "/" + pure.as_posix()


def absolute_internal_path(source_rel: str, href: str) -> str:
    base = "https://verification.invalid" + route_for_source_page(source_rel)
    return urlsplit(urljoin(base, href)).path


def check_legacy_footers(root: Path, html_files: list[Path], vercel: dict[str, Any]) -> CheckResult:
    redirects = vercel.get("redirects", []) if isinstance(vercel, dict) else []
    redirect_sources = [
        str(item.get("source")) for item in redirects
        if isinstance(item, dict) and item.get("source") and not item.get("has") and not item.get("missing")
    ]
    errors: list[str] = []
    checked = 0
    excluded = 0

    for path in html_files:
        rel = posix_rel(path, root)
        if page_is_redirected(rel, redirect_sources):
            excluded += 1
            continue
        checked += 1
        parser = FooterServiceParser()
        parser.feed(read_text(path))
        for line, text, href, classes in parser.links:
            normalized_label = normalize_text(text).lower()
            if normalized_label in LEGACY_FOOTER_LABELS:
                errors.append(
                    f"{rel}:{line}: legacy footer label {text!r}; use the Branding / Marketing / Sales Systems taxonomy"
                )
            if href:
                route = absolute_internal_path(rel, href).rstrip("/").lower()
                if any(route.startswith(prefix) for prefix in LEGACY_FOOTER_ROUTE_PREFIXES):
                    errors.append(f"{rel}:{line}: legacy footer destination {href!r} ({route})")

    return CheckResult(
        "non-redirect-footer-taxonomy",
        f"checked {checked} non-redirect HTML files; excluded {excluded} redirect-only files",
        errors,
    )


def check_brand_assets(root: Path) -> CheckResult:
    errors: list[str] = []
    for rel, expected_hash in EXPECTED_SOURCE_HASHES.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: supplied source logo is missing")
            continue
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(
                f"{rel}: SHA-256 mismatch; expected {expected_hash}, got {actual_hash}. "
                "Restore the exact user-supplied transparent PNG."
            )

    for rel in REQUIRED_REFRESH_ASSETS:
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: required refresh asset is missing")
        elif path.stat().st_size == 0:
            errors.append(f"{rel}: required refresh asset exists but is empty")

    brand_manifest_path = root / "assets" / "brand" / "current" / "manifest.json"
    if brand_manifest_path.is_file():
        try:
            brand_manifest = load_json(brand_manifest_path)
            declared = {
                str(item.get("path")): str(item.get("sha256", "")).lower()
                for item in brand_manifest.get("sources", [])
                if isinstance(item, dict) and item.get("path")
            }
            for rel, expected_hash in EXPECTED_SOURCE_HASHES.items():
                if declared.get(rel) != expected_hash:
                    errors.append(
                        f"assets/brand/current/manifest.json: source {rel} must declare SHA-256 {expected_hash}"
                    )
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"assets/brand/current/manifest.json: invalid brand manifest: {exc}")

    return CheckResult(
        "brand-assets-and-source-hashes",
        f"{len(EXPECTED_SOURCE_HASHES)} source hashes and {len(REQUIRED_REFRESH_ASSETS)} generated assets checked",
        errors,
    )


def check_generated_visual_system(root: Path) -> CheckResult:
    errors: list[str] = []
    visual_dir = root / "assets" / "brand" / "visuals" / "2026"
    manifest_path = visual_dir / "manifest.json"
    declared: dict[str, str] = {}
    try:
        manifest = load_json(manifest_path)
        declared = {
            str(item.get("path")): str(item.get("sha256", "")).lower()
            for item in manifest.get("assets", [])
            if isinstance(item, dict) and item.get("path")
        }
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        errors.append(f"assets/brand/visuals/2026/manifest.json: invalid visual manifest: {exc}")

    visual_paths = (
        "assets/brand/visuals/2026/branding-signal.webp",
        "assets/brand/visuals/2026/marketing-signal.webp",
        "assets/brand/visuals/2026/sales-signal.webp",
        "assets/brand/visuals/2026/ai-automation-signal.webp",
        *SERVICE_VISUAL_PATHS,
        "assets/brand/visuals/2026/reveal-straight-answers.webp",
        "assets/brand/visuals/2026/reveal-video-infrastructure.webp",
    )
    for rel in visual_paths:
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: generated visual is missing")
            continue
        payload = path.read_bytes()
        if len(payload) < 30_000:
            errors.append(f"{rel}: generated visual is unexpectedly small ({len(payload)} bytes)")
        if payload[:4] != b"RIFF" or payload[8:12] != b"WEBP":
            errors.append(f"{rel}: generated visual is not a valid WebP container")
        actual_hash = hashlib.sha256(payload).hexdigest()
        if declared.get(rel) != actual_hash:
            errors.append(
                f"assets/brand/visuals/2026/manifest.json: {rel} must declare SHA-256 {actual_hash}"
            )

    css_path = root / "assets" / "css" / "ra-refresh-2026.css"
    css = css_path.read_text(encoding="utf-8") if css_path.is_file() else ""
    for rel in visual_paths:
        if f"/{rel}" not in css:
            errors.append(f"assets/css/ra-refresh-2026.css: missing generated visual reference /{rel}")
    if "@keyframes ra-generated-visual-drift" not in css:
        errors.append("assets/css/ra-refresh-2026.css: generated visual motion is missing")

    for rel, expected_theme in EXPECTED_VISUAL_ASSIGNMENTS.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: expected generated-visual page is missing")
            continue
        text = path.read_text(encoding="utf-8")
        body = re.search(r"<body\b[^>]*>", text, re.I | re.S)
        if not body or body.group(0).count(f'data-ra-visual="{expected_theme}"') != 1:
            errors.append(f"{rel}: body must declare data-ra-visual={expected_theme!r}")
        expected_hero = "ar-hero" if rel.startswith("the-reveal/") else "p-hero"
        if f'class="{expected_hero}' not in text:
            errors.append(f"{rel}: expected .{expected_hero} visual host is missing")

    if len(set(SERVICE_VISUAL_PATHS)) != len(EXPECTED_SERVICE_VISUAL_ASSIGNMENTS):
        errors.append("service hero visual assignments must be one-to-one")
    for rel, (service_slug, visual_path) in EXPECTED_SERVICE_VISUAL_ASSIGNMENTS.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: expected service visual page is missing")
            continue
        text = path.read_text(encoding="utf-8")
        body = re.search(r"<body\b[^>]*>", text, re.I | re.S)
        if not body or body.group(0).count(f'data-ra-service="{service_slug}"') != 1:
            errors.append(f"{rel}: body must declare data-ra-service={service_slug!r}")
        selector = re.compile(
            rf"body\[data-ra-service=['\"]{re.escape(service_slug)}['\"]\]\s*\{{"
            rf"[^}}]*url\(['\"]?/{re.escape(visual_path)}['\"]?\)",
            re.I | re.S,
        )
        if not selector.search(css):
            errors.append(
                f"assets/css/ra-refresh-2026.css: {service_slug!r} must use /{visual_path}"
            )

    receipt_paths = (
        "artifacts/service-image-generation-branding-v2.json",
        "artifacts/service-image-generation-marketing-v2.json",
        "artifacts/service-image-generation-sales-v2.json",
    )
    receipted: dict[str, str] = {}
    for receipt_rel in receipt_paths:
        receipt_path = root / receipt_rel
        try:
            receipt = load_json(receipt_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{receipt_rel}: invalid image generation receipt: {exc}")
            continue
        for item in receipt.get("assets", []):
            if not isinstance(item, dict):
                continue
            output = item.get("output") if isinstance(item.get("output"), dict) else {}
            output_path = item.get("outputPath") or item.get("output_path") or output.get("path")
            output_hash = item.get("sha256") or item.get("outputSha256") or output.get("sha256")
            if output_path and output_hash:
                receipted[str(output_path)] = str(output_hash).lower()
    for rel in SERVICE_VISUAL_PATHS:
        path = root / rel
        if path.is_file():
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if receipted.get(rel) != actual_hash:
                errors.append(f"{rel}: generation receipt must declare SHA-256 {actual_hash}")

    reveal_index = (root / "the-reveal" / "index.html").read_text(encoding="utf-8")
    for rel in visual_paths[-2:]:
        if f"/{rel}" not in reveal_index:
            errors.append(f"the-reveal/index.html: missing first-party card visual /{rel}")

    return CheckResult(
        "generated-editorial-visual-system",
        f"{len(visual_paths)} first-party visuals, {len(EXPECTED_VISUAL_ASSIGNMENTS)} themed pages, "
        f"and {len(EXPECTED_SERVICE_VISUAL_ASSIGNMENTS)} unique service heroes checked",
        errors,
    )


def clean_public_path(value: str) -> str:
    parsed = urlsplit(value)
    path = re.sub(r"/index\.html$", "", parsed.path, flags=re.I)
    path = re.sub(r"\.html$", "", path, flags=re.I)
    if path != "/":
        path = path.rstrip("/")
    path = path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return path + query


def check_vercel_routes(root: Path, vercel: dict[str, Any]) -> CheckResult:
    errors: list[str] = []
    if vercel.get("cleanUrls") is not True:
        errors.append("vercel.json: cleanUrls must remain true")
    if vercel.get("trailingSlash") is not False:
        errors.append("vercel.json: trailingSlash must remain false")

    migration_sources: set[str] = set()
    migration_count = 0
    for section in ("redirects", "rewrites"):
        rules = vercel.get(section, [])
        if not isinstance(rules, list):
            errors.append(f"vercel.json: {section} must be an array")
            continue
        seen: set[str] = set()
        for index, rule in enumerate(rules):
            label = f"vercel.json {section}[{index}]"
            if not isinstance(rule, dict):
                errors.append(f"{label}: rule must be an object")
                continue
            source = rule.get("source")
            destination = rule.get("destination")
            if not isinstance(source, str) or not isinstance(destination, str):
                errors.append(f"{label}: source and destination must be strings")
                continue
            if ".html" in source.lower() or ".html" in destination.lower():
                errors.append(f"{label}: cleanUrls rules cannot contain .html ({source} -> {destination})")
            if source in seen:
                errors.append(f"{label}: duplicate source {source!r} within {section}")
            seen.add(source)

            conditional = bool(rule.get("has") or rule.get("missing"))
            if section == "redirects" and not conditional:
                migration_count += 1
                if source in migration_sources:
                    errors.append(f"{label}: duplicate migration redirect source {source!r}")
                migration_sources.add(source)
                if rule.get("permanent") is not True:
                    errors.append(f"{label}: migration redirect must be permanent")
                if clean_public_path(source) == clean_public_path(destination):
                    errors.append(f"{label}: self-loop {source} -> {destination}")

            parsed = urlsplit(destination)
            if parsed.scheme in {"http", "https"}:
                if parsed.netloc.lower() not in {"revelationagency.com", "www.revelationagency.com"}:
                    continue
                if ":path*" in parsed.path:
                    continue
            if ":path*" not in parsed.path and not static_target_exists(root, parsed.path):
                errors.append(f"{label}: destination does not resolve locally: {destination}")

    canonical_rules = [
        rule for rule in vercel.get("redirects", [])
        if isinstance(rule, dict)
        and rule.get("source") == "/:path*"
        and rule.get("destination") == "https://www.revelationagency.com/:path*"
        and any(
            isinstance(condition, dict)
            and condition.get("type") == "host"
            and condition.get("value") == "revelationagency.com"
            for condition in rule.get("has", [])
        )
        and rule.get("permanent") is True
    ]
    if len(canonical_rules) != 1:
        errors.append("vercel.json: expected one permanent apex-to-www host-conditioned redirect")

    rewrites = {
        (str(rule.get("source")), str(rule.get("destination")))
        for rule in vercel.get("rewrites", [])
        if isinstance(rule, dict)
    }
    expected_rewrites = {
        ("/g/bill", "/sales-growth-engine?ref=bill-gerard"),
        ("/partners/bill", "/sales-growth-engine?ref=bill-gerard"),
    }
    if rewrites != expected_rewrites:
        errors.append(f"vercel.json: sales aliases mismatch; expected {sorted(expected_rewrites)}, got {sorted(rewrites)}")

    migration_redirects = {
        str(rule.get("source")): str(rule.get("destination"))
        for rule in vercel.get("redirects", [])
        if isinstance(rule, dict) and not rule.get("has") and not rule.get("missing")
    }
    for source, destination in EXPECTED_CORRECTED_ROUTE_REDIRECTS.items():
        actual = migration_redirects.get(source)
        if actual != destination:
            errors.append(
                f"vercel.json: corrected route must redirect {source} directly to "
                f"{destination}, got {actual!r}"
            )
    if "/services/marketing/digital-ads" in migration_redirects:
        errors.append(
            "vercel.json: /services/marketing/digital-ads is canonical Marketing work, "
            "not a redirect source"
        )
    if migration_count != 38:
        errors.append(f"vercel.json: expected 38 clean migration redirects, found {migration_count}")

    return CheckResult(
        "vercel-clean-routing",
        f"{migration_count} migration redirects, {len(vercel.get('rewrites', []))} rewrites, canonical host rule checked",
        errors,
    )


def meta_content_values(text: str, attribute: str, name: str) -> list[str]:
    tag_pattern = re.compile(
        rf'<meta\b(?=[^>]*\b{re.escape(attribute)}=["\']{re.escape(name)}["\'])[^>]*>',
        re.I,
    )
    values: list[str] = []
    for match in tag_pattern.finditer(text):
        content = re.search(r'\bcontent=["\']([^"\']*)["\']', match.group(0), re.I)
        values.append(content.group(1) if content else "")
    return values


def check_social_metadata(root: Path, html_files: list[Path]) -> CheckResult:
    expected = "https://www.revelationagency.com/assets/brand/current/ra-social-card.png"
    errors: list[str] = []
    for path in html_files:
        rel = posix_rel(path, root)
        text = read_text(path)
        for attribute, name, wanted in (
            ("property", "og:image", expected),
            ("property", "og:image:width", "1200"),
            ("property", "og:image:height", "630"),
            ("name", "twitter:card", "summary_large_image"),
            ("name", "twitter:image", expected),
        ):
            values = meta_content_values(text, attribute, name)
            if values != [wanted]:
                errors.append(f"{rel}: expected one {name}={wanted!r}, got {values!r}")
        if "/assets/img/og-share.svg" in text or "/assets/images/generated/" in text:
            errors.append(f"{rel}: retired or nonexistent social preview remains")
        favicon_links = re.findall(
            r'<link\b(?=[^>]*\brel=["\'][^"\']*icon[^"\']*["\'])[^>]*>',
            text,
            re.I,
        )
        expected_favicons = {
            '<link rel="icon" href="/favicon.ico" sizes="any">',
            '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">',
            '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
        }
        if set(favicon_links) != expected_favicons or len(favicon_links) != 3:
            errors.append(f"{rel}: favicon set is not the canonical ICO + PNG32 + Apple trio")
    return CheckResult(
        "social-preview-metadata",
        f"{len(html_files)} HTML social-preview heads checked",
        errors,
    )


def check_sitemap_contract(root: Path) -> CheckResult:
    errors: list[str] = []
    sitemap_path = root / "sitemap.xml"
    proposed_path = root / "artifacts" / "proposed-routes.json"
    if not sitemap_path.is_file() or not proposed_path.is_file():
        return CheckResult(
            "canonical-sitemap",
            "sitemap and proposed-route artifact required",
            ["sitemap.xml or artifacts/proposed-routes.json is missing"],
        )
    urls = re.findall(r"<loc>([^<]+)</loc>", read_text(sitemap_path))
    proposed = load_json(proposed_path).get("urls", [])
    if len(urls) != len(proposed):
        errors.append(
            f"sitemap.xml: expected {len(proposed)} canonical URLs "
            f"(artifacts/proposed-routes.json), found {len(urls)}"
        )
    if len(urls) != len(set(urls)):
        errors.append("sitemap.xml: duplicate URLs found")
    if set(urls) != set(proposed):
        errors.append(
            "sitemap.xml does not exactly match artifacts/proposed-routes.json; "
            f"missing={sorted(set(proposed) - set(urls))[:8]} extra={sorted(set(urls) - set(proposed))[:8]}"
        )
    service_paths = {
        urlsplit(url).path
        for url in urls
        if urlsplit(url).path.startswith("/services/")
    }
    if service_paths != EXPECTED_SERVICE_CANONICAL_PATHS:
        errors.append(
            "sitemap.xml: corrected 5/4/4 service architecture mismatch; "
            f"missing={sorted(EXPECTED_SERVICE_CANONICAL_PATHS - service_paths)} "
            f"extra={sorted(service_paths - EXPECTED_SERVICE_CANONICAL_PATHS)}"
        )
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "www.revelationagency.com":
            errors.append(f"sitemap.xml: noncanonical host URL {url}")
        if ".html" in parsed.path.lower() or (parsed.path != "/" and parsed.path.endswith("/")):
            errors.append(f"sitemap.xml: URL violates clean/no-trailing contract: {url}")
        if not static_target_exists(root, parsed.path):
            errors.append(f"sitemap.xml: URL has no local source target: {url}")
    priority_by_url: dict[str, str] = {}
    for block in re.findall(r"<url>(.*?)</url>", read_text(sitemap_path), re.S):
        loc = re.search(r"<loc>([^<]+)</loc>", block)
        value = re.search(r"<priority>([^<]+)</priority>", block)
        if loc and value:
            priority_by_url[loc.group(1)] = value.group(1)
    expected_hub_priorities = {
        "https://www.revelationagency.com/services/branding": "0.9",
        "https://www.revelationagency.com/services/marketing": "0.9",
        "https://www.revelationagency.com/services/sales": "0.9",
        "https://www.revelationagency.com/the-reveal": "0.8",
    }
    for url, wanted in expected_hub_priorities.items():
        if priority_by_url.get(url) != wanted:
            errors.append(
                f"sitemap.xml: expected hub priority {wanted} for {url}, "
                f"got {priority_by_url.get(url)!r}"
            )
    return CheckResult(
        "canonical-sitemap",
        f"{len(urls)} clean canonical URLs compared to proposed route inventory",
        errors,
    )


def check_structured_data_json(root: Path, html_files: list[Path]) -> CheckResult:
    errors: list[str] = []
    blocks = 0
    creative_works = 0
    for path in html_files:
        rel = posix_rel(path, root)
        text = read_text(path)
        for match in re.finditer(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', text, re.I | re.S):
            blocks += 1
            raw = match.group(1).strip()
            if "&amp;" in raw:
                errors.append(f"{rel}: JSON-LD contains an HTML entity instead of raw JSON text")
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD: {exc}")
                continue
            items = value if isinstance(value, list) else [value]
            creative_works += sum(
                1 for item in items
                if isinstance(item, dict) and item.get("@type") == "CreativeWork"
            )
    if creative_works != EXPECTED_CASE_COUNT:
        errors.append(f"expected {EXPECTED_CASE_COUNT} CreativeWork JSON-LD records, found {creative_works}")
    return CheckResult(
        "structured-data-json",
        f"{blocks} JSON-LD blocks parsed; {creative_works} CreativeWork records",
        errors,
    )


def check_public_taxonomy(root: Path, html_files: list[Path], vercel: dict[str, Any]) -> CheckResult:
    redirect_sources = [
        str(rule.get("source"))
        for rule in vercel.get("redirects", [])
        if isinstance(rule, dict) and rule.get("source") and not rule.get("has") and not rule.get("missing")
    ]
    errors: list[str] = []
    checked = 0
    for path in html_files:
        rel = posix_rel(path, root)
        if page_is_redirected(rel, redirect_sources):
            continue
        checked += 1
        text = read_text(path)
        if rel.startswith("portfolio/case-studies/"):
            for blocker in (
                "More Creative Engagements",
                "Browse all creative case studies",
                "View creative work",
                '<div class="cs-cross__lbl">Creative</div>',
            ):
                if blocker.lower() in text.lower():
                    errors.append(f"{rel}: legacy case-study taxonomy remains: {blocker}")
            if "net-metering-systems" in rel and '<div class="cs-cross__lbl">Systems</div>' in text:
                errors.append(f"{rel}: NMS cross-card still labels CRM/automation work as Systems")
            for blocker in (
                ">Paid Ads</a>",
                '<div class="cs-cross__title">Paid Ads</div>',
                '<span class="eyebrow">05 &mdash; The Paid Ads</span>',
                '<span class="lbl">Creative</span><span class="val">Video-fed campaigns</span>',
            ):
                if blocker in text:
                    errors.append(f"{rel}: case-study service UI remains outside the 2026 taxonomy: {blocker}")
        if rel == "services.html":
            if "Brand Systems &middot; Website" in text:
                errors.append(f"{rel}: featured-work label still uses retired Brand Systems wording")
            retired_card_cats = re.findall(
                r'<a\b[^>]*class="[^"]*pf-card[^"]*"[^>]*\bdata-cat="[^"]*(?:strategy|creative)[^"]*"',
                text,
                re.I,
            )
            if retired_card_cats:
                errors.append(f"{rel}: {len(retired_card_cats)} featured-work cards retain retired data-cat values")
        if rel == "the-reveal/index.html":
            for blocker in ('data-filter="strategy"', 'data-filter="creative"', 'data-cat="strategy"', 'data-cat="creative"'):
                if blocker in text:
                    errors.append(f"{rel}: retired editorial filter remains: {blocker}")
            if "Strategy. Insights. Announcements." in text:
                errors.append(f"{rel}: retired Strategy-led editorial subtitle remains")
        if rel.startswith("the-reveal/") and re.search(
            r'<span class="ar-hero__tag[^>]*>\s*(?:Strategy|Creative)\s*</span>', text, re.I
        ):
            errors.append(f"{rel}: retired editorial hero taxonomy remains")
        if re.search(r"AI\s*(?:&|&amp;)\s*Automation", text, re.I):
            errors.append(f"{rel}: retired AI & Automation service label remains")
        if re.search(
            r'<span><i class="fa-regular fa-folder"></i>\s*(?:Strategy|Creative)\s*</span>',
            text,
            re.I,
        ):
            errors.append(f"{rel}: retired editorial folder taxonomy remains")
        if re.search(r'<div class="faq-insight__tag">\s*(?:Strategy|Creative|Systems)\s*</div>', text, re.I):
            errors.append(f"{rel}: retired FAQ insight taxonomy remains")
        for retired_title in (
            "SEO &amp; AI Visibility",
            "Websites &amp; Landing Pages",
            "Back to Website Development",
        ):
            if retired_title.lower() in text.lower():
                errors.append(f"{rel}: retired service title remains: {retired_title}")
        retired_related = re.findall(
            r'<h3\b[^>]*>\s*(Outsourced Marketing|Performance Marketing (?:&|&amp;) Paid Ads|Website Development|Video Production|Sales Infrastructure|Search Rankings (?:&|&amp;) SEO)\s*</h3>',
            text,
            re.I,
        )
        if retired_related:
            errors.append(f"{rel}: retired related-service heading(s) remain: {retired_related}")
        for blocker in (
            ">Systems Work<",
            ">Creative Work<",
            "What is the Systems Build",
            "Systems &middot; Creative &middot; Marketing",
            "Strategy · Web · Product · Visual",
            "paid social program",
        ):
            if blocker.lower() in text.lower():
                errors.append(f"{rel}: stale public architecture copy remains: {blocker}")
        for pattern, label in (
            (r'href=["\']/services/sales["\'][^>]*>\s*Sales\s*<', "bare Sales service-parent label"),
            (r'href=["\']/portfolio/sales["\'][^>]*>\s*Sales Work\s*<', "bare Sales portfolio-parent label"),
            (r'<h1[^>]*>\s*Sales Services\b', "bare Sales Services H1"),
            (r'<h1[^>]*>\s*Sales work\.', "bare Sales portfolio H1"),
            (r'data-filter=["\']sales["\'][^>]*>\s*Sales\s*<', "bare Sales filter label"),
            (r'Case Study · (?:Branding · )?Marketing · Sales(?! Systems)', "bare Sales case-study eyebrow"),
            (r'Branding, Marketing (?:&|&amp;) Sales(?! Systems)', "bare Sales ampersand phrase"),
            (r'Branding · Marketing · Sales(?! Systems)', "bare Sales dot-navigation phrase"),
        ):
            if re.search(pattern, text, re.I):
                errors.append(f"{rel}: public pillar must say Sales Systems ({label})")
    return CheckResult(
        "public-brand-taxonomy",
        f"{checked} non-redirect public/source pages checked for Branding / Marketing / Sales Systems alignment",
        errors,
    )


def check_proof_safety(root: Path) -> CheckResult:
    scopes: list[tuple[str, list[Path], list[tuple[str, re.Pattern[str]]]]] = [
        (
            "Net Metering Systems",
            sorted((root / "portfolio" / "case-studies").glob("net-metering-systems*.html"))
            + [root / "portfolio" / "systems" / "ai-automation.html"],
            [
                ("$50 claim", re.compile(r"\$50", re.I)),
                ("25% appointment claim", re.compile(r"25%\s+lead-to-appointment", re.I)),
                ("5x return claim", re.compile(r"5x.{0,30}(?:ROAS|return)", re.I | re.S)),
                ("unsupported return claim", re.compile(r"positive return on ad spend", re.I)),
                ("unproved automation count", re.compile(r"\b12\s+management automations?\b", re.I)),
            ],
        ),
        (
            "Trust Energy",
            sorted((root / "portfolio" / "case-studies").glob("trust-energy*.html"))
            + [
                root / "services.html",
                root / "services" / "marketing" / "digital-ads.html",
                root / "services" / "systems" / "brand-systems.html",
                root / "portfolio" / "marketing" / "digital-ads.html",
                root / "portfolio" / "systems" / "ai-automation.html",
            ],
            [
                ("$25 claim", re.compile(r"\$25", re.I)),
                ("$40-$50 benchmark", re.compile(r"\$40\s*[-–]\s*\$50", re.I)),
                ("appointment ratio", re.compile(r"1-in-4|1:4", re.I)),
                ("exact tenure", re.compile(r"\b4\s+years?\b|\bfour years\b", re.I)),
                ("industry comparison", re.compile(r"half-industry\s+CPL", re.I)),
            ],
        ),
        (
            "Highlands Energy",
            sorted((root / "portfolio" / "case-studies").glob("highlands-energy*.html")),
            [
                ("$9 claim", re.compile(r"\$9", re.I)),
                ("CPL benchmark multiplier", re.compile(r"3\s*[-–]\s*5x", re.I)),
            ],
        ),
    ]
    errors: list[str] = []
    files_checked: set[Path] = set()
    for project, paths, patterns in scopes:
        for path in paths:
            if not path.is_file():
                continue
            files_checked.add(path)
            text = read_text(path)
            rel = posix_rel(path, root)
            for label, pattern in patterns:
                if pattern.search(text):
                    errors.append(f"{rel}: {project} proof ledger blocks {label}")
    return CheckResult(
        "portfolio-proof-safety",
        f"{len(files_checked)} proof-sensitive files checked against quarantine patterns",
        errors,
    )


def strip_query_fragment(path: str) -> str:
    return unquote(urlsplit(path).path)


def static_target_exists(root: Path, url_path: str) -> bool:
    path = strip_query_fragment(url_path)
    if not path.startswith("/") or path.startswith("//"):
        return True
    relative = path.lstrip("/")
    candidates: list[Path] = []
    if not relative:
        candidates.append(root / "index.html")
    else:
        exact = root / PurePosixPath(relative)
        candidates.append(exact)
        if path.endswith("/"):
            candidates.append(exact / "index.html")
        elif PurePosixPath(relative).suffix:
            # Explicit extension: only the exact static file is valid.
            pass
        else:
            candidates.append(root / PurePosixPath(relative + ".html"))
            candidates.append(exact / "index.html")
    return any(candidate.is_file() for candidate in candidates)


def match_route_rule(path: str, rules: list[dict[str, Any]]) -> Optional[str]:
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        # Host/header-conditional rules cannot be inferred from a bare link.
        if rule.get("has") or rule.get("missing"):
            continue
        source = rule.get("source")
        destination = rule.get("destination")
        if not isinstance(source, str) or not isinstance(destination, str):
            continue
        if ":path*" in source:
            prefix = source.split(":path*", 1)[0]
            if path.startswith(prefix):
                tail = path[len(prefix):]
                return destination.replace(":path*", tail)
        elif source == path:
            return destination
    return None


def root_link_resolves(root: Path, raw_path: str, vercel: dict[str, Any]) -> bool:
    path = strip_query_fragment(raw_path)
    if static_target_exists(root, path):
        return True

    redirects = vercel.get("redirects", []) if isinstance(vercel, dict) else []
    rewrites = vercel.get("rewrites", []) if isinstance(vercel, dict) else []
    destination = match_route_rule(path, redirects) or match_route_rule(path, rewrites)
    if not destination:
        return False
    parsed = urlsplit(destination)
    if parsed.scheme in {"http", "https"} and parsed.netloc not in {
        "revelationagency.com", "www.revelationagency.com"
    }:
        return True
    return static_target_exists(root, parsed.path)


def check_root_relative_links(root: Path, html_files: list[Path], vercel: dict[str, Any]) -> CheckResult:
    errors: list[str] = []
    checked = 0
    for path in html_files:
        parser = RootLinkParser()
        parser.feed(read_text(path))
        rel = posix_rel(path, root)
        for line, tag, attr, value in parser.links:
            checked += 1
            if not root_link_resolves(root, value, vercel):
                errors.append(
                    f"{rel}:{line}: <{tag}> {attr}={value!r} does not resolve as a file, clean URL, "
                    "redirect, or rewrite"
                )
    return CheckResult(
        "root-relative-link-resolution",
        f"{checked} root-relative href/src/action references checked offline",
        errors,
    )


def check_service_proof_alignment(root: Path) -> CheckResult:
    """Require every service-specific proof card to carry that service code."""
    errors: list[str] = []
    manifest = load_json(root / "assets/data/portfolio-taxonomy-2026.json")
    masters = manifest.get("masterCardsByRoute", {}) if isinstance(manifest, dict) else {}
    checked = 0

    for code, rel in EXPECTED_SERVICE_LEAVES.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: canonical service leaf is missing")
            continue
        text = read_text(path)
        if f'data-service-code="{code}"' not in text:
            errors.append(f"{rel}: hero does not declare service code {code}")
        section = re.search(
            r'<section\b[^>]*class=["\'][^"\']*\bra-service-proof-section\b[^"\']*["\'][^>]*>.*?</section>',
            text,
            re.I | re.S,
        )
        if not section:
            errors.append(f"{rel}: service proof/proof-standard section is missing")
            continue
        slugs = re.findall(
            r'href=["\']/portfolio/case-studies/([^"\'/?#]+)',
            section.group(0),
            re.I,
        )
        if code == "S1":
            if slugs:
                errors.append(f"{rel}: Outreach has no ratified S1 proof but publishes {slugs}")
            if "Proof Standard" not in section.group(0):
                errors.append(f"{rel}: Outreach must state the no-invented-proof standard")
            continue
        if len(slugs) != 3:
            errors.append(f"{rel}: expected 3 service-specific proof cards, found {len(slugs)}")
        for slug in slugs:
            checked += 1
            record = masters.get(f"/portfolio/case-studies/{slug}.html")
            disciplines = record.get("disciplines", []) if isinstance(record, dict) else []
            if code not in disciplines:
                errors.append(f"{rel}: {slug} does not carry {code} in the portfolio manifest")

    return CheckResult(
        "service-proof-taxonomy",
        f"{len(EXPECTED_SERVICE_LEAVES)} service leaves and {checked} attributed proof cards checked",
        errors,
    )


def check_mobile_navigation_contract(root: Path, html_files: list[Path]) -> CheckResult:
    """Protect the canonical desktop mega-menu and mobile accordion."""
    errors: list[str] = []
    nav_pages = 0
    retired_markers: list[str] = []
    for path in html_files:
        text = read_text(path)
        rel = posix_rel(path, root)
        if 'id="ra-nav"' in text:
            nav_pages += 1
            nav_match = re.search(r'<nav\b[^>]*id=["\']ra-nav["\'][^>]*>.*?</nav>', text, re.I | re.S)
            if not nav_match:
                errors.append(f"{rel}: canonical nav could not be isolated")
            else:
                nav = nav_match.group(0)
                for href, label in EXPECTED_PORTFOLIO_NAV_LINKS.items():
                    pattern = (
                        r'<a\b[^>]*href=["\']' + re.escape(href) + r'["\'][^>]*>\s*'
                        + re.escape(label) + r'\s*</a>'
                    )
                    if not re.search(pattern, nav, re.I):
                        errors.append(f"{rel}: Portfolio menu missing {label!r} -> {href}")
                for href, label in (
                    ("/portfolio/branding", "Branding Work"),
                    ("/portfolio/marketing", "Marketing Work"),
                    ("/portfolio/sales", "Sales Systems Work"),
                ):
                    if not re.search(
                        r'<a\b[^>]*href=["\']' + re.escape(href) + r'["\'][^>]*>\s*'
                        + re.escape(label) + r'\s*<i\b',
                        nav,
                        re.I,
                    ):
                        errors.append(f"{rel}: Portfolio parent missing {label!r} -> {href}")
                if not re.search(r'href=["\']/portfolio["\'][^>]*>\s*All Work\s*</a>', nav, re.I):
                    errors.append(f"{rel}: Portfolio menu missing All Work link")
        if any(
            marker in text
            for marker in (
                "RA-MOBILE-NAV-JS-FIX-START",
                "RA-MOBILE-NAV-FIX-START",
                "NAV-3L-MOBILE",
                "NAV-REBUILD-MOBILE",
                "NAV-3L-JS",
                "NAV-REBUILD-JS",
            )
        ):
            retired_markers.append(rel)
        if re.search(r"</nav>\s*<script>(?:(?!</script>).)*?ra-nav-hamburger", text, re.I | re.S):
            retired_markers.append(rel + " (post-nav handler)")
        for pattern, label in (
            (r"classList\.toggle\(['\"]is-open['\"]", "inline is-open controller"),
            (r"document\.querySelectorAll\(['\"]\.has-drop-l3 > a['\"]\)", "inline label controller"),
            (r"document\.querySelectorAll\(['\"]\.ra-nav__services-toggle['\"]\)", "inline level-one controller"),
            (r"document\.querySelectorAll\(['\"]\.ra-nav__l2-toggle['\"]\)", "inline level-two controller"),
            (
                r"(?:var|let|const)\s+(?:ham|hamBtn)\s*=\s*document\.getElementById"
                r"\(['\"]ra-nav-hamburger['\"]\)",
                "dead inline hamburger binding",
            ),
        ):
            if re.search(pattern, text):
                retired_markers.append(rel + f" ({label})")
    if retired_markers:
        errors.append(
            "retired page-local mobile-nav overrides remain: "
            + ", ".join(retired_markers[:12])
        )

    css = read_text(root / "assets/css/ra-refresh-2026.css")
    for token in (
        "body.ra-mobile-nav-open chat-widget",
        "#ra-nav.is-open .ra-nav__links",
        "grid-template-columns: minmax(0, 1fr)",
        ".p-leaf",
        ".ra-orbit__frame:not(.ra-orbit--active)",
        "#ra-nav .ra-nav__links > li.has-drop > .ra-drop--l2",
        "grid-template-columns: repeat(3, minmax(0, 1fr))",
        "top: calc(100% + 14px)",
        "#ra-nav .ra-nav__links .ra-drop--l2 > .has-drop-l3:hover > a",
        "@media (min-width: 1200px)",
        "@media (max-width: 1199px)",
        "flex-direction: column !important",
        "align-items: stretch !important",
    ):
        if token not in css:
            errors.append(f"assets/css/ra-refresh-2026.css: missing navigation contract token {token!r}")

    shared_nav_css = read_text(root / "assets/css/ra-nav-footer.css")
    if "@media (max-width: 1199px)" not in shared_nav_css:
        errors.append("assets/css/ra-nav-footer.css: compact accordion breakpoint must extend through 1199px")
    for token in ("min-width: 220px", "left: calc(100% + 6px)"):
        if token in shared_nav_css:
            errors.append(f"assets/css/ra-nav-footer.css: retired compact flyout token remains {token!r}")

    js = read_text(root / "assets/js/ra-refresh-2026.js")
    for token in (
        "function setupMobileNavigation()",
        'doc.body.classList.toggle("ra-mobile-nav-open", open)',
        "window.location.assign(anchor.href)",
        "event.stopImmediatePropagation()",
        'var mobileQuery = window.matchMedia("(max-width: 1199px)")',
    ):
        if token not in js:
            errors.append(f"assets/js/ra-refresh-2026.js: missing mobile contract token {token!r}")

    if nav_pages < 100:
        errors.append(f"only {nav_pages} HTML pages expose the canonical mobile navigation")
    return CheckResult(
        "mobile-navigation-contract",
        f"{nav_pages} nav pages; desktop 5 / 4 / 4 mega-menu plus mobile accordion and chat rules checked",
        errors,
    )


def check_responsive_spacing_contract(root: Path, html_files: list[Path]) -> CheckResult:
    """Guard the exact mobile defects reported from the production phone UI."""
    errors: list[str] = []
    proof_images = 0
    outcome_pages = 0
    for path in html_files:
        text = read_text(path)
        rel = posix_rel(path, root)
        outcome_pages += int('class="cs-outcomes"' in text)
        for card in re.findall(
            r'<a\b[^>]*class=["\'][^"\']*\bra-service-proof\b[^"\']*["\'][^>]*>.*?</a>',
            text,
            re.I | re.S,
        ):
            image = re.search(r'<img\b[^>]*>', card, re.I)
            if not image:
                errors.append(f"{rel}: service proof card has no image")
                continue
            proof_images += 1
            tag = image.group(0)
            width = re.search(r'\bwidth=["\'](\d+)["\']', tag, re.I)
            height = re.search(r'\bheight=["\'](\d+)["\']', tag, re.I)
            if not width or not height or (int(width.group(1)), int(height.group(1))) != (1600, 900):
                errors.append(f"{rel}: proof image must declare its natural 1600x900 size: {tag}")

    if proof_images < 40:
        errors.append(f"expected the shared service proof cards across the site, found only {proof_images} images")

    css = read_text(root / "assets/css/ra-refresh-2026.css")
    for token in (
        ".ra-service-proof img",
        "height: auto;",
        "aspect-ratio: 16 / 9;",
        ".container > .pf-grid",
        ".cs-outcomes__inner",
        ".cs-outcomes__grid",
        "#hero-network",
        ".ra-orbit__summary",
        "@media (max-width: 360px)",
        "@media (min-width: 1200px)",
        "rgba(255, 255, 255, 0.78) !important",
    ):
        if token not in css:
            errors.append(f"assets/css/ra-refresh-2026.css: missing responsive spacing token {token!r}")
    if re.search(r"animation:\s*ra-orbit-(?:node-signal|core-breathe)", css):
        errors.append("assets/css/ra-refresh-2026.css: removed widget pulse loops are still active")

    portfolio_css = read_text(root / "assets/css/portfolio-cards-v3.css")
    if re.search(r"\.pf-grid\s*\{.*?padding:\s*0\s+24px", portfolio_css, re.S):
        errors.append("assets/css/portfolio-cards-v3.css: nested portfolio grid still adds a second 24px gutter")

    homepage = read_text(root / "index.html")
    for retired in (
        'class="ra-orbit__grid"',
        'class="ra-orbit__sweep"',
        'ra-orbit__route--triangle',
        'ra-orbit__track--inner',
        'class="ra-orbit__capability"',
        'class="ra-orbit__caption"',
    ):
        if retired in homepage:
            errors.append(f"index.html: crowded orbit element remains: {retired}")
    route_count = len(re.findall(r'class="ra-orbit__route\s+ra-orbit__route--', homepage))
    if route_count != 3:
        errors.append(f"index.html: simplified orbit must expose exactly 3 direct routes, found {route_count}")
    if "Sales Systems turn that attention into revenue." not in homepage:
        errors.append("index.html: plain-language connected-system summary is missing")
    if "We help with Branding, Marketing &amp; Sales Systems" not in homepage:
        errors.append("index.html: approved Branding / Marketing / Sales Systems hero tagline is missing")
    approved_home_intro = (
        "Revelation Agency helps you run your Branding, Marketing, and Sales as one connected growth system "
        "— operator-led, deliberately scoped, and backed by receipts."
    )
    if approved_home_intro not in homepage:
        errors.append("index.html: approved connected-growth hero paragraph is missing")
    approved_connected_delivery = (
        "We diagnose the constraint, choose the exact services it requires, and operate Branding, Marketing, "
        "and Sales Systems as one connected system. Websites, campaigns, CRM, and AI automation share clear "
        "handoffs instead of becoming disconnected projects."
    )
    if approved_connected_delivery not in homepage:
        errors.append("index.html: generated Connected Delivery section has drifted from its current source contract")
    if "Explore Sales Systems" not in homepage or "Explore Sales <" in homepage:
        errors.append("index.html: Sales Systems service CTA is not using the approved public pillar label")
    proof_note_pages = (
        root / "portfolio/case-studies/reservwise-app.html",
        root / "portfolio/case-studies/revelation-portal.html",
    )
    for proof_note_page in proof_note_pages:
        if 'cs-gallery__item--proof-note' not in read_text(proof_note_page):
            errors.append(f"{proof_note_page.relative_to(root).as_posix()}: text gallery proof note lacks its responsive wrap hook")
    if ".cs-gallery__item--proof-note" not in css or "overflow-wrap: anywhere;" not in css:
        errors.append("assets/css/ra-refresh-2026.css: text gallery proof-note wrapping contract is missing")
    if ".ra-proof-logo--trust" not in css or "padding: clamp(28px, 8vw, 112px)" not in css:
        errors.append("assets/css/ra-refresh-2026.css: Trust Energy logo proof lacks responsive padding")
    for trust_logo_page in (
        root / "portfolio/case-studies/trust-energy.html",
        root / "portfolio/case-studies/trust-energy-branding.html",
    ):
        trust_logo_text = read_text(trust_logo_page)
        if 'class="ra-proof-logo--trust"' not in trust_logo_text:
            errors.append(f"{trust_logo_page.relative_to(root).as_posix()}: Trust Energy logo proof hook is missing")
        if re.search(r'trust-energy/logo\.png[^>]*padding:\s*140px', trust_logo_text, re.I):
            errors.append(f"{trust_logo_page.relative_to(root).as_posix()}: fixed 140px logo padding still crops mobile proof")
    if ".cs-service-card p" not in css or "word-break: break-word;" not in css:
        errors.append("assets/css/ra-refresh-2026.css: long case-study technical strings lack a wrapping contract")
    hosting = read_text(root / "web-hosting.html")
    if 'class="wh-hero__crumb-current"' not in hosting or ".wh-hero__crumbs{display:flex;flex-wrap:wrap" not in hosting:
        errors.append("web-hosting.html: mobile breadcrumb wrapping contract is missing")
    for deck_path in (root / "sales-growth-engine/index.html", root / "sales-intelligence/index.html"):
        deck = read_text(deck_path)
        for token in (".slide-header__left { flex: 1 1 auto; min-width: 0", ".slide-header__doc-sep { display: none; }"):
            if token not in deck:
                errors.append(f"{deck_path.relative_to(root).as_posix()}: mobile deck header constraint is missing ({token})")

    return CheckResult(
        "responsive-spacing-contract",
        f"{proof_images} 16:9 proof images, {outcome_pages} outcome pages, simplified orbit, and single-gutter portfolio checked",
        errors,
    )


def check_generator_guardrails(root: Path) -> CheckResult:
    """Ensure superseded authors cannot silently restore the retired site."""
    errors: list[str] = []
    retired = {
        "scripts/regen_sitemap.py": "write_vercel_and_sitemap.py",
        "scripts/build_pillar_pages.py": "apply_2026_portfolio_taxonomy.py",
        "scripts/rewrite_nav_footer.py": "apply_2026_site_refresh.py",
        "scripts/repair_p5_pillar_nav_footer.py": "apply_2026_site_refresh.py",
        "scripts/build_landing_pages.py": "apply_2026_site_refresh.py",
        "scripts/mobile_nav_fix_v1.py": "apply_2026_site_refresh.py",
    }
    for rel, successor in retired.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: retired generator is missing rather than explicitly guarded")
            continue
        text = read_text(path)
        if "DEPRECATED:" not in text or "raise SystemExit(" not in text:
            errors.append(f"{rel}: retired generator does not fail closed")
        if successor not in text:
            errors.append(f"{rel}: deprecation message does not name successor {successor}")
    return CheckResult(
        "retired-generator-guardrails",
        f"{len(retired)} superseded page/route authors checked for fail-closed behavior",
        errors,
    )


def load_vercel(root: Path) -> tuple[dict[str, Any], list[str]]:
    path = root / "vercel.json"
    if not path.is_file():
        return {}, ["vercel.json is missing; redirect/rewrite-aware checks cannot run accurately"]
    try:
        data = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"vercel.json is invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return {}, ["vercel.json must contain a JSON object"]
    return data, []


def parse_args(argv: list[str]) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help=f"repository root (default: {default_root})",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=60,
        help="maximum actionable errors printed per check (default: 60; use 0 for all)",
    )
    return parser.parse_args(argv)


def render_results(results: list[CheckResult], max_errors: int) -> int:
    print("Revelation Agency 2026 refresh verification (offline, read-only)")
    print("=" * 66)
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"[{status}] {result.name}: {result.summary}")
        if not result.ok:
            shown = result.errors if max_errors == 0 else result.errors[:max_errors]
            for error in shown:
                print(f"       - {error}")
            remaining = len(result.errors) - len(shown)
            if remaining > 0:
                print(f"       - ... {remaining} additional error(s) omitted; rerun with --max-errors 0")
    failures = [result for result in results if not result.ok]
    print("-" * 66)
    print(f"Result: {len(results) - len(failures)}/{len(results)} checks passed")
    return 1 if failures else 0


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"Verifier error: repository root does not exist: {root}", file=sys.stderr)
        return 2

    html_files = sorted(root.rglob("*.html"))
    vercel, vercel_errors = load_vercel(root)

    results = [
        check_vercel_routes(root, vercel),
        check_global_includes(root, html_files),
        check_old_logo_references(root, html_files),
        check_case_page_metadata(root),
        check_portfolio_manifest(root),
        check_portfolio_cards(root),
        check_legacy_footers(root, html_files, vercel),
        check_brand_assets(root),
        check_generated_visual_system(root),
        check_social_metadata(root, html_files),
        check_sitemap_contract(root),
        check_structured_data_json(root, html_files),
        check_public_taxonomy(root, html_files, vercel),
        check_proof_safety(root),
        check_root_relative_links(root, html_files, vercel),
        check_service_proof_alignment(root),
        check_mobile_navigation_contract(root, html_files),
        check_responsive_spacing_contract(root, html_files),
        check_generator_guardrails(root),
    ]
    if vercel_errors:
        results.insert(0, CheckResult("vercel-routing-config", "vercel.json is required", vercel_errors))
    return render_results(results, max(0, args.max_errors))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Verification interrupted.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:  # Keep unexpected verifier defects distinct from site failures.
        print(f"Verifier error: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
