#!/usr/bin/env python3
"""Nexulabs Studio: bespoke, art-directed slides, Story frames and Reels.

Every post is designed from scratch as its own HTML and CSS. There are no slide templates here on
purpose (Lee, 11 Nov 2026: the template posts looked "very repetitive, very basic"). Read DESIGN.md first.

  python3 studio.py render posts/<id>     art/slide-NN.html -> slide-NN.jpg, plus .sheet.jpg to look at
  python3 studio.py reel   posts/<id>     art/reel.html     -> reel.mp4, cover.jpg, .reel-sheet.jpg
  python3 studio.py check  posts/<id>     automatic checks: tiny text, clipped text, safe areas, word count,
                                          and repeats against design-log.json. Exit 1 if anything fails.
  python3 studio.py log    posts/<id>     add this post's design.json to design-log.json (after publishing)
  python3 studio.py recent                what the last posts used, so the next one is different

posts/<id>/design.json:
  {"format": "feed" | "story" | "reel",
   "composition": ["type-crop", "device-tilt", ...],   one name per slide/scene, your own words are fine
   "background": ["#0A0A0A", ...],                      the main background colour of each slide
   "display_font": "Unbounded", "accent": "#C6F432", "concept": "one line on the idea behind the look"}

A slide file is an HTML fragment: a <style> block and the markup. It is placed inside
<div class="frame"> (1080x1350 feed, 1080x1920 story or reel). Helpers you can use inside it:
  <!--logo:#FFFFFF,#667DFF-->   the Nexulabs wordmark (text colour, full-stop colour); size it with a wrapper height
  <!--grain:0.06-->             fine film grain over the whole frame (opacity)
  data-ui                       put on a mockup's root so the small-text check ignores the interface inside it
  .mac / .iphone / .browser     device shells (see DESIGN.md); what goes on the screen is yours to design
Fonts: Geist, GeistMono, InterTight, Instrument, Unbounded, Fraun, News, Playfair, DMSerif, Brico, Arch,
       Grotesk, Outfit, Syne, Cond (Anton), Oswald.
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FONTS = (ROOT / "fonts").as_uri()
FAMILIES = {"Geist-": "Geist", "GeistMono-": "GeistMono", "inter-tight": "InterTight", "instrument-serif": "Instrument",
            "unbounded": "Unbounded", "fraunces": "Fraun", "newsreader": "News", "playfair-display": "Playfair",
            "dm-serif-display": "DMSerif", "bricolage-grotesque": "Brico", "archivo": "Arch", "space-grotesk": "Grotesk",
            "outfit": "Outfit", "syne": "Syne", "anton": "Cond", "oswald": "Oswald"}
GEIST_W = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}


def font_css():
    out = []
    for f in sorted((ROOT / "fonts").glob("*.woff2")):
        fam = next((v for k, v in FAMILIES.items() if f.name.startswith(k)), None)
        if not fam:
            continue
        if f.name.startswith("Geist"):
            w, style = GEIST_W.get(f.stem.split("-")[1], 400), "normal"
        else:
            m = re.search(r"-(\d{3})-(normal|italic)\.woff2$", f.name)
            w, style = int(m.group(1)), m.group(2)
        out.append(f"@font-face{{font-family:{fam};src:url({FONTS}/{f.name});font-weight:{w};font-style:{style}}}")
    return "\n".join(out)


BASE = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#000;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
.frame{position:relative;width:1080px;height:VAR_Hpx;overflow:hidden;font-family:Geist;color:#fff;background:#000}
.frame img{display:block}
.nx-logo{display:inline-block;height:34px}.nx-logo svg{height:100%;width:auto;display:block}
.nx-grain{position:absolute;inset:0;pointer-events:none;z-index:50;mix-blend-mode:overlay}
/* device shells: the screen content is designed per post */
.mac{position:relative;width:860px}
.mac .lid{background:#0b0b0c;border-radius:22px 22px 4px 4px;padding:14px 14px 16px;box-shadow:0 0 0 2px #2a2b2e,0 0 0 3px #000}
.mac .lid:before{content:"";position:absolute;left:50%;top:5px;width:6px;height:6px;border-radius:50%;background:#1c1d20;transform:translateX(-50%)}
.mac .screen{aspect-ratio:16/10;border-radius:6px;overflow:hidden;background:#fff;position:relative}
.mac .base{height:16px;margin:0 -64px;border-radius:2px 2px 14px 14px;background:linear-gradient(#d9dadd,#a9abb0 60%,#7d7f85);position:relative}
.mac .base:before{content:"";position:absolute;left:50%;top:0;width:150px;height:7px;border-radius:0 0 8px 8px;background:#8b8d93;transform:translateX(-50%)}
.iphone{position:relative;width:390px;border-radius:64px;padding:11px;background:#0b0b0c;box-shadow:0 0 0 2px #3a3b40,0 0 0 4px #111}
.iphone .screen{aspect-ratio:9/19.5;border-radius:54px;overflow:hidden;background:#fff;position:relative}
.iphone .screen:before{content:"";position:absolute;left:50%;top:13px;width:112px;height:32px;border-radius:20px;background:#000;transform:translateX(-50%);z-index:5}
.browser{position:relative;width:860px;border-radius:16px;overflow:hidden;background:#fff}
.browser .bar{height:46px;display:flex;align-items:center;gap:8px;padding:0 18px;background:#ececee}
.browser .bar i{width:12px;height:12px;border-radius:50%;background:#c9cacf}
.browser .bar b{flex:1;margin:0 40px 0 22px;height:26px;border-radius:8px;background:#fff;font:500 13px Geist;color:#77797f;display:flex;align-items:center;justify-content:center}
.browser .screen{position:relative;overflow:hidden}
"""

REEL_BASE = """
.scene{position:absolute;inset:0;overflow:hidden;opacity:0;animation:nxIn .01s linear var(--t0) both,nxOut .01s linear var(--t1) forwards}
.scene.fade{animation:nxIn .5s ease var(--t0) both,nxOut .4s ease var(--t1) forwards}
@keyframes nxIn{from{opacity:0}to{opacity:1}}@keyframes nxOut{to{opacity:0}}
/* entrance helpers: add the class, set --d for the delay inside the scene, e.g. style="--d:.6s" */
.up,.fadein,.pop,.wipe,.left,.right{animation-duration:.8s;animation-timing-function:cubic-bezier(.16,1,.3,1);animation-fill-mode:both;animation-delay:calc(var(--t0) + var(--d,0s))}
.up{animation-name:nxUp}.fadein{animation-name:nxIn}.pop{animation-name:nxPop}.wipe{animation-name:nxWipe}.left{animation-name:nxLeft}.right{animation-name:nxRight}
@keyframes nxUp{from{opacity:0;transform:translateY(70px)}to{opacity:1;transform:none}}
@keyframes nxPop{from{opacity:0;transform:scale(.86)}to{opacity:1;transform:none}}
@keyframes nxWipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes nxLeft{from{opacity:0;transform:translateX(120px)}to{opacity:1;transform:none}}
@keyframes nxRight{from{opacity:0;transform:translateX(-120px)}to{opacity:1;transform:none}}
"""

GRAIN = ('<svg class="nx-grain" style="opacity:%s" width="100%%" height="100%%"><filter id="g"><feTurbulence type="fractalNoise" '
         'baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 1 0"/></filter>'
         '<rect width="100%%" height="100%%" filter="url(#g)"/></svg>')
LOGO = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text().replace("<title>nexulabs</title>", "")


def expand(html, post):
    def logo(m):
        a = [x.strip() for x in (m.group(1) or "#FFFFFF,#667DFF").split(",")]
        fg, dot = a[0], (a[1] if len(a) > 1 else a[0])
        return '<span class="nx-logo">' + LOGO.replace('fill="#FFFFFF"', f'fill="{fg}"').replace('fill="#667DFF"', f'fill="{dot}"') + "</span>"
    html = re.sub(r"<!--logo(?::([^>]*?))?-->", logo, html)
    html = re.sub(r"<!--grain(?::([\d.]+))?-->", lambda m: GRAIN % (m.group(1) or "0.06"), html)
    return html.replace("{{post}}", post.as_uri()).replace("{{root}}", ROOT.as_uri())


def spec(post):
    p = post / "design.json"
    d = json.loads(p.read_text()) if p.exists() else {}
    d.setdefault("format", "story" if post.parent.name == "stories" else "feed")
    return d


def doc(body, h, extra=""):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{font_css()}{BASE.replace('VAR_H', str(h))}{extra}</style></head>"
            f"<body>{body}</body></html>")


def browser(p):
    exe = "/usr/bin/google-chrome"
    return p.chromium.launch(executable_path=exe) if Path(exe).exists() else p.chromium.launch()


def slide_files(post):
    return sorted((post / "art").glob("slide-[0-9][0-9].html"))


def sheet(files, out, h=440):
    from PIL import Image
    ims = [Image.open(f).convert("RGB") for f in files]
    ims = [i.resize((int(i.width * h / i.height), h)) for i in ims]
    s = Image.new("RGB", (sum(i.width + 10 for i in ims) + 10, h + 20), "#777")
    x = 10
    for i in ims:
        s.paste(i, (x, 10)); x += i.width + 10
    s.save(out, quality=88)


def render(post):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    h = 1350 if spec(post)["format"] == "feed" else 1920
    files = slide_files(post)
    if not files:
        sys.exit("no art/slide-NN.html files")
    outs = []
    with sync_playwright() as p:
        b = browser(p)
        pg = b.new_page(viewport={"width": 1080, "height": h}, device_scale_factor=2)
        for f in files:
            tmp = post / f".{f.stem}.html"
            tmp.write_text(doc(f'<div class="frame">{expand(f.read_text(), post)}</div>', h))
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
            png = post / f".{f.stem}.png"
            pg.screenshot(path=str(png))
            dst = post / f"{f.stem}.jpg"
            Image.open(png).convert("RGB").resize((1080, h), Image.LANCZOS).save(dst, "JPEG", quality=94, optimize=True, progressive=True, subsampling=0)
            png.unlink(); tmp.unlink(); outs.append(dst)
        b.close()
    for old in post.glob("slide-[0-9][0-9].jpg"):
        if old not in outs:
            old.unlink()
    sheet(outs, post / ".sheet.jpg")
    print(json.dumps({"slides": [str(o) for o in outs], "look_at": str(post / ".sheet.jpg")}))


def reel_doc(post):
    src = expand((post / "art" / "reel.html").read_text(), post)
    durs = [float(x) for x in re.findall(r'class="scene[^"]*"[^>]*data-dur="([\d.]+)"', src)]
    if not durs:
        sys.exit('reel.html needs <section class="scene" data-dur="3.2"> blocks')
    t, k = 0.0, 0
    def stamp(m):
        nonlocal t, k
        d = durs[k]; k += 1
        s = f'{m.group(0)[:-1]} style="--t0:{t:.2f}s;--t1:{t + d:.2f}s">' if k < len(durs) else f'{m.group(0)[:-1]} style="--t0:{t:.2f}s;--t1:9999s">'
        t += d
        return s
    src = re.sub(r'<section class="scene[^>]*>', stamp, src)
    return doc(f'<div class="frame">{src}</div>', 1920, REEL_BASE), durs


def reel(post):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    html, durs = reel_doc(post)
    total, fps = sum(durs), 30
    tmp = post / ".reel.html"; tmp.write_text(html)
    frames = post / ".frames"; shutil.rmtree(frames, ignore_errors=True); frames.mkdir()
    n = int(round(total * fps))
    with sync_playwright() as p:
        b = browser(p)
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.evaluate("document.getAnimations().forEach(a => a.pause())")
        for f in range(n):
            pg.evaluate(f"document.getAnimations().forEach(a => {{ a.currentTime = {f * 1000 / fps}; }})")
            pg.screenshot(path=str(frames / f"{f:05d}.jpg"), type="jpeg", quality=93)
        b.close()
    mp4 = post / "reel.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "%05d.jpg"),
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", str(mp4)], check=True)
    picks, t = [], 0.0
    for d in durs:
        picks.append(frames / f"{min(n - 1, int((t + d * .85) * fps)):05d}.jpg"); t += d
    shutil.copy(picks[0], post / "cover.jpg")
    sheet(picks, post / ".reel-sheet.jpg", 480)
    shutil.rmtree(frames); tmp.unlink()
    print(json.dumps({"video": str(mp4), "seconds": round(total, 1), "look_at": str(post / ".reel-sheet.jpg")}))


CHECK_JS = """
(cfg) => {
  const out = [], F = document.querySelector('.frame').getBoundingClientRect();
  const vis = el => { const s = getComputedStyle(el); return s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity) > 0.05; };
  let words = 0;
  const w = document.createTreeWalker(document.querySelector('.frame'), NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode, t = n.textContent.trim(), el = n.parentElement;
    if (!t || !el || el.closest('style,script,svg.nx-grain') || !vis(el)) continue;
    const ui = el.closest('[data-ui]');
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
    if (!b.width) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (!ui) {
      words += t.split(/\\s+/).length;
      if (fs < cfg.min) out.push(`text too small (${Math.round(fs)}px, minimum ${cfg.min}): "${t.slice(0, 40)}"`);
      if (!el.closest('[data-bleed]') && (b.left < cfg.side - 1 || b.right > F.width - cfg.side + 1 || b.top < cfg.top - 1 || b.bottom > F.height - cfg.bottom + 1))
        out.push(`text outside the safe area: "${t.slice(0, 40)}"`);
    }
    let p = el;
    while (p && !p.classList.contains('frame')) {
      const s = getComputedStyle(p);
      if ((s.overflow !== 'visible' || s.textOverflow === 'ellipsis') && !p.closest('[data-bleed]') && !p.hasAttribute('data-ui') && !ui) {
        const pb = p.getBoundingClientRect();
        if (b.right > pb.right + 2 || b.bottom > pb.bottom + 2 || b.left < pb.left - 2 || b.top < pb.top - 2) { out.push(`text clipped by its box: "${t.slice(0, 40)}"`); break; }
      }
      p = p.parentElement;
    }
  }
  if (words > cfg.words) out.push(`${words} words on one frame (maximum ${cfg.words}): cut the copy, one idea per frame`);
  return {problems: out, words};
}
"""


def check(post):
    from playwright.sync_api import sync_playwright
    d = spec(post)
    fmt = d["format"]
    cfg = {"feed": {"min": 26, "side": 56, "top": 56, "bottom": 56, "words": 40},
           "story": {"min": 30, "side": 64, "top": 250, "bottom": 320, "words": 32},
           "reel": {"min": 34, "side": 64, "top": 220, "bottom": 380, "words": 22}}[fmt]
    problems = []
    with sync_playwright() as p:
        b = browser(p)
        if fmt == "reel":
            html, durs = reel_doc(post)
            tmp = post / ".check.html"; tmp.write_text(html)
            pg = b.new_page(viewport={"width": 1080, "height": 1920})
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready")
            pg.evaluate("document.getAnimations().forEach(a => a.pause())")
            t = 0.0
            for i, dur in enumerate(durs, 1):
                pg.evaluate(f"document.getAnimations().forEach(a => {{ a.currentTime = {(t + dur * .9) * 1000}; }})")
                r = pg.evaluate(CHECK_JS, cfg)
                problems += [f"scene {i}: {x}" for x in r["problems"]]
                if dur < 1.2 + r["words"] * 0.28:
                    problems.append(f"scene {i}: {r['words']} words in {dur}s is too fast to read")
                t += dur
            tmp.unlink()
            n = len(durs)
        else:
            h = 1350 if fmt == "feed" else 1920
            pg = b.new_page(viewport={"width": 1080, "height": h})
            files = slide_files(post)
            for f in files:
                tmp = post / f".{f.stem}.html"
                tmp.write_text(doc(f'<div class="frame">{expand(f.read_text(), post)}</div>', h))
                pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready")
                problems += [f"{f.stem}: {x}" for x in pg.evaluate(CHECK_JS, cfg)["problems"]]
                tmp.unlink()
            n = len(files)
        b.close()
    # the design record, and repeats
    for k in ("composition", "background", "display_font", "accent", "concept"):
        if not d.get(k):
            problems.append(f"design.json is missing '{k}'")
    comp, bgs = [c.lower() for c in d.get("composition", [])], [c.upper() for c in d.get("background", [])]
    if comp and len(comp) != n:
        problems.append(f"design.json lists {len(comp)} compositions for {n} frames")
    if len(set(comp)) < len(comp):
        problems.append("the same composition is used twice in this post: every frame needs its own")
    if "orange" in json.dumps(d).lower():
        problems.append("no orange")
    hist = [e for e in history() if e.get("id") != post.name]
    for e in hist[-12:]:
        again = set(comp) & {c.lower() for c in e.get("composition", [])}
        if again:
            problems.append(f"composition already used in {e['id']}: {', '.join(sorted(again))}")
    for e in hist[-5:]:
        if bgs and e.get("background") and bgs[0] == e["background"][0].upper():
            problems.append(f"same opening background colour as {e['id']} ({bgs[0]})")
    for e in hist[-3:]:
        if d.get("display_font") and d["display_font"] == e.get("display_font"):
            problems.append(f"same display typeface as {e['id']} ({d['display_font']})")
        if d.get("accent") and d["accent"].upper() == (e.get("accent") or "").upper():
            problems.append(f"same accent colour as {e['id']} ({d['accent']})")
    print(json.dumps({"ok": not problems, "problems": problems}, indent=1))
    return 1 if problems else 0


def history():
    p = ROOT / "design-log.json"
    return json.loads(p.read_text()) if p.exists() else []


def log(post):
    d = spec(post)
    h = [e for e in history() if e.get("id") != post.name]
    h.append({"id": post.name, **{k: d.get(k) for k in ("format", "composition", "background", "display_font", "accent", "concept")}})
    (ROOT / "design-log.json").write_text(json.dumps(h[-120:], indent=1, ensure_ascii=False) + "\n")
    print(f"logged {post.name}")


def recent():
    for e in history()[-12:]:
        print(f"{e['id']}\n   {e.get('format')} | {e.get('display_font')} | accent {e.get('accent')} | bg {', '.join(e.get('background') or [])}\n   {', '.join(e.get('composition') or [])}\n   {e.get('concept')}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "recent":
        recent(); sys.exit(0)
    if cmd not in ("render", "reel", "check", "log") or len(sys.argv) < 3:
        sys.exit(__doc__)
    post = Path(sys.argv[2]).resolve()
    sys.exit({"render": render, "reel": reel, "check": check, "log": log}[cmd](post) or 0)
