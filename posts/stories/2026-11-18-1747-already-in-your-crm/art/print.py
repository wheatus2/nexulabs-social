"""Prints for the duplicate book: the white top sheet (blue biro), the yellow copy under it (carbon),
and a height map of the pen strokes. Handwriting is a single-stroke Hershey script, smoothed and jittered.
  python3.13 print.py   -> .top.png .copy.png .press.png  (1680x2368, 16px per mm of a 105x148mm sheet)
"""
import asyncio, random, math
from pathlib import Path
from HersheyFonts import HersheyFonts
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
W, H = 1680, 2368
FIELDS = [("Name", "Jo Okafor"), ("Phone", "07700 900412"), ("Job", "New side gate"), ("When", "Any Friday")]
ROW0, ROWH, LEFT = 760, 372, 150


def hand(text, x, base, size, seed):
    f = HersheyFonts(); f.load_default_font("scripts"); f.normalize_rendering(size)
    rng = random.Random(seed)
    paths = []
    drift = rng.uniform(-0.012, 0.004)
    for st in f.strokes_for_text(text):
        pts = [(x + px + rng.uniform(-1.2, 1.2), base - py + (px * drift) + rng.uniform(-1.2, 1.2)) for px, py in st]
        if len(pts) < 2:
            continue
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        P = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        paths.append(d)
    return paths


def strokes():
    out = []
    for i, (_, val) in enumerate(FIELDS):
        out += hand(val, LEFT + 40, ROW0 + i * ROWH + 238, 150, 11 + i)
    return out


def page(kind):
    paper = {"top": "#F4F2EC", "copy": "#F2D94B", "press": "#000"}[kind]
    ink = {"top": "#1B2FA6", "copy": "#343A7A", "press": "#fff"}[kind]
    rule = {"top": "#9FB0C8", "copy": "#8C7A1E", "press": "transparent"}[kind]
    label = {"top": "#1D2740", "copy": "#2B2609", "press": "transparent"}[kind]
    head = {"top": "Website enquiry", "copy": "CRM copy", "press": ""}[kind]
    sw = {"top": 7.5, "copy": 9.5, "press": 9}[kind]
    paths = "".join(f'<path d="{d}"/>' for d in strokes())
    rows = "".join(
        f'<div class="lab" style="top:{ROW0 + i * ROWH}px">{lab}</div><div class="rule" style="top:{ROW0 + i * ROWH + 292}px"></div>'
        for i, (lab, _) in enumerate(FIELDS))
    filt = ""
    if kind == "copy":
        filt = '''<filter id="carbon" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="4" result="n"/>
        <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 2.0" result="m"/>
        <feGaussianBlur in="SourceGraphic" stdDeviation="1.0" result="b"/><feComposite in="b" in2="m" operator="in"/></filter>'''
    fonts = (ROOT / "fonts").as_uri()
    return f'''<html><body style="margin:0"><style>
@font-face{{font-family:Mono;src:url({fonts}/GeistMono-Medium.woff2)}}
@font-face{{font-family:Out;src:url({fonts}/outfit-latin-700-normal.woff2)}}
.s{{position:relative;width:{W}px;height:{H}px;background:{paper};overflow:hidden}}
.perf{{position:absolute;left:0;right:0;top:150px;height:0;border-top:7px dotted {rule};opacity:.9}}
.head{{position:absolute;left:{LEFT}px;top:300px;font:700 150px/1 Out;letter-spacing:-.02em;color:{label}}}
.no{{position:absolute;right:{LEFT}px;top:520px;font:500 96px/1 Mono;color:{"#C21A2B" if kind != "press" else "transparent"};letter-spacing:.02em}}
.kick{{position:absolute;left:{LEFT}px;top:535px;font:500 60px/1 Mono;letter-spacing:.12em;text-transform:uppercase;color:{label};opacity:.92}}
.lab{{position:absolute;left:{LEFT}px;font:500 56px/1 Mono;letter-spacing:.12em;text-transform:uppercase;color:{label}}}
.rule{{position:absolute;left:{LEFT}px;right:{LEFT}px;border-top:5px solid {rule}}}
svg{{position:absolute;left:0;top:0}}
</style><div class="s"><div class="perf"></div><div class="head">{head}</div><div class="kick">{"Top copy" if kind == "top" else "Stays in the book"}</div><div class="no">No 0218</div>{rows}
<svg width="{W}" height="{H}"><defs>{filt}</defs><g fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {'filter="url(#carbon)" opacity=".86" transform="translate(5,7)"' if kind == "copy" else ""}>{paths}</g></svg>
</div></body></html>'''


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        for kind in ("top", "copy", "press"):
            (HERE / ".print.html").write_text(page(kind)); await pg.goto((HERE / ".print.html").as_uri()); await pg.wait_for_timeout(500)
            await pg.screenshot(path=str(HERE / f".{kind}.png"))
        await b.close()

asyncio.run(main())
