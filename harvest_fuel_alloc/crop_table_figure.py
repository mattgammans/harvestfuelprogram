"""Table figure: payment per acre by crop under each scenario, with Scenario 3's lowest and highest state.
Reads output/county_crop_detail.csv (run harvest_fuel_alloc.py first). State values are state-crop payment / acres,
for states with at least MIN_ACRES of the crop.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from harvest_fuel_alloc import INK, INK2, MUTED, OUT, SURFACE

MIN_ACRES = 10_000
GRID, BAND = "#e1e0d9", "#f4f3ef"
HIDE = {"peanuts"}  # left out of the table


def table_rows(a: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = [(c, d) for c, d in a.groupby("crop") if c not in HIDE]
    groups.sort(key=lambda cd: -cd[1].acres.sum())
    for crop, d in groups:
        st = d.groupby("state").agg(acres=("acres", "sum"), pay=("pay_s3", "sum"))
        st = st[st.acres >= MIN_ACRES]
        per = st.pay / st.acres
        rows.append({"crop": crop.capitalize(),
                     "acres_m": d.acres.sum() / 1e6,
                     "s1": d.pay_s1.sum() / d.acres.sum(), "s2": d.pay_s2.sum() / d.acres.sum(),
                     "s3": d.pay_s3.sum() / d.acres.sum(),
                     "s3_lo": per.min(), "s3_lo_st": per.idxmin(), "s3_hi": per.max(), "s3_hi_st": per.idxmax()})
    return pd.DataFrame(rows)


def main() -> None:
    a = pd.read_csv(OUT / "county_crop_detail.csv")
    t = table_rows(a)
    t.round(2).to_csv(OUT / "crop_table.csv", index=False)

    plt.rcParams.update({"font.family": "DejaVu Sans"})
    esc = lambda s: s.replace("$", r"\$")
    cols = [("Crop", 0.02, "left"), ("Acres\n(millions)", 0.27, "right"), ("Scenario 1\nFarmer Bridge", 0.42, "right"),
            ("Scenario 2\nfuel, national", 0.56, "right"), ("Scenario 3\nU.S. average", 0.70, "right"),
            ("Scenario 3\nlowest state", 0.84, "right"), ("Scenario 3\nhighest state", 0.98, "right")]
    n = len(t)
    row_h, top = 0.062, 0.80
    fig = plt.figure(figsize=(7.2, 1.45 + 0.30 * n), dpi=250)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.02, 0.09, 0.96, 0.83])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    row_h = 0.98 / (n + 1.6)
    head_y = 1 - row_h * 0.7
    for label, x, ha in cols:
        ax.text(x, head_y, label, ha=ha, va="center", fontsize=7.4, fontweight="bold", color=INK, linespacing=1.15)
    ax.axhline(head_y - row_h * 0.75, color=INK2, lw=0.8)
    for i, r in t.iterrows():
        y = head_y - row_h * (i + 1.35)
        if i % 2 == 1:
            ax.add_patch(plt.Rectangle((0, y - row_h / 2), 1, row_h, fc=BAND, ec="none", zorder=0))
        vals = [r.crop, f"{r.acres_m:.1f}", f"${r.s1:,.2f}", f"${r.s2:,.2f}", f"${r.s3:,.2f}",
                f"${r.s3_lo:,.2f} ({r.s3_lo_st})", f"${r.s3_hi:,.2f} ({r.s3_hi_st})"]
        for (label, x, ha), v in zip(cols, vals):
            ax.text(x, y, esc(v), ha=ha, va="center", fontsize=7.6, color=INK if x < 0.1 or x > 0.3 else INK2,
                    family="DejaVu Sans")
    ax.axhline(head_y - row_h * (n + 0.85), color=INK2, lw=0.8)

    fig.text(0.02, 0.975, "Payment per acre by crop under three allocation rules", fontsize=10.5, fontweight="bold",
             color=INK, va="top")
    fig.text(0.02, 0.012, esc(
        "Scenario 1: Farmer Bridge formula (91 FR 8360) with ERS 2026F total cost and Oct. 2026 WASDE yields and prices.\nScenario 2: proportional to ERS's U.S. 2026 fuel, lube and electricity cost "
        "per acre. Scenario 3: ERS 2025 regional fuel cost × ERS's 2026 increase;\nstate values are state averages, for "
        f"states with at least {MIN_ACRES:,} acres of the crop. Acres: FSA 2026 planted acres."),
        fontsize=5.2, color=MUTED, linespacing=1.4)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"crop_table.{ext}", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
