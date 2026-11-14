"""Prints the two ink stamps that go on the eggs (tex/stamp-2019.png, tex/stamp-2026.png).

An egg stamp is a rubber or inkjet print on a curved shell: the ink is never even. Each stamp is set in
Geist Mono, then the ink is thinned in places, a few pinholes are left where the shell's pores did not
take it, and the edges are softened a touch, as ink does on chalk.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TTF = Path("/tmp/nx-geistmono-medium.ttf")
if not TTF.exists():
    f = TTFont(ROOT / "fonts" / "GeistMono-Medium.woff2"); f.flavor = None; f.save(TTF)

W, H = 2048, 768


def stamp(text, seed):
    rng = np.random.default_rng(seed)
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(TTF), 380)
    bb = d.textbbox((0, 0), text, font=font)
    x = (W - (bb[2] - bb[0])) / 2 - bb[0]
    y = (H - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x, y), text, font=font, fill=255)
    a = np.asarray(im, dtype=np.float32) / 255
    a = gaussian_filter(a, 2.2)
    a = np.clip((a - 0.5) * 3 + 0.5, 0, 1)                  # soft, slightly spread edge
    # uneven ink: broad patches lighter, a fine mottle, and pinholes where the pores refused it
    broad = gaussian_filter(rng.normal(0, 1, (H, W)), 60); broad /= np.abs(broad).max()
    fine = gaussian_filter(rng.normal(0, 1, (H, W)), 2.5); fine /= np.abs(fine).max()
    holes = gaussian_filter(rng.random((H, W)), 1.3)
    holes = (holes > np.quantile(holes, 0.035)).astype(np.float32)
    ink = np.clip(0.93 + 0.12 * broad + 0.10 * fine, 0.45, 1.0) * gaussian_filter(holes, 0.8)
    a = a * ink
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 255, 255, 255
    rgba[..., 3] = (a * 255).astype(np.uint8)
    out = HERE / "tex" / f"stamp-{text[-4:]}.png"
    Image.fromarray(rgba, "RGBA").save(out)
    print("wrote", out)


if __name__ == "__main__":
    (HERE / "tex").mkdir(exist_ok=True)
    stamp("© 2019", 19)
    stamp("© 2026", 26)
