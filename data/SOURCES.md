# Data sources

All files are in `data/raw/`. Everything was accessed on **2026-09-30** unless noted. HTML pages were
saved with `curl` using a browser user agent. "Secondary" means news reporting, used only where no
primary document was available.

## Policy documents (primary)

| File | Source | URL | Notes |
|---|---|---|---|
| `nd_EO_2026-08.pdf` | ND Governor, Executive Order 2026-08 | https://www.governor.nd.gov/sites/default/files/documents/Executive%20Order%202026-08%20Diesel%20emergency.pdf | Scanned; read visually (no text layer). The handwritten signing day is hard to read ("27th"/"29th"). |
| `nd_gov_release.html` | Governor's release, 9/29/2026 | https://www.governor.nd.gov/news/armstrong-declares-diesel-emergency-takes-action-provide-relief-fuel-costs-agricultural | Source for "does not affect the federal ... 24.4-cent" and Goehring's 19¢ quote. |
| `ndcc_57-43.2.pdf`, `.txt` | NDCC ch. 57-43.2 (special fuels tax) | https://ndlegis.gov/cencode/t57c43-2.pdf | §§02, 02.3, 03, 19, 41. |
| `ndcc_54-27.pdf`, `.txt` | NDCC ch. 54-27 (HTDF split, §54-27-19) | https://ndlegis.gov/cencode/t54c27.pdf | |
| `nd_fuel_tax_rates.pdf` | ND Tax Commissioner, fuel tax rates by customer | https://www.tax.nd.gov/sites/www/files/documents/guidelines/business/motor-fuel/ndfueltaxrates1.pdf | Shows that the only 19¢ special-fuel refund is for reefer units. |
| `irs_IR-2024-265_milton.html` | IRS IR-2024-265 (precedent) | https://content.govdelivery.com/accounts/USIRS/bulletins/3bb6f6e | Penalty relief conditioned on paying the 24.4¢. |
| `tr_texas_wildfire_2024.html` | Thomson Reuters summary of IRS IR-2024-67 | https://tax.thomsonreuters.com/news/dyed-diesel-penalty-relief-granted-due-to-texas-wildfires/ | Secondary summary of an IRS release. |

## Other states (mostly secondary)

| File | What | URL |
|---|---|---|
| `dtn_nebraska_2states.html` | NE / AL / LA actions (DTN 9/25) | https://www.dtnpf.com/agriculture/web/ag/news/business-inputs/article/2026/09/25/nebraska-2-states-allow-farm-diesel |
| `ne_faq_ruralradio.html` | NE Governor's FAQ on EO 26-21 (via Rural Radio) | https://ruralradio.com/kuvr/news/faq-what-nebraska-farmers-need-to-know-about-dyed-diesel-under-pillens-executive-order/ |
| `mansfield_emergency_provisions.html` | Fuel-distributor summary of state provisions (incl. GA tax suspension) | https://mansfield.energy/2026/09/30/whats-that-emergency-fuel-provisions/ |
| `states_la_gov.html` | Louisiana Governor release (primary) | https://gov.louisiana.gov/news/5178 |
| `states_tx_gov.html` | Texas Governor release (primary) | https://gov.texas.gov/news/post/governor-abbott-waives-dyed-diesel-restrictions |
| `states_ok_gov.html` | Oklahoma Governor release (primary) | https://oklahoma.gov/governor/newsroom/newsroom/2026/governor-stitt-issues-order-to-bring-relief-for-agriculture-comm.html |
| `states_ar_neareport.html` | Arkansas EO 26-15 (news) | https://neareport.com/2026/09/30/sanders-signs-order-allowing-dyed-diesel-in-qualifying-farm-logging-vehicles/ |
| `states_in_wfyi.html` | Indiana (news) | https://www.wfyi.org/statewide/2026-09-30/braun-extends-gas-tax-holiday-adds-relief-for-farmers |
| `states_sd_drgnews.html`, `states_sd_keloland.html` | South Dakota EO 2026-11 (text of the governor's release, reprinted) | https://drgnews.com/2026/09/29/governor-rhoden-provides-flexibility-for-farmers-at-harvest/ |
| `states_mn_boreal.html` | Minnesota: a senator's request; no gubernatorial action found | https://www.boreal.org/2026/09/26/585146/senator-hauschild-calls-for-immediate-state-and-federal-diesel-relief-for-northern-minnesota |
| `states_mt_gov.html` | Montana: hours-of-service relief only | https://news.mt.gov/Governors-Office/Governor-Gianforte-Issues-Executive-Order-to-Extend-Federal-Fuel-Hauling-Flexibility-to-Montana-Carriers |
| `spokesman_whitehouse_dyed.html` | Reuters (via Spokesman-Review): White House weighing federal dyed-diesel relief | https://www.spokesman.com/stories/2026/sep/28/white-house-weighs-red-dyed-diesel-tax-relief-to-l/ |
| `inforum_article.html`, `states_nd_*.html` | ND news coverage | see files |

## Prices

| File | Source | URL |
|---|---|---|
| `eia_pet_pri_gnd_w.xls` | EIA weekly U.S. retail diesel (No. 2) | https://www.eia.gov/dnav/pet/xls/PET_PRI_GND_DCUS_NUS_W.xls |
| `eia_pet_pri_gnd_r20_w.xls` | EIA weekly Midwest (PADD 2) retail diesel | https://www.eia.gov/dnav/pet/xls/PET_PRI_GND_DCUS_R20_W.xls |
| (manual) | AAA, ND average diesel: $6.14 on 9/30/2026 and a $6.25 record on 9/21; U.S. record $6.53 on 9/22 | As quoted by InForum 9/29/2026. AAA's state pages are not scriptable, so these values were **not independently verified**. |

No free public source for the dyed-versus-clear rack spread was found. OPIS and DTN rack data are paywalled. The
analysis values the relief at the statutory tax difference (19¢), which is what the order changes.

## Crops

| File | Source | URL |
|---|---|---|
| `nass_crop0926.pdf`, `.txt` | NASS Crop Production, 9/11/2026 (Sept. 1 forecasts: corn, soybeans, sugarbeets) | https://esmis.nal.usda.gov/sites/default/release-files/796056/crop0926.pdf |
| `nass_crop0826.pdf`, `.txt` | NASS Crop Production, 8/12/2026 (spring wheat, durum, barley, dry beans) | https://esmis.nal.usda.gov/sites/default/release-files/796015/crop0826.pdf |
| `nass_prog3926.pdf`, `.txt` | NASS Crop Progress, week ending 9/27/2026 (released 9/28) | https://esmis.nal.usda.gov/sites/default/release-files/796082/prog3926.pdf |
| `nass_prog3826.pdf` | NASS Crop Progress, week ending 9/20/2026 | https://esmis.nal.usda.gov/sites/default/release-files/796068/prog3826_0.pdf |

## Farm finance and benchmarks (files prefixed `finance_`)

| File | Source | URL / note |
|---|---|---|
| `finance_census22_nd_st38_1_{001,004,041,072}_*.pdf` | 2022 Census of Agriculture, ND Tables 1, 4, 41, 72 | https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_1_State_Level/North_Dakota/ (`_009_010` was downloaded by mistake and is unused) |
| `finance_ers_fiws_september-3-2026-release.zip` | ERS Farm Income and Wealth Statistics, Sept. 3, 2026 (ND diesel expense 2025 = $359,817K; ND NFI) | https://www.ers.usda.gov/data-products/farm-income-and-wealth-statistics/ |
| `finance_nass_fpex0726.pdf` | NASS Farm Production Expenditures 2025 (Plains region) | https://downloads.usda.library.cornell.edu (fpex0726) |
| `finance_nass_agpr0926.pdf` | NASS Agricultural Prices, 9/29/2026 (diesel index; ND prices received) | esmis.nal.usda.gov |
| `finance_ndsu_2026_ec16xx.pdf` | NDSU Extension 2026 projected crop budgets (EC1654, 1656, 1659, 1660) | https://www.ndsu.edu/agriculture/extension/ |
| `finance_raff_Fall2025_ND_Farm_Income_Outlook.pdf` | NDSU RaFF/CAPTS ND farm income outlook | ndsu.edu |
| `finance_ams_3878_nd_daily_grain_bids_20260930.pdf` | USDA AMS ND daily grain bids, 9/30/2026 | https://www.ams.usda.gov/mnreports/ams_3878.pdf |
| `finance_newscoopnd_*`, `finance_inforum_*`, `finance_prairiepublic_*`, `finance_agdaily_*` | News: NDSU's Haugen (+$5-8/ac), NDFU comments, AAA prices | secondary |

## Top-down gallons (files prefixed `topdown_`)

| File | Source | URL / note |
|---|---|---|
| `topdown_eia_adjusted_distillate_by_enduse_ND_annual.xls`, `.html` | EIA adjusted sales of distillate by end use, ND (farm: 194,938K gal in 2020; the series ended in 2020) | https://www.eia.gov/dnav/pet/pet_cons_821dsta_dcu_SND_a.htm |
| `topdown_fhwa_hs2024_mf33sf.*` | FHWA Highway Statistics 2024, MF-33SF (ND monthly special fuel: Sep 30.66M, Oct 26.68M, Nov 30.58M gal) | https://www.fhwa.dot.gov/policyinformation/statistics/2024/ (fetched with `curl -k` because of a certificate-chain error) |
| `topdown_fhwa_hs2024_mf21.*`, `mf2.*`, `mf24.*` | FHWA MF-21, MF-2, MF-24 | same |
| `topdown_ndtax_5{5,6,7}th_biennial_report.pdf` | ND Tax Commissioner biennial reports (special fuel tax collections) | https://www.tax.nd.gov/.../publications/ |

## Parameters and law (files prefixed `params_`)

| File | Source |
|---|---|
| `params_ugpti_dp284_farm_truck_fleet.pdf` | Vachal, *Northern Plains Grain Farm Truck Fleet & Marketing Patterns*, UGPTI DP-284 (2015). Haul miles, fleet mix, loads |
| `params_ugpti_2024_infrastructure_needs.pdf` | UGPTI, *Infrastructure Needs: ND County, Township and Tribal Roads and Bridges 2024-2043* |
| `params_ugpti_dp143_regional_elevator_survey.pdf` | UGPTI DP-143 (2001) |
| `params_ornl_tedb_ed40.pdf` | ORNL Transportation Energy Data Book, Ed. 40 (truck mpg) |
| `params_fhwa_hcas2000_addendum.html`, `params_fhwa_hcas1997_*` | FHWA Highway Cost Allocation Study, 1997 and 2000 Addendum (Table 13: 80-kip rural interstate pavement 12.7¢/mi, verified) |
| `params_irs_pub225.pdf`, `params_irs_pub510_2025-12.pdf` | IRS Pubs. 225 and 510 (dyed fuel in farm trucks on the highway; quote verified) |
| `params_usc26_{4041,4082,6427,6715}.html`, `params_ecfr_26cfr48.4082-1.xml` | Federal statute and regulations |
| `params_ecfr_40cfr1090.xml`, `params_epa_fuel_waivers_list.html` | EPA: 15 ppm for all diesel (§1090.305); waiver list (no ND/TX diesel waiver as of 9/30) |
| `params_texas_abbott_letter_zeldin_ulsd_waiver.pdf`, `params_texas_gov_dyed_diesel_20260928.html` | Texas request for an EPA waiver |
| `params_dahl2012_ideas_repec.html`, `params_winebrake2015_*`, `params_usaee_hdv_rebound_trucking.pdf` | Elasticity literature (abstracts only; the Dahl U.S. diesel value is from a secondary citation) |

## Sources added in the second pass (replacing judgment parameters)

These were accessed 2026-09-30. `analysis/derive.py` uses the files marked **used**; the rest are supporting context.

| Files | Source | Used for |
|---|---|---|
| `src2_cropprog_*.txt` (127 releases) | NASS Crop Progress, fall weeks 2016–2025 (ESMIS) | **used**: ND % harvested near Nov 30 (corn, soybeans, sugarbeets, sunflower) |
| `src2_grst0924/0925/0125/0126/0926.txt` | NASS Grain Stocks | **used**: ND on-farm stocks Sept 1 and Dec 1 (wheat, barley, corn, soybeans) |
| `src2_cropan25.txt`, `src2_cropan26.txt` | NASS Crop Production Annual Summaries | **used**: 2024–25 production; 2025 sunflower, canola, potatoes |
| `src2_acrg0626.txt` | NASS Acreage, June 30, 2026 | **used**: 2026 canola and sunflower acres |
| `src2_catl0126.txt` | NASS Cattle, Jan 30, 2026 | **used**: 2025 calf crop |
| `src2_ers_fertilizer_use_price_all_tables.xls` | USDA ERS fertilizer use | **used**: ND corn N rate |
| `src2_ndsu_*`, `src2_ams_2100_*`, `src2_ndda_*` | NDSU guidance, AMS auction summary, NDDA fertilizer tonnage | context. The NDDA tonnage report is internally inconsistent and **not used** |
| `src3_umn_lazarus_machinery_cost_estimates.*` | UMN Machinery Cost Estimates, July 2024 | **used**: fuel gal/ac per field operation |
| `src3_isu_pm709_fuel_field_ops.*` | ISU PM 709 (2001) | **used**: anhydrous applicator fuel |
| `src3_nass_usual_planting_harvesting_dates_2010.*` | NASS Usual Planting and Harvesting Dates (2010) | **used**: ND dry bean and potato harvest timing |
| `src3_vius_2021_puf_csv.zip`, `src3_vius_2021_puf_data_dictionary.xlsx` | USDOT/Census 2021 VIUS public-use microdata | **used** via `analysis/vius.py`: ag pickup share, diesel share, miles, mpg, refueling location |
| `src3_bls_cpiu_*.json`, `src3_dot_nhcci_r94d-n4f9.csv`, `src3_fhwa_bpi_pt2006q4.html` | BLS CPI-U; DOT NHCCI; FHWA Bid Price Index | **used**: pavement cost inflator |
| `src3_epa_wrrda_farm_oil_storage_study_2015.*` | EPA, Oil Storage on U.S. Farms (2015) | context on on-farm fuel storage |
| `src3_eia_*` | EIA distillate prices excluding taxes (discontinued) | not used; the series end in 2010 or 2022 |
| `src4_acsharvest_*.html`, `src4_mdf_receiving-stations.html`, `src4_agweek_acs_2026_prepile.html`, `src4_gfherald_beet_drivers.html` | American Crystal and Minn-Dak receiving sites; ND beet acres; a news example of haul distance | **used**: beet haul geometry |
| `src4_census22_nd_county_st38_2_008_008.*` | 2022 Census of Agriculture, Table 8 (county) | **used**: county harvested cropland (border share, RRV) |
| `src4_ugpti_dp143/284/314/319.*` | UGPTI reports | DP-284 **used** (also as `params_ugpti_dp284_*`); others are context on elevator flows |
| `src4_*` news/government pages | State orders, Nebraska FAQ, take-up search | context. No take-up data exist |
| `src5_census22_nd_table47_landuse.pdf` | 2022 Census of Agriculture, Table 47 | **used**: intensive-tillage acres |
| `src5_census_gazetteer_2023_counties_nd.zip` | Census 2023 Gazetteer, counties | **used**: county land areas |
| `src5_ndda_livestock_auction_markets.pdf` | NDDA licensed livestock auction markets | **used**: 10 cattle markets (duplicate license and horse-only entries excluded) |
| `src5_osu_feeder_cattle_lot_size.html` | OSU Beef Team: pot load ≈ 80 head of 500-lb calves | **used** |
| `dp284.txt`, `t8.txt` | `pdftotext -layout` extracts of DP-284 and Census Table 8 | derived text; `t8.txt` is regenerated by the code if missing |

Removed: two EIA error pages, and a duplicate VIUS zip.

## Added Oct. 2, 2026

| File | Source | URL | Notes |
|---|---|---|---|
| `ers_farm_sector_income_forecast_20260903.html` | USDA ERS, Farm Sector Income Forecast (updated 9/3/2026) | https://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/farm-sector-income-forecast | Quote: "Fuel and oil expenses are also expected to increase (by $4.8 billion or 28.8 percent)." |
| `finance_ers_fiws_september-3-2026-release.zip` | ERS FIWS data, Sept. 3, 2026 release | https://www.ers.usda.gov/media/29517/september-3-2026-release.zip (listed on https://www.ers.usda.gov/data-products/farm-income-and-wealth-statistics/data-files-us-and-state-level-farm-income-and-wealth-statistics) | Series EXAUSIPPT--P (U.S. fuel & oil: 2025 $16,786,376K; 2026F $21,624,155K); EXANDIPPTDSP (ND diesel 2025 $359,817K) |
| `fred_GASDESW.csv` (not obtained) | FRED weekly U.S. diesel (GASDESW) | https://fred.stlouisfed.org/series/GASDESW | Download timed out; Figure 1 uses the identical EIA series (eia_pet_pri_gnd_w.xls) |
| VIUS (link only) | Census Bureau, 2021 VIUS datasets | https://www.census.gov/programs-surveys/vius/data/datasets.html | Linked in the article |
| ORNL TEDB Ed. 40 (link only) | ORNL Transportation Energy Data Book, Ed. 40 | https://tedb.ornl.gov/wp-content/uploads/2022/03/TEDB_Ed_40.pdf | Linked in the article; Table 5.2 |

| `nass_acrg0626.txt` | USDA NASS Acreage, June 30, 2026 (principal crops planted by state) | https://usda.library.cornell.edu/sites/default/release-files/795961/acrg0626.txt | Used by `analysis/harvest_fuel_alloc.py` (accessed Oct. 20, 2026). |
| `fsa_acres_2026/2026_fsa_acres_web_100126.xlsx` | USDA FSA 2026 crop acreage data, as of Oct. 1, 2026 (county × crop planted and failed acres) | https://www.fsa.usda.gov/sites/default/files/2026-10/IV4i8vWMYLge.zip (listed on FSA crop acreage data page as "2026 acreage data as of October 9, 2026") | Used by `analysis/harvest_fuel_alloc.py` (accessed Oct. 20, 2026). |
| `ers_ccr/*.csv` | USDA ERS Commodity Costs and Returns: nine field crops (history incl. 2025 regional) and cost-of-production forecasts 2026F–2027F | https://www.ers.usda.gov/data-products/commodity-costs-and-returns | "Fuel, lube, and electricity," $/planted acre. Used by `analysis/harvest_fuel_alloc.py`. |
| `ers_reglink.xls` | USDA ERS county-to-Farm Resource Region crosswalk | https://www.ers.usda.gov/sites/default/files/images/reglink.xls | Used by `analysis/harvest_fuel_alloc.py`. |
| `eia_diesel_regions/PET_PRI_GND_DCUS_*_W.xls` | EIA weekly retail No. 2 diesel by region (U.S., PADD 1A/1B/1C, 2, 3, 4, 5 ex-CA, CA), through Oct. 19, 2026 | https://www.eia.gov/dnav/pet/xls/PET_PRI_GND_DCUS_{region}_W.xls | Used by `analysis/harvest_fuel_alloc.py` (accessed Oct. 20, 2026). |
