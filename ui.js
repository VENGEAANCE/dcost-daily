// Requires CONFIG (config.js loaded first). Newsletter switches on when BEEHIIV_EMBED_URL is set (full URL or bare Beehiiv form id).
// The beehiiv form is framed at the card's width (no beehiiv embed.js, which forced a fixed 560px width).
(function(){const v=(CONFIG.BEEHIIV_EMBED_URL||"").trim();if(v){const src=/^https?:/.test(v)?v:"https://subscribe-forms.beehiiv.com/"+v;
document.querySelectorAll(".nl").forEach(b=>{b.classList.add("on");b.innerHTML='<div class="bh"><iframe src="'+src+'" class="beehiiv-embed" data-test-id="beehiiv-embed" title="Subscribe to dcost daily" frameborder="0" scrolling="no"></iframe></div><p class="nlnote">Trouble with the form? <a href="https://dcostdaily.beehiiv.com/subscribe" target="_blank" rel="noopener">Subscribe on beehiiv</a>.</p>'});
const frames=()=>document.querySelectorAll(".nl iframe");
addEventListener("message",e=>{if(e.origin!=="https://subscribe-forms.beehiiv.com")return;const t=e.data&&e.data.type,p=(e.data&&e.data.payload)||{};
 frames().forEach(f=>{if(f.contentWindow!==e.source)return;
  if(t==="beehiiv:child-loaded")f.contentWindow.postMessage({type:"beehiiv:parent-loaded",payload:{handlesRedirect:false}},"*");
  else if((t==="beehiiv:styles"||t==="beehiiv:challenge")&&p.height){const h=parseInt(p.height,10);if(h>0)f.style.height=h+"px";f.parentNode.classList.toggle("chal",t==="beehiiv:challenge")}
  else if(t==="beehiiv:challenge-resolved")f.parentNode.classList.remove("chal")})})}
const d=document.querySelector(".disc"),m=document.querySelector(".menu");if(d)d.onclick=()=>m.classList.toggle("open")})();
// Footer disclosure: static HTML carries the Associates line; swap to the fallback if AMAZON_TAG is ever emptied.
(function(){const tagged=!!((CONFIG.AMAZON_TAG||"").trim());if(tagged)return;addEventListener("DOMContentLoaded",()=>{const dt=typeof CHARGER_PRICE_DATE!=="undefined"?CHARGER_PRICE_DATE:"Oct 19, 2026";
 document.querySelectorAll(".amz-f").forEach(p=>p.textContent="Some links may become affiliate links. Prices as of "+dt+".")})})();
// Full Charge: savings are mint only when the EV actually saves money (calculator card 04).
(function(){const sv=document.getElementById("sv");if(!sv||!("MutationObserver" in window))return;const t=()=>sv.classList.toggle("neg",sv.textContent.trim().startsWith("-"));new MutationObserver(t).observe(sv,{childList:true,characterData:true,subtree:true});t()})();
