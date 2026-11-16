"""Prints the paper for this post as PNGs (Playwright):
  quote.png        an A4 quote from a made-up firm (Sprucewick Fencing) to a made-up customer, 21 x 29.7 cm at 200 px/cm.
                   It is folded into a paper dart with the top of the sheet at the tail, so only the parts of the sheet
                   that end up on top of the two wings are designed: a block either side of the centre fold.
  diary-left.png, diary-right.png   two pages of an A5 day-to-a-page diary, Wednesday 18 and Thursday 19 November 2026.
Handwriting: Caveat (OFL, @fontsource) in art/fonts. Printed type: Geist, GeistMono, Oswald, Playfair from the repo.
  python3 sheet.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
F = (ROOT / "fonts").as_uri()
A = (HERE / "fonts").as_uri()
TEAL = "#0B5A63"
INK = "#1B1C20"

FONTS = f"""
@font-face{{font-family:Hand;src:url({A}/caveat-latin-600-normal.woff2)}}
@font-face{{font-family:GM;src:url({F}/GeistMono-Medium.woff2)}}
@font-face{{font-family:G;src:url({F}/Geist-SemiBold.woff2);font-weight:600}}
@font-face{{font-family:G;src:url({F}/Geist-Medium.woff2);font-weight:500}}
@font-face{{font-family:Os;src:url({F}/oswald-latin-700-normal.woff2)}}
@font-face{{font-family:Pf;src:url({F}/playfair-display-latin-700-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
"""

# ---- the quote: 1 cm = 100 css px, so the page is 2100 x 2970 ----
QUOTE = f"""<html><head><style>{FONTS}
body{{width:2100px;height:2970px;background:#FBFAF6;position:relative;overflow:hidden;color:{INK}}}
.a{{position:absolute}}
.mark{{left:150px;top:150px;width:92px;height:92px;background:{TEAL}}}
.firm{{left:150px;top:150px;font:700 54px/1 Os;letter-spacing:.06em;text-transform:uppercase}}
.firm2{{left:150px;top:212px;font:700 54px/1 Os;letter-spacing:.06em;color:#8A8B90}}
.q{{left:144px;top:372px;font:700 172px/1 Os;letter-spacing:.015em}}
.no{{left:150px;top:592px;font:500 52px/1 GM;letter-spacing:.06em;color:#3A3B40}}
.rule{{height:5px;background:{INK}}}
.lab{{font:500 30px/1 GM;letter-spacing:.14em;color:#6A6B70}}
.val{{font:600 62px/1.08 G;letter-spacing:-.01em}}
.box{{left:1300px;top:150px;width:600px;height:520px;border:9px solid {TEAL};color:{TEAL};text-align:center}}
.box i{{display:block;font:700 86px/1 Os;letter-spacing:.07em;font-style:normal;margin-top:52px}}
.box b{{display:block;font:700 250px/.98 Os;letter-spacing:.0em;margin-top:6px}}
.box u{{display:block;font:700 96px/1 Os;letter-spacing:.2em;text-decoration:none;margin-left:.2em}}
.row{{left:150px;right:150px;height:3px;background:#C9C7C0}}
.it{{font:500 40px/1 G;color:#3A3B40}}
.pr{{font:500 40px/1 GM;color:#3A3B40}}
</style></head><body>
<div class="a firm">Sprucewick<br></div><div class="a firm2">FENCING</div>
<div class="a q">QUOTE</div>
<div class="a no">No. 0412</div>
<div class="a rule" style="left:150px;top:676px;width:456px"></div>
<div class="a box"><i>VALID FOR</i><b>30</b><u>DAYS</u></div>
<div class="a lab" style="left:300px;top:740px">FOR</div><div class="a val" style="left:300px;top:784px">Mrs J. Hall</div>
<div class="a lab" style="left:1300px;top:740px">DATE</div><div class="a val" style="left:1300px;top:784px">16 Nov 2026</div>
<div class="a lab" style="left:300px;top:910px">JOB</div><div class="a val" style="left:300px;top:954px">New fence</div>
<div class="a lab" style="left:1640px;top:910px">TOTAL</div><div class="a val" style="left:1640px;top:954px">£1,480</div>
{''.join(f'<div class="a row" style="top:{1100+i*120}px"></div>' for i in range(12))}
</body></html>"""

# ---- diary pages: A5, 14.8 x 21 cm, 1 cm = 100 css px ----
def diary(side):
    lines = "".join(f'<div class="ln" style="top:{560+i*124}px"></div>' for i in range(12))
    if side == "left":
        head = '<div class="num" style="left:120px;top:60px">18</div><div class="day" style="left:126px;top:360px;font-size:50px">Wednesday</div>'       # kept to the outer margin
        pen = ""
    else:
        head = '<div class="num" style="left:150px">19</div><div class="day" style="left:500px">Thursday<br><span>November 2026</span></div>'
        pen = ('<div class="pen" style="left:175px;top:752px;transform:rotate(-1.2deg)">Ring Mrs Hall</div>'
               '<div class="pen" style="left:180px;top:1002px;transform:rotate(-.6deg)">fence quote</div>')
    return f"""<html><head><style>{FONTS}
body{{width:1480px;height:2100px;background:#F6F1E4;position:relative;overflow:hidden;color:{INK}}}
.num{{position:absolute;top:110px;font:700 300px/1 Pf;letter-spacing:-.02em;color:{TEAL}}}
.day{{position:absolute;top:168px;font:600 76px/1.1 G;letter-spacing:-.01em}}
.day span{{display:block;margin-top:14px;font:500 44px/1 GM;letter-spacing:.04em;color:#77756C}}
.top{{position:absolute;left:{120 if side=='left' else 150}px;width:1210px;top:470px;height:6px;background:{INK}}}
.ln{{position:absolute;left:{120 if side=='left' else 150}px;width:1210px;height:3px;background:#C9C2AE;margin-top:248px}}
.pen{{position:absolute;font:600 225px/1 Hand;color:#1B2A6B;white-space:nowrap;transform-origin:left bottom}}
</style></head><body>{head}<div class="top"></div>{lines}{pen}</body></html>"""


if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, html, w, h in (("quote", QUOTE, 2100, 2970), ("diary-left", diary("left"), 1480, 2100), ("diary-right", diary("right"), 1480, 2100)):
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            tmp = HERE / f".{name}.html"; tmp.write_text(html)
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(HERE / f"{name}.png")); pg.close()
            print("wrote", name)
        b.close()
