"""The made-up brand's artwork for this Reel (Tidewrack Soap Co., an invented soap maker).
  die.png        the soap die as a height map: white is pressed in (1800x1160, 20px to the mm, bar 90x58mm)
  band-top.png   the paper band's top panel, 56x46mm
  band-side.png  the paper band's side panel, 56x12mm
  python3.13 prints.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import glob

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
F = (ROOT / "fonts").as_uri()
FONTS = f"""
@font-face{{font-family:Fraun;src:url({F}/fraunces-latin-600-normal.woff2);font-weight:600}}
@font-face{{font-family:FraunI;src:url({F}/fraunces-latin-400-italic.woff2);font-weight:400}}
@font-face{{font-family:Arch;src:url({F}/archivo-latin-700-normal.woff2);font-weight:700}}
*{{margin:0;padding:0;box-sizing:border-box}}
"""
# the mark: a tide line in a ring. Units are px at 20 to the mm.
def mark(d, stroke, colour):
    r = d / 2 - stroke / 2
    w = d * 0.50
    def wave(y):
        x0 = d / 2 - w / 2
        q = w / 4
        a = d * 0.10
        return (f"M{x0:.1f} {y:.1f} q{q/2:.1f} {-a:.1f} {q:.1f} 0 t{q:.1f} 0 t{q:.1f} 0 t{q:.1f} 0")
    ys = [d * 0.42, d * 0.62]
    paths = "".join(f'<path d="{wave(y)}" fill="none" stroke="{colour}" stroke-width="{stroke}" stroke-linecap="round"/>' for y in ys)
    return (f'<svg width="{d}" height="{d}" viewBox="0 0 {d} {d}"><circle cx="{d/2}" cy="{d/2}" r="{r}" fill="none" stroke="{colour}" stroke-width="{stroke}"/>{paths}</svg>')

DIE = f"""<style>{FONTS}
body{{width:1800px;height:1160px;background:#000;position:relative;overflow:hidden}}
.k{{position:absolute;left:190px;top:170px;width:1420px;height:820px;border:17px solid #fff;border-radius:120px}}
.m{{position:absolute;left:755px;top:214px}}
.w{{position:absolute;left:0;width:1800px;top:532px;text-align:center;font:600 166px/1 Fraun;letter-spacing:.075em;text-indent:.075em;color:#fff;-webkit-text-stroke:5px #fff}}
.s{{position:absolute;left:0;width:1800px;top:760px;text-align:center;font:700 78px/1 Arch;letter-spacing:.42em;text-indent:.42em;color:#fff;-webkit-text-stroke:3px #fff}}
</style><div class="k"></div><div class="m">{mark(290, 21, '#fff')}</div><div class="w">TIDEWRACK</div><div class="s">SOAP CO.</div>"""

INK = "#17402F"
PAPER = "#EBE2CC"
TOP = f"""<style>{FONTS}
body{{width:1120px;height:920px;background:{PAPER};position:relative;overflow:hidden;color:{INK}}}
.m{{position:absolute;left:465px;top:96px}}
.w{{position:absolute;left:0;width:1120px;top:356px;text-align:center;font:600 130px/1 Fraun;letter-spacing:.07em;text-indent:.07em}}
.s{{position:absolute;left:0;width:1120px;top:540px;text-align:center;font:700 56px/1 Arch;letter-spacing:.42em;text-indent:.42em}}
.r{{position:absolute;left:330px;width:460px;top:660px;height:5px;background:{INK}}}
.v{{position:absolute;left:0;width:1120px;top:712px;text-align:center;font:400 88px/1 FraunI;letter-spacing:.005em}}
</style><div class="m">{mark(190, 15, INK)}</div><div class="w">TIDEWRACK</div><div class="s">SOAP CO.</div><div class="r"></div><div class="v">Sea kelp &amp; mint</div>"""

SIDE = f"""<style>{FONTS}
body{{width:1120px;height:240px;background:{INK};position:relative;overflow:hidden;color:{PAPER}}}
.s{{position:absolute;left:0;width:1120px;top:84px;text-align:center;font:700 66px/1 Arch;letter-spacing:.30em;text-indent:.30em}}
</style><div class="s">TIDEWRACK SOAP CO.</div>"""

if __name__ == "__main__":
    with sync_playwright() as p:
        exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
        b = p.chromium.launch(executable_path=exe[0]) if exe else p.chromium.launch()
        for name, html, w, h in (("die", DIE, 1800, 1160), ("band-top", TOP, 1120, 920), ("band-side", SIDE, 1120, 240)):
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            tmp = HERE / f".{name}.html"; tmp.write_text("<!doctype html><meta charset=utf-8>" + html)
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300); tmp.unlink()
            pg.screenshot(path=str(HERE / f"{name}.png")); pg.close()
        b.close()
    print("ok")
