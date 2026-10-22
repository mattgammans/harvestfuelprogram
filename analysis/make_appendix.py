"""Render appendix.md: the five-parameter estimate in full (from outputs/simple_estimate.json), with the fuller model
(outputs/results.json) summarized as a cross-check."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import simple_estimate as se  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    s = json.loads((ROOT / "outputs" / "simple_estimate.json").read_text())
    full = json.loads((ROOT / "outputs" / "results.json").read_text())
    R = {r["crop"]: r for r in s["rows"]}
    out = []
    a = out.append
    a("# Appendix: the five-parameter estimate\n")
    a("Every number here is produced by `python analysis/run_all.py`; the estimate itself is in `analysis/simple_estimate.py`.\n")

    a("## A1. Policy definition\n")
    a("These are not counted as parameters:")
    a("- **Savings per gallon:** 19¢, the ND special fuel tax on clear diesel (23¢) minus the tax on dyed diesel (4¢), NDCC 57-43.2-02 and -03.")
    a("- **Window:** Sept. 29–Nov. 30, 2026 (63 days), per EO 2026-08.")
    a("- **Federal tax:** the 24.4¢ is not relieved, so federal revenue forgone is $0.")
    a("- **Eligible use:** licensed vehicles hauling agricultural products.\n")
    a("**Formula:** savings = Σ crops [production × share hauled off-farm in window] × (2 × one-way miles ÷ mpg ÷ tons per load) × $0.19\n")

    a("## A2. The five parameters\n")
    a("| # | Parameter | Corn | Soybeans | Wheat | Source |\n|---|---|---:|---:|---:|---|")
    a(f"| 1 | 2026 production (M bu) | {R['corn']['production_mbu']:.1f} | {R['soybeans']['production_mbu']:.1f} | {R['wheat']['production_mbu']:.2f} | {s['sources']['P1']} |")
    a(f"| 2 | Share hauled off-farm in window | {R['corn']['share']:.3f} | {R['soybeans']['share']:.3f} | {R['wheat']['share']:.3f} | {s['sources']['P2']} |")
    a(f"| 3 | One-way haul (mi) | {R['corn']['oneway_miles']} | {R['soybeans']['oneway_miles']} | {R['wheat']['oneway_miles']} | {s['sources']['P3']} |")
    a(f"| 4 | Tons per load | {R['corn']['tons_per_load']:.2f} | {R['soybeans']['tons_per_load']:.2f} | {R['wheat']['tons_per_load']:.2f} | {s['sources']['P4']} |")
    a(f"| 5 | Fuel economy (mpg) | {s['mpg']} | {s['mpg']} | {s['mpg']} | {s['sources']['P5']} |\n")

    a("**Parameter 2, worked out.** All figures in thousand bushels, ND on-farm stocks.")
    for y in (2024, 2025):
        st, pr = se.STOCKS[y], se.PRODUCTION_PAST[y]
        a(f"- **{y}:**")
        a(f"  - Corn: 1 − {st['corn_dec1']:,} ÷ {pr['corn']:,} = {R['corn']['share_by_year'][str(y)]:.3f}.")
        a(f"  - Soybeans: 1 − {st['soy_dec1']:,} ÷ {pr['soybeans']:,} = {R['soybeans']['share_by_year'][str(y)]:.3f}.")
        a(f"  - Wheat: ({st['wheat_sep1']:,} − {st['wheat_dec1']:,}) ÷ {pr['wheat']:,} × 63/91 = {R['wheat']['share_by_year'][str(y)]:.3f}.")
    a("- **Value used:** the average of the two years.")
    a("- **Caveat:** Dec. 1 stocks include a little old crop, and some corn is still unharvested on Dec. 1. The two push in opposite directions.\n")
    a("**Parameter 4, worked out.**")
    a("- Bushels per load by truck type come from DP-284 Table 3.65.")
    a("- Each is weighted by the share of ND grain delivered by that type (UGPTI 2024 Table 12): "
      + ", ".join(f"{k} {v:.1%}" for k, v in se.TRUCK_SHARE.items()) + ".")
    a("- Corn: " + " + ".join(f"{se.TRUCK_SHARE[k]:.3f} × {se.BU_PER_LOAD['corn'][k]}" for k in se.TRUCK_SHARE)
      + f" = {R['corn']['tons_per_load'] * 2000 / 56:.0f} bu, which is {R['corn']['tons_per_load']:.2f} tons.\n")

    a("## A3. Calculation by crop\n")
    a("| Crop | Production (t) | × share | = tons hauled | Gal/ton = 2 × mi ÷ mpg ÷ t/load | Gallons | Savings (× $0.19) |\n|---|---:|---:|---:|---|---:|---:|")
    for c in se.CROPS:
        r = R[c]
        a(f"| {c.capitalize()} | {r['tons'] / 1e6:.2f} M | {r['share']:.3f} | {r['hauled_tons'] / 1e6:.2f} M | 2 × {r['oneway_miles']} ÷ {s['mpg']} ÷ {r['tons_per_load']:.2f} = {r['gal_per_ton']:.3f} | {r['gallons'] / 1e6:.2f} M | ${r['savings'] / 1e3:,.0f}K |")
    a(f"| **Total** | | | **{sum(r['hauled_tons'] for r in s['rows']) / 1e6:.2f} M** | | **{s['total_gallons'] / 1e6:.2f} M** | **${s['total_savings'] / 1e6:.3f} M** |\n")
    a(f"**Take-up.** The total above assumes every eligible truck gallon switches. If only trucks fueled mainly from farm tanks switch "
      f"(52.8% of Class 6–8 diesel farm trucks, 2021 VIUS microdata, n≈2,300), savings are ${s['if_only_onhand_trucks'] / 1e6:.2f} million. "
      "Federal penalty exposure (at least $1,000 per violation, 26 U.S.C. §6715; no IRS relief as of Oct. 2, 2026) may lower take-up further.\n")

    a("## A4. Sensitivity (each parameter at its low and high value; all-switch basis)\n")
    a("| Input | Savings, low | Savings, high |\n|---|---:|---:|")
    for x in s["sensitivity"]:
        a(f"| {x['input']} | ${x['low'] / 1e6:.2f} M | ${x['high'] / 1e6:.2f} M |")
    a("\nThe range is driven almost entirely by haul distance and take-up. Every other input moves the total by $0.2 million or less.\n")

    a("## A5. Context\n")
    a(f"- **Per farm:** ${s['total_savings'] / 1e6:.3f}M ÷ 25,068 farms = ${s['per_farm']:.0f} (all switch), or ${s['per_farm'] * se.ONHAND_TRUCKS:.0f} at 53% take-up.")
    a(f"- **Per acre:** ÷ 16.6M acres of corn, soybeans and wheat = {100 * s['per_acre_three_crops']:.1f}¢.")
    a(f"- **Per bushel hauled:** ÷ {sum(s['hauled_bushels'].values()) / 1e6:.0f}M bushels = {s['per_bushel_hauled_cents']:.2f}¢.")
    a(f"- **Price rise:** EIA Midwest retail ${se.EIA_LATEST:.2f} (Sept. 28, 2026) − ${se.EIA_BASELINE:.2f} (Sept.–Nov. 2025 average) = ${s['price_rise']:.2f}. 19¢ is {100 * s['relief_share_of_price_rise']:.1f}% of it.")
    a(f"- **Share of the fall fuel shock:**")
    a(f"  - Fuel: corn and soybean harvest field fuel (UMN combine + grain cart: 3.44 and 3.48 gal/ac × NASS acres) + truck gallons = {s['fall_fuel_gal'] / 1e6:.1f}M gal.")
    a(f"  - Extra cost: × ${s['price_rise']:.2f} = ${s['fall_fuel_shock'] / 1e6:.0f}M.")
    a(f"  - The relief is **{100 * s['share_of_fall_fuel_shock']:.2f}%** of that (all switch), or {100 * s['share_of_fall_fuel_shock'] * se.ONHAND_TRUCKS:.2f}% at 53% take-up.")
    ef = s["example_farm"]
    a(f"- **Example farm** (1,000 ac corn + 1,000 ac soybeans, {ef['bushels']:,.0f} bu):")
    a(f"  - Hauling: {ef['onroad_gal']:,.0f} gal, so savings are ${ef['savings']:,.0f}.")
    a(f"  - Harvest field fuel: {ef['field_gal_harvest']:,.0f} gal.")
    a(f"  - Higher harvest diesel bill: ${ef['fall_diesel_increase']:,.0f}.")
    a("- **Where the forgone revenue would have gone** (NDCC 54-27-19, all-switch basis): " + "; ".join(f"{k} ${v / 1e3:,.0f}K" for k, v in s["split"].items()) + ".")
    a(f"- **Statewide diesel tax holiday:** {s['taxable_hwy_gal'] / 1e6:.1f}M gal of taxable highway diesel (FHWA MF-33SF 2024, Oct.–Nov. + 2 days) × $0.23 = ${s['holiday_cost'] / 1e6:.1f}M.")
    a(f"- **Per-acre payment at the order's cost:** ${s['total_savings'] / 1e6:.2f}M ÷ 21.8M harvested cropland acres = {s['per_acre_payment_cents']:.1f}¢.\n")
    loaded = sum(r["hauled_tons"] / r["tons_per_load"] * r["oneway_miles"] for r in s["rows"])
    a("## A6. Road-use arithmetic (order of magnitude)\n")
    a(f"- **Loaded truck miles hauling the three crops in the window:** {loaded / 1e6:.1f} million.")
    a("- **State fuel tax per loaded mile:** about 4.5¢ on clear diesel vs. under 1¢ on dyed.")
    a("- **Pavement cost:** FHWA's 2000 Highway Cost Allocation Study Addendum (Table 13) puts it at 12.7¢/mi (2000$) for an 80,000-lb 5-axle truck on rural interstates.")
    a("  - That is about 25¢ in 2026 dollars using CPI, or 41¢ using the highway construction cost index.")
    a("  - County and township roads cost more per mile.")
    a("- **For scale:** UGPTI puts local road needs at $618 million a year.\n")

    a("## A7. Cross-check: the fuller model\n")
    fc = full["components_central"]
    a("An earlier, more detailed model covers more hauling:")
    a("- Each crop's harvest timing comes from NASS Crop Progress.")
    a("- It adds sugarbeets, sunflower, dry beans and potatoes; field-to-bin trips; calves and fall anhydrous; and stored-grain sales.")
    a("- It applies the 53% farm-tank take-up and a small border loss.\n")
    a(f"It finds:")
    a(f"- {full['eligible_gal_central'] / 1e6:.1f}M eligible truck gallons, of which {fc['harvest_to_market'] / 1e6:.2f}M is harvest hauled to market and {fc['stored_small_grain_to_market'] / 1e6:.2f}M is stored grain. The five-parameter estimate covers these same hauls with {s['total_gallons'] / 1e6:.2f}M.")
    a(f"- {full['gallons_headline']['central'] / 1e6:.1f}M switched gallons (range {full['gallons_headline']['low'] / 1e6:.1f}–{full['gallons_headline']['high'] / 1e6:.1f}M).")
    a(f"- **${full['levels']['central']['fiscal']['state_revenue_forgone'] / 1e6:.2f}M** in savings, between the five-parameter estimate's 53%-take-up value (${s['if_only_onhand_trucks'] / 1e6:.2f}M) and its all-switch value (${s['total_savings'] / 1e6:.2f}M).\n")
    a("Every input of that model is listed with its source in `methods_inputs_and_calculations.docx` and `outputs/derived_params.csv`.")
    (ROOT / "appendix.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
