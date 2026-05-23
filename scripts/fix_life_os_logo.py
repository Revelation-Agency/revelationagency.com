"""
Step 3 — replace incorrect Revelation Agency phoenix on Life OS portfolio assets
with the OFFICIAL Life OS notebook logo sourced from
02_internal_projects/lifeos/public/icon-512.png.

Strategy:
  1. Overwrite assets/img/portfolio/life-os/logo.png with icon-512.png
     (canonical Life OS asset for the case study + any future single-use).
  2. Re-render assets/img/portfolio/life-os/thumbnail.png (full APP + STRATEGY)
     using the canonical v5-a renderer from the legacy dev repo with the
     correct logo passed via logo_path_override.
  3. Re-render assets/img/portfolio/life-os/thumbnail-app.png (app-only
     discipline thumbnail) the same way with eyebrow ["App"] only.

The v5-a renderer is the canonical thumbnail spec for the whole portfolio
grid, so this preserves visual consistency with every other client card —
only the logo inside the white square changes.

No HTML changes needed: portfolio.html, portfolio/creative/app-development.html,
and services/creative/app-development.html all reference the same filenames,
and the logo.png is referenced by the case-study page through the v5-a layout.
"""
import shutil
import sys
from pathlib import Path

# --- Locate the canonical v5-a renderer in the legacy dev repo ----------
LEGACY_REPO = Path(
    r"C:\Users\blain\Desktop\Revelation Command Center"
    r"\02_internal_projects\dev-revelation"
)
sys.path.insert(0, str(LEGACY_REPO / "portfolio_system"))
from v5a_thumbnail_renderer import render_v5a  # noqa: E402

# --- Source + destination paths -----------------------------------------
PROD_REPO = Path(__file__).resolve().parents[1]
OFFICIAL_LOGO = Path(
    r"C:\Users\blain\Desktop\Revelation Command Center"
    r"\02_internal_projects\lifeos\public\icon-512.png"
)
LIFE_OS_ASSET_DIR = PROD_REPO / "assets" / "img" / "portfolio" / "life-os"


def main():
    if not OFFICIAL_LOGO.exists():
        sys.exit(f"FATAL: official Life OS logo missing at {OFFICIAL_LOGO}")
    LIFE_OS_ASSET_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Replace logo.png with the official asset
    dest_logo = LIFE_OS_ASSET_DIR / "logo.png"
    shutil.copy2(OFFICIAL_LOGO, dest_logo)
    print(f"WROTE  {dest_logo.relative_to(PROD_REPO)}  ({dest_logo.stat().st_size//1024} KB)")

    # 2) Regen thumbnail.png — APP + STRATEGY eyebrow (the portfolio main card)
    out1 = LIFE_OS_ASSET_DIR / "thumbnail.png"
    render_v5a(
        output_path=out1,
        client_slug="life-os",
        line1="LIFE",
        line2="OS",
        services=["App", "Strategy"],
        icon_key="multi",  # 2 disciplines → venn icon
        logo_tile="white",
        logo_path_override=OFFICIAL_LOGO,
    )
    print(f"WROTE  {out1.relative_to(PROD_REPO)}  ({out1.stat().st_size//1024} KB)")

    # 3) Regen thumbnail-app.png — APP only (discipline-leaf card)
    out2 = LIFE_OS_ASSET_DIR / "thumbnail-app.png"
    render_v5a(
        output_path=out2,
        client_slug="life-os",
        line1="LIFE",
        line2="OS",
        services=["App"],
        icon_key="app",  # single-discipline
        logo_tile="white",
        logo_path_override=OFFICIAL_LOGO,
    )
    print(f"WROTE  {out2.relative_to(PROD_REPO)}  ({out2.stat().st_size//1024} KB)")

    print("\nAll Life OS thumbnails regenerated with the OFFICIAL notebook logo.")


if __name__ == "__main__":
    main()
