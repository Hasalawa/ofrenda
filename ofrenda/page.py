"""The single-page interface served by `ofrenda serve` (no external assets, works offline)."""

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ofrenda</title>
<style>
:root{--gold:#ffb000;--orange:#e8650f;--pink:#e0357a;--teal:#2bb3c0;--green:#7bc74d;
 --night:#0d0618;--plum:#241239;--plum2:#1a0c2c;--paper:#fff3dc;--muted:#c9b6dd}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%}
body{background:radial-gradient(120% 70% at 50% -5%,#55238a 0%,#24103e 42%,var(--night) 100%) fixed;
 color:var(--paper);font-family:Georgia,"Palatino Linotype",Palatino,serif;overflow-x:hidden}
button,input,select,textarea{font:inherit;color:inherit}
canvas#fx{position:fixed;inset:0;pointer-events:none;z-index:1}
.moon{position:fixed;top:70px;right:8vw;width:90px;height:90px;border-radius:50%;
 background:radial-gradient(circle at 35% 35%,#fffbe8,#f2dfa5 60%,#d8bf7a);
 box-shadow:0 0 60px 20px #ffe9a533,0 0 160px 60px #ffe9a51a;opacity:.9;z-index:0}

/* papel picado */
.papel{display:flex;overflow:hidden;height:66px;position:relative;z-index:2}
.flag{flex:0 0 74px;height:60px;transform-origin:50% 0;animation:sway 4s ease-in-out infinite alternate;
 clip-path:polygon(0 0,100% 0,100% 82%,87% 100%,75% 82%,62% 100%,50% 82%,38% 100%,25% 82%,13% 100%,0 82%);
 -webkit-mask:radial-gradient(circle at 50% 38%,transparent 0 6px,#000 7px),radial-gradient(circle at 20% 70%,transparent 0 3px,#000 4px);
 -webkit-mask-composite:source-in;mask:radial-gradient(circle at 50% 38%,transparent 0 6px,#000 7px),radial-gradient(circle at 20% 70%,transparent 0 3px,#000 4px);
 mask-composite:intersect}
@keyframes sway{from{transform:rotate(-2.5deg)}to{transform:rotate(2.5deg)}}

header{text-align:center;padding:1.2rem 1rem .4rem;position:relative;z-index:2}
h1{margin:0;font-size:clamp(2.4rem,7vw,4rem);letter-spacing:.08em;color:var(--gold);font-weight:normal;
 text-shadow:0 0 18px #ffb00088,0 0 50px #e8650f66}
.tag{color:var(--muted);font-style:italic;margin-top:.2rem}
.status{display:inline-flex;gap:.5rem;align-items:center;margin-top:.8rem;font-size:.82rem;color:var(--muted);
 border:1px solid #ffffff22;border-radius:999px;padding:.25rem .8rem;background:#0004}
.dot{width:8px;height:8px;border-radius:50%;background:#777}
.dot.on{background:var(--green);box-shadow:0 0 8px var(--green)}
.dot.off{background:var(--orange)}

/* altar */
main{position:relative;z-index:2;max-width:1060px;margin:0 auto;padding:1rem 1rem 5rem}
.altar{display:flex;flex-direction:column;align-items:center;gap:0}
.shelf{width:100%;display:flex;justify-content:center;gap:1.4rem;padding:1.2rem 1rem 0;position:relative;
 flex-wrap:wrap}
.board{width:100%;height:46px;border-radius:6px 6px 0 0;position:relative;
 background:linear-gradient(180deg,#f08a1c 0 55%,#d0560c 55% 100%);box-shadow:0 8px 24px #0008}
.board::before{content:"";position:absolute;left:0;right:0;top:-13px;height:26px;
 background:radial-gradient(circle at 14px 13px,#ffe27a 0 3px,#ffb000 4px 8px,#e8650f 9px 12px,transparent 13px) repeat-x;
 background-size:28px 26px;filter:drop-shadow(0 2px 3px #0006)}
.board::after{content:"";position:absolute;left:0;right:0;bottom:-14px;height:16px;
 background:linear-gradient(90deg,var(--pink) 0 25%,var(--teal) 25% 50%,var(--green) 50% 75%,var(--gold) 75%);
 background-size:120px 100%;clip-path:polygon(0 0,100% 0,100% 30%,96% 100%,92% 30%,88% 100%,84% 30%,80% 100%,
 76% 30%,72% 100%,68% 30%,64% 100%,60% 30%,56% 100%,52% 30%,48% 100%,44% 30%,40% 100%,36% 30%,32% 100%,
 28% 30%,24% 100%,20% 30%,16% 100%,12% 30%,8% 100%,4% 30%,0 100%)}
.shrine{position:relative;display:flex;align-items:flex-end;gap:.5rem;padding-bottom:.2rem}
.shrine::before{content:"";position:absolute;inset:-30px -40px 0;border-radius:50%;pointer-events:none;
 background:radial-gradient(ellipse at 50% 60%,#ffb00033,transparent 65%)}
.portrait{position:relative;background:none;border:0;padding:0;cursor:pointer;text-align:center;
 transition:transform .25s}
.portrait:hover,.portrait:focus-visible{transform:translateY(-6px) scale(1.04);outline:none}
.frame{width:150px;height:186px;border-radius:10px;padding:8px;position:relative;
 background:linear-gradient(135deg,#ffd45a,#c97a0a 55%,#ffd45a);box-shadow:0 10px 30px #000a,0 0 30px #ffb00055}
.frame .in{width:100%;height:100%;border-radius:4px;overflow:hidden;background:linear-gradient(#3b1d5c,#1d0d33);
 display:grid;place-items:center}
.frame img{width:100%;height:100%;object-fit:cover;filter:sepia(.25) contrast(1.05)}
.sil{font-size:3.4rem;filter:drop-shadow(0 0 12px #ffb000)}
.plate{margin:.5rem auto 0;max-width:170px;background:#150a24cc;border:1px solid #ffb00066;border-radius:8px;padding:.3rem .5rem}
.plate b{display:block;font-weight:normal;color:var(--gold);font-size:1.05rem;line-height:1.2}
.plate small{color:var(--muted)}
.candle{position:relative;width:15px;height:62px;border-radius:3px 3px 2px 2px;margin-bottom:0;
 background:linear-gradient(90deg,#e6d6b4,#fff8e6 50%,#d6c5a0);box-shadow:0 0 18px #ffb00055}
.candle:nth-child(3){height:48px}
.flame{position:absolute;left:50%;bottom:100%;width:13px;height:24px;margin-left:-6.5px;transform-origin:50% 100%;
 border-radius:50% 50% 50% 50%/62% 62% 38% 38%;
 background:radial-gradient(ellipse at 50% 72%,#fff 8%,#ffe27a 38%,#ff9d1c 72%,transparent 100%);
 filter:drop-shadow(0 0 8px #ffb000) drop-shadow(0 0 20px #ff7a00);animation:flick 1.1s ease-in-out infinite alternate}
.candle:nth-child(3) .flame{animation-duration:1.5s;animation-delay:-.4s}
@keyframes flick{0%{transform:scale(1,1) rotate(-3deg)}35%{transform:scale(.92,1.08) rotate(2deg)}
 70%{transform:scale(1.06,.94) rotate(-1deg)}100%{transform:scale(.97,1.05) rotate(3deg)}}
.offer{display:flex;justify-content:center;gap:.25rem;font-size:1.15rem;min-height:1.6rem;margin-top:.3rem}
.add .frame{background:none;border:2px dashed #ffb00088;box-shadow:none;display:grid;place-items:center}
.add .in{background:none}
.add .sil{font-size:2.6rem;opacity:.85}
.add:hover .frame{border-color:var(--gold);box-shadow:0 0 30px #ffb00055}
.empty{max-width:520px;margin:1rem auto 2rem;text-align:center;color:var(--muted);line-height:1.6}

/* drawer */
.scrim{position:fixed;inset:0;background:#0009;opacity:0;pointer-events:none;transition:opacity .3s;z-index:20}
.scrim.open{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;right:0;bottom:0;width:min(540px,100vw);z-index:21;display:flex;flex-direction:column;
 background:linear-gradient(180deg,#2d1648,#170a29);border-left:1px solid #ffb00055;
 transform:translateX(102%);transition:transform .35s cubic-bezier(.2,.8,.2,1);box-shadow:-20px 0 60px #000a}
.drawer.open{transform:none}
.dhead{display:flex;gap:1rem;align-items:center;padding:1rem 1.2rem;border-bottom:1px solid #ffffff1a;position:relative}
.avatar{width:68px;height:68px;border-radius:50%;border:3px solid var(--gold);overflow:hidden;flex:none;
 display:grid;place-items:center;background:#1d0d33;box-shadow:0 0 20px #ffb00066}
.avatar img{width:100%;height:100%;object-fit:cover}
.dhead h2{margin:0;font-weight:normal;color:var(--gold);font-size:1.5rem;line-height:1.15}
.dhead .meta{color:var(--muted);font-size:.92rem}
.x{margin-left:auto;background:none;border:1px solid #ffffff33;border-radius:50%;width:36px;height:36px;cursor:pointer}
.x:hover{background:#ffffff1a}
.tabs{display:flex;border-bottom:1px solid #ffffff1a}
.tab{flex:1;background:none;border:0;padding:.7rem .3rem;cursor:pointer;color:var(--muted);border-bottom:3px solid transparent}
.tab[aria-selected=true]{color:var(--gold);border-color:var(--gold)}
.dbody{flex:1;overflow-y:auto;padding:1rem 1.2rem}
.note{font-size:.82rem;color:var(--muted);text-align:center;margin:.2rem 0 1rem}

/* chat */
.msg{display:flex;gap:.6rem;margin:.7rem 0;align-items:flex-end}
.msg.me{flex-direction:row-reverse}
.orb{width:30px;height:30px;border-radius:50%;flex:none;background:radial-gradient(circle at 50% 60%,#fff 6%,#ffd45a 35%,#ff8a1c 75%);
 box-shadow:0 0 14px #ffb000;animation:flick 1.3s ease-in-out infinite alternate}
.bubble{max-width:82%;padding:.65rem .9rem;border-radius:16px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word}
.ai .bubble{background:#3a1d5a;border:1px solid #ffb00044;border-bottom-left-radius:4px}
.me .bubble{background:linear-gradient(135deg,#ffc233,#f08a1c);color:#2a1100;border-bottom-right-radius:4px}
.say{background:none;border:0;cursor:pointer;opacity:.7;font-size:1rem;padding:.2rem}
.say:hover{opacity:1}
.dots span{display:inline-block;width:7px;height:7px;margin:0 2px;border-radius:50%;background:var(--gold);animation:bob 1s infinite}
.dots span:nth-child(2){animation-delay:.15s}.dots span:nth-child(3){animation-delay:.3s}
@keyframes bob{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1}}
.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0}
.chip{background:#ffb00018;border:1px solid #ffb00077;border-radius:999px;padding:.25rem .8rem;font-size:.92rem;color:var(--paper)}
button.chip{cursor:pointer}button.chip:hover{background:#ffb00044}
.composer{display:flex;gap:.5rem;padding:.8rem 1.2rem 1rem;border-top:1px solid #ffffff1a;background:#12081f}
.composer input{flex:1;background:#2a1445;border:1px solid #ffffff33;border-radius:999px;padding:.65rem 1rem;outline:none}
.composer input:focus,.field:focus{border-color:var(--gold)}
.btn{background:linear-gradient(135deg,#ffc233,#f08a1c);color:#2a1100;border:0;border-radius:999px;padding:.6rem 1.2rem;
 cursor:pointer;font-weight:bold}
.btn:hover{filter:brightness(1.1)}.btn:disabled{opacity:.5;cursor:wait}
.btn.ghost{background:none;color:var(--gold);border:1px solid var(--gold)}
.toggle{display:flex;align-items:center;gap:.4rem;font-size:.85rem;color:var(--muted);cursor:pointer}

/* stories / offerings */
.quote{border-left:4px solid var(--orange);background:#ffffff0d;border-radius:0 12px 12px 0;padding:.8rem 1rem;
 font-size:1.05rem;line-height:1.6;margin:0 0 .6rem;font-style:italic}
.story{background:#ffffff0d;border-radius:12px;padding:.8rem 1rem;margin:.7rem 0}
.story h4{margin:0 0 .3rem;color:var(--gold);font-weight:normal;font-size:1.05rem}
.story p{margin:0;line-height:1.55;white-space:pre-wrap}.story small{color:var(--muted)}
.field{width:100%;background:#2a1445;border:1px solid #ffffff33;border-radius:10px;padding:.6rem .8rem;margin:.3rem 0;outline:none}
textarea.field{min-height:90px;resize:vertical}
.form{border:1px dashed #ffffff33;border-radius:12px;padding:.8rem;margin-top:1rem}
.form h4{margin:0 0 .3rem;font-weight:normal;color:var(--muted)}
.row{display:flex;gap:.5rem}.row .field{margin:.3rem 0}
h3{color:var(--gold);font-weight:normal;margin:1.2rem 0 .3rem}
.big{width:100%;padding:.9rem;font-size:1.1rem;margin:.6rem 0}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(120px);background:#3a1030;border:1px solid var(--pink);
 padding:.7rem 1.2rem;border-radius:12px;z-index:50;transition:transform .3s}
.toast.show{transform:translateX(-50%)}
dialog{background:linear-gradient(180deg,#2d1648,#170a29);color:var(--paper);border:1px solid var(--gold);border-radius:18px;
 padding:1.4rem;width:min(440px,92vw);box-shadow:0 0 60px #000}
dialog::backdrop{background:#000a}
dialog h3{margin-top:0}
.preview{width:90px;height:110px;border-radius:8px;object-fit:cover;border:3px solid var(--gold);display:none;margin:.4rem 0}
footer{text-align:center;color:var(--muted);font-size:.85rem;padding:1rem 1rem 2.5rem;position:relative;z-index:2}
@media (max-width:560px){.frame{width:128px;height:160px}.moon{display:none}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head>
<body>
<canvas id="fx"></canvas><div class="moon"></div>
<div class="papel" id="papel" aria-hidden="true"></div>
<header>
 <h1>Ofrenda</h1>
 <div class="tag">Those we remember never really leave.</div>
 <div class="status"><span class="dot" id="dot"></span><span id="status">checking the AI…</span></div>
</header>
<main><div class="altar" id="altar"></div></main>
<footer>Private by design: your stories and the AI stay on this computer.</footer>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" aria-hidden="true"></aside>
<dialog id="addDlg">
 <form method="dialog" id="addForm">
  <h3>Add someone to the ofrenda</h3>
  <input class="field" id="fName" placeholder="Name" required maxlength="80" autocomplete="off">
  <div class="row">
   <input class="field" id="fYears" placeholder="Years (1940 - 2020)" maxlength="40">
   <input class="field" id="fRel" list="rels" placeholder="Who were they to you?" maxlength="40">
  </div>
  <datalist id="rels"><option>grandmother<option>grandfather<option>mother<option>father<option>aunt<option>uncle
   <option>sister<option>brother<option>friend<option>pet</datalist>
  <label class="note" style="display:block;text-align:left">A photo (optional, stays on this computer)</label>
  <input type="file" id="fPhoto" accept="image/*" class="field">
  <img class="preview" id="fPrev" alt="">
  <div class="row" style="justify-content:flex-end;margin-top:.6rem">
   <button class="btn ghost" type="button" id="addCancel">Cancel</button>
   <button class="btn" type="submit" id="addGo">Light the first candle</button>
  </div>
 </form>
</dialog>
<div class="toast" id="toast"></div>

<script>
"use strict";
const $=s=>document.querySelector(s);
function h(tag,props={},...kids){const e=document.createElement(tag);
 for(const [k,v] of Object.entries(props)){
  if(k==="class")e.className=v;else if(k.startsWith("on"))e.addEventListener(k.slice(2),v);
  else if(k==="style")e.style.cssText=v;else if(v!==false&&v!=null)e.setAttribute(k,v===true?"":v)}
 for(const kid of kids.flat()){if(kid==null||kid===false)continue;e.append(kid.nodeType?kid:document.createTextNode(kid))}
 return e}
let people=[],current=null,tab="talk",voiceOn=false,busy=false;
const chats={};   // slug -> [{who,text}]

async function api(path,body){
 const r=await fetch(path,body?{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}:undefined);
 if(!r.ok){let m="Something went wrong";try{m=(await r.json()).error||m}catch(e){}throw new Error(m)}
 return r}
async function refresh(){people=await (await api("/api/people")).json()}
function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.add("show");clearTimeout(toast.t);toast.t=setTimeout(()=>t.classList.remove("show"),3500)}
function first(p){return p.name.split(/[ (]/)[0]}
function speak(text){if(!("speechSynthesis" in window))return toast("This browser has no voice");
 speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang="en-US";u.rate=.95;speechSynthesis.speak(u)}

/* ---------- decoration ---------- */
(function papel(){const c=["#e0357a","#ffb000","#2bb3c0","#7bc74d","#e8650f","#9b5de5"];const w=$("#papel");
 for(let i=0;i<Math.ceil(innerWidth/74)+1;i++){w.append(h("div",{class:"flag",style:`background:${c[i%c.length]};animation-delay:${(i%5)*-.7}s`}))}})();
(function fx(){const cv=$("#fx"),cx=cv.getContext("2d");let W,H;const size=()=>{W=cv.width=innerWidth;H=cv.height=innerHeight};
 size();addEventListener("resize",size);if(matchMedia("(prefers-reduced-motion:reduce)").matches)return;
 const cols=["#ffb000","#e8650f","#ffd34d"];
 const petal=(init)=>({x:Math.random()*W,y:init?Math.random()*H:-20,r:4+Math.random()*5,vx:-.2+Math.random()*.6,vy:.25+Math.random()*.6,
  a:Math.random()*6.28,va:(Math.random()-.5)*.05,c:cols[Math.random()*3|0]});
 const ember=(init)=>({x:Math.random()*W,y:init?Math.random()*H:H+10,r:.8+Math.random()*1.8,vy:-.2-Math.random()*.5,ph:Math.random()*6.28});
 const P=Array.from({length:26},()=>petal(true)),E=Array.from({length:40},()=>ember(true));
 (function tick(t){cx.clearRect(0,0,W,H);
  for(const p of P){p.x+=p.vx+Math.sin(t/900+p.a)*.4;p.y+=p.vy;p.a+=p.va;
   if(p.y>H+20)Object.assign(p,petal(false));
   cx.save();cx.translate(p.x,p.y);cx.rotate(p.a);cx.fillStyle=p.c;cx.globalAlpha=.8;
   cx.beginPath();cx.ellipse(0,0,p.r,p.r*.55,0,0,6.28);cx.fill();cx.restore()}
  for(const e of E){e.y+=e.vy;e.x+=Math.sin(t/700+e.ph)*.3;if(e.y<-10)Object.assign(e,ember(false));
   cx.globalAlpha=.35+.35*Math.sin(t/400+e.ph);cx.fillStyle="#ffd27a";cx.shadowColor="#ffb000";cx.shadowBlur=8;
   cx.beginPath();cx.arc(e.x,e.y,e.r,0,6.28);cx.fill();cx.shadowBlur=0}
  cx.globalAlpha=1;requestAnimationFrame(tick)})(0)})();

/* ---------- altar ---------- */
function candle(){return h("div",{class:"candle"},h("i",{class:"flame"}))}
function frame(p,extra){return h("div",{class:"frame"},h("div",{class:"in"},
 p&&p.photo_url?h("img",{src:p.photo_url,alt:p.name}):h("span",{class:"sil"},extra||"\u{1F33C}")))}
function offerings(p){const f=p.favorites||{};const icons=[];
 (f.foods||[]).slice(0,2).forEach(()=>icons.push("\u{1F372}"));(f.songs||[]).slice(0,1).forEach(()=>icons.push("\u{1F3B5}"));
 (f.flowers||[]).slice(0,2).forEach(()=>icons.push("\u{1F33C}"));
 for(let i=0;i<Math.min(p.candles||0,3);i++)icons.push("\u{1F56F}️");
 return h("div",{class:"offer"},icons.join(" "))}
function shrine(p){return h("div",{class:"shrine"},candle(),
 h("button",{class:"portrait",onclick:()=>openDrawer(p.slug),"aria-label":"Open "+p.name},frame(p),
  h("div",{class:"plate"},h("b",{},p.name),h("small",{},[p.years,p.relation].filter(Boolean).join(" · ")||" ")),offerings(p)),
 candle())}
function addShrine(){return h("div",{class:"shrine add"},
 h("button",{class:"portrait",onclick:()=>$("#addDlg").showModal(),"aria-label":"Add someone"},frame(null,"+"),
  h("div",{class:"plate"},h("b",{},"Add someone"),h("small",{},"to remember")),h("div",{class:"offer"}," ")))}
function renderAltar(){const a=$("#altar");a.replaceChildren();
 const items=people.map(shrine);items.push(addShrine());
 if(!people.length)a.append(h("p",{class:"empty"},"The altar is waiting. Add someone you miss, write down the stories you never want to lose, and then talk about them with a private AI that only knows what you tell it."));
 const caps=[2,3,4];let i=0,row=0;
 while(i<items.length){const cap=caps[Math.min(row,caps.length-1)];const group=items.slice(i,i+cap);i+=cap;row++;
  const maxw=Math.min(100,40+cap*17);
  a.append(h("div",{class:"shelf",style:`max-width:${maxw}%`},group),h("div",{class:"board",style:`max-width:${maxw}%`}))}}

/* ---------- drawer ---------- */
const person=()=>people.find(p=>p.slug===current);
function openDrawer(slug,t){current=slug;tab=t||"talk";renderDrawer();
 $("#drawer").classList.add("open");$("#scrim").classList.add("open");$("#drawer").setAttribute("aria-hidden","false")}
function closeDrawer(){$("#drawer").classList.remove("open");$("#scrim").classList.remove("open");speechSynthesis&&speechSynthesis.cancel()}
$("#scrim").onclick=closeDrawer;addEventListener("keydown",e=>{if(e.key==="Escape")closeDrawer()});

function renderDrawer(){const p=person();if(!p)return;const d=$("#drawer");d.replaceChildren(
 h("div",{class:"dhead"},h("div",{class:"avatar"},p.photo_url?h("img",{src:p.photo_url,alt:""}):h("span",{class:"sil",style:"font-size:2rem"},"\u{1F33C}")),
  h("div",{},h("h2",{},p.name),h("div",{class:"meta"},[p.years,p.relation].filter(Boolean).join(" · "))),
  h("button",{class:"x",onclick:closeDrawer,"aria-label":"Close"},"✕")),
 h("div",{class:"tabs",role:"tablist"},...[["talk","\u{1F4AC} Talk"],["stories","\u{1F4D6} Stories"],["gifts","\u{1F33C} Offerings"]].map(([k,l])=>
  h("button",{class:"tab",role:"tab","aria-selected":String(tab===k),onclick:()=>{tab=k;renderDrawer()}},l))),
 h("div",{class:"dbody",id:"dbody"}),
 tab==="talk"?composer(p):null);
 ({talk:renderTalk,stories:renderStories,gifts:renderGifts})[tab](p)}

/* talk */
function renderTalk(p){const b=$("#dbody");const log=chats[p.slug]||(chats[p.slug]=[]);
 b.append(h("div",{class:"note"},`${first(p)}'s AI companion only knows the stories you wrote. It talks about ${first(p)}, never as them.`));
 const msgs=h("div",{id:"msgs"});b.append(msgs);
 if(!log.length){addMsg(msgs,"ai",`Hello. Ask me anything about ${first(p)}. I only know what you have written down, so the more stories you add, the more I can remember with you.`,false);
  const chips=h("div",{class:"chips"},...[`Tell me about ${first(p)}`,"What did they love?","Tell me a story","What made them laugh?"].map(q=>h("button",{class:"chip",onclick:()=>send(q)},q)));
  b.append(chips)}
 else log.forEach(m=>addMsg(msgs,m.who,m.text,m.who==="ai"));
 b.scrollTop=b.scrollHeight}
function composer(p){const inp=h("input",{id:"q",placeholder:`Ask about ${first(p)}…`,autocomplete:"off",maxlength:"500"});
 inp.addEventListener("keydown",e=>{if(e.key==="Enter"&&inp.value.trim()){send(inp.value.trim());inp.value=""}});
 return h("div",{class:"composer"},
  h("label",{class:"toggle",title:"Read answers aloud"},h("input",{type:"checkbox",checked:voiceOn,onchange:e=>{voiceOn=e.target.checked;if(!voiceOn)speechSynthesis.cancel()}}),"\u{1F50A}"),
  inp,h("button",{class:"btn",id:"sendBtn",onclick:()=>{if(inp.value.trim()){send(inp.value.trim());inp.value=""}}},"Ask"))}
function addMsg(box,who,text,canSpeak){const bub=h("div",{class:"bubble"},text);
 const row=h("div",{class:"msg "+who},who==="ai"?h("div",{class:"orb"}):null,bub,
  canSpeak&&who==="ai"?h("button",{class:"say",title:"Listen",onclick:()=>speak(bub.textContent)},"\u{1F50A}"):null);
 box.append(row);return {row,bub}}
async function send(text){if(busy)return;const p=person();const log=chats[p.slug]||(chats[p.slug]=[]);
 const b=$("#dbody");b.querySelector(".chips")?.remove();const box=$("#msgs");
 log.push({who:"me",text});addMsg(box,"me",text);
 const {row,bub}=addMsg(box,"ai","",false);bub.replaceChildren(h("span",{class:"dots"},h("span"),h("span"),h("span")));
 b.scrollTop=b.scrollHeight;busy=true;$("#sendBtn")&&($("#sendBtn").disabled=true);let full="";
 try{const r=await api("/api/ask",{slug:p.slug,question:text});const rd=r.body.getReader(),dec=new TextDecoder();
  for(;;){const {done,value}=await rd.read();if(done)break;full+=dec.decode(value,{stream:true});bub.textContent=full;b.scrollTop=b.scrollHeight}
 }catch(e){full="I could not answer just now. "+e.message;bub.textContent=full}
 finally{busy=false;$("#sendBtn")&&($("#sendBtn").disabled=false)}
 log.push({who:"ai",text:full});
 row.append(h("button",{class:"say",title:"Listen",onclick:()=>speak(full)},"\u{1F50A}"));
 if(voiceOn)speak(full)}

/* stories */
function renderStories(p){const b=$("#dbody");
 if(p.remembrance)b.append(h("blockquote",{class:"quote"},p.remembrance));
 const rb=h("button",{class:"btn ghost",style:"width:100%",onclick:async()=>{
  if(!(p.stories||[]).length&&!(p.favorites.foods.length+p.favorites.songs.length+p.favorites.flowers.length))return toast("Add a story or an offering first");
  rb.disabled=true;rb.textContent="✨ Gathering the words…";
  try{const r=await (await api("/api/remember",{slug:p.slug})).json();p.remembrance=r.text;renderDrawer()}
  catch(e){toast(e.message);rb.disabled=false;rb.textContent="✨ Write a remembrance"}}},p.remembrance?"✨ Write it again":"✨ Write a remembrance");
 b.append(rb);
 (p.stories||[]).slice().reverse().forEach(s=>b.append(h("div",{class:"story"},h("h4",{},s.title),h("p",{},s.text),h("small",{},s.added))));
 if(!(p.stories||[]).length)b.append(h("p",{class:"note"},"No stories yet. Write the first one below."));
 const t=h("input",{class:"field",placeholder:"Title (optional)",maxlength:"120"}),x=h("textarea",{class:"field",placeholder:`A memory of ${first(p)}… (English works best)`,maxlength:"5000"});
 b.append(h("div",{class:"form"},h("h4",{},"Add a story"),t,x,h("button",{class:"btn",onclick:async e=>{
  if(!x.value.trim())return toast("Write a few words first");e.target.disabled=true;
  try{const r=await (await api("/api/story",{slug:p.slug,title:t.value,text:x.value})).json();upd(r);renderDrawer()}catch(er){toast(er.message);e.target.disabled=false}}},"Keep this memory")))}

/* offerings */
function renderGifts(p){const b=$("#dbody");const f=p.favorites;
 const sec=(label,icon,arr)=>{b.append(h("h3",{},label));b.append(arr.length?h("div",{class:"chips"},arr.map(v=>h("span",{class:"chip"},icon+" "+v))):h("div",{class:"note",style:"text-align:left"},"Nothing yet"))};
 sec("Foods they loved","\u{1F372}",f.foods);sec("Songs","\u{1F3B5}",f.songs);sec("Flowers","\u{1F33C}",f.flowers);
 const kind=h("select",{class:"field",style:"max-width:130px"},h("option",{value:"food"},"Food"),h("option",{value:"song"},"Song"),h("option",{value:"flower"},"Flower"));
 const val=h("input",{class:"field",placeholder:"e.g. pan de muerto",maxlength:"80"});
 b.append(h("div",{class:"form"},h("h4",{},"Place an offering"),h("div",{class:"row"},kind,val),h("button",{class:"btn",onclick:async e=>{
  if(!val.value.trim())return;e.target.disabled=true;
  try{const r=await (await api("/api/fav",{slug:p.slug,kind:kind.value,value:val.value})).json();upd(r);renderDrawer()}catch(er){toast(er.message);e.target.disabled=false}}},"Add to the altar")));
 b.append(h("button",{class:"btn big",onclick:async()=>{try{const r=await (await api("/api/candle",{slug:p.slug})).json();upd(r);renderDrawer();toast(`A candle is lit for ${first(p)}. (${r.candles} so far)`)}catch(er){toast(er.message)}}},
  `\u{1F56F}️ Light a candle${p.candles?` (${p.candles} lit)`:""}`))}
function upd(np){const i=people.findIndex(p=>p.slug===np.slug);if(i>=0)people[i]=np;else people.push(np);renderAltar()}

/* add person dialog */
function readPhoto(file){return new Promise((res,rej)=>{const img=new Image(),url=URL.createObjectURL(file);
 img.onload=()=>{const m=520,s=Math.min(1,m/Math.max(img.width,img.height)),c=document.createElement("canvas");
  c.width=Math.round(img.width*s);c.height=Math.round(img.height*s);c.getContext("2d").drawImage(img,0,0,c.width,c.height);
  URL.revokeObjectURL(url);res(c.toDataURL("image/jpeg",.85))};img.onerror=()=>rej(new Error("Could not read that image"));img.src=url})}
let photoData="";
$("#fPhoto").onchange=async e=>{const f=e.target.files[0];photoData="";$("#fPrev").style.display="none";if(!f)return;
 try{photoData=await readPhoto(f);$("#fPrev").src=photoData;$("#fPrev").style.display="block"}catch(er){toast(er.message)}};
$("#addCancel").onclick=()=>$("#addDlg").close();
$("#addForm").onsubmit=async e=>{e.preventDefault();const go=$("#addGo");go.disabled=true;
 try{const r=await (await api("/api/person",{name:$("#fName").value,years:$("#fYears").value,relation:$("#fRel").value,photo:photoData})).json();
  upd(r);$("#addDlg").close();$("#addForm").reset();photoData="";$("#fPrev").style.display="none";openDrawer(r.slug,"stories")}
 catch(er){toast(er.message)}finally{go.disabled=false}};

(async()=>{try{await refresh();renderAltar()}catch(e){toast(e.message)}
 try{const i=await (await api("/api/info")).json();$("#dot").className="dot "+(i.ai?"on":"off");
  $("#status").textContent=i.ai?`Local AI ready · ${i.model}`:"AI not running: answers will use simple templates"}
 catch(e){$("#status").textContent="offline"}})();
</script></body></html>
"""
