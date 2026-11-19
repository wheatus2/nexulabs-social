"""Draws the print on both sides of the tape measure (run with python3.13, before build.py).

Front: ivory, millimetre ticks along the foot, a numeral at every centimetre, the tens in violet,
and the Nexulabs wordmark (the real SVG, brand/nexulabs-logo-white.svg) as the maker's mark before 0.
Back: violet, ticks along the top, and kinds of business where the numbers would be.
Writes .tape-front.png and .tape-back.png (20 px to the millimetre). The tape is made up.
"""
import io, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PX = 20                      # pixels per millimetre
LEAD = 90                    # mm of tape before the 0 mark
LEN = 1500                   # mm of scale
TOTAL = LEAD + LEN + 10
WID = 20                     # mm
IVORY = (240, 233, 214)
INK = (24, 19, 40)
VIOLET = (62, 36, 190)
TRADES = ["CAFÉS", "JOINERS", "SALONS", "VETS", "GARAGES", "FLORISTS", "BUILDERS", "BAKERS", "DENTISTS",
          "PLUMBERS", "GYMS", "ROOFERS", "BARBERS", "SOLICITORS"]


def ttf(name):
    out = HERE / f".{name}.ttf"
    if not out.exists():
        f = TTFont(str(ROOT / "fonts" / f"{name}.woff2")); f.flavor = None; f.save(str(out))
    return str(out)


def logo(height_px, colour):
    """The wordmark SVG, rasterised by the browser, as an RGBA image."""
    from playwright.sync_api import sync_playwright
    svg = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text()
    svg = re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="rgb{colour}"', svg)
    w = round(height_px * 4021 / 722)
    svg = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{w}" height="{height_px}"', svg, count=1)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=next(str(x) for x in Path("/opt/pw-browsers").glob("chromium*/chrome-linux*/chrome"))); pg = b.new_page(viewport={"width": w, "height": height_px})
        pg.set_content(f'<body style="margin:0;background:transparent">{svg}</body>')
        png = pg.screenshot(omit_background=True); b.close()
    return Image.open(io.BytesIO(png)).convert("RGBA")


def spaced(d, x, y, text, font, fill, track):
    """Text with letter-spacing, centred on x. Returns nothing."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    cx = x - total / 2
    for ch, w in zip(text, widths):
        d.text((cx, y), ch, font=font, fill=fill, anchor="ls"); cx += w + track


def front():
    im = Image.new("RGB", (TOTAL * PX, WID * PX), IVORY); d = ImageDraw.Draw(im)
    num = ImageFont.truetype(ttf("inter-tight-latin-700-normal"), int(6.6 * PX))
    num3 = ImageFont.truetype(ttf("inter-tight-latin-700-normal"), int(5.0 * PX))
    ten = ImageFont.truetype(ttf("inter-tight-latin-800-normal"), int(8.4 * PX))
    H = WID * PX
    for mm in range(0, LEN + 1):
        x = (LEAD + mm) * PX
        if mm % 10 == 0:
            h, w = 6.2, 0.34
        elif mm % 5 == 0:
            h, w = 4.4, 0.26
        else:
            h, w = 2.8, 0.22
        d.rectangle([x - w * PX / 2, H - h * PX, x + w * PX / 2, H], fill=INK)
    for cm in range(1, LEN // 10 + 1):
        x = (LEAD + cm * 10) * PX
        base = H - 8.0 * PX
        if cm % 10 == 0:
            d.text((x, base), str(cm), font=ten, fill=VIOLET, anchor="ms")
        else:
            d.text((x, base), str(cm), font=num3 if cm > 100 else num, fill=INK, anchor="ms")
    d.rectangle([LEAD * PX, int(1.5 * PX), (LEAD + LEN) * PX, int(1.5 * PX) + int(0.22 * PX)], fill=INK)
    lg = logo(int(9.4 * PX), INK)
    im.paste(lg, (int(19 * PX), (H - lg.size[1]) // 2 + int(0.4 * PX)), lg)
    im.save(HERE / ".tape-front.png")


def back():
    im = Image.new("RGB", (TOTAL * PX, WID * PX), VIOLET); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(ttf("inter-tight-latin-800-normal"), int(8.6 * PX))
    for mm in range(0, TOTAL, 1):
        x = mm * PX
        h, w = (4.6, 0.30) if mm % 10 == 0 else ((3.2, 0.24) if mm % 5 == 0 else (0, 0))
        if h:
            d.rectangle([x - w * PX / 2, 0, x + w * PX / 2, h * PX], fill=IVORY)
    x = 12 * PX; i = 0
    gap = 30 * PX
    while x < (TOTAL - 60) * PX:
        w = sum(d.textlength(ch, font=f) for ch in TRADES[i % len(TRADES)]) + 0.7 * PX * (len(TRADES[i % len(TRADES)]) - 1)
        spaced(d, x + w / 2, int(14.6 * PX), TRADES[i % len(TRADES)], f, IVORY, 0.7 * PX)
        dx = x + w + gap; r = 1.1 * PX
        d.ellipse([dx - r, 11.3 * PX - r, dx + r, 11.3 * PX + r], fill=IVORY)
        x = dx + gap; i += 1
    im.save(HERE / ".tape-back.png")


if __name__ == "__main__":
    front(); back(); print("wrote tape prints", TOTAL * PX, WID * PX)
