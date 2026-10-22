"""Foregone revenue, fund split, and the relief put in context (per farm / acre / bushel, share of price shock)."""
from __future__ import annotations

from model import gal_per_ton


def fiscal(switched_gal: float, params: dict) -> dict:
    cost = switched_gal * params["tax"]["relief_cents"] / 100
    s = params["htdf_split"]
    county_pool = cost * s["counties_and_cities"]
    return {
        "state_revenue_forgone": cost,
        "split": {
            "state_highway_fund": cost * s["state_highway_fund"],
            "counties": county_pool * (1 - s["city_share_of_county"]),
            "cities": county_pool * s["city_share_of_county"],
            "townships": cost * s["townships"],
            "public_transit": cost * s["public_transit"],
        },
        "federal_revenue_forgone": 0.0,  # 24.4c still owed; no IRS relief (memo_critical_facts.md)
    }


def context(switched_gal: float, tons: dict, params: dict, prices: dict, window_farm_diesel: float) -> dict:
    relief = params["tax"]["relief_cents"] / 100
    savings = switched_gal * relief
    c = params["inputs"]["crops_2026"]
    fall_acres = c["corn"]["acres"] + c["soybeans"]["acres"] + c["sugarbeets"]["acres"]
    corn_soy_bu = tons["corn"] * 2000 / c["corn"]["lb_per_bu"] + tons["soybeans"] * 2000 / c["soybeans"]["lb_per_bu"]
    shock = prices["shock_midwest"]
    return {
        "savings_total": savings,
        "per_farm": savings / params["inputs"]["census2022"]["farms"],
        "per_fall_crop_acre": savings / fall_acres,
        "per_cropland_acre": savings / params["inputs"]["census2022"]["harvested_cropland_acres"],
        "per_bushel_corn_soy_cents": 100 * savings / corn_soy_bu,
        "relief_share_of_shock_on_covered_gal": relief / shock,
        "window_farm_diesel_gal": window_farm_diesel,
        "shock_cost_all_farm_diesel": window_farm_diesel * shock,
        "relief_share_of_total_farm_fuel_shock": savings / (window_farm_diesel * shock),
    }


def road(params: dict, p: dict, tons: dict, switched_share_trucks: float) -> dict:
    """Order-of-magnitude pavement cost vs. fuel tax per loaded semi-mile, market legs only."""
    rc = params["inputs"]["road_cost"]
    loaded_miles = (tons["market"] + tons["stored_small_grain"]) / p["payload_tons_market"] * p["oneway_miles_to_market"] \
        + tons["sugarbeets"] / p["payload_tons_market"] * p["oneway_miles_beets"]
    pave = rc["pavement_cents_80kip_rural_interstate_2000"] * p["pavement_inflator"]
    t = params["tax"]
    return {
        "loaded_market_miles": loaded_miles,
        "loaded_miles_switched": loaded_miles * switched_share_trucks,
        "pavement_cents_per_mile_2026": pave,
        "state_tax_cents_per_loaded_mile": {"clear": t["nd_clear_cents"] / p["mpg_loaded"], "dyed": t["nd_dyed_cents"] / p["mpg_loaded"]},
        "pavement_cost_loaded_market_miles": loaded_miles * pave / 100,
        "local_road_needs_per_year": rc["local_road_needs_per_year"],
    }


def example_farm(params: dict, p: dict, fall: dict, notes: dict, shock: float) -> dict:
    """A 1,000-ac corn + 1,000-ac soybean operation at 2026 state forecast yields and central logistics."""
    I = params["inputs"]
    c, f = I["crops_2026"], I["example_farm"]
    p27 = I["pct_harvested_sep27_2026"]
    bu_c = f["corn_acres"] * c["corn"]["production_bu"] / c["corn"]["acres"]
    bu_s = f["soy_acres"] * c["soybeans"]["production_bu"] / c["soybeans"]["acres"]
    t_c = bu_c * 56 / 2000 * (1 - p27["corn"]) * p["done_by_nov30_corn"]
    t_s = bu_s * 60 / 2000 * (1 - p27["soybeans"]) * p["done_by_nov30_soybeans"]
    g_m = gal_per_ton(p["oneway_miles_to_market"], p["payload_tons_market"], p["mpg_loaded"], p["mpg_empty"])
    g_b = gal_per_ton(p["oneway_miles_field_to_bin"], p["payload_tons_field_to_bin"], p["mpg_loaded"], p["mpg_empty"])
    dc = min(p["direct_from_field_corn"], p["offfarm_by_dec1_corn"])
    ds = min(p["direct_from_field_soybeans"], p["offfarm_by_dec1_soybeans"])
    haul = (t_c * p["offfarm_by_dec1_corn"] + t_s * p["offfarm_by_dec1_soybeans"]) * g_m + (t_c * (1 - dc) + t_s * (1 - ds)) * g_b
    onroad = haul  # trucks only; pickups excluded
    hg, iw = fall["harvest_gal_per_acre"], fall["inwindow_harvest_share"]
    field = f["corn_acres"] * hg["corn"] * iw["corn"] + f["soy_acres"] * hg["platform"] * iw["soybeans"]
    relief = params["tax"]["relief_cents"] / 100
    return {"bushels": bu_c + bu_s, "haul_gal": haul, "onroad_gal": onroad, "field_gal": field,
            "savings": onroad * relief, "shock_cost_fall_diesel": (onroad + field) * shock,
            "savings_share_of_shock": onroad * relief / ((onroad + field) * shock)}


def alternatives(params: dict, switched_gal: float) -> dict:
    t, m = params["tax"], params["inputs"]["fhwa_mf33sf_2024_gal"]
    hwy = m["oct"] + m["nov"] + m["sep"] * 2 / 30
    return {
        "taxable_highway_diesel_in_window_gal": hwy,
        "eo_state_cost": switched_gal * t["relief_cents"] / 100,
        "statewide_diesel_holiday_23c": hwy * t["nd_clear_cents"] / 100,
        "per_acre_payment_equal_cost_cents": 100 * switched_gal * t["relief_cents"] / 100
        / params["inputs"]["census2022"]["harvested_cropland_acres"],
    }
