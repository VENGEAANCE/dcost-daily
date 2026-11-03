# EV vs gas comparison pages. Not run on its own: gen_pages.py exec()s this file at the end, so it shares
# page(), write(), the helpers and the same rates.json/EPA data. Writes compare/<pair>.html, compare/index.html,
# ev-vs-gas/<city>.html and vehicles.js (the calculator's vehicle list). Every number comes from
# data/epa.json (EPA fueleconomy.gov) and data/rates.json (EIA). No em-dashes (write() refuses them).
import sys as _sys
_sys.path.insert(0, os.path.join(ROOT, "scripts"))
from vehicles import EV as VEV, GAS as VGAS, PAIRS, CITIES, NAMES
EPA = json.load(open(os.path.join(ROOT, "data", "epa.json")))["vehicles"]
PSRC = R["premium_source"]; US_P = R["us_premium"]
# Why this rival and this version. Only facts that are visible in the EPA listing for the 2026 model year.
WHY = {
 "tesla-model-y-vs-toyota-rav4": "Every 2026 RAV4 listed on fueleconomy.gov is a hybrid, so this is the toughest gas rival a Model Y can draw. Both sides here are all-wheel drive.",
 "tesla-model-y-vs-honda-cr-v": "This is the regular 1.5L turbo CR-V with all-wheel drive, the version without a hybrid system. The CR-V Hybrid is in the versions table below.",
 "tesla-model-y-vs-lexus-rx": "The EPA lists premium gasoline for the RX 350, so the gas side uses EIA's premium price, not regular.",
 "tesla-model-3-vs-toyota-camry": "Every 2026 Camry listed on fueleconomy.gov is a hybrid, and the front-drive LE is the most efficient one. If the Model 3 beats this car, it beats almost any sedan.",
 "tesla-model-3-vs-honda-accord": "This is the regular 1.5L turbo Accord. The Accord Hybrid gets far better mileage, and it's in the versions table below.",
 "tesla-model-3-vs-honda-civic": "This is the regular 2.0L Civic sedan, the cheapest car on this list to buy. The Civic Hybrid is in the versions table below.",
 "tesla-model-3-vs-bmw-3-series": "The Model 3 Premium AWD against the all-wheel-drive 330i. The EPA lists premium gasoline for the BMW, so the gas side uses EIA's premium price.",
 "tesla-cybertruck-vs-ford-f-150": "This is the 4WD F-150 with the 3.5L EcoBoost V6. Ford's 2.7L, the 5.0L V8 and the PowerBoost hybrid are in the versions table below.",
 "tesla-cybertruck-vs-chevy-silverado": "This is the 4WD Silverado with the 5.3L V8. The 2.7L turbo four is in the versions table below.",
 "tesla-cybertruck-vs-ram-1500": "This is the 4WD Ram 1500 with the 3.0L straight six. The 3.6L V6 eTorque is in the versions table below.",
 "tesla-model-s-vs-bmw-5-series": "The Model S against the 540i xDrive, BMW's six-cylinder all-wheel-drive 5 Series. The EPA lists premium gasoline for it, so the gas side uses EIA's premium price.",
 "tesla-model-s-vs-mercedes-e-class": "The Model S against the E 350 4MATIC. The EPA lists premium gasoline for it, so the gas side uses EIA's premium price.",
 "tesla-model-x-vs-bmw-x5": "The Model X against the X5 xDrive40i. The EPA lists premium gasoline for the X5, so the gas side uses EIA's premium price.",
 "tesla-model-x-vs-honda-pilot": "Both seat up to seven. This is the all-wheel-drive Pilot with its 3.5L V6.",
}
def V(sl): return EPA[sl]
def ekwh(sl, k="combE"): return float(V(sl)[k])
def mpg(sl, k="comb08"): return float(V(sl)[k])
def prem(sl): return V(sl)["fuelType1"].startswith("Premium")
def glab(sl): return VGAS[sl][0]
def elab(sl): return VEV[sl][0]
def gprice(sl, ab=None, city=None):
    k = "premium" if prem(sl) else "usd"
    if city: return R["cities"][city][k]
    return S[ab]["gas"][k] if ab else (US_P if prem(sl) else US_G)
def evmo(sl, r): return MI * ekwh(sl) / 100 * r
def gasmo(sl, g): return MI / mpg(sl) * g
def sgn(x): return ("+" if x >= 0 else "-") + m(abs(x))
def fuelword(sl): return "premium" if prem(sl) else "regular"
def gsrc(sl): return PSRC if prem(sl) else GSRC
def epa_link(i, txt="fueleconomy.gov"): return f'<a class="lnk" href="https://www.fueleconomy.gov/feg/PowerSearch.do?action=noform&amp;path=1&amp;year1=2026&amp;year2=2026&amp;id={i}">{txt}</a>'
def calc_pair(ev, gs, ab=None):
    q = ["ev=" + ev, "gas=" + gs] + (["state=" + ab.lower()] if ab else [])
    return "/calculator?" + "&amp;".join(q)
def bars(rows, cap):
    """Two or three horizontal bars, $ a month. rows = [(label, value, color)]. Sized for a 390px phone."""
    W = 360; mx = max(v for _, v, _ in rows) or 1; y = 0; out = []
    for lab, v, col in rows:
        w = max(4, v / mx * (W - 70))
        out.append(f'<text x="0" y="{y+12}" fill="#ffffff99" font-size="12">{e(lab)}</text><rect x="0" y="{y+18}" width="{w:.1f}" height="22" rx="6" fill="{col}"/><text x="{w+8:.1f}" y="{y+34}" fill="#fff" font-size="14" font-weight="500">{m(v)}</text>')
        y += 52
    return f'<figure class="strip"><svg viewBox="0 0 {W} {y}" role="img" aria-label="{e(cap)}">{"".join(out)}</svg><figcaption>{cap}</figcaption></figure>'

def src_note_pair(gs_list):
    p = any(prem(g) for g in gs_list)
    extra = f' Premium: week of {GWEEK}, <a href="{PSRC}">EIA weekly retail premium gasoline by area</a>.' if p else ""
    return src_note().replace("</p>", f"{extra} Vehicle ratings: 2026 model year, <a href=\"https://www.fueleconomy.gov/ws/rest/vehicle/\">fueleconomy.gov web services</a>.</p>")

# ---------- pair pages ----------
pair_rows = []
for psl, ev, gs, alts in PAIRS:
    en, gn = NAMES[psl]; es, gsh = VEV[ev][1], VGAS[gs][1]
    r = US_C / 100; g = gprice(gs)
    em, gm = evmo(ev, r), gasmo(gs, g); sv = gm - em
    be_gas = ekwh(ev) / 100 * r * mpg(gs)            # $/gal where they tie at the US electricity price
    be_c = (g / mpg(gs)) / (ekwh(ev) / 100) * 100      # cents/kWh where they tie at the US gas price
    pair_rows.append((psl, en, gn, ev, gs, em, gm, sv))
    # state table
    st = []
    for ab in ORDER:
        a_em, a_gm = evmo(ev, rate(ab)), gasmo(gs, gprice(gs, ab)); st.append((ab, a_em, a_gm, (a_gm - a_em) * 12))
    st.sort(key=lambda x: -x[3]); wins = [x for x in st if x[3] > 0]; loses = [x for x in st if x[3] <= 0]
    best, worst = st[0], st[-1]
    srows = [[f'<a href="/ev-cost/{slug(a)}">{S[a]["name"]}</a>', m(x), m(y), sgn(z)] for a, x, y, z in st]
    if loses:
        def _lose(a):
            gg = gprice(gs, a); tie_c = (gg / mpg(gs)) / (ekwh(ev) / 100) * 100
            where = "" if S[a]["gas"]["own"] else f", using the {S[a]['gas']['area']} gas average"
            return f'{S[a]["name"]} ({S[a]["cents"]:.2f}¢ power vs {m2(gg)} gas{where}; power would need to fall to {tie_c:.1f}¢ to tie)'
        lose_txt = f'The {gsh} is cheaper to fuel in {len(loses)} of {N}: ' + "; ".join(_lose(a) for a, *_ in loses) + ". A utility EV or time-of-use plan can sometimes get you under that."
    else:
        lose_txt = f'It wins in all {N}, even {S[worst[0]]["name"]} at {S[worst[0]]["cents"]:.2f}¢ per kWh.'
    # city / highway / combined, US average prices
    modes = [("City", "cityE", "city08"), ("Highway", "highwayE", "highway08"), ("Combined (55/45)", "combE", "comb08")]
    mrows, gaps = [], []
    for lab, ek, gk in modes:
        e100 = ekwh(ev, ek) * r; g100 = 100 / mpg(gs, gk) * g; gaps.append((lab, g100 - e100, ekwh(ev, ek), mpg(gs, gk)))
        mrows.append([lab, f'{ekwh(ev, ek):.1f} kWh, {m2(e100)}', f'{mpg(gs, gk):.0f} MPG, {m2(g100)}', sgn(g100 - e100).replace("$", "$") ])
    mrows = [[a, b, c, ("+" if g100e >= 0 else "-") + m2(abs(g100e))] for (a, b, c, _), (_, g100e, _, _) in zip(mrows, gaps)]
    wide = max(gaps[:2], key=lambda x: x[1]); narrow = min(gaps[:2], key=lambda x: x[1])
    mode_txt = (f"The gap is widest in {wide[0].lower()} driving: the {es} uses {wide[2]:.1f} kWh per 100 miles there and the {gsh} gets {wide[3]:.0f} MPG. " +
                (f"In {narrow[0].lower()} driving it narrows to {m2(narrow[1])} per 100 miles." if narrow[1] >= 0 else f"In {narrow[0].lower()} driving the {gsh} is {m2(-narrow[1])} per 100 miles cheaper."))
    if wide[0] == "City" and mpg(gs, "city08") > mpg(gs, "highway08"):
        mode_txt += f" Hybrids do their best work in stop-and-go traffic, yet the {es} still pulls further ahead there, because regenerative braking helps it too."
    elif wide[0] == "City":
        mode_txt += f" Stop-and-go traffic is where a gas engine wastes the most, so city drivers save the most by switching."
    # versions table: gas versions, then EV siblings
    vrows = []
    for v in [gs] + alts:
        vg = gasmo(v, gprice(v)); vrows.append([glab(v) + (" (premium)" if prem(v) else ""), f"{mpg(v):.0f}", m(vg), sgn((vg - em) * 12)])
    sibs = [k for k in VEV if VEV[k][1] == es]
    erows = [[elab(k), f"{ekwh(k):.1f}", m(evmo(k, r)), sgn((gm - evmo(k, r)) * 12)] for k in sibs]
    # range, home charging, CO2
    rng = int(V(ev)["range"]); mph48 = 48 * 0.24 * 0.9 / (ekwh(ev) / 100); co2 = float(V(gs)["co2TailpipeGpm"])
    fc_e, fc_g = int(V(ev)["fuelCost08"]), int(V(gs)["fuelCost08"])
    sbs = f"https://www.fueleconomy.gov/feg/Find.do?action=sbs&amp;id={V(ev)['id']}&amp;id={V(gs)['id']}"
    head = (f"<b>{m(sv*12)} a year.</b> That's the fuel saving for a 2026 {elab(ev)} over a 2026 {glab(gs)} at {MI*12:,} miles a year on US average prices: "
            f"<b>{m(em)}</b> a month to charge at home vs <b>{m(gm)}</b> in gas.") if sv > 0 else (
            f"<b>The {gsh} is {m(-sv*12)} a year cheaper to fuel.</b> At {MI*12:,} miles a year on US average prices, a 2026 {glab(gs)} costs {m(gm)} a month in gas vs {m(em)} to charge a 2026 {elab(ev)} at home.")
    tie = (f"Gas would have to fall to <b>{m2(be_gas)}</b> a gallon for the {gsh} to tie, or home electricity climb to <b>{be_c:.1f}¢</b> per kWh."
           if sv > 0 else f"Electricity would need to drop to {be_c:.1f}¢ per kWh for the {es} to tie.")
    body = f'''<p class="lead">{head} Electricity is {US_C:.2f}¢ per kWh ({MONTH}, EIA) and {fuelword(gs)} gas is {m2(g)} a gallon (week of {GWEEK}, EIA). {tie}</p>
{stats([(m(em), f"{es}, charging a month"), (m(gm), f"{gsh}, {fuelword(gs)} gas a month"), (sgn(sv*12) if sv < 0 else m(sv*12), "saved a year" if sv > 0 else "a year, Tesla costs more"), (m2(be_gas), f"gas price where they tie")])}
{bars([(f"2026 {elab(ev)}, {ekwh(ev):.1f} kWh/100 mi", em, "#fff"), (f"2026 {glab(gs)}, {mpg(gs):.0f} MPG", gm, "#ffffff4d")], f"Fuel a month, {MI:,} miles, US average prices. Sources: EPA, EIA.")}
<p class="txt">{WHY[psl]}</p>
<a class="pill w cta" href="{calc_pair(ev, gs)}">Run these two with your miles and rates</a>
<h2 class="h2s">State by state<span>Fuel a month, {MI:,} miles. Biggest saving first.</span></h2>
<p class="txt">The {es} saves the most in {S[best[0]]["name"]}, {m(best[3])} a year, where cheap power meets {m2(gprice(gs, best[0]))} gas. {lose_txt}</p>
{table(["State", es, gsh, "Saves / yr"], srows)}
<p class="txt">Electricity is each state's {MONTH} residential average. Gas is the state's own EIA weekly series where one exists and its region's average otherwise; each state page says which.</p>
<h2 class="h2s">City vs highway<span>Cost per 100 miles at US average prices.</span></h2>
{table(["Driving", es, gsh, "Tesla saves"], mrows)}
<p class="txt">{mode_txt} EPA's combined rating weights city 55% and highway 45%, which is what every other number on this page uses.</p>
<h2 class="h2s">Which version you buy matters<span>2026 EPA ratings, {MI:,} miles a month, US average prices.</span></h2>
{table(["Gas version", "MPG", "Gas / mo", "Saves / yr"], vrows)}
{table([f"{es} version", "kWh/100 mi", "Charge / mo", "Saves / yr"], erows) if len(erows) > 1 else ""}
<h2 class="h2s">Beyond the fuel bill<span>Range, home charging, tailpipe.</span></h2>
<p class="txt"><b>Range.</b> The EPA rates the {elab(ev)} at {rng} miles on a charge. On a 48A home charger it adds about {mph48:.0f} miles an hour, so a typical day's driving (about {MI*12/365:.0f} miles) goes back in {hrs(MI*12/365/mph48)}. <a class="lnk" href="/guides/level-1-vs-level-2-charging">Level 1 vs Level 2</a>.</p>
<p class="txt"><b>Tailpipe.</b> The {gsh} puts out {co2:.0f} grams of CO2 per mile (EPA), about {co2*MI/1000:.0f} kg over {MI:,} miles. The {es} has no tailpipe; its emissions depend on how your grid makes power.</p>
<p class="txt"><b>Second opinion.</b> fueleconomy.gov's own yearly fuel cost estimate, at 15,000 miles and its national prices, is {m(fc_e)} for the {es} and {m(fc_g)} for the {gsh}. <a class="lnk" href="{sbs}">See EPA's side by side</a>.</p>
<p class="txt"><b>What this leaves out.</b> Purchase price, insurance and maintenance usually move the total more than fuel does, and Supercharging on road trips costs more than home power. The <a class="lnk" href="{calc_pair(ev, gs)}">calculator</a> has fields for payment, insurance and maintenance.</p>
{links_block(f"More {es} matchups", [(f"/compare/{p[0]}", f"{NAMES[p[0]][0]} vs {NAMES[p[0]][1]}") for p in PAIRS if p[1].split("-")[1] == ev.split("-")[1] and p[0] != psl] + [(f"/tesla/{ev}", f"Cost to charge a {elab(ev).replace('Tesla ', '')} in every state")] if ev in T and T[ev][5] else [(f"/compare/{p[0]}", f"{NAMES[p[0]][0]} vs {NAMES[p[0]][1]}") for p in PAIRS if p[1].split("-")[1] == ev.split("-")[1] and p[0] != psl])}
{links_block("Other matchups", [("/compare/", "Every EV vs gas matchup")] + [(f"/compare/{p[0]}", f"{NAMES[p[0]][0]} vs {NAMES[p[0]][1]}") for p in PAIRS if p[1].split("-")[1] != ev.split("-")[1]][:5])}
{links_block("Gas prices by city", [(f"/ev-vs-gas/{c}", f"EV vs gas in {CITIES[c][0]}") for c in list(CITIES)[:5]])}
{src_note_pair([gs] + alts)}'''
    title = f"{en} vs {gn} fuel cost: " + (f"{m(sv*12)} a year saved" if sv > 0 else f"{gn} {m(-sv*12)} a year cheaper") + f" ({MONTH} prices) · dcost daily"
    desc = (f"A 2026 {elab(ev).replace('Tesla ', '')} costs {m(em)} a month to charge vs {m(gm)} in gas for a {mpg(gs):.0f} MPG {glab(gs)}, 1,000 miles at US average prices. "
            f"State by state, city vs highway, every version. EPA and EIA data.")
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "EV vs gas", "item": BASE + "/compare/"}, {"@type": "ListItem", "position": 2, "name": f"{en} vs {gn}", "item": f"{BASE}/compare/{psl}"}]}
    h1b = (f"{m(sv)} a month cheaper to fuel" if sv > 0 else f"the {gsh} is {m(-sv)} a month cheaper")
    write(f"/compare/{psl}", f"compare/{psl}.html", page(f"/compare/{psl}", title, desc, f"{en}<br>vs {gn}", h1b, body, on="/compare/", jsld=ld, eff=ekwh(ev)))

# ---------- city pages ----------
city_rows = []
ref = PAIRS[0]  # Model Y vs RAV4: best-selling Tesla vs the toughest gas rival
for csl, (cn, ab) in CITIES.items():
    c = R["cities"][cn]; st_g = S[ab]["gas"]; r = rate(ab)
    em, gm = evmo(ref[1], r), gasmo(ref[2], c["usd"]); city_rows.append((csl, cn, ab, c, em, gm, (gm - em) * 12))
for csl, cn, ab, c, em, gm, svy in city_rows:
    st_g = S[ab]["gas"]; r = rate(ab); nm = S[ab]["name"]; d = c["usd"] - st_g["usd"]
    if st_g["own"]: gas_cmp = f"{cn}'s regular price is {m2(abs(d))} {'above' if d >= 0 else 'below'} {nm}'s statewide average of {m2(st_g['usd'])}, which is what the <a class=\"lnk\" href=\"/ev-cost/{slug(ab)}\">{nm} page</a> uses."
    else: gas_cmp = f"{cn}'s regular price is {m2(abs(d))} {'above' if d >= 0 else 'below'} the {st_g['area']} average of {m2(st_g['usd'])}, which is what the <a class=\"lnk\" href=\"/ev-cost/{slug(ab)}\">{nm} page</a> uses because EIA has no weekly series for {nm}."
    rows = []
    for psl, ev, gs, _ in PAIRS:
        a, b = evmo(ev, r), gasmo(gs, c["premium" if prem(gs) else "usd"])
        rows.append([f'<a href="/compare/{psl}">{NAMES[psl][0].replace("Tesla ", "")} vs {NAMES[psl][1]}</a>', m(a), m(b), sgn((b - a) * 12)])
    others = [[f'<a href="/ev-vs-gas/{x[0]}">{x[1]}</a>' if x[0] != csl else f"<b>{x[1]}</b>", m2(x[3]["usd"]), m2(x[3]["premium"]), f'{S[x[2]]["cents"]:.2f}¢', m(x[6])] for x in sorted(city_rows, key=lambda x: -x[6])]
    rk = [x[0] for x in sorted(city_rows, key=lambda x: -x[6])].index(csl) + 1
    body = f'''<p class="lead"><b>{m(svy)} a year.</b> That's what a 2026 Model Y Long Range AWD saves over a 2026 RAV4 Hybrid AWD in {cn} at {MI*12:,} miles a year: {m(em)} a month to charge on {nm}'s average home electricity price ({S[ab]["cents"]:.2f}¢ per kWh, {MONTH}) vs {m(gm)} in gas at {cn}'s own regular price of {m2(c["usd"])} (EIA, week of {GWEEK}). That's {ordinal(rk)} of the {len(CITIES)} cities EIA tracks.</p>
{stats([(m2(c["usd"]), f"regular in {cn}"), (m2(c["premium"]), f"premium in {cn}"), (f'{S[ab]["cents"]:.2f}¢', f"{nm} power, statewide"), (m(em), "Model Y LR AWD, a month")])}
<p class="txt"><b>Gas is local, power here is statewide.</b> {gas_cmp} EIA doesn't publish home electricity prices by city, so the electricity side is the {nm} statewide average. Your utility's rate can sit well above or below it; divide your bill's total by the kWh used to get yours.</p>
<a class="pill w cta" href="/calculator?state={ab.lower()}">Run your own numbers with {nm} prices</a>
<h2 class="h2s">Every matchup in {cn}<span>Fuel only, {MI:,} miles a month. Premium cars priced at {cn} premium.</span></h2>
{table(["Matchup", "Tesla / mo", "Gas / mo", "Saves / yr"], rows)}
<h2 class="h2s">The {len(CITIES)} cities EIA tracks<span>Model Y LR AWD vs RAV4 Hybrid AWD, saving a year.</span></h2>
{table(["City", "Regular", "Premium", "State power", "Saves / yr"], others)}
<p class="txt">These are the only US cities with their own EIA weekly gas price. For anywhere else, use your <a class="lnk" href="/ev-cost/">state page</a>.</p>
{links_block("Go deeper", [(f"/ev-cost/{slug(ab)}", f"Every Tesla trim in {nm}"), ("/compare/", "Every EV vs gas matchup, US average"), ("/chargers", "Home charger picks")])}
<p class="note">Gas: regular and premium retail for {cn}, week of {GWEEK}, <a href="{GSRC}">EIA weekly retail gasoline</a> and <a href="{PSRC}">premium</a>. Electricity: {nm} residential average, {MONTH}, <a href="{ESRC}">EIA Electric Power Monthly Table 5.6.A</a>; EIA has no city-level series. Efficiency: EPA 2026 ratings from <a href="https://www.fueleconomy.gov">fueleconomy.gov</a>. Monthly figures use {MI:,} miles.</p>'''
    title = f"EV vs gas in {cn}: Model Y saves {m(svy)} a year at {m2(c['usd'])} gas · dcost daily"
    desc = f"{cn} regular gas is {m2(c['usd'])} (EIA, week of {GWEEK}). A Model Y costs {m(em)} a month to charge on {nm} power vs {m(gm)} in gas for a RAV4 Hybrid. All 14 Tesla vs gas matchups at {cn} prices."
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "EV vs gas", "item": BASE + "/compare/"}, {"@type": "ListItem", "position": 2, "name": cn, "item": f"{BASE}/ev-vs-gas/{csl}"}]}
    write(f"/ev-vs-gas/{csl}", f"ev-vs-gas/{csl}.html", page(f"/ev-vs-gas/{csl}", title, desc, f"EV vs gas<br>in {cn}", f"{m2(c['usd'])} gas, {S[ab]['cents']:.2f}¢ power", body, on="/compare/", jsld=ld, eff=ekwh(ref[1])))

# ---------- hub ----------
hr = sorted(pair_rows, key=lambda x: -x[7])
rows = [[f'<a href="/compare/{p}">{en.replace("Tesla ", "")} vs {gn}</a>', m(em), m(gm), sgn(sv * 12)] for p, en, gn, ev, gs, em, gm, sv in hr]
lo_p, hi_p = hr[-1], hr[0]
body = f'''<p class="lead"><b>{m(lo_p[7]*12)} to {m(hi_p[7]*12)} a year.</b> That's the fuel saving across {len(PAIRS)} Tesla vs gas matchups at {MI*12:,} miles a year on US average prices, from {lo_p[1].replace("Tesla ", "")} vs {lo_p[2]} to {hi_p[1].replace("Tesla ", "")} vs {hi_p[2]}. Each car is matched to the gas model people cross-shop it with, and hybrids are included where that's what the rival sells.</p>
{stats([(str(len(PAIRS)), "matchups"), (m(hi_p[7]*12), f"biggest saving, {hi_p[1].replace('Tesla ', '')} vs {hi_p[2]}"), (f"{US_C:.2f}¢", f"US power, {MONTH}"), (m2(US_G), f"US regular, week of {GWEEK}")])}
<a class="pill w cta" href="/calculator">Build your own matchup</a>
<h2 class="h2s">Every matchup<span>Fuel only, {MI:,} miles a month, US average. Biggest saving first.</span></h2>
{table(["Matchup", "Tesla / mo", "Gas / mo", "Saves / yr"], rows)}
<p class="txt">Trucks save the most because full-size pickups burn the most gas, even though the Cybertruck uses the most electricity of any Tesla. The closest calls are against hybrids. Every page has the state-by-state numbers, city vs highway, and the other versions of each car.</p>
{links_block("By city (local gas, state power)", [(f"/ev-vs-gas/{x[0]}", f"{x[1]}: {m2(x[3]['usd'])} gas, Model Y saves {m(x[6])} a year vs a RAV4 Hybrid") for x in sorted(city_rows, key=lambda x: -x[6])])}
{links_block("By state", [("/ev-cost/", f"All {N} states ranked")] + guide_links()[:2])}
{src_note_pair([p[4] for p in pair_rows])}'''
write("/compare/", "compare/index.html", page("/compare/", f"Tesla vs gas car fuel cost: {len(PAIRS)} matchups ({MONTH} prices) · dcost daily", f"Model Y vs RAV4, Model 3 vs Camry, Cybertruck vs F-150 and {len(PAIRS)-3} more. Fuel cost a month and a year at US average prices, from EPA ratings and EIA prices. {m(lo_p[7]*12)} to {m(hi_p[7]*12)} saved a year.", "Tesla vs gas", f"{len(PAIRS)} matchups, real prices", body, on="/compare/", eff=T[HEAD][3]))

# ---------- calculator vehicle list ----------
evl = [[f"2026 {VEV[k][0]}", round(ekwh(k), 1), V(k)["id"], k, VEV[k][1]] for k in VEV]
gl = [[f"2026 {VGAS[k][0]}", int(mpg(k)), V(k)["id"], k, 1 if prem(k) else 0, VGAS[k][1]] for k in VGAS]
gl.sort(key=lambda x: (x[3] != "toyota-camry-hybrid-le", x[0]))
open(os.path.join(ROOT, "vehicles.js"), "w").write("// Generated by scripts/gen_compare.py from data/epa.json (EPA fueleconomy.gov, 2026 model year). Do not edit by hand.\n// EV: [label, kWh/100mi, EPA id, slug, short name]. GAS: [label, MPG, EPA id, slug, premium 1/0, short name].\n"
    f"const EV={json.dumps(evl)};\nconst GAS={json.dumps(gl)};\n")
json.dump({"ev": {k: [VEV[k][0], VEV[k][1], round(ekwh(k), 1)] for k in VEV}, "gas": {k: [VGAS[k][0], VGAS[k][1], int(mpg(k)), 1 if prem(k) else 0] for k in VGAS},
           "states": {ab.lower(): S[ab]["name"] for ab in S}}, open(os.path.join(ROOT, "data", "vehicles.json"), "w"))
print("compare:", len(PAIRS), "pairs,", len(CITIES), "cities, hub, vehicles.js")
