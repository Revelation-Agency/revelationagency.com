"""Emit an updated vercel.json (new redirect map, direct + single-hop) and
regenerate sitemap.xml from artifacts/proposed-routes.json.

The header + rewrite blocks of vercel.json are preserved from the baseline;
only the `redirects` array is replaced. This lets a reviewer diff the
redirect list alone.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def rebuild_vercel_json() -> None:
    baseline = load("vercel.json")
    new_redirects = load("artifacts/redirect-map.json")["redirects"]
    baseline["redirects"] = new_redirects
    # keep cleanUrls, trailingSlash, rewrites, and headers untouched
    write("vercel.json", baseline)
    print(f"vercel.json: wrote {len(new_redirects)} redirects (single-hop, permanent)")


SITEMAP_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

SITEMAP_FOOTER = "</urlset>\n"

CANON = "https://www.revelationagency.com"


def priority(url: str) -> str:
    if url == f"{CANON}/":
        return "1.0"
    if url.endswith("/services/") or url.endswith("/services.html") or url.endswith("/portfolio.html"):
        return "0.9"
    if "/services/branding/" in url or "/services/marketing/" in url or "/services/sales/" in url:
        # index vs leaves
        if url.endswith("/branding/") or url.endswith("/marketing/") or url.endswith("/sales/"):
            return "0.9"
        return "0.8"
    if "/portfolio/case-studies/" in url:
        return "0.6"
    if "/portfolio/" in url:
        return "0.7"
    if "/the-reveal/" in url:
        return "0.7"
    return "0.6"


def changefreq(url: str) -> str:
    if url == f"{CANON}/":
        return "weekly"
    if "/portfolio/case-studies/" in url:
        return "monthly"
    if "/the-reveal/" in url:
        return "monthly"
    return "monthly"


def build_sitemap() -> None:
    urls = load("artifacts/proposed-routes.json")["urls"]
    # De-dupe and sort by group for stable diff:
    groups = {"core": [], "services": [], "portfolio": [], "the-reveal": [], "landing": [], "other": []}
    for u in urls:
        p = u.replace(CANON, "") or "/"
        if p in ("/", "/about.html", "/booking.html", "/contact.html", "/faq.html",
                 "/portfolio.html", "/services.html", "/web-hosting.html"):
            groups["core"].append(u)
        elif p.startswith("/services/"):
            groups["services"].append(u)
        elif p.startswith("/portfolio/"):
            groups["portfolio"].append(u)
        elif p.startswith("/the-reveal/"):
            groups["the-reveal"].append(u)
        elif p in ("/lead-agent/", "/sales-agent/", "/sales-growth-engine/", "/sales-intelligence/"):
            groups["landing"].append(u)
        else:
            groups["other"].append(u)

    lines = [SITEMAP_HEADER, "\n  <!-- Core pages -->\n"]
    for u in sorted(groups["core"]):
        lines.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-08-14</lastmod>\n    <changefreq>{changefreq(u)}</changefreq>\n    <priority>{priority(u)}</priority>\n  </url>\n")
    lines.append("\n  <!-- Services (Branding / Marketing / Sales + AI cross-cutting) -->\n")
    for u in sorted(groups["services"]):
        lines.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-08-14</lastmod>\n    <changefreq>{changefreq(u)}</changefreq>\n    <priority>{priority(u)}</priority>\n  </url>\n")
    lines.append("\n  <!-- Portfolio -->\n")
    for u in sorted(groups["portfolio"]):
        lines.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-08-14</lastmod>\n    <changefreq>{changefreq(u)}</changefreq>\n    <priority>{priority(u)}</priority>\n  </url>\n")
    lines.append("\n  <!-- The Reveal -->\n")
    for u in sorted(groups["the-reveal"]):
        lines.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-08-14</lastmod>\n    <changefreq>{changefreq(u)}</changefreq>\n    <priority>{priority(u)}</priority>\n  </url>\n")
    lines.append("\n  <!-- Lead / sales landing routes (preserved pending separate review) -->\n")
    for u in sorted(groups["landing"]):
        lines.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-08-14</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>\n")
    lines.append(SITEMAP_FOOTER)
    with open("sitemap.xml", "w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))
    total = sum(len(v) for v in groups.values())
    print(f"sitemap.xml: wrote {total} URLs")


if __name__ == "__main__":
    rebuild_vercel_json()
    build_sitemap()
