"""Draws both sides of the woven label ribbon (run with python3.13 before build.py).

The label is for a made-up knitwear maker, Thrumwick: the name in DM Serif Display between two selvedge
stripes, with a small diamond between labels. Front: navy ground, ivory figure. Back: the same the other way
round. The ground is shaded as fine ribs lying across the ribbon and the figure as floats standing up, five
threads to the millimetre. Writes .rib-<frame>-<front|back>.png and a height map for each (-h.png).
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import geom

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NAVY = (19, 27, 78)
IVORY = (238, 229, 208)
PXS = {1: 50, 2: 60, 3: 60}       # pixels to the millimetre
TH = 0.2                           # one thread, mm
NAME = "Thrumwick"
Image.MAX_IMAGE_PIXELS = None


def ttf(name):
    out = HERE / f".{name}.ttf"
    if not out.exists():
        f = TTFont(str(ROOT / "fonts" / f"{name}.woff2")); f.flavor = None; f.save(str(out))
    return str(out)


def side(scene, which):
    L = geom.layout(scene)
    px = PXS[scene]
    Wp = int(round(L["period"] * 10 * px))
    Hp = int(round(geom.WID * 10 * px))
    m = Image.new("L", (Wp, Hp), 0); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(ttf("dm-serif-display-latin-400-normal"), int(11.6 * px))
    def X(c):
        x = c * 10 * px
        return Wp - x if which == 1 else x
    for y0 in (1.5, geom.WID * 10 - 1.5 - 0.45):
        d.rectangle([0, y0 * px, Wp, (y0 + 0.45) * px - 1], fill=255)
    for c, s in L["labels"]:
        if s == which:
            widths = [d.textlength(ch, font=f) for ch in NAME]
            tr = 0.34 * px
            tot = sum(widths) + tr * (len(NAME) - 1)
            x = X(c) - tot / 2
            for ch, w in zip(NAME, widths):
                d.text((x, Hp / 2 + 3.75 * px), ch, font=f, fill=255, anchor="ls", stroke_width=max(1, round(0.05 * px)), stroke_fill=255); x += w + tr
    for c, s in L["dots"]:
        if s == which:
            x = X(c); y = Hp / 2 + 0.2 * px; r = 1.15 * px
            d.polygon([(x - r, y), (x, y - r), (x + r, y), (x, y + r)], fill=255)
    a = (np.asarray(m, dtype=np.float32) / 255.0)
    cell = TH * px
    yy = ((np.arange(Hp) + 0.5) / cell) % 1.0
    xx = ((np.arange(Wp) + 0.5) / cell) % 1.0
    ribs = np.sin(np.pi * yy).astype(np.float32)[:, None]
    flo = np.sin(np.pi * xx).astype(np.float32)[None, :]
    rng = np.random.default_rng(scene * 2 + which)
    jy = np.repeat(rng.normal(1.0, 0.02, int(Hp / cell) + 2), int(np.ceil(cell)))[:Hp].astype(np.float32)[:, None]
    jx = np.repeat(rng.normal(1.0, 0.02, int(Wp / cell) + 2), int(np.ceil(cell)))[:Wp].astype(np.float32)[None, :]
    shade = (a * (0.93 + 0.07 * flo) * jx + (1 - a) * (0.88 + 0.12 * ribs) * jy)
    g, fg = (NAVY, IVORY) if which == 0 else (IVORY, NAVY)
    col = (a[..., None] * np.array(fg, np.float32) + (1 - a[..., None]) * np.array(g, np.float32)) * shade[..., None]
    stem = f".rib-{scene}-{'front' if which == 0 else 'back'}"
    Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").save(HERE / (stem + ".png"))
    h = a * (0.66 + 0.34 * flo) + (1 - a) * (0.25 + 0.30 * ribs)
    Image.fromarray((h * 255).astype(np.uint8), "L").save(HERE / (stem + "-h.png"))
    print("wrote", scene, which, Wp, Hp, flush=True)


if __name__ == "__main__":
    for sc in ([int(a) for a in sys.argv[1:]] or [1, 2, 3]):
        side(sc, 0); side(sc, 1)
