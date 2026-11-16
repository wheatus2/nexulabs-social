"""Draws the two manila key tags for a made-up florist (Wrenfield Flowers).
  tex/tag-couk.png   RGBA: rgb = printed and stamped ink, a = how much ink
  tex/tag-com.png
  tex/mask.png       the tag's outline with its punched hole (white = paper)
  tex/ring.png       the reinforcing ring round the hole (white = ring), used as colour and bump
A tag is 60 x 120 mm, drawn at 20 px per mm. The domain is rubber-stamped in a blue-black ink;
the tag maker printed a faint KEY label and one rule in brown.
"""
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE / "tex"; OUT.mkdir(exist_ok=True)


def ttf(name, out):
    p = Path("/tmp") / out
    if not p.exists():
        f = TTFont(ROOT / "fonts" / name); f.flavor = None; f.save(p)
    return str(p)


ANTON = ttf("anton-latin-400-normal.woff2", "nx-anton.ttf")
GEIST = ttf("Geist-SemiBold.woff2", "nx-geist-sb.ttf")

PX = 20                      # px per mm
TW, TH = 60 * PX, 120 * PX
HOLE = (30 * PX, 11 * PX)
HOLE_R = 2.7 * PX
RING_R = 6.6 * PX
CLIP = 9 * PX                # the clipped top corners

STAMP = (0.020, 0.024, 0.055)
PRINT = (0.30, 0.20, 0.12)


def outline():
    im = Image.new("L", (TW * 2, TH * 2), 0)
    d = ImageDraw.Draw(im)
    s = 2
    d.polygon([(CLIP * s, 0), ((TW - CLIP) * s, 0), (TW * s, CLIP * s), (TW * s, TH * s), (0, TH * s), (0, CLIP * s)], fill=255)
    hx, hy = HOLE
    d.ellipse([(hx - HOLE_R) * s, (hy - HOLE_R) * s, (hx + HOLE_R) * s, (hy + HOLE_R) * s], fill=0)
    return im.resize((TW, TH), Image.LANCZOS)


def ring():
    im = Image.new("L", (TW * 2, TH * 2), 0)
    d = ImageDraw.Draw(im)
    hx, hy = HOLE
    d.ellipse([(hx - RING_R) * 2, (hy - RING_R) * 2, (hx + RING_R) * 2, (hy + RING_R) * 2], fill=255)
    return im.resize((TW, TH), Image.LANCZOS)


def fit(text, font_path, width, ls=0.0):
    """Font size that sets text to the given width (with tracking ls in em)."""
    lo, hi = 10, 2000
    while hi - lo > 1:
        m = (lo + hi) // 2
        f = ImageFont.truetype(font_path, m)
        w = sum(f.getlength(c) for c in text) + ls * m * (len(text) - 1)
        lo, hi = (m, hi) if w <= width else (lo, m)
    return lo


def set_line(d, text, font_path, size, x, baseline, ls=0.0, fill=255):
    f = ImageFont.truetype(font_path, size)
    for c in text:
        d.text((x, baseline), c, font=f, fill=fill, anchor="ls")
        x += f.getlength(c) + ls * size


def width(text, font_path, size, ls=0.0):
    f = ImageFont.truetype(font_path, size)
    return sum(f.getlength(c) for c in text) + ls * size * (len(text) - 1)


def stamp_alpha(lines, seed):
    """A rubber letter set: every letter pressed on its own, so each sits a touch off the line, turned a degree
    or two, and takes its own amount of ink, with the darker rim a rubber letter leaves and a starved patch here and there."""
    rng = np.random.default_rng(seed)
    a = np.zeros((TH, TW), np.float32)
    for (text, size, y, ls) in lines:
        f = ImageFont.truetype(ANTON, size)
        w = width(text, ANTON, size, ls)
        x = (TW - w) / 2
        for c in text:
            cw = f.getlength(c)
            pad = size
            im = Image.new("L", (int(cw) + 2 * pad, 2 * size + pad), 0)
            ImageDraw.Draw(im).text((pad, size + pad // 2), c, font=f, fill=255, anchor="ls")
            im = im.rotate(rng.normal(0, 1.4), resample=Image.BICUBIC, center=(pad + cw / 2, size + pad // 2 - size * 0.35))
            g = np.asarray(im, np.float32) / 255
            g = gaussian_filter(g, 0.9)
            # rim: ink pools at the edge of the rubber
            edge = np.clip(g - gaussian_filter(g, 3.0), 0, 1) * 1.6
            dens = rng.uniform(0.84, 0.98)
            nz = gaussian_filter(rng.random(g.shape).astype(np.float32), 7)
            nz = (nz - nz.min()) / (nz.max() - nz.min() + 1e-6)
            starve = np.clip((nz - 0.78) * 4, 0, 1) * rng.uniform(0.15, 0.4)
            gr = gaussian_filter(rng.random(g.shape).astype(np.float32), 1.0)
            gr = (gr - gr.min()) / (gr.max() - gr.min() + 1e-6)
            k = dens * (1 - starve) * np.where(gr < 0.14, 0.6, 1.0)
            g = np.clip(g * k + edge * 0.25, 0, 1)
            ox = int(round(x - pad + rng.normal(0, 3))); oy = int(round(y - size - pad // 2 + rng.normal(0, 5)))
            h, ww = g.shape
            x0, y0 = max(ox, 0), max(oy, 0); x1, y1 = min(ox + ww, TW), min(oy + h, TH)
            a[y0:y1, x0:x1] = np.maximum(a[y0:y1, x0:x1], g[y0 - oy:y1 - oy, x0 - ox:x1 - ox])
            x += cw + ls * size
    return np.clip(a, 0, 1)


def printed_alpha():
    im = Image.new("L", (TW, TH), 0)
    d = ImageDraw.Draw(im)
    s = 4.2 * PX
    w = width("KEY", GEIST, int(s), 0.18)
    set_line(d, "KEY", GEIST, int(s), (TW - w) / 2, 26 * PX, 0.18)
    d.rectangle([7 * PX, 108 * PX, TW - 7 * PX, 108 * PX + 5], fill=255)
    a = np.asarray(im, np.float32) / 255
    return gaussian_filter(a, 0.6) * 1.0


def tag(ending, seed, out):
    lines = []
    # the name, then the ending at one size on both tags (fitted to .co.uk), so neither looks favoured
    s1 = fit("wrenfield", ANTON, 41 * PX, 0.04)
    s2 = fit(".co.uk", ANTON, 42 * PX, 0.04)
    lines.append(("wrenfield", s1, 60 * PX, 0.04))
    lines.append((ending, s2, 60 * PX + int(s2 * 0.98), 0.04))
    sa = stamp_alpha(lines, seed)
    pa = printed_alpha()
    a = np.clip(sa + pa * (1 - sa), 0, 1)
    rgb = np.zeros((TH, TW, 3), np.float32)
    for c in range(3):
        rgb[..., c] = (STAMP[c] * sa + PRINT[c] * pa * (1 - sa)) / np.maximum(a, 1e-4)
    srgb = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)
    arr = np.dstack([np.clip(srgb, 0, 1), a]) * 255
    Image.fromarray((arr + 0.5).astype(np.uint8), "RGBA").save(OUT / out)
    print("wrote", out, s1, s2)


if __name__ == "__main__":
    outline().save(OUT / "mask.png")
    ring().save(OUT / "ring.png")
    tag(".co.uk", 5, "tag-couk.png")
    tag(".com", 9, "tag-com.png")
