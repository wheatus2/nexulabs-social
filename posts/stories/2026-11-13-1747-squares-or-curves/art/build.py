#!/usr/bin/env python3
"""Builds the three frames of the 'squares or curves' Story.
One made-up logo mark (a ring and a stem), drawn once as cubic curves and shown three ways:
solid, as the pixels of a small picture of itself, and as the path with its points and handles.
Two colours only. Every line is counterchanged: bone where it crosses violet, violet where it crosses bone.
Run: python3 posts/stories/<id>/art/build.py   then   python3 studio.py render posts/stories/<id>
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
VIO, BONE = "#5A2BE6", "#F4EEE1"
D, W, RC = 0.78, 0.50, 0.44          # stem left edge, stem width, counter radius (in units of R)
H = math.sqrt(1 - D * D)
T0 = math.degrees(math.atan2(H, D))


def arc(t1, t2, r=1.0):
    """cubic for a circle arc (degrees, y down): p0, c1, c2, p3"""
    a, b = math.radians(t1), math.radians(t2)
    k = 4 / 3 * math.tan((b - a) / 4)
    p0 = (r * math.cos(a), r * math.sin(a)); p3 = (r * math.cos(b), r * math.sin(b))
    return p0, (p0[0] - k * r * math.sin(a), p0[1] + k * r * math.cos(a)), (p3[0] + k * r * math.sin(b), p3[1] - k * r * math.cos(b)), p3


def mark(cx, cy, R, step=90):
    """svg path of the mark and its curve anchors [(point, handle_in, handle_out)]; the ring has a point every `step` degrees"""
    cuts = [T0] + [a for a in range(step, 360, step) if T0 < a < 360 - T0] + [360 - T0]
    outer = [arc(a, b) for a, b in zip(cuts, cuts[1:])]
    counter = [arc(a, a + 90, RC) for a in (0, 90, 180, 270)]
    X = lambda p: (cx + R * p[0], cy + R * p[1])
    f = lambda p: "%.2f %.2f" % X(p)
    d = f"M{f((D, -1))} L{f((D + W, -1))} L{f((D + W, 1))} L{f((D, 1))} L{f((D, H))} "
    d += "".join(f"C{f(c1)} {f(c2)} {f(p3)} " for _, c1, c2, p3 in outer) + "Z M" + f(counter[0][0]) + " "
    d += "".join(f"C{f(c1)} {f(c2)} {f(p3)} " for _, c1, c2, p3 in counter) + "Z"
    an = [(X(outer[i][3]), X(outer[i][2]), X(outer[i + 1][1])) for i in range(len(outer) - 1)]
    an += [(X(counter[i][3]), X(counter[i][2]), X(counter[(i + 1) % 4][1])) for i in range(4)]
    return d, an


def counterchange(d, lines, uid):
    """draw `lines` (svg markup using currentColor) bone outside the mark and violet inside it"""
    return (f'<defs><mask id="in{uid}"><rect width="1080" height="1920" fill="#000"/><path d="{d}" fill="#fff" fill-rule="evenodd"/></mask>'
            f'<mask id="out{uid}"><rect width="1080" height="1920" fill="#fff"/><path d="{d}" fill="#000" fill-rule="evenodd"/></mask></defs>'
            f'<g mask="url(#out{uid})" color="{BONE}">{lines}</g><g mask="url(#in{uid})" color="{VIO}">{lines}</g>')


def knob(x, y, s=26):
    return f'<rect x="{x - s / 2:.1f}" y="{y - s / 2:.1f}" width="{s}" height="{s}" fill="currentColor"/>'


CSS = f"""
.f{{position:absolute;inset:0;background:{VIO};color:{BONE};font-family:Outfit}}
.f svg.art{{position:absolute;left:0;top:0}}
.h{{position:absolute;font:800 146.4px/1 Syne;letter-spacing:.012em;white-space:nowrap}}
.h i{{font-style:normal}}
.s{{position:absolute;left:63px;font:500 46px/60px Outfit;letter-spacing:-.005em;white-space:nowrap}}
"""

# ---------- frame 1: the mark, solid, with the patch we are about to look at
R1, CX1, CY1 = 700, 200, 1620
ZOOM = 10 / 3
BOX = (485, 794, 809, 1370)           # 324 x 576, the shape of the frame; frame 2 is this patch, 3.33 times bigger


def frame1():
    d, _ = mark(CX1, CY1, R1)
    x0, y0, x1, y1 = BOX
    box = f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="currentColor" stroke-width="4"/>'
    knobs = "".join(knob(x, y) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    return f"""<style>{CSS}
.h1{{top:258px;left:53.6px}}
.q{{position:absolute;right:60px;text-align:right;top:1452px;font:800 56px/1.08 Syne;letter-spacing:.012em;color:{VIO};white-space:nowrap}}
</style>
<div class="f">
<svg class="art" width="1080" height="1920" viewBox="0 0 1080 1920"><path d="{d}" fill="{BONE}" fill-rule="evenodd"/>
{counterchange(d, box + knobs, 1)}</svg>
<div class="h h1" data-bleed>Zoom in<br>on y<i style="margin-left:.045em">our</i><br>log<i style="margin-left:.02em">o.</i></div>
<div class="q" data-bleed>Squares<br>or curves?</div>
</div><!--grain:0.05-->"""


def tiles():
    """the patch in BOX as a small picture: 9 x 16 pixels, each the plain average of what it covers"""
    S = 8
    x0, y0, x1, y1 = BOX
    w, h = x1 - x0, y1 - y0
    im = Image.new("RGB", (w * S, h * S), VIO); dr = ImageDraw.Draw(im)
    T = lambda x, y: ((x - x0) * S, (y - y0) * S)
    dr.ellipse([*T(CX1 - R1, CY1 - R1), *T(CX1 + R1, CY1 + R1)], fill=BONE)
    dr.rectangle([*T(CX1 + D * R1, CY1 - R1), *T(CX1 + (D + W) * R1, CY1 + R1)], fill=BONE)
    dr.ellipse([*T(CX1 - RC * R1, CY1 - RC * R1), *T(CX1 + RC * R1, CY1 + RC * R1)], fill=VIO)
    im = im.filter(ImageFilter.GaussianBlur(0.2 * 36 * S))          # the softness of a small, resized picture
    small = im.resize((9, 16), Image.BOX)
    v, b = Image.new("RGB", (1, 1), VIO).getpixel((0, 0)), Image.new("RGB", (1, 1), BONE).getpixel((0, 0))
    px = small.load()
    for y in range(16):
        for x in range(9):
            t = (px[x, y][1] - v[1]) / (b[1] - v[1])                     # how much of the pixel is logo
            t = 0 if t < .07 else 1 if t > .93 else min(.75, max(.25, round(t * 4) / 4))        # no ghosts: nearly-empty and nearly-full pixels are clean, the rest are a quarter, a half or three quarters
            px[x, y] = tuple(round(v[i] + (b[i] - v[i]) * t) for i in range(3))
    return small.resize((2160, 3840), Image.NEAREST)


def frame2():
    tiles().save(HERE / "pixels.png")
    return f"""<style>{CSS}
.px{{position:absolute;inset:0;width:1080px;height:1920px;image-rendering:pixelated}}
.s2{{top:284px}}
.h2{{top:1388px;left:59.5px;color:{VIO};font-size:134.7px}}
</style>
<div class="f">
<img class="px" src="{{{{post}}}}/art/pixels.png">
<div class="s s2">A JPG or a PNG is only a picture.<br>Bigger picture, bigger squares.</div>
<div class="h h2" data-bleed>Squ<i style="margin-left:.02em">a</i><i style="margin-left:.03em">r</i><i style="margin-left:.055em">es.</i></div>
</div><!--grain:0.05-->"""


R3, CX3, CY3 = 1300, 540, 1732


def frame3():
    d, an = mark(CX3, CY3, R3, step=45)
    lines = ""
    for p, hi, ho in an:
        for h in (hi, ho):
            lines += (f'<path d="M{p[0]:.1f} {p[1]:.1f} L{h[0]:.1f} {h[1]:.1f}" stroke="currentColor" stroke-width="4"/>'
                      f'<circle cx="{h[0]:.1f}" cy="{h[1]:.1f}" r="13" fill="currentColor"/>')
    knobs = "".join(knob(p[0], p[1]) for p, _, _ in an)
    return f"""<style>{CSS}
.h3{{top:640px;left:54.5px;color:{VIO};font-size:157.6px}}
.s3{{top:836px;color:{VIO}}}
.ft{{top:1456px;color:{BONE}}}
.lg{{position:absolute;right:64px;top:1520px;height:44px}}.lg .nx-logo{{height:44px}}
</style>
<div class="f">
<svg class="art" width="1080" height="1920" viewBox="0 0 1080 1920"><path d="{d}" fill="{BONE}" fill-rule="evenodd"/>
{counterchange(d, lines + knobs, 3)}</svg>
<div class="h h3" data-bleed>Cur<i style="margin-left:.08em">v</i><i style="margin-left:.02em">es.</i></div>
<div class="s s3">That’s the logo itself. A vector file:<br>SVG, AI or EPS. Sharp on a pen.<br>Sharp on the side of a van.</div>
<div class="s ft">Ask whoever made<br>your logo for it.</div>
<div class="lg"><!--logo:{BONE},{BONE}--></div>
</div><!--grain:0.05-->"""


if __name__ == "__main__":
    for i, fn in enumerate((frame1, frame2, frame3), 1):
        (HERE / f"slide-{i:02d}.html").write_text(fn())
    print("built")
