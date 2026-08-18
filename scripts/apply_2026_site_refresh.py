#!/usr/bin/env python3
"""Apply the 2026 Revelation Agency brand and architecture across static HTML.

This is an idempotent, local-only migration. It does not call the network,
submit forms, publish, or deploy. The two goals are to make every source page
inherit one visual system and to make internal routes safe under Vercel's
cleanUrls/no-trailing-slash configuration.
"""

from __future__ import annotations

import json
import posixpath
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.rglob("*.html"))
CSS_MARKER = "<!-- RA-REFRESH-2026:css -->"
JS_MARKER = "<!-- RA-REFRESH-2026:js -->"
REFRESH_ASSET_VERSION = "20260817f"
REFRESH_CSS_URL = f"/assets/css/ra-refresh-2026.css?v={REFRESH_ASSET_VERSION}"
REFRESH_JS_URL = f"/assets/js/ra-refresh-2026.js?v={REFRESH_ASSET_VERSION}"
APEX = "https://www.revelationagency.com"

REVEAL_CATEGORY_BY_SLUG = {
    "why-ai-answer-engines-are-rewriting-the-seo-playbook": "Marketing",
    "video-is-no-longer-optional-its-infrastructure": "Branding",
    "the-paid-ads-playbook-is-dead": "Marketing",
    "your-brand-isnt-what-you-say-it-is": "Branding",
    "the-website-is-still-your-most-important-real-estate": "Branding",
    "why-social-media-reach-is-a-vanity-metric": "Marketing",
    "what-gohighlevel-actually-does": "Sales Systems",
    "outsourcing-your-marketing-isnt-a-shortcut": "Marketing",
    "the-ai-content-trap": "Marketing",
}

REVEAL_RELATED_SERVICE_BY_SLUG = {
    "outsourcing-your-marketing-isnt-a-shortcut": "Marketing Services",
    "the-ai-content-trap": "Digital Advertising",
    "the-paid-ads-playbook-is-dead": "Digital Advertising",
    "the-website-is-still-your-most-important-real-estate": "Websites",
    "video-is-no-longer-optional-its-infrastructure": "Video",
    "what-gohighlevel-actually-does": "CRMs / Sales Tools",
    "why-ai-answer-engines-are-rewriting-the-seo-playbook": "SEO / AI Answers",
}

GENERATED_VISUAL_BY_REL = {
    "services/ai-automation.html": "ai-automation",
    "the-reveal/straight-answers.html": "reveal-straight-answers",
    "the-reveal/video-is-no-longer-optional-its-infrastructure.html":
        "reveal-video-infrastructure",
}


def generated_visual_for_rel(rel: str) -> str | None:
    """Return the restrained editorial visual family for a public page."""
    if rel.startswith("services/branding/"):
        return "branding"
    if rel.startswith("services/marketing/"):
        return "marketing"
    if rel.startswith("services/sales/"):
        return "sales"
    return GENERATED_VISUAL_BY_REL.get(rel)


def normalize_generated_visual(text: str, rel: str) -> str:
    """Keep visual assignments explicit and idempotent on the body element."""
    theme = generated_visual_for_rel(rel)
    body_match = re.search(r"<body\b[^>]*>", text, re.I | re.S)
    if not body_match:
        return text

    body_tag = body_match.group(0)
    body_tag = re.sub(
        r"\s+data-ra-visual=(?:\"[^\"]*\"|'[^']*')",
        "",
        body_tag,
        flags=re.I,
    )
    if theme:
        body_tag = body_tag[:-1] + f' data-ra-visual="{theme}">'
    return text[:body_match.start()] + body_tag + text[body_match.end():]


def normalize_generated_visual_sources(text: str, rel: str) -> str:
    """Replace the two weakest Reveal placeholders with first-party art."""
    article_visuals = {
        "the-reveal/straight-answers.html":
            "/assets/brand/visuals/2026/reveal-straight-answers.webp",
        "the-reveal/video-is-no-longer-optional-its-infrastructure.html":
            "/assets/brand/visuals/2026/reveal-video-infrastructure.webp",
    }
    article_visual = article_visuals.get(rel)
    if article_visual:
        text = re.sub(
            r"(?<=\.ar-hero__bg\{position:absolute;inset:0;background-image:)url\([^)]*\)",
            f"url('{article_visual}')",
            text,
            count=1,
        )

    if rel != "the-reveal/index.html":
        return text

    card_visuals = {
        "/the-reveal/straight-answers":
            "/assets/brand/visuals/2026/reveal-straight-answers.webp",
        "/the-reveal/video-is-no-longer-optional-its-infrastructure":
            "/assets/brand/visuals/2026/reveal-video-infrastructure.webp",
    }
    for href, image_path in card_visuals.items():
        pattern = re.compile(
            rf'<a\b(?=[^>]*\bhref="{re.escape(href)}")(?=[^>]*\bclass="[^"]*\brv-card__img\b[^"]*")[^>]*>',
            re.I,
        )

        def replace_card(match: re.Match[str]) -> str:
            tag = re.sub(
                r"\s+style=(?:\"[^\"]*\"|'[^']*')",
                "",
                match.group(0),
                flags=re.I,
            )
            style = (
                "background-image:linear-gradient(135deg,rgba(17,17,17,0.16),"
                f"rgba(17,17,17,0.48)),url('{image_path}');"
                "background-size:cover;background-position:center;"
            )
            return tag[:-1] + f' style="{style}">'

        text, count = pattern.subn(replace_card, text, count=1)
        if count != 1:
            raise ValueError(f"Reveal visual card not found for {href}")
    return text


SERVICE_LIST = """<ul class="ra-footer__svc">
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="/services/branding">Branding<span class="ra-footer__svc-caret" aria-hidden="true">&#9662;</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="/services/branding/websites-landing-pages">Websites</a></li>
              <li><a href="/services/branding/apps-digital-products">Apps</a></li>
              <li><a href="/services/branding/brand-strategy-identity">Brand Identity</a></li>
              <li><a href="/services/branding/design">Design</a></li>
              <li><a href="/services/branding/video-visual-content">Video</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="/services/marketing">Marketing<span class="ra-footer__svc-caret" aria-hidden="true">&#9662;</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="/services/marketing/seo-ai-visibility">SEO / AI Answers</a></li>
              <li><a href="/services/marketing/social-media">Social Media</a></li>
              <li><a href="/services/marketing/digital-ads">Digital Advertising</a></li>
              <li><a href="/services/marketing/email-lifecycle-marketing">Customer Nurture</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="/services/sales">Sales Systems<span class="ra-footer__svc-caret" aria-hidden="true">&#9662;</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="/services/sales/lead-generation-outreach">Outreach</a></li>
              <li><a href="/services/sales/lead-gen-ads">Lead Gen Ads</a></li>
              <li><a href="/services/sales/crm-sales-infrastructure">CRMs / Sales Tools</a></li>
              <li><a href="/services/sales/ai-automation-systems">AI Automation Systems</a></li>
            </ul>
          </li>
        </ul>"""


def build_nav_links(rel: str) -> str:
    """Render one public Branding / Marketing / Sales Systems taxonomy."""
    current = {
        "home": rel == "index.html",
        "about": rel == "about.html",
        "services": rel == "services.html" or rel.startswith("services/"),
        "reveal": rel.startswith("the-reveal/"),
        "portfolio": rel == "portfolio.html" or rel.startswith("portfolio/"),
        "contact": rel == "contact.html",
    }

    def active(key: str) -> str:
        return ' class="is-current"' if current[key] else ""

    return f"""<ul class="ra-nav__links">
      <li><a href="/"{active("home")}>Home</a></li>
      <li><a href="/about"{active("about")}>About</a></li>
      <li class="has-drop">
        <a href="/services"{active("services")}>Services <i class="fa-solid fa-chevron-down" style="font-size:9px;margin-left:3px;"></i></a>
        <button class="ra-nav__services-toggle" type="button" aria-label="Toggle Services menu" aria-expanded="false">&#9662;</button>
        <ul class="ra-drop ra-drop--l2">
          <li class="has-drop-l3">
            <a href="/services/branding">Branding <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Branding menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="/services/branding/websites-landing-pages">Websites</a></li>
              <li><a href="/services/branding/apps-digital-products">Apps</a></li>
              <li><a href="/services/branding/brand-strategy-identity">Brand Identity</a></li>
              <li><a href="/services/branding/design">Design</a></li>
              <li><a href="/services/branding/video-visual-content">Video</a></li>
            </ul>
          </li>
          <li class="has-drop-l3">
            <a href="/services/marketing">Marketing <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Marketing menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="/services/marketing/seo-ai-visibility">SEO / AI Answers</a></li>
              <li><a href="/services/marketing/social-media">Social Media</a></li>
              <li><a href="/services/marketing/digital-ads">Digital Advertising</a></li>
              <li><a href="/services/marketing/email-lifecycle-marketing">Customer Nurture</a></li>
            </ul>
          </li>
          <li class="has-drop-l3">
            <a href="/services/sales">Sales Systems <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Sales Systems menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="/services/sales/lead-generation-outreach">Outreach</a></li>
              <li><a href="/services/sales/lead-gen-ads">Lead Gen Ads</a></li>
              <li><a href="/services/sales/crm-sales-infrastructure">CRMs / Sales Tools</a></li>
              <li><a href="/services/sales/ai-automation-systems">AI Automation Systems</a></li>
            </ul>
          </li>
        </ul>
      </li>
      <li><a href="/the-reveal"{active("reveal")}>The Reveal</a></li>
      <li class="has-drop">
        <a href="/portfolio"{active("portfolio")}>Portfolio <i class="fa-solid fa-chevron-down" style="font-size:9px;margin-left:3px;"></i></a>
        <button class="ra-nav__services-toggle" type="button" aria-label="Toggle Portfolio menu" aria-expanded="false">&#9662;</button>
        <ul class="ra-drop ra-drop--l2">
          <li class="has-drop-l3">
            <a href="/portfolio/branding">Branding Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Branding portfolio menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="/portfolio?filter=b1">Websites</a></li>
              <li><a href="/portfolio?filter=b2">Apps</a></li>
              <li><a href="/portfolio?filter=b3">Brand Identity</a></li>
              <li><a href="/portfolio?filter=b4">Design</a></li>
              <li><a href="/portfolio?filter=b5">Video</a></li>
            </ul>
          </li>
          <li class="has-drop-l3">
            <a href="/portfolio/marketing">Marketing Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Marketing portfolio menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="/portfolio?filter=m1">SEO / AI Answers</a></li>
              <li><a href="/portfolio?filter=m2">Social Media</a></li>
              <li><a href="/portfolio?filter=m3">Digital Advertising</a></li>
              <li><a href="/portfolio?filter=m4">Customer Nurture</a></li>
            </ul>
          </li>
          <li class="has-drop-l3">
            <a href="/portfolio/sales">Sales Systems Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Sales Systems portfolio menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="/portfolio?filter=s1">Outreach</a></li>
              <li><a href="/portfolio?filter=s2">Lead Gen Ads</a></li>
              <li><a href="/portfolio?filter=s3">CRMs / Sales Tools</a></li>
              <li><a href="/portfolio?filter=s4">AI Automation Systems</a></li>
            </ul>
          </li>
          <li><a href="/portfolio" style="padding:10px 12px;font-size:13px;color:var(--charcoal);opacity:0.7;">All Work</a></li>
        </ul>
      </li>
      <li><a href="/contact"{active("contact")}>Contact</a></li>
    </ul>"""


HERO_VISUAL = """      <div class="ra-hero__visual">
        <div class="ra-orbit" role="group" aria-label="Branding, Marketing, and Sales Systems connected as one growth system">
          <div class="ra-orbit__frame">
            <svg class="ra-orbit__routes" viewBox="0 0 620 620" preserveAspectRatio="none" aria-hidden="true" focusable="false">
              <path class="ra-orbit__route ra-orbit__route--branding" d="M310 310 C310 250 310 196 310 142"></path>
              <path class="ra-orbit__route ra-orbit__route--marketing" d="M310 310 C252 342 202 395 146 464"></path>
              <path class="ra-orbit__route ra-orbit__route--sales" d="M310 310 C368 342 418 395 474 464"></path>
            </svg>
            <div class="ra-orbit__track ra-orbit__track--outer" aria-hidden="true"><i></i></div>
            <a class="ra-orbit__node ra-orbit__node--branding" href="/services/branding">
              <span>01 /</span>
              <strong>Branding</strong>
            </a>
            <a class="ra-orbit__node ra-orbit__node--marketing" href="/services/marketing">
              <span>02 /</span>
              <strong>Marketing</strong>
            </a>
            <a class="ra-orbit__node ra-orbit__node--sales" href="/services/sales">
              <span>03 /</span>
              <strong>Sales Systems</strong>
            </a>
            <div class="ra-orbit__core">
              <img src="/assets/brand/current/ra-mark-red.png" alt="" width="116" height="116">
            </div>
          </div>
          <p class="ra-orbit__summary">Branding makes you clear. Marketing earns attention. Sales Systems turn that attention into revenue.</p>
        </div>
      </div>"""


SPRINT_REPLACEMENT = """<!-- ==================== CONNECTED DELIVERY ==================== -->
<section class="ra-sprint" id="connected-delivery">
  <div class="ra-sprint__glow-l"></div>
  <div class="ra-sprint__glow-r"></div>
  <div class="container">
    <div class="ra-sprint__inner">
      <div class="fade-up">
        <span class="eyebrow eyebrow--white">Connected Delivery</span>
        <h2 class="display-2 ra-sprint__title">One <span class="highlight">Growth System</span></h2>
        <p class="ra-sprint__desc">We diagnose the constraint, choose the exact services it requires, and operate Branding, Marketing, and Sales Systems as one connected system. Websites, campaigns, CRM, and AI automation share clear handoffs instead of becoming disconnected projects.</p>
        <ul class="ra-sprint__list">
          <li><i class="fa-solid fa-stethoscope"></i> Diagnose the highest-leverage constraint</li>
          <li><i class="fa-solid fa-fingerprint"></i> Sharpen the position and brand people remember</li>
          <li><i class="fa-solid fa-window-maximize"></i> Build the surfaces where attention converts</li>
          <li><i class="fa-solid fa-signal"></i> Create visibility, authority, and qualified demand</li>
          <li><i class="fa-solid fa-route"></i> Connect CRM, follow-up, and the path to revenue</li>
          <li><i class="fa-solid fa-receipt"></i> Instrument the work so decisions have receipts</li>
        </ul>
        <a href="/services" class="btn btn--white">Explore the Connected System <i class="fa-solid fa-arrow-right btn-arrow"></i></a>
      </div>
      <div class="fade-up fade-up-d2">
        <div class="ra-sprint__visual">
          <div class="ra-sprint__fw-head">
            <div>
              <div class="ra-sprint__fw-title">Operating Framework</div>
              <div class="ra-sprint__fw-sub">Brand · Demand · Revenue</div>
            </div>
            <div class="ra-sprint__fw-meta">System<strong>Connected</strong></div>
          </div>
          <div class="ra-sprint__fw-steps">
            <div class="ra-sprint__fw-step" data-progress="88"><div><div class="ra-sprint__fw-step-phase">01 Diagnose</div><div class="ra-sprint__fw-step-label">Constraint</div></div><div class="ra-sprint__fw-step-track"><div class="ra-sprint__fw-step-bar"></div></div><div class="ra-sprint__fw-step-week">READ</div></div>
            <div class="ra-sprint__fw-step" data-progress="82"><div><div class="ra-sprint__fw-step-phase">02 Position</div><div class="ra-sprint__fw-step-label">Brand</div></div><div class="ra-sprint__fw-step-track"><div class="ra-sprint__fw-step-bar"></div></div><div class="ra-sprint__fw-step-week">ALIGN</div></div>
            <div class="ra-sprint__fw-step" data-progress="76"><div><div class="ra-sprint__fw-step-phase">03 Build</div><div class="ra-sprint__fw-step-label">Surfaces</div></div><div class="ra-sprint__fw-step-track"><div class="ra-sprint__fw-step-bar"></div></div><div class="ra-sprint__fw-step-week">MAKE</div></div>
            <div class="ra-sprint__fw-step" data-progress="70"><div><div class="ra-sprint__fw-step-phase">04 Activate</div><div class="ra-sprint__fw-step-label">Demand</div></div><div class="ra-sprint__fw-step-track"><div class="ra-sprint__fw-step-bar"></div></div><div class="ra-sprint__fw-step-week">EARN</div></div>
            <div class="ra-sprint__fw-step" data-progress="84"><div><div class="ra-sprint__fw-step-phase">05 Convert</div><div class="ra-sprint__fw-step-label">Pipeline</div></div><div class="ra-sprint__fw-step-track"><div class="ra-sprint__fw-step-bar"></div></div><div class="ra-sprint__fw-step-week">MOVE</div></div>
            <div class="ra-sprint__fw-step" data-progress="94"><div><div class="ra-sprint__fw-step-phase">06 Prove</div><div class="ra-sprint__fw-step-label">Receipts</div></div><div class="ra-sprint__fw-step-track"><div class="ra-sprint__fw-step-bar"></div></div><div class="ra-sprint__fw-step-week">LEARN</div></div>
          </div>
          <div class="ra-sprint__fw-foot"><span><span class="ra-sprint__fw-foot-dot"></span>Operator-led</span><span>Scoped to the constraint</span></div>
        </div>
        <div class="ra-sprint__stats" style="margin-top:16px;">
          <div class="ra-sprint__stat"><div class="ra-sprint__stat-num">One</div><div class="ra-sprint__stat-label">Connected system</div></div>
          <div class="ra-sprint__stat"><div class="ra-sprint__stat-num">Three</div><div class="ra-sprint__stat-label">Public pillars</div></div>
          <div class="ra-sprint__stat"><div class="ra-sprint__stat-num">Live</div><div class="ra-sprint__stat-label">Decision receipts</div></div>
          <div class="ra-sprint__stat"><div class="ra-sprint__stat-num">Fit</div><div class="ra-sprint__stat-label">Scoped delivery</div></div>
        </div>
      </div>
    </div>
  </div>
</section>"""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def clean_route(path: str) -> str:
    """Convert a URL path to the Vercel cleanUrls/no-trailing form."""
    if not path:
        return "/"
    route = "/" + path.lstrip("/")
    route = re.sub(r"/index\.html$", "", route, flags=re.I)
    route = re.sub(r"\.html$", "", route, flags=re.I)
    if route != "/":
        route = route.rstrip("/")
    return route or "/"


def build_redirect_map() -> dict[str, str]:
    config = json.loads(read(ROOT / "vercel.json"))
    mapped: dict[str, str] = {}
    for item in config.get("redirects", []):
        source = item.get("source", "")
        destination = item.get("destination", "")
        if not source or not destination or ":" in source or "*" in source:
            continue
        dest_parts = urlsplit(destination)
        dest = clean_route(dest_parts.path)
        if dest_parts.query:
            dest += "?" + dest_parts.query
        mapped[clean_route(source)] = dest
    return mapped


REDIRECTS = build_redirect_map()


def follow_redirect(route: str) -> str:
    current = route
    seen: set[str] = set()
    while current in REDIRECTS and current not in seen:
        seen.add(current)
        current = REDIRECTS[current]
        if "?" in current:
            break
    return current


def route_for_file(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return follow_redirect(clean_route(rel))


def replace_balanced_tag(text: str, start: int, tag: str, replacement: str) -> tuple[str, bool]:
    pattern = re.compile(rf"</?{re.escape(tag)}\b[^>]*>", re.I)
    depth = 0
    for match in pattern.finditer(text, start):
        token = match.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[match.end():], True
        else:
            depth += 1
    return text, False


def replace_footer_services(text: str) -> tuple[str, bool]:
    marker = '<ul class="ra-footer__svc">'
    start = text.find(marker)
    if start < 0:
        return text, False
    return replace_balanced_tag(text, start, "ul", SERVICE_LIST)


def normalize_nav(text: str, rel: str) -> str:
    nav_start = text.find("<!-- RA-NAV-CANONICAL-START -->")
    nav_end = text.find("<!-- RA-NAV-CANONICAL-END -->", nav_start + 1) if nav_start >= 0 else -1
    if nav_start < 0:
        nav_start = text.find("<nav")
    if nav_start < 0:
        return text
    if nav_end < 0:
        close = text.find("</nav>", nav_start)
        nav_end = close + len("</nav>") if close >= 0 else -1
    if nav_end < 0:
        return text

    links_start = text.find('<ul class="ra-nav__links">', nav_start, nav_end)
    if links_start >= 0:
        text, _ = replace_balanced_tag(text, links_start, "ul", build_nav_links(rel))
        nav_end = text.find("<!-- RA-NAV-CANONICAL-END -->", nav_start + 1)
        if nav_end < 0:
            close = text.find("</nav>", nav_start)
            nav_end = close + len("</nav>") if close >= 0 else -1
    if nav_end < 0:
        return text

    segment = text[nav_start:nav_end]
    segment = re.sub(
        r'(<a\b[^>]*class=["\'][^"\']*ra-nav__logo[^"\']*["\'][^>]*>\s*<img\b[^>]*\bsrc=["\'])[^"\']+(["\'])',
        r'\1/assets/brand/current/ra-mark-red.png\2',
        segment,
        count=1,
        flags=re.I | re.S,
    )

    def normalize_nav_mark(match: re.Match[str]) -> str:
        tag = re.sub(r'\s+(?:width|height)=["\'][^"\']*["\']', "", match.group(0), flags=re.I)
        return tag[:-1].rstrip() + ' width="640" height="640">'

    segment = re.sub(
        r'<img\b(?=[^>]*\bsrc=["\']/assets/brand/current/ra-mark-red\.png["\'])[^>]*>',
        normalize_nav_mark,
        segment,
        count=1,
        flags=re.I,
    )
    return text[:nav_start] + segment + text[nav_end:]


def remove_retired_mobile_nav_overrides(text: str) -> str:
    """Remove page-local mobile-nav patches now owned by the shared assets.

    The retired capture handler treated category links as accordion controls,
    so a tap could animate a submenu instead of navigating to the selected
    service page. Page-local CSS also competed with the desktop mega-menu and
    produced off-canvas dark panels on narrow iPhones. The 2026 experience
    layer now owns this behavior once, sitewide.
    """
    text = re.sub(
        r"\s*/\* RA-MOBILE-NAV-FIX-START.*?/\* RA-MOBILE-NAV-FIX-END \*/\s*",
        "\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\s*<!-- RA-MOBILE-NAV-JS-FIX-START.*?<!-- RA-MOBILE-NAV-JS-FIX-END -->\s*",
        "\n",
        text,
        flags=re.S,
    )

    # Retire the earlier page-local accordion models. They used competing
    # `.is-open` and `.open` conventions and duplicated the shared runtime.
    # Keep the surrounding @media block intact while removing only the named
    # rule groups.
    for marker, following in (
        ("NAV-3L-MOBILE", "LOGO-MOBILE-FIRM|NAV-3L-HIERARCHY|NAV-REBUILD-MOBILE"),
        ("LOGO-MOBILE-FIRM", "NAV-3L-HIERARCHY|NAV-REBUILD-MOBILE"),
        ("NAV-3L-HIERARCHY", "NAV-REBUILD-MOBILE"),
    ):
        text = re.sub(
            rf"\s*/\* {marker} \*/.*?(?=\s*/\* (?:{following}) \*/|\n\}})",
            "\n",
            text,
            flags=re.S,
        )
    text = re.sub(
        r"\s*/\* NAV-REBUILD-MOBILE \*/.*?(?=\n\})",
        "\n",
        text,
        flags=re.S,
    )

    # The external 2026 experience layer is the sole navigation controller.
    # Remove the immediate post-nav script that previously wired hamburger,
    # label, and chevron handlers a second time.
    text = re.sub(
        r"(</nav>)\s*<script>(?:(?!</script>).)*?ra-nav-hamburger(?:(?!</script>).)*?</script>",
        r"\1",
        text,
        count=1,
        flags=re.S | re.I,
    )

    # Some older pages appended the same handlers to a larger page script
    # instead of the immediate post-nav script. Remove only the named tails,
    # preserving the surrounding page IIFE and its real functionality.
    text = re.sub(
        r"\s*/\* NAV-3L-JS \*/.*?(?=\n\s*\}\)\(\);)",
        "\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\s*/\* NAV-REBUILD-JS \*/\s*\(function\(\)\{.*?\n\s*\}\)\(\);",
        "\n",
        text,
        flags=re.S,
    )

    # Earlier templates also embedded unmarked copies of the same handlers in
    # their main page scripts. Remove those bounded statements while keeping
    # scroll, reveal, canvas, filter, and other page behavior intact.
    text = re.sub(
        r"^[ \t]*if\s*\(\s*ham\s*&&\s*nav\s*\)\s*ham\.addEventListener\([^\r\n]*nav\.classList\.toggle\(['\"]is-open['\"]\)[^\r\n]*\r?\n?",
        "",
        text,
        flags=re.M,
    )
    text = re.sub(
        r"^(?P<indent>[ \t]*)if\s*\(\s*btn\s*&&\s*nav\s*\)\s*\{\r?\n"
        r".*?^(?P=indent)\}\r?\n?",
        "",
        text,
        flags=re.M | re.S,
    )

    # A pre-release pass used an insufficiently anchored version of the rule
    # above and could leave `); }` after removing the click callback.  Repair
    # only that exact hamburger-declaration shape while retaining a following
    # `nav` declaration used by unrelated sticky-scroll code.
    def repair_partial_hamburger_block(match: re.Match[str]) -> str:
        return match.group("nav") or ""

    text = re.sub(
        r"^[ \t]*(?:var|let|const)\s+btn\s*=\s*document\.getElementById\(['\"]ra-nav-hamburger['\"]\);\r?\n"
        r"(?P<nav>^[ \t]*(?:var|let|const)\s+nav\s*=\s*document\.getElementById\(['\"]ra-nav['\"]\);\r?\n)?"
        r"^[ \t]*\);\r?\n^[ \t]*\}\r?\n?",
        repair_partial_hamburger_block,
        text,
        flags=re.M,
    )
    text = re.sub(
        r"^[ \t]*(?:var|let|const)\s+(?:ham|hamBtn)\s*=\s*"
        r"document\.getElementById\(['\"]ra-nav-hamburger['\"]\);\r?\n",
        "",
        text,
        flags=re.M,
    )
    # Remove complete selector-owned forEach statements before considering any
    # compact one-line variants.  Matching the closing line at the opener's
    # indentation keeps nested event-handler closures inside the deletion.
    for selector in (
        r"\.ra-nav__services-toggle",
        r"\.has-drop-l3 > a",
        r"\.ra-nav__l2-toggle",
    ):
        text = re.sub(
            rf"^(?P<indent>[ \t]*)document\.querySelectorAll\(['\"]{selector}['\"]\)"
            rf"\.forEach\(function\([^)]*\)\{{\r?\n.*?^(?P=indent)\}}\);\r?\n?",
            "",
            text,
            flags=re.M | re.S,
        )

    # Repair the twelve retained redirect documents that an older cleanup pass
    # left with the forEach opener removed but its anchor callback still in
    # place.  This is deliberately bounded to the legacy anchor variable and
    # the two matching statement closures.
    text = re.sub(
        r"^(?P<indent>[ \t]*)anchor\.addEventListener\(['\"]click['\"],\s*function\(ev\)\{\r?\n"
        r".*?^(?P=indent)\}\);\r?\n^[ \t]*\}\);\r?\n?",
        "",
        text,
        flags=re.M | re.S,
    )
    text = re.sub(
        r"\s*\(function\(\)\{\s*var\s+navEl\s*=\s*document\.getElementById\(['\"]ra-nav['\"]\);.*?\n\s*\}\)\(\);\s*",
        "\n",
        text,
        flags=re.S,
    )
    return text


def normalize_brand_image_dimensions(text: str) -> str:
    """Give the square supplied lockup an intrinsic ratio to avoid layout shift."""

    def normalize_lockup(match: re.Match[str]) -> str:
        tag = re.sub(r'\s+(?:width|height)=["\'][^"\']*["\']', "", match.group(0), flags=re.I)
        return tag[:-1].rstrip() + ' width="960" height="960">'

    return re.sub(
        r'<img\b(?=[^>]*\bsrc=["\']/assets/brand/current/ra-lockup-red\.png["\'])[^>]*>',
        normalize_lockup,
        text,
        flags=re.I,
    )


def normalize_href(value: str, rel_path: str) -> str:
    raw = value.strip()
    if not raw or raw.startswith(("#", "?", "//")):
        return value
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc or raw.lower().startswith(("mailto:", "tel:", "javascript:", "data:")):
        return value

    if parsed.path.startswith("/"):
        resolved = posixpath.normpath(parsed.path)
    else:
        base = "/" + posixpath.dirname(rel_path)
        resolved = posixpath.normpath(posixpath.join(base, parsed.path))
    if not resolved.startswith("/"):
        resolved = "/" + resolved

    # Only route-like documents get clean URL treatment. Assets keep suffixes.
    if resolved.lower().endswith(".html") or resolved.endswith("/"):
        resolved = clean_route(resolved)
    resolved = follow_redirect(resolved)

    # A mapped destination may include a query string.
    mapped = urlsplit(resolved)
    query = mapped.query or parsed.query
    return urlunsplit(("", "", mapped.path, query, parsed.fragment))


def normalize_internal_hrefs(text: str, rel_path: str) -> str:
    attr = re.compile(r"(?P<prefix>\bhref\s*=\s*)(?P<quote>[\"'])(?P<value>.*?)(?P=quote)", re.I)

    def repl(match: re.Match[str]) -> str:
        value = normalize_href(match.group("value"), rel_path)
        return match.group("prefix") + match.group("quote") + value + match.group("quote")

    return attr.sub(repl, text)


def normalize_external_target_security(text: str) -> str:
    """Make new-tab anchors explicit about opener/referrer isolation."""
    pattern = re.compile(
        r'<a\b(?=[^>]*\btarget=["\']_blank["\'])(?![^>]*\brel=)([^>]*)>',
        re.I,
    )
    return pattern.sub(r'<a\1 rel="noopener noreferrer">', text)


def normalize_favicon_links(text: str) -> str:
    text = re.sub(
        r'\s*<!-- RA-REFRESH-2026:favicons -->.*?<!-- /RA-REFRESH-2026:favicons -->\s*',
        "\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r'\s*<link\b(?=[^>]*\brel=["\'][^"\']*icon[^"\']*["\'])[^>]*>\s*',
        "\n",
        text,
        flags=re.I,
    )
    block = (
        '<!-- RA-REFRESH-2026:favicons -->\n'
        '<link rel="icon" href="/favicon.ico" sizes="any">\n'
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">\n'
        '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n'
        '<!-- /RA-REFRESH-2026:favicons -->\n'
    )
    return text.replace("</head>", block + "</head>", 1)


def replace_meta_url(text: str, property_name: str, url: str) -> str:
    tag_pattern = re.compile(
        rf"<meta\b[^>]*\bproperty=[\"']{re.escape(property_name)}[\"'][^>]*>", re.I
    )
    match = tag_pattern.search(text)
    if not match:
        return text
    tag = re.sub(r"\bcontent=[\"'][^\"']*[\"']", f'content="{url}"', match.group(0), count=1, flags=re.I)
    return text[:match.start()] + tag + text[match.end():]


def replace_or_insert_meta(text: str, attribute: str, name: str, content: str) -> str:
    pattern = re.compile(
        rf'<meta\b(?=[^>]*\b{re.escape(attribute)}=["\']{re.escape(name)}["\'])[^>]*>',
        re.I,
    )
    match = pattern.search(text)
    if match:
        tag = match.group(0)
        if re.search(r'\bcontent=["\'][^"\']*["\']', tag, re.I):
            tag = re.sub(
                r'\bcontent=["\'][^"\']*["\']',
                f'content="{content}"',
                tag,
                count=1,
                flags=re.I,
            )
        else:
            tag = tag[:-1] + f' content="{content}">'
        return text[:match.start()] + tag + text[match.end():]
    return text.replace(
        "</head>",
        f'<meta {attribute}="{name}" content="{content}">\n</head>',
        1,
    )


def normalize_metadata(text: str, route: str) -> str:
    canonical_url = APEX + ("/" if route == "/" else route.split("?", 1)[0])
    canonical_tag = re.compile(r"<link\b[^>]*\brel=[\"']canonical[\"'][^>]*>", re.I)
    match = canonical_tag.search(text)
    if match:
        tag = re.sub(r"\bhref=[\"'][^\"']*[\"']", f'href="{canonical_url}"', match.group(0), count=1, flags=re.I)
        text = text[:match.start()] + tag + text[match.end():]
    else:
        text = text.replace("</head>", f'<link rel="canonical" href="{canonical_url}">\n</head>', 1)

    text = replace_meta_url(text, "og:url", canonical_url)
    # Structured-data URLs must follow the same clean-URL contract as the
    # canonical tag. This is intentionally scoped to first-party absolute
    # document URLs so image and third-party URLs remain untouched.
    text = re.sub(
        r'https://www\.revelationagency\.com(?P<path>/[^"\'<>\s]*?)\.html(?P<suffix>["\'])',
        lambda match: APEX + clean_route(match.group("path") + ".html") + match.group("suffix"),
        text,
    )
    if not re.search(r'<meta\b[^>]*\bproperty=["\']og:site_name["\']', text, re.I):
        text = text.replace(
            "</head>",
            '<meta property="og:site_name" content="Revelation Agency">\n</head>',
            1,
        )
    # Social previews are a brand surface. Retire the old orange SVG and all
    # inconsistent page-level previews in favor of the supplied-logo card.
    social_url = APEX + "/assets/brand/current/ra-social-card.png"
    text = replace_or_insert_meta(text, "property", "og:image", social_url)
    text = replace_or_insert_meta(text, "property", "og:image:width", "1200")
    text = replace_or_insert_meta(text, "property", "og:image:height", "630")
    text = replace_or_insert_meta(text, "name", "twitter:card", "summary_large_image")
    text = replace_or_insert_meta(text, "name", "twitter:image", social_url)

    # Keep the palette token last so first-run insertions cannot reorder it on
    # the idempotence pass.
    text = re.sub(
        r'<meta\b(?=[^>]*\bname=["\']theme-color["\'])[^>]*>\s*',
        "",
        text,
        flags=re.I,
    )
    text = text.replace(
        "</head>",
        '<meta name="theme-color" content="#C91C1D">\n</head>',
        1,
    )
    return text


def normalize_reveal_taxonomy(text: str, rel: str) -> str:
    if rel == "the-reveal/index.html":
        text = text.replace(
            "Strategy. Insights. Announcements. We don't just do the work &mdash; we explain how it works.",
            "Branding. Marketing. Sales Systems. We do the work, show the receipts, and explain the operating logic.",
        )
        text = text.replace('data-chip-filter="strategy">Strategy', 'data-chip-filter="branding">Branding')
        text = text.replace('data-chip-filter="creative">Creative', 'data-chip-filter="sales">Sales')
        text = text.replace('data-filter="strategy">Strategy', 'data-filter="branding">Branding')
        text = text.replace('data-filter="creative">Creative', 'data-filter="sales">Sales')
        text = re.sub(
            r'(data-chip-filter="sales">)Sales(?: Systems)*',
            r'\1Sales Systems',
            text,
        )
        text = re.sub(
            r'(data-filter="sales">)Sales(?: Systems)*',
            r'\1Sales Systems',
            text,
        )

        def card_repl(match: re.Match[str]) -> str:
            block = match.group(0)
            for slug, category in REVEAL_CATEGORY_BY_SLUG.items():
                if f'/the-reveal/{slug}' not in block:
                    continue
                token = "sales" if category == "Sales Systems" else category.lower()
                block = re.sub(r'data-cat=["\'][^"\']+["\']', f'data-cat="{token}"', block, count=1)
                block = re.sub(
                    r'(<span class="rv-card__tag">).*?(</span>)',
                    rf'\1{category}\2',
                    block,
                    count=1,
                    flags=re.S,
                )
                break
            return block

        text = re.sub(r'<article\b[^>]*class="[^"]*rv-card[^"]*".*?</article>', card_repl, text, flags=re.S | re.I)
        return text

    if rel.startswith("the-reveal/"):
        slug = Path(rel).stem
        category = REVEAL_CATEGORY_BY_SLUG.get(slug)
        if category:
            text = re.sub(
                r'(<span class="ar-hero__tag[^>]*>).*?(</span>)',
                rf'\1{category}\2',
                text,
                count=1,
                flags=re.S,
            )
            text = re.sub(
                r'(<span><i class="fa-regular fa-folder"></i>\s*).*?(</span>)',
                rf'\1{category}\2',
                text,
                count=1,
                flags=re.S,
            )
        related_service = REVEAL_RELATED_SERVICE_BY_SLUG.get(slug)
        if related_service:
            text = re.sub(
                r'(<section class="rv-related-services".*?<h3\b[^>]*>).*?(</h3>)',
                rf'\1{related_service}\2',
                text,
                count=1,
                flags=re.I | re.S,
            )
    return text


def replace_home_visual(text: str) -> str:
    start = text.find('      <div class="ra-hero__visual">')
    if start < 0:
        return text
    updated, changed = replace_balanced_tag(text, start, "div", HERO_VISUAL)
    return updated if changed else text


def replace_between_markers(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        return text
    return text[:start] + replacement + "\n\n" + text[end:]


def apply_home_copy(text: str) -> str:
    text = text.replace(
        "Revelation Agency — Your Strategic Growth Partner",
        "Branding, Marketing &amp; Sales | Revelation Agency",
    )
    text = re.sub(
        r'<div class="ra-hero__tagline">.*?</div>',
        '<div class="ra-hero__tagline">We help with Branding, Marketing &amp; Sales Systems</div>',
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace('We help build <em>systems</em><br>that drive your growth', 'Build the brand.<br><em>Create demand.</em><br>Convert the opportunity.')
    text = text.replace(
        'Dream. <span class="highlight">Build.</span> Scale.',
        'Brand. <span class="highlight">Demand.</span> Revenue.',
    )
    text = text.replace('<h3>Dream — Branding</h3>', '<h3>Brand — Identity</h3>')
    text = text.replace('<h3>Build — Marketing</h3>', '<h3>Demand — Marketing</h3>')
    text = text.replace('<h3>Scale — Sales</h3>', '<h3>Revenue — Sales</h3>')
    text = text.replace(
        'Revelation Agency designs, builds, and operates the systems, creative, and marketing infrastructure behind your next stage of growth.',
        'Revelation Agency helps you run your Branding, Marketing, and Sales as one connected growth system — operator-led, deliberately scoped, and backed by receipts.',
    )
    text = re.sub(
        r'(<p class="ra-hero__desc">\s*).*?(\s*</p>)',
        r'\1Revelation Agency helps you run your Branding, Marketing, and Sales as one connected growth system — operator-led, deliberately scoped, and backed by receipts.\2',
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace('View Our Work', 'Explore the Proof')
    text = text.replace('Operators. Not decorators.', 'One connected growth system.')
    home_service_copy = {
        'Identity, websites, apps, and video — built as one connected system, not a folder of assets. The layer people see first, and the layer that governs everything else downstream.':
            'Websites, apps, brand identity, design, and video — the things customers see and use to understand your business.',
        'SEO and AI visibility, positioning and authority, social, and lifecycle marketing — the disciplines that build audience and demand around the brand instead of leaking it into a feed.':
            'SEO / AI Answers, social media, digital advertising, and customer nurture — the work that helps the right people find, remember, and return to you.',
        'Lead generation and outreach, CRM and sales infrastructure, disciplined follow-up, and conversion advertising — the layer that turns attention into pipeline and pipeline into revenue.':
            'Outreach, lead gen ads, CRMs / sales tools, and AI automation systems — the work that creates opportunities and helps your team move them forward.',
        'Earn visibility and authority through the right mix of search, content, social, and lifecycle marketing.':
            'Build demand through SEO / AI Answers, social media, digital advertising, and customer nurture.',
        'Connect leads, CRM, follow-up, and conversion. Measure the handoffs, then improve the system from real evidence.':
            'Connect outreach, lead gen ads, CRMs / sales tools, and AI automation. Measure the handoffs, then improve them from real evidence.',
        'Every engagement starts with diagnosis. We identify the constraint, scope the Branding, Marketing, and Sales disciplines required to solve it, define ownership and evidence, then operate the connected handoffs. AI and automation are woven in only where they improve the system. Strategy, coaching, and fractional advisory remain separate from the Agency offer.':
            'Every engagement starts with diagnosis. We identify the constraint, choose the exact Branding, Marketing, and Sales services required, define ownership and evidence, then operate the handoffs. AI Automation Systems are scoped inside Sales when faster response, routing, or follow-through will improve the result.',
    }
    for old, new in home_service_copy.items():
        text = text.replace(old, new)
    text = replace_home_visual(text)
    text = text.replace('id="ecosystem"', 'id="growth-machine"', 1)
    text = text.replace(
        'Three phases. One integrated system. Every engagement follows the same disciplined arc — from systems through execution to compounding growth.',
        'The brand people remember, the demand you earn, and the sales system that converts it — designed to move as one.',
    )
    # Keep the generated section authoritative after its marker is renamed.
    # The legacy SPRINT marker is retained as a one-way migration fallback.
    text = replace_between_markers(
        text,
        '<!-- ==================== CONNECTED DELIVERY ==================== -->',
        '<!-- ==================== WORK ==================== -->',
        SPRINT_REPLACEMENT,
    )
    text = replace_between_markers(
        text,
        '<!-- ==================== SPRINT ==================== -->',
        '<!-- ==================== WORK ==================== -->',
        SPRINT_REPLACEMENT,
    )
    text = text.replace('Systems, creative, and <span class="highlight">growth</span> — in action.', 'Branding, Marketing, and <span class="highlight">Sales</span> — proven in the work.')
    text = text.replace('Discover. Systematize. <span class="highlight">Create.</span> Market.', 'Diagnose. Build. <span class="highlight">Operate.</span> Prove.')
    text = text.replace('href="/services/systems" class="ra-process__step fade-up fade-up-d1"', 'href="/services" class="ra-process__step fade-up fade-up-d1"')
    text = text.replace('<h3>Discover</h3>\n        <p>Deep audit of brand, sales, digital, and automation. We pull the business apart to find the real constraint — not the symptom.</p>', '<h3>Diagnose</h3>\n        <p>Read the brand, demand, pipeline, and operating reality together. Find the constraint before prescribing the work.</p>')
    text = text.replace('href="/services/systems" class="ra-process__step fade-up fade-up-d2"', 'href="/services/branding" class="ra-process__step fade-up fade-up-d2"')
    text = text.replace('<h3>Systematize</h3>\n        <p>Architect the systems underneath — sales infrastructure, digital presence, and the AI &amp; agentic automation stack. Every layer mapped before a pixel moves.</p>', '<h3>Build the Brand</h3>\n        <p>Align the position, identity, and conversion surfaces so every downstream touchpoint tells the same clear story.</p>')
    text = text.replace('href="/services/creative" class="ra-process__step fade-up fade-up-d3"', 'href="/services/marketing" class="ra-process__step fade-up fade-up-d3"')
    text = text.replace('<h3>Create</h3>\n        <p>Execute with discipline. Websites, branding, apps, video — every asset built on the systems foundation.</p>', '<h3>Create Demand</h3>\n        <p>Earn visibility and authority through the right mix of search, content, social, and lifecycle marketing.</p>')
    text = text.replace('<h3>Market</h3>\n        <p>Activate acquisition. Ads, content, social — running on real infrastructure where measurement maps to revenue.</p>', '<h3>Convert &amp; Improve</h3>\n        <p>Connect leads, CRM, follow-up, and conversion. Measure the handoffs, then improve the system from real evidence.</p>')
    text = text.replace('href="/services" class="ra-process__step fade-up fade-up-d2"', 'href="/services/branding" class="ra-process__step fade-up fade-up-d2"')
    text = text.replace('href="/services/branding" class="ra-process__step fade-up fade-up-d3"', 'href="/services/marketing" class="ra-process__step fade-up fade-up-d3"')
    text = text.replace('href="/services/marketing" class="ra-process__step fade-up fade-up-d4"', 'href="/services/sales" class="ra-process__step fade-up fade-up-d4"')
    text = text.replace(
        'We reveal the <em>secrets</em> of modern marketing',
        'We reveal how <em>connected growth</em> actually works',
    )
    text = text.replace(
        'Strategy. Insights. Announcements. We don\'t just do the work &mdash; we explain how it works.',
        'Branding. Marketing. Sales. We do the work, show the receipts, and explain the operating logic.',
    )
    text = text.replace(
        '<a href="/the-reveal/why-ai-answer-engines-are-rewriting-the-seo-playbook" class="ra-reveal__card ra-reveal__card--d1"',
        '<a href="/the-reveal/why-ai-answer-engines-are-rewriting-the-seo-playbook" class="ra-reveal__card ra-reveal__card--d1"',
    )
    text = re.sub(
        r'(<a href="/the-reveal/why-ai-answer-engines-are-rewriting-the-seo-playbook".*?<span class="ra-reveal__card-tag">).*?(</span>)',
        r'\1Marketing\2',
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace('<span class="ra-reveal__card-tag">Creative</span>', '<span class="ra-reveal__card-tag">Branding</span>')
    text = text.replace('Ready to build the machine behind your growth?', 'Ready to connect the system behind your growth?')
    text = text.replace('<h4>Systems First, Always</h4>', '<h4>Diagnosis First, Always</h4>')
    text = text.replace(
        "Every engagement starts with a deep audit. We don't run ads on a broken foundation. We build the system first, then scale what works.",
        "Every engagement starts with a connected diagnosis. We find the constraint before prescribing the work, then scope only what the evidence requires.",
    )
    text = text.replace(
        '"We built the machine first on ourselves — then applied it to every client engagement. The systems we use aren\'t hypothetical. They\'re the same ones that took Revelation Agency from concept to a full client roster in under 12 months."',
        '"We built the operating system on ourselves first, then carried the discipline into every client engagement. The work is not hypothetical; it is how Revelation runs."',
    )
    text = text.replace(
        'href="/portfolio/case-studies/trust-energy">\n        <div class="ra-work__placeholder" style="background:#1E1E1E url(\'/assets/img/portfolio/trust-energy/thumbnail.png\') center/cover no-repeat;"',
        'href="/portfolio/case-studies/the-whole-vine">\n        <div class="ra-work__placeholder" style="background:#1E1E1E url(\'/assets/img/portfolio/the-whole-vine/thumbnail.png\') center/cover no-repeat;"',
    )
    text = text.replace('Thirty minutes. Real strategy. No pitch. Walk away with clarity on what\'s broken, what matters most, and whether we\'re the right partner to fix it.', 'Bring the real constraint. We\'ll tell you how we see it, where the connected system is breaking, and whether Revelation is the right operator to help.')
    text = text.replace('We build the systems, creative, and marketing infrastructure that growing businesses need but rarely have.', 'We connect the Branding, Marketing, and Sales disciplines growing businesses need but rarely operate as one.')
    text = text.replace('Systems, creative, and marketing are one machine, not three vendors.', 'Branding, Marketing, and Sales are one system, not three disconnected vendors.')
    text = text.replace('What is the Systems Build and is it right for me?', 'How does a connected engagement work?')
    text = text.replace(
        'The Systems Build is our flagship engagement — a structured build of the continuity-holding systems beneath your growth engine: sales infrastructure, digital presence, and an AI &amp; agentic automation stack. It\'s right for you if you\'re spending on marketing without compounding returns, if your operations depend on your personal time rather than a repeatable system, or if you want AI working in your business instead of just talked about. (Looking for strategy, coaching, or advisory? That now lives with Blaine McKenzie at blainemckenzie.com.)',
        'Every engagement starts with diagnosis. We identify the constraint, scope the Branding, Marketing, and Sales disciplines required to solve it, define ownership and evidence, then operate the connected handoffs. AI and automation are woven in only where they improve the system. Strategy, coaching, and fractional advisory remain separate from the Agency offer.',
    )
    text = text.replace(
        'Depends on what you\'re building. Systems Build deliverables are ready within 2–4 months. Creative projects typically run 6–12 weeks. Marketing campaigns generate early signal within 30–60 days, but real compounding growth becomes visible at 90+ days once the system is running properly.',
        'Timing depends on the constraint, baseline, buying cycle, and channel. The scope defines the sequence, leading indicators, decision gates, and definition of done. We report what the evidence supports rather than promising a universal clock.',
    )
    return text


def apply_about_copy(text: str) -> str:
    replacements = {
        'Revelation Agency is a systems-first growth partner for businesses that are done guessing. We don\'t sell tactics in isolation — we audit the foundation, build the assets, and scale what works. Systems, creative, and marketing running as one connected machine.': 'Revelation Agency is the operator-led growth partner for businesses done managing disconnected vendors. We diagnose the constraint, then run Branding, Marketing, and Sales as one connected system with visible receipts.',
        'A short walk-through of the Revelation system — systems, creative, and marketing operating as one connected machine.': 'A short walk-through of Branding, Marketing, and Sales operating as one connected growth system.',
        'We built the opposite — a single partner that owns systems, creative, and marketing as one connected system. Every engagement follows the same disciplined path: audit the foundation, build the assets, scale what works. No shortcuts. No guessing.': 'We built the opposite — one accountable partner connecting the brand people remember, the marketing that earns demand, and the sales system that converts it. Every engagement starts with diagnosis, becomes a deliberate scope, and is operated against evidence.',
        '<h3>Systems Before Execution</h3>': '<h3>Diagnosis Before Prescription</h3>',
        'Every engagement starts with a full-system audit — brand, funnel, digital, AI readiness — before a single asset is built. No guessing which lever moves the number.': 'Every engagement starts with a connected read of brand, demand, pipeline, and operating reality. We find the constraint before prescribing the work.',
        '<h3>Systems Over Tactics</h3>': '<h3>Connected Over Fragmented</h3>',
        'You want systems, creative, and marketing owned by one accountable partner': 'You want Branding, Marketing, and Sales owned by one accountable partner',
        'Every engagement follows the same sequence — because the sequence is the system. Strategy feeds creative. Creative feeds marketing. Marketing feeds back into strategy. The whole thing compounds.': 'Branding shapes what the market remembers. Marketing turns that clarity into demand. Sales converts the demand and feeds the evidence back into the system.',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    old_phases = re.compile(r'<div class="ra-about-approach__phases">.*?</div>\s*\n\s*</div>\s*\n\s*</div>\s*\n</section>', re.S)
    new_phases = """<div class="ra-about-approach__phases">
        <a href="/services/branding" class="ra-about-approach__phase fade-up fade-up-d1" style="color:inherit;text-decoration:none;">
          <div class="ra-about-approach__phase-num">01</div><div><h4>Branding</h4><p>Position, identity, websites, products, and visual content built to make the business clear and memorable.</p></div>
        </a>
        <a href="/services/marketing" class="ra-about-approach__phase fade-up fade-up-d2" style="color:inherit;text-decoration:none;">
          <div class="ra-about-approach__phase-num">02</div><div><h4>Marketing</h4><p>Visibility, authority, social, and lifecycle work that earns attention around a coherent brand.</p></div>
        </a>
        <a href="/services/sales" class="ra-about-approach__phase fade-up fade-up-d3" style="color:inherit;text-decoration:none;">
          <div class="ra-about-approach__phase-num">03</div><div><h4>Sales</h4><p>Lead generation, CRM, nurture, and conversion infrastructure that moves attention toward revenue.</p></div>
        </a>
      </div>
    </div>
  </div>
</section>"""
    text, _ = old_phases.subn(new_phases, text, count=1)
    text = text.replace('See the full system on the <a href="/index#growth-machine"', 'See the full system on the <a href="/#growth-machine"')
    return text


def apply_services_copy(text: str) -> str:
    text = text.replace('You choose the entry point. We build the system.', 'We diagnose the entry point, scope the connected work, and build the system.')
    text = text.replace('Each stack is a focused discipline. Engage one. Stack them all. Either way, we build with systems thinking from day one.', 'Each discipline has a clear role. We scope the ones your diagnosed constraint requires and design every handoff to strengthen the next.')
    text = text.replace('When systems, creative, and marketing run together, compounding results become possible. This is how we build growth machines.', 'When Branding, Marketing, and Sales run together, each layer makes the next stronger. This is how we build connected growth systems.')
    text = text.replace('Real engagements where systems, creative, and marketing run as one system.', 'Real engagements where Branding, Marketing, and Sales move as one connected system.')
    text = text.replace(
        'Systems &middot; Creative &middot; Marketing &middot; SEO &middot; Social',
        'Branding &middot; Marketing &middot; Sales &middot; AI-enabled',
    )
    text = text.replace('paid social program paid social', 'measured paid social program')
    featured_replacements = {
        'data-cat="strategy-brand-strategy"': 'data-cat="branding"',
        'data-cat="strategy-creative-marketing"': 'data-cat="branding-marketing-sales"',
        'data-cat="creative-marketing"': 'data-cat="branding-marketing-sales"',
        'data-cat="creative-marketing-strategy"': 'data-cat="branding-marketing-sales"',
        'Brand Systems &middot; Website &middot; Bilingual Video':
            'Branding &middot; Website &middot; Bilingual Video',
        'Website &middot; Video &middot; Paid Ads &middot; GHL':
            'Website &middot; Video &middot; Conversion Advertising &middot; CRM',
        'Brand &middot; Video &middot; Paid Ads &middot; Social &middot; GHL':
            'Branding &middot; Video &middot; Conversion Advertising &middot; Social &middot; CRM',
    }
    for old, new in featured_replacements.items():
        text = text.replace(old, new)
    return text


def apply_booking_copy(text: str) -> str:
    text = text.replace('<title>Book a Strategy Session — Revelation Agency</title>', '<title>Start a Growth Conversation — Revelation Agency</title>')
    text = text.replace('Book your free 30-minute strategy session. Real strategy. No pitch. Walk away with a plan whether or not we work together.', 'Start a direct conversation about the constraint holding growth back and whether Revelation is the right operating partner.')
    text = text.replace('<meta property="og:title" content="Book a Strategy Session — Revelation Agency">', '<meta property="og:title" content="Start a Growth Conversation — Revelation Agency">')
    text = text.replace('Book Your <em>Free Strategy Session.</em>', 'Start a <em>Growth Conversation.</em>')
    text = text.replace('Thirty minutes. Real strategy. No pitch deck. You walk away with a plan whether or not we end up working together.', 'Bring the real constraint. We’ll read the connected system, name the highest-leverage next move, and be direct about fit.')
    text = text.replace('No pitch deck. <em>Just the plan.</em>', 'No theater. <em>A direct read.</em>')
    text = text.replace('Thirty minutes is enough to diagnose what\'s stalling growth and outline what to do next — whether it ends with us or not.', 'The goal is clarity: understand what is stalling growth, what should move next, and whether Revelation should operate it.')
    text = text.replace('<h4>A 90-Day Plan</h4>', '<h4>A Clear Next Move</h4>')
    text = text.replace('The next three moves — what to launch, what to fix, what to stop. You get a documented direction, not a vibes conversation.', 'A concrete view of what to launch, what to fix, and what to stop — grounded in the constraint, not a prebuilt package.')
    text = text.replace('Prefer email first? <a href="/contact" style="color:#fff;text-decoration:underline;">Send a brief</a> · <em>30-minute response during business hours.</em>', 'Prefer email first? <a href="/contact" style="color:#fff;text-decoration:underline;">Send a brief</a> and we’ll take it from there.')
    return text


def apply_faq_copy(text: str) -> str:
    replacements = {
        'Most client relationships run <strong>six to twelve months</strong>. The first 90 days install the growth machine — systems, creative foundation, and marketing infrastructure. After that, the engagement compounds: we run, measure, refine, and expand. Short one-off projects (a brand identity, a single landing page) are possible, but the real leverage shows up over quarters.': 'Engagements are scoped around the diagnosed constraint and the connected disciplines required to solve it. Before work begins, you get a clear sequence, ownership model, investment, and definition of done — not an arbitrary term or bundle.',
        'Engagements are scoped monthly — not hourly. A typical growth machine retainer ranges from <strong>$8K to $30K/month</strong> depending on channel mix, creative volume, and paid media footprint. Project-based work (a brand identity sprint, a site build) is quoted as a flat fee against a defined deliverable.': 'We scope the system your business actually needs. After diagnosis, you receive a clear scope, sequence, investment, and decision gates. We do not sell fixed packages or hours disconnected from an outcome.',
        'Most agencies sell a service. We build a <strong>system</strong>. Systems, creative, and marketing are engineered as one machine — so the copy matches the ads, the ads match the site, the site matches the sales process, and every dollar compounds instead of leaking.': 'Most agencies sell a service. We connect a <strong>system</strong>. Branding, Marketing, and Sales are operated together so the position matches the content, the content matches the conversion surface, and the sales process can act on the demand.',
        'We can — that\'s what the <a href="/services/marketing">Outsourced Marketing</a> track is for. A fractional CMO plus the full delivery bench (strategy, design, media buying, content, analytics) for roughly the cost of a single senior hire.': 'We can work alongside an internal team or own the connected disciplines they cannot cover. Responsibilities are diagnosed and scoped explicitly so there is one accountable operating model, not overlapping vendors.',
        'More often we <strong>augment</strong> in-house teams — running systems and creative while their team handles product marketing or internal comms. Either works. We scope to the gap.': 'Often we <strong>augment</strong> a capable in-house team. We keep what already works, connect what is missing, and scope responsibilities to the real gap.',
        'Paid media can move the pipeline inside <strong>30 days</strong>. Organic channels (SEO, AEO, content, social) compound on a 90–180 day curve. Brand and positioning shifts show up in close rates and deal size — typically visible by month three.': 'Timing depends on the constraint, baseline, buying cycle, and channel. We establish the leading and lagging indicators up front, instrument the handoffs, and report what the evidence supports rather than promising a universal clock.',
        'You get a live dashboard covering spend, pipeline, conversion, creative performance, and revenue attribution — not a monthly PDF nobody reads. We run a <strong>weekly 30-minute operating rhythm</strong> call to review numbers, decide next moves, and unblock anything on your end.': 'Reporting follows the scope: the work, the handoffs, and the business signals it is meant to change. You see the relevant receipts and the decisions they drive, not a vanity-metric PDF.',
        'Quarterly, we deliver a strategic review — what\'s working, what\'s not, and what changes for the next 90 days.': 'The review cadence is defined in the scope and built around decisions: what is working, what is not, and what changes next.',
        'You get a 30-minute call with a principal — <strong>not a sales rep</strong>. We diagnose the actual growth bottleneck, sketch a 90-day plan, and tell you honestly whether we\'re the right team for it.': 'You speak with a principal — <strong>not a script-reading sales rep</strong>. We read the actual growth constraint, name the highest-leverage next move, and tell you honestly whether we are the right team.',
        'If we\'re a fit, a scoped proposal lands in your inbox within 72 hours. If we\'re not, we\'ll tell you who is. Either way, you walk away with a plan.': 'If there is a fit, the next step is a deliberate scope. If there is not, we will say so directly. Either way, the conversation should create clarity.',
        'A third of searches now end without a click. If you only optimize for SEO, you\'re invisible to that traffic. Our <a href="/services/marketing/seo-ai-visibility">Search &amp; AI Rankings</a> track runs both in parallel.': 'Search now includes both ranked links and generated answers. Our <a href="/services/marketing/seo-ai-visibility">SEO &amp; AI Visibility</a> work helps a brand become technically discoverable, useful, and citable across both surfaces.',
        'Yes. A lot of our long-term relationships start with a <strong>Growth Machine Blueprint</strong> — a 30-day strategic sprint that maps positioning, offer, funnel, and growth plan. From there, you can take it to any team, or we roll into build-and-run.': 'Yes, when a bounded first scope is the right diagnosed move. We define the deliverable and its relationship to the wider system rather than forcing a preset starter package.',
        'Brand identity sprints, site builds, and creative production runs can also stand alone.': 'A brand, site, or production scope can stand alone when it solves the actual constraint and has a clear definition of done.',
        'Yes — the <a href="/services/systems/ai-automation">AI &amp; Automation</a> track inside Strategy covers CRM automation, lead routing, follow-up sequences, internal AI agents, and workflow systems that remove manual work from sales and ops teams. It\'s a core part of the growth machine for most clients.': 'Yes. Our <a href="/services/sales/ai-automation-systems">AI Automation Systems</a> service covers governed CRM automation, lead routing, follow-up, internal workflows, and evidence capture. It sits clearly inside Sales and connects to the rest of the system when needed.',
        'That\'s common. We\'ll run the parts they can\'t — systems, creative, paid media scaling, AEO — and coexist with the parts they do well. Our job is to install what\'s missing, not to displace what\'s working.': 'That is common. We can operate the Branding, Marketing, or Sales disciplines they cannot cover and connect cleanly to the work they already do well. Our job is to fix the gap, not displace what works.',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace(
        'Yes. <a href="/services/ai-automation">AI &amp; Automation</a> is a governed capability woven through Branding, Marketing, and Sales where it improves the system — including CRM automation, routing, follow-up, internal workflows, and evidence capture. It is not a fourth public pillar.',
        'Yes. Our <a href="/services/sales/ai-automation-systems">AI Automation Systems</a> service covers governed CRM automation, lead routing, follow-up, internal workflows, and evidence capture. It sits clearly inside Sales and connects to the rest of the system when needed.',
    )
    text = text.replace(
        'Yes — the <a href="/services/sales/ai-automation-systems">AI &amp; Automation</a> track inside Strategy covers CRM automation, lead routing, follow-up sequences, internal AI agents, and workflow systems that remove manual work from sales and ops teams. It\'s a core part of the growth machine for most clients.',
        'Yes. Our <a href="/services/sales/ai-automation-systems">AI Automation Systems</a> service covers governed CRM automation, lead routing, follow-up, internal workflows, and evidence capture. It sits clearly inside Sales and connects to the rest of the system when needed.',
    )
    text = text.replace('<div class="faq-insight__tag">Systems</div>', '<div class="faq-insight__tag">Sales</div>')
    text = text.replace('<div class="faq-insight__tag">Strategy</div>', '<div class="faq-insight__tag">Branding</div>')
    return text


def apply_straight_answers_copy(text: str) -> str:
    """Keep the public FAQ article aligned with the ratified service model."""
    replacements = {
        'Most client relationships run <strong>six to twelve months</strong>. The first 90 days install the growth machine &mdash; systems, creative foundation, and marketing infrastructure. After that, the engagement compounds: we run, measure, refine, and expand. Short one-off projects (a brand identity, a single landing page) are possible, but the real leverage shows up over quarters.': 'Engagements are scoped around the diagnosed constraint and the connected disciplines required to solve it. Before work begins, you get a clear sequence, ownership model, investment, and definition of done &mdash; not an arbitrary term or bundle.',
        'Engagements are scoped monthly &mdash; not hourly. A typical growth machine retainer ranges from <strong>$8K to $30K/month</strong> depending on channel mix, creative volume, and paid media footprint. Project-based work (a brand identity sprint, a site build) is quoted as a flat fee against a defined deliverable.': 'We scope the system your business actually needs. After diagnosis, you receive a clear scope, sequence, investment, and decision gates. We do not sell fixed packages or hours disconnected from an outcome.',
        'Most agencies sell a service. We build a <strong>system</strong>. Systems, creative, and marketing are engineered as one machine &mdash; so the copy matches the ads, the ads match the site, the site matches the sales process, and every dollar compounds instead of leaking.': 'Most agencies sell a service. We connect a <strong>system</strong>. Branding, Marketing, and Sales are operated together so the position matches the content, the content matches the conversion surface, and the sales process can act on the demand.',
        '"Most agencies sell a service. We <em>build a system</em> &mdash; one connected machine where every dollar compounds instead of leaking."': '"Branding, Marketing, and Sales work better as <em>one connected system</em> &mdash; with evidence at every handoff."',
        'We\'re industry-agnostic by design, but the pattern is consistent: <strong>businesses doing $1M&ndash;$50M in revenue</strong> that have stalled, plateaued, or never built their growth infrastructure properly. Professional services, B2B SaaS, home services, health &amp; wellness, and DTC brands make up most of the roster.': 'Fit is less about an industry label than the operating problem. We work best with established businesses that have real demand, a real offer, and a meaningful constraint across brand, marketing, or sales.',
        'Regulated industries (finance, healthcare, legal) are welcome &mdash; we\'ve built compliant funnels before.': 'When an industry carries regulatory requirements, those constraints become part of the scope and approval process from the beginning.',
        'We can &mdash; that\'s what the <a href="/services/marketing">Outsourced Marketing</a> track is for. A fractional CMO plus the full delivery bench (strategy, design, media buying, content, analytics) for roughly the cost of a single senior hire.': 'We can work alongside an internal team or own the connected disciplines they cannot cover. Responsibilities are diagnosed and scoped explicitly so there is one accountable operating model, not overlapping vendors.',
        'More often we <strong>augment</strong> in-house teams &mdash; running strategy and creative while their team handles product marketing or internal comms. Either works. We scope to the gap.': 'Often we <strong>augment</strong> a capable in-house team. We keep what already works, connect what is missing, and scope responsibilities to the real gap.',
        'Paid media can move the pipeline inside <strong>30 days</strong>. Organic channels (SEO, AEO, content, social) compound on a 90&ndash;180 day curve. Brand and positioning shifts show up in close rates and deal size &mdash; typically visible by month three.': 'Timing depends on the constraint, baseline, buying cycle, and channel. We establish the leading and lagging indicators up front, instrument the handoffs, and report what the evidence supports rather than promising a universal clock.',
        'You get a live dashboard covering spend, pipeline, conversion, creative performance, and revenue attribution &mdash; not a monthly PDF nobody reads. We run a <strong>weekly 30-minute operating rhythm</strong> call to review numbers, decide next moves, and unblock anything on your end.': 'Reporting follows the scope: the work, the handoffs, and the business signals it is meant to change. You see the relevant receipts and the decisions they drive, not a vanity-metric PDF.',
        'Quarterly, we deliver a strategic review &mdash; what\'s working, what\'s not, and what changes for the next 90 days.': 'The review cadence is defined in the scope and built around decisions: what is working, what is not, and what changes next.',
        'You get a 30-minute call with a principal &mdash; <strong>not a sales rep</strong>. We diagnose the actual growth bottleneck, sketch a 90-day plan, and tell you honestly whether we\'re the right team for it.': 'You speak with a principal &mdash; <strong>not a script-reading sales rep</strong>. We read the actual growth constraint, name the highest-leverage next move, and tell you honestly whether we are the right team.',
        'If we\'re a fit, a scoped proposal lands in your inbox within 72 hours. If we\'re not, we\'ll tell you who is. Either way, you walk away with a plan.': 'If there is a fit, the next step is a deliberate scope. If there is not, we will say so directly. Either way, the conversation should create clarity.',
        '<p><strong>You do.</strong> Every asset we produce &mdash; brand files, copy, creative, site code, ad accounts, CRM builds &mdash; is yours. We work inside your ad accounts, your GHL instance, your hosting. Nothing is hostage to the relationship.</p>': '<p>Ownership and licensing are defined plainly in the scope. Wherever practical, we build inside client-owned accounts and make the handoff requirements explicit before work begins.</p>',
        'If the engagement ends, you walk away with a functioning system, full documentation, and clean handoff to whoever comes next.': 'If the engagement ends, the agreed deliverables, access, and documentation move through a defined handoff rather than becoming leverage against the client.',
        'A third of searches now end without a click. If you only optimize for SEO, you\'re invisible to that traffic. Our <a href="/services/marketing/seo-ai-visibility">Search &amp; AI Rankings</a> track runs both in parallel.': 'Search now includes both ranked links and generated answers. Our <a href="/services/marketing/seo-ai-visibility">SEO &amp; AI Visibility</a> work helps a brand become technically discoverable, useful, and citable across both surfaces.',
        'Yes. A lot of our long-term relationships start with a <strong>Growth Machine Blueprint</strong> &mdash; a 30-day strategic sprint that maps positioning, offer, funnel, and growth plan. From there, you can take it to any team, or we roll into build-and-run.': 'Yes, when a bounded first scope is the right diagnosed move. We define the deliverable and its relationship to the wider system rather than forcing a preset starter package.',
        'Brand identity sprints, site builds, and creative production runs can also stand alone.': 'A brand, site, or production scope can stand alone when it solves the actual constraint and has a clear definition of done.',
        'Yes &mdash; the <a href="/services/ai-automation">AI &amp; Automation</a> track inside Strategy covers CRM automation, lead routing, follow-up sequences, internal AI agents, and workflow systems that remove manual work from sales and ops teams. It\'s a core part of the growth machine for most clients.': 'Yes. Our <a href="/services/sales/ai-automation-systems">AI Automation Systems</a> service covers governed CRM automation, lead routing, follow-up, internal workflows, and evidence capture. It sits clearly inside Sales and connects to the rest of the system when needed.',
        'That\'s common. We\'ll run the parts they can\'t &mdash; systems, creative, paid media scaling, AEO &mdash; and coexist with the parts they do well. Our job is to install what\'s missing, not to displace what\'s working.': 'That is common. We can operate the Branding, Marketing, or Sales disciplines they cannot cover and connect cleanly to the work they already do well. Our job is to fix the gap, not displace what works.',
        'Thirty minutes with a principal. No pitch. Walk away with a plan.': 'Bring the real constraint. Get a direct read on the connected system and whether Revelation is the right operator.',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace(
        'Yes. <a href="/services/ai-automation">AI &amp; Automation</a> is a governed capability woven through Branding, Marketing, and Sales where it improves the system &mdash; including CRM automation, routing, follow-up, internal workflows, and evidence capture. It is not a fourth public pillar.',
        'Yes. Our <a href="/services/sales/ai-automation-systems">AI Automation Systems</a> service covers governed CRM automation, lead routing, follow-up, internal workflows, and evidence capture. It sits clearly inside Sales and connects to the rest of the system when needed.',
    )
    text = text.replace(
        'Yes. <a href="/services/sales/ai-automation-systems">AI &amp; Automation</a> is a governed capability woven through Branding, Marketing, and Sales where it improves the system &mdash; including CRM automation, routing, follow-up, internal workflows, and evidence capture. It is not a fourth public pillar.',
        'Yes. Our <a href="/services/sales/ai-automation-systems">AI Automation Systems</a> service covers governed CRM automation, lead routing, follow-up, internal workflows, and evidence capture. It sits clearly inside Sales and connects to the rest of the system when needed.',
    )
    return text


GLOBAL_REPLACEMENTS = {
    'href="/services/.../..."': 'href="/services"',
    'https://revelationagency.com/assets/brand/current/ra-social-card.png': 'https://www.revelationagency.com/assets/brand/current/ra-social-card.png',
    'SEO &amp; AI Visibility': 'SEO / AI Answers',
    'Websites &amp; Landing Pages': 'Websites',
    'Back to Website Development': 'Back to Websites',
    'Book a Free Strategy Session': 'Start a Growth Conversation',
    'Book Your Free Strategy Session': 'Start a Growth Conversation',
    'Book a Strategy Session': 'Start a Growth Conversation',
    'Book a strategy session': 'Start a growth conversation',
    'Book a Discovery Call': 'Start a Growth Conversation',
    'book a free strategy session': 'start a growth conversation',
    'book a strategy session': 'start a growth conversation',
    'Book a free strategy session': 'Start a growth conversation',
    'Book a free 30-minute strategy session. It\'s not a sales call — it\'s a real conversation about where your growth is stuck, what\'s causing it, and whether we\'re the right team to fix it. You\'ll leave with clarity regardless of whether we work together.': 'Bring the real constraint. We\'ll read the connected system, name the highest-leverage next move, and be direct about whether Revelation is the right operator.',
    'Free 30-minute session': 'Start here',
    'Thirty minutes. Real strategy. No pitch. Walk away with clarity on what&rsquo;s broken and whether we&rsquo;re the right partner.': 'Bring the real constraint. We&rsquo;ll give you a direct read on the connected system and whether Revelation is the right operator.',
    "Thirty minutes. Real strategy. No pitch. Walk away with clarity on what's broken and whether we're the right partner.": "Bring the real constraint. We'll give you a direct read on the connected system and whether Revelation is the right operator.",
    'Thirty minutes with a principal. No pitch. Walk away with a plan.': 'Bring the real constraint. Get a direct read on the connected system and whether Revelation is the right operator.',
    "Thirty minutes. Real strategy. No pitch. Walk away with clarity on what's broken, what matters, and what to do next.": "Bring the real constraint. Get a direct read on what's breaking the connected system and what should move next.",
    "Thirty minutes. Real strategy. No pitch. We'll tell you whether you need the full system or a single phase — or whether we're the wrong fit entirely.": "Bring the real constraint. We'll tell you which connected discipline should move first — or whether Revelation is the wrong fit entirely.",
    "Thirty minutes on the phone answers more than any FAQ ever will. No pitch, no deck — just the plan.": "A direct conversation answers more than a generic FAQ. Bring the constraint; we'll give you an honest read on fit and the next move.",
    "Book a discovery call. Thirty minutes — we'll tell you whether we're the right fit and what your first 90 days would look like.": "Bring the real constraint. We'll give you a direct read on the connected system and whether Revelation is the right operator.",
    'Thirty minutes. Real strategy. No pitch. Walk away with clarity on what\'s broken and whether we\'re the right partner.': 'Bring the real constraint. We\'ll give you a direct read on the connected system and whether Revelation is the right operator.',
    'Thirty minutes. Real strategy. No pitch. We respond within one business day.': 'A direct read. No pitch theater. We will respond with the clearest next step.',
    "We'll be in touch within one business day. If it's urgent, call": "We'll review the brief and follow up. If it's urgent, call",
    ' (we reply within one business day) or start a growth conversation to lock in a time.': ' or start a growth conversation to choose a time.',
    'Book a 30-minute strategy session and we\'ll get straight to the plan.': 'Start a direct growth conversation and we\'ll get straight to the constraint.',
    'Book a Session →': 'Start Here →',
    'Book Your Session': 'Start the Conversation',
    'Monday – Friday · 8am to 6pm PT<br>We respond within one business day.': 'Monday – Friday · 8am to 6pm PT<br>Send the real context and we will take it from there.',
    "If you know you're ready to talk, skip the brief and grab time directly. Thirty minutes, real strategy, no pitch deck. You walk away with a plan whether or not we work together.": "If you know you're ready to talk, skip the brief and choose a time directly. Bring the real constraint; we'll give you a candid read on fit and the next move.",
    'The next 90 days, mapped. What to do, what to stop.': 'The next move, clarified. What to do, what to stop.',
    '30-Minute Session': 'Direct Conversation',
    '30 minutes. Real strategy. No pitch.': 'A direct read on the connected system. No pitch theater.',
    'Revelation Agency is a systems-first growth partner built for operators. Systems, creative, and marketing — integrated into one machine.': 'Revelation Agency is the operator-led growth partner connecting Branding, Marketing, and Sales around the constraint that matters most.',
    'Revelation Agency is a full-service strategic growth firm building integrated growth machines — systems, creative, and marketing.': 'Revelation Agency is an operator-led growth firm connecting Branding, Marketing, and Sales as one accountable system.',
    'Systems, creative, and marketing — engineered together as one machine. See every service we offer and how they connect.': 'Branding, Marketing, and Sales — operated as one connected system. See the disciplines and how they reinforce one another.',
    'Systems, creative, and marketing &mdash; engineered together as one machine. See every service we offer and how they connect.': 'Branding, Marketing, and Sales &mdash; operated as one connected system. See the disciplines and how they reinforce one another.',
    'Dream. Build. Scale.': 'Branding. Marketing. Sales.',
    'Your strategic growth partner. We build the machine behind growth — so you can stop selling chaos and start scaling clarity.': 'We run Branding, Marketing, and Sales as one connected growth system — and make the receipts visible.',
    'Your strategic growth partner. We build the machine behind growth &mdash; so you can stop selling chaos and start scaling clarity.': 'We run Branding, Marketing, and Sales as one connected growth system &mdash; and make the receipts visible.',
    'Ready to build the machine behind growth?': 'Ready to connect your growth system?',
    "Start a growth conversation. We'll audit what you have, name what's missing, and prescribe the smallest next step.": "Bring the constraint. We'll read the connected system, name the highest-leverage next move, and be direct about fit.",
}

PALETTE_REPLACEMENTS = {
    "#D72532": "#C91C1D",
    "#d72532": "#c91c1d",
    "#ED1C24": "#ED2A31",
    "#ed1c24": "#ed2a31",
    "#AD1C24": "#9E1115",
    "#ad1c24": "#9e1115",
    "#840D11": "#780A0E",
    "#840d11": "#780a0e",
    "215,37,50": "201,28,29",
    "237,28,36": "237,42,49",
}


def normalize_sales_systems_public_copy(text: str) -> str:
    """Use Sales Systems as the public pillar without changing stable tokens.

    Internal routes, data attributes, and manifest membership intentionally
    remain ``sales`` / ``Sales``. These bounded replacements only touch known
    public category phrases and labels; ordinary uses such as sales team,
    sales pipeline, and CRMs / Sales Tools remain unchanged.
    """
    for pattern, replacement in (
        (r"Branding, Marketing &amp; Sales(?! Systems)", "Branding, Marketing &amp; Sales Systems"),
        (r"Branding, Marketing & Sales(?! Systems)", "Branding, Marketing & Sales Systems"),
        (r"Branding · Marketing · Sales(?! Systems)", "Branding · Marketing · Sales Systems"),
        (r"Branding &middot; Marketing &middot; Sales(?! Systems)", "Branding &middot; Marketing &middot; Sales Systems"),
        (r"Branding\. Marketing\. Sales\.(?! Systems)", "Branding. Marketing. Sales Systems."),
        (r"Branding / Marketing / Sales(?! Systems)", "Branding / Marketing / Sales Systems"),
        (r"Case Study · Marketing · Sales(?! Systems)", "Case Study · Marketing · Sales Systems"),
        (r"Case Study · Branding · Marketing · Sales(?! Systems)", "Case Study · Branding · Marketing · Sales Systems"),
    ):
        text = re.sub(pattern, replacement, text)

    text = re.sub(
        r'(<a\b[^>]*href=["\']/services/sales["\'][^>]*>)Sales(?=\s*<)',
        r'\1Sales Systems',
        text,
        flags=re.I,
    )
    text = re.sub(
        r'(<a\b[^>]*href=["\']/portfolio/sales["\'][^>]*>)Sales Work(?=\s*<)',
        r'\1Sales Systems Work',
        text,
        flags=re.I,
    )
    text = re.sub(
        r'(<a\b[^>]*href=["\']/services/sales["\'][^>]*>)Explore Sales(?=\s*<)',
        r'\1Explore Sales Systems',
        text,
        flags=re.I,
    )
    text = re.sub(
        r'(<a\b[^>]*href=["\'][^"\']*net-metering-systems-strategy["\'][^>]*>)Sales(?=</a>)',
        r'\1Sales Systems',
        text,
        flags=re.I,
    )
    for old, new in (
        ('aria-label="Toggle Sales menu"', 'aria-label="Toggle Sales Systems menu"'),
        ('<h4>Sales</h4>', '<h4>Sales Systems</h4>'),
        ('<div class="faq-insight__tag">Sales</div>', '<div class="faq-insight__tag">Sales Systems</div>'),
        ('<div class="cs-cross__lbl">Sales</div>', '<div class="cs-cross__lbl">Sales Systems</div>'),
        ('<span class="highlight">Sales</span>', '<span class="highlight">Sales Systems</span>'),
        ('Revenue — Sales</h3>', 'Revenue — Sales Systems</h3>'),
        ('AI Automation Systems as a defined Sales service', 'AI Automation Systems as a defined Sales Systems service'),
        ('AI Automation Systems are scoped inside Sales when', 'AI Automation Systems are scoped inside Sales Systems when'),
        ('It sits clearly inside Sales and', 'It sits clearly inside Sales Systems and'),
        ('data-chip-filter="sales">Sales</button>', 'data-chip-filter="sales">Sales Systems</button>'),
        ('data-filter="sales">Sales</button>', 'data-filter="sales">Sales Systems</button>'),
    ):
        text = text.replace(old, new)
    text = re.sub(
        r'(<div class="ra-hero__trust-item">.*?>\s*)Sales(\s*</div>)',
        r'\1Sales Systems\2',
        text,
        flags=re.I,
    )
    return text


def migrate_html(path: Path) -> tuple[bool, bool]:
    original = read(path)
    text = original
    rel = path.relative_to(ROOT).as_posix()
    text = normalize_generated_visual(text, rel)
    text = normalize_generated_visual_sources(text, rel)

    # Explicit logo roles: compact mark in navigation, supplied lockup in footer.
    text = re.sub(
        r'(?:(?:\.\./)*/?|/)assets/brand/approved/ra-landscape-black-updated\.png',
        '/assets/brand/current/ra-mark-red.png',
        text,
    )
    text = re.sub(
        r'(?:(?:\.\./)*/?|/)assets/revelation-logo\.png',
        '/assets/brand/current/ra-lockup-red.png',
        text,
    )
    text = normalize_nav(text, rel)
    text = remove_retired_mobile_nav_overrides(text)
    text = normalize_brand_image_dimensions(text)

    text, footer_changed = replace_footer_services(text)
    for old, new in GLOBAL_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in PALETTE_REPLACEMENTS.items():
        text = text.replace(old, new)

    # Retired portfolio landing pages used a variable discipline name inside
    # the same discovery-call promise. Keep them safe if a static host ever
    # serves the document before the canonical redirect executes.
    text = re.sub(
        r"Book a discovery call\. Thirty minutes — we'll tell you whether we're the right fit and whether .*? is the lever worth pulling first\.",
        "Bring the real constraint. We'll give you a direct read on the connected system and whether Revelation is the right operator.",
        text,
    )

    # Keep the mobile action compact without reverting to the retired
    # appointment/package language used by the former brand architecture.
    text = re.sub(
        r'(<a\b[^>]*class=["\'][^"\']*ra-nav__cta-mobile[^"\']*["\'][^>]*>)(?:Book a Call|Start Here)(</a>)',
        r'\1Start Here\2',
        text,
        flags=re.I,
    )

    if rel == "index.html":
        text = apply_home_copy(text)
    elif rel == "about.html":
        text = apply_about_copy(text)
    elif rel == "services.html":
        text = apply_services_copy(text)
    elif rel == "booking.html":
        text = apply_booking_copy(text)
    elif rel == "faq.html":
        text = apply_faq_copy(text)
    elif rel == "the-reveal/straight-answers.html":
        text = apply_straight_answers_copy(text)

    text = normalize_reveal_taxonomy(text, rel)
    if rel == "the-reveal/revelation-agency-is-now-live.html":
        text = text.replace(
            "We're starting with the ten categories of work that matter most to the businesses we serve: brand systems, paid media, video, AI-native content and SEO, automation, web design, social, outsourced marketing, and the creative systems that tie all of it together. We're going deep on each, with real research, real opinions, and real utility.",
            "We're organizing the work around three clear categories businesses must connect: Branding, Marketing, and Sales. That includes AI Automation Systems as a defined Sales service. We're going deep on each with research, direct opinions, and useful operating detail.",
        )
    if rel == "web-hosting.html":
        text = text.replace(
            '<a href="/services/branding">Creative</a><span>/</span><a href="/services/branding/websites-landing-pages">Website Development</a>',
            '<a href="/services/branding">Branding</a><span>/</span><a href="/services/branding/websites-landing-pages">Websites &amp; Landing Pages</a>',
        )

    # Case-study links that visibly pointed at the retired Creative shelf.
    if rel.startswith("portfolio/case-studies/"):
        text = text.replace('href="../creative.html"', 'href="/portfolio/branding"')
        text = text.replace('>Creative Work<', '>Branding Work<')
        text = text.replace('All Creative Work', 'All Branding Work')

    text = normalize_sales_systems_public_copy(text)

    text = re.sub(
        r'href=(["\'])/assets/css/ra-refresh-2026\.css(?:\?v=[^"\']*)?\1',
        lambda match: f'href={match.group(1)}{REFRESH_CSS_URL}{match.group(1)}',
        text,
    )
    text = re.sub(
        r'src=(["\'])/assets/js/ra-refresh-2026\.js(?:\?v=[^"\']*)?\1',
        lambda match: f'src={match.group(1)}{REFRESH_JS_URL}{match.group(1)}',
        text,
    )
    if CSS_MARKER not in text:
        text = text.replace(
            "</head>",
            f'{CSS_MARKER}\n<link rel="stylesheet" href="{REFRESH_CSS_URL}">\n</head>',
            1,
        )
    if JS_MARKER not in text:
        text = text.replace(
            "</body>",
            f'{JS_MARKER}\n<script src="{REFRESH_JS_URL}" defer></script>\n</body>',
            1,
        )

    text = normalize_internal_hrefs(text, rel)
    text = normalize_external_target_security(text)
    text = normalize_metadata(text, route_for_file(path))
    text = normalize_favicon_links(text)

    changed = text != original
    if changed:
        write(path, text)
    return changed, footer_changed


def migrate_sitemap() -> int:
    path = ROOT / "sitemap.xml"
    text = read(path)
    seen: set[str] = set()
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        parsed = urlsplit(match.group(1).strip())
        route = follow_redirect(clean_route(parsed.path))
        url = APEX + ("/" if route == "/" else route.split("?", 1)[0])
        if url in seen:
            raise ValueError(f"Duplicate sitemap URL after normalization: {url}")
        seen.add(url)
        count += 1
        return f"<loc>{url}</loc>"

    updated = re.sub(r"<loc>(.*?)</loc>", repl, text)
    updated = re.sub(r"<lastmod>[^<]+</lastmod>", "<lastmod>2026-08-17</lastmod>", updated)
    if updated != text:
        write(path, updated)
    return count


def migrate_runtime_palette() -> int:
    changed = 0
    runtime_files = sorted((ROOT / "assets" / "css").glob("*.css")) + sorted((ROOT / "assets" / "js").glob("*.js"))
    for path in runtime_files:
        original = read(path)
        text = original
        for old, new in PALETTE_REPLACEMENTS.items():
            text = text.replace(old, new)
        if text != original:
            write(path, text)
            changed += 1
    return changed


def main() -> None:
    changed = 0
    footer_changed = 0
    changed_paths: list[str] = []
    for path in HTML_FILES:
        did_change, did_footer = migrate_html(path)
        changed += int(did_change)
        footer_changed += int(did_footer)
        if did_change:
            changed_paths.append(path.relative_to(ROOT).as_posix())

    sitemap_count = migrate_sitemap()
    palette_count = migrate_runtime_palette()
    robots = ROOT / "robots.txt"
    if robots.exists():
        text = read(robots)
        text = text.replace("https://www.revelationagency.com/sitemap.xml", APEX + "/sitemap.xml")
        text = text.replace("https://revelationagency.com/sitemap.xml", APEX + "/sitemap.xml")
        text = text.replace("Disallow: /asset-review.html", "Disallow: /asset-review")
        text = text.replace(
            "Disallow: /the-reveal/article-template.html",
            "Disallow: /the-reveal/article-template",
        )
        write(robots, text)

    print(f"HTML inventory: {len(HTML_FILES)}")
    print(f"HTML changed: {changed}")
    if changed_paths:
        print("Changed paths: " + ", ".join(changed_paths))
    print(f"Footers normalized: {footer_changed}")
    print(f"Sitemap URLs normalized: {sitemap_count}")
    print(f"Runtime palette files normalized: {palette_count}")


if __name__ == "__main__":
    main()
