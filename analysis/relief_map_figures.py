"""Map and timeline of fall 2026 diesel-tax relief by state, drawn from data/state_relief_2026-10-16.csv.

Grouping treats permission to run untaxed dyed diesel on the road as an effective waiver of the state tax.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "state_relief_2026-10-16.csv"
OUT = ROOT / "outputs"
AS_OF = date(2026, 10, 16)

# Reference palette (dataviz skill, light mode). Groups form an ordinal blue ramp (validated --ordinal);
# "other" and "none" are recessive neutrals, with a hatch on "other" so it never relies on color alone.
SURFACE, INK, INK2, MUTED, BASE, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#c3c2b7", "#e1e0d9"
GROUPS = {
    "tax_suspended": dict(color="#104281", text="white", label="State diesel tax suspended for everyone"),
    "dyed_everyone": dict(color="#2a78d6", text="white", label="Dyed diesel allowed on roads, all drivers"),
    "dyed_farm": dict(color="#86b6ef", text=INK, label="Dyed diesel allowed on roads, farm/forestry only"),
    "other": dict(color="#d6d5cd", text=INK, label="Other fuel-tax relief (rate freeze or gas only)", hatch="////"),
    "none": dict(color="#efeee9", text=MUTED, label="No statewide diesel relief"),
}

# Square tile grid (col, row); row 0 at top.
TILES = {
    "AK": (0, 0), "ME": (11, 0),
    "VT": (10, 1), "NH": (11, 1),
    "WA": (1, 2), "ID": (2, 2), "MT": (3, 2), "ND": (4, 2), "MN": (5, 2), "IL": (6, 2), "WI": (7, 2),
    "MI": (8, 2), "NY": (9, 2), "RI": (10, 2), "MA": (11, 2),
    "OR": (1, 3), "NV": (2, 3), "WY": (3, 3), "SD": (4, 3), "IA": (5, 3), "IN": (6, 3), "OH": (7, 3),
    "PA": (8, 3), "NJ": (9, 3), "CT": (10, 3),
    "CA": (1, 4), "UT": (2, 4), "CO": (3, 4), "NE": (4, 4), "MO": (5, 4), "KY": (6, 4), "WV": (7, 4),
    "VA": (8, 4), "MD": (9, 4), "DE": (10, 4),
    "AZ": (2, 5), "NM": (3, 5), "KS": (4, 5), "AR": (5, 5), "TN": (6, 5), "NC": (7, 5), "SC": (8, 5),
    "DC": (9, 5),
    "OK": (4, 6), "LA": (5, 6), "MS": (6, 6), "AL": (7, 6), "GA": (8, 6),
    "HI": (0, 7), "TX": (4, 7), "FL": (9, 7),
}
SOURCE_LINE = ("Sources: governors' orders, state revenue departments, EO 14435, IRS IR-2026-122; "
               "StartBusinessByState tracker (Oct. 6) for AL, AR, IN, KY, NC, ND, NE, OH, OK, UT. Status as of Oct. 16, 2026.")


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["start", "end"])
    assert len(TILES) == 51, len(TILES)
    return df


def _base(fig):
    plt.rcParams.update({"font.family": "DejaVu Sans", "hatch.linewidth": 0.8})
    fig.patch.set_facecolor(SURFACE)


def tile_map(df: pd.DataFrame, stem: Path) -> None:
    group_of = dict(zip(df.state, df.group))
    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=200)
    _base(fig)
    ax.set_facecolor(SURFACE)
    size, gap = 1.0, 0.08
    for st, (c, r) in TILES.items():
        g = GROUPS[group_of.get(st, "none")]
        ax.add_patch(FancyBboxPatch((c + gap / 2, -r + gap / 2), size - gap, size - gap,
                                    boxstyle="round,pad=0,rounding_size=0.08", fc=g["color"],
                                    ec=MUTED if "hatch" in g else "none", lw=0.6, hatch=g.get("hatch")))
        ax.text(c + 0.5, -r + 0.5, st, ha="center", va="center", fontsize=8.5,
                fontweight="bold" if st in group_of else "normal", color=g["text"])
    ax.set_xlim(-0.2, 12.2)
    ax.set_ylim(-7.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")

    counts = df[df.state != "US"].group.value_counts()
    counts["none"] = 51 - counts.sum()
    handles = [Patch(fc=g["color"], ec=MUTED if "hatch" in g else "none", lw=0.6, hatch=g.get("hatch"),
                     label=f"{g['label']} ({counts[k]})")
               for k, g in GROUPS.items()]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.01), ncol=1, frameon=False,
              fontsize=8, labelcolor=INK2, handlelength=1.4, handleheight=1.1, borderaxespad=0)

    n_diesel = int(counts.reindex(["tax_suspended", "dyed_everyone", "dyed_farm"]).sum())
    fig.text(0.02, 0.975, f"{n_diesel} states have waived or sidestepped their diesel tax this fall",
             fontsize=11.5, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.935, "Most let farm and forestry trucks run untaxed, off-road dyed diesel on public roads. "
             "Federally, the\n24.4¢ tax on dyed diesel used on highways is deferred Oct. 5 to Dec. 31 (EO 14435).",
             fontsize=8.5, color=INK2, va="top", linespacing=1.4)
    fig.text(0.02, 0.012, SOURCE_LINE, fontsize=5.6, color=MUTED, wrap=True)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.85, bottom=0.25)
    for ext in ("png", "svg"):
        fig.savefig(stem.with_suffix(f".{ext}"), facecolor=SURFACE)
    plt.close(fig)


def timeline(df: pd.DataFrame, stem: Path) -> None:
    x0, x1 = pd.Timestamp("2026-09-20"), pd.Timestamp("2027-02-12")
    order = ["federal", "tax_suspended", "dyed_everyone", "dyed_farm"]
    d = df[df.group.isin(order)].copy()
    d["g"] = d.group.map(order.index)
    d["end_sort"] = d.end.fillna(x1)
    d = d.sort_values(["g", "end_sort"]).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=200)
    _base(fig)
    ax.set_facecolor(SURFACE)
    h = 0.62
    ys, y = [], 0.0
    prev = None
    for _, r in d.iterrows():
        if prev is not None and r.g != prev:
            y += 0.55  # gap between groups
        ys.append(y)
        prev = r.g
        y += 1
    d["y"] = ys

    for _, r in d.iterrows():
        y = r.y
        color = INK2 if r.group == "federal" else GROUPS[r.group]["color"]
        start, end = r.start, r.end if pd.notna(r.end) else x1
        if r.state == "MO":  # ag-only until EO 26-20 opened it to all vehicles on Oct 9
            mid = pd.Timestamp("2026-10-09")
            ax.barh(y, mid - start, left=start, height=h, color=GROUPS["dyed_farm"]["color"], edgecolor=SURFACE, lw=1)
            ax.barh(y, end - mid, left=mid, height=h, color=color, edgecolor=SURFACE, lw=1)
        elif r.end_kind == "estimated":
            ax.barh(y, end - start, left=start, height=h, color=SURFACE, edgecolor=color, lw=1.2, hatch="////")
        else:
            ax.barh(y, end - start, left=start, height=h, color=color, edgecolor=SURFACE, lw=1)
        if r.end_kind == "renewable":
            ax.barh(y, x1 - end, left=end, height=h, color="none", edgecolor=color, lw=1, ls=(0, (3, 2)))
            label = f"{end:%b %-d}, renewable"
            lx = end + pd.Timedelta(days=2)
        elif r.end_kind == "open":
            label, lx = "no end date", None
        else:
            label = f"{end:%b %-d}" + (" (est.)" if r.end_kind == "estimated" else "")
            lx = end + pd.Timedelta(days=2)
        if lx is not None:
            ax.text(lx, y, label, va="center", fontsize=7.2, color=INK2)
        else:
            ax.text(x1 - pd.Timedelta(days=2), y, label, va="center", ha="right", fontsize=7.2,
                    color="white", fontweight="bold")

    ax.set_yticks(d.y, d.name, fontsize=8.5, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(x0, x1)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", colors=MUTED, labelcolor=INK2, length=0, labelsize=8)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    today = pd.Timestamp(AS_OF)
    ax.axvline(today, color=INK, lw=1)
    ax.text(today + pd.Timedelta(days=1.5), -0.75, f"Today ({AS_OF:%b} {AS_OF.day})",
            fontsize=7, color=INK, va="center")
    ax.axvline(pd.Timestamp("2027-01-01"), color=BASE, lw=0.8)

    handles = [Patch(fc=INK2, label="Federal dyed-diesel deferral"),
               *[Patch(fc=GROUPS[k]["color"], label=GROUPS[k]["label"]) for k in order[1:]],
               Patch(fc=SURFACE, ec=MUTED, hatch="////", label="End date is a 120-day count, not in the order")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(-0.17, -0.015), ncol=2, frameon=False,
              fontsize=7.2, labelcolor=INK2, handlelength=1.4, borderaxespad=0, columnspacing=1.2)

    fig.text(0.02, 0.98, "Most diesel relief expires by Dec. 31", fontsize=11.5, fontweight="bold",
             color=INK, va="top")
    fig.text(0.02, 0.945, "Start and end dates in each order. Missouri opened its order to all vehicles on Oct. 9; "
             "Texas's\nproclamation lapses after 30 days unless the governor renews it.",
             fontsize=8.5, color=INK2, va="top", linespacing=1.4)
    fig.text(0.02, 0.012, SOURCE_LINE, fontsize=5.6, color=MUTED, wrap=True)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.86, bottom=0.14)
    for ext in ("png", "svg"):
        fig.savefig(stem.with_suffix(f".{ext}"), facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    df = load()
    tile_map(df, OUT / "relief_map")
    timeline(df, OUT / "relief_timeline")


if __name__ == "__main__":
    main()
