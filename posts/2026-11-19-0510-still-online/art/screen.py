"""Draws what is on the arcade screen, one PNG per frame: our own 5x7 dot lettering on an 98 x 114 grid.
  python3.13 screen.py   -> .screen-1.png .screen-2.png .screen-3.png (20px per screen dot)
Nothing here is taken from any game: the lettering, the little people and the layout are drawn for this post.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
GW, GH, CELL = 98, 114, 20
F = {
 "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
 "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
 "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
 "G": "01110 10001 10000 10111 10001 10001 01110", "H": "10001 10001 10001 11111 10001 10001 10001",
 "I": "11111 00100 00100 00100 00100 00100 11111", "L": "10000 10000 10000 10000 10000 10000 11111",
 "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
 "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
 "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
 "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
 "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
 "W": "10001 10001 10001 10101 10101 11011 10001", "Y": "10001 10001 01010 00100 00100 00100 00100",
 "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
 "2": "01110 10001 00001 00110 01000 10000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
 "4": "00010 00110 01010 10010 11111 00010 00010", "6": "01110 10000 10000 11110 10001 10001 01110",
 "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00001 01110",
 ".": "00000 00000 00000 00000 00000 01100 01100", "'": "01100 01100 01000 00000 00000 00000 00000",
 "%": "11001 11010 00010 00100 01000 01011 10011", "/": "00001 00010 00010 00100 01000 01000 10000",
 "+": "00000 00100 00100 11111 00100 00100 00000", " ": "00000 00000 00000 00000 00000 00000 00000",
}
PERSON = ["00111100", "00111100", "00111100", "00011000", "11111111", "11111111", "10111101", "00111100", "00100100", "01100110"]
WHITE, GREEN, DIM, OFF = 1, 2, 3, 0
COL = {OFF: (5, 6, 16), WHITE: (255, 246, 228), GREEN: (70, 255, 140), DIM: (92, 96, 188)}


def text(g, s, x, y, k, c):
    for ch in s:
        rows = F[ch].split()
        for j, r in enumerate(rows):
            for i, b in enumerate(r):
                if b == "1":
                    g[y + j * k:y + (j + 1) * k, x + i * k:x + (i + 1) * k] = c
        x += 6 * k
    return x


def width(s, k):
    return (6 * len(s) - 1) * k


def frame(n):
    g = np.zeros((GH, GW), np.uint8)
    L = 8
    if n == 1:
        text(g, "19 NOV 2026", L, 5, 1, DIM)
        for i, ln in enumerate(("GTA 6", "IS OUT", "TODAY.")):
            text(g, ln, L, 20 + i * 19, 2, WHITE)
        text(g, "LOADING", L, 88, 1, DIM); text(g, "100%", GW - L - width("100%", 1), 88, 1, GREEN)
        g[99:108, L:GW - L] = GREEN
    if n == 2:
        text(g, "OUT OF OFFICE", L, 5, 1, DIM)
        for i, ln in enumerate(("SO IS", "HALF", "YOUR", "TEAM.")):
            text(g, ln, L, 20 + i * 19, 2, WHITE)
        for p in range(8):
            for j, r in enumerate(PERSON):
                for i, b in enumerate(r):
                    if b == "1":
                        g[99 + j, L + round(p * (GW - 2 * L - 8) / 7) + i] = GREEN if p < 4 else DIM
    if n == 3:
        text(g, "STILL ONLINE", L, 5, 1, GREEN)
        for i, ln in enumerate(("YOUR", "WEBSITE", "ISN'T.")):
            text(g, ln, L, 20 + i * 19, 2, WHITE)
        text(g, "ENQUIRIES", L, 88, 1, DIM); text(g, "+3", GW - L - width("+3", 1), 88, 1, GREEN)
        g[99:108, L:GW - L] = GREEN
        for gap in (26, 54):                        # three blocks of 26 dots, two dots apart
            g[99:108, L + gap:L + gap + 2] = OFF
    img = np.zeros((GH * CELL, GW * CELL, 3), np.uint8); img[:] = (2, 2, 7)
    pad = 2
    for c, rgb in COL.items():
        ys, xs = np.nonzero(g == c)
        for y, x in zip(ys, xs):
            img[y * CELL + pad:(y + 1) * CELL - pad, x * CELL + pad:(x + 1) * CELL - pad] = rgb
    im = Image.fromarray(img)
    glow = im.filter(ImageFilter.GaussianBlur(9))
    out = np.maximum(np.asarray(im).astype(np.float32), np.asarray(glow).astype(np.float32) * 0.55)
    # faint scan lines
    out *= (0.86 + 0.14 * (np.arange(GH * CELL) % CELL < CELL - 5))[:, None, None]
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(HERE / f".screen-{n}.png")


for n in (1, 2, 3):
    frame(n)
