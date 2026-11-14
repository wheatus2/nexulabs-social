"""Prints the faces of the five leaves of the colour fan as pictures for build.py to put on them (python3 cards.py).

A fan deck for one made-up logo: five leaves, 165 x 70 mm, riveted at the left end. Each has a white band
along its top edge with the colour's name at the far end from the rivet, and a field of colour with a small
line saying where that purple ended up. All five are called "Purple." The top leaf, the logo's own colour,
also exists in two more states: with its code in place of the name, and with the code and a line printed
across the field. 24 px to the millimetre, corners cut round in the mesh, not here.
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import studio

PX = 24
CW, CH, BAND, RAD = 165, 70, 25, 3.2      # millimetres
# from the top of the deck down; leaf 0 is the logo's real colour
CARDS = [
    dict(k=0, colour="#5B2A86", where="LOGO"),
    dict(k=1, colour="#6D3BB0", where="VAN"),
    dict(k=2, colour="#43297F", where="SIGN"),
    dict(k=3, colour="#8046A0", where="WEBSITE"),
    dict(k=4, colour="#55215F", where="UNIFORM"),
]
PAPER, INK = "#F4EFE6", "#22102F"
M = 6.8                                   # the right-hand margin everything printed hangs from

CSS = f"""
html,body{{background:transparent!important;margin:0}}
.c{{position:relative;width:{CW * PX}px;height:{CH * PX}px;overflow:hidden;margin:0 0 30px}}
.band{{position:absolute;left:0;right:0;top:0;height:{BAND * PX}px;background:{PAPER};color:{INK}}}
.name{{position:absolute;right:{(M - 0.37) * PX}px;top:{3.6 * PX}px;font:700 {17.6 * PX}px/1 News;letter-spacing:-.022em;white-space:nowrap}}
.code{{position:absolute;right:{(M - 0.13) * PX}px;top:{5.2 * PX}px;font:500 {14.6 * PX}px/1 GeistMono;letter-spacing:-.04em;white-space:nowrap}}
.field{{position:absolute;left:0;right:0;top:{BAND * PX}px;bottom:0;color:{PAPER}}}
.where{{position:absolute;right:{(M - 0.24) * PX}px;top:{4.6 * PX}px;font:500 {5.6 * PX}px/1 GeistMono;letter-spacing:.1em;margin-right:-.1em;white-space:nowrap;opacity:.92}}
.line{{position:absolute;right:{(M - 0.41) * PX}px;top:{12.4 * PX}px;font:700 {24 * PX}px/1 News;letter-spacing:-.022em;white-space:nowrap}}
.line i{{font-style:italic;letter-spacing:-.01em}}
"""


def card(c, state="name"):
    ident = f"c{c['k']}" + ("" if state == "name" else state)
    h = c["colour"].lstrip("#")
    rgb = " ".join(str(int(h[j:j + 2], 16)) for j in (0, 2, 4))
    band = '<div class="name">Purple.</div>' if state == "name" else f'<div class="code">{c["colour"]}</div>'
    field = {"name": f'<div class="where">{c["where"]}</div>',
             "code": f'<div class="where">RGB {rgb}</div>',
             "this": '<div class="line"><i>This</i> purple.</div>'}[state]
    return ident, (f'<div class="c" id="{ident}"><div class="field" style="background:{c["colour"]}">{field}</div>'
                   f'<div class="band">{band}</div></div>')


def main():
    from playwright.sync_api import sync_playwright
    items = [card(c) for c in CARDS] + [card(CARDS[0], "code"), card(CARDS[0], "this")]
    out = HERE / "tex"; out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = studio.browser(p)
        pg = b.new_page(viewport={"width": CW * PX, "height": 1800})
        tmp = HERE / ".cards.html"
        tmp.write_text(studio.doc("".join(h for _, h in items), 100, CSS))
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        for ident, _ in items:
            pg.locator(f"#{ident}").screenshot(path=str(out / f"{ident}.png"))
        b.close(); tmp.unlink()
    (out / "cards.json").write_text(json.dumps(dict(w=CW, h=CH, band=BAND, rad=RAD, cards=CARDS), indent=1))
    print("printed", [i for i, _ in items])


if __name__ == "__main__":
    main()
