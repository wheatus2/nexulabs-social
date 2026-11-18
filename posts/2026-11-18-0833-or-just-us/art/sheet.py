"""Prints the four envelope fronts for this post as PNGs (Playwright), DL size, 22 x 11 cm, 1 cm = 100 css px at 2x.
  env-1.png  Quillby Domains      "About your domain name"      (made-up company)
  env-2.png  Northmoss Hosting    "About your web hosting"      (made-up company)
  env-3.png  Tarnbeck Mail        "About your email"            (made-up company)
  env-nx.png Nexulabs             "About your website, hosting, domain and email."
  env-mask.png  white where the window film is (for the gloss)
  python3 sheet.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
F = (ROOT / "fonts").as_uri()
INK = "#17191C"
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("#FFFFFF", "#0B0B0C").replace("#667DFF", "#0C23A8")

FONTS = f"""
@font-face{{font-family:GM;src:url({F}/GeistMono-Medium.woff2)}}
@font-face{{font-family:G;src:url({F}/Geist-Bold.woff2);font-weight:700}}
@font-face{{font-family:G;src:url({F}/Geist-Medium.woff2);font-weight:500}}
@font-face{{font-family:Os;src:url({F}/oswald-latin-700-normal.woff2)}}
@font-face{{font-family:Pf;src:url({F}/playfair-display-latin-700-normal.woff2)}}
@font-face{{font-family:Ou;src:url({F}/outfit-latin-700-normal.woff2);font-weight:700}}
@font-face{{font-family:Ou;src:url({F}/outfit-latin-500-normal.woff2);font-weight:500}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:2200px;height:1100px;position:relative;overflow:hidden;color:{INK};background:#FAF9F5}}
.a{{position:absolute}}
.head{{left:130px;top:292px;font:700 140px/1.02 G;letter-spacing:-.03em;white-space:nowrap}}
.win{{left:1300px;top:716px;width:770px;height:300px;border-radius:22px;background:#E4E2DA;box-shadow:inset 0 5px 10px rgba(0,0,0,.16),inset 0 0 0 2px rgba(0,0,0,.10)}}
.adr{{left:1356px;top:760px;font:500 46px/1.42 GM;color:#2A2C30;letter-spacing:.01em}}
.ind{{right:130px;top:112px;width:300px;height:170px;border:5px solid #8C8D90;border-radius:10px;color:#77787C;font:500 36px/1.25 GM;letter-spacing:.1em;text-align:center;padding-top:36px}}
.snd{{left:130px;top:104px;white-space:nowrap;display:flex;align-items:center;gap:26px}}
</style>"""

SENDERS = {
    "1": ('<i style="width:74px;height:74px;border-radius:50%;background:#8E1F2F;display:block"></i>'
          '<span style="font:700 84px/1 Pf;color:#8E1F2F;letter-spacing:-.01em">Quillby</span>'
          '<span style="font:500 40px/1 GM;color:#8E1F2F;letter-spacing:.2em;margin-top:22px">DOMAINS</span>',
          "About your<br>domain name"),
    "2": ('<i style="width:74px;height:74px;background:#1E2F6B;display:block"></i>'
          '<span style="font:700 76px/1 Os;color:#1E2F6B;letter-spacing:.09em">NORTHMOSS HOSTING</span>',
          "About your<br>web hosting"),
    "3": ('<i style="width:74px;height:74px;border-radius:22px 22px 22px 0;background:#1F5A3A;display:block"></i>'
          '<span style="font:700 84px/1 Ou;color:#1F5A3A;letter-spacing:-.02em">tarnbeck<b style="font-weight:500">mail</b></span>',
          "About your<br>email"),
    "nx": ('<span style="height:112px;display:block;margin-top:-14px" class="lg">' + LOGO + '</span>',
           '<span style="display:block;margin-top:34px">About your website,<br>hosting, domain<br>and email.</span>'),
}


def page(key):
    snd, head = SENDERS[key]
    return f"""<html><head><style>{FONTS}
<style>.lg svg{{height:100%;width:auto;display:block}}</style></head><body>
<div class="a snd">{snd}</div>
<div class="a head">{head}</div>
<div class="a win"></div>
<div class="a adr">The Owner<br>Your Business Ltd<br>1 Example Street</div>
</body></html>"""


MASK = """<html><body style="margin:0;width:2200px;height:1100px;background:#000;position:relative">
<div style="position:absolute;left:1300px;top:716px;width:770px;height:300px;border-radius:22px;background:#fff"></div></body></html>"""

if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch()
        jobs = [(f"env-{k}", page(k)) for k in SENDERS] + [("env-mask", MASK)]
        for name, html in jobs:
            pg = b.new_page(viewport={"width": 2200, "height": 1100}, device_scale_factor=2)
            tmp = HERE / f".{name}.html"; tmp.write_text(html)
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(HERE / f"{name}.png")); pg.close(); tmp.unlink()
            print("wrote", name)
        b.close()
