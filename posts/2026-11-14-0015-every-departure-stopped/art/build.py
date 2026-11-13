#!/usr/bin/env python3
"""Writes art/slide-01..03.html. One split-flap departures board, seen at three distances.
Run: python3 art/build.py"""
from pathlib import Path

HERE = Path(__file__).parent

CSS = """
.frame{background:#0B0C0E}
.wall{position:absolute;inset:0;background:radial-gradient(1200px 900px at 30% 0%,#1B1D21 0%,#101114 55%,#0A0B0D 100%)}
/* one flap: two leaves hinged on a dark axle, lit from above */
.board{position:absolute;display:grid;gap:var(--g);grid-template-columns:repeat(var(--n),var(--w))}
.f{position:relative;width:var(--w);height:calc(var(--w)*1.42);border-radius:calc(var(--w)*.07);overflow:hidden;
  background:linear-gradient(to bottom,#2A2D32 0%,#202328 49.2%,#060607 49.2%,#060607 50.8%,#17191D 50.8%,#101215 100%);
  box-shadow:0 calc(var(--w)*.04) calc(var(--w)*.09) rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.10);
  font:600 calc(var(--w)*1.04)/calc(var(--w)*1.42) Oswald;text-align:center;color:#F1EFE6}
.f b{position:absolute;left:0;right:0;top:calc(var(--w)*-.035);height:100%;font-weight:600}
.f:before{content:"";position:absolute;inset:0;z-index:2;background:
  linear-gradient(to bottom,rgba(255,255,255,.06) 0%,rgba(255,255,255,0) 30%,rgba(0,0,0,0) 49%,#050506 49.2%,#050506 50.8%,rgba(0,0,0,.2) 50.9%,rgba(0,0,0,0) 62%)}
.f:after{content:"";position:absolute;left:0;right:0;top:calc(50% - var(--w)*.05);height:calc(var(--w)*.10);z-index:3;background:
  linear-gradient(90deg,#3A3D43 0,#3A3D43 calc(var(--w)*.045),transparent calc(var(--w)*.045),transparent calc(100% - var(--w)*.045),#3A3D43 calc(100% - var(--w)*.045))}
.f.y{color:#FFE14A}
.f.dim{color:#F1EFE6}
/* a leaf caught falling: the upper leaf of the next letter, seen edge on */
.f.fall .leaf{position:absolute;left:0;right:0;top:calc(var(--w)*.31);height:calc(var(--w)*.40);z-index:4;overflow:hidden;border-radius:calc(var(--w)*.05) calc(var(--w)*.05) 0 0;
  background:linear-gradient(to bottom,#3B3F45,#2A2D32);box-shadow:0 calc(var(--w)*.05) calc(var(--w)*.08) rgba(0,0,0,.65)}
.small{font:500 38px/1.3 Geist;letter-spacing:-.006em;color:#E9E7DE}
.small em{font-style:normal;color:#9A9B9F}
.src{font:500 26px/1.3 GeistMono;letter-spacing:.02em;color:#A2A4A9;text-transform:uppercase}
"""


def board(rows, n, w, g, x, y, yellow=(), fall=()):
    """rows: list of strings (padded to n). yellow: row indexes set in yellow. fall: (row, col) leaves mid-fall."""
    cells = []
    for r, text in enumerate(rows):
        text = text.ljust(n)[:n]
        for c, ch in enumerate(text):
            cls = "f" + (" y" if r in yellow else "") + (" fall" if (r, c) in fall else "")
            leaf = '<i class="leaf"></i>' if (r, c) in fall else ""
            cells.append(f'<div class="{cls}"><b>{ch if ch != " " else ""}</b>{leaf}</div>')
    return (f'<div class="board" data-ui style="--n:{n};--w:{w}px;--g:{g}px;left:{x}px;top:{y}px">' + "".join(cells) + "</div>")


def write(name, body, extra=""):
    (HERE / name).write_text(f"<style>{CSS}{extra}</style>\n<div class=\"wall\"></div>\n{body}\n<!--grain:0.06-->\n")


def build():
    M = 58                                    # one side margin for the type and for the board in frames 1 and 3
    # 1. The whole board, ten letters wide, cut to the margins.
    n, g = 10, 6
    w = (1080 - 2 * M - (n - 1) * g) / n
    rows = ["", "EVERY", "DEPARTURE", "IN AMERICA", "STOPPED."]
    write("slide-01.html",
          '<div class="hd"><span>Departures</span><span>Fri 13 Nov 2026</span></div>'
          + board(rows, n, w, g, M, 152, yellow=(4,))
          + '<p class="small s1">On Friday 13 November the FAA ordered every<br>departing flight in the US to stay on the ground.</p>'
          + '<p class="src s1b">As reported by AP, Reuters and CBS News</p>',
          """
.hd{position:absolute;left:58px;right:58px;top:74px;display:flex;justify-content:space-between;font:500 30px/1 GeistMono;letter-spacing:.14em;text-transform:uppercase;color:#A2A4A9}
.s1{position:absolute;left:58px;top:960px;margin:0}
.s1b{position:absolute;left:58px;bottom:76px;margin:0}
""")

    # 2. Closer: the board runs off both sides by the same amount; six whole letters across.
    n, w, g = 8, 150, 8
    x = (1080 - (n * w + (n - 1) * g)) // 2
    rows = [" THE", " COMMS", " FAILED"]
    write("slide-02.html",
          board(rows, n, w, g, x, 96, yellow=(1,))
          + '<p class="small s2">The US transport secretary called it<br>“a communication issue” at all of America’s<br>air route traffic control centres.<br><em>He said FAA technicians were investigating.</em></p>'
          + '<p class="src s2b">As reported by CBS News and Yahoo News</p>',
          """
.s2{position:absolute;left:58px;top:838px;margin:0}
.s2b{position:absolute;left:58px;bottom:76px;margin:0}
""")

    # 3. The question, and what to do tonight.
    n, g = 8, 7
    w = (1080 - 2 * M - (n - 1) * g) / n
    rows = ["IS YOUR", "OWN LINE", "OPEN?"]
    write("slide-03.html",
          '<p class="small s3">The comms failed and every departure stopped.<br><em>When a contact form fails, nothing stops.<br>The enquiry just never arrives.</em></p>'
          + board(rows, n, w, g, M, 372, yellow=(2,))
          + '<p class="small s3b"><b>Send your own website an enquiry tonight.</b><br><em>See if it reaches you.</em></p>'
          + '<div class="mark" data-ui><!--logo:#F1EFE6,#FFE14A--></div>',
          """
.s3{position:absolute;left:58px;top:92px;margin:0;font-size:40px;line-height:1.26;letter-spacing:-.01em}
.s3b{position:absolute;left:58px;top:990px;margin:0;font-size:40px}
.s3b b{font-weight:600}
.mark{position:absolute;right:58px;bottom:76px}
.mark .nx-logo{height:40px}
""")


if __name__ == "__main__":
    build()
