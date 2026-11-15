"""Prints the two textures the counter needs (art/tex/):
  wheel.png   one number wheel: the digits 0 to 9 round its edge, white on black
  dymo.png    a strip of embossed label tape reading GOOGLE (colour), dymo-h.png (height for the emboss)
Fonts are the repo's woff2 files converted to TTF with fontTools (see build.py)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "tex"; OUT.mkdir(exist_ok=True)
TTF = Path("/tmp/claude-0/ttf")

# wheel: the strip runs round the wheel. Cell = width of the wheel x one tenth of its circumference.
CW, CH = 330, 258
img = Image.new("L", (CW, CH * 10), 8)
d = ImageDraw.Draw(img)
f = ImageFont.truetype(str(TTF / "oswald-latin-500-normal.ttf"), 250)
for k in range(10):
    cy = CH * k + CH / 2
    d.text((CW / 2, cy + 4), str(k), font=f, fill=236, anchor="mm")
img = img.filter(ImageFilter.GaussianBlur(0.6))
img.convert("RGB").save(OUT / "wheel.png")

# label tape: 9mm high. Raised letters go pale where the plastic is stretched.
TH = 300
f2 = ImageFont.truetype(str(TTF / "archivo-latin-800-normal.ttf"), 196)
word = "GOOGLE"
spacing = 34
widths = [f2.getbbox(c)[2] - f2.getbbox(c)[0] for c in word]
TW = sum(widths) + spacing * (len(word) - 1) + 2 * 150
mask = Image.new("L", (TW, TH), 0)
dm = ImageDraw.Draw(mask)
x = 150
for c, w in zip(word, widths):
    bb = f2.getbbox(c)
    dm.text((x - bb[0], TH / 2), c, font=f2, fill=255, anchor="lm")
    x += w + spacing
m = np.asarray(mask, np.float32) / 255
h = np.asarray(mask.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
Image.fromarray((h * 255).astype(np.uint8)).save(OUT / "dymo-h.png")
# colour: deep green tape, letters a stressed pale green, tiny streaks along the tape
GREEN = np.array([17, 66, 49], np.float32)
PALE = np.array([214, 232, 220], np.float32)
rng = np.random.default_rng(3)
streak = rng.normal(0, 1, (TH, 1)).repeat(TW, 1)
streak = np.asarray(Image.fromarray(((streak + 3) * 40).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur((40, 1))), np.float32) / 255 - 0.5
soft = np.asarray(mask.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
col = GREEN[None, None] * (1 + 0.06 * streak[..., None]) * (1 - soft[..., None]) + PALE[None, None] * soft[..., None] * (0.93 + 0.07 * rng.random((TH, TW, 1)))
Image.fromarray(col.clip(0, 255).astype(np.uint8)).save(OUT / "dymo.png")
print("tape px", TW, TH)
