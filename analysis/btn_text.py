"""Write by_the_numbers.md from outputs/simple_estimate.json (the five-parameter estimate), so every figure in the
piece comes from the same run as the brief and appendix. URL is also used by the Word-document generators."""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derive  # noqa: E402
import model  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

URL = {
    "eo": "https://www.governor.nd.gov/sites/default/files/documents/Executive%20Order%202026-08%20Diesel%20emergency.pdf",
    "release": "https://www.governor.nd.gov/news/armstrong-declares-diesel-emergency-takes-action-provide-relief-fuel-costs-agricultural",
    "ndcc57": "https://ndlegis.gov/cencode/t57c43-2.pdf",
    "ndcc54": "https://ndlegis.gov/cencode/t54c27.pdf",
    "irs265": "https://content.govdelivery.com/accounts/USIRS/bulletins/3bb6f6e",
    "pub225": "https://www.irs.gov/publications/p225",
    "usc6715": "https://www.law.cornell.edu/uscode/text/26/6715",
    "eia_mw": "https://www.eia.gov/dnav/pet/xls/PET_PRI_GND_DCUS_R20_W.xls",
    "eia_us": "https://www.eia.gov/dnav/pet/xls/PET_PRI_GND_DCUS_NUS_W.xls",
    "crop0926": "https://esmis.nal.usda.gov/sites/default/release-files/796056/crop0926.pdf",
    "crop0826": "https://esmis.nal.usda.gov/sites/default/release-files/796015/crop0826.pdf",
    "prog3926": "https://esmis.nal.usda.gov/sites/default/release-files/796082/prog3926.pdf",
    "progress": "https://esmis.nal.usda.gov/publication/crop-progress",
    "stocks": "https://esmis.nal.usda.gov/publication/grain-stocks",
    "cropan": "https://esmis.nal.usda.gov/publication/crop-production-annual-summary",
    "usual": "https://www.nass.usda.gov/Publications/Todays_Reports/reports/fcdate10.pdf",
    "census": "https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_1_State_Level/North_Dakota/",
    "census_cty": "https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/North_Dakota/",
    "gazetteer": "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html",
    "dp284": "https://www.ugpti.org/resources/reports/downloads/dp-284.pdf",
    "ugpti24": "https://www.ugpti.org/resources/reports/downloads/2024-10-infrastructure-needs.pdf",
    "tedb": "https://tedb.ornl.gov/",
    "vius": "https://www.census.gov/programs-surveys/vius.html",
    "umn": "https://wlazarus.cfans.umn.edu/",
    "isu709": "https://www.extension.iastate.edu/agdm/crops/html/a3-27.html",
    "eia_enduse": "https://www.eia.gov/dnav/pet/pet_cons_821dsta_dcu_SND_a.htm",
    "ers_fiws": "https://www.ers.usda.gov/data-products/farm-income-and-wealth-statistics/",
    "fhwa24": "https://www.fhwa.dot.gov/policyinformation/statistics/2024/",
    "ndda_auction": "https://www.ndda.nd.gov/sites/www/files/documents/files/Livestock%20Auction%20Markets.pdf",
    "osu_pot": "https://u.osu.edu/beef/2022/06/15/feeder-cattle-lot-size/",
    "ers_fert": "https://www.ers.usda.gov/data-products/fertilizer-use-and-price",
    "acs": "https://www.crystalsugar.com/",
    "mdf": "https://www.mdf.coop/",
    "sd_eo": "https://drgnews.com/2026/09/29/governor-rhoden-provides-flexibility-for-farmers-at-harvest/",
}


def L(name: str, key: str) -> str:
    return f"[{name}]({URL[key]})"


def M(x: float, d: int = 2) -> str:
    return f"{x / 1e6:,.{d}f} million"


def main() -> None:
    s = json.loads((ROOT / "outputs" / "simple_estimate.json").read_text())
    R = {r["crop"]: r for r in s["rows"]}
    sens = {x["input"].split(" (")[0]: x for x in s["sensitivity"]}
    ef = s["example_farm"]
    tot, gal = s["total_savings"], s["total_gallons"]
    onhand = s["if_only_onhand_trucks"]
    hl, hh = s["haul_sensitivity"]["21.7"], s["haul_sensitivity"]["41.7"]
    out = []
    a = out.append
    a(f"""---
title: "Ag by the Numbers: Red Diesel on the Highway"
subtitle: "What North Dakota's emergency dyed-diesel order is worth, and how we estimated it"
author: "Matthew Gammans, NDSU Center for Agricultural Policy and Trade Studies (draft)"
date: "October 2, 2026"
header-includes:
  - \\usepackage{{caption}}
  - \\captionsetup[figure]{{labelformat=empty}}
---

On Sept. 29, Gov. Kelly Armstrong signed {L('Executive Order 2026-08', 'eo')}. Through Nov. 30 it lets licensed vehicles hauling farm products run red-dyed diesel on North Dakota roads. Here is what that is worth, estimated with five numbers from public data.

## The starting point: 19¢ a gallon

- **19¢ saved per gallon.** North Dakota taxes clear diesel at 23¢ a gallon and farm dyed diesel at 4¢ ({L('NDCC 57-43.2', 'ndcc57')}).
- **24.4¢ still owed.** The order doesn't touch the federal tax ({L("governor's release", 'release')}). The governor's order covers state penalties only; until the IRS grants relief, a truck caught with dyed fuel on a public road faces a federal penalty of $1,000 or $10 a gallon, whichever is greater ({L('26 U.S.C. §6715', 'usc6715')}).
- **${s['price_rise']:.2f} a gallon: the price rise since last harvest** ({L('EIA', 'eia_mw')}). The 19¢ covers {100 * s['relief_share_of_price_rise']:.0f}% of that on a gallon that qualifies.

![](outputs/btn_tax_per_gallon.png){{width=72%}}

## The estimate: five numbers

Tractors, combines and grain carts already run on dyed fuel, so the order only helps trucks hauling crops on public roads. We count corn, soybeans and wheat, which make up most of that hauling:

> **savings = tons hauled to market this fall × gallons per ton × 19¢**
>
> gallons per ton = 2 × one-way miles ÷ miles per gallon ÷ tons per load

| | Corn | Soybeans | Wheat | Source |
|-------------------------------|------:|------:|------:|------------------------------------|
| **1. 2026 production (million bu)** | {R['corn']['production_mbu']:.1f} | {R['soybeans']['production_mbu']:.1f} | {R['wheat']['production_mbu']:.1f} | {L('NASS Crop Production', 'crop0926')}, Sept. 2026 |
| **2. Share hauled off the farm this fall** | {R['corn']['share']:.0%} | {R['soybeans']['share']:.0%} | {R['wheat']['share']:.0%} | {L('NASS Grain Stocks', 'stocks')}, 2024–25 |
| **3. One-way haul (miles)** | {R['corn']['oneway_miles']} | {R['soybeans']['oneway_miles']} | {R['wheat']['oneway_miles']} | {L('UGPTI farm truck survey', 'dp284')} |
| **4. Tons per load** | {R['corn']['tons_per_load']:.1f} | {R['soybeans']['tons_per_load']:.1f} | {R['wheat']['tons_per_load']:.1f} | UGPTI survey and {L('UGPTI 2024', 'ugpti24')} |
| **5. Truck fuel economy (mpg)** | {s['mpg']} | {s['mpg']} | {s['mpg']} | {L('ORNL Transportation Energy Data Book', 'tedb')} |
| Tons hauled (million) | {R['corn']['hauled_tons'] / 1e6:.2f} | {R['soybeans']['hauled_tons'] / 1e6:.2f} | {R['wheat']['hauled_tons'] / 1e6:.2f} | (1) × (2) |
| Gallons per ton | {R['corn']['gal_per_ton']:.3f} | {R['soybeans']['gal_per_ton']:.3f} | {R['wheat']['gal_per_ton']:.3f} | 2 × (3) ÷ (5) ÷ (4) |
| **Gallons (million)** | **{R['corn']['gallons'] / 1e6:.2f}** | **{R['soybeans']['gallons'] / 1e6:.2f}** | **{R['wheat']['gallons'] / 1e6:.2f}** | |
| **Savings at 19¢** | **${R['corn']['savings'] / 1e3:,.0f}K** | **${R['soybeans']['savings'] / 1e3:,.0f}K** | **${R['wheat']['savings'] / 1e3:,.0f}K** | **Total ${tot / 1e6:.2f} million** |

**How the share hauled is measured.**
- *Corn and soybeans:* one minus the share of the crop still in on-farm storage on Dec. 1.
- *Wheat:* harvested in August, so we use how much on-farm stocks fell from Sept. 1 to Dec. 1, scaled to the order's 63 days.
- Both are averaged over 2024 and 2025.

![](outputs/btn_simple_crops.png){{width=80%}}

## What it adds up to

- **About ${tot / 1e6:.1f} million** in state tax saved on **{gal / 1e6:.1f} million gallons**, *if every eligible truck switches.*
- **About ${onhand / 1e6:.1f} million** if only trucks already fueled from farm tanks switch. That is 53% of heavy farm trucks in USDOT's 2021 {L('Vehicle Inventory and Use Survey', 'vius')}. Federal penalty risk may hold some farmers back, too.
- **About ${s['per_farm']:.0f} per ND farm, {100 * s['per_acre_three_crops']:.0f}¢ per acre of corn, soybeans and wheat, {s['per_bushel_hauled_cents']:.2f}¢ per bushel hauled.** That is too small to show up in elevator bids or grocery prices.
- **{100 * s['share_of_fall_fuel_shock']:.1f}% of the higher fall fuel bill.** Combines and grain carts burn about {(s['fall_fuel_gal'] - gal) / 1e6:.0f} million gallons harvesting this year's corn and soybeans ({L('UMN', 'umn')} fuel per acre × NASS acres). The trucks add {gal / 1e6:.1f} million. At ${s['price_rise']:.2f} more per gallon, that is ${s['fall_fuel_shock'] / 1e6:.0f} million in extra cost.
- **The road fund gives it up.** The money would have gone to the Highway Tax Distribution Fund; nearly 40% of that goes to counties, cities and townships ({L('NDCC 54-27-19', 'ndcc54')}).

**One farm.** Take 1,000 acres of corn and 1,000 of soybeans at this year's forecast yields. Hauling this fall's share of the crop burns about {round(ef['onroad_gal'], -2):,.0f} gallons, so the order saves about **${round(ef['savings'], -1):,.0f}**. Its combines and grain carts burn about {ef['field_gal_harvest']:,.0f} gallons. Together, its harvest diesel bill is up about **${round(ef['fall_diesel_increase'], -3):,.0f}**.

![](outputs/btn_example_farm.png){{width=80%}}

## How sure are we?

Haul distance matters most. The UGPTI survey's North Dakota trips range from 21.7 miles (semis hauling wheat) to 41.7 miles (the second-choice delivery point). Over that range savings run from ${hl / 1e6:.1f} million to ${hh / 1e6:.1f} million. Each of the other inputs moves the total by about $0.2 million or less:
- 2024 vs. 2025 storage patterns: ${sens['Share hauled off-farm']['low'] / 1e6:.2f}M–{sens['Share hauled off-farm']['high'] / 1e6:.2f}M.
- An all-semi fleet vs. a fleet weighted by truck count: ${sens['Tons per load']['low'] / 1e6:.2f}M–{sens['Tons per load']['high'] / 1e6:.2f}M.
- 5.1 vs. 6.2 mpg: ${sens['Fuel economy']['low'] / 1e6:.2f}M–{sens['Fuel economy']['high'] / 1e6:.2f}M.

We also leave some hauling out: sugarbeets, potatoes and other crops, trips from field to bin, livestock and fertilizer, and pickups. The project's fuller model puts the excluded truck hauls at about 2 million more gallons.

![](outputs/btn_simple_haul.png){{width=80%}}

## Three more numbers

- **26%:** share of ND cropland in counties bordering Minnesota or South Dakota ({L('Census', 'census_cty')}). Neither state allows dyed fuel on its roads, so farms delivering across the line get nothing ({L("South Dakota's order", 'sd_eo')} raised weight limits instead).
- **${s['holiday_cost'] / 1e6:.0f} million:** cost of suspending the 23¢ on *all* highway diesel for the same two months. That is {s['taxable_hwy_gal'] / 1e6:.0f} million gallons × $0.23 ({L('FHWA', 'fhwa24')}), about {s['holiday_cost'] / tot:.0f} times the order's cost.
- **$0:** cost of asking the IRS for penalty relief, as five other states have. It wouldn't save farmers money, since the 24.4¢ would still be owed, but it would remove their legal risk.

## Data and code

Every number comes from `analysis/simple_estimate.py`, run on public data in the project folder.
- `data/raw/` holds each source file, and `data/SOURCES.md` lists the URLs.
- `simple_estimate.docx` gives the parameter table and the calculation.
- The policy brief and its appendix carry the same estimate, plus caveats and a cross-check against a fuller model.
""")
    lines = "\n".join(out).split("\n")
    fixed = []
    for ln in lines:
        if ln.startswith("- ") and fixed and fixed[-1].strip() and not fixed[-1].lstrip().startswith(("- ", "|")):
            fixed.append("")
        fixed.append(ln)
    (ROOT / "by_the_numbers.md").write_text("\n".join(fixed))


if __name__ == "__main__":
    main()
