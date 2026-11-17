#!/usr/bin/env python3
"""Writes slide-01..03.html for this post. One concept CRM (made-up firm: Hollowbeck Landscapes),
drawn once here as real HTML, then shot three ways. Run: python3 build.py"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
BG, INK, PAPER, ACC = "#101319", "#0F1217", "#F4F5F7", "#9BD5FF"

COMMON = f"""
.frame{{background:{BG};color:#F3F5F8;font-family:Geist}}
.h{{font-family:InterTight;font-weight:700;letter-spacing:-.028em;line-height:.94;color:#F6F8FB;font-size:160px}}
.h em{{font-style:normal;color:{ACC}}}
.sub{{font:500 34px/1.28 Geist;letter-spacing:-.01em;color:#F3F5F8}}
.sub span{{color:#8D95A3}}
/* ---------- the app (interface: exempt from the small-text check) ---------- */
.app{{display:flex;background:{PAPER};color:{INK};border-radius:30px;overflow:hidden;font-family:Geist}}
.side{{width:272px;flex:none;background:#E9EBEF;border-right:1px solid #DCDFE5;padding:36px 24px}}
.brand{{display:flex;align-items:center;gap:14px;margin:0 6px 46px}}
.mark{{width:46px;height:46px;border-radius:13px;background:{INK};display:grid;place-items:center}}
.mark svg{{width:26px;height:26px}}
.brand b{{display:block;font:600 22px/1.05 Geist;letter-spacing:-.02em}}
.brand i{{display:block;font:500 16px/1.3 Geist;font-style:normal;color:#7B828E}}
.nav a{{display:flex;justify-content:space-between;align-items:center;font:500 21px/1 Geist;color:#515865;padding:15px 16px;border-radius:13px;margin-bottom:4px;letter-spacing:-.01em}}
.nav a u{{text-decoration:none;font:500 16px/1 GeistMono;color:#6F7683}}
.nav a.on{{background:#fff;color:{INK};font-weight:600;box-shadow:0 1px 2px rgba(15,18,23,.08)}}
.main{{flex:1;padding:38px 40px 0}}
.top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:34px}}
.top h3{{font:600 46px/1 Geist;letter-spacing:-.035em}}
.top .r{{display:flex;gap:14px;align-items:center}}
.find{{width:270px;height:52px;border-radius:14px;background:#E9EBEF;display:flex;align-items:center;padding:0 18px;font:500 18px Geist;color:#8B92A0}}
.new{{height:52px;border-radius:14px;background:{INK};color:#fff;font:600 19px/52px Geist;padding:0 24px;letter-spacing:-.01em}}
.cols{{display:flex;gap:22px}}
.col{{flex:1;min-width:0}}
.col h4{{color:#515865;display:flex;justify-content:space-between;font:600 19px/1 Geist;color:#515865;margin:0 6px 18px;letter-spacing:-.005em}}
.col h4 u{{text-decoration:none;font:500 16px/1.2 GeistMono;color:#6F7683}}
.card{{color:{INK};background:#fff;border-radius:18px;padding:22px 22px 20px;margin-bottom:16px;box-shadow:0 1px 1px rgba(15,18,23,.05),0 6px 16px rgba(15,18,23,.05)}}
.card b{{display:block;font:600 24px/1.12 Geist;letter-spacing:-.025em;margin-bottom:8px}}
.card p{{font:500 18px/1.25 Geist;color:#737A87;margin-bottom:20px}}
.card .f{{display:flex;justify-content:space-between;align-items:center;font:500 18px/1 Geist;color:#515865}}
.pill{{font:600 15px/1 Geist;padding:8px 12px;border-radius:99px;background:#ECEEF1;color:#515865;letter-spacing:0}}
.card.lit{{background:{ACC};box-shadow:0 2px 2px rgba(15,18,23,.1),0 18px 40px rgba(44,120,180,.35)}}
.card.lit p{{color:#274A66}}.card.lit .f{{color:#14324A}}.card.lit .pill{{background:{INK};color:#fff}}
.slot{{height:158px;border-radius:18px;border:2.5px dashed #B9C0CB;margin-bottom:16px}}
"""

LEAF = '<svg viewBox="0 0 24 24" fill="none"><path d="M5 19C5 10 10 5 19 5c0 9-5 14-14 14Z" fill="#9BD5FF"/><path d="M5 19 13 11" stroke="#0F1217" stroke-width="1.8" stroke-linecap="round"/></svg>'


def card(title, who, pill, right, cls=""):
    return (f'<div class="card {cls}"><b>{title}</b><p>{who}</p>'
            f'<div class="f"><span class="pill">{pill}</span><span>{right}</span></div></div>')


ENQ = [("Front garden", "Mr Okafor, Pelton", "Website", "Tue 08:52"),
       ("Fence, 14 panels", "J. Whitfield, Durham", "Phone", "Mon 15:20"),
       ("Artificial lawn", "Mr Tindale, Sacriston", "Website", "Mon 09:14"),
       ("Gravel path", "P. Nowak, Langley Park", "Website", "Fri 17:03")]
QUO = [("Patio and steps", "Mrs Hallam, Lanchester", "Quote sent", "£4,200"),
       ("Block-paved drive", "D. Carr, Consett", "Quote sent", "£6,850"),
       ("Raised beds, six", "Mrs Akhtar, Esh Winning", "Follow up Thu", "£1,900")]
BOO = [("Raised decking", "S. Iqbal, Stanley", "Thu 26 Nov", "2 days"),
       ("New turf, back lawn", "A. Robson, Burnhope", "Mon 30 Nov", "1 day"),
       ("Retaining wall", "Mr Lyle, Witton Gilbert", "Wed 2 Dec", "3 days")]
DON = [("Hedge and border tidy", "K. Bains, Durham", "Done", "Fri 13 Nov"),
       ("Pergola", "T. Coulson, Esh", "Done", "Wed 11 Nov"),
       ("Garden clearance", "R. Maddison, Annfield Plain", "Done", "Mon 9 Nov")]


def col(name, items, lit=None, slot_at=None, skip=None):
    out = [f'<div class="col"><h4>{name}<u>{len(items)}</u></h4>']
    for i, it in enumerate(items):
        if slot_at == i:
            out.append('<div class="slot"></div>')
        if skip == i:
            continue
        out.append(card(*it, cls="lit" if lit == i else ""))
    if slot_at is not None and slot_at >= len(items):
        out.append('<div class="slot"></div>')
    return "".join(out) + "</div>"


def side():
    nav = [("Enquiries", "4", ""), ("Quotes", "3", ""), ("Jobs", "13", "on"), ("Bookings", "3", ""), ("Customers", "86", ""), ("Calendar", "", "")]
    return ('<div class="side"><div class="brand"><div class="mark">' + LEAF + '</div><div><b>Hollowbeck</b><i>Landscapes</i></div></div><div class="nav">'
            + "".join(f'<a class="{c}">{n}<u>{k}</u></a>' for n, k, c in nav) + "</div></div>")


def top():
    return '<div class="top"><h3>Jobs</h3><div class="r"><div class="find">Search jobs and customers</div><div class="new">New enquiry</div></div></div>'


# ---------------------------------------------------------------- frame 1
S1 = f"""<style>{COMMON}
.h1{{position:absolute;left:68px;top:88px}}
.s1{{position:absolute;left:72px;top:416px;width:960px}}
.glow{{position:absolute;left:-100px;top:480px;width:1300px;height:1000px;background:radial-gradient(closest-side,rgba(110,190,255,.30),rgba(110,190,255,0) 100%);filter:blur(10px)}}
.stage{{position:absolute;left:72px;top:620px;perspective:2300px;perspective-origin:0% 20%}}
.app{{width:1900px;height:1300px;transform-origin:0 0;transform:rotateY(24deg) rotateX(5deg);
  box-shadow:0 0 0 1px rgba(255,255,255,.5) inset,-34px 50px 90px rgba(0,0,0,.6),-8px 14px 26px rgba(0,0,0,.45)}}
.app .cols{{gap:VARGAPpx}}.app .col{{flex:none;width:VARCOLpx}}
</style>
<div class="glow"></div>
<div class="h h1" data-ui>Every job.<br><em>One screen.</em></div>
<div class="sub s1">A custom CRM, built around how you work.<br><span>Concept for a made-up firm.</span></div>
<div class="stage" data-ui data-bleed><div class="app">{side()}<div class="main">{top()}<div class="cols">
{col("Enquiry", ENQ[:3])}{col("Quoted", QUO, lit=0)}{col("Booked", BOO)}{col("Done", DON)}
</div></div></div></div>
<!--grain:0.05-->
""".replace("VARGAP", "70").replace("VARCOL", "276")

# ---------------------------------------------------------------- frame 2
T2 = "rotateX(48deg) rotateZ(-22deg) scale(1.34)"
B2 = [(t, w, d, "") for t, w, d, _ in BOO]
S2 = f"""<style>{COMMON}
.h2{{position:absolute;left:68px;top:88px;z-index:9}}
.world{{position:absolute;left:0;top:0;width:1080px;height:1350px;perspective:1700px;perspective-origin:50% 38%}}
.plane{{position:absolute;left:-250px;top:770px;width:1700px;transform-origin:50% 40%;transform:{T2}}}
.plane .cols{{gap:26px;position:relative}}
.plane .col h4{{visibility:hidden}}
.plane .col.gone{{visibility:hidden}}
.plane .card{{box-shadow:0 1px 1px rgba(15,18,23,.08),0 10px 22px rgba(15,18,23,.10)}}
.bed{{position:absolute;inset:-90px -200px -600px;background:#E6E9EE;border-radius:34px}}
.shadow{{position:absolute;left:612px;top:96px;width:360px;height:150px;border-radius:26px;background:rgba(15,25,40,.30);filter:blur(16px);transform:rotateZ(5deg)}}
.fly{{position:absolute;left:585px;top:36px;width:383px;transform:rotateZ(5deg)}}
.plane.lift{{transform:{T2} translateZ(70px)}}
.fly .card{{margin:0;box-shadow:0 0 0 1px rgba(255,255,255,.4) inset}}
.slot{{border-color:#AEB6C2}}
.slot.to{{border-color:#4FA2DE;background:rgba(155,213,255,.28)}}
.topfade{{position:absolute;left:0;top:0;width:1080px;height:640px;background:linear-gradient(180deg,{BG} 0,{BG} 66%,rgba(16,19,25,0) 100%);z-index:5}}
.vig{{position:absolute;left:0;top:1010px;width:1080px;height:340px;background:linear-gradient(180deg,rgba(16,19,25,0),{BG} 92%);z-index:4}}
</style>
<div class="world" data-ui data-bleed>
 <div class="plane"><div class="bed"></div><div class="cols">
<div class="col gone"></div>{col("Quoted", QUO, slot_at=0, skip=0)}<div class="col"><h4>Booked<u>4</u></h4><div class="slot to"></div>{"".join(card(*c) for c in B2)}</div><div class="col gone"></div>
 </div><div class="shadow"></div></div>
 <div class="plane lift"><div class="fly">{card(*QUO[0][:2], "Booked", "Thu 3 Dec", cls="lit")}</div><div class="cols" style="visibility:hidden">{col("Enquiry", ENQ)}</div></div>
</div>
<div class="vig"></div><div class="topfade"></div>
<div class="h h2" data-ui>See where<br><em>every job</em><br>is up to.</div>
<!--grain:0.05-->
"""

# ---------------------------------------------------------------- frame 3
S3 = f"""<style>{COMMON}
.h3{{position:absolute;left:68px;top:88px}}
.url{{position:absolute;left:72px;top:416px;font:600 60px/1 InterTight;letter-spacing:-.02em;color:{ACC}}}
.logo3{{position:absolute;right:72px;top:432px}}.logo3 .nx-logo{{height:40px}}
.glow3{{position:absolute;left:0;top:520px;width:1200px;height:1000px;background:radial-gradient(closest-side,rgba(110,190,255,.30),rgba(110,190,255,0));filter:blur(10px)}}
.stage3{{position:absolute;left:72px;top:640px;width:936px;perspective:2300px;perspective-origin:100% 20%}}
.rec{{width:1010px;height:1100px;margin-left:-74px;transform-origin:100% 0;transform:rotateY(-13deg) rotateX(4deg);background:{PAPER};color:{INK};border-radius:38px;padding:58px 64px 0;
  box-shadow:0 0 0 1px rgba(255,255,255,.5) inset,34px 50px 90px rgba(0,0,0,.6),8px 14px 26px rgba(0,0,0,.45)}}
.rec .k{{font:500 23px/1 GeistMono;color:#6F7683;margin-bottom:22px}}
.rec .t{{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}}
.rec .t b{{font:600 76px/1 Geist;letter-spacing:-.04em}}
.rec .t span{{font:600 28px/1 Geist;background:{ACC};color:{INK};padding:17px 28px;border-radius:99px}}
.rec .w{{font:500 34px/1.2 Geist;color:#636A77;letter-spacing:-.01em;margin-bottom:56px}}
.ev{{position:relative;display:flex;justify-content:space-between;align-items:baseline;font:600 40px/1 Geist;letter-spacing:-.02em;padding:0 0 64px 66px}}
.ev u{{text-decoration:none;font:500 26px/1 GeistMono;color:#6F7683;letter-spacing:0}}
.ev:after{{content:"";position:absolute;left:13px;top:34px;bottom:-2px;width:3px;background:#D0D5DC}}
.ev:last-child:after{{display:none}}
.ev:before{{content:"";position:absolute;left:0;top:4px;width:29px;height:29px;border-radius:50%;background:{INK}}}
.ev.now:before{{background:{ACC};box-shadow:0 0 0 5px {PAPER},0 0 0 8px {INK}}}
.ev.next{{color:#9BA2AE}}.ev.next:before{{background:{PAPER};box-shadow:inset 0 0 0 3px #AEB5C0}}
</style>
<div class="glow3"></div>
<div class="h h3" data-ui>See what<br>we build.</div>
<div class="url">nexulabs.co.uk</div>
<div class="logo3"><!--logo:#F6F8FB,{ACC}--></div>
<div class="stage3" data-ui data-bleed><div class="rec">
 <div class="k">JOB 0214 &nbsp;/&nbsp; HOLLOWBECK LANDSCAPES</div>
 <div class="t"><b>Patio and steps</b><span>Booked</span></div>
 <div class="w">Mrs Hallam, Lanchester</div>
 <div class="ev">Enquiry from the website<u>Mon 09:14</u></div>
 <div class="ev">Quote sent, £4,200<u>Mon 16:40</u></div>
 <div class="ev now">Booked for Thu 3 Dec<u>Wed 11:02</u></div>
 <div class="ev next">Job done<u></u></div>
</div></div>
<!--grain:0.05-->
"""

for i, s in enumerate((S1, S2, S3), 1):
    (HERE / f"slide-{i:02d}.html").write_text(s)
print("wrote 3 slides")
