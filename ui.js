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
const d=document.querySelector(".disc"),m=document.querySelector(".menu");
if(d&&m){
 m.id="site-menu";m.setAttribute("aria-label","Site navigation");
 d.setAttribute("aria-controls",m.id);d.setAttribute("aria-expanded","false");
 const toggle=open=>{m.classList.toggle("open",open);m.inert=!open;d.setAttribute("aria-expanded",String(open));d.setAttribute("aria-label",open?"Close menu":"Open menu")};
 toggle(false);d.onclick=()=>toggle(!m.classList.contains("open"));
 m.addEventListener("click",e=>{if(e.target.closest("a"))toggle(false)});
 document.addEventListener("click",e=>{if(!m.contains(e.target)&&!d.contains(e.target))toggle(false)});
 document.addEventListener("keydown",e=>{if(e.key==="Escape"&&m.classList.contains("open")){toggle(false);d.focus()}});
 document.addEventListener("focusin",e=>{if(!m.contains(e.target)&&!d.contains(e.target))toggle(false)});
 matchMedia("(min-width:1100px)").addEventListener("change",e=>{if(e.matches)toggle(false)});
}
const current=location.pathname.replace(/\/$/,"")||"/";
document.querySelectorAll(".menu a,.side a").forEach(a=>{if(!a.hash&&(a.pathname.replace(/\/$/,"")||"/")===current)a.setAttribute("aria-current","page")});
const main=document.querySelector(".main");if(main){main.id="main-content";main.setAttribute("role","main");main.tabIndex=-1;const skip=document.createElement("a");skip.className="skip";skip.href="#main-content";skip.textContent="Skip to content";document.body.prepend(skip)}})();
// Footer disclosure: static HTML carries the Associates line; swap to the fallback if AMAZON_TAG is ever emptied.
(function(){const tagged=!!((CONFIG.AMAZON_TAG||"").trim());if(tagged)return;addEventListener("DOMContentLoaded",()=>{const dt=typeof CHARGER_PRICE_DATE!=="undefined"?CHARGER_PRICE_DATE:"Oct 19, 2026";
 document.querySelectorAll(".amz-f").forEach(p=>p.textContent="Some links may become affiliate links. Prices as of "+dt+".")})})();
// Full Charge: savings are mint only when the EV actually saves money (calculator card 04).
(function(){const sv=document.getElementById("sv");if(!sv||!("MutationObserver" in window))return;const t=()=>sv.classList.toggle("neg",sv.textContent.trim().startsWith("-"));new MutationObserver(t).observe(sv,{childList:true,characterData:true,subtree:true});t()})();

// Associate the existing floating labels with their controls on every tool page.
document.querySelectorAll(".fld").forEach((field,i)=>{const control=field.querySelector("input,select"),label=field.querySelector("label");if(control&&label){if(!control.id)control.id="field-"+i;label.htmlFor=control.id}});
document.querySelectorAll(".chip").forEach(chip=>{chip.setAttribute("aria-pressed",String(chip.classList.contains("on")));chip.addEventListener("click",()=>{document.querySelectorAll(".chip").forEach(other=>other.setAttribute("aria-pressed",String(other===chip)))})});

// Stageshow motion principles applied to real controls: input, response, rest.
// No synthetic values or loops; the underlying DOM always holds the real result.
(() => {
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const activeAnimations = new Map();

  const respond = (element, frames, options = {}) => {
    if (!element || reducedMotion.matches || !element.animate) return;
    activeAnimations.get(element)?.cancel();
    const animation = element.animate(frames, {
      duration: 220,
      fill: 'backwards',
      easing: 'cubic-bezier(0.25, 0.8, 0.25, 1)',
      ...options,
    });
    activeAnimations.set(element, animation);
    animation.onfinish = () => {
      if (activeAnimations.get(element) === animation) {
        activeAnimations.delete(element);
      }
    };
  };

  // Change only the updated value; retain the result's text and geometry.
  for (const id of ['sv', 'pct']) {
    const element = document.getElementById(id);
    if (!element) continue;
    let previous = element.textContent;
    new MutationObserver(() => {
      const next = element.textContent;
      if (previous && next !== previous) {
        respond(element, [{opacity: 0.65}, {opacity: 1}]);
      }
      previous = next;
    }).observe(element, {childList: true, characterData: true, subtree: true});
  }

  // Data can load below the fold. Reveal the comparison once, when visible.
  const comparison = document.getElementById('cx');
  let ready = false;
  let visible = !('IntersectionObserver' in window);
  let played = false;
  let observer;
  const revealComparison = () => {
    if (!ready || !visible || played) return;
    played = true;
    observer?.disconnect();
    comparison.querySelectorAll('.trk > i').forEach((bar, index) => {
      respond(bar, [{transform: 'scaleX(0)'}, {transform: 'scaleX(1)'}], {
        duration: 650,
        delay: index * 70,
      });
    });
    respond(document.getElementById('cx-s'),
      [{opacity: 0.65}, {opacity: 1}], {duration: 300, delay: 140});
  };
  if (comparison) {
    document.addEventListener('fullcharge:rates', () => {
      ready = true;
      revealComparison();
    }, {once: true});
    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver((entries) => {
        visible = entries[0].isIntersecting && entries[0].intersectionRatio >= 0.3;
        revealComparison();
      }, {threshold: 0.3});
      observer.observe(comparison);
    }
  }

  // Preference changes take effect immediately, including during a transition.
  reducedMotion.addEventListener('change', (event) => {
    if (!event.matches) return;
    activeAnimations.forEach((animation) => animation.cancel());
    activeAnimations.clear();
    document.querySelectorAll('.cell.charging').forEach((cell) => {
      cell.classList.remove('charging');
    });
  });
})();
