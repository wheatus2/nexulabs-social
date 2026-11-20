"""Prints for the Oxlip props (a made-up restaurant): matchbox sleeve, striker, coaster, table card.
  python3.13 print.py   -> .sleeve.png .striker.png .coaster.png .tent.png .blank.png   (200px per cm)
"""
import asyncio, math
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = 200
LILAC, INK, CREAM = "#B9A2F5", "#17130F", "#EFE7D3"


def mark(size, col, hole):
    """The Oxlip mark: five round petals and a centre."""
    c = "".join(f'<circle cx="{50 + 25 * math.sin(math.radians(72 * i)):.2f}" cy="{50 - 25 * math.cos(math.radians(72 * i)):.2f}" r="21.5"/>' for i in range(5))
    return f'<svg width="{size}" height="{size}" viewBox="0 0 100 100"><g fill="{col}">{c}</g><circle cx="50" cy="50" r="9.5" fill="{hole}"/></svg>'


def css():
    fonts = (ROOT / "fonts").as_uri()
    return f'''@font-face{{font-family:Fr;src:url({fonts}/fraunces-latin-600-normal.woff2)}}
@font-face{{font-family:Fi;src:url({fonts}/fraunces-latin-400-italic.woff2)}}
@font-face{{font-family:G;src:url({fonts}/Geist-SemiBold.woff2)}}
body{{margin:0}} .s{{position:relative;overflow:hidden}} .a{{position:absolute}}'''


def sleeve():
    w, h = int(5.3 * S), int(3.6 * S)
    return w, h, f'''<html><body><style>{css()}</style><div class="s" style="width:{w}px;height:{h}px;background:{LILAC}">
<div class="a" style="left:90px;top:{(h - 290) // 2}px">{mark(290, INK, LILAC)}</div>
<div class="a" style="left:428px;top:{h // 2 - 132}px;font:600 215px/1 Fr;letter-spacing:-.01em;color:{INK}">Oxlip</div>
</div></body></html>'''


def blank():
    """The next box: a proof with the mark and the name still to come."""
    w, h = int(5.3 * S), int(3.6 * S)
    g = "#8F8B7E"
    return w, h, f'''<html><body><style>{css()}</style><div class="s" style="width:{w}px;height:{h}px;background:#F4F1E8">
<svg class="a" style="left:90px;top:{(h - 290) // 2}px" width="290" height="290"><circle cx="145" cy="145" r="132" fill="none" stroke="{g}" stroke-width="9" stroke-dasharray="26 20"/></svg>
<div class="a" style="left:428px;top:{h // 2 - 72}px;font:600 114px/1 Fr;letter-spacing:-.01em;white-space:nowrap;color:{g}">Your name</div>
</div></body></html>'''


def striker():
    w, h = int(5.3 * S), int(1.6 * S)
    return w, h, f'''<html><body><style>{css()}</style><div class="s" style="width:{w}px;height:{h}px;background:{LILAC}">
<div class="a" style="left:70px;right:70px;top:66px;bottom:66px;background:#2A1A16;border-radius:6px"></div></div></body></html>'''


def striker_blank():
    w, h = int(5.3 * S), int(1.6 * S)
    return w, h, f'''<html><body><style>{css()}</style><div class="s" style="width:{w}px;height:{h}px;background:#F4F1E8">
<div class="a" style="left:70px;right:70px;top:66px;bottom:66px;background:#2A1A16;border-radius:6px"></div></div></body></html>'''


def coaster():
    w = int(9.4 * S)
    r = w / 2
    return w, w, f'''<html><body><style>{css()}</style><div class="s" style="width:{w}px;height:{w}px;background:{CREAM}">
<svg class="a" width="{w}" height="{w}" viewBox="0 0 {w} {w}">
<circle cx="{r}" cy="{r}" r="{r - 70}" fill="none" stroke="{INK}" stroke-width="10"/>
<circle cx="{r}" cy="{r}" r="{r - 330}" fill="{LILAC}"/>
<defs><path id="c" d="M {r},{r} m -{r - 235},0 a {r - 235},{r - 235} 0 1,1 {2 * (r - 235)},0 a {r - 235},{r - 235} 0 1,1 -{2 * (r - 235)},0"/></defs>
<text font-family="G" font-size="124" letter-spacing="46" fill="{INK}" text-anchor="middle"><textPath href="#c" startOffset="25%">OXLIP  ·  KITCHEN &amp; BAR</textPath></text>
</svg>
<div class="a" style="left:{r - 420}px;top:{r - 420}px">{mark(840, INK, LILAC)}</div>
</div></body></html>'''


def tent():
    w, h = int(10.0 * S), int(7.4 * S)
    return w, h, f'''<html><body><style>{css()}</style><div class="s" style="width:{w}px;height:{h}px;background:{CREAM}">
<div class="a" style="left:0;right:0;top:150px;display:flex;justify-content:center">{mark(360, INK, CREAM)}</div>
<div class="a" style="left:0;right:0;top:590px;text-align:center;font:400 360px/1 Fi;color:{INK}">Reserved</div>
<div class="a" style="left:0;right:0;bottom:0;height:230px;background:{LILAC}"></div>
<div class="a" style="left:0;right:0;bottom:62px;text-align:center;font:600 104px/1 G;letter-spacing:.3em;text-indent:.3em;color:{INK}">OXLIP</div>
</div></body></html>'''


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        for name, fn in [("sleeve", sleeve), ("blank", blank), ("striker", striker), ("striker-blank", striker_blank), ("coaster", coaster), ("tent", tent)]:
            w, h, html = fn()
            pg = await b.new_page(viewport={"width": w, "height": h})
            (HERE / ".print.html").write_text(html); await pg.goto((HERE / ".print.html").as_uri()); await pg.wait_for_timeout(400)
            await pg.screenshot(path=str(HERE / f".{name}.png")); await pg.close()
        await b.close()
    (HERE / ".print.html").unlink()

if __name__ == "__main__":
    asyncio.run(main())
