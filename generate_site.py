# 从 data/*.json 生成静态 HTML 网站到 site/ 目录
import json
import os
import glob
import html
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
SITE_DIR = os.path.join(BASE, "site")

CAT_NAMES = {"cs.CV": "计算机视觉", "cs.CL": "计算与语言", "cs.LG": "机器学习", "cs.MM": "多媒体"}
CAT_COLORS = {"cs.CV": "#7b93ff", "cs.CL": "#ff8c6b", "cs.LG": "#45d4c8", "cs.MM": "#c06cff"}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#0a0e1a;--glass:rgba(255,255,255,0.07);--gb:rgba(255,255,255,0.12);--t:#fff;--t2:#b0b8d0;--t3:#7880a0;--ac:#7b93ff;--ac2:#45d4c8;--hf:#ff9d00}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--t);min-height:100vh}
body::before{content:"";position:fixed;top:-200px;right:-200px;width:600px;height:600px;background:radial-gradient(circle,rgba(123,147,255,0.07)0%,transparent 70%);pointer-events:none}
.c{max-width:1000px;margin:0 auto;padding:40px 20px;position:relative;z-index:1}
a{color:var(--ac);text-decoration:none}a:hover{color:#9db4ff}
h1{font-size:2.4rem;font-weight:800;background:linear-gradient(135deg,#7b93ff,#45d4c8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin-bottom:8px}
.sub{text-align:center;color:var(--t2);margin-bottom:10px;font-size:0.95rem}
.pills{display:flex;justify-content:center;gap:6px;margin-bottom:40px;flex-wrap:wrap}
.pill{font-size:.72rem;padding:3px 11px;border-radius:16px;background:var(--glass);border:1px solid var(--gb);color:var(--t2)}
.section{margin-bottom:40px}
.label{font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:var(--t3);margin-bottom:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.dcard{display:flex;align-items:center;justify-content:space-between;background:var(--glass);border:1px solid var(--gb);border-radius:12px;padding:14px 18px;color:var(--t);transition:all .2s}
.dcard:hover{border-color:rgba(255,255,255,.18);transform:translateY(-1px);box-shadow:0 6px 20px rgba(0,0,0,.3)}
.dcard .dt{font-weight:700;font-size:1rem}
.badges{display:flex;gap:5px}
.badge{font-size:.82rem;font-weight:700;padding:3px 10px;border-radius:7px;background:rgba(255,255,255,.06);border:1px solid var(--gb)}
.b-a{color:#9db4ff}.b-h{color:#ffb840}
.src-links{display:flex;gap:6px;flex-wrap:wrap}
.src-btn{font-size:.78rem;font-weight:600;padding:5px 12px;border-radius:7px;display:inline-flex;align-items:center;gap:5px;transition:all .15s;text-decoration:none}
.src-btn span{font-weight:800}
.src-btn.hf{background:rgba(255,157,0,.12);border:1px solid rgba(255,157,0,.25);color:#ffb840}
.src-btn.hf:hover{background:rgba(255,157,0,.22);color:#ffc860}
.src-btn.ax{background:rgba(123,147,255,.1);border:1px solid rgba(123,147,255,.2);color:#9db4ff}
.src-btn.ax:hover{background:rgba(123,147,255,.2);color:#b0c4ff}
.dcard{position:relative}.dcard-del{position:absolute;top:6px;right:6px;width:22px;height:22px;border:none;border-radius:5px;background:transparent;color:var(--t3);font-size:.9rem;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;transition:all .15s}
.dcard:hover .dcard-del{opacity:1}.dcard-del:hover{color:#ff6b6b;background:rgba(255,107,107,.1)}
.topbar{position:sticky;top:0;z-index:100;background:rgba(10,14,26,.9);backdrop-filter:blur(16px);border-bottom:1px solid var(--gb);padding:12px 20px}
.topbar-in{max-width:1100px;margin:0 auto;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.back{color:var(--t3);font-size:.85rem;font-weight:500}
.back:hover{color:var(--ac)}
.topbar h2{font-size:1.05rem;font-weight:700}
.spacer{flex:1}
.search{position:relative;width:280px}
.search input{width:100%;background:rgba(255,255,255,.08);border:1px solid var(--gb);border-radius:9px;padding:8px 12px 8px 36px;color:var(--t);font-size:.88rem;font-family:inherit;outline:0}
.search input:focus{border-color:var(--ac)}
.search input::placeholder{color:var(--t3)}
.search svg{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--t3)}
.cnt{font-size:.8rem;color:var(--t3);white-space:nowrap}
.filters{max-width:1100px;margin:0 auto;padding:12px 20px 0;display:flex;gap:7px;flex-wrap:wrap;align-items:center}
.fbtn{background:var(--glass);border:1px solid var(--gb);border-radius:9px;padding:6px 14px;color:var(--t2);font-size:.8rem;font-weight:500;cursor:pointer;font-family:inherit;white-space:nowrap;display:inline-flex;align-items:center;gap:5px;transition:all .15s}
.fbtn:hover{border-color:rgba(255,255,255,.18);color:var(--t);background:rgba(255,255,255,.1)}
.fbtn.on{background:var(--ac);border-color:var(--ac);color:#fff}
.fbtn.on-hf{background:var(--hf);border-color:var(--hf);color:#fff}
.fc{opacity:.7;font-size:.73rem}
.cdot{width:6px;height:6px;border-radius:50%;display:inline-block}
.fsep{width:1px;height:18px;background:var(--gb);margin:0 3px}
.list{max-width:1100px;margin:0 auto;padding:12px 20px 60px}
.card{background:var(--glass);border:1px solid var(--gb);border-radius:12px;padding:18px 22px;margin-bottom:9px;transition:all .2s}
.card:hover{border-color:rgba(255,255,255,.16);background:rgba(255,255,255,.1)}
.ch{display:flex;align-items:flex-start;gap:12px}
.ci{font-size:.72rem;color:var(--t3);min-width:26px;padding-top:3px;font-weight:600}
.cb{flex:1;min-width:0}
.ct{font-size:1rem;font-weight:700;line-height:1.4;margin-bottom:4px}
.ct a{color:var(--t)}.ct a:hover{color:var(--ac)}
.ca{font-size:.86rem;color:var(--t2);margin-bottom:7px;line-height:1.4}
.tags{display:flex;gap:5px;flex-wrap:wrap;align-items:center}
.tag{font-size:.72rem;font-weight:500;padding:2px 8px;border-radius:5px;background:rgba(255,255,255,.06);border:1px solid var(--gb);color:var(--t2)}
.links{display:flex;gap:5px;flex-shrink:0;margin-left:auto}
.links a{font-size:.78rem;font-weight:500;color:var(--ac);padding:4px 10px;border:1px solid rgba(123,147,255,.2);border-radius:7px}
.links a:hover{background:rgba(123,147,255,.1)}
.abs{margin-top:8px;margin-left:38px;font-size:.86rem;line-height:1.6;color:var(--t2)}
.actions{display:flex;gap:4px;flex-shrink:0;align-items:center}
.abtn{width:30px;height:30px;border:1px solid var(--gb);border-radius:7px;background:transparent;color:var(--t3);font-size:1.1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s;font-family:inherit;line-height:1}
.fav-btn:hover,.fav-btn.on{color:#ff4d6a;border-color:rgba(255,77,106,.3);background:rgba(255,77,106,.08)}
.fav-btn.on{font-size:1rem}
.del-btn:hover{color:#ff6b6b;border-color:rgba(255,107,107,.3);background:rgba(255,107,107,.08)}
.card.deleted{opacity:.3;transform:scale(.97);pointer-events:none;max-height:0;padding:0;margin:0;border:0;overflow:hidden;transition:all .3s}
.toggle{margin-top:6px;margin-left:38px;font-size:.78rem;color:var(--ac);cursor:pointer;user-select:none;padding:2px 0;opacity:.8;transition:opacity .15s}
.toggle:hover{opacity:1}
.nr{text-align:center;padding:60px;color:var(--t3)}
.stop{position:fixed;bottom:24px;right:24px;width:40px;height:40px;background:var(--ac);border:none;border-radius:10px;color:#fff;font-size:1.1rem;cursor:pointer;opacity:0;transition:all .2s;z-index:99;box-shadow:0 4px 16px rgba(123,147,255,.15)}
.stop.v{opacity:1}.stop:hover{transform:translateY(-2px)}
.rbtn{font-size:.78rem;font-weight:600;padding:6px 16px;border-radius:8px;background:var(--ac);color:#fff;text-transform:none;letter-spacing:0;text-decoration:none;transition:all .15s;display:inline-flex;align-items:center;gap:4px;border:none;cursor:pointer;font-family:inherit}
.rbtn:hover{background:#6680ff;color:#fff;transform:translateY(-1px)}
.stop-btn{background:rgba(255,255,255,.08);color:var(--t2);border:1px solid var(--gb)}.stop-btn:hover{background:rgba(255,255,255,.14);color:var(--t)}
.fetch-panel{display:flex;align-items:center;gap:8px;margin-bottom:14px;flex-wrap:wrap}
.fetch-date{background:rgba(255,255,255,.08);border:1px solid var(--gb);border-radius:8px;padding:6px 12px;color:var(--t);font-size:.85rem;font-family:inherit;outline:0;color-scheme:dark}
.fetch-date:focus{border-color:var(--ac)}
.fetch-status{font-size:.8rem;color:var(--t3)}
footer{text-align:center;padding:28px 0;color:var(--t3);font-size:.75rem;margin-top:30px}
@media(max-width:700px){.search{width:100%;order:10}.links{display:none}.ci{display:none}.abs{margin-left:0}.ch{gap:6px}}
"""

def esc(s):
    return html.escape(str(s))

def get_dates():
    files = glob.glob(os.path.join(DATA_DIR, "????-??-??.json"))
    return sorted([os.path.basename(f).replace(".json", "") for f in files], reverse=True)

def load_data(date_str):
    path = os.path.join(DATA_DIR, f"{date_str}.json")
    if not os.path.exists(path):
        return {"arxiv": [], "huggingface": []}
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    if isinstance(d, list):
        return {"arxiv": d, "huggingface": []}
    return d

def gen_index():
    dates = get_dates()
    date_cards = ""
    for d in dates:
        data = load_data(d)
        ac = len(data["arxiv"])
        hc = len(data["huggingface"])
        hf_link = f'<a class="src-btn hf" href="{d}.html#hf">HF 热门 <span>{hc}</span></a>' if hc else ""
        ax_link = f'<a class="src-btn ax" href="{d}.html#arxiv">arXiv <span>{ac}</span></a>' if ac else ""
        date_cards += f'<div class="dcard" id="dc-{d}"><span class="dt">{d}</span><div class="src-links">{hf_link}{ax_link}</div><button class="dcard-del" onclick="delDate(\'{d}\')" title="隐藏">&times;</button></div>\n'

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#0a0e1a"><meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="icon-192.png">
<title>arXiv Papers</title><style>{CSS}</style></head><body>
<div class="c">
<h1>探索人类智能边界 · 每日arXiv计划</h1>
<p class="sub">成为地球上前 0.000000001% 的顶尖人工智能科学家</p>
<div class="pills"><span class="pill">cs.CV</span><span class="pill">cs.CL</span><span class="pill">cs.LG</span><span class="pill">cs.MM</span><span class="pill" style="color:var(--hf)">HuggingFace</span><a href="favorites.html" class="pill" style="color:#ff4d6a;border-color:rgba(255,77,106,.3)">&#9829; 收藏夹</a></div>
<div class="section">
<div class="label" style="display:flex;align-items:center;gap:12px">Daily Papers</div>
<div class="fetch-panel">
<input type="date" id="fd" class="fetch-date">
<button class="rbtn" onclick="doFetch()">&#x21bb; 抓取</button>
<button class="rbtn stop-btn" id="stopBtn" style="display:none" onclick="window.open('https://github.com/Issac304/arxiv-papers/actions','_blank')">查看进度</button>
<span class="fetch-status" id="fs"></span>
</div>
{f'<div class="grid">{date_cards}</div>' if date_cards else '<div class="nr">暂无数据</div>'}
</div>
<footer>arXiv Papers &bull; <a href="https://arxiv.org">arXiv.org</a> &bull; <a href="https://huggingface.co/papers">HuggingFace</a></footer>
</div>
<script>
if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{{}});
document.getElementById('fd').value=new Date().toISOString().slice(0,10);

function delDate(d){{const el=document.getElementById('dc-'+d);if(el){{el.style.transition='all .3s';el.style.opacity='0';el.style.transform='scale(.95)';setTimeout(()=>el.remove(),300)}}
const hd=JSON.parse(localStorage.getItem('hidden_dates')||'[]');if(!hd.includes(d))hd.push(d);localStorage.setItem('hidden_dates',JSON.stringify(hd))}}
(function(){{const hd=JSON.parse(localStorage.getItem('hidden_dates')||'[]');hd.forEach(d=>{{const el=document.getElementById('dc-'+d);if(el)el.remove()}})}})()

const REPO='Issac304/arxiv-papers';
function getToken(){{let t=localStorage.getItem('gh_token');if(!t){{t=prompt('首次使用需输入 GitHub Token\\n\\n获取方法：GitHub → Settings → Developer settings → Personal access tokens → Fine-grained → Generate\\n\\n权限只需勾选 Actions: Read and Write');if(t)localStorage.setItem('gh_token',t)}}return t}}

async function doFetch(){{
const token=getToken();if(!token)return;
const dateVal=document.getElementById('fd').value;
const fs=document.getElementById('fs');
const sb=document.getElementById('stopBtn');
fs.textContent='正在触发抓取...';fs.style.color='var(--ac)';
sb.style.display='inline-flex';
try{{
const r=await fetch(`https://api.github.com/repos/${{REPO}}/actions/workflows/daily.yml/dispatches`,{{
method:'POST',headers:{{'Authorization':`token ${{token}}`,'Accept':'application/vnd.github.v3+json'}},
body:JSON.stringify({{ref:'master',inputs:{{date:dateVal}})
}});
if(r.status===204){{fs.textContent=`已触发抓取 ${{dateVal}}，约1-2分钟后刷新页面查看`;fs.style.color='var(--ac2)';pollRun(token,dateVal)}}
else if(r.status===401){{localStorage.removeItem('gh_token');fs.textContent='Token 无效，请重新输入';fs.style.color='#ff6b6b';sb.style.display='none'}}
else{{const j=await r.json().catch(()=>({{}}));fs.textContent='触发失败: '+(j.message||r.status);fs.style.color='#ff6b6b'}}
}}catch(e){{fs.textContent='网络错误: '+e.message;fs.style.color='#ff6b6b'}}
}}

async function pollRun(token,dateVal){{
const fs=document.getElementById('fs');
for(let i=0;i<30;i++){{
await new Promise(r=>setTimeout(r,5000));
try{{
const r=await fetch(`https://api.github.com/repos/${{REPO}}/actions/runs?per_page=1`,{{headers:{{'Authorization':`token ${{token}}`}}}});
const d=await r.json();const run=d.workflow_runs&&d.workflow_runs[0];
if(!run)continue;
if(run.status==='completed'){{
if(run.conclusion==='success'){{fs.textContent=`${{dateVal}} 抓取完成! 刷新页面查看`;fs.style.color='#45d4c8'}}
else{{fs.textContent=`抓取结束 (${{run.conclusion}})`;fs.style.color='#ff6b6b'}}
document.getElementById('stopBtn').style.display='none';return}}
fs.textContent=`抓取中... (${{run.status}})`;
}}catch{{}}
}}
}}
</script></body></html>"""

def gen_paper_card(p, i, is_hf=False):
    au = p.get("authors", [])
    au_str = esc(", ".join(au[:6]) + (f" 等({len(au)}位)" if len(au) > 6 else ""))

    tags = ""
    if is_hf:
        up = p.get("upvotes", 0)
        if up: tags += f'<span class="tag" style="color:var(--hf);border-color:rgba(255,157,0,.25);font-weight:600">&#9650; {up}</span>'
        org = p.get("organization", "")
        if org: tags += f'<span class="tag" style="color:var(--ac);border-color:rgba(123,147,255,.2)">{esc(org)}</span>'
    else:
        for c in (p.get("categories") or [])[:5]:
            col = CAT_COLORS.get(c, "")
            style = f'color:{col};border-color:{col}33' if col else ""
            tags += f'<span class="tag" style="{style}">{c}</span>'
        cm = p.get("comment", "")
        if cm:
            cm_short = esc(cm[:55] + "..." if len(cm) > 55 else cm)
            tags += f'<span class="tag" style="color:var(--ac2);border-color:rgba(69,212,200,.2);font-style:italic;font-size:.7rem">{cm_short}</span>'

    link = f"http://arxiv.org/abs/{p['id']}" if is_hf else p.get("link", "")
    hf_link = f'<a href="{p.get("link","")}" target="_blank">HF</a>' if is_hf else ""
    summary = esc(p.get("summary", ""))
    pid = esc(p.get("id", ""))
    title_esc = esc(p["title"]).replace("'", "&#39;")
    pdf = p.get("pdf", "")

    return f"""<div class="card" data-pid="{pid}"><div class="ch">
<span class="ci">{i}</span><div class="cb">
<div class="ct"><a href="{link}" target="_blank">{esc(p["title"])}</a></div>
<div class="ca">{au_str}</div>
<div class="tags">{tags}</div></div>
<div class="actions">
<button class="abtn fav-btn" onclick="toggleFav(this,'{pid}','{title_esc}','{link}','{pdf}')" title="收藏">&#9825;</button>
<button class="abtn del-btn" onclick="delPaper(this,'{pid}')" title="删除">&times;</button>
</div>
<div class="links">{hf_link}<a href="{link}" target="_blank">arXiv</a><a href="{p.get('pdf','')}" target="_blank">PDF</a></div>
</div><div class="abs" style="display:none">{summary}</div><div class="toggle" onclick="var a=this.previousElementSibling;if(a.style.display==='none'){{a.style.display='block';this.textContent='▲ 收起摘要'}}else{{a.style.display='none';this.textContent='▼ 查看摘要'}}">&#9660; 查看摘要</div></div>"""

def gen_daily_page(date_str):
    data = load_data(date_str)
    arxiv = data["arxiv"]
    hf = data["huggingface"]

    hf_cards = "".join(gen_paper_card(p, i+1, True) for i, p in enumerate(hf))

    cats = {}
    for p in arxiv:
        for c in (p.get("listed_in") or p.get("categories") or []):
            if c in CAT_NAMES: cats[c] = cats.get(c, 0) + 1

    arxiv_cat_btns = ""
    arxiv_cat_btns += f'<button class="fbtn on" data-cat="all" onclick="showCat(this)">全部 <span class="fc">{len(arxiv)}</span></button>'
    cat_sections = {}
    for cat in CAT_NAMES:
        if cat not in cats: continue
        col = CAT_COLORS.get(cat, "#888")
        arxiv_cat_btns += f'<button class="fbtn" data-cat="{cat}" onclick="showCat(this)"><span class="cdot" style="background:{col}"></span>{cat} <span class="fc">{cats[cat]}</span></button>'
        cp = [p for p in arxiv if cat in (p.get("listed_in") or p.get("categories") or [])]
        cat_sections[cat] = "".join(gen_paper_card(p, i+1) for i, p in enumerate(cp))

    all_arxiv_cards = "".join(gen_paper_card(p, i+1) for i, p in enumerate(arxiv))

    hf_section = ""
    if hf:
        hf_section = f"""<div class="sec-block" id="hf">
<div class="sec-head"><span class="sec-icon" style="background:var(--hf)">HF</span><span class="sec-title">HuggingFace 热门</span><span class="sec-cnt">{len(hf)} 篇</span></div>
<div id="hf-list">{hf_cards}</div></div>"""

    arxiv_section = ""
    if arxiv:
        arxiv_section = f"""<div class="sec-block" id="arxiv">
<div class="sec-head"><span class="sec-icon" style="background:var(--ac)">Ax</span><span class="sec-title">arXiv 论文</span><span class="sec-cnt">{len(arxiv)} 篇</span></div>
<div class="arxiv-filters">{arxiv_cat_btns}</div>
<div id="arxiv-list"></div></div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#0a0e1a"><meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="icon-192.png">
<title>{date_str} - arXiv Papers</title><style>{CSS}
.sec-block{{margin-bottom:28px}}
.sec-head{{display:flex;align-items:center;gap:10px;padding:14px 0 10px;border-bottom:1px solid var(--gb);margin-bottom:12px}}
.sec-icon{{width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:.7rem;font-weight:800}}
.sec-title{{font-size:1.1rem;font-weight:700}}
.sec-cnt{{font-size:.8rem;color:var(--t3);margin-left:auto}}
.arxiv-filters{{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:10px}}
</style></head><body>
<div class="topbar"><div class="topbar-in">
<a class="back" href="index.html">&#8592; 首页</a>
<h2>{date_str}</h2><span class="spacer"></span>
<div class="search"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
<input id="si" type="text" placeholder="搜索标题、作者..." oninput="filter()"></div>
<span class="cnt" id="cnt"></span></div></div>
<div class="list">
{hf_section}
{arxiv_section}
</div>
<button class="stop" id="st" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#8593;</button>
<script>
const AX={{"all":`{_js_escape(all_arxiv_cards)}`{_cat_entries(cat_sections)}}};
const HF=`{_js_escape(hf_cards)}`;
let curCat="all";
function showCat(b){{document.querySelectorAll('.arxiv-filters .fbtn').forEach(x=>x.classList.remove('on'));b.classList.add('on');curCat=b.dataset.cat;filter()}}
function filter(){{
const q=document.getElementById('si').value.toLowerCase();
let total=0;
const ae=document.getElementById('arxiv-list');
if(ae){{const d=document.createElement('div');d.innerHTML=AX[curCat]||AX['all'];const cards=[...d.querySelectorAll('.card')];let h='';cards.forEach(c=>{{const t=c.textContent.toLowerCase();if(!q||q.split(/\\s+/).every(w=>t.includes(w))){{h+=c.outerHTML;total++}}}});ae.innerHTML=h||'<div class="nr">没有匹配的论文</div>'}}
const he=document.getElementById('hf-list');
if(he){{const d=document.createElement('div');d.innerHTML=HF;const cards=[...d.querySelectorAll('.card')];let h='';cards.forEach(c=>{{const t=c.textContent.toLowerCase();if(!q||q.split(/\\s+/).every(w=>t.includes(w))){{h+=c.outerHTML;total++}}}});he.innerHTML=h||'<div class="nr">没有匹配的论文</div>'}}
document.getElementById('cnt').textContent=total+' 篇';
}}
window.addEventListener('scroll',()=>document.getElementById('st').classList.toggle('v',window.scrollY>400));

function getDeleted(){{try{{return JSON.parse(localStorage.getItem('del_papers')||'[]')}}catch{{return[]}}}}
function getFavs(){{try{{return JSON.parse(localStorage.getItem('fav_papers')||'{{}}')}}catch{{return{{}}}}}}
function delPaper(btn,pid){{const dels=getDeleted();if(!dels.includes(pid))dels.push(pid);localStorage.setItem('del_papers',JSON.stringify(dels));const card=btn.closest('.card');if(card)card.classList.add('deleted');setTimeout(()=>{{if(card)card.remove()}},300)}}
function toggleFav(btn,pid,title,link,pdf){{const favs=getFavs();if(favs[pid]){{delete favs[pid];btn.innerHTML='&#9825;';btn.classList.remove('on')}}else{{favs[pid]={{title,link,pdf,t:Date.now()}};btn.innerHTML='&#9829;';btn.classList.add('on')}}localStorage.setItem('fav_papers',JSON.stringify(favs))}}
function initCards(){{const dels=getDeleted();const favs=getFavs();document.querySelectorAll('.card[data-pid]').forEach(c=>{{const pid=c.dataset.pid;if(dels.includes(pid)){{c.remove();return}}const fb=c.querySelector('.fav-btn');if(fb&&favs[pid]){{fb.innerHTML='&#9829;';fb.classList.add('on')}}}})}}
filter();initCards();
</script></body></html>"""

def _js_escape(s):
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

def _cat_entries(cat_sections):
    parts = ""
    for cat, html_str in cat_sections.items():
        parts += f',"{cat}":`{_js_escape(html_str)}`'
    return parts


def gen_pwa_files():
    manifest = {
        "name": "arXiv Papers",
        "short_name": "Papers",
        "description": "AI 论文每日追踪",
        "start_url": ".",
        "display": "standalone",
        "background_color": "#0a0e1a",
        "theme_color": "#0a0e1a",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        ]
    }
    with open(os.path.join(SITE_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    sw = """const V='v1';
self.addEventListener('install',e=>e.waitUntil(caches.open(V).then(c=>c.addAll(['./',]))));
self.addEventListener('fetch',e=>{e.respondWith(fetch(e.request).then(r=>{if(r&&r.status===200){const c=r.clone();caches.open(V).then(cache=>cache.put(e.request,c))}return r}).catch(()=>caches.match(e.request)))});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k))))));"""
    with open(os.path.join(SITE_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw)

    gen_icon(192)
    gen_icon(512)


def gen_icon(size):
    import base64, struct, zlib
    w = h = size
    raw = []
    cx, cy = w // 2, h // 2
    r1 = int(size * 0.38)
    r2 = int(size * 0.22)
    for y in range(h):
        row = b'\x00'
        for x in range(w):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            if dist <= r1:
                t = dist / r1
                rr = int(123 + (69 - 123) * t)
                gg = int(147 + (212 - 147) * t)
                bb = int(255 + (200 - 255) * t)
                aa = 255
            elif dist <= r1 + 2:
                rr, gg, bb, aa = 10, 14, 26, 255
            else:
                rr, gg, bb, aa = 10, 14, 26, 255
            row += struct.pack('BBBB', rr, gg, bb, aa)
        raw.append(row)
    raw_data = b''.join(raw)

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw_data, 9))
    png += chunk(b'IEND', b'')
    with open(os.path.join(SITE_DIR, f"icon-{size}.png"), "wb") as f:
        f.write(png)


def gen_favorites_page():
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#0a0e1a"><meta name="apple-mobile-web-app-capable" content="yes">
<link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="icon-192.png">
<title>收藏夹 - arXiv Papers</title><style>{CSS}
.fav-card{{background:var(--glass);border:1px solid var(--gb);border-radius:12px;padding:16px 20px;margin-bottom:9px;display:flex;align-items:center;gap:14px;transition:all .2s}}
.fav-card:hover{{border-color:rgba(255,255,255,.16);background:rgba(255,255,255,.1)}}
.fav-heart{{color:#ff4d6a;font-size:1.1rem;flex-shrink:0}}
.fav-info{{flex:1;min-width:0}}
.fav-title{{font-size:1rem;font-weight:700;line-height:1.4;margin-bottom:3px}}
.fav-title a{{color:var(--t)}}.fav-title a:hover{{color:var(--ac)}}
.fav-links{{display:flex;gap:5px;flex-shrink:0}}
.fav-links a{{font-size:.78rem;font-weight:500;color:var(--ac);padding:4px 10px;border:1px solid rgba(123,147,255,.2);border-radius:7px}}
.fav-links a:hover{{background:rgba(123,147,255,.1)}}
.rm-btn{{width:28px;height:28px;border:1px solid var(--gb);border-radius:7px;background:transparent;color:var(--t3);font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s;flex-shrink:0}}
.rm-btn:hover{{color:#ff6b6b;border-color:rgba(255,107,107,.3);background:rgba(255,107,107,.08)}}
.clear-btn{{font-size:.78rem;padding:5px 14px;border-radius:8px;background:rgba(255,107,107,.1);border:1px solid rgba(255,107,107,.2);color:#ff6b6b;cursor:pointer;font-family:inherit;transition:all .15s}}
.clear-btn:hover{{background:rgba(255,107,107,.2)}}
</style></head><body>
<div class="topbar"><div class="topbar-in">
<a class="back" href="index.html">&#8592; 首页</a>
<h2>&#9829; 收藏夹</h2><span class="spacer"></span>
<span class="cnt" id="cnt"></span>
<button class="clear-btn" onclick="clearAll()">清空收藏</button>
</div></div>
<div class="list" id="fl" style="max-width:1100px;margin:0 auto;padding:12px 20px 60px"></div>
<script>
function getFavs(){{try{{return JSON.parse(localStorage.getItem('fav_papers')||'{{}}')}}catch{{return{{}}}}}}
function render(){{
const favs=getFavs();const keys=Object.keys(favs).sort((a,b)=>(favs[b].t||0)-(favs[a].t||0));
const el=document.getElementById('fl');
if(!keys.length){{el.innerHTML='<div class="nr">还没有收藏论文<br><br><a href="index.html" style="color:var(--ac)">去看看今天的论文 →</a></div>';document.getElementById('cnt').textContent='0 篇';return}}
let h='';
keys.forEach(pid=>{{const p=favs[pid];
h+=`<div class="fav-card" data-pid="${{pid}}"><span class="fav-heart">&#9829;</span><div class="fav-info"><div class="fav-title"><a href="${{p.link}}" target="_blank">${{p.title}}</a></div></div><div class="fav-links"><a href="${{p.link}}" target="_blank">arXiv</a><a href="${{p.pdf}}" target="_blank">PDF</a></div><button class="rm-btn" onclick="removeFav('${{pid}}')" title="取消收藏">&times;</button></div>`;
}});
el.innerHTML=h;document.getElementById('cnt').textContent=keys.length+' 篇';
}}
function removeFav(pid){{const favs=getFavs();delete favs[pid];localStorage.setItem('fav_papers',JSON.stringify(favs));render()}}
function clearAll(){{if(confirm('确定清空所有收藏？')){{localStorage.setItem('fav_papers','{{}}');render()}}}}
render();
</script></body></html>"""


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    os.makedirs(SITE_DIR, exist_ok=True)

    print("Generating PWA files...")
    gen_pwa_files()

    print("Generating index.html...")
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(gen_index())

    print("Generating favorites.html...")
    with open(os.path.join(SITE_DIR, "favorites.html"), "w", encoding="utf-8") as f:
        f.write(gen_favorites_page())

    dates = get_dates()
    for d in dates:
        print(f"Generating {d}.html...")
        with open(os.path.join(SITE_DIR, f"{d}.html"), "w", encoding="utf-8") as f:
            f.write(gen_daily_page(d))

    print(f"Done! {len(dates)+1} pages generated in site/")


if __name__ == "__main__":
    main()
