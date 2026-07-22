#!/usr/bin/env python3
"""Generate lightweight WebP variants of every PNG under assets/.

Each asset ships in two tiers:

  * PNG  — the original, full-resolution source. Used for on-screen fallback and
           for the *print* PDF export, where full fidelity matters.
  * WebP — a smaller, down-scaled copy. Used for on-screen viewing and for the
           *digital* PDF export, where a light file matters more than print DPI.

The PNGs are never modified. Re-run this whenever a PNG changes:

    python scripts/optimize-images.py

Requires Pillow with WebP support (Pillow >= 9).
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
QUALITY = 74

# Max longest-side (px) for the WebP copy, by top-level assets/ sub-folder.
# The PNG keeps full resolution for print; these caps only shrink the WebP.
# Kept modest on purpose: the WebP feeds the web view and the *digital* PDF,
# where a light file matters more than print DPI (the plants render small on
# the cards, so 700px still looks crisp on screen).
CAPS = {
    "plants": 700,
    "cover": 1500,
    "logos": 2000,
    "background": 1500,
}
DEFAULT_CAP = 1400


def cap_for(png: Path) -> int:
    top = png.relative_to(ASSETS).parts[0]
    return CAPS.get(top, DEFAULT_CAP)


def main() -> None:
    pngs = sorted(ASSETS.rglob("*.png"))
    if not pngs:
        print(f"No PNGs found under {ASSETS}")
        return

    total_png = total_webp = 0
    for png in pngs:
        cap = cap_for(png)
        with Image.open(png) as im:
            longest = max(im.size)
            if longest > cap:
                scale = cap / longest
                im = im.resize(
                    (round(im.width * scale), round(im.height * scale)),
                    Image.LANCZOS,
                )
            im.save(png.with_suffix(".webp"), "WEBP", quality=QUALITY, method=6)

        webp = png.with_suffix(".webp")
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
