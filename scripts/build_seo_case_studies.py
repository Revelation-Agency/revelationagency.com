#!/usr/bin/env python3
"""Build the SEO / AI-Answers case studies used for outreach.

Three clients demonstrate the M1 discipline (SEO / AI Answers) and none of
them had an outreach-ready page:

  Shepherd Cleaning Solutions  no case study at all, and no portfolio entry
  Excel Sign Company           one master card, no discipline page
  Net Metering Systems         had an M1 page written before results landed,
                               whose outcomes section still said rankings had
                               not moved yet

Every number on these pages is sourced and dated in the page itself. Claims
that cannot be substantiated on demand do not belong on a page whose entire
job is to be believed by a stranger.

Sources used:
  SpyFu API pull, 21 Aug 2026 (SERP index 15 Jun - 17 Aug 2026)
  Operator verification on Google and AI assistants, 21 Aug 2026

Run after this: build_routes_artifacts.py, write_vercel_and_sitemap.py,
verify_2026_refresh.py --max-errors 0
"""
from __future__ import annotations

import html
import io
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CS = REPO / "portfolio" / "case-studies"
TEMPLATE = CS / "net-metering-systems-seo.html"
CANON = "https://www.revelationagency.com"

NAV_END = "<!-- RA-NAV-CANONICAL-END -->"
FOOTER_START = "<!-- RA-FOOTER-CANONICAL-START -->"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# --------------------------------------------------------------------------
# Page specs
# --------------------------------------------------------------------------

SHEPHERD_SIBLINGS = [
    ("shepherd-cleaning-solutions", "Full Case Study"),
    ("shepherd-cleaning-solutions-seo", "SEO / AI Answers"),
]
EXCEL_SIBLINGS = [
    ("excel-sign-company", "Full Case Study"),
    ("excel-sign-company-seo", "SEO / AI Answers"),
]

PAGES = [
    {
        "slug": "shepherd-cleaning-solutions-seo",
        "project": "Shepherd Cleaning Solutions",
        "pillars": ["Marketing"],
        "title": "Shepherd Cleaning Solutions — SEO & AI Answer Visibility | Revelation Agency",
        "desc": ("A new Clovis commercial cleaning brand that AI assistants now recommend by "
                 "name. Case study in SEO and AI answer engine visibility."),
        "eyebrow": "Case Study — Marketing",
        "h1_top": "Shepherd Cleaning Solutions",
        "h1_hl": "SEO &amp; AI Answer Visibility",
        "chips": [("M1", "SEO / AI Answers", "/services/marketing/seo-ai-visibility")],
        "meta_line": "New Domain &middot; Commercial Cleaning &middot; AI Answer Visibility &middot; Clovis &amp; Fresno &middot; 2026",
        "siblings": SHEPHERD_SIBLINGS,
        "active": "shepherd-cleaning-solutions-seo",
        "context_h2": "A brand-new domain that answer engines already name.",
        "facts": [
            ("Client", "Shepherd Cleaning Solutions"),
            ("Industry", "B2B Commercial Cleaning"),
            ("Year", "2026"),
            ("Live Site", '<a href="https://shepherdcleaningsolutions.com/" target="_blank" rel="noopener" style="color:var(--red);">ShepherdCleaningSolutions.com</a>'),
            ("Market", "Clovis, Fresno &amp; Central Valley"),
            ("Segments", "Office, medical, retail, fitness, faith, industrial"),
        ],
        "context_body": [
            "Commercial cleaning is a referral business that has quietly become a search business. "
            "Facility managers and office administrators no longer start with a phone call to a "
            "peer — they start by asking, and increasingly they are asking an assistant rather "
            "than a search box. The question is not &ldquo;commercial cleaning Clovis&rdquo; typed into "
            "Google. It is &ldquo;who is the best commercial cleaning company in Clovis?&rdquo; asked in "
            "plain language, and answered in a paragraph with one or two names in it.",
            "Shepherd Cleaning Solutions launched into that market with no domain history, no "
            "backlink profile, and no incumbent advantage. Revelation built the brand and the "
            "digital presence around how the buying decision actually gets made: a clear "
            "positioning a machine can summarise, service and industry pages that answer the "
            "specific question a facility manager is asking, structured business data, and "
            "content written to be quoted rather than merely ranked.",
            "The result is a company that punches far above its domain age. As of August 2026, "
            "ask a major AI assistant who the top commercial cleaning company in Clovis is and "
            "Shepherd Cleaning Solutions is named in the answer — a position normally reserved "
            "for businesses with a decade of accumulated authority. Verify it yourself: the "
            "claim is reproducible in about fifteen seconds.",
        ],
        "services_h2": "What&rsquo;s running.",
        "services": [
            ("fa-solid fa-brain", "Answer Engine Optimization",
             "Positioning, service and industry pages written so an assistant can extract a clean, "
             "confident recommendation — not just crawl a keyword."),
            ("fa-solid fa-location-dot", "Local Entity Foundation",
             "Consistent name, address, phone and service-area data so every surface agrees on who "
             "Shepherd is and where it operates."),
            ("fa-solid fa-sitemap", "Industry &amp; Service Architecture",
             "Dedicated pages for commercial office, medical, retail, fitness, faith, industrial, "
             "education and hospitality — the way buyers actually self-identify."),
            ("fa-solid fa-comments", "Question-Shaped Content",
             "Copy structured around the questions facility managers ask out loud, with the answer "
             "in the first sentence where an engine will find it."),
            ("fa-solid fa-shield-halved", "Trust Signals",
             "Insurance, vetting, walkthrough process and standards made explicit — the details a "
             "buyer needs before switching vendors."),
            ("fa-solid fa-gauge-high", "Conversion Path",
             "A single obvious next step — a walkthrough within 48 hours — rather than a contact "
             "form and hope."),
        ],
        "outcomes_h2": "Named, not just ranked.",
        "metrics": [
            ("#1", "Google position for commercial cleaning in Clovis, operator-verified 21 Aug 2026"),
            ("Named", "Recommended by name when AI assistants are asked for the top Clovis commercial cleaner"),
            ("New", "Achieved on a domain with no prior history or backlink profile"),
            ("8", "Industry segments given dedicated positioning"),
        ],
        "source_note": ("Ranking position and AI assistant recommendation independently verified by "
                        "Revelation Agency on 21 August 2026. AI answers vary by phrasing and change "
                        "over time — this claim is reproducible, not permanent."),
        "cross": [
            ("/portfolio/case-studies/shepherd-cleaning-solutions", "Full Project", "Shepherd Cleaning Solutions",
             "The complete engagement — brand, website, and search visibility for a new commercial cleaning company."),
            ("/services/marketing/seo-ai-visibility", "Service", "SEO / AI Answers",
             "How we build businesses that answer engines cite, not just search engines rank."),
            ("/locations/clovis-ca", "Location", "Marketing Agency in Clovis",
             "The local market this was built to win, and the rest of what we do here."),
        ],
        "cta_h2": "Want to be the name the answer gives?",
        "cta_p": "AI answer visibility is winnable right now, especially in local markets. Tell us the "
                 "question your buyers ask and we will tell you honestly whether you can own the answer.",
    },
    {
        "slug": "excel-sign-company-seo",
        "project": "Excel Sign Company",
        "pillars": ["Marketing"],
        "title": "Excel Sign Company — Local SEO & Geo Landing Pages | Revelation Agency",
        "desc": ("How a Clovis sign manufacturer built first-page presence across Clovis and Fresno "
                 "sign search with a service-by-city landing page architecture."),
        "eyebrow": "Case Study — Marketing",
        "h1_top": "Excel Sign Company",
        "h1_hl": "Local SEO &amp; Geo Landing Pages",
        "chips": [("M1", "SEO / AI Answers", "/services/marketing/seo-ai-visibility")],
        "meta_line": "Service &times; City Architecture &middot; Clovis &amp; Fresno &middot; Since 2004 &middot; 2026",
        "siblings": EXCEL_SIBLINGS,
        "active": "excel-sign-company-seo",
        "context_h2": "One page for every service, in every city.",
        "facts": [
            ("Client", "Excel Sign Company"),
            ("Industry", "Custom Signage &amp; Vehicle Wraps"),
            ("In Business Since", "2004"),
            ("Live Site", '<a href="https://www.excelsigncompany.com/" target="_blank" rel="noopener" style="color:var(--red);">ExcelSignCompany.com</a>'),
            ("Architecture", "Location hubs + service &times; city pages"),
            ("Market", "Clovis, Fresno &amp; Central Valley"),
        ],
        "context_body": [
            "Excel Sign Company has built signs in the Central Valley since 2004. The reputation was "
            "never the problem. The problem was that a business searching for a monument sign in "
            "Clovis and a business searching for a vehicle wrap in Fresno are two different searches, "
            "and a single homepage cannot win both — no matter how good the company behind it is.",
            "Revelation built Excel Sign an architecture that matches how the searches are actually "
            "phrased. Location hubs for Clovis and Fresno anchor the geography. Beneath them sits a "
            "page for each service in each city — monument signs, channel letters, cabinet signs, "
            "illuminated and non-illuminated signage, banners, dimensional letters, vehicle wraps — "
            "plus a permit-and-cost editorial layer answering the questions that come before a quote "
            "request.",
            "The structure is the strategy. Each page targets one intent, in one place, with the "
            "specificity a local buyer is searching with, and links back into the hub so authority "
            "accumulates rather than scattering. As of August 2026, SpyFu records Excel Sign ranking "
            "for fifteen distinct keywords that explicitly contain Clovis or Fresno, holding first "
            "position on its category term, and drawing more estimated organic traffic than most "
            "agencies in the same market draw for themselves.",
        ],
        "services_h2": "What&rsquo;s running.",
        "services": [
            ("fa-solid fa-map-location-dot", "Location Hubs",
             "Dedicated Clovis and Fresno pages that anchor the geography and carry internal "
             "authority down to every service page beneath them."),
            ("fa-solid fa-layer-group", "Service &times; City Pages",
             "Twenty-plus pages pairing each signage service with each city, so every distinct "
             "local search has a page written for exactly it."),
            ("fa-solid fa-file-lines", "Pre-Quote Editorial",
             "Permit, cost and specification content answering what buyers research before they "
             "ever request a quote."),
            ("fa-solid fa-code", "Structured Business Data",
             "LocalBusiness markup with geographic coordinates, hours and service area so search "
             "engines resolve Excel Sign as one confident local entity."),
            ("fa-solid fa-link", "Internal Link Architecture",
             "Hub-and-spoke linking that compounds authority instead of leaving pages orphaned."),
            ("fa-solid fa-magnifying-glass-chart", "Intent Mapping",
             "Every page mapped to a single search intent, so pages compete for buyers rather "
             "than against each other."),
        ],
        "outcomes_h2": "Specific pages win specific searches.",
        "metrics": [
            ("#1", "Best organic position held (SpyFu, 21 Aug 2026)"),
            ("15", "Distinct ranking keywords explicitly containing Clovis or Fresno"),
            ("20+", "Service &times; city landing pages deployed"),
            ("36", "Unique organic keywords in the SpyFu index"),
        ],
        "source_note": ("Ranking figures from a SpyFu API pull on 21 August 2026, US market; SpyFu's "
                        "SERP index for these terms was dated 15 June to 17 August 2026. Third-party "
                        "index data lags live Google results."),
        "cross": [
            ("/portfolio/case-studies/excel-sign-company", "Full Project", "Excel Sign Company",
             "The complete engagement — brand, website, and local search architecture."),
            ("/services/marketing/seo-ai-visibility", "Service", "SEO / AI Answers",
             "The discipline behind this build, and how we apply it to other local businesses."),
            ("/locations/clovis-ca", "Location", "Marketing Agency in Clovis",
             "The same architecture, applied to our own market."),
        ],
        "cta_h2": "Own every search in your market.",
        "cta_p": "If your business sells more than one service in more than one city, a single "
                 "homepage is leaving most of the market uncontested. Let's map what you should own.",
    },
    {
        "slug": "shepherd-cleaning-solutions",
        "project": "Shepherd Cleaning Solutions",
        "pillars": ["Branding", "Marketing"],
        "title": "Shepherd Cleaning Solutions — Brand, Website & Search | Revelation Agency",
        "desc": ("Brand, website, and search visibility for a new Clovis commercial cleaning "
                 "company that AI assistants now recommend by name."),
        "eyebrow": "Case Study — Branding &amp; Marketing",
        "h1_top": "Shepherd Cleaning Solutions",
        "h1_hl": "Premium B2B Cleaning, Built From Zero",
        "chips": [
            ("B3", "Brand Identity", "/services/branding/brand-strategy-identity"),
            ("B1", "Websites", "/services/branding/websites-landing-pages"),
            ("M1", "SEO / AI Answers", "/services/marketing/seo-ai-visibility"),
        ],
        "meta_line": "Brand Identity &middot; Website &middot; SEO &amp; AI Answers &middot; Clovis CA &middot; 2026",
        "siblings": SHEPHERD_SIBLINGS,
        "active": "shepherd-cleaning-solutions",
        "context_h2": "A standard, not a cleaning crew.",
        "facts": [
            ("Client", "Shepherd Cleaning Solutions"),
            ("Industry", "B2B Commercial Cleaning"),
            ("Year", "2026"),
            ("Live Site", '<a href="https://shepherdcleaningsolutions.com/" target="_blank" rel="noopener" style="color:var(--red);">ShepherdCleaningSolutions.com</a>'),
            ("Scope", "Brand identity, website, search visibility"),
            ("Market", "Clovis, Fresno &amp; Central Valley"),
        ],
        "context_body": [
            "Commercial cleaning is a category where almost every competitor sounds identical. "
            "The same stock photography, the same promises about reliability and attention to "
            "detail, the same request for a quote. A facility manager comparing five vendors "
            "cannot tell them apart, so the decision defaults to price — which is a race the "
            "good operators lose.",
            "Shepherd needed to enter that category and not sound like it. Revelation built the "
            "positioning around a single idea the company actually operates by: where others "
            "see a building, Shepherd sees a standard. That line drove everything downstream — "
            "a restrained, premium visual identity that reads more like a professional services "
            "firm than a janitorial vendor, and a site organised around the buyer&rsquo;s world "
            "rather than the vendor&rsquo;s service list.",
            "Eight industry segments each get their own positioning, because a medical clinic, "
            "a fitness studio and a warehouse are not buying the same thing. The conversion path "
            "is one clear commitment — a walkthrough within 48 hours — instead of a contact form. "
            "And the whole thing was written to be legible to machines as well as people, which "
            "is why a domain with no history is now named directly in AI assistant answers.",
        ],
        "services_h2": "What we built.",
        "services": [
            ("fa-solid fa-fingerprint", "Brand Identity",
             "Positioning, voice, and a restrained premium visual system that separates Shepherd "
             "from a category of near-identical competitors."),
            ("fa-solid fa-display", "Website",
             "A full site organised by industry and solution, built around one clear commitment "
             "rather than a generic quote request."),
            ("fa-solid fa-building-user", "Industry Positioning",
             "Eight segments — office, medical, retail, fitness, faith, industrial, education, "
             "hospitality — each addressed on its own terms."),
            ("fa-solid fa-brain", "AI Answer Visibility",
             "Content and structure written so answer engines can extract a confident "
             "recommendation, not just index a page."),
            ("fa-solid fa-location-dot", "Local Search Foundation",
             "Structured business data and consistent local signals across every surface."),
            ("fa-solid fa-calendar-check", "Conversion Path",
             "A single, specific next step — a walkthrough within 48 hours — that a facility "
             "manager can actually say yes to."),
        ],
        "outcomes_h2": "From zero to named.",
        "metrics": [
            ("#1", "Google position for commercial cleaning in Clovis, operator-verified 21 Aug 2026"),
            ("Named", "Recommended by name when AI assistants are asked for the top Clovis commercial cleaner"),
            ("8", "Industry segments given dedicated positioning"),
            ("48hr", "Walkthrough commitment as the single conversion path"),
        ],
        "source_note": ("Ranking position and AI assistant recommendation independently verified by "
                        "Revelation Agency on 21 August 2026. AI answers vary by phrasing and change "
                        "over time — this claim is reproducible, not permanent."),
        "cross": [
            ("/portfolio/case-studies/shepherd-cleaning-solutions-seo", "Marketing", "SEO &amp; AI Answer Visibility",
             "How a brand-new domain became the name the answer gives."),
            ("/services/branding/brand-strategy-identity", "Service", "Brand Identity",
             "The positioning and identity discipline behind this build."),
            ("/locations/clovis-ca", "Location", "Marketing Agency in Clovis",
             "The local market this was built to win."),
        ],
        "cta_h2": "Entering a crowded category?",
        "cta_p": "The businesses that win categories like this are not the loudest — they are the "
                 "clearest. Tell us what you do differently and we will tell you whether it is "
                 "sayable.",
    },
]


NMS_SEO = CS / "net-metering-systems-seo.html"

# The NMS M1 page was written before results landed. Its outcomes section still
# described the build rather than what it produced, and its closing context
# paragraph said rankings had not moved yet. Both are now measurably wrong.
NMS_OLD_TAIL = (
    "Rankings aren&rsquo;t lighting up overnight &mdash; SEO never does &mdash; but the "
    "trajectory is clear and the foundation is built to make Net Metering Systems the "
    "dominant search presence for solar in the Central Valley."
)
NMS_NEW_TAIL = (
    "The system worked. As of August 2026, SpyFu records Net Metering Systems holding "
    "first position on its category terms, ranking across 159 distinct organic keywords, "
    "and sitting on page one for the Clovis solar cluster &mdash; alongside top-five "
    "positions in Auberry, Oakhurst, Parlier and Dinuba, towns most competitors never "
    "bothered to target."
)

NMS_OLD_METRICS = """      <div class="cs-metric">
        <div class="cs-metric__value">150</div>
        <div class="cs-metric__label">Listing pages deployed and optimized for local intent</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">Weekly</div>
        <div class="cs-metric__label">Research-driven blog publishing cadence</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">Top 5</div>
        <div class="cs-metric__label">Local solar competitors tracked programmatically</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">AI</div>
        <div class="cs-metric__label">Answer engine optimization &mdash; built to be cited</div>
      </div>"""

NMS_NEW_METRICS = """      <div class="cs-metric">
        <div class="cs-metric__value">#1</div>
        <div class="cs-metric__label">Position held on category search terms</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">159</div>
        <div class="cs-metric__label">Distinct organic keywords ranking</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">Page 1</div>
        <div class="cs-metric__label">Across the Clovis solar search cluster</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">150</div>
        <div class="cs-metric__label">Listing pages deployed and optimized for local intent</div>
      </div>"""

NMS_SOURCE_NOTE = (
    '    <p style="margin-top:40px;font-size:12px;line-height:1.7;'
    'color:rgba(255,255,255,0.5);max-width:70ch;">Ranking figures from a SpyFu API pull on '
    '21 August 2026, US market; SpyFu&rsquo;s SERP index for these terms was dated 15 June to '
    '17 August 2026. Third-party index data lags live Google results.</p>\n'
)


def patch_nms() -> bool:
    """Replace the pre-results copy on the NMS M1 page with measured outcomes."""
    s = io.open(NMS_SEO, encoding="utf-8").read()
    if "159" in s and "SpyFu" in s:
        print("  net-metering-systems-seo.html: already updated")
        return False
    changed = False
    if NMS_OLD_TAIL in s:
        s = s.replace(NMS_OLD_TAIL, NMS_NEW_TAIL, 1)
        changed = True
    else:
        print("  WARNING: NMS context tail not found; left as-is")
    if NMS_OLD_METRICS in s:
        s = s.replace(NMS_OLD_METRICS, NMS_NEW_METRICS, 1)
        changed = True
    else:
        print("  WARNING: NMS metrics block not found; left as-is")
    if changed and "SpyFu API pull on" not in s:
        s = s.replace("    </div>\n  </div>\n</section>\n\n<section class=\"cs-cross\">",
                      "    </div>\n" + NMS_SOURCE_NOTE + "  </div>\n</section>\n\n<section class=\"cs-cross\">", 1)
    if changed:
        io.open(NMS_SEO, "w", encoding="utf-8", newline="").write(s)
        print("  patched net-metering-systems-seo.html with measured outcomes")
    return changed


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def load_template() -> tuple[str, str]:
    raw = TEMPLATE.read_text(encoding="utf-8")
    i = raw.index(NAV_END) + len(NAV_END)
    j = raw.index(FOOTER_START)
    return raw[:i], raw[j:]


def set_creative_work(head: str, *, project: str, url: str,
                      about: list[str], pillars: list[str]) -> str:
    """Rewrite the cloned CreativeWork node to describe THIS case study.

    The head is cloned from the Net Metering M1 page, which carries its own
    CreativeWork JSON-LD. Left alone, every generated page would tell search
    engines it is a Net Metering Systems case study.
    """
    node = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": f"{project} — Revelation Agency Case Study",
        "url": url,
        "creator": {"@type": "Organization", "name": "Revelation Agency"},
        "about": about,
        "keywords": pillars,
    }
    return re.sub(
        r'(<script type="application/ld\+json">)\s*\{.*?\}\s*(</script>)',
        lambda m: m.group(1) + "\n" + json.dumps(node, indent=2) + "\n" + m.group(2),
        head, count=1, flags=re.S)


def set_head(head: str, *, title: str, desc: str, url: str) -> str:
    out = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", head, count=1, flags=re.S)
    out = re.sub(r'(<meta name="description" content=")[^"]*(")',
                 lambda m: m.group(1) + html.escape(desc, quote=True) + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
                 lambda m: m.group(1) + url + m.group(2), out, count=1)
    for prop, val in (("og:title", title), ("og:description", desc), ("og:url", url)):
        out = re.sub(rf'(<meta property="{prop}" content=")[^"]*(")',
                     lambda m, v=val: m.group(1) + html.escape(v, quote=True) + m.group(2),
                     out, count=1)
    return out


def render(spec: dict) -> str:
    sib = "\n".join(
        f'        <a href="/portfolio/case-studies/{s}"'
        + (' class="active"' if s == spec["active"] else "")
        + f'>{lbl}</a>'
        for s, lbl in spec["siblings"]
    )
    facts = "\n".join(
        f'        <li><span class="lbl">{k}</span><span class="val">{v}</span></li>'
        for k, v in spec["facts"]
    )
    ctx = "\n".join(f"      <p>{p}</p>" for p in spec["context_body"])
    svc = "\n".join(
        f'''      <div class="cs-service-card">
        <div class="cs-service-card__icon"><i class="{icon}"></i></div>
        <h3>{name}</h3>
        <p>{body}</p>
      </div>''' for icon, name, body in spec["services"]
    )
    mets = "\n".join(
        f'''      <div class="cs-metric">
        <div class="cs-metric__value">{v}</div>
        <div class="cs-metric__label">{l}</div>
      </div>''' for v, l in spec["metrics"]
    )
    cross = "\n".join(
        f'''    <a class="cs-cross__card" href="{href}">
      <div class="cs-cross__lbl">{lbl}</div>
      <div class="cs-cross__title">{title}</div>
      <p style="font-size:14px;line-height:1.6;color:#555;margin-bottom:16px;">{body}</p>
      <div class="cs-cross__arrow">View <i class="fa-solid fa-arrow-right"></i></div>
    </a>''' for href, lbl, title, body in spec["cross"]
    )
    chips = "".join(
        f'<a href="{href}" class="ra-case-taxonomy__chip" title="{code} &middot; {label}">'
        f'<span>{code}</span>{label}</a>'
        for code, label, href in spec["chips"]
    )
    return f'''
<section class="cs-hero">
  <div class="container">
    <div class="cs-hero__inner">
      <a class="cs-hero__back" href="/portfolio">
        <i class="fa-solid fa-arrow-left"></i> Back to portfolio
      </a>
      <div class="cs-hero__nav">
{sib}
      </div>
      <span class="eyebrow">{spec["eyebrow"]}</span>
      <h1>{spec["h1_top"]}<br><span class="highlight">{spec["h1_hl"]}</span></h1>
      <!-- RA-PORTFOLIO-TAXONOMY:visible -->
<div class="ra-case-taxonomy" aria-label="Mapped service disciplines">{chips}</div>
      <div class="cs-hero__meta">{spec["meta_line"]}</div>
    </div>
  </div>
</section>

<section class="cs-context">
  <div class="cs-context__inner">
    <div>
      <div class="cs-context__num">01 &mdash; Context</div>
      <h2>{spec["context_h2"]}</h2>
      <ul class="cs-meta-list">
{facts}
      </ul>
    </div>
    <div class="cs-context__body">
{ctx}
    </div>
  </div>
</section>

<section class="cs-services">
  <div class="cs-services__head">
    <span class="eyebrow">02 &mdash; Services Delivered</span>
    <h2>{spec["services_h2"]}</h2>
  </div>
  <div class="cs-services__grid">
{svc}
  </div>
</section>

<section class="cs-outcomes">
  <div class="cs-outcomes__inner">
    <h2>{spec["outcomes_h2"]}</h2>
    <div class="cs-outcomes__grid">
{mets}
    </div>
    <p style="margin-top:40px;font-size:12px;line-height:1.7;color:rgba(255,255,255,0.5);max-width:70ch;">{spec["source_note"]}</p>
  </div>
</section>

<section class="cs-cross">
  <div class="cs-cross__head">
    <span class="eyebrow">Cross-Discipline</span>
    <h2>Part of a bigger system.</h2>
  </div>
  <div class="cs-cross__grid">
{cross}
  </div>
</section>

<section class="cs-cta">
  <div class="cs-cta__inner">
    <h2>{spec["cta_h2"]}</h2>
    <p>{spec["cta_p"]}</p>
    <a href="/booking" class="btn btn--white" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a>
  </div>
</section>

'''


def main() -> int:
    head_t, foot_t = load_template()
    written = []
    for spec in PAGES:
        url = f"{CANON}/portfolio/case-studies/{spec['slug']}"
        head = set_head(head_t, title=spec["title"], desc=spec["desc"], url=url)
        head = set_creative_work(
            head, project=spec["project"], url=url,
            about=[label for _c, label, _h in spec["chips"]],
            pillars=spec["pillars"])
        page = head + render(spec) + foot_t
        out = CS / f"{spec['slug']}.html"
        io.open(out, "w", encoding="utf-8", newline="").write(page)
        written.append(out.relative_to(REPO).as_posix())
        print(f"  wrote {out.relative_to(REPO)}")
    patch_nms()
    print(f"{len(written)} case studies written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
