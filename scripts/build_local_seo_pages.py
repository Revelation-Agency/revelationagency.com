#!/usr/bin/env python3
"""Build the local-SEO geo architecture for revelationagency.com.

The agency ranks for essentially nothing in its own market (SpyFu, 21 Aug 2026:
18 organic records, 0 estimated monthly clicks, best position #19) while two of
its clients hold #1 positions off the back of 20+ geo landing pages each.
Revelation had zero. This builds them.

Emits, from the canonical service-leaf template:

    /locations                          location index
    /locations/<city>                   city hub          (one per CITIES row)
    /locations/<city>/<service>         service x city    (CITIES x SERVICES)

Every page carries ProfessionalService + BreadcrumbList + FAQPage JSON-LD.
Content is written per city from real local proof, not spun from one template
string -- thin duplicated doorway pages are a ranking liability, not an asset.

Pipeline (routes are NOT auto-discovered; they are registered in
build_routes_artifacts.py):

    python scripts/build_local_seo_pages.py
    python scripts/build_routes_artifacts.py
    python scripts/write_vercel_and_sitemap.py
    python scripts/verify_2026_refresh.py --max-errors 0
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "services" / "branding" / "brand-strategy-identity.html"
CANON = "https://www.revelationagency.com"

NAV_END = "<!-- RA-NAV-CANONICAL-END -->"
FOOTER_START = "<!-- RA-FOOTER-CANONICAL-START -->"

# --- Business facts (from the site's existing Organization block) -------------
NAP = {
    "street": "55 Shaw Ave #201",
    "city": "Clovis",
    "region": "CA",
    "zip": "93612",
    "phone": "+15592017039",
    "phone_display": "(559) 201-7039",
    "email": "connect@revelationagency.com",
    "lat": 36.8252,
    "lon": -119.7029,
}

# --- Services offered per city ------------------------------------------------
# slug, nav label, H1 noun, one-line promise, canonical service-leaf to link to
SERVICES = [
    ("branding", "Branding", "Branding",
     "Positioning, identity, and the rules that keep it consistent everywhere.",
     "/services/branding/brand-strategy-identity"),
    ("web-design", "Web Design", "Web Design",
     "Sites built to be found, understood, and acted on.",
     "/services/branding/websites-landing-pages"),
    ("seo", "SEO", "SEO",
     "The architecture that makes a business findable in search and in AI answers.",
     "/services/marketing/seo-ai-visibility"),
    ("google-ads", "Google Ads", "Google Ads Management",
     "Paid search that buys qualified calls, not impressions.",
     "/services/marketing/digital-ads"),
    ("social-media", "Social Media", "Social Media Marketing",
     "Consistent presence that compounds instead of resetting every month.",
     "/services/marketing/social-media"),
    ("video-production", "Video", "Video Production",
     "Video built as infrastructure — used across sales, ads, and site.",
     "/services/branding/video-visual-content"),
]

# --- Cities -------------------------------------------------------------------
# Each city needs genuinely distinct content. `context` is the local business
# reality, `proof` is real client work in or near that city, `faqs` are written
# per city. Nothing here is boilerplate with the city name swapped in.
CITIES = [
    {
        "slug": "clovis-ca",
        "name": "Clovis",
        "full": "Clovis, CA",
        "headline": "Clovis",
        "intro": (
            "Revelation Agency is headquartered on Shaw Avenue in Clovis. We are not a "
            "national firm with a Clovis landing page — the office, the team, and the "
            "work are here."
        ),
        "context": (
            "Clovis businesses compete in a market where word of mouth still closes deals "
            "and a weak digital presence quietly disqualifies you before the first call. "
            "Most local companies do not need more marketing channels. They need the "
            "brand, the site, and the follow-up to stop contradicting each other."
        ),
        "proof": [
            ("excel-sign-company", "Excel Sign Company",
             "A Clovis sign manufacturer with page-one visibility across Clovis and Fresno sign terms."),
            ("net-metering-systems", "Net Metering Systems",
             "Solar installer holding first-page positions across the Clovis solar cluster."),
            ("ivory-pools", "Ivory Pool Services",
             "Brand identity, website, signage, and bilingual video for a Central Valley service company."),
        ],
        "faqs": [
            ("Do you actually have an office in Clovis?",
             "Yes. Revelation Agency is at 55 Shaw Ave #201, Clovis, CA 93612. Meetings happen in person."),
            ("What does a marketing agency cost in Clovis?",
             "It depends on scope, and any agency that quotes a flat number before understanding the "
             "business is guessing. We scope the work, explain what each piece does, and are direct "
             "about what you do not need yet."),
            ("Do you only work with Clovis businesses?",
             "No. We work across Fresno, Madera, Visalia and the wider Central Valley, and with clients "
             "outside California. Clovis is simply where we are based."),
            ("Which services do Clovis businesses ask for most?",
             "Branding and websites first, because those are usually what is holding everything else "
             "back, followed by SEO and paid ads once the foundation can convert the traffic."),
        ],
    },
    {
        "slug": "fresno-ca",
        "name": "Fresno",
        "full": "Fresno, CA",
        "headline": "Fresno",
        "intro": (
            "Fresno is the largest market in the Central Valley and the most crowded. "
            "Revelation Agency works with Fresno businesses from our office minutes away "
            "in Clovis."
        ),
        "context": (
            "Fresno has no shortage of agencies. What it has a shortage of is agencies that "
            "will tell a business owner the honest sequence — brand, then site, then demand, "
            "then follow-up — instead of selling whichever service is easiest to bill monthly. "
            "Buying ads on top of a site that cannot convert is the most common and most "
            "expensive mistake we see here."
        ),
        "proof": [
            ("fresno-financial-advisors", "Fresno Financial Advisors",
             "Brand and digital presence for a Fresno financial practice."),
            ("net-metering-systems", "Net Metering Systems",
             "Fresno-based solar company with 159 ranking keywords and multiple #1 positions."),
            ("trust-energy", "Trust Energy",
             "Brand, video, social, paid media, CRM, and sales tooling as one system."),
        ],
        "faqs": [
            ("What makes you different from other Fresno marketing agencies?",
             "We sequence the work. Most engagements here start with fixing what the business "
             "already has rather than adding a new channel on top of it."),
            ("Do you do SEO for Fresno businesses?",
             "Yes — technical architecture, local landing pages, structured data, and the content "
             "that makes a business citable by AI answer engines, not just ranked in blue links."),
            ("Can you run our Google and Facebook ads too?",
             "Yes, though we will usually ask to see the site and the follow-up process first. "
             "Ads amplify whatever is already there, including the problems."),
            ("How long before we see results in Fresno search?",
             "Local search difficulty in this market is genuinely low, so structural fixes often "
             "move positions within weeks. Anyone promising a specific rank on a specific date is "
             "selling certainty that does not exist."),
        ],
    },
    {
        "slug": "madera-ca",
        "name": "Madera",
        "full": "Madera, CA",
        "headline": "Madera",
        "intro": (
            "Madera businesses are close enough to Fresno to compete with it and far enough "
            "out to be ignored by agencies based there. We work Madera as its own market."
        ),
        "context": (
            "Competition for Madera search terms is thin. That is an advantage for any local "
            "business willing to build a real presence, and a standing risk for the ones who "
            "assume nobody is looking. The businesses that show up here tend to keep showing up."
        ),
        "proof": [
            ("net-metering-systems", "Net Metering Systems",
             "Ranking across Madera and the surrounding Valley towns for solar terms."),
            ("infinite-heating-cooling", "Infinite Heating & Cooling",
             "Brand and website for a Central Valley home-services company."),
            ("four-cs-construction", "Four C's Construction",
             "Identity and digital presence for a Valley construction firm."),
        ],
        "faqs": [
            ("Do you work with Madera businesses?",
             "Yes. Madera is roughly 25 minutes from our Clovis office and we treat it as a "
             "distinct market rather than a Fresno suburb."),
            ("Is it worth doing SEO in a market this size?",
             "Often more worth it than in Fresno. Fewer competitors means the cost of reaching "
             "the first page is lower, and local intent converts well."),
            ("What is the smallest engagement you take?",
             "We would rather do one thing properly than five things thinly. If the honest answer "
             "is that you need a website and nothing else yet, that is what we will say."),
        ],
    },
    {
        "slug": "visalia-ca",
        "name": "Visalia",
        "full": "Visalia, CA",
        "headline": "Visalia",
        "intro": (
            "Visalia sits at the south end of our service area. We work with Visalia companies "
            "the same way we work with Clovis ones — in person where it matters."
        ),
        "context": (
            "Visalia has a strong independent business community and comparatively little "
            "agency competition. The opportunity for most companies here is not a bigger "
            "marketing budget; it is a presence that matches the quality of the operation."
        ),
        "proof": [
            ("net-metering-systems", "Net Metering Systems",
             "Solar visibility extended across Visalia and the southern Valley."),
            ("highlands-energy", "Highlands Energy",
             "Video and brand work for an energy company operating across the Valley."),
            ("the-whole-vine", "The Whole Vine",
             "Brand, website, social, and video for a Valley food and agriculture brand."),
        ],
        "faqs": [
            ("Are you able to service Visalia clients properly from Clovis?",
             "Yes. Visalia is about 45 minutes out. Most of the work is remote by nature, and we "
             "travel for the parts that are not."),
            ("Do you understand agriculture and Valley industry?",
             "A significant share of our client base is Valley agriculture, energy, construction, "
             "and home services. It is the market we come from."),
            ("Can you take over marketing we already have running?",
             "Usually. We will audit what exists first and tell you plainly what to keep."),
        ],
    },
]


# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_template() -> tuple[str, str, str]:
    """Return (head_and_nav, _unused_body, footer_and_tail) split on the markers."""
    raw = TEMPLATE.read_text(encoding="utf-8")
    i = raw.index(NAV_END) + len(NAV_END)
    j = raw.index(FOOTER_START)
    return raw[:i], raw[i:j], raw[j:]


def set_head(head: str, *, title: str, desc: str, url: str) -> str:
    """Rewrite the head meta for this page. Operates only on known-single tags."""
    out = head
    out = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", out, count=1, flags=re.S)
    out = re.sub(r'(<meta name="description" content=")[^"]*(")',
                 lambda m: m.group(1) + esc(desc) + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
                 lambda m: m.group(1) + url + m.group(2), out, count=1)
    for prop, val in (("og:title", title), ("og:description", desc), ("og:url", url)):
        out = re.sub(rf'(<meta property="{prop}" content=")[^"]*(")',
                     lambda m, v=val: m.group(1) + esc(v) + m.group(2), out, count=1)
    for name, val in (("twitter:title", title), ("twitter:description", desc)):
        out = re.sub(rf'(<meta name="twitter:title" content=")[^"]*(")' if name == "twitter:title"
                     else rf'(<meta name="twitter:description" content=")[^"]*(")',
                     lambda m, v=val: m.group(1) + esc(v) + m.group(2), out, count=1)
    return out


def local_business_ld(page_url: str, city: str | None, service_name: str | None) -> dict:
    area = [{"@type": "City", "name": c["name"] + ", CA"} for c in CITIES]
    node = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": CANON + "/#organization",
        "name": "Revelation Agency",
        "url": CANON,
        "logo": CANON + "/assets/brand/current/ra-lockup-red.png",
        "image": CANON + "/assets/brand/current/ra-social-card.png",
        "description": "Marketing agency in Clovis and Fresno, CA. Branding, websites, "
                       "SEO, paid ads, social, and video built as one system.",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": NAP["street"],
            "addressLocality": NAP["city"],
            "addressRegion": NAP["region"],
            "postalCode": NAP["zip"],
            "addressCountry": "US",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": NAP["lat"], "longitude": NAP["lon"]},
        "telephone": NAP["phone"],
        "email": NAP["email"],
        "priceRange": "$$",
        "areaServed": area,
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "09:00", "closes": "17:00",
        }],
        "sameAs": [
            "https://www.linkedin.com/company/reviiiagency",
            "https://www.instagram.com/reviiiagency/",
            "https://www.facebook.com/revelationagency/",
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": label}}
                for _, label, _, _, _ in SERVICES
            ],
        },
    }
    if city:
        node["serviceArea"] = {"@type": "City", "name": city}
    return node


def breadcrumb_ld(trail: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": CANON + path}
            for i, (name, path) in enumerate(trail)
        ],
    }


def faq_ld(faqs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }


def ld_block(*nodes: dict) -> str:
    return "\n".join(
        '<script type="application/ld+json">\n' + json.dumps(n, indent=2) + "\n</script>"
        for n in nodes
    )


def render_faqs(faqs: list[tuple[str, str]], heading: str) -> str:
    items = "\n".join(
        f'      <div class="ra-faq__item fade-up">\n'
        f'        <h3>{esc(q)}</h3>\n'
        f'        <p>{esc(a)}</p>\n'
        f'      </div>'
        for q, a in faqs
    )
    return f'''
<section class="p-section p-section--grey">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">Common Questions</div>
      <h2>{esc(heading)}</h2>
    </div>
    <div class="ra-faq">
{items}
    </div>
  </div>
</section>'''


def render_proof(proof: list[tuple[str, str, str]], heading: str, lede: str) -> str:
    cards = "\n".join(
        f'''      <a class="ra-service-proof fade-up fade-up-d{i+1}" href="/portfolio/case-studies/{slug}">
        <img src="/assets/img/portfolio/{slug}/thumbnail.png" alt="{esc(name)} case study" loading="lazy" width="1600" height="900">
        <span>Related work</span>
        <strong>{esc(name)}</strong>
        <p>{esc(blurb)}</p>
      </a>'''
        for i, (slug, name, blurb) in enumerate(proof)
    )
    return f'''
<section class="p-section ra-service-proof-section">
  <div class="container">
    <div class="ra-service-proof-heading fade-up">
      <div class="eyebrow">Local Work</div>
      <h2>{esc(heading)}</h2>
      <p class="lead">{esc(lede)}</p>
    </div>
    <div class="ra-service-proof-grid">
{cards}
    </div>
    <div class="ra-service-proof-more fade-up"><a href="/portfolio" class="btn btn--outline">Explore the full portfolio <i class="fa-solid fa-arrow-right"></i></a></div>
  </div>
</section>'''


def render_nap() -> str:
    return f'''
<section class="p-section">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">Find Us</div>
      <h2>Revelation Agency</h2>
      <p class="lead">
        {esc(NAP["street"])}, {esc(NAP["city"])}, {esc(NAP["region"])} {esc(NAP["zip"])}<br>
        <a href="tel:{NAP["phone"]}">{esc(NAP["phone_display"])}</a> ·
        <a href="mailto:{NAP["email"]}">{esc(NAP["email"])}</a>
      </p>
    </div>
  </div>
</section>'''


def city_service_links(city: dict) -> str:
    items = "\n".join(
        f'      <li><a href="/locations/{city["slug"]}/{s_slug}">{esc(h1_noun)} in {esc(city["name"])}</a> — {esc(promise)}</li>'
        for s_slug, _label, h1_noun, promise, _leaf in SERVICES
    )
    return f'''
<section class="p-section">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">What We Do Here</div>
      <h2>Services for {esc(city["name"])} businesses.</h2>
    </div>
    <ul class="ra-loc-services fade-up">
{items}
    </ul>
  </div>
</section>'''


def hero(eyebrow: str, h1: str, lead: str, secondary_href: str, secondary_label: str) -> str:
    return f'''<section class="p-hero ra-service-hero">
  <div class="container">
    <div class="p-hero__inner fade-up">
      <div class="eyebrow" style="color:rgba(255,255,255,0.62);">{esc(eyebrow)}</div>
      <h1>{esc(h1)}</h1>
      <p class="lead">{esc(lead)}</p>
      <div class="p-hero__cta">
        <a href="/booking" class="btn btn--primary" data-cta="primary" data-cta-placement="leaf-hero" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a>
        <a href="{secondary_href}" class="btn btn--ghost-dark">{esc(secondary_label)}</a>
      </div>
    </div>
  </div>
</section>'''


def cta(heading: str, body: str) -> str:
    return f'''
<section class="p-cta">
  <div class="container fade-up"><h2>{esc(heading)}</h2><p>{esc(body)}</p><a href="/booking" class="btn btn--white" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a></div>
</section>
'''


LOCAL_CSS = '<link rel="stylesheet" href="/assets/css/ra-local-seo.css?v=20260821a">'


def write(path: Path, head: str, body: str, footer: str, ld: str) -> None:
    head = head.replace("</head>", LOCAL_CSS + "\n" + ld + "\n</head>", 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(head + "\n" + body + "\n" + footer, encoding="utf-8")


def build_city_hub(city: dict, head_t: str, foot_t: str) -> str:
    url = f"{CANON}/locations/{city['slug']}"
    title = f"Marketing Agency in {city['full']} | Revelation Agency"
    desc = (f"Marketing agency serving {city['full']}. Branding, web design, SEO, Google Ads, "
            f"social, and video built as one system. Based in Clovis.")
    head = set_head(head_t, title=title, desc=desc, url=url)
    ld = ld_block(
        local_business_ld(url, city["full"], None),
        breadcrumb_ld([("Home", "/"), ("Locations", "/locations"),
                       (city["full"], f"/locations/{city['slug']}")]),
        faq_ld(city["faqs"]),
    )
    body = (
        hero(f"Marketing Agency · {city['full']}",
             f"Marketing Agency in {city['headline']}",
             city["intro"], "/locations", "All locations")
        + f'''
<section class="p-section ra-service-intro">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">The Market</div>
      <h2>What {esc(city["name"])} businesses are actually up against.</h2>
      <p class="lead">{esc(city["context"])}</p>
    </div>
  </div>
</section>'''
        + city_service_links(city)
        + render_proof(city["proof"],
                       f"Work for {city['name']} and Central Valley businesses.",
                       "Real client engagements. Generated concept art is never presented as client proof.")
        + render_faqs(city["faqs"], f"Working with an agency in {city['name']}.")
        + render_nap()
        + cta(f"Need a marketing agency in {city['name']}?",
              "Tell us what you are trying to improve. We will ask a few direct questions, "
              "explain the right next step, and be honest about fit.")
    )
    write(REPO / "locations" / f"{city['slug']}.html", head, body, foot_t, ld)
    return f"/locations/{city['slug']}"


def build_service_city(city: dict, svc: tuple, head_t: str, foot_t: str) -> str:
    s_slug, label, h1_noun, promise, leaf = svc
    url = f"{CANON}/locations/{city['slug']}/{s_slug}"
    title = f"{h1_noun} in {city['full']} | Revelation Agency"
    desc = f"{h1_noun} for {city['full']} businesses. {promise} Based in Clovis, CA."
    head = set_head(head_t, title=title, desc=desc, url=url)
    faqs = [
        (f"Do you provide {h1_noun.lower()} in {city['name']}?",
         f"Yes. {promise} We are based at {NAP['street']}, {NAP['city']}, {NAP['region']} "
         f"and work with businesses throughout {city['full']} and the Central Valley."),
        (f"How does {h1_noun.lower()} fit with the rest of our marketing?",
         "It is one piece of a system. We will tell you honestly whether this is the right "
         "next step for your business or whether something else should come first."),
        (f"What does {h1_noun.lower()} cost in {city['name']}?",
         "Scope drives the number. We scope the work, explain what each piece does, and are "
         "direct about what you do not need yet."),
    ]
    ld = ld_block(
        local_business_ld(url, city["full"], h1_noun),
        breadcrumb_ld([("Home", "/"), ("Locations", "/locations"),
                       (city["full"], f"/locations/{city['slug']}"),
                       (h1_noun, f"/locations/{city['slug']}/{s_slug}")]),
        faq_ld(faqs),
    )
    others = "\n".join(
        f'      <li><a href="/locations/{city["slug"]}/{o_slug}">{esc(o_noun)} in {esc(city["name"])}</a></li>'
        for o_slug, _l, o_noun, _p, _lf in SERVICES if o_slug != s_slug
    )
    body = (
        hero(f"{label} · {city['full']}", f"{h1_noun} in {city['headline']}", promise,
             f"/locations/{city['slug']}", f"All services in {city['name']}")
        + f'''
<section class="p-section ra-service-intro">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">What It Is</div>
      <h2>{esc(h1_noun)} for {esc(city["name"])} businesses.</h2>
      <p class="lead">{esc(city["context"])}</p>
      <p><a href="{leaf}">Read how we approach {esc(h1_noun.lower())} in detail →</a></p>
    </div>
  </div>
</section>

<section class="p-section p-section--grey">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">Also in {esc(city["name"])}</div>
      <h2>The rest of the system.</h2>
    </div>
    <ul class="ra-loc-services fade-up">
{others}
    </ul>
  </div>
</section>'''
        + render_proof(city["proof"], f"Related work in the Central Valley.",
                       "Real client engagements. Generated concept art is never presented as client proof.")
        + render_faqs(faqs, f"{h1_noun} in {city['name']}.")
        + render_nap()
        + cta(f"Need {h1_noun.lower()} in {city['name']}?",
              "Tell us what you are trying to improve. We will ask a few direct questions, "
              "explain the right next step, and be honest about fit.")
    )
    write(REPO / "locations" / city["slug"] / f"{s_slug}.html", head, body, foot_t, ld)
    return f"/locations/{city['slug']}/{s_slug}"


def build_index(head_t: str, foot_t: str) -> str:
    url = f"{CANON}/locations"
    title = "Marketing Agency Locations | Clovis, Fresno & Central Valley"
    desc = ("Revelation Agency serves Clovis, Fresno, Madera, and Visalia from our office "
            "in Clovis, CA. Branding, web design, SEO, ads, social, and video.")
    head = set_head(head_t, title=title, desc=desc, url=url)
    faqs = [
        ("Where is Revelation Agency based?",
         f"{NAP['street']}, {NAP['city']}, {NAP['region']} {NAP['zip']}."),
        ("Which areas do you serve?",
         "Clovis, Fresno, Madera, and Visalia directly, plus the wider Central Valley. "
         "We also work with clients outside California."),
        ("Do you meet in person?",
         "Yes, for local clients. Much of the work is remote by nature, but we travel for "
         "the parts that are better done face to face."),
    ]
    ld = ld_block(
        local_business_ld(url, None, None),
        breadcrumb_ld([("Home", "/"), ("Locations", "/locations")]),
        faq_ld(faqs),
    )
    # Deliberately NOT .ra-service-proof: these are navigation cards, not client
    # proof, and the responsive-spacing contract requires every proof card to
    # carry a 16:9 image. Reusing the proof class here would be a false claim in
    # the markup as well as a failing check.
    cards = "\n".join(
        f'''      <a class="ra-loc-card fade-up fade-up-d{i+1}" href="/locations/{c["slug"]}">
        <span>Location</span>
        <strong>{esc(c["full"])}</strong>
        <p>{esc(c["intro"])}</p>
      </a>''' for i, c in enumerate(CITIES)
    )
    body = (
        hero("Locations", "Where We Work",
             "Revelation Agency is based in Clovis and works across the Central Valley.",
             "/services", "See all services")
        + f'''
<section class="p-section">
  <div class="container">
    <div class="ra-loc-grid">
{cards}
    </div>
  </div>
</section>'''
        + render_faqs(faqs, "Working with us locally.")
        + render_nap()
        + cta("Not sure where to start?",
              "Tell us what you are trying to improve. We will ask a few direct questions and "
              "be honest about fit.")
    )
    write(REPO / "locations" / "index.html", head, body, foot_t, ld)
    return "/locations"


def main() -> int:
    head_t, _body_t, foot_t = load_template()
    routes = [build_index(head_t, foot_t)]
    for city in CITIES:
        routes.append(build_city_hub(city, head_t, foot_t))
        for svc in SERVICES:
            routes.append(build_service_city(city, svc, head_t, foot_t))
    print(f"wrote {len(routes)} pages")
    out = REPO / "artifacts" / "local-seo-routes.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"count": len(routes), "routes": sorted(routes)}, indent=2) + "\n",
                   encoding="utf-8")
    print(f"route manifest -> {out.relative_to(REPO)}")
    for r in sorted(routes):
        print("  ", r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
