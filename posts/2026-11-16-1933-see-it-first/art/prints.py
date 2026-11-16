"""Prints the paper for this post as PNGs (Playwright):
  proof.png   a printed homepage design for a made-up joinery firm (Marrowfield Joinery), 30 x 42 cm at 120 px/cm
  tag.png     a swing tag, 6 x 12 cm at 300 px/cm, with the eyelet hole cut out in the alpha channel
  python3 prints.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
F = (ROOT / "fonts").as_uri()
BLUE, INK, SAGE, BONE, MOSS = "#0C23A8", "#1D2A24", "#DDE5D8", "#F6F3EC", "#2F4A3C"
FONTS = f"""
@font-face{{font-family:Ins;src:url({F}/instrument-serif-latin-400-normal.woff2)}}
@font-face{{font-family:Ins;src:url({F}/instrument-serif-latin-400-italic.woff2);font-style:italic}}
@font-face{{font-family:IT;src:url({F}/inter-tight-latin-800-normal.woff2);font-weight:800}}
@font-face{{font-family:IT;src:url({F}/inter-tight-latin-600-normal.woff2);font-weight:600}}
@font-face{{font-family:IT;src:url({F}/inter-tight-latin-500-normal.woff2);font-weight:500}}
*{{margin:0;padding:0;box-sizing:border-box}}
"""
# proof: 1 cm = 50 css px at 2.4x -> 1500 x 2100 css
PROOF = f"""<html><head><style>{FONTS}
body{{width:1500px;height:2100px;background:#fff;position:relative;overflow:hidden;font-family:IT;color:{INK}}}
.pg{{position:absolute;left:70px;top:70px;right:70px;bottom:70px;background:{BONE};overflow:hidden}}
.nav{{display:flex;justify-content:space-between;align-items:center;padding:44px 56px 0}}
.nav b{{font:400 44px/1 Ins;letter-spacing:-.01em}}
.nav span{{font:500 21px/1 IT;display:flex;gap:40px;align-items:center}}
.nav em{{font-style:normal;background:{MOSS};color:#fff;padding:16px 26px;border-radius:40px;font-weight:600}}
.hero{{padding:120px 56px 0}}
.hero h1{{font:400 146px/.9 Ins;letter-spacing:-.025em}}
.hero h1 i{{color:{MOSS}}}
.hero p{{font:500 30px/1.35 IT;margin-top:44px;width:640px;color:#44524a}}
.hero a{{display:inline-block;margin-top:44px;background:{INK};color:#fff;font:600 26px/1 IT;padding:26px 38px;border-radius:50px}}
.hero u{{text-decoration:none;font:500 24px/1 IT;margin-left:30px;color:#44524a}}
.pic{{position:absolute;left:56px;right:56px;top:980px;height:520px;border-radius:18px;background:{SAGE};overflow:hidden}}
.pic s{{position:absolute;top:70px;bottom:0;width:270px;background:{MOSS};border-radius:10px 10px 0 0}}
.pic s:before{{content:"";position:absolute;inset:26px 26px 60px;border:5px solid rgba(255,255,255,.22);border-radius:6px}}
.pic s:after{{content:"";position:absolute;right:22px;top:50%;width:10px;height:70px;border-radius:5px;background:#D9C9A0}}
.pic q{{position:absolute;left:0;right:0;top:40px;height:30px;background:#C9B48A}}
.row{{position:absolute;left:56px;right:56px;top:1560px;display:flex;gap:28px}}
.row div{{flex:1;border-top:3px solid {INK};padding-top:24px}}
.row h3{{font:400 50px/1 Ins}}
.row p{{font:500 21px/1.4 IT;color:#44524a;margin-top:12px}}
.cap{{position:absolute;left:70px;right:70px;bottom:44px;display:flex;justify-content:space-between;font:600 20px/1 IT;letter-spacing:.14em;text-transform:uppercase;color:#7b7f86}}
</style></head><body><div class="pg">
<div class="nav"><b>Marrowfield Joinery</b></div>
<div class="hero"><h1>Kitchens<br>made <i>by hand,</i><br>fitted by us.</h1><p>Bespoke kitchens and fitted furniture, built in our workshop and fitted in your home.</p><a>Get a quote</a><u>or call 07700 900412</u></div>
<div class="pic"><q></q><s style="left:60px"></s><s style="left:350px"></s><s style="left:640px"></s><s style="left:930px"></s></div>
<div class="row"><div><h3>Kitchens</h3><p>Designed with you, built to fit.</p></div><div><h3>Wardrobes</h3><p>Floor to ceiling, no wasted space.</p></div><div><h3>Get in touch</h3><p>Tell us about the room.</p></div></div>
</div></body></html>"""

# tag: 1 cm = 100 css px at 3x -> 600 x 1200 css. The hole is near the top.
TAG = f"""<html><head><style>{FONTS}
html,body{{background:transparent}}
body{{width:600px;height:1200px;position:relative;overflow:hidden;font-family:IT;color:#fff}}
.t{{position:absolute;inset:0;background:{BLUE};clip-path:polygon(120px 0,480px 0,600px 120px,600px 1200px,0 1200px,0 120px);
  -webkit-mask:radial-gradient(circle 34px at 300px 120px,transparent 33px,#000 34px)}}
.ring{{position:absolute;left:246px;top:66px;width:108px;height:108px;border-radius:50%;border:4px solid rgba(255,255,255,.5)}}
.a{{position:absolute;left:56px;top:300px;font:600 40px/1 IT;letter-spacing:.16em;text-transform:uppercase}}
.r{{position:absolute;left:56px;right:56px;top:372px;border-top:4px solid #fff}}
.p{{position:absolute;left:50px;top:446px;font:800 172px/1 IT;letter-spacing:-.04em}}
.b{{position:absolute;left:56px;right:50px;top:690px;font:500 45px/1.22 IT;letter-spacing:-.005em}}
.c{{position:absolute;left:56px;right:40px;bottom:70px;font:400 italic 74px/1.02 Ins;letter-spacing:-.005em}}
</style></head><body><div class="t"></div><div class="ring"></div>
<div class="a">Homepage concept</div><div class="r"></div><div class="p">Yours.</div>
<div class="b">What your new homepage could look like, before you commit to anything.</div>
<div class="c">Free when you book a call.</div></body></html>"""

if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, html, w, h, sc in (("proof", PROOF, 1500, 2100, 2.4), ("tag", TAG, 600, 1200, 3)):
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=sc)
            (HERE / ".p.html").write_text(html); pg.goto((HERE / ".p.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(HERE / f"{name}.png"), omit_background=True)
        b.close(); (HERE / ".p.html").unlink()
    print("printed")
