"""Prints for the sticky notes: eighteen yellow notes in handwriting, the one that falls, and the blue Nexulabs note.
Everything written on the notes is made up.   python3.13 print.py   -> .note-NN.png .hero.png .nx.png .contact.png
A note is 7.6 x 7.6 cm. Handwriting is a single-stroke Hershey script, smoothed and jittered.
"""
import asyncio, random
from pathlib import Path
from HersheyFonts import HersheyFonts
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "")
YELLOW, BLUE, INK = "#F6E36A", "#0C23A8", "#1B1D2A"
# (lines, hand, pen): hand = a Hershey face, pen = (colour, width at 760px)
MARKER, BIRO, PENCIL, RED = ("#1B1D2A", 11.5), ("#1F35B0", 7.0), ("#2C2C32", 7.5), ("#C0202C", 8.5)
NOTES = [
    (["quote for", "14 Elm Row", "fence"], "scripts", BIRO), (["BOILER SVC", "THURS 2PM"], "futural", MARKER),
    (["INV 212", "PAID ??"], "futural", RED), (["Hall kitchen", "tiles Fri"], "cursive", BIRO),
    (["deposit in?", "check bank"], "scripts", PENCIL), (["SAT 9AM", "MR OKOYE"], "futural", BIRO),
    (["order skip", "for Monday"], "cursive", MARKER), (["chase Tom", "re: quote"], "scripts", MARKER),
    (["07700", "900318"], "futural", MARKER), (["gate job", "measure up"], "cursive", PENCIL),
    (["new enquiry", "off website"], "scripts", BIRO), (["BOOKING", "FRI 3PM"], "futural", MARKER),
    (["van MOT", "Tuesday"], "cursive", BIRO), (["send quote", "to Priya"], "scripts", RED),
    (["LOGO PROOFS", "TO SAM"], "futural", PENCIL), (["roof quote", "9 Dene St"], "cursive", MARKER),
    (["call bank", "card reader"], "scripts", BIRO), (["MRS WEBB", "WANTS TUES"], "futural", BIRO),
]
HERO = (["RING MRS", "RIDLEY BACK", "TODAY"], "futural", MARKER)


def hand(text, x, base, size, seed, slope=-0.04, jit=1.0, face="scripts"):
    f = HersheyFonts(); f.load_default_font(face); f.normalize_rendering(size)
    rng = random.Random(seed)
    paths = []
    for st in f.strokes_for_text(text):
        pts = [(x + px + rng.uniform(-jit, jit), base - py + px * slope + rng.uniform(-jit, jit)) for px, py in st]
        if len(pts) < 2:
            continue
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        P = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        paths.append(d)
    return paths


def width(text, size, face="scripts"):
    f = HersheyFonts(); f.load_default_font(face); f.normalize_rendering(size)
    xs = [px for st in f.strokes_for_text(text) for px, _ in st]
    return max(xs) - min(xs) if xs else 0


def note(spec, S, seed, hero=False):
    """S = px across the note."""
    lines, face, (ink, pw) = spec
    k = S / 760
    rng = random.Random(seed)
    size = (118 if hero else rng.uniform(84, 112)) * k * (0.80 if face == "futural" else 1.0)
    while max(width(l, size, face) for l in lines) > S * 0.76:
        size *= 0.96
    lh = size * (1.55 if face == "futural" else 1.72) * rng.uniform(0.96, 1.08)
    top = (S - lh * len(lines)) / 2 + S * rng.uniform(-0.03, 0.05)
    x0 = S * 0.12 + rng.uniform(0, S * 0.05)
    slope = rng.uniform(-0.09, 0.015)
    paths = []
    for i, l in enumerate(lines):
        paths += hand(l, x0 + rng.uniform(-10, 14) * k, top + lh * (i + 0.8), size, seed * 7 + i, slope=slope, jit=(1.6 if face == "futural" else 1.1) * k, face=face)
    extra = ""
    if hero:
        w = width(lines[-1], size, face); y = top + lh * (len(lines) - 0.2) + 26 * k + (w * slope)
        extra = (f'<g stroke="{MARKER[0]}" stroke-width="{12 * k:.1f}"><path d="M{x0 - 8 * k:.0f},{y + 16 * k:.0f} q{w / 2:.0f},{-16 * k:.0f} {w + 30 * k:.0f},{w * slope - 4 * k:.0f}"/>'
                 f'<path d="M{x0 + 6 * k:.0f},{y + 50 * k:.0f} q{w / 2:.0f},{-10 * k:.0f} {w + 10 * k:.0f},{w * slope + 2 * k:.0f}"/></g>')
    sw = pw * k * (1.12 if hero else 1.0)
    bg = YELLOW if seed % 3 else "#F3E784"
    body = "".join(f'<path d="{d}"/>' for d in paths) + extra
    return f'''<html><body style="margin:0"><div style="position:relative;width:{S}px;height:{S}px;background:{bg};overflow:hidden">
<svg width="{S}" height="{S}" style="position:absolute;left:0;top:0"><g fill="none" stroke="{ink}" stroke-width="{sw:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity=".93">{body}</g></svg></div></body></html>'''


def nx(S):
    fonts = (ROOT / "fonts").as_uri()
    k = S / 1520
    return f'''<html><body style="margin:0"><style>
@font-face{{font-family:G;src:url({fonts}/Geist-Medium.woff2)}}
.s{{position:relative;width:{S}px;height:{S}px;background:{BLUE};overflow:hidden}}
.g{{position:absolute;left:{190 * k}px;top:{560 * k}px;width:{1140 * k}px}} .g svg{{width:100%;height:auto;display:block}}
svg.l{{position:absolute;left:{190 * k}px;top:{830 * k}px}}
</style><div class="s"><div class="g">{LOGO.replace('fill="#667DFF"', 'fill="#FFFFFF"')}</div>
<svg class="l" width="{1140 * k}" height="{160 * k}"><text x="{6 * k}" y="{120 * k}" textLength="{1118 * k}" lengthAdjust="spacing" font-family="G" font-weight="500" font-size="{118 * k}" fill="#fff">Custom CRM systems</text></svg></div></body></html>'''


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        async def shot(html, name, S):
            pg = await b.new_page(viewport={"width": S, "height": S})
            (HERE / ".print.html").write_text(html); await pg.goto((HERE / ".print.html").as_uri()); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(HERE / name)); await pg.close()
        for i, lines in enumerate(NOTES):
            await shot(note(lines, 760, 31 + i), f".note-{i:02d}.png", 760)
        await shot(note(HERO, 1520, 5, hero=True), ".hero.png", 1520)
        await shot(nx(1520), ".nx.png", 1520)
        await shot(f'<html><body style="margin:0;background:{YELLOW}"></body></html>', ".note-blank.png", 760)
        await b.close()
    (HERE / ".print.html").unlink()
    from PIL import Image
    names = [f".note-{i:02d}.png" for i in range(len(NOTES))] + [".hero.png", ".nx.png"]
    sheet = Image.new("RGB", (8 * 390, 2 * 390), "#555")
    for i, n in enumerate(names):
        sheet.paste(Image.open(HERE / n).convert("RGB").resize((380, 380)), (5 + (i % 8) * 390, 5 + (i // 8) * 390))
    sheet.save(HERE / ".contact.png")

asyncio.run(main())
