#!/usr/bin/env python3
"""Instagram highlight covers for Nexulabs (Lee, 9 Nov 2026: "the highlight cover doesn't fit the circle").

Instagram shows a highlight cover as a small circle cropped from the CENTRE of a 1080x1920 frame.
Sources disagree on the exact crop (640-880px), so these covers are built to survive any of them:
  - the whole frame is the flat brand colour, so the circle is always fully filled;
  - the icon sits inside a 520px box at the exact centre (540, 960), inside even the tightest quoted crop (640px).
    On the profile Instagram actually showed the full 1080px width as the circle (checked 9 Nov 2026), so 520px reads well;
  - the highlight's name sits low in the frame, outside the circle, so it only shows when someone opens the highlight.
Outputs brand/highlight-covers/<slug>.jpg (1080x1920, for a Story / web cover picker)
    and brand/highlight-covers/<slug>-square.jpg (1080x1080, for uploading from a phone's camera roll),
    plus preview.jpg showing all of them as profile circles.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "brand" / "highlight-covers"
FONTS = (ROOT / "fonts").as_uri()
W, B = "#FFFFFF", "#667DFF"
S = 'fill="none" stroke="#fff" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"'
SB = f'fill="none" stroke="{B}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "websites": ("Websites", f'<rect x="30" y="60" width="320" height="260" rx="28" {S}/><path d="M30 130H350" {S}/><circle cx="80" cy="95" r="9" fill="{B}"/><circle cx="112" cy="95" r="9" fill="#fff"/><circle cx="144" cy="95" r="9" fill="#fff"/><path d="M80 200H220M80 250H170" {S}/><rect x="250" y="190" width="56" height="70" rx="10" fill="{B}"/>'),
    "crm": ("CRM", f'<rect x="30" y="70" width="320" height="240" rx="28" {S}/><circle cx="120" cy="160" r="38" {S}/><path d="M66 262c12-34 36-50 54-50s42 16 54 50" {S}/><path d="M220 150H300M220 200H300" {S}/><path d="M220 250H270" {SB}/>'),
    "web-crm": ("Web + CRM", f'<rect x="20" y="70" width="170" height="140" rx="22" {S}/><path d="M20 112H190" {S}/><rect x="210" y="170" width="150" height="140" rx="22" {S}/><circle cx="262" cy="222" r="20" {S}/><path d="M236 282c6-16 16-24 26-24s20 8 26 24" {S}/><path d="M105 210v40q0 30 30 30h75" {SB}/><circle cx="105" cy="210" r="0" fill="{B}"/>'),
    "branding": ("Branding", f'<path d="M190 40 300 150 230 300H150L80 150Z" {S}/><path d="M190 40v150" {S}/><circle cx="190" cy="200" r="22" fill="{B}"/><path d="M140 340H240" {SB}/>'),
    "domains": ("Domains", f'<circle cx="190" cy="190" r="150" {S}/><path d="M40 190H340" {S}/><ellipse cx="190" cy="190" rx="66" ry="150" {SB}/><path d="M66 115H314M66 265H314" {S}/>'),
    "hosting": ("Hosting", f'<rect x="40" y="40" width="300" height="90" rx="20" {S}/><rect x="40" y="150" width="300" height="90" rx="20" {S}/><rect x="40" y="260" width="300" height="90" rx="20" {S}/><circle cx="90" cy="85" r="12" fill="{B}"/><circle cx="90" cy="195" r="12" fill="{B}"/><circle cx="90" cy="305" r="12" fill="#fff"/><path d="M200 85H290M200 195H290M200 305H290" {S}/>'),
    "ai-automation": ("AI & automation", f'<path d="M318 160a130 130 0 0 0-236-60" {S}/><path d="M70 50v58h58" {S}/><path d="M62 220a130 130 0 0 0 236 60" {S}/><path d="M310 330v-58h-58" {S}/><path d="M190 130l16 44 44 16-44 16-16 44-16-44-44-16 44-16z" fill="{B}" stroke="{B}" stroke-width="8" stroke-linejoin="round"/>'),
    "tech-news": ("Tech news", f'<path d="M60 60H280V300a40 40 0 0 0 40 40H90a30 30 0 0 1-30-30Z" {S}/><path d="M280 140h50v160a40 40 0 0 1-40 40" {S}/><path d="M110 120H230" {SB}/><path d="M110 185H230M110 240H230M110 290H180" {S}/>'),
}

def page(label, svg, square=False):
    h = 1080 if square else 1920
    name = "" if square else f'<div class="nm">{label}</div><div class="lg">nexulabs<span>.</span></div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:G;src:url({FONTS}/Geist-SemiBold.woff2);font-weight:600}}
html,body{{margin:0;width:1080px;height:{h}px;background:#0B0B0C;overflow:hidden}}
.ic{{position:absolute;left:280px;top:{h//2-260}px;width:520px;height:520px}}
.nm{{position:absolute;left:0;right:0;top:1540px;text-align:center;color:#fff;font:600 72px G;letter-spacing:-.03em}}
.lg{{position:absolute;left:0;right:0;top:1650px;text-align:center;color:#fff;opacity:.6;font:600 34px G;letter-spacing:-.03em}}
.lg span{{color:{B}}}
</style></head><body><svg class="ic" viewBox="0 0 380 380" xmlns="http://www.w3.org/2000/svg">{svg}</svg>{name}</body></html>"""

def main():
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for slug, (label, svg) in ICONS.items():
            for sq in (False, True):
                pg = b.new_page(viewport={"width": 1080, "height": 1080 if sq else 1920})
                tmp = OUT / ".tmp.html"; tmp.write_text(page(label, svg, sq))
                pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(100)
                png = OUT / ".tmp.png"; pg.screenshot(path=str(png)); pg.close()
                Image.open(png).convert("RGB").save(OUT / f"{slug}{'-square' if sq else ''}.jpg", quality=95)
                png.unlink(); tmp.unlink()
        b.close()
    # preview: each cover cropped to the tightest circle quoted (640px) and shown at profile size
    n = len(ICONS); D = 160
    prev = Image.new("RGB", (n * (D + 40) + 40, D + 80), "white"); d = ImageDraw.Draw(prev)
    for i, (slug, (label, _)) in enumerate(ICONS.items()):
        im = Image.open(OUT / f"{slug}.jpg").crop((220, 640, 860, 1280)).resize((D, D))
        m = Image.new("L", (D, D), 0); ImageDraw.Draw(m).ellipse((0, 0, D, D), fill=255)
        x = 40 + i * (D + 40); prev.paste(im, (x, 20), m)
        d.ellipse((x - 4, 16, x + D + 4, 24 + D), outline="#d8d8d8", width=2)
        d.text((x + D / 2 - len(label) * 3, D + 34), label, fill="black")
    prev.save(OUT / "preview.jpg", quality=92)

if __name__ == "__main__":
    main()
