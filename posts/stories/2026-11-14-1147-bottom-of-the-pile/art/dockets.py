"""Prints the enquiry dockets as pictures for build.py to wrap on to the paper (python3 dockets.py).

Thirty-six dockets from one made-up week, Monday 9 November 09:05 to Friday 13 November 16:42, as a
till printer would print them: a header, the job, a number to ring back (07700 900xxx, Ofcom's
drama range) and the day and time in double-height figures at the foot. 20 px to the millimetre,
80 mm wide, with the tear bar's saw edge cut into the top and bottom (transparent).
"""
import json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
import studio

PX = 20   # pixels per millimetre
JOBS = ["NEW KITCHEN", "GARDEN ROOM", "LOFT CONVERSION", "BATHROOM REFIT", "FENCE REPAIR", "DRIVEWAY", "NEW BOILER",
        "REWIRE", "EXTENSION", "DECKING", "ROOF REPAIR", "FRONT DOOR", "PATIO", "WET ROOM", "GARAGE DOOR", "SASH WINDOWS",
        "FLAT ROOF", "PLASTERING", "UNDER-STAIRS", "GUTTERS"]
TIMES = ["MON 09:05", "MON 11:30", "MON 14:12", "MON 16:48", "TUE 08:51", "TUE 09:40", "TUE 10:17", "TUE 12:40", "TUE 14:03",
         "TUE 15:26", "TUE 17:02", "WED 09:33", "WED 10:21", "WED 11:08", "WED 13:55", "WED 15:02", "WED 16:19", "THU 08:44",
         "THU 10:02", "THU 11:20", "THU 12:16", "THU 13:37", "THU 14:45", "THU 15:50", "THU 17:15", "FRI 09:12", "FRI 09:58",
         "FRI 10:46", "FRI 11:58", "FRI 12:33", "FRI 13:21", "FRI 14:34", "FRI 15:07", "FRI 15:49", "FRI 16:10", "FRI 16:42"]
DATES = {"MON": "9 NOV 2026", "TUE": "10 NOV 2026", "WED": "11 NOV 2026", "THU": "12 NOV 2026", "FRI": "13 NOV 2026"}


def html(i, t, job, phone, long):
    day = t[:3]
    extra = "<p class='l'>MESSAGE</p><p class='m'>PLEASE RING<br>WITH A PRICE</p><hr>" if long else ""
    return f"""<div class="d" id="d{i}"><div class="in">
<p class="no">No. {412 + i:04d}</p>
<p class="h">ENQUIRY</p><hr>
<p class="l">JOB</p><p class="m">{job}</p>
<p class="l">RING BACK</p><p class="m">{phone}</p><hr>
{extra}<p class="l">CAME IN</p>
<p class="t">{t}</p>
<p class="dt">{DATES[day]}</p>
</div></div>"""


CSS = f"""
html,body{{background:transparent!important;margin:0}}
.d{{width:{80 * PX}px;margin:0 0 40px;background:#FBFAF5;color:#17171d;
  --s:{2 * PX}px;
  clip-path:polygon(SAW)}}
.in{{padding:{11 * PX}px {7 * PX}px {12 * PX}px}}
p{{font-family:GeistMono;font-weight:500;margin:0;white-space:nowrap}}
.no{{font-size:{3.3 * PX}px;text-align:right;opacity:.75}}
.h{{font-size:{8.6 * PX}px;letter-spacing:.2em;margin-right:-.2em;text-align:center;margin-top:{3 * PX}px;transform:scaleY(1.25);transform-origin:50% 100%}}
hr{{border:0;border-top:{0.45 * PX}px dashed #17171d;margin:{4.2 * PX}px 0;opacity:.8}}
.l{{font-size:{3.3 * PX}px;letter-spacing:.08em;opacity:.75;margin-top:{2.2 * PX}px}}
.m{{font-size:{6.1 * PX}px;line-height:1.2}}
.t{{font-size:{11.9 * PX}px;line-height:1;letter-spacing:-.02em;margin-top:{9.5 * PX}px;transform:scaleY(1.7);transform-origin:0 100%}}
.dt{{font-size:{4.2 * PX}px;margin-top:{2.6 * PX}px;opacity:.85}}
"""


def saw(n=40):
    pts = []
    for k in range(n + 1):
        pts.append(f"{k * 100 / n:.3f}% {'0' if k % 2 else str(0.8 * PX) + 'px'}")
    for k in range(n, -1, -1):
        pts.append(f"{k * 100 / n:.3f}% {'100%' if k % 2 else 'calc(100% - ' + str(0.8 * PX) + 'px)'}")
    return ",".join(pts)


def main():
    from playwright.sync_api import sync_playwright
    rnd = random.Random(5)
    jobs = [JOBS[i % len(JOBS)] for i in range(len(TIMES))]
    rnd.shuffle(jobs)
    jobs[0], jobs[-1] = "NEW KITCHEN", "GARDEN ROOM"
    body, meta = "", []
    for i, t in enumerate(TIMES):
        phone = "07700 900" + f"{rnd.randrange(100, 999)}"
        long = i == 0 or rnd.random() < 0.3
        body += html(i, t, jobs[i], phone, long)
    out = HERE / "tex"; out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = studio.browser(p)
        pg = b.new_page(viewport={"width": 80 * PX, "height": 2000})
        tmp = HERE / ".dockets.html"
        tmp.write_text(studio.doc(body, 100, CSS.replace("SAW", saw())))
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        for i, t in enumerate(TIMES):
            el = pg.locator(f"#d{i}")
            box = el.bounding_box()
            el.screenshot(path=str(out / f"docket-{i:02d}.png"), omit_background=True)
            meta.append({"i": i, "time": t, "mm": round(box["height"] / PX, 1)})
        b.close(); tmp.unlink()
    (out / "dockets.json").write_text(json.dumps(meta, indent=1))
    print(meta[0], meta[-1], len(meta))


if __name__ == "__main__":
    main()
