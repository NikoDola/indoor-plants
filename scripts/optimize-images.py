#!/usr/bin/env python3
"""Generate WebP variants of every PNG under assets/.

The WebP files are served to browsers for on-screen viewing; the original PNGs
are kept as the print / fallback source (see the <picture> elements in
index.html and the image-set() rules in styles.css).

Run from the repo root:

    python scripts/optimize-images.py

Requires Pillow with WebP support (Pillow >= 9).
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
QUALITY = 82  # visually lossless for these photos, ~3-5x smaller than PNG


def main() -> None:
    pngs = sorted(ASSETS.rglob("*.png"))
    if not pngs:
        print(f"No PNGs found under {ASSETS}")
        return

    total_png = total_webp = 0
    for png in pngs:
        webp = png.with_suffix(".webp")
        with Image.open(png) as im:
            im.save(webp, "WEBP", quality=QUALITY, method=6)
        png_size, webp_size = png.stat().st_size, webp.stat().st_size
        total_png += png_size
        total_webp += webp_size
        print(
            f"{png.relative_to(ROOT).as_posix():<40} "
            f"{png_size // 1024:>5} KB -> {webp_size // 1024:>4} KB "
            f"({100 * webp_size // png_size}%)"
        )

    print("-" * 60)
    print(
        f"{'total':<40} {total_png // 1024:>5} KB -> {total_webp // 1024:>4} KB "
        f"({100 * total_webp // total_png}% of original)"
    )


if __name__ == "__main__":
    main()
