"""Table figure: Scenario 1 (Farmer Bridge formula, 2026 inputs) payment per acre by crop. No title or footnote.
Reads output/county_crop_detail.csv (run harvest_fuel_alloc.py first).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from crop_table_figure import BAND, table_rows
from harvest_fuel_alloc import INK, INK2, OUT, SURFACE


def main() -> None:
    t = table_rows(pd.read_csv(OUT / "county_crop_detail.csv"))
    t[["crop", "acres_m", "s1"]].round(2).to_csv(OUT / "crop_table_s1.csv", index=False)

    plt.rcParams.update({"font.family": "DejaVu Sans"})
    esc = lambda s: s.replace("$", r"\$")
    cols = [("Crop", 0.04, "left"), ("Acres\n(millions)", 0.45, "right"),
            ("Farmer Bridge method,\n2026 inputs ($/acre)", 0.96, "right")]
    n = len(t)
    fig = plt.figure(figsize=(3.6, 0.55 + 0.25 * n), dpi=250)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    row_h = 0.98 / (n + 1.6)
    head_y = 1 - row_h * 0.7
    for label, x, ha in cols:
        ax.text(x, head_y, esc(label), ha=ha, va="center", fontsize=7.4, fontweight="bold", color=INK, linespacing=1.15)
    ax.axhline(head_y - row_h * 0.75, color=INK2, lw=0.8)
    for i, r in t.iterrows():
        y = head_y - row_h * (i + 1.35)
        if i % 2 == 1:
            ax.add_patch(plt.Rectangle((0, y - row_h / 2), 1, row_h, fc=BAND, ec="none", zorder=0))
        for (label, x, ha), v in zip(cols, [r.crop, f"{r.acres_m:.1f}", f"${r.s1:,.2f}"]):
            ax.text(x, y, esc(v), ha=ha, va="center", fontsize=7.6, color=INK2 if label.startswith("Acres") else INK)
    ax.axhline(head_y - row_h * (n + 0.85), color=INK2, lw=0.8)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"crop_table_s1.{ext}", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
