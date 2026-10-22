"""Bottom-up estimate of on-road ag diesel switched to dyed fuel, Sept. 29 - Nov. 30, 2026.

All uncertain parameters come from analysis/derive.py as {low, central, high}; scenarios pick each parameter's
end that lowers (raises) switched gallons. The fall farm-diesel denominator and the fleet-based cross-check are
computed at central values.
"""
from __future__ import annotations

import statistics
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_params(path: Path = ROOT / "params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def point(D: dict, level: str = "central", overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    return {k: v[overrides.get(k, level)] for k, v in D.items()}


def uncertain(D: dict) -> list[str]:
    return [k for k, v in D.items() if abs(v["high"] - v["low"]) > 1e-12]


def gal_per_ton(oneway_mi: float, payload_t: float, mpg_loaded: float, mpg_empty: float) -> float:
    """Round-trip fuel per ton delivered: loaded out, empty back."""
    return (oneway_mi / mpg_loaded + oneway_mi / mpg_empty) / payload_t


def window_tons(params: dict, p: dict) -> dict:
    c = params["inputs"]["crops_2026"]
    p27 = params["inputs"]["pct_harvested_sep27_2026"]
    return {
        "corn": c["corn"]["production_bu"] * c["corn"]["lb_per_bu"] / 2000 * (1 - p27["corn"]) * p["done_by_nov30_corn"],
        "soybeans": c["soybeans"]["production_bu"] * c["soybeans"]["lb_per_bu"] / 2000 * (1 - p27["soybeans"]) * p["done_by_nov30_soybeans"],
        "sugarbeets": c["sugarbeets"]["production_tons"] * (1 - p27["sugarbeets"]) * p["done_by_nov30_sugarbeets"],
        "other_fall": p["other_fall_crops_tons"],
        "stored_small_grain": p["stored_small_grain_tons_in_window"],
    }


def gallons(params: dict, p: dict) -> dict:
    t = window_tons(params, p)
    off_c, off_s = p["offfarm_by_dec1_corn"], p["offfarm_by_dec1_soybeans"]
    off_pool = (t["corn"] * off_c + t["soybeans"] * off_s) / (t["corn"] + t["soybeans"])
    dir_c, dir_s = min(p["direct_from_field_corn"], off_c), min(p["direct_from_field_soybeans"], off_s)
    dir_pool = (t["corn"] * dir_c + t["soybeans"] * dir_s) / (t["corn"] + t["soybeans"])
    market_t = t["corn"] * off_c + t["soybeans"] * off_s + t["other_fall"] * off_pool
    bin_t = t["corn"] * (1 - dir_c) + t["soybeans"] * (1 - dir_s) + t["other_fall"] * (1 - dir_pool)

    g_m = gal_per_ton(p["oneway_miles_to_market"], p["payload_tons_market"], p["mpg_loaded"], p["mpg_empty"])
    g_b = gal_per_ton(p["oneway_miles_field_to_bin"], p["payload_tons_field_to_bin"], p["mpg_loaded"], p["mpg_empty"])
    g_s = gal_per_ton(p["oneway_miles_beets"], p["payload_tons_market"], p["mpg_loaded"], p["mpg_empty"])
    trucks = {
        "harvest_to_market": market_t * g_m,
        "field_to_bin": bin_t * g_b,
        "sugarbeets_to_station": t["sugarbeets"] * g_s,
        "stored_small_grain_to_market": t["stored_small_grain"] * g_m,
        "livestock_and_fertilizer": p["other_ag_hauling_gal"],
    }
    # Farm pickups are excluded (VIUS sample too thin to estimate their use or fueling reliably).
    keep = (1 - p["border_loss_share"]) * p["risk_acceptance"]
    switched = sum(trucks.values()) * p["onhand_share_trucks"] * keep
    return {
        "components_eligible_gal": trucks,
        "eligible_gal": sum(trucks.values()),
        "switched_gal": switched,
        "ceiling_switched_gal": sum(trucks.values()) * p["onhand_share_trucks"] * (1 - p["border_loss_share"]),
        "tons": dict(t, market=market_t, bin=bin_t),
        "gal_per_ton": {"market": g_m, "field_to_bin": g_b, "beets": g_s},
    }


def scenarios(params: dict, D: dict) -> dict:
    names = uncertain(D)
    base = gallons(params, point(D))["switched_gal"]
    lo_over, hi_over, tornado = {}, {}, []
    for n in names:
        g_lo = gallons(params, point(D, overrides={n: "low"}))["switched_gal"]
        g_hi = gallons(params, point(D, overrides={n: "high"}))["switched_gal"]
        lo_over[n] = "low" if g_lo <= g_hi else "high"
        hi_over[n] = "high" if g_lo <= g_hi else "low"
        tornado.append({"parameter": n, "gal_at_low_value": g_lo, "gal_at_high_value": g_hi,
                        "swing_gal": abs(g_hi - g_lo), "swing_pct_of_central": abs(g_hi - g_lo) / base})
    tornado.sort(key=lambda r: -r["swing_gal"])
    return {"low": gallons(params, point(D, overrides=lo_over)), "central": gallons(params, point(D)),
            "high": gallons(params, point(D, overrides=hi_over)), "tornado": tornado}


def fall_farm_diesel(params: dict, D: dict, notes: dict, eligible_onroad: float) -> dict:
    """ND farm diesel burned in the window: harvest field work (UMN per-operation fuel x acres x share harvested in
    window) + fall tillage + fall anhydrous + eligible on-road. Livestock and other year-round uses are left out, so
    this denominator is conservative (it makes the relief look larger, not smaller)."""
    I, Bd = params["inputs"], params["bounds"]
    p = point(D)
    c, ops, nb = I["crops_2026"], I["field_ops_gal_per_acre"], I["ndsu_budgets_fuel_lube_per_acre"]
    p27 = I["pct_harvested_sep27_2026"]
    harvest_gal_ac = {"corn": ops["combine_corn"] + ops["grain_cart"], "platform": ops["combine_platform"] + ops["grain_cart"]}
    inwin = {
        "corn": (1 - p27["corn"]) * p["done_by_nov30_corn"],
        "soybeans": (1 - p27["soybeans"]) * p["done_by_nov30_soybeans"],
        "sunflower": (1 - p27["sunflower"]) * p["done_by_nov30_sunflower"],
        "dry_beans": notes["beans_share_after_sep29"],
        "sugarbeets": (1 - p27["sugarbeets"]) * p["done_by_nov30_sugarbeets"],
    }
    by_crop = {
        "corn": c["corn"]["acres"] * harvest_gal_ac["corn"] * inwin["corn"],
        "sugarbeets": c["sugarbeets"]["acres"] * harvest_gal_ac["corn"] * inwin["sugarbeets"],  # proxy: corn-head harvest fuel
        **{k: c[k]["acres"] * harvest_gal_ac["platform"] * inwin[k] for k in ("soybeans", "sunflower", "dry_beans")},
    }
    window_harvest = sum(by_crop.values())
    tillage = I["census2022"]["intensive_tillage_acres"] * ops["chisel"] * Bd["fall_share_intensive_tillage"]["central"]
    nh3 = c["corn"]["acres"] * ops["anhydrous_isu"] * Bd["fall_share_nh3"]["central"]

    # Consistency checks against the annual total: NDSU budget fuel per acre x acres, and the farm truck fleet.
    per_gal = nb["diesel_price"] * (1 + nb["lube_share"])
    gal_ac = {k: statistics.mean(v) / per_gal for k, v in nb.items() if isinstance(v, list)}
    annual_crop = sum(c[k]["acres"] * gal_ac[k] for k in gal_ac)
    dp, m, v = I["dp284"], I["mpg"], notes["vius"]
    trucks = I["census2022"]["trucks_incl_pickups"]
    grain_trucks = trucks * (1 - v["pickup_share_of_ag_trucks"]["p"])
    fs, mi = dp["nd_fleet_share"], dp["annual_miles"]
    su, cb = m["single_unit_avg"], m["combination_avg"]
    per_truck = (fs["single"] * mi["single"] / su + (fs["tandem"] + fs["other"]) * mi["tandem"] / su + fs["tridem"] * mi["tridem"] / su
                 + fs["semi5"] * mi["semi5"] / cb + fs["semi7"] * mi["semi7"] / cb)
    fleet_grain_annual = grain_trucks * per_truck
    pickups_annual = (trucks * v["pickup_share_of_ag_trucks"]["p"] * v["diesel_share_of_ag_pickups"]["p"]
                      * v["diesel_pickup_miles_per_year"]["p"] / v["diesel_pickup_mpg"]["p"])
    annual = p["annual_farm_diesel_gal"]
    window_total = window_harvest + tillage + nh3 + eligible_onroad
    return {
        "harvest_gal_per_acre": harvest_gal_ac, "inwindow_harvest_share": inwin, "window_harvest_by_crop": by_crop,
        "window_harvest_gal": window_harvest, "window_tillage_gal": tillage, "window_nh3_gal": nh3,
        "window_onroad_eligible_gal": eligible_onroad, "window_farm_diesel_gal": window_total,
        "annual_farm_diesel_gal": annual, "window_share_of_annual": window_total / annual,
        "ndsu_gal_per_acre": gal_ac, "ndsu_implied_annual_crop_gal": annual_crop,
        "fleet_grain_trucks": grain_trucks, "fleet_grain_truck_annual_gal": fleet_grain_annual,
        "pickups_annual_gal": pickups_annual, "onroad_share_of_annual": (fleet_grain_annual + pickups_annual) / annual,
    }


def fleet_crosscheck(params: dict, D: dict, fall: dict, central: dict) -> dict:
    """Independent of haul distance/payload/mpg: fleet annual truck fuel x window share of annual crop tonnage moved."""
    c = params["inputs"]["crops_2026"]
    ann_t = (c["corn"]["production_bu"] * 56 + c["soybeans"]["production_bu"] * 60) / 2000 + c["sugarbeets"]["production_tons"] \
        + (c["spring_wheat"]["production_bu"] + c["durum"]["production_bu"]) * 60 / 2000 + c["barley"]["production_bu"] * 48 / 2000 \
        + c["canola"]["production_lb_2025"] / 2000 + c["sunflower"]["production_lb_2025"] / 2000 \
        + c["dry_beans"]["production_cwt"] * 100 / 2000 + c["potatoes"]["production_cwt_2025"] * 100 / 2000
    t = central["tons"]
    win_t = t["market"] + t["sugarbeets"] + t["stored_small_grain"]
    share = win_t / ann_t
    fleet_window = fall["fleet_grain_truck_annual_gal"] * share
    bottom_up = sum(central["components_eligible_gal"][k] for k in ("harvest_to_market", "sugarbeets_to_station", "stored_small_grain_to_market"))
    return {"annual_crop_tons": ann_t, "window_market_tons": win_t, "window_share_of_tonnage": share,
            "fleet_based_window_gal": fleet_window, "bottom_up_same_legs_gal": bottom_up}
