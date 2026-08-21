"""Fail-closed verification for the public Revelation Agency privacy notice."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    page_path = ROOT / "privacy.html"
    require(page_path.is_file(), "privacy.html is missing")

    page = page_path.read_text(encoding="utf-8")
    lowered = page.lower()
    required_fragments = {
        "canonical URL": 'rel="canonical" href="https://www.revelationagency.com/privacy"',
        "Reviii identity": "reviii privacy notice",
        "five-mode system": "assist, ops, sales, outreach, and marketing",
        "data collected": "data we collect",
        "data use": "how we use data",
        "AI processing": "ai processing",
        "no model training": "do not use slack data to train",
        "retention": "retention",
        "deletion": "access, correction, export, or deletion",
        "no sale": "do not sell",
        "security": "security",
        "contact": "connect@revelationagency.com",
        "effective date": "effective august 20, 2026",
    }
    for label, fragment in required_fragments.items():
        require(fragment in lowered, f"privacy page is missing {label}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    require(
        "<loc>https://www.revelationagency.com/privacy</loc>" in sitemap,
        "privacy URL is missing from sitemap.xml",
    )

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    require('href="/privacy"' in home, "homepage does not link to the privacy notice")

    print("privacy page contract: PASS")


if __name__ == "__main__":
    main()
