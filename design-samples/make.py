import sys, html
sys.path.insert(0, '/home/claude/nexulabs-social')
import render as R
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
OUT = Path(__file__).parent
F = R.FONTS
BASE = f"""
@font-face{{font-family:G;src:url({F}/Geist-Regular.woff2);font-weight:400}}
@font-face{{font-family:G;src:url({F}/Geist-Medium.woff2);font-weight:500}}
@font-face{{font-family:G;src:url({F}/Geist-SemiBold.woff2);font-weight:600}}
@font-face{{font-family:G;src:url({F}/Geist-Bold.woff2);font-weight:700}}
@font-face{{font-family:M;src:url({F}/GeistMono-Regular.woff2);font-weight:400}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
body{{font-family:G;-webkit-font-smoothing:antialiased;font-feature-settings:"tnum"}}
.logo svg{{height:34px;width:auto;display:block}}
"""
def logo(theme): return f'<div class="logo">{R.logo(theme)}</div>'

# A: Swiss print — off-white, strict grid, big type, rules, numbers as type
A = f"""<style>{BASE}
body{{background:#F3F2EE;color:#0B0B0C}}
.p{{position:absolute;inset:0;padding:80px 84px;display:flex;flex-direction:column}}
.hd{{display:flex;justify-content:space-between;align-items:center;padding-bottom:26px;border-bottom:2px solid #0B0B0C}}
.hd span{{font-size:22px;font-weight:500}}
h1{{font-size:118px;font-weight:600;letter-spacing:-.05em;line-height:.95;margin-top:70px}}
h1 em{{font-style:normal;color:#3B2BFF}}
.intro{{font-size:30px;line-height:1.35;max-width:640px;margin-top:34px;color:#3a3a3e}}
.rows{{margin-top:auto}}
.r{{display:grid;grid-template-columns:120px 260px 1fr;align-items:baseline;border-top:1.5px solid #0B0B0C;padding:26px 0 24px}}
.r .n{{font-size:26px;font-weight:500}}
.r .k{{font-size:44px;font-weight:600;letter-spacing:-.03em}}
.r .d{{font-size:27px;line-height:1.3;color:#3a3a3e}}
.r.on .k{{color:#3B2BFF}}
.ft{{display:flex;justify-content:space-between;border-top:2px solid #0B0B0C;padding-top:22px;font-size:20px;color:#55555a}}
</style><div class="p">
<div class="hd">{logo('paper')}<span>CRM / Quotes</span></div>
<h1>Sent the quote.<br>Then nothing.</h1>
<p class="intro">Four statuses that stop quotes going quiet in your sent folder.</p>
<div class="rows">
<div class="r"><span class="n">1</span><span class="k">Sent</span><span class="d">Logged on the day, with a reminder set.</span></div>
<div class="r on"><span class="n">2</span><span class="k">Chased</span><span class="d">Day three, then a week. Note every call.</span></div>
<div class="r"><span class="n">3</span><span class="k">Won</span><span class="d">Turns into a job. No retyping.</span></div>
<div class="r"><span class="n">4</span><span class="k">Lost</span><span class="d">Closed at two weeks, with the reason.</span></div>
</div>
<div class="ft"><span>nexulabs.co.uk</span><span>Websites and CRM systems</span></div>
</div>"""

# B: Real product — a believable CRM screen on a flat colour field
rows = [("Q-1048","Kitchen refit","Sent","4 Nov","Chase today","s"),
        ("Q-1046","Boiler swap","Chased","31 Oct","Call Fri","c"),
        ("Q-1045","Loft insulation","Won","29 Oct","Job booked","w"),
        ("Q-1043","Garden wall","Lost","24 Oct","Price","l"),
        ("Q-1041","Bathroom tiling","Chased","22 Oct","Close Mon","c")]
tr = "".join(f'<tr><td class="id">{a}</td><td>{b}</td><td><span class="pill {e}">{c}</span></td><td class="m">{d}</td><td class="m">{f}</td></tr>' for a,b,c,d,f,e in rows)
LOGO_B = R.logo('ink','#FFFFFF')
B = f"""<style>{BASE}
body{{background:#3B2BFF;color:#fff}}
.p{{position:absolute;inset:0;padding:80px 84px;display:flex;flex-direction:column}}
h1{{font-size:96px;font-weight:600;letter-spacing:-.045em;line-height:.98;margin-top:64px}}
.sub{{font-size:30px;line-height:1.35;margin-top:26px;opacity:.85;max-width:780px}}
.win{{margin-top:auto;background:#fff;color:#0B0B0C;border-radius:18px;overflow:hidden;box-shadow:0 30px 60px -30px rgba(0,0,0,.45)}}
.bar{{display:flex;align-items:center;justify-content:space-between;padding:22px 30px;border-bottom:1px solid #E6E6EA}}
.bar b{{font-size:26px;font-weight:600}}
.tabs{{display:flex;gap:10px;font-size:19px;color:#6b6b72}}
.tabs span{{padding:6px 14px;border-radius:8px}} .tabs .a{{background:#F1F1F4;color:#0B0B0C}}
table{{width:100%;border-collapse:collapse;font-size:25px}}
th{{text-align:left;font-weight:500;color:#8a8a92;font-size:18px;padding:18px 26px 12px;border-bottom:1px solid #EEE}}
td{{padding:25px 26px;border-bottom:1px solid #F0F0F3}}
td.id{{font-family:M;font-size:18px;color:#6b6b72}} td.m{{color:#55555c}}
.pill{{display:inline-block;padding:5px 14px;border-radius:999px;font-size:18px;font-weight:500}}
.pill.s{{background:#EEF0FF;color:#3B2BFF}} .pill.c{{background:#3B2BFF;color:#fff}}
.pill.w{{background:#E6F4EA;color:#1F7A3A}} .pill.l{{background:#F2F2F4;color:#6b6b72}}
.cap{{font-size:18px;opacity:.7;margin-top:22px}}
</style><div class="p">
<div class="logo">{LOGO_B}</div>
<h1>Sent the quote.<br>Then nothing.</h1>
<p class="sub">Give every quote a status and a reminder, so nothing sits in your sent folder.</p>
<div class="win"><div class="bar"><b>Open quotes</b><div class="tabs"><span class="a">All</span><span>Needs a chase</span><span>Won</span></div></div>
<table><tr><th>Ref</th><th>Job</th><th>Status</th><th>Sent</th><th>Next</th></tr>{tr}</table></div>
<p class="cap">Example screen. Chase on day three and after a week, close at two weeks.</p>
</div>"""

# C: Colour block — flat fields, one geometric shape, no gradients
C = f"""<style>{BASE}
body{{background:#0B0B0C;color:#fff}}
.top{{position:absolute;left:0;right:0;top:0;height:690px;background:#E9E7FF;color:#0B0B0C;padding:80px 84px;overflow:hidden}}
.disc{{position:absolute;width:420px;height:420px;border-radius:50%;background:#3B2BFF;right:-140px;top:-150px}}
.disc2{{position:absolute;width:260px;height:520px;border-radius:0 260px 260px 0;background:#0B0B0C;right:150px;top:120px;display:none}}
h1{{position:relative;font-size:112px;font-weight:600;letter-spacing:-.05em;line-height:.95;margin-top:300px;max-width:860px}}
.bot{{position:absolute;left:0;right:0;bottom:0;top:690px;padding:64px 84px 120px;display:grid;grid-template-columns:1fr 1fr;gap:56px 56px;align-content:start}}
.c .k{{font-size:46px;font-weight:600;letter-spacing:-.03em}}
.c .k i{{font-style:normal;display:inline-block;width:16px;height:16px;border-radius:50%;background:#667DFF;margin-right:14px;vertical-align:middle;position:relative;top:-4px}}
.c .d{{font-size:28px;line-height:1.35;opacity:.72;margin-top:10px}}
.url{{position:absolute;left:84px;bottom:56px;font-size:20px;opacity:.55}}
</style>
<div class="top"><div class="disc"></div>{logo('paper')}<h1>Sent the quote. Then nothing.</h1></div>
<div class="bot">
<div class="c"><div class="k"><i></i>Sent</div><div class="d">Logged on the day, with a reminder set.</div></div>
<div class="c"><div class="k"><i></i>Chased</div><div class="d">Day three, then a week. Note every call.</div></div>
<div class="c"><div class="k"><i></i>Won</div><div class="d">Turns into a job. No retyping.</div></div>
<div class="c"><div class="k"><i></i>Lost</div><div class="d">Closed at two weeks, with the reason.</div></div>
</div><div class="url">nexulabs.co.uk</div>"""

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width":1080,"height":1350}, device_scale_factor=2)
    for name, body in [("A-swiss",A),("B-product",B),("C-colour-block",C)]:
        f = OUT/f".{name}.html"; f.write_text(f"<!doctype html><meta charset=utf-8>{body}")
        pg.goto(f.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
        png = OUT/f".{name}.png"; pg.screenshot(path=str(png))
        Image.open(png).convert("RGB").resize((1080,1350), Image.LANCZOS).save(OUT/f"{name}.jpg", quality=92)
        png.unlink(); f.unlink()
    b.close()
ims=[Image.open(OUT/f"{n}.jpg") for n in ["A-swiss","B-product","C-colour-block"]]
S=Image.new("RGB",(3*1080+80,1350),"#ffffff")
for i,im in enumerate(ims): S.paste(im,(i*1120,0))
S.resize((S.width//2,S.height//2)).save(OUT/"compare.jpg",quality=90)
