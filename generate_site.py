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
:root{--bg:#070a13;--surface:rgba(255,255,255,0.03);--surface-hover:rgba(255,255,255,0.06);--border:rgba(255,255,255,0.08);--border-hover:rgba(255,255,255,0.15);--t:#f1f4f9;--t2:#9ba1b0;--t3:#656a7a;--ac:#6382ff;--ac-hover:#829aff;--ac2:#38d9c9;--hf:#ff9d00}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--t);min-height:100vh;line-height:1.5;background-image:url('bg.png');background-size:cover;background-position:center;background-attachment:fixed;background-repeat:no-repeat}
body::before{content:"";position:fixed;inset:0;background:rgba(7,10,19,0.85);pointer-events:none;z-index:0}
.c{max-width:1040px;margin:0 auto;padding:60px 20px;position:relative;z-index:1}
a{color:var(--ac);text-decoration:none;transition:color .2s}a:hover{color:var(--ac-hover)}
h1{font-size:3rem;font-weight:800;letter-spacing:-0.03em;background:linear-gradient(135deg,#fff 30%,#a5b4fc 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin-bottom:16px}
.sub{text-align:center;color:var(--t2);margin-bottom:12px;font-size:1.1rem;font-weight:400;letter-spacing:0.01em}
.pills{display:flex;justify-content:center;gap:8px;margin-bottom:60px;flex-wrap:wrap}
.pill{font-size:.75rem;font-weight:500;padding:4px 14px;border-radius:20px;background:var(--surface);border:1px solid var(--border);color:var(--t2);backdrop-filter:blur(8px);transition:all .2s}
.pill:hover{background:var(--surface-hover);border-color:var(--border-hover);color:var(--t)}
.section{margin-bottom:50px}
.label{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--t3);margin-bottom:20px;display:flex;align-items:center;gap:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.dcard{display:flex;align-items:center;justify-content:space-between;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px 24px;color:var(--t);backdrop-filter:blur(12px);transition:all .3s cubic-bezier(0.25, 0.8, 0.25, 1);position:relative;overflow:hidden}
.dcard::before{content:"";position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(180deg,rgba(255,255,255,0.03) 0%,transparent 100%);opacity:0;transition:opacity .3s}
.dcard:hover{border-color:var(--border-hover);transform:translateY(-2px);box-shadow:0 12px 30px rgba(0,0,0,0.3);background:var(--surface-hover)}
.dcard:hover::before{opacity:1}
.dcard .dt{font-weight:700;font-size:1.1rem;letter-spacing:-0.01em;position:relative;z-index:1}
.src-links{display:flex;gap:8px;flex-wrap:wrap;position:relative;z-index:1}
.src-btn{font-size:.75rem;font-weight:600;padding:6px 14px;border-radius:10px;display:inline-flex;align-items:center;gap:6px;transition:all .2s;text-decoration:none}
.src-btn span{font-weight:800;opacity:0.9}
.src-btn.hf{background:rgba(255,157,0,0.08);border:1px solid rgba(255,157,0,0.2);color:#ffb840}
.src-btn.hf:hover{background:rgba(255,157,0,0.15);border-color:rgba(255,157,0,0.3);color:#ffc860;transform:translateY(-1px)}
.src-btn.ax{background:rgba(99,130,255,0.08);border:1px solid rgba(99,130,255,0.2);color:#9db4ff}
.src-btn.ax:hover{background:rgba(99,130,255,0.15);border-color:rgba(99,130,255,0.3);color:#b0c4ff;transform:translateY(-1px)}
.dcard-refresh{position:absolute;top:10px;right:38px;width:24px;height:24px;border:none;border-radius:8px;background:transparent;color:var(--t3);font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;transition:all .2s;z-index:2}
.dcard:hover .dcard-refresh{opacity:1}
.dcard-refresh:hover{color:var(--ac);background:rgba(99,130,255,0.15)}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
.dcard-del{position:absolute;top:10px;right:10px;width:24px;height:24px;border:none;border-radius:8px;background:transparent;color:var(--t3);font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;transition:all .2s;z-index:2}
.dcard:hover .dcard-del{opacity:1}
.dcard-del:hover{color:#ff6b6b;background:rgba(255,107,107,0.15)}
.topbar{position:sticky;top:0;z-index:100;background:rgba(7,10,19,0.85);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:14px 20px}
.topbar-in{max-width:1100px;margin:0 auto;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.back{color:var(--t2);font-size:.9rem;font-weight:500;display:flex;align-items:center;gap:6px;transition:color .2s}
.back:hover{color:var(--t)}
.topbar h2{font-size:1.1rem;font-weight:700;letter-spacing:-0.01em;color:var(--t)}
.spacer{flex:1}
.search{position:relative;width:300px}
.search input{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 14px 10px 40px;color:var(--t);font-size:.9rem;font-family:inherit;outline:0;transition:all .2s;backdrop-filter:blur(8px)}
.search input:focus{border-color:var(--ac);background:var(--surface-hover);box-shadow:0 0 0 3px rgba(99,130,255,0.15)}
.search input::placeholder{color:var(--t3)}
.search svg{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--t2)}
.cnt{font-size:.85rem;color:var(--t3);font-weight:500;white-space:nowrap}
.filters{max-width:1100px;margin:0 auto;padding:20px 20px 0;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.fbtn{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:8px 16px;color:var(--t2);font-size:.85rem;font-weight:500;cursor:pointer;font-family:inherit;white-space:nowrap;display:inline-flex;align-items:center;gap:6px;transition:all .2s;backdrop-filter:blur(8px)}
.fbtn:hover{border-color:var(--border-hover);color:var(--t);background:var(--surface-hover);transform:translateY(-1px)}
.fbtn.on{background:var(--ac);border-color:var(--ac);color:#fff;box-shadow:0 4px 12px rgba(99,130,255,0.2)}
.fbtn.on-hf{background:var(--hf);border-color:var(--hf);color:#fff;box-shadow:0 4px 12px rgba(255,157,0,0.2)}
.fc{opacity:.8;font-size:.75rem;font-weight:600}
.cdot{width:8px;height:8px;border-radius:50%;display:inline-block}
.fsep{width:1px;height:24px;background:var(--border);margin:0 4px}
.list{max-width:1100px;margin:0 auto;padding:20px 20px 80px}
.sec-block{margin-bottom:40px}
.sec-head{display:flex;align-items:center;gap:12px;padding:0 0 16px;border-bottom:1px solid var(--border);margin-bottom:20px}
.sec-icon{width:32px;height:32px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:.8rem;font-weight:800;box-shadow:0 4px 12px rgba(0,0,0,0.2)}
.sec-title{font-size:1.2rem;font-weight:700;letter-spacing:-0.01em}
.sec-cnt{font-size:.85rem;font-weight:500;color:var(--t3);margin-left:auto}
.arxiv-filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px 28px;margin-bottom:16px;transition:all .3s cubic-bezier(0.25, 0.8, 0.25, 1);backdrop-filter:blur(12px)}
.card:hover{border-color:var(--border-hover);background:var(--surface-hover);transform:translateY(-2px);box-shadow:0 12px 30px rgba(0,0,0,0.2)}
.ch{display:flex;align-items:flex-start;gap:16px}
.ci{font-size:.8rem;color:var(--t3);min-width:30px;padding-top:4px;font-weight:700;font-variant-numeric:tabular-nums}
.cb{flex:1;min-width:0}
.ct{font-size:1.15rem;font-weight:700;line-height:1.4;margin-bottom:6px;letter-spacing:-0.01em}
.ct a{color:var(--t)}.ct a:hover{color:var(--ac)}
.sum-cn{font-size:.9rem;font-weight:500;color:var(--ac2);margin-top:4px;margin-bottom:8px;line-height:1.5}
.ca{font-size:.9rem;color:var(--t2);margin-bottom:12px;line-height:1.5}
.tags{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.tag{font-size:.75rem;font-weight:600;padding:4px 10px;border-radius:6px;background:rgba(255,255,255,0.04);border:1px solid var(--border);color:var(--t2)}
.actions{display:flex;gap:6px;flex-shrink:0;align-items:flex-start;margin-left:8px}
.abtn{width:36px;height:36px;border:1px solid var(--border);border-radius:10px;background:var(--surface);color:var(--t2);font-size:1.1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;font-family:inherit}
.abtn:hover{background:var(--surface-hover);border-color:var(--border-hover);color:var(--t);transform:translateY(-1px)}
.chk-btn:hover,.chk-btn.on{color:#38d9c9;border-color:rgba(56,217,201,0.3);background:rgba(56,217,201,0.08);box-shadow:0 4px 12px rgba(56,217,201,0.15)}
.card.checked{border-color:rgba(56,217,201,0.25);background:rgba(56,217,201,0.03)}
.fav-btn:hover,.fav-btn.on{color:#ff4d6a;border-color:rgba(255,77,106,0.3);background:rgba(255,77,106,0.08);box-shadow:0 4px 12px rgba(255,77,106,0.15)}
.fav-btn.on{font-size:1rem}
.del-btn:hover{color:#ff6b6b;border-color:rgba(255,107,107,0.3);background:rgba(255,107,107,0.08)}
.card.deleted{opacity:0;transform:scale(0.95);pointer-events:none;max-height:0;padding:0;margin:0;border:0;overflow:hidden;transition:all .3s cubic-bezier(0.25, 0.8, 0.25, 1)}
.links{display:flex;gap:6px;flex-shrink:0;align-items:flex-start;margin-left:8px}
.links a{font-size:.8rem;font-weight:600;color:var(--ac);padding:8px 14px;border:1px solid rgba(99,130,255,0.2);border-radius:10px;background:rgba(99,130,255,0.05);transition:all .2s}
.links a:hover{background:rgba(99,130,255,0.15);border-color:rgba(99,130,255,0.3);transform:translateY(-1px)}
.abs{margin-top:16px;margin-left:46px;font-size:.95rem;line-height:1.7;color:var(--t2);background:rgba(0,0,0,0.2);padding:16px 20px;border-radius:12px;border:1px solid var(--border)}
.toggle{margin-top:12px;margin-left:46px;font-size:.85rem;font-weight:600;color:var(--ac);cursor:pointer;user-select:none;padding:6px 12px;display:inline-flex;align-items:center;gap:6px;border-radius:8px;background:var(--surface);border:1px solid var(--border);transition:all .2s}
.toggle:hover{background:var(--surface-hover);border-color:var(--ac);color:var(--ac-hover);transform:translateY(-1px)}
.nr{text-align:center;padding:80px 20px;color:var(--t3);font-size:1rem}
.stop{position:fixed;bottom:30px;right:30px;width:48px;height:48px;background:var(--ac);border:1px solid rgba(255,255,255,0.1);border-radius:14px;color:#fff;font-size:1.3rem;cursor:pointer;opacity:0;transition:all .3s cubic-bezier(0.25, 0.8, 0.25, 1);z-index:99;box-shadow:0 8px 24px rgba(99,130,255,0.25);transform:translateY(20px)}
.stop.v{opacity:1;transform:translateY(0)}
.stop:hover{background:var(--ac-hover);transform:translateY(-3px);box-shadow:0 12px 30px rgba(99,130,255,0.35)}
.fetch-panel{display:flex;align-items:center;gap:12px;margin-bottom:20px;flex-wrap:wrap;background:var(--surface);padding:16px 20px;border-radius:16px;border:1px solid var(--border);backdrop-filter:blur(12px)}
.fetch-date{background:rgba(0,0,0,0.2);border:1px solid var(--border);border-radius:10px;padding:8px 14px;color:var(--t);font-size:.9rem;font-weight:500;font-family:inherit;outline:0;color-scheme:dark;transition:all .2s}
.fetch-date:focus{border-color:var(--ac);box-shadow:0 0 0 3px rgba(99,130,255,0.15)}
.rbtn{font-size:.85rem;font-weight:600;padding:8px 18px;border-radius:10px;background:var(--ac);color:#fff;text-transform:none;letter-spacing:0;text-decoration:none;transition:all .2s;display:inline-flex;align-items:center;gap:6px;border:1px solid rgba(255,255,255,0.1);cursor:pointer;font-family:inherit;box-shadow:0 4px 12px rgba(99,130,255,0.2)}
.rbtn:hover{background:var(--ac-hover);color:#fff;transform:translateY(-1px);box-shadow:0 6px 16px rgba(99,130,255,0.3)}
.stop-btn{background:var(--surface);color:var(--t2);border:1px solid var(--border);box-shadow:none}.stop-btn:hover{background:var(--surface-hover);color:var(--t);border-color:var(--border-hover)}
.fetch-status{font-size:.85rem;color:var(--t2);font-weight:500;margin-left:4px}
footer{text-align:center;padding:40px 0;color:var(--t3);font-size:.85rem;margin-top:40px;border-top:1px solid var(--border)}
.chat-btn{position:fixed;bottom:30px;left:30px;width:52px;height:52px;background:var(--ac);border:1px solid rgba(255,255,255,0.1);border-radius:50%;color:#fff;font-size:1.5rem;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:200;box-shadow:0 8px 24px rgba(99,130,255,0.3);transition:all .3s}
.chat-btn:hover{transform:scale(1.1);box-shadow:0 12px 30px rgba(99,130,255,0.4)}
.chat-box{position:fixed;bottom:90px;left:20px;width:380px;max-width:calc(100vw - 40px);height:500px;max-height:calc(100vh - 120px);background:rgba(7,10,19,0.95);border:1px solid var(--border);border-radius:20px;z-index:200;display:none;flex-direction:column;backdrop-filter:blur(20px);box-shadow:0 20px 60px rgba(0,0,0,0.5)}
.chat-box.open{display:flex}
.chat-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.chat-header span{font-weight:700;font-size:1rem}
.chat-close{background:none;border:none;color:var(--t3);font-size:1.3rem;cursor:pointer;padding:4px}
.chat-close:hover{color:var(--t)}
.chat-msgs{flex:1;overflow-y:auto;padding:16px 20px;display:flex;flex-direction:column;gap:12px}
.chat-msg{max-width:85%;padding:12px 16px;border-radius:14px;font-size:.9rem;line-height:1.6;word-break:break-word}
.chat-msg.user{align-self:flex-end;background:var(--ac);color:#fff;border-bottom-right-radius:4px}
.chat-msg.bot{align-self:flex-start;background:var(--surface-hover);color:var(--t);border:1px solid var(--border);border-bottom-left-radius:4px}
.chat-msg.loading{color:var(--t3);font-style:italic}
.chat-input{display:flex;gap:8px;padding:12px 16px;border-top:1px solid var(--border);flex-shrink:0}
.chat-input input{flex:1;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 14px;color:var(--t);font-size:.9rem;font-family:inherit;outline:0}
.chat-input input:focus{border-color:var(--ac)}
.chat-input button{background:var(--ac);border:none;border-radius:12px;color:#fff;padding:10px 16px;cursor:pointer;font-family:inherit;font-weight:600;font-size:.9rem;transition:all .2s}
.chat-input button:hover{background:var(--ac-hover)}
.fav-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px 24px;margin-bottom:12px;display:flex;align-items:center;gap:20px;transition:all .3s cubic-bezier(0.25, 0.8, 0.25, 1);backdrop-filter:blur(12px)}
.fav-card:hover{border-color:var(--border-hover);background:var(--surface-hover);transform:translateY(-2px);box-shadow:0 12px 30px rgba(0,0,0,0.2)}
.fav-heart{color:#ff4d6a;font-size:1.4rem;flex-shrink:0;text-shadow:0 0 12px rgba(255,77,106,0.3)}
.fav-info{flex:1;min-width:0}
.fav-title{font-size:1.1rem;font-weight:700;line-height:1.4;margin-bottom:6px;letter-spacing:-0.01em}
.fav-title a{color:var(--t)}.fav-title a:hover{color:var(--ac)}
.fav-links{display:flex;gap:8px;flex-shrink:0}
.fav-links a{font-size:.8rem;font-weight:600;color:var(--ac);padding:6px 14px;border:1px solid rgba(99,130,255,0.2);border-radius:10px;background:rgba(99,130,255,0.05);transition:all .2s}
.fav-links a:hover{background:rgba(99,130,255,0.15);border-color:rgba(99,130,255,0.3);transform:translateY(-1px)}
.rm-btn{width:36px;height:36px;border:1px solid var(--border);border-radius:10px;background:var(--surface);color:var(--t3);font-size:1.2rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0}
.rm-btn:hover{color:#ff6b6b;border-color:rgba(255,107,107,0.3);background:rgba(255,107,107,0.08);transform:translateY(-1px)}
.clear-btn{font-size:.85rem;font-weight:600;padding:8px 16px;border-radius:10px;background:rgba(255,107,107,0.1);border:1px solid rgba(255,107,107,0.2);color:#ff6b6b;cursor:pointer;font-family:inherit;transition:all .2s}
.clear-btn:hover{background:rgba(255,107,107,0.2);border-color:rgba(255,107,107,0.4);transform:translateY(-1px)}
@media(max-width:768px){
  h1{font-size:2rem}
  .c{padding:30px 16px}
  .search{width:100%;order:10}
  .links{display:none}
  .ci{display:none}
  .abs{margin-left:0;padding:12px 16px}
  .toggle{margin-left:0}
  .ch{gap:12px;flex-direction:column}
  .actions{margin-left:0;margin-top:12px;width:100%;justify-content:flex-start}
  .card{padding:20px}
  .fav-card{flex-direction:column;align-items:flex-start;gap:12px;padding:16px}
  .fav-links{width:100%}
  .rm-btn{position:absolute;top:16px;right:16px}
}
"""

CHAT_HTML = """
<button class="chat-btn" onclick="document.getElementById('chatbox').classList.toggle('open')" title="AI 助手">&#128172;</button>
<div class="chat-box" id="chatbox">
<div class="chat-header"><span>Frontier AI</span><button class="chat-close" onclick="document.getElementById('chatbox').classList.remove('open')">&times;</button></div>
<div class="chat-msgs" id="chatmsgs"><div class="chat-msg bot">你好！我是 AI 助手，可以帮你解读论文、回答 AI 相关问题。</div></div>
<div class="chat-input"><input id="chatin" placeholder="输入问题..." onkeydown="if(event.key==='Enter')sendChat()"><button onclick="sendChat()">发送</button></div>
</div>
<script>
function getZhipuKey(){let k=localStorage.getItem('zhipu_key');if(!k){k=prompt('输入智谱 API Key（GLM-4-Flash 免费）');if(k)localStorage.setItem('zhipu_key',k)}return k}
async function sendChat(){
const input=document.getElementById('chatin');const msg=input.value.trim();if(!msg)return;
const key=getZhipuKey();if(!key)return;
const msgs=document.getElementById('chatmsgs');
msgs.innerHTML+=`<div class="chat-msg user">${msg.replace(/</g,'&lt;')}</div>`;
msgs.innerHTML+=`<div class="chat-msg bot loading" id="botloading">思考中...</div>`;
msgs.scrollTop=msgs.scrollHeight;input.value='';
try{
const r=await fetch('https://open.bigmodel.cn/api/paas/v4/chat/completions',{
method:'POST',headers:{'Authorization':'Bearer '+key,'Content-Type':'application/json'},
body:JSON.stringify({model:'glm-4-flash',messages:[{role:'system',content:'你是一个AI论文助手，帮助用户理解论文、解释概念、回答AI相关问题。用中文回答，简洁专业。'},{role:'user',content:msg}],temperature:0.7,max_tokens:1000})
});
const d=await r.json();const reply=d.choices[0].message.content;
document.getElementById('botloading').outerHTML=`<div class="chat-msg bot">${reply.replace(/</g,'&lt;').replace(/\\n/g,'<br>')}</div>`;
}catch(e){document.getElementById('botloading').outerHTML=`<div class="chat-msg bot" style="color:#ff6b6b">请求失败: ${e.message}</div>`}
msgs.scrollTop=msgs.scrollHeight;
}
</script>
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

def load_cvpr():
    path = os.path.join(DATA_DIR, "cvpr26.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _gen_cvpr_section():
    papers = load_cvpr()
    if not papers:
        return ""
    return f"""<div class="section">
<div class="label" style="display:flex;align-items:center;gap:12px">CVPR 2026</div>
<div class="dcard" style="max-width:320px"><a href="cvpr26.html" style="text-decoration:none;color:var(--t);flex:1;display:flex;align-items:center;justify-content:space-between"><span class="dt">CVPR 2026 Papers</span><div class="badges"><span class="badge b-a">{len(papers)}</span></div></a><button class="dcard-refresh" onclick="refreshCvpr(event)" style="position:relative;top:0;right:0;margin-left:12px" title="重新抓取">&#x21bb;</button></div>
</div>"""

def gen_cvpr_page():
    papers = load_cvpr()
    if not papers:
        return None
    cards = "".join(gen_paper_card(p, i+1) for i, p in enumerate(papers))
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#0a0e1a"><meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="icon-192.png">
<title>CVPR 2026 - arXiv Papers</title><style>{CSS}</style></head><body>
<div class="topbar"><div class="topbar-in">
<a class="back" href="index.html">&#8592; 首页</a>
<h2>CVPR 2026</h2><span class="spacer"></span>
<button class="rbtn" onclick="doFetchCvpr()">&#x21bb; 更新抓取</button>
<span class="fetch-status" id="fs" style="font-size:.8rem;color:var(--t3)"></span>
<div class="search"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
<input id="si" type="text" placeholder="搜索标题、作者..." oninput="filter()"></div>
<span class="cnt" id="cnt"></span></div></div>
<div class="list" id="pl"></div>
<button class="stop" id="st" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#8593;</button>
<script>
const ALL=`{_js_escape(cards)}`;
function getDeleted(){{try{{return JSON.parse(localStorage.getItem('del_papers')||'[]')}}catch{{return[]}}}}
function getFavs(){{try{{return JSON.parse(localStorage.getItem('fav_papers')||'{{}}')}}catch{{return{{}}}}}}
function getChecked(){{try{{return JSON.parse(localStorage.getItem('chk_papers')||'[]')}}catch{{return[]}}}}
function toggleCheck(btn,pid){{const chks=getChecked();const card=btn.closest('.card');if(chks.includes(pid)){{chks.splice(chks.indexOf(pid),1);btn.classList.remove('on');if(card)card.classList.remove('checked')}}else{{chks.push(pid);btn.classList.add('on');if(card)card.classList.add('checked')}}localStorage.setItem('chk_papers',JSON.stringify(chks))}}
function renum(){{document.querySelectorAll('.card').forEach((c,i)=>{{const ci=c.querySelector('.ci');if(ci)ci.textContent=i+1}})}}
function delPaper(btn,pid){{const dels=getDeleted();if(!dels.includes(pid))dels.push(pid);localStorage.setItem('del_papers',JSON.stringify(dels));const card=btn.closest('.card');if(card){{card.style.transition='all .3s';card.style.opacity='0';card.style.transform='scale(.97)';setTimeout(()=>{{card.remove();renum()}},300)}}}}
function toggleFav(btn,pid,title,link,pdf){{const favs=getFavs();if(favs[pid]){{delete favs[pid];btn.innerHTML='&#9825;';btn.classList.remove('on')}}else{{favs[pid]={{title,link,pdf,t:Date.now()}};btn.innerHTML='&#9829;';btn.classList.add('on')}}localStorage.setItem('fav_papers',JSON.stringify(favs))}}
function initCards(){{const dels=getDeleted();const favs=getFavs();const chks=getChecked();document.querySelectorAll('.card[data-pid]').forEach(c=>{{const pid=c.dataset.pid;if(dels.includes(pid)){{c.remove();return}}const fb=c.querySelector('.fav-btn');if(fb&&favs[pid]){{fb.innerHTML='&#9829;';fb.classList.add('on')}}const cb=c.querySelector('.chk-btn');if(cb&&chks.includes(pid)){{cb.classList.add('on');c.classList.add('checked')}}}});renum()}};
function filter(){{const q=document.getElementById('si').value.toLowerCase();const el=document.getElementById('pl');const d=document.createElement('div');d.innerHTML=ALL;const cards=[...d.querySelectorAll('.card')];let n=0;let h='';cards.forEach(c=>{{const t=c.textContent.toLowerCase();if(!q||q.split(/\\s+/).every(w=>t.includes(w))){{h+=c.outerHTML;n++}}}});el.innerHTML=h||'<div class="nr">没有匹配的论文</div>';document.getElementById('cnt').textContent=n+' 篇';initCards()}}
window.addEventListener('scroll',()=>document.getElementById('st').classList.toggle('v',window.scrollY>400));

const REPO='Issac304/arxiv-papers';
function getToken(){{let t=localStorage.getItem('gh_token');if(!t){{t=prompt('首次使用需输入 GitHub Token\\n\\nGitHub → Settings → Developer settings → Personal access tokens → Fine-grained → Generate\\n\\n权限勾选 Actions: Read and Write');if(t)localStorage.setItem('gh_token',t)}}return t}}
async function doFetchCvpr(){{
const token=getToken();if(!token)return;
const fs=document.getElementById('fs');
fs.textContent='正在触发 CVPR 抓取...';fs.style.color='var(--ac)';
try{{
const r=await fetch(`https://api.github.com/repos/${{REPO}}/actions/workflows/daily.yml/dispatches`,{{
method:'POST',headers:{{'Authorization':`token ${{token}}`,'Accept':'application/vnd.github.v3+json'}},
body:JSON.stringify({{ref:'master',inputs:{{date:''}}}})
}});
if(r.status===204){{fs.textContent='已触发抓取，约2-3分钟后刷新页面查看';fs.style.color='var(--ac2)';pollCvpr(token)}}
else if(r.status===401){{localStorage.removeItem('gh_token');fs.textContent='Token 无效，请重新输入';fs.style.color='#ff6b6b'}}
else{{fs.textContent='触发失败';fs.style.color='#ff6b6b'}}
}}catch(e){{fs.textContent='网络错误: '+e.message;fs.style.color='#ff6b6b'}}
}}
async function pollCvpr(token){{
const fs=document.getElementById('fs');
for(let i=0;i<30;i++){{
await new Promise(r=>setTimeout(r,5000));
try{{
const r=await fetch(`https://api.github.com/repos/${{REPO}}/actions/runs?per_page=1`,{{headers:{{'Authorization':`token ${{token}}`}}}});
const d=await r.json();const run=d.workflow_runs&&d.workflow_runs[0];
if(!run)continue;
if(run.status==='completed'){{
if(run.conclusion==='success'){{fs.textContent='CVPR 抓取完成! 刷新页面查看';fs.style.color='#45d4c8'}}
else{{fs.textContent='抓取结束 ('+run.conclusion+')';fs.style.color='#ff6b6b'}}
return}}
fs.textContent='抓取中... ('+run.status+')';
}}catch{{}}
}}
}}

filter();
</script>{CHAT_HTML}</body></html>"""

def gen_index():
    dates = get_dates()
    date_cards = ""
    for d in dates:
        data = load_data(d)
        ac = len(data["arxiv"])
        hc = len(data["huggingface"])
        hf_link = f'<a class="src-btn hf" href="{d}.html#hf">HF 热门 <span>{hc}</span></a>' if hc else '<span class="src-btn hf" style="opacity:0.3;pointer-events:none">HF 热门 <span>0</span></span>'
        ax_link = f'<a class="src-btn ax" href="{d}.html#arxiv">arXiv <span>{ac}</span></a>' if ac else '<span class="src-btn ax" style="opacity:0.3;pointer-events:none">arXiv <span>0</span></span>'
        date_cards += f'<div class="dcard" id="dc-{d}"><span class="dt">{d}</span><div class="src-links">{hf_link}{ax_link}</div><button class="dcard-refresh" onclick="refreshDate(\'{d}\')" title="重新抓取">&#x21bb;</button><button class="dcard-del" onclick="delDate(\'{d}\')" title="隐藏">&times;</button></div>\n'

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#0a0e1a"><meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="icon-192.png">
<title>arXiv Papers</title><style>{CSS}</style></head><body>
<div class="c">
<h1>探索智能边界 · 每天掌握10000篇最新arXiv论文</h1>
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
{_gen_cvpr_section()}
<footer>arXiv Papers &bull; <a href="https://arxiv.org">arXiv.org</a> &bull; <a href="https://huggingface.co/papers">HuggingFace</a></footer>
</div>
<script>
if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{{}});
var now=new Date();document.getElementById('fd').value=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0');

async function refreshDate(d){{
const token=getToken();if(!token)return;
const btn=event.target;btn.style.animation='spin 1s linear infinite';
try{{
const r=await fetch(`https://api.github.com/repos/${{REPO}}/actions/workflows/daily.yml/dispatches`,{{
method:'POST',headers:{{'Authorization':`token ${{token}}`,'Accept':'application/vnd.github.v3+json'}},
body:JSON.stringify({{ref:'master',inputs:{{date:d}}}})
}});
if(r.status===204){{btn.style.color='var(--ac2)';setTimeout(()=>{{btn.style.animation='';btn.title='已触发，2分钟后刷新'}},2000)}}
else{{btn.style.animation='';btn.style.color='#ff6b6b'}}
}}catch{{btn.style.animation='';btn.style.color='#ff6b6b'}}
}}
async function refreshCvpr(e){{
e.preventDefault();
const token=getToken();if(!token)return;
const btn=e.target;btn.style.animation='spin 1s linear infinite';
try{{
const r=await fetch(`https://api.github.com/repos/${{REPO}}/actions/workflows/daily.yml/dispatches`,{{
method:'POST',headers:{{'Authorization':`token ${{token}}`,'Accept':'application/vnd.github.v3+json'}},
body:JSON.stringify({{ref:'master',inputs:{{date:''}}}})
}});
if(r.status===204){{btn.style.color='var(--ac2)';setTimeout(()=>{{btn.style.animation='';btn.title='已触发，2分钟后刷新'}},2000)}}
else{{btn.style.animation='';btn.style.color='#ff6b6b'}}
}}catch{{btn.style.animation='';btn.style.color='#ff6b6b'}}
}}
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
body:JSON.stringify({{ref:'master',inputs:{{date:dateVal}}}})
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
</script>{CHAT_HTML}</body></html>"""

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
{f'<div class="sum-cn">{esc(p["summary_cn"])}</div>' if p.get("summary_cn") else ""}</div>
<div class="actions">
<button class="abtn chk-btn" onclick="toggleCheck(this,'{pid}')" title="已读">&#10003;</button>
<button class="abtn fav-btn" onclick="toggleFav(this,'{pid}','{title_esc}','{link}','{pdf}')" title="收藏">&#9825;</button>
<button class="abtn del-btn" onclick="delPaper(this,'{pid}')" title="删除">&times;</button>
</div>
<div class="links">{hf_link}<a href="{link}" target="_blank">arXiv</a><a href="{p.get('pdf','')}" target="_blank">PDF</a></div>
</div></div>"""

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
initCards();
}}
window.addEventListener('scroll',()=>document.getElementById('st').classList.toggle('v',window.scrollY>400));

function getDeleted(){{try{{return JSON.parse(localStorage.getItem('del_papers')||'[]')}}catch{{return[]}}}}
function getFavs(){{try{{return JSON.parse(localStorage.getItem('fav_papers')||'{{}}')}}catch{{return{{}}}}}}
function getChecked(){{try{{return JSON.parse(localStorage.getItem('chk_papers')||'[]')}}catch{{return[]}}}}
function toggleCheck(btn,pid){{const chks=getChecked();const card=btn.closest('.card');if(chks.includes(pid)){{chks.splice(chks.indexOf(pid),1);btn.classList.remove('on');if(card)card.classList.remove('checked')}}else{{chks.push(pid);btn.classList.add('on');if(card)card.classList.add('checked')}}localStorage.setItem('chk_papers',JSON.stringify(chks))}}
function renum(){{document.querySelectorAll('.card').forEach((c,i)=>{{const ci=c.querySelector('.ci');if(ci)ci.textContent=i+1}})}}
function delPaper(btn,pid){{const dels=getDeleted();if(!dels.includes(pid))dels.push(pid);localStorage.setItem('del_papers',JSON.stringify(dels));const card=btn.closest('.card');if(card){{card.style.transition='all .3s';card.style.opacity='0';card.style.transform='scale(.97)';setTimeout(()=>{{card.remove();renum()}},300)}}}}
function toggleFav(btn,pid,title,link,pdf){{const favs=getFavs();if(favs[pid]){{delete favs[pid];btn.innerHTML='&#9825;';btn.classList.remove('on')}}else{{favs[pid]={{title,link,pdf,t:Date.now()}};btn.innerHTML='&#9829;';btn.classList.add('on')}}localStorage.setItem('fav_papers',JSON.stringify(favs))}}
function initCards(){{const dels=getDeleted();const favs=getFavs();const chks=getChecked();document.querySelectorAll('.card[data-pid]').forEach(c=>{{const pid=c.dataset.pid;if(dels.includes(pid)){{c.remove();return}}const fb=c.querySelector('.fav-btn');if(fb&&favs[pid]){{fb.innerHTML='&#9829;';fb.classList.add('on')}}const cb=c.querySelector('.chk-btn');if(cb&&chks.includes(pid)){{cb.classList.add('on');c.classList.add('checked')}}}});renum()}};
filter();
</script>{CHAT_HTML}</body></html>"""

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

    bg_src = os.path.join(BASE, "bg.png")
    bg_dst = os.path.join(SITE_DIR, "bg.png")
    if os.path.exists(bg_src) and not os.path.exists(bg_dst):
        import shutil
        shutil.copy2(bg_src, bg_dst)

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
</script>{CHAT_HTML}</body></html>"""


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

    cvpr = gen_cvpr_page()
    if cvpr:
        print("Generating cvpr26.html...")
        with open(os.path.join(SITE_DIR, "cvpr26.html"), "w", encoding="utf-8") as f:
            f.write(cvpr)

    dates = get_dates()
    for d in dates:
        print(f"Generating {d}.html...")
        with open(os.path.join(SITE_DIR, f"{d}.html"), "w", encoding="utf-8") as f:
            f.write(gen_daily_page(d))

    print(f"Done! {len(dates)+1} pages generated in site/")


if __name__ == "__main__":
    main()
