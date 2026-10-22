// Render outputs/simple_estimate.json to simple_estimate.docx.
// Run: python analysis/simple_estimate.py && node analysis/make_simple_docx.js   (needs `npm install docx`)
const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, HeadingLevel,
  AlignmentType, BorderStyle, LevelFormat } = require("docx");

const ROOT = path.resolve(__dirname, "..");
const d = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs", "simple_estimate.json"), "utf8"));
const FONT = "Calibri", W = 9360, FILL = "1C5CAB", LIGHT = "E8F0FB";
const b = { style: BorderStyle.SINGLE, size: 4, color: "C3C2B7" };
const borders = { top: b, bottom: b, left: b, right: b };
const t = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, italics: o.italics, color: o.color });
const p = (runs, after = 120) => new Paragraph({ children: [].concat(runs), spacing: { after } });
const cell = (text, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA }, borders, margins: { top: 60, bottom: 60, left: 90, right: 90 },
  shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
  children: [new Paragraph({ alignment: o.align, children: [t(text, { size: 18, bold: o.bold, color: o.color })] })],
});
const table = (cols, header, rows, rightFrom = 1) => new Table({
  width: { size: W, type: WidthType.DXA }, columnWidths: cols,
  rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, cols[i], { fill: FILL, color: "FFFFFF", bold: true, align: i >= rightFrom ? AlignmentType.RIGHT : undefined })) })]
    .concat(rows.map((r, k) => new TableRow({ children: r.map((v, i) => cell(v, cols[i], {
      align: i >= rightFrom ? AlignmentType.RIGHT : undefined, bold: k === rows.length - 1 && r[0] === "Total", fill: r[0] === "Total" ? LIGHT : undefined })) }))),
});
const H = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: FONT })], spacing: { before: 240, after: 100 } });
const bullet = (text) => new Paragraph({ numbering: { reference: "b", level: 0 }, children: [t(text)], spacing: { after: 60 } });

const R = Object.fromEntries(d.rows.map((r) => [r.crop, r]));
const M = (x, k = 2) => (x / 1e6).toFixed(k) + "M";
const pct = (x) => (100 * x).toFixed(0) + "%";
const pct1 = (x) => (100 * x).toFixed(1) + "%";
const cap = (s) => s[0].toUpperCase() + s.slice(1);

const params = [
  ["1. 2026 production", `Corn ${R.corn.production_mbu.toFixed(1)}M bu; soybeans ${R.soybeans.production_mbu.toFixed(1)}M bu; spring wheat + durum ${R.wheat.production_mbu.toFixed(1)}M bu`, d.sources.P1],
  ["2. Share hauled off-farm in the window", `Corn ${pct(R.corn.share)}; soybeans ${pct(R.soybeans.share)}; wheat ${pct(R.wheat.share)}`,
    "Corn and soybeans: 1 − Dec. 1 on-farm stocks ÷ production. Wheat: Sept. 1–Dec. 1 drop in on-farm stocks ÷ production × 63/91 days. 2024–25 average. " + d.sources.P2],
  ["3. One-way haul distance", `Corn and soybeans ${R.corn.oneway_miles} mi; wheat ${R.wheat.oneway_miles} mi`, d.sources.P3],
  ["4. Tons per truckload", `Corn ${R.corn.tons_per_load.toFixed(1)}; soybeans ${R.soybeans.tons_per_load.toFixed(1)}; wheat ${R.wheat.tons_per_load.toFixed(1)}`, d.sources.P4],
  ["5. Truck fuel economy", `${d.mpg} mpg (loaded and empty miles)`, d.sources.P5],
];
const calcRows = d.rows.map((r) => [cap(r.crop), (r.tons / 1e6).toFixed(2), pct(r.share), (r.hauled_tons / 1e6).toFixed(2),
  r.gal_per_ton.toFixed(3), M(r.gallons), "$" + (r.savings / 1e3).toFixed(0) + "K"]);
calcRows.push(["Total", "", "", (d.rows.reduce((s, r) => s + r.hauled_tons, 0) / 1e6).toFixed(2), "", M(d.total_gallons), "$" + (d.total_savings / 1e6).toFixed(2) + "M"]);

function shareTable() {
  const cols = [1300, 900, 1500, 2300, 1560, 1800];
  const head = ["Crop", "Year", "Production", "On-farm stocks", "Left the farm", "Share used"];
  const rows = d.share_detail.map((r) => {
    if (r.year === "Average") return [cap(r.crop) + " average", "2024–25", "", "", "", pct1(r.share)];
    const share = r.crop === "wheat" ? `${pct1(r.pct_raw)} × 63/91 = ${pct1(r.share)}` : pct1(r.share);
    return [cap(r.crop), String(r.year), r.production.toFixed(1), r.stocks, r.left.toFixed(1), share];
  });
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: cols,
    rows: [new TableRow({ tableHeader: true, children: head.map((h, i) => cell(h, cols[i], { fill: FILL, color: "FFFFFF", bold: true, align: i >= 2 ? AlignmentType.RIGHT : undefined })) })]
      .concat(rows.map((r) => {
        const avg = r[0].endsWith("average");
        return new TableRow({ children: r.map((v, i) => cell(v, cols[i], { align: i >= 2 ? AlignmentType.RIGHT : undefined, bold: avg, fill: avg ? LIGHT : undefined })) });
      })),
  });
}

const body = [
  new Paragraph({ children: [new TextRun({ text: "What North Dakota's Dyed-Diesel Order Saves Farmers in 2026", font: FONT, size: 32, bold: true })], spacing: { after: 60 } }),
  p(t("A five-parameter estimate · Matthew Gammans, NDSU CAPTS (draft) · October 2, 2026", { size: 18, color: "52514E" }), 200),
  p([t("Estimate: ", { bold: true }), t(`about $${(d.total_savings / 1e6).toFixed(1)} million`, { bold: true }),
    t(` in state fuel tax saved on ${(d.total_gallons / 1e6).toFixed(1)} million gallons of truck diesel, hauling corn, soybeans and wheat to market between Sept. 29 and Nov. 30, 2026. This assumes every eligible truck gallon switches to dyed fuel, so it is an upper bound.`)]),
  H("Method"),
  p([t("Policy definition: ", { bold: true }), t("19¢ saved per gallon (ND tax of 23¢ on clear diesel vs. 4¢ on dyed, NDCC 57-43.2); window Sept. 29–Nov. 30, 2026 (63 days); licensed vehicles hauling agricultural products.")]),
  p([t("Formula: ", { bold: true }), t("savings = Σ crops [ production × share hauled off-farm in window ] × (2 × one-way miles ÷ mpg ÷ tons per load) × $0.19")]),
  H("Five sourced parameters"),
  table([2300, 2700, 4360], ["Parameter", "Value", "Source"], params, 99),
  p(t("Datasets used (6): NASS Crop Production 2026; NASS Crop Production 2025 Summary; NASS Grain Stocks (2024–2026 releases); UGPTI DP-284 farm truck survey; UGPTI Infrastructure Needs 2024; ORNL Transportation Energy Data Book Ed. 40. The policy definition comes from EO 2026-08 and NDCC 57-43.2.", { size: 18, italics: true }), 120),
  H("How parameter 2 is calculated: share of grain that left the farm"),
  p(t("NASS Grain Stocks reports how much grain sits in on-farm storage on set dates. For corn and soybeans, the crop that is not in a farm bin on Dec. 1 has left the farm during harvest. Wheat is harvested in August, so its fall hauling is the drop in on-farm stocks from Sept. 1 to Dec. 1, scaled to the order's 63 of those 91 days. The 2024 and 2025 shares are averaged, because Dec. 1, 2026 stocks will not be published until January 2027.", { size: 19 }), 100),
  shareTable(),
  p(t("Million bushels. Production: NASS Crop Production 2025 Summary. Stocks: NASS Grain Stocks (Sept. and Jan. releases), North Dakota on-farm.", { size: 17, italics: true }), 160),
  H("Calculation"),
  table([1500, 1300, 1200, 1350, 1250, 1350, 1410], ["Crop", "Production (M tons)", "Share hauled", "Hauled (M tons)", "Gal per ton", "Gallons", "Savings"], calcRows),
  p(t(`Gallons per ton = 2 × miles ÷ ${d.mpg} mpg ÷ tons per load. For example, corn: 2 × ${R.corn.oneway_miles} ÷ ${d.mpg} ÷ ${R.corn.tons_per_load.toFixed(2)} = ${R.corn.gal_per_ton.toFixed(3)} gal/ton.`, { size: 18 }), 160),
  H("What it leaves out, and how much that matters"),
  bullet(`Not every truck will switch. Only 53% of heavy farm trucks fuel mainly from farm tanks (2021 VIUS). If only those switch, savings are about $${(d.if_only_onhand_trucks / 1e6).toFixed(1)} million. The governor's order covers state penalties only; until the IRS grants relief, a truck caught with dyed fuel on a public road faces a federal penalty of $1,000 or $10 a gallon, whichever is greater.`),
  bullet(`Haul distance is the main uncertainty. With the survey's shortest ND trip (21.7 mi) savings are $${(d.haul_sensitivity["21.7"] / 1e6).toFixed(1)} million; with its 41.7-mile second-choice delivery point, $${(d.haul_sensitivity["41.7"] / 1e6).toFixed(1)} million.`),
  bullet("Left out: sugarbeets, potatoes and other crops (mostly short hauls to piling sites and processors), on-farm field-to-bin trips, livestock and fertilizer hauling, and farm pickups. These would add to the total: the fuller model puts the excluded truck hauls (beets, field-to-bin, calves and fertilizer) at about 2.0 million gallons, roughly 40% more, before counting pickups."),
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: FONT, color: FILL }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 0 } }] },
  numbering: { config: [{ reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1440, right: 1440 } } }, children: body }],
});
Packer.toBuffer(doc).then((buf) => { const out = path.join(ROOT, "simple_estimate.docx"); fs.writeFileSync(out, buf); console.log("wrote", out); });
