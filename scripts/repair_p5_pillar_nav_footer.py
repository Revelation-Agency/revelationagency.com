"""P5 rebrand — pillar-page nav/footer repair.

Fixes three evidenced blockers on the P5 candidate:

  1. The 19 new pillar hub / leaf / cross-cutting / portfolio-pillar pages
     have the RA-NAV-CANONICAL nav HTML but ZERO nav-related CSS (the
     legacy pages carry hundreds of lines of inline nav CSS, the new
     pages do not) — so the nav collapses to an unstyled vertical
     bulleted list. Fix: link the shared assets/css/ra-nav-footer.css
     into <head> on those 19 pages. Idempotent (skips if already linked).

  2. Those same 19 pages have an EMPTY footer placeholder:

         <!-- RA-FOOTER-CANONICAL-START -->
         <!-- Footer injected by rewrite_nav_footer.py -->
         <!-- RA-FOOTER-CANONICAL-END -->

     which renders as a large blank/black region at the bottom of the
     page. Fix: inject a full canonical footer between those markers,
     using the approved Branding / Marketing / Sales pillar structure.

  3. The 9 legacy baseline pages (index/about/contact/faq/services/
     portfolio/booking/web-hosting/404) still carry the pre-rebrand
     "Systems / Creative / Marketing" service list inside <footer
     class="ra-footer">. Fix: swap those three groups for
     Branding / Marketing / Sales, preserving every surrounding byte
     (miniform webhook, mailto, tel, chat widget, booking iframe,
     copyright, address).

The script is idempotent: rerunning produces zero diff. All writes go
back through utf-8 with LF line endings preserved.

No network. No credential access. No commit. Local-only, reviewable.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from typing import Dict, List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


# ------------------------------------------------------------------ helpers

def read(path: str) -> str:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def depth_prefix(rel_path: str) -> str:
    """Return '', '../', '../../' etc. based on directory depth relative to repo root."""
    parts = os.path.dirname(rel_path).replace("\\", "/").split("/")
    parts = [p for p in parts if p]
    return "".join(["../"] * len(parts))


def sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------ page inventory

# Every page carrying an EMPTY RA-FOOTER-CANONICAL placeholder.
PILLAR_PAGES: List[str] = [
    "services/branding/index.html",
    "services/branding/brand-strategy-identity.html",
    "services/branding/websites-landing-pages.html",
    "services/branding/apps-digital-products.html",
    "services/branding/video-visual-content.html",
    "services/marketing/index.html",
    "services/marketing/seo-ai-visibility.html",
    "services/marketing/positioning-content-authority.html",
    "services/marketing/social-media.html",
    "services/marketing/email-lifecycle-marketing.html",
    "services/sales/index.html",
    "services/sales/lead-generation-outreach.html",
    "services/sales/crm-sales-infrastructure.html",
    "services/sales/follow-up-nurture.html",
    "services/sales/conversion-advertising.html",
    "services/ai-automation.html",
    "portfolio/branding.html",
    "portfolio/marketing.html",
    "portfolio/sales.html",
]

# Baseline pages that already have a rendered footer but still carry the
# legacy Systems / Creative / Marketing service list. Their integration
# snippets (WEBHOOK line, mailto, tel, iframes) must be preserved
# byte-identically — the sweep touches ONLY the ra-footer__svc <ul>.
BASELINE_PAGES: List[str] = [
    "index.html",
    "about.html",
    "contact.html",
    "faq.html",
    "services.html",
    "portfolio.html",
    "booking.html",
    "web-hosting.html",
    "404.html",
]


# ------------------------------------------------------------------ Fix 1: CSS link injection

CSS_LINK_MARKER_START = "<!-- RA-NAV-FOOTER-CSS:start -->"
CSS_LINK_MARKER_END = "<!-- RA-NAV-FOOTER-CSS:end -->"


def inject_shared_css_link(text: str, prefix: str) -> Tuple[str, bool]:
    """Insert a <link rel='stylesheet' href='.../assets/css/ra-nav-footer.css'>
    into <head> immediately before </head>, wrapped in idempotency markers.
    Returns (new_text, changed?)."""
    if CSS_LINK_MARKER_START in text:
        return text, False
    link_block = (
        f"{CSS_LINK_MARKER_START}\n"
        f'<link rel="stylesheet" href="{prefix}assets/css/ra-nav-footer.css">\n'
        f"{CSS_LINK_MARKER_END}\n"
    )
    # Insert immediately before </head> — preserves surrounding whitespace.
    new_text, n = re.subn(r"</head>", link_block + "</head>", text, count=1)
    return new_text, n == 1


# ------------------------------------------------------------------ Fix 2: footer injection

FOOTER_START = "<!-- RA-FOOTER-CANONICAL-START -->"
FOOTER_END = "<!-- RA-FOOTER-CANONICAL-END -->"


def canonical_footer(prefix: str) -> str:
    """Build the canonical footer HTML with path prefix for links.
    Uses Branding / Marketing / Sales — the approved P5 pillar architecture.
    Does NOT include the miniform webhook (that lives only on the 9 baseline
    pages whose integration snippets are pinned in the baseline). Instead the
    CTA column points at the booking page — same destination, no new webhook
    activation.
    """
    p = prefix
    return f"""{FOOTER_START}
<footer class="ra-footer">
  <div class="container">
    <div class="ra-footer__inner">
      <div class="ra-footer__brand">
        <div class="ra-footer__logo">
          <img src="{p}assets/revelation-logo.png" alt="Revelation Agency">
        </div>
        <p>Your strategic growth partner. We build the machine behind growth &mdash; so you can stop selling chaos and start scaling clarity.</p>
        <div class="ra-footer__tagline">Branding. Marketing. Sales.</div>
        <div class="ra-footer__social">
          <a href="https://www.linkedin.com/company/revelation-agency" target="_blank" rel="noopener" aria-label="LinkedIn"><i class="fa-brands fa-linkedin-in"></i></a>
          <a href="https://www.instagram.com/revelationagency/" target="_blank" rel="noopener" aria-label="Instagram"><i class="fa-brands fa-instagram"></i></a>
          <a href="https://www.facebook.com/revelationagency/" target="_blank" rel="noopener" aria-label="Facebook"><i class="fa-brands fa-facebook"></i></a>
        </div>
        <address style="font-style:normal; margin-top:18px; font-size:12.5px; line-height:1.55; color:rgba(255,255,255,0.5); letter-spacing:0.01em;">
          <div style="color:rgba(255,255,255,0.72); font-weight:600; letter-spacing:0.08em; font-size:11px; text-transform:uppercase; margin-bottom:6px;">Revelation Agency</div>
          <div>55 Shaw Ave. #201</div>
          <div>Clovis, CA 93612</div>
          <div style="margin-top:6px; font-style:italic; color:rgba(255,255,255,0.55);">We work remotely across the globe.</div>
        </address>
      </div>

      <div class="ra-footer__nav ra-footer__nav--services">
        <h5>Services</h5>
        <ul class="ra-footer__svc">
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="{p}services/branding/index.html">Branding<span class="ra-footer__svc-caret" aria-hidden="true">&#9662;</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="{p}services/branding/brand-strategy-identity.html">Brand Strategy &amp; Identity</a></li>
              <li><a href="{p}services/branding/websites-landing-pages.html">Websites &amp; Landing Pages</a></li>
              <li><a href="{p}services/branding/apps-digital-products.html">Apps &amp; Digital Products</a></li>
              <li><a href="{p}services/branding/video-visual-content.html">Video &amp; Visual Content</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="{p}services/marketing/index.html">Marketing<span class="ra-footer__svc-caret" aria-hidden="true">&#9662;</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="{p}services/marketing/seo-ai-visibility.html">SEO &amp; AI Visibility</a></li>
              <li><a href="{p}services/marketing/positioning-content-authority.html">Positioning, Content &amp; Authority</a></li>
              <li><a href="{p}services/marketing/social-media.html">Social Media</a></li>
              <li><a href="{p}services/marketing/email-lifecycle-marketing.html">Email &amp; Lifecycle Marketing</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="{p}services/sales/index.html">Sales<span class="ra-footer__svc-caret" aria-hidden="true">&#9662;</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="{p}services/sales/lead-generation-outreach.html">Lead Generation &amp; Outreach</a></li>
              <li><a href="{p}services/sales/crm-sales-infrastructure.html">CRM &amp; Sales Infrastructure</a></li>
              <li><a href="{p}services/sales/follow-up-nurture.html">Follow-up &amp; Nurture</a></li>
              <li><a href="{p}services/sales/conversion-advertising.html">Conversion Advertising</a></li>
            </ul>
          </li>
        </ul>
      </div>

      <div class="ra-footer__nav">
        <h5>Connect</h5>
        <ul>
          <li><a href="{p}the-reveal/index.html">The Reveal</a></li>
          <li><a href="{p}portfolio.html">Portfolio</a></li>
          <li><a href="{p}contact.html">Contact</a></li>
          <li><a href="tel:+15592017039">(559) 201-7039</a></li>
          <li><a href="mailto:connect@revelationagency.com">connect@revelationagency.com</a></li>
        </ul>
      </div>

      <div class="ra-footer__cta">
        <h4>Ready to build the machine behind growth?</h4>
        <p>Book a free strategy session. We'll audit what you have, name what's missing, and prescribe the smallest next step.</p>
        <a href="{p}booking.html" class="btn btn--primary" style="width:100%; justify-content:center;">Book a Strategy Session <i class="fa-solid fa-arrow-right btn-arrow"></i></a>
      </div>
    </div>

    <div class="ra-footer__bottom">
      <p class="ra-footer__copyright">&copy; 2026 <a href="{p}index.html">Revelation Agency</a>. Branding. Marketing. Sales.</p>
    </div>
  </div>
</footer>
{FOOTER_END}"""


def inject_footer(text: str, prefix: str) -> Tuple[str, bool]:
    """Replace the empty <!-- RA-FOOTER-CANONICAL-START -->…<!-- END --> block
    with the canonical footer. Idempotent: if the block already contains a
    non-empty <footer>, we regenerate to keep the prefix / labels current."""
    start = text.find(FOOTER_START)
    end = text.find(FOOTER_END)
    if start == -1 or end == -1 or end < start:
        return text, False
    new_block = canonical_footer(prefix)
    new_text = text[:start] + new_block + text[end + len(FOOTER_END):]
    return new_text, new_text != text


# ------------------------------------------------------------------ Fix 3: baseline footer label swap

# The exact legacy service-list block that appears in every one of the 9
# baseline pages, byte-identical. Preserving the exact bytes lets us swap
# it out safely without ambiguity and without touching the surrounding
# miniform / webhook / iframe integrations.
LEGACY_SVC_BLOCK_VARIANTS: List[str] = [
    # Homepage variant — <li> labels include "Brand Strategy" instead of
    # "Brand Systems" (real drift between homepage and other pages).
    """        <ul class="ra-footer__svc">
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/systems/">Systems<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/systems/brand-systems.html">Brand Strategy</a></li>
              <li><a href="services/systems/ai-automation.html">AI &amp; Automation</a></li>
              <li><a href="services/systems/digital-presence.html">Websites</a></li>
              <li><a href="services/systems/sales-infrastructure.html">CRM &amp; Sales Infra</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/creative/">Creative<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/creative/branding.html">Branding</a></li>
              <li><a href="services/creative/video-production.html">Video Production</a></li>
              <li><a href="services/creative/website-development.html">Website Development</a></li>
              <li><a href="services/creative/app-development.html">App Development</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/marketing/">Marketing<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/marketing/digital-ads.html">Digital Ads</a></li>
              <li><a href="services/marketing/social-media.html">Social Media</a></li>
              <li><a href="services/marketing/search-rankings.html">Search Rankings</a></li>
              <li><a href="services/marketing/outsource-marketing.html">Outsource Marketing</a></li>
            </ul>
          </li>
        </ul>""",
    # About / contact / faq / services / portfolio / booking / web-hosting / 404
    # — Systems row uses "Brand Systems" for the first child.
    """        <ul class="ra-footer__svc">
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/systems/">Systems<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/systems/brand-systems.html">Brand Systems</a></li>
              <li><a href="services/systems/ai-automation.html">AI &amp; Automation</a></li>
              <li><a href="services/systems/digital-presence.html">Digital Presence</a></li>
              <li><a href="services/systems/sales-infrastructure.html">Sales Infrastructure</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/creative/">Creative<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/creative/branding.html">Branding</a></li>
              <li><a href="services/creative/video-production.html">Video Production</a></li>
              <li><a href="services/creative/website-development.html">Website Development</a></li>
              <li><a href="services/creative/app-development.html">App Development</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/marketing/">Marketing<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/marketing/digital-ads.html">Digital Ads</a></li>
              <li><a href="services/marketing/social-media.html">Social Media</a></li>
              <li><a href="services/marketing/search-rankings.html">Search Rankings</a></li>
              <li><a href="services/marketing/outsource-marketing.html">Outsource Marketing</a></li>
            </ul>
          </li>
        </ul>""",
]

# The canonical Branding / Marketing / Sales service list — identical for
# every baseline page (all baseline pages sit at repo root, no prefix).
CANONICAL_SVC_BLOCK: str = """        <ul class="ra-footer__svc">
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/branding/index.html">Branding<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/branding/brand-strategy-identity.html">Brand Strategy &amp; Identity</a></li>
              <li><a href="services/branding/websites-landing-pages.html">Websites &amp; Landing Pages</a></li>
              <li><a href="services/branding/apps-digital-products.html">Apps &amp; Digital Products</a></li>
              <li><a href="services/branding/video-visual-content.html">Video &amp; Visual Content</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/marketing/index.html">Marketing<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/marketing/seo-ai-visibility.html">SEO &amp; AI Visibility</a></li>
              <li><a href="services/marketing/positioning-content-authority.html">Positioning, Content &amp; Authority</a></li>
              <li><a href="services/marketing/social-media.html">Social Media</a></li>
              <li><a href="services/marketing/email-lifecycle-marketing.html">Email &amp; Lifecycle Marketing</a></li>
            </ul>
          </li>
          <li class="ra-footer__svc-group">
            <a class="ra-footer__svc-parent" href="services/sales/index.html">Sales<span class="ra-footer__svc-caret" aria-hidden="true">▾</span></a>
            <ul class="ra-footer__svc-children">
              <li><a href="services/sales/lead-generation-outreach.html">Lead Generation &amp; Outreach</a></li>
              <li><a href="services/sales/crm-sales-infrastructure.html">CRM &amp; Sales Infrastructure</a></li>
              <li><a href="services/sales/follow-up-nurture.html">Follow-up &amp; Nurture</a></li>
              <li><a href="services/sales/conversion-advertising.html">Conversion Advertising</a></li>
            </ul>
          </li>
        </ul>"""


def swap_baseline_service_list(text: str) -> Tuple[str, bool]:
    """Idempotent swap: legacy Systems/Creative/Marketing block -> canonical."""
    if CANONICAL_SVC_BLOCK in text:
        return text, False
    for legacy in LEGACY_SVC_BLOCK_VARIANTS:
        if legacy in text:
            return text.replace(legacy, CANONICAL_SVC_BLOCK, 1), True
    return text, False


# ------------------------------------------------------------------ main

def main() -> int:
    raise SystemExit(
        "DEPRECATED: this repair emits retired Systems/Creative markup. "
        "Run apply_2026_site_refresh.py and apply_2026_portfolio_taxonomy.py instead."
    )
    css_file = "assets/css/ra-nav-footer.css"
    if not os.path.exists(css_file):
        print(f"[FAIL] shared CSS file missing: {css_file}")
        return 2
    print(f"[OK]   shared CSS present: {css_file} "
          f"({os.path.getsize(css_file)} bytes, sha16={sha16(read(css_file))})")

    report: Dict[str, List[str]] = {"css_linked": [], "footer_injected": [],
                                    "svc_block_swapped": [], "skipped_noop": []}

    # ---- 19 pillar pages: link CSS + inject footer ----
    for rel in PILLAR_PAGES:
        if not os.path.exists(rel):
            print(f"[WARN] pillar page missing on disk: {rel}")
            continue
        text = read(rel)
        prefix = depth_prefix(rel)
        text, css_changed = inject_shared_css_link(text, prefix)
        text, footer_changed = inject_footer(text, prefix)
        if css_changed or footer_changed:
            write(rel, text)
            if css_changed:
                report["css_linked"].append(rel)
            if footer_changed:
                report["footer_injected"].append(rel)
        else:
            report["skipped_noop"].append(rel)

    # ---- 9 baseline pages: swap legacy service labels ----
    for rel in BASELINE_PAGES:
        if not os.path.exists(rel):
            print(f"[WARN] baseline page missing on disk: {rel}")
            continue
        text = read(rel)
        text, changed = swap_baseline_service_list(text)
        if changed:
            write(rel, text)
            report["svc_block_swapped"].append(rel)
        else:
            report["skipped_noop"].append(rel)

    print()
    print(f"CSS linked into pillar pages   : {len(report['css_linked'])}")
    print(f"Footer injected on pillar pages: {len(report['footer_injected'])}")
    print(f"Service block swapped baseline : {len(report['svc_block_swapped'])}")
    print(f"Skipped (already canonical)    : {len(report['skipped_noop'])}")
    for k in ("css_linked", "footer_injected", "svc_block_swapped"):
        for p in report[k]:
            print(f"  [{k}] {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
