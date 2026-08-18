"""Retired sitemap writer kept only as a fail-closed compatibility entrypoint.

The 2026 route inventory is the source of truth. Use, in order:

    python scripts/build_routes_artifacts.py
    python scripts/write_vercel_and_sitemap.py
    python scripts/verify_2026_refresh.py --max-errors 0

The previous implementation emitted apex-host URLs, ``.html`` leaves, and
redirect-only pages, which conflicts with ``cleanUrls: true``.
"""

from __future__ import annotations


if __name__ == "__main__":
    raise SystemExit(
        "DEPRECATED: regen_sitemap.py emitted pre-2026 routes. Run "
        "build_routes_artifacts.py followed by write_vercel_and_sitemap.py."
    )
