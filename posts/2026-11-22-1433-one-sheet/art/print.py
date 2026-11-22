"""Draws the print for the concertina leaflet (run with python3.13, before build.py).

One sheet, seven pages, each 9 x 15 cm: a big numeral, one red line that runs through every fold with a
ring on each page, and the page's name. Page 7 carries the Nexulabs wordmark (the real SVG).
Writes .sheet.png (200 px to the centimetre). The leaflet is made up.
"""
import io, re
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAGES = ["Website", "Enquiries", "Quotes", "Bookings", "Jobs", "Hosting", None]
RED = "#D0202B"
INK = "#141416"
PAPER = "#FBFAF6"
W, H = 900, 1500              # CSS px per page (100 px to the cm), shot at 2x
LINE_Y, LINE_T = 985, 44
NODE_X, NODE_D, NODE_S = 160, 184, 46


def css():
    f = (ROOT / "fonts").as_uri()
    return "".join(f"@font-face{{font-family:IT;src:url({f}/inter-tight-latin-{w}-normal.woff2);font-weight:{w}}}" for w in (600, 700, 800))


def page(i, name):
    logo = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace('fill="#FFFFFF"', f'fill="{INK}"').replace('fill="#667DFF"', f'fill="{RED}"')
    logo = re.sub(r'width="[\d.]+" height="[\d.]+"', 'height="136"', logo, count=1)
    x0 = NODE_X if i == 0 else 0
    x1 = NODE_X if name is None else W
    ring = (f'<div style="position:absolute;left:{NODE_X - NODE_D / 2}px;top:{LINE_Y - NODE_D / 2}px;width:{NODE_D}px;height:{NODE_D}px;border-radius:50%;box-sizing:border-box;'
            + (f'background:{RED}' if name is None else f'background:{PAPER};border:{NODE_S}px solid {RED}') + '"></div>')
    body = f'''<div style="position:absolute;left:{x0}px;top:{LINE_Y - LINE_T / 2}px;width:{x1 - x0}px;height:{LINE_T}px;background:{RED}"></div>{ring}'''
    if name:
        body += f'<div style="position:absolute;left:58px;top:20px;font:800 600px/1 IT;letter-spacing:-.04em;color:{INK}">{i + 1}</div>'
        body += f'<div style="position:absolute;left:66px;top:1190px;font:700 152px/1 IT;letter-spacing:-.025em;color:{INK};white-space:nowrap">{name}</div>'
    else:
        body += f'<div style="position:absolute;left:66px;top:96px">{logo}</div>'
        body += f'<div style="position:absolute;left:62px;top:292px;font:800 121px/1.04 IT;letter-spacing:-.03em;color:{INK};white-space:nowrap">Websites and<br>CRM systems.</div>'
        body += f'<div style="position:absolute;left:66px;top:1190px;font:700 108px/1 IT;letter-spacing:-.02em;color:{INK};white-space:nowrap;margin-top:34px">nexulabs.co.uk</div>'
    return f'<style>{css()}*{{margin:0}}body{{width:{W}px;height:{H}px;background:{PAPER};position:relative;overflow:hidden}}</style>{body}'


if __name__ == "__main__":
    sheet = Image.new("RGB", (W * 2 * len(PAGES), H * 2), PAPER)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=next(str(x) for x in Path("/opt/pw-browsers").glob("chromium*/chrome-linux*/chrome")))
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        for i, name in enumerate(PAGES):
            (HERE / ".page.html").write_text(page(i, name)); pg.goto((HERE / ".page.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
            sheet.paste(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"), (i * W * 2, 0))
        b.close()
    sheet.save(HERE / ".sheet.png")
    sheet.resize((W * len(PAGES) // 3, H // 3)).save(HERE / ".sheet-small.jpg", quality=88)
    print("wrote .sheet.png", sheet.size)
