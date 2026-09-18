#!/usr/bin/env python3
"""Build the local-SEO geo architecture for revelationagency.com.

The site needs dedicated, useful pages for people comparing agencies in each
Central Valley market. This builder keeps those pages truthful, distinct and
connected to the canonical service pages and relevant client work.

Emits, from the canonical service-leaf template:

    /locations                          location index
    /locations/<city>                   city hub          (one per CITIES row)
    /locations/<city>/<service>         service x city    (CITIES x SERVICES)

Every page carries ProfessionalService + WebPage/Service + BreadcrumbList +
FAQPage JSON-LD.
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
             "Website and search architecture for a Clovis sign manufacturer serving the Central Valley."),
            ("net-metering-systems", "Net Metering Systems",
             "Website, local service pages, and search structure for a Central Valley solar installer."),
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
             "Website, local service pages, and search structure for a Fresno-area solar company."),
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
             "Timing depends on the starting site, competition, content, authority, and Google's "
             "crawl and indexing cycles. We report what changed and what the search data shows; "
             "we do not promise a specific rank by a specific date."),
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
            "Madera businesses often compete for customers across city lines, so a useful local "
            "presence has to explain both the service and the actual area served. Clear pages, "
            "consistent business information, and credible local proof give searchers enough "
            "information to choose the next step."
        ),
        "proof": [
            ("net-metering-systems", "Net Metering Systems",
             "Local service architecture for a solar company serving Madera and nearby Valley communities."),
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
             "It can be when local customers search before they call. We validate the opportunity "
             "with search demand, current visibility, competition, and the value of a qualified lead."),
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
            "Visalia has a strong independent business community. The opportunity for many local "
            "companies is a clear digital presence that matches the quality of the operation and "
            "answers the questions customers ask before they call."
        ),
        "proof": [
            ("net-metering-systems", "Net Metering Systems",
             "Local service architecture for a solar company serving Visalia and the southern Valley."),
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


# Service detail is shared only where the underlying work is genuinely the
# same. The market copy below is written separately for Fresno and Clovis so
# the priority pages answer local buyer questions instead of swapping a city
# name into one generic paragraph.
SERVICE_CONTENT = {
    "branding": {
        "title_noun": "Branding Agency",
        "h1_noun": "Branding Agency",
        "summary": "Positioning, messaging, visual identity, and practical brand rules for businesses that have outgrown an improvised look.",
        "deliverables": [
            ("Positioning and message", "Clarify who the business serves, why it is different, and what customers should remember."),
            ("Visual identity", "Build or refine the logo, color, typography, and supporting visual system."),
            ("Brand standards", "Document the rules so the website, signs, sales material, social content, and ads stay consistent."),
            ("Launch support", "Carry the approved identity into the customer-facing places that matter first."),
        ],
        "process": [
            ("Find the real position", "We interview the people closest to the customer and review the market before drawing anything."),
            ("Build the system", "We develop the verbal and visual identity together so the brand says one coherent thing."),
            ("Apply it", "We turn the approved direction into usable assets and standards, then help launch it consistently."),
        ],
    },
    "web-design": {
        "title_noun": "Web Design Company",
        "h1_noun": "Web Design Company",
        "summary": "Strategy, copy, design, development, local search foundations, analytics, and conversion paths in one website engagement.",
        "deliverables": [
            ("Site strategy", "Map the services, customer questions, locations, and calls to action before design begins."),
            ("Copy and design", "Write and design pages that make the offer easy to understand on phones and desktops."),
            ("Development", "Build a fast, secure, accessible site with clean technical search foundations."),
            ("Measurement", "Connect analytics and conversion tracking so future decisions can use real behavior."),
        ],
        "process": [
            ("Plan", "We inventory the current site, search demand, proof, offers, and customer journey."),
            ("Create", "Copy, design, and development move together so the page structure supports the message."),
            ("Launch and learn", "We verify the live site, monitor performance, and improve weak paths with evidence."),
        ],
    },
    "seo": {
        "title_noun": "SEO Company",
        "h1_noun": "SEO Company",
        "summary": "Technical SEO, local search architecture, useful content, structured data, and authority work tied to qualified demand.",
        "deliverables": [
            ("Technical foundation", "Repair crawling, indexing, canonical, performance, mobile, sitemap, and structured-data issues."),
            ("Local search pages", "Build useful service and location pages around the way nearby customers actually search."),
            ("Content and internal links", "Answer commercial and informational questions, then connect each answer to the right service."),
            ("Measurement", "Track queries, pages, leads, and priority positions so the plan follows evidence instead of guesses."),
        ],
        "process": [
            ("Audit the opportunity", "We compare current visibility, site quality, search intent, competitors, and conversion value."),
            ("Fix the foundation", "We resolve technical blockers and strengthen the pages closest to revenue first."),
            ("Build authority", "We publish helpful resources, improve local proof, and pursue relevant citations and links."),
        ],
    },
    "google-ads": {
        "title_noun": "Google Ads Agency",
        "h1_noun": "Google Ads Agency",
        "summary": "Search campaigns, landing pages, conversion tracking, and ongoing optimization built around qualified calls and leads.",
        "deliverables": [
            ("Intent-led campaigns", "Organize search terms, ads, locations, and negatives around the services worth buying traffic for."),
            ("Conversion-ready pages", "Send each campaign to a focused page that matches the promise in the ad."),
            ("Reliable tracking", "Measure calls, forms, booked appointments, and the actions that represent a real opportunity."),
            ("Ongoing optimization", "Shift budget using search terms, lead quality, conversion cost, and sales feedback."),
        ],
        "process": [
            ("Confirm the economics", "We review the offer, margin, close rate, service area, and follow-up before setting a budget."),
            ("Build the path", "Campaign, ad, landing page, tracking, and lead handoff are configured as one journey."),
            ("Improve with lead quality", "We use real inquiries and sales feedback to reduce waste and expand what works."),
        ],
    },
    "social-media": {
        "title_noun": "Social Media Marketing Agency",
        "h1_noun": "Social Media Marketing Agency",
        "summary": "Strategy, production, publishing, and measurement for brands that need a consistent local presence and reusable content.",
        "deliverables": [
            ("Channel strategy", "Choose the audiences, topics, formats, and publishing rhythm each channel can support."),
            ("Content production", "Create photography, video, graphics, and copy from a planned production system."),
            ("Publishing and response", "Schedule approved content and define how comments, questions, and leads move to the right person."),
            ("Performance review", "Measure reach, engagement, traffic, and inquiries, then refine the content mix."),
        ],
        "process": [
            ("Set the role", "We decide what social should do in the larger marketing and sales system."),
            ("Create in batches", "Planned production days create a dependable library without interrupting the business every week."),
            ("Publish and learn", "We review audience response and business outcomes, then adjust topics and formats."),
        ],
    },
    "video-production": {
        "title_noun": "Video Production Company",
        "h1_noun": "Video Production Company",
        "summary": "Strategy, scripting, production, editing, and distribution planning for video that supports sales, recruiting, ads, and the website.",
        "deliverables": [
            ("Pre-production", "Define the audience, job of the video, story, interviews, locations, schedule, and shot plan."),
            ("Production", "Capture interviews, customer stories, operations, team, products, and supporting footage on location."),
            ("Post-production", "Edit the core story, sound, color, graphics, captions, and approved format variations."),
            ("Content system", "Plan where each asset belongs across the site, social channels, ads, recruiting, and sales follow-up."),
        ],
        "process": [
            ("Choose the story", "We begin with the audience and decision the video must support."),
            ("Plan the shoot", "A clear schedule and shot plan protects production time and captures the needed material."),
            ("Build the library", "We deliver the primary edit and practical cutdowns so one shoot can work in more than one place."),
        ],
    },
}


LOCAL_MARKET_COPY = {
    ("fresno-ca", "branding"): (
        "Fresno Branding for Established Local Businesses",
        "Fresno companies compete across agriculture, construction, healthcare, professional services, retail, and home services. A useful brand has to be recognizable in that crowded mix and practical enough to work on a truck, sign, proposal, website, uniform, and phone screen.",
        "This work fits a Fresno business preparing for growth, a leadership transition, a new location, or a website rebuild when the current identity no longer represents the quality of the company."
    ),
    ("fresno-ca", "web-design"): (
        "Web Design Built Around Fresno Search and Sales",
        "Fresno customers often compare several local providers before they call. The website has to state the service, service area, proof, process, and next step quickly, while giving Google a clear page for each important offering rather than forcing every query onto the homepage.",
        "This work fits Fresno service companies, professional firms, manufacturers, contractors, and regional brands whose current site is slow, difficult to update, unclear, or unable to show which marketing creates inquiries."
    ),
    ("fresno-ca", "seo"): (
        "Local SEO for the Fresno Searches That Lead to Business",
        "Fresno search results mix established local companies, directories, map listings, and firms publishing a separate page for every service. Competing requires more than repeating a city name. The site needs complete service pages, local proof, consistent business data, sound technical structure, and useful answers connected by internal links.",
        "This work fits a Fresno-area business with proven services and capacity to serve more customers. We prioritize terms that show buying intent, then build supporting answers around the questions people ask before choosing a provider."
    ),
    ("fresno-ca", "google-ads"): (
        "Paid Search for Fresno Service Areas",
        "Fresno campaigns can waste money when broad searches, out-of-area clicks, and weak landing pages are left unchecked. We separate services and locations, use negative keywords, match each ad to a relevant page, and connect tracking to the inquiries the team can actually work.",
        "This work fits Fresno businesses that know the value of a qualified lead, can respond promptly, and have an offer with enough margin to support paid acquisition."
    ),
    ("fresno-ca", "social-media"): (
        "Social Content That Makes a Fresno Business Familiar",
        "Local buyers notice the people, work, customers, and community behind a company. A planned content library can show that proof consistently across Instagram, Facebook, LinkedIn, YouTube, and short-form video without making the team invent a post every morning.",
        "This work fits Fresno organizations with real stories, active teams, projects, customers, or expertise that are not yet visible online."
    ),
    ("fresno-ca", "video-production"): (
        "Fresno Video Production With a Distribution Plan",
        "A strong production day can create a company story, customer proof, recruiting material, website footage, ad creative, and short social edits. Planning those uses before the cameras arrive makes the investment more useful and keeps the finished footage from sitting in one post.",
        "This work fits Fresno companies that need to explain a complex service, show the quality of their work, recruit people, document a customer story, or build a dependable content library."
    ),
    ("clovis-ca", "branding"): (
        "Brand Strategy and Identity From Our Clovis Office",
        "Clovis is where Revelation Agency works every day. We see local companies grow from referrals into regional operations, and the brand often falls behind the business. We build an identity that keeps the trust already earned while making the company easier to recognize and explain.",
        "This work fits a Clovis business whose logo, message, site, signs, and sales material no longer feel like one company. In-person working sessions are available at our Shaw Avenue office."
    ),
    ("clovis-ca", "web-design"): (
        "Clovis Web Design With Local Access",
        "A Clovis website should make the business easy to understand for nearby customers and credible to buyers across the Valley. We organize services, locations, proof, and calls to action into a site that works on a phone, loads quickly, and gives every important offer a clear place to rank.",
        "This work fits Clovis companies that want direct access to the team building the site and a process that includes strategy, copy, design, development, local search, and measurement."
    ),
    ("clovis-ca", "seo"): (
        "Local SEO Managed in Clovis",
        "Clovis businesses often serve customers in Fresno and across the Central Valley, but the site still has to prove the local connection clearly. We connect the verified Clovis address, services, customer proof, location coverage, technical structure, and Google Business Profile rather than relying on a city name in a title tag.",
        "This work fits a Clovis business ready to improve the site, publish useful material, earn legitimate local mentions, and measure inquiries over time. Meetings are available at our local office."
    ),
    ("clovis-ca", "google-ads"): (
        "Google Ads Management From Clovis",
        "Local paid search works best when location targeting, search terms, landing pages, call tracking, and follow-up all agree. We build those pieces together from our Clovis office and review the actual quality of inquiries, not only the number of clicks recorded by the ad platform.",
        "This work fits Clovis companies with a clear service area, responsive sales process, and enough lead value to learn from a controlled campaign."
    ),
    ("clovis-ca", "social-media"): (
        "Social Media Production for Clovis Brands",
        "Clovis customers respond to recognizable people, places, work, and community involvement. We turn those real inputs into a consistent content plan, with local production available for interviews, project footage, photography, and customer stories.",
        "This work fits Clovis businesses that have a strong operation and want their online presence to show the same care customers see in person."
    ),
    ("clovis-ca", "video-production"): (
        "Clovis Video Production, Planned for Reuse",
        "Our Clovis location gives local teams a nearby production partner for interviews, company stories, customer testimonials, recruiting films, ads, and website footage. We plan the distribution before the shoot so the footage can support more than one channel.",
        "This work fits Clovis organizations that want a clear production process, local coordination, and a practical library of finished video assets."
    ),
}


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


def webpage_ld(page_url: str, title: str, desc: str, page_type: str = "WebPage") -> dict:
    return {
        "@context": "https://schema.org",
        "@type": page_type,
        "@id": page_url + "/#webpage",
        "url": page_url,
        "name": title,
        "description": desc,
        "dateModified": "2026-09-17",
        "isPartOf": {"@id": CANON + "/#website"},
        "about": {"@id": CANON + "/#organization"},
        "inLanguage": "en-US",
    }


def service_ld(page_url: str, service_name: str, description: str, city: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": page_url + "/#service",
        "name": f"{service_name} in {city['full']}",
        "serviceType": service_name,
        "description": description,
        "url": page_url,
        "provider": {"@id": CANON + "/#organization"},
        "areaServed": {"@type": "City", "name": city["full"]},
        "availableChannel": {
            "@type": "ServiceChannel",
            "serviceUrl": page_url,
            "servicePhone": NAP["phone"],
        },
    }


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
    title = f"{city['name']} Marketing Agency | Revelation Agency"
    desc = (f"Marketing agency serving {city['full']}. Branding, web design, SEO, Google Ads, "
            f"social, and video built as one system. Based in Clovis.")
    head = set_head(head_t, title=title, desc=desc, url=url)
    ld = ld_block(
        local_business_ld(url, city["full"], None),
        webpage_ld(url, title, desc, "CollectionPage"),
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
    detail = SERVICE_CONTENT[s_slug]
    title_noun = detail["title_noun"]
    display_label = label if label in {"SEO", "Google Ads"} else label.lower()
    local_heading, local_copy, fit_copy = LOCAL_MARKET_COPY.get(
        (city["slug"], s_slug),
        (
            f"{title_noun} for {city['name']} Businesses",
            city["context"],
            f"This work fits {city['name']} businesses that need a clearer, more measurable approach to {display_label}.",
        ),
    )
    url = f"{CANON}/locations/{city['slug']}/{s_slug}"
    title = f"{city['name']} {title_noun} | Revelation Agency"
    desc = f"{title_noun} serving {city['full']}. {detail['summary']} Talk with our Clovis-based team."
    head = set_head(head_t, title=title, desc=desc, url=url)
    head = re.sub(
        r'<body data-ra-service="[^"]+" data-ra-visual="[^"]+">',
        f'<body data-ra-service="local-{s_slug}" data-ra-visual="{s_slug}">',
        head,
        count=1,
    )
    faqs = [
        (f"Does Revelation Agency provide {label} in {city['name']}?",
         f"Yes. Revelation Agency is based at {NAP['street']} in Clovis and serves businesses "
         f"throughout {city['full']} and the Central Valley. The engagement is scoped around "
         "the business, service area, customer journey, and measurable goal."),
        (f"What is included in {label}?",
         detail["summary"] + " The exact deliverables are documented before work begins."),
        (f"How does {label} connect to the rest of our marketing?",
         "We review the brand, website, traffic sources, conversion path, and follow-up around it. "
         "If another constraint should be fixed first, we explain that during scoping."),
        (f"What does {label} cost in {city['name']}?",
         "Scope, complexity, existing assets, and the amount of production required determine the price. "
         "After discovery, we provide a written scope that explains the work and the intended outcome."),
        (f"Can we meet your team in person?",
         f"Yes. Local meetings are available at our office at {NAP['street']}, Clovis, CA {NAP['zip']}, "
         "and we travel for production or working sessions when the engagement calls for it."),
    ]
    ld = ld_block(
        local_business_ld(url, city["full"], h1_noun),
        webpage_ld(url, title, desc),
        service_ld(url, title_noun, detail["summary"], city),
        breadcrumb_ld([("Home", "/"), ("Locations", "/locations"),
                       (city["full"], f"/locations/{city['slug']}"),
                       (h1_noun, f"/locations/{city['slug']}/{s_slug}")]),
        faq_ld(faqs),
    )
    others = "\n".join(
        f'      <li><a href="/locations/{city["slug"]}/{o_slug}">{esc(o_noun)} in {esc(city["name"])}</a></li>'
        for o_slug, _l, o_noun, _p, _lf in SERVICES if o_slug != s_slug
    )
    deliverables = "\n".join(
        f'''      <li><strong>{esc(name)}</strong><span>{esc(copy)}</span></li>'''
        for name, copy in detail["deliverables"]
    )
    process = "\n".join(
        f'''      <li><span class="ra-local-step">{i}</span><div><strong>{esc(name)}</strong><p>{esc(copy)}</p></div></li>'''
        for i, (name, copy) in enumerate(detail["process"], 1)
    )
    body = (
        hero(f"{label} · {city['full']}", f"{title_noun} in {city['headline']}", detail["summary"],
             f"/locations/{city['slug']}", f"All services in {city['name']}")
        + f'''
<section class="p-section ra-service-intro">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">Local Strategy</div>
      <h2>{esc(local_heading)}</h2>
      <p class="lead">{esc(local_copy)}</p>
      <p>{esc(fit_copy)}</p>
      <p><a href="{leaf}">See our complete {esc(display_label)} approach →</a></p>
    </div>
  </div>
</section>

<section class="p-section p-section--grey">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">What We Handle</div>
      <h2>A complete {esc(display_label)} engagement.</h2>
      <p class="lead">The scope is built around the constraint that is limiting growth, with the work defined before production starts.</p>
    </div>
    <ul class="ra-local-detail-grid fade-up">
{deliverables}
    </ul>
  </div>
</section>

<section class="p-section">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">How It Works</div>
      <h2>From diagnosis to a working system.</h2>
    </div>
    <ol class="ra-local-process fade-up">
{process}
    </ol>
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
        webpage_ld(url, title, desc, "CollectionPage"),
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


def add_local_links_to_service_pages() -> int:
    """Give every canonical service page direct links to the priority local pages."""
    start = "<!-- RA-LOCAL-SERVICE-LINKS-START -->"
    end = "<!-- RA-LOCAL-SERVICE-LINKS-END -->"
    changed = 0
    for s_slug, label, _noun, _promise, leaf in SERVICES:
        path = REPO / (leaf.lstrip("/") + ".html")
        if not path.exists():
            raise FileNotFoundError(f"canonical service page missing: {path}")
        cards = "\n".join(
            f'''      <div class="fade-up fade-up-d{i}">
        <div class="eyebrow">{esc(city["name"])} Service</div>
        <h3><a href="/locations/{city["slug"]}/{s_slug}">{esc(city["name"])} {esc(label)}</a></h3>
        <p>See the local approach, scope, process, proof, and common questions for {esc(city["name"])} businesses.</p>
      </div>'''
            for i, city in enumerate(CITIES[:2], 1)
        )
        block = f'''{start}
<section class="p-section p-section--grey" aria-labelledby="local-{s_slug}-heading">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">Local Service Areas</div>
      <h2 id="local-{s_slug}-heading">{esc(label)} in Fresno and Clovis.</h2>
      <p class="lead">Meet with our Clovis-based team and see how this service applies in each local market.</p>
    </div>
    <div class="p-two">
{cards}
    </div>
  </div>
</section>
{end}'''
        raw = path.read_text(encoding="utf-8")
        if start in raw:
            new = re.sub(re.escape(start) + r".*?" + re.escape(end), block, raw, count=1, flags=re.S)
        else:
            marker = '<section class="p-cta">'
            if marker not in raw:
                raise ValueError(f"CTA marker missing in {path}")
            new = raw.replace(marker, block + "\n\n" + marker, 1)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
    return changed


def write_llms_txt() -> None:
    content = """# Revelation Agency

> Revelation Agency is a Clovis, California marketing agency serving Fresno and the Central Valley with branding, web design, SEO, Google Ads, social media, video production, CRM, automation, and sales infrastructure.

## Local marketing services

- [Clovis Marketing Agency](https://www.revelationagency.com/locations/clovis-ca): Local agency overview, services, proof, questions, and office information.
- [Fresno Marketing Agency](https://www.revelationagency.com/locations/fresno-ca): Marketing services for Fresno businesses from the nearby Clovis office.
- [Clovis SEO Company](https://www.revelationagency.com/locations/clovis-ca/seo): Technical, local, content, and AI-search optimization for Clovis businesses.
- [Fresno SEO Company](https://www.revelationagency.com/locations/fresno-ca/seo): SEO strategy and execution for Fresno businesses.
- [Clovis Web Design Company](https://www.revelationagency.com/locations/clovis-ca/web-design): Website strategy, copy, design, development, and measurement.
- [Fresno Web Design Company](https://www.revelationagency.com/locations/fresno-ca/web-design): Conversion-focused website design and development for Fresno businesses.
- [Clovis Google Ads Agency](https://www.revelationagency.com/locations/clovis-ca/google-ads): Paid search, landing pages, tracking, and optimization.
- [Fresno Google Ads Agency](https://www.revelationagency.com/locations/fresno-ca/google-ads): Google Ads management for qualified Fresno-area demand.

## Core services

- [Services](https://www.revelationagency.com/services): Complete service directory.
- [Brand Strategy and Identity](https://www.revelationagency.com/services/branding/brand-strategy-identity): Positioning, messaging, identity, and standards.
- [Websites and Landing Pages](https://www.revelationagency.com/services/branding/websites-landing-pages): Strategy, copy, design, development, and conversion paths.
- [SEO and AI Visibility](https://www.revelationagency.com/services/marketing/seo-ai-visibility): Search and answer-engine visibility.
- [Digital Ads](https://www.revelationagency.com/services/marketing/digital-ads): Paid search and paid social campaigns.
- [Social Media](https://www.revelationagency.com/services/marketing/social-media): Social strategy, production, publishing, and measurement.
- [Video and Visual Content](https://www.revelationagency.com/services/branding/video-visual-content): Video planning, production, editing, and reuse.

## Evidence and company information

- [Case Studies](https://www.revelationagency.com/portfolio/case-studies): Selected client engagements and delivered work.
- [About Revelation Agency](https://www.revelationagency.com/about): Company approach and team.
- [Contact](https://www.revelationagency.com/contact): Office and contact information.
- [Book a Conversation](https://www.revelationagency.com/booking): Request a discovery conversation.

## Business details

- Address: 55 Shaw Ave #201, Clovis, CA 93612
- Phone: (559) 201-7039
- Email: connect@revelationagency.com
- Primary service area: Clovis, Fresno, Madera, Visalia, and the Central Valley
"""
    (REPO / "llms.txt").write_text(content, encoding="utf-8")


def main() -> int:
    head_t, _body_t, foot_t = load_template()
    routes = [build_index(head_t, foot_t)]
    for city in CITIES:
        routes.append(build_city_hub(city, head_t, foot_t))
        for svc in SERVICES:
            routes.append(build_service_city(city, svc, head_t, foot_t))
    linked = add_local_links_to_service_pages()
    write_llms_txt()
    print(f"wrote {len(routes)} pages")
    print(f"updated {linked} canonical service pages with local links")
    print("wrote llms.txt")
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
