"""The print for the blueprint: a homepage drawn as a plan, white line on blue, with a title block.
Nothing on it is a real client's: it is "your business".   python3.13 print.py -> .plan.png (3000 x 10000, 100px a cm)
The sheet is 30 x 100 cm; the drawing ends at 79 cm, the rest stays inside the roll.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "").replace('fill="#667DFF"', 'fill="#FFFFFF"')
BLUE, LINE = "#1C4A9C", "#F4F7FF"
C = 100  # px per cm
W, H = 30 * C, 100 * C


def html():
    fonts = (ROOT / "fonts").as_uri()
    s = []
    A = s.append
    def line(x1, y1, x2, y2, w=0.07, o=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        A(f'<line x1="{x1*C:.1f}" y1="{y1*C:.1f}" x2="{x2*C:.1f}" y2="{y2*C:.1f}" stroke-width="{w*C:.1f}" opacity="{o}"{d}/>')
    def rect(x, y, w, h, sw=0.07, r=0, fill="none", o=1):
        A(f'<rect x="{x*C:.1f}" y="{y*C:.1f}" width="{w*C:.1f}" height="{h*C:.1f}" rx="{r*C:.1f}" stroke-width="{sw*C:.1f}" fill="{fill}" opacity="{o}"/>')
    def text(x, y, t, cap, anchor="start", fill=LINE, fam="M", weight=500, ls=0.08, extra=""):
        fs = cap / 0.71 * C
        A(f'<text x="{x*C:.1f}" y="{y*C:.1f}" font-family="{fam}" font-weight="{weight}" font-size="{fs:.1f}" letter-spacing="{ls}em" text-anchor="{anchor}" fill="{fill}" stroke="none" {extra}>{t}</text>')
    def arrow(x, y, dx, dy, a=0.55):
        # a filled drafting arrowhead at (x,y) pointing along (dx,dy)
        px, py = -dy, dx
        A(f'<path d="M{x*C:.1f},{y*C:.1f} L{(x-dx*a+px*a*.22)*C:.1f},{(y-dy*a+py*a*.22)*C:.1f} L{(x-dx*a-px*a*.22)*C:.1f},{(y-dy*a-py*a*.22)*C:.1f}Z" fill="{LINE}" stroke="none"/>')
    def cross(x, y, w, h):
        line(x, y, x + w, y + h, 0.035, .8); line(x + w, y, x, y + h, 0.035, .8)

    # grid
    for i in range(1, 12):
        line(i * 2.5, 1.0, i * 2.5, 79.0, 0.02, .16)
    for j in range(1, 32):
        line(1.0, 1.0 + j * 2.5, 29.0, 1.0 + j * 2.5, 0.02, .16)
    # sheet border
    rect(1.0, 1.0, 28.0, 78.0, 0.12)
    # width dimension over the page
    line(5, 3.6, 25, 3.6, 0.035); arrow(5, 3.6, -1, 0); arrow(25, 3.6, 1, 0)
    line(5, 2.9, 5, 5.4, 0.03); line(25, 2.9, 25, 5.4, 0.03)
    A(f'<rect x="{11.4*C}" y="{3.0*C}" width="{7.2*C}" height="{1.2*C}" fill="{BLUE}" stroke="none"/>')
    text(15, 3.92, "HOMEPAGE", 0.62, "middle", ls=0.22)
    # height dimension of the first screen, left
    line(3.3, 6, 3.3, 37.6, 0.035); arrow(3.3, 6, 0, -1); arrow(3.3, 37.6, 0, 1)
    line(2.6, 6, 4.6, 6, 0.03); line(2.6, 37.6, 4.6, 37.6, 0.03)
    A(f'<rect x="{2.7*C}" y="{17.0*C}" width="{1.2*C}" height="{9.6*C}" fill="{BLUE}" stroke="none"/>')
    text(0, 0, "FIRST SCREEN", 0.62, "middle", ls=0.22, extra=f'transform="translate({3.61*C:.0f},{21.8*C:.0f}) rotate(-90)"')
    # the page
    rect(5, 6, 20, 57, 0.10)
    # nav
    line(5, 9.2, 25, 9.2, 0.05)
    A(f'<circle cx="{6.9*C}" cy="{7.6*C}" r="{0.62*C}" stroke-width="{0.06*C}" fill="none"/>')
    line(7.9, 7.6, 10.6, 7.6, 0.16)
    for x in (14.2, 16.4, 18.6):
        line(x, 7.6, x + 1.5, 7.6, 0.07)
    rect(21.0, 6.85, 3.0, 1.5, 0.06, r=0.75)
    # hero: outlined lettering on construction lines
    for y in (11.3, 13.6, 15.2, 17.5):
        line(5.6, y, 24.4, y, 0.018, .55, dash="14 10")
    hs = 2.3 / 0.71 * C
    for y, t in ((13.6, "Your"), (17.5, "headline.")):
        A(f'<text x="{6.5*C}" y="{y*C}" font-family="G" font-weight="700" font-size="{hs:.0f}" letter-spacing="0.035em" fill="none" stroke="{LINE}" stroke-width="{0.05*C}">{t}</text>')
    line(6.5, 19.5, 19.5, 19.5, 0.09, .9); line(6.5, 20.5, 16.0, 20.5, 0.09, .9)
    # button, the one solid thing on the drawing
    rect(6.5, 22.2, 9.6, 2.5, 0.06, r=1.25, fill=LINE)
    text(11.3, 23.87, "BOOK A CALL", 0.74, "middle", fill=BLUE, weight=500, ls=0.14)
    # photo
    rect(6.5, 26.6, 17, 9.6, 0.06); cross(6.5, 26.6, 17, 9.6)
    A(f'<rect x="{12.6*C}" y="{30.6*C}" width="{4.8*C}" height="{1.6*C}" fill="{BLUE}" stroke="none"/>')
    text(15, 31.78, "PHOTO", 0.72, "middle", ls=0.22)
    line(5, 37.6, 25, 37.6, 0.03, .8, dash="30 18")
    # services
    text(6.5, 40.6, "WHAT YOU DO", 0.72, ls=0.2)
    for i in range(3):
        x = 6.5 + i * 5.85
        rect(x, 41.8, 5.3, 6.6, 0.06, r=0.3)
        A(f'<circle cx="{(x+1.35)*C:.0f}" cy="{43.3*C:.0f}" r="{0.7*C:.0f}" stroke-width="{0.06*C}" fill="none"/>')
        line(x + 0.7, 45.3, x + 4.3, 45.3, 0.09); line(x + 0.7, 46.3, x + 3.5, 46.3, 0.06, .8); line(x + 0.7, 47.1, x + 3.9, 47.1, 0.06, .8)
    # enquiry form
    text(6.5, 52.0, "ENQUIRY FORM", 0.72, ls=0.2)
    rect(6.5, 53.1, 8.2, 2.0, 0.06, r=0.2); rect(15.3, 53.1, 8.2, 2.0, 0.06, r=0.2)
    text(7.1, 54.36, "NAME", 0.5, ls=0.18); text(15.9, 54.36, "PHONE", 0.5, ls=0.18)
    rect(6.5, 55.7, 17, 3.3, 0.06, r=0.2); text(7.1, 56.96, "MESSAGE", 0.5, ls=0.18)
    rect(6.5, 59.6, 5.6, 2.0, 0.06, r=1.0, fill=LINE); text(9.3, 60.87, "SEND", 0.62, "middle", fill=BLUE, ls=0.2)
    # balloons on leaders, right
    for y, t in ((16.0, "A"), (45.1, "B"), (57.3, "C")):
        line(25, y, 26.3, y, 0.035)
        A(f'<circle cx="{27.3*C}" cy="{y*C}" r="{1.0*C}" stroke-width="{0.06*C}" fill="none"/>')
        text(27.33, y + 0.36, t, 0.72, "middle", ls=0)
    # title block: the offer, who it is drawn for, and the maker's name across the full width
    T0, T1 = 66.0, 79.0
    line(1.0, T0, 29.0, T0, 0.12)
    line(1.0, 69.6, 29.0, 69.6, 0.05)
    text(2.3, 68.33, "FREE HOMEPAGE CONCEPT", 0.86, ls=0.14, weight=500)
    line(21.9, T0, 21.9, 69.6, 0.05)
    text(22.7, 67.2, "DRAWN FOR", 0.36, ls=0.2); text(22.7, 68.75, "YOU", 0.78, ls=0.14)
    lw = 23.4 * C; lh = lw * 722 / 4021
    logo = f'<div style="position:absolute;left:{2.3*C - lw*0.0}px;top:{(69.6 + (T1 - 69.6) / 2) * C - lh * 0.5 - 20:.0f}px;width:{lw}px">{LOGO}</div>'
    body = "".join(s)
    return f'''<html><body style="margin:0"><style>
@font-face{{font-family:G;font-weight:700;src:url({fonts}/Geist-Bold.woff2)}}
@font-face{{font-family:M;font-weight:500;src:url({fonts}/GeistMono-Medium.woff2)}}
.s{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:{BLUE}}}
.s:before{{content:"";position:absolute;inset:0;background:radial-gradient(120% 60% at 50% 40%,rgba(8,24,70,.20),rgba(255,255,255,.05) 100%)}}
svg.d{{position:absolute;left:0;top:0;filter:blur(1.1px)}} div svg{{width:100%;height:auto;display:block}}
</style><div class="s"><svg class="d" width="{W}" height="{H}" fill="none" stroke="{LINE}" stroke-linecap="butt">{body}</svg>{logo}</div></body></html>'''


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        (HERE / ".print.html").write_text(html()); await pg.goto((HERE / ".print.html").as_uri()); await pg.wait_for_timeout(500)
        await pg.screenshot(path=str(HERE / ".plan.png")); await b.close()
    (HERE / ".print.html").unlink()
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(HERE / ".plan.png").convert("RGB")
    im.crop((0, 0, W, 8000)).resize((750, 2000)).save(HERE / ".plan-small.jpg", quality=88)

asyncio.run(main())
