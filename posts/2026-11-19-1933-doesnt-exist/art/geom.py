"""The path the label ribbon stands along, for each frame, and where its labels sit (shared by print.py and build.py).
Units are centimetres. The ribbon and the knitwear maker on it (Thrumwick) are made up."""
import math

DS = 0.05
WID = 2.2          # the ribbon is 22 mm wide
PITCH = 7.6        # one label every 7.6 cm
R = 1.6            # radius of a fold


def run(pieces, start=(0.0, 0.0), heading=0.0):
    pts, hd = [start], [heading]
    x, y, th = start[0], start[1], heading
    for ln, k0, k1 in pieces:
        n = max(1, int(round(ln / DS)))
        for i in range(n):
            k = k0 + (k1 - k0) * (i + 0.5) / n
            th += k * DS * 0.5
            x += math.cos(th) * DS; y += math.sin(th) * DS
            th += k * DS * 0.5
            pts.append((x, y)); hd.append(th)
    return pts, hd


def spiral(pts, hd, length, r_in, pitch, lead_in=7.0):
    x, y = pts[-1]; th = hd[-1]
    r_out = math.sqrt(r_in ** 2 + pitch * length / math.pi)
    n = int(lead_in / DS)
    for i in range(n):
        t = (i + 1) / n; k = (1 / r_out) * (3 * t * t - 2 * t * t * t)
        th += k * DS * 0.5; x += math.cos(th) * DS; y += math.sin(th) * DS; th += k * DS * 0.5
        pts.append((x, y)); hd.append(th)
    r = r_out; s = 0.0
    while s < length and r > r_in * 0.98:
        k = 1 / r
        th += k * DS * 0.5; x += math.cos(th) * DS; y += math.sin(th) * DS; th += k * DS * 0.5
        r -= pitch / (2 * math.pi * r) * DS; s += DS
        pts.append((x, y)); hd.append(th)
    return pts, hd


def plen(pieces):
    return sum(round(p[0] / DS) * DS for p in pieces)


ROWS, LR, RP, LEAD1 = 8, 15.2, 0.5, 16.0


R2, LR2, ROWS2 = 1.9, 34.0, 3
TAILTEX = 26.0     # cm of the roll's ribbon that the print covers; past it the stripes carry on


def layout(scene):
    """Returns dict: pts, hd, period and u0 (the print repeats every `period` cm from tape position u0),
    labels and dots as (cm within the period, side); side 0 front (navy), 1 back (ivory)."""
    if scene in (1, 2):
        # rows there and back; every row carries the same print, so the print is one row long and repeats
        rows, lr, r, lead = (ROWS, LR, R, LEAD1) if scene == 1 else (ROWS2, LR2, R2, 6.0)
        k = 1 / r
        arc = (math.pi - k * RP) / k
        pieces = [(lead, 0, 0)]
        for i in range(rows):
            pieces.append((lr, 0, 0))
            if i < rows - 1:
                sg = 1 if i % 2 == 0 else -1
                pieces += [(RP, 0, sg * k), (arc, sg * k, sg * k), (RP, sg * k, 0)]
        pieces.append((lead, 0, 0))
        period = lr + plen([(RP, 0, k), (arc, k, k), (RP, k, 0)])
        if scene == 1:
            labels = [(lr / 2 - PITCH / 2, s) for s in (0, 1)] + [(lr / 2 + PITCH / 2, s) for s in (0, 1)]
            dots = [(lr / 2, 0), (lr / 2, 1)]
        else:
            labels = [(lr / 2, 0), (lr / 2, 1)]
            dots = []
        pts, hd = run(pieces, start=(lr / 2 + lead, (rows - 1) * r), heading=math.pi)
        return dict(pts=pts, hd=hd, period=period, u0=lead, labels=labels, dots=dots)
    if scene == 3:
        # the roll, with its tail drawn out to the left and cut
        tail = [(3.4, 0.0, 0.015), (4, 0.015, 0.09)]
        pts, hd = run(tail, start=(-7.0, -1.0), heading=math.radians(3))
        pts, hd = spiral(pts, hd, 150.0, 1.3, 0.34, lead_in=5.0)
        return dict(pts=pts, hd=hd, period=TAILTEX, u0=0.0, labels=[(1.3 + PITCH / 2, 0)], dots=[])
