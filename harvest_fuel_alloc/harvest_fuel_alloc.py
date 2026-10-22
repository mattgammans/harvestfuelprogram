"""Hypothetical allocation of the row-crop share of USDA's $8B Harvest Fuel Relief Program.

Assumptions: all $8B reaches farmers, split across groups in the same proportions as last year's Farmer Bridge
Assistance (FBA) payments: specialty crops 1/12 ($1B of $12B); the $11B row-crop share divided between crops with an
ERS cost-of-production budget (corn, soybeans, wheat, cotton, rice, sorghum, barley, oats, peanuts) and the other FBA
row crops (pulses, minor oilseeds) by actual FBA payments (FBA rate x FSA 2025 eligible acres). Only the ERS-budget
crops' share is allocated here; payments are per acre, with FBA acreage rules (91 FR 8360).

Data:
  ERS Commodity Costs and Returns, 2025 "Fuel, lube, and electricity" $/planted acre by crop and ERS Farm Resource Region
    (county's region via the ERS crosswalk; U.S. value where ERS has no regional estimate).
  ERS cost-of-production forecasts (Oct. 2026): U.S. 2026F "Fuel, lube, and electricity" $/planted acre by crop.
  FSA planted (and failed) acres by county and crop: 2026 for the allocation, 2025 for the FBA split.

Scenarios (the pool is split in proportion to each county-crop's acres x the per-acre basis):
  S1  Farmer Bridge formula (91 FR 8360), 2026 inputs: national rate per crop = factor x max(0, cost - yield x price),
      ERS 2026F total cost and Oct. 2026 WASDE 2026/27 yield and price (peanuts, not in WASDE, carry forward USDA's 2025
      modeled loss = FBA rate / 0.3041). No diesel input.
  S2  projected 2026 fuel expenditure for a crop, national: ERS U.S. 2026F fuel, lube and electricity $/acre
      -> one rate per crop nationwide.
  S3  projected 2026 fuel expenditure for a crop by ERS region: ERS 2025 regional $/acre x the crop's ERS national
      2026F/2025 ratio (ERS publishes no regional 2026 forecast).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch

HERE = Path(__file__).resolve().parent
RAW = HERE / "data"
OUT = HERE / "output"

# Chart ink (dataviz reference palette, light mode) and square tile-grid positions (col, row), as in
# ../analysis/relief_map_figures.py; copied so this folder runs on its own.
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
TILES = {
    "AK": (0, 0), "ME": (11, 0), "VT": (10, 1), "NH": (11, 1),
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
PROGRAM_USD = 8e9  # USDA, Oct. 19, 2026 (farmdoc daily / Agri-Pulse)
TITLE_I_SHARE = 11 / 12  # Farmer Bridge Assistance split: $11B row crops of $12B (Specialty Crop Caucus, Dec. 18, 2025)
FSA_2025_XLSX = RAW / "fsa_acres_2025" / "2025_fsa_acres_web_010526.xlsx"  # acreage behind the FBA split
MIN_ACRES = 50_000  # below this, per-acre values rest on a handful of farms; shown as n/a on the map
FSA_XLSX = RAW / "fsa_acres_2026" / "2026_fsa_acres_web_100126.xlsx"
ERS_CROPS = ["corn", "soybeans", "wheat", "cotton", "rice", "sorghum", "barley", "oats", "peanuts"]
CROPS = ERS_CROPS  # the crops allocated here; other FBA crops enter only through the FBA split
SCENARIOS = {"s1": "Farmer Bridge formula", "s2": "2026 fuel spending, national",
             "s3": "2026 fuel spending, by region"}
FBA_FACTOR_2025 = 0.3041  # FBA: share of modeled 2025 loss paid (91 FR 8360)

ERS_REGION = {1: "Heartland", 2: "Northern Crescent", 3: "Northern Great Plains", 4: "Prairie Gateway",
              5: "Eastern Uplands", 6: "Southern Seaboard", 7: "Fruitful Rim", 8: "Basin and Range",
              9: "Mississippi Portal"}
FSA_CROP = {"CORN": "corn", "SOYBEANS": "soybeans", "WHEAT": "wheat", "COTTON, UPLAND": "cotton",
            "COTTON, ELS": "cotton", "RICE": "rice", "SORGHUM": "sorghum", "BARLEY": "barley", "OATS": "oats",
            "PEANUTS": "peanuts", "CANOLA": "canola", "RAPESEED": "rapeseed", "CRAMBE": "crambe", "FLAX": "flax",
            "MUSTARD": "mustard", "SUNFLOWERS": "sunflower", "SAFFLOWER": "safflower", "SESAME": "sesame",
            "LENTILS": "lentils", "PEAS": "peas", "BEANS": "chickpeas"}
# FBA: "grazing, left standing, volunteer, green manure, or experimental" acres and cover crops are ineligible.
# Fresh-market use is dropped too (vegetable peas and sweet corn are specialty crops, not FBA row crops).
INELIGIBLE_USE = {"Grazing", "Left Standing", "Volunteer", "Green Manure", "Experimental", "Cover Only", "Fresh"}
DROP_TYPE = ("SWEET", "POPCORN", "EDAMAME", "ORNAMENTAL")
DRY_PEA_TYPES = {"YELLOW VARIETY", "GREEN", "AUSTRIAN", "ARVIKA/4010", "WRINKLED SEED"}
STATE_FIPS = {1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE", 11: "DC", 12: "FL", 13: "GA",
              15: "HI", 16: "ID", 17: "IL", 18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD",
              25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE", 32: "NV", 33: "NH", 34: "NJ",
              35: "NM", 36: "NY", 37: "NC", 38: "ND", 39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI", 45: "SC",
              46: "SD", 47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA", 54: "WV", 55: "WI", 56: "WY"}


def ers_fuel_2025() -> pd.DataFrame:
    rows = []
    for crop in ERS_CROPS:
        d = pd.read_csv(RAW / "ers_ccr" / f"{crop}.csv")
        d = d[(d.Item == "Fuel, lube, and electricity") & (d.Year == 2025)]
        rows += [(crop, r.Region, r.Value) for r in d.itertuples()]
    return pd.DataFrame(rows, columns=["crop", "region", "fuel_2025"]).set_index(["crop", "region"]).fuel_2025


def ers_fuel_2026_us() -> pd.Series:
    """ERS U.S. 2026F "Fuel, lube, and electricity" $/planted acre by crop (cost-of-production forecasts, Oct. 2026)."""
    fc = pd.read_csv(RAW / "ers_ccr" / "cost-of-production-forecasts-for-major-us-field-crops-2026f-2027f.csv")
    fc = fc[(fc.Item == "Fuel, lube, and electricity") & (fc.Year == "2026F")]
    return fc.set_index(fc.Commodity.str.lower()).Value


def fba_split() -> tuple[pd.DataFrame, dict]:
    """Last year's FBA payments by crop (rate x FSA 2025 eligible acres) and the resulting group shares of $12B."""
    a = fsa_acres(FSA_2025_XLSX)
    fba = pd.read_csv(RAW / "fba_table3_2025.csv").set_index("model_crop")
    t = a.groupby("crop").acres.sum().to_frame("acres_2025").join(fba.fba_rate_per_acre)
    t["fba_payment"] = t.acres_2025 * t.fba_rate_per_acre
    t["has_ers_budget"] = t.index.isin(ERS_CROPS)
    row_total = t.fba_payment.sum()
    ers_of_row = t.fba_payment[t.has_ers_budget].sum() / row_total
    shares = {"specialty": 1 - TITLE_I_SHARE, "row_ers": TITLE_I_SHARE * ers_of_row,
              "row_non_ers": TITLE_I_SHARE * (1 - ers_of_row), "fba_row_payments_computed": row_total}
    return t.sort_values("fba_payment", ascending=False), shares


def usda_loss_per_acre() -> pd.DataFrame:
    """Modeled economic loss per planted acre by crop for S4 (FBA formula with 2026 inputs where available)."""
    fc = pd.read_csv(RAW / "ers_ccr" / "cost-of-production-forecasts-for-major-us-field-crops-2026f-2027f.csv")
    fc = fc[(fc.Item == "Total, costs listed") & (fc.Year == "2026F")]
    cost = fc.set_index(fc.Commodity.str.lower()).Value
    w = pd.read_csv(RAW / "wasde" / "wasde1026_us_2026_27.csv").set_index("crop")
    fba = pd.read_csv(RAW / "fba_table3_2025.csv").set_index("model_crop")
    rows = {}
    for crop in fba.index:
        if crop in w.index and crop in cost.index:
            rev = w.loc[crop, "yield"] * w.loc[crop, "price"]
            rows[crop] = {"cost": cost[crop], "gross_return": rev, "loss": max(0.0, cost[crop] - rev),
                          "loss_source": "ERS 2026F cost, WASDE Oct. 2026"}
        else:
            rows[crop] = {"cost": fba.cost_2025[crop], "gross_return": fba.yield_2025[crop] * fba.price_2025[crop],
                          "loss": fba.fba_rate_per_acre[crop] / FBA_FACTOR_2025,
                          "loss_source": "USDA 2025 modeled loss (FBA rate / 0.3041)"}
    return pd.DataFrame(rows).T


def county_region() -> pd.Series:
    x = pd.read_excel(RAW / "ers_reglink.xls", header=None, skiprows=3, usecols=[0, 1], names=["fips", "region"])
    x = x.dropna()
    return x.set_index(x.fips.astype(int)).region.astype(int).map(ERS_REGION)


def fsa_acres(path: Path = FSA_XLSX) -> pd.DataFrame:
    d = pd.read_excel(path, sheet_name="county_data", header=1)
    ctype = d["Crop Type"].fillna("").astype(str)
    keep = d.Crop.isin(FSA_CROP) & ~d["Intended Use"].isin(INELIGIBLE_USE) & ~ctype.str.contains("|".join(DROP_TYPE))
    keep &= ~(d.Crop.isin(["BARLEY", "OATS"]) & ctype.str.contains("CANOLA"))  # canola types misfiled as small grains
    keep &= (d.Crop != "PEAS") | ctype.isin(DRY_PEA_TYPES)
    keep &= (d.Crop != "BEANS") | (ctype.str.contains("GARBANZO") & ~ctype.str.contains("GREEN"))
    d = d[keep]
    d = d.assign(crop=d.Crop.map(FSA_CROP))
    chick = d.crop == "chickpeas"
    d.loc[chick, "crop"] = d.loc[chick, "Crop Type"].astype(str).map(
        lambda t: "chickpeas_large" if "LG" in t else "chickpeas_small")
    d = d.assign(fips=d["State County Code"].astype(int),
                 state=d["State Code"].astype(int).map(STATE_FIPS))
    return d.groupby(["state", "fips", "crop"], as_index=False)["Planted and Failed Acres"].sum().rename(
        columns={"Planted and Failed Acres": "acres"})


def ers_budget_region(row) -> str:
    """ERS region label used for this county's crop budget (rice and peanuts use their own sub-regions)."""
    if row.crop == "rice":
        if row.state == "CA":
            return "California"
        if row.state in ("TX", "LA"):
            return "Gulf Coast"
        if row.state == "AR" and row.ers_region != "Mississippi Portal":
            return "Arkansas Non-Delta"
        return "Mississippi River Delta"
    if row.crop == "peanuts":
        if row.ers_region == "Fruitful Rim":
            return "Fruitful Rim"
        if row.state in ("VA", "NC", "SC"):
            return "Southern Seaboard (VA, NC, SC)"
        return "Southern Seaboard (AL, GA)"
    return row.ers_region


def allocate() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Returns (county x crop detail, state table, national info)."""
    f25 = ers_fuel_2025()
    split_table, shares = fba_split()
    pool = PROGRAM_USD * shares["row_ers"]
    f26_us = ers_fuel_2026_us()

    a = fsa_acres()
    a = a[a.crop.isin(ERS_CROPS)]
    a["ers_region"] = a.fips.map(county_region())
    a["budget_region"] = a.apply(ers_budget_region, axis=1)
    us = f25.xs("U.S. total", level="region")
    a["used_us_value"] = [(c, r) not in f25.index for c, r in zip(a.crop, a.budget_region)]
    a["ers_fuel_usd_per_acre"] = [f25.get((c, r), us[c]) for c, r in zip(a.crop, a.budget_region)]
    growth = f26_us / us  # ERS national 2026F / 2025, by crop (about 1.28)
    a["ers_growth_2026"] = a.crop.map(growth)
    a["fuel_2026_per_acre"] = a.ers_fuel_usd_per_acre * a.ers_growth_2026  # regional, projected
    a["fuel_2026_us_per_acre"] = a.crop.map(f26_us)  # national
    loss = usda_loss_per_acre()
    a["usda_loss_per_acre"] = a.crop.map(loss.loss).astype(float)
    basis = {"s1": a.usda_loss_per_acre, "s2": a.fuel_2026_us_per_acre, "s3": a.fuel_2026_per_acre}
    for sc, per_acre in basis.items():
        a[f"pay_per_acre_{sc}"] = pool * per_acre / (a.acres * per_acre).sum()
        a[f"pay_{sc}"] = a.acres * a[f"pay_per_acre_{sc}"]

    g = a.groupby("state")
    s = g.agg(acres=("acres", "sum"))
    wtd = lambda col: (a.acres * a[col]).groupby(a.state).sum() / s.acres
    s["fuel_2025_per_acre_wtd"] = wtd("ers_fuel_usd_per_acre")
    s["fuel_2026_per_acre_wtd"] = wtd("fuel_2026_per_acre")
    s["fuel_2026_usd"] = (a.acres * a.fuel_2026_per_acre).groupby(a.state).sum()
    s["usda_loss_usd"] = (a.acres * a.usda_loss_per_acre).groupby(a.state).sum()
    s["share_acres_us_fallback"] = a.acres.where(a.used_us_value, 0).groupby(a.state).sum() / s.acres
    for sc in SCENARIOS:
        s[f"payment_{sc}"] = g[f"pay_{sc}"].sum()
        s[f"share_{sc}"] = s[f"payment_{sc}"] / pool
        s[f"per_acre_{sc}"] = s[f"payment_{sc}"] / s.acres
    s["shown_on_map"] = s.acres >= MIN_ACRES
    by_crop = a.pivot_table(index="state", columns="crop", values="acres", aggfunc="sum").reindex(columns=CROPS)
    s = s.join(by_crop.add_prefix("acres_").fillna(0))
    info = {"group_shares": {k: round(v, 4) for k, v in shares.items()}, "pool_usd": pool,
            "fba_split_table": split_table, "us_acres": a.acres.sum(),
            "us_fuel_2025": (a.acres * a.ers_fuel_usd_per_acre).sum(), "us_fuel_2026": (a.acres * a.fuel_2026_per_acre).sum(),
            "ers_growth_2026": growth.round(4).to_dict(),
            "share_acres_us_fallback": a.acres[a.used_us_value].sum() / a.acres.sum(),
            "s1_factor": pool / (a.acres * a.usda_loss_per_acre).sum(),
            "s1_loss": loss.loc[ERS_CROPS].assign(
                rate=lambda d: d.loss.astype(float) * pool / (a.acres * a.usda_loss_per_acre).sum()).round(2).to_dict("index")}
    return a, s.sort_values("per_acre_s3"), info


def wquantile(x: pd.Series, w: pd.Series, q: float) -> float:
    """Acre-weighted quantile: the value below which share q of acres fall."""
    o = x.argsort()
    x, cw = x.iloc[o].to_numpy(), w.iloc[o].cumsum().to_numpy()
    return float(x[(cw >= q * cw[-1]).argmax()])


def crop_summary(a: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sc in SCENARIOS:
        for crop, d in [*a.groupby("crop"), ("all eligible crops", a)]:
            d = d[d.acres > 0]
            x = d[f"pay_per_acre_{sc}"]
            rows.append({"scenario": sc, "crop": crop, "acres": d.acres.sum(), "payment_usd": d[f"pay_{sc}"].sum(),
                         "mean_per_acre": d[f"pay_{sc}"].sum() / d.acres.sum(),
                         **{n: wquantile(x, d.acres, q) for n, q in
                            [("p10_per_acre", 0.10), ("median_per_acre", 0.50), ("p90_per_acre", 0.90)]},
                         "share_acres_us_fallback": d.acres[d.used_us_value].sum() / d.acres.sum()})
    out = pd.DataFrame(rows)
    order = out[out.scenario == "s3"].set_index("crop").mean_per_acre.rank(ascending=False)
    return out.assign(o=out.crop.map(order)).sort_values(["scenario", "o"]).drop(columns="o").set_index(["scenario", "crop"])

BINS = [(0, 25, "#86b6ef", INK), (25, 30, "#5598e7", INK), (30, 40, "#2a78d6", "white"),
        (40, 60, "#1c5cab", "white"), (60, float("inf"), "#0d366b", "white")]
BIN_LABELS = ["Under $25", "$25–30", "$30–40", "$40–60", "$60 or more"]
NA_COLOR = "#efeee9"


def tile_map(s: pd.DataFrame, info: dict, sc: str, stem: Path) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    esc = lambda t: t.replace("$", r"\$")  # keep matplotlib from reading $...$ as math
    col = f"per_acre_{sc}"
    fig, ax = plt.subplots(figsize=(7.2, 5.5), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    gap = 0.08
    for st, (c, row) in TILES.items():
        if st in s.index and s.acres[st] >= MIN_ACRES:
            v = s[col][st]
            _, _, fc, tc = next(b for b in BINS if b[0] <= v < b[1])
            val = esc(f"${v:,.0f}")
        else:
            fc, tc, val = NA_COLOR, MUTED, "n/a"
        ax.add_patch(FancyBboxPatch((c + gap / 2, -row + gap / 2), 1 - gap, 1 - gap,
                                    boxstyle="round,pad=0,rounding_size=0.08", fc=fc, ec="none"))
        ax.text(c + 0.5, -row + 0.62, st, ha="center", va="center", fontsize=7.5, fontweight="bold", color=tc)
        ax.text(c + 0.5, -row + 0.32, val, ha="center", va="center", fontsize=6.6, color=tc)
    ax.set_xlim(-0.2, 12.2)
    ax.set_ylim(-7.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    handles = [Patch(fc=b[2], label=esc(l)) for b, l in zip(BINS, BIN_LABELS)]
    handles.append(Patch(fc=NA_COLOR, label="Under 50,000 acres"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=6, frameon=False, fontsize=7.5,
              labelcolor=INK2, handlelength=1.2, columnspacing=1.0, borderaxespad=0,
              title="Dollars per eligible acre", title_fontsize=7.5)

    pool = info["pool_usd"]
    nat = pool / info["us_acres"]
    shown = s[s.acres >= MIN_ACRES][col]
    lo, hi = shown.idxmin(), shown.idxmax()
    n = list(SCENARIOS).index(sc) + 1
    fig.text(0.02, 0.975, esc(f"Scenario {n}: split by {SCENARIOS[sc]}"),
             fontsize=11, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.935, esc(f"Hypothetical payment per acre from ${pool / 1e9:.2f} billion of USDA's $8 billion (the Farmer "
             f"Bridge share for ERS-budget crops).\nNational average ${nat:,.0f}; ranges from ${shown[lo]:,.0f} ({lo}) to "
             f"${shown[hi]:,.0f} ({hi})."), fontsize=8.3, color=INK2, va="top", linespacing=1.4)
    method = {
        "s1": "Farmer Bridge formula (91 FR 8360): one national rate per crop = factor × max(0, ERS 2026F total cost − Oct. "
              "2026 WASDE yield × price);\npeanuts (not in WASDE) carry forward USDA's 2025 modeled loss. No diesel input.",
        "s2": "One national rate per crop ∝ ERS's 2026 forecast of fuel, lube and electricity cost per planted acre (U.S.).\n"
              "No regional variation; state differences come from crop mix.",
        "s3": "Rate ∝ projected 2026 fuel, lube and electricity cost per acre by crop and ERS farm resource region: ERS 2025 "
              "regional cost\n× the crop's ERS national 2026/2025 ratio. States average their counties' regions.",
    }[sc]
    fig.text(0.02, 0.012, esc(method + "\nAcres: FSA 2026 planted acres of the 9 ERS-budget crops. Sources: USDA FSA; USDA ERS Commodity Costs "
             "and Returns;\nUSDA WASDE (Oct. 2026); Farmer Bridge rule (91 FR 8360)."),
             fontsize=5.4, color=MUTED, linespacing=1.4)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.21)
    for ext in ("png", "svg"):
        fig.savefig(stem.with_suffix(f".{ext}"), facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    a, s, info = allocate()
    OUT.mkdir(exist_ok=True)
    info.pop("fba_split_table").to_csv(OUT / "fba_2025_split_by_crop.csv", float_format="%.2f", index_label="crop")
    s.to_csv(OUT / "state_inputs_outputs.csv", float_format="%.4f", index_label="state")
    cs = crop_summary(a)
    cs.to_csv(OUT / "crop_per_acre_summary.csv", float_format="%.2f")
    a.to_csv(OUT / "county_crop_detail.csv", float_format="%.4f", index=False)
    for k_, v in info.items():
        print(f"{k_}: {v}")
    print(cs.round(2).to_string())
    for sc in SCENARIOS:
        tile_map(s, info, sc, OUT / f"per_acre_map_{sc}")


if __name__ == "__main__":
    main()
