"""Prints the card for this post as PNGs (Playwright):
  front.png   the front of a made-up "Christmas opening hours" door calendar, 35.5 x 26 cm at 150 px/cm:
              eight doors, 24 to 31 December 2026, four to a row. Pine green, cream print.
  perf.png    the same sheet as a height map: the perforation round each door (for a bump in the render)
  in-24.png, in-25.png, in-26.png   what is printed behind three of the doors, 7 x 7 cm at 300 px/cm
  python3 prints.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
F = (ROOT / "fonts").as_uri()
PINE, CREAM, RED = "#123F30", "#F3E9D2", "#A3182B"
DAYS = ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]   # 24 Dec 2026 is a Thursday

FONTS = f"""
@font-face{{font-family:Fr;src:url({F}/fraunces-latin-600-normal.woff2);font-weight:600}}
@font-face{{font-family:Fr;src:url({F}/fraunces-latin-400-normal.woff2);font-weight:400}}
@font-face{{font-family:Fr;src:url({F}/fraunces-latin-400-italic.woff2);font-weight:400;font-style:italic}}
@font-face{{font-family:G;src:url({F}/Geist-SemiBold.woff2);font-weight:600}}
*{{margin:0;padding:0;box-sizing:border-box}}
"""
# 1 cm = 100 css px, shot at 1.5x. Sheet 3550 x 2600. Header 750 at the top, then 2 rows of 700 doors with 150 gaps.


def doors(perf):
    out = []
    for i in range(8):
        c, r = i % 4, i // 4
        x, y = 150 + c * 850, 150 + r * 850
        if perf:
            out.append(f'<div class="pf" style="left:{x}px;top:{y}px"></div>')
        else:
            out.append(f'<div class="d{" hero" if i == 1 else ""}" style="left:{x}px;top:{y}px"><i>{DAYS[i]}</i><b>{24 + i}</b></div>')
    return "".join(out)


FRONT = f"""<html><head><style>{FONTS}
body{{width:3550px;height:2000px;background:{PINE};position:relative;overflow:hidden;color:{CREAM}}}
.hd{{position:absolute;left:150px;top:150px;right:150px;height:600px;display:flex;align-items:flex-end;justify-content:space-between;padding-bottom:110px}}
.hd h1{{font:400 italic 230px/1 Fr;letter-spacing:-.01em;white-space:nowrap}}
.hd span{{font:600 62px/1 G;letter-spacing:.2em;text-transform:uppercase;padding-bottom:26px;white-space:nowrap}}
.d{{position:absolute;width:700px;height:700px;border:5px dashed rgba(243,233,210,.55);border-radius:10px}}
.d i{{position:absolute;left:52px;top:50px;font:600 50px/1 G;letter-spacing:.2em;text-transform:uppercase;font-style:normal;opacity:.82}}
.d b{{position:absolute;left:44px;bottom:6px;font:600 470px/1 Fr;letter-spacing:-.035em;font-feature-settings:"lnum"}}
.d.hero{{background:{CREAM};color:{RED};border-color:rgba(163,24,43,.5)}}
</style></head><body>{doors(False)}</body></html>"""

PERF = f"""<html><head><style>*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:3550px;height:2000px;background:#fff;position:relative;overflow:hidden}}
.pf{{position:absolute;width:700px;height:700px;border:9px dashed #000;border-radius:10px;filter:blur(2px)}}
</style></head><body>{doors(True)}</body></html>"""


def inside(day, big, small, colour):
    return f"""<html><head><style>{FONTS}
body{{width:700px;height:700px;background:{CREAM};position:relative;overflow:hidden;color:{PINE}}}
.a{{position:absolute;left:56px;top:74px;font:600 50px/1 G;letter-spacing:.2em;text-transform:uppercase}}
.b{{position:absolute;left:50px;top:236px;font:600 {178 if len(big) < 8 else 150}px/1.02 Fr;letter-spacing:-.03em;color:{colour}}}
.c{{position:absolute;left:56px;bottom:84px;font:400 italic 60px/1 Fr}}
.r{{position:absolute;left:56px;right:56px;top:166px;border-top:4px solid {PINE}}}
</style></head><body><div class="a">{day}</div><div class="r"></div><div class="b">{big}</div><div class="c">{small}</div></body></html>"""


if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 3550, "height": 2000}, device_scale_factor=1.5)
        for name, html in (("front", FRONT), ("perf", PERF)):
            (HERE / ".p.html").write_text(html); pg.goto((HERE / ".p.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(HERE / f"{name}.png"))
        pg = b.new_page(viewport={"width": 700, "height": 700}, device_scale_factor=3)
        for n, args in ((24, ("Thu 24 Dec", "Open<br>to 1pm", "Christmas Eve", PINE)),
                        (25, ("Fri 25 Dec", "Closed", "Christmas Day", RED)),
                        (26, ("Sat 26 Dec", "Closed", "Boxing Day", RED))):
            (HERE / ".p.html").write_text(inside(*args)); pg.goto((HERE / ".p.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(HERE / f"in-{n}.png"))
        b.close(); (HERE / ".p.html").unlink()
    print("printed")
