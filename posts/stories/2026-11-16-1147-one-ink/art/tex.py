"""Draws the made-up bakery's logo (Halfloaf Bakehouse, Sunderland) and prints it two ways:
  tex/print.png   the impression on the paper bag: one ink, uneven, with pinholes where kraft fibres refused it
  tex/die.png     the rubber die, mirrored, as a height map (white = raised)
The logo is one colour by design: a ring of letters round a half loaf with three score cuts.
"""
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TTF = Path("/tmp/nx-archivo-800.ttf")
if not TTF.exists():
    f = TTFont(ROOT / "fonts" / "archivo-latin-800-normal.woff2"); f.flavor = None; f.save(TTF)

S = 2048
C = S / 2


def ring_text(d, text, radius, size, top=True, track=0.0):
    font = ImageFont.truetype(str(TTF), size)
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + track * size * (len(text) - 1)
    ang = total / radius                       # radians the text spans
    a = -math.pi / 2 - ang / 2 if top else math.pi / 2 + ang / 2
    for ch, w in zip(text, widths):
        step = (w + track * size) / radius
        mid = a + (w / 2) / radius * (1 if top else -1)
        im = Image.new("L", (size * 2, size * 2), 0)
        ImageDraw.Draw(im).text((size - w / 2, size), ch, font=font, fill=255, anchor="ls" if top else "lt")
        rot = -math.degrees(mid + math.pi / 2) if top else -math.degrees(mid - math.pi / 2)
        im = im.rotate(rot, resample=Image.BICUBIC, center=(size, size))
        x = C + radius * math.cos(mid) - size; y = C + radius * math.sin(mid) - size
        d._image.paste(255, (int(x), int(y)), im) if False else None
        yield im, int(round(x)), int(round(y))
        a += step if top else -step


def logo():
    im = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(im)
    # outer ring and inner hairline ring
    d.ellipse([C - 960, C - 960, C + 960, C + 960], fill=255)
    d.ellipse([C - 905, C - 905, C + 905, C + 905], fill=0)
    d.ellipse([C - 640, C - 640, C + 640, C + 640], fill=255)
    d.ellipse([C - 618, C - 618, C + 618, C + 618], fill=0)
    for g, x, y in ring_text(d, "HALFLOAF", 690, 200, True, 0.10):
        im.paste(255, (x, y), g)
    for g, x, y in ring_text(d, "BAKEHOUSE", 690, 150, False, 0.16):
        im.paste(255, (x, y), g)
    # two dots on the ring's sides
    for sx in (-1, 1):
        d.ellipse([C + sx * 770 - 26, C - 26, C + sx * 770 + 26, C + 26], fill=255)
    # the half loaf: a dome on a flat base, three score cuts as gaps
    R = 420; by = C + 190
    d.pieslice([C - R, by - R, C + R, by + R], 180, 360, fill=255)
    d.rectangle([C - R, by - 4, C + R, by + 58], fill=255)
    cut = Image.new("L", (S, S), 0); dc = ImageDraw.Draw(cut)
    for k in (-1, 0, 1):
        cx = C + k * 190; cy = by - 210 + abs(k) * 40
        L = 150 - abs(k) * 20
        dc.line([(cx - L * 0.55, cy + L * 0.75), (cx + L * 0.55, cy - L * 0.75)], fill=255, width=46)
        for px, py in ((cx - L * 0.55, cy + L * 0.75), (cx + L * 0.55, cy - L * 0.75)):
            dc.ellipse([px - 23, py - 23, px + 23, py + 23], fill=255)
    a = np.asarray(im, np.float32) / 255
    a = np.clip(a - np.asarray(cut, np.float32) / 255, 0, 1)
    # base line under the loaf, separate
    return a


def main():
    a = logo()
    rng = np.random.default_rng(7)
    # print: ink spreads a touch into the paper, fills unevenly, pinholes; the stamp pressed harder on the left
    p = gaussian_filter(a, 2.4); p = np.clip((p - 0.5) * 2.6 + 0.5, 0, 1)
    broad = gaussian_filter(rng.normal(0, 1, (S, S)), 90); broad /= np.abs(broad).max()
    fine = gaussian_filter(rng.normal(0, 1, (S, S)), 3); fine /= np.abs(fine).max()
    holes = gaussian_filter(rng.random((S, S)), 1.6)
    holes = (holes > np.quantile(holes, 0.03)).astype(np.float32)
    yy, xx = np.mgrid[0:S, 0:S]
    press = np.clip(1.0 - 0.12 * (xx / S) ** 2, 0, 1)
    ink = np.clip(1.0 + 0.10 * broad + 0.08 * fine, 0.55, 1.0) * gaussian_filter(holes, 0.9) * press
    rgba = np.zeros((S, S, 4), np.uint8); rgba[..., :3] = 255
    rgba[..., 3] = (np.clip(p * ink, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(HERE / "tex" / "print.png")
    # die: mirrored, slightly rounded shoulders
    die = gaussian_filter(a[:, ::-1], 3.0)
    Image.fromarray((np.clip(die, 0, 1) * 65535).astype(np.uint16)).save(HERE / "tex" / "die.png")
    Image.fromarray((a * 255).astype(np.uint8)).save(HERE / "tex" / "logo-flat.png")
    print("ok")


if __name__ == "__main__":
    main()
