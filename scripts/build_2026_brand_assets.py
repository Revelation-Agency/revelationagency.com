#!/usr/bin/env python3
"""Build optimized web assets from the user-supplied 2026 Revelation logos.

The source PNGs live in assets/brand/current/source so the web outputs are
reproducible without depending on a desktop path. This script crops only
transparent padding, preserves the supplied artwork, and writes deterministic
PNG/ICO derivatives plus a small provenance manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "brand" / "current" / "source"
OUT_DIR = ROOT / "assets" / "brand" / "current"

MARK_SOURCE = SOURCE_DIR / "revelation-logo-no-text.png"
LOCKUP_SOURCE = SOURCE_DIR / "revelation-logo-with-text.png"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def crop_alpha(image: Image.Image, padding_ratio: float = 0.035) -> Image.Image:
    rgba = image.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    if not bbox:
        raise ValueError("Source image contains no visible pixels")
    left, top, right, bottom = bbox
    pad = max(8, round(max(right - left, bottom - top) * padding_ratio))
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(rgba.width, right + pad)
    bottom = min(rgba.height, bottom + pad)
    return rgba.crop((left, top, right, bottom))


def fit_square(image: Image.Image, size: int, padding_ratio: float = 0.08) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    usable = max(1, round(size * (1 - 2 * padding_ratio)))
    fitted = image.copy()
    fitted.thumbnail((usable, usable), Image.Resampling.LANCZOS)
    x = (size - fitted.width) // 2
    y = (size - fitted.height) // 2
    canvas.alpha_composite(fitted, (x, y))
    return canvas


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True, compress_level=9)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def build_social_card(mark: Image.Image) -> Image.Image:
    """Create a deterministic 1200x630 open-graph card from the supplied mark."""
    card = Image.new("RGBA", (1200, 630), "#171717")
    grid = Image.new("RGBA", card.size, (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    for x in range(0, 1201, 60):
        grid_draw.line((x, 0, x, 630), fill=(255, 255, 255, 16), width=1)
    for y in range(0, 631, 60):
        grid_draw.line((0, y, 1200, y), fill=(255, 255, 255, 16), width=1)
    card.alpha_composite(grid)

    glow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((760, 20, 1300, 560), fill=(201, 28, 29, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(110))
    card.alpha_composite(glow)

    mark_panel = Image.new("RGBA", (360, 360), (255, 253, 250, 245))
    panel_mark = fit_square(mark, 294, padding_ratio=0.08)
    mark_panel.alpha_composite(panel_mark, ((360 - 294) // 2, (360 - 294) // 2))
    card.alpha_composite(mark_panel, (790, 112))

    draw = ImageDraw.Draw(card)
    small = load_font(20, bold=True)
    display = load_font(67, bold=True)
    caption = load_font(18, bold=False)
    draw.text((70, 58), "REVELATION AGENCY", font=small, fill="#C91C1D")
    draw.text((70, 148), "BRANDING.", font=display, fill="#FFFDF9")
    draw.text((70, 226), "MARKETING.", font=display, fill="#FFFDF9")
    draw.text((70, 304), "SALES.", font=display, fill="#C91C1D")
    draw.line((70, 420, 690, 420), fill="#C91C1D", width=4)
    draw.text((70, 452), "ONE CONNECTED GROWTH SYSTEM.", font=caption, fill=(255, 255, 255, 185))
    draw.text((70, 492), "OPERATOR-LED  /  EVIDENCE-BACKED", font=small, fill=(255, 255, 255, 115))
    opaque = Image.new("RGBA", card.size, "#171717")
    opaque.alpha_composite(card)
    return opaque


def main() -> None:
    missing = [str(path) for path in (MARK_SOURCE, LOCKUP_SOURCE) if not path.exists()]
    if missing:
        raise SystemExit("Missing source logo(s): " + ", ".join(missing))

    mark_original = Image.open(MARK_SOURCE).convert("RGBA")
    lockup_original = Image.open(LOCKUP_SOURCE).convert("RGBA")
    mark = crop_alpha(mark_original)
    lockup = crop_alpha(lockup_original, padding_ratio=0.025)

    mark_web = fit_square(mark, 640, padding_ratio=0.07)
    lockup_web = fit_square(lockup, 960, padding_ratio=0.035)
    save_png(mark_web, OUT_DIR / "ra-mark-red.png")
    save_png(lockup_web, OUT_DIR / "ra-lockup-red.png")
    save_png(build_social_card(mark), OUT_DIR / "ra-social-card.png")

    # Compatibility asset used by older pages and Organization JSON-LD.
    save_png(fit_square(mark, 512, padding_ratio=0.07), ROOT / "assets" / "revelation-logo.png")

    icon_outputs = {
        "favicon-32.png": 32,
        "apple-touch-icon.png": 180,
        "icon-192.png": 192,
        "icon-512.png": 512,
    }
    for filename, size in icon_outputs.items():
        save_png(fit_square(mark, size, padding_ratio=0.08), ROOT / filename)

    ico_frames = [fit_square(mark, size, padding_ratio=0.08) for size in (16, 32, 48, 64, 128, 256)]
    ico_frames[-1].save(
        ROOT / "favicon.ico",
        format="ICO",
        sizes=[(frame.width, frame.height) for frame in ico_frames],
        append_images=ico_frames[:-1],
    )

    manifest = {
        "version": "2026-08-17.user-supplied",
        "authority": "Files supplied directly by Blaine McKenzie for this website refresh",
        "palette": {
            "logo_red_observed": "#C91C1D",
            "site_red": "#C91C1D",
            "ink": "#171717",
            "paper": "#F6F3EE",
        },
        "sources": [
            {
                "path": MARK_SOURCE.relative_to(ROOT).as_posix(),
                "sha256": sha256(MARK_SOURCE),
                "width": mark_original.width,
                "height": mark_original.height,
            },
            {
                "path": LOCKUP_SOURCE.relative_to(ROOT).as_posix(),
                "sha256": sha256(LOCKUP_SOURCE),
                "width": lockup_original.width,
                "height": lockup_original.height,
            },
        ],
        "outputs": [
            "assets/brand/current/ra-mark-red.png",
            "assets/brand/current/ra-lockup-red.png",
            "assets/brand/current/ra-social-card.png",
            "assets/revelation-logo.png",
            "favicon-32.png",
            "apple-touch-icon.png",
            "icon-192.png",
            "icon-512.png",
            "favicon.ico",
        ],
        "transform": "transparent-padding crop, proportional resize, no artwork or color changes",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("Built current Revelation brand assets")
    print(f"  mark source sha256   : {manifest['sources'][0]['sha256']}")
    print(f"  lockup source sha256 : {manifest['sources'][1]['sha256']}")


if __name__ == "__main__":
    main()
