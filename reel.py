#!/usr/bin/env python3
"""Nexulabs Reel maker: animated 9:16 videos in the same design system as render.py.

Usage:  python3 reel.py posts/<id>/reel.json
Writes  posts/<id>/reel.mp4  (1080x1920, 30fps, H.264 + silent AAC track)
        posts/<id>/cover.jpg (thumbnail frame)

reel.json:
{
  "id": "...", "series": "Web design",
  "style": "neon", "palette": "ultraviolet", "pattern": "waves",   # same options as render.py
  "scenes": [                                  # 4-7 scenes, 2.5-4s each; total 12-25s
    {"type": "cover", "headline": "Your homepage has\\n*3 seconds*.", "dur": 3.2},
    {"type": "stat", "value": "53%", "statement": "...", "source": "...", "dur": 3.5},
    {"type": "compare" | "list" | "flow" | "browser" | "palette" | "quote" | "photo" ..., "dur": 4},
    {"type": "cta", "headline": "...", "cta": "nexulabs.co.uk", "dur": 3}
  ]
}
Every slide type from render.py works as a scene. Text animates in line by line; the
background drifts; scenes cross-fade. First scene = the hook (it's what people see first).
Keep on-screen text big and short: most people watch without sound.
"""
import json, shutil, subprocess, sys
from pathlib import Path

import render

FPS = 30
W, H = 1080, 1920

REEL_CSS = """
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
.scene{position:absolute;inset:0;opacity:0}
.scene .s{width:1080px;height:1920px;padding:230px 88px 300px;--ph-top:330px;--ph-h:900px}
.scene .st-signal h1{font-size:140px!important}.scene .st-signal.photo h1{font-size:120px!important}
.scene .st-journal h2,.scene .st-press h2{font-size:92px}.scene .st-soft h2{font-size:86px}
.scene .s .body{justify-content:flex-end}
.scene h1{font-size:118px}
.scene .cover h1,.scene .cta h1{font-size:122px}
.scene .big{font-size:440px}
.scene .stat h2,.scene h2{font-size:70px}
.scene p.lead{font-size:38px}
.scene .foot{font-size:20px}
.scene .meta{font-size:22px}
.scene .mark svg{height:42px}
.scene .chart{height:760px}
.scene .swipe{display:none}
.scene .it h3{font-size:52px}.scene .it p{font-size:30px}.scene .it .n{font-size:26px}
.scene .card .tx{font-size:52px}.scene .card .sm{font-size:30px}.scene .card .lb{font-size:22px}
.scene .st h3{font-size:56px}.scene .st p{font-size:30px}
.scene .row .lab{font-size:34px}.scene .row .lab b{font-size:42px}
.scene .legend div{font-size:32px}.scene .ctabox .r{font-size:48px}
.scene .screen h2{font-size:100px}.scene .screen p.lead{font-size:38px}.scene .win table{font-size:28px}
.scene .win .wbar b{font-size:32px}.scene .win .tabs{font-size:22px}.scene .win .rec .f small{font-size:22px}.scene .win .rec .f span{font-size:34px}.scene .win .rec .f span .pill{font-size:24px}.scene .win .rec .tl h5{font-size:21px}.scene .win .rec .ev{font-size:30px;padding:20px 0}.scene .win .rec .ev i{font-size:20px;min-width:118px;white-space:nowrap}
.scene .fx{animation:drift VAR_TOTALs linear both}
.scene .pat svg{animation:patdrift VAR_TOTALs linear both}
@keyframes drift{from{transform:scale(1.08) translate(-20px,10px)}to{transform:scale(1.18) translate(30px,-40px)}}
@keyframes patdrift{from{transform:translateY(0)}to{transform:translateY(-60px)}}
@keyframes sceneIn{from{opacity:0;transform:scale(1.03)}to{opacity:1;transform:none}}
@keyframes sceneOut{from{opacity:1}to{opacity:0;transform:scale(.98)}}
@keyframes rise{from{opacity:0;transform:translateY(46px);filter:blur(6px)}to{opacity:1;transform:none;filter:none}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes growx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.progress{display:none}
.progress i{position:absolute;inset:0;background:linear-gradient(90deg,#667DFF,#00D1FF);transform-origin:left;animation:bar VAR_TOTALs linear both}
"""


def scene_html(i, scene, total_scenes, spec, t0, dur, total):
    style = spec.get("style", "studio")
    sec = render.build(scene, i + 1, total_scenes, spec.get("series", ""), style)
    fade_in = 0 if i == 0 else 0.45
    anim = []
    if i == 0:
        anim.append(f"sceneIn .01s linear {t0:.2f}s both")
    else:
        anim.append(f"sceneIn {fade_in}s ease-out {t0:.2f}s both")
    if i < total_scenes - 1:
        anim.append(f"sceneOut .4s ease-in {t0 + dur - .4:.2f}s forwards")
    return f'<div class="scene" data-t0="{t0}" style="animation:{",".join(anim)}">{sec}</div>'


STAGGER_JS = """
(() => {
  const sel = '.kicker, h1, h2, p.lead, .win, .phonewrap, .excap, .big, .card, .it, .st, .row, .col, .bw, .legend > div, .sw .row, .qm, .ctabox, .chart, .xl';
  document.querySelectorAll('.scene').forEach(sc => {
    const t0 = parseFloat(sc.dataset.t0);
    let k = 0;
    sc.querySelectorAll(sel).forEach(el => {
      if (el.closest('.bw') && !el.classList.contains('bw')) return;
      const d = t0 + 0.25 + k * 0.16; k++;
      el.style.animation = `rise .7s cubic-bezier(.2,.8,.2,1) ${d.toFixed(2)}s both`;
    });
    sc.querySelectorAll('.col .bar').forEach((b, j) => { b.style.transformOrigin = 'bottom'; b.style.animation = `grow .9s cubic-bezier(.2,.8,.2,1) ${(t0 + .6 + j*.12).toFixed(2)}s both`; });
    sc.querySelectorAll('.row .fill').forEach((b, j) => { b.style.transformOrigin = 'left'; b.style.animation = `growx .9s cubic-bezier(.2,.8,.2,1) ${(t0 + .6 + j*.12).toFixed(2)}s both`; });
  });
  document.getAnimations().forEach(a => a.pause());
})();
"""


def make(spec_path):
    from playwright.sync_api import sync_playwright
    spec_path = Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text())
    out = spec_path.parent
    render._POST_DIR = str(out)
    render._PALETTE = spec.get("palette", "electric")
    render._PATTERN = spec.get("pattern")
    scenes = spec["scenes"]
    total = sum(float(s.get("dur", 3.2)) for s in scenes)
    t, parts = 0.0, []
    for i, sc in enumerate(scenes):
        d = float(sc.get("dur", 3.2))
        parts.append(scene_html(i, sc, len(scenes), spec, t, d, total))
        t += d
    css = render.CSS + REEL_CSS.replace("VAR_TOTAL", f"{total:.2f}")
    doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(parts)}<div class='progress'><i></i></div></body></html>"
    tmp = out / ".reel.html"
    tmp.write_text(doc)
    frames = out / ".frames"
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir()
    n = int(round(total * FPS))
    with sync_playwright() as p:
        exe = "/usr/bin/google-chrome" if Path("/usr/bin/google-chrome").exists() else None
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(tmp.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        pg.evaluate(STAGGER_JS)
        for f in range(n):
            ms = f * 1000 / FPS
            pg.evaluate(f"document.getAnimations().forEach(a => {{ a.currentTime = {ms}; }})")
            pg.screenshot(path=str(frames / f"{f:05d}.jpg"), type="jpeg", quality=92)
        b.close()
    mp4 = out / "reel.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%05d.jpg"),
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(mp4)], check=True)
    cover_frame = frames / f"{min(n - 1, int(FPS * min(2.2, scenes[0].get('dur', 3.2) - .3))):05d}.jpg"
    shutil.copy(cover_frame, out / "cover.jpg")
    # contact sheet of key moments for checking
    from PIL import Image
    picks, t = [], 0.0
    for sc in scenes:
        d = float(sc.get("dur", 3.2)); picks.append(int((t + d * .8) * FPS)); t += d
    ims = [Image.open(frames / f"{min(p_, n-1):05d}.jpg").resize((270, 480)) for p_ in picks]
    sheet = Image.new("RGB", (280 * len(ims) + 10, 490), "#888")
    for k, im in enumerate(ims):
        sheet.paste(im, (10 + k * 280, 5))
    sheet.save(out / ".reel-sheet.jpg", quality=88)
    shutil.rmtree(frames)
    tmp.unlink()
    print(json.dumps({"video": str(mp4), "cover": str(out / "cover.jpg"), "seconds": round(total, 1),
                      "check_sheet": str(out / ".reel-sheet.jpg")}))


if __name__ == "__main__":
    make(sys.argv[1])
