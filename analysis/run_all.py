"""One command: `python analysis/run_all.py`. Writes everything under outputs/ and regenerates appendix.md."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import derive  # noqa: E402
import fiscal  # noqa: E402
import model  # noqa: E402
import prices  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def quadrature_bounds(central: float, tornado: list[dict]) -> tuple[float, float]:
    """Headline low/high: one-way log swings combined in quadrature (parameters treated as independent)."""
    down = math.sqrt(sum(math.log(central / min(r["gal_at_low_value"], r["gal_at_high_value"])) ** 2 for r in tornado))
    up = math.sqrt(sum(math.log(max(r["gal_at_low_value"], r["gal_at_high_value"]) / central) ** 2 for r in tornado))
    return central * math.exp(-down), central * math.exp(up)


def main() -> dict:
    OUT.mkdir(exist_ok=True)
    params = model.load_params()

    w = prices.load_weekly()
    w.to_csv(OUT / "prices_weekly.csv")
    ps = prices.summarize(w, params)
    prices.figure(w, ps, params["tax"]["relief_cents"] / 100, OUT / "fig_prices.png")

    D, notes = derive.derive(params, ps)
    pd.DataFrame([{"parameter": k, **v} for k, v in D.items()]).to_csv(OUT / "derived_params.csv", index=False)

    sc = model.scenarios(params, D)
    cen = sc["central"]
    central = cen["switched_gal"]
    q_lo, q_hi = quadrature_bounds(central, sc["tornado"])
    headline = {"low": q_lo, "central": central, "high": q_hi}
    corners = {k: sc[k]["switched_gal"] for k in ("low", "central", "high")}
    by_risk = {lvl: model.gallons(params, model.point(D, overrides={"risk_acceptance": lvl}))["switched_gal"]
               for lvl in ("low", "central", "high")}

    fall = model.fall_farm_diesel(params, D, notes, cen["eligible_gal"])
    xcheck = model.fleet_crosscheck(params, D, fall, cen)
    pc = model.point(D)

    results = {
        "prices": ps, "notes": notes, "derived": D,
        "gallons_headline": headline, "gallons_corners": corners, "gallons_by_risk_acceptance": by_risk,
        "ceiling_switched_gal": cen["ceiling_switched_gal"],
        "eligible_gal_central": cen["eligible_gal"],
        "components_central": cen["components_eligible_gal"],
        "components_low": sc["low"]["components_eligible_gal"],
        "components_high": sc["high"]["components_eligible_gal"],
        "tons_central": cen["tons"], "gal_per_ton_central": cen["gal_per_ton"],
        "fall_farm_diesel": fall, "fleet_crosscheck": xcheck, "tornado": sc["tornado"], "levels": {},
    }
    for lvl, gal in headline.items():
        results["levels"][lvl] = {"switched_gal": gal, "fiscal": fiscal.fiscal(gal, params),
                                  "context": fiscal.context(gal, cen["tons"], params, ps, fall["window_farm_diesel_gal"])}
    results["levels_corners"] = {lvl: fiscal.fiscal(g, params)["state_revenue_forgone"] for lvl, g in corners.items()}
    truck_share = cen["switched_gal"] / cen["eligible_gal"]
    results["road"] = fiscal.road(params, pc, cen["tons"], truck_share)
    results["example_farm"] = fiscal.example_farm(params, pc, fall, notes, ps["shock_midwest"])
    results["alternatives"] = fiscal.alternatives(params, central)

    rows = []
    for lvl in ("low", "central", "high"):
        L = results["levels"][lvl]
        c = L["context"]
        rows.append({"scenario": lvl, "gallons_switched_M": L["switched_gal"] / 1e6,
                     "state_revenue_forgone_$M": L["fiscal"]["state_revenue_forgone"] / 1e6,
                     "per_farm_$": c["per_farm"], "per_fall_crop_acre_$": c["per_fall_crop_acre"],
                     "per_bu_corn_soy_cents": c["per_bushel_corn_soy_cents"],
                     "share_of_window_farm_fuel_shock_pct": 100 * c["relief_share_of_total_farm_fuel_shock"]})
    pd.DataFrame(rows).round(3).to_csv(OUT / "table_fiscal.csv", index=False)
    pd.DataFrame(sc["tornado"]).round(4).to_csv(OUT / "table_tornado.csv", index=False)
    pd.DataFrame({k: sc[k]["components_eligible_gal"] for k in ("low", "central", "high")}).div(1e6).round(3) \
        .to_csv(OUT / "table_components_Mgal.csv")
    (OUT / "results.json").write_text(json.dumps(results, indent=2, default=float))
    return results


if __name__ == "__main__":
    r = main()
    import simple_estimate
    simple_estimate.main()
    import make_appendix
    make_appendix.main()
    import btn_figures
    btn_figures.main()
    import btn_text
    btn_text.main()
    h = r["gallons_headline"]
    print("Switched gallons (M): low {:.2f} central {:.2f} high {:.2f}".format(*(v / 1e6 for v in h.values())))
    print("State revenue forgone ($M):", {k: round(v["fiscal"]["state_revenue_forgone"] / 1e6, 2) for k, v in r["levels"].items()})
