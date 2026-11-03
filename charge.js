// Full Charge home page (Oct 21 2026). Two jobs, no account, nothing sent anywhere:
// 1) The pack: one cell per story in today's digest. A cell fills once that story's card has been on screen
//    (60% visible) for 2 seconds, one cell at a time, or its source link is opened. Progress lives in localStorage for today's
//    date only, so a new digest always starts at 0%. A first visit always shows 0% and "Start charging".
// 2) The EV vs gas teaser: same defaults and formula as /calculator (first EV and first gas car in vehicles.js,
//    1,000 mi a month, US average prices from data/rates.json), so the home number can never drift from it.
(function(){
const KEY="dd-charge",$=id=>document.getElementById(id),DWELL=2000;
const load=date=>{try{const v=JSON.parse(localStorage.getItem(KEY)||"null");return v&&v.date===date&&Array.isArray(v.read)?v.read:[]}catch(e){return[]}};
const save=(date,read)=>{try{localStorage.setItem(KEY,JSON.stringify({date,read}))}catch(e){}};
const pad=i=>String(i+1).padStart(2,"0");
const nice=d=>new Date(d+"T12:00:00").toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"});
window.onToday=function(day){
 const S=day.stories,N=S.length,read=new Set(load(day.date).filter(i=>Number.isInteger(i)&&i>=0&&i<N));
 const cards=[...document.querySelectorAll("#list .card")];cards.forEach((c,i)=>c.id="s"+(i+1));
 $("dl").textContent=nice(day.date);
 const words=S.reduce((a,s)=>a+((s.title||"")+" "+(s.takeaway||"")).split(/\s+/).filter(Boolean).length,0);
 const secs=Math.max(10,Math.round(words/230*60/5)*5);$("rt").textContent=N+" stories, about "+secs+" seconds.";
 $("cells").style.setProperty("--n",N);
 $("q").dataset.state="ready";
 const draw=(changed=-1)=>{const focused=document.activeElement,focusIndex=focused&&focused.closest("#cells")?focused.dataset.i:null;const n=read.size,next=[...Array(N).keys()].find(i=>!read.has(i));
  if(!$("cells").querySelector("[data-i]")){
   $("cells").innerHTML=S.map((s,i)=>`<button type="button" class="cell" style="--c:${tagc(s.tag)}" data-i="${i}"><span>${esc(s.tag)}</span></button>`).join("");
  }
  [...$("cells").children].forEach((cell,i)=>{
   cell.classList.toggle("on",read.has(i));
   cell.classList.toggle("nx",i===next&&n>0);
   cell.setAttribute("aria-pressed",String(read.has(i)));
   cell.setAttribute("aria-label",`Story ${pad(i)}, ${S[i].tag}${read.has(i)?", read":""}. Jump to it.`);
   if(i===changed&&!matchMedia("(prefers-reduced-motion: reduce)").matches){
    cell.classList.add("charging");
    cell.addEventListener("animationend",()=>cell.classList.remove("charging"),{once:true});
   }
  });
  $("q").innerHTML=S.map((s,i)=>`<li class="${read.has(i)?"done":i===next?"next":""}" style="--c:${tagc(s.tag)}"><a href="#s${i+1}"><i>${read.has(i)?"\u2713":pad(i)}</i><span>${esc(s.title)}</span></a></li>`).join("");
  const pct=N?Math.round(n/N*100):0;$("pct").innerHTML=pct+"<small>%</small>";$("pack").classList.toggle("full",n===N);
  $("left").textContent=n===N?"All caught up":(N-n)+(N-n===1?" story":" stories");
  const go=$("go");if(n===0){go.textContent="Start charging";go.href="#s1"}else if(n<N){go.textContent="Keep charging";go.href="#s"+(next+1)}else{go.textContent="Read the archive";go.href="/archive"}
  const r=$("resume");if(n>0&&n<N){r.hidden=false;r.innerHTML="Closed the tab? We kept your place. <b>Next up: story "+pad(next)+".</b>"}else if(n===N){r.hidden=false;r.innerHTML="<b>Charged.</b> Same time tomorrow."}else r.hidden=true;
  cards.forEach((c,i)=>c.classList.toggle("read",read.has(i)));
  document.querySelectorAll("#cells .cell").forEach(c=>c.onclick=()=>{const t=$("s"+(+c.dataset.i+1));if(t)t.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"center"})});if(focusIndex!==null){const cell=$("cells").querySelector(`[data-i="${focusIndex}"]`);if(cell)cell.focus({preventScroll:true})}};
 const mark=i=>{if(read.has(i))return;read.add(i);save(day.date,[...read]);draw(i)};
 draw();
 cards.forEach((c,i)=>{const a=c.querySelector("a.src");if(a)a.addEventListener("click",()=>mark(i))});
 // One cell at a time: every 2 seconds, the first unread card that is at least 60% on screen fills.
 // Three cards side by side on desktop take 6 seconds, not 2, so the battery tracks reading, not scrolling.
 if("IntersectionObserver" in window){const vis=new Set();let tm=null;
  const tick=()=>{tm=null;const i=[...vis].filter(i=>!read.has(i)).sort((a,b)=>a-b)[0];if(i===undefined)return;mark(i);vis.delete(i);arm()};
  const arm=()=>{if(!tm&&[...vis].some(i=>!read.has(i)))tm=setTimeout(tick,DWELL)};
  const io=new IntersectionObserver(es=>{es.forEach(e=>{const i=cards.indexOf(e.target);if(e.isIntersecting&&e.intersectionRatio>=.6)vis.add(i);else vis.delete(i)});
   if(![...vis].some(i=>!read.has(i))){clearTimeout(tm);tm=null}else arm()},{threshold:[0,.6]});
  cards.forEach((c,i)=>{if(!read.has(i))io.observe(c)})}
};
// If the digest fails to load, say so where people are looking.
addEventListener("unhandledrejection",()=>{const q=$("q");if(q&&q.dataset.state==="loading"){q.dataset.state="err";q.innerHTML='<li><a href="https://x.com/dcostaverage"><i>!</i><span>Today\'s stories didn\'t load. Refresh, or read them on X at @dcostaverage.</span></a></li>'}});
// EV vs gas teaser, same math as /calculator.
(function(){if(typeof EV==="undefined"||!$("cx"))return;const e=EV[0],g=GAS[0],mi=1000,c2=x=>"$"+x.toFixed(2),f=x=>"$"+Math.round(x).toLocaleString();
 fetch("/data/rates.json").then(r=>r.json()).then(R=>{const kwh=R.us_cents/100,gal=R.us_gas,ev=mi*e[1]/100*kwh,gas=g[1]?mi/g[1]*gal:0,s=gas-ev;
  const wk=new Date(R.gas_week+"T12:00:00").toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"});
  $("cx-g").textContent=c2(gas);$("cx-e").textContent=c2(ev);
  $("cx-gn").textContent="Gas \u00b7 "+g[0].replace(/^2026 /,"");$("cx-en").textContent="EV \u00b7 "+e[0].replace(/^2026 /,"");
  const w=gas>0?Math.min(100,ev/gas*100):100;$("cx-ei").style.width=w.toFixed(1)+"%";$("cx-gap").style.left=w.toFixed(1)+"%";
  $("cx-s").textContent=s>=0?f(s):"-"+f(-s);$("cx").classList.toggle("negative",s<0);$("cx-y").textContent=s>=0?"about "+f(s*12)+" a year":"gas wins at these prices";
  $("cx-f").innerHTML=`${mi.toLocaleString()} mi \u00f7 ${g[1]} MPG \u00d7 $${gal.toFixed(3)}/gal = ${c2(gas)}. ${mi.toLocaleString()} mi \u00d7 ${e[1]} kWh/100 mi \u00d7 $${kwh.toFixed(4)}/kWh = ${c2(ev)}. EPA ratings from <a href="https://www.fueleconomy.gov">fueleconomy.gov</a>. EIA prices: US average regular gas, week of ${wk}; US average home electricity, ${R.elec_month}. Same defaults and formula as the calculator.`;document.dispatchEvent(new Event("fullcharge:rates"))}).catch(()=>{$("cx-g").textContent="Unavailable";$("cx-e").textContent="Unavailable";$("cx-s").textContent="";$("cx-y").textContent="Enter your rates in the calculator";$("cx-f").textContent="Current prices could not be loaded. Open the calculator to enter your own electricity and gas rates."})})();
})();
