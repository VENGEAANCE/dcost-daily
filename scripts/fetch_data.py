#!/usr/bin/env python3
"""Refresh data/rates.json from EIA (public domain). Run monthly when EIA posts a new
Electric Power Monthly (Table 5.6.A), then run gen_pages.py and deploy.
Electricity: residential average price by state, latest month and same month a year earlier.
Gas: EIA weekly retail regular gasoline by area. 9 states have their own series; every other
state uses its PADD region average, and the pages say so."""
import re, html, json, os, urllib.request, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 dcostdaily.com data refresh"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "ignore")
def cells(t):
    rows = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        c = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if c: rows.append(c)
    return rows
STATES = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}
PADD = {"New England (PADD 1A)":"CT ME MA NH RI VT","Central Atlantic (PADD 1B)":"DE DC MD NJ NY PA","Lower Atlantic (PADD 1C)":"FL GA NC SC VA WV",
        "Midwest (PADD 2)":"IL IN IA KS KY MI MN MO NE ND SD OH OK TN WI","Gulf Coast (PADD 3)":"AL AR LA MS NM TX",
        "Rocky Mountain (PADD 4)":"CO ID MT UT WY","West Coast less California":"AK AZ HI NV OR WA"}
OWN_GAS = {"California":"CA","Colorado":"CO","Florida":"FL","Massachusetts":"MA","Minnesota":"MN","New York":"NY","Ohio":"OH","Texas":"TX","Washington":"WA"}
def main():
    eu = "https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a"
    rows = cells(get(eu))
    hdr = next(r for r in rows if len(r) > 2 and re.match(r"[A-Z][a-z]+ \d{4}", r[1]))
    month, prior = hdr[1], hdr[2]
    byname = {r[0]: r for r in rows if len(r) > 2}
    elec = {}
    for ab, nm in STATES.items():
        r = byname[nm]; elec[ab] = {"cents": float(r[1]), "cents_prior": float(r[2])}
    us = byname["U.S. Total"]
    def areas(u):
        t = get(u); wk = re.findall(r'class="Series5">(\d\d/\d\d/\d\d)<', t)[-1]; a = {}
        for blk in t.split('class="DataStub1"')[1:]:
            name = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", blk[1:blk.index("</td>")]))).strip()
            vals = re.findall(r'class="(?:DataB|Current2)">([\d.]+)<', blk.split("DataHist")[0])
            if name and vals: a[name] = float(vals[-1])
        return wk, a
    gu = "https://www.eia.gov/dnav/pet/pet_pri_gnd_a_epmr_pte_dpgal_w.htm"
    pu = "https://www.eia.gov/dnav/pet/pet_pri_gnd_a_epmp_pte_dpgal_w.htm"  # premium, same areas (added 2026-10-20 for the BMW/Mercedes/Lexus comparisons)
    week, area = areas(gu)
    pweek, parea = areas(pu)
    assert pweek == week, f"regular week {week} vs premium week {pweek}"
    gas = {}
    for nm, ab in OWN_GAS.items(): gas[ab] = {"usd": area[nm], "premium": parea[nm], "area": nm, "own": True}
    for reg, sts in PADD.items():
        for ab in sts.split():
            if ab not in gas: gas[ab] = {"usd": area[reg], "premium": parea[reg], "area": reg, "own": False}
    # EIA's 10 city series. Electricity has no city series; city pages use the state average and say so.
    CITY = ["Boston", "Chicago", "Cleveland", "Denver", "Houston", "Los Angeles", "Miami", "New York City", "San Francisco", "Seattle"]
    cities = {c: {"usd": area[c], "premium": parea[c]} for c in CITY}
    m, d, y = week.split("/"); wk = datetime.date(2000 + int(y), int(m), int(d))
    out = {"elec_month": month, "elec_prior_month": prior, "elec_source": eu, "us_cents": float(us[1]), "us_cents_prior": float(us[2]),
           "gas_week": wk.isoformat(), "gas_source": gu, "us_gas": area["U.S."], "premium_source": pu, "us_premium": parea["U.S."], "cities": cities, "fetched": datetime.date.today().isoformat(),
           "states": {ab: {"name": STATES[ab], **elec[ab], "gas": gas[ab]} for ab in STATES}}
    json.dump(out, open(os.path.join(ROOT, "data", "rates.json"), "w"), indent=1)
    print("rates.json:", month, "electricity;", "gas week of", wk, "; US", us[1], "c/kWh,", area["U.S."], "$/gal")
if __name__ == "__main__": main()
