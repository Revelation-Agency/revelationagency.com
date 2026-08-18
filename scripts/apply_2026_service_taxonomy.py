#!/usr/bin/env python3
"""Build the clear 2026 Branding / Marketing / Sales service architecture.

The user-facing contract is intentionally plain: five Branding services, four
Marketing services, and four Sales services.  Existing equity-bearing file
paths are retained when possible; redirects are owned by the route generator.
This script only authors canonical service HTML and the main services overview.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANON = "https://www.revelationagency.com"


PROJECTS = {
    "ams-energy-solutions": ("AMS Energy Solutions", "Brand identity, website, and visual system."),
    "highlands-energy": ("Highlands Energy", "Video, lead gen ads, CRM, and sales operations."),
    "infinite-roofing-solutions": ("Infinite Roofing Solutions", "Website, video, advertising, and CRM delivery."),
    "ivory-pools": ("Ivory Pool Services", "Brand identity, website, design, signage, and bilingual video."),
    "life-os": ("Life OS", "A custom AI-enabled digital product."),
    "net-metering-systems": ("Net Metering Systems", "Website, content, SEO, paid media, CRM, and automation."),
    "plan-grow-lead": ("Plan Grow Lead", "Brand identity and a focused conversion website."),
    "reservwise": ("ReservWise", "Brand, app, website, CRM, and automation system."),
    "revelation-portal": ("Revelation Portal", "A purpose-built operations and sales platform."),
    "risen-sun-solar-roofing": ("Risen Sun Solar & Roofing", "Brand, website, customer nurture, lead gen ads, CRM, and automation."),
    "the-whole-vine": ("The Whole Vine Festival", "Website, social media, video, and campaign delivery."),
    "trust-energy": ("Trust Energy", "Brand, video, social, paid media, CRM, and sales tools."),
    "wealth-coach-360": ("Wealth Coach 360", "Brand, app, website, nurture, CRM, and automation."),
}


SERVICES = [
    {
        "code": "B1", "pillar": "Branding", "slug": "websites-landing-pages", "title": "Websites",
        "dek": "Clear, fast websites that explain what you do and turn visits into action.",
        "intro": "We plan, write, design, and build websites and landing pages around the questions real customers ask. The result is easy to understand, easy to use on a phone, and ready to support search, advertising, and sales.",
        "scope": ["Website strategy and page planning", "Copywriting and conversion-focused design", "Custom development and mobile optimization", "Landing pages for campaigns and offers", "Analytics, forms, search foundations, and launch support"],
        "method": ["Plain-language messaging before visual polish", "Fast, accessible pages with clear next steps", "Ownership, hosting, and handoff terms stated up front", "Built to connect with your CRM and marketing tools"],
        "proof": ["ivory-pools", "net-metering-systems", "infinite-roofing-solutions"],
    },
    {
        "code": "B2", "pillar": "Branding", "slug": "apps-digital-products", "title": "Apps",
        "dek": "Custom apps, portals, and digital tools built around the way your business actually works.",
        "intro": "When a website is not enough, we design and build focused software for customers, staff, and sales teams. We keep the experience simple, the permissions clear, and the product maintainable.",
        "scope": ["Customer and employee portals", "Operational dashboards and internal tools", "Mobile-friendly web applications", "Product design, prototyping, and development", "Integrations, permissions, reporting, and launch support"],
        "method": ["Start with the job the tool must do", "Prototype the high-risk decisions first", "Build in small, testable releases", "Document ownership, maintenance, and rollback"],
        "proof": ["life-os", "reservwise", "revelation-portal"],
    },
    {
        "code": "B3", "pillar": "Branding", "slug": "brand-strategy-identity", "title": "Brand Identity",
        "dek": "A clear identity people recognize, remember, and trust.",
        "intro": "We shape the story, logo, color, typography, and rules that make your company look and sound consistent. The system is built to work everywhere—from a phone screen to a truck, sign, proposal, or video.",
        "scope": ["Positioning and brand story", "Logo and supporting marks", "Color, typography, and visual direction", "Voice and messaging foundations", "Practical brand guidelines and source files"],
        "method": ["Understand the business before drawing the mark", "Present focused directions with clear reasoning", "Test the identity in real-world applications", "Deliver usable rules, files, and ownership"],
        "proof": ["ams-energy-solutions", "ivory-pools", "trust-energy"],
    },
    {
        "code": "B4", "pillar": "Branding", "slug": "design", "title": "Design",
        "dek": "Professional design for the materials your customers and team see every day.",
        "intro": "We turn your brand into useful, polished materials: presentations, proposals, campaign creative, signs, print pieces, social templates, apparel, and more. Every piece follows one visual system instead of becoming another one-off.",
        "scope": ["Sales decks, proposals, and presentations", "Print, signage, apparel, and event materials", "Campaign and advertising creative", "Social templates and content graphics", "Reusable design systems and production files"],
        "method": ["Design around the audience and use case", "Keep hierarchy and calls to action obvious", "Create repeatable templates where they save time", "Deliver production-ready files in the right formats"],
        "proof": ["ivory-pools", "ams-energy-solutions", "infinite-roofing-solutions"],
    },
    {
        "code": "B5", "pillar": "Branding", "slug": "video-visual-content", "title": "Video",
        "dek": "Video that makes the business easier to understand and the brand harder to forget.",
        "intro": "We plan, direct, film, and edit brand, customer, educational, and campaign video. Each production is designed for the places it will actually be used—your website, social channels, advertising, sales process, and training.",
        "scope": ["Brand and company story videos", "Customer stories and testimonials", "Educational and social video", "Advertising creative and short-form cuts", "Planning, production, editing, and distribution formats"],
        "method": ["Define the business job before the shot list", "Capture multiple useful assets in each production", "Edit for the platform and attention window", "Organize footage so it can keep compounding"],
        "proof": ["net-metering-systems", "trust-energy", "the-whole-vine"],
    },
    {
        "code": "M1", "pillar": "Marketing", "slug": "seo-ai-visibility", "title": "SEO / AI Answers",
        "dek": "Help customers find you in search results and in AI-generated answers.",
        "intro": "We improve the technical structure, pages, content, and proof that help search engines and AI answer tools understand your business. The goal is not jargon or traffic for its own sake—it is qualified discovery.",
        "scope": ["Technical and on-page SEO", "Local search and service-area visibility", "Content built around customer questions", "Structured data and answer-engine readiness", "Measurement, reporting, and ongoing priorities"],
        "method": ["Start with how customers actually search", "Fix technical blockers before adding volume", "Publish clear, useful, citable answers", "Measure qualified actions, not vanity rankings"],
        "proof": ["net-metering-systems", "highlands-energy", "infinite-roofing-solutions"],
    },
    {
        "code": "M2", "pillar": "Marketing", "slug": "social-media", "title": "Social Media",
        "dek": "Consistent social content that builds familiarity, trust, and demand.",
        "intro": "We plan the content, capture the material, produce the posts, and manage the publishing rhythm. The work is tied to a clear audience and business objective—not posting simply to stay busy.",
        "scope": ["Channel and content strategy", "Content capture, writing, design, and editing", "Publishing and community support", "Short-form video and campaign content", "Reporting tied to useful business signals"],
        "method": ["Choose channels based on the audience", "Build repeatable content pillars", "Turn one production into many useful pieces", "Review what creates attention, trust, and action"],
        "proof": ["net-metering-systems", "trust-energy", "the-whole-vine"],
    },
    {
        "code": "M3", "pillar": "Marketing", "slug": "digital-ads", "title": "Digital Advertising",
        "dek": "Paid campaigns with clear creative, targeting, budgets, and measurement.",
        "intro": "We plan and manage advertising across the platforms your audience uses. Digital Advertising owns the media strategy, campaign creative, traffic, and optimization; when the goal is captured sales leads, it connects directly to our Lead Gen Ads work.",
        "scope": ["Campaign strategy and media planning", "Google, Meta, and platform management", "Audience, offer, and creative testing", "Budget pacing and conversion measurement", "Landing-page and analytics coordination"],
        "method": ["Agree on the objective before spending", "Match creative and offer to audience intent", "Test controlled variables instead of guessing", "Report what happened and what changes next"],
        "proof": ["net-metering-systems", "infinite-roofing-solutions", "trust-energy"],
    },
    {
        "code": "M4", "pillar": "Marketing", "slug": "email-lifecycle-marketing", "title": "Customer Nurture",
        "dek": "Email and text follow-up that helps more prospects and customers take the next step.",
        "intro": "We build useful, human follow-up across the customer journey—from the first inquiry through education, reminders, reactivation, and long-term loyalty. Every sequence has a clear purpose and a clear handoff.",
        "scope": ["Email and SMS nurture sequences", "Lead education and appointment reminders", "Customer onboarding and retention communication", "Reactivation and referral campaigns", "Segmentation, measurement, and CRM coordination"],
        "method": ["Map the questions people have at each stage", "Write like a helpful person, not a robot", "Use timing and segmentation with restraint", "Measure replies, appointments, and progression"],
        "proof": ["wealth-coach-360", "risen-sun-solar-roofing", "net-metering-systems"],
    },
    {
        "code": "S1", "pillar": "Sales", "slug": "lead-generation-outreach", "title": "Outreach",
        "dek": "Focused outbound campaigns that start real conversations with the right prospects.",
        "intro": "We help define the audience, build the list, shape the offer, and run personalized outreach. The work is designed to create credible conversations—not spray generic messages across the internet.",
        "scope": ["Audience definition and prospect research", "List building and data preparation", "Email, phone, and multi-channel outreach", "Messaging, scripts, and offer testing", "Reply handling, qualification, and CRM handoff"],
        "method": ["Prioritize fit over list size", "Personalize around a real business reason", "Protect reputation and follow platform rules", "Route every useful response to an owner"],
        # No published case currently proves Revelation directly performed
        # outbound prospecting. Keep this empty rather than relabel inbound or
        # paid-lead work as Outreach.
        "proof": [],
    },
    {
        "code": "S2", "pillar": "Sales", "slug": "lead-gen-ads", "title": "Lead Gen Ads",
        "dek": "Advertising built to capture, qualify, and route sales leads.",
        "intro": "Lead Gen Ads connect paid media to a clear offer, a simple form or landing page, immediate routing, and visible pipeline follow-up. The goal is not just clicks—it is giving your sales team the right opportunities quickly.",
        "scope": ["Lead offer and campaign planning", "Lead forms and landing pages", "Qualification questions and routing rules", "CRM connection and rapid-response workflows", "Pipeline reporting from lead to sales outcome"],
        "method": ["Define a qualified lead before launch", "Reduce friction without lowering intent", "Notify and route leads immediately", "Review cost, quality, speed, and pipeline movement together"],
        "proof": ["net-metering-systems", "trust-energy", "infinite-roofing-solutions"],
    },
    {
        "code": "S3", "pillar": "Sales", "slug": "crm-sales-infrastructure", "title": "CRMs / Sales Tools",
        "dek": "A practical sales system your team can see, use, and manage.",
        "intro": "We configure CRMs, pipelines, forms, dashboards, calendars, and integrations around the way your team sells. The system gives every lead an owner, every deal a next step, and leadership a clear view of what is happening.",
        "scope": ["CRM selection, setup, and cleanup", "Pipelines, stages, ownership, and tasks", "Forms, calendars, dashboards, and reporting", "Integrations with websites and marketing tools", "Team training, documentation, and governance"],
        "method": ["Fit the tool to the sales process", "Keep required fields and stages understandable", "Automate repetitive work without hiding ownership", "Make reporting useful to the people running the business"],
        "proof": ["reservwise", "net-metering-systems", "revelation-portal"],
    },
    {
        "code": "S4", "pillar": "Sales", "slug": "ai-automation-systems", "title": "AI Automation Systems",
        "dek": "AI and automation that respond faster, move work forward, and keep people in control.",
        "intro": "We build sales-focused automation for lead response, qualification, routing, reminders, updates, and reporting. AI is used where it improves speed or consistency, with clear rules, human handoffs, and visible ownership.",
        "scope": ["AI-assisted lead response and qualification", "Workflow, task, and reminder automation", "Lead routing and pipeline updates", "Sales assistants, knowledge tools, and reporting", "Human approvals, exception handling, and monitoring"],
        "method": ["Automate a proven process, not confusion", "Keep customer-facing behavior clear and supervised", "Make every handoff and exception visible", "Document how to pause, change, and own the system"],
        "proof": ["reservwise", "net-metering-systems", "wealth-coach-360"],
    },
]


PILLAR_COPY = {
    "Branding": {
        "dek": "We make the business clear, recognizable, and professional everywhere customers see it.",
        "why": "Branding is the visible foundation: the identity, website, app, design, and video people use to understand and judge the business.",
        "proof": ["ivory-pools", "ams-energy-solutions", "trust-energy"],
    },
    "Marketing": {
        "dek": "We help the right people find you, understand you, and stay connected.",
        "why": "Marketing creates visibility and demand through search, social media, advertising, and thoughtful customer nurture.",
        "proof": ["net-metering-systems", "the-whole-vine", "trust-energy"],
    },
    "Sales": {
        "dek": "We help you create opportunities, organize the pipeline, and follow through faster.",
        "why": "Sales turns attention into action through outreach, lead generation, practical sales tools, and carefully governed automation.",
        "proof": ["net-metering-systems", "reservwise", "risen-sun-solar-roofing"],
    },
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def clean_route(service: dict[str, object]) -> str:
    return f"/services/{str(service['pillar']).lower()}/{service['slug']}"


def proof_cards(slugs: list[str]) -> str:
    cards = []
    for idx, slug in enumerate(slugs, 1):
        name, description = PROJECTS[slug]
        cards.append(f"""      <a class="ra-service-proof fade-up fade-up-d{min(idx, 3)}" href="/portfolio/case-studies/{slug}">
        <img src="/assets/img/portfolio/{slug}/thumbnail.png" alt="{esc(name)} case study" loading="lazy" width="640" height="420">
        <span>Related work</span>
        <strong>{esc(name)}</strong>
        <p>{esc(description)}</p>
      </a>""")
    return "\n".join(cards)


def list_items(items: list[str]) -> str:
    return "".join(f"<li>{esc(item)}</li>" for item in items)


def render_leaf(service: dict[str, object]) -> str:
    pillar = str(service["pillar"])
    title = str(service["title"])
    proof = list(service["proof"])
    if proof:
        proof_section = f"""<section class="p-section p-section--grey ra-service-proof-section">
  <div class="container">
    <div class="ra-service-proof-heading fade-up"><div class="eyebrow">Related Work</div><h2>See {esc(title)} in real projects.</h2><p class="lead">These are real client engagements. Generated concept art is never presented as client proof.</p></div>
    <div class="ra-service-proof-grid">
{proof_cards(proof)}
    </div>
    <div class="ra-service-proof-more fade-up"><a href="/portfolio" class="btn btn--outline">Explore the full portfolio <i class="fa-solid fa-arrow-right"></i></a></div>
  </div>
</section>"""
    else:
        proof_section = f"""<section class="p-section p-section--grey ra-service-proof-section ra-service-proof-section--pending">
  <div class="container">
    <div class="ra-service-proof-heading fade-up"><div class="eyebrow">Proof Standard</div><h2>We only call direct outreach work Outreach.</h2><p class="lead">Paid advertising, inbound lead handling, and a client&rsquo;s own prospecting are different services. We will publish an Outreach case study here when Revelation directly operates the work and can document it.</p></div>
    <div class="ra-service-proof-more fade-up"><a href="/portfolio/sales" class="btn btn--outline">See related Sales work <i class="fa-solid fa-arrow-right"></i></a></div>
  </div>
</section>"""
    return f"""<section class="p-hero ra-service-hero" data-service-code="{service['code']}">
  <div class="container">
    <div class="p-hero__inner fade-up">
      <div class="eyebrow" style="color:rgba(255,255,255,0.62);">{esc(pillar)} Service</div>
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(str(service['dek']))}</p>
      <div class="p-hero__cta">
        <a href="/booking" class="btn btn--primary" data-cta="primary" data-cta-placement="leaf-hero" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a>
        <a href="/services/{pillar.lower()}" class="btn btn--ghost-dark">See all {esc(pillar)} services</a>
      </div>
    </div>
  </div>
</section>

<section class="p-section ra-service-intro">
  <div class="container">
    <div class="ra-service-intro__lede fade-up">
      <div class="eyebrow">What It Is</div>
      <h2>{esc(title)}, explained plainly.</h2>
      <p class="lead">{esc(str(service['intro']))}</p>
    </div>
    <div class="p-two">
      <div class="fade-up fade-up-d1"><div class="eyebrow">What We Do</div><h2>Included in the work.</h2><ul>{list_items(service['scope'])}</ul></div>
      <div class="fade-up fade-up-d2"><div class="eyebrow">How We Work</div><h2>Clear and accountable.</h2><ul>{list_items(service['method'])}</ul></div>
    </div>
  </div>
</section>

{proof_section}

<section class="p-cta">
  <div class="container fade-up"><h2>Need {esc(title)}?</h2><p>Tell us what you are trying to improve. We will ask a few direct questions, explain the right next step, and be honest about fit.</p><a href="/booking" class="btn btn--white" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a></div>
</section>

"""


def validate_service_proof_assignments() -> None:
    """Fail closed if a service page claims proof its portfolio record lacks."""
    manifest = json.loads((ROOT / "assets/data/portfolio-taxonomy-2026.json").read_text(encoding="utf-8"))
    masters = manifest["masterCardsByRoute"]
    by_slug = {
        route.removeprefix("/portfolio/case-studies/").removesuffix(".html"): record
        for route, record in masters.items()
    }
    issues: list[str] = []
    for service in SERVICES:
        code = str(service["code"])
        for slug in service["proof"]:
            record = by_slug.get(str(slug))
            if not record or code not in record.get("disciplines", []):
                issues.append(f"{code} {service['title']}: unsupported proof {slug}")
    if issues:
        raise ValueError("Service proof must match the portfolio manifest:\n" + "\n".join(issues))


def render_hub(pillar: str) -> str:
    services = [service for service in SERVICES if service["pillar"] == pillar]
    cards = []
    for idx, service in enumerate(services, 1):
        cards.append(f"""      <a class="p-leaf fade-up fade-up-d{min(idx, 3)}" href="{clean_route(service)}">
        <div class="p-leaf__num">{idx:02d} / Service</div>
        <h3>{esc(str(service['title']))}</h3>
        <p>{esc(str(service['dek']))}</p>
        <span class="p-leaf__cta">Explore <i class="fa-solid fa-arrow-right"></i></span>
      </a>""")
    copy = PILLAR_COPY[pillar]
    return f"""<section class="p-hero ra-service-hero ra-service-hero--pillar">
  <div class="container"><div class="p-hero__inner fade-up"><div class="eyebrow" style="color:rgba(255,255,255,0.62);">Services</div><h1>{pillar} Services</h1><p class="lead">{esc(copy['dek'])}</p><div class="p-hero__cta"><a href="/booking" class="btn btn--primary" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a><a href="#services" class="btn btn--ghost-dark">See the Services</a></div></div></div>
</section>

<section class="p-section p-section--grey">
  <div class="container"><div class="ra-service-intro__lede fade-up"><div class="eyebrow">What {pillar} Means Here</div><h2>{pillar}, explained plainly.</h2><p class="lead">{esc(copy['why'])}</p></div></div>
</section>

<section class="p-section" id="services">
  <div class="container"><div class="eyebrow fade-up">{len(services)} Clear Services</div><h2 class="fade-up">Choose the work you need.</h2><p class="lead fade-up">Start with one service or connect several. Each title means exactly what it says.</p><div class="p-leaves">
{chr(10).join(cards)}
    </div></div>
</section>

<section class="p-section p-section--grey ra-service-proof-section">
  <div class="container"><div class="ra-service-proof-heading fade-up"><div class="eyebrow">Selected {pillar} Work</div><h2>Real work, shown clearly.</h2></div><div class="ra-service-proof-grid">
{proof_cards(copy['proof'])}
    </div></div>
</section>

<section class="p-cta"><div class="container fade-up"><h2>Need help choosing?</h2><p>Tell us what is not working. We will identify the clearest starting point and explain why.</p><a href="/booking" class="btn btn--white" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a></div></section>

"""


def metadata(text: str, *, title: str, description: str, route: str) -> str:
    canonical = CANON + route
    replacements = [
        (r"<title>.*?</title>", f"<title>{esc(title)}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(description)}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canonical}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(description)}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canonical}">'),
        (r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{esc(title)}">'),
        (r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{esc(description)}">'),
    ]
    for pattern, replacement in replacements:
        text, count = re.subn(pattern, replacement, text, count=1, flags=re.I | re.S)
        if not count:
            if "</head>" not in text:
                raise ValueError(f"Missing </head> while adding metadata for {route}")
            text = text.replace("</head>", f"  {replacement}\n</head>", 1)
    return text


def canonical_body(text: str, *, pillar: str, slug: str, content: str) -> str:
    text, count = re.subn(
        r'<body\b[^>]*>',
        f'<body data-ra-service="{slug}" data-ra-visual="{pillar.lower()}">',
        text,
        count=1,
        flags=re.I,
    )
    if not count:
        raise ValueError(f"Missing body for {pillar}/{slug}")
    start = text.find('<section class="p-hero')
    end = text.find('<!-- RA-FOOTER-CANONICAL-START -->', start)
    if start < 0 or end < 0:
        raise ValueError(f"Missing service content boundaries for {pillar}/{slug}")
    return text[:start] + content + text[end:]


def write_if_changed(path: Path, text: str) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def build_leaf(service: dict[str, object]) -> bool:
    pillar = str(service["pillar"])
    path = ROOT / "services" / pillar.lower() / f"{service['slug']}.html"
    source_by_pillar = {
        "Branding": ROOT / "services/branding/brand-strategy-identity.html",
        "Marketing": ROOT / "services/marketing/seo-ai-visibility.html",
        "Sales": ROOT / "services/sales/crm-sales-infrastructure.html",
    }
    if path.exists():
        candidate = path.read_text(encoding="utf-8")
        text = candidate if '<section class="p-hero' in candidate else source_by_pillar[pillar].read_text(encoding="utf-8")
    else:
        text = source_by_pillar[pillar].read_text(encoding="utf-8")
    route = clean_route(service)
    title = f"{service['title']} | {pillar} Services | Revelation Agency"
    text = metadata(text, title=title, description=str(service["dek"]), route=route)
    text = canonical_body(text, pillar=pillar, slug=str(service["slug"]), content=render_leaf(service))
    return write_if_changed(path, text)


def build_hub(pillar: str) -> bool:
    path = ROOT / "services" / pillar.lower() / "index.html"
    text = path.read_text(encoding="utf-8")
    copy = PILLAR_COPY[pillar]
    route = f"/services/{pillar.lower()}"
    text = metadata(
        text,
        title=f"{pillar} Services | Revelation Agency",
        description=copy["dek"],
        route=route,
    )
    text = canonical_body(text, pillar=pillar, slug=f"{pillar.lower()}-services", content=render_hub(pillar))
    return write_if_changed(path, text)


def stack(pillar: str) -> str:
    services = [s for s in SERVICES if s["pillar"] == pillar]
    items = "".join(
        f'<li><a href="{clean_route(s)}"><i class="fa-solid fa-chevron-right"></i><span>{esc(str(s["title"]))}</span></a></li>'
        for s in services
    )
    taglines = {"Branding": "Look &amp; Experience", "Marketing": "Visibility &amp; Demand", "Sales": "Pipeline &amp; Revenue"}
    return f"""      <article class="ra-stack fade-up">
        <a href="/services/{pillar.lower()}" class="ra-stack__headline-link"><div class="ra-stack__name">{pillar}</div><div class="ra-stack__tagline">{taglines[pillar]}</div></a>
        <ul class="ra-stack__list">{items}</ul>
        <a href="/services/{pillar.lower()}" class="ra-stack__cta">Explore {pillar} <i class="fa-solid fa-arrow-right"></i></a>
      </article>"""


def services_overview_content() -> str:
    return f"""<!-- ==================== SERVICES: CLEAR 5 / 4 / 4 TAXONOMY ==================== -->
<section class="ra-services-hero">
  <canvas class="ra-services-hero__canvas" id="services-hero-network" aria-hidden="true"></canvas><div class="ra-services-hero__glow" aria-hidden="true"></div><div class="ra-services-hero__grid" aria-hidden="true"></div>
  <div class="container"><div class="ra-services-hero__inner"><div class="ra-services-hero__tagline fade-up">What We Do</div><h1 class="ra-services-hero__title fade-up fade-up-d1">Branding, Marketing &amp; Sales <em>Services</em></h1><p class="ra-services-hero__desc fade-up fade-up-d2">Clear services for businesses that need to look professional, reach more customers, and turn opportunities into revenue. Start with one service or connect several into one system.</p><div class="ra-services-hero__actions fade-up fade-up-d3"><a href="#service-list" class="btn btn--primary">See Every Service <i class="fa-solid fa-arrow-down btn-arrow"></i></a></div></div></div>
</section>

<section class="ra-services-system"><div class="container"><div class="ra-services-system__header fade-up"><span class="eyebrow">Three Clear Categories</span><h2>Easy to understand. Built to work together.</h2><p>Branding shapes what people see. Marketing helps the right people find and remember you. Sales creates and manages the path from opportunity to revenue.</p></div><div class="ra-services-system__grid">
  <a href="/services/branding" class="ra-services-system__card fade-up"><div class="ra-services-system__num">01 / BRANDING</div><h3>Look clear and professional.</h3><p>Websites, apps, brand identity, design, and video.</p></a>
  <a href="/services/marketing" class="ra-services-system__card fade-up"><div class="ra-services-system__num">02 / MARKETING</div><h3>Reach and nurture customers.</h3><p>SEO / AI Answers, social media, digital advertising, and customer nurture.</p></a>
  <a href="/services/sales" class="ra-services-system__card fade-up"><div class="ra-services-system__num">03 / SALES</div><h3>Create and manage opportunities.</h3><p>Outreach, lead gen ads, CRMs / sales tools, and AI automation systems.</p></a>
</div></div></section>

<section class="ra-services-stacks" id="service-list"><div class="ra-services-stacks__grid-lines" aria-hidden="true"></div><div class="container"><div class="ra-services-stacks__header fade-up"><span class="eyebrow eyebrow--white">All 13 Services</span><h2>Choose the exact <span class="highlight">work you need.</span></h2><p>The titles are intentionally plain. Open any service to see what is included, how we work, and related client proof.</p></div><div class="ra-services-stacks__grid">
{stack('Branding')}
{stack('Marketing')}
{stack('Sales')}
</div></div></section>

<section class="ra-services-engage"><div class="container"><div class="ra-services-engage__header fade-up"><span class="eyebrow">How We Engage</span><h2>One service or one connected team.</h2></div><div class="ra-services-engage__grid"><div class="ra-services-engage__col fade-up"><h3>Focused Project</h3><p>Bring us one clear need—like a website, brand identity, CRM, or campaign—and we will scope that work plainly.</p></div><div class="ra-services-engage__col ra-services-engage__col--integrated fade-up"><h3>Connected Growth System</h3><p>When several needs affect one another, we connect Branding, Marketing, and Sales so the handoffs are owned and visible.</p></div></div></div></section>

<section class="ra-services-featured p-section p-section--grey"><div class="container"><div class="ra-service-proof-heading fade-up"><span class="eyebrow">Real Client Work</span><h2>See the services working together.</h2><p class="lead">Client proof uses authentic project imagery. Concept art is used only to explain services.</p></div><div class="ra-service-proof-grid">
{proof_cards(['ivory-pools', 'net-metering-systems', 'reservwise'])}
</div><div class="ra-service-proof-more fade-up"><a href="/portfolio" class="btn btn--outline">Explore the full portfolio <i class="fa-solid fa-arrow-right"></i></a></div></div></section>

<section class="ra-cta"><div class="container"><div class="ra-cta__content fade-up"><h2 class="ra-cta__title">Not sure what you need?</h2><p class="ra-cta__desc">Tell us what is not working. We will explain the clearest starting point in plain language.</p><a href="/booking" class="btn btn--white">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a></div></div></section>

"""


def build_services_overview() -> bool:
    path = ROOT / "services.html"
    text = path.read_text(encoding="utf-8")
    text = metadata(
        text,
        title="Branding, Marketing & Sales Services | Revelation Agency",
        description="Websites, apps, brand identity, design, video, SEO, social media, advertising, nurture, outreach, lead generation, CRM, and AI automation services.",
        route="/services",
    )
    start = text.find("<!-- ==================== 1. HERO ==================== -->")
    if start < 0:
        start = text.find("<!-- ==================== SERVICES: CLEAR 5 / 4 / 4 TAXONOMY ==================== -->")
    end = text.find("<!-- RA-FOOTER-CANONICAL-START -->", start)
    if start < 0 or end < 0:
        raise ValueError("Missing services overview boundaries")
    text = text[:start] + services_overview_content() + text[end:]
    text = re.sub(r'<body\b[^>]*>', '<body data-ra-service="all-services">', text, count=1, flags=re.I)
    return write_if_changed(path, text)


def main() -> int:
    validate_service_proof_assignments()
    changed: list[str] = []
    for pillar in PILLAR_COPY:
        if build_hub(pillar):
            changed.append(f"services/{pillar.lower()}/index.html")
    for service in SERVICES:
        if build_leaf(service):
            changed.append(f"services/{str(service['pillar']).lower()}/{service['slug']}.html")
    if build_services_overview():
        changed.append("services.html")
    print(f"service taxonomy: {len(changed)} files changed")
    for rel in changed:
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
