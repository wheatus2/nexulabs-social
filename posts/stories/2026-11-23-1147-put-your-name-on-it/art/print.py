"""Prints for the label tapes.   python3.13 print.py   -> .name-c.png .name-h.png .hello-c.png .hello-h.png .nx.png .contact.png
Embossed tape: a colour map (gloss black, the pressed letters stressed white) and a height map (the letters raised).
Printed tape: white, with the real Nexulabs wordmark and one line. The web and email addresses are placeholders, not real ones.
P px to the centimetre. The long black ribbon and the white ribbon are as long as the tails and rolls in build.py."""
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = 240
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "").replace("#FFFFFF", "#0B0B0C")
FONT = f"@font-face{{font-family:M;src:url(file://{ROOT}/fonts/GeistMono-Medium.woff2)}}@font-face{{font-family:G;src:url(file://{ROOT}/fonts/Geist-SemiBold.woff2)}}"
CAP, PITCH = 0.50, 0.50          # cm
FS = CAP * P / 0.70              # Geist Mono cap height is about 0.70 em
LS = PITCH * P - 0.60 * FS


def emboss(text, length, width, start, kind):
    """kind c: colour, h: height. `start` cm from the left end to the first letter."""
    w, h = round(length * P), round(width * P)
    if kind == "h":
        bg, fg, blur = "#000", "#fff", 2.6
    else:
        bg, fg, blur = "#0A0A0C", "#F4F2EC", 1.1
    return w, h, f"""<style>{FONT}*{{margin:0;padding:0}}body{{width:{w}px;height:{h}px;background:{bg};overflow:hidden;position:relative}}
    .t{{position:absolute;left:{start * P:.1f}px;top:0;height:{h}px;line-height:{h}px;font:500 {FS:.1f}px/{h}px M;letter-spacing:{LS:.1f}px;color:{fg};white-space:pre;filter:blur({blur}px);
    -webkit-text-stroke:{2.0 if kind == 'h' else 1.2}px {fg}}}</style><div class=t>{text}</div>"""


def printed(length, width, start, period):
    w, h = round(length * P), round(width * P)
    lh = 1.12 * P                                   # wordmark height
    lw = lh * 4021 / 722
    unit = f"""<div class=u><div class=l>{LOGO}</div></div>"""
    n = int(length / period) + 2
    return w, h, f"""<style>{FONT}*{{margin:0;padding:0}}body{{width:{w}px;height:{h}px;background:#DCDAD4;overflow:hidden;position:relative}}
    .r{{position:absolute;left:{start * P:.1f}px;top:0;height:{h}px;display:flex}}
    .u{{width:{period * P:.1f}px;height:{h}px;display:flex;align-items:center;flex:none}}
    .l svg{{display:block;width:{lw:.1f}px;height:{lh:.1f}px}} .l{{margin-top:{-0.04 * P:.1f}px}}
    .s{{font:600 {0.64 * P:.1f}px/1 G;color:#0B0B0C;margin-left:{0.75 * P:.1f}px;letter-spacing:-.01em;white-space:nowrap}}</style><div class=r>{unit * n}</div>"""


JOBS = None


def jobs(L):
    return [(".name-c.png", emboss("YOURNAME.CO.UK", L["name"], 1.2, 0.62, "c")), (".name-h.png", emboss("YOURNAME.CO.UK", L["name"], 1.2, 0.62, "h")),
            (".hello-c.png", emboss("HELLO@YOURNAME.CO.UK", L["hello"], 1.2, 0.62, "c")), (".hello-h.png", emboss("HELLO@YOURNAME.CO.UK", L["hello"], 1.2, 0.62, "h")),
            (".nx.png", printed(L["nx"], 1.9, 0.75, L["period"]))]


async def main(L):
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch()
        except Exception:
            b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        for name, (w, h, html) in jobs(L):
            pg = await b.new_page(viewport={"width": w, "height": h})
            tmp = HERE / ".tmp.html"; tmp.write_text("<!doctype html><meta charset=utf-8>" + html)
            await pg.goto(f"file://{tmp}"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300); tmp.unlink()
            await pg.screenshot(path=str(HERE / name)); await pg.close()
            print("wrote", name, w, h)
        await b.close()


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    import geom
    asyncio.run(main(geom.LENGTHS))
