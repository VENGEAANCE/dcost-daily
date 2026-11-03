// Home charger picks, shared by calculator.html and chargers.html. Requires CONFIG (config.js) first.
// Prices are what each Amazon product page showed on CHARGER_PRICE_DATE. Re-check before changing them.
// The Associates tag lives in ONE place: CONFIG.AMAZON_TAG in config.js. Empty = links carry no tag param.
const CHARGER_PRICE_DATE="Oct 19, 2026";
const CHARGERS=[
 {asin:"B0CSPMC93Y",name:"ChargePoint HomeFlex",variant:"NACS, hardwired",price:549,amps:50,plug:"NACS",install:"Hardwired, so budget for an electrician",rating:"4.2",reviews:"228",
  who:"Tesla owners, and any newer EV with the NACS port",
  why:"Tesla plug, no adapter, up to 50A. Tesla's own Wall Connector only shows marked-up resellers on Amazon right now, so this is my Tesla pick there."},
 {asin:"B082LMVSLY",name:"Grizzl-E Classic",variant:"NEMA 14-50 plug",price:299.99,amps:40,plug:"J1772",install:"Plugs into a NEMA 14-50 outlet, no app",rating:"4.6",reviews:"3,445",
  who:"Anyone with a 14-50 outlet who wants the cheapest solid option",
  why:"Metal box, no Wi-Fi, nothing to update."},
 {asin:"B0CKKW6GNF",name:"Emporia EV Charger",variant:"J1772, hardwired",price:449,amps:48,plug:"J1772",install:"Hardwired, so budget for an electrician",rating:"4.8",reviews:"506",
  who:"Non-Tesla EVs that want full speed and a charging schedule",
  why:"Full 48A and an app that can start charging when your power is cheapest. Best rated of the three."}
];
const amzUrl=asin=>{const t=((typeof CONFIG!=="undefined"&&CONFIG.AMAZON_TAG)||"").trim();return "https://www.amazon.com/dp/"+asin+(t?"?tag="+encodeURIComponent(t):"")};
const usd=x=>"$"+(Math.round(x*100)%100?x.toFixed(2):Math.round(x).toLocaleString());
// Miles of range added per hour of charging. kW at the wall times ~90% charging efficiency, divided by the car's kWh per mile.
const miPerHr=(kw,kwhPer100)=>kwhPer100>0?kw*0.9/(kwhPer100/100):0;
const hrs=h=>!isFinite(h)||h<=0?"0 hr":h<1?Math.max(5,Math.round(h*60/5)*5)+" min":h.toFixed(1).replace(/\.0$/,"")+" hr";
function chargerCard(c,o){o=o||{};const kw=c.amps*0.24,mph=o.eff?miPerHr(kw,o.eff):0;
 const fit=o.tesla?(c.plug==="NACS"?'<span class="fit ok">Plugs straight into your Tesla</span>':'<span class="fit">Tesla needs a J1772 adapter</span>'):"";
 return `<article class="chg${o.tesla&&c.plug==="NACS"?" top":""}"><div class="chg-h"><div><div class="chg-n">${c.name}</div><div class="chg-v">${c.variant}</div></div><div class="chg-p">${usd(c.price)}<small>on Amazon, ${CHARGER_PRICE_DATE}</small></div></div>
 <div class="chg-spec"><span class="plug ${c.plug==="NACS"?"nacs":"j"}">${c.plug}</span><span>${c.amps}A</span><span>${kw.toFixed(1)} kW</span>${mph?`<span>~${Math.round(mph)} mi per hr</span>`:""}<span>${c.rating}★ (${c.reviews})</span></div>
 ${fit}<p class="chg-who"><b>For:</b> ${c.who}</p><p class="chg-why">${c.why}</p><p class="chg-in">${c.install}</p>
 <a class="pill w chg-b" href="${amzUrl(c.asin)}" target="_blank" rel="sponsored noopener">See it on Amazon</a></article>`}
// Disclosure is only true once an Associates tag is set. Until then, the fallback line.
const AMZ_TAGGED=!!((typeof CONFIG!=="undefined"&&CONFIG.AMAZON_TAG)||"").trim();
const AMZ_DISCLOSE=AMZ_TAGGED?"As an Amazon Associate I earn from qualifying purchases. Prices as of "+CHARGER_PRICE_DATE+"; the Amazon page has the current one.":"Some links may become affiliate links. Prices as of "+CHARGER_PRICE_DATE+".";
