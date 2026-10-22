"""Tile-map grids: rows = crops (corn, soybeans, wheat; and cotton, rice); columns = scenarios. Each tile is a state's average
payment per acre of that crop (state-crop payment / state-crop acres). Reads output/county_crop_detail.csv.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch

from matplotlib.collections import PolyCollection

from harvest_fuel_alloc import INK, INK2, MUTED, OUT, SCENARIOS, SURFACE, TILES
from region_maps import GEO, albers

NATIONAL_RATE = {"s1", "s2"}
DROP_TILES = {"AK", "HI", "ME", "NH", "VT"}  # left off the tile panels  # scenarios with one rate per crop nationwide: drawn as a single filled outline

MIN_ACRES = 10_000  # state-crop acres below this are left blank
NA_COLOR = "#efeee9"
# Ordinal blue ramp, 100-step spacing (dataviz reference palette; validated --ordinal, light mode).
RAMP = [("#86b6ef", INK), ("#5598e7", INK), ("#2a78d6", "white"), ("#1c5cab", "white"), ("#104281", "white")]


def bins(edges: list[float]) -> tuple[list, list[str]]:
    """Five ramp bins from four interior edges, plus their legend labels."""
    lo = [0, *edges]
    hi = [*edges, float("inf")]
    b = [(l, h, fc, tc) for l, h, (fc, tc) in zip(lo, hi, RAMP)]
    labels = [f"Under ${edges[0]:g}"] + [f"${l:g}–{h:g}" for l, h in zip(edges, edges[1:])] + [f"${edges[-1]:g} or more"]
    return b, labels


# Bins differ per figure: cotton and rice run roughly 3-5x the corn/soy/wheat rates.
GRIDS = [
    {"rows": ["corn", "soybeans", "wheat"], "edges": [15, 20, 30, 40], "stem": "crop_scenario_grid",
     "title": "Corn, soybean and wheat"},
    {"rows": ["cotton", "rice"], "edges": [50, 75, 100, 150], "stem": "crop_scenario_grid_cotton_rice",
     "title": "Cotton and rice", "note": " ERS survey base years: cotton 2019, rice 2021."},
]


def state_crop(a: pd.DataFrame, rows: list[str]) -> pd.DataFrame:
    g = a[a.crop.isin(rows)].groupby(["crop", "state"])
    out = g.acres.sum().to_frame()
    for sc in SCENARIOS:
        out[sc] = g[f"pay_{sc}"].sum() / out.acres
    return out


def panel(ax, vals: pd.Series, acres: pd.Series, bins: list) -> None:
    esc = lambda t: t.replace("$", r"\$")
    gap = 0.1
    for st, (c, row) in TILES.items():
        if st in DROP_TILES:
            continue
        ok = st in vals.index and acres.get(st, 0) >= MIN_ACRES
        if ok:
            v = vals[st]
            _, _, fc, tc = next(b for b in bins if b[0] <= v < b[1])
        else:
            fc, tc = NA_COLOR, MUTED
        ax.add_patch(FancyBboxPatch((c + gap / 2, -row + gap / 2), 1 - gap, 1 - gap,
                                    boxstyle="round,pad=0,rounding_size=0.1", fc=fc, ec="none"))
        ax.text(c + 0.5, -row + 0.66, st, ha="center", va="center", fontsize=3.6, color=tc,
                fontweight="bold" if ok else "normal")
        if ok:
            ax.text(c + 0.5, -row + 0.3, esc(f"${v:.0f}"), ha="center", va="center", fontsize=3.6, color=tc)
    ax.set_xlim(-0.1, 12.1)
    ax.set_ylim(-7.1, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")


def lower48() -> list[list[tuple[float, float]]]:
    """Lower-48 state rings in Albers, small islands dropped; drawn with a thick same-color edge to soften detail."""
    import json
    out = []
    for f in json.load(open(GEO / "us-states.json"))["features"]:
        if f["properties"]["name"] in ("Alaska", "Hawaii", "Puerto Rico"):
            continue
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            ring = [albers(x, y) for x, y in poly[0]]
            area = 0.5 * abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1])))
            if area > 2e-4:
                out.append(ring)
    return out


def national_panel(ax, v: float, outline: list, bins: list) -> None:
    esc = lambda t: t.replace("$", r"\$")
    _, _, fc, tc = next(b for b in bins if b[0] <= v < b[1])
    ax.add_collection(PolyCollection(outline, facecolors=fc, edgecolors=fc, lw=1.6, joinstyle="round"))
    ax.autoscale_view()
    ax.margins(0.08)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.text((x0 + x1) / 2, y0 + (y1 - y0) * 0.5, esc(f"${v:.2f}"), ha="center", va="center", fontsize=15,
            fontweight="bold", color=tc)
    ax.text((x0 + x1) / 2, y0 + (y1 - y0) * 0.36, "per acre in every state", ha="center", va="center", fontsize=5.6,
            color=tc)
    ax.set_aspect("equal")
    ax.axis("off")


def grid(a: pd.DataFrame, outline: list, rows: list[str], edges: list[float], stem: str, title: str,
         note: str = "") -> pd.DataFrame:
    """One figure: rows = crops, columns = scenarios. Vertical spacing is fixed in inches so any row count lays out."""
    t = state_crop(a, rows)
    b, labels = bins(edges)
    esc = lambda s: s.replace("$", r"\$")
    h = 4.004 / 3 * len(rows) + 0.728 + 0.868  # panels + header + legend/footnote (3 rows -> 5.6 in, as before)
    fig, axes = plt.subplots(len(rows), len(SCENARIOS), figsize=(2.4 * len(SCENARIOS), h), dpi=250, squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for j, sc in enumerate(SCENARIOS):
        for i, crop in enumerate(rows):
            ax = axes[i, j]
            d = t.loc[crop]
            nat = a.loc[a.crop == crop, f"pay_{sc}"].sum() / a.loc[a.crop == crop, "acres"].sum()
            if sc in NATIONAL_RATE:
                national_panel(ax, nat, outline, b)
            else:
                panel(ax, d[sc], d.acres, b)
                ax.text(0.03, 0.915, esc(f"${nat:.2f}"), transform=ax.transAxes, fontsize=13, fontweight="bold",
                        color=INK, ha="left", va="top")
                # label clears the number: 0.40 fits "$NN.NN"; each extra digit adds ~0.07 of the panel width
                lx = 0.40 + 0.07 * max(0, len(f"{nat:.2f}") - 5)
                ax.text(lx, 0.86, "U.S. average\nper acre", transform=ax.transAxes, fontsize=5.6, color=INK2,
                        ha="left", va="center", linespacing=1.1)
            if i == 0:
                ax.set_title(f"Scenario {j + 1}\n{SCENARIOS[sc]}", fontsize=7.2, color=INK, fontweight="bold", pad=3)
            if j == 0:
                ax.text(-0.04, 0.5, crop.capitalize(), transform=ax.transAxes, rotation=90, ha="right", va="center",
                        fontsize=8, fontweight="bold", color=INK)
    handles = [Patch(fc=x[2], label=esc(l)) for x, l in zip(b, labels)]
    handles.append(Patch(fc=NA_COLOR, label=f"Under {MIN_ACRES:,} acres of the crop"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.3472 / h), ncol=6, frameon=False,
               fontsize=6.3, labelcolor=INK2, handlelength=1.2, columnspacing=0.9,
               title="Average payment per acre of the crop", title_fontsize=6.5)
    fig.text(0.02, 1 - 0.084 / h, f"{title} payments per acre, by state, under {len(SCENARIOS)} allocation rules",
             fontsize=10, fontweight="bold", color=INK, va="top")
    pool = a.pay_s1.sum()
    fig.text(0.02, 1 - 0.2688 / h, esc(f"Hypothetical split of ${pool / 1e9:.2f} billion of USDA's $8 billion: the share "
             f"last year's Farmer Bridge paid the 9 crops with ERS cost budgets."), fontsize=7, color=INK2, va="top")
    fig.text(0.02, 0.0448 / h, "Scenario 1: Farmer Bridge formula (91 FR 8360), a national rate per crop proportional to ERS "
             "2026F total cost minus Oct. 2026 WASDE yield × price.\nScenario 2: a national rate per crop proportional to "
             "ERS's 2026 fuel, lube and electricity cost per acre. Scenario 3: ERS 2025 regional fuel cost per acre\n× the "
             "crop's national 2026 increase; state values average their counties' ERS regions. Acres: FSA 2026." + note,
             fontsize=4.8, color=MUTED, linespacing=1.35)
    fig.subplots_adjust(left=0.04, right=0.995, top=1 - 0.728 / h, bottom=0.868 / h, wspace=0.02, hspace=0.06)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"{stem}.{ext}", facecolor=SURFACE)
    plt.close(fig)
    return t


def main() -> None:
    a = pd.read_csv(OUT / "county_crop_detail.csv")
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    outline = lower48()
    tables = [grid(a, outline, **g) for g in GRIDS]
    pd.concat(tables).round(2).to_csv(OUT / "state_crop_per_acre.csv")


if __name__ == "__main__":
    main()
