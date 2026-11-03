// SEO cost pages: render the shared charger picks (chargers.js) into #pk-list.
(function(){const L=document.getElementById("pk-list");if(!L||typeof CHARGERS==="undefined")return;
 const tesla=L.dataset.tesla==="1",eff=+L.dataset.eff||0;
 const list=CHARGERS.slice().sort((a,b)=>tesla?(a.plug==="NACS"?-1:b.plug==="NACS"?1:0):0);
 L.innerHTML=list.map(c=>chargerCard(c,{eff,tesla})).join("");const d=document.getElementById("pk-d");if(d)d.textContent=AMZ_DISCLOSE})();
