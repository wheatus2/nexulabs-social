#!/usr/bin/env python3
"""Nexulabs Instagram renderer.

Usage:  python3 render.py posts/<id>/post.json
Writes  posts/<id>/slide-01.jpg ... (1080x1350, 4:5 portrait)

Slide types: cover, stat, bars, hbars, list, quote, cta, compare, browser, palette, flow, photo (Unsplash background: "image", "credit", optional "shade": full|blue, "focus")
browser "site" may include "nav_text" (e.g. a phone number shown in the mock header); compare, list and flow may include "title_size".
Text markup: *word* -> accent colour. Line breaks with \n.
Themes: "ink" (dark), "paper" (light) or "blue" (brand blue background).
Post-level "style": studio | editorial | bold | minimal | poster (rotate; never the same two posts running).
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FONTS = (ROOT / "fonts").as_uri()

ACCENT = "#3B2BFF"      # on light backgrounds (brand blue)
ACCENT_DARK = "#667DFF" # on dark backgrounds (logo full stop)
INK = "#0B0B0C"
PAPER = "#F5F5F7"


def md(text):
    t = html.escape(text or "")
    t = re.sub(r"\*(.+?)\*", r'<span class="acc">\1</span>', t)
    t = re.sub(r"(?<=\w)-(?=\w)", "\u2011", t)
    return t.replace("\n", "<br>")


CSS = f"""
@font-face{{font-family:Disp;src:url({FONTS}/Geist-Regular.woff2);font-weight:400}}
@font-face{{font-family:Disp;src:url({FONTS}/Geist-Medium.woff2);font-weight:500}}
@font-face{{font-family:Disp;src:url({FONTS}/Geist-SemiBold.woff2);font-weight:600}}
@font-face{{font-family:Disp;src:url({FONTS}/Geist-Bold.woff2);font-weight:700}}
@font-face{{font-family:Text;src:url({FONTS}/Geist-Regular.woff2);font-weight:400}}
@font-face{{font-family:Text;src:url({FONTS}/Geist-Medium.woff2);font-weight:500}}
@font-face{{font-family:Text;src:url({FONTS}/Geist-SemiBold.woff2);font-weight:600}}
@font-face{{font-family:Mono;src:url({FONTS}/GeistMono-Regular.woff2);font-weight:400}}
@font-face{{font-family:Mono;src:url({FONTS}/GeistMono-Medium.woff2);font-weight:500}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
body{{font-family:Text;-webkit-font-smoothing:antialiased;font-feature-settings:"tnum"}}
.s{{position:relative;width:1080px;height:1350px;padding:84px 88px;display:flex;flex-direction:column;overflow:hidden}}
.ink{{background:{INK};color:{PAPER};--acc:{ACCENT_DARK};--fg:{PAPER}}}
.paper{{background:{PAPER};color:{INK};--acc:{ACCENT};--fg:{INK}}}
.acc{{color:var(--acc)}}
.grid{{position:absolute;inset:0;pointer-events:none;opacity:.07;
 background-image:linear-gradient(currentColor 1px,transparent 1px),linear-gradient(90deg,currentColor 1px,transparent 1px);
 background-size:90px 90px;background-position:-1px -1px;
 -webkit-mask-image:radial-gradient(ellipse at 70% 30%,#000 10%,transparent 75%)}}
.paper .grid{{opacity:.06}}
.glow{{position:absolute;width:1100px;height:1100px;right:-480px;top:-520px;border-radius:50%;
 background:radial-gradient(circle,{ACCENT_DARK}66 0%,{ACCENT_DARK}22 35%,transparent 68%);filter:blur(10px)}}
.glow.low{{top:auto;bottom:-620px;right:-420px}}
.grain{{position:absolute;inset:0;opacity:.09;mix-blend-mode:overlay;pointer-events:none;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.top{{position:relative;display:flex;justify-content:space-between;align-items:center;z-index:2}}
.mark svg{{height:36px;width:auto;display:block}}
.meta{{font-family:Mono;font-size:19px;letter-spacing:.06em;text-transform:uppercase;opacity:.6}}
.body{{position:relative;z-index:2;flex:1;display:flex;flex-direction:column}}
.foot{{position:relative;z-index:2;display:flex;justify-content:space-between;align-items:flex-end;gap:40px;
 font-family:Mono;font-size:17px;letter-spacing:.02em;line-height:1.5;opacity:.55}}
.foot .src{{max-width:760px}}
.kicker{{font-family:Mono;font-size:21px;letter-spacing:.08em;text-transform:uppercase;display:flex;align-items:center;gap:14px}}
.kicker:before{{content:"";width:34px;height:2px;background:var(--acc)}}
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
.col.hl .bar{{background:var(--acc);opacity:1}}
.col.hl .v{{color:var(--acc)}}
.xl{{display:flex;gap:28px;margin-top:18px}}
.xl div{{flex:1;font-family:Mono;font-size:21px;letter-spacing:.04em;opacity:.65}}
.bars h2{{margin-top:44px}}
/* hbars */
.hb{{margin-top:auto;display:flex;flex-direction:column;gap:30px}}
.row .lab{{display:flex;justify-content:space-between;font-size:27px;font-weight:500;margin-bottom:12px;letter-spacing:-.01em}}
.row .lab b{{font-family:Disp;font-weight:600;font-size:34px;letter-spacing:-.03em}}
.row .track{{height:22px;border-radius:11px;background:rgba(127,127,127,.16);overflow:hidden}}
.row .fill{{height:100%;border-radius:11px;background:currentColor;opacity:.5}}
.row.hl .fill{{background:var(--acc);opacity:1}}
.row.hl .lab{{color:var(--acc)}}
.hbars h2{{margin-top:44px}}
/* list */
.list h2{{margin-top:40px}}
.items{{margin-top:auto;display:flex;flex-direction:column}}
.it{{display:flex;gap:34px;padding:30px 0;border-top:1px solid rgba(127,127,127,.3)}}
.it .n{{font-family:Mono;font-size:22px;color:var(--acc);padding-top:8px;min-width:44px}}
.it h3{{font-family:Disp;font-weight:600;font-size:38px;letter-spacing:-.03em;line-height:1.1}}
.it p{{font-size:25px;line-height:1.42;opacity:.68;margin-top:8px}}
/* quote */
.quote h1{{font-size:88px;margin-top:auto;line-height:1.02}}
.quote .qm+h1{{margin-top:36px}}
.qm{{font-family:Disp;font-size:220px;line-height:.6;color:var(--acc);height:110px}}
.quote p.lead{{margin-top:44px}}
/* cta */
.cta h1{{font-size:100px;margin-top:auto}}
.cta p.lead{{margin-top:40px}}
.ctabox{{margin-top:64px;display:flex;align-items:center;justify-content:space-between;padding:34px 40px;border-radius:22px;
 border:1.5px solid rgba(127,127,127,.35)}}
.ctabox .l{{font-family:Mono;font-size:19px;letter-spacing:.08em;text-transform:uppercase;opacity:.6}}
.ctabox .r{{font-family:Disp;font-weight:600;font-size:40px;letter-spacing:-.03em;margin-top:6px}}
.ctabox .btn{{width:84px;height:84px;border-radius:50%;background:var(--acc);color:#fff;display:flex;align-items:center;justify-content:center;font-size:36px}}
/* compare */
.compare h2{{margin-top:40px}}
.cmp{{margin-top:auto;display:flex;flex-direction:column;gap:26px}}
.card{{border-radius:24px;padding:38px 42px;border:1.5px solid rgba(127,127,127,.28)}}
.card .lb{{font-family:Mono;font-size:19px;letter-spacing:.1em;text-transform:uppercase;opacity:.6;display:flex;align-items:center;gap:12px}}
.card .tx{{font-family:Disp;font-weight:600;font-size:40px;letter-spacing:-.03em;line-height:1.15;margin-top:14px}}
.card .sm{{font-size:24px;line-height:1.45;opacity:.7;margin-top:12px}}
.card.bad .tx{{opacity:.55}}
.card.good{{border-color:var(--acc);background:rgba(102,125,255,.08)}}
.card.good .lb{{color:var(--acc);opacity:1}}
.ico{{width:30px;height:30px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:18px;border:1.5px solid currentColor}}
/* browser mockup */
.browser h2{{margin-top:40px;margin-bottom:44px}}
.bw{{margin-top:auto;border-radius:22px;overflow:hidden;border:1.5px solid rgba(127,127,127,.3);background:#fff;color:#0B0B0C;box-shadow:0 40px 80px -30px rgba(0,0,0,.45);position:relative}}
.bw .bar{{height:58px;background:#ECECEF;display:flex;align-items:center;gap:10px;padding:0 22px}}
.bw .bar i{{width:13px;height:13px;border-radius:50%;background:#C9C9CF}}
.bw .url{{margin-left:18px;flex:1;height:34px;border-radius:17px;background:#fff;font-family:Mono;font-size:17px;display:flex;align-items:center;padding:0 18px;color:#6b6b73}}
.bw .pg{{padding:34px 44px 44px;position:relative}}
.bw .nav{{display:flex;justify-content:space-between;align-items:center}}
.bw .nav b{{font-family:Disp;font-weight:700;font-size:26px;letter-spacing:-.03em}}
.bw .nav span{{display:flex;gap:22px;margin-right:64px}}
.bw .nav .navtx{{font-style:normal;font-family:Text;font-weight:600;font-size:21px;color:#0B0B0C}}
.bw .nav span u{{width:64px;height:10px;border-radius:5px;background:#DADADF;text-decoration:none}}
.bw .hero{{margin-top:56px;font-family:Disp;font-weight:600;font-size:52px;letter-spacing:-.04em;line-height:1.02;max-width:640px}}
.bw .lede{{margin-top:18px;font-size:22px;color:#55555c;max-width:560px;line-height:1.4}}
.bw .btn{{margin-top:28px;display:inline-flex;align-items:center;gap:10px;padding:18px 28px;border-radius:14px;background:{ACCENT};color:#fff;font-weight:600;font-size:22px}}
.bw .tiles{{display:flex;gap:16px;margin-top:38px;margin-right:40px}}
.bw .tiles div{{flex:1;height:74px;border-radius:12px;background:#F0F0F3}}
.pin{{position:absolute;width:42px;height:42px;border-radius:50%;background:{ACCENT_DARK};color:#fff;font-family:Mono;font-size:18px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 6px rgba(102,125,255,.25)}}
.legend{{display:flex;flex-direction:column;gap:14px;margin-top:34px}}
.legend div{{display:flex;gap:18px;font-size:25px;line-height:1.35;align-items:baseline}}
.legend b{{font-family:Mono;font-weight:500;color:var(--acc);font-size:20px;min-width:34px}}
/* palette */
.palette h2{{margin-top:40px}}
.sw{{margin-top:auto;display:flex;flex-direction:column;gap:18px}}
.sw .row{{display:flex;gap:18px;height:150px}}
.sw .c{{flex:1;border-radius:20px;padding:22px 24px;display:flex;flex-direction:column;justify-content:flex-end;border:1.5px solid rgba(127,127,127,.25)}}
.sw .c b{{font-family:Disp;font-weight:600;font-size:27px;letter-spacing:-.02em}}
.sw .c span{{font-family:Mono;font-size:17px;opacity:.75;margin-top:4px}}
/* flow */
.flow h2{{margin-top:40px}}
.fl{{margin-top:auto;display:flex;flex-direction:column;position:relative}}
.fl:before{{content:"";position:absolute;left:35px;top:40px;bottom:40px;width:2px;background:linear-gradient(var(--acc),rgba(127,127,127,.25))}}
.st{{display:flex;gap:34px;align-items:center;padding:26px 0;position:relative}}
.st .dot{{width:72px;height:72px;flex:none;border-radius:18px;border:1.5px solid rgba(127,127,127,.35);display:flex;align-items:center;justify-content:center;font-family:Mono;font-size:20px;background:inherit}}
.ink .st .dot{{background:#161618}}
.paper .st .dot{{background:#fff}}
.st.hl .dot{{background:var(--acc);border-color:var(--acc);color:#fff}}
.st h3{{font-family:Disp;font-weight:600;font-size:46px;letter-spacing:-.03em}}
.st p{{font-size:25px;opacity:.65;margin-top:6px}}
/* ===== blue theme ===== */
.blue{{background:{ACCENT};color:#FFFFFF;--acc:#0B0B0C;--fg:#FFFFFF}}
.blue .grid{{opacity:.12}}
.blue .row .track{{background:rgba(255,255,255,.22)}}
.blue .row.hl .fill{{background:#0B0B0C}}
.blue .col .bar{{background:#fff;opacity:.35}}
.blue .col.hl .bar{{background:#0B0B0C;opacity:1}}
.blue .card.good{{background:rgba(255,255,255,.12);border-color:#fff}}
.blue .card.good .lb{{color:#fff}}
.blue .card.bad .tx{{opacity:.78}}
.blue .card.bad .sm{{opacity:.8}}
.blue .ctabox .btn{{background:#0B0B0C}}
.blue .st .dot{{background:rgba(255,255,255,.12)}}
.blue .st.hl .dot{{background:#0B0B0C;border-color:#0B0B0C}}
/* ===== style: editorial ===== */
.st-editorial .grid,.st-editorial .glow{{display:none}}
.st-editorial .top{{padding-bottom:26px;border-bottom:2px solid currentColor}}
.st-editorial .foot{{border-top:2px solid currentColor;padding-top:22px;opacity:.75}}
.st-editorial h1{{font-weight:500;letter-spacing:-.055em}}
.st-editorial h2{{font-weight:500;letter-spacing:-.045em;font-size:72px}}
.st-editorial .kicker:before{{display:none}}
.st-editorial .kicker{{font-size:20px;opacity:.7}}
.st-editorial .big{{font-weight:500}}
.st-editorial .card,.st-editorial .ctabox,.st-editorial .bw{{border-radius:4px}}
.st-editorial .ctabox .btn{{border-radius:4px}}
.st-editorial .row .track,.st-editorial .row .fill{{border-radius:0;height:14px}}
.st-editorial .col .bar{{border-radius:0}}
/* ===== style: bold ===== */
.st-bold .grid,.st-bold .glow{{display:none}}
.st-bold .body{{order:1}}
.st-bold .top{{order:2;margin-top:34px}}
.st-bold .foot{{order:3;margin-top:18px}}
.st-bold .mark svg{{height:46px}}
.st-bold h1{{font-weight:700;letter-spacing:-.06em;line-height:.9}}
.st-bold h2{{font-weight:700;letter-spacing:-.05em;font-size:76px;line-height:.98}}
.st-bold .big{{font-weight:700;letter-spacing:-.075em}}
.st-bold .kicker{{opacity:.85}}
/* ===== style: minimal ===== */
.st-minimal .grid,.st-minimal .glow,.st-minimal .grain{{display:none}}
.st-minimal .top{{justify-content:center}}
.st-minimal .meta{{display:none}}
.st-minimal .mark svg{{height:30px}}
.st-minimal .body{{text-align:center;align-items:center}}
.st-minimal .kicker{{justify-content:center}}
.st-minimal .kicker:before{{display:none}}
.st-minimal h1{{font-weight:500;letter-spacing:-.05em}}
.st-minimal h2{{font-weight:500}}
.st-minimal p.lead{{margin-left:auto;margin-right:auto}}
.st-minimal .big{{margin-left:0}}
.st-minimal .items,.st-minimal .hb,.st-minimal .cmp,.st-minimal .fl,.st-minimal .bw,.st-minimal .sw,.st-minimal .chart,.st-minimal .xl,.st-minimal .ctabox,.st-minimal .legend{{text-align:left;align-self:stretch}}
.st-minimal .foot{{justify-content:center;text-align:center}}
/* ===== style: poster ===== */
.st-poster .grid{{display:none}}
.deco{{position:absolute;z-index:1;font-family:Disp;font-weight:700;line-height:.78;letter-spacing:-.07em;white-space:nowrap;
 color:transparent;-webkit-text-stroke:4px var(--fg);opacity:.2;pointer-events:none}}
.st-poster h1{{font-weight:700;letter-spacing:-.06em}}
.st-poster h2{{font-weight:700}}
.st-poster .top{{border:1.5px solid rgba(127,127,127,.35);border-radius:999px;padding:16px 26px}}
.st-poster .mark svg{{height:30px}}
/* photo */
.photo{{color:#fff}}
.photo .bgimg{{position:absolute;inset:0;background-size:cover;background-position:center;z-index:0}}
.photo .shade{{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(11,11,12,.55) 0%,rgba(11,11,12,.05) 30%,rgba(11,11,12,.15) 52%,rgba(11,11,12,.88) 100%)}}
.photo.shade-full .shade{{background:rgba(11,11,12,.55)}}
.photo.shade-blue .shade{{background:linear-gradient(180deg,rgba(59,43,255,.15) 0%,rgba(59,43,255,.0) 35%,rgba(59,43,255,.92) 100%)}}
.photo h1{{margin-top:auto;font-size:100px;text-shadow:0 2px 30px rgba(0,0,0,.25)}}
.photo p.lead{{margin-top:30px;opacity:.9}}
.photo .credit{{position:absolute;z-index:3;right:88px;bottom:40px;font-family:Mono;font-size:15px;opacity:.65;letter-spacing:.02em}}
.photo .grid,.photo .glow{{display:none}}
.photo .acc{{color:#9AA8FF}}
.photo.shade-blue .acc{{color:#0B0B0C}}
"""


_POST_DIR = "."
LOGO_SVG = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text()


def logo(theme):
    fg = INK if theme == "paper" else "#FFFFFF"
    dot = {"ink": ACCENT_DARK, "paper": ACCENT, "blue": INK}.get(theme, ACCENT)
    return (LOGO_SVG.replace('fill="#FFFFFF"', f'fill="{fg}"').replace('fill="#667DFF"', f'fill="{dot}"')
            .replace('<title>nexulabs</title>', ''))


def frame(slide, idx, total, series, inner, foot_left="", foot_right="", style="studio"):
    theme = slide.get("theme", "paper")
    glow = ""
    if slide.get("glow", theme == "ink"):
        glow = f'<div class="glow{" low" if slide.get("glow_low") else ""}"></div>'
    deco = ""
    if style == "poster" and slide.get("deco", None) != "":
        d = html.escape(str(slide.get("deco", f"{idx:02d}")))
        size = slide.get("deco_size", 880 if len(d) <= 2 else 520)
        deco = f'<div class="deco" style="font-size:{size}px;right:-40px;bottom:-60px">{d}</div>'
    photo = ""
    if slide["type"] == "photo":
        img = (Path(_POST_DIR) / slide["image"]).resolve().as_uri()
        photo = f'<div class="bgimg" style="background-image:url({img});background-position:{slide.get("focus","center")}"></div><div class="shade"></div>'
        if slide.get("credit"):
            photo += f'<div class="credit">{html.escape(slide["credit"])}</div>'
    shade = f" shade-{slide['shade']}" if slide.get("shade") else ""
    return f"""<section class="s {theme} {slide['type']} st-{style}{shade}">
{photo}{glow}<div class="grid"></div>{deco}
<div class="top"><div class="mark">{logo(theme)}</div>
<div class="meta">{html.escape(series)}{f" &nbsp;·&nbsp; {idx:02d}/{total:02d}" if total > 1 else ""}</div></div>
<div class="body">{inner}</div>
<div class="foot"><div class="src">{foot_left}</div><div>{foot_right}</div></div>
<div class="grain"></div></section>"""


def kick(slide):
    k = slide.get("kicker")
    return f'<div class="kicker" style="margin-top:96px">{md(k)}</div>' if k else '<div style="height:96px"></div>'


def src(slide):
    s = slide.get("source")
    return f"Source: {html.escape(s)}" if s else ""


def build(slide, idx, total, series, style="studio"):
    t = slide["type"]
    fr = ""
    if t == "cover":
        inner = f"""{kick(slide)}
<h1 style="font-size:{slide.get('size',112)}px">{md(slide['headline'])}</h1>
{f'<p class="lead">{md(slide["sub"])}</p>' if slide.get('sub') else ''}<div style="height:70px"></div>"""
        fr = '<div class="swipe">Swipe <b>→</b></div>' if total > 1 else ""
    elif t == "stat":
        v = html.escape(slide["value"])
        m = re.match(r"^([^%x+£$]*)([%x+]?)$", v)
        num, suf = (m.group(1), m.group(2)) if m else (v, "")
        inner = f"""{kick(slide)}
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
        inner = f"""{kick(slide)}
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
        inner = f"""{kick(slide)}
<h2>{md(slide['title'])}</h2><div class="hb">{rows}</div><div style="height:56px"></div>"""
    elif t == "list":
        items = "".join(
            f'<div class="it"><div class="n">{i+1:02d}</div><div><h3>{md(a)}</h3>'
            f'{f"<p>{md(b)}</p>" if b else ""}</div></div>' for i, (a, b) in enumerate(slide["items"]))
        inner = f"""{kick(slide)}
<h2{f' style="font-size:{slide["title_size"]}px"' if slide.get('title_size') else ''}>{md(slide['title'])}</h2><div class="items">{items}</div><div style="height:40px"></div>"""
    elif t == "quote":
        inner = f"""<div class="qm" style="margin-top:auto">“</div><h1>{md(slide['text'])}</h1>
{f'<p class="lead">{md(slide["sub"])}</p>' if slide.get('sub') else ''}<div style="height:70px"></div>"""
    elif t == "cta":
        inner = f"""{kick(slide)}
<h1 style="font-size:{slide.get('size',100)}px">{md(slide['headline'])}</h1>
{f'<p class="lead">{md(slide["body"])}</p>' if slide.get('body') else ''}
<div class="ctabox"><div><div class="l">{md(slide.get('cta_label','Talk to us'))}</div>
<div class="r">{md(slide.get('cta','nexulabs.co.uk'))}</div></div><div class="btn">→</div></div><div style="height:40px"></div>"""
    elif t == "compare":
        bad, good = slide["instead"], slide["try"]
        def card(c, cls, label, ic):
            sm = f'<div class="sm">{md(c[1])}</div>' if len(c) > 1 and c[1] else ""
            return f'<div class="card {cls}"><div class="lb"><span class="ico">{ic}</span>{label}</div><div class="tx">{md(c[0])}</div>{sm}</div>'
        inner = f"""{kick(slide)}
<h2{f' style="font-size:{slide["title_size"]}px"' if slide.get('title_size') else ''}>{md(slide['title'])}</h2><div class="cmp">{card(bad,'bad',slide.get('instead_label','Instead of'),'×')}{card(good,'good',slide.get('try_label','Try'),'✓')}</div><div style="height:48px"></div>"""
    elif t == "browser":
        site = slide["site"]
        pins = slide.get("pins", [])
        pos = [("top:20px;right:24px", 0), ("top:118px;right:24px", 1), ("top:300px;right:24px", 2), ("bottom:24px;right:24px", 3)]
        pin_html = "".join(f'<div class="pin" style="{pos[i][0]}">{i+1:02d}</div>' for i in range(min(len(pins), 4)))
        legend = "".join(f'<div><b>{i+1:02d}</b><span>{md(x)}</span></div>' for i, x in enumerate(pins))
        inner = f"""{kick(slide) if slide.get('kicker') else '<div style="height:40px"></div>'}
<h2>{md(slide['title'])}</h2>
<div class="bw"><div class="bar"><i></i><i></i><i></i><div class="url">{html.escape(site.get('url','yourbusiness.co.uk'))}</div></div>
<div class="pg"><div class="nav"><b>{html.escape(site.get('brand','Your Business'))}</b><span>{f'<em class="navtx">{html.escape(site["nav_text"])}</em>' if site.get('nav_text') else '<u></u><u></u>'}</span></div>
<div class="hero">{md(site['headline'])}</div><div class="lede">{md(site.get('lede',''))}</div>
<div class="btn">{html.escape(site.get('button','Get a quote'))} →</div><div class="tiles"><div></div><div></div><div></div></div>{pin_html}</div></div>
{f'<div class="legend">{legend}</div>' if pins else ''}<div style="height:40px"></div>"""
    elif t == "photo":
        inner = f"""{kick(slide) if slide.get('kicker') else ''}
<h1 style="font-size:{slide.get('size',100)}px">{md(slide['headline'])}</h1>
{f'<p class="lead">{md(slide["sub"])}</p>' if slide.get('sub') else ''}<div style="height:60px"></div>"""
        fr = '<div class="swipe">Swipe <b>→</b></div>' if total > 1 and idx == 1 else ""
    elif t == "flow":
        hl = slide.get("highlight", [])
        steps = "".join(
            f'<div class="st{" hl" if i in hl else ""}"><div class="dot">{i+1:02d}</div><div><h3>{md(a)}</h3>{f"<p>{md(b)}</p>" if b else ""}</div></div>'
            for i, (a, b) in enumerate(slide["steps"]))
        inner = f"""{kick(slide)}
<h2{f' style="font-size:{slide["title_size"]}px"' if slide.get('title_size') else ''}>{md(slide['title'])}</h2><div class="fl">{steps}</div><div style="height:40px"></div>"""
    elif t == "palette":
        rows = ""
        for row in slide["rows"]:
            cells = "".join(
                f'<div class="c" style="background:{c[1]};color:{c[2] if len(c)>2 else "#fff"}"><b>{html.escape(c[0])}</b><span>{html.escape(c[1].upper())}</span></div>' for c in row)
            rows += f'<div class="row">{cells}</div>'
        inner = f"""{kick(slide)}
<h2>{md(slide['title'])}</h2>{f'<p class="lead" style="margin-top:24px">{md(slide["sub"])}</p>' if slide.get('sub') else ''}<div class="sw">{rows}</div><div style="height:48px"></div>"""
    else:
        raise ValueError(f"unknown slide type {t}")
    return frame(slide, idx, total, series, inner, src(slide), fr, style)


def render(spec_path):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    spec_path = Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text())
    out = spec_path.parent
    global _POST_DIR
    _POST_DIR = str(out)
    slides = spec["slides"]
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome") if Path("/usr/bin/google-chrome").exists() else p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        for i, s in enumerate(slides, 1):
            doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{build(s, i, len(slides), spec.get('series',''), spec.get('style','studio'))}</body></html>"
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
