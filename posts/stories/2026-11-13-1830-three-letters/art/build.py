#!/usr/bin/env python3
"""Builds the three frames of the 'three letters' Story: engraved brass plates on an oxblood door, shot three ways.

Run from the repo root:  python3 posts/stories/2026-11-13-1830-three-letters/art/build.py
then                     python3 studio.py render posts/stories/2026-11-13-1830-three-letters

How it works. Each plate face is drawn flat in HTML and CSS (brass, bevel, screws, and letters cut with an SVG
lighting filter) and captured as a picture. A small pinhole camera then places the door, the shadows, the plate's
sides and its face in 3D and writes art/bg-0N.jpg. The slide files put that picture under the headline.
(The browser's own CSS 3D dropped parts of a plate this big, so the camera is done here instead.)"""
import json, math, sys
from pathlib import Path
import numpy as np, cv2

ART = Path(__file__).resolve().parent
ROOT = ART.parents[3]
sys.path.insert(0, str(ROOT))
import studio

DOOR, CREAM, BRASS = "#5B0F1C", "#F5E9D6", "#E6CB72"
FW, FH, SS = 1080, 1920, 2          # frame size, and the scale the background picture is made at
T = 15                               # plate thickness in plate units (1 unit = 1px when the name is set at 100px)


# ------------------------------------------------------------------ flat plate faces (HTML -> PNG)
def engrave(fid, w):
    """A chamfered cut with an enamel floor, lit from the top left. w = chamfer width in px."""
    return f"""<filter id="{fid}" x="-2%" y="-12%" width="104%" height="124%" color-interpolation-filters="sRGB">
<feMorphology in="SourceAlpha" operator="erode" radius="{w:.2f}" result="fl"/>
<feGaussianBlur in="SourceAlpha" stdDeviation="{w*.5:.2f}" result="hm"/>
<feDiffuseLighting in="hm" surfaceScale="{-w*1.5:.2f}" diffuseConstant="1.25" lighting-color="#FFE7A2" result="lit"><feDistantLight azimuth="225" elevation="38"/></feDiffuseLighting>
<feComposite in="lit" in2="SourceAlpha" operator="in" result="walls"/>
<feFlood flood-color="#17110A"/><feComposite in2="fl" operator="in" result="floor"/>
<feOffset in="fl" dx="{w*.9:.2f}" dy="{w*1.25:.2f}" result="fo"/><feComposite in="fl" in2="fo" operator="out"/><feGaussianBlur stdDeviation="{w*.45:.2f}" result="fs0"/>
<feFlood flood-color="#000" flood-opacity=".85"/><feComposite in2="fs0" operator="in"/><feComposite in2="fl" operator="in" result="fsh"/>
<feOffset in="fl" dx="{-w*.5:.2f}" dy="{-w*.7:.2f}" result="go"/><feComposite in="fl" in2="go" operator="out"/><feGaussianBlur stdDeviation="{w*.5:.2f}" result="gl0"/>
<feFlood flood-color="#6A5A3C" flood-opacity=".55"/><feComposite in2="gl0" operator="in"/><feComposite in2="fl" operator="in" result="gloss"/>
<feMerge><feMergeNode in="walls"/><feMergeNode in="floor"/><feMergeNode in="fsh"/><feMergeNode in="gloss"/></feMerge>
</filter>"""


def face_css(q):
    def p(n):
        return f"{n*q:.2f}px"
    return f"""
html,body{{background:transparent}}
.fin{{position:absolute;left:0;top:0;border-radius:{p(7)};overflow:hidden;
  background:var(--gloss,linear-gradient(#0000,#0000)),
   linear-gradient(104deg,rgba(64,44,6,0) 0 var(--d0,10%),rgba(64,44,6,.34) calc(var(--d0,10%) + 14%),rgba(64,44,6,.05) calc(var(--d0,10%) + 30%),rgba(64,44,6,0) calc(var(--d0,10%) + 40%) 100%),
   linear-gradient(180deg,#F3DF98 0%,#E0C56C 12%,#CFAF52 44%,#C2A248 62%,#A98A37 100%);
  box-shadow:inset 0 {p(2.2)} 0 rgba(255,250,224,.95),inset {p(2.2)} 0 0 rgba(255,246,206,.7),
   inset 0 {p(-2.4)} 0 rgba(78,56,10,.8),inset {p(-2.2)} 0 0 rgba(78,56,10,.55),inset 0 0 {p(40)} rgba(92,66,12,.28)}}
.fin .tex{{position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:overlay;opacity:.3}}
.fin .pat{{position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:multiply;opacity:.07}}
.fin .cham{{position:absolute;inset:{p(9)};border-radius:{p(4)};box-shadow:0 0 0 {p(.8)} rgba(84,60,10,.55),{p(.9)} {p(1.2)} 0 {p(.8)} rgba(255,250,222,.6)}}
.eng{{position:absolute;font-family:News;font-weight:700;color:#000;text-transform:uppercase;white-space:nowrap}}
.screw{{position:absolute;width:{p(40)};height:{p(40)};border-radius:50%;
  background:radial-gradient(circle at 34% 28%,#FFF8D6 0%,#EAD288 22%,#C2A248 55%,#8A6E28 82%,#5E4914 100%);
  box-shadow:0 0 0 {p(2.2)} rgba(34,22,2,.9),0 0 0 {p(4.6)} rgba(126,98,30,.55),{p(2.4)} {p(4)} {p(5)} {p(3.4)} rgba(40,26,2,.5),{p(-1.2)} {p(-2)} 0 {p(4.4)} rgba(255,246,206,.4)}}
.screw:before{{content:"";position:absolute;left:5%;right:5%;top:50%;height:16%;margin-top:-8%;border-radius:{p(1)};
  background:linear-gradient(180deg,#0E0902 0%,#2A1E06 55%,#6B531A 100%);box-shadow:0 {p(1.3)} 0 rgba(255,246,206,.8);transform:rotate(var(--r,24deg))}}
"""


def gloss(kind, s0):
    """What the polished face reflects. Each view gets its own, and it is kept off the three letters."""
    if kind == "window":   # two panes of a window and the bar between them
        return (f"linear-gradient(104deg,rgba(255,252,236,0) 0 {s0}%,rgba(255,252,236,.78) {s0+.6}%,rgba(255,252,236,.62) {s0+4.2}%,rgba(255,252,236,0) {s0+4.8}%,"
                f"rgba(255,252,236,0) {s0+5.6}%,rgba(255,252,236,.5) {s0+6}%,rgba(255,252,236,.4) {s0+7.6}%,rgba(255,252,236,0) {s0+8}% 100%)")
    if kind == "soft":     # one broad, soft band of sky
        return f"linear-gradient(98deg,rgba(255,252,236,0) 0 {s0}%,rgba(255,252,236,.5) {s0+7}%,rgba(255,252,236,.42) {s0+10}%,rgba(255,252,236,0) {s0+20}% 100%)"
    if kind == "sky":      # a strip of sky along the top, above the letters
        return "linear-gradient(180deg,rgba(255,252,236,0) 5%,rgba(255,252,236,.5) 9%,rgba(255,252,236,.34) 20%,rgba(255,252,236,0) 29%)"
    if kind == "edge":     # light catching one end only
        return f"linear-gradient(90deg,rgba(255,252,236,0) 0 {s0}%,rgba(255,252,236,.42) 100%)"
    return "linear-gradient(#0000,#0000)"


TEX = '<svg class="tex"><rect width="100%" height="100%" filter="url(#grainb)"/></svg><svg class="pat"><rect width="100%" height="100%" filter="url(#patina)"/></svg><div class="cham"></div>'


def screws(q, W, H, ends="lr"):
    s = ""
    for side, r1, r2 in (("left", 31, 72), ("right", -18, 8)):
        if side[0] in ends:
            s += f'<i class="screw" style="{side}:{38*q:.1f}px;top:{38*q:.1f}px;--r:{r1}deg"></i><i class="screw" style="{side}:{38*q:.1f}px;bottom:{38*q:.1f}px;--r:{r2}deg"></i>'
    return s


NAME = (1840, 204)     # the name plate, in plate units
LIST = (2400, 690)      # the small-print plate


def name_face(q, gl=("window", 91), d0="30%"):
    W, H = NAME[0] * q, NAME[1] * q
    return W, H, f"""<div class="fin" style="width:{W:.1f}px;height:{H:.1f}px;--gloss:{gloss(*gl)};--d0:{d0}">
{TEX}{screws(q, W, H)}
<div class="eng" style="right:{180*q:.1f}px;top:{56*q:.1f}px;font-size:{100*q:.1f}px;line-height:1;letter-spacing:.1em;word-spacing:.3em;filter:url(#eng)">Kittiwake &amp; Quay <span style="letter-spacing:.07em">L</span><span style="letter-spacing:.1em">T</span>D</div>
</div>""", [engrave("eng", 1.25 * q)]


def list_face(q, gl=("sky", 0), d0="56%"):
    """The second plate: the four things, one to a line. A long plate with its fixings top and bottom at the middle."""
    W, H = LIST[0] * q, LIST[1] * q
    rows = [("Kittiwake &amp; Quay Ltd", 86, 158, "eng", ".1em"), ("Registered in England and Wales", 56, 297, "eng2", ".07em"),
            ("Registered office: 12 Quay Row", 56, 388, "eng2", ".07em"), ("Company No. 24601357", 56, 479, "eng2", ".07em")]
    txt = "".join(f'<div class="eng" style="left:0;width:100%;text-align:center;top:{y*q:.1f}px;font-size:{f*q:.1f}px;line-height:1;letter-spacing:{ls};filter:url(#{fid})">{t}</div>' for t, f, y, fid, ls in rows)
    sc = "".join(f'<i class="screw" style="left:{(LIST[0]/2-20)*q:.1f}px;{e}:{34*q:.1f}px;--r:{r}deg"></i>' for e, r in (("top", -14), ("bottom", 52)))
    return W, H, f"""<div class="fin" style="width:{W:.1f}px;height:{H:.1f}px;--gloss:{gloss(*gl)};--d0:{d0}">
{TEX}{sc}{txt}</div>""", [engrave("eng", 1.15 * q), engrave("eng2", .95 * q)]


def shoot(jobs):
    """jobs: {name: (q, face function, kwargs)} -> {name: RGBA array}"""
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = studio.browser(p)
        for name, (q, fn, kw) in jobs.items():
            kw = dict(kw); crop = kw.pop("crop", None)
            W, H, html, filters = fn(q, **kw)
            cx = int(W - crop * q) if crop else 0
            doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{studio.font_css()}*{{box-sizing:border-box;margin:0;padding:0}}"
                   f"html,body{{-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}{face_css(q)}</style></head><body>"
                   f"<svg width='0' height='0' style='position:absolute'><defs>{''.join(filters)}"
                   f"<filter id='grainb' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='{0.012/q*2.5:.4f} {0.85/q*2.5:.3f}' numOctaves='2' seed='7'/>"
                   f"<feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.3 -.3'/></filter>"
                   f"<filter id='patina' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='{0.0035/q:.5f} {0.006/q:.5f}' numOctaves='3' seed='11'/>"
                   f"<feColorMatrix values='0 0 0 0 .42  0 0 0 0 .32  0 0 0 0 .1  0 0 0 2.2 -.95'/></filter></defs></svg><div style='position:absolute;left:{-cx}px;top:0'>{html}</div></body></html>")
            tmp = ART / f".{name}.html"; tmp.write_text(doc)
            pg = b.new_page(viewport={"width": int(W) - cx + 2, "height": int(H) + 2}, device_scale_factor=1)
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(250)
            png = ART / f".{name}.png"
            pg.screenshot(path=str(png), omit_background=True, clip={"x": 0, "y": 0, "width": int(W) - cx, "height": int(H)})
            pg.close(); tmp.unlink()
            out[name] = cv2.imread(str(png), cv2.IMREAD_UNCHANGED); png.unlink()
        b.close()
    return out


# ------------------------------------------------------------------ the camera
def rot(ry=0, rx=0, rz=0):
    a, b, c = (math.radians(v) for v in (ry, rx, rz))
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


class Cam:
    """Plate units -> frame pixels. piv = the point (in units) that sits at 'at' (frame px) and that the scene turns about."""
    def __init__(self, k, piv, at, ry=0, rx=0, rz=0, d=1500, vp=(540, 1100)):
        self.k, self.piv, self.at, self.R, self.d, self.vp = k, np.array([*piv, 0.0]), np.array(at, float), rot(ry, rx, rz), d, np.array(vp, float)

    def pt(self, X, Y, Z=0.0):
        v = self.R @ (np.array([X, Y, Z], float) - self.piv) * self.k
        w = self.d / (self.d - v[2])
        return (self.vp + (self.at + v[:2] - self.vp) * w) * SS

    def quad(self, x0, y0, x1, y1, z):
        return np.float32([self.pt(x0, y0, z), self.pt(x1, y0, z), self.pt(x1, y1, z), self.pt(x0, y1, z)])


def warp(tex, cam, x0, y0, x1, y1, z):
    """Draw a flat picture onto the rectangle x0..x1, y0..y1 at height z. Returns premultiplied RGBA float32, mip-blended."""
    h, w = tex.shape[:2]
    dst = cam.quad(x0, y0, x1, y1, z)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), dst)
    size = (FW * SS, FH * SS)
    t = tex.astype(np.float32) / 255
    if t.shape[2] == 4:
        t[..., :3] *= t[..., 3:4]
    # how many texture pixels fall in one output pixel, per pixel
    Mi = np.linalg.inv(M)
    ys, xs = np.mgrid[0:size[1]:8, 0:size[0]:8].astype(np.float64)
    def inv(x, y):
        d = Mi[2, 0] * x + Mi[2, 1] * y + Mi[2, 2]
        return (Mi[0, 0] * x + Mi[0, 1] * y + Mi[0, 2]) / d, (Mi[1, 0] * x + Mi[1, 1] * y + Mi[1, 2]) / d
    u0, v0 = inv(xs, ys); u1, v1 = inv(xs + 1, ys); u2, v2 = inv(xs, ys + 1)
    m = np.maximum(np.hypot(u1 - u0, v1 - v0), np.hypot(u2 - u0, v2 - v0))
    lam = np.clip(np.log2(np.maximum(m, 1e-6)), 0, 3)
    lam = cv2.resize(lam.astype(np.float32), size, interpolation=cv2.INTER_LINEAR)
    out = np.zeros((size[1], size[0], t.shape[2]), np.float32)
    lvl = t
    for i in range(4):
        S = np.diag([2.0 ** i, 2.0 ** i, 1.0])
        wimg = cv2.warpPerspective(lvl, M @ S, size, flags=cv2.INTER_CUBIC if i == 0 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        wgt = np.clip(1 - np.abs(lam - i), 0, 1)[..., None]
        out += wimg * wgt
        if i < 3:
            lvl = cv2.resize(lvl, (max(1, lvl.shape[1] // 2), max(1, lvl.shape[0] // 2)), interpolation=cv2.INTER_AREA)
    return np.clip(out, 0, 1)


def over(dst, src):
    a = src[..., 3:4]
    dst[..., :3] = src[..., :3] + dst[..., :3] * (1 - a)


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (4, 2, 0)], np.float32) / 255   # BGR


def door_texture(plates, light, span=(-2600, -2600, 5200, 5200), q=0.5):
    """What the plates do to the door, as a flat two-channel picture in door space: brass light thrown back onto
    the paint, and shadow (a tight contact shadow plus a long soft one down and to the right). The paint itself is
    lit in the frame, in render(): 'light' = (x, y, rx, ry) of the pool of light, in frame pixels."""
    x0, y0, x1, y1 = span
    w, h = int((x1 - x0) * q), int((y1 - y0) * q)
    fx = np.zeros((h, w, 2), np.float32)
    for (px, py, pw, ph) in plates:
        def rect(dx, dy, grow, blur, strength):
            m = np.zeros((h, w), np.float32)
            cv2.rectangle(m, (int((px + dx - grow - x0) * q), int((py + dy - grow - y0) * q)), (int((px + pw + dx + grow - x0) * q), int((py + ph + dy + grow - y0) * q)), 1.0, -1)
            return cv2.GaussianBlur(m, (0, 0), blur * q) * strength
        fx[..., 0] = np.maximum(fx[..., 0], rect(0, 0, 60, 120, .16))
        fx[..., 1] = np.maximum(fx[..., 1], np.clip(rect(34, 62, 0, 46, .62) + rect(9, 15, 0, 9, .8), 0, .93))
    return fx, span, light


def paint(light):
    """Gloss oxblood paint with one soft pool of light, top left."""
    lx, ly, rx, ry = light
    yy, xx = np.mgrid[0:FH * SS, 0:FW * SS].astype(np.float32)
    r = np.hypot((xx / SS - lx) / rx, (yy / SS - ly) / ry)
    g = np.clip(1 - r, 0, 1) ** 1.6
    base, hi, lo = hexc("#5B0F1C"), hexc("#932A3B"), hexc("#3A0710")
    img = lo + (base - lo) * np.clip(1.25 - r * .55, .3, 1)[..., None]
    return img + (hi - img) * (g * .9)[..., None]


def render(name, cam, door, parts):
    """parts: list of (texture RGBA, x, y, w, h in units). Writes art/<name>.jpg."""
    fx, (x0, y0, x1, y1), light = door
    dh, dw = fx.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [dw, 0], [dw, dh], [0, dh]]), cam.quad(x0, y0, x1, y1, 0))
    fxw = cv2.warpPerspective(fx, M, (FW * SS, FH * SS), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    canvas = paint(light)
    canvas = canvas + (hexc("#D8B25A") - canvas) * fxw[..., 0:1]
    canvas = canvas * (1 - fxw[..., 1:2]) + hexc("#24040A") * fxw[..., 1:2]
    side = {"t": ("#FFF3C4", "#D9BC62"), "l": ("#F6E6A6", "#C9AA50"), "b": ("#7B6220", "#3E2F0B"), "r": ("#9A7C2E", "#4A390F")}
    for tex, x, y, w, h in parts:
        quads = {"t": [(x, y, T), (x + w, y, T), (x + w, y, 0), (x, y, 0)], "b": [(x, y + h, T), (x + w, y + h, T), (x + w, y + h, 0), (x, y + h, 0)],
                 "l": [(x, y, T), (x, y + h, T), (x, y + h, 0), (x, y, 0)], "r": [(x + w, y, T), (x + w, y + h, T), (x + w, y + h, 0), (x + w, y, 0)]}
        layer = np.zeros((FH * SS, FW * SS, 4), np.float32)
        for s, q4 in quads.items():
            pts = np.array([cam.pt(*p) for p in q4])
            c = (hexc(side[s][0]) * .55 + hexc(side[s][1]) * .45)
            poly = np.round(pts * 16).astype(np.int32)
            cv2.fillConvexPoly(layer, poly, (float(c[0]), float(c[1]), float(c[2]), 1.0), lineType=cv2.LINE_AA, shift=4)
        over(canvas, layer)
        over(canvas, warp(tex, cam, x, y, x + w, y + h, T))
    out = np.clip(canvas * 255 + .5, 0, 255).astype(np.uint8)
    cv2.imwrite(str(ART / f"{name}.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 96])
    return out


# ------------------------------------------------------------------ the three frames
HEAD = f"""
.frame{{background:#3A0710;color:{CREAM};font-family:Outfit}}
.bg{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
.h{{position:absolute;left:64px;font:700 124px/1.02 Outfit;letter-spacing:-.02em;color:{CREAM}}}
.h b{{font-weight:700;color:{BRASS}}}
"""


def frame1(tex, n="bg-01", k=2.4, at=(48, 1250), ry=62, rx=0, rz=0, d=2400, vp=(900, 950), crop=1000):
    """The right-hand end of the plate from the left: QUAY LTD, the end and its two screws. Frame 2 is the same view, closer."""
    nm = NAME
    x0 = nm[0] - crop
    cam = Cam(k=k, piv=(1030, nm[1] / 2), at=at, ry=ry, rx=rx, rz=rz, d=d, vp=vp)
    door = door_texture([(x0 - 600, 0, crop + 600, nm[1])], light=(300, 60, 1500, 2000), span=(nm[0] - 3200, -2600, nm[0] + 2600, 2800), q=0.4)
    render(n, cam, door, [(tex["name_macro"], x0, 0, crop, nm[1])])
    return f"""<style>{HEAD}</style><img class="bg" src="{{{{post}}}}/art/{n}.jpg">
<div class="h" style="top:292px">Limited<br>company?</div>
<!--grain:0.04-->"""


def frame2(tex, n="bg-02", k=3.7, at=(62, 676), ry=57, rx=0, rz=0, d=2600, vp=(900, 366), crop=1000):
    nm = NAME
    x0 = nm[0] - crop
    cam = Cam(k=k, piv=(nm[0] - 417, nm[1] / 2), at=at, ry=ry, rx=rx, rz=rz, d=d, vp=vp)
    door = door_texture([(x0 - 400, 0, crop + 400, nm[1])], light=(330, -60, 1500, 2000), span=(nm[0] - 2200, -2000, nm[0] + 2600, 2400))
    render(n, cam, door, [(tex["name_macro"], x0, 0, crop, nm[1])])
    return f"""<style>{HEAD}</style><img class="bg" src="{{{{post}}}}/art/{n}.jpg">
<div class="h" style="top:1196px">Those three<br>letters come<br>with <b>a list.</b></div>
<!--grain:0.04-->"""


def frame3(tex, n="bg-03", k=0.77, at=(528, 1030), ry=-20, rx=9, rz=-8, d=2200, vp=(540, 1030)):
    ls = LIST
    cam = Cam(k=k, piv=(ls[0] / 2, ls[1] / 2), at=at, ry=ry, rx=rx, rz=rz, d=d, vp=vp)
    door = door_texture([(0, 0, *ls)], light=(320, 240, 1500, 2000), span=(-1600, -2600, ls[0] + 1600, 3200), q=0.4)
    render(n, cam, door, [(tex["list"], 0, 0, *ls)])
    return f"""<style>{HEAD}
.foot{{position:absolute;left:64px;right:64px;top:1468px;height:110px}}
.foot p{{position:absolute;left:0;top:0;font:700 46px/1 Outfit;letter-spacing:-.01em;color:{CREAM};white-space:nowrap}}
.foot p+p{{top:66px;font:500 36px/1 Outfit;letter-spacing:0;color:rgba(245,233,214,.84)}}
.foot .nx-logo{{position:absolute;right:0;top:7px;height:34px}}
</style><img class="bg" src="{{{{post}}}}/art/{n}.jpg">
<div class="h" style="top:292px">Your website has<br>to show <b>all four.</b></div>
<div class="foot"><p>Check your footer tonight.</p><p>Source: gov.uk, Running a limited company</p><!--logo:{CREAM},{BRASS}--></div>
<!--grain:0.04-->"""


def frames(tex):
    return [frame1(tex), frame2(tex), frame3(tex)]


def main(only=None):
    tex = shoot({"name_macro": (9.0, name_face, {"gl": ("sky", 0), "d0": "40%", "crop": 1000}),
                 "list": (3.0, list_face, {})})
    for i, html in enumerate(frames(tex), 1):
        (ART / f"slide-{i:02d}.html").write_text(html)


if __name__ == "__main__":
    main()
