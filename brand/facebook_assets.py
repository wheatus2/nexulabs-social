#!/usr/bin/env python3
"""Render the Nexulabs Facebook/Instagram profile picture and Facebook cover photo."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = Path(__file__).resolve().parent
FONTS = (HERE.parent / "fonts").as_uri()
LOGO = (HERE / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "")
FAV = (HERE / "favicon.svg").read_text().replace("<title>nexulabs</title>", "")

BASE = f"""
@font-face{{font-family:G;src:url({FONTS}/Geist-Regular.woff2);font-weight:400}}
@font-face{{font-family:G;src:url({FONTS}/Geist-Medium.woff2);font-weight:500}}
@font-face{{font-family:GM;src:url({FONTS}/GeistMono-Regular.woff2);font-weight:400}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0B0B0C;color:#F5F5F7;font-family:G;-webkit-font-smoothing:antialiased;overflow:hidden}}
.grid{{position:absolute;inset:0;opacity:.07;background-image:linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px);
 background-size:82px 82px;-webkit-mask-image:radial-gradient(ellipse at 50% 50%,#000 0%,transparent 70%)}}
.glow{{position:absolute;border-radius:50%;background:radial-gradient(circle,#667DFF55 0%,#3B2BFF22 38%,transparent 68%)}}
.grain{{position:absolute;inset:0;opacity:.08;mix-blend-mode:overlay;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
"""

# Facebook cover: 1640x624 (2x of 820x312 desktop). Mobile shows the centre ~1110 px, so keep content centred.
COVER = f"""<style>{BASE}
.c{{position:relative;width:1640px;height:624px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.logo svg{{height:92px;width:auto;display:block}}
.tag{{margin-top:34px;font-size:40px;font-weight:500;letter-spacing:-.025em;color:#F5F5F7}}
.sub{{margin-top:22px;font-family:GM;font-size:22px;letter-spacing:.14em;text-transform:uppercase;color:#8E8E96}}
.sub b{{color:#667DFF;font-weight:400}}
</style><div class="c"><div class="glow" style="width:1300px;height:1300px;left:170px;top:-340px"></div><div class="grid"></div>
<div class="logo" style="position:relative">{LOGO}</div>
<div class="tag" style="position:relative">Websites and CRM systems for all types of businesses</div>
<div class="sub" style="position:relative">Websites <b>·</b> CRM systems <b>·</b> Hosting <b>·</b> Branding</div>
<div class="grain"></div></div>"""

# Profile picture: the site's favicon mark, full-bleed square (Facebook crops to a circle).
PROFILE = f"""<style>{BASE}
.p{{position:relative;width:1080px;height:1080px;background:#0B0B0C;display:flex;align-items:center;justify-content:center}}
.p svg{{width:1080px;height:1080px}}
.p svg rect{{rx:0}}
</style><div class="p">{FAV.replace('rx="237.6"', 'rx="0"')}</div>"""


def shot(html, w, h, out):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        tmp = HERE / ".tmp.html"
        tmp.write_text("<!doctype html><meta charset=utf-8>" + html)
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
        pg.screenshot(path=str(HERE / ".tmp.png")); b.close(); tmp.unlink()
    Image.open(HERE / ".tmp.png").convert("RGB").resize((w, h), Image.LANCZOS).save(out, "PNG", optimize=True)
    (HERE / ".tmp.png").unlink()
    print(out)


if __name__ == "__main__":
    shot(COVER, 1640, 624, HERE / "facebook-cover.png")
    shot(PROFILE, 1080, 1080, HERE / "profile-picture.png")
