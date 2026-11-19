"""Prints for the rotary card file: the typed customer card (with one pencil note), the Nexulabs card,
and the A to Z index tabs. Everything on the cards is made up.
  python3.13 print.py   -> .card-dunn.png .card-nx.png .tab-<L>.png   (200px per cm)
A card is 10.2 x 5.7 cm; an index card is the same with a 0.9 cm tab on top (so 10.2 x 6.6 cm).
"""
import asyncio, random, string
from pathlib import Path
from HersheyFonts import HersheyFonts
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = 200
CW, CH, TAB = int(10.2 * S), int(5.7 * S), int(0.9 * S)
TABW = int(1.9 * S)
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "")
PAPER, BUFF, PINK = "#F1ECDD", "#D8C593", "#E0237A"


def tab_x(k):
    """Left edge of tab k (0..4) on the card, px."""
    return int((0.35 + k * 1.9) * S)


def hand(text, x, base, size, seed, slope=-0.05):
    f = HersheyFonts(); f.load_default_font("scripts"); f.normalize_rendering(size)
    rng = random.Random(seed)
    paths = []
    for st in f.strokes_for_text(text):
        pts = [(x + px + rng.uniform(-1.0, 1.0), base - py + px * slope + rng.uniform(-1.0, 1.0)) for px, py in st]
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


def css():
    fonts = (ROOT / "fonts").as_uri()
    return f'''@font-face{{font-family:Mono;src:url({fonts}/GeistMono-Medium.woff2)}}
@font-face{{font-family:Out;src:url({fonts}/outfit-latin-700-normal.woff2)}}
body{{margin:0}} .s{{position:relative;overflow:hidden}} svg.h{{position:absolute;left:0;top:0}}'''


def dunn():
    paths = "".join(f'<path d="{d}"/>' for d in hand("fence quote??", 165, 880, 132, 5, slope=-0.035) + hand("ask Dave", 165, 1055, 132, 9, slope=-0.035))
    return f'''<html><body><style>{css()}
.s{{width:{CW}px;height:{CH}px;background:{PAPER}}}
.n{{position:absolute;left:150px;top:150px;font:500 172px/1 Mono;letter-spacing:.01em;color:#1a1a1c}}
.l{{position:absolute;left:150px;font:500 112px/1 Mono;color:#2a2a2d}}
.r{{position:absolute;left:150px;right:150px;top:372px;border-top:5px solid #B9364A;opacity:.75}}
</style><div class="s"><div class="n">DUNN, Mrs P.</div><div class="r"></div>
<div class="l" style="top:440px">3 Larkspur Row</div><div class="l" style="top:590px">07700 900146</div>
<svg class="h" width="{CW}" height="{CH}"><g fill="none" stroke="#3c3c42" stroke-width="9.5" stroke-linecap="round" stroke-linejoin="round" opacity=".9">{paths}</g></svg>
</div></body></html>'''


def nx():
    logo = LOGO.replace('fill="#667DFF"', 'fill="#FFFFFF"')
    return f'''<html><body><style>{css()}
.s{{width:{CW}px;height:{CH}px;background:{PINK}}}
.g{{position:absolute;left:150px;top:170px;height:250px}} .g svg{{height:100%;width:auto;display:block}}
.l{{position:absolute;left:156px;font:500 112px/1 Mono;color:#fff}}
</style><div class="s"><div class="g">{logo}</div>
<div class="l" style="top:560px">Custom CRM systems</div>
</div></body></html>'''


def tab(letter, k):
    return f'''<html><body><style>{css()}
.s{{width:{CW}px;height:{CH + TAB}px;background:{BUFF}}}
.t{{position:absolute;left:{tab_x(k)}px;top:10px;width:{TABW}px;height:{TAB}px;font:700 150px/{TAB}px Out;text-align:center;color:#1d1a12}}
</style><div class="s"><div class="t">{letter}</div></div></body></html>'''


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        async def shot(html, name, w, h):
            pg = await b.new_page(viewport={"width": w, "height": h})
            (HERE / ".print.html").write_text(html); await pg.goto((HERE / ".print.html").as_uri()); await pg.wait_for_timeout(350)
            await pg.screenshot(path=str(HERE / name)); await pg.close()
        await shot(dunn(), ".card-dunn.png", CW, CH)
        await shot(nx(), ".card-nx.png", CW, CH)
        for i, L in enumerate(string.ascii_uppercase):
            await shot(tab(L, i % 5), f".tab-{L}.png", CW, CH + TAB)
        await shot(tab("", 0), ".tab-blank.png", CW, CH + TAB)   # for a tab that is half hidden in a shot: no sliced letter
        await b.close()
    (HERE / ".print.html").unlink()

if __name__ == "__main__":
    asyncio.run(main())
