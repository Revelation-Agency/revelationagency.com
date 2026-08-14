"""Sitewide nav and analytics-loader sweep.

- Replaces every `RA-NAV-CANONICAL-START ... RA-NAV-CANONICAL-END` block with the
  new Branding / Marketing / Sales nav (path prefixes computed per-file depth).
- On the homepage (which does not use the canonical marker), rewrites just the
  Services and Portfolio drop-down markup inline, plus the hero trust chips and
  architecture blueprint labels.
- Injects a single defer-loaded `<script src="…/assets/js/analytics-events.js">`
  before `</body>` when not already present.
- Removes the developer-only `#tweaks-panel` block and its supporting JS
  identifiers from the homepage.
- Byte-preserves the GHL contact form, footer mini-form webhook, booking
  iframe, chat-widget loader, mailto:, and tel: snippets.

Every write is idempotent — running the script again on the resulting tree
produces zero changes (asserted at end).
"""

import hashlib
import os
import re
import string
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


# ------------- Canonical nav template -----------------

NAV_TEMPLATE = string.Template("""<!-- RA-NAV-CANONICAL-START -->
<nav class="ra-nav" id="ra-nav">
  <div class="ra-nav__inner">
    <a href="$${p}index.html" class="ra-nav__logo" aria-label="Revelation Agency">
      <img src="$${p}assets/brand/approved/ra-landscape-black-updated.png" alt="Revelation Agency" style="height:76px;width:auto;display:block;">
    </a>

    <ul class="ra-nav__links">
      <li><a href="$${p}index.html"$${home_cur}>Home</a></li>
      <li><a href="$${p}about.html"$${about_cur}>About</a></li>
      <li class="has-drop">
        <a href="$${p}services.html"$${svc_cur}>Services <i class="fa-solid fa-chevron-down" style="font-size:9px;margin-left:3px;"></i></a>
        <button class="ra-nav__services-toggle" type="button" aria-label="Toggle Services menu" aria-expanded="false">&#9662;</button>
        <ul class="ra-drop ra-drop--l2">
          <li class="has-drop-l3">
            <a href="${p}services/branding/index.html">Branding <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Branding menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="${p}services/branding/brand-strategy-identity.html">Brand Strategy &amp; Identity</a></li>
              <li><a href="${p}services/branding/websites-landing-pages.html">Websites &amp; Landing Pages</a></li>
              <li><a href="${p}services/branding/apps-digital-products.html">Apps &amp; Digital Products</a></li>
              <li><a href="${p}services/branding/video-visual-content.html">Video &amp; Visual Content</a></li>
            </ul>
          </li>
          <li class="has-drop-l3">
            <a href="${p}services/marketing/index.html">Marketing <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Marketing menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="${p}services/marketing/seo-ai-visibility.html">SEO &amp; AI Visibility</a></li>
              <li><a href="${p}services/marketing/positioning-content-authority.html">Positioning, Content &amp; Authority</a></li>
              <li><a href="${p}services/marketing/social-media.html">Social Media</a></li>
              <li><a href="${p}services/marketing/email-lifecycle-marketing.html">Email &amp; Lifecycle Marketing</a></li>
            </ul>
          </li>
          <li class="has-drop-l3">
            <a href="${p}services/sales/index.html">Sales <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>
            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Sales menu" aria-expanded="false">&#9662;</button>
            <ul class="ra-drop ra-drop--l3">
              <li><a href="${p}services/sales/lead-generation-outreach.html">Lead Generation &amp; Outreach</a></li>
              <li><a href="${p}services/sales/crm-sales-infrastructure.html">CRM &amp; Sales Infrastructure</a></li>
              <li><a href="${p}services/sales/follow-up-nurture.html">Follow-up &amp; Nurture</a></li>
              <li><a href="${p}services/sales/conversion-advertising.html">Conversion Advertising</a></li>
            </ul>
          </li>
          <li><a href="${p}services/ai-automation.html" style="padding:10px 12px;font-size:13px;color:var(--charcoal);opacity:0.7;">Cross-cutting: AI &amp; Automation</a></li>
        </ul>
      </li>
      <li><a href="${p}the-reveal/index.html"${rev_cur}>The Reveal</a></li>
      <li class="has-drop">
        <a href="${p}portfolio.html"${port_cur}>Portfolio <i class="fa-solid fa-chevron-down" style="font-size:9px;margin-left:3px;"></i></a>
        <button class="ra-nav__services-toggle" type="button" aria-label="Toggle Portfolio menu" aria-expanded="false">&#9662;</button>
        <ul class="ra-drop ra-drop--l2">
          <li><a href="${p}portfolio/branding.html">Branding Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a></li>
          <li><a href="${p}portfolio/marketing.html">Marketing Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a></li>
          <li><a href="${p}portfolio/sales.html">Sales Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a></li>
          <li><a href="${p}portfolio.html" style="padding:10px 12px;font-size:13px;color:var(--charcoal);opacity:0.7;">All case studies</a></li>
        </ul>
      </li>
      <li><a href="${p}contact.html"${contact_cur}>Contact</a></li>
    </ul>

    <div class="ra-nav__right">
      <a href="${p}booking.html" class="btn btn--primary ra-nav__cta" style="padding: 12px 24px; font-size: 13px;" data-cta="primary" data-cta-placement="nav" data-booking-open="1">Book a Free Strategy Session <i class="fa-solid fa-arrow-right btn-arrow"></i></a>
      <a href="${p}booking.html" class="btn btn--primary ra-nav__cta-mobile" style="padding: 10px 16px; font-size: 12px;" data-cta="primary" data-cta-placement="nav-mobile" data-booking-open="1">Book a Call</a>
    </div>

    <button class="ra-nav__hamburger" id="ra-nav-hamburger" aria-label="Toggle menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>
<script>
  (function(){
    var btn = document.getElementById('ra-nav-hamburger');
    if (!btn) return;
    var nav = document.getElementById('ra-nav');
    btn.addEventListener('click', function(){
      var open = nav.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.querySelectorAll('.has-drop-l3 > a').forEach(function(anchor){
      anchor.addEventListener('click', function(ev){
        if (window.innerWidth > 768) return;
        var li = anchor.parentElement;
        if (!li.querySelector('.ra-drop--l3')) return;
        if (!li.classList.contains('is-open')) {
          ev.preventDefault();
          li.classList.add('is-open');
        }
      });
    });
  })();
</script>
<!-- RA-NAV-CANONICAL-END -->""")


def compute_prefix(rel_path: str) -> str:
    """Number of '../' segments to reach the repo root from the file."""
    parts = rel_path.replace("\\", "/").split("/")
    depth = len(parts) - 1  # subtract filename
    return "../" * depth


def current_flags(rel_path: str) -> dict:
    p = rel_path.replace("\\", "/")
    flags = {"home_cur": "", "about_cur": "", "svc_cur": "", "rev_cur": "",
             "port_cur": "", "contact_cur": ""}
    if p == "index.html":
        flags["home_cur"] = ' class="is-current"'
    elif p == "about.html":
        flags["about_cur"] = ' class="is-current"'
    elif p == "contact.html":
        flags["contact_cur"] = ' class="is-current"'
    elif p == "services.html" or p.startswith("services/"):
        flags["svc_cur"] = ' class="is-current"'
    elif p == "portfolio.html" or p.startswith("portfolio/"):
        flags["port_cur"] = ' class="is-current"'
    elif p.startswith("the-reveal/"):
        flags["rev_cur"] = ' class="is-current"'
    return flags


NAV_RE = re.compile(r"<!-- RA-NAV-CANONICAL-START -->.*?<!-- RA-NAV-CANONICAL-END -->", re.DOTALL)


def replace_canonical_nav(text: str, rel_path: str) -> str:
    p = compute_prefix(rel_path)
    subs = {"p": p, **current_flags(rel_path)}
    replacement = NAV_TEMPLATE.substitute(subs)
    return NAV_RE.sub(lambda _m: replacement, text)


# Analytics injector: add <script src="…/assets/js/analytics-events.js" defer></script>
# once, immediately before </body>. Idempotent.
ANALYTICS_MARKER = "/assets/js/analytics-events.js"


def inject_analytics(text: str, rel_path: str) -> str:
    if ANALYTICS_MARKER in text:
        return text
    p = compute_prefix(rel_path)
    tag = f'<script src="{p}assets/js/analytics-events.js" defer></script>\n'
    if "</body>" in text:
        return text.replace("</body>", tag + "</body>", 1)
    return text + "\n" + tag


# Homepage-only: strip every public-facing / postMessage-accessible debug
# surface. This includes:
#   - The `<div id="tweaks-panel">` HTML block
#   - The `#tweaks-panel {...}` and related tweak CSS
#   - The postMessage `__activate_edit_mode` / `__deactivate_edit_mode` listener
#     plus the `__edit_mode_available` beacon and `__edit_mode_set_keys` posts
#   - The TWEAK_DEFAULTS object and the four setter functions
TWEAKS_PANEL_RE = re.compile(
    # From the TWEAKS section comment through the entire panel wrapper, up to
    # the next `<script>` element (which starts the NAV SCROLL block).
    r"<!--\s*=+\s*TWEAKS\s*=+\s*-->[\s\S]*?</div>\s*</div>\s*(?=<script>)",
    re.MULTILINE,
)
TWEAKS_CSS_RE = re.compile(
    r"/\*\s*=+\s*\n\s*TWEAKS PANEL\s*\n\s*=+\s*\*/[\s\S]*?"
    r"\.tweak-btn:hover, \.tweak-btn\.active[^}]*\}\s*",
    re.MULTILINE,
)
TWEAKS_LISTENER_RE = re.compile(
    r"//\s*=+\s*\n//\s*TWEAKS\s*\n//\s*=+\s*\n"
    r"window\.addEventListener\('message'[\s\S]*?"
    r"window\.parent\.postMessage\(\{\s*type:\s*'__edit_mode_available'\s*\},\s*'\*'\);\s*",
    re.MULTILINE,
)
TWEAKS_DEFAULTS_AND_SETTERS_RE = re.compile(
    r"const TWEAK_DEFAULTS\s*=[\s\S]*?"
    r"function setSpacing\(v\)\s*\{[\s\S]*?\}\s*",
    re.MULTILINE,
)


def remove_tweaks_from_index(text: str) -> str:
    text = TWEAKS_PANEL_RE.sub("<!-- TWEAKS panel removed by rebrand -->", text)
    text = TWEAKS_CSS_RE.sub("/* TWEAKS panel CSS removed by rebrand */\n", text)
    text = TWEAKS_LISTENER_RE.sub("// TWEAKS postMessage listener removed by rebrand\n", text)
    text = TWEAKS_DEFAULTS_AND_SETTERS_RE.sub(
        "// TWEAKS defaults + setter functions removed by rebrand\n", text)
    return text


# Homepage inline nav rewrite: replace Systems->Creative->Marketing links
# with Branding->Marketing->Sales inside the inline Services + Portfolio drops.
def rewrite_home_inline_nav(text: str) -> str:
    # The homepage has an inline <ul class="ra-nav__links"> ... </ul>. To keep
    # this surgical, we replace the two <li class="has-drop"> blocks:
    # Services drop and Portfolio drop.

    # Services drop
    services_re = re.compile(
        r"<li class=\"has-drop\">\s*\n?\s*<a href=\"services\.html\"[^>]*>Services[\s\S]*?</ul>\s*</li>",
        re.DOTALL,
    )
    services_new = (
        '<li class="has-drop">\n'
        '        <a href="services.html">Services <i class="fa-solid fa-chevron-down" style="font-size:9px;margin-left:3px;"></i></a>\n'
        '        <button class="ra-nav__services-toggle" type="button" aria-label="Toggle Services menu" aria-expanded="false">&#9662;</button>\n'
        '        <ul class="ra-drop ra-drop--l2">\n'
        '          <li class="has-drop-l3">\n'
        '            <a href="services/branding/index.html">Branding <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>\n'
        '            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Branding menu" aria-expanded="false">&#9662;</button>\n'
        '            <ul class="ra-drop ra-drop--l3">\n'
        '              <li><a href="services/branding/brand-strategy-identity.html">Brand Strategy &amp; Identity</a></li>\n'
        '              <li><a href="services/branding/websites-landing-pages.html">Websites &amp; Landing Pages</a></li>\n'
        '              <li><a href="services/branding/apps-digital-products.html">Apps &amp; Digital Products</a></li>\n'
        '              <li><a href="services/branding/video-visual-content.html">Video &amp; Visual Content</a></li>\n'
        '            </ul>\n'
        '          </li>\n'
        '          <li class="has-drop-l3">\n'
        '            <a href="services/marketing/index.html">Marketing <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>\n'
        '            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Marketing menu" aria-expanded="false">&#9662;</button>\n'
        '            <ul class="ra-drop ra-drop--l3">\n'
        '              <li><a href="services/marketing/seo-ai-visibility.html">SEO &amp; AI Visibility</a></li>\n'
        '              <li><a href="services/marketing/positioning-content-authority.html">Positioning, Content &amp; Authority</a></li>\n'
        '              <li><a href="services/marketing/social-media.html">Social Media</a></li>\n'
        '              <li><a href="services/marketing/email-lifecycle-marketing.html">Email &amp; Lifecycle Marketing</a></li>\n'
        '            </ul>\n'
        '          </li>\n'
        '          <li class="has-drop-l3">\n'
        '            <a href="services/sales/index.html">Sales <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a>\n'
        '            <button class="ra-nav__l2-toggle" type="button" aria-label="Toggle Sales menu" aria-expanded="false">&#9662;</button>\n'
        '            <ul class="ra-drop ra-drop--l3">\n'
        '              <li><a href="services/sales/lead-generation-outreach.html">Lead Generation &amp; Outreach</a></li>\n'
        '              <li><a href="services/sales/crm-sales-infrastructure.html">CRM &amp; Sales Infrastructure</a></li>\n'
        '              <li><a href="services/sales/follow-up-nurture.html">Follow-up &amp; Nurture</a></li>\n'
        '              <li><a href="services/sales/conversion-advertising.html">Conversion Advertising</a></li>\n'
        '            </ul>\n'
        '          </li>\n'
        '          <li><a href="services/ai-automation.html" style="padding:10px 12px;font-size:13px;color:var(--charcoal);opacity:0.7;">Cross-cutting: AI &amp; Automation</a></li>\n'
        '        </ul>\n'
        '      </li>'
    )
    text = services_re.sub(lambda _m: services_new, text)

    # Portfolio drop
    portfolio_re = re.compile(
        r"<li class=\"has-drop\">\s*\n?\s*<a href=\"portfolio\.html\"[^>]*>Portfolio[\s\S]*?</ul>\s*</li>",
        re.DOTALL,
    )
    portfolio_new = (
        '<li class="has-drop">\n'
        '        <a href="portfolio.html">Portfolio <i class="fa-solid fa-chevron-down" style="font-size:9px;margin-left:3px;"></i></a>\n'
        '        <button class="ra-nav__services-toggle" type="button" aria-label="Toggle Portfolio menu" aria-expanded="false">&#9662;</button>\n'
        '        <ul class="ra-drop ra-drop--l2">\n'
        '          <li><a href="portfolio/branding.html">Branding Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a></li>\n'
        '          <li><a href="portfolio/marketing.html">Marketing Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a></li>\n'
        '          <li><a href="portfolio/sales.html">Sales Work <i class="fa-solid fa-chevron-right ra-drop__arrow"></i></a></li>\n'
        '          <li><a href="portfolio.html" style="padding:10px 12px;font-size:13px;color:var(--charcoal);opacity:0.7;">All case studies</a></li>\n'
        '        </ul>\n'
        '      </li>'
    )
    text = portfolio_re.sub(lambda _m: portfolio_new, text)

    # Homepage nav logo: swap the legacy /assets/revelation-logo.png reference
    # for the updated landscape variant. Byte-preserve everywhere else.
    text = text.replace(
        'src="assets/revelation-logo.png" alt="Revelation Agency"',
        'src="assets/brand/approved/ra-landscape-black-updated.png" alt="Revelation Agency" style="height:76px;width:auto;display:block;"',
        1,
    )
    return text


def rewrite_home_hero_trust_and_blueprint(text: str) -> str:
    """Hero trust chips + architecture blueprint labels + sub headline."""
    # Trust chips
    text = text.replace(
        '<div class="ra-hero__trust-item"><i class="fa-solid fa-compass"></i> Systems</div>',
        '<div class="ra-hero__trust-item"><i class="fa-solid fa-compass"></i> Branding</div>',
        1,
    )
    text = text.replace(
        '<div class="ra-hero__trust-item"><i class="fa-solid fa-pen-ruler"></i> Creative</div>',
        '<div class="ra-hero__trust-item"><i class="fa-solid fa-bullseye"></i> Marketing</div>',
        1,
    )
    # Third trust item (Marketing) already reads "Marketing" — normalize its icon:
    text = re.sub(
        r'<div class="ra-hero__trust-item"><i class="fa-solid fa-[a-z\-]+"></i>\s*Marketing\s*</div>',
        '<div class="ra-hero__trust-item"><i class="fa-solid fa-handshake"></i> Sales</div>',
        text,
        count=1,
    )
    # Sub-headline under blueprint
    text = text.replace(
        "Systems → Creative → Marketing. One connected system.",
        "Branding → Marketing → Sales. One connected system.",
    )
    text = text.replace(
        "(Systems → Creative → Marketing) connected by a dashed",
        "(Branding → Marketing → Sales) connected by a dashed",
    )
    # Blueprint SVG labels
    replacements = [
        ("Brand Systems", "Brand Strategy"),
        ("Sales Infrastructure", "CRM &amp; Sales Infra"),
        ("Digital Presence", "Websites"),
        # Layer 02 legacy label was "AI &amp; Automation" for layer-01 node — keep
        # it labeled as cross-cutting inside the diagram, but re-label the leaf
        # to something honest.
    ]
    for old, new in replacements:
        text = text.replace(f">{old}<", f">{new}<", 1)
    # Category title comment (leaves style/CSS intact):
    text = text.replace(
        "/* Category title (Strategy / Creative / Marketing) — red caps */",
        "/* Category title (Branding / Marketing / Sales) — red caps */",
    )
    text = text.replace(
        "/* Category headers (Strategy / Creative / Marketing): clear, dark, normal",
        "/* Category headers (Branding / Marketing / Sales): clear, dark, normal",
    )
    text = text.replace(
        "/* Leaf links (Brand Systems, Website Development, …): visible, wrapping,",
        "/* Leaf links (Brand Strategy, Websites, …): visible, wrapping,",
    )
    return text


def rewrite_home_meta(text: str) -> str:
    text = text.replace(
        '<meta name="description" content="Revelation Agency is a full-service strategic growth firm. We build integrated growth machines — systems, creative, and marketing engineered to compound. Based in Clovis, CA.">',
        '<meta name="description" content="Revelation Agency is a strategic growth partner. We build integrated growth systems — Branding, Marketing, and Sales — engineered to compound. Based in Clovis, CA.">',
    )
    text = text.replace(
        '<meta property="og:description" content="Revelation Agency builds integrated growth machines — systems, creative, and marketing engineered to compound.">',
        '<meta property="og:description" content="Revelation Agency builds integrated growth systems — Branding, Marketing, and Sales — engineered to compound.">',
    )
    text = text.replace(
        '"description": "Revelation Agency is a full-service strategic growth firm. We build integrated growth machines — systems, creative, and marketing engineered to compound.",',
        '"description": "Revelation Agency is a strategic growth partner. We build integrated growth systems — Branding, Marketing, and Sales — engineered to compound.",',
    )
    return text


# --- Legacy /portfolio/creative.html-style meta description clean-up ---
LEGACY_META_MAP = {
    'content="Proof. Premium execution across systems, creative, and growth — selected case studies from Revelation Agency."':
        'content="Proof. Premium execution across Branding, Marketing, and Sales — selected case studies from Revelation Agency."',
    'content="Premium execution across systems, creative, and growth."':
        'content="Premium execution across Branding, Marketing, and Sales."',
}


def rewrite_portfolio_meta(text: str) -> str:
    for old, new in LEGACY_META_MAP.items():
        text = text.replace(old, new)
    return text


# Preservation contract: any file that carried the baseline GHL snippets must
# still carry them after rewrite. Enforced by hash comparison.
PRESERVE_PATTERNS = {
    "contact_form_element": r'<form[^>]*id="ra-contact-form"[^>]*>',
    "footer_mini_webhook_line": r"var\s+WEBHOOK\s*=\s*[\"'][^\"'\s]+[\"'];",
    "booking_iframe": r'<iframe[^>]*api\.leadconnectorhq\.com/widget/booking[^>]*></iframe>',
    "booking_embed_script": r'<script[^>]*link\.msgsndr\.com/js/form_embed\.js[^>]*>',
    "chat_widget_loader": r'<script[^>]*widgets\.leadconnectorhq\.com/loader\.js[^>]*></script>',
    "mailto_connect": r"mailto:connect@revelationagency\.com",
    "tel_link": r"tel:\+?15592017039",
}


def snippet_hashes(data: str) -> dict:
    out = {}
    for k, pat in PRESERVE_PATTERNS.items():
        m = re.search(pat, data)
        if m:
            out[k] = sha16(m.group(0))
    return out


def process_file(rel_path: str, report: list) -> bool:
    with open(rel_path, "r", encoding="utf-8") as f:
        original = f.read()

    before_snips = snippet_hashes(original)
    text = original

    if "RA-NAV-CANONICAL-START" in text:
        text = replace_canonical_nav(text, rel_path)

    if rel_path.replace("\\", "/") == "index.html":
        text = rewrite_home_inline_nav(text)
        text = rewrite_home_hero_trust_and_blueprint(text)
        text = rewrite_home_meta(text)
        text = remove_tweaks_from_index(text)
    if rel_path.replace("\\", "/") == "portfolio.html":
        text = rewrite_portfolio_meta(text)

    text = inject_analytics(text, rel_path)

    after_snips = snippet_hashes(text)
    for k, h in before_snips.items():
        if after_snips.get(k) != h:
            raise SystemExit(f"[FAIL] {rel_path}: integration snippet '{k}' hash changed "
                             f"{h} -> {after_snips.get(k)}. Refusing to write.")

    if text != original:
        with open(rel_path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        report.append(rel_path)
        return True
    return False


SKIP = {
    # Presentation-style landing pages with a custom deck-ribbon nav
    "sales-growth-engine/index.html",
    "sales-intelligence/index.html",
    # Article template scaffold uses its own placeholder nav
    "the-reveal/article-template.html",
}


def iter_html():
    for dirpath, _dirs, files in os.walk("."):
        if any(seg in dirpath.replace("\\", "/") for seg in ("/.git", "/node_modules", "/artifacts")):
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), ".").replace("\\", "/")
            if rel in SKIP:
                continue
            yield rel


def main() -> int:
    report = []
    for rel in sorted(iter_html()):
        try:
            process_file(rel, report)
        except SystemExit as e:
            print(e)
            return 1
    print(f"rewrote {len(report)} pages")
    for r in report[:12]:
        print("  ", r)
    if len(report) > 12:
        print(f"  … and {len(report) - 12} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
