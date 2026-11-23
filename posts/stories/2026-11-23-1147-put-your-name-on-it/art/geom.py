"""The shapes of the tapes, shared by print.py and build.py. Centimetres. A tape is a ribbon along a profile in the x-z plane."""
import math

R = 2.2                      # roll radius
PHI = math.radians(60)
R1 = R2 = 2.2


def tail_profile(flat, r=R, turns=1.0, step=0.0125, shrink=0.045):
    """Flat on the table from the cut end, up in an S to the top of a standing roll, then round it.
    Returns [(x, z, s)] and the roll centre."""
    d = (2 * r - (R1 + R2) * (1 - math.cos(PHI))) / math.sin(PHI)
    segs = [("line", flat), ("arc", R1, PHI), ("line", d), ("arc", R2, -PHI), ("roll", r, turns)]
    pts = []; x = z = th = s = 0.0
    centre = None
    for sg in segs:
        if sg[0] == "line":
            n = max(1, int(sg[1] / step))
            for i in range(n):
                pts.append((x, z, s)); x += math.cos(th) * sg[1] / n; z += math.sin(th) * sg[1] / n; s += sg[1] / n
        elif sg[0] == "arc":
            rad, ang = sg[1], sg[2]; L = rad * abs(ang); n = max(1, int(L / step))
            for i in range(n):
                pts.append((x, z, s)); th += ang / n; x += math.cos(th - ang / n / 2) * L / n; z += math.sin(th - ang / n / 2) * L / n; s += L / n
        else:
            rad, turns_ = sg[1], sg[2]
            centre = (x, z - rad)
            n = int(2 * math.pi * rad * turns_ / step)
            for i in range(n + 1):
                a = math.pi / 2 - 2 * math.pi * turns_ * i / n
                rr = rad - shrink * turns_ * i / n
                pts.append((centre[0] + rr * math.cos(a), centre[1] + rr * math.sin(a), s + 2 * math.pi * rad * turns_ * i / n))
    return pts, centre


def curl_profile(flat, rad, ang, step=0.0125):
    """Flat for `flat`, then lifting off the table on one radius."""
    pts = []; x = z = th = s = 0.0
    n = int(flat / step)
    for i in range(n):
        pts.append((x, z, s)); x += flat / n; s += flat / n
    L = rad * ang; n = int(L / step)
    for i in range(n + 1):
        pts.append((x, z, s)); th += ang / n; x += math.cos(th) * L / n; z += math.sin(th) * L / n; s += L / n
    return pts


NAME_FLAT = 8.2
NX_FLAT = 7.8
MAIL_LEN = 11.2
LENGTHS = dict(name=tail_profile(NAME_FLAT)[0][-1][2], hello=MAIL_LEN, nx=tail_profile(NX_FLAT, r=2.3)[0][-1][2], period=60.0, name_cut=NAME_FLAT)
