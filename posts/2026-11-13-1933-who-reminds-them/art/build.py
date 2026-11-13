#!/usr/bin/env python3
"""Writes art/reel.html for this post. One tear-off wall calendar, drawn once and shot four ways.
Run: python3 art/build.py   (art/paper.png and art/stamp-mask.png are the paper and ink textures)

Pad units (--u px each): a page is 600 x 780, the header card above it is 120 high, and the pad stands
36 off the wall. The front of the pad is at translateZ(36u); the wall is z = 0. Light comes from the top left.
Everything printed on a page hangs off one left margin, 64 units in.
"""
import datetime
from pathlib import Path

MONTH = {11: "November", 12: "December"}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NUM_BEAR = {"1": 7.5, "2": 22, "3": 22, "4": 7.5, "5": 22}          # left side bearing of each first digit at 470 units, DM Serif
CAP_BEAR = {"N": 1.9, "D": 1.9, "F": 1.9, "M": 1.9, "T": .5, "S": .5, "W": .5}


def weekday(m, d):
    return DAYS[datetime.date(2026, m, d).weekday()]


def curl_path(side, lift=30, span=50, n=16):
    """clip-path for a page whose lower corner (side 'r' or 'l') stands `lift` units off the pad."""
    pts = ["0 0", "100% 0"]
    edge = []
    for i in range(n + 1):
        t = i / n
        x = 100 - t * span if side == "r" else t * span
        y = lift * (1 - t) ** 2.4
        edge.append(f"{x:.2f}% calc(100% - var(--u)*{y:.2f})")
    if side == "r":
        pts += edge + ["0 100%"]
    else:
        pts += ["100% 100%"] + list(reversed(edge))
    return "polygon(" + ",".join(pts) + ")"


def sheet(m, d, cls="", extra="", style="", curl="", under=""):
    """One page of the pad: month, the big date, the day. `extra` is printed under a rule, lower down.
    curl='r'|'l' lifts that lower corner; under='r'|'l' puts the lifted corner's shadow on the page beneath."""
    rule = '<div class="rule"></div>' if extra else ""
    if curl:
        cls += f" c{curl}"
        extra += f'<div class="curl {curl}"></div>'
    if under:
        extra += f'<div class="ush {under}"></div>'
    k = -0.02 if d > 9 else 0
    wd = weekday(m, d)
    return (f'<div class="sheet {cls}" style="{style}"><div class="perf"></div>'
            f'<div class="mo" data-ui style="left:calc(var(--u)*{64 - CAP_BEAR[MONTH[m][0]]})">{MONTH[m]}</div>'
            f'<div class="num" data-ui style="letter-spacing:{k}em;left:calc(var(--u)*{64 - NUM_BEAR[str(d)[0]]})">{d}</div>'
            f'<div class="wd" data-ui style="left:calc(var(--u)*{64 - CAP_BEAR[wd[0]]})">{wd}</div>'
            f'{rule}{extra}<div class="lit"></div><div class="next"></div><div class="shade"></div></div>')


def pad(x, y, u, cam, sheets, cls=""):
    """The pad at frame position x,y (its top left corner on the wall), u px to a unit, turned by `cam`."""
    return (f'<div class="pad {cls}" style="left:{x}px;top:{y}px;--u:{u}px;transform:{cam}" data-bleed>'
            '<div class="cast"></div><div class="side l"></div><div class="side r"></div>'
            '<div class="side b"></div><div class="side t"></div>'
            + sheets + '<div class="bind"></div></div>')


def focus(fx, fy, r0, r1, px=6):
    m = f'radial-gradient(circle at {fx}px {fy}px,transparent {r0}px,#000 {r1}px)'
    return (f'<div class="dof" style="backdrop-filter:blur({px}px);-webkit-mask-image:{m};mask-image:{m}"></div>'
            f'<div class="vig" style="background:radial-gradient(circle at {fx}px {fy}px,rgba(20,8,4,0) {r0 + 80}px,rgba(20,8,4,.42) {r1 + 520}px)"></div>')


CSS = """
.scene{--ink:#24130C;--paper:#F4ECDD;--pink:#FF8CB2;--cream:#F7EFE0;overflow:hidden;visibility:hidden;color:var(--cream);
  animation:nxIn .01s linear var(--t0) both,nxOut .01s linear var(--t1) forwards,sv calc(var(--t1) - var(--t0) + .02s) linear var(--t0)}
@keyframes sv{0%,100%{visibility:visible}}
.scene.s1{opacity:1;animation:nxOut .01s linear var(--t1) forwards,sv calc(var(--t1) - var(--t0) + .02s) linear var(--t0)}
.wall{position:absolute;inset:0;background:
  radial-gradient(1700px 2000px at var(--lx,12%) var(--ly,6%),#7A4530 0%,#643624 34%,#4E2A1B 68%,#3C1F14 100%)}
.stage{position:absolute;inset:0;perspective:2600px;perspective-origin:var(--px,50%) var(--py,50%)}
.dof,.vig{position:absolute;inset:0}

/* ---- the pad ---- */
.pad{position:absolute;transform-style:preserve-3d;width:calc(var(--u)*600);height:calc(var(--u)*900);transform-origin:50% 50%}
.pad>*{position:absolute}
.cast{inset:0;background:rgba(20,8,4,.7);border-radius:calc(var(--u)*3);
  box-shadow:calc(var(--u)*10) calc(var(--u)*14) calc(var(--u)*18) rgba(20,8,4,.7),calc(var(--u)*64) calc(var(--u)*92) calc(var(--u)*84) calc(var(--u)*8) rgba(20,8,4,.5)}
/* the edges of the stack: one line to a few pages */
.side{background:repeating-linear-gradient(90deg,#F1E8D7 0,#F1E8D7 calc(var(--u)*3),#CFC1A8 calc(var(--u)*4.4),#F1E8D7 calc(var(--u)*5.2))}
.side.l,.side.r{top:0;width:calc(var(--u)*36);height:100%;transform-origin:left center;transform:rotateY(-90deg)}
.side.l{left:0}.side.r{left:100%}
.side.l:before,.side.r:before{content:"";position:absolute;left:0;right:0;top:0;height:calc(var(--u)*120);background:linear-gradient(90deg,#3A302B,#15100D)}
.side.r:after{content:"";position:absolute;inset:0;background:rgba(58,30,16,.46)}
.side.b,.side.t{left:0;width:100%;height:calc(var(--u)*36);transform-origin:center top;transform:rotateX(90deg);
  background:linear-gradient(0deg,#E3D8C2 0%,#D2C5AC 30%,#E0D4BD 46%,#CDBFA5 72%,#DACDB5 100%)}
.side.b{top:100%}
.side.t{top:0;background:linear-gradient(#5A4E47,#2A2320)}

.sheet{left:0;top:calc(var(--u)*120);width:100%;height:calc(var(--u)*780);transform:translateZ(calc(var(--u)*36));transform-origin:50% 0;
  background:linear-gradient(168deg,#FBF5E9 0%,#F4ECDD 42%,#E9DFCC 100%);color:var(--ink);backface-visibility:hidden}
.sheet.pink{background:linear-gradient(168deg,#FFA3C2 0%,#FF8CB2 45%,#F47AA2 100%)}
.perf{position:absolute;left:0;right:0;top:calc(var(--u)*13);height:calc(var(--u)*5);
  background:radial-gradient(circle at 50% 50%,rgba(60,34,20,.55) calc(var(--u)*1.25),transparent calc(var(--u)*1.7)) 0 0/calc(var(--u)*9) 100%}
.mo,.wd{position:absolute;font:700 calc(var(--u)*30)/1 Outfit;letter-spacing:.3em;text-transform:uppercase;white-space:nowrap}
.mo{top:calc(var(--u)*62)}
.wd{top:calc(var(--u)*566)}
.num{position:absolute;top:calc(var(--u)*86);font:400 calc(var(--u)*470)/1 DMSerif;white-space:nowrap}
.pink .rule{right:calc(var(--u)*96)}
.rule{position:absolute;left:calc(var(--u)*64);right:calc(var(--u)*64);top:calc(var(--u)*628);height:calc(var(--u)*1.6);background:var(--ink);opacity:.5}
.note{position:absolute;left:calc(var(--u)*62);top:calc(var(--u)*654);font:500 calc(var(--u)*33)/1.22 Outfit;letter-spacing:.004em;word-spacing:.05em;white-space:nowrap}
.note.big{top:calc(var(--u)*650);font-size:calc(var(--u)*38);line-height:1.2}
/* paper: light from the upper left, the shadow of the header card along the top, fibre and mottling */
.lit{position:absolute;inset:0;background:
  linear-gradient(to bottom,rgba(40,18,8,.30) 0,rgba(40,18,8,0) calc(var(--u)*16)),
  linear-gradient(100deg,rgba(255,255,255,.20) 0%,rgba(255,255,255,0) 34%,rgba(60,30,14,0) 70%,rgba(60,30,14,.14) 100%)}
.lit:after{content:"";position:absolute;inset:0;background:url({{post}}/art/paper.png) 0 0/100% 100%;mix-blend-mode:multiply}
/* the foot of the page stands a little off the pad: its shadow, then the next three pages showing under it */
.next{position:absolute;left:0;right:0;bottom:0;height:calc(var(--u)*9);background:linear-gradient(to bottom,
  #8E7B66 0,#C9BBA2 calc(var(--u)*.9),#F2E9D8 calc(var(--u)*1.6),#F2E9D8 calc(var(--u)*3.6),
  #A8987F calc(var(--u)*3.6),#E9DFCC calc(var(--u)*4.4),#E9DFCC calc(var(--u)*6.2),
  #A8987F calc(var(--u)*6.2),#DED3BD calc(var(--u)*7),#DED3BD 100%)}
.next:before{content:"";position:absolute;left:0;right:0;bottom:100%;height:calc(var(--u)*46);
  background:linear-gradient(to bottom,rgba(255,255,255,0) 0,rgba(255,255,255,.16) 55%,rgba(60,28,10,.10) 100%)}
.shade{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(40,16,6,.0),rgba(40,16,6,.55));opacity:0}
/* a resting page lifts at one lower corner: the corner is cut on a long shallow curve and the page under it shows there */
.sheet.cr{border-bottom-right-radius:54% calc(var(--u)*30);overflow:hidden}
.sheet.cl{border-bottom-left-radius:54% calc(var(--u)*30);overflow:hidden}
/* the lifted corner catches the light, then turns away from it at the very edge */
.curl{position:absolute;bottom:0;width:52%;height:calc(var(--u)*150)}
.curl.r{right:0;background:linear-gradient(to bottom right,rgba(255,255,255,0) 52%,rgba(255,255,255,.34) 76%,rgba(255,255,255,.10) 90%,rgba(70,34,14,.22) 100%)}
.curl.l{left:0;background:linear-gradient(to bottom left,rgba(255,255,255,0) 52%,rgba(255,255,255,.34) 76%,rgba(255,255,255,.10) 90%,rgba(70,34,14,.22) 100%)}
.ush{position:absolute;bottom:0;width:56%;height:calc(var(--u)*70)}
.ush.r{right:0;background:radial-gradient(ellipse at 100% 100%,rgba(40,14,4,.62) 0%,rgba(40,14,4,.34) 38%,rgba(40,14,4,0) 72%)}
.ush.l{left:0;background:radial-gradient(ellipse at 0% 100%,rgba(40,14,4,.62) 0%,rgba(40,14,4,.34) 38%,rgba(40,14,4,0) 72%)}
.bind{left:calc(var(--u)*-5);top:0;width:calc(var(--u)*610);height:calc(var(--u)*126);transform:translateZ(calc(var(--u)*41));border-radius:calc(var(--u)*3);
  background:linear-gradient(to bottom,#4A3F39 0,#2E2622 5%,#1D1714 28%,#14100D 80%,#231D19 100%);display:flex;align-items:center;padding-left:calc(var(--u)*69);
  box-shadow:0 calc(var(--u)*5) calc(var(--u)*7) rgba(30,12,4,.55),inset 0 calc(var(--u)*1.2) 0 rgba(255,255,255,.22)}
.bind .nx-logo{height:calc(var(--u)*46)}
.hang{left:calc(var(--u)*274);top:calc(var(--u)*-40);width:calc(var(--u)*52);height:calc(var(--u)*60);transform:translateZ(calc(var(--u)*36));border-radius:calc(var(--u)*26) calc(var(--u)*26) 0 0;
  background:linear-gradient(120deg,#D9D2C8,#8F867C 60%,#6B625A);box-shadow:calc(var(--u)*5) calc(var(--u)*8) calc(var(--u)*8) rgba(20,8,4,.5)}
.hang:before{content:"";position:absolute;left:calc(var(--u)*15);top:calc(var(--u)*12);width:calc(var(--u)*22);height:calc(var(--u)*22);border-radius:50%;
  background:radial-gradient(circle at 38% 32%,#FFFFFF 0%,#C9C1B6 40%,#4F463F 100%);box-shadow:calc(var(--u)*2) calc(var(--u)*3) calc(var(--u)*3) rgba(0,0,0,.5)}

/* a page comes away: it lifts off the pad at the foot, then falls past the camera, blurred by its own speed */
.tear{animation:tear var(--td,.9s) linear calc(var(--t0) + var(--k,0s)) both}
.tear .shade{animation:shd var(--td,.9s) linear calc(var(--t0) + var(--k,0s)) both}
@keyframes tear{
  0%{transform:translateZ(calc(var(--u)*36.6)) rotateX(0deg);filter:blur(0px);animation-timing-function:cubic-bezier(.3,0,.4,1)}
  38%{transform:translateZ(calc(var(--u)*36.6)) rotateX(24deg);filter:blur(0px);animation-timing-function:cubic-bezier(.5,0,.9,.5)}
  99%{opacity:1;visibility:visible}
  100%{transform:translateZ(calc(var(--u)*190)) translateY(calc(var(--u)*1500)) rotateX(58deg) rotateZ(var(--rz,-8deg));filter:blur(calc(var(--u)*5));opacity:0;visibility:hidden}}
@keyframes shd{0%{opacity:0}38%{opacity:.32}100%{opacity:.5}}

/* type on the wall */
.d{font-family:DMSerif;font-weight:400;letter-spacing:-.012em;line-height:.98}
.d span{display:block}
.t{font:500 46px/1.25 Outfit;letter-spacing:-.005em}
"""

SCENES_CSS = """
/* 1: from the right. The pad hangs top left and its shadow falls across the wall; the question sits under it. */
.s1{--lx:6%;--ly:0%;--px:78%;--py:38%}
.s1 .stage{animation:push1 3.9s linear var(--t0) both;transform-origin:40% 40%}
@keyframes push1{from{transform:scale(1)}to{transform:scale(1.03)}}
.s1 h1{position:absolute;left:64px;top:1276px;font-size:116px}
/* 2: the pink page, from below and to the right, right up against it. */
.s3{--lx:14%;--ly:4%;--px:66%;--py:84%}
.s3 .stage{animation:push3 5.8s linear var(--t0) both;transform-origin:50% 60%}
@keyframes push3{from{transform:scale(1)}to{transform:scale(1.025)}}
.stamp{position:absolute;left:calc(var(--u)*322);top:calc(var(--u)*300);width:calc(var(--u)*192);height:calc(var(--u)*192);border-radius:50%;
  border:calc(var(--u)*5.5) solid var(--ink);color:var(--ink);mix-blend-mode:multiply;opacity:0;
  -webkit-mask-image:url(STAMPMASK);mask-image:url(STAMPMASK);-webkit-mask-size:100% 100%;mask-size:100% 100%;
  animation:thump .3s cubic-bezier(.2,1.6,.4,1) calc(var(--t0) + 2.75s) both}
.stamp .in{position:absolute;inset:calc(var(--u)*6);border-radius:50%;border:calc(var(--u)*1.8) solid var(--ink);overflow:hidden;
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-transform:uppercase;white-space:nowrap}
.stamp span{font:700 calc(var(--u)*18)/1 Outfit;letter-spacing:.14em;margin-right:-.14em}
.stamp b{font:700 calc(var(--u)*49)/1 Outfit;letter-spacing:.04em;margin:calc(var(--u)*9) 0;padding:calc(var(--u)*8) 0 calc(var(--u)*6);width:100%;text-align:center;
  border-top:calc(var(--u)*2.6) solid var(--ink);border-bottom:calc(var(--u)*2.6) solid var(--ink)}
@keyframes thump{0%{opacity:0;transform:rotate(-11deg) scale(2)}55%{opacity:.95}100%{opacity:.93;transform:rotate(-11deg) scale(1)}}
/* 3: the opener's answer. The same pad from the other side on the day itself; the payoff sits under it, with the wordmark. */
.s4{--lx:6%;--ly:0%;--px:22%;--py:4%}
.s4 .stage{animation:push4 4.6s linear var(--t0) both;transform-origin:60% 40%}
@keyframes push4{from{transform:scale(1)}to{transform:scale(1.03)}}
.s4 h2{position:absolute;left:64px;top:1276px;font-size:116px}
.s4 .mark{position:absolute;right:64px;top:1446px}
.s4 .mark .nx-logo{height:38px}
"""

DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>'
        '<filter id="mb1" x="-4%" y="-12%" width="108%" height="124%"><feGaussianBlur stdDeviation="0 7"/></filter>'
        '<filter id="mb2" x="-4%" y="-20%" width="108%" height="140%"><feGaussianBlur stdDeviation="0 16"/></filter>'
        '</defs></svg>')


def build():
    # 1: from the right. The pad runs off the top; the question sits under it on the wall.
    s1 = ('<section class="scene s1" data-dur="3.9"><div class="wall"></div><div class="stage">'
          + pad(34, -240, 1.52, "rotateY(-26deg) rotateX(-2deg) rotateZ(-.5deg)",
                sheet(11, 14, under="r") + sheet(11, 13, "tear", '<div class="note">Booked in for 4 December.</div>', "--k:3.56s;--td:.8s", curl="r"))
          + '</div>' + focus(420, 560, 760, 1500, 4)
          + '<h1 class="d"><span>Who reminds</span><span>your customers?</span></h1></section>')

    # 2: right up against the pad, from below and to the right. Nineteen pages come away, one after another,
    # and stop on the pink one. Then the stamp lands.
    seq = [(11, d) for d in range(14, 31)] + [(12, 1), (12, 2)]
    pages = sheet(12, 4) + sheet(12, 3, "pink", '<div class="note big">The day before,<br>a text goes out.</div>'
                                 '<div class="stamp"><div class="in"><span>Reminder</span><b>Sent</b><span>09:00</span></div></div>')
    step, first = 0.08, 0.15
    for i, (m, d) in reversed(list(enumerate(seq))):
        pages += sheet(m, d, "tear", "", f"--k:{first + i * step:.3f}s;--td:.5s;--rz:{(-9, 7, -5, 10, -7)[i % 5]}deg")
    s2 = ('<section class="scene s3" data-dur="5.8"><div class="wall"></div><div class="stage">'
          + pad(-24, -490, 2.0, "rotateX(8deg) rotateY(-12deg) rotateZ(-1deg)", pages)
          + '</div></section>')

    # 3: the day itself, from the left. The pink page comes away, then the payoff.
    s4 = ('<section class="scene s4" data-dur="4.6"><div class="wall"></div><div class="stage">'
          + pad(150, -176, 1.42, "rotateY(26deg) rotateX(-2deg) rotateZ(.3deg)",
                sheet(12, 5, under="l") + sheet(12, 4, "", '<div class="note">Let your bookings<br>send the reminder.</div>', "", curl="l")
                + sheet(12, 3, "pink tear", "", "--k:.1s;--td:.8s;--rz:7deg"))
          + '</div>' + focus(660, 560, 760, 1500, 4)
          + '<h2 class="d"><span class="up" style="--d:.75s">Nobody had</span><span class="up" style="--d:.87s">to remember.</span></h2>'
          + '<div class="mark up" style="--d:1.2s" data-ui><!--logo:#F7EFE0,#FF8CB2--></div></section>')

    import base64
    mask = "data:image/png;base64," + base64.b64encode(Path(__file__).with_name("stamp-mask.png").read_bytes()).decode()
    html = f"<style>{CSS}{SCENES_CSS.replace('STAMPMASK', mask)}</style>\n" + DEFS + "\n" + "\n".join([s1, s2, s4]) + "\n<!--grain:0.09-->\n"
    Path(__file__).with_name("reel.html").write_text(html)


if __name__ == "__main__":
    build()
