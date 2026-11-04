"""Generate the original background artwork used by the app (no stock photos needed).

Run:  python tools/make_backgrounds.py      (needs: pip install pillow numpy)
Output: static/img/hero_bg.jpg, band_bg.jpg, texture_bg.jpg
Everything is drawn from the app palette: soft colour fields plus thin arcs and dots that echo
the four-part circle logo.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "static" / "img"
OUT.mkdir(parents=True, exist_ok=True)

INDIGO, MAGENTA, TEAL, OCHRE = (58, 63, 216), (184, 23, 95), (10, 124, 116), (168, 90, 0)
PAPER, INK = (244, 245, 251), (21, 23, 61)
rng = np.random.default_rng(7)


def field(w, h, base, blobs):
    """Base colour plus soft gaussian colour blobs: (cx, cy, radius, colour, strength)."""
    img = np.zeros((h, w, 3), dtype=np.float32)
    img[:] = base
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for cx, cy, r, col, a in blobs:
        g = np.exp(-(((xx - cx * w) ** 2 + (yy - cy * h) ** 2) / (2 * (r * w) ** 2)))[..., None]
        img = img * (1 - a * g) + np.array(col, dtype=np.float32) * (a * g)
    return img


def finish(arr, name, grain=2.0, q=82):
    arr = arr + rng.normal(0, grain, arr.shape)           # fine grain avoids gradient banding
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(OUT / name, quality=q, optimize=True)
    print("wrote", name, (OUT / name).stat().st_size // 1024, "KB")


def overlay_lines(arr, draw_fn, blur=0.0):
    layer = Image.new("RGBA", (arr.shape[1], arr.shape[0]), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    return np.array(Image.alpha_composite(base, layer).convert("RGB"), dtype=np.float32)


# ---------------------------------------------------------------- hero: soft light colour field
def hero(w=2200, h=900):
    arr = field(w, h, PAPER, [(0.86, 0.35, 0.22, INDIGO, 0.22), (0.98, 0.95, 0.18, MAGENTA, 0.20),
                              (0.70, 1.05, 0.20, TEAL, 0.22), (0.45, -0.05, 0.16, OCHRE, 0.16),
                              (0.05, 0.9, 0.18, INDIGO, 0.10)])

    def rings(d):
        cx, cy = int(w * 0.80), int(h * 0.50)
        for i, r in enumerate(range(160, 760, 95)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*INK, 20 - i * 2), width=2)
        for k in range(4):                                  # four spokes: the logo's four parts
            a = math.pi / 4 + k * math.pi / 2
            d.line([cx, cy, cx + 900 * math.cos(a), cy + 900 * math.sin(a)], fill=(*INK, 16), width=2)
        for gx in range(60, w, 44):                         # dotted grid on the left
            for gy in range(60, h, 44):
                if gx < w * 0.42:
                    d.ellipse([gx, gy, gx + 3, gy + 3], fill=(*INK, 20))
    finish(overlay_lines(arr, rings), "hero_bg.jpg", grain=1.2)


# ---------------------------------------------------------------- band: dark indigo, glowing fields
def band(w=2200, h=620):
    arr = field(w, h, (22, 24, 70), [(0.12, 0.2, 0.20, INDIGO, 0.75), (0.55, 1.1, 0.22, TEAL, 0.55),
                                     (0.95, 0.1, 0.24, MAGENTA, 0.60), (0.75, 0.9, 0.12, OCHRE, 0.35)])

    def marks(d):
        for gx in range(40, w, 40):
            for gy in range(40, h, 40):
                d.ellipse([gx, gy, gx + 3, gy + 3], fill=(255, 255, 255, 30))
        cx, cy = int(w * 0.88), int(h * 0.55)
        for r in range(120, 700, 80):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 26), width=2)
    finish(overlay_lines(arr, marks), "band_bg.jpg", grain=1.5)


# ---------------------------------------------------------------- texture: very faint page backdrop
def texture(w=2000, h=1200):
    arr = field(w, h, PAPER, [(0.10, 0.0, 0.30, INDIGO, 0.10), (0.95, 0.05, 0.25, MAGENTA, 0.07),
                              (0.55, 0.0, 0.20, TEAL, 0.07)])
    finish(arr, "texture_bg.jpg", grain=0.8, q=80)


if __name__ == "__main__":
    hero(); band(); texture()
