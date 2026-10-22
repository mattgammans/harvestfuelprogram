"""2021 VIUS public-use microdata: agricultural vehicles (KINDOFBUS 05) - pickup share of trucks, diesel share,
miles, mpg, and share refueled at own facility. Weighted by TABWEIGHT; the +/- is an approximate 95% interval
using the unweighted n (the PUF has no replicate weights), stated as such."""
from __future__ import annotations

import math
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load() -> pd.DataFrame:
    z = zipfile.ZipFile(ROOT / "data" / "raw" / "src3_vius_2021_puf_csv.zip")
    d = pd.read_csv(z.open("vius_2021_puf.csv"), low_memory=False, dtype=str)
    d["w"] = d["TABWEIGHT"].astype(float)
    for c in ("MILESANNL", "MPG"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d[d["KINDOFBUS"] == "05"]


def share(df: pd.DataFrame, mask: pd.Series) -> dict:
    p = df.loc[mask, "w"].sum() / df["w"].sum()
    n = len(df)
    half = 1.96 * math.sqrt(p * (1 - p) / n)
    return {"p": p, "lo": max(0.0, p - half), "hi": min(1.0, p + half), "n": n}


def wmean(df: pd.DataFrame, col: str) -> dict:
    s = df[[col, "w"]].dropna()
    s = s[s[col] > 0]
    m = (s[col] * s["w"]).sum() / s["w"].sum()
    sd = math.sqrt(((s[col] - m) ** 2 * s["w"]).sum() / s["w"].sum())
    half = 1.96 * sd / math.sqrt(len(s))
    return {"p": m, "lo": m - half, "hi": m + half, "n": len(s)}


def summarize() -> dict:
    ag = load()
    fueled = ag[ag["FUELTYPE"].isin(["10", "20"])]
    pickups = fueled[fueled["BTYPE"] == "01"]
    dpick = pickups[pickups["FUELTYPE"] == "20"]
    heavy = fueled[(fueled["FUELTYPE"] == "20") & fueled["GVWR_CLASS"].isin(["6", "7", "8"])]
    fw = lambda df: df[df["FUELWHERE"].isin(["1", "2", "3", "4", "5"])]  # noqa: E731
    return {
        "pickup_share_of_ag_trucks": share(fueled, fueled["BTYPE"] == "01"),
        "diesel_share_of_ag_pickups": share(pickups, pickups["FUELTYPE"] == "20"),
        "diesel_pickup_miles_per_year": wmean(dpick, "MILESANNL"),
        "diesel_pickup_mpg": wmean(dpick, "MPG"),
        "own_facility_share_diesel_pickups": share(fw(dpick), fw(dpick)["FUELWHERE"] == "3"),
        "own_facility_share_diesel_class6to8": share(fw(heavy), fw(heavy)["FUELWHERE"] == "3"),
        "own_facility_share_diesel_ND_all": share(fw(ag[(ag["REGSTATE"] == "ND") & (ag["FUELTYPE"] == "20")]),
                                                  fw(ag[(ag["REGSTATE"] == "ND") & (ag["FUELTYPE"] == "20")])["FUELWHERE"] == "3"),
    }


if __name__ == "__main__":
    for k, v in summarize().items():
        print(f"{k}: {v['p']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}] n={v['n']}")
