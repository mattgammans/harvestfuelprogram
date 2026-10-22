# Appendix: the five-parameter estimate

Every number here is produced by `python analysis/run_all.py`; the estimate itself is in `analysis/simple_estimate.py`.

## A1. Policy definition

These are not counted as parameters:
- **Savings per gallon:** 19¢, the ND special fuel tax on clear diesel (23¢) minus the tax on dyed diesel (4¢), NDCC 57-43.2-02 and -03.
- **Window:** Sept. 29–Nov. 30, 2026 (63 days), per EO 2026-08.
- **Federal tax:** the 24.4¢ is not relieved, so federal revenue forgone is $0.
- **Eligible use:** licensed vehicles hauling agricultural products.

**Formula:** savings = Σ crops [production × share hauled off-farm in window] × (2 × one-way miles ÷ mpg ÷ tons per load) × $0.19

## A2. The five parameters

| # | Parameter | Corn | Soybeans | Wheat | Source |
|---|---|---:|---:|---:|---|
| 1 | 2026 production (M bu) | 578.5 | 203.7 | 282.44 | NASS Crop Production, Sept. 11, 2026 (corn, soybeans; nass_crop0926.txt) and Aug. 12, 2026 (spring wheat, durum; nass_crop0826.txt) |
| 2 | Share hauled off-farm in window | 0.433 | 0.605 | 0.101 | NASS Grain Stocks: Sept. 30, 2024 & 2025; Jan. 2025 & Jan. 12, 2026 (src2_grst*.txt); NASS Crop Production 2025 Summary, Jan. 12, 2026 (src2_cropan26.txt) |
| 3 | One-way haul (mi) | 27.8 | 27.8 | 24.5 | UGPTI DP-284 (Vachal 2015), ND corn Table 3.56 (also used for soybeans; no ND soybean table) and ND wheat Table 3.52 |
| 4 | Tons per load | 21.48 | 21.73 | 21.97 | UGPTI DP-284 Table 3.65 (bushels per load) weighted by UGPTI Infrastructure Needs 2024 Table 12 (share of ND grain by truck type) |
| 5 | Fuel economy (mpg) | 6.2 | 6.2 | 6.2 | ORNL Transportation Energy Data Book Ed. 40, Table 5.2: Class 7-8 combination trucks, 2020 average |

**Parameter 2, worked out.** All figures in thousand bushels, ND on-farm stocks.
- **2024:**
  - Corn: 1 − 325,000 ÷ 542,360 = 0.401.
  - Soybeans: 1 − 79,000 ÷ 245,625 = 0.678.
  - Wheat: (222,000 − 173,000) ÷ 368,285 × 63/91 = 0.092.
- **2025:**
  - Corn: 1 − 380,000 ÷ 711,000 = 0.466.
  - Soybeans: 1 − 105,000 ÷ 223,905 = 0.531.
  - Wheat: (221,000 − 168,000) ÷ 334,055 × 63/91 = 0.110.
- **Value used:** the average of the two years.
- **Caveat:** Dec. 1 stocks include a little old crop, and some corn is still unharvested on Dec. 1. The two push in opposite directions.

**Parameter 4, worked out.**
- Bushels per load by truck type come from DP-284 Table 3.65.
- Each is weighted by the share of ND grain delivered by that type (UGPTI 2024 Table 12): semi 55.0%, tandem 25.1%, tridem 12.6%, single 7.3%.
- Corn: 0.550 × 930 + 0.252 × 581 + 0.126 × 661 + 0.073 × 366 = 767 bu, which is 21.48 tons.

## A3. Calculation by crop

| Crop | Production (t) | × share | = tons hauled | Gal/ton = 2 × mi ÷ mpg ÷ t/load | Gallons | Savings (× $0.19) |
|---|---:|---:|---:|---|---:|---:|
| Corn | 16.20 M | 0.433 | 7.02 M | 2 × 27.8 ÷ 6.2 ÷ 21.48 = 0.418 | 2.93 M | $557K |
| Soybeans | 6.11 M | 0.605 | 3.70 M | 2 × 27.8 ÷ 6.2 ÷ 21.73 = 0.413 | 1.53 M | $290K |
| Wheat | 8.47 M | 0.101 | 0.86 M | 2 × 24.5 ÷ 6.2 ÷ 21.97 = 0.360 | 0.31 M | $58K |
| **Total** | | | **11.57 M** | | **4.76 M** | **$0.905 M** |

**Take-up.** The total above assumes every eligible truck gallon switches. If only trucks fueled mainly from farm tanks switch (52.8% of Class 6–8 diesel farm trucks, 2021 VIUS microdata, n≈2,300), savings are $0.48 million. Federal penalty exposure (at least $1,000 per violation, 26 U.S.C. §6715; no IRS relief as of Oct. 2, 2026) may lower take-up further.

## A4. Sensitivity (each parameter at its low and high value; all-switch basis)

| Input | Savings, low | Savings, high |
|---|---:|---:|
| Share hauled off-farm (2024-only vs. 2025-only stocks) | $0.89 M | $0.92 M |
| Haul distance (21.7 mi ND semi wheat trip to 41.7 mi second-choice point, DP-284) | $0.71 M | $1.37 M |
| Tons per load (all 5-axle semis to truck-count weighted fleet) | $0.74 M | $0.99 M |
| Fuel economy (6.2 to 5.1 mpg; ORNL T5.2 and T5.12) | $0.90 M | $1.10 M |
| Take-up (only trucks fueled from farm tanks, 53%, VIUS; vs. all) | $0.48 M | $0.90 M |

The range is driven almost entirely by haul distance and take-up. Every other input moves the total by $0.2 million or less.

## A5. Context

- **Per farm:** $0.905M ÷ 25,068 farms = $36 (all switch), or $19 at 53% take-up.
- **Per acre:** ÷ 16.6M acres of corn, soybeans and wheat = 5.4¢.
- **Per bushel hauled:** ÷ 402M bushels = 0.22¢.
- **Price rise:** EIA Midwest retail $6.53 (Sept. 28, 2026) − $3.74 (Sept.–Nov. 2025 average) = $2.79. 19¢ is 6.8% of it.
- **Share of the fall fuel shock:**
  - Fuel: corn and soybean harvest field fuel (UMN combine + grain cart: 3.44 and 3.48 gal/ac × NASS acres) + truck gallons = 43.7M gal.
  - Extra cost: × $2.79 = $122M.
  - The relief is **0.74%** of that (all switch), or 0.39% at 53% take-up.
- **Example farm** (1,000 ac corn + 1,000 ac soybeans, 160,000 bu):
  - Hauling: 883 gal, so savings are $168.
  - Harvest field fuel: 6,920 gal.
  - Higher harvest diesel bill: $21,733.
- **Where the forgone revenue would have gone** (NDCC 54-27-19, all-switch basis): state highway fund $543K; counties $231K; cities $86K; townships $31K; public transit $14K.
- **Statewide diesel tax holiday:** 59.3M gal of taxable highway diesel (FHWA MF-33SF 2024, Oct.–Nov. + 2 days) × $0.23 = $13.6M.
- **Per-acre payment at the order's cost:** $0.90M ÷ 21.8M harvested cropland acres = 4.1¢.

## A6. Road-use arithmetic (order of magnitude)

- **Loaded truck miles hauling the three crops in the window:** 14.8 million.
- **State fuel tax per loaded mile:** about 4.5¢ on clear diesel vs. under 1¢ on dyed.
- **Pavement cost:** FHWA's 2000 Highway Cost Allocation Study Addendum (Table 13) puts it at 12.7¢/mi (2000$) for an 80,000-lb 5-axle truck on rural interstates.
  - That is about 25¢ in 2026 dollars using CPI, or 41¢ using the highway construction cost index.
  - County and township roads cost more per mile.
- **For scale:** UGPTI puts local road needs at $618 million a year.

## A7. Cross-check: the fuller model

An earlier, more detailed model covers more hauling:
- Each crop's harvest timing comes from NASS Crop Progress.
- It adds sugarbeets, sunflower, dry beans and potatoes; field-to-bin trips; calves and fall anhydrous; and stored-grain sales.
- It applies the 53% farm-tank take-up and a small border loss.

It finds:
- 6.2M eligible truck gallons, of which 3.86M is harvest hauled to market and 0.39M is stored grain. The five-parameter estimate covers these same hauls with 4.76M.
- 3.2M switched gallons (range 2.3–4.5M).
- **$0.60M** in savings, between the five-parameter estimate's 53%-take-up value ($0.48M) and its all-switch value ($0.90M).

Every input of that model is listed with its source in `methods_inputs_and_calculations.docx` and `outputs/derived_params.csv`.
