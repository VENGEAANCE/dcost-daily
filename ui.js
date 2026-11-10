// Use Beehiiv's current v3 embed; keep the static signup link independent.
(function(){
const value = (CONFIG.BEEHIIV_EMBED_URL || '').trim();
const formId = value.match(/[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}/i)?.[0];
if (formId) {
 const loadEmbed = (container) => {
  const observer = new MutationObserver(() => {
   const frame = container.querySelector('iframe');
   if (!frame) return;
   frame.title = 'Subscribe to dcost daily';
   frame.classList.add('beehiiv-embed');
   observer.disconnect();
  });
  observer.observe(container, {childList: true, subtree: true});
  const loader = document.createElement('script');
  loader.async = true;
  loader.src = 'https://subscribe-forms.beehiiv.com/v3/loader.js';
  loader.dataset.beehiivForm = formId;
  container.append(loader);
 };
 const containers = document.querySelectorAll('.nl-embed');
 if ('IntersectionObserver' in window) {
  const embedObserver = new IntersectionObserver((entries) => {
   for (const entry of entries) {
    if (entry.isIntersecting) {
     embedObserver.unobserve(entry.target);
     entry.target.querySelectorAll('.nl-embed').forEach(loadEmbed);
    }
   }
  }, {rootMargin: '400px'});
  // Observe the visible newsletter section, not its initially empty container.
  for (const container of containers) {
   const section = container.closest('#newsletter') || container.parentElement;
   if (!section) {
    loadEmbed(container);
    continue;
   }
   embedObserver.observe(section);
  }
 } else {
  containers.forEach(loadEmbed);
 }
}
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
