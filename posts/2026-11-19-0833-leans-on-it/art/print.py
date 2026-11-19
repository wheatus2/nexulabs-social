"""The writing on the whiteboard, as textures (40px per cm of a 150 x 100cm board, 6000 x 4000).
Marker capitals are a single-stroke Hershey face, slanted, wobbled and smoothed, drawn with a round nib.
  python3.13 print.py  ->  .board-1.png (the week), .board-2.png (the same, leant on), .board-3.png (wiped, tea rota)
                           .rough-N.png (ink is matt, the board is glossy)
Everything on the board is made up.
"""
import asyncio, random, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from HersheyFonts import HersheyFonts
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
S = 40
W, H = 150 * S, 100 * S
BLACK, RED = "#18181B", "#D3202B"
X0, NAMEW, DAYW = 2.0, 18.0, 25.6          # cm
TOP, HEADH, ROWH = 3.0, 11.5, 27.5
DAYS = ["MON", "TUE", "WED", "THU", "FRI"]
NAMES = ["KEV", "SAL", "DAZ"]
JOBS = {
    ("KEV", "MON"): ["BOILER", "SERVICE", "MRS HALL"], ("KEV", "TUE"): ["NEW COMBI", "TINDALE", "ALL DAY"],
    ("KEV", "WED"): ["GAS SAFETY", "3 FLATS"], ("KEV", "THU"): ["RAD SWAP", "ELLIS", "10AM"],
    ("KEV", "FRI"): ["2ND FIX", "OKAFOR"],
    ("SAL", "MON"): ["QUOTE", "NOWAK 2PM"], ("SAL", "TUE"): ["FLUSH", "BAINS"],
    ("SAL", "WED"): ["HOLIDAY"], ("SAL", "THU"): ["TANK OUT", "CARR 8AM"], ("SAL", "FRI"): ["SERVICE", "LYLE 9AM"],
    ("DAZ", "MON"): ["CYLINDER", "IQBAL"], ("DAZ", "TUE"): ["LEAK", "ROBSON", "ASAP"],
    ("DAZ", "WED"): ["SNAGS", "AKHTAR"], ("DAZ", "THU"): ["BATHROOM", "1ST FIX", "COULSON"],
    ("DAZ", "FRI"): ["VAN MOT"],
}
RED_JOB = ("KEV", "TUE")
INSET = 2.7


def smooth(pts):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


_F = {}


def glyph(ch, size):
    if size not in _F:
        f = HersheyFonts(); f.load_default_font("futural"); f.normalize_rendering(size); _F[size] = f
    st = [list(x) for x in _F[size].strokes_for_text(ch)]
    if not st:
        return [], 0.0
    mn = min(p[0] for x in st for p in x); mx = max(p[0] for x in st for p in x)
    return [[(px - mn, py) for px, py in x] for x in st], mx - mn


def hand(text, x, base, size, seed, slant=0.10, maxw=None):
    """Marker capitals, a letter at a time: no two the same. x, base and size in px. Returns (paths, width)."""
    rng = random.Random(seed)
    gap = size * 0.21
    raw = sum((glyph(c, size)[1] + gap) if c != " " else size * 0.42 for c in text) - gap
    sq = 0.86 * (min(1.0, maxw / (0.86 * raw)) if maxw else 1.0)
    drift = rng.uniform(-0.03, 0.012); ph = rng.uniform(0, 6.28)
    out = []; cx = 0.0
    for c in text:
        if c == " ":
            cx += size * 0.42 * sq * rng.uniform(0.85, 1.2); continue
        st, w = glyph(c, size)
        sx = sq * rng.uniform(0.90, 1.10); sy = rng.uniform(0.93, 1.07)
        rot = math.radians(rng.uniform(-3.2, 3.2)); sl = slant + rng.uniform(-0.05, 0.05)
        by = size * rng.uniform(-0.035, 0.035) + size * 0.03 * math.sin(cx / (size * 2.0) + ph) + cx * drift
        j = size * 0.02
        for stroke in st:
            ox, oy = rng.uniform(-j, j), rng.uniform(-j, j)
            pts = []
            for px, py in stroke:
                gx = px * sx + sl * py * sy; gy = py * sy
                rx = gx * math.cos(rot) - (gy - size / 2) * math.sin(rot); ry = gx * math.sin(rot) + (gy - size / 2) * math.cos(rot) + size / 2
                pts.append((x + cx + rx + ox + rng.uniform(-j, j) * 0.6, base - ry + by + oy + rng.uniform(-j, j) * 0.6))
            if len(pts) >= 2:
                out.append(smooth(pts))
        cx += (w * sx + gap * sq * rng.uniform(0.8, 1.25))
    return out, cx


def ruled(x1, y1, x2, y2, seed):
    rng = random.Random(seed); n = 9
    pts = [(x1 + (x2 - x1) * i / n + rng.uniform(-3, 3), y1 + (y2 - y1) * i / n + rng.uniform(-3, 3)) for i in range(n + 1)]
    return smooth(pts)


def cm(v):
    return v * S


def week():
    black, red, lines = [], [], []
    right = X0 + NAMEW + 5 * DAYW; bottom = TOP + HEADH + 3 * ROWH
    k = 0
    for i in range(6):
        x = X0 + NAMEW + i * DAYW if i < 5 else right
        lines.append(ruled(cm(x), cm(TOP - 0.6), cm(x) + 4, cm(bottom + 0.4), 100 + i))
    for r in range(4):
        y = TOP + HEADH + r * ROWH
        lines.append(ruled(cm(X0 - 0.4), cm(y), cm(right + 0.5), cm(y) + 5, 200 + r))
    for i, d in enumerate(DAYS):
        p, w = hand(d, 0, 0, 190, 300 + i)
        p, _ = hand(d, cm(X0 + NAMEW + i * DAYW + DAYW / 2) - w / 2 - 12, cm(TOP + HEADH - 3.2), 190, 300 + i)
        black += p
    thin = []
    p, _ = hand("W/C", cm(X0 + 2.2), cm(TOP + 4.3), 100, 390); thin += p
    p, _ = hand("16 NOV", cm(X0 + 2.2), cm(TOP + HEADH - 2.6), 100, 391, maxw=cm(NAMEW - 5)); thin += p
    for r, n in enumerate(NAMES):
        p, _ = hand(n, cm(X0 + 2.2), cm(TOP + HEADH + r * ROWH + 9.0), 190, 400 + r, maxw=cm(NAMEW - 5.4)); black += p
        for i, d in enumerate(DAYS):
            rows = JOBS[(n, d)]
            for li, t in enumerate(rows):
                k += 1
                xx = cm(X0 + NAMEW + i * DAYW + INSET); yy = cm(TOP + HEADH + r * ROWH + 7.4 + li * 6.6)
                p, w = hand(t, xx, yy, 124, 500 + k, maxw=cm(DAYW - 2 * INSET - 0.4)); black += p
                if (n, d) == RED_JOB and li == 0:
                    red.append(ruled(xx - 10, yy + 62, xx + w + 40, yy + 50, 900))
                    red.append(ruled(xx + 6, yy + 92, xx + w + 22, yy + 84, 901))
            if rows == ["HOLIDAY"]:
                black.append(ruled(xx - 6, yy + 110, xx + cm(DAYW - 4.5), yy + 96, 950))
    return black, red, lines, thin


def rota():
    """Tea rota, bottom left of the wiped board (the tray is under it)."""
    black, red = [], []
    x = cm(9.0); y = cm(52.0)
    p, w = hand("TEA ROTA", x, y, 300, 71); red += p
    red.append(ruled(x - 10, y + 104, x + w + 70, y + 84, 72))
    who = ["KEV", "SAL", "DAZ", "KEV", "SAL"]
    for i, d in enumerate(DAYS):
        yy = y + cm(10.6) + i * cm(6.9)
        p, _ = hand(d, x + 14, yy, 172, 80 + i); black += p
        p, w = hand(who[i], x + cm(15.5), yy, 172, 90 + i); black += p
        if i < 3:   # a tick
            tx = x + cm(15.5) + w + cm(3.2)
            rng = random.Random(60 + i)
            red.append(smooth([(tx, yy - 80 + rng.uniform(-8, 8)), (tx + 44, yy - 14), (tx + 76, yy - 96), (tx + 150 + rng.uniform(-10, 10), yy - 226)]))
    return black, red


def svg(groups):
    g = "".join(f'<g fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">' + "".join(f'<path d="{d}"/>' for d in ps) + "</g>"
                for c, sw, ps in groups)
    return f'<html><body style="margin:0;background:transparent"><svg width="{W}" height="{H}" style="display:block">{g}</svg></body></html>'


async def shoot(pages):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        for name, html in pages.items():
            (HERE / ".print.html").write_text(html); await pg.goto((HERE / ".print.html").as_uri()); await pg.wait_for_timeout(400)
            await pg.screenshot(path=str(HERE / f".{name}.png"), omit_background=True)
        await b.close()


def noise(shape, cell, seed, blur=0):
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, shape[0] // cell[0]), max(2, shape[1] // cell[1]))).astype(np.float32)
    im = Image.fromarray(small, mode="F").resize((shape[1], shape[0]), Image.BICUBIC)
    return np.clip(np.asarray(im), 0, 1)


def load(name):
    a = np.asarray(Image.open(HERE / f".{name}.png").convert("RGBA")).astype(np.float32) / 255
    return a[..., :3] * a[..., 3:], a[..., 3]          # premultiplied colour, alpha


def marker(pm, al, seed):
    """Marker ink is never even: a little thinner in streaks along the stroke."""
    n = 0.80 + 0.20 * noise(al.shape, (9, 30), seed) * (0.6 + 0.4 * noise(al.shape, (60, 60), seed + 1))
    n = np.clip(n + 0.06, 0, 1)
    return pm * n[..., None], al * n


def lean(pm, al):
    """Somebody's shoulder goes along the board from Monday towards Thursday, sinking as it goes.
    Dry-wipe ink does not blur: it comes off, and what comes off is pushed along in threads and left further on."""
    hh, ww = al.shape
    x_in = int(cm(X0 + NAMEW + 9.5)); x_out = int(cm(X0 + NAMEW + 3 * DAYW + 6.0))
    xs1 = np.arange(ww, dtype=np.float32)
    u = np.clip((xs1 - x_in) / (x_out - x_in), -0.2, 1.3)
    yc = cm(TOP + HEADH + 13.5) + cm(11.5) * np.clip(u, 0, None) ** 1.5 + cm(1.3) * np.sin(u * 7.0)           # the path of the shoulder
    half = cm(9.5) * (0.82 + 0.25 * np.sin(u * 3.1 + 0.4))                                    # how much of it is touching
    sh = np.round(yc - hh / 2).astype(int)
    def straighten(a, back=False):
        out = np.empty_like(a)
        for x in range(ww):
            out[:, x] = np.roll(a[:, x], sh[x] if back else -sh[x], axis=0)
        return out
    A = straighten(al); C = straighten(pm)
    t = (np.arange(hh, dtype=np.float32) - hh / 2)[:, None]
    edge = 55 * (noise((hh, ww), (700, 220), 5) - 0.5)
    press = np.clip((half[None, :] - np.abs(t + edge)) / cm(3.2), 0, 1) ** 0.8                 # heavy in the middle, light at the edges
    wob_in = 150 * (noise((hh, 1), (90, 1), 6) - 0.5)
    onset = np.clip((xs1[None, :] - (x_in + wob_in)) / 70, 0, 1)
    wob_out = 900 * (noise((hh, 1), (140, 1), 7) - 0.5)
    lift_off = np.clip((x_out + wob_out - xs1[None, :]) / 900, 0, 1)
    patch = 0.55 + 0.45 * noise((hh, ww), (260, 420), 15)                                     # it bounces: some patches are missed
    m = press * onset * np.clip(lift_off * 2.2, 0, 1) * patch
    rng = np.random.default_rng(8)
    rowsn = rng.random(hh).astype(np.float32)
    rowsn = np.convolve(rowsn, np.array([0.1, 0.2, 0.4, 0.2, 0.1], np.float32), mode="same")
    rowsn = ((rowsn - rowsn.min()) / (rowsn.max() - rowsn.min()))[:, None]
    coarse = noise((hh, 1), (34, 1), 9)
    keep = np.clip(0.04 + 0.7 * np.clip(rowsn * 1.5 - 1.0, 0, 1) + 0.6 * np.clip(coarse - 0.70, 0, 1) * 2, 0, 1)
    lift = np.clip(m * 1.25, 0, 1) * (1 - keep)
    tA = A * lift; tC = C * lift[..., None]
    rA = A - tA; rC = C - tC
    xa, xb = x_in - 220, min(ww, x_out + 900)
    dA = np.zeros_like(A); dC = np.zeros_like(C)
    accA = np.zeros(hh, np.float32); accC = np.zeros((hh, 3), np.float32)
    carry = (0.9982 - 0.0016 * rng.random(hh)).astype(np.float32)
    lay = (0.0035 + 0.004 * rng.random(hh)).astype(np.float32)                                # how fast a thread lets go of what it carries
    for x in range(xa, xb):
        live = np.clip(m[:, x] * 1.5, 0, 1)
        accA = accA + tA[:, x]; accC = accC + tC[:, x]
        put = accA * lay * live; putC = accC * (lay * live)[:, None]
        dA[:, x] = put * 11; dC[:, x] = putC * 11
        accA = (accA - put) * carry; accC = (accC - putC) * carry[:, None]
    thread = (0.25 + 1.3 * rowsn ** 1.5) * (0.5 + 1.0 * noise((hh, ww), (3, 1100), 12))
    dA = np.clip(dA * thread, 0, 0.5); dC = dC * thread[..., None]
    dC = np.minimum(dC, dA[..., None])
    a2 = rA + dA * (1 - rA); c2 = rC + dC * (1 - rA)[..., None]
    return straighten(c2, True), straighten(a2, True), straighten(lift, True)


def board(pm, al, haze_seed, ghost=None, haze=0.024):
    hh, ww = al.shape
    white = np.array([0.905, 0.91, 0.905], np.float32)
    hz = noise((hh, ww), (700, 900), haze_seed) * 0.8 + noise((hh, ww), (160, 1200), haze_seed + 1) * 0.2
    base = white[None, None, :] * (1 - haze * hz)[..., None]
    if ghost is not None:
        g = np.asarray(Image.fromarray((ghost * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32) / 255
        base = base * (1 - 0.075 * g * (0.4 + 0.6 * noise((hh, ww), (300, 300), 31)))[..., None]
    rgb = base * (1 - al)[..., None] + pm
    rough = 0.16 + 0.42 * al + 0.10 * hz * haze / 0.024
    return rgb, rough


def save(n, rgb, rough):
    Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB").save(HERE / f".board-{n}.png")
    Image.fromarray((np.clip(rough, 0, 1) * 255 + 0.5).astype(np.uint8), "L").save(HERE / f".rough-{n}.png")


def main():
    b, r, l, th = week(); rb, rr = rota()
    half = len(b) // 2
    asyncio.run(shoot({"grid": svg([(BLACK, 11, l)]), "week": svg([(BLACK, 13, th), (BLACK, 16, b[::2]), (BLACK, 18.5, b[1::2]), (RED, 17, r)]),
                       "rota": svg([(BLACK, 19, rb), (RED, 21, rr)])}))
    pm, al = marker(*load("week"), 21)
    gpm, gal = marker(*load("grid"), 22)
    over = lambda c, a, c2, a2: (c + c2 * (1 - a)[..., None], a + a2 * (1 - a))
    full = over(pm, al, gpm, gal)
    save(1, *board(*full, 40))
    lc, la, lift = lean(pm, al)
    thin = 1 - 0.62 * lift                               # the ruled lines are thinned where it passed, not carried off
    save(2, *board(*over(lc, la, gpm * thin[..., None], gal * thin), 40))
    al = full[1]
    rpm, ral = marker(*load("rota"), 23)
    # the corner the rota is written in was wiped properly first: no ghost under it
    hh, ww = al.shape
    ys = np.arange(hh, dtype=np.float32)[:, None]; xs = np.arange(ww, dtype=np.float32)[None, :]
    clear = np.clip((xs - cm(50)) / cm(9), 0, 1) + np.clip((cm(36) - ys) / cm(7), 0, 1)
    save(3, *board(rpm, ral, 44, ghost=None, haze=0.035))
    for n in (1, 2, 3):
        Image.open(HERE / f".board-{n}.png").resize((1500, 1000), Image.LANCZOS).save(HERE / f".board-{n}-small.jpg", quality=90)
    Image.open(HERE / ".board-2.png").crop((int(cm(0)), int(cm(8)), int(cm(124)), int(cm(70)))).resize((2480, 1240), Image.LANCZOS).crop((0,0,2480,1240)).save(HERE / ".board-2-crop.jpg", quality=90)

main()
