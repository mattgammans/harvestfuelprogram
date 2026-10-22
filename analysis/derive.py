"""Derive every model parameter from sourced inputs in params.yaml.

Each derived parameter is {"low", "central", "high", "how"}. `how` is the calculation in words and is
printed in the appendix, so no parameter enters the model without a source or a stated computation.
"""
from __future__ import annotations

import datetime as dt
import math
import re
import statistics
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

import vius

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANHATTAN = 4 / math.pi  # mean grid-road distance / straight-line distance, uniformly random direction


def P(low, central, high, how):
    return {"low": float(low), "central": float(central), "high": float(high), "how": how}


def pct(xs, q):
    return float(np.percentile(xs, q))


# ---------------------------------------------------------------- helpers reading raw files
def county_harvested_cropland() -> dict:
    """Census 2022 Table 8: harvested cropland acres by ND county (parsed from pdftotext output)."""
    txt = RAW / "t8.txt"
    if not txt.exists():
        import subprocess
        subprocess.run(["pdftotext", "-layout", str(RAW / "src4_census22_nd_county_st38_2_008_008.pdf"), str(txt)], check=True)
    lines = txt.read_text().splitlines()
    res, hdr = {}, None
    for i, line in enumerate(lines):
        if re.match(r"\s*Item\s", line):
            hdr = re.split(r"\s{2,}", line.strip())[1:]
        if hdr and re.match(r"\s*Harvested cropland \.", line):
            for j in range(i + 1, i + 5):
                if "acres, 2022" in lines[j]:
                    nums = re.findall(r"\d[\d,]*", lines[j].split("acres, 2022")[1])
                    for name, n in zip(hdr[-len(nums):], nums):
                        res.setdefault(name, int(n.replace(",", "")))
                    break
    return res


def county_land_sqmi() -> dict:
    z = zipfile.ZipFile(RAW / "src5_census_gazetteer_2023_counties_nd.zip")
    g = pd.read_csv(z.open(z.namelist()[0]), sep="\t", dtype=str)
    g.columns = [c.strip() for c in g.columns]
    g = g[g["USPS"] == "ND"]
    return {n.replace(" County", ""): float(a) for n, a in zip(g["NAME"], g["ALAND_SQMI"])}


def interp_share_done(dates: list[str], on: str) -> float:
    """NASS usual dates: begin=5%, most-active 15%->85%, end=95%; linear in between, 0/100% outside."""
    yr = 2026
    d = [dt.date.fromisoformat(f"{yr}-{x}") for x in dates]
    pts = [(d[0] - dt.timedelta(days=(d[1] - d[0]).days / 2), 0.0), (d[0], 0.05), (d[1], 0.15), (d[2], 0.85),
           (d[3], 0.95), (d[3] + dt.timedelta(days=(d[3] - d[2]).days / 2), 1.0)]
    t = dt.date.fromisoformat(f"{yr}-{on}")
    xs = [(p[0] - t).days for p in pts]
    return float(np.interp(0, xs, [p[1] for p in pts]))


def circle_fraction_beyond_line(x: float, r: float) -> float:
    """Share of a disk of radius r whose center is x from a straight line that lies on the far side."""
    if x >= r:
        return 0.0
    th = 2 * math.acos(x / r)
    return (th - math.sin(th)) / (2 * math.pi)


# ---------------------------------------------------------------- main
def derive(params: dict, price_summary: dict) -> tuple[dict, dict]:
    I, B = params["inputs"], params["bounds"]
    c26 = I["crops_2026"]
    D: dict = {}
    notes: dict = {}
    wfrac_days = params["window"]["days"]

    # --- harvest completion by Nov 30 (share of what remained on Sept 27)
    p27 = I["pct_harvested_sep27_2026"]
    hist = I["pct_harvested_late_nov_history"]
    for crop in ("corn", "soybeans", "sugarbeets", "sunflower"):
        h = [v / 100 for v in hist[crop]]
        f = lambda q: min(1.0, (q - p27[crop]) / (1 - p27[crop]))  # noqa: E731
        D[f"done_by_nov30_{crop}"] = P(f(pct(h, 10)), f(statistics.median(h)), f(pct(h, 90)),
            f"ND % harvested near Nov 30, 2016-2025 (10th pct / median / 90th pct = {pct(h,10):.0%} / "
            f"{statistics.median(h):.0%} / {pct(h,90):.0%}), converted to share of the {1-p27[crop]:.0%} still in the field on Sept 27, 2026")

    # --- share of harvest leaving the farm by Dec 1 (market leg) and via bins (bin leg)
    gs, prod, hv = I["grain_stocks_onfarm_1000bu"], I["production_1000bu"], I["harvested_by_dec1_share"]
    off = {}
    for crop, key in (("corn", "corn"), ("soybeans", "soy")):
        vals = [1 - gs[y][f"{key}_dec1"] / (prod[y][crop] * hv[y][crop]) for y in ("y2024", "y2025")]
        off[crop] = vals
        D[f"offfarm_by_dec1_{crop}"] = P(min(vals), statistics.mean(vals), max(vals),
            f"1 - ND on-farm stocks Dec 1 / (production x share harvested by Dec 1), 2024 and 2025 = "
            f"{vals[0]:.2f}, {vals[1]:.2f} (NASS Grain Stocks, Crop Production). Dec 1 stocks include a little old crop, so this slightly understates movement")
    dp = I["dp284"]
    D["direct_from_field_corn"] = P(dp["direct_from_field_share"]["corn_nd"], dp["direct_from_field_share"]["corn_nd"],
                                    dp["direct_from_field_share"]["wheat_nd"], "UGPTI DP-284 p. 11: ND corn 33% hauled direct from field; ND wheat 36% as upper value")
    D["direct_from_field_soybeans"] = P(min(off["soybeans"]), dp["direct_from_field_share"]["soybeans_region"], dp["direct_from_field_share"]["soybeans_region"],
                                        "UGPTI DP-284 p. 11: regional soybeans 66% direct (no ND value); capped below by the observed off-farm share")

    # --- other fall crops: tons harvested in window
    sun_t = c26["sunflower"]["production_lb_2025"] * c26["sunflower"]["acres"] / c26["sunflower"]["acres_2025"] / 2000
    ud = I["usual_harvest_dates_nd"]
    beans_share = 1 - interp_share_done(ud["dry_beans"], "09-29")
    pot_share = 1 - interp_share_done(ud["potatoes"], "09-29")
    beans_t = c26["dry_beans"]["production_cwt"] * 100 / 2000
    pot_t = c26["potatoes"]["production_cwt_2025"] * 100 / 2000
    sd = D["done_by_nov30_sunflower"]
    other = {k: sun_t * (1 - p27["sunflower"]) * sd[k] + beans_t * beans_share + pot_t * pot_share for k in ("low", "central", "high")}
    D["other_fall_crops_tons"] = P(other["low"], other["central"], other["high"],
        f"Sunflower: 2025 production x 2026/2025 acres ({sun_t/1e6:.2f} Mt) x 97% unharvested x done-by-Nov-30 range; "
        f"dry beans: 2026 forecast ({beans_t/1e6:.2f} Mt) x {beans_share:.0%} harvested after Sept 29; potatoes: 2025 production "
        f"({pot_t/1e6:.2f} Mt) x {pot_share:.0%} after Sept 29 (NASS usual harvest dates, linear between the 5/15/85/95% dates)")

    # --- stored small grain sold in window: on-farm Sep 1 -> Dec 1 decline rate x 2026 Sep 1 stocks x 63/91
    rates = {y: (gs[y]["wheat_sep1"] - gs[y]["wheat_dec1"], gs[y]["barley_sep1"] - gs[y]["barley_dec1"]) for y in ("y2024", "y2025")}
    t26 = []
    for y in ("y2024", "y2025"):
        rw = rates[y][0] / gs[y]["wheat_sep1"]
        rb = rates[y][1] / gs[y]["barley_sep1"]
        bu_w = gs["y2026"]["wheat_sep1"] * 1000 * rw
        bu_b = gs["y2026"]["barley_sep1"] * 1000 * rb
        t26.append((bu_w * 60 + bu_b * 48) / 2000 * wfrac_days / 91)
    D["stored_small_grain_tons_in_window"] = P(min(t26), statistics.mean(t26), max(t26),
        "ND on-farm wheat and barley stocks fell 22-24% (wheat) and 6-33% (barley) between Sept 1 and Dec 1 in 2024 and 2025; "
        f"applied to Sept 1, 2026 on-farm stocks and prorated 63/91 days (NASS Grain Stocks). Tons: {t26[0]/1e6:.2f} / {t26[1]/1e6:.2f} M")

    # --- haul distance to market
    om = dp["oneway_miles"]
    D["oneway_miles_to_market"] = P(om["semi_wheat_nd"], om["corn_nd"], om["region_second"],
        "UGPTI DP-284: ND corn trip 27.8 mi (T3.56, central; corn dominates in-window tonnage); ND 5-axle wheat 21.7 mi (T3.70, low); "
        "regional second-choice delivery point 41.7 mi (T3.46, high)")

    # --- payload
    bu = dp["corn_bu_per_load"]
    u = I["ugpti_2024_grain_to_elevator_share"]
    rest = 1 - u["semi5"] - u["tandem"] - u["tridem"]
    bu_ugpti = u["semi5"] * bu["semi5"] + u["tandem"] * bu["tandem"] + u["tridem"] * bu["tridem"] + rest * bu["single"]
    fs = dp["nd_fleet_share"]
    bu_fleet = (fs["single"] * bu["single"] + (fs["tandem"] + fs["other"]) * bu["tandem"] + fs["tridem"] * bu["tridem"]
                + fs["semi5"] * bu["semi5"] + fs["semi7"] * bu["semi7"])
    t = lambda b: b * 56 / 2000  # noqa: E731
    D["payload_tons_market"] = P(t(bu_fleet), t(bu_ugpti), t(bu["semi5"]),
        f"Corn bushels per load by truck type (DP-284 T3.65) weighted by share of ND grain delivered by each type "
        f"(UGPTI 2024 T12; remainder as single-axle) = {bu_ugpti:.0f} bu; low weights by ND truck count (T3.34) = {bu_fleet:.0f} bu; high = all 5-axle semis")
    D["payload_tons_field_to_bin"] = P(t(bu["tandem"]), t(bu_fleet), t(bu["semi5"]),
        "Short field-to-bin hauls use the whole farm fleet: truck-count-weighted load (DP-284 T3.34 x T3.65); low tandem, high semi")

    # --- fuel economy
    m = I["mpg"]
    D["mpg_loaded"] = P(m["class8_speed_test_low"], (m["class8_speed_test_low"] + m["class8_speed_test_high"]) / 2, m["combination_avg"],
        "ORNL TEDB T5.12 Class 8 at 25-55 mph 4.4-5.8 mpg (midpoint central); high = all-trip combination average 6.2 (T5.2)")
    D["mpg_empty"] = P(m["class8_speed_test_high"], m["combination_avg"], m["single_unit_avg"],
        "Empty return: between the Class 8 test upper value 5.8 and the single-unit average 7.6 (TEDB); central = combination average 6.2")

    # --- field-to-bin distance: geometry of a farm's fields around its yard
    sz = I["census2022"]["size_classes_harvested"]
    a_w = sum(h * h / f for f, h in sz) / sum(h for _, h in sz)
    dens = I["census2022"]["harvested_cropland_acres"] / (county_land_sqmi_total(I) * 640)
    fb = B["field_share_farmed_within_radius"]
    dist = {}
    for k in ("low", "central", "high"):
        r = math.sqrt(a_w / (math.pi * 640 * dens * fb[k]))
        dist[k] = 2 * r / 3 * MANHATTAN
    D["oneway_miles_field_to_bin"] = P(dist["high"], dist["central"], dist["low"],
        f"Acre-weighted ND farm size {a_w:,.0f} harvested acres (Census Table 9); cropland is {dens:.0%} of ND land (Census, Gazetteer); "
        "fields spread over a disk around the yard in which the farm operates a share f of cropland (BOUND 0.25-1.0); "
        "mean distance 2r/3 x 4/pi grid-road factor")

    # --- beets to receiving station
    land = county_land_sqmi()
    rrv_land = sum(land[c] for c in I["census2022"]["rrv_beet_counties"])
    b = I["beets"]
    rb = lambda n: math.sqrt(rrv_land / n / math.pi)  # noqa: E731
    D["oneway_miles_beets"] = P(2 * rb(b["nd_receiving_sites"]) / 3, 2 * rb(b["nd_receiving_sites"]) / 3 * MANHATTAN,
                                2 * rb(b["nd_receiving_sites_acs_only"]) / 3 * MANHATTAN,
        f"Land area of the 6 ND Red River Valley counties ({rrv_land:,.0f} sq mi, Census Gazetteer) / 15 ND receiving sites "
        "(ACS 12 + Minn-Dak 3) = service disk; mean distance 2r/3 x 4/pi. Low = straight-line; high = ACS sites only. "
        f"Check: news example haul {b['news_example_miles']} mi")

    # --- pickups (VIUS x Census)
    v = vius.summarize()
    notes["vius"] = {k: {kk: float(vv) for kk, vv in val.items()} for k, val in v.items()}
    trucks = I["census2022"]["trucks_incl_pickups"]
    pk = v["pickup_share_of_ag_trucks"]["p"]
    ds, mi, mpg = v["diesel_share_of_ag_pickups"], v["diesel_pickup_miles_per_year"], v["diesel_pickup_mpg"]
    g = lambda d_, m_, e_: trucks * pk * d_ * m_ * wfrac_days / 365 / e_  # noqa: E731
    per_pickup = mi["p"] * wfrac_days / 365 / mpg["p"]

    # --- livestock and fertilizer hauling
    lv = I["livestock"]
    r_auc = math.sqrt(county_land_sqmi_total(I) / lv["auction_markets"] / math.pi)
    rt_auc = 2 * (2 * r_auc / 3 * MANHATTAN)
    cs = B["calves_shipped_in_window"]
    liv = {k: lv["calf_crop"] * cs[k] / lv["head_per_load"] * rt_auc / m["combination_avg"] for k in ("low", "central", "high")}
    fz = I["fertilizer"]
    nh3_t = c26["corn"]["acres"] * fz["corn_n_lb_per_acre"] / fz["nh3_n_share"] / 2000
    fn = B["fall_share_nh3"]
    fert = {k: nh3_t * fn[k] / fz["nurse_tank_tons"] * 2 * D["oneway_miles_to_market"]["central"] / m["single_unit_avg"] for k in ("low", "central", "high")}
    D["other_ag_hauling_gal"] = P(liv["low"] + fert["low"], liv["central"] + fert["central"], liv["high"] + fert["high"],
        f"Calves: 860,000 calf crop x share shipped in window (BOUND 0-1) / 80 head per pot load x {rt_auc:.0f}-mi round trip "
        f"(ND land / 10 auction markets -> service disk) / 6.2 mpg. Fall anhydrous: corn acres x 146 lb N / 0.82 = {nh3_t/1e3:,.0f}k t NH3 "
        "x fall share (BOUND 0-1) / 2.1-t nurse tank x round trip to market distance / 7.6 mpg")

    # --- take-up
    own_t = v["own_facility_share_diesel_class6to8"]
    own_nd = v["own_facility_share_diesel_ND_all"]
    D["onhand_share_trucks"] = P(own_nd["p"], own_t["p"], own_t["hi"],
        "VIUS 2021: diesel Class 6-8 ag trucks refueled mainly at own facility = 53% (central); ND ag diesel vehicles 49% (low); upper 95% bound (high)")
    harv = county_harvested_cropland()
    border = set(I["census2022"]["mn_border_counties"]) | set(I["census2022"]["sd_border_counties"])
    bshare = sum(harv[c] for c in border) / harv["North Dakota"]
    side = statistics.mean(math.sqrt(land[c]) for c in border)
    loss = {}
    for k, miles in (("low", om["semi_wheat_nd"]), ("central", om["corn_nd"]), ("high", om["region_second"])):
        rad = miles / MANHATTAN
        xs = np.linspace(0, side, 200)
        loss[k] = bshare * float(np.mean([circle_fraction_beyond_line(x, rad) for x in xs]))
    D["border_loss_share"] = P(loss["low"], loss["central"], loss["high"],
        f"Share of ND harvested cropland in MN/SD border counties ({bshare:.0%}, Census Table 8) x average share of a delivery disk "
        f"(radius = one-way haul / 4/pi) lying across the state line for farms spread evenly across a {side:.0f}-mi-deep county")
    D["risk_acceptance"] = P(B["risk_acceptance"]["low"], B["risk_acceptance"]["central"], B["risk_acceptance"]["high"],
                             "ASSUMPTION: " + B["risk_acceptance"]["why"])

    # --- annual farm diesel
    fa = I["farm_diesel_annual"]
    dyed_price_2025 = price_summary["avg_2025_midwest"] - (params["tax"]["nd_clear_cents"] + params["tax"]["federal_cents"]
                                                          - params["tax"]["nd_dyed_cents"] - params["tax"]["lust_cents"]) / 100
    ers_gal = fa["ers_diesel_expense_2025"] / dyed_price_2025
    eia_mean = statistics.mean(fa["eia_farm_gal"])
    D["annual_farm_diesel_gal"] = P(ers_gal, (ers_gal + eia_mean) / 2, max(fa["eia_farm_gal"]),
        f"Low: ERS 2025 ND diesel expense $359.8M / ${dyed_price_2025:.2f} (EIA 2025 Midwest retail avg less highway taxes, plus dyed taxes) = {ers_gal/1e6:.0f}M gal; "
        f"high: EIA farm distillate 2020 = {max(fa['eia_farm_gal'])/1e6:.0f}M; central: mean of ERS-implied and EIA 2016-20 average ({eia_mean/1e6:.0f}M)")

    # --- road cost inflator
    rc = I["road_cost"]
    nh = rc["nhcci_2026q1"] * rc["bpi_2003"] / rc["bpi_2000"]
    cpi = rc["cpi_aug2026"] / rc["cpi_2000"]
    D["pavement_inflator"] = P(cpi, nh, nh, f"Central/high: NHCCI 2026Q1 (2003Q1=1) x FHWA Bid Price Index 2003/2000 = {nh:.2f}; low: CPI-U Aug 2026 / 2000 = {cpi:.2f}")

    notes.update({"acre_weighted_farm_size": a_w, "cropland_density": dens, "border_share_cropland": bshare,
                  "dyed_price_2025": dyed_price_2025, "per_diesel_pickup_window_gal": per_pickup,
                  "beans_share_after_sep29": beans_share, "potato_share_after_sep29": pot_share,
                  "nh3_tons": nh3_t, "auction_round_trip_mi": rt_auc})
    return D, notes


def county_land_sqmi_total(I: dict) -> float:
    return sum(county_land_sqmi().values())
