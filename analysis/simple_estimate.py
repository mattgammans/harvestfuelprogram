"""Simple estimate of 2026 farm savings from EO 2026-08: five sourced parameters, three crops.

    savings = sum over crops [ production x share hauled off-farm in window ]
              x ( 2 x one-way miles / mpg / tons per load ) x $0.19

Policy definitions (not counted as parameters): 19c/gal state tax difference; window Sept. 29-Nov. 30 (63 days).
Assumes every eligible truck gallon switches to dyed fuel (an upper bound; see notes).
Writes outputs/simple_estimate.json and outputs/simple_estimate.md.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RELIEF = 0.19          # policy: 23c - 4c (NDCC 57-43.2)
WINDOW_DAYS = 63       # policy: Sept. 29 - Nov. 30, 2026
CROPS = ("corn", "soybeans", "wheat")
LB_PER_BU = {"corn": 56, "soybeans": 60, "wheat": 60}

# ---- Parameter 1: 2026 production (1,000 bu) ----
PRODUCTION_2026 = {"corn": 578_500, "soybeans": 203_700, "wheat": 246_950 + 35_490}  # wheat = other spring + durum
P1_SOURCE = "NASS Crop Production, Sept. 11, 2026 (corn, soybeans; nass_crop0926.txt) and Aug. 12, 2026 (spring wheat, durum; nass_crop0826.txt)"

# ---- Parameter 2: share of the crop hauled off the farm during the window ----
# Corn, soybeans: 1 - (Dec. 1 on-farm stocks / production), averaged over 2024 and 2025.
# Wheat (harvested in Aug.): Sept. 1 -> Dec. 1 drop in on-farm stocks / production, averaged 2024-25, x 63/91 days.
STOCKS = {  # 1,000 bu, ND on-farm (NASS Grain Stocks)
    2024: {"corn_dec1": 325_000, "soy_dec1": 79_000, "wheat_sep1": 222_000, "wheat_dec1": 173_000},
    2025: {"corn_dec1": 380_000, "soy_dec1": 105_000, "wheat_sep1": 221_000, "wheat_dec1": 168_000},
}
PRODUCTION_PAST = {  # 1,000 bu (NASS Crop Production 2025 Summary)
    2024: {"corn": 542_360, "soybeans": 245_625, "wheat": 368_285},
    2025: {"corn": 711_000, "soybeans": 223_905, "wheat": 334_055},
}
P2_SOURCE = ("NASS Grain Stocks: Sept. 30, 2024 & 2025; Jan. 2025 & Jan. 12, 2026 (src2_grst*.txt); "
             "NASS Crop Production 2025 Summary, Jan. 12, 2026 (src2_cropan26.txt)")

# ---- Parameter 3: one-way miles to first delivery point (bushel-weighted, ND) ----
ONEWAY_MILES = {"corn": 27.8, "soybeans": 27.8, "wheat": 24.5}
P3_SOURCE = "UGPTI DP-284 (Vachal 2015), ND corn Table 3.56 (also used for soybeans; no ND soybean table) and ND wheat Table 3.52"

# ---- Parameter 4: tons per load (bushels per load by truck type x share of ND grain hauled by each type) ----
BU_PER_LOAD = {  # DP-284 Table 3.65: single, tandem, tridem, 5-axle semi
    "corn": {"single": 366, "tandem": 581, "tridem": 661, "semi": 930},
    "soybeans": {"single": 331, "tandem": 532, "tridem": 635, "semi": 885},
    "wheat": {"single": 324, "tandem": 547, "tridem": 674, "semi": 885},
}
TRUCK_SHARE = {"semi": 0.5496, "tandem": 0.2515, "tridem": 0.1255}  # UGPTI Infrastructure Needs 2024, Table 12
TRUCK_SHARE["single"] = 1 - sum(TRUCK_SHARE.values())                # remainder assigned to single-axle trucks
P4_SOURCE = "UGPTI DP-284 Table 3.65 (bushels per load) weighted by UGPTI Infrastructure Needs 2024 Table 12 (share of ND grain by truck type)"

# ---- Parameter 5: truck fuel economy over loaded and empty miles ----
MPG = 6.2
P5_SOURCE = "ORNL Transportation Energy Data Book Ed. 40, Table 5.2: Class 7-8 combination trucks, 2020 average"

# Sensitivity only (not part of the estimate)
ONHAND_TRUCKS = 0.528  # 2021 VIUS: Class 6-8 farm diesel trucks fueled mainly at own facility


def offfarm_share(crop: str) -> tuple[float, dict]:
    vals = {}
    for y in (2024, 2025):
        s, prod = STOCKS[y], PRODUCTION_PAST[y][crop]
        if crop == "corn":
            vals[y] = 1 - s["corn_dec1"] / prod
        elif crop == "soybeans":
            vals[y] = 1 - s["soy_dec1"] / prod
        else:
            vals[y] = (s["wheat_sep1"] - s["wheat_dec1"]) / prod * WINDOW_DAYS / 91
    return sum(vals.values()) / len(vals), vals


def share_detail() -> list[dict]:
    """Rows for the 'grain that left the farm' table (million bushels)."""
    rows = []
    for c in CROPS:
        for y in (2024, 2025):
            s, prod = STOCKS[y], PRODUCTION_PAST[y][c] / 1000
            if c == "wheat":
                sep1, dec1 = s["wheat_sep1"] / 1000, s["wheat_dec1"] / 1000
                left = sep1 - dec1
                rows.append({"crop": c, "year": y, "production": prod, "stocks": f"Sept. 1: {sep1:.1f} → Dec. 1: {dec1:.1f}",
                             "left": left, "pct_raw": left / prod, "share": left / prod * WINDOW_DAYS / 91})
            else:
                dec1 = s["corn_dec1" if c == "corn" else "soy_dec1"] / 1000
                left = prod - dec1
                rows.append({"crop": c, "year": y, "production": prod, "stocks": f"Dec. 1: {dec1:.1f}",
                             "left": left, "pct_raw": left / prod, "share": left / prod})
        rows.append({"crop": c, "year": "Average", "share": offfarm_share(c)[0]})
    return rows


def tons_per_load(crop: str) -> float:
    bu = sum(TRUCK_SHARE[k] * BU_PER_LOAD[crop][k] for k in TRUCK_SHARE)
    return bu * LB_PER_BU[crop] / 2000


# Context inputs (not part of the five-parameter estimate)
ACRES_2026 = {"corn": 4.45e6, "soybeans": 6.79e6, "wheat": 4.49e6 + 0.91e6}   # NASS harvested acres, 2026 forecasts
ND_FARMS = 25_068                                                              # 2022 Census of Agriculture
CROPLAND_ACRES = 21_824_571                                                    # 2022 Census of Agriculture
HTDF_SPLIT = {"state highway fund": 0.60, "counties": 0.35 * 0.73, "cities": 0.35 * 0.27, "townships": 0.034, "public transit": 0.016}
FIELD_GAL_PER_ACRE = {"corn": 2.00 + 1.44, "soybeans": 2.04 + 1.44}            # UMN 2024: combine + grain cart
TAXABLE_HWY_DIESEL_WINDOW = 26_684_819 + 30_579_990 + 30_658_884 * 2 / 30      # FHWA MF-33SF 2024, ND (Oct + Nov + 2 Sept days)
EIA_BASELINE, EIA_LATEST = 3.7408, 6.526                                       # EIA Midwest retail: Sept-Nov 2025 avg; Sept. 28, 2026

# Sensitivity ranges for each parameter (sources in appendix)
SENS = {
    "share hauled (2024 vs. 2025 stocks)": "share",
    "haul distance (21.7–41.7 mi, DP-284)": "miles",
    "tons per load (truck-count weighted to all-semi)": "load",
    "fuel economy (5.1–6.2 mpg, ORNL)": "mpg",
}


def estimate(share_year=None, miles_scale=None, load="fleet", mpg=MPG) -> float:
    gal = 0.0
    for c in CROPS:
        share = offfarm_share(c)[1][share_year] if share_year else offfarm_share(c)[0]
        miles = miles_scale[c] if miles_scale else ONEWAY_MILES[c]
        if load == "fleet":
            tpl = tons_per_load(c)
        elif load == "count":  # DP-284 T3.34 ND fleet by truck count (more small trucks)
            w = {"single": 0.187, "tandem": 0.224 + 0.044, "tridem": 0.105, "semi": 0.406 + 0.033}
            tpl = sum(w[k] * BU_PER_LOAD[c][k] for k in w) * LB_PER_BU[c] / 2000
        else:  # all 5-axle semis
            tpl = BU_PER_LOAD[c]["semi"] * LB_PER_BU[c] / 2000
        gal += PRODUCTION_2026[c] * 1000 * LB_PER_BU[c] / 2000 * share * 2 * miles / mpg / tpl
    return gal * RELIEF


def sensitivity() -> list[dict]:
    rows = []
    rows.append({"input": "Share hauled off-farm (2024-only vs. 2025-only stocks)", "low": estimate(share_year=2024), "high": estimate(share_year=2025)})
    rows.append({"input": "Haul distance (21.7 mi ND semi wheat trip to 41.7 mi second-choice point, DP-284)",
                 "low": estimate(miles_scale={c: 21.7 for c in CROPS}), "high": estimate(miles_scale={c: 41.7 for c in CROPS})})
    rows.append({"input": "Tons per load (all 5-axle semis to truck-count weighted fleet)", "low": estimate(load="semi"), "high": estimate(load="count")})
    rows.append({"input": "Fuel economy (6.2 to 5.1 mpg; ORNL T5.2 and T5.12)", "low": estimate(mpg=6.2), "high": estimate(mpg=5.1)})
    rows.append({"input": "Take-up (only trucks fueled from farm tanks, 53%, VIUS; vs. all)", "low": estimate() * ONHAND_TRUCKS, "high": estimate()})
    return rows


def main() -> dict:
    rows, tot_gal = [], 0.0
    for c in CROPS:
        share, by_year = offfarm_share(c)
        tons = PRODUCTION_2026[c] * 1000 * LB_PER_BU[c] / 2000
        hauled = tons * share
        tpl = tons_per_load(c)
        gal_per_ton = 2 * ONEWAY_MILES[c] / MPG / tpl
        gal = hauled * gal_per_ton
        tot_gal += gal
        rows.append({"crop": c, "production_mbu": PRODUCTION_2026[c] / 1000, "tons": tons, "share": share, "share_by_year": by_year,
                     "hauled_tons": hauled, "oneway_miles": ONEWAY_MILES[c], "tons_per_load": tpl, "gal_per_ton": gal_per_ton,
                     "gallons": gal, "savings": gal * RELIEF})
    out = {
        "rows": rows, "total_gallons": tot_gal, "total_savings": tot_gal * RELIEF,
        "if_only_onhand_trucks": tot_gal * RELIEF * ONHAND_TRUCKS,
        "haul_sensitivity": {m: sum(r["hauled_tons"] * 2 * m / MPG / r["tons_per_load"] for r in rows) * RELIEF for m in (21.7, 41.7)},
        "sources": {"P1": P1_SOURCE, "P2": P2_SOURCE, "P3": P3_SOURCE, "P4": P4_SOURCE, "P5": P5_SOURCE},
        "mpg": MPG,
    }
    sav = tot_gal * RELIEF
    hauled_bu = {r["crop"]: r["hauled_tons"] * 2000 / LB_PER_BU[r["crop"]] for r in rows}
    ex = {}
    for c, ac in (("corn", 1000), ("soybeans", 1000)):
        r = next(x for x in rows if x["crop"] == c)
        bu = ac * PRODUCTION_2026[c] * 1000 / ACRES_2026[c]
        ex[c] = {"bu": bu, "gal": bu * LB_PER_BU[c] / 2000 * r["share"] * r["gal_per_ton"]}
    ex_gal = sum(v["gal"] for v in ex.values())
    field = sum(1000 * FIELD_GAL_PER_ACRE[c] for c in ("corn", "soybeans"))
    shock = EIA_LATEST - EIA_BASELINE
    out.update({
        "per_farm": sav / ND_FARMS,
        "per_acre_three_crops": sav / sum(ACRES_2026.values()),
        "per_bushel_hauled_cents": 100 * sav / sum(hauled_bu.values()),
        "hauled_bushels": hauled_bu,
        "relief_share_of_price_rise": RELIEF / shock,
        "price_rise": shock,
        "split": {k: sav * v for k, v in HTDF_SPLIT.items()},
        "example_farm": {"bushels": sum(v["bu"] for v in ex.values()), "onroad_gal": ex_gal, "savings": ex_gal * RELIEF,
                         "field_gal_harvest": field, "fall_diesel_increase": (ex_gal + field) * shock},
        "fall_fuel_gal": sum(ACRES_2026[c] * FIELD_GAL_PER_ACRE[c] for c in ("corn", "soybeans")) + tot_gal,
        "fall_fuel_shock": (sum(ACRES_2026[c] * FIELD_GAL_PER_ACRE[c] for c in ("corn", "soybeans")) + tot_gal) * shock,
        "share_of_fall_fuel_shock": sav / ((sum(ACRES_2026[c] * FIELD_GAL_PER_ACRE[c] for c in ("corn", "soybeans")) + tot_gal) * shock),
        "holiday_cost": TAXABLE_HWY_DIESEL_WINDOW * 0.23,
        "taxable_hwy_gal": TAXABLE_HWY_DIESEL_WINDOW,
        "per_acre_payment_cents": 100 * sav / CROPLAND_ACRES,
        "sensitivity": sensitivity(),
        "share_detail": share_detail(),
        "haul_curve": [{"miles": m, "savings": estimate(miles_scale={c: m for c in CROPS})} for m in range(10, 51, 5)],
    })
    (ROOT / "outputs" / "simple_estimate.json").write_text(json.dumps(out, indent=1, default=float))
    return out


if __name__ == "__main__":
    o = main()
    for r in o["rows"]:
        print(f"{r['crop']:9s} prod {r['production_mbu']:6.1f}M bu  share {r['share']:.3f} {r['share_by_year']}  hauled {r['hauled_tons'] / 1e6:5.2f}M t  "
              f"{r['oneway_miles']} mi  {r['tons_per_load']:.1f} t/load  {r['gal_per_ton']:.3f} gal/t  {r['gallons'] / 1e6:.2f}M gal  ${r['savings'] / 1e6:.3f}M")
    print(f"TOTAL {o['total_gallons'] / 1e6:.2f}M gal  ${o['total_savings'] / 1e6:.3f}M;  if only on-hand trucks ${o['if_only_onhand_trucks'] / 1e6:.3f}M; "
          f"haul 21.7/41.7 mi: {[round(v / 1e6, 3) for v in o['haul_sensitivity'].values()]}")
