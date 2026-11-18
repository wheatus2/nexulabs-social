"""Prints for the Reel: the made-up website shown on the phone's screen (screen.png) and the three pink
flags with a marker numeral on each (flag-1.png ...). Ashgarth Kitchens is invented.
  python3.13 print.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import studio

SCREEN = """
<style>
html,body{background:#fff}
.s{position:relative;width:393px;height:852px;background:#FBFAF7;overflow:hidden;font-family:Geist;color:#222}
.st{position:absolute;left:0;right:0;top:0;height:54px;background:#fff}
.st b{position:absolute;left:34px;top:19px;font:600 16px Geist;letter-spacing:-.01em;color:#000}
.isl{position:absolute;left:50%;top:12px;width:118px;height:34px;border-radius:20px;background:#000;transform:translateX(-50%)}
.st svg{position:absolute;right:30px;top:20px}
.hd{position:absolute;left:0;right:0;top:54px;height:62px;background:#fff;border-bottom:1px solid #D9D6CF}
.hd .n{position:absolute;left:20px;top:14px;font:700 15px/1.1 Playfair;letter-spacing:.09em;color:#1F2B4D}
.hd .n small{display:block;font:500 8.5px Geist;letter-spacing:.32em;color:#8A8578;margin-top:4px}
.hd i{position:absolute;right:22px;top:21px;width:24px;height:2px;background:#1F2B4D;box-shadow:0 8px #1F2B4D,0 16px #1F2B4D}
.hero{position:absolute;left:0;right:0;top:117px;height:236px;background:#1F2B4D;
  background-image:linear-gradient(135deg,rgba(255,255,255,.07) 0 50%,transparent 50%)}
.hero h1{position:absolute;left:28px;right:60px;top:60px;font:500 38px/1.08 Playfair;color:#fff;letter-spacing:-.005em}
.hero u{position:absolute;left:30px;top:164px;width:54px;height:3px;background:#C9B27A}
.p{position:absolute;left:28px;right:92px;top:378px;font:400 10.5px/1.55 Geist;color:#8E8B84}
.p b{display:block;font:700 15px Playfair;color:#1F2B4D;margin-bottom:8px;letter-spacing:.01em}
.btn{position:absolute;left:28px;right:92px;top:636px;text-align:center;font:600 13px Geist;color:#fff;background:#9A9588;padding:13px 22px;border-radius:3px;letter-spacing:.02em}
.ft{position:absolute;left:0;right:0;top:716px;bottom:0;background:#fff;border-top:1px solid #D9D6CF}
.ft b{position:absolute;left:28px;top:26px;font:700 15px Playfair;color:#1F2B4D}
.g{position:absolute;left:28px;top:60px;display:flex;gap:10px}
.g i{width:106px;height:92px;background:#E4E0D6;display:block}
.g i:nth-child(2){background:#D5D9E2}.g i:nth-child(3){background:#DDD4C4}
.bar{position:absolute;left:50%;bottom:9px;width:140px;height:5px;border-radius:3px;background:#111;transform:translateX(-50%)}
</style>
<div class="s">
 <div class="st"><b>9:41</b><div class="isl"></div>
  <svg width="68" height="14" viewBox="0 0 68 14"><g fill="#000"><rect x="0" y="9" width="3" height="4" rx="1"/><rect x="5" y="6" width="3" height="7" rx="1"/><rect x="10" y="3" width="3" height="10" rx="1"/><rect x="15" y="0" width="3" height="13" rx="1"/>
  <path d="M24 5.2a9 9 0 0 1 14 0l-1.6 1.6a6.8 6.8 0 0 0-10.8 0zM27 8.3a5 5 0 0 1 8 0l-1.7 1.7a2.8 2.8 0 0 0-4.6 0zM31 13l-1.8-2a2.4 2.4 0 0 1 3.6 0z"/>
  <rect x="44" y="1" width="21" height="12" rx="3.5" fill="none" stroke="#000" stroke-opacity=".4"/><rect x="45.6" y="2.6" width="17.8" height="8.8" rx="2.2"/><rect x="66" y="5" width="1.6" height="4" rx=".8" fill-opacity=".45"/></g></svg></div>
 <div class="hd"><div class="n">ASHGARTH<small>KITCHENS · DURHAM</small></div><i></i></div>
 <div class="hero"><h1>Welcome to our<br>website</h1><u></u></div>
 <div class="p"><b>About us</b>Ashgarth Kitchens is a family run business which has been supplying and fitting kitchens for many years. We pride ourselves on offering a wide range of kitchens to suit all tastes and budgets, and we are committed to providing a high standard of service to all of our customers at all times. Please feel free to browse our website, where you will find further information about all of the products and services that we are able to offer, and do not hesitate to get in touch if you have any questions at all.</div>
 <div class="btn">Read more</div>
 <div class="ft"><b>Our kitchens</b><div class="g"><i></i><i></i><i></i></div></div>
 <div class="bar"></div>
</div>
"""

# marker numerals as single strokes (x right, y down, in a 100 x 140 box), drawn with a round nib
NUM = {1: "M40 38 L57 20 L57 124", 2: "M26 44 C28 8 80 8 76 46 C74 70 40 92 24 122 L80 122",
       3: "M26 28 C50 4 86 22 70 50 C62 64 48 66 44 66 C92 66 90 132 24 116"}
FLAG = """
<style>html,body{background:#FF2E7E}
.f{position:relative;width:1640px;height:480px;background:#FF2E7E;overflow:hidden}
svg{position:absolute;left:%dpx;top:60px}
</style>
<div class="f"><svg width="257" height="360" viewBox="0 0 100 140"><path d="%s" fill="none" stroke="#17141A" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
"""

with sync_playwright() as p:
    b = studio.browser(p)
    pg = b.new_page(viewport={"width": 393, "height": 852}, device_scale_factor=6)
    t = HERE / ".tmp.html"
    t.write_text(studio.doc(SCREEN, 852)); pg.goto(t.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.locator(".s").screenshot(path=str(HERE / "screen.png"))
    pg2 = b.new_page(viewport={"width": 1640, "height": 480}, device_scale_factor=1)
    for n, d in NUM.items():
        # the flag is 41 mm long (40 px a mm); the numeral starts 9 mm from the point
        t.write_text(studio.doc(FLAG % (270, d), 480)); pg2.goto(t.as_uri()); pg2.wait_for_timeout(100)
        pg2.locator(".f").screenshot(path=str(HERE / f"flag-{n}.png"))
    t.unlink(); b.close()
print("ok")
