"""Single list of every vehicle the site prices, by EPA fueleconomy.gov vehicle id.
fetch_epa.py pulls each id's official numbers into data/epa.json; gen_compare.py and the
calculator (vehicles.js, written by gen_compare.py) read from there. Add a car here, rerun
fetch_epa.py, then gen_pages.py. Labels are ours; every number comes from EPA."""
# slug: (label, short name, EPA id)
EV = {
 "model-3-standard-rwd": ("Tesla Model 3 Standard RWD", "Model 3", 50251),
 "model-3-premium-rwd": ("Tesla Model 3 Premium RWD", "Model 3", 50038),
 "model-3-premium-awd": ("Tesla Model 3 Premium AWD", "Model 3", 50037),
 "model-3-performance-awd": ("Tesla Model 3 Performance AWD", "Model 3", 50250),
 "model-y-standard-rwd": ("Tesla Model Y Standard RWD (18in wheels)", "Model Y", 50040),
 "model-y-long-range-rwd": ("Tesla Model Y Long Range RWD", "Model Y", 49743),
 "model-y-long-range-awd": ("Tesla Model Y Long Range AWD", "Model Y", 49744),
 "model-y-performance-awd": ("Tesla Model Y Performance AWD", "Model Y", 50253),
 "model-s": ("Tesla Model S", "Model S", 49741),
 "model-x": ("Tesla Model X", "Model X", 49745),
 "cybertruck-awd": ("Tesla Cybertruck AWD", "Cybertruck", 50039),
}
# slug: (label, short name, EPA id). Fuel grade (regular/premium) comes from EPA's fuelType1.
GAS = {
 "toyota-camry-hybrid-le": ("Toyota Camry Hybrid LE FWD", "Camry Hybrid", 49823),
 "toyota-camry-hybrid-se-xle": ("Toyota Camry Hybrid SE/XLE/XSE FWD", "Camry Hybrid", 49824),
 "toyota-camry-hybrid-awd-le": ("Toyota Camry Hybrid AWD LE", "Camry Hybrid", 49825),
 "toyota-rav4-hybrid-fwd": ("Toyota RAV4 Hybrid FWD (base)", "RAV4 Hybrid", 50285),
 "toyota-rav4-hybrid-awd": ("Toyota RAV4 Hybrid AWD (SE & LE)", "RAV4 Hybrid", 50135),
 "toyota-rav4-hybrid-awd-xle": ("Toyota RAV4 Hybrid AWD XLE", "RAV4 Hybrid", 50136),
 "honda-accord": ("Honda Accord 1.5T", "Accord", 50070),
 "honda-accord-se": ("Honda Accord SE 1.5T", "Accord", 50055),
 "honda-accord-hybrid": ("Honda Accord Hybrid", "Accord Hybrid", 50071),
 "honda-cr-v-awd": ("Honda CR-V AWD 1.5T", "CR-V", 49487),
 "honda-cr-v-fwd": ("Honda CR-V FWD 1.5T", "CR-V", 49352),
 "honda-cr-v-hybrid-awd": ("Honda CR-V Hybrid AWD", "CR-V Hybrid", 49488),
 "honda-civic": ("Honda Civic Sedan 2.0", "Civic", 49287),
 "honda-civic-hybrid": ("Honda Civic Hybrid Sedan", "Civic Hybrid", 49289),
 "bmw-330i-xdrive": ("BMW 330i xDrive", "330i", 49234),
 "bmw-330i": ("BMW 330i (RWD)", "330i", 49233),
 "ford-f-150-35-4wd": ("Ford F-150 4WD 3.5L EcoBoost V6", "F-150", 50099),
 "ford-f-150-27-4wd": ("Ford F-150 4WD 2.7L EcoBoost V6", "F-150", 50098),
 "ford-f-150-50-4wd": ("Ford F-150 4WD 5.0L V8", "F-150", 50100),
 "ford-f-150-hybrid-4wd": ("Ford F-150 PowerBoost Hybrid 4WD", "F-150 Hybrid", 50097),
 "chevrolet-silverado-53-4wd": ("Chevrolet Silverado 4WD 5.3L V8", "Silverado", 49391),
 "chevrolet-silverado-27-4wd": ("Chevrolet Silverado 4WD 2.7L Turbo", "Silverado", 49378),
 "ram-1500-30-4wd": ("Ram 1500 4WD 3.0L I6", "Ram 1500", 49420),
 "ram-1500-36-4wd": ("Ram 1500 4WD 3.6L V6 eTorque", "Ram 1500", 49840),
 "bmw-540i-xdrive": ("BMW 540i xDrive", "540i", 49274),
 "bmw-530i-xdrive": ("BMW 530i xDrive", "530i", 49273),
 "mercedes-e350-4matic": ("Mercedes-Benz E 350 4MATIC", "E 350", 49296),
 "mercedes-e350": ("Mercedes-Benz E 350 (RWD)", "E 350", 49294),
 "bmw-x5-xdrive40i": ("BMW X5 xDrive40i", "X5", 49564),
 "bmw-x5-sdrive40i": ("BMW X5 sDrive40i", "X5", 49548),
 "lexus-rx-350-awd": ("Lexus RX 350 AWD", "RX 350", 49858),
 "lexus-rx-350h-awd": ("Lexus RX 350h AWD", "RX 350h", 49857),
 "honda-pilot-awd": ("Honda Pilot AWD", "Pilot", 50154),
 "honda-pilot-fwd": ("Honda Pilot FWD", "Pilot", 50113),
}
# Comparison pages: url slug, EV, main gas rival, other versions of the rival shown in the "which version" table.
PAIRS = [
 ("tesla-model-y-vs-toyota-rav4", "model-y-long-range-awd", "toyota-rav4-hybrid-awd", ["toyota-rav4-hybrid-fwd", "toyota-rav4-hybrid-awd-xle"]),
 ("tesla-model-y-vs-honda-cr-v", "model-y-long-range-awd", "honda-cr-v-awd", ["honda-cr-v-fwd", "honda-cr-v-hybrid-awd"]),
 ("tesla-model-y-vs-lexus-rx", "model-y-long-range-awd", "lexus-rx-350-awd", ["lexus-rx-350h-awd"]),
 ("tesla-model-3-vs-toyota-camry", "model-3-standard-rwd", "toyota-camry-hybrid-le", ["toyota-camry-hybrid-se-xle", "toyota-camry-hybrid-awd-le"]),
 ("tesla-model-3-vs-honda-accord", "model-3-standard-rwd", "honda-accord", ["honda-accord-se", "honda-accord-hybrid"]),
 ("tesla-model-3-vs-honda-civic", "model-3-standard-rwd", "honda-civic", ["honda-civic-hybrid"]),
 ("tesla-model-3-vs-bmw-3-series", "model-3-premium-awd", "bmw-330i-xdrive", ["bmw-330i"]),
 ("tesla-cybertruck-vs-ford-f-150", "cybertruck-awd", "ford-f-150-35-4wd", ["ford-f-150-27-4wd", "ford-f-150-50-4wd", "ford-f-150-hybrid-4wd"]),
 ("tesla-cybertruck-vs-chevy-silverado", "cybertruck-awd", "chevrolet-silverado-53-4wd", ["chevrolet-silverado-27-4wd"]),
 ("tesla-cybertruck-vs-ram-1500", "cybertruck-awd", "ram-1500-30-4wd", ["ram-1500-36-4wd"]),
 ("tesla-model-s-vs-bmw-5-series", "model-s", "bmw-540i-xdrive", ["bmw-530i-xdrive"]),
 ("tesla-model-s-vs-mercedes-e-class", "model-s", "mercedes-e350-4matic", ["mercedes-e350"]),
 ("tesla-model-x-vs-bmw-x5", "model-x", "bmw-x5-xdrive40i", ["bmw-x5-sdrive40i"]),
 ("tesla-model-x-vs-honda-pilot", "model-x", "honda-pilot-awd", ["honda-pilot-fwd"]),
]
# Page headings for each matchup.
NAMES = {"tesla-model-y-vs-toyota-rav4": ("Tesla Model Y", "Toyota RAV4"), "tesla-model-y-vs-honda-cr-v": ("Tesla Model Y", "Honda CR-V"),
 "tesla-model-y-vs-lexus-rx": ("Tesla Model Y", "Lexus RX"), "tesla-model-3-vs-toyota-camry": ("Tesla Model 3", "Toyota Camry"),
 "tesla-model-3-vs-honda-accord": ("Tesla Model 3", "Honda Accord"), "tesla-model-3-vs-honda-civic": ("Tesla Model 3", "Honda Civic"),
 "tesla-model-3-vs-bmw-3-series": ("Tesla Model 3", "BMW 3 Series"), "tesla-cybertruck-vs-ford-f-150": ("Tesla Cybertruck", "Ford F-150"),
 "tesla-cybertruck-vs-chevy-silverado": ("Tesla Cybertruck", "Chevy Silverado"), "tesla-cybertruck-vs-ram-1500": ("Tesla Cybertruck", "Ram 1500"),
 "tesla-model-s-vs-bmw-5-series": ("Tesla Model S", "BMW 5 Series"), "tesla-model-s-vs-mercedes-e-class": ("Tesla Model S", "Mercedes E-Class"),
 "tesla-model-x-vs-bmw-x5": ("Tesla Model X", "BMW X5"), "tesla-model-x-vs-honda-pilot": ("Tesla Model X", "Honda Pilot")}
# EIA weekly retail gasoline publishes these 10 cities. Electricity has no city series, so city pages use the state average and say so.
CITIES = {"boston": ("Boston", "MA"), "chicago": ("Chicago", "IL"), "cleveland": ("Cleveland", "OH"), "denver": ("Denver", "CO"),
          "houston": ("Houston", "TX"), "los-angeles": ("Los Angeles", "CA"), "miami": ("Miami", "FL"), "new-york-city": ("New York City", "NY"),
          "san-francisco": ("San Francisco", "CA"), "seattle": ("Seattle", "WA")}
