"""Figures for the 'Ag by the numbers' piece, drawn from outputs/results.json (run run_all.py first)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# Reference palette (dataviz skill, light mode): emphasis color + recessive grays; ink tokens for text.
BLUE, BLUE_LIGHT = "#2a78d6", "#86b6ef"
GRAY, GRAY_LIGHT = "#898781", "#e1e0d9"
SURFACE, INK, INK2, MUTED, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#c3c2b7"


def _style(fig, ax):
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASE)
    ax.tick_params(colors=MUTED, labelcolor=INK2, length=0)


def tax_per_gallon(r: dict, p: dict, path: Path) -> None:
    t = p["tax"]
    st_clear, st_dyed, fed = t["nd_clear_cents"], t["nd_dyed_cents"], t["federal_cents"]
    fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=200)
    _style(fig, ax)
    rows = [("Clear diesel, on the road", st_clear), ("Dyed diesel under the order", st_dyed)]
    for i, (label, st) in enumerate(rows):
        y = 1 - i
        ax.barh(y, st, color=BLUE, height=0.5, edgecolor=SURFACE, linewidth=2, label="ND state tax" if i == 0 else None)
        ax.barh(y, fed, left=st, color=GRAY_LIGHT, height=0.5, edgecolor=SURFACE, linewidth=2,
                label="Federal tax (still owed)" if i == 0 else None)
        ax.text(st + fed + 0.8, y, f"{st + fed:.1f}¢", va="center", color=INK, fontsize=9, fontweight="bold")
        ax.text(st / 2, y, f"{st}¢", va="center", ha="center", color="white" if st > 6 else INK, fontsize=8)
    ax.set_yticks([1, 0], [r[0] for r in rows], fontsize=9)
    ax.set_xlim(0, 56)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:.0f}¢"))
    ax.grid(axis="x", color=GRAY_LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False, fontsize=8, labelcolor=INK2)
    ax.set_title("Fuel tax per gallon: the order saves 19¢, not 43¢", loc="left", color=INK, fontsize=10, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)




def example_farm(r: dict, path: Path) -> None:
    ef = r["example_farm"]
    save, shock = round(ef["savings"], -1), round(ef["shock_cost_fall_diesel"], -3)
    fig, ax = plt.subplots(figsize=(7.2, 2.2), dpi=200)
    _style(fig, ax)
    ax.barh([1], [shock], color=GRAY_LIGHT, height=0.5)
    ax.barh([0], [save], color=BLUE, height=0.5)
    ax.text(shock - 300, 1, f"${shock:,.0f}", va="center", ha="right", color=INK, fontsize=9, fontweight="bold")
    ax.text(save + 300, 0, f"${save:,.0f}", va="center", color=INK, fontsize=9, fontweight="bold")
    ax.set_yticks([1, 0], ["Higher fall diesel bill", "Savings from the order"], fontsize=9)
    ax.set_xlim(0, shock * 1.02)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
    ax.grid(axis="x", color=GRAY_LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("A 2,000-acre corn and soybean farm this fall, drawn to scale", loc="left", color=INK, fontsize=10,
                 fontweight="bold")
    fig.text(0.01, 0.01, "1,000 ac corn + 1,000 ac soybeans at 2026 forecast yields; assumes all truck fuel switches (pickups excluded). "
             "Diesel up $2.79/gal vs. fall 2025.", color=MUTED, fontsize=6.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    main_simple()








def tornado(r: dict, path: Path, top: int = 8) -> None:
    names = {"oneway_miles_to_market": "Haul distance to market",
             "other_ag_hauling_gal": "Calf and anhydrous hauling", "payload_tons_market": "Truck payload",
             "mpg_loaded": "Loaded fuel economy", "onhand_share_trucks": "Trucks fueled from farm tanks",
             "done_by_nov30_corn": "Corn harvest finished by Nov. 30",
             "mpg_empty": "Empty fuel economy", "offfarm_by_dec1_corn": "Share of corn leaving farm by Dec. 1",
             "offfarm_by_dec1_soybeans": "Share of soybeans leaving farm by Dec. 1", "border_loss_share": "Trips crossing into MN/SD"}
    rows = r["tornado"][:top][::-1]
    base = r["gallons_headline"]["central"] / 1e6
    fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=200)
    _style(fig, ax)
    for y, row in enumerate(rows):
        lo, hi = sorted([row["gal_at_low_value"] / 1e6, row["gal_at_high_value"] / 1e6])
        ax.barh(y, base - lo, left=lo, color=GRAY_LIGHT, height=0.6)
        ax.barh(y, hi - base, left=base, color=BLUE_LIGHT, height=0.6)
        ax.text(lo - 0.04, y, f"{lo:.1f}", va="center", ha="right", color=INK2, fontsize=7.5)
        ax.text(hi + 0.04, y, f"{hi:.1f}", va="center", color=INK2, fontsize=7.5)
    ax.axvline(base, color=INK2, lw=1)
    ax.set_yticks(range(len(rows)), [names.get(rw["parameter"], rw["parameter"]) for rw in rows], fontsize=8)
    ax.set_xlim(base - 1.5, base + 1.3)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:.1f}M"))
    ax.grid(axis="x", color=GRAY_LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    fig.suptitle("What moves the estimate most", x=0.01, ha="left", color=INK, fontsize=10, fontweight="bold")
    fig.text(0.01, 0.01, f"Gallons switched, one input at a time at its low or high value; line = central {base:.2f}M. "
             "Gray lowers it; blue raises it.", color=MUTED, fontsize=6.5)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(path)
    plt.close(fig)


def category_values(r: dict) -> list[tuple[str, float, float]]:
    """(label, eligible gallons, switched gallons) for the three broad truck categories (pickups excluded)."""
    D = {k: v["central"] for k, v in r["derived"].items()}
    c = r["components_central"]
    keep = (1 - D["border_loss_share"]) * D["risk_acceptance"]
    tf = D["onhand_share_trucks"] * keep
    harvest = c["harvest_to_market"] + c["sugarbeets_to_station"] + c["field_to_bin"]
    return [("Hauling the fall harvest", harvest, harvest * tf),
            ("Calves and fertilizer", c["livestock_and_fertilizer"], c["livestock_and_fertilizer"] * tf),
            ("Selling stored wheat and barley", c["stored_small_grain_to_market"], c["stored_small_grain_to_market"] * tf)]


def categories(r: dict, path: Path) -> None:
    rows = category_values(r)[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 3.1), dpi=200)
    _style(fig, ax)
    for y, (lab, el, sw) in enumerate(rows):
        ax.barh(y + 0.18, el / 1e6, height=0.34, color=BLUE_LIGHT, label="Eligible gallons" if y == 0 else None)
        ax.barh(y - 0.18, sw / 1e6, height=0.34, color=BLUE, label="Likely switched to dyed fuel" if y == 0 else None)
        ax.text(el / 1e6 + 0.06, y + 0.18, f"{el / 1e6:.2f}M", va="center", color=INK2, fontsize=8)
        ax.text(sw / 1e6 + 0.06, y - 0.18, f"{sw / 1e6:.2f}M", va="center", color=INK, fontsize=8, fontweight="bold")
    ax.set_yticks(range(len(rows)), [r_[0] for r_ in rows], fontsize=9)
    ax.set_xlim(0, max(r_[1] for r_ in rows) / 1e6 * 1.15)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:.0f}M"))
    ax.grid(axis="x", color=GRAY_LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", frameon=False, fontsize=8, labelcolor=INK2)
    tot_e, tot_s = sum(x[1] for x in rows), sum(x[2] for x in rows)
    fig.suptitle(f"On-road farm diesel, Sept. 29–Nov. 30: {tot_e / 1e6:.1f}M gallons eligible, {tot_s / 1e6:.1f}M likely switched",
                 x=0.01, ha="left", color=INK, fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path)
    plt.close(fig)


def main_all() -> None:
    import model
    r = json.loads((OUT / "results.json").read_text())
    p = model.load_params()
    tax_per_gallon(r, p, OUT / "btn_tax_per_gallon.png")
    categories(r, OUT / "btn_categories.png")
    example_farm(r, OUT / "btn_example_farm.png")
    tornado(r, OUT / "btn_tornado.png")




# ---------------- simple five-parameter estimate charts ----------------
def simple_crops(s: dict, path: Path) -> None:
    rows = sorted(s["rows"], key=lambda r: r["savings"])
    fig, ax = plt.subplots(figsize=(7.2, 2.4), dpi=200)
    _style(fig, ax)
    ys = range(len(rows))
    ax.barh(list(ys), [r["savings"] / 1e3 for r in rows], color=BLUE, height=0.55)
    for y, r in zip(ys, rows):
        ax.text(r["savings"] / 1e3 + 8, y, f"${r['savings'] / 1e3:,.0f}K  ({r['gallons'] / 1e6:.2f}M gal)", va="center", color=INK, fontsize=8.5)
    ax.set_yticks(list(ys), [r["crop"].capitalize() for r in rows], fontsize=9)
    ax.set_xlim(0, max(r["savings"] for r in rows) / 1e3 * 1.45)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}K"))
    ax.grid(axis="x", color=GRAY_LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    fig.suptitle(f"Savings by crop if every eligible truck gallon switches: ${s['total_savings'] / 1e6:.2f} million total",
                 x=0.01, ha="left", color=INK, fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path)
    plt.close(fig)


def simple_haul(s: dict, path: Path) -> None:
    xs = [h["miles"] for h in s["haul_curve"]]
    ys = [h["savings"] / 1e6 for h in s["haul_curve"]]
    fig, ax = plt.subplots(figsize=(7.2, 2.8), dpi=200)
    _style(fig, ax)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(BASE)
    ax.plot(xs, ys, color=BLUE, lw=2)
    on = [y * 0.528 for y in ys]
    ax.plot(xs, on, color=GRAY, lw=2)
    ax.text(xs[-1] + 0.5, ys[-1], "Every eligible truck switches", va="center", color=INK2, fontsize=8)
    ax.text(xs[-1] + 0.5, on[-1], "Only trucks fueled from farm tanks (53%)", va="center", color=INK2, fontsize=8)
    ax.axvline(27.8, color=GRAY_LIGHT, lw=1)
    ax.text(28.3, max(ys) * 0.98, "ND corn trip, 27.8 mi", color=MUTED, fontsize=7.5, va="top")
    ax.set_xlim(10, 76)
    ax.set_xticks(range(10, 51, 10))
    ax.set_ylim(0, max(ys) * 1.08)
    ax.set_xlabel("Average one-way haul to elevator or plant (miles)", color=INK2, fontsize=8.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:.1f}M"))
    ax.grid(axis="y", color=GRAY_LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    fig.suptitle("Statewide savings by average haul distance", x=0.01, ha="left", color=INK, fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path)
    plt.close(fig)


def simple_example(s: dict, path: Path) -> None:
    ef = s["example_farm"]
    save, shock = round(ef["savings"], -1), round(ef["fall_diesel_increase"], -3)
    fig, ax = plt.subplots(figsize=(7.2, 2.2), dpi=200)
    _style(fig, ax)
    ax.barh([1], [shock], color=GRAY_LIGHT, height=0.5)
    ax.barh([0], [save], color=BLUE, height=0.5)
    ax.text(shock - 300, 1, f"${shock:,.0f}", va="center", ha="right", color=INK, fontsize=9, fontweight="bold")
    ax.text(save + 300, 0, f"${save:,.0f}", va="center", color=INK, fontsize=9, fontweight="bold")
    ax.set_yticks([1, 0], ["Higher harvest diesel bill", "Savings from the order"], fontsize=9)
    ax.set_xlim(0, shock * 1.02)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
    ax.grid(axis="x", color=GRAY_LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("A 2,000-acre corn and soybean farm this fall, drawn to scale", loc="left", color=INK, fontsize=10, fontweight="bold")
    fig.text(0.01, 0.01, f"1,000 ac corn + 1,000 ac soybeans at 2026 forecast yields; all truck fuel switches. Diesel up ${s['price_rise']:.2f}/gal vs. fall 2025.",
             color=MUTED, fontsize=6.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def main_simple() -> None:
    import model
    s = json.loads((OUT / "simple_estimate.json").read_text())
    p = model.load_params()
    r = json.loads((OUT / "results.json").read_text())
    tax_per_gallon(r, p, OUT / "btn_tax_per_gallon.png")
    simple_crops(s, OUT / "btn_simple_crops.png")
    simple_haul(s, OUT / "btn_simple_haul.png")
    simple_example(s, OUT / "btn_example_farm.png")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
