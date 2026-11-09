"""LinkedIn company page banner for Nexulabs: 1128x191 (rendered at 2x = 2256x382).

LinkedIn overlays the page logo bottom-left and crops the sides on mobile,
so the message sits centre-right and the left third is decoration only.
Run: python3 brand/linkedin_banner.py  ->  brand/linkedin-banner.png
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
FONTS = (ROOT / "fonts").as_uri()
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text()
OUT = ROOT / "brand" / "linkedin-banner.png"

# contour-line pattern (soft topographic rings), drawn as SVG
rings = "".join(
    f'<ellipse cx="300" cy="230" rx="{60 + i * 42}" ry="{34 + i * 26}" />' for i in range(14)
)
rings2 = "".join(
    f'<ellipse cx="1060" cy="-20" rx="{40 + i * 36}" ry="{24 + i * 22}" />' for i in range(10)
)

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Disp;src:url({FONTS}/Geist-SemiBold.woff2);font-weight:600}}
@font-face{{font-family:Disp;src:url({FONTS}/Geist-Medium.woff2);font-weight:500}}
@font-face{{font-family:Mono;src:url({FONTS}/GeistMono-Medium.woff2);font-weight:500}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1128px;height:191px;overflow:hidden;background:#0A0A2E}}
.wrap{{position:relative;width:1128px;height:191px;overflow:hidden;background:#0A0A2E}}
.blob{{position:absolute;border-radius:50%;filter:blur(46px)}}
.b1{{width:520px;height:300px;left:-120px;top:20px;background:#0C23A8;opacity:.95}}
.b2{{width:360px;height:220px;left:230px;top:-120px;background:#00D1FF;opacity:.55}}
.b3{{width:420px;height:260px;left:880px;top:40px;background:#A78BFA;opacity:.55}}
.b4{{width:300px;height:200px;left:640px;top:120px;background:#0C23A8;opacity:.5}}
.fade{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,10,46,0) 0%,rgba(10,10,46,.55) 42%,rgba(10,10,46,.78) 62%,rgba(10,10,46,.35) 100%)}}
svg.pat{{position:absolute;inset:0}}
svg.pat ellipse{{fill:none;stroke:#fff;stroke-width:.8;opacity:.16}}
.dots{{position:absolute;right:0;top:0;width:330px;height:191px;
  background-image:radial-gradient(rgba(255,255,255,.28) 1.1px,transparent 1.3px);background-size:14px 14px;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 70%);mask-image:linear-gradient(90deg,transparent,#000 70%)}}
.copy{{position:absolute;left:392px;top:0;height:191px;display:flex;flex-direction:column;justify-content:center;gap:12px}}
h1{{font-family:Disp;font-weight:600;font-size:38px;line-height:1.02;letter-spacing:-1.2px;color:#fff}}
h1 em{{font-style:normal;background:linear-gradient(90deg,#00D1FF,#A78BFA);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{font-family:Mono;font-weight:500;font-size:11.5px;letter-spacing:1.6px;text-transform:uppercase;color:rgba(255,255,255,.78);display:flex;gap:10px;align-items:center}}
.sub i{{display:inline-block;width:4px;height:4px;border-radius:50%;background:#00D1FF}}
.mark{{position:absolute;right:36px;bottom:24px;width:120px;opacity:.95}}
.mark svg{{width:120px;height:auto;display:block}}
</style></head><body><div class="wrap">
<div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="blob b4"></div>
<svg class="pat" viewBox="0 0 1128 191" preserveAspectRatio="none">{rings}{rings2}</svg>
<div class="fade"></div><div class="dots"></div>
<div class="copy">
  <h1>Websites and <em>CRM systems</em><br>built around your business</h1>
  <div class="sub">Businesses of every kind <i></i> North East England <i></i> nexulabs.co.uk</div>
</div>
<div class="mark">{LOGO}</div>
</div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 1128, "height": 191}, device_scale_factor=2)
    tmp = ROOT / "brand" / ".banner.html"
    tmp.write_text(HTML)
    pg.goto(tmp.as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT), type="png")
    b.close()
print(OUT)
