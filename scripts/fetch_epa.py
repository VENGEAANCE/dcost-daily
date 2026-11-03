#!/usr/bin/env python3
"""Pull official EPA ratings for every vehicle in vehicles.py from the fueleconomy.gov web
services (https://www.fueleconomy.gov/ws/rest/vehicle/<id>) into data/epa.json.
EPA numbers rarely change mid model year; rerun when you add a car or a new model year lands."""
import json, os, sys, urllib.request, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vehicles import EV, GAS
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEEP = ["id", "year", "make", "model", "drive", "atvType", "fuelType1", "comb08", "city08", "highway08", "combE", "cityE", "highwayE",
        "range", "co2TailpipeGpm", "fuelCost08", "VClass", "displ", "cylinders", "trany"]
def get(i):
    r = urllib.request.Request(f"https://www.fueleconomy.gov/ws/rest/vehicle/{i}", headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 dcostdaily.com data refresh"})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())
out = {"source": "https://www.fueleconomy.gov/ws/rest/vehicle/", "fetched": datetime.date.today().isoformat(), "vehicles": {}}
for grp in (EV, GAS):
    for slug, (_, _, vid) in grp.items():
        d = get(vid); out["vehicles"][slug] = {k: d.get(k) for k in KEEP}
json.dump(out, open(os.path.join(ROOT, "data", "epa.json"), "w"), indent=1)
print("epa.json:", len(out["vehicles"]), "vehicles")
