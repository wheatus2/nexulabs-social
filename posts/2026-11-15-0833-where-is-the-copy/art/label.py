"""Prints the paper label for the disk (70 x 54 mm at 30 px/mm) as a PNG, in two states:
  blank  NAME filled in by hand ("Website"), DATE left empty
  done   the same label, later: DATE filled in and a red tick beside it
Handwriting: Permanent Marker (OFL, from @fontsource), in art/fonts. Printed type: Geist / GeistMono from the repo.
  python3 label.py   -> art/label-blank.png, art/label-done.png
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
F = (ROOT / "fonts").as_uri()
A = (HERE / "fonts").as_uri()
W, H = 2100, 1620

CSS = f"""
@font-face{{font-family:Marker;src:url({A}/permanent-marker-latin-400-normal.woff2)}}
@font-face{{font-family:GM;src:url({F}/GeistMono-Medium.woff2)}}
@font-face{{font-family:G;src:url({F}/Geist-SemiBold.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#F4F1EA;position:relative;overflow:hidden}}
.band{{position:absolute;left:0;right:0;top:0;height:250px;background:#C8202E}}
.band p{{position:absolute;left:120px;top:84px;font:500 74px/1 GM;letter-spacing:.14em;color:#F7EDEA}}
.band b{{position:absolute;right:120px;top:70px;font:600 96px/1 G;letter-spacing:.02em;color:#F7EDEA}}
.row{{position:absolute;left:120px;right:120px;height:3px;background:#2A2B30}}
.lab{{position:absolute;left:120px;font:500 58px/1 GM;letter-spacing:.16em;color:#4A4B52}}
.pen{{position:absolute;font:400 300px/1 Marker;color:#17181C;transform-origin:left bottom}}
.tick{{position:absolute}}
"""


def page(state):
    date = ""
    if state == "done":
        date = ('<div class="pen" style="left:700px;top:880px;font-size:210px;transform:rotate(-1.6deg)">15/11/26</div>'
                '<svg class="tick" style="left:1530px;top:790px" width="380" height="330" viewBox="0 0 380 330">'
                '<path d="M30 190 C70 215 110 250 140 292 C190 190 260 90 350 26" fill="none" stroke="#C8202E" '
                'stroke-width="38" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    return f"""<html><head><style>{CSS}</style></head><body>
<div class="band"><p>MF2HD</p><b>1.44 MB</b></div>
<div class="lab" style="top:400px">NAME</div>
<div class="pen" style="left:760px;top:430px;transform:rotate(-2.2deg)">Website</div>
<div class="row" style="top:770px"></div>
<div class="lab" style="top:860px">DATE</div>
{date}
<div class="row" style="top:1150px"></div>
<div class="lab" style="top:1240px">NOTES</div>
<div class="row" style="top:1500px"></div>
</body></html>"""


if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        for st in ("blank", "done"):
            tmp = HERE / f".label-{st}.html"; tmp.write_text(page(st))
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(HERE / f"label-{st}.png"))
            print("wrote", st)
        b.close()
