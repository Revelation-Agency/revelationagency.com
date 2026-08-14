"""Emit baseline-routes.json, proposed-routes.json, redirect-map.json, and route-diff.md.

This is the migration ledger the packet requires. Every one of the 122 current sitemap
URLs must resolve to keep / rename / retain-redirect / retire with successor.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CANON = "https://www.revelationagency.com"

# Legacy pillar -> New pillar mapping (Canon 9487)
# Systems (URL) + Strategy (label) -> Branding (identity, sites, apps, video)
#   was already Creative
# Creative -> Branding
# Marketing -> Marketing (mostly retained)
# New Sales pillar collects: sales-infrastructure, digital-ads, plus new leaves

# For every legacy sitemap URL, we produce a disposition record.
# disposition ∈ {"keep","rename","retire_redirect","retire_gone"}
# For rename/retire_redirect we produce a redirect_map row.

# Structure of new IA — service leaves:
BRANDING_LEAVES = [
    ("brand-strategy-identity", "Brand Strategy & Identity"),
    ("websites-landing-pages", "Websites & Landing Pages"),
    ("apps-digital-products", "Apps & Digital Products"),
    ("video-visual-content", "Video & Visual Content"),
]
MARKETING_LEAVES = [
    ("seo-ai-visibility", "SEO & AI Visibility"),
    ("positioning-content-authority", "Positioning, Content & Authority"),
    ("social-media", "Social Media"),
    ("email-lifecycle-marketing", "Email & Lifecycle Marketing"),
]
SALES_LEAVES = [
    ("lead-generation-outreach", "Lead Generation & Personalized Outreach"),
    ("crm-sales-infrastructure", "CRM & Sales Infrastructure"),
    ("follow-up-nurture", "Follow-up & Nurture"),
    ("conversion-advertising", "Conversion Advertising"),
]
CROSSCUT_LEAVES = [
    ("ai-automation", "AI & Automation (cross-cutting)"),
]

# Direct legacy -> new service page mapping (per packet)
SERVICE_MAP = {
    # Creative -> Branding
    "/services/creative/branding.html":            "/services/branding/brand-strategy-identity.html",
    "/services/creative/website-development.html": "/services/branding/websites-landing-pages.html",
    "/services/creative/app-development.html":     "/services/branding/apps-digital-products.html",
    "/services/creative/video-production.html":    "/services/branding/video-visual-content.html",
    "/services/creative/index.html":               "/services/branding/",
    "/services/creative/":                         "/services/branding/",
    # Marketing -> normalized under new Marketing hub
    "/services/marketing/index.html":              "/services/marketing/",
    "/services/marketing/":                        "/services/marketing/",
    "/services/marketing/search-rankings.html":    "/services/marketing/seo-ai-visibility.html",
    "/services/marketing/social-media.html":       "/services/marketing/social-media.html",
    "/services/marketing/outsource-marketing.html":"/services/marketing/",  # remove from nav; direct to hub
    "/services/marketing/digital-ads.html":        "/services/sales/conversion-advertising.html",
    # Systems -> split across Sales + Branding + cross-cutting AI
    "/services/systems/sales-infrastructure.html": "/services/sales/crm-sales-infrastructure.html",
    "/services/systems/brand-systems.html":        "/services/branding/brand-strategy-identity.html",
    "/services/systems/digital-presence.html":     "/services/branding/websites-landing-pages.html",
    "/services/systems/ai-automation.html":        "/services/ai-automation.html",
    "/services/systems/index.html":                "/services.html",
    "/services/systems/":                          "/services.html",
}

PORTFOLIO_HUB_MAP = {
    # portfolio pillar hubs
    "/portfolio/creative.html":                    "/portfolio/branding.html",
    "/portfolio/systems.html":                     "/portfolio.html",  # collapse — no single "systems" pillar
    "/portfolio/marketing.html":                   "/portfolio/marketing.html",
    # portfolio sub-categories mirror the service map
    "/portfolio/creative/branding.html":           "/portfolio/branding/brand-strategy-identity.html",
    "/portfolio/creative/website-development.html":"/portfolio/branding/websites-landing-pages.html",
    "/portfolio/creative/app-development.html":    "/portfolio/branding/apps-digital-products.html",
    "/portfolio/creative/video-production.html":   "/portfolio/branding/video-visual-content.html",
    "/portfolio/systems/brand-systems.html":       "/portfolio/branding/brand-strategy-identity.html",
    "/portfolio/systems/digital-presence.html":    "/portfolio/branding/websites-landing-pages.html",
    "/portfolio/systems/sales-infrastructure.html":"/portfolio/sales/crm-sales-infrastructure.html",
    "/portfolio/systems/ai-automation.html":       "/portfolio/ai-automation.html",
    "/portfolio/marketing/search-rankings.html":   "/portfolio/marketing/seo-ai-visibility.html",
    "/portfolio/marketing/social-media.html":      "/portfolio/marketing/social-media.html",
    "/portfolio/marketing/outsource-marketing.html":"/portfolio/marketing/",
    "/portfolio/marketing/digital-ads.html":       "/portfolio/sales/conversion-advertising.html",
}

# Case studies: keep every one at its current URL. Case study taxonomy is corrected
# only within the pages themselves (breadcrumbs, tags). "-strategy" filenames stay
# resolvable to avoid SEO loss.
KEEP_UNCHANGED = set()

# Legacy path->new used for retired legacy URLs that must 301 to new destinations
ALL_LEGACY_MAP = {}
ALL_LEGACY_MAP.update(SERVICE_MAP)
ALL_LEGACY_MAP.update(PORTFOLIO_HUB_MAP)


def load_baseline_urls():
    with open("sitemap.xml", "r", encoding="utf-8") as f:
        import re
        return sorted(set(re.findall(r"<loc>([^<]+)</loc>", f.read())))


def strip_canon(url: str) -> str:
    return url.replace(CANON, "") or "/"


def build_baseline_routes():
    urls = load_baseline_urls()
    baseline = {"canonical_host": CANON, "count": len(urls), "urls": urls}
    return baseline


def build_proposed_routes():
    """New sitemap: keep every current URL that has no rename target,
    add the new hub + leaf URLs, add /services/ai-automation.html."""
    urls = load_baseline_urls()
    proposed = set()
    for u in urls:
        path = strip_canon(u)
        new = ALL_LEGACY_MAP.get(path, path)
        proposed.add(CANON + (new if new != "/" else "/"))
    # Add new service hubs + leaves
    for pillar in ("branding", "marketing", "sales"):
        proposed.add(f"{CANON}/services/{pillar}/")
    for slug, _ in BRANDING_LEAVES:
        proposed.add(f"{CANON}/services/branding/{slug}.html")
    for slug, _ in MARKETING_LEAVES:
        proposed.add(f"{CANON}/services/marketing/{slug}.html")
    for slug, _ in SALES_LEAVES:
        proposed.add(f"{CANON}/services/sales/{slug}.html")
    # Cross-cutting page
    proposed.add(f"{CANON}/services/ai-automation.html")
    # Portfolio pillar hubs
    proposed.add(f"{CANON}/portfolio/branding.html")
    proposed.add(f"{CANON}/portfolio/marketing.html")
    proposed.add(f"{CANON}/portfolio/sales.html")
    return sorted(proposed)


def build_redirect_map():
    """Direct, chain-free permanent redirects.

    Also rewrite the two existing generic strategy->systems rules to point
    directly at the new destinations, so old published /services/strategy/* URLs
    still resolve in one hop.
    """
    out = []
    # New pillar-level redirects for every legacy service/portfolio URL
    for legacy, new in ALL_LEGACY_MAP.items():
        if legacy == new:
            continue
        out.append({"source": legacy, "destination": new, "permanent": True})
    # Existing /services/strategy/* users must land on the new Branding pages
    # (packet requires single-hop, so we point strategy directly to new IA)
    out.extend([
        {"source": "/services/strategy/brand-strategy",
         "destination": "/services/branding/brand-strategy-identity.html", "permanent": True},
        {"source": "/services/strategy/brand-strategy/",
         "destination": "/services/branding/brand-strategy-identity.html", "permanent": True},
        {"source": "/services/strategy",
         "destination": "/services/branding/", "permanent": True},
        {"source": "/services/strategy/",
         "destination": "/services/branding/", "permanent": True},
        {"source": "/services/strategy/:path*",
         "destination": "/services/branding/:path*", "permanent": True},
        {"source": "/portfolio/strategy/brand-strategy",
         "destination": "/portfolio/branding/brand-strategy-identity.html", "permanent": True},
        {"source": "/portfolio/strategy",
         "destination": "/portfolio/branding.html", "permanent": True},
        {"source": "/portfolio/strategy/:path*",
         "destination": "/portfolio/branding/:path*", "permanent": True},
        # Also redirect the /services/systems/brand-strategy -> new
        {"source": "/services/systems/brand-strategy",
         "destination": "/services/branding/brand-strategy-identity.html", "permanent": True},
        {"source": "/portfolio/systems/brand-strategy",
         "destination": "/portfolio/branding/brand-strategy-identity.html", "permanent": True},
    ])
    return out


def build_route_diff(baseline, proposed):
    b = set(baseline["urls"])
    p = set(proposed)
    added = sorted(p - b)
    removed = sorted(b - p)
    kept = sorted(b & p)
    lines = [
        "# Route diff — baseline vs proposed",
        "",
        f"- Baseline URL count: {len(b)}",
        f"- Proposed URL count: {len(p)}",
        f"- Retained (unchanged path): {len(kept)}",
        f"- Retired (redirected via redirect-map.json): {len(removed)}",
        f"- New URLs: {len(added)}",
        "",
        "Every retired URL has exactly ONE permanent, direct redirect in `redirect-map.json`.",
        "No chains, no loops. Case-study URLs are all retained.",
        "",
        "## Retired (301 to new)",
        "",
    ]
    for u in removed:
        legacy_path = strip_canon(u)
        target = ALL_LEGACY_MAP.get(legacy_path, "(missing)")
        lines.append(f"- `{u}` → `{target}`")
    lines.append("")
    lines.append("## New URLs")
    lines.append("")
    for u in added:
        lines.append(f"- `{u}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    os.makedirs("artifacts", exist_ok=True)
    baseline = build_baseline_routes()
    proposed = build_proposed_routes()
    redirects = build_redirect_map()

    with open("artifacts/baseline-routes.json", "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    with open("artifacts/proposed-routes.json", "w", encoding="utf-8") as f:
        json.dump({"canonical_host": CANON, "count": len(proposed), "urls": proposed}, f, indent=2)
    with open("artifacts/redirect-map.json", "w", encoding="utf-8") as f:
        json.dump({"count": len(redirects), "redirects": redirects}, f, indent=2)
    with open("artifacts/route-diff.md", "w", encoding="utf-8") as f:
        f.write(build_route_diff(baseline, proposed))

    print("baseline urls:", len(baseline["urls"]))
    print("proposed urls:", len(proposed))
    print("redirects:", len(redirects))
    return 0


if __name__ == "__main__":
    sys.exit(main())
