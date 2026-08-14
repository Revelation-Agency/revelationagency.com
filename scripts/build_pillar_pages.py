"""Generate new Branding/Marketing/Sales pillar hubs, service leaves,
the AI/automation cross-cutting page, and portfolio pillar hubs.

Each page is a self-contained static HTML file that reuses the deployed
design tokens + nav/footer canonical markers, so the sitewide nav-rewriter
script (rewrite_nav_footer.py) can update them together with legacy pages.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# Depth = how many "../" a page needs to reach root.
DEPTH_ROOT = ""
DEPTH_1    = "../"
DEPTH_2    = "../../"


HEAD_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
  <!-- RA-PWA-HEAD:start -->
  <link rel="icon" href="{prefix}favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="{prefix}favicon-32.png">
  <link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">
  <link rel="manifest" href="{prefix}manifest.webmanifest">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Revelation">
  <meta name="theme-color" content="#D72532">
  <!-- RA-PWA-HEAD:end -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://www.revelationagency.com{canon_path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Revelation Agency">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="https://www.revelationagency.com{canon_path}">
<meta property="og:image" content="https://www.revelationagency.com/assets/img/og-share.svg">
<meta name="twitter:card" content="summary_large_image">

<link rel="preload" as="font" type="font/woff2" href="{prefix}assets/webfonts/Orbitron-VF.woff2" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Orbitron:wght@400;500;600;700;800;900&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
@font-face {{ font-family: 'Orbitron'; src: url('{prefix}assets/webfonts/Orbitron-VF.woff2') format('woff2'); font-weight: 400 900; font-style: normal; font-display: swap; }}

:root {{
  --red: #D72532; --red-deep: #AD1C24; --red-dark: #840D11;
  --charcoal: #2B2B2B; --black: #181818; --off-black: #1E1E1E;
  --grey-light: #F7F7F5; --grey-mid: #EDECE9; --white: #FFFFFF;
  --font-head: 'Bebas Neue', 'Orbitron', sans-serif;
  --font-body: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  --btn-radius: 45px 0 45px 45px;
  --section-pad: 110px 0;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; font-size: 16px; }}
body {{ font-family: var(--font-body); font-size: 1rem; line-height: 1.65; color: var(--charcoal); background: var(--white); -webkit-font-smoothing: antialiased; overflow-x: hidden; }}
img {{ display: block; max-width: 100%; }}
a {{ color: inherit; text-decoration: none; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 0 32px; }}
.eyebrow {{ font-family: var(--font-body); font-size: 11px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: var(--red); display: inline-block; margin-bottom: 16px; }}
h1, h2, h3, h4 {{ font-family: var(--font-head); line-height: 1.1; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }}
.highlight {{ color: var(--red); }}

.btn {{ display: inline-flex; align-items: center; gap: 10px; font-family: var(--font-body); font-size: 14px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding: 16px 36px; border-radius: var(--btn-radius); border: none; cursor: pointer; transition: transform .25s var(--ease-out), background .25s, box-shadow .25s; text-decoration: none; position: relative; overflow: hidden; }}
.btn--primary {{ background: var(--red); color: var(--white); }}
.btn--primary:hover {{ background: var(--red-deep); transform: translateY(-2px); box-shadow: 0 12px 32px rgba(215,37,50,0.4); }}
.btn--outline {{ background: transparent; color: var(--charcoal); border: 1.5px solid rgba(43,43,43,0.3); }}
.btn--outline:hover {{ border-color: var(--charcoal); background: var(--charcoal); color: var(--white); }}
.btn--white {{ background: var(--white); color: var(--charcoal); }}
.btn--white:hover {{ transform: translateY(-2px); box-shadow: 0 10px 28px rgba(0,0,0,0.15); }}
.btn--ghost-dark {{ background: transparent; color: #fff; border: 1.5px solid rgba(255,255,255,0.25); }}
.btn--ghost-dark:hover {{ border-color: #fff; background: #fff; color: var(--charcoal); }}

/* Pillar page skeleton */
.p-hero {{ background: var(--off-black); color: var(--white); padding: 160px 0 100px; position: relative; overflow: hidden; }}
.p-hero::before {{ content: ""; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px); background-size: 44px 44px; }}
.p-hero__inner {{ position: relative; max-width: 900px; }}
.p-hero h1 {{ font-size: clamp(44px, 6vw, 84px); line-height: 1.02; color: var(--white); margin-bottom: 22px; }}
.p-hero p.lead {{ font-size: 19px; line-height: 1.65; color: rgba(255,255,255,0.7); max-width: 720px; margin-bottom: 36px; }}
.p-hero__cta {{ display: flex; flex-wrap: wrap; gap: 16px; }}

.p-section {{ padding: var(--section-pad); }}
.p-section--dark {{ background: var(--off-black); color: var(--white); }}
.p-section--grey {{ background: var(--grey-light); }}
.p-section h2 {{ font-size: clamp(30px, 3.6vw, 50px); margin-bottom: 18px; }}
.p-section p.lead {{ font-size: 18px; color: #555; line-height: 1.7; max-width: 780px; margin-bottom: 42px; }}
.p-section--dark p.lead {{ color: rgba(255,255,255,0.7); }}

.p-leaves {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }}
.p-leaf {{ background: var(--white); border: 1px solid rgba(0,0,0,0.08); border-radius: 20px; padding: 32px 28px; display: flex; flex-direction: column; gap: 12px; transition: transform .25s var(--ease-out), box-shadow .25s, border-color .25s; }}
.p-leaf:hover {{ transform: translateY(-3px); box-shadow: 0 18px 44px rgba(0,0,0,0.08); border-color: rgba(215,37,50,0.4); }}
.p-leaf__num {{ font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--red); }}
.p-leaf h3 {{ font-size: 22px; }}
.p-leaf p {{ font-size: 15px; color: #555; line-height: 1.6; }}
.p-leaf__cta {{ margin-top: 8px; font-size: 13px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--red); }}

.p-two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: start; }}
.p-two h2 {{ margin-bottom: 20px; }}
.p-two ul {{ list-style: none; display: flex; flex-direction: column; gap: 14px; }}
.p-two li {{ padding-left: 28px; position: relative; font-size: 16px; color: #333; line-height: 1.6; }}
.p-two li::before {{ content: ""; position: absolute; left: 0; top: 10px; width: 14px; height: 2px; background: var(--red); }}

.p-crosscut {{ background: linear-gradient(135deg, #1a1a1a 0%, #2a1518 100%); color: #fff; padding: 90px 0; }}
.p-crosscut h2 {{ margin-bottom: 18px; }}
.p-crosscut p {{ font-size: 17px; line-height: 1.65; color: rgba(255,255,255,0.72); max-width: 760px; margin-bottom: 24px; }}

.p-cta {{ background: var(--red); color: var(--white); padding: 100px 0; text-align: center; }}
.p-cta h2 {{ font-size: clamp(30px, 3.8vw, 48px); color: var(--white); margin-bottom: 18px; }}
.p-cta p {{ font-size: 17px; color: rgba(255,255,255,0.85); max-width: 620px; margin: 0 auto 32px; }}
.p-cta .btn--white {{ background: var(--white); color: var(--red); }}
.p-cta .btn--white:hover {{ background: var(--charcoal); color: var(--white); }}

@media (max-width: 780px) {{
  .p-two {{ grid-template-columns: 1fr; gap: 32px; }}
  .p-hero {{ padding: 130px 0 72px; }}
}}
"""

# Nav + footer canonical blocks are inserted by rewrite_nav_footer.py during
# the sitewide sweep, so the pillar page generator only emits placeholder
# markers here. The rewriter replaces them.
NAV_PLACEHOLDER = """<!-- RA-NAV-CANONICAL-START -->
<!-- Nav injected by rewrite_nav_footer.py -->
<!-- RA-NAV-CANONICAL-END -->"""

FOOTER_PLACEHOLDER = """<!-- RA-FOOTER-CANONICAL-START -->
<!-- Footer injected by rewrite_nav_footer.py -->
<!-- RA-FOOTER-CANONICAL-END -->"""


def leaf_block(num: str, title: str, subtitle: str, desc: str, href: str) -> str:
    return f"""      <a class="p-leaf" href="{href}">
        <div class="p-leaf__num">{num}</div>
        <h3>{title}</h3>
        <p style="font-size:13px;letter-spacing:0.08em;text-transform:uppercase;color:var(--charcoal);opacity:0.7;margin-top:-4px;">{subtitle}</p>
        <p>{desc}</p>
        <span class="p-leaf__cta">Explore <i class="fa-solid fa-arrow-right"></i></span>
      </a>"""


def pillar_hub_body(pillar_title, pillar_subtitle, lead, why_grid, leaves_html, crosscut_line, cta_line):
    return f"""
{NAV_PLACEHOLDER}

<section class="p-hero">
  <div class="container">
    <div class="p-hero__inner">
      <div class="eyebrow" style="color:rgba(255,255,255,0.55);">Services · {pillar_title}</div>
      <h1>{pillar_subtitle}</h1>
      <p class="lead">{lead}</p>
      <div class="p-hero__cta">
        <a href="../../booking.html" class="btn btn--primary" data-cta="primary" data-cta-placement="pillar-hero" data-booking-open="1">Book a Free Strategy Session <i class="fa-solid fa-arrow-right"></i></a>
        <a href="#leaves" class="btn btn--ghost-dark" data-cta="secondary" data-cta-placement="pillar-hero">See the Four Disciplines</a>
      </div>
    </div>
  </div>
</section>

<section class="p-section p-section--grey">
  <div class="container">
    <div class="eyebrow">Why {pillar_title} Sits Here</div>
    <h2>{why_grid['heading']}</h2>
    <p class="lead">{why_grid['body']}</p>
    <div class="p-two">
      <div>
        <h3 style="font-size:22px;margin-bottom:16px;">{why_grid['left_title']}</h3>
        <ul>{"".join(f'<li>{x}</li>' for x in why_grid['left_items'])}</ul>
      </div>
      <div>
        <h3 style="font-size:22px;margin-bottom:16px;">{why_grid['right_title']}</h3>
        <ul>{"".join(f'<li>{x}</li>' for x in why_grid['right_items'])}</ul>
      </div>
    </div>
  </div>
</section>

<section class="p-section" id="leaves">
  <div class="container">
    <div class="eyebrow">The Four Disciplines</div>
    <h2>{pillar_title}, <span class="highlight">broken into systems.</span></h2>
    <p class="lead">Hire us for one — or stack them all. Each discipline stands alone and gets stronger next to the others.</p>
    <div class="p-leaves">
{leaves_html}
    </div>
  </div>
</section>

<section class="p-crosscut">
  <div class="container">
    <div class="eyebrow" style="color:rgba(255,255,255,0.55);">Cross-Cutting Capability</div>
    <h2>AI &amp; automation live inside every pillar — not on top of them.</h2>
    <p>{crosscut_line}</p>
    <p><a href="../ai-automation.html" class="btn btn--ghost-dark" data-cta="secondary" data-cta-placement="pillar-crosscut">How we implement AI &amp; automation <i class="fa-solid fa-arrow-right"></i></a></p>
  </div>
</section>

<section class="p-cta">
  <div class="container">
    <h2>{cta_line['h']}</h2>
    <p>{cta_line['p']}</p>
    <a href="../../booking.html" class="btn btn--white" data-cta="primary" data-cta-placement="pillar-cta" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a>
  </div>
</section>

{FOOTER_PLACEHOLDER}

<script src="../../assets/js/analytics-events.js" defer></script>
</body>
</html>
"""


def leaf_body(pillar_title, leaf_title, leaf_subtitle, lead, what_we_do, how_we_work, related_link, related_label):
    return f"""
{NAV_PLACEHOLDER}

<section class="p-hero">
  <div class="container">
    <div class="p-hero__inner">
      <div class="eyebrow" style="color:rgba(255,255,255,0.55);">Services · {pillar_title} · {leaf_title}</div>
      <h1>{leaf_subtitle}</h1>
      <p class="lead">{lead}</p>
      <div class="p-hero__cta">
        <a href="../../booking.html" class="btn btn--primary" data-cta="primary" data-cta-placement="leaf-hero" data-booking-open="1">Book a Free Strategy Session <i class="fa-solid fa-arrow-right"></i></a>
        <a href="index.html" class="btn btn--ghost-dark" data-cta="secondary" data-cta-placement="leaf-hero">Back to {pillar_title}</a>
      </div>
    </div>
  </div>
</section>

<section class="p-section">
  <div class="container">
    <div class="p-two">
      <div>
        <div class="eyebrow">What We Actually Do</div>
        <h2>Scope, plainly.</h2>
        <ul>{"".join(f'<li>{x}</li>' for x in what_we_do)}</ul>
      </div>
      <div>
        <div class="eyebrow">How We Work</div>
        <h2>Ordered, governed, honest.</h2>
        <ul>{"".join(f'<li>{x}</li>' for x in how_we_work)}</ul>
      </div>
    </div>
  </div>
</section>

<section class="p-section p-section--grey">
  <div class="container">
    <div class="eyebrow">Related Work</div>
    <h2>See what we ship.</h2>
    <p class="lead">All case studies are factual descriptions of what we built. Outcome numbers are only shown when a proof record supports them.</p>
    <a href="{related_link}" class="btn btn--outline" data-cta="secondary" data-cta-placement="leaf-related">{related_label} <i class="fa-solid fa-arrow-right"></i></a>
  </div>
</section>

<section class="p-cta">
  <div class="container">
    <h2>Talk it through with us.</h2>
    <p>Book a strategy session. We'll ask what you're trying to move, what's already in place, and where {pillar_title.lower()} would move the needle.</p>
    <a href="../../booking.html" class="btn btn--white" data-cta="primary" data-cta-placement="leaf-cta" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a>
  </div>
</section>

{FOOTER_PLACEHOLDER}

<script src="../../assets/js/analytics-events.js" defer></script>
</body>
</html>
"""


def crosscut_body(pillar_stack):
    return f"""
{NAV_PLACEHOLDER}

<section class="p-hero">
  <div class="container">
    <div class="p-hero__inner">
      <div class="eyebrow" style="color:rgba(255,255,255,0.55);">Cross-Cutting Capability</div>
      <h1>AI &amp; automation, wired into the work.</h1>
      <p class="lead">AI and automation are not a fourth pillar. They sit inside every Branding, Marketing, and Sales engagement — as governed implementations, not vendor demos.</p>
      <div class="p-hero__cta">
        <a href="../booking.html" class="btn btn--primary" data-cta="primary" data-cta-placement="ai-hero" data-booking-open="1">Book a Free Strategy Session <i class="fa-solid fa-arrow-right"></i></a>
        <a href="#stack" class="btn btn--ghost-dark" data-cta="secondary" data-cta-placement="ai-hero">See where it lives</a>
      </div>
    </div>
  </div>
</section>

<section class="p-section">
  <div class="container">
    <div class="p-two">
      <div>
        <div class="eyebrow">What We Mean By AI &amp; Automation</div>
        <h2>Governed implementation.</h2>
        <p>AI in the wrong hands is faster nonsense. We use it where it removes real toil — draft generation the human still edits, research assistants the human still verifies, follow-up sequences the human still owns. Reviii, our internal operator, is <strong>managed</strong> today; there is no public self-service API implication.</p>
      </div>
      <div>
        <div class="eyebrow">Human Authority</div>
        <h2>People decide.</h2>
        <p>Every automation names its owner, its next reviewer, and its rollback. We do not ship autonomous selling, instant-response promises, or dashboards that only look busy. If a step needs judgment, a person keeps it.</p>
      </div>
    </div>
  </div>
</section>

<section class="p-section p-section--grey" id="stack">
  <div class="container">
    <div class="eyebrow">Where It Shows Up</div>
    <h2>Inside the pillars.</h2>
    <p class="lead">Same capability, three contexts.</p>
    <div class="p-leaves">
      {"".join(pillar_stack)}
    </div>
  </div>
</section>

<section class="p-cta">
  <div class="container">
    <h2>Talk through what to automate — and what NOT to.</h2>
    <p>The honest audit is more valuable than the flashy demo. Book a call and we'll show you where an AI-assisted system would actually pay for itself.</p>
    <a href="../booking.html" class="btn btn--white" data-cta="primary" data-cta-placement="ai-cta" data-booking-open="1">Start a Conversation <i class="fa-solid fa-arrow-right"></i></a>
  </div>
</section>

{FOOTER_PLACEHOLDER}

<script src="../assets/js/analytics-events.js" defer></script>
</body>
</html>
"""


def portfolio_pillar_body(pillar_title, filter_key, lead_body):
    return f"""
{NAV_PLACEHOLDER}

<section class="p-hero">
  <div class="container">
    <div class="p-hero__inner">
      <div class="eyebrow" style="color:rgba(255,255,255,0.55);">Portfolio · {pillar_title}</div>
      <h1>{pillar_title} work.</h1>
      <p class="lead">{lead_body}</p>
      <div class="p-hero__cta">
        <a href="../portfolio.html?filter={filter_key}" class="btn btn--primary" data-cta="primary" data-cta-placement="portfolio-pillar-hero">See {pillar_title} Case Studies <i class="fa-solid fa-arrow-right"></i></a>
        <a href="../booking.html" class="btn btn--ghost-dark" data-cta="secondary" data-cta-placement="portfolio-pillar-hero" data-booking-open="1">Book a Free Strategy Session</a>
      </div>
    </div>
  </div>
</section>

<section class="p-section">
  <div class="container">
    <div class="eyebrow">Every Card Is Factual</div>
    <h2>What we built. What we shipped. Who it was for.</h2>
    <p class="lead">Case studies here describe the work delivered. Outcome numbers (CPL, conversion, revenue) only appear when we have a signed proof record from the client — otherwise we describe the system we built and skip the number.</p>
    <a href="../portfolio.html?filter={filter_key}" class="btn btn--outline" data-cta="secondary" data-cta-placement="portfolio-pillar-body">Browse the full {pillar_title} shelf <i class="fa-solid fa-arrow-right"></i></a>
  </div>
</section>

{FOOTER_PLACEHOLDER}

<script src="../assets/js/analytics-events.js" defer></script>
</body>
</html>
"""


# ---------------- Pillar hub content ------------------

BRANDING_HUB = {
    "canon_path": "/services/branding/",
    "title": "Branding — Revelation Agency",
    "description": "Branding is the identity + surface layer. Brand strategy, websites, apps, and video — built as connected systems.",
    "pillar_title": "Branding",
    "pillar_subtitle": "Identity you can build a business on.",
    "lead": "Branding is the layer people see first — and the layer that governs everything else. We build the identity, websites, apps, and video that carry the brand into the market as a connected system.",
    "why_grid": {
        "heading": "Brand is infrastructure, not decoration.",
        "body": "A great logo does not save a broken funnel. But a coherent brand system — identity, sites, product surfaces, and video that all speak the same language — makes every other layer of Marketing and Sales work harder.",
        "left_title": "What Branding Owns",
        "left_items": [
            "Brand strategy, identity, and guidelines",
            "Websites and landing pages as governed systems",
            "Apps and digital products with real ownership terms",
            "Video and visual content designed to compound",
        ],
        "right_title": "What Branding Does NOT Own",
        "right_items": [
            "Ad targeting and buying — that is Sales",
            "SEO/authority strategy — that is Marketing",
            "Lead qualification and follow-up — that is Sales",
            "Ongoing content publishing cadence — that is Marketing",
        ],
    },
    "leaves": [
        ("brand-strategy-identity", "01 / Discipline", "Brand Strategy & Identity", "Identity. Guidelines. Materials.",
         "Positioning, mark, color system, typography, and a brand guide teams can actually follow."),
        ("websites-landing-pages", "02 / Discipline", "Websites & Landing Pages", "Conversion. Authority. Platform.",
         "Coded, governed sites and campaign landing pages built as systems — not templates. Ownership, hosting, portability, and exit terms are always stated."),
        ("apps-digital-products", "03 / Discipline", "Apps & Digital Products", "Product. Portal. Portal-of-record.",
         "Custom apps and internal portals when the business case is bigger than a website. Built to be maintained, versioned, and rolled back."),
        ("video-visual-content", "04 / Discipline", "Video & Visual Content", "Brand. Story. Scale.",
         "Directed video and photography engineered to feed the whole stack — ads, socials, sales conversations, and product surfaces."),
    ],
    "crosscut": "Inside Branding, AI and automation power a fast brand-style pass, first-draft copy the strategist edits, image generation the designer approves, and CMS scaffolding the developer owns. Human judgment stays in the loop.",
    "cta": {"h": "Ready to build a brand that actually holds up?", "p": "Book a strategy session. We'll audit what you have, name what's missing, and prescribe the smallest next step."}
}

MARKETING_HUB = {
    "canon_path": "/services/marketing/",
    "title": "Marketing — Revelation Agency",
    "description": "Marketing is the visibility + demand layer. SEO & AI visibility, positioning, social, and email/lifecycle — connected to the brand and the sales system.",
    "pillar_title": "Marketing",
    "pillar_subtitle": "Visibility that earns attention. Attention that becomes demand.",
    "lead": "Marketing is the middle layer. It takes the brand people see and turns it into demand people act on — through search, authority content, social, and lifecycle communication.",
    "why_grid": {
        "heading": "Attention is the currency. Demand is the outcome.",
        "body": "Most agencies sell 'marketing' as one loud thing. We treat it as four connected disciplines that turn a defensible brand into demand pipeline — search visibility, positioning, social presence, and lifecycle communication.",
        "left_title": "What Marketing Owns",
        "left_items": [
            "SEO and AI-answer-engine visibility",
            "Positioning, content, and authority publishing",
            "Social media presence with a working cadence",
            "Email and lifecycle marketing to owned lists",
        ],
        "right_title": "What Marketing Does NOT Own",
        "right_items": [
            "Brand identity or website design — that is Branding",
            "Paid conversion advertising — that is Sales",
            "CRM setup or lead routing — that is Sales",
            "Personal outreach or booking — that is Sales",
        ],
    },
    "leaves": [
        ("seo-ai-visibility", "01 / Discipline", "SEO & AI Visibility", "Organic. Discovery. Authority.",
         "Technical SEO, information architecture, structured data, and content strategy — tuned for both classical search and AI answer engines."),
        ("positioning-content-authority", "02 / Discipline", "Positioning, Content & Authority", "Point of view. Substance. Repeatability.",
         "The point of view that makes people care, and the publishing rhythm that makes it stick. The Reveal is a working example."),
        ("social-media", "03 / Discipline", "Social Media", "Presence. Consistency. Relevance.",
         "Managed presence with a real publishing cadence — no vanity metrics, no 'AI slop', no promise of viral. Consistency, then relevance, then reach."),
        ("email-lifecycle-marketing", "04 / Discipline", "Email & Lifecycle Marketing", "Owned list. Actual value. Governed sends.",
         "Newsletters, onboarding sequences, and lifecycle nurture on infrastructure you own. Send discipline, deliverability, and unsubscribe hygiene are non-negotiable."),
    ],
    "crosscut": "Inside Marketing, AI drafts topic clusters the strategist edits, summarizes long-form content into social variants a human approves, and identifies retention risk in a lifecycle sequence a human decides how to answer.",
    "cta": {"h": "Ready to compound attention into demand?", "p": "Book a call. We'll audit your visibility, name the gap between attention and pipeline, and propose the fastest defensible next step."}
}

SALES_HUB = {
    "canon_path": "/services/sales/",
    "title": "Sales — Revelation Agency",
    "description": "Sales is the acquisition + revenue layer. Lead generation, CRM and sales infrastructure, follow-up and nurture, and conversion advertising.",
    "pillar_title": "Sales",
    "pillar_subtitle": "Systems that turn interest into revenue.",
    "lead": "Sales is where the pillars pay off. Brand earns attention, Marketing earns demand, and Sales converts it — through outreach, CRM infrastructure, disciplined follow-up, and conversion advertising that actually respects the budget.",
    "why_grid": {
        "heading": "Every dollar of brand and marketing dies at a broken sales system.",
        "body": "You can have a beautiful brand and full-funnel attention and still not close. Sales is the layer that catches the demand, qualifies it, and moves it to revenue on infrastructure that does not lose leads.",
        "left_title": "What Sales Owns",
        "left_items": [
            "Lead generation and personalized outreach",
            "CRM and sales infrastructure (the durable pipe)",
            "Follow-up, nurture, and reactivation sequences",
            "Conversion advertising tied to the sales system",
        ],
        "right_title": "What Sales Does NOT Own",
        "right_items": [
            "Brand voice or identity — that is Branding",
            "Long-form authority content — that is Marketing",
            "The website design system — that is Branding",
            "SEO / AI visibility strategy — that is Marketing",
        ],
    },
    "leaves": [
        ("lead-generation-outreach", "01 / Discipline", "Lead Generation & Personalized Outreach", "Prospecting. List. Message.",
         "Targeted outbound campaigns to people who actually match — with copy the operator reviews before it goes out. No autonomous selling; humans stay on the trigger."),
        ("crm-sales-infrastructure", "02 / Discipline", "CRM & Sales Infrastructure", "Pipe. Routing. Reporting.",
         "The durable pipe: pipeline stages, ownership rules, routing, and reporting so no lead sits waiting and no handoff falls through."),
        ("follow-up-nurture", "03 / Discipline", "Follow-up & Nurture", "Cadence. Care. Reactivation.",
         "Ordered cadences that respect the prospect — helpful check-ins, useful content, and cleanly managed reactivation for cold leads."),
        ("conversion-advertising", "04 / Discipline", "Conversion Advertising", "Paid. Measurable. Governed.",
         "Paid campaigns tied to the sales system so every dollar has a destination. We say what we can attribute, what we cannot, and why."),
    ],
    "crosscut": "Inside Sales, AI-assisted operators (Reviii and its managed peers) draft outreach for humans to approve, watch for stalled deals so a human can intervene, and keep the CRM tidy — never sending on their own initiative.",
    "cta": {"h": "Ready to plug the leaks and compound the wins?", "p": "Book a strategy session. We'll audit your funnel, name where leads are dying, and prescribe the fastest fix that respects your team."}
}


# --------- Leaves content (short but real; no lorem-ipsum) ----------

BRANDING_LEAVES = {
    "brand-strategy-identity": {
        "canon_path": "/services/branding/brand-strategy-identity.html",
        "title": "Brand Strategy & Identity — Revelation Agency",
        "description": "Positioning, identity system, and brand guide — built as infrastructure, not decoration.",
        "leaf_title": "Brand Strategy & Identity",
        "leaf_subtitle": "Positioning first. Marks second.",
        "lead": "The identity has to hold up in a browser, on a business card, on a screen behind a stage, and in a ten-second video. We build brand systems that survive that test.",
        "what_we_do": [
            "Positioning audit and category mapping",
            "Naming input (when needed) and story development",
            "Primary and secondary logo marks with rationale",
            "Color system, typography, and grid",
            "A brand guide that a designer can actually follow",
        ],
        "how_we_work": [
            "Discovery is a conversation, not a form dump",
            "One primary direction with one clearly explained runner-up",
            "Every deliverable is versioned, reviewed, and rolled back if needed",
            "Ownership terms and source files are stated up front",
        ],
        "related_link": "../../portfolio/branding.html",
        "related_label": "Branding case studies",
    },
    "websites-landing-pages": {
        "canon_path": "/services/branding/websites-landing-pages.html",
        "title": "Websites & Landing Pages — Revelation Agency",
        "description": "Coded, governed sites and campaign landing pages built as systems — not templates.",
        "leaf_title": "Websites & Landing Pages",
        "leaf_subtitle": "A site that behaves like infrastructure.",
        "lead": "A professionally managed codebase gives you faster iteration, disciplined technical SEO, integrated analytics and CRM, versioned changes, and a clean rollback story. That is the outcome — the platform is a choice we make with you, not a religion we sell you.",
        "what_we_do": [
            "Custom coded sites (React/Vite/Astro/Next as the case demands)",
            "Campaign landing pages that measure themselves",
            "Structured data, sitemap, and canonical hygiene",
            "Integrated forms, booking, and analytics contracts",
            "Ownership, hosting, maintenance, and exit terms stated in writing",
        ],
        "how_we_work": [
            "We do not claim WordPress / Wix / Squarespace is 'always worse'",
            "We prescribe a replatform only when the client evidence supports it",
            "Governed iteration: changes are reviewed, versioned, and reversible",
            "Analytics is a contract with a real destination and a real consent story",
        ],
        "related_link": "../../portfolio/branding.html",
        "related_label": "Websites we've shipped",
    },
    "apps-digital-products": {
        "canon_path": "/services/branding/apps-digital-products.html",
        "title": "Apps & Digital Products — Revelation Agency",
        "description": "Custom apps and internal portals — built to be maintained, versioned, and rolled back.",
        "leaf_title": "Apps & Digital Products",
        "leaf_subtitle": "When 'website' is the wrong answer.",
        "lead": "Some problems are not a page. They are a workflow, a portal, a booking engine, an internal operator surface. When that is the honest scope, we build the app — with the same discipline we bring to the site.",
        "what_we_do": [
            "Scoping and MVP definition, honestly bounded",
            "Custom web apps and portals with real auth + roles",
            "Booking, scheduling, and lifecycle engines",
            "Internal operator surfaces (case-in-point: the Revelation Portal)",
            "Ownership, IP, and hand-off terms up front",
        ],
        "how_we_work": [
            "Build in vertical slices; ship the first working version early",
            "Reviii is managed — we do not sell a public self-service Reviii API",
            "Every product carries a rollback and a change log",
            "Handoff docs are written for the team who will operate it",
        ],
        "related_link": "../../portfolio/branding.html",
        "related_label": "Products we've built",
    },
    "video-visual-content": {
        "canon_path": "/services/branding/video-visual-content.html",
        "title": "Video & Visual Content — Revelation Agency",
        "description": "Directed video and photography engineered to feed the whole stack.",
        "leaf_title": "Video & Visual Content",
        "leaf_subtitle": "Directed. Distributed. Reused.",
        "lead": "Great video is expensive to produce and cheap to reuse. We plan every shoot to feed ads, socials, sales conversations, and product surfaces — not just one hero cut.",
        "what_we_do": [
            "Brand films and founder-story pieces",
            "Product and service explainers",
            "Case-study video, filmed on real premises",
            "Photography for the site, the deck, and the ads",
            "Motion / animation when it earns its place",
        ],
        "how_we_work": [
            "Every shoot is planned against a distribution list",
            "We name usage rights and reuse terms up front",
            "Talent, music, and stock get licensed cleanly",
            "Files are delivered organized, not dumped in a folder",
        ],
        "related_link": "../../portfolio/branding.html",
        "related_label": "Video work",
    },
}

MARKETING_LEAVES = {
    "seo-ai-visibility": {
        "canon_path": "/services/marketing/seo-ai-visibility.html",
        "title": "SEO & AI Visibility — Revelation Agency",
        "description": "Technical SEO, information architecture, and content strategy tuned for both classical search and AI answer engines.",
        "leaf_title": "SEO & AI Visibility",
        "leaf_subtitle": "Rank where it counts. Get quoted where it matters.",
        "lead": "SEO now covers two stacks: the classical search index and the AI answer engines that summarize your site into a response. We tune both — with structured data, clean IA, and content that is quotable.",
        "what_we_do": [
            "Technical SEO audit (crawl, index, canonical, schema)",
            "Information architecture and internal linking",
            "Content strategy targeted at intent, not keyword volume",
            "Structured data and answer-engine formatting",
            "Reporting that says what moved and what did not",
        ],
        "how_we_work": [
            "We do not spin up thin AI-generated location/service pages",
            "We do not promise a ranking number we cannot back",
            "Content is drafted by humans; AI assists on research and outline",
            "Every recommendation is prioritized by defensibility, not novelty",
        ],
        "related_link": "../../portfolio/marketing.html",
        "related_label": "Marketing case studies",
    },
    "positioning-content-authority": {
        "canon_path": "/services/marketing/positioning-content-authority.html",
        "title": "Positioning, Content & Authority — Revelation Agency",
        "description": "The point of view that makes people care, and the publishing rhythm that makes it stick.",
        "leaf_title": "Positioning, Content & Authority",
        "leaf_subtitle": "Point of view. Substance. Repeatability.",
        "lead": "Authority is boring to build and cheap to lose. We help you articulate a defensible point of view and establish a publishing rhythm that compounds — The Reveal is a working example.",
        "what_we_do": [
            "Positioning worksheet and messaging spine",
            "Long-form article production and editing",
            "Editorial calendar with a cadence you can actually keep",
            "Point-of-view assets used across sales conversations",
            "Cross-posting and repurposing rules",
        ],
        "how_we_work": [
            "Substance beats frequency — a slower cadence you keep beats a fast one you miss",
            "The point of view is the client's; we help you sharpen it, not replace it",
            "AI is used to research and outline; humans write",
            "No 'thought leadership' fluff we would not sign our own name to",
        ],
        "related_link": "../../the-reveal/index.html",
        "related_label": "The Reveal (worked example)",
    },
    "social-media": {
        "canon_path": "/services/marketing/social-media.html",
        "title": "Social Media — Revelation Agency",
        "description": "Managed social presence with a real publishing cadence.",
        "leaf_title": "Social Media",
        "leaf_subtitle": "Presence. Consistency. Relevance.",
        "lead": "Reach is a vanity metric. We manage social presence for the same reasons a store keeps its windows clean — because people who show up expect to see somebody home.",
        "what_we_do": [
            "Platform strategy (which platforms actually matter to your buyer)",
            "Content pillars and monthly cadence",
            "Post production, scheduling, and moderation",
            "Community reply hygiene and DM triage rules",
            "Reporting on what actually influenced conversation",
        ],
        "how_we_work": [
            "No engagement-farming tactics that hurt long-term signal",
            "No promise of virality — that is not a service",
            "AI-assist writes drafts; humans post",
            "We say what a post is meant to do before it goes up",
        ],
        "related_link": "../../portfolio/marketing.html",
        "related_label": "Social work",
    },
    "email-lifecycle-marketing": {
        "canon_path": "/services/marketing/email-lifecycle-marketing.html",
        "title": "Email & Lifecycle Marketing — Revelation Agency",
        "description": "Newsletters, onboarding sequences, and lifecycle nurture on infrastructure you own.",
        "leaf_title": "Email & Lifecycle Marketing",
        "leaf_subtitle": "Owned list. Actual value. Governed sends.",
        "lead": "Email still outperforms nearly every other channel — until you overuse it. We design sequences with cadence, unsubscribe hygiene, deliverability discipline, and the assumption that the list belongs to you.",
        "what_we_do": [
            "Newsletter production on a cadence you can hold",
            "Onboarding, activation, and reactivation sequences",
            "Segmentation by real behavior, not just tags",
            "Deliverability audit and warm-up plan",
            "Consent, unsubscribe, and preference infrastructure",
        ],
        "how_we_work": [
            "Owned list first; rented audiences second",
            "Every send is worth reading or it does not go out",
            "AI-assist drafts variants; the human editor picks the send",
            "Reporting focuses on downstream action, not open rate theater",
        ],
        "related_link": "../../portfolio/marketing.html",
        "related_label": "Marketing work",
    },
}

SALES_LEAVES = {
    "lead-generation-outreach": {
        "canon_path": "/services/sales/lead-generation-outreach.html",
        "title": "Lead Generation & Personalized Outreach — Revelation Agency",
        "description": "Targeted outbound campaigns with copy the operator reviews before it goes out.",
        "leaf_title": "Lead Generation & Personalized Outreach",
        "leaf_subtitle": "Real people, real messages, human trigger.",
        "lead": "Cold outreach is not dead — sloppy cold outreach is. We build small, targeted campaigns to people who match, with messages a human reviews before send.",
        "what_we_do": [
            "Ideal-customer definition and list building",
            "Personalized outbound sequences (email, SMS, LinkedIn)",
            "Deliverability + domain warm-up + reply hygiene",
            "Handoff to CRM with clean pipeline mapping",
            "Ongoing tuning based on reply rates and sales feedback",
        ],
        "how_we_work": [
            "No autonomous selling; humans stay on the trigger",
            "Volume is not the measure — reply quality is",
            "Every campaign has an exit criterion and a rollback",
            "We say what we sent, what worked, and what we killed",
        ],
        "related_link": "../../portfolio/sales.html",
        "related_label": "Sales case studies",
    },
    "crm-sales-infrastructure": {
        "canon_path": "/services/sales/crm-sales-infrastructure.html",
        "title": "CRM & Sales Infrastructure — Revelation Agency",
        "description": "The durable pipe: pipeline stages, ownership rules, routing, and reporting.",
        "leaf_title": "CRM & Sales Infrastructure",
        "leaf_subtitle": "The durable pipe under the funnel.",
        "lead": "The best campaigns die in a bad CRM. We build the pipeline so no lead sits waiting, no handoff falls through, and the reports actually match reality.",
        "what_we_do": [
            "CRM setup or rebuild (GoHighLevel is the default; others on request)",
            "Pipeline stages, ownership, and routing rules",
            "Contact hygiene, deduplication, and merge policy",
            "Reporting dashboards keyed to the sales motion",
            "Handoff runbook so an operator can actually run it",
        ],
        "how_we_work": [
            "We name what the CRM will do — and what it will not",
            "Every automation carries an owner and a rollback",
            "Screenshots of live workflows in the case study, not vendor screenshots",
            "Managed today; a public self-service Reviii API is later, not now",
        ],
        "related_link": "../../portfolio/sales.html",
        "related_label": "Sales infrastructure work",
    },
    "follow-up-nurture": {
        "canon_path": "/services/sales/follow-up-nurture.html",
        "title": "Follow-up & Nurture — Revelation Agency",
        "description": "Ordered cadences that respect the prospect.",
        "leaf_title": "Follow-up & Nurture",
        "leaf_subtitle": "Persistence with taste.",
        "lead": "Most deals are lost between message three and message seven. We design follow-up cadences that are useful to the prospect and disciplined about when to stop.",
        "what_we_do": [
            "Post-inquiry follow-up sequences",
            "Long-cycle nurture for slow buyers",
            "Reactivation cadences for cold leads",
            "Rules for when to escalate a human",
            "Language, tone, and stop-criteria baked into the sequence",
        ],
        "how_we_work": [
            "No 'instant automated response' promise unless the operating system proves it",
            "Cadences have a defined end — they do not haunt forever",
            "Reply monitoring is a human job; alerts, not autonomy",
            "Every message earns its send",
        ],
        "related_link": "../../portfolio/sales.html",
        "related_label": "Related work",
    },
    "conversion-advertising": {
        "canon_path": "/services/sales/conversion-advertising.html",
        "title": "Conversion Advertising — Revelation Agency",
        "description": "Paid campaigns tied to the sales system so every dollar has a destination.",
        "leaf_title": "Conversion Advertising",
        "leaf_subtitle": "Paid. Measurable. Governed.",
        "lead": "Paid media is not a growth strategy on its own; it is a lever on top of a real sales system. We run conversion advertising where the funnel is ready to receive it — and we say when it is not.",
        "what_we_do": [
            "Meta, Google, and platform-specific campaigns",
            "Landing pages tied to specific offers, not the general site",
            "Creative test plans with hypotheses and kill criteria",
            "Attribution contract with what we can and cannot measure",
            "Weekly reporting that says what changed and why",
        ],
        "how_we_work": [
            "No 'starting at $500' anchor for a full site + SEO program",
            "No claim we cannot back with a report a client can see",
            "Budgets carry a floor and a ceiling before we start",
            "If paid is not the right lever, we say so",
        ],
        "related_link": "../../portfolio/sales.html",
        "related_label": "Conversion advertising work",
    },
}

AI_STACK = [
    """      <div class="p-leaf" style="cursor:default;">
        <div class="p-leaf__num">Inside Branding</div>
        <h3>Faster identity iteration</h3>
        <p>AI supports moodboarding, style variants, and copy first-drafts — designers and strategists still decide.</p>
      </div>""",
    """      <div class="p-leaf" style="cursor:default;">
        <div class="p-leaf__num">Inside Marketing</div>
        <h3>Research + drafting assistants</h3>
        <p>AI drafts topic clusters, summarizes long-form to social variants, and flags retention risk in lifecycle sequences.</p>
      </div>""",
    """      <div class="p-leaf" style="cursor:default;">
        <div class="p-leaf__num">Inside Sales</div>
        <h3>Reviii, managed operator</h3>
        <p>Reviii drafts outreach for approval, watches for stalled deals, and keeps the CRM tidy — never sending unattended.</p>
      </div>""",
]


def write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("  wrote", path)


def build_all():
    # ---- Service pillar hubs ----
    for slug, spec in (("branding", BRANDING_HUB), ("marketing", MARKETING_HUB), ("sales", SALES_HUB)):
        head = HEAD_TMPL.format(
            prefix=DEPTH_2,
            title=spec["title"],
            description=spec["description"],
            canon_path=spec["canon_path"],
        )
        leaves_html = "\n".join(
            leaf_block(l[1], l[2], l[3], l[4], f"{l[0]}.html") for l in spec["leaves"]
        )
        body = pillar_hub_body(
            spec["pillar_title"], spec["pillar_subtitle"], spec["lead"],
            spec["why_grid"], leaves_html, spec["crosscut"], spec["cta"],
        )
        out = f"services/{slug}/index.html"
        write(out, head + body + "</style>\n</head>\n<body>\n" if False else head + "</style>\n</head>\n<body>\n" + body)

    # ---- Service leaves ----
    def emit_leaves(pillar_title, slug_root, leaves):
        for leaf_slug, spec in leaves.items():
            head = HEAD_TMPL.format(
                prefix=DEPTH_2,
                title=spec["title"],
                description=spec["description"],
                canon_path=spec["canon_path"],
            )
            body = leaf_body(
                pillar_title=pillar_title,
                leaf_title=spec["leaf_title"],
                leaf_subtitle=spec["leaf_subtitle"],
                lead=spec["lead"],
                what_we_do=spec["what_we_do"],
                how_we_work=spec["how_we_work"],
                related_link=spec["related_link"],
                related_label=spec["related_label"],
            )
            out = f"services/{slug_root}/{leaf_slug}.html"
            write(out, head + "</style>\n</head>\n<body>\n" + body)

    emit_leaves("Branding",  "branding",  BRANDING_LEAVES)
    emit_leaves("Marketing", "marketing", MARKETING_LEAVES)
    emit_leaves("Sales",     "sales",     SALES_LEAVES)

    # ---- Cross-cutting AI page (depth 1 = /services/ai-automation.html) ----
    head = HEAD_TMPL.format(
        prefix=DEPTH_1,
        title="AI & Automation — Revelation Agency",
        description="AI and automation as a cross-cutting capability across Branding, Marketing, and Sales — governed, human-owned, and honestly bounded.",
        canon_path="/services/ai-automation.html",
    )
    body = crosscut_body(AI_STACK)
    write("services/ai-automation.html", head + "</style>\n</head>\n<body>\n" + body)

    # ---- Portfolio pillar hubs (depth 1 = /portfolio/{pillar}.html) ----
    for pillar_title, slug, filter_key, lead in [
        ("Branding",  "branding",  "branding",  "Identity, sites, apps, and video — the surfaces we build for the brand to live on."),
        ("Marketing", "marketing", "marketing", "Search visibility, authority content, social presence, and lifecycle work."),
        ("Sales",     "sales",     "sales",     "Lead generation, CRM infrastructure, follow-up, and conversion advertising."),
    ]:
        head = HEAD_TMPL.format(
            prefix=DEPTH_1,
            title=f"{pillar_title} Work — Revelation Agency Portfolio",
            description=f"Selected {pillar_title.lower()} case studies from Revelation Agency.",
            canon_path=f"/portfolio/{slug}.html",
        )
        body = portfolio_pillar_body(pillar_title, filter_key, lead)
        write(f"portfolio/{slug}.html", head + "</style>\n</head>\n<body>\n" + body)


if __name__ == "__main__":
    build_all()
    print("done")
