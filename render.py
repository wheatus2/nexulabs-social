#!/usr/bin/env python3
"""Nexulabs Instagram renderer.

Usage:  python3 render.py posts/<id>/post.json
Writes  posts/<id>/slide-01.jpg ... (1080x1350, 4:5 portrait)

Slide types: cover, stat, bars, hbars, list, quote, cta
Text markup: *word* -> accent colour. Line breaks with \n.
Themes: "ink" (dark) or "paper" (light).
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FONTS = (ROOT / "fonts").as_uri()

ACCENT = "#FF5A1F"
INK = "#0B0B0C"
PAPER = "#F3F1EC"


def md(text):
    t = html.escape(text or "")
    t = re.sub(r"\*(.+?)\*", r'<span class="acc">\1</span>', t)
    t = re.sub(r"(?<=\w)-(?=\w)", "\u2011", t)
    return t.replace("\n", "<br>")


CSS = f"""
@font-face{{font-family:Disp;src:url({FONTS}/InterDisplay-Regular.otf);font-weight:400}}
@font-face{{font-family:Disp;src:url({FONTS}/InterDisplay-Medium.otf);font-weight:500}}
@font-face{{font-family:Disp;src:url({FONTS}/InterDisplay-SemiBold.otf);font-weight:600}}
@font-face{{font-family:Disp;src:url({FONTS}/InterDisplay-Bold.otf);font-weight:700}}
@font-face{{font-family:Text;src:url({FONTS}/Inter-Regular.otf);font-weight:400}}
@font-face{{font-family:Text;src:url({FONTS}/Inter-Medium.otf);font-weight:500}}
@font-face{{font-family:Text;src:url({FONTS}/Inter-SemiBold.otf);font-weight:600}}
@font-face{{font-family:Mono;src:url({FONTS}/jetbrains-mono-latin-400-normal.woff2);font-weight:400}}
@font-face{{font-family:Mono;src:url({FONTS}/jetbrains-mono-latin-500-normal.woff2);font-weight:500}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
body{{font-family:Text;-webkit-font-smoothing:antialiased;font-feature-settings:"ss01","cv11","tnum"}}
.s{{position:relative;width:1080px;height:1350px;padding:84px 88px;display:flex;flex-direction:column;overflow:hidden}}
.ink{{background:{INK};color:{PAPER}}}
.paper{{background:{PAPER};color:{INK}}}
.acc{{color:{ACCENT}}}
.grid{{position:absolute;inset:0;pointer-events:none;opacity:.07;
 background-image:linear-gradient(currentColor 1px,transparent 1px),linear-gradient(90deg,currentColor 1px,transparent 1px);
 background-size:90px 90px;background-position:-1px -1px;
 -webkit-mask-image:radial-gradient(ellipse at 70% 30%,#000 10%,transparent 75%)}}
.paper .grid{{opacity:.06}}
.glow{{position:absolute;width:1100px;height:1100px;right:-480px;top:-520px;border-radius:50%;
 background:radial-gradient(circle,{ACCENT}55 0%,{ACCENT}18 35%,transparent 68%);filter:blur(10px)}}
.glow.low{{top:auto;bottom:-620px;right:-420px}}
.grain{{position:absolute;inset:0;opacity:.09;mix-blend-mode:overlay;pointer-events:none;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.top{{position:relative;display:flex;justify-content:space-between;align-items:center;z-index:2}}
.mark{{font-family:Disp;font-weight:600;font-size:34px;letter-spacing:-.035em;display:flex;align-items:center;gap:10px}}
.mark i{{display:inline-block;width:11px;height:11px;border-radius:50%;background:{ACCENT}}}
.meta{{font-family:Mono;font-size:19px;letter-spacing:.06em;text-transform:uppercase;opacity:.6}}
.body{{position:relative;z-index:2;flex:1;display:flex;flex-direction:column}}
.foot{{position:relative;z-index:2;display:flex;justify-content:space-between;align-items:flex-end;gap:40px;
 font-family:Mono;font-size:17px;letter-spacing:.02em;line-height:1.5;opacity:.55}}
.foot .src{{max-width:760px}}
.kicker{{font-family:Mono;font-size:21px;letter-spacing:.08em;text-transform:uppercase;display:flex;align-items:center;gap:14px}}
.kicker:before{{content:"";width:34px;height:2px;background:{ACCENT}}}
h1{{font-family:Disp;font-weight:600;letter-spacing:-.045em;line-height:.98}}
h2{{font-family:Disp;font-weight:600;letter-spacing:-.035em;line-height:1.04;font-size:64px}}
p.lead{{font-size:31px;line-height:1.42;letter-spacing:-.01em;opacity:.78;max-width:820px}}
.rule{{height:1px;background:currentColor;opacity:.18}}
/* cover */
.cover h1{{font-size:112px;margin-top:auto}}
.cover p.lead{{margin-top:44px}}
.swipe{{font-family:Mono;font-size:19px;letter-spacing:.08em;text-transform:uppercase;display:flex;align-items:center;gap:12px;opacity:1}}
.swipe b{{display:inline-flex;width:58px;height:58px;border-radius:50%;border:1.5px solid currentColor;align-items:center;justify-content:center;font-weight:400;font-size:24px}}
/* stat */
.big{{font-family:Disp;font-weight:600;letter-spacing:-.065em;line-height:.82;font-size:400px;margin-top:auto;margin-left:-14px}}
.big small{{font-size:.42em;letter-spacing:-.04em;vertical-align:top;margin-left:6px;position:relative;top:.12em}}
.stat h2{{margin-top:56px;max-width:860px}}
.stat p.lead{{margin-top:28px}}
/* bars */
.chart{{margin-top:auto;display:flex;align-items:flex-end;gap:28px;height:640px;border-bottom:1.5px solid currentColor;padding-bottom:0}}
.col{{flex:1;display:flex;flex-direction:column;align-items:stretch;justify-content:flex-end;height:100%}}
.col .v{{font-family:Disp;font-weight:600;font-size:52px;letter-spacing:-.04em;margin-bottom:16px}}
.col .bar{{border-radius:6px 6px 0 0;background:currentColor;opacity:.16}}
.col.hl .bar{{background:{ACCENT};opacity:1}}
.col.hl .v{{color:{ACCENT}}}
.xl{{display:flex;gap:28px;margin-top:18px}}
.xl div{{flex:1;font-family:Mono;font-size:21px;letter-spacing:.04em;opacity:.65}}
.bars h2{{margin-top:44px}}
/* hbars */
.hb{{margin-top:auto;display:flex;flex-direction:column;gap:30px}}
.row .lab{{display:flex;justify-content:space-between;font-size:27px;font-weight:500;margin-bottom:12px;letter-spacing:-.01em}}
.row .lab b{{font-family:Disp;font-weight:600;font-size:34px;letter-spacing:-.03em}}
.row .track{{height:22px;border-radius:11px;background:rgba(127,127,127,.16);overflow:hidden}}
.row .fill{{height:100%;border-radius:11px;background:currentColor;opacity:.5}}
.row.hl .fill{{background:{ACCENT};opacity:1}}
.row.hl .lab{{color:{ACCENT}}}
.hbars h2{{margin-top:44px}}
/* list */
.list h2{{margin-top:40px}}
.items{{margin-top:auto;display:flex;flex-direction:column}}
.it{{display:flex;gap:34px;padding:30px 0;border-top:1px solid rgba(127,127,127,.3)}}
.it .n{{font-family:Mono;font-size:22px;color:{ACCENT};padding-top:8px;min-width:44px}}
.it h3{{font-family:Disp;font-weight:600;font-size:38px;letter-spacing:-.03em;line-height:1.1}}
.it p{{font-size:25px;line-height:1.42;opacity:.68;margin-top:8px}}
/* quote */
.quote h1{{font-size:88px;margin-top:auto;line-height:1.02}}
.qm{{font-family:Disp;font-size:220px;line-height:.6;color:{ACCENT};height:110px}}
.quote p.lead{{margin-top:44px}}
/* cta */
.cta h1{{font-size:100px;margin-top:auto}}
.cta p.lead{{margin-top:40px}}
.ctabox{{margin-top:64px;display:flex;align-items:center;justify-content:space-between;padding:34px 40px;border-radius:22px;
 border:1.5px solid rgba(127,127,127,.35)}}
.ctabox .l{{font-family:Mono;font-size:19px;letter-spacing:.08em;text-transform:uppercase;opacity:.6}}
.ctabox .r{{font-family:Disp;font-weight:600;font-size:40px;letter-spacing:-.03em;margin-top:6px}}
.ctabox .btn{{width:84px;height:84px;border-radius:50%;background:{ACCENT};color:#fff;display:flex;align-items:center;justify-content:center;font-size:36px}}
"""


def frame(slide, idx, total, series, inner, foot_left="", foot_right=""):
    theme = slide.get("theme", "paper")
    glow = ""
    if slide.get("glow", theme == "ink"):
        glow = f'<div class="glow{" low" if slide.get("glow_low") else ""}"></div>'
    return f"""<section class="s {theme} {slide['type']}">
{glow}<div class="grid"></div>
<div class="top"><div class="mark">nexulabs<i></i></div>
<div class="meta">{html.escape(series)} &nbsp;·&nbsp; {idx:02d}/{total:02d}</div></div>
<div class="body">{inner}</div>
<div class="foot"><div class="src">{foot_left}</div><div>{foot_right}</div></div>
<div class="grain"></div></section>"""


def src(slide):
    s = slide.get("source")
    return f"Source: {html.escape(s)}" if s else ""


def build(slide, idx, total, series):
    t = slide["type"]
    fr = ""
    if t == "cover":
        inner = f"""<div class="kicker" style="margin-top:96px">{md(slide.get('kicker',''))}</div>
<h1 style="font-size:{slide.get('size',112)}px">{md(slide['headline'])}</h1>
{f'<p class="lead">{md(slide["sub"])}</p>' if slide.get('sub') else ''}<div style="height:70px"></div>"""
        fr = '<div class="swipe">Swipe <b>→</b></div>' if total > 1 else ""
    elif t == "stat":
        v = html.escape(slide["value"])
        m = re.match(r"^([^%x+£$]*)([%x+]?)$", v)
        num, suf = (m.group(1), m.group(2)) if m else (v, "")
        inner = f"""<div class="kicker" style="margin-top:96px">{md(slide.get('kicker',''))}</div>
<div class="big" style="font-size:{slide.get('size',400)}px">{num}{f'<small class="acc">{suf}</small>' if suf else ''}</div>
<h2>{md(slide['statement'])}</h2>
{f'<p class="lead">{md(slide["detail"])}</p>' if slide.get('detail') else ''}<div style="height:56px"></div>"""
    elif t == "bars":
        data = slide["data"]
        mx = max(v for _, v in data) * slide.get("headroom", 1.08)
        hl = slide.get("highlight", data[-1][0])
        unit = html.escape(slide.get("unit", ""))
        cols = "".join(
            f'<div class="col{" hl" if str(k)==str(hl) else ""}"><div class="v">{v}{unit}</div>'
            f'<div class="bar" style="height:{v/mx*82:.1f}%"></div></div>' for k, v in data)
        xl = "".join(f"<div>{html.escape(str(k))}</div>" for k, _ in data)
        inner = f"""<div class="kicker" style="margin-top:96px">{md(slide.get('kicker',''))}</div>
<h2>{md(slide['title'])}</h2>
<div class="chart">{cols}</div><div class="xl">{xl}</div><div style="height:56px"></div>"""
    elif t == "hbars":
        data = slide["data"]
        mx = slide.get("max", max(v for _, v in data))
        hl = slide.get("highlight")
        unit = html.escape(slide.get("unit", ""))
        rows = "".join(
            f'<div class="row{" hl" if k==hl else ""}"><div class="lab"><span>{html.escape(k)}</span><b>{v}{unit}</b></div>'
            f'<div class="track"><div class="fill" style="width:{v/mx*100:.1f}%"></div></div></div>' for k, v in data)
        inner = f"""<div class="kicker" style="margin-top:96px">{md(slide.get('kicker',''))}</div>
<h2>{md(slide['title'])}</h2><div class="hb">{rows}</div><div style="height:56px"></div>"""
    elif t == "list":
        items = "".join(
            f'<div class="it"><div class="n">{i+1:02d}</div><div><h3>{md(a)}</h3>'
            f'{f"<p>{md(b)}</p>" if b else ""}</div></div>' for i, (a, b) in enumerate(slide["items"]))
        inner = f"""<div class="kicker" style="margin-top:96px">{md(slide.get('kicker',''))}</div>
<h2>{md(slide['title'])}</h2><div class="items">{items}</div><div style="height:40px"></div>"""
    elif t == "quote":
        inner = f"""<div class="qm" style="margin-top:auto">“</div><h1>{md(slide['text'])}</h1>
{f'<p class="lead">{md(slide["sub"])}</p>' if slide.get('sub') else ''}<div style="height:70px"></div>"""
    elif t == "cta":
        inner = f"""<div class="kicker" style="margin-top:96px">{md(slide.get('kicker',''))}</div>
<h1 style="font-size:{slide.get('size',100)}px">{md(slide['headline'])}</h1>
{f'<p class="lead">{md(slide["body"])}</p>' if slide.get('body') else ''}
<div class="ctabox"><div><div class="l">{md(slide.get('cta_label','Talk to us'))}</div>
<div class="r">{md(slide.get('cta','nexulabs.co.uk'))}</div></div><div class="btn">→</div></div><div style="height:40px"></div>"""
    else:
        raise ValueError(f"unknown slide type {t}")
    return frame(slide, idx, total, series, inner, src(slide), fr)


def render(spec_path):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    spec_path = Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text())
    out = spec_path.parent
    slides = spec["slides"]
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome") if Path("/usr/bin/google-chrome").exists() else p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        for i, s in enumerate(slides, 1):
            doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{build(s, i, len(slides), spec.get('series',''))}</body></html>"
            tmp = out / f".slide-{i:02d}.html"
            tmp.write_text(doc)
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            png = out / f".slide-{i:02d}.png"
            pg.screenshot(path=str(png))
            im = Image.open(png).convert("RGB").resize((1080, 1350), Image.LANCZOS)
            dst = out / f"slide-{i:02d}.jpg"
            im.save(dst, "JPEG", quality=93, optimize=True, progressive=True, subsampling=0)
            png.unlink(); tmp.unlink()
            files.append(dst)
        b.close()
    for f in files:
        print(f)


if __name__ == "__main__":
    render(sys.argv[1])
