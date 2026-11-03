const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const host=u=>{try{return new URL(u).hostname.replace(/^www\./,"")}catch(e){return ""}};
const thumb=s=>{const src=s.image?s.image:(s.image===null?"":"/og-image?u="+encodeURIComponent(s.url||""));if(!src)return "";const cr=s.imageCredit||s.source||host(s.url);
return `<figure class="cimg" style="position:relative;display:block;box-sizing:border-box;width:calc(100% + 40px);max-width:none;margin:-20px -20px 16px;padding:0;aspect-ratio:16/9;overflow:hidden;border-radius:27px 27px 0 0;background:#262626"><img style="display:block;width:100%;height:100%;max-width:100%;object-fit:cover;margin:0;border:0" src="${esc(src)}" alt="${esc(s.imageAlt||s.title)}" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.parentNode.remove()"><figcaption style="position:absolute;right:10px;bottom:8px;max-width:calc(100% - 20px);padding:2px 8px;border-radius:9999px;background:rgba(0,0,0,.6);color:#ffffffcc;font-size:10px;line-height:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">Image: ${esc(cr)}</figcaption></figure>`};
// Full Charge: tag color rule. Tesla blue, EV mint, everything else white.
const tagc=t=>t==="EV"?"var(--mint)":t==="Tesla"?"var(--ac)":"var(--t1)";
const story=(s,i)=>`<article class="card" style="--c:${tagc(s.tag)}">${thumb(s)}<div class="cm"><span>${String(i+1).padStart(2,"0")}</span><span>${esc(s.tag)}</span></div><h3 class="ct">${esc(s.title)}</h3><div class="cb">${esc(s.takeaway)}</div><a class="src" href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.source)} · ${esc(host(s.url))}</a></article>`;
async function render(mode){try{const response=await fetch("/data/digests.json");if(!response.ok)throw new Error("Digest unavailable");const d=(await response.json()).sort((a,b)=>b.date.localeCompare(a.date));if(!d.length)throw new Error("Empty digest");const el=document.getElementById("list");
if(mode==="today"){el.innerHTML='<div class="cards">'+d[0].stories.map(story).join("")+'</div>';const c=document.getElementById("dcount");if(c)c.textContent=d[0].stories.length+" stories for "+d[0].date;if(typeof onToday==="function")onToday(d[0]);
// The digest arrives above signup after the browser's initial hash navigation.
// Re-align only this explicit destination once the async content is in place.
if(location.hash==="#newsletter"){
 const signup=document.getElementById("newsletter"),controller=new AbortController();
 let interrupted=false,resize;
 const stop=()=>{interrupted=true;resize?.disconnect();controller.abort()};
 for(const type of ["wheel","touchstart","pointerdown","keydown","hashchange"])addEventListener(type,stop,{once:true,passive:true,signal:controller.signal});
 const align=()=>{if(!interrupted&&location.hash==="#newsletter")signup?.scrollIntoView({block:"start"})};
 // Lazy images can resolve after the digest itself. Stop following as soon
 // as the visitor interacts, so delayed content cannot override their scroll.
 if("ResizeObserver" in window){resize=new ResizeObserver(()=>requestAnimationFrame(align));resize.observe(el)}
 requestAnimationFrame(align);
}}

else el.innerHTML=d.map(x=>`<p class="eyebrow" style="margin:40px 0 16px">${esc(x.date)}</p><div class="cards">`+x.stories.map(story).join("")+'</div>').join("") }catch(error){const el=document.getElementById("list");el.innerHTML='<p class="lead" role="status">The digest could not be loaded. Please refresh, or <a class="lnk" href="https://x.com/dcostaverage">read @dcostaverage on X</a>.</p>';const q=document.getElementById("q");if(q){q.dataset.state="err";q.innerHTML='<li><a href="https://x.com/dcostaverage"><i>!</i><span>Stories unavailable. Read today’s updates on X.</span></a></li>'}const go=document.getElementById("go");if(go){go.textContent="Read updates on X";go.href="https://x.com/dcostaverage"}}}
