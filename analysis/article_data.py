"""Numbers and Figure 1 for the article 'The impact of emergency diesel tax relief for agricultural producers'.
Reads outputs/simple_estimate.json (run analysis/simple_estimate.py first). Writes outputs/article.json and
outputs/article_fig1.png."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prices  # noqa: E402
import simple_estimate as se  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_CROPS = ("corn", "soybeans")  # the article covers corn and soybeans only
OUT = ROOT / "outputs"
BLUE, INK, INK2, MUTED, GRID, BASE = "#2a78d6", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"


def figure1(path: Path) -> dict:
    w = prices.load_weekly(start="2015-01-01")["us"].dropna()
    peak_date, peak = w.idxmax(), w.max()
    fig, ax = plt.subplots(figsize=(6.5, 3.0), dpi=220)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(BASE)
    ax.spines["bottom"].set_color(BASE)
    ax.plot(w.index, w.values, color=BLUE, lw=1.4)
    ax.annotate(f"${peak:.2f}\n{peak_date:%b. %-d, %Y}", xy=(peak_date, peak), xytext=(-70, -8), textcoords="offset points",
                ha="right", va="center", fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:.0f}"))
    ax.set_ylabel("Dollars per gallon", color=INK2, fontsize=8)
    ax.tick_params(colors=MUTED, labelcolor=INK2, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_ylim(1.5, 7.2)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return {"peak": float(peak), "peak_date": f"{peak_date:%B %-d, %Y}", "latest": float(w.iloc[-1]),
            "latest_date": f"{w.index[-1]:%B %-d, %Y}", "start_year": int(w.index[0].year)}


def main() -> dict:
    s = json.loads((OUT / "simple_estimate.json").read_text())
    R = {r["crop"]: r for r in s["rows"]}
    rows = []
    for c in ARTICLE_CROPS:
        r = R[c]
        loads = r["hauled_tons"] / r["tons_per_load"]
        miles = loads * 2 * r["oneway_miles"]
        rows.append({"crop": c, "hauled_bu": r["hauled_tons"] * 2000 / se.LB_PER_BU[c], "loads": loads, "miles": miles,
                     "gallons": miles / se.MPG, "savings": miles / se.MPG * se.RELIEF})
    tot_gal = sum(r["gallons"] for r in rows)
    haul = {m: sum(R[c]["hauled_tons"] * 2 * m / se.MPG / R[c]["tons_per_load"] for c in ARTICLE_CROPS) * se.RELIEF for m in (21.7, 41.7)}
    out = {
        "fig1": figure1(OUT / "article_fig1.png"),
        "rows": rows,
        "total_loads": sum(r["loads"] for r in rows), "total_miles": sum(r["miles"] for r in rows),
        "total_gallons": tot_gal, "total_savings": tot_gal * se.RELIEF,
        "if_only_onhand": tot_gal * se.RELIEF * se.ONHAND_TRUCKS,
        "haul_low": haul[21.7], "haul_high": haul[41.7],
        "params": {c: {"production_mbu": R[c]["production_mbu"], "share": R[c]["share"], "miles": R[c]["oneway_miles"],
                       "tons_per_load": R[c]["tons_per_load"]} for c in ARTICLE_CROPS},
        "mpg": se.MPG,
        "farm_cornsoy": s["example_farm"],
        "share_detail": [r for r in s["share_detail"] if r["crop"] in ARTICLE_CROPS],
    }
    (OUT / "article.json").write_text(json.dumps(out, indent=1, default=float))
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: o[k] for k in ("fig1", "total_loads", "total_miles", "total_gallons", "total_savings", "if_only_onhand", "haul_low", "haul_high", "farm_cornsoy")}, indent=1, default=float))
    for r in o["rows"]:
        print(r)
