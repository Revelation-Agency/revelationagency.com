#!/usr/bin/env python3
"""Apply the ratified portfolio taxonomy to all case studies and shelves.

Source of truth: assets/data/portfolio-taxonomy-2026.json. This migration is
idempotent and local-only. It adds machine-readable page metadata, visible
discipline chips, accurate multi-pillar card filtering, and populated pillar
shelves without inventing new project claims.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "data" / "portfolio-taxonomy-2026.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
TAXONOMY: dict[str, str] = MANIFEST["taxonomy"]
CASE_STUDIES: dict[str, dict] = MANIFEST["caseStudiesByRoute"]
MASTER_CARDS: dict[str, dict] = MANIFEST["masterCardsByRoute"]


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


PILLAR_COPY = {
    "Branding": {
        "eyebrow": "Branding Proof",
        "title": "The brand, built to live.",
        "description": "Websites, Apps, Brand Identity, Design, and Video — the surfaces where the market meets the business.",
    },
    "Marketing": {
        "eyebrow": "Marketing Proof",
        "title": "Demand, earned with clarity.",
        "description": "SEO / AI Answers, Social Media, Digital Advertising, and Customer Nurture connected to a measurable next step.",
    },
    "Sales": {
        "eyebrow": "Sales Systems Proof",
        "title": "Attention, moved toward revenue.",
        "description": "Outreach, Lead Gen Ads, CRMs / Sales Tools, and AI Automation Systems — built so demand has somewhere disciplined to go.",
    },
}


PILLAR_PUBLIC_LABEL = {
    "Branding": "Branding",
    "Marketing": "Marketing",
    "Sales": "Sales Systems",
}


def public_pillar(pillar: str) -> str:
    return PILLAR_PUBLIC_LABEL[pillar]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def clean_case_route(href: str) -> str:
    route = href.split("?", 1)[0].split("#", 1)[0]
    if route.startswith("https://revelationagency.com"):
        route = route.removeprefix("https://revelationagency.com")
    if route.startswith("https://www.revelationagency.com"):
        route = route.removeprefix("https://www.revelationagency.com")
    if not route.startswith("/"):
        route = "/" + route.lstrip("./")
    if not route.endswith(".html"):
        route += ".html"
    return route


def with_body_metadata(text: str, record: dict) -> str:
    match = re.search(r"<body\b([^>]*)>", text, re.I)
    if not match:
        raise ValueError("Missing <body>")
    attrs = re.sub(r'\sdata-ra-(?:page-kind|project|pillars|disciplines|ai)=["\'][^"\']*["\']', "", match.group(1), flags=re.I)
    metadata = (
        f' data-ra-page-kind="{html.escape(record["pageKind"], quote=True)}"'
        f' data-ra-project="{html.escape(record["project"], quote=True)}"'
        f' data-ra-pillars="{" ".join(p.lower() for p in record["pillars"])}"'
        f' data-ra-disciplines="{" ".join(record["disciplines"])}"'
        f' data-ra-ai="{str(bool(record["aiAutomation"])).lower()}"'
    )
    replacement = "<body" + attrs + metadata + ">"
    return text[:match.start()] + replacement + text[match.end():]


def taxonomy_chips(record: dict) -> str:
    links = []
    for code in record["disciplines"]:
        links.append(
            f'<a href="{DISCIPLINE_LINKS[code]}" class="ra-case-taxonomy__chip" '
            f'title="{html.escape(code + " · " + TAXONOMY[code], quote=True)}">'
            f'<span>{code}</span>{html.escape(TAXONOMY[code])}</a>'
        )
    return (
        '<!-- RA-PORTFOLIO-TAXONOMY:visible -->\n'
        '<div class="ra-case-taxonomy" aria-label="Mapped service disciplines">'
        + "".join(links)
        + "</div>"
    )


def add_visible_taxonomy(text: str, record: dict) -> str:
    text = re.sub(
        r'\s*<!-- RA-PORTFOLIO-TAXONOMY:visible -->\s*<div class="ra-case-taxonomy".*?</div>',
        "",
        text,
        count=1,
        flags=re.S,
    )
    hero_start = text.find('<section class="cs-hero">')
    meta_match = re.search(r'<(?:div|p) class="cs-hero__meta">', text[hero_start:]) if hero_start >= 0 else None
    meta_start = hero_start + meta_match.start() if meta_match else -1
    if hero_start < 0 or meta_start < 0:
        raise ValueError("Missing case-study hero/meta")

    prefix = text[hero_start:meta_start]
    pillar_label = " · ".join(public_pillar(pillar) for pillar in record["pillars"])
    prefix, count = re.subn(
        r'<span class="eyebrow">.*?</span>',
        f'<span class="eyebrow">Case Study · {html.escape(pillar_label)}</span>',
        prefix,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise ValueError("Missing case-study eyebrow")
    text = text[:hero_start] + prefix + text[meta_start:]
    meta_match = re.search(r'<(?:div|p) class="cs-hero__meta">', text[hero_start:])
    meta_start = hero_start + meta_match.start() if meta_match else -1
    if meta_start < 0:
        raise ValueError("Missing case-study meta after eyebrow rewrite")
    return text[:meta_start] + taxonomy_chips(record) + "\n      " + text[meta_start:]


def add_case_jsonld(text: str, record: dict, route: str) -> str:
    text = re.sub(
        r'\s*<!-- RA-PORTFOLIO-TAXONOMY:jsonld -->\s*<script type="application/ld\+json">.*?</script>',
        "",
        text,
        count=1,
        flags=re.S,
    )
    clean = route.removesuffix(".html")
    payload = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": record["project"] + " — Revelation Agency Case Study",
        "url": "https://www.revelationagency.com" + clean,
        "creator": {"@type": "Organization", "name": "Revelation Agency"},
        "about": [TAXONOMY[code] for code in record["disciplines"]],
        "keywords": [public_pillar(pillar) for pillar in record["pillars"]]
        + (["AI-enabled"] if record["aiAutomation"] else []),
    }
    block = (
        '<!-- RA-PORTFOLIO-TAXONOMY:jsonld -->\n'
        '<script type="application/ld+json">'
        + json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
        + "</script>\n"
    )
    theme_anchor = '<meta name="theme-color" content="#C91C1D">'
    if theme_anchor in text:
        return text.replace(theme_anchor, block + theme_anchor, 1)
    favicon_anchor = "<!-- RA-REFRESH-2026:favicons -->"
    if favicon_anchor in text:
        return text.replace(favicon_anchor, block + favicon_anchor, 1)
    return text.replace("</head>", block + "</head>", 1)


def migrate_case_studies() -> int:
    changed = 0
    for route, record in CASE_STUDIES.items():
        path = ROOT / route.lstrip("/")
        if not path.exists():
            raise FileNotFoundError(path)
        original = read(path)
        text = with_body_metadata(original, record)
        text = add_visible_taxonomy(text, record)

        # Global navigation/footer vocabulary is owned by the site-refresh
        # generator. Protect those shared blocks while normalizing case copy.
        protected_chrome: list[str] = []

        def protect_chrome(match: re.Match[str]) -> str:
            protected_chrome.append(match.group(0))
            return f"<!-- RA-PORTFOLIO-PROTECTED-CHROME:{len(protected_chrome) - 1} -->"

        text = re.sub(
            r'<(?:nav|footer)\b.*?</(?:nav|footer)>',
            protect_chrome,
            text,
            flags=re.I | re.S,
        )

        # Normalize only service-label vocabulary; project claims stay intact.
        # The replacements are deliberately one-way so a second run is byte-stable.
        for old, new in (
            ("Brand Strategy &amp; Identity", "Brand Identity"),
            ("Websites &amp; Landing Pages", "Websites"),
            ("Website Development", "Websites"),
            ("Apps &amp; Digital Products", "Apps"),
            ("App Development", "Apps"),
            ("Video &amp; Visual Content", "Video"),
            ("Video Production", "Video"),
            ("SEO &amp; AI Visibility", "SEO / AI Answers"),
            ("Search &amp; AI Rankings", "SEO / AI Answers"),
            ("Search Rankings", "SEO / AI Answers"),
            ("Positioning, Content &amp; Authority", "SEO / AI Answers"),
            ("Email &amp; Lifecycle Marketing", "Customer Nurture"),
            ("Lead Generation &amp; Personalized Outreach", "Lead Gen Ads"),
            ("Follow-up &amp; Nurture", "Customer Nurture"),
            ("Conversion Advertising", "Digital Advertising"),
            ("AI &amp; Automation", "AI Automation Systems"),
            ("AI & Automation", "AI Automation Systems"),
        ):
            text = text.replace(old, new)
        text = re.sub(
            r'(?:(?:CRM (?:&amp;|&) )*)Sales Infrastructure',
            'CRMs / Sales Tools',
            text,
        )
        text = re.sub(r"AI Automation(?! Systems)", "AI Automation Systems", text)
        text = text.replace("More Creative Engagements", "More Branding Engagements")
        text = text.replace(
            "Browse all creative case studies across the Revelation portfolio.",
            "Browse Branding case studies across the Revelation portfolio.",
        )
        text = text.replace("View creative work", "View Branding work")
        text = text.replace('<div class="cs-cross__lbl">Creative</div>', '<div class="cs-cross__lbl">Branding</div>')
        text = text.replace("Outsourced Marketing Ops", "Lifecycle Marketing Ops")
        text = text.replace("Book Your Free Session", "Start a Growth Conversation")
        text = text.replace(">Paid Ads</a>", ">Digital Advertising</a>")
        text = text.replace(
            '<div class="cs-cross__title">Paid Ads</div>',
            '<div class="cs-cross__title">Digital Advertising</div>',
        )
        text = text.replace(
            '<span class="eyebrow">05 &mdash; The Paid Ads</span>',
            '<span class="eyebrow">05 &mdash; Digital Advertising</span>',
        )
        text = text.replace(
            '<span class="highlight">Paid Ads</span>',
            '<span class="highlight">Digital Advertising</span>',
        )
        text = text.replace(
            '<span class="lbl">Creative</span><span class="val">Video-fed campaigns</span>',
            '<span class="lbl">Campaign Assets</span><span class="val">Video-fed campaigns</span>',
        )
        # Two app case studies use a text-only gallery proof note instead of
        # an image. Give that note a stable hook so long hostnames and CTAs
        # wrap cleanly on narrow screens rather than being clipped by the
        # gallery tile's overflow mask.
        text = re.sub(
            r'(<div class="cs-gallery__item cs-gallery__item--wide)(?="[^>]*>[^\n]*<code)',
            r'\1 cs-gallery__item--proof-note',
            text,
        )

        # The former NMS "Systems" tab contains CRM, customer nurture,
        # automation, and reporting. AI Automation Systems belongs to Sales Systems.
        text = re.sub(
            r'(<a\b[^>]*href=["\']/portfolio/case-studies/net-metering-systems-strategy["\'][^>]*>)(?:Systems|Sales(?: &amp; AI| Systems)?)(</a>)',
            r'\1Sales Systems\2',
            text,
            flags=re.I,
        )
        text = re.sub(
            r'(<a\b[^>]*href=["\'][^"\']*net-metering-systems-strategy["\'][^>]*>.*?<div class="cs-cross__lbl">)(?:Systems|Sales(?: &amp; AI| Systems)?)(</div>)',
            r'\1Sales Systems\2',
            text,
            flags=re.I | re.S,
        )
        text = re.sub(
            r'(<a\b[^>]*href=["\'][^"\']*net-metering-systems-seo["\'][^>]*>.*?<div class="cs-cross__lbl">)(?:Systems|Marketing)(</div>)',
            r'\1Marketing\2',
            text,
            flags=re.I | re.S,
        )

        for index, chrome in enumerate(protected_chrome):
            text = text.replace(
                f"<!-- RA-PORTFOLIO-PROTECTED-CHROME:{index} -->",
                chrome,
                1,
            )

        # Add raw JSON only after visible HTML entities are normalized so
        # discipline names remain valid JSON strings rather than "&amp;" text.
        text = add_case_jsonld(text, record, route)

        if text != original:
            write(path, text)
            changed += 1
    return changed


def enhance_card_opening(opening: str, record: dict) -> str:
    opening = re.sub(r'\sdata-(?:pillars|disciplines|ai)=["\'][^"\']*["\']', "", opening)
    pillar_tokens = " ".join(p.lower() for p in record["pillars"])
    opening = re.sub(r'\sdata-cat=["\'][^"\']*["\']', f' data-cat="{pillar_tokens}"', opening)
    insert = (
        f' data-pillars="{pillar_tokens}"'
        f' data-disciplines="{" ".join(record["disciplines"])}"'
        f' data-ai="{str(bool(record["aiAutomation"])).lower()}"'
    )
    return opening[:-1] + insert + ">"


def migrate_master_cards(text: str) -> tuple[str, int]:
    card_pattern = re.compile(r'<a\b[^>]*class="[^"]*\bpf-card\b[^"]*"[^>]*>.*?</a>', re.S | re.I)
    mapped = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal mapped
        block = match.group(0)
        opening_end = block.find(">") + 1
        opening = block[:opening_end]
        href_match = re.search(r'href=["\']([^"\']+)["\']', opening, re.I)
        if not href_match:
            return block
        route = clean_case_route(href_match.group(1))
        record = MASTER_CARDS.get(route)
        if not record:
            return block
        mapped += 1
        opening = enhance_card_opening(opening, record)
        block = opening + block[opening_end:]
        if route == "/portfolio/case-studies/revelation-portal.html":
            block = block.replace(
                "background:url('/assets/img/portfolio/revelation-portal/thumbnail.png') center/cover no-repeat;",
                "background:#1E1E1E url('/assets/brand/current/ra-mark-red.png') center/30% auto no-repeat;",
            )
        label = " · ".join(public_pillar(pillar) for pillar in record["pillars"])
        thumbnail_label = label.upper()

        def thumbnail_repl(bg_match: re.Match[str]) -> str:
            bg_opening = re.sub(
                r'\sdata-taxonomy=["\'][^"\']*["\']',
                "",
                bg_match.group(0),
            )
            return (
                bg_opening[:-1]
                + f' data-taxonomy="{html.escape(thumbnail_label, quote=True)}">'
            )

        block = re.sub(
            r'<div\b[^>]*class=["\'][^"\']*\bpf-card__bg\b[^"\']*["\'][^>]*>',
            thumbnail_repl,
            block,
            count=1,
            flags=re.I,
        )
        block = re.sub(
            r'(<span class="pf-card__label">).*?(</span>)',
            lambda m: m.group(1) + html.escape(label) + m.group(2),
            block,
            count=1,
            flags=re.S,
        )
        return block

    return card_pattern.sub(repl, text), mapped


def update_filter_script(text: str) -> str:
    replacement = """  // RA-PORTFOLIO-FILTERS:START
  function portfolioFilterMatches(card, filter) {
    var normalized = (filter || 'all').toLowerCase();
    if (normalized === 'all') return true;
    var isDiscipline = /^[bms]\\d+$/.test(normalized);
    var attribute = isDiscipline ? 'data-disciplines' : 'data-pillars';
    var values = (card.getAttribute(attribute) || '')
      .toLowerCase().split(/\\s+/).filter(Boolean);
    return values.indexOf(normalized) !== -1;
  }

  const filterBtns = document.querySelectorAll('.pf-filter-btn');
  const cards = document.querySelectorAll('.pf-card');
  const filterStatus = document.getElementById('pf-filter-status');
  const emptyState = document.getElementById('pf-empty-state');
  const emptyLabel = document.getElementById('pf-empty-label');

  function findFilterButton(filter) {
    var match = null;
    filterBtns.forEach(function(button) {
      if (!match && button.getAttribute('data-filter') === filter) match = button;
    });
    return match;
  }

  function applyPortfolioFilter(filter, updateQuery) {
    var normalized = (filter || 'all').toLowerCase();
    var shown = 0;
    filterBtns.forEach(function(button) {
      var active = button.getAttribute('data-filter') === normalized;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    cards.forEach(function(card) {
      var visible = portfolioFilterMatches(card, normalized);
      card.classList.toggle('pf-card--hidden', !visible);
      if (visible) shown += 1;
    });
    if (filterStatus) {
      filterStatus.textContent = 'Showing ' + shown + (shown === 1 ? ' project' : ' projects');
    }
    if (emptyState) {
      var activeButton = findFilterButton(normalized);
      var activeLabel = activeButton && activeButton.firstChild
        ? activeButton.firstChild.textContent.trim() : 'Selected service';
      if (emptyLabel) emptyLabel.textContent = activeLabel;
      emptyState.hidden = shown !== 0;
    }
    if (updateQuery && window.history && window.history.replaceState) {
      var url = new URL(window.location.href);
      if (normalized === 'all') url.searchParams.delete('filter');
      else url.searchParams.set('filter', normalized);
      window.history.replaceState({}, '', url.pathname + url.search + url.hash);
    }
  }

  filterBtns.forEach(function(button) {
    button.addEventListener('click', function() {
      applyPortfolioFilter(button.getAttribute('data-filter'), true);
    });
  });

  (function initPortfolioFilter() {
    var query = new URLSearchParams(location.search || '');
    var requested = (query.get('filter') || 'all').toLowerCase();
    var target = findFilterButton(requested);
    applyPortfolioFilter(target ? requested : 'all', false);
  })();
  // RA-PORTFOLIO-FILTERS:END"""
    marker_pattern = re.compile(
        r"  // RA-PORTFOLIO-FILTERS:START.*?  // RA-PORTFOLIO-FILTERS:END",
        re.S,
    )
    if marker_pattern.search(text):
        return marker_pattern.sub(lambda _match: replacement, text, count=1)

    legacy_pattern = re.compile(
        r"  // Portfolio filter.*?  \}\)\(\);",
        re.S,
    )
    text, count = legacy_pattern.subn(lambda _match: replacement, text, count=1)
    if count != 1:
        raise ValueError("Portfolio filter script not found")
    return text


def add_filter_styles(text: str) -> str:
    marker = """/* RA-PORTFOLIO-SERVICE-FILTERS:START */
.pf-filters__label{font-size:10px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:rgba(43,43,43,.54);text-align:center;margin:0 0 12px;}
.pf-service-filters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:24px auto 0;max-width:1240px;}
.pf-service-filter-group{background:rgba(255,255,255,.72);border:1px solid rgba(43,43,43,.08);border-radius:16px;padding:16px;}
.pf-service-filter-group__title{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--red);margin:0 0 10px;}
.pf-service-filter-group__buttons{display:flex;flex-wrap:wrap;gap:8px;}
.pf-filter-btn--service{font-size:12px;letter-spacing:.01em;text-transform:none;padding:9px 13px;}
.pf-filter-count{font-variant-numeric:tabular-nums;opacity:.68;margin-left:4px;}
.pf-filter-status{font-size:12px;color:rgba(43,43,43,.62);text-align:center;margin:18px 0 0;}
.pf-empty-state{max-width:720px;margin:32px auto 0;padding:clamp(24px,5vw,42px);border:1px solid rgba(201,28,29,.2);border-radius:22px;background:linear-gradient(145deg,#fff 0%,#f8f4f1 100%);text-align:center;box-shadow:0 18px 50px rgba(18,18,18,.07);}
.pf-empty-state[hidden]{display:none!important;}
.pf-empty-state__eyebrow{display:block;margin-bottom:10px;color:var(--red);font-size:10px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;}
.pf-empty-state h2{margin:0 0 10px;font-size:clamp(24px,4vw,38px);line-height:1.05;}
.pf-empty-state p{max-width:54ch;margin:0 auto 20px;color:rgba(43,43,43,.68);line-height:1.65;}
@media (max-width:900px){.pf-service-filters{grid-template-columns:1fr;max-width:620px;}}
@media (max-width:520px){.pf-service-filter-group{padding:13px}.pf-filter-btn--service{font-size:11px;padding:8px 11px}}
/* RA-PORTFOLIO-SERVICE-FILTERS:END */"""
    text = re.sub(
        r"\n?/\* RA-PORTFOLIO-SERVICE-FILTERS:START \*/.*?/\* RA-PORTFOLIO-SERVICE-FILTERS:END \*/\n?",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    anchor = ".pf-filter-btn.is-active{background:var(--red);border-color:var(--red);color:#fff;}"
    if anchor not in text:
        raise ValueError("Portfolio filter style anchor not found")
    return text.replace(anchor, anchor + "\n" + marker, 1)


def build_filter_section() -> str:
    pillar_counts = {
        pillar.lower(): sum(pillar in record["pillars"] for record in MASTER_CARDS.values())
        for pillar in PILLAR_COPY
    }
    discipline_counts = {
        code: sum(code in record["disciplines"] for record in MASTER_CARDS.values())
        for code in TAXONOMY
    }
    pillar_buttons = [
        f'<button class="pf-filter-btn is-active" data-filter="all" aria-pressed="true">All Work <span class="pf-filter-count">{len(MASTER_CARDS)}</span></button>'
    ]
    pillar_buttons.extend(
        f'<button class="pf-filter-btn" data-filter="{pillar.lower()}" aria-pressed="false">{public_pillar(pillar)} <span class="pf-filter-count">{pillar_counts[pillar.lower()]}</span></button>'
        for pillar in PILLAR_COPY
    )

    service_groups: list[str] = []
    for pillar, prefix in (("Branding", "B"), ("Marketing", "M"), ("Sales", "S")):
        buttons = "\n          ".join(
            f'<button class="pf-filter-btn pf-filter-btn--service" data-filter="{code.lower()}" data-discipline="{code}" aria-pressed="false">{html.escape(title)} <span class="pf-filter-count">{discipline_counts[code]}</span></button>'
            for code, title in TAXONOMY.items()
            if code.startswith(prefix)
        )
        service_groups.append(
            f'''<div class="pf-service-filter-group" data-service-pillar="{pillar.lower()}">
        <div class="pf-service-filter-group__title">{public_pillar(pillar)}</div>
        <div class="pf-service-filter-group__buttons">
          {buttons}
        </div>
      </div>'''
        )

    return f'''<section class="pf-filters">
  <div class="container">
    <div class="pf-filters__label">Filter by pillar</div>
    <div class="pf-filters__bar fade-up">
      {chr(10).join(pillar_buttons)}
    </div>
    <div class="pf-service-filters" aria-label="Filter portfolio by service">
      {chr(10).join(service_groups)}
    </div>
    <p class="pf-filter-status" id="pf-filter-status" aria-live="polite">Showing {len(MASTER_CARDS)} projects</p>
    <div class="pf-empty-state" id="pf-empty-state" aria-live="polite" hidden>
      <span class="pf-empty-state__eyebrow">Proof inventory</span>
      <h2><span id="pf-empty-label">Selected service</span> work is not published yet.</h2>
      <p>There is no public case study in this filter yet. The service is available; ask us for the most relevant private example.</p>
      <a class="btn btn--primary" href="/contact">Ask about this service <i class="fa-solid fa-arrow-right btn-arrow"></i></a>
    </div>
  </div>
</section>'''


def replace_filter_section(text: str) -> str:
    text, count = re.subn(
        r'<section class="pf-filters">.*?</section>',
        lambda _match: build_filter_section(),
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise ValueError("Portfolio filter section not found")
    return text


def neutralize_unverified_summary_stats(text: str) -> str:
    replacements = {
        '<div class="pf-numbers__num">100+</div>\n        <div class="pf-numbers__label">Engagements Delivered</div>': '<div class="pf-numbers__num">Selected</div>\n        <div class="pf-numbers__label">Work, not promises</div>',
        '<div class="pf-numbers__num">12+</div>\n        <div class="pf-numbers__label">Industries Served</div>': '<div class="pf-numbers__num">Cross-Industry</div>\n        <div class="pf-numbers__label">Operators served</div>',
        '<div class="pf-numbers__num">3x</div>\n        <div class="pf-numbers__label">Avg Pipeline Lift</div>': '<div class="pf-numbers__num">Measured</div>\n        <div class="pf-numbers__label">Evidence at each handoff</div>',
        '<div class="pf-numbers__num">10yr+</div>\n        <div class="pf-numbers__label">Collective Experience</div>': '<div class="pf-numbers__num">Operator-Led</div>\n        <div class="pf-numbers__label">Senior ownership</div>',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def migrate_portfolio_hub() -> tuple[int, str]:
    path = ROOT / "portfolio.html"
    original = read(path)
    text, mapped = migrate_master_cards(original)
    if mapped != 21:
        raise ValueError(f"Expected 21 mapped master cards, found {mapped}")
    text = add_filter_styles(text)
    text = replace_filter_section(text)
    text = update_filter_script(text)
    text = neutralize_unverified_summary_stats(text)
    if text != original:
        write(path, text)
    return mapped, text


def extract_mapped_cards(portfolio_text: str) -> dict[str, str]:
    cards: dict[str, str] = {}
    for match in re.finditer(r'<a\b[^>]*class="[^"]*\bpf-card\b[^"]*"[^>]*>.*?</a>', portfolio_text, re.S | re.I):
        block = match.group(0)
        href = re.search(r'href=["\']([^"\']+)["\']', block, re.I)
        if not href:
            continue
        route = clean_case_route(href.group(1))
        if route in MASTER_CARDS:
            cards[route] = block
    if len(cards) != 21:
        raise ValueError(f"Expected 21 extractable cards, found {len(cards)}")
    return cards


def build_pillar_section(pillar: str, cards: dict[str, str]) -> str:
    copy = PILLAR_COPY[pillar]
    selected = [
        cards[route]
        for route, record in MASTER_CARDS.items()
        if pillar in record["pillars"]
    ]
    return f"""<section class="p-section ra-portfolio-shelf" data-ra-portfolio-shelf="{pillar.lower()}">
  <div class="container">
    <div class="eyebrow">{copy['eyebrow']} · {len(selected)} Projects</div>
    <h2>{copy['title']}</h2>
    <p class="lead">{copy['description']} Cross-pillar projects appear everywhere they carry evidence.</p>
    <div class="pf-grid">
      {chr(10).join(selected)}
    </div>
    <div class="ra-portfolio-shelf__footer">
      <a href="/portfolio?filter={pillar.lower()}" class="btn btn--outline">Open the filtered {public_pillar(pillar)} proof index <i class="fa-solid fa-arrow-right"></i></a>
    </div>
  </div>
</section>"""


def populate_pillar_hubs(portfolio_text: str) -> int:
    cards = extract_mapped_cards(portfolio_text)
    changed = 0
    for pillar in PILLAR_COPY:
        path = ROOT / "portfolio" / f"{pillar.lower()}.html"
        original = read(path)
        text = original
        copy = PILLAR_COPY[pillar]
        if pillar == "Sales":
            text = text.replace("Sales Work", "Sales Systems Work")
            text = text.replace("Sales work.", "Sales Systems work.")
            text = re.sub(r"Portfolio · Sales(?! Systems)", "Portfolio · Sales Systems", text)
            text = re.sub(r"Portfolio &middot; Sales(?! Systems)", "Portfolio &middot; Sales Systems", text)
        text, hero_count = re.subn(
            r'(<section class="p-hero">.*?<h1>.*?</h1>\s*<p class="lead">).*?(</p>)',
            rf"\g<1>{copy['description']}\g<2>",
            text,
            count=1,
            flags=re.S,
        )
        if hero_count != 1:
            raise ValueError(f"Could not normalize pillar hero in {path}")
        section = build_pillar_section(pillar, cards)
        text, count = re.subn(
            r'<section class="p-section(?: ra-portfolio-shelf)?"[^>]*>.*?</section>',
            section,
            text,
            count=1,
            flags=re.S,
        )
        if count != 1:
            raise ValueError(f"Could not replace pillar section in {path}")
        if "portfolio-cards-v3.css" not in text:
            text = text.replace(
                '<!-- RA-REFRESH-2026:css -->',
                '<link rel="stylesheet" href="/assets/css/portfolio-cards-v3.css">\n<!-- RA-REFRESH-2026:css -->',
                1,
            )
        if text != original:
            write(path, text)
            changed += 1
    return changed


def qualitative_outcomes(heading: str, metrics: list[tuple[str, str]]) -> str:
    cards = "\n".join(
        "      <div class=\"cs-metric\">\n"
        f"        <div class=\"cs-metric__value\">{value}</div>\n"
        f"        <div class=\"cs-metric__label\">{label}</div>\n"
        "      </div>"
        for value, label in metrics
    )
    return (
        '<section class="cs-outcomes">\n'
        '  <div class="cs-outcomes__inner">\n'
        f'    <h2>{heading}</h2>\n'
        '    <div class="cs-outcomes__grid">\n'
        f'{cards}\n'
        '    </div>\n'
        '  </div>\n'
        '</section>'
    )


def replace_outcomes(
    text: str,
    heading: str,
    metrics: list[tuple[str, str]],
) -> str:
    return re.sub(
        r'<section class="cs-outcomes">.*?</section>',
        qualitative_outcomes(heading, metrics),
        text,
        count=1,
        flags=re.S,
    )


def sanitize_nms_proof(text: str, rel: str) -> str:
    if "net-metering-systems" not in rel:
        return text

    safe_overview = (
        "Multi-discipline engagement &mdash; brand, website, video, social, SEO, and marketing "
        "operations &mdash; with paid-social and CRM/sales-automation systems in production."
    )
    safe_marketing = (
        "Paid-social campaigns and ad creative connected to live reporting and CRM follow-up."
    )
    safe_automation = (
        "GoHighLevel automations covering lead intake, follow-up, rep reminders, pipeline "
        "management, and weekly reporting."
    )

    replacements = {
        "Paid social advertising and social media management for Net Metering Systems — measured paid-social program, 25% lead-to-appointment rate, positive return on ad spend via Facebook and Instagram.":
            "Paid-social campaigns and social media operations for Net Metering Systems, connected to live reporting and CRM follow-up.",
        "GoHighLevel automation system, AI-powered follow-up, and live sales intelligence built for Net Metering Systems — 12 management automations and weekly owner performance reports.":
            "GoHighLevel automation, AI-assisted follow-up, and live sales intelligence built for Net Metering Systems.",
        "paid social program. <span class=\"highlight\">positive return on ad spend.</span>":
            "Paid social. <span class=\"highlight\">Connected to live reporting.</span>",
        "Active Facebook and Instagram ad campaigns &mdash; paid social program, 25% lead-to-appointment, positive return on ad spend &mdash; with live performance data piped into the Revelation Portal.":
            "Active Facebook and Instagram campaigns connected to live reporting, CRM follow-up, and the Revelation Portal.",
        "GoHighLevel subaccount with 12 management automations &mdash; AI-powered custom follow-up replies, automated sales rep reminders, weekly owner performance reports.":
            safe_automation,
        "GoHighLevel subaccount running 12 management automations &mdash; AI-generated follow-up replies on every incoming lead, automated sales rep reminders, weekly owner performance reports, all wired into the Revelation Portal&rsquo;s live data feed.":
            safe_automation,
        "12 management automations, AI-generated follow-up replies, weekly performance reports.":
            safe_automation,
        "12 management automations, AI follow-up replies, weekly performance reports.":
            safe_automation,
        "Full-stack growth system &mdash; AI-generated follow-up replies on every lead, 12 management automations, and live Revelation Portal intelligence.":
            "Connected CRM follow-up, rep reminders, pipeline management, weekly reporting, and live Revelation Portal intelligence.",
        "Vertical Facebook + Instagram ad creative produced in-house alongside the long-form solar project videos. These spots power the paid social engine &mdash; paid social program, positive return on ad spend &mdash; and live double-duty as social and ad content.":
            "Vertical Facebook and Instagram ad creative produced alongside the long-form solar project videos. The spots support paid-social campaigns and also work as organic social content.",
        "Paid Facebook + Instagram campaigns and 9 short-form vertical ad spots feeding live performance intelligence through the Revelation Portal &mdash; $50 average cost per lead, 25% lead-to-appointment, 5x sustained ROAS.":
            safe_marketing,
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r'<p>We built the complete stack\..*?</p>',
        f'<p>{safe_overview}</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p>Result:.*?</p>',
        '<p>The paid-social and CRM/sales-automation systems are in production and connected to live reporting.</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p>The ad system is connected to the Revelation Portal,.*?</p>',
        f'<p>{safe_marketing}</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p>The nine short-form ad spots were purpose-built.*?</p>',
        '<p>Short-form ad spots were purpose-built for paid social, formatted for mobile-first viewing, and structured around one clear message.</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p>We built out a fully customized GoHighLevel subaccount with 12 management automations.*?</p>',
        f'<p>{safe_automation}</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<p>Fully customized GoHighLevel subaccount — 12 management automations.*?</p>',
        f'<p>{safe_automation}</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'\b12 management automations?\b',
        "connected GoHighLevel automations",
        text,
        flags=re.I,
    )

    if rel.endswith("net-metering-systems-marketing.html"):
        text = replace_outcomes(text, "Connected campaign operations.", [
            ("Paid Social", "Campaign delivery"),
            ("Live", "Performance reporting"),
            ("CRM", "Follow-up connected"),
            ("In Production", "Operating system"),
        ])
    elif rel.endswith("net-metering-systems-video.html"):
        text = replace_outcomes(text, "Content in market.", [
            ("Long-Form", "Case-study video"),
            ("Short-Form", "Campaign creative"),
            ("Multi-Platform", "Publishing system"),
            ("In Production", "Active campaign use"),
        ])
    return text


def sanitize_trust_proof(text: str, rel: str) -> str:
    trust_case = rel.startswith("portfolio/case-studies/trust-energy")
    legacy_trust_files = {
        "services.html",
        "services/marketing/digital-ads.html",
        "services/systems/brand-systems.html",
        "portfolio/marketing/digital-ads.html",
        "portfolio/systems/ai-automation.html",
    }
    if not trust_case and rel not in legacy_trust_files:
        return text

    safe_full_stack = (
        "Full-stack engagement covering brand, website, video, and marketing operations."
    )
    safe_operations = (
        "Paid-social campaigns with GHL follow-up, lead delegation, a call-center build, and a training portal."
    )
    replacements = {
        "Multi-year Facebook ads at <strong>paid social program</strong> against an industry CPL of $40-$50, with a <strong>1-in-4 lead-to-appointment ratio</strong>. Custom GHL follow-up + lead delegation, a call center build, and a training portal that onboards new solar reps without manager bandwidth.":
            safe_operations,
        "<strong>paid social program</strong> sustained for 4 years &mdash; against $40-$50 industry CPL.":
            safe_operations,
        "Facebook Acquisition &mdash; paid social program, 4 Years Sustained":
            "Facebook Acquisition &mdash; Multi-Year Engagement",
        "Solar Industry &middot; 4 Years &middot; paid social program":
            "Solar Industry &middot; Multi-Year Engagement &middot; Connected Delivery",
        "The Trust Energy brand piece &mdash; the foundation video that anchored 4 years of solar storytelling and powered the paid acquisition engine.":
            "The Trust Energy brand piece anchored a multi-year run of solar storytelling and campaign creative.",
        "paid social program. <span class=\"highlight\">4 years sustained.</span>":
            "Paid social. <span class=\"highlight\">Multi-year engagement.</span>",
        "Facebook acquisition at <strong>paid social program</strong> &mdash; against $40-$50 industry CPL, with a 1-in-4 lead-to-appointment ratio. Seasonal creative, AI-generated concepts, and on-the-ground activations powered the engine.":
            safe_operations,
        "Full ownership of the Trust Energy Facebook presence across 4 years &mdash; content cadence, community engagement, page health, and brand-consistent storytelling.":
            "Full ownership of the Trust Energy Facebook presence across a multi-year engagement &mdash; content cadence, community engagement, page health, and brand-consistent storytelling.",
        "paid social program Facebook acquisition sustained for 4 years.":
            "Paid-social campaigns connected to GHL follow-up and lead delegation.",
        "paid social program for 4 years against $40-$50 industry CPL.":
            safe_operations,
        "Custom GHL follow-up + delegation routing leads to specific reps &mdash; powering the paid social program acquisition engine sustained over 4 years.":
            safe_operations,
        "Whole-brand build for the solar dealer surface &mdash; identity system anchoring 4 years of paid acquisition at paid social program.":
            safe_full_stack,
        "(vs. $40-$50 industry CPL)":
            "(connected to CRM follow-up and live reporting)",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    if trust_case:
        text = re.sub(
            r'<p>The compound effect:.*?</p>',
            '<p>Organic social and paid creative were managed as one operating cadence, reinforcing recognition before and after each campaign touch.</p>',
            text,
            count=1,
            flags=re.S,
        )
        text = replace_outcomes(text, "A connected system in production.", [
            ("Full-Stack", "Brand, content, and operations"),
            ("Multi-Year", "Connected engagement"),
            ("In Production", "GHL and campaign operations"),
        ])

        # Tenure is safe only as qualitative, multi-year delivery copy.
        text = text.replace("4 Years Sustained", "Multi-Year Engagement")
        text = text.replace("4 years sustained", "multi-year engagement")
        text = text.replace("sustained for 4 years", "operated as a multi-year engagement")
        text = text.replace("across 4 years", "across the multi-year engagement")
        text = text.replace("over 4 years", "across a multi-year engagement")
        text = text.replace("for 4 years", "as a multi-year engagement")
        text = text.replace("Four years", "Multi-year engagement")
        text = text.replace("four years", "multi-year engagement")
    return text


def sanitize_highlands_proof(text: str, rel: str) -> str:
    if not rel.startswith("portfolio/case-studies/highlands-energy"):
        return text
    text = text.replace(
        'Revelation Agency produced an authority video for the PG&amp;E ISA program offer, ran <strong>paid social program Facebook ads</strong> against it (industry CPL benchmarks for solar are 3-5x that), and built a GoHighLevel routing system that hands every inbound directly to the call center within minutes.',
        'Revelation Agency produced an authority video for the PG&amp;E ISA program offer and connected the campaign to a GoHighLevel routing workflow.',
    )
    text = text.replace(
        'Paid acquisition tuned to <strong>$9 per lead</strong> &mdash; well under industry CPL benchmarks for solar.',
        'Paid distribution connected to the authority video and GoHighLevel routing workflow.',
    )
    return replace_outcomes(text, "Video connected to delivery.", [
        ("Authority", "PG&amp;E ISA video"),
        ("Paid", "Campaign distribution"),
        ("Routed", "GoHighLevel workflow"),
    ])


def proof_blockers(text: str, rel: str) -> list[str]:
    patterns: list[tuple[str, str]] = []
    if "net-metering-systems" in rel:
        patterns.extend([
            (r"\$50", "$50 claim"),
            (r"25%\s+lead-to-appointment", "25% appointment claim"),
            (r"5x.{0,30}(?:ROAS|return)", "5x return claim"),
            (r"positive return on ad spend", "unsupported return claim"),
            (r"\b12\s+management automations?\b", "unproved automation count"),
        ])
    if rel.startswith("portfolio/case-studies/trust-energy") or rel in {
        "services.html",
        "services/marketing/digital-ads.html",
        "services/systems/brand-systems.html",
        "portfolio/marketing/digital-ads.html",
        "portfolio/systems/ai-automation.html",
    }:
        patterns.extend([
            (r"\$25", "$25 claim"),
            (r"\$40\s*[-–]\s*\$50", "$40-$50 benchmark"),
            (r"1-in-4|1:4", "appointment ratio"),
            (r"\b4\s+years?\b|\bfour years\b", "exact tenure claim"),
            (r"half-industry\s+CPL", "industry comparison"),
        ])
    if rel.startswith("portfolio/case-studies/highlands-energy"):
        patterns.extend([
            (r"\$9", "$9 claim"),
            (r"3\s*[-–]\s*5x", "CPL benchmark multiplier"),
        ])
    return [label for pattern, label in patterns if re.search(pattern, text, re.I | re.S)]


def normalize_paid_social_placeholder(text: str) -> str:
    replacements = {
        "ran the Facebook lead-gen at <strong>paid social program</strong> through paid ads":
            "ran Facebook lead-generation campaigns",
        "ran <strong>paid social program Facebook ads for two years</strong>":
            "ran <strong>multi-year Facebook campaigns</strong>",
        "paid social program paid social": "paid-social campaigns",
        "paid social program paid acquisition engine": "paid acquisition engine",
        "paid social program acquisition engine": "paid acquisition engine",
        "paid social program Facebook + Instagram ad campaigns": "Facebook + Instagram ad campaigns",
        "paid social program Facebook acquisition": "Facebook acquisition",
        "paid social program Facebook ads": "Facebook campaigns",
        "paid social program ads": "paid-social campaigns",
        "booked site visits at qualified site-visit opportunities": "qualified site-visit opportunities",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    def repl(match: re.Match[str]) -> str:
        return "Paid-social campaigns" if match.group(0)[0].isupper() else "paid-social campaigns"

    return re.sub(r"paid social program", repl, text, flags=re.I)


def neutralize_proof_exceptions() -> int:
    # Keep this generator bounded to the portfolio surfaces it owns. Global
    # service, route, and navigation pages are maintained by other generators.
    files = sorted({
        ROOT / "portfolio.html",
        *(ROOT / "portfolio" / f"{pillar.lower()}.html" for pillar in PILLAR_COPY),
        *(ROOT / route.lstrip("/") for route in CASE_STUDIES),
    })
    replacements = {
        "single-digit lead costs": "qualified site-visit opportunities",
        "Two years, single-digit leads.": "A coordinated acquisition system.",
        "12 Automations": "Connected Automations",
        "12 automations": "Connected automations",
        "12 management automations": "connected GoHighLevel automations",
        "Zero leads dropped.": "Follow-up made visible.",
        "4-Year": "Multi-Year",
        "4-year": "multi-year",
        "four-year": "multi-year",
        "Four Disciplines. Multi-Year Engagement.": "Connected Disciplines. Multi-Year Engagement.",
    }
    unresolved: list[str] = []
    staged: list[tuple[Path, str]] = []
    for path in files:
        original = read(path)
        text = original
        rel = path.relative_to(ROOT).as_posix()
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = neutralize_unverified_summary_stats(text)
        text = sanitize_nms_proof(text, rel)
        text = sanitize_trust_proof(text, rel)
        text = sanitize_highlands_proof(text, rel)
        text = normalize_paid_social_placeholder(text)
        for blocker in proof_blockers(text, rel):
            unresolved.append(f"{rel}: {blocker}")
        if text != original:
            staged.append((path, text))
    if unresolved:
        raise ValueError("Proof-safety migration left blocked claims: " + "; ".join(unresolved))
    for path, text in staged:
        write(path, text)
    return len(staged)


def main() -> None:
    case_changes = migrate_case_studies()
    mapped, portfolio_text = migrate_portfolio_hub()
    pillar_changes = populate_pillar_hubs(portfolio_text)
    proof_changes = neutralize_proof_exceptions()
    print(f"Case-study records applied: {len(CASE_STUDIES)} ({case_changes} files changed)")
    print(f"Master cards mapped: {mapped}")
    print(f"Pillar shelves populated: {pillar_changes}")
    print(f"Proof-safe copy files changed: {proof_changes}")


if __name__ == "__main__":
    main()
