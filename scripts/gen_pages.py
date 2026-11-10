#!/usr/bin/env python3
"""Generate the SEO cost pages from data/rates.json (EIA) and the EPA ratings below.
Writes ev-cost/<state>.html (51), ev-cost/index.html (hub), tesla/<trim>.html, guides/<slug>.html,
and data/pages.txt (URL list). Run after fetch_data.py; then gen_sitemap.py; then deploy.
Voice: plain, number-first, every number with its source and date. No em-dashes."""
import json, os, re, html, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://dcostdaily.com"
ASSET_VERSION = "20261103signup"
R = json.load(open(os.path.join(ROOT, "data", "rates.json")))
S = R["states"]
MONTH, PRIOR = R["elec_month"], R["elec_prior_month"]
GW = datetime.date.fromisoformat(R["gas_week"]); GWEEK = f"{GW:%b} {GW.day}, {GW.year}"
US_C, US_G = R["us_cents"], R["us_gas"]
ESRC, GSRC = R["elec_source"], R["gas_source"]
PRICE_DATE = re.search(r'CHARGER_PRICE_DATE="([^"]+)"', open(os.path.join(ROOT, "chargers.js"), encoding="utf-8").read()).group(1)
MI = 1000  # miles a month, same default as the calculator
# EPA combined kWh/100 mi (fueleconomy.gov web services, 2026 model year). hub=True gets its own page.
TRIMS = [
 ("model-3-standard-rwd","Model 3 Standard RWD",50251,24.3033,321,True),
 ("model-3-premium-rwd","Model 3 Premium RWD",50038,24.6398,363,False),
 ("model-3-premium-awd","Model 3 Premium AWD",50037,26.3757,346,True),
 ("model-3-performance-awd","Model 3 Performance AWD",50250,30.2452,314,True),
 ("model-y-standard-rwd","Model Y Standard RWD",50040,24.3451,321,True),
 ("model-y-long-range-rwd","Model Y Long Range RWD",49743,25.2252,357,False),
 ("model-y-long-range-awd","Model Y Long Range AWD",49744,27.4959,327,True),
 ("model-y-performance-awd","Model Y Performance AWD",50253,31.977,306,True),
 ("model-s","Model S",49741,27.1309,410,True),
 ("model-x","Model X",49745,32.2022,352,True),
 ("cybertruck-awd","Cybertruck AWD",50039,42.9059,325,True),
]
T = {t[0]: t for t in TRIMS}
HEAD = "model-y-long-range-awd"
GAS = [("Toyota Camry Hybrid LE",51,49823),("Toyota RAV4 Hybrid",43,50285),("Honda Accord 1.5T",32,50070),("Honda CR-V 1.5T",30,49352)]
ADJ = {"AL":"FL GA MS TN","AK":"WA OR","AZ":"CA NV UT NM CO","AR":"LA MS MO OK TN TX","CA":"AZ NV OR","CO":"AZ KS NE NM OK UT WY","CT":"MA NY RI","DE":"MD NJ PA","DC":"MD VA","FL":"AL GA","GA":"AL FL NC SC TN","HI":"CA WA","ID":"MT NV OR UT WA WY","IL":"IN IA KY MO WI","IN":"IL KY MI OH","IA":"IL MN MO NE SD WI","KS":"CO MO NE OK","KY":"IL IN MO OH TN VA WV","LA":"AR MS TX","ME":"NH MA","MD":"DE PA VA WV DC","MA":"CT NH NY RI VT","MI":"IN OH WI","MN":"IA ND SD WI","MS":"AL AR LA TN","MO":"AR IL IA KS KY NE OK TN","MT":"ID ND SD WY","NE":"CO IA KS MO SD WY","NV":"AZ CA ID OR UT","NH":"ME MA VT","NJ":"DE NY PA","NM":"AZ CO OK TX","NY":"CT MA NJ PA VT","NC":"GA SC TN VA","ND":"MN MT SD","OH":"IN KY MI PA WV","OK":"AR CO KS MO NM TX","OR":"CA ID NV WA","PA":"DE MD NJ NY OH WV","RI":"CT MA","SC":"GA NC","SD":"IA MN MT NE ND WY","TN":"AL AR GA KY MS MO NC VA","TX":"AR LA NM OK","UT":"AZ CO ID NV NM WY","VT":"MA NH NY","VA":"KY MD NC TN WV DC","WA":"ID OR","WV":"KY MD OH PA VA","WI":"IL IA MI MN","WY":"CO ID MT NE SD UT"}
slug = lambda ab: re.sub(r"[^a-z]+", "-", S[ab]["name"].lower()).strip("-")
rate = lambda ab: S[ab]["cents"] / 100
ORDER = sorted(S, key=lambda a: S[a]["cents"])  # cheapest first
RANK = {a: i + 1 for i, a in enumerate(ORDER)}
N = len(ORDER)
def m(x): return "$" + f"{x:,.0f}"
def m2(x): return "$" + f"{x:,.2f}"
def per100(eff, r): return eff * r          # $ per 100 mi: kWh/100mi x $/kWh
def month(eff, r, mi=MI): return mi * eff / 100 * r
def gas100(mpg, g): return 100 / mpg * g
def pct(a, b): return (a - b) / b * 100
def nth(n, word): return f"the {word}" if n == 1 else f"the {ordinal(n)} {word}"
def ordinal(n): return f"{n}{'th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def e(s): return html.escape(s, quote=True)
def calc_url(ab=None, ev=None):
    q = []
    if ab: q.append("state=" + ab.lower())
    if ev: q.append("ev=" + ev)
    return "/calculator" + ("?" + "&amp;".join(q) if q else "")

NAV = [("/", "Today"), ("/archive", "Archive"), ("/calculator", "Calculator"), ("/ev-cost/", "By state"), ("/compare/", "EV vs gas"), ("/chargers", "Chargers"), ("/#newsletter", "Newsletter")]
def page(path, title, desc, h1, h1b, body, on="/ev-cost/", jsld=None, picks=True, tesla=True, eff=None):
    nav_m = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    nav_s = "".join(f'<a class="{"on" if h == on else ""}" href="{h}">{t}</a>' for h, t in NAV)
    pk = ""
    if picks:
        pk = f'''<section class="picks" id="picks" aria-labelledby="pk-h"><p class="eyebrow">Home charger picks</p><h3 id="pk-h">Charge it at home</h3><p class="pk-math">Home charging is how you get the prices on this page. These are the three Level 2 chargers I'd buy, Amazon prices from {PRICE_DATE}.</p><div class="chgs" id="pk-list" data-tesla="{1 if tesla else 0}" data-eff="{eff or ''}"></div><p class="amz-d" id="pk-d">As an Amazon Associate I earn from qualifying purchases. Prices as of {PRICE_DATE}.</p><a class="pk-all" href="/chargers">Compare all three on one page <span aria-hidden="true">→</span></a></section>'''
    ld = f'<script type="application/ld+json">{json.dumps(jsld)}</script>' if jsld else ""
    return f'''<!doctype html><html lang=en data-theme="dark"><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}"><link rel="icon" href="/favicon.svg?v=20261103signup" type="image/svg+xml"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}"><link rel=preconnect href="https://fonts.googleapis.com"><link rel=preconnect href="https://fonts.gstatic.com" crossorigin><link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Semi+Condensed:wght@500;600;700;800&display=swap"><link rel=stylesheet href="/style.css?v={ASSET_VERSION}">{ld}</head><body><header class="hd"><a class="wm" href="/"><svg class="wm-b" width="41" height="22" viewBox="0 0 41 22" aria-hidden="true"><rect x="1" y="1" width="36" height="20" rx="4" fill="none" stroke="#fff" stroke-width="2"/><rect x="37" y="7" width="3" height="8" rx="1" fill="#fff"/><rect x="4" y="4" width="5" height="14" rx="1" fill="#fff"/><rect x="10.5" y="4" width="5" height="14" rx="1" fill="#fff"/><rect x="17" y="4" width="5" height="14" rx="1" fill="#fff"/><rect x="23.5" y="4" width="5" height="14" rx="1" fill="#fff"/><rect x="30" y="4" width="5" height="14" rx="1" fill="#1d9bf0"/></svg><b>DCOST</b><span>DAILY</span></a><div class="hr"><a class="pill o" href="/#newsletter">Subscribe</a><button class="disc" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 16 16"><path d="M2 4h12M2 8h12M2 12h12" stroke="#fff" stroke-width="1.5"/></svg></button></div></header><nav class="menu">{nav_m}</nav><div class="shell"><nav class="side">{nav_s}</nav><div class="main"><section class="hero"><h1>{h1}<br><span style="color:#ffffff99">{h1b}</span></h1></section>
<section class="sec sp">{body}{pk}</section></div></div>{FOOT}<script src="/config.js?v={ASSET_VERSION}"></script><script src="/ui.js?v={ASSET_VERSION}"></script><script src="/chargers.js?v={ASSET_VERSION}"></script><script src="/pages.js?v={ASSET_VERSION}"></script></body></html>
'''
FOOT = f'''<footer><div class="fg"><div><h2>Site</h2><a href="/">Today</a><a href="/archive">Archive</a><a href="/calculator">Calculator</a><a href="/ev-cost/">EV cost by state</a><a href="/compare/">Tesla vs gas matchups</a><a href="/chargers">Home charger picks</a><a href="/#newsletter">Newsletter</a></div><div><h2>Guides</h2><a href="/guides/ev-electric-bill">What an EV adds to your power bill</a><a href="/guides/tesla-vs-hybrid-fuel-cost">Tesla vs a hybrid, by state</a><a href="/guides/level-1-vs-level-2-charging">Level 1 vs Level 2</a><a href="/guides/ev-charger-breaker-size">Charger breaker size</a><a href="/guides/nema-14-50-vs-hardwired">14-50 outlet vs hardwired</a><a href="/guides/electricity-price-change-by-state">Electricity price change by state</a></div><div><h2>Sources</h2><a href="https://www.fueleconomy.gov">fueleconomy.gov (EPA)</a><a href="{ESRC}">EIA Electric Power Monthly, Table 5.6.A</a><a href="{GSRC}">EIA weekly retail gasoline by area</a><a href="https://x.com/dcostaverage">@dcostaverage</a></div></div><p class="amz-f">As an Amazon Associate I earn from qualifying purchases.</p><div class="copy">© 2026 dcost daily</div><svg class="huge" viewBox="0 0 1000 150" preserveAspectRatio="xMidYMid meet"><text x="500" y="128" text-anchor="middle" textLength="990" lengthAdjust="spacingAndGlyphs" font-family="ui-sans-serif,system-ui,sans-serif" font-size="150" font-weight="500" fill="none" stroke="#ffffff66" stroke-width="1">DCOSTDAILY</text></svg></footer>'''

def strip(hl=None):
    """All 51 state rates as ticks on one line, the page's state lit. Sized for a 390px phone."""
    lo, hi, W = 10, 50, 360
    x = lambda c: 6 + (min(c, hi) - lo) / (hi - lo) * (W - 12)
    ticks = "".join(f'<line x1="{x(S[a]["cents"]):.1f}" x2="{x(S[a]["cents"]):.1f}" y1="24" y2="46" stroke="{"#fff" if a == hl else "#ffffff4d"}" stroke-width="{3 if a == hl else 1}"/>' for a in ORDER if a != hl)
    if hl: ticks += f'<line x1="{x(S[hl]["cents"]):.1f}" x2="{x(S[hl]["cents"]):.1f}" y1="20" y2="50" stroke="#fff" stroke-width="3"/>'
    usx = x(US_C)
    lab = ""
    if hl:
        hx = x(S[hl]["cents"]); anc = "start" if hx < 70 else "end" if hx > 290 else "middle"
        lab = f'<text x="{hx:.1f}" y="13" fill="#fff" font-size="12" font-weight="500" text-anchor="{anc}">{e(S[hl]["name"])} {S[hl]["cents"]:.2f}¢</text>'
    return f'''<figure class="strip"><svg viewBox="0 0 {W} 70" role="img" aria-label="Residential electricity price in all {N} states, {MONTH}">{lab}{ticks}<line x1="{usx:.1f}" x2="{usx:.1f}" y1="20" y2="50" stroke="#1d9bf0" stroke-width="1.5" stroke-dasharray="2 2"/><text x="6" y="64" fill="#ffffff80" font-size="10">10¢</text><text x="{usx:.1f}" y="64" fill="#1d9bf0" font-size="10" text-anchor="middle">US {US_C:.2f}¢</text><text x="{W-6}" y="64" fill="#ffffff80" font-size="10" text-anchor="end">50¢</text></svg><figcaption>Each line is one state's average home electricity price, {MONTH}. Cheaper to the left. Source: <a href="{ESRC}">EIA</a>.</figcaption></figure>'''

def gas_label(ab):
    g = S[ab]["gas"]
    return (f'{S[ab]["name"]}\'s own EIA series' if g["own"] else f'the EIA {g["area"]} average (EIA has no separate weekly series for {S[ab]["name"]})')

def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="dt {cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
def src_note():
    return f'<p class="note">Electricity: residential average, {MONTH}, <a href="{ESRC}">EIA Electric Power Monthly Table 5.6.A</a>. Gas: regular retail, week of {GWEEK}, <a href="{GSRC}">EIA weekly retail gasoline by area</a>. Efficiency: EPA combined kWh per 100 miles, which already includes charging losses, from <a href="https://www.fueleconomy.gov">fueleconomy.gov</a>. Monthly figures use {MI:,} miles.</p>'
def stats(items):
    return '<div class="stats">' + "".join(f'<div class="stat"><div class="sv">{v}</div><div class="sl">{l}</div></div>' for v, l in items) + "</div>"
def links_block(title, items):
    return f'<div class="rel"><p class="eyebrow">{title}</p><ul>' + "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in items) + "</ul></div>"
def guide_links(skip=None):
    G = [("/guides/ev-electric-bill","What an EV adds to your power bill"),("/guides/tesla-vs-hybrid-fuel-cost","Tesla vs a 51 MPG hybrid, state by state"),("/guides/level-1-vs-level-2-charging","Level 1 vs Level 2: hours per night"),("/guides/ev-charger-breaker-size","What breaker an EV charger needs"),("/guides/nema-14-50-vs-hardwired","NEMA 14-50 outlet or hardwired?"),("/guides/electricity-price-change-by-state","Where electricity got pricier this year")]
    return [g for g in G if g[0] != skip]

pages = []  # (path, file)
import sys as _s; _s.path.insert(0, os.path.join(ROOT, "scripts")); from vehicles import PAIRS as _PAIRS, NAMES as _NAMES
def write(path, f, doc):
    assert "—" not in doc and "–" not in doc, f"dash in {f}"
    os.makedirs(os.path.dirname(os.path.join(ROOT, f)), exist_ok=True)
    open(os.path.join(ROOT, f), "w", encoding="utf-8").write(doc); pages.append((path, f))

# ---------- state pages ----------
hy = GAS[0]; suv = GAS[3]
for ab in ORDER:
    st = S[ab]; nm = st["name"]; r = rate(ab); c = st["cents"]; g = st["gas"]["usd"]
    hd = T[HEAD]; mo = month(hd[3], r); rk = RANK[ab]
    vs_us = pct(c, US_C); yoy = pct(c, st["cents_prior"])
    suv_mo = MI / suv[1] * g; hy_mo = MI / hy[1] * g
    m3 = T["model-3-standard-rwd"]; m3_100 = per100(m3[3], r); hy_100 = gas100(hy[1], g)
    be_gas = m3_100 / (100 / hy[1])  # gas price where the 51 MPG hybrid matches a Model 3 Standard
    be_rate = hy_100 / m3[3] * 100   # c/kWh where the Model 3 matches the hybrid
    kwh_mo = MI * hd[3] / 100
    # lead sentence varies with where the state sits
    if rk <= 10: tier = f"That's {abs(vs_us):.0f}% below the US average and {nth(rk, 'cheapest')} of {N} (50 states plus DC), so {nm} is {'the cheapest place' if rk == 1 else 'one of the cheapest places'} in the country to charge at home."
    elif rk > N - 10: tier = f"That's {abs(vs_us):.0f}% above the US average and {nth(N - rk + 1, 'most expensive')} of {N} (50 states plus DC), so charging at home costs more here than {'anywhere else' if rk == N else 'almost anywhere'}."
    else: tier = f"That's {abs(vs_us):.0f}% {'below' if c < US_C else 'above'} the US average of {US_C:.2f}¢, and {ordinal(rk)} cheapest of {N} (50 states plus DC)."
    if abs(yoy) < 1: trend = f"It barely moved from {PRIOR} ({st['cents_prior']:.2f}¢)."
    elif yoy > 0: trend = f"Prices are up {yoy:.1f}% from {st['cents_prior']:.2f}¢ in {PRIOR}, so the same driving costs {m2(mo - month(hd[3], st['cents_prior']/100))} more a month than a year ago."
    else: trend = f"Prices are down {-yoy:.1f}% from {st['cents_prior']:.2f}¢ in {PRIOR}, so the same driving costs {m2(month(hd[3], st['cents_prior']/100) - mo)} less a month than a year ago."
    if m3_100 < hy_100:
        hyb = f"Even against a 51 MPG Camry Hybrid, the Model 3 Standard wins here: {m2(m3_100)} vs {m2(hy_100)} per 100 miles. Gas would have to fall to {m2(be_gas)} a gallon for the hybrid to tie."
    else:
        hyb = f"Here's the catch: a 51 MPG Camry Hybrid is cheaper to fuel than a Model 3 Standard in {nm}, {m2(hy_100)} vs {m2(m3_100)} per 100 miles. Electricity would need to drop to {be_rate:.1f}¢ for the Tesla to tie. A time-of-use or EV plan from your utility can get you there, so check yours."
    rows = []
    for t in TRIMS:
        lab = f'<a href="/tesla/{t[0]}">{t[1]}</a>' if t[5] else t[1]
        rows.append([lab, f"{t[3]:.1f}", m2(per100(t[3], r)), m(month(t[3], r))])
    grows = [[f"{gname} ({mpg} MPG)", m2(gas100(mpg, g)), m(MI / mpg * g), m((MI / mpg * g - mo) * 12)] for gname, mpg, _ in GAS]
    nb = [a for a in ADJ[ab].split()]
    nbl = []
    for a in sorted(nb, key=lambda a: S[a]["cents"]):
        d = month(hd[3], rate(a)) - mo
        nbl.append((f"/ev-cost/{slug(a)}", f"{S[a]['name']}: {S[a]['cents']:.2f}¢, {m(month(hd[3], rate(a)))} a month ({'+' if d >= 0 else '-'}{m(abs(d))})"))
    nb_title = "Nearby states, same Model Y" if ab not in ("AK", "HI") else "Closest mainland states, same Model Y"
    body = f'''<p class="lead"><b>{m(mo)} a month.</b> That's what {MI:,} miles in a {hd[1]} costs on {nm}'s average home electricity price of <b>{c:.2f}¢ per kWh</b> ({MONTH}, EIA). {tier} {trend}</p>
{stats([(m(mo), f"{hd[1]}, {MI:,} mi a month"), (m2(per100(hd[3], r)), "per 100 miles"), (m(suv_mo), f"gas for a {suv[1]} MPG {suv[0].split(' ',1)[1]}, same miles"), (f"{kwh_mo:.0f} kWh", "added to your monthly bill")])}
{strip(ab)}
<a class="pill w cta" href="{calc_url(ab, HEAD)}">Run your own miles with {nm} prices</a>
<h2 class="h2s">Every Tesla in {nm}<span>{c:.2f}¢ per kWh, {MI:,} miles a month.</span></h2>
{table(["Trim", "kWh/100 mi", "Per 100 mi", "Per month"], rows)}
<p class="txt">The spread is the battery's appetite. A Cybertruck uses {T['cybertruck-awd'][3]/m3[3]:.1f}x the energy of a Model 3 Standard per mile, so it costs {m(month(T['cybertruck-awd'][3], r) - month(m3[3], r))} more a month to drive the same {MI:,} miles in {nm}.</p>
<h2 class="h2s">EV vs gas in {nm}<span>Regular gas at {m2(g)} a gallon, week of {GWEEK}.</span></h2>
<p class="txt">Gas price is from {gas_label(ab)}. Savings compare each car to the {hd[1]} above over 12 months.</p>
{table(["Gas car", "Per 100 mi", "Per month", "Model Y saves / yr"], grows)}
<p class="txt">{hyb}</p>
<p class="txt"><b>Before you trust the average:</b> {c:.2f}¢ is what {nm} homes paid on average, fees included. Your bill shows your real rate; divide the total by the kWh used. Supercharging usually costs more than home power, so road trips will run above these numbers.</p>
{links_block(nb_title, nbl)}
{links_block("Go deeper", [("/ev-cost/", f"All {N} states ranked"), ("/compare/", "Tesla vs gas car matchups")] + [(f"/tesla/{t[0]}", f"Cost to charge a {t[1]} in every state") for t in TRIMS if t[0] in ("model-3-standard-rwd", "cybertruck-awd")] + guide_links()[:3])}
{src_note()}'''
    title = f"Cost to charge a Tesla in {nm}: {m(mo)} a month ({MONTH}) · dcost daily"
    desc = f"{nm} homes paid {c:.2f}¢/kWh in {MONTH} (EIA), {ordinal(rk)} cheapest of {N}. A {hd[1]} costs {m(mo)} a month for {MI:,} miles vs {m(suv_mo)} in gas for a {suv[1]} MPG SUV. Every trim listed."
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "EV cost by state", "item": BASE + "/ev-cost/"}, {"@type": "ListItem", "position": 2, "name": nm, "item": f"{BASE}/ev-cost/{slug(ab)}"}]}
    write(f"/ev-cost/{slug(ab)}", f"ev-cost/{slug(ab)}.html", page(f"/ev-cost/{slug(ab)}", title, desc, f"Charging a Tesla in {nm}", f"{m(mo)} a month at {c:.2f}¢ per kWh", body, jsld=ld, eff=hd[3]))

# ---------- hub ----------
hd = T[HEAD]
rows = []
for ab in ORDER:
    st = S[ab]; r = rate(ab); mo = month(hd[3], r); sv = (MI / suv[1] * st["gas"]["usd"] - mo) * 12
    rows.append([f'{RANK[ab]}', f'<a href="/ev-cost/{slug(ab)}">{st["name"]}</a>', f'{st["cents"]:.2f}¢', m(mo), m(sv)])
lo, hi_ = ORDER[0], ORDER[-1]
body = f'''<p class="lead"><b>{m(month(hd[3], rate(lo)))} to {m(month(hd[3], rate(hi_)))} a month.</b> That's the range for {MI:,} miles in a {hd[1]}, from {S[lo]["name"]} ({S[lo]["cents"]:.2f}¢ per kWh) to {S[hi_]["name"]} ({S[hi_]["cents"]:.2f}¢), using {MONTH} home electricity prices from EIA. The US average is {US_C:.2f}¢, or {m(month(hd[3], US_C/100))} a month.</p>
{strip()}
<a class="pill w cta" href="/calculator">Open the calculator</a>
<h2 class="h2s">All {N} states, cheapest first<span>{hd[1]}, {MI:,} miles a month. Savings vs a {suv[1]} MPG SUV.</span></h2>
{table(["#", "State", "¢/kWh", "Per mo", "Saves/yr"], rows, "rank")}
<p class="txt">Savings use each state's regular gas price for the week of {GWEEK}. EIA publishes weekly gas prices for 9 states; the rest use their region's average, and each state page says which.</p>
{links_block("Cost by Tesla trim", [(f"/tesla/{t[0]}", f"{t[1]}: {m(month(t[3], US_C/100))} a month at the US average") for t in TRIMS if t[5]])}
{links_block("Guides", guide_links())}
{src_note()}'''
write("/ev-cost/", "ev-cost/index.html", page("/ev-cost/", f"Cost to charge an EV in every state ({MONTH}) · dcost daily", f"Home charging cost for a Tesla in all 50 states and DC, ranked. {m(month(hd[3], rate(lo)))} a month in {S[lo]['name']} to {m(month(hd[3], rate(hi_)))} in {S[hi_]['name']} for {MI:,} miles. EIA {MONTH} prices.", "EV charging cost<br>by state", f"{MONTH} prices, all {N} ranked", body, eff=hd[3]))

# ---------- trim hubs ----------
for t in [t for t in TRIMS if t[5]]:
    sl, name, vid, eff, rng, _ = t
    usmo = month(eff, US_C / 100)
    rows = [[f'<a href="/ev-cost/{slug(ab)}">{S[ab]["name"]}</a>', f'{S[ab]["cents"]:.2f}¢', m2(per100(eff, rate(ab))), m(month(eff, rate(ab)))] for ab in ORDER]
    sib = [x for x in TRIMS if x[1].split()[1] == name.split()[1] and x[0] != sl] if name.startswith("Model") else []
    if not sib: sib = [x for x in TRIMS if x[0] in ("model-y-long-range-awd", "model-3-standard-rwd")]
    sibtxt = " ".join(f"A {x[1]} uses {x[3]:.1f} kWh, so it costs {m(abs(month(x[3], US_C/100) - usmo))} {'more' if x[3] > eff else 'less'} a month." for x in sib[:3])
    l2 = [(a, a * 0.24) for a in (32, 40, 48)]
    spd = "; ".join(f"{a}A Level 2 adds about {kw * 0.9 / (eff / 100):.0f}" for a, kw in l2)
    hy100 = gas100(hy[1], US_G); m100 = per100(eff, US_C / 100)
    gas_line = (f"At the US average it costs {m2(m100)} per 100 miles to charge, against {m2(gas100(suv[1], US_G))} in gas for a {suv[1]} MPG SUV and {m2(hy100)} for a {hy[1]} MPG Camry Hybrid at {m2(US_G)} a gallon.")
    body = f'''<p class="lead"><b>{m(usmo)} a month</b> at the US average of {US_C:.2f}¢ per kWh. The EPA rates the 2026 {name} at <b>{eff:.1f} kWh per 100 miles</b> and {rng} miles of range (<a class="lnk" href="https://www.fueleconomy.gov/feg/PowerSearch.do?action=noform&amp;path=1&amp;year1=2026&amp;year2=2026&amp;id={vid}">fueleconomy.gov</a>). Across the states that swings from {m(month(eff, rate(lo)))} in {S[lo]["name"]} to {m(month(eff, rate(hi_)))} in {S[hi_]["name"]}.</p>
{stats([(m(usmo), f"{MI:,} mi a month, US average"), (m2(m100), "per 100 miles"), (f"{MI*eff/100:.0f} kWh", "added to your monthly bill"), (m(usmo*12), "a year at 12,000 miles")])}
<a class="pill w cta" href="{calc_url(None, sl)}">Open the calculator with a {name}</a>
<p class="txt">{gas_line} {sibtxt}</p>
<p class="txt"><b>Charging speed at home:</b> a regular 120V outlet adds about {1.44 * 0.9 / (eff / 100):.0f} miles per hour. {spd} miles per hour, if the car's onboard charger accepts that much. <a class="lnk" href="/guides/level-1-vs-level-2-charging">How many hours a night that means</a>.</p>
<h2 class="h2s">{name} cost in every state<span>Cheapest first, {MI:,} miles a month.</span></h2>
{table(["State", "¢/kWh", "Per 100 mi", "Per month"], rows)}
{links_block("Against gas cars", [(f"/compare/{p[0]}", f"{_NAMES[p[0]][0]} vs {_NAMES[p[0]][1]}") for p in _PAIRS if p[1].split("-")[1] == sl.split("-")[1]] + [("/compare/", "Every matchup")])}
{links_block("Other Teslas", [(f"/tesla/{x[0]}", f"{x[1]}: {m(month(x[3], US_C/100))} a month") for x in TRIMS if x[5] and x[0] != sl])}
{links_block("Guides", guide_links()[:4])}
{src_note()}'''
    write(f"/tesla/{sl}", f"tesla/{sl}.html", page(f"/tesla/{sl}", f"Cost to charge a {name}: {m(usmo)} a month, every state · dcost daily", f"The 2026 {name} uses {eff:.1f} kWh per 100 miles (EPA). Charging costs {m(usmo)} a month for {MI:,} miles at the US average, from {m(month(eff, rate(lo)))} to {m(month(eff, rate(hi_)))} by state. {MONTH} EIA prices.", f"Cost to charge a<br>{name}", f"{m(usmo)} a month at the US average", body, eff=eff))

# ---------- guides ----------
def guide(sl, title, desc, h1, h1b, body):
    write(f"/guides/{sl}", f"guides/{sl}.html", page(f"/guides/{sl}", title + " · dcost daily", desc, h1, h1b, body + links_block("More guides", guide_links(f"/guides/{sl}")) + links_block("By state", [("/ev-cost/", f"All {N} states ranked")] + [(f"/ev-cost/{slug(a)}", S[a]["name"]) for a in ("CA", "TX", "FL", "NY", "WA")]) + src_note(), eff=T[HEAD][3]))

# 1 power bill
rows = [[t[1], f"{500*t[3]/100:.0f}", f"{1000*t[3]/100:.0f}", f"{1500*t[3]/100:.0f}"] for t in TRIMS]
cost = [[f'<a href="/ev-cost/{slug(a)}">{S[a]["name"]}</a>', f'{S[a]["cents"]:.2f}¢', m(month(T[HEAD][3], rate(a))), m(month(T["cybertruck-awd"][3], rate(a)))] for a in (lo, ORDER[N//2], hi_)]
guide("ev-electric-bill", f"What an EV adds to your electric bill: {1000*T[HEAD][3]/100:.0f} kWh a month for a Model Y", f"A Model Y Long Range AWD adds about {1000*T[HEAD][3]/100:.0f} kWh a month to your bill for 1,000 miles. That's {m(month(T[HEAD][3], US_C/100))} at the US average, {m(month(T[HEAD][3], rate(lo)))} to {m(month(T[HEAD][3], rate(hi_)))} by state.",
 "What an EV adds<br>to your power bill", f"about {1000*T[HEAD][3]/100:.0f} kWh a month for a Model Y",
 f'''<p class="lead"><b>{1000*T[HEAD][3]/100:.0f} kWh a month.</b> That's what 1,000 miles in a {T[HEAD][1]} adds to your meter, using the EPA's {T[HEAD][3]:.1f} kWh per 100 miles. The EPA number is measured at the wall, so charging losses are already in it. At the US average of {US_C:.2f}¢ that's {m(month(T[HEAD][3], US_C/100))} more on your bill.</p>
{stats([(f"{1000*T[HEAD][3]/100:.0f} kWh", "Model Y, 1,000 mi"), (m(month(T[HEAD][3], US_C/100)), "at the US average"), (f"{1000*T['cybertruck-awd'][3]/100:.0f} kWh", "Cybertruck, 1,000 mi"), (m(month(T['cybertruck-awd'][3], US_C/100)), "Cybertruck at the US average")])}
<a class="pill w cta" href="/calculator">Put in your own miles</a>
<h2 class="h2s">kWh added per month<span>By trim and miles driven.</span></h2>
{table(["Trim", "500 mi", "1,000 mi", "1,500 mi"], rows)}
<h2 class="h2s">What that costs<span>Cheapest, middle and priciest state, 1,000 mi.</span></h2>
{table(["State", "¢/kWh", "Model Y LR AWD", "Cybertruck"], cost)}
<p class="txt"><b>Spotting it on the bill.</b> Most homes use several hundred kWh a month before an EV, so a Model Y can be a large share of the jump in your first bill. If your utility has tiered pricing, those extra kWh can land in a pricier tier, so the real cost per kWh can sit above your state's average. If it offers a time-of-use or EV plan, charging overnight is where the savings are.</p>''')

# 2 hybrid
m3 = T["model-3-standard-rwd"]
res = []
for a in ORDER:
    ev100 = per100(m3[3], rate(a)); h100 = gas100(hy[1], S[a]["gas"]["usd"])
    res.append((a, ev100, h100, (h100 - ev100) * 120))
hyw = [x for x in res if x[3] < 0]
rows = [[f'<a href="/ev-cost/{slug(a)}">{S[a]["name"]}</a>', m2(ev), m2(h), ("+" if d >= 0 else "-") + m(abs(d))] for a, ev, h, d in sorted(res, key=lambda x: -x[3])]
best = max(res, key=lambda x: x[3])
guide("tesla-vs-hybrid-fuel-cost", f"Tesla vs a 51 MPG hybrid: who's cheaper to fuel in {N - len(hyw)} of {N} states", f"A Model 3 Standard costs less to charge than a 51 MPG Camry Hybrid costs to fuel in {N - len(hyw)} of {N} states. The hybrid wins in {', '.join(S[x[0]]['name'] for x in hyw) or 'none'}. EIA {MONTH} and {GWEEK} prices.",
 "Tesla vs a hybrid", f"the Tesla wins in {N - len(hyw)} of {N} states",
 f'''<p class="lead"><b>{N - len(hyw)} of {N}.</b> That's how many states make a 2026 Model 3 Standard RWD ({m3[3]:.1f} kWh per 100 mi, EPA) cheaper to fuel than a 51 MPG Camry Hybrid at home electricity and local gas prices. {"The hybrid wins in " + ", ".join(f'<a class="lnk" href="/ev-cost/{slug(x[0])}">{S[x[0]]["name"]}</a>' for x in hyw) + ", where electricity is pricey enough to erase the gap." if hyw else "The hybrid doesn't win anywhere."} A 30 MPG gas car makes any EV look good. The best hybrid is the honest test.</p>
{stats([(str(N - len(hyw)), "states where the Tesla is cheaper"), (m((best[3])), f"most saved per year, {S[best[0]]['name']}"), (m2(per100(m3[3], US_C/100)), "Model 3 per 100 mi, US avg"), (m2(gas100(hy[1], US_G)), "Camry Hybrid per 100 mi, US avg")])}
<a class="pill w cta" href="/calculator?ev=model-3-standard-rwd">Compare with your own rates</a>
<h2 class="h2s">State by state<span>Fuel only, 12,000 miles a year.</span></h2>
{table(["State", "Model 3 / 100 mi", "Hybrid / 100 mi", "Tesla saves / yr"], rows)}
<p class="txt">EIA has no weekly gas series for most states, so those use their region's average, and each state page says which. Hawaii and Alaska use the West Coast (less California) average, so check your local pump price before you trust the hybrid's win there.</p>
<p class="txt">Fuel is only one line. Insurance, payments and maintenance usually matter more, and the <a class="lnk" href="/calculator">calculator</a> has fields for all three.</p>''')

# 3 level 1 vs 2
day = MI * 12 / 365
lv = [("120V outlet (Level 1, 12A)", 1.44), ("Level 2, 32A", 32 * 0.24), ("Level 2, 40A", 40 * 0.24), ("Level 2, 48A", 48 * 0.24)]
rows = [[t[1]] + [f"{kw*0.9/(t[3]/100):.0f} mi" for _, kw in lv] for t in TRIMS if t[5]]
hrs = lambda h: f"{h:.1f} hr" if h >= 1 else f"{round(h*60/5)*5:.0f} min"
eY = T[HEAD][3]
guide("level-1-vs-level-2-charging", f"Level 1 vs Level 2 charging: {hrs(day/(1.44*0.9/(eY/100)))} vs {hrs(day/(48*0.24*0.9/(eY/100)))} a night for a Model Y", f"A wall outlet adds about {1.44*0.9/(eY/100):.0f} miles an hour to a Model Y, so 1,000 miles a month needs {hrs(day/(1.44*0.9/(eY/100)))} plugged in every night. A 48A Level 2 charger needs {hrs(day/(48*0.24*0.9/(eY/100)))}. Every trim listed.",
 "Level 1 vs Level 2", "hours plugged in, every night",
 f'''<p class="lead"><b>{hrs(day/(1.44*0.9/(eY/100)))} vs {hrs(day/(48*0.24*0.9/(eY/100)))}.</b> That's how long a {T[HEAD][1]} has to sit plugged in each night to cover {MI:,} miles a month (about {day:.0f} miles a day): on a regular 120V outlet, then on a 48A Level 2 charger.</p>
{stats([(f"{1.44*0.9/(eY/100):.0f} mi/hr", "120V outlet, Model Y"), (f"{48*0.24*0.9/(eY/100):.0f} mi/hr", "48A Level 2, Model Y"), (f"{day:.0f} mi", "a day at 1,000 a month"), (hrs(day/(1.44*0.9/(eY/100))), "on 120V, every night")])}
<a class="pill w cta" href="/calculator">Check your own daily miles</a>
<h2 class="h2s">Miles added per hour<span>By trim and charger.</span></h2>
{table(["Trim", "120V", "32A", "40A", "48A"], rows)}
<p class="txt"><b>How these are worked out.</b> Power is amps times 240V (120V for the outlet), times about 90% for charging losses, divided by the car's EPA energy use per mile. Real numbers wobble with temperature and battery level.</p>
<p class="txt"><b>The car sets the ceiling.</b> A 48A charger only helps if the car's onboard charger takes 48A. Some trims accept less, so check your car's spec before paying for the bigger install.</p>
<p class="txt"><b>When 120V is enough.</b> If you drive under about 30 miles a day and park for 10+ hours, a plain outlet keeps up for a Model 3 or Model Y. A Cybertruck needs {T['cybertruck-awd'][3]/eY:.1f}x the energy, so it struggles on 120V.</p>''')

# 4 breaker
rows = [[f"{a}A", f"{int(a*1.25)}A", f"{a*0.24:.1f} kW", f"{a*0.24*0.9/(eY/100):.0f} mi"] for a in (16, 24, 32, 40, 48)]
guide("ev-charger-breaker-size", "EV charger breaker size: 40A needs 50A, 48A needs 60A", "An EV charger counts as a continuous load, so the breaker must be at least 125% of the charging current: 32A on a 40A breaker, 40A on 50A, 48A on 60A. Table with kW and miles per hour.",
 "What breaker does<br>an EV charger need?", "125% of the charging amps",
 f'''<p class="lead"><b>Breaker = charging amps x 1.25.</b> The National Electrical Code (NFPA 70, Article 625) treats EV charging as a continuous load, so the circuit has to be rated for 125% of what the charger draws. A 48A charger needs a 60A breaker. A 40A charger needs 50A.</p>
{stats([("60A", "breaker for a 48A charger"), ("50A", "breaker for a 40A charger"), ("40A", "most you can pull from a 14-50 outlet"), (f"{48*0.24:.1f} kW", "48A at 240V")])}
<h2 class="h2s">Amps, breaker, speed<span>Speed shown for a {T[HEAD][1]}.</span></h2>
{table(["Charging", "Breaker", "Power", "Miles / hr"], rows)}
<p class="txt"><b>Panel space comes first.</b> A 60A circuit is a big ask for an older 100A panel. If yours is tight, a charger set to 32A or 40A, or one with load management, can avoid a panel upgrade. Most hardwired chargers, including the ChargePoint and Emporia picks below, let the installer set the current to match the breaker.</p>
<p class="txt"><b>Who decides.</b> Your electrician and local code do, not this page. Wire size depends on distance and conduit, and many towns want a permit. Use the table to ask for the right quote.</p>''')

# 5 14-50
guide("nema-14-50-vs-hardwired", "NEMA 14-50 outlet or hardwired EV charger? 40A vs 48A", "A NEMA 14-50 outlet on a 50A breaker tops out at 40A of charging. Hardwiring a charger on a 60A circuit allows 48A. Here's the speed difference for every Tesla and when each choice makes sense.",
 "NEMA 14-50 or hardwired?", "40A max vs 48A",
 f'''<p class="lead"><b>40A vs 48A.</b> A NEMA 14-50 outlet sits on a 50A breaker, and the 125% rule caps charging at 40A ({40*0.24:.1f} kW). Hardwiring on a 60A circuit allows 48A ({48*0.24:.1f} kW). For a {T[HEAD][1]} that's about {40*0.24*0.9/(eY/100):.0f} vs {48*0.24*0.9/(eY/100):.0f} miles added per hour.</p>
{stats([(f"{40*0.24*0.9/(eY/100):.0f} mi/hr", "14-50 plug-in, Model Y"), (f"{48*0.24*0.9/(eY/100):.0f} mi/hr", "hardwired 48A, Model Y"), (hrs(day/(40*0.24*0.9/(eY/100))), "a night for 1,000 mi/mo on 40A"), (hrs(day/(48*0.24*0.9/(eY/100))), "on 48A")])}
<p class="txt"><b>Pick the outlet if</b> you already have a 14-50 in the garage, you rent, or you might take the charger with you. The Grizzl-E pick below plugs straight in. Overnight, 40A refills a typical day's driving in under an hour.</p>
<p class="txt"><b>Hardwire if</b> you're running a new circuit anyway, the car accepts 48A, or the charger is outside. Fewer connections to wear out, and a hardwired unit can be set to whatever your panel can spare.</p>
<p class="txt"><b>One gotcha.</b> Newer editions of the electrical code require GFCI protection on 240V garage outlets. Some chargers have their own ground fault detection and can nuisance trip a GFCI breaker. Ask your electrician which way your local code goes before you pick.</p>
<p class="txt">Either way the speed gap matters less than people think: at {day:.0f} miles a day, both finish long before morning. <a class="lnk" href="/guides/ev-charger-breaker-size">Breaker sizes for every charger</a>.</p>''')

# 6 yoy
yo = sorted(ORDER, key=lambda a: -pct(S[a]["cents"], S[a]["cents_prior"]))
up = [a for a in yo if S[a]["cents"] > S[a]["cents_prior"]]
rows = [[f'<a href="/ev-cost/{slug(a)}">{S[a]["name"]}</a>', f'{S[a]["cents_prior"]:.2f}¢', f'{S[a]["cents"]:.2f}¢', f'{pct(S[a]["cents"], S[a]["cents_prior"]):+.1f}%', ("+" if S[a]["cents"] >= S[a]["cents_prior"] else "-") + m2(abs(month(eY, rate(a)) - month(eY, S[a]["cents_prior"]/100)))] for a in yo]
top = yo[0]
guide("electricity-price-change-by-state", f"Electricity prices rose in {len(up)} of {N} states: {PRIOR} to {MONTH}", f"Home electricity got pricier in {len(up)} of {N} states from {PRIOR} to {MONTH} (EIA). The US average went from {R['us_cents_prior']:.2f}¢ to {US_C:.2f}¢. Biggest jump: {S[top]['name']}, {pct(S[top]['cents'], S[top]['cents_prior']):+.1f}%. What it does to an EV's monthly cost.",
 "Where charging got pricier", f"{len(up)} of {N} states, {PRIOR} to {MONTH}",
 f'''<p class="lead"><b>{pct(US_C, R["us_cents_prior"]):+.1f}% in a year.</b> The US average home electricity price went from {R["us_cents_prior"]:.2f}¢ in {PRIOR} to {US_C:.2f}¢ in {MONTH} (EIA). It rose in {len(up)} of {N} states. The biggest jump was {S[top]["name"]}, {S[top]["cents_prior"]:.2f}¢ to {S[top]["cents"]:.2f}¢ ({pct(S[top]["cents"], S[top]["cents_prior"]):+.1f}%).</p>
{stats([(f"{pct(US_C, R['us_cents_prior']):+.1f}%", "US average, year over year"), (str(len(up)), f"of {N} states went up"), (f"{pct(S[top]['cents'], S[top]['cents_prior']):+.1f}%", S[top]["name"]), (m2(month(eY, US_C/100) - month(eY, R['us_cents_prior']/100)), "more a month, Model Y, US avg")])}
<h2 class="h2s">Every state, biggest rise first<span>Monthly change for a {T[HEAD][1]}, {MI:,} mi.</span></h2>
{table(["State", PRIOR, MONTH, "Change", "Model Y / mo"], rows)}
<p class="txt">These are July numbers, peak air conditioning season, and summer prices run higher than the yearly average in most states. Compare July to July, not July to your January bill.</p>''')

# EV vs gas matchups, city pages, hub and the calculator vehicle list (added 2026-10-20)
exec(open(os.path.join(ROOT, "scripts", "gen_compare.py"), encoding="utf-8").read())

# URL list
open(os.path.join(ROOT, "data", "pages.txt"), "w").write("\n".join(BASE + p for p, _ in pages) + "\n")
print(len(pages), "pages generated")
