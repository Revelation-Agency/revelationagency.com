"""Emit clean-URL Vercel routing and the canonical sitemap.

The migration redirect map is generated separately. This writer adds the
canonical apex-to-www host redirect, normalizes the two retained rewrites,
preserves security/cache headers, and refuses to emit extension-bearing route
rules while ``cleanUrls`` is enabled.
"""
import json
import os
import re
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


def clean_public_path(value: str) -> str:
    """Normalize an internal route while preserving query strings."""
    path, separator, query = value.partition("?")
    path = re.sub(r"/index\.html$", "", path, flags=re.I)
    path = re.sub(r"\.html$", "", path, flags=re.I)
    if path != "/":
        path = path.rstrip("/")
    path = path or "/"
    return path + (separator + query if separator else "")


CANONICAL_HOST_REDIRECT = {
    "source": "/:path*",
    "has": [{"type": "host", "value": "revelationagency.com"}],
    "destination": "https://www.revelationagency.com/:path*",
    "permanent": True,
}


def rebuild_vercel_json() -> None:
    baseline = load("vercel.json")
    new_redirects = load("artifacts/redirect-map.json")["redirects"]
    baseline["redirects"] = [CANONICAL_HOST_REDIRECT, *new_redirects]
    baseline["rewrites"] = [
        {
            "source": clean_public_path(rule["source"]),
            "destination": clean_public_path(rule["destination"]),
        }
        for rule in baseline.get("rewrites", [])
    ]

    for section in ("redirects", "rewrites"):
        for rule in baseline.get(section, []):
            for key in ("source", "destination"):
                value = str(rule.get(key, ""))
                if ".html" in value.lower():
                    raise ValueError(f"{section} {key} must be extensionless with cleanUrls=true: {value}")

    write("vercel.json", baseline)
    print(
        "vercel.json: wrote "
        f"{len(new_redirects)} migration redirects + 1 canonical-host redirect "
        f"and {len(baseline['rewrites'])} rewrites"
    )


SITEMAP_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

SITEMAP_FOOTER = "</urlset>\n"

CANON = "https://www.revelationagency.com"


def priority(url: str) -> str:
    if url == f"{CANON}/":
        return "1.0"
    if url in {
        f"{CANON}/services",
        f"{CANON}/services/branding",
        f"{CANON}/services/marketing",
        f"{CANON}/services/sales",
        f"{CANON}/portfolio",
    }:
        return "0.9"
    if url == f"{CANON}/the-reveal":
        return "0.8"
    if "/services/branding/" in url or "/services/marketing/" in url or "/services/sales/" in url:
        # index vs leaves
        if url.endswith("/branding") or url.endswith("/marketing") or url.endswith("/sales"):
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
    if len(urls) != len(set(urls)):
        raise ValueError("artifacts/proposed-routes.json contains duplicate URLs")
    # De-dupe and sort by group for stable diff:
    groups = {"core": [], "services": [], "portfolio": [], "the-reveal": [], "landing": [], "other": []}
    for u in urls:
        p = u.replace(CANON, "") or "/"
        if p in ("/", "/about", "/booking", "/contact", "/faq",
                 "/portfolio", "/services", "/web-hosting"):
            groups["core"].append(u)
        elif p.startswith("/services/"):
            groups["services"].append(u)
        elif p.startswith("/portfolio/"):
            groups["portfolio"].append(u)
        elif p == "/the-reveal" or p.startswith("/the-reveal/"):
            groups["the-reveal"].append(u)
        elif p in ("/lead-agent", "/sales-agent", "/sales-growth-engine", "/sales-intelligence"):
            groups["landing"].append(u)
        else:
            groups["other"].append(u)

    emitted_urls: list[str] = []

    def append_group(lines: list[str], key: str, *, frequency: str | None = None, fixed_priority: str | None = None) -> None:
        for u in sorted(groups[key]):
            emitted_urls.append(u)
            lines.append(
                "  <url>\n"
                f"    <loc>{u}</loc>\n"
                "    <lastmod>2026-08-17</lastmod>\n"
                f"    <changefreq>{frequency or changefreq(u)}</changefreq>\n"
                f"    <priority>{fixed_priority or priority(u)}</priority>\n"
                "  </url>\n"
            )

    lines = [SITEMAP_HEADER, "\n  <!-- Core pages -->\n"]
    append_group(lines, "core")
    lines.append("\n  <!-- Services (Branding / Marketing / Sales + AI cross-cutting) -->\n")
    append_group(lines, "services")
    lines.append("\n  <!-- Portfolio -->\n")
    append_group(lines, "portfolio")
    lines.append("\n  <!-- The Reveal -->\n")
    append_group(lines, "the-reveal")
    lines.append("\n  <!-- Lead / sales landing routes (preserved pending separate review) -->\n")
    append_group(lines, "landing", frequency="monthly", fixed_priority="0.5")
    if groups["other"]:
        lines.append("\n  <!-- Other canonical routes -->\n")
        append_group(lines, "other")
    lines.append(SITEMAP_FOOTER)

    if set(emitted_urls) != set(urls) or len(emitted_urls) != len(urls):
        missing = sorted(set(urls) - set(emitted_urls))
        extra = sorted(set(emitted_urls) - set(urls))
        raise ValueError(f"sitemap grouping mismatch: missing={missing} extra={extra}")
    with open("sitemap.xml", "w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))
    print(f"sitemap.xml: wrote {len(emitted_urls)} URLs")


if __name__ == "__main__":
    rebuild_vercel_json()
    build_sitemap()
