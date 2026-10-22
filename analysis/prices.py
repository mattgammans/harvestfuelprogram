"""EIA weekly retail diesel (U.S. and Midwest/PADD 2): tidy series, pre-shock baseline, figure."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

SERIES = {
    "us": ("eia_pet_pri_gnd_w.xls", "Weekly U.S. No 2 Diesel Retail Prices  (Dollars per Gallon)"),
    "midwest": ("eia_pet_pri_gnd_r20_w.xls", "Weekly Midwest No 2 Diesel Retail Prices  (Dollars per Gallon)"),
}

# Reference palette (dataviz skill, light mode): categorical slots 1-2, ink and grid tokens.
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"


def load_weekly(start: str = "2021-01-01") -> pd.DataFrame:
    frames = []
    for key, (fname, col) in SERIES.items():
        d = pd.read_excel(RAW / fname, sheet_name="Data 1", header=2)[["Date", col]]
        frames.append(d.rename(columns={"Date": "date", col: key}).set_index("date"))
    out = pd.concat(frames, axis=1).sort_index()
    return out[out.index >= start].dropna(how="all")


def summarize(w: pd.DataFrame, params: dict) -> dict:
    b0, b1 = params["inputs"]["prices"]["baseline_window"]
    base = w.loc[b0:b1].mean()
    last = w.dropna().iloc[-1]
    peak_date = w["midwest"].idxmax()
    return {
        "baseline_window": [b0, b1],
        "baseline_midwest": float(base["midwest"]),
        "baseline_us": float(base["us"]),
        "latest_date": str(w.dropna().index[-1].date()),
        "latest_midwest": float(last["midwest"]),
        "latest_us": float(last["us"]),
        "peak_midwest": float(w["midwest"].max()),
        "peak_midwest_date": str(peak_date.date()),
        "shock_midwest": float(last["midwest"] - base["midwest"]),
        "shock_nd_aaa": float(params["inputs"]["prices"]["nd_current_aaa"] - base["midwest"]),
        "avg_2025_midwest": float(w.loc["2025", "midwest"].mean()),
    }


def figure(w: pd.DataFrame, s: dict, relief: float, path: Path) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.plot(w.index, w["us"], color=ORANGE, lw=1.6, label="U.S. average")
    ax.plot(w.index, w["midwest"], color=BLUE, lw=1.6, label="Midwest (PADD 2)")

    # Pre-shock baseline, and the shock vs. relief bracket drawn to scale at the right edge.
    b0 = pd.Timestamp(s["baseline_window"][0])
    ax.hlines(s["baseline_midwest"], b0, w.index[-1], color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.text(pd.Timestamp("2024-10-01"), s["baseline_midwest"] - 0.42, f"Fall 2025 Midwest avg ${s['baseline_midwest']:.2f}",
            color=INK2, fontsize=8, va="top")
    x = w.index[-1] + pd.Timedelta(days=45)
    top, bot = s["latest_midwest"], s["baseline_midwest"]
    ax.plot([x, x], [bot, top], color=MUTED, lw=6, solid_capstyle="butt")
    ax.plot([x, x], [top - relief, top], color=INK, lw=6, solid_capstyle="butt")
    ax.text(x + pd.Timedelta(days=25), (top + bot) / 2, f"Price rise\n${top - bot:.2f}/gal", color=INK2,
            fontsize=8, va="center")
    ax.text(x + pd.Timedelta(days=25), top - relief / 2, "ND relief 19¢", color=INK, fontsize=8,
            va="center", fontweight="bold")

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(BASE)
    ax.spines["bottom"].set_color(BASE)
    ax.tick_params(colors=MUTED, labelcolor=INK2)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_ylim(2, 7.2)
    ax.set_xlim(w.index[0], w.index[-1] + pd.Timedelta(days=230))
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:.0f}"))
    ax.set_ylabel("Retail No. 2 diesel, $/gal", color=INK2)
    ax.legend(loc="upper left", frameon=False, labelcolor=INK2)
    ax.set_title("Diesel prices and the size of the relief", loc="left", color=INK, fontsize=10,
                 fontweight="bold")
    fig.text(0.01, 0.01, "Source: EIA weekly retail prices through " + s["latest_date"]
             + ". Bracket: latest Midwest price vs. Sep-Nov 2025 average; dark segment = 19¢ state tax relief.",
             color=MUTED, fontsize=6.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path)
    plt.close(fig)
