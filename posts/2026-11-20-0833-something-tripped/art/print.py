"""Prints for the breaker box: the four breaker faces (on and off), the label strip under the row,
the hand-filled chart inside the door (before and after) and the yellow Nexulabs sticker.
Everything written on them is made up.
  python3.13 print.py   -> .face-<n>-<on|off>.png .labels.png .chart-a.png .chart-b.png .sticker.png  (200px per cm)
"""
import asyncio, random
from pathlib import Path
from HersheyFonts import HersheyFonts
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = 200
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "")
NAMES = ["WEBSITE", "EMAIL", "DOMAIN", "HOSTING"]
YEL = "#F3E11C"


def hand(text, x, base, size, seed, slope=-0.03, font="scripts"):
    f = HersheyFonts(); f.load_default_font(font); f.normalize_rendering(size)
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
@font-face{{font-family:Arch;font-weight:800;src:url({fonts}/archivo-latin-800-normal.woff2)}}
@font-face{{font-family:Arch;font-weight:500;src:url({fonts}/archivo-latin-500-normal.woff2)}}
body{{margin:0}} .s{{position:relative;overflow:hidden}} svg.h{{position:absolute;left:0;top:0}}'''


FW, FH = int(2.34 * S), int(3.4 * S)


def face(n, on):
    win = "#35C46A" if on else "#E3242B"
    return f'''<html><body><style>{css()}
.s{{width:{FW}px;height:{FH}px;background:#1B1C1F;color:#C9CBD0}}
.n{{position:absolute;right:40px;top:36px;font:800 78px/1 Arch}}
.w{{position:absolute;left:50%;margin-left:-56px;bottom:112px;width:112px;height:44px;border-radius:8px;background:{win};box-shadow:inset 0 0 0 5px rgba(0,0,0,.35)}}
.t{{position:absolute;left:0;right:0;bottom:40px;text-align:center;font:500 46px/1 Mono;letter-spacing:.06em;color:#8E9198}}
</style><div class="s"><div class="n">{n}</div><div class="w"></div><div class="t">{"ON" if on else "OFF"}</div></div></body></html>'''


LW, LH = int(9.6 * S), int(5.2 * S)


def labels():
    cells = "".join(f'<div class="c" style="left:{i * 480}px"><span>{w}</span></div>' for i, w in enumerate(NAMES))
    return f'''<html><body><style>{css()}
.s{{width:{LW}px;height:{LH}px;background:#F4F2EC}}
.c{{position:absolute;top:0;width:480px;height:{LH}px;border-left:4px solid #C9C6BC;box-sizing:border-box}}
.c:first-child{{border-left:0}}
.c span{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(-90deg);font:800 188px/1 Arch;letter-spacing:.02em;color:#17171A;white-space:nowrap}}
</style><div class="s">{cells}</div></body></html>'''


CW, CH = int(12 * S), int(16.35 * S)
NOTES_A = ["Kev's lad, 2019", "came with the wifi?", "Sue. (Sue's left)", "no idea"]
NOTES_B = ["Nexulabs"] * 4


def chart(notes, seed, fill="Fill in"):
    rows, ink = "", ""
    for i, (nm, note) in enumerate(zip(NAMES, notes)):
        top = 560 + i * 620
        rows += f'<div class="r" style="top:{top}px"><b>{i + 1}</b><i>{nm}</i></div><div class="ln" style="top:{top + 540}px"></div>'
        size = 215 if len(note) < 12 else 190
        ink += "".join(f'<path d="{d}"/>' for d in hand(note, 250, top + 400, size, seed + i * 7, slope=-0.022))
    return f'''<html><body><style>{css()}
.s{{width:{CW}px;height:{CH}px;background:#F3EFE4}}
.t{{position:absolute;left:200px;top:190px;font:800 150px/1 Arch;letter-spacing:.02em;color:#1a1a1c}}
.u{{position:absolute;right:200px;top:226px;font:500 78px/1 Mono;color:#77756d}}
.hr{{position:absolute;left:200px;right:200px;top:420px;border-top:12px solid #1a1a1c}}
.r{{position:absolute;left:200px;font:800 96px/1 Arch;letter-spacing:.05em;color:#1a1a1c}}
.r b{{display:inline-block;width:110px;font-weight:800;color:#8a877e}} .r i{{font-style:normal}}
.ln{{position:absolute;left:200px;right:200px;border-top:5px solid #BDB9AD}}
</style><div class="s"><div class="t">WHO TO RING</div><div class="u">{fill}</div><div class="hr"></div>{rows}
<svg class="h" width="{CW}" height="{CH}"><g fill="none" stroke="#1F2C6B" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" opacity=".92">{ink}</g></svg>
</div></body></html>'''


SW, SH = int(9.6 * S), int(3.0 * S)


def sticker():
    logo = LOGO.replace('fill="#667DFF"', 'fill="#111114"').replace('fill="#FFFFFF"', 'fill="#111114"').replace('fill="#fff"', 'fill="#111114"').replace('fill="white"', 'fill="#111114"')
    return f'''<html><body><style>{css()}
.s{{width:{SW}px;height:{SH}px;background:{YEL}}}
.g{{position:absolute;left:0;right:0;top:160px;height:280px;display:flex;justify-content:center;color:#111114}} .g svg{{height:100%;width:auto;display:block}}
</style><div class="s"><div class="g">{logo}</div></div></body></html>'''


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        async def shot(html, name, w, h):
            pg = await b.new_page(viewport={"width": w, "height": h})
            (HERE / ".print.html").write_text(html); await pg.goto((HERE / ".print.html").as_uri()); await pg.wait_for_timeout(350)
            await pg.screenshot(path=str(HERE / name)); await pg.close()
        for n in range(1, 5):
            await shot(face(n, True), f".face-{n}-on.png", FW, FH)
            await shot(face(n, False), f".face-{n}-off.png", FW, FH)
        await shot(labels(), ".labels.png", LW, LH)
        await shot(chart(NOTES_A, 3), ".chart-a.png", CW, CH)
        await shot(chart(NOTES_B, 40, ""), ".chart-b.png", CW, CH)
        await shot(sticker(), ".sticker.png", SW, SH)
        await b.close()
    (HERE / ".print.html").unlink()

if __name__ == "__main__":
    asyncio.run(main())
