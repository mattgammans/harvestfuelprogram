// Render the article from outputs/article.json + outputs/article_fig1.png to diesel_relief_article.docx.
// Run: python analysis/simple_estimate.py && python analysis/article_data.py && node analysis/make_article_docx.js
const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  BorderStyle, ImageRun, HeadingLevel, ExternalHyperlink } = require("docx");

const ROOT = path.resolve(__dirname, "..");
const d = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs", "article.json"), "utf8"));
const FONT = "Calibri", W = 9360, FILL = "1C5CAB", LIGHT = "E8F0FB";
const b = { style: BorderStyle.SINGLE, size: 4, color: "C3C2B7" };
const borders = { top: b, bottom: b, left: b, right: b };

const t = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 22, bold: o.bold, italics: o.italics, color: o.color });
const p = (runs, o = {}) => new Paragraph({ children: [].concat(runs), spacing: { after: o.after ?? 160, line: 276 }, alignment: o.align });
const UGPTI_DP284 = "https://www.ugpti.org/resources/reports/details.php?id=821";
const ORNL_TEDB40 = "https://tedb.ornl.gov/wp-content/uploads/2022/03/TEDB_Ed_40.pdf";
const VIUS = "https://www.census.gov/programs-surveys/vius/data/datasets.html";
const bodyLink = (text, url) => new ExternalHyperlink({ link: url, children: [new TextRun({ text, font: FONT, size: 22, style: "Hyperlink" })] });
// Cell content: a string, or an array of parts: "text", { br: "text after a line break" }, { link: url, text }.
function richRuns(content, o) {
  const parts = Array.isArray(content) ? content : [content];
  return parts.flatMap((part) => {
    if (typeof part === "string") return [t(part, { size: 19, bold: o.bold, color: o.color })];
    if (part.br !== undefined) return [new TextRun({ text: part.br, font: FONT, size: 19, break: 1 })];
    return [new ExternalHyperlink({ link: part.link, children: [new TextRun({ text: part.text, font: FONT, size: 19, style: "Hyperlink" })] })];
  });
}
const cell = (content, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA }, borders, margins: { top: 60, bottom: 60, left: 100, right: 100 },
  shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
  children: [new Paragraph({ alignment: o.align, children: richRuns(content, o) })],
});
const table = (cols, header, rows, opts = {}) => new Table({
  width: { size: W, type: WidthType.DXA }, columnWidths: cols,
  rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, cols[i], { fill: FILL, color: "FFFFFF", bold: true, align: i >= (opts.rightFrom ?? 1) && i < (opts.rightTo ?? 99) ? AlignmentType.RIGHT : undefined })) })]
    .concat(rows.map((r) => {
      const strong = opts.boldRow && opts.boldRow(r);
      return new TableRow({ children: r.map((v, i) => cell(v, cols[i], { align: i >= (opts.rightFrom ?? 1) && i < (opts.rightTo ?? 99) ? AlignmentType.RIGHT : undefined, bold: strong, fill: strong ? LIGHT : undefined })) });
    })),
});
const caption = (label, text) => p([t(label, { bold: true, size: 20 }), t(text, { size: 20 })], { after: 80 });
const note = (text) => p(t(text, { size: 17, italics: true, color: "52514E" }), { after: 240 });

const P = d.params, R = Object.fromEntries(d.rows.map((r) => [r.crop, r]));
const usd0 = (x) => "$" + Math.round(x).toLocaleString("en-US");
const usdK = (x) => "$" + (Math.round(x / 10000) * 10000).toLocaleString("en-US");  // nearest $10,000 so parts sum to total
const M = (x, k = 1) => (x / 1e6).toFixed(k);
const pct = (x) => (100 * x).toFixed(0) + "%";
const pct1 = (x) => (100 * x).toFixed(1) + "%";

// ---------- Table 1: assumptions and data sources (layout and wording follow the author's edits of Oct. 2) ----------
const DP284 = { link: UGPTI_DP284, text: "Northern Plains Grain Farm Truck Fleet & Marketing Patterns report" };
const t1 = table([1887, 711, 952, 5810], ["Assumption", "Corn", "Soybeans", "Sources and notes"], [
  [["2026 production", { br: "(million bushels)" }], P.corn.production_mbu.toFixed(1), P.soybeans.production_mbu.toFixed(1),
    ["USDA NASS, Crop Production ", { br: "(Sept. 11, 2026)" }]],
  ["Share of crop hauled off the farm, Sept. 29–Nov. 30", pct(P.corn.share), pct(P.soybeans.share),
    ["(Production − Dec. 1 on-farm stocks) ÷ production. ", { br: "Source: USDA NASS, Grain Stocks, North Dakota on-farm stocks, 2024–25 average " }]],
  ["Average load (tons per truck)", P.corn.tons_per_load.toFixed(1), P.soybeans.tons_per_load.toFixed(1),
    [DP284, ". Bushels per load by truck type (Table 3.65), weighted by each type's share of ND grain hauling (UGPTI 2024, Table 12)"]],
  ["Average one-way trip (miles)", P.corn.miles.toFixed(1), P.soybeans.miles.toFixed(1),
    [DP284, " (UGPTI DP-284), Table 3.56, North Dakota corn deliveries (no separate soybean table; corn value used for both)"]],
  ["Truck fuel economy (miles per gallon)", d.mpg.toFixed(1), d.mpg.toFixed(1), [{ link: ORNL_TEDB40, text: "Oak Ridge National Laboratory, Transportation Energy Data Book, Ed. 40" }, ", Table 5.2"]],
  ["State tax savings (cents per gallon)", "19", "19", "NDCC 57-43.2: 23¢ on clear diesel minus 4¢ on dyed diesel"],
], { rightFrom: 1, rightTo: 3 });

// ---------- Table 2: savings by crop ----------
const rows2 = d.rows.map((r) => [r.crop[0].toUpperCase() + r.crop.slice(1), M(r.hauled_bu), Math.round(r.loads).toLocaleString("en-US"),
  M(r.miles), M(r.gallons, 2), usdK(r.savings)]);
rows2.push(["Total", M(d.rows.reduce((s, r) => s + r.hauled_bu, 0)), Math.round(d.total_loads).toLocaleString("en-US"), M(d.total_miles),
  M(d.total_gallons, 2), usdK(d.total_savings)]);
const t2 = table([1600, 1700, 1500, 1500, 1500, 1560], ["Crop", "Bushels hauled (million)", "Truckloads", "Miles driven (million)", "Diesel (million gallons)", "Savings"],
  rows2, { boldRow: (r) => r[0] === "Total" });

const fig = new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(ROOT, "outputs", "article_fig1.png")), transformation: { width: 600, height: 277 } })] });

const corn = R.corn, soy = R.soybeans;
const body = [
  new Paragraph({ children: [new TextRun({ text: "The impact of emergency diesel tax relief for agricultural producers", font: FONT, size: 34, bold: true })], spacing: { after: 240 } }),
  p(t(`On September 29, Gov. Kelly Armstrong declared a fuel emergency and signed an executive order letting licensed vehicles used in agricultural operations utilize red-dyed diesel on North Dakota highways through Nov. 30. Typically, red-dyed diesel can only be used for certain off-highway purposes. Red-dyed diesel includes 4 cents per gallon of North Dakota excise tax, compared to the 23 cents per gallon charged on regular diesel. The federal tax of 24.4 cents per gallon is unaffected by this policy. This policy comes in response to historically high diesel prices, which exceeded $6.50/gallon last month according to the U.S. Energy Information Administration (the series is also published by the Federal Reserve Bank of St. Louis). The historical time series of diesel prices can be seen in Figure 1 below:`)),
  fig,
  caption("Figure 1. ", `U.S. average retail price of No. 2 diesel, weekly, ${d.fig1.start_year}–2026. Prices peaked at $${d.fig1.peak.toFixed(2)} per gallon in the week of ${d.fig1.peak_date}.`),
  note("Source: U.S. Energy Information Administration, Weekly Retail Gasoline and Diesel Prices (FRED series GASDESW)."),
  p(t("The recently announced diesel tax relief will generate savings for farmers that utilize diesel fuel for on-highway purposes. This article estimates the impact of this executive order on North Dakota's corn and soybean farmers. To estimate savings generated, I first estimate the total number of truckloads hauled on-highway during the harvest season. Assumptions and data sources are shown in Table 1. I use USDA NASS Crop Production forecasts for 2026 production of each crop, USDA NASS Grain Stocks reports for the share of each crop hauled off the farm between Sept. 29 and Nov. 30, and NDSU's Upper Great Plains Transportation Institute (UGPTI) farm truck survey for the average truckload.")),
  p(t(`I combine the above estimates of truckloads with an assumed average one-way trip length of ${P.corn.miles} miles from the UGPTI farm truck survey, which gives total miles driven. I then apply an assumed truck fuel economy of ${d.mpg} miles per gallon from Oak Ridge National Laboratory's Transportation Energy Data Book to convert miles into gallons of diesel. Each gallon that switches to dyed diesel saves 19 cents in state tax.`)),
  caption("Table 1. ", "Assumptions and data sources"),
  t1,
  new Paragraph({ spacing: { after: 240 }, children: [] }),
  p([t(`Total savings by crop are shown in Table 2 below. I find that the order saves corn farmers about ${usdK(corn.savings)} and soybean farmers about ${usdK(soy.savings)}, for a total of about ${usdK(d.total_savings)} on ${M(d.total_gallons, 1)} million gallons of diesel. This total assumes every eligible truck switches to dyed diesel. If only trucks already fueled from on-farm tanks switch (about 53% of heavy farm trucks in the `), bodyLink("2021 Vehicle Inventory and Use Survey", VIUS), t(`), savings would be about ${usdK(d.if_only_onhand)}. Federal penalties for using dyed diesel on highways also still apply unless the IRS grants relief, which may limit use. Trip length matters most: average trips of 21.7 to 41.7 miles imply total savings of $${M(d.haul_low, 2)} to $${M(d.haul_high, 2)} million. These values would imply that a 2,000 acre corn/soy operation would see total savings of about ${usd0(Math.round(d.farm_cornsoy.savings / 10) * 10)}.`)]),
  caption("Table 2. ", "Estimated savings by crop, Sept. 29–Nov. 30, 2026"),
  t2,
  note("Assumes every eligible truck gallon switches to dyed diesel. Excludes wheat and other small grains (mostly hauled before Sept. 29 or after Nov. 30), sugarbeets, potatoes and other crops, trips from field to on-farm bins, livestock and fertilizer hauling, and pickups."),
  p(t(`Overall, the executive order should generate savings for North Dakota farms, although the magnitude of these savings will be quite small relative to the substantial increase in diesel expenditures due to high prices. With diesel up about $2.79 per gallon since last fall, the same 2,000 acre corn/soy operation's harvest diesel bill, including combines and grain carts, is up roughly ${usd0(Math.round(d.farm_cornsoy.fall_diesel_increase / 1000) * 1000)}.`)),
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [{ id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: FONT, color: FILL }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 1 } }] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children: body }],
});
Packer.toBuffer(doc).then((buf) => { const out = path.join(ROOT, "diesel_relief_article.docx"); fs.writeFileSync(out, buf); console.log("wrote", out); });
