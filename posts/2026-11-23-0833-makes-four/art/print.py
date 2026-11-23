"""Prints for the bakery boxes and bag. Everything on them is made up (Brindlow is not a real bakery).
Before: three box fronts with three different logos, and a rubber-stamped bag with a fourth.
After: one brand (oxblood on cream) used on all of them.
  python3.13 print.py   -> .a-*.png (before) and .b-*.png (after), 100px per cm
"""
import asyncio, math, random
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = 100
CARD = "#F3EEE3"
OX = "#6E1423"
CREAM = "#F6EBDD"
# box fronts (width x lid height, cm) and the bag front
BOXES = {"1": (30, 10.4), "2": (24.5, 9.4), "3": (19, 8.4)}
TOP = (19, 19)
BAG = (17, 33)


def css():
    f = (ROOT / "fonts").as_uri()
    return f'''@font-face{{font-family:PlayI;src:url({f}/playfair-display-latin-500-italic.woff2)}}
@font-face{{font-family:Play;font-weight:700;src:url({f}/playfair-display-latin-700-normal.woff2)}}
@font-face{{font-family:Anton;src:url({f}/anton-latin-400-normal.woff2)}}
@font-face{{font-family:Outfit;font-weight:700;src:url({f}/outfit-latin-700-normal.woff2)}}
@font-face{{font-family:Outfit;font-weight:500;src:url({f}/outfit-latin-500-normal.woff2)}}
@font-face{{font-family:Oswald;font-weight:700;src:url({f}/oswald-latin-700-normal.woff2)}}
@font-face{{font-family:Fraun;font-weight:600;src:url({f}/fraunces-latin-600-normal.woff2)}}
@font-face{{font-family:FraunI;font-weight:600;src:url({f}/fraunces-latin-600-italic.woff2)}}
@font-face{{font-family:Mono;src:url({f}/GeistMono-Medium.woff2)}}
body{{margin:0}} .s{{position:relative;overflow:hidden}} .c{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}}
svg{{display:block}}'''


def page(w, h, bg, body, style=""):
    return f'<html><body><style>{css()}.s{{width:{int(w * S)}px;height:{int(h * S)}px;background:{bg}}}{style}</style><div class="s">{body}</div></body></html>'


def wheat(col, h=560):
    g = ""
    for i in range(6):
        y = 60 + i * 62
        for s in (-1, 1):
            g += f'<ellipse cx="{100 + s * 34}" cy="{y + 30}" rx="20" ry="46" transform="rotate({s * 28} {100 + s * 34} {y + 30})"/>'
    g += '<ellipse cx="100" cy="34" rx="20" ry="46"/>'
    return f'<svg width="{h * 200 / 560:.0f}" height="{h}" viewBox="0 0 200 560" fill="{col}">{g}<rect x="94" y="60" width="12" height="490" rx="6"/></svg>'


# ---------- before ----------
def a1():
    w, h = BOXES["1"]
    blue = "#1C3F9E"
    return page(w, h, CARD, f'''<div class="o"><div class="n">Brindlow&rsquo;s</div><div class="t">FAMILY BAKERS &middot; EST. 1987</div></div>''', f'''
.o{{position:absolute;left:330px;right:330px;top:120px;bottom:120px;border:14px solid {blue};border-radius:50%;box-shadow:inset 0 0 0 18px {CARD},inset 0 0 0 23px {blue};display:flex;flex-direction:column;align-items:center;justify-content:center;color:{blue}}}
.n{{font:500 400px/1 PlayI;letter-spacing:-.005em;margin-top:-50px}}
.t{{font:700 76px/1 Play;letter-spacing:.2em;margin-top:38px;margin-right:-.2em}}''')


def a2():
    w, h = BOXES["2"]
    g = "#145C36"
    return page(w, h, CARD, f'''<div class="c"><div class="r">{wheat(g, 520)}<div><div class="n">BRINDLOW</div><div class="t">&amp; SON &nbsp;BAKERS</div></div>{wheat(g, 520)}</div></div>''', f'''
.r{{display:flex;align-items:center;gap:90px;color:{g}}}
.n{{font:400 400px/.9 Anton;letter-spacing:.015em}}
.t{{font:400 132px/1 Anton;letter-spacing:.27em;margin-top:34px;text-align:center;margin-right:-.27em}}''')


def a3():
    w, h = BOXES["3"]
    return page(w, h, CARD, '''<div class="c"><div class="r"><i></i><div><div class="n">the brindlow</div><div class="n">bakehouse</div></div></div></div>''', '''
.r{display:flex;align-items:center;gap:70px;color:#17181B}
.r i{width:330px;height:330px;border-radius:50%;background:#F2CB1D;display:block}
.n{font:700 196px/1.02 Outfit;letter-spacing:-.02em}''')


def stamp():
    """A round rubber stamp, a little off square, the ink uneven."""
    w, h = BAG
    W_, H_ = int(w * S), int(h * S)
    ink = "#4B3524"
    rng = random.Random(11)
    blots = "".join(f'<circle cx="{rng.uniform(-560, 560):.0f}" cy="{rng.uniform(-560, 560):.0f}" r="{rng.uniform(4, 15):.0f}"/>' for _ in range(70))
    return page(w, h, CARD, f'''<svg width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}">
<defs><path id="ct" d="M -415 0 A 415 415 0 1 1 415 0"/><path id="cb" d="M -468 0 A 468 468 0 0 0 468 0"/>
<filter id="rough" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="4"/><feDisplacementMap in="SourceGraphic" scale="9"/></filter>
<mask id="m"><rect x="-700" y="-700" width="1400" height="1400" fill="#fff"/><g fill="#000">{blots}</g><rect x="-700" y="210" width="1400" height="60" fill="#000" opacity=".35" transform="rotate(-18)"/></mask></defs>
<g transform="translate({W_ / 2:.0f} 1880) rotate(-7)" filter="url(#rough)"><g mask="url(#m)" fill="{ink}" opacity=".9">
<circle r="575" fill="none" stroke="{ink}" stroke-width="20"/><circle r="535" fill="none" stroke="{ink}" stroke-width="7"/>
<circle r="268" fill="none" stroke="{ink}" stroke-width="9"/>
<text font-family="Oswald" font-weight="700" font-size="128" letter-spacing="8" text-anchor="middle"><textPath href="#ct" startOffset="50%">BRINDLOWS BAKERY</textPath></text>
<text font-family="Oswald" font-weight="700" font-size="104" letter-spacing="16" text-anchor="middle"><textPath href="#cb" startOffset="50%">FRESH EVERY DAY</textPath></text>
<text font-family="Play" font-weight="700" font-size="330" text-anchor="middle" y="112">B</text>
<circle cx="-485" cy="45" r="16"/><circle cx="485" cy="45" r="16"/>
</g></g></svg>''')


# ---------- after ----------
def word(size, col, sub=True, subcol=None):
    s = f'<div style="font:600 {size}px/1 Fraun;letter-spacing:-.025em;color:{col}">Brindlow</div>'
    if sub:
        s += f'<div style="font:400 {size * .135:.0f}px/1 Mono;letter-spacing:.42em;margin-right:-.42em;color:{subcol or col};margin-top:{size * .16:.0f}px">BAKEHOUSE &middot; SINCE 1987</div>'
    return s


def mono(d, fg, bg):
    return f'<div style="width:{d}px;height:{d}px;border-radius:50%;background:{bg};color:{fg};display:flex;align-items:center;justify-content:center;font:600 {d * .74:.0f}px/1 FraunI"><span style="margin-top:-{d * .05:.0f}px;margin-left:-{d * .02:.0f}px">B</span></div>'


def b1():
    w, h = BOXES["1"]
    return page(w, h, CREAM, f'<div class="c">{word(560, OX)}</div>')


def b2():
    w, h = BOXES["2"]
    return page(w, h, OX, f'<div class="c">{word(440, CREAM)}</div>')


def b3():
    w, h = BOXES["3"]
    return page(w, h, CREAM, f'<div class="c" style="flex-direction:row;gap:90px">{mono(430, CREAM, OX)}<div>{word(270, OX, sub=False)}<div style="font:400 40px/1 Mono;letter-spacing:.4em;color:{OX};margin-top:40px">BAKEHOUSE</div></div></div>')


def btop():
    w, h = TOP
    return page(w, h, CREAM, f'<div class="c">{mono(1050, CREAM, OX)}</div>')


def bbag():
    w, h = BAG
    return page(w, h, CREAM, f'<div class="c" style="justify-content:flex-start;padding-top:1520px">{mono(900, CREAM, OX)}<div style="height:150px"></div>{word(300, OX)}</div>')


def plain(w, h, col):
    return page(w, h, col, "")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        async def shot(html, name):
            import re
            m = re.search(r"\.s\{width:(\d+)px;height:(\d+)px", html)
            w, h = int(m.group(1)), int(m.group(2))
            pg = await b.new_page(viewport={"width": w, "height": h})
            (HERE / ".print.html").write_text(html); await pg.goto((HERE / ".print.html").as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(350)
            await pg.screenshot(path=str(HERE / name)); await pg.close()
        await shot(a1(), ".a-1.png"); await shot(a2(), ".a-2.png"); await shot(a3(), ".a-3.png"); await shot(stamp(), ".a-bag.png")
        await shot(b1(), ".b-1.png"); await shot(b2(), ".b-2.png"); await shot(b3(), ".b-3.png")
        await shot(btop(), ".b-top.png"); await shot(bbag(), ".b-bag.png")
        await b.close()
    (HERE / ".print.html").unlink()
    from PIL import Image
    names = [".a-1.png", ".a-2.png", ".a-3.png", ".a-bag.png", ".b-1.png", ".b-2.png", ".b-3.png", ".b-top.png", ".b-bag.png"]
    ims = [Image.open(HERE / n).convert("RGB") for n in names]
    ims = [i.resize((int(i.width * 300 / i.height) if i.height > i.width else 700, 300 if i.height > i.width else int(i.height * 700 / i.width))) for i in ims]
    sh = Image.new("RGB", (1500, 1000), "#888"); x = y = 10; rowh = 0
    for i in ims:
        if x + i.width > 1490:
            x = 10; y += rowh + 10; rowh = 0
        sh.paste(i, (x, y)); x += i.width + 10; rowh = max(rowh, i.height)
    sh.save(HERE / ".prints.jpg", quality=88)

if __name__ == "__main__":
    asyncio.run(main())
