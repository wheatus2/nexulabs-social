#!/usr/bin/env python3
"""Nexulabs Instagram renderer.

Usage:  python3 render.py posts/<id>/post.json
Writes  posts/<id>/slide-01.jpg ... (1080x1350, 4:5 portrait)

Slide types: cover, stat, bars, hbars, list, quote, cta, compare, browser, palette, flow, photo (Unsplash background: "image", "credit", optional "shade": full|blue, "focus")
browser "site" may include "nav_text" (e.g. a phone number shown in the mock header); compare, list and flow may include "title_size".
Text markup: *word* -> accent colour. Line breaks with \n.
Themes: "ink" (dark), "paper" (light) or "blue" (brand blue background).
Post-level "style": studio | editorial | bold | minimal | poster | aurora | neon | spectrum | glass (rotate; never the same two posts running).
Gradient styles (aurora, neon, spectrum, glass) take a post-level "palette": electric | ultraviolet | ocean | dusk.
Any post/slide can add "pattern": dots | stripes | waves | contours | halftone | isometric | rings | bauhaus | chevrons | plus | diagonal-grid (optional "pattern_opacity").
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
    t = re.sub(r"\*(.+?)\*", r'<span class="acc">\1</span>', t, flags=re.S)
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
/* ===== colour / gradient styles: aurora, neon, spectrum, glass ===== */
.gx{{color:#fff;--fg:#fff}}
.gx .grid{{opacity:.06}}
.gx .glow{{display:none}}
.gx .fx{{position:absolute;inset:0;z-index:0;overflow:hidden}}
.gx .fx i{{position:absolute;display:block;border-radius:50%}}
.gx .acc{{background:linear-gradient(95deg,var(--c3),var(--c4));-webkit-background-clip:text;background-clip:text;color:transparent}}
.gx .kicker:before{{background:linear-gradient(90deg,var(--c3),var(--c4))}}
.gx .grain{{opacity:.14}}
.gx .card,.gx .ctabox,.gx .it,.gx .sw .c{{border-color:rgba(255,255,255,.22)}}
.gx .card.good{{border-color:var(--c3);background:rgba(255,255,255,.08)}}
.gx .card.good .lb,.gx .legend b,.gx .it .n{{color:var(--c3)}}
.gx .ctabox .btn{{background:linear-gradient(135deg,var(--c3),var(--c4))}}
.gx .col.hl .bar,.gx .row.hl .fill,.gx .st.hl .dot{{background:linear-gradient(135deg,var(--c3),var(--c4));border-color:transparent;opacity:1}}
.gx .col.hl .v,.gx .row.hl .lab{{color:var(--c3)}}
.gx .col .bar,.gx .row .fill{{background:#fff;opacity:.3}}
.gx .row .track{{background:rgba(255,255,255,.14)}}
.gx .st .dot{{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.25)}}
.gx .big small{{background:linear-gradient(95deg,var(--c3),var(--c4));-webkit-background-clip:text;background-clip:text;color:transparent}}
.st-aurora.gx{{background:var(--c1)}}
.st-aurora .fx i{{filter:blur(90px);opacity:.9}}
.st-aurora .fx:after,.st-glass .fx:after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 25%,var(--c1) 88%)}}
.st-neon.gx{{background:#07070A}}
.st-neon .fx i.ring{{border:3px solid transparent;background:linear-gradient(#07070A,#07070A) padding-box,conic-gradient(from 0deg,var(--c2),var(--c3),var(--c4),var(--c2)) border-box;box-shadow:0 0 80px -10px var(--c3)}}
.st-neon .fx i.orb{{background:radial-gradient(circle at 35% 30%,#fff 0%,var(--c3) 18%,var(--c2) 55%,transparent 72%);filter:blur(2px);opacity:.9}}
.st-neon .fx i.haze{{filter:blur(120px);opacity:.55}}
.st-spectrum.gx{{background:var(--c2)}}
.st-spectrum .fx{{background:linear-gradient(215deg,var(--c3) -10%,var(--c4) 22%,var(--c2) 55%,var(--c1) 100%)}}
.st-spectrum .fx i.disc{{background:radial-gradient(circle at 30% 30%,rgba(255,255,255,.55),rgba(255,255,255,.05) 60%,transparent 70%);mix-blend-mode:soft-light}}
.st-spectrum .fx i.line{{border:2px solid rgba(255,255,255,.35);background:none}}
.st-spectrum h1,.st-spectrum h2{{font-weight:700;letter-spacing:-.055em}}
.st-spectrum .acc,.st-spectrum .big small{{background:none;-webkit-background-clip:initial;background-clip:initial;color:var(--c3)}}
.st-glass.gx{{background:var(--c1)}}
.st-glass .fx i{{filter:blur(50px);opacity:.75}}
.st-glass .body{{background:rgba(12,10,40,.38);border:1.5px solid rgba(255,255,255,.28);border-radius:40px;padding:0 54px 40px;margin:36px -20px 0;
 -webkit-backdrop-filter:blur(28px) saturate(140%);backdrop-filter:blur(28px) saturate(140%);box-shadow:0 30px 80px -30px rgba(0,0,0,.45)}}
.st-glass .foot{{margin-top:26px}}
/* ===== patterns ===== */
.pat{{position:absolute;inset:0;z-index:1;pointer-events:none;color:var(--pc,currentColor)}}
.pat svg{{position:absolute;inset:0;width:100%;height:100%}}
.has-pat .grid{{display:none}}
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



PALETTES = {
    # c1 = base, c2 = brand blue family, c3/c4 = highlight pair (used for gradient text & accents)
    "electric":    ("#0A0A2E", "#3B2BFF", "#00D1FF", "#A78BFA"),
    "ultraviolet": ("#14082E", "#3B2BFF", "#C084FC", "#F472B6"),
    "ocean":       ("#03122E", "#0C23A8", "#22D3EE", "#667DFF"),
    "dusk":        ("#120A2A", "#4F46E5", "#F0ABFC", "#818CF8"),
}
GRADIENT_STYLES = {"aurora", "neon", "spectrum", "glass"}


def fx_layer(style, idx, pal):
    """Decorative gradient shapes; positions shift per slide so each slide looks different."""
    import random
    rnd = random.Random(idx * 7919 + len(style))
    c1, c2, c3, c4 = PALETTES.get(pal, PALETTES["electric"])
    out = []
    if style in ("aurora", "glass"):
        for k, (col, size) in enumerate(((c2, 900), (c3, 700), (c4, 760), (c2, 600))):
            x = rnd.randint(-350, 650)
            y = rnd.randint(-400, 300) if k % 2 else rnd.randint(-200, 900)
            out.append(f'<i style="width:{size}px;height:{size}px;left:{x}px;top:{y}px;background:{col}"></i>')
    elif style == "neon":
        out.append(f'<i class="haze" style="width:900px;height:900px;left:{rnd.randint(-300,500)}px;top:{rnd.randint(-300,700)}px;background:{c2}"></i>')
        out.append(f'<i class="haze" style="width:600px;height:600px;left:{rnd.randint(200,700)}px;top:{rnd.randint(500,1100)}px;background:{c4}"></i>')
        r = rnd.choice([520, 640, 760])
        out.append(f'<i class="ring" style="width:{r}px;height:{r}px;right:{rnd.randint(-260,-60)}px;top:{rnd.randint(-160,260)}px"></i>')
        out.append(f'<i class="ring" style="width:{r-180}px;height:{r-180}px;right:{rnd.randint(-120,40)}px;top:{rnd.randint(-60,360)}px;opacity:.6"></i>')
        o = rnd.choice([150, 190, 230])
        out.append(f'<i class="orb" style="width:{o}px;height:{o}px;left:{rnd.randint(600,860)}px;top:{rnd.randint(420,700)}px"></i>')
    elif style == "spectrum":
        for _ in range(2):
            d = rnd.randint(500, 900)
            out.append(f'<i class="disc" style="width:{d}px;height:{d}px;left:{rnd.randint(-300,600)}px;top:{rnd.randint(-300,900)}px"></i>')
        for k in range(3):
            d = 420 + k * 170
            out.append(f'<i class="line" style="width:{d}px;height:{d}px;right:{-d//2}px;top:{-d//3}px;border-color:rgba(11,11,12,.25)"></i>')
    return f'<div class="fx">{"".join(out)}</div>'


PATTERNS = ["dots", "stripes", "waves", "contours", "halftone", "isometric", "rings", "bauhaus", "chevrons", "plus", "diagonal-grid"]


def pattern_layer(name, idx, colors, opacity=None):
    """Inline SVG background patterns (1080x1350). colors = (main, accent1, accent2)."""
    import math, random
    rnd = random.Random(idx * 104729 + sum(map(ord, name)))
    main, a1, a2 = colors
    W, H = 1080, 1350
    op = opacity if opacity is not None else {"bauhaus": 1, "halftone": .5, "dots": .4}.get(name, .22)
    els = []
    if name == "dots":
        g = rnd.choice([30, 36, 44]); r = rnd.choice([2.2, 3, 3.6])
        els.append(f'<defs><pattern id="p" width="{g}" height="{g}" patternUnits="userSpaceOnUse"><circle cx="{g/2}" cy="{g/2}" r="{r}" fill="{main}"/></pattern>'
                   f'<radialGradient id="m"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'
                   f'<mask id="k"><rect width="{W}" height="{H}" fill="url(#m)"/></mask></defs>'
                   f'<rect width="{W}" height="{H}" fill="url(#p)" mask="url(#k)"/>')
    elif name == "stripes":
        ang = rnd.choice([30, 45, -35, 60]); w = rnd.choice([14, 22, 34])
        els.append(f'<defs><pattern id="p" width="{w*2}" height="{w*2}" patternUnits="userSpaceOnUse" patternTransform="rotate({ang})"><rect width="{w}" height="{w*2}" fill="{main}"/></pattern></defs><rect width="{W}" height="{H}" fill="url(#p)"/>')
    elif name == "waves":
        n = rnd.choice([14, 18, 24]); amp = rnd.randint(30, 70); fr = rnd.uniform(1.2, 2.6); ph = rnd.uniform(0, 6)
        for k in range(n):
            y0 = H * (k + .5) / n
            pts = " ".join(f"{x},{y0 + amp*math.sin(fr*2*math.pi*x/W + ph + k*.35):.1f}" for x in range(0, W + 20, 20))
            col = a1 if k % 5 == 0 else main
            els.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2"/>')
    elif name == "contours":
        cx, cy = rnd.randint(200, 880), rnd.randint(200, 1150)
        seeds = [rnd.uniform(0, 6.28) for _ in range(4)]
        for k in range(1, 26):
            R = k * 46
            pts = []
            for t in range(0, 361, 6):
                a = math.radians(t)
                rr = R * (1 + .12*math.sin(3*a + seeds[0]) + .08*math.sin(5*a + seeds[1]) + .05*math.sin(2*a + seeds[2] + k*.2))
                pts.append(f"{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}")
            col = a1 if k % 6 == 0 else main
            els.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="1.8"/>')
    elif name == "halftone":
        g = 34; cx, cy = rnd.choice([(W + 40, -40), (W*.95, -120)])
        D = math.hypot(W, H)
        for y in range(0, H + g, g):
            for x in range(0, W + g, g):
                d = math.hypot(x - cx, y - cy) / D
                r = max(0, (1 - d*2.2)) * g * .48
                if r > .6:
                    els.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{main}"/>')
    elif name == "isometric":
        g = rnd.choice([60, 80])
        for a in (30, 150, 90):
            els.append(f'<defs><pattern id="p{a}" width="{g}" height="{g}" patternUnits="userSpaceOnUse" patternTransform="rotate({a})"><line x1="0" y1="0" x2="{g}" y2="0" stroke="{main}" stroke-width="1.6"/></pattern></defs><rect width="{W}" height="{H}" fill="url(#p{a})"/>')
    elif name == "checker-unused":
        g = rnd.choice([90, 135])
        els.append(f'<defs><pattern id="p" width="{g*2}" height="{g*2}" patternUnits="userSpaceOnUse"><rect width="{g}" height="{g}" fill="{main}"/><rect x="{g}" y="{g}" width="{g}" height="{g}" fill="{main}"/></pattern></defs><rect width="{W}" height="{H}" fill="url(#p)"/>')
    elif name == "rings":
        cx, cy = rnd.choice([(W, 0), (0, H*.3), (W*.9, H), (W*.5, H*1.05)])
        for k in range(1, 30):
            els.append(f'<circle cx="{cx}" cy="{cy}" r="{k*42}" fill="none" stroke="{a1 if k%7==0 else main}" stroke-width="2"/>')
    elif name == "bauhaus":
        # bold geometric blocks in the top area, leaving the lower half for text
        cell = 230
        cols = [a1, a2, main]
        for gy in range(2):
            for gx in range(4):
                if (gx, gy) in ((0, 0), (1, 0)) or rnd.random() < .3:
                    continue
                x, y = 160 + gx * cell, 150 + gy * cell
                c = rnd.choice(cols); shape = rnd.choice(["q", "c", "h", "s", "t"])
                if shape == "q":
                    corner = rnd.choice([(x, y), (x + cell, y), (x, y + cell), (x + cell, y + cell)])
                    els.append(f'<clipPath id="c{gx}{gy}"><rect x="{x}" y="{y}" width="{cell}" height="{cell}"/></clipPath><circle cx="{corner[0]}" cy="{corner[1]}" r="{cell}" fill="{c}" clip-path="url(#c{gx}{gy})"/>')
                elif shape == "c":
                    els.append(f'<circle cx="{x+cell/2}" cy="{y+cell/2}" r="{cell*.42}" fill="{c}"/>')
                elif shape == "h":
                    els.append(f'<clipPath id="c{gx}{gy}"><rect x="{x}" y="{y}" width="{cell}" height="{cell/2}"/></clipPath><circle cx="{x+cell/2}" cy="{y+cell/2}" r="{cell/2}" fill="{c}" clip-path="url(#c{gx}{gy})"/>')
                elif shape == "s":
                    els.append(f'<rect x="{x+cell*.12}" y="{y+cell*.12}" width="{cell*.76}" height="{cell*.76}" fill="none" stroke="{c}" stroke-width="16"/>')
                else:
                    els.append(f'<polygon points="{x},{y+cell} {x+cell},{y+cell} {x+cell},{y}" fill="{c}"/>')
    elif name == "chevrons":
        g = rnd.choice([60, 80]); h2 = g/2
        els.append(f'<defs><pattern id="p" width="{g}" height="{g}" patternUnits="userSpaceOnUse"><polyline points="0,{h2+10} {h2},{10} {g},{h2+10}" fill="none" stroke="{main}" stroke-width="3"/></pattern></defs><rect width="{W}" height="{H}" fill="url(#p)"/>')
    elif name == "plus":
        g = rnd.choice([54, 72]); a = 7
        els.append(f'<defs><pattern id="p" width="{g}" height="{g}" patternUnits="userSpaceOnUse"><path d="M{g/2-a} {g/2}H{g/2+a}M{g/2} {g/2-a}V{g/2+a}" stroke="{main}" stroke-width="2.4"/></pattern></defs><rect width="{W}" height="{H}" fill="url(#p)"/>')
    elif name == "diagonal-grid":
        g = rnd.choice([70, 100])
        els.append(f'<defs><pattern id="p" width="{g}" height="{g}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0H{g}M0 0V{g}" stroke="{main}" stroke-width="1.6" fill="none"/></pattern></defs><rect width="{W}" height="{H}" fill="url(#p)"/>')
    else:
        return ""
    return f'<div class="pat" style="opacity:{op}"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">{"".join(els)}</svg></div>'

_POST_DIR = "."
_PALETTE = "electric"
_PATTERN = None
LOGO_SVG = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text()


def logo(theme, dot_override=None):
    fg = INK if theme == "paper" else "#FFFFFF"
    dot = dot_override or {"ink": ACCENT_DARK, "paper": ACCENT, "blue": INK}.get(theme, ACCENT)
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
    gx = ""
    dot = None
    if style in GRADIENT_STYLES and slide["type"] != "photo":
        pal = slide.get("palette", _PALETTE)
        c1, c2, c3, c4 = PALETTES.get(pal, PALETTES["electric"])
        gx = f' gx" style="--c1:{c1};--c2:{c2};--c3:{c3};--c4:{c4}'
        photo = fx_layer(style, idx, pal) + photo
        theme = "ink"
        dot = c3
    patname = slide.get("pattern", _PATTERN)
    if patname and patname != "none" and slide["type"] != "photo":
        if gx:
            c1, c2, c3, c4 = PALETTES.get(slide.get("palette", _PALETTE), PALETTES["electric"])
            cols = ("#FFFFFF", c3, c4)
        elif theme == "paper":
            cols = (INK, ACCENT, ACCENT_DARK)
        elif theme == "blue":
            cols = ("#FFFFFF", INK, "#9AA8FF")
        else:
            cols = (PAPER, ACCENT_DARK, ACCENT)
        photo = photo + pattern_layer(patname, idx, cols, slide.get("pattern_opacity"))
        shade += " has-pat"
    return f"""<section class="s {theme} {slide['type']} st-{style}{shade}{gx}">
{photo}{glow}<div class="grid"></div>{deco}
<div class="top"><div class="mark">{logo(theme, dot)}</div>
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
    global _POST_DIR, _PALETTE, _PATTERN
    _POST_DIR = str(out)
    _PALETTE = spec.get("palette", "electric")
    _PATTERN = spec.get("pattern")
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
