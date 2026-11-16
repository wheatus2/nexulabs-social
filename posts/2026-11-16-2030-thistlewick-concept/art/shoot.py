"""Screenshots of the concept homepage (art/site/index.html), a real web page built for this post:
  shot-desktop.jpg  1440x900 first screen at 2x     shot-mobile.jpg  390x844 first screen at 3x     shot-full.jpg  whole desktop page at 1x
  python3 shoot.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, sc, full in (("desktop", 1440, 900, 2, False), ("mobile", 390, 844, 3, False), ("full", 1440, 900, 2, True)):
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=sc)
        pg.goto((HERE / "site" / "index.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
        pg.screenshot(path=str(HERE / f"shot-{name}.jpg"), full_page=full, type="jpeg", quality=94)
        print(name, pg.evaluate("document.documentElement.scrollWidth"), "px wide")
    b.close()
