"""County maps, one panel per crop:
  1. baseline: ERS 2025 fuel, lube and electricity cost per planted acre for the county's budget region
  2. delta:    projected 2026 cost per acre (baseline x the crop's ERS national 2026F/2025 ratio)
Counties are colored only where FSA reports at least MIN_ACRES of the crop in 2026. Reads output/county_crop_detail.csv
(run harvest_fuel_alloc.py first). Lower 48 only.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
GEO = HERE / "data" / "geo"
OUT = HERE / "output"
MIN_ACRES = 100
CROPS = ["corn", "soybeans", "wheat", "cotton", "rice", "sorghum", "barley", "oats", "peanuts"]
SKIP_STATES = {"02", "15", "72"}  # AK, HI, PR

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
EMPTY, STATE_LINE = "#efeee9", "#c3c2b7"
# Ordinal blue ramp, 100-step spacing (dataviz reference palette; validated --ordinal, light mode).
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
METRICS = {
    "baseline": dict(col="ers_fuel_usd_per_acre", edges=[12, 20, 35, 70], unit="$", legend="Dollars per planted acre",
                     title="Fuel, lube and electricity cost per planted acre, 2025",
                     sub="ERS regional cost-of-production estimates for the county's farm resource region.\n"
                         "Shaded where FSA reports the crop in 2026."),
    "delta": dict(col="fuel_2026_per_acre", edges=[15, 25, 45, 90], unit="$", legend="Dollars per planted acre",
                  title="Projected fuel, lube and electricity cost per planted acre, 2026",
                  sub="ERS 2025 regional cost × the crop's ERS national 2026 forecast increase (about 28%).\n"
                      "Shaded where FSA reports the crop in 2026."),
}


def albers(lon: float, lat: float) -> tuple[float, float]:
    """USGS Albers equal-area conic for the lower 48 (standard parallels 29.5 and 45.5, origin 37.5N 96W)."""
    p1, p2, p0, l0 = map(math.radians, (29.5, 45.5, 37.5, -96.0))
    n = (math.sin(p1) + math.sin(p2)) / 2
    c = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    rho0 = math.sqrt(c - 2 * n * math.sin(p0)) / n
    rho = math.sqrt(c - 2 * n * math.sin(math.radians(lat))) / n
    th = n * (math.radians(lon) - l0)
    return rho * math.sin(th), rho0 - rho * math.cos(th)


def rings(geom: dict) -> list[list[tuple[float, float]]]:
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    return [[albers(x, y) for x, y in poly[0]] for poly in polys]  # outer rings only


def load_geo() -> tuple[dict[int, list], list]:
    counties = {}
    for f in json.load(open(GEO / "geojson-counties-fips.json"))["features"]:
        if f["id"][:2] not in SKIP_STATES:
            counties[int(f["id"])] = rings(f["geometry"])
    states = [r for f in json.load(open(GEO / "us-states.json"))["features"]
              if f["properties"]["name"] not in ("Alaska", "Hawaii", "Puerto Rico") for r in rings(f["geometry"])]
    return counties, states


def bin_color(v: float, edges: list[float]) -> str:
    return RAMP[sum(v >= e for e in edges)]


def draw(metric: str, d: pd.DataFrame, counties: dict, states: list, path: Path) -> None:
    m = METRICS[metric]
    plt.rcParams.update({"font.family": "DejaVu Sans", "hatch.linewidth": 0.5})
    esc = lambda t: t.replace("$", r"\$")
    fig, axes = plt.subplots(3, 3, figsize=(7.2, 6.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    all_polys = [r for rs in counties.values() for r in rs]
    for ax, crop in zip(axes.flat, CROPS):
        ax.set_facecolor(SURFACE)
        ax.add_collection(PolyCollection(all_polys, facecolors=EMPTY, edgecolors="none"))
        c = d[(d.crop == crop) & (d.acres >= MIN_ACRES) & d.fips.isin(counties)]
        polys, colors, fb = [], [], []
        for r in c.itertuples():
            for ring in counties[r.fips]:
                polys.append(ring)
                colors.append(bin_color(getattr(r, m["col"]), m["edges"]))
                if r.used_us_value:
                    fb.append(ring)
        ax.add_collection(PolyCollection(polys, facecolors=colors, edgecolors="none"))
        if fb:
            ax.add_collection(PolyCollection(fb, facecolors="none", edgecolors=SURFACE, hatch="////", lw=0))
        ax.add_collection(PolyCollection(states, facecolors="none", edgecolors=STATE_LINE, lw=0.25))
        lo, hi = c[m["col"]].min(), c[m["col"]].max()
        ax.set_title(f"{crop.capitalize()}", loc="left", fontsize=8.5, fontweight="bold", color=INK, pad=2)
        rng = f"${lo:,.2f}–${hi:,.2f} per acre" if m["unit"] == "$" else f"{lo:,.1f}–{hi:,.1f} gal per acre"
        ax.text(0.0, -0.02, esc(rng), transform=ax.transAxes, fontsize=6.5, color=INK2, va="top")
        ax.autoscale_view()
        ax.set_aspect("equal")
        ax.axis("off")

    e = m["edges"]
    u = "$" if m["unit"] == "$" else ""
    labels = [f"Under {u}{e[0]:g}", *[f"{u}{a:g}–{b:g}" for a, b in zip(e, e[1:])], f"{u}{e[-1]:g} or more"]
    handles = [Patch(fc=col, label=esc(l)) for col, l in zip(RAMP, labels)]
    handles += [Patch(fc=EMPTY, label=f"Crop not grown (under {MIN_ACRES} acres)"),
                Patch(fc=RAMP[1], ec=SURFACE, hatch="////", lw=0, label="No ERS estimate for region; U.S. value used")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.045), ncol=4, frameon=False, fontsize=6.8,
               labelcolor=INK2, handlelength=1.3, columnspacing=1.0, title=m["legend"],
               title_fontsize=7)
    fig.text(0.02, 0.985, m["title"], fontsize=11, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.952, m["sub"], fontsize=7.8, color=INK2, va="top", linespacing=1.35)
    fig.text(0.02, 0.01, "Sources: USDA ERS Commodity Costs and Returns (2025 regional estimates); "
             "USDA ERS cost-of-production forecasts (Oct. 2026); USDA ERS farm resource region crosswalk;\nUSDA FSA crop acreage (Oct. 1, 2026). "
             "Lower 48 states. Shared color scale across crops.", fontsize=5.4, color=MUTED, linespacing=1.4)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.885, bottom=0.17, wspace=0.04, hspace=0.22)
    for ext in ("png", "svg"):
        fig.savefig(path.with_suffix(f".{ext}"), facecolor=SURFACE)
    plt.close(fig)


def region_table(d: pd.DataFrame) -> pd.DataFrame:
    g = d[d.acres > 0].groupby(["crop", "budget_region", "used_us_value"]).agg(
        acres=("acres", "sum"), states=("state", lambda s: ",".join(sorted(set(s)))),
        fuel_2025_per_acre=("ers_fuel_usd_per_acre", "first"), fuel_2026_per_acre=("fuel_2026_per_acre", "first"),
        pay_per_acre_s1=("pay_per_acre_s1", "first"), pay_per_acre_s2=("pay_per_acre_s2", "first"),
        pay_per_acre_s3=("pay_per_acre_s3", "first"))
    g["share_of_crop_acres"] = g.acres / g.groupby(level="crop").acres.transform("sum")
    return g.reset_index().sort_values(["crop", "fuel_2025_per_acre"])


def main() -> None:
    d = pd.read_csv(OUT / "county_crop_detail.csv")
    counties, states = load_geo()
    for metric in METRICS:
        draw(metric, d, counties, states, OUT / f"region_map_{metric}")
    region_table(d).to_csv(OUT / "region_crop_values.csv", index=False, float_format="%.4f")


if __name__ == "__main__":
    main()
