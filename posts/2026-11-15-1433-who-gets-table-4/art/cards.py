"""Prints the face of each black tent card (90 x 65 mm at 20 px/mm) as a PNG.
  a  TABLE 4, 19:30, Ellis, 2 - booked on the website (made-up)
  c  the phone booking once both share one diary: Patel, 20:00
  b  TABLE 4, 19:30, Patel, 2 - booked by phone (made-up)
Type: Archivo from the repo.   python3 cards.py -> art/card-a.png, art/card-b.png
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
F = (ROOT / "fonts").as_uri()
W, H = 1800, 1300
CSS = f"""
@font-face{{font-family:A;src:url({F}/archivo-latin-800-normal.woff2);font-weight:800}}
@font-face{{font-family:A;src:url({F}/archivo-latin-500-normal.woff2);font-weight:500}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#111113;position:relative;overflow:hidden;color:#F7F2E6;font-family:A}}
.k{{position:absolute;left:130px;top:140px;font-weight:500;font-size:84px;letter-spacing:.22em}}
.t{{position:absolute;left:69px;top:262px;font-weight:800;font-size:600px;line-height:1;letter-spacing:-.035em}}
.r{{position:absolute;left:130px;right:130px;top:930px;height:5px;background:#F1EBDD;opacity:.85}}
.n{{position:absolute;left:130px;top:1010px;font-weight:500;font-size:110px;letter-spacing:-.005em}}
.v{{position:absolute;right:130px;top:1010px;font-weight:500;font-size:110px;opacity:.72}}
"""
def page(name, via, tm="19:30"):
    return f"""<html><head><style>{CSS}</style></head><body>
<div class="k">TABLE 4 · RESERVED</div><div class="t" style="left:{69 if tm == '19:30' else 92}px">{tm}</div><div class="r"></div>
<div class="n">{name}, 2</div><div class="v">{via}</div></body></html>"""

if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        for k, (n, v, t) in {"a": ("Ellis", "Website", "19:30"), "b": ("Patel", "Phone", "19:30"), "c": ("Patel", "Phone", "20:00")}.items():
            tf = HERE / f".card-{k}.html"; tf.write_text(page(n, v, t))
            pg.goto(tf.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(HERE / f"card-{k}.png")); print("wrote", k)
        b.close()
