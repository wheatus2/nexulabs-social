"""Prints the till slip for build.py (python3 slip.py -> tex/slip.png). A made-up confirmation, as a till
printer would print it: 58 mm roll at 20 px/mm, saw edge top and bottom in the alpha."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import studio
PX = 20
def saw(n=30):
    pts = []
    for k in range(n + 1):
        pts.append(f"{k * 100 / n:.3f}% {'0' if k % 2 else str(0.8 * PX) + 'px'}")
    for k in range(n, -1, -1):
        pts.append(f"{k * 100 / n:.3f}% {'100%' if k % 2 else 'calc(100% - ' + str(0.8 * PX) + 'px)'}")
    return ",".join(pts)
CSS = f"""
html,body{{background:transparent!important;margin:0}}
.d{{width:{58 * PX}px;background:#FBFAF5;color:#15161c;clip-path:polygon({saw()})}}
.in{{padding:{8 * PX}px {5 * PX}px {9 * PX}px}}
p{{font-family:GeistMono;font-weight:500;margin:0;white-space:nowrap}}
.no{{font-size:{3.0 * PX}px;display:flex;justify-content:space-between;opacity:.8}}
.h{{font-size:{8.0 * PX}px;letter-spacing:.02em;margin-top:{6.5 * PX}px;transform:scaleY(1.5);transform-origin:0 100%}}
hr{{border:0;border-top:{0.4 * PX}px dashed #15161c;margin:{3.6 * PX}px 0;opacity:.8}}
.l{{font-size:{4.0 * PX}px;letter-spacing:.06em;margin-top:{1 * PX}px}}
.t{{font-size:{9.9 * PX}px;line-height:1;letter-spacing:-.01em;margin-top:{9.5 * PX}px;transform:scaleY(1.7);transform-origin:0 100%}}
.f{{font-size:{3.4 * PX}px;letter-spacing:.06em;text-align:center;opacity:.85}}
"""
BODY = """<div class="d" id="d"><div class="in">
<p class="no"><span>SUN 15 NOV</span><span>19:42</span></p>
<p class="h">RECEIVED</p><hr>
<p class="l">YOUR MESSAGE</p><p class="l">REF 2318</p><hr>
<p class="l">WE'LL REPLY BY</p>
<p class="t">10AM MON</p><hr>
<p class="f">THANK YOU</p>
</div></div>"""
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    (HERE / "tex").mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = studio.browser(p); pg = b.new_page(viewport={"width": 58 * PX, "height": 2400})
        tmp = HERE / ".slip.html"; tmp.write_text(studio.doc(BODY, 100, CSS))
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        el = pg.locator("#d"); box = el.bounding_box()
        el.screenshot(path=str(HERE / "tex" / "slip.png"), omit_background=True)
        b.close(); tmp.unlink()
    print("mm", box["height"] / PX)
