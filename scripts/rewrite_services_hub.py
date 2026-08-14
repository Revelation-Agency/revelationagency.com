"""Rewrite services.html hub in-place to the Branding / Marketing / Sales
architecture.

Only textual + link substitutions are made — the surrounding layout,
navigation, footer, and integration snippets are left byte-identical (their
hashes are re-verified afterward by verify_integration_preservation.py).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PATH = "services.html"

SUBSTITUTIONS = [
    # Meta + og
    (
        '<meta name="description" content="Three disciplines. One growth machine. Systems, Creative, and Marketing — each a focused discipline, or connected into one integrated growth system.">',
        '<meta name="description" content="Three pillars. One growth system. Branding, Marketing, and Sales — each a focused discipline, or connected into one integrated growth system.">',
    ),
    (
        '<meta property="og:description" content="Three disciplines. One growth machine. Systems, Creative, and Marketing — each a focused discipline, or connected into one integrated growth system.">',
        '<meta property="og:description" content="Three pillars. One growth system. Branding, Marketing, and Sales — each a focused discipline, or connected into one integrated growth system.">',
    ),
    # Hero
    (
        '<h1 class="ra-services-hero__title fade-up fade-up-d1">Three Systems.<br>One <em>Growth Machine</em>.</h1>',
        '<h1 class="ra-services-hero__title fade-up fade-up-d1">Three Pillars.<br>One <em>Growth System</em>.</h1>',
    ),
    (
        '<p class="ra-services-hero__desc fade-up fade-up-d2">Revelation operates across three disciplines — Systems, Creative, and Marketing. Each service can stand alone as a focused engagement, or connect into one integrated growth system. You choose the entry point. We build the machine.</p>',
        '<p class="ra-services-hero__desc fade-up fade-up-d2">Revelation operates across three pillars — Branding, Marketing, and Sales — with AI and automation as a cross-cutting capability. Each pillar can stand alone as a focused engagement, or connect into one integrated growth system. You choose the entry point. We build the system.</p>',
    ),
    # HOW IT WORKS intro
    (
        '<p>Systems hold the foundation. Creative builds the assets. Marketing activates the audience. When all three run together, results compound.</p>',
        '<p>Branding builds the identity and the surfaces people see. Marketing earns visibility and demand. Sales converts demand into revenue. When the three run together, every layer makes the next stronger.</p>',
    ),
    # HOW IT WORKS three cards
    (
        '<a href="services/systems/index.html" class="ra-services-system__card fade-up fade-up-d1" data-ra-system-link="1" style="color:inherit;text-decoration:none;display:block;">\n        <div class="ra-services-system__num">01 / SYSTEMS</div>\n        <h3>The Foundation</h3>\n        <p>We build your sales infrastructure, digital presence, and AI &amp; agentic automation stack — the continuity-holding system everything else runs on.</p>\n        <span class="ra-services-system__arrow" aria-hidden="true" style="display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;color:var(--red);">Explore Systems <i class="fa-solid fa-arrow-right"></i></span>\n      </a>',
        '<a href="services/branding/index.html" class="ra-services-system__card fade-up fade-up-d1" data-ra-system-link="1" style="color:inherit;text-decoration:none;display:block;">\n        <div class="ra-services-system__num">01 / BRANDING</div>\n        <h3>The Identity</h3>\n        <p>Brand strategy, websites and landing pages, apps and digital products, and video. The identity + surface layer people encounter first — built as connected systems.</p>\n        <span class="ra-services-system__arrow" aria-hidden="true" style="display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;color:var(--red);">Explore Branding <i class="fa-solid fa-arrow-right"></i></span>\n      </a>',
    ),
    (
        '<a href="services/creative/index.html" class="ra-services-system__card fade-up fade-up-d2" data-ra-system-link="1" style="color:inherit;text-decoration:none;display:block;">\n        <div class="ra-services-system__num">02 / CREATIVE</div>\n        <h3>The Build</h3>\n        <p>We create the identity, digital presence, and content systems that make the system visible.</p>\n        <span class="ra-services-system__arrow" aria-hidden="true" style="display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;color:var(--red);">Explore Creative <i class="fa-solid fa-arrow-right"></i></span>\n      </a>',
        '<a href="services/marketing/index.html" class="ra-services-system__card fade-up fade-up-d2" data-ra-system-link="1" style="color:inherit;text-decoration:none;display:block;">\n        <div class="ra-services-system__num">02 / MARKETING</div>\n        <h3>The Visibility</h3>\n        <p>SEO and AI visibility, positioning and authority content, social media, and email/lifecycle marketing. The visibility + demand layer.</p>\n        <span class="ra-services-system__arrow" aria-hidden="true" style="display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;color:var(--red);">Explore Marketing <i class="fa-solid fa-arrow-right"></i></span>\n      </a>',
    ),
    (
        '<a href="services/marketing/index.html" class="ra-services-system__card fade-up fade-up-d3" data-ra-system-link="1" style="color:inherit;text-decoration:none;display:block;">\n        <div class="ra-services-system__num">03 / MARKETING</div>\n        <h3>The Activation</h3>\n        <p>We deploy and operate the channels, campaigns, and systems that drive pipeline and revenue.</p>\n        <span class="ra-services-system__arrow" aria-hidden="true" style="display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;color:var(--red);">Explore Marketing <i class="fa-solid fa-arrow-right"></i></span>\n      </a>',
        '<a href="services/sales/index.html" class="ra-services-system__card fade-up fade-up-d3" data-ra-system-link="1" style="color:inherit;text-decoration:none;display:block;">\n        <div class="ra-services-system__num">03 / SALES</div>\n        <h3>The Conversion</h3>\n        <p>Lead generation and personalized outreach, CRM and sales infrastructure, follow-up and nurture, conversion advertising. The acquisition + revenue layer.</p>\n        <span class="ra-services-system__arrow" aria-hidden="true" style="display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;color:var(--red);">Explore Sales <i class="fa-solid fa-arrow-right"></i></span>\n      </a>',
    ),

    # STACKS SECTION
    # Systems stack -> Branding stack
    (
        '''      <!-- Systems Stack -->
      <article class="ra-stack fade-up fade-up-d1">
        <a href="services/systems/index.html" class="ra-stack__headline-link" style="color:inherit;text-decoration:none;display:block;">
          <div class="ra-stack__num">01</div>
          <div class="ra-stack__name">Systems</div>
          <div class="ra-stack__tagline">Foundation &amp; Direction</div>
        </a>
        <ul class="ra-stack__list">
          <li><a href="services/systems/brand-systems.html"><i class="fa-solid fa-chevron-right"></i><span>Brand Systems</span></a></li>
          <li><a href="services/systems/sales-infrastructure.html"><i class="fa-solid fa-chevron-right"></i><span>Sales Infrastructure</span></a></li>
          <li><a href="services/systems/digital-presence.html"><i class="fa-solid fa-chevron-right"></i><span>Digital Presence</span></a></li>
          <li><a href="services/systems/ai-automation.html"><i class="fa-solid fa-chevron-right"></i><span>AI &amp; Automation</span></a></li>
        </ul>
        <a href="services/systems/index.html" class="ra-stack__cta">Explore Strategy <i class="fa-solid fa-arrow-right"></i></a>
      </article>''',
        '''      <!-- Branding Stack -->
      <article class="ra-stack fade-up fade-up-d1">
        <a href="services/branding/index.html" class="ra-stack__headline-link" style="color:inherit;text-decoration:none;display:block;">
          <div class="ra-stack__num">01</div>
          <div class="ra-stack__name">Branding</div>
          <div class="ra-stack__tagline">Identity &amp; Surfaces</div>
        </a>
        <ul class="ra-stack__list">
          <li><a href="services/branding/brand-strategy-identity.html"><i class="fa-solid fa-chevron-right"></i><span>Brand Strategy &amp; Identity</span></a></li>
          <li><a href="services/branding/websites-landing-pages.html"><i class="fa-solid fa-chevron-right"></i><span>Websites &amp; Landing Pages</span></a></li>
          <li><a href="services/branding/apps-digital-products.html"><i class="fa-solid fa-chevron-right"></i><span>Apps &amp; Digital Products</span></a></li>
          <li><a href="services/branding/video-visual-content.html"><i class="fa-solid fa-chevron-right"></i><span>Video &amp; Visual Content</span></a></li>
        </ul>
        <a href="services/branding/index.html" class="ra-stack__cta">Explore Branding <i class="fa-solid fa-arrow-right"></i></a>
      </article>''',
    ),
    # Creative stack -> Marketing stack
    (
        '''      <!-- Creative Stack -->
      <article class="ra-stack fade-up fade-up-d2">
        <a href="services/creative/index.html" class="ra-stack__headline-link" style="color:inherit;text-decoration:none;display:block;">
          <div class="ra-stack__num">02</div>
          <div class="ra-stack__name">Creative</div>
          <div class="ra-stack__tagline">Identity &amp; Build</div>
        </a>
        <ul class="ra-stack__list">
          <li><a href="services/creative/branding.html"><i class="fa-solid fa-chevron-right"></i><span>Branding</span></a></li>
          <li><a href="services/creative/website-development.html"><i class="fa-solid fa-chevron-right"></i><span>Website Development</span></a></li>
          <li><a href="services/creative/app-development.html"><i class="fa-solid fa-chevron-right"></i><span>App Development</span></a></li>
          <li><a href="services/creative/video-production.html"><i class="fa-solid fa-chevron-right"></i><span>Video Production</span></a></li>
        </ul>
        <a href="services/creative/index.html" class="ra-stack__cta">Explore Creative <i class="fa-solid fa-arrow-right"></i></a>
      </article>''',
        '''      <!-- Marketing Stack -->
      <article class="ra-stack fade-up fade-up-d2">
        <a href="services/marketing/index.html" class="ra-stack__headline-link" style="color:inherit;text-decoration:none;display:block;">
          <div class="ra-stack__num">02</div>
          <div class="ra-stack__name">Marketing</div>
          <div class="ra-stack__tagline">Visibility &amp; Demand</div>
        </a>
        <ul class="ra-stack__list">
          <li><a href="services/marketing/seo-ai-visibility.html"><i class="fa-solid fa-chevron-right"></i><span>SEO &amp; AI Visibility</span></a></li>
          <li><a href="services/marketing/positioning-content-authority.html"><i class="fa-solid fa-chevron-right"></i><span>Positioning, Content &amp; Authority</span></a></li>
          <li><a href="services/marketing/social-media.html"><i class="fa-solid fa-chevron-right"></i><span>Social Media</span></a></li>
          <li><a href="services/marketing/email-lifecycle-marketing.html"><i class="fa-solid fa-chevron-right"></i><span>Email &amp; Lifecycle Marketing</span></a></li>
        </ul>
        <a href="services/marketing/index.html" class="ra-stack__cta">Explore Marketing <i class="fa-solid fa-arrow-right"></i></a>
      </article>''',
    ),
    # Marketing stack -> Sales stack
    (
        '''      <!-- Marketing Stack -->
      <article class="ra-stack fade-up fade-up-d3">
        <a href="services/marketing/index.html" class="ra-stack__headline-link" style="color:inherit;text-decoration:none;display:block;">
          <div class="ra-stack__num">03</div>
          <div class="ra-stack__name">Marketing</div>
          <div class="ra-stack__tagline">Growth &amp; Reach</div>
        </a>
        <ul class="ra-stack__list">
          <li><a href="services/marketing/digital-ads.html"><i class="fa-solid fa-chevron-right"></i><span>Digital Ads</span></a></li>
          <li><a href="services/marketing/social-media.html"><i class="fa-solid fa-chevron-right"></i><span>Social Media</span></a></li>
          <li><a href="services/marketing/search-rankings.html"><i class="fa-solid fa-chevron-right"></i><span>Search &amp; AI Rankings</span></a></li>
          <li><a href="services/marketing/outsource-marketing.html"><i class="fa-solid fa-chevron-right"></i><span>Outsource Marketing</span></a></li>
        </ul>
        <a href="services/marketing/index.html" class="ra-stack__cta">Explore Marketing <i class="fa-solid fa-arrow-right"></i></a>
      </article>''',
        '''      <!-- Sales Stack -->
      <article class="ra-stack fade-up fade-up-d3">
        <a href="services/sales/index.html" class="ra-stack__headline-link" style="color:inherit;text-decoration:none;display:block;">
          <div class="ra-stack__num">03</div>
          <div class="ra-stack__name">Sales</div>
          <div class="ra-stack__tagline">Acquisition &amp; Revenue</div>
        </a>
        <ul class="ra-stack__list">
          <li><a href="services/sales/lead-generation-outreach.html"><i class="fa-solid fa-chevron-right"></i><span>Lead Generation &amp; Outreach</span></a></li>
          <li><a href="services/sales/crm-sales-infrastructure.html"><i class="fa-solid fa-chevron-right"></i><span>CRM &amp; Sales Infrastructure</span></a></li>
          <li><a href="services/sales/follow-up-nurture.html"><i class="fa-solid fa-chevron-right"></i><span>Follow-up &amp; Nurture</span></a></li>
          <li><a href="services/sales/conversion-advertising.html"><i class="fa-solid fa-chevron-right"></i><span>Conversion Advertising</span></a></li>
        </ul>
        <a href="services/sales/index.html" class="ra-stack__cta">Explore Sales <i class="fa-solid fa-arrow-right"></i></a>
      </article>''',
    ),

    # Footer service tree
    (
        '<a class="ra-footer__svc-parent" href="services/systems/">Systems<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>',
        '<a class="ra-footer__svc-parent" href="services/branding/">Branding<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>',
    ),
    (
        '<a class="ra-footer__svc-parent" href="services/creative/">Creative<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>',
        '<a class="ra-footer__svc-parent" href="services/marketing/">Marketing<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>',
    ),
    (
        '<a class="ra-footer__svc-parent" href="services/marketing/">Marketing<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>',
        '<a class="ra-footer__svc-parent" href="services/sales/">Sales<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>',
    ),
]


def main() -> int:
    with open(PATH, "r", encoding="utf-8") as f:
        data = f.read()
    original = data
    for old, new in SUBSTITUTIONS:
        if old in data:
            data = data.replace(old, new, 1)
    if data == original:
        print("services.html: no substitutions applied (already migrated?)")
        return 0
    with open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    print("services.html: rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
