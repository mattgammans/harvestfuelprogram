# Harvest Fuel Relief: hypothetical allocations

Three ways the row-crop share of USDA's $8 billion Harvest Fuel Relief Program (announced Oct. 19, 2026) could be split, if the goal were to compensate farmers in proportion to their exposure to rising diesel prices.

To run it, use the project's virtualenv from this folder:

```
../.venv/bin/python harvest_fuel_alloc.py      # allocation, CSVs, state maps
../.venv/bin/python region_maps.py             # county maps by crop (2025 and projected 2026 fuel cost)
../.venv/bin/python crop_scenario_grid.py      # grids: corn/soy/wheat and cotton/rice x scenarios
```

The scripts read only `data/` and write to `output/`.

## Assumptions

- **All $8 billion reaches farmers.** Program and transaction costs are ignored.
- **Money is split across groups as last year's Farmer Bridge (FBA) payments were** (`output/fba_2025_split_by_crop.csv`).

  | Group | Share of $12B FBA | Share of $8B | Basis |
  |---|---:|---:|---|
  | Specialty crops and other commodities | 8.33% | $0.67B | $1B of $12B (Specialty Crop Caucus, Dec. 18, 2025) |
  | Row crops with an ERS cost budget (corn, soybeans, wheat, cotton, rice, sorghum, barley, oats, peanuts) | 90.34% | **$7.23B** | 98.55% of FBA row-crop payments |
  | Other FBA row crops (pulses, minor oilseeds) | 1.33% | $0.11B | 1.45% of FBA row-crop payments |

  FBA payments by crop = FBA rate (91 FR 8360, Table 3) × FSA 2025 eligible acres (FBA acreage rules). They sum to $10.60B, or 96% of the $11B budget. The shares use the computed total.

- **Only the ERS-budget crops' $7.23B is allocated here.** The specialty and non-ERS row-crop shares are held aside, so no proxy cost data is needed.
- **Payments are made per acre**, as in Farmer Bridge. Acres follow the FBA rule: grazing, left-standing, volunteer, green-manure, experimental and cover-crop acres are ineligible; forage and silage count; sweet corn, popcorn and fresh-market use are dropped.

## Data

All fuel figures come from USDA ERS. No EIA price data is used.

**Fuel cost per acre, 2025.** ERS Commodity Costs and Returns publishes 2025 "Fuel, lube, and electricity" cost per planted acre by crop and ERS Farm Resource Region.
- Each county is assigned its region with the ERS crosswalk. Rice and peanuts use ERS's own sub-regions.
- Where ERS has no estimate for a crop in a region, the U.S. value is used.

**Fuel cost per acre, 2026.** ERS's cost-of-production forecasts (Oct. 2026) give the U.S. 2026F value for the same line, by crop. The 2026F/2025 ratio is 1.28 for every crop except wheat (1.27). ERS publishes no regional 2026 forecast.

**Acres.** FSA planted (and failed) acres by county and crop: 2026 (as of Oct. 1, 2026) for the allocation, and 2025 (as of Jan. 5, 2026) for the FBA split.

## Scenarios

The $7.23 billion is split in proportion to each county-crop's acres × the per-acre basis below.

**S1: identical formula to last year's Farmer Bridge payments** (91 FR 8360, Table 3), with 2026 inputs. USDA says Harvest Fuel Relief uses the same inputs: FSA planted acres, ERS cost of production, and WASDE yields and prices.
- National rate per crop = factor × max(0, ERS 2026F "Total, costs listed" − Oct. 2026 WASDE 2026/27 yield × season-average price).
- The factor is set so payments sum to $7.23B: 0.317, against Farmer Bridge's 0.3041.
- Eight crops use 2026 inputs. Peanuts are not in WASDE, so they carry forward USDA's 2025 modeled loss (FBA rate ÷ 0.3041; `data/fba_table3_2025.csv`).
- There is no diesel input. Differences across states come only from crop mix.

**S2: projected 2026 fuel expenditure for a crop, calculated nationally.**
- Basis = ERS U.S. 2026F fuel, lube and electricity cost per acre.
- This gives one rate per crop nationwide.

**S3: projected 2026 fuel expenditure for a crop, by region.**
- Basis = ERS 2025 regional cost per acre × the crop's ERS national 2026F/2025 ratio.
- This rate varies by crop × ERS farm resource region. State figures average the regions of the state's counties.

National totals across eligible acres of the 9 crops:
- 2025 fuel, lube and electricity cost: $5.40 billion
- Projected 2026 cost: $6.91 billion

## Files

**`data/`**

| File | Source |
|---|---|
| `fsa_acres_2025/2025_fsa_acres_web_010526.xlsx` | USDA FSA Crop Acreage Data, 2025, as of Jan. 5, 2026 (posted as "January 12, 2026"). https://www.fsa.usda.gov/sites/default/files/2026-01/DoISjehvQfz9.ZIP. Used for the FBA split |
| `fsa_acres_2026/2026_fsa_acres_web_100126.xlsx` | USDA FSA Crop Acreage Data, 2026, as of Oct. 1 (posted Oct. 9). https://www.fsa.usda.gov/sites/default/files/2026-10/IV4i8vWMYLge.zip |
| `ers_ccr/<crop>.csv` (9 crops) | USDA ERS Commodity Costs and Returns. https://www.ers.usda.gov/data-products/commodity-costs-and-returns. Survey base years: corn 2021, soybeans 2023, wheat 2022, cotton 2019, rice 2021, peanuts 2023, sorghum 2019, barley 2019, oats 2023 |
| `ers_reglink.xls` | USDA ERS county-to-Farm Resource Region crosswalk. https://www.ers.usda.gov/sites/default/files/images/reglink.xls |
| `fr_2026-03456_fba.txt` | Farmer Bridge Assistance rule, 91 FR 8360 (Feb. 23, 2026) |
| `fba_table3_2025.csv` | Transcribed from FR Table 3: 2025 yield, price, cost, net return and rate by commodity |
| `wasde/wasde1026.pdf`, `.xls`, `.txt`; `wasde/wasde1026_us_2026_27.csv` | USDA WASDE-676, Oct. 2026. https://www.usda.gov/oce/commodity/wasde/wasde1026.pdf. The CSV transcribes U.S. 2026/27 October projections (pp. 11–17) |
| `ers_ccr/cost-of-production-forecasts-for-major-us-field-crops-2026f-2027f.csv` | ERS cost-of-production forecasts (Oct. 2026); 2026F total costs (S1) and fuel, lube and electricity (S2, S3) |
| `geo/geojson-counties-fips.json`, `geo/us-states.json` | County and state boundaries for the maps (plotly/datasets; PublicaMundi) |

All files were downloaded Oct. 20, 2026.

**`output/`**
- **`fba_2025_split_by_crop.csv`**: FBA 2025 rate, eligible acres and payment by crop, flagged by ERS budget.
- **`state_inputs_outputs.csv`**: one row per state, with these columns:
  - acres in total and by crop
  - acre-weighted ERS fuel cost per acre for 2025 and 2026, and total projected 2026 fuel cost
  - total modeled Farmer Bridge loss (S1 basis)
  - share of acres priced at the U.S. fallback
  - for each scenario: payment, share of the pool and payment per acre
- **`crop_per_acre_summary.csv`**: by scenario × crop. Acres, payment, mean, p10, median and p90 per acre (acre-weighted across county-crop cells), and the share of acres at the U.S. fallback.
- **`state_crop_per_acre.csv`**: state × crop (corn, soybeans, wheat, cotton, rice) average payment per acre by scenario.
- **`county_crop_detail.csv`**: every county × crop cell with all intermediate values.
- **`region_crop_values.csv`**: distinct values by crop × ERS region, with acre shares.
- **Maps**:
  - `per_acre_map_s1/s2/s3`: state payment per acre under each scenario
  - `region_map_baseline`: 2025 fuel cost per acre, by crop
  - `region_map_delta`: projected 2026 fuel cost per acre, by crop
  - `crop_scenario_grid`: corn, soybeans and wheat × the three scenarios
  - `crop_scenario_grid_cotton_rice`: cotton and rice × the three scenarios (own color bins: $50/75/100/150)

## Caveats

- **ERS's fuel line includes lube and irrigation electricity,** so it overstates diesel alone for irrigated rice, cotton and corn.
- **ERS's 2026 increase is national and the same for every crop** (about 28%). S3's regional pattern therefore equals ERS's 2025 regional pattern; regional differences in the diesel price rise are not captured.
- **Within-region variation is not captured.** Per-acre values vary only across ERS regions, so crop percentiles can coincide.
- **Silage and forage are priced at grain fuel costs,** which understates fuel used for chopping and hauling.
- **The non-row-crop share is not modeled.** Livestock, hay, specialty crops and the $0.67 billion non-row-crop share are outside the model.
