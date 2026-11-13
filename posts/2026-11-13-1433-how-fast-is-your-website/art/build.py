#!/usr/bin/env python3
"""Writes art/reel.html for this post. The stopwatch is drawn once here (dial, hand, case) and shot
four ways, close up and off centre, so every scene shows the same object. Run: python3 art/build.py

Dial units: the case is 1000 across, hub at 0,0, one turn is five seconds.
  step 276 | hand tip 288 | ticks 288-328 | numerals 369 | coloured flange 410-422 | wall 428-440 | case 440-500
"""
import math
from pathlib import Path

INK, RED, MID = "#081A36", "#E4212B", "#6C8FBD"
LIGHT = (-0.64, -0.77)          # where the light comes from (top left); shadows fall the other way


def pt(a, r):
    a = math.radians(a)
    return r * math.sin(a), -r * math.cos(a)


def arc(a0, a1, r):
    x0, y0 = pt(a0, r); x1, y1 = pt(a1, r)
    return f"M{x0:.2f} {y0:.2f}A{r} {r} 0 {1 if a1 - a0 > 180 else 0} 1 {x1:.2f} {y1:.2f}"


def dial_print():
    o = ['<svg class="print" viewBox="-500 -500 1000 1000" xmlns="http://www.w3.org/2000/svg">',
         '<defs><filter id="tsh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.5"/></filter></defs>']
    # the tick track sits a step below the middle of the dial, turned with fine rings
    o.append('<g fill="none" stroke="#0B2A5C" stroke-width=".55" opacity=".10">'
             + "".join(f'<circle r="{278 + i * 2.3:.1f}"/>' for i in range(1, 25)) + "</g>")
    o.append('<circle r="276.9" fill="none" stroke="#0B2A5C" stroke-width="1.5" opacity=".34"/>')
    o.append('<circle r="275.3" fill="none" stroke="#FFFFFF" stroke-width="1.7" opacity=".9"/>')
    # the flange: good to 2.5, needs work to 4.0, poor after
    g = 0.42
    for a0, a1, c in ((g, 180 - g, INK), (180 + g, 288 - g, MID), (288 + g, 360 - g, RED)):
        o.append(f'<path d="{arc(a0, a1, 416)}" fill="none" stroke="{c}" stroke-width="12"/>')
    ticks, shadows = [], []
    for i in range(50):
        a = i * 7.2
        ln, w = (40, 7) if i % 10 == 0 else (40, 3.8) if i % 5 == 0 else (18, 2.6)
        shadows.append(f'<rect x="{-w / 2}" y="-328" width="{w}" height="{ln}" transform="translate(2.1 3.4) rotate({a:.1f})"/>')
        ticks.append(f'<rect x="{-w / 2}" y="-328" width="{w}" height="{ln}" rx="{w * .14:.2f}" fill="{INK}" transform="rotate({a:.1f})"/>')
        # the long side that faces the light catches it
        ar = math.radians(a)
        d = -math.cos(ar) * LIGHT[0] - math.sin(ar) * LIGHT[1]
        hw = w * .26
        x = -w / 2 if d > 0 else w / 2 - hw
        ticks.append(f'<rect x="{x:.2f}" y="-328" width="{hw:.2f}" height="{ln}" fill="#5F7FB5" opacity="{0.25 + 0.6 * abs(d):.2f}" transform="rotate({a:.1f})"/>')
    o.append(f'<g fill="#0B2A5C" opacity=".36" filter="url(#tsh)">{"".join(shadows)}</g>')
    o += ticks
    for n in range(1, 6):
        x, y = pt(n * 72, 369)
        o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Grotesk" font-weight="700" font-size="48" '
                 f'text-anchor="middle" dominant-baseline="central" fill="{INK}">{n}</text>')
        x, y = pt(n * 72 - 36, 369)
        o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Grotesk" font-weight="500" font-size="32" letter-spacing="-.6" '
                 f'text-anchor="middle" dominant-baseline="central" fill="{INK}" opacity=".8">{n - 1}.5</text>')
    o.append("</svg>")
    return "".join(o)


def needle(shadow=False):
    """Hub at 0,0, pointing up: a slim folded lance whose point meets the inner end of a tick."""
    if shadow:
        return ('<svg class="ndl" viewBox="-40 -340 80 480" xmlns="http://www.w3.org/2000/svg">'
                '<path d="M0 -291L-2.5 -250L-5.2 0L-5 20L5 20L5.2 0L2.5 -250Z" fill="#0B2A5C"/></svg>')
    return ('<svg class="ndl" viewBox="-40 -340 80 480" xmlns="http://www.w3.org/2000/svg">'
            '<defs><linearGradient id="nl" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#F0444E"/><stop offset="1" stop-color="#E4212B"/></linearGradient>'
            '<linearGradient id="nr" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#D2141E"/><stop offset="1" stop-color="#B80E18"/></linearGradient></defs>'
            '<path d="M0 -291L-2.5 -250L-5.2 0L-5 20L0 20Z" fill="url(#nl)"/>'
            '<path d="M0 -291L2.5 -250L5.2 0L5 20L0 20Z" fill="url(#nr)"/>'
            '<path d="M0 -280L0 18" stroke="#FFFFFF" stroke-width=".55" opacity=".6"/>'
            '</svg>')


def hand(hx, hy, u):
    st = f'left:{hx}px;top:{hy}px;--u:{u}px'
    return (f'<div class="hd sh" style="{st}"><div class="rot">{needle(True)}</div></div>'
            f'<div class="hd" style="{st}"><div class="rot">{needle()}</div></div>'
            f'<div class="hub" style="{st}"></div>')


def watch(hx, hy, u):
    st = f'left:{hx - 500 * u:.1f}px;top:{hy - 500 * u:.1f}px;--u:{u}px'
    return (f'<div class="watch" style="{st}" data-ui data-bleed>'
            '<div class="bz"></div><div class="wall"></div><div class="face"></div>'
            + dial_print() + '<div class="glass"></div></div>')


def focus(fx, fy, r0, r1, px=7):
    """Depth of field: the dial away from the point in focus goes soft, and the corners fall off."""
    m = f'radial-gradient(circle at {fx}px {fy}px,transparent {r0}px,#000 {r1}px)'
    return (f'<div class="dof" style="backdrop-filter:blur({px}px);-webkit-mask-image:{m};mask-image:{m}"></div>'
            f'<div class="vig" style="background:radial-gradient(circle at {fx}px {fy}px,rgba(8,26,54,0) {r0 + 100}px,rgba(8,26,54,.26) {r1 + 420}px)"></div>')


def shot(hx, hy, u, f, cls=""):
    """One camera position: the dial, the focus, then the hand sharp over the top."""
    return f'<div class="clip"><div class="cam {cls}">' + watch(hx, hy, u) + focus(*f) + hand(hx, hy, u) + '</div></div>'


CSS = """
.scene{--ink:#081A36;--red:#E4212B;overflow:visible;visibility:hidden;color:var(--ink);
  animation:nxIn .01s linear var(--t0) both,nxOut .01s linear var(--t1) forwards,sv calc(var(--t1) - var(--t0) + .02s) linear var(--t0)}
@keyframes sv{0%,100%{visibility:visible}}
/* the first scene is there from the very first frame */
.scene.s1{opacity:1;animation:nxOut .01s linear var(--t1) forwards,sv calc(var(--t1) - var(--t0) + .02s) linear var(--t0)}
.clip{position:absolute;inset:0;overflow:hidden;background:#D4DBE3}
.cam{position:absolute;inset:0}
.dof,.vig{position:absolute;inset:0}

/* ---- the stopwatch, in dial units (--u) ---- */
.watch{position:absolute;width:calc(var(--u)*1000);height:calc(var(--u)*1000)}
.watch>*{position:absolute}
.bz{inset:0;border-radius:50%;
  background:conic-gradient(from 318deg,#E6EBF1 0deg,#D3DAE2 28deg,#9FACBB 74deg,#D0D8E0 118deg,#7E8C9D 168deg,#C3CCD7 214deg,#8D9AAA 262deg,#D6DDE5 318deg,#E6EBF1 360deg);
  box-shadow:inset 0 0 0 calc(var(--u)*1.6) rgba(255,255,255,.6),inset 0 0 0 calc(var(--u)*3.4) rgba(60,80,110,.16)}
.wall{inset:calc(var(--u)*58);border-radius:50%;background:linear-gradient(150deg,#465466 0%,#7D8B9D 45%,#D5DCE4 100%);
  box-shadow:0 0 0 calc(var(--u)*1.2) rgba(255,255,255,.45)}
.face{inset:calc(var(--u)*71);border-radius:50%;background:radial-gradient(circle at 36% 28%,#C2E0F9 0%,#ABD3F5 46%,#95C5EF 100%);
  box-shadow:inset calc(var(--u)*7) calc(var(--u)*12) calc(var(--u)*18) rgba(8,34,78,.40),inset 0 0 0 calc(var(--u)*1) rgba(20,40,70,.35)}
.watch .print{inset:0;width:100%;height:100%}
.glass{inset:calc(var(--u)*71);border-radius:50%;
  background:linear-gradient(128deg,rgba(255,255,255,.30) 0%,rgba(255,255,255,.07) 22%,rgba(255,255,255,0) 38%);mix-blend-mode:screen}

/* the hand: an anchor on the hub, the blade turns inside it */
.hd,.hub{position:absolute;width:0;height:0}
.hd .rot{position:absolute;left:0;top:0;width:0;height:0}
.ndl{position:absolute;left:calc(var(--u)*-40);top:calc(var(--u)*-340);width:calc(var(--u)*80);height:calc(var(--u)*480)}
.hd.sh{transform:translate(calc(var(--u)*4),calc(var(--u)*7));filter:blur(calc(var(--u)*1.8));opacity:.34}
.hub:before{content:"";position:absolute;left:calc(var(--u)*-24);top:calc(var(--u)*-24);width:calc(var(--u)*48);height:calc(var(--u)*48);border-radius:50%;
  background:radial-gradient(circle at 36% 30%,#40609A 0%,#122A52 48%,#051328 100%);
  box-shadow:calc(var(--u)*3) calc(var(--u)*6) calc(var(--u)*8) rgba(8,26,54,.45),inset 0 0 0 calc(var(--u)*1) rgba(255,255,255,.2),
   inset calc(var(--u)*-2) calc(var(--u)*-3) calc(var(--u)*5) rgba(0,0,0,.35)}
.hub:after{content:"";position:absolute;left:calc(var(--u)*-7);top:calc(var(--u)*-7);width:calc(var(--u)*14);height:calc(var(--u)*14);border-radius:50%;
  background:radial-gradient(circle at 36% 30%,#FFFFFF 0%,#C4CEDA 55%,#7C8A9C 100%);box-shadow:0 calc(var(--u)*1) calc(var(--u)*1.5) rgba(0,0,0,.4)}

/* type */
.d{font-family:Grotesk;font-weight:700;letter-spacing:-.045em;line-height:.9}
.t{font:500 52px/1.24 Geist;letter-spacing:-.02em}
.t b{font-weight:700;display:block}
.t span{display:block;opacity:.72}

/* ---- 1. the question, with the hand waiting on zero; then it goes ---- */
.s1 .cam{transform-origin:830px 490px;animation:push 3.4s linear var(--t0) both}
@keyframes push{from{transform:scale(1)}to{transform:scale(1.03)}}
.s1 h1{position:absolute;left:55px;top:1058px;font-size:170px;line-height:.94;white-space:nowrap}
.s1 h1 span{display:block}
.s1 .rot{animation:set1 .7s cubic-bezier(.3,1.5,.5,1) var(--t0) both,run1 .5s linear calc(var(--t0) + 2.9s) forwards}
@keyframes set1{from{transform:rotate(7deg)}to{transform:rotate(0deg)}}
@keyframes run1{from{transform:rotate(0deg)}to{transform:rotate(36deg)}}

/* ---- 2. right up against 2.5 ---- */
.s2 .rot{animation:run2 .42s linear var(--t0) both}
@keyframes run2{0%{transform:rotate(165.6deg)}47.6%{transform:rotate(180deg)}68%{transform:rotate(180.4deg)}100%{transform:rotate(180deg)}}
.s2 .n{position:absolute;left:345px;top:232px;font-size:250px}
.s2 .t{position:absolute;left:354px;top:486px}

/* ---- 3. up at 4.0 ---- */
.s3 .rot{animation:run3 1.54s linear var(--t0) both}
@keyframes run3{0%{transform:rotate(180deg)}97.4%{transform:rotate(288deg)}98.8%{transform:rotate(288.4deg)}100%{transform:rotate(288deg)}}
.s3 .n{position:absolute;left:616px;top:770px;font-size:180px;color:var(--red)}
.s3 .t{position:absolute;left:628px;top:964px}

/* ---- 4. back to zero: time yours ---- */
.s4 .rot{animation:run4 .62s cubic-bezier(.3,1.45,.5,1) calc(var(--t0) + .4s) both}
@keyframes run4{from{transform:rotate(288deg)}to{transform:rotate(360deg)}}
.s4 h2{position:absolute;left:231px;top:966px;font-size:196px;white-space:nowrap}
.s4 h2 span{display:block}
.s4 .url{position:absolute;left:231px;top:1398px;font:500 62px/1 Grotesk;letter-spacing:-.035em;white-space:nowrap;display:flex;align-items:center}
.s4 .url i{font-style:normal;opacity:0;animation:nxIn .01s linear calc(var(--t0) + var(--k)) both}
"""


def url_letters(s, start=1.5, step=0.066):
    return "".join(f'<i style="--k:{start + i * step:.3f}s">{c}</i>' for i, c in enumerate(s))


def build():
    # 1: the head of the dial. The hand stands on zero down the right; the question sits low on the left.
    u1, hx1, hy1 = 4.2, 830, 1868
    s1 = ('<section class="scene s1" data-dur="3.4">' + shot(hx1, hy1, u1, (700, 830, 680, 1500))
          + '<h1 class="d" data-bleed><span style="margin-left:-2px">How fast</span><span style="margin-left:1px">is your</span><span style="margin-left:3px">website?</span></h1>'
          + '</section>')
    # 2: the foot of the dial. The hand comes down the left and stops on 2.5; the verdict sits high on the right.
    u2, hx2 = 4.8, 270
    hy2 = 1090 - 288 * u2
    s2 = ('<section class="scene s2" data-dur="4.4">' + shot(hx2, hy2, u2, (hx2 + 60, hy2 + 328 * u2, 460, 1500))
          + '<div class="d n up" style="--d:.42s" data-bleed>Good.</div>'
          + '<p class="t up" style="--d:.58s"><b>Main content on screen<br>by 2.5 seconds.</b><span>That’s Google’s line.</span></p>'
          + '</section>')
    # 3: the shoulder of the dial, where the flange turns red. The hand comes across from the right.
    u3, hx3, hy3 = 3.9, 1620, 880
    s3 = ('<section class="scene s3" data-dur="4.4">' + shot(hx3, hy3, u3, (hx3 - .951 * 328 * u3, hy3 - .309 * 328 * u3, 430, 1500))
          + '<div class="d n up" style="--d:1.62s" data-bleed>Poor.</div>'
          + '<p class="t up" style="--d:1.78s"><b>Anything past<br>4 seconds.</b><span>Google again.</span></p>'
          + '</section>')
    # 4: pulled back to the hub. The hand flies back to zero; the order and the address sit inside the ring.
    u4, hx4, hy4 = 2.9, 904, 1340
    s4 = ('<section class="scene s4" data-dur="4.2">' + shot(hx4, hy4, u4, (600, 930, 720, 1500))
          + '<h2 class="d" data-bleed><span class="up" style="--d:.95s">Time</span><span class="up" style="--d:1.05s;margin-left:-8px">yours.</span></h2>'
          + '<div class="url" data-ui>' + url_letters("pagespeed.web.dev") + '</div>'
          + '</section>')
    html = f"<style>{CSS}</style>\n" + "\n".join([s1, s2, s3, s4]) + "\n<!--grain:0.08-->\n"
    Path(__file__).with_name("reel.html").write_text(html)


if __name__ == "__main__":
    build()
