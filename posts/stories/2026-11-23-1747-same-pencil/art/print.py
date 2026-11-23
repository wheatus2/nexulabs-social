"""Foil stamp for the pencil.   python3.13 print.py   -> .stamp.png (white on black: a mask)
One flat of the pencil, 17.5 x 0.40 cm, P px to the centimetre: WEBSITE towards the red end, CRM towards the blue end,
and the real Nexulabs wordmark across the join in the middle."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = 400
LEN, FLAT = 17.5, 0.40
WEB_X, CRM_X = 3.05, 12.75     # cm from the red tip to the start of each word (see build.py probe)
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "")
FONT = f"@font-face{{font-family:M;src:url(file://{ROOT}/fonts/GeistMono-Medium.woff2)}}"
CAP = 0.205
FS = CAP * P / 0.70
LH = 0.30 * P
LW = LH * 4021 / 722


def html():
    w, h = round(LEN * P), round(FLAT * P)
    t = f"position:absolute;top:0;height:{h}px;font:500 {FS:.1f}px/{h}px M;letter-spacing:.16em;color:#fff;white-space:pre;-webkit-text-stroke:1.5px #fff"
    return w, h, f"""<style>{FONT}*{{margin:0;padding:0}}body{{width:{w}px;height:{h}px;background:#000;overflow:hidden;position:relative}}
    .l{{position:absolute;left:{(LEN / 2) * P - LW / 2:.1f}px;top:{(h - LH) / 2 - 0.012 * P:.1f}px}} .l svg{{display:block;width:{LW:.1f}px;height:{LH:.1f}px}}</style>
    <div style="{t};left:{WEB_X * P:.0f}px">WEBSITE</div><div style="{t};left:{CRM_X * P:.0f}px">CRM</div><div class=l>{LOGO}</div>"""


async def main():
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch()
        except Exception:
            b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        w, h, doc = html()
        pg = await b.new_page(viewport={"width": w, "height": h})
        tmp = HERE / ".tmp.html"; tmp.write_text("<!doctype html><meta charset=utf-8>" + doc)
        await pg.goto(f"file://{tmp}"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300); tmp.unlink()
        await pg.screenshot(path=str(HERE / ".stamp.png")); await pg.close(); await b.close()
        print("wrote .stamp.png", w, h)

if __name__ == "__main__":
    asyncio.run(main())
