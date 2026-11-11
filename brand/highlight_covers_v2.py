#!/usr/bin/env python3
"""Highlight covers, new standard (11 Nov 2026): cobalt, one thick-stroke mark in white and butter yellow.
Writes brand/highlight-covers/<slug>.jpg (1080x1920 Story frame, mark inside the circle crop), <slug>-square.jpg
and preview.jpg. Run: python3 brand/highlight_covers_v2.py"""
import json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
W, Y = "#fff", "#FFF36B"
def sparkle(cx, cy, r, c):
    k = r * .08
    return (f'<path fill="{c}" d="M{cx} {cy-r} C{cx+k} {cy-r*.4},{cx+r*.4} {cy-k},{cx+r} {cy} C{cx+r*.4} {cy+k},{cx+k} {cy+r*.4},{cx} {cy+r} '
            f'C{cx-k} {cy+r*.4},{cx-r*.4} {cy+k},{cx-r} {cy} C{cx-r*.4} {cy-k},{cx-k} {cy-r*.4},{cx} {cy-r}Z"/>')
S = 'fill="none" stroke-width="44" stroke-linecap="round" stroke-linejoin="round"'
MARKS = {
 "web-crm": f'<circle cx="190" cy="270" r="150" stroke="{W}" {S}/><circle cx="350" cy="270" r="150" stroke="{Y}" {S}/><path d="M270 143 A150 150 0 0 1 270 397" stroke="{W}" fill="none" stroke-width="44"/>',
 "websites": f'<rect x="62" y="102" width="416" height="336" rx="56" stroke="{W}" {S}/><path d="M150 212H390" stroke="{Y}" {S}/>',
 "crm": f'<rect x="52" y="112" width="436" height="316" rx="56" stroke="{W}" {S}/><circle cx="182" cy="270" r="50" fill="{Y}"/><path d="M290 236H400M290 306H360" stroke="{W}" {S}/>',
 "branding": f'<rect x="62" y="150" width="250" height="250" rx="24" stroke="{W}" {S}/><circle cx="350" cy="262" r="128" stroke="{Y}" {S}/>',
 "domains": f'<circle cx="270" cy="270" r="196" stroke="{W}" {S}/><ellipse cx="270" cy="270" rx="84" ry="196" stroke="{Y}" {S}/><path d="M74 270H466" stroke="{W}" {S}/>',
 "hosting": f'<rect x="62" y="96" width="416" height="150" rx="50" stroke="{W}" {S}/><rect x="62" y="294" width="416" height="150" rx="50" stroke="{Y}" {S}/><circle cx="150" cy="171" r="20" fill="{W}"/><circle cx="150" cy="369" r="20" fill="{Y}"/>',
 "ai-automation": sparkle(236, 300, 216, W) + sparkle(438, 104, 84, Y),
 "tech-news": f'<circle cx="126" cy="414" r="52" fill="{Y}"/><path d="M126 232A182 182 0 0 1 308 414" stroke="{W}" {S}/><path d="M126 80A334 334 0 0 1 460 414" stroke="{W}" {S}/>',
 "book-call": f'<rect x="72" y="118" width="396" height="340" rx="56" stroke="{W}" {S}/><path d="M178 66V150M362 66V150" stroke="{W}" {S}/><circle cx="270" cy="306" r="50" fill="{Y}"/>',
}
def main():
    sys.path.insert(0, str(ROOT)); import studio
    from PIL import Image
    tmp = ROOT / ".covers"; shutil.rmtree(tmp, ignore_errors=True)
    out = ROOT / "brand" / "highlight-covers"
    for slug, mark in MARKS.items():
        d = tmp / slug / "art"; d.mkdir(parents=True)
        (d / "slide-01.html").write_text(f'''<style>.frame{{background:#1437FF}}
.halo{{position:absolute;left:140px;top:560px;width:800px;height:800px;border-radius:50%;background:radial-gradient(closest-side,rgba(255,255,255,.14),rgba(255,255,255,0))}}
svg.m{{position:absolute;left:270px;top:690px}}</style><div class="halo"></div>
<svg class="m" width="540" height="540" viewBox="0 0 540 540">{mark}</svg><!--grain:0.05-->''')
        (tmp / slug / "design.json").write_text(json.dumps({"format": "story"}))
        subprocess.run([sys.executable, str(ROOT / "studio.py"), "render", str(tmp / slug)], check=True, stdout=subprocess.DEVNULL)
        im = Image.open(tmp / slug / "slide-01.jpg")
        im.save(out / f"{slug}.jpg", quality=94, subsampling=0)
        im.crop((0, 420, 1080, 1500)).save(out / f"{slug}-square.jpg", quality=94, subsampling=0)
    from PIL import ImageDraw
    names = list(MARKS); sheet = Image.new("RGB", (len(names) * 230 + 10, 240), "#fff")
    for i, s in enumerate(names):
        c = Image.open(out / f"{s}-square.jpg").resize((220, 220)); m = Image.new("L", (220, 220), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 220, 220), fill=255); sheet.paste(c, (10 + i * 230, 10), m)
    sheet.save(out / "preview.jpg", quality=90); shutil.rmtree(tmp)
main()
