"""Assemble content for the Word methods document (inputs table + calculation walk-through) from the model run.
Writes outputs/methods_doc.json; analysis/make_methods_docx.js renders it."""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derive  # noqa: E402
import model  # noqa: E402
from btn_figures import category_values  # noqa: E402
from btn_text import URL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def M(x, d=2):
    return f"{x / 1e6:,.{d}f} million"


def rng(lo, c, hi, f):
    return f"{f(c)} ({f(lo)}–{f(hi)})" if abs(hi - lo) > 1e-9 else f(c)


def main() -> None:
    r = json.loads((ROOT / "outputs" / "results.json").read_text())
    p = model.load_params()
    I, B = p["inputs"], p["bounds"]
    Dr = r["derived"]
    D = {k: v["central"] for k, v in Dr.items()}
    n, ps, fall, xc = r["notes"], r["prices"], r["fall_farm_diesel"], r["fleet_crosscheck"]
    c26, p27, hist = I["crops_2026"], I["pct_harvested_sep27_2026"], I["pct_harvested_late_nov_history"]
    gs, prod, hv = I["grain_stocks_onfarm_1000bu"], I["production_1000bu"], I["harvested_by_dec1_share"]
    comp, t = r["components_central"], r["tons_central"]
    cen, lo, hi = r["levels"]["central"], r["levels"]["low"], r["levels"]["high"]
    v = n["vius"]
    ops = I["field_ops_gal_per_acre"]
    land = derive.county_land_sqmi()
    rrv = sum(land[x] for x in I["census2022"]["rrv_beet_counties"])
    gm, gb, gbt = (r["gal_per_ton_central"][k] for k in ("market", "field_to_bin", "beets"))
    keep = (1 - D["border_loss_share"]) * D["risk_acceptance"]
    tf = D["onhand_share_trucks"] * keep
    liv = I["livestock"]["calf_crop"] * 0.5 / I["livestock"]["head_per_load"] * n["auction_round_trip_mi"] / I["mpg"]["combination_avg"]
    fert = comp["livestock_and_fertilizer"] - liv
    pct = lambda x: f"{x:.0%}"  # noqa: E731
    pct1 = lambda x: f"{x:.1%}"  # noqa: E731
    num1 = lambda x: f"{x:.1f}"  # noqa: E731
    mt = lambda x: M(x, 2)  # noqa: E731

    def row(group, name, value, kind, source, key=None):
        return {"group": group, "input": name, "value": value, "kind": kind, "source": source, "url": URL.get(key) if key else None}

    rows = [
        row("Policy and prices", "ND tax, clear diesel / dyed diesel", "23¢ / 4¢ per gal (difference 19¢)", "Sourced", "NDCC 57-43.2-02, -03", "ndcc57"),
        row("Policy and prices", "Federal diesel tax (not relieved)", "24.4¢ per gal", "Sourced", "Governor's release 9/29/2026; 26 U.S.C. 4081; IRS IR-2024-265 precedent", "release"),
        row("Policy and prices", "Window covered by the order", "Sept. 29–Nov. 30, 2026 (63 days)", "Sourced", "Executive Order 2026-08", "eo"),
        row("Policy and prices", "Midwest retail diesel, fall 2025 average / Sept. 28, 2026", f"${ps['baseline_midwest']:.2f} / ${ps['latest_midwest']:.2f} (rise ${ps['shock_midwest']:.2f})", "Sourced", "EIA weekly retail diesel, PADD 2", "eia_mw"),
        row("Crops", "2026 production forecasts", f"Corn {c26['corn']['production_bu'] / 1e6:.1f}M bu; soybeans {c26['soybeans']['production_bu'] / 1e6:.1f}M bu; sugarbeets {c26['sugarbeets']['production_tons'] / 1e6:.2f}M t; dry beans {c26['dry_beans']['production_cwt'] / 1e6:.2f}M cwt", "Sourced", "NASS Crop Production, Sept. 11 and Aug. 12, 2026", "crop0926"),
        row("Crops", "Sunflower and potatoes (no 2026 forecast yet)", f"Sunflower {c26['sunflower']['production_lb_2025'] / 1e6:,.0f}M lb × 2026/2025 acres ({c26['sunflower']['acres'] / 1e6:.3f}/{c26['sunflower']['acres_2025'] / 1e6:.3f}M); potatoes {c26['potatoes']['production_cwt_2025'] / 1e6:.2f}M cwt (2025)", "Sourced (proxy year)", "NASS Crop Production 2025 Summary; NASS Acreage, June 2026", "cropan"),
        row("Crops", "Share harvested by Sept. 27, 2026", f"Corn {pct(p27['corn'])}; soybeans {pct(p27['soybeans'])}; sugarbeets {pct(p27['sugarbeets'])}; sunflower {pct(p27['sunflower'])}", "Sourced", "NASS Crop Progress, Sept. 28, 2026", "prog3926"),
        row("Crops", "Share of remaining harvest done by Nov. 30", f"Corn {rng(Dr['done_by_nov30_corn']['low'], D['done_by_nov30_corn'], Dr['done_by_nov30_corn']['high'], pct)}; soybeans {pct(D['done_by_nov30_soybeans'])}; beets {pct(D['done_by_nov30_sugarbeets'])}", "Calculated", "NASS Crop Progress 2016–2025, ND late-November values (median; 10th–90th percentile)", "progress"),
        row("Crops", "Dry beans and potatoes harvested after Sept. 29", f"Dry beans {pct(n['beans_share_after_sep29'])}; potatoes {pct(n['potato_share_after_sep29'])}", "Calculated", "NASS Usual Planting and Harvesting Dates (2010), ND; interpolated between the 5/15/85/95% dates", "usual"),
        row("Crops", "Share of crop off the farm by Dec. 1", f"Corn {rng(Dr['offfarm_by_dec1_corn']['low'], D['offfarm_by_dec1_corn'], Dr['offfarm_by_dec1_corn']['high'], pct)}; soybeans {rng(Dr['offfarm_by_dec1_soybeans']['low'], D['offfarm_by_dec1_soybeans'], Dr['offfarm_by_dec1_soybeans']['high'], pct)}", "Calculated", "1 − Dec. 1 on-farm stocks ÷ (production × share harvested), 2024 and 2025; NASS Grain Stocks and Crop Production", "stocks"),
        row("Crops", "Share hauled straight from field at harvest", "Corn 33%; soybeans 66%", "Sourced", "UGPTI DP-284 (Vachal 2015), p. 11 (soybean value is regional)", "dp284"),
        row("Crops", "On-farm wheat and barley stocks, Sept. 1, 2026; Sept.–Dec. decline", f"Wheat {gs['y2026']['wheat_sep1'] / 1e3:.0f}M bu, barley {gs['y2026']['barley_sep1'] / 1e3:.1f}M bu; wheat fell 22–24% Sept. 1–Dec. 1 in 2024–25", "Sourced", "NASS Grain Stocks (Sept. 2024, 2025, 2026; Jan. 2025, 2026)", "stocks"),
        row("Hauling", "One-way miles to elevator or plant", rng(Dr['oneway_miles_to_market']['low'], D['oneway_miles_to_market'], Dr['oneway_miles_to_market']['high'], num1), "Sourced", "UGPTI DP-284: ND corn trip (T3.56); ND semi wheat trip (T3.70, low); regional second-choice point (T3.46, high)", "dp284"),
        row("Hauling", "Tons per load (fleet-weighted)", rng(Dr['payload_tons_market']['low'], D['payload_tons_market'], Dr['payload_tons_market']['high'], num1), "Calculated", "Bushels per load by truck type (DP-284 T3.65) × share of ND grain each type hauls (UGPTI 2024 Infrastructure Needs, T12)", "ugpti24"),
        row("Hauling", "Fuel economy, loaded / empty (mpg)", f"{rng(Dr['mpg_loaded']['low'], D['mpg_loaded'], Dr['mpg_loaded']['high'], num1)} / {rng(Dr['mpg_empty']['low'], D['mpg_empty'], Dr['mpg_empty']['high'], num1)}", "Sourced", "ORNL Transportation Energy Data Book Ed. 40, Tables 5.1, 5.2, 5.12", "tedb"),
        row("Hauling", "Sugarbeet one-way miles to receiving station", rng(Dr['oneway_miles_beets']['low'], D['oneway_miles_beets'], Dr['oneway_miles_beets']['high'], num1), "Calculated", f"Land area of 6 RRV counties ({rrv:,.0f} sq mi, Census Gazetteer) ÷ 15 ND receiving sites (American Crystal 12, Minn-Dak 3); mean trip ⅔ radius × 4/π", "gazetteer"),
        row("Hauling", "Field-to-bin one-way miles", rng(Dr['oneway_miles_field_to_bin']['low'], D['oneway_miles_field_to_bin'], Dr['oneway_miles_field_to_bin']['high'], num1), "Calculated + bound", f"Acre-weighted farm size {n['acre_weighted_farm_size']:,.0f} ac (Census Table 9); cropland {pct(n['cropland_density'])} of ND land; farm operates 50% of nearby cropland (bound 25–100%)", "census"),
        row("Calves and fertilizer", "Calves shipped in window", f"{I['livestock']['calf_crop']:,} calf crop × 50% (bound 0–100%)", "Sourced + bound", "NASS Cattle, Jan. 2026; no monthly shipment data published", None),
        row("Calves and fertilizer", "Calves per load; trip length", f"{I['livestock']['head_per_load']} head; {n['auction_round_trip_mi']:.0f}-mile round trip", "Sourced / calculated", "OSU Beef Team (pot load ~80 head of 500-lb calves); ND land ÷ 10 licensed cattle auctions (NDDA)", "ndda_auction"),
        row("Calves and fertilizer", "Fall anhydrous ammonia hauled", f"{n['nh3_tons'] / 1e3:,.0f}k t NH3 × 50% fall (bound 0–100%); 2.1-t nurse tanks; {2 * D['oneway_miles_to_market']:.0f}-mi round trip; 7.6 mpg", "Calculated + bound", "Corn acres × 146 lb N/ac (USDA ERS) ÷ 82% N; NDSU bars fall NH3 before Oct. 1", "ers_fert"),
        row("Switching", "Heavy farm trucks fueled from own tanks", rng(Dr['onhand_share_trucks']['low'], D['onhand_share_trucks'], Dr['onhand_share_trucks']['high'], pct), "Sourced (proxy)", "2021 VIUS microdata, Class 6–8 diesel farm trucks (n≈2,300); ND-only 64%, Northern Plains 47%", "vius"),
        row("Switching", "Hauls not crossing into MN/SD", rng(1 - Dr['border_loss_share']['high'], 1 - D['border_loss_share'], 1 - Dr['border_loss_share']['low'], pct1), "Calculated", f"{pct(n['border_share_cropland'])} of ND cropland in border counties (Census Table 8) × share of delivery circle across the line", "census_cty"),
        row("Switching", "Farmers willing to take federal penalty risk", "100%", "Assumption", "Upper bound; no IRS relief as of Oct. 2, 2026 (penalty ≥ $1,000 or $10/gal)", "usc6715"),
        row("Switching", "Farm pickups", "Excluded", "Scope choice", "VIUS diesel farm pickup sample too thin (effective n ≈ 12); biases totals down", None),
        row("Context", "Harvest fuel per acre (combine + grain cart)", f"Corn/beets {fall['harvest_gal_per_acre']['corn']:.2f}; soybeans/sunflower/dry beans {fall['harvest_gal_per_acre']['platform']:.2f} gal/ac", "Sourced", "UMN Machinery Cost Estimates, July 2024", "umn"),
        row("Context", "Fall tillage and fall anhydrous field fuel", f"{I['census2022']['intensive_tillage_acres'] / 1e6:.2f}M intensive-till ac × {ops['chisel']} gal × 50%; corn ac × {ops['anhydrous_isu']} gal × 50%", "Sourced + bound", "Census Table 47; UMN; ISU PM 709; fall shares bounded 0–100%", "isu709"),
        row("Context", "Annual ND farm diesel", rng(Dr['annual_farm_diesel_gal']['low'], D['annual_farm_diesel_gal'], Dr['annual_farm_diesel_gal']['high'], lambda x: f"{x / 1e6:.0f}M gal"), "Calculated", f"ERS 2025 ND diesel expense $359.8M ÷ ${n['dyed_price_2025']:.2f}/gal (low); EIA farm distillate 2016–20 (avg) and 2020 (high)", "ers_fiws"),
        row("Context", "ND farms; harvested cropland", f"{I['census2022']['farms']:,} farms; {I['census2022']['harvested_cropland_acres'] / 1e6:.1f}M acres", "Sourced", "2022 Census of Agriculture, Table 1", "census"),
        row("Context", "Highway Tax Distribution Fund split", "State 60%; counties 35% (27% of that to cities); townships 3.4%; transit 1.6%", "Sourced", "NDCC 54-27-19", "ndcc54"),
        row("Context", "ND taxable highway diesel, Oct.–Nov. (+2 Sept. days)", M(r['alternatives']['taxable_highway_diesel_in_window_gal'], 1) + " gal", "Sourced", "FHWA Highway Statistics 2024, Table MF-33SF", "fhwa24"),
    ]

    cats = category_values(r)
    tot_e, tot_s = sum(c[1] for c in cats), sum(c[2] for c in cats)
    hs = fall["window_harvest_by_crop"]
    tons_corn = c26["corn"]["production_bu"] * 56 / 2000
    tons_soy = c26["soybeans"]["production_bu"] * 60 / 2000
    steps = [
        {"title": "Step 1. Value per gallon",
         "lines": ["Savings per gallon = ND clear tax − ND dyed tax = 23¢ − 4¢ = 19¢.",
                   "The 24.4¢ federal tax is not relieved, so it is not counted. Federal revenue forgone = $0.",
                   f"Price rise = ${ps['latest_midwest']:.2f} − ${ps['baseline_midwest']:.2f} = ${ps['shock_midwest']:.2f}/gal; 19¢ ÷ ${ps['shock_midwest']:.2f} = {100 * 0.19 / ps['shock_midwest']:.1f}% of the rise on a covered gallon."]},
        {"title": "Step 2. Tons harvested inside the window",
         "lines": ["Tons in window = production (tons) × share not yet harvested on Sept. 27 × share of the remainder done by Nov. 30.",
                   f"Corn: {tons_corn / 1e6:.2f}M t × {1 - p27['corn']:.2f} × {D['done_by_nov30_corn']:.3f} = {mt(t['corn'])} t.",
                   f"Soybeans: {tons_soy / 1e6:.2f}M t × {1 - p27['soybeans']:.2f} × {D['done_by_nov30_soybeans']:.3f} = {mt(t['soybeans'])} t.",
                   f"Sugarbeets: {c26['sugarbeets']['production_tons'] / 1e6:.2f}M t × {1 - p27['sugarbeets']:.2f} × {D['done_by_nov30_sugarbeets']:.3f} = {mt(t['sugarbeets'])} t.",
                   f"Sunflower, dry beans, potatoes (other fall crops) = {mt(t['other_fall'])} t."]},
        {"title": "Step 3. Fuel per ton hauled",
         "lines": ["Gallons per ton = (one-way miles ÷ loaded mpg + one-way miles ÷ empty mpg) ÷ tons per load.",
                   f"To elevator/plant: ({D['oneway_miles_to_market']:.1f} ÷ {D['mpg_loaded']:.1f} + {D['oneway_miles_to_market']:.1f} ÷ {D['mpg_empty']:.1f}) ÷ {D['payload_tons_market']:.2f} = {gm:.3f} gal/t.",
                   f"Sugarbeets to station: ({D['oneway_miles_beets']:.1f} ÷ {D['mpg_loaded']:.1f} + {D['oneway_miles_beets']:.1f} ÷ {D['mpg_empty']:.1f}) ÷ {D['payload_tons_market']:.2f} = {gbt:.3f} gal/t.",
                   f"Field to bin: ({D['oneway_miles_field_to_bin']:.2f} ÷ {D['mpg_loaded']:.1f} + {D['oneway_miles_field_to_bin']:.2f} ÷ {D['mpg_empty']:.1f}) ÷ {D['payload_tons_field_to_bin']:.2f} = {gb:.3f} gal/t."]},
        {"title": f"Step 4. Category A: hauling the fall harvest = {M(cats[0][1], 2)} gal",
         "lines": [f"Tons to market = corn {mt(t['corn'])} × {D['offfarm_by_dec1_corn']:.3f} + soybeans {mt(t['soybeans'])} × {D['offfarm_by_dec1_soybeans']:.3f} + other fall crops at the pooled share = {mt(t['market'])} t.",
                   f"To market: {mt(t['market'])} t × {gm:.3f} = {mt(comp['harvest_to_market'])} gal.",
                   f"Sugarbeets: {mt(t['sugarbeets'])} t × {gbt:.3f} = {mt(comp['sugarbeets_to_station'])} gal.",
                   f"Into bins: tons not hauled straight from the field (corn 67%, soybeans {1 - min(D['direct_from_field_soybeans'], D['offfarm_by_dec1_soybeans']):.0%}) = {mt(t['bin'])} t × {gb:.3f} = {mt(comp['field_to_bin'])} gal.",
                   f"Total A = {mt(cats[0][1])} gal."]},
        {"title": f"Step 5. Category B: calves and fertilizer = {M(comp['livestock_and_fertilizer'], 2)} gal",
         "lines": [f"Calves: {I['livestock']['calf_crop']:,} × 50% ÷ {I['livestock']['head_per_load']} head per load × {n['auction_round_trip_mi']:.0f} mi ÷ 6.2 mpg = {M(liv, 3)} gal.",
                   f"Anhydrous: {c26['corn']['acres'] / 1e6:.2f}M ac × 146 lb N ÷ 0.82 ÷ 2,000 = {n['nh3_tons'] / 1e3:,.0f}k t × 50% ÷ 2.1 t per tank × {2 * D['oneway_miles_to_market']:.1f} mi ÷ 7.6 mpg = {M(fert, 3)} gal."]},
        {"title": f"Step 6. Category C: selling stored wheat and barley = {M(comp['stored_small_grain_to_market'], 2)} gal",
         "lines": [f"Sept. 1–Dec. 1 decline in ND on-farm stocks: wheat {', '.join(f'{(gs[y]['wheat_sep1'] - gs[y]['wheat_dec1']) / gs[y]['wheat_sep1']:.1%} ({y[1:]})' for y in ('y2024', 'y2025'))}; barley {', '.join(f'{(gs[y]['barley_sep1'] - gs[y]['barley_dec1']) / gs[y]['barley_sep1']:.1%} ({y[1:]})' for y in ('y2024', 'y2025'))}.",
                   f"Each year's rates × 2026 Sept. 1 stocks (wheat {gs['y2026']['wheat_sep1'] / 1e3:.0f}M bu at 60 lb, barley {gs['y2026']['barley_sep1'] / 1e3:.1f}M bu at 48 lb) × 63/91 days, averaged over the two years = {mt(t['stored_small_grain'])} t.",
                   f"{mt(t['stored_small_grain'])} t × {gm:.3f} gal/t = {mt(comp['stored_small_grain_to_market'])} gal."]},
        {"title": f"Step 7. Eligible on-road truck gallons = {M(tot_e, 2)}",
         "lines": [f"A + B + C = {mt(cats[0][1])} + {mt(cats[1][1])} + {mt(cats[2][1])} = {mt(tot_e)} gal. Farm pickups are excluded."]},
        {"title": f"Step 8. Gallons switched to dyed fuel = {M(tot_s, 2)}",
         "lines": [f"Share switching = fueled from farm tanks {D['onhand_share_trucks']:.3f} × staying in ND {1 - D['border_loss_share']:.3f} × willing to take federal risk {D['risk_acceptance']:.2f} = {tf:.3f}.",
                   f"Switched = {mt(tot_e)} × {tf:.3f} = {mt(tot_s)} gal.",
                   "Federal risk: the governor's order covers state penalties only. Until the IRS grants relief, a truck caught with dyed fuel on a public road faces a federal penalty of $1,000 or $10 a gallon, whichever is greater. Assuming every farmer accepts that risk makes this an upper bound on this factor."]},
        {"title": f"Step 9. State revenue forgone = ${cen['fiscal']['state_revenue_forgone'] / 1e6:.2f} million",
         "lines": [f"{mt(tot_s)} gal × $0.19 = ${cen['fiscal']['state_revenue_forgone'] / 1e6:.3f} million.",
                   "Split (NDCC 54-27-19): " + "; ".join(f"{k.replace('_', ' ')} ${v / 1e3:,.0f}K" for k, v in cen['fiscal']['split'].items()) + "."]},
        {"title": "Step 10. Context",
         "lines": [f"Fall farm diesel = harvest field work {M(fall['window_harvest_gal'], 1)} + fall tillage {M(fall['window_tillage_gal'], 1)} + fall anhydrous {M(fall['window_nh3_gal'], 1)} + on-road {M(fall['window_onroad_eligible_gal'], 1)} = {M(fall['window_farm_diesel_gal'], 1)} gal ({fall['window_share_of_annual']:.0%} of annual).",
                   f"Harvest field work by crop: " + "; ".join(f"{k.replace('_', ' ')} {M(v, 1)}" for k, v in hs.items()) + ".",
                   f"Extra cost from price rise = {M(fall['window_farm_diesel_gal'], 1)} × ${ps['shock_midwest']:.2f} = ${cen['context']['shock_cost_all_farm_diesel'] / 1e6:.0f} million; relief ÷ extra cost = {100 * cen['context']['relief_share_of_total_farm_fuel_shock']:.2f}%.",
                   f"Per farm = ${cen['fiscal']['state_revenue_forgone']:,.0f} ÷ {I['census2022']['farms']:,} = ${cen['context']['per_farm']:.0f}. Per fall-crop acre = {100 * cen['context']['per_fall_crop_acre']:.1f}¢. Per bushel of corn and soybeans harvested in window = {cen['context']['per_bushel_corn_soy_cents']:.3f}¢."]},
        {"title": "Step 11. Example farm (1,000 ac corn + 1,000 ac soybeans)",
         "lines": [f"Bushels = 1,000 × 130 + 1,000 × 30 = {r['example_farm']['bushels']:,.0f}. Same shares and fuel per ton as Steps 2–4.",
                   f"On-road truck fuel = {r['example_farm']['haul_gal']:,.0f} gal; savings = {r['example_farm']['haul_gal']:,.0f} × $0.19 = ${r['example_farm']['savings']:,.0f}.",
                   f"Fall field fuel = 1,000 × {fall['harvest_gal_per_acre']['corn']:.2f} × {fall['inwindow_harvest_share']['corn']:.2f} + 1,000 × {fall['harvest_gal_per_acre']['platform']:.2f} × {fall['inwindow_harvest_share']['soybeans']:.3f} = {r['example_farm']['field_gal']:,.0f} gal.",
                   f"Higher fall diesel bill = ({r['example_farm']['haul_gal']:,.0f} + {r['example_farm']['field_gal']:,.0f}) × ${ps['shock_midwest']:.2f} = ${r['example_farm']['shock_cost_fall_diesel']:,.0f}."]},
        {"title": "Step 12. Range and cross-check",
         "lines": [f"Each input is moved to its low and high value one at a time. The log changes in switched gallons are combined in quadrature (inputs treated as independent): {M(r['gallons_headline']['low'], 1)}–{M(r['gallons_headline']['high'], 1)} gal, ${lo['fiscal']['state_revenue_forgone'] / 1e6:.2f}–{hi['fiscal']['state_revenue_forgone'] / 1e6:.2f} million. All inputs at their extremes together: ${r['levels_corners']['low'] / 1e6:.2f}–{r['levels_corners']['high'] / 1e6:.2f} million.",
                   f"Fleet cross-check: {fall['fleet_grain_trucks']:,.0f} non-pickup farm trucks × UGPTI annual miles by type ÷ ORNL mpg = {M(fall['fleet_grain_truck_annual_gal'], 1)} gal/yr × {xc['window_share_of_tonnage']:.0%} of the year's crop tonnage moved in window = {M(xc['fleet_based_window_gal'], 1)} gal, vs. {M(xc['bottom_up_same_legs_gal'], 1)} gal bottom-up for the same hauls."]},
    ]
    sens = [{"input": row_["parameter"], "low": row_["gal_at_low_value"] / 1e6, "high": row_["gal_at_high_value"] / 1e6,
             "swing": 100 * row_["swing_pct_of_central"]} for row_ in r["tornado"][:10]]
    summary = [[c[0], M(c[1], 2), f"{c[2] / c[1]:.0%}", M(c[2], 2), f"${c[2] * 0.19 / 1e3:,.0f}K"] for c in cats]
    summary.append(["Total", M(tot_e, 2), f"{tot_s / tot_e:.0%}", M(tot_s, 2), f"${tot_s * 0.19 / 1e6:.2f}M"])
    out = {"date": "October 2, 2026", "rows": rows, "steps": steps, "summary": summary, "sens": sens,
           "central_gal": tot_s, "revenue": cen["fiscal"]["state_revenue_forgone"]}
    (ROOT / "outputs" / "methods_doc.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
