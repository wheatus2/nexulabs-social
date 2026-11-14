"""Prints the gallery label (the wall card beside the empty frame) to art/label.png with Playwright.
The card is 200 x 110 mm; the PNG is 2000 x 1100 px, so 10 px to the millimetre."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = (HERE.parents[2] / "fonts").as_uri()

HTML = f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:F;src:url({FONTS}/fraunces-latin-600-normal.woff2);font-weight:600}}
@font-face{{font-family:F;src:url({FONTS}/fraunces-latin-400-italic.woff2);font-weight:400;font-style:italic}}
@font-face{{font-family:G;src:url({FONTS}/Geist-Regular.woff2);font-weight:400}}
@font-face{{font-family:G;src:url({FONTS}/Geist-Medium.woff2);font-weight:500}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:2000px;height:1100px;background:#F2EDE4;color:#1E1418;-webkit-font-smoothing:antialiased}}
.c{{position:absolute;left:150px;top:208px;right:150px}}
h1{{font:600 230px/1 F;letter-spacing:-.012em}}
h2{{font:italic 400 160px/1.1 F;margin-top:58px;letter-spacing:-.005em}}
p{{font:500 112px/1.2 G;margin-top:73px;color:#2A1D22}}
</style><div class=c><h1>Untitled (404)</h1><h2>Page not found</h2><p>Still linked from the homepage</p></div>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 2000, "height": 1100})
    tmp = HERE / ".label.html"; tmp.write_text(HTML)
    pg.goto(tmp.as_uri()); pg.wait_for_timeout(600)
    pg.screenshot(path=str(HERE / "label.png"))
    b.close()
print("label.png")
