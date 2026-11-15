"""Prints the two fortune slips (art/tex/slip-guess.png, slip-check.png).
A fortune-cookie slip: thin white paper, one line printed in ultramarine, a hairline rule at each end.
Fonts are the repo's woff2 files converted to TTF with fontTools."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "tex"; OUT.mkdir(exist_ok=True)
TTF = Path("/tmp/claude-0/ttf")
W, H = 3000, 520          # slip 66mm x 11.4mm
INK = (26, 36, 150)
LINES = {"guess": "Yes, we’re open on Sundays.", "check": "I’ll check with the team."}

rng = np.random.default_rng(3)
fibre = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
fib = Image.fromarray(((fibre * 6) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
for key, line in LINES.items():
    f = ImageFont.truetype(str(TTF / "newsreader-latin-400-italic.ttf"), 230)
    txt = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(txt)
    d.text((W / 2, H / 2 + 6), line, font=f, fill=255, anchor="mm")
    # a little ink spread, uneven
    txt = txt.filter(ImageFilter.GaussianBlur(0.9))
    a = np.asarray(txt, np.float32) / 255
    a *= 0.93 + 0.07 * (np.asarray(fib, np.float32) - 128) / 12
    a = a.clip(0, 1)
    base = np.ones((H, W, 3), np.float32) * np.array([246, 244, 236], np.float32)
    base += (np.asarray(fib, np.float32)[..., None] - 128) * 0.5
    out = base * (1 - a[..., None]) + np.array(INK, np.float32) * a[..., None]
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(OUT / f"slip-{key}.png")
print("ok")
