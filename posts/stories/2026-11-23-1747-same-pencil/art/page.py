"""What the pencil has written on the paper.   python3.13 page.py   -> .page-1.png .page-2.png .page-3.png, one for each frame (transparent, P px to the centimetre)
The page is the patch of table from (X0, Y0) to (X0 + PW, Y0 + PH) cm in build.py. Frame 1, by the red end: "new enquiry". Frame 2, by the blue end: quoted, booked, done, each ticked. Frame 3, behind the join: "enquiry" in red and a blue tick, one line.
Handwriting is a single-stroke Hershey script, smoothed and jittered. Everything written is made up."""
import asyncio, random
from pathlib import Path
from HersheyFonts import HersheyFonts
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
P = 150
X0, Y0, PW, PH = -5.0, -1.0, 28.0, 9.0
RED, BLUE = "#B80F1A", "#16309E"
# (text, x cm, baseline y cm, size cm, colour)
PAGES = {
    1: ([("enquiry", 1.6, 1.75, 2.1, RED)], []),
    2: ([("quoted", 13.9, 4.7, 0.9, BLUE), ("booked", 14.1, 3.1, 0.9, BLUE), ("done", 14.3, 1.5, 0.9, BLUE)], [(16.9, 4.7), (17.1, 3.1), (17.3, 1.5)]),
    3: ([], []),
}


def hand(text, x, base, size, seed, slope=-0.03, jit=1.0, face="scripts"):
    f = HersheyFonts(); f.load_default_font(face); f.normalize_rendering(size)
    rng = random.Random(seed)
    paths = []
    for st in f.strokes_for_text(text):
        pts = [(x + px + rng.uniform(-jit, jit), base - py + px * slope + rng.uniform(-jit, jit)) for px, py in st]
        if len(pts) < 2:
            continue
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        Q = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(Q) - 2):
            p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        paths.append(d)
    return paths


def html(n):
    LINES, TICKS = PAGES[n]
    w, h = round(PW * P), round(PH * P)
    px = lambda x: (x - X0) * P
    py = lambda y: h - (y - Y0) * P
    out = ""
    for i, (t, x, y, s, c) in enumerate(LINES):
        ds = hand(t, px(x), py(y), s * P, 11 + i, jit=1.2)
        out += f'<g stroke="{c}" stroke-width="{0.115 * P:.1f}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>"
    for i, (x, y) in enumerate(TICKS):
        a, b = px(x), py(y)
        k = P * 0.72
        out += f'<path stroke="{BLUE}" stroke-width="{0.125 * P:.1f}" d="M{a:.0f},{b - .42 * k:.0f} q{.2 * k:.0f},{.12 * k:.0f} {.34 * k:.0f},{.42 * k:.0f} q{.5 * k:.0f},{-.75 * k:.0f} {1.25 * k:.0f},{-1.15 * k:.0f}"/>'
    if n == 99:
        out += f'<path stroke="{RED}" stroke-width="{0.125 * P:.1f}" d="M{px(0.9):.0f},{py(0.72):.0f} q{2.4 * P:.0f},{-0.22 * P:.0f} {5.0 * P:.0f},{-0.05 * P:.0f}"/>'
    return w, h, f"""<body style="margin:0;background:transparent"><svg width="{w}" height="{h}"><defs>
    <filter id="g" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/>
    <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  5 0 0 0 -0.2"/><feComposite in="SourceGraphic" operator="in"/></filter></defs>
    <g fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#g)">{out}</g></svg></body>"""


async def main():
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch()
        except Exception:
            b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        for n in PAGES:
            w, h, doc = html(n)
            pg = await b.new_page(viewport={"width": w, "height": h})
            tmp = HERE / ".tmp.html"; tmp.write_text("<!doctype html><meta charset=utf-8>" + doc)
            await pg.goto(f"file://{tmp}"); await pg.wait_for_timeout(300); tmp.unlink()
            await pg.screenshot(path=str(HERE / f".page-{n}.png"), omit_background=True); await pg.close()
            print("wrote page", n, w, h)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
