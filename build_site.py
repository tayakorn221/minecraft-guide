#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — แปลงคู่มือ .md ใน docs/ เป็นเว็บ HTML ธีม "ตำราเวท" (grimoire)
เข้าชุดกับ origin-selector.html · single-file ต่อหน้า · ไม่พึ่ง dependency ภายนอก
รัน:  python build_site.py
"""
import re, html, pathlib, sys, markdown
try:
    sys.stdout.reconfigure(encoding='utf-8')  # กัน UnicodeEncodeError ตอน print ไทยบน Windows
except Exception:
    pass

DOCS = pathlib.Path(__file__).parent / "docs"

# ── ผังหน้า: ไฟล์ .md → slug .html (ASCII = URL สวย) + ชื่อเมนู + กลุ่ม ──────────
PAGES = [
    # md filename,                         slug,                title(เมนู),         group
    ("INDEX.md",                          "index.html",        "หน้าแรก",           "home"),
    ("เลือกเผ่า-guide.md",                "choose-origin.html","เลือกเผ่า",          "origins"),
    ("rpg-origins-เริ่มเล่น.md",          "getting-started.html","เริ่มเล่น",        "origins"),
    ("origin-keybinds.md",                "keybinds.html",     "ปุ่มพลัง",          "origins"),
    ("RPG-Origins-คู่มือเผ่า.md",         "origins-codex.html","คู่มือเผ่า 27",      "origins"),
    ("เซิร์ฟเพื่อน-วิธีเข้า.md",          "join-server.html",  "เข้าเซิร์ฟเพื่อน",   "server"),
    ("มอดใหม่-26.1.2-วิธีใช้.md",         "mods-2612.html",    "มอดใหม่ 26.1.2",     "server"),
]
# ลิงก์เสริม (ไฟล์ที่มีอยู่แล้ว ไม่ต้องแปลง)
EXTRA_NAV = [("origin-selector.html", "เลือกเผ่า (interactive)", "origins")]

MD2HTML = {md: slug for md, slug, _, _ in PAGES}
TITLES  = {slug: title for _, slug, title, _ in PAGES}
GROUPS  = {"home": "", "origins": "RPG Origins · 1.21.1", "server": "เซิร์ฟเพื่อน · 26.1.2"}

GH_REPO = "https://github.com/tayakorn221/minecraft-guide"

# คำโปรยสั้นต่อหน้า (ใช้บนการ์ดหน้าแรก)
DESC = {
    "choose-origin.html":   "ตัดสินใจเลือก 1 ใน 27 เผ่าใน 2 นาที — decision flow + ตารางตามสไตล์ + \"เลี่ยงถ้า…\"",
    "getting-started.html": "เปิดเกมครั้งแรกทำอะไรก่อน + ระบบ RPG/คาถา/คอมแบทของแพ็คนี้ทำงานยังไง",
    "keybinds.html":        "ปุ่มพลัง active ทุกเผ่า + คูลดาวน์จริง + ปุ่มเดียวที่ต้องตั้งเอง",
    "origins-codex.html":   "คู่มือเผ่าครบ 27 ตัว — พลัง/จุดอ่อนทุกข้อ (อ้างอิงละเอียด)",
    "join-server.html":     "เพื่อนไม่เคยลงมอด อ่านแล้วเข้าเซิร์ฟได้เองทีละสเต็ป + Troubleshoot",
    "mods-2612.html":       "VeinMiner/Waystones/Backpack/Combatify ใช้ยังไง กดอะไร คราฟต์อะไร",
    "origin-selector.html": "หน้าเว็บเลือกเผ่า interactive — ฟิลเตอร์ตาม tier/สไตล์ + เทียบเผ่า",
}
LAND_TITLE = {"origin-selector.html": "เลือกเผ่า (interactive)"}  # ไฟล์นอก PAGES

# ── ธีม CSS (โทเค็นดึงจาก origin-selector.html เป๊ะ) ─────────────────────────────
CSS = r"""
:root{
  --bg:#14110c;--surface:#1c1812;--raised:#242019;--raised-2:#2b2619;
  --line:#3a3225;--line-soft:#2c2519;--line-bright:#4d4231;
  --ink:#f3ecdd;--ink-dim:#d2c6ad;--ink-mute:#a1957c;
  --gold:#c9a24b;--gold-bright:#e2bf6e;
  --t1:#7aa45c;--t2:#c89a45;--t3:#bd5651;--t0:#8f8975;
  --good:#86a85f;--bad:#c4625b;
  --nav-bg:rgba(20,17,12,.95);--code-bg:#100d08;--sb-thumb:#3c3324;
  --serif:"Georgia","Iowan Old Style","Palatino Linotype","Times New Roman",serif;
  --sans:"Leelawadee UI","Segoe UI","Noto Sans Thai",Tahoma,sans-serif;
  --nav-h:58px;
}
:root[data-theme="light"]{
  --bg:#f0e7d2;--surface:#e8ddc2;--raised:#e0d4b6;--raised-2:#d8c9a6;
  --line:#c5b389;--line-soft:#d6c9a8;--line-bright:#b09a6e;
  --ink:#2a2216;--ink-dim:#473c28;--ink-mute:#706245;
  --gold:#7e6010;--gold-bright:#785915;
  --t1:#4d7a2f;--t2:#946a14;--t3:#a83c34;--t0:#6a6350;
  --good:#4d7a2f;--bad:#a83c34;
  --nav-bg:rgba(240,231,210,.95);--code-bg:#e3d7b8;--sb-thumb:#c2b084;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
::selection{background:rgba(201,162,75,.28)}
::-webkit-scrollbar{width:11px;height:11px}
::-webkit-scrollbar-track{background:var(--surface)}
::-webkit-scrollbar-thumb{background:var(--sb-thumb);border:3px solid var(--surface);border-radius:8px}
::-webkit-scrollbar-thumb:hover{background:#4d4231}
body{font-family:var(--sans);background:var(--bg);color:var(--ink);line-height:1.7;-webkit-font-smoothing:antialiased;position:relative;min-height:100vh}
body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.05;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
body,.nav,main blockquote,main thead th,main tbody td,main pre,.foot a,.shell{transition:background-color .22s ease,border-color .22s ease,color .22s ease}

/* ── top nav ── */
.nav{position:sticky;top:0;z-index:60;height:var(--nav-h);background:var(--nav-bg);border-bottom:1px solid var(--line);backdrop-filter:blur(8px);display:flex;align-items:center;gap:18px;padding:0 20px}
.nav .brand{font-family:var(--serif);font-weight:700;font-size:17px;color:var(--ink);display:flex;align-items:center;gap:9px;white-space:nowrap;text-decoration:none}
.nav .brand .di{color:var(--gold);transform:rotate(45deg);display:inline-block;font-size:11px}
.nav .brand em{font-style:italic;color:var(--gold)}
.nav .links{display:flex;gap:3px;flex:1;overflow-x:auto;scrollbar-width:none}
.nav .links::-webkit-scrollbar{display:none}
.nav a.nl{font-size:13px;color:var(--ink-mute);text-decoration:none;padding:7px 12px;border-radius:3px;white-space:nowrap;transition:color .15s,background .15s;border:1px solid transparent}
.nav a.nl:hover{color:var(--ink);background:var(--surface)}
.nav a.nl.active{color:var(--gold-bright);border-color:var(--line-bright);background:var(--surface)}
.nav .gh{color:var(--ink-mute);text-decoration:none;font-size:13px;border:1px solid var(--line-bright);padding:6px 12px;border-radius:3px;white-space:nowrap;transition:all .15s}
.nav .gh:hover{color:var(--ink);border-color:var(--gold)}
.theme-btn{background:var(--surface);border:1px solid var(--line-bright);color:var(--ink-dim);width:36px;height:36px;border-radius:3px;font-size:15px;line-height:1;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:color .15s,border-color .15s}
.theme-btn:hover{color:var(--gold-bright);border-color:var(--gold)}
.menu-btn{display:none;background:var(--surface);border:1px solid var(--line-bright);color:var(--ink);width:38px;height:38px;border-radius:3px;font-size:18px;cursor:pointer}

/* ── layout ── */
.shell{max-width:1180px;margin:0 auto;padding:0 22px;display:grid;grid-template-columns:232px 1fr;gap:40px;position:relative;z-index:1}
.toc{position:sticky;top:calc(var(--nav-h) + 24px);align-self:start;height:calc(100vh - var(--nav-h) - 48px);overflow-y:auto;padding:28px 0 40px;font-size:13px}
.toc .tl{font-size:10.5px;text-transform:uppercase;letter-spacing:.2em;color:var(--gold);font-weight:700;margin-bottom:14px;padding-left:13px}
.toc a{display:block;color:var(--ink-mute);text-decoration:none;padding:5px 13px;border-left:2px solid var(--line-soft);line-height:1.45;transition:color .15s,border-color .15s}
.toc a:hover{color:var(--ink-dim)}
.toc a.h3{padding-left:26px;font-size:12.5px}
.toc a.on{color:var(--gold-bright);border-left-color:var(--gold)}
main{min-width:0;padding:38px 0 80px;max-width:820px}

/* ── prose ── */
.kicker{font:700 11.5px/1 var(--sans);letter-spacing:.28em;text-transform:uppercase;color:var(--gold);margin-bottom:16px}
main h1{font-family:var(--serif);font-weight:700;font-size:clamp(30px,5vw,46px);line-height:1.08;letter-spacing:.4px;color:var(--ink);margin:0 0 10px;padding-bottom:22px;border-bottom:1px solid var(--line)}
main h1 em{font-style:italic;color:var(--gold)}
main h2{font-family:var(--serif);font-weight:700;font-size:clamp(22px,3vw,28px);color:var(--ink);margin:46px 0 16px;padding-top:10px;display:flex;align-items:center;gap:13px;scroll-margin-top:calc(var(--nav-h) + 16px)}
main h2::before{content:"◆";color:var(--gold);font-size:14px;flex-shrink:0}
main h2::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line-bright),transparent)}
main h3{font-family:var(--serif);font-weight:700;font-size:19px;color:var(--gold-bright);margin:30px 0 12px;letter-spacing:.2px;scroll-margin-top:calc(var(--nav-h) + 16px)}
main h4{font-family:var(--sans);font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-dim);margin:22px 0 10px}
main p{color:var(--ink-dim);margin:13px 0}
main a{color:var(--gold-bright);text-decoration:none;border-bottom:1px solid rgba(201,162,75,.32);transition:border-color .15s}
main a:hover{border-bottom-color:var(--gold-bright)}
main strong{color:var(--ink);font-weight:700}
main em{color:var(--ink-dim)}
main ul,main ol{margin:13px 0 13px 4px;padding-left:22px}
main li{color:var(--ink-dim);margin:7px 0;padding-left:6px}
main ul li::marker{color:var(--gold);content:"◆  ";font-size:.8em}
main ol li::marker{color:var(--gold);font-family:var(--serif);font-weight:700}
main li>ul,main li>ol{margin:7px 0}
main hr{border:none;height:34px;position:relative;margin:30px 0}
main hr::before{content:"◆";position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);color:var(--gold);font-size:12px;background:var(--bg);padding:0 14px}
main hr::after{content:"";position:absolute;left:0;right:0;top:50%;height:1px;background:linear-gradient(90deg,transparent,var(--line-bright),transparent)}

/* code */
main code{font-family:"Consolas","SF Mono",monospace;font-size:.86em;background:var(--raised-2);color:var(--gold-bright);border:1px solid var(--line);border-radius:3px;padding:2px 7px;white-space:nowrap}
main pre{background:var(--code-bg);border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:4px;padding:16px 18px;overflow-x:auto;margin:16px 0}
main pre code{background:none;border:none;color:var(--ink-dim);padding:0;white-space:pre;font-size:13.5px;line-height:1.6}

/* tables — ledger style */
.tw{overflow-x:auto;margin:18px 0;border:1px solid var(--line);border-radius:5px}
main table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:480px}
main thead th{background:var(--raised-2);color:var(--gold-bright);font-family:var(--serif);font-weight:700;text-align:left;padding:11px 15px;border-bottom:1px solid var(--line-bright);letter-spacing:.2px;white-space:nowrap}
main tbody td{padding:10px 15px;border-bottom:1px solid var(--line-soft);color:var(--ink-dim);vertical-align:top}
main tbody tr:nth-child(even){background:rgba(255,255,255,.012)}
main tbody tr:hover{background:rgba(201,162,75,.05)}
main tbody tr:last-child td{border-bottom:none}
main td strong{color:var(--ink)}

/* blockquote → callout */
main blockquote{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:3px;padding:13px 18px;margin:16px 0;color:var(--ink-dim);font-size:14px}
main blockquote p{margin:6px 0;color:var(--ink-dim)}
main blockquote p:first-child{margin-top:0}main blockquote p:last-child{margin-bottom:0}
main blockquote.warn{border-left-color:var(--t3);background:linear-gradient(90deg,rgba(189,86,81,.07),var(--surface) 60%)}
main blockquote.tip{border-left-color:var(--gold)}
main blockquote.goal{border-left-color:var(--t1);background:linear-gradient(90deg,rgba(122,164,92,.06),var(--surface) 60%)}

/* task list checkboxes */
main .task{list-style:none;padding-left:0;position:relative}
main .task::marker{content:""}
main .cb{display:inline-flex;width:17px;height:17px;border:1px solid var(--line-bright);border-radius:3px;margin-right:9px;vertical-align:-3px;align-items:center;justify-content:center;font-size:11px;color:var(--gold);flex-shrink:0}
main .cb.on{background:var(--gold);border-color:var(--gold);color:#1a1408}

/* footer nav */
.foot{border-top:1px solid var(--line);margin-top:50px;padding-top:26px;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
.foot a{flex:1;min-width:200px;background:var(--surface);border:1px solid var(--line);border-radius:4px;padding:14px 18px;text-decoration:none;transition:border-color .18s,transform .15s;display:block}
.foot a:hover{border-color:var(--gold);transform:translateY(-2px)}
.foot .fl{font-size:11px;color:var(--ink-mute);text-transform:uppercase;letter-spacing:.14em}
.foot .ft{font-family:var(--serif);font-size:16px;color:var(--gold-bright);font-weight:700;margin-top:3px}
.foot a.nx{text-align:right}
.credit{text-align:center;color:var(--ink-mute);font-size:12px;padding:36px 0 10px;line-height:1.8}
.credit .di{color:var(--gold);transform:rotate(45deg);display:inline-block;margin:0 6px}

/* ── mobile guide nav (ใน toc drawer) ── */
.toc-guides{display:none}
.toc-guides .tl{font-size:10.5px;text-transform:uppercase;letter-spacing:.2em;color:var(--gold);font-weight:700;margin-bottom:12px;padding-left:13px}
.toc-guides a{display:block;color:var(--ink-dim);text-decoration:none;padding:7px 13px;border-left:2px solid var(--line-soft);font-size:13.5px;font-family:var(--serif);transition:color .15s,border-color .15s}
.toc-guides a:hover{color:var(--ink)}
.toc-guides a.cur{color:var(--gold-bright);border-left-color:var(--gold)}

/* ── landing (หน้าแรก) ── */
.landing-wrap{max-width:1000px;margin:0 auto;padding:0 22px;position:relative;z-index:1}
.landing{padding:0 0 60px}
.hero{text-align:center;padding:58px 12px 44px;border-bottom:1px solid var(--line);margin-bottom:38px}
.hero .kicker{margin-bottom:14px}
.hero h1{font-family:var(--serif);font-weight:700;font-size:clamp(40px,8vw,74px);line-height:1.02;color:var(--ink);margin:4px 0 16px;letter-spacing:.5px}
.hero h1 em{font-style:italic;color:var(--gold)}
.hero .lead{color:var(--ink-dim);font-size:clamp(15px,2.2vw,18px);max-width:640px;margin:0 auto;line-height:1.7}
.gsec{margin-bottom:36px}
.gsec-h{font-family:var(--serif);font-weight:700;font-size:20px;color:var(--gold-bright);margin-bottom:16px;display:flex;align-items:center;gap:11px}
.gsec-h .di{color:var(--gold);transform:rotate(45deg);display:inline-block;font-size:11px}
.gsec-h::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line-bright),transparent)}
.guide-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(248px,1fr));gap:15px}
.gcard{background:var(--surface);border:1px solid var(--line);border-radius:5px;padding:19px 20px 17px;text-decoration:none;display:flex;flex-direction:column;gap:7px;position:relative;overflow:hidden;transition:border-color .2s,transform .2s,box-shadow .2s;animation:rise .5s ease both}
.gcard::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--gold);opacity:0;transition:opacity .2s}
.gcard:hover{border-color:var(--line-bright);transform:translateY(-3px);box-shadow:0 14px 30px rgba(0,0,0,.34)}
.gcard:hover::before{opacity:1}
.gcard .gc-n{font-family:var(--serif);font-size:19px;font-weight:700;color:var(--ink);line-height:1.15}
.gcard .gc-d{font-size:13.5px;color:var(--ink-dim);line-height:1.55;flex:1}
.gcard .gc-go{font-size:12.5px;color:var(--gold-bright);font-weight:700;margin-top:3px}
.gcard.feat{background:var(--raised);border-color:var(--line-bright)}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

/* ── responsive ── */
@media(max-width:900px){
  .shell{grid-template-columns:1fr;gap:0}
  .toc{position:fixed;top:var(--nav-h);left:0;bottom:0;width:262px;height:auto;background:var(--surface);border-right:1px solid var(--line);padding:24px 14px 40px;transform:translateX(-105%);transition:transform .26s ease;z-index:55}
  .toc.open{transform:none;box-shadow:18px 0 40px rgba(0,0,0,.5)}
  .menu-btn{display:flex;align-items:center;justify-content:center}
  main{padding:26px 0 60px}
  .nav .links{display:none}
  .toc-guides{display:block}
  .scrim{position:fixed;inset:var(--nav-h) 0 0;background:rgba(8,6,4,.6);z-index:54;display:none}
  .scrim.show{display:block}
}
@media(min-width:901px){.menu-btn,.scrim{display:none}}
"""

JS = r"""
const mb=document.querySelector('.menu-btn'),toc=document.querySelector('.toc'),scrim=document.querySelector('.scrim');
if(mb){mb.onclick=()=>{toc.classList.toggle('open');scrim.classList.toggle('show')};
  scrim.onclick=()=>{toc.classList.remove('open');scrim.classList.remove('show')};
  toc.querySelectorAll('a').forEach(a=>a.onclick=()=>{toc.classList.remove('open');scrim.classList.remove('show')});}
const links=[...document.querySelectorAll('.toc a')],secs=links.map(a=>document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
const spy=()=>{let i=secs.length;while(--i>=0){if(secs[i]&&secs[i].getBoundingClientRect().top<120)break}
  links.forEach(a=>a.classList.remove('on'));if(i>=0&&links[i])links[i].classList.add('on')};
document.addEventListener('scroll',spy,{passive:true});spy();
const tb=document.querySelector('.theme-btn');
function _icon(){const light=document.documentElement.dataset.theme==='light';tb.textContent=light?'☾':'☀';tb.setAttribute('aria-label',light?'สลับเป็นโหมดมืด':'สลับเป็นโหมดสว่าง')}
if(tb){_icon();tb.onclick=()=>{const next=document.documentElement.dataset.theme==='light'?'dark':'light';document.documentElement.dataset.theme=next;try{localStorage.setItem('mc-theme',next)}catch(e){}_icon()}}
"""

def slugify(text):
    t = re.sub(r'<[^>]+>', '', text)
    t = re.sub(r'[^0-9A-Za-z฀-๿]+', '-', t).strip('-')
    return t.lower() or 'sec'

def convert(md_text):
    md = markdown.Markdown(extensions=['tables','fenced_code','sane_lists','attr_list'])
    body = md.convert(md_text)
    return body

def postprocess(bodyhtml):
    # wrap tables for horizontal scroll
    bodyhtml = bodyhtml.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
    # blockquote variants by leading emoji
    def bq(m):
        inner = m.group(1)
        cls = 'tip'
        if any(x in inner for x in ['⚠️','🔴','🚫','☠️','💀']): cls='warn'
        elif any(x in inner for x in ['🎯','✅','💰','👥']): cls='goal'
        return f'<blockquote class="{cls}">{inner}</blockquote>'
    bodyhtml = re.sub(r'<blockquote>(.*?)</blockquote>', bq, bodyhtml, flags=re.S)
    # task list checkboxes  [ ] / [x]
    def cb(m):
        mark = m.group(1)
        box = '<span class="cb on">✓</span>' if mark.lower()=='x' else '<span class="cb"></span>'
        return f'<li class="task">{box}'
    bodyhtml = re.sub(r'<li>\[([ xX])\]\s*', cb, bodyhtml)
    # add ids to h2/h3 for TOC + collect
    toc=[]
    def head(m):
        lvl=m.group(1); txt=m.group(2); hid=slugify(txt)
        toc.append((lvl,hid,txt))
        return f'<h{lvl} id="{hid}">{txt}</h{lvl}>'
    bodyhtml = re.sub(r'<h([23])>(.*?)</h\1>', head, bodyhtml, flags=re.S)
    return bodyhtml, toc

def rewrite_links(bodyhtml):
    for md_name, slug in MD2HTML.items():
        bodyhtml = bodyhtml.replace(f'href="{md_name}"', f'href="{slug}"')
        # links may be URL-encoded by markdown? keep raw; also handle with ./
        bodyhtml = bodyhtml.replace(f'href="./{md_name}"', f'href="{slug}"')
    return bodyhtml

def nav_html(current_slug):
    items=[]
    for _, slug, title, grp in PAGES:
        if slug=='index.html':
            continue
        active=' active' if slug==current_slug else ''
        items.append(f'<a class="nl{active}" href="{slug}">{title}</a>')
    return ''.join(items)

def toc_html(toc):
    if not toc: return ''
    out=['<div class="tl">ในหน้านี้</div>']
    for lvl,hid,txt in toc:
        cls='h3' if lvl=='3' else ''
        clean=re.sub(r'<[^>]+>','',txt)
        out.append(f'<a class="{cls}" href="#{hid}">{clean}</a>')
    return ''.join(out)

def toc_guides_html(current):
    # เมนูข้ามคู่มือ — โชว์เฉพาะมือถือ (ใน drawer) เดสก์ท็อปใช้ nav บนแทน
    out=['<div class="toc-guides"><div class="tl">คู่มือทั้งหมด</div>',
         '<a href="index.html">หน้าแรก</a>']
    for _, slug, title, grp in PAGES:
        if slug=='index.html': continue
        cur=' class="cur"' if slug==current else ''
        out.append(f'<a href="{slug}"{cur}>{title}</a>')
    out.append('</div>')
    return ''.join(out)

def landing_body():
    groups=[("RPG Origins · 1.21.1", ["choose-origin.html","getting-started.html","keybinds.html","origins-codex.html","origin-selector.html"]),
            ("เซิร์ฟเพื่อน · 26.1.2", ["join-server.html","mods-2612.html"])]
    secs=[]
    for gh,slugs in groups:
        cards=[]
        for s in slugs:
            title=TITLES.get(s) or LAND_TITLE.get(s,s)
            feat=' feat' if s=='origin-selector.html' else ''
            go='เปิดเครื่องมือ →' if s=='origin-selector.html' else 'เปิดอ่าน →'
            cards.append(f'<a class="gcard{feat}" href="{s}"><div class="gc-n">{title}</div><div class="gc-d">{DESC.get(s,"")}</div><div class="gc-go">{go}</div></a>')
        secs.append(f'<div class="gsec"><div class="gsec-h"><span class="di">◆</span> {gh}</div><div class="guide-grid">{"".join(cards)}</div></div>')
    hero=('<div class="hero"><div class="kicker">คู่มือเล่นภาษาไทย · ทุกตัวเลขตรวจกับไฟล์มอดจริง</div>'
          '<h1>ตำรา <em>Minecraft</em></h1>'
          '<p class="lead">RPG Origins (1.21.1) + เซิร์ฟเพื่อน (26.1.2) — เลือกเผ่า · ปุ่มพลัง · เริ่มเล่น · เข้าเซิร์ฟ · วิธีใช้มอด</p></div>')
    return f'<main class="landing">{hero}{"".join(secs)}</main>'

def foot_html(idx):
    prev_a=nxt_a=''
    content_pages=[p for p in PAGES if p[1]!='index.html']
    # find position among content pages
    slugs=[p[1] for p in content_pages]
    cur=PAGES[idx][1]
    if cur in slugs:
        i=slugs.index(cur)
        if i>0:
            _,s,t,_=content_pages[i-1]; prev_a=f'<a class="pv" href="{s}"><div class="fl">← ก่อนหน้า</div><div class="ft">{t}</div></a>'
        if i<len(content_pages)-1:
            _,s,t,_=content_pages[i+1]; nxt_a=f'<a class="nx" href="{s}"><div class="fl">ถัดไป →</div><div class="ft">{t}</div></a>'
    home='<a href="index.html"><div class="fl">⌂ กลับ</div><div class="ft">หน้าแรก</div></a>'
    return f'<div class="foot">{prev_a or home}{nxt_a}</div>'

TEMPLATE = """<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} · ตำรา RPG Origins</title>
<style>{css}</style>
<script>try{{var _t=localStorage.getItem('mc-theme');if(_t)document.documentElement.dataset.theme=_t}}catch(e){{}}</script>
</head><body>
<nav class="nav">
<button class="menu-btn" aria-label="menu">☰</button>
<a class="brand" href="index.html"><span class="di">◆</span> ตำรา <em>Minecraft</em></a>
<div class="links">{nav}</div>
<button class="theme-btn" aria-label="สลับโหมดสว่าง/มืด">☀</button>
<a class="gh" href="{gh}" target="_blank" rel="noopener">GitHub ↗</a>
</nav>
<div class="scrim"></div>
<div class="shell">
<aside class="toc">{tocguides}{toc}</aside>
<main>{body}{foot}
<div class="credit"><span class="di">◆</span> ตำรา Minecraft · RPG Origins + เซิร์ฟเพื่อน 26.1.2 <span class="di">◆</span><br>เนื้อหาตรวจกับไฟล์มอดจริง (jar)</div>
</main></div>
<script>{js}</script>
</body></html>"""

LANDING_TEMPLATE = """<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ตำรา Minecraft · คู่มือ RPG Origins + เซิร์ฟเพื่อน 26.1.2</title>
<style>{css}</style>
<script>try{{var _t=localStorage.getItem('mc-theme');if(_t)document.documentElement.dataset.theme=_t}}catch(e){{}}</script>
</head><body>
<nav class="nav">
<a class="brand" href="index.html"><span class="di">◆</span> ตำรา <em>Minecraft</em></a>
<div class="links">{nav}</div>
<button class="theme-btn" aria-label="สลับโหมดสว่าง/มืด">☀</button>
<a class="gh" href="{gh}" target="_blank" rel="noopener">GitHub ↗</a>
</nav>
<div class="scrim"></div>
<div class="landing-wrap">{body}
<div class="credit"><span class="di">◆</span> เนื้อหาตรวจกับไฟล์มอดจริง (jar) · ภาษาไทย <span class="di">◆</span></div>
</div>
<script>{js}</script>
</body></html>"""

def build():
    built=[]
    for idx,(md_name, slug, title, grp) in enumerate(PAGES):
        if slug=='index.html':   # หน้าแรก = landing สร้างเอง (ไม่แปลงจาก INDEX.md)
            page=LANDING_TEMPLATE.format(css=CSS, js=JS, nav=nav_html(slug), gh=GH_REPO, body=landing_body())
            (DOCS/slug).write_text(page, encoding='utf-8'); built.append(slug); print("  ✓", slug, "(landing)"); continue
        src = DOCS / md_name
        if not src.exists():
            print("  ! ขาด", md_name); continue
        raw = src.read_text(encoding='utf-8')
        body = convert(raw)
        body, toc = postprocess(body)
        body = rewrite_links(body)
        page = TEMPLATE.format(title=title, css=CSS, js=JS, nav=nav_html(slug),
                               tocguides=toc_guides_html(slug), toc=toc_html(toc), body=body, foot=foot_html(idx), gh=GH_REPO)
        (DOCS / slug).write_text(page, encoding='utf-8')
        built.append(slug); print("  ✓", slug, f"({len(toc)} หัวข้อ)")
    print(f"\nเสร็จ {len(built)} หน้า → docs/")

if __name__=='__main__':
    print("สร้างเว็บจากคู่มือ .md ...")
    build()
