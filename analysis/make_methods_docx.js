// Render outputs/methods_doc.json to methods_inputs_and_calculations.docx.
// Run: python analysis/methods_doc_data.py && node analysis/make_methods_docx.js   (needs `npm install docx`)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  HeadingLevel, AlignmentType, ExternalHyperlink, Footer, PageNumber, BorderStyle, LevelFormat,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const d = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs", "methods_doc.json"), "utf8"));

const FONT = "Calibri";
const W = 10800; // 8.5in - 2 x 0.85in margins, in DXA
const border = { style: BorderStyle.SINGLE, size: 4, color: "C3C2B7" };
const borders = { top: border, bottom: border, left: border, right: border };
const HEAD_FILL = "1C5CAB";
const GROUP_FILL = "E8F0FB";

const run = (text, opts = {}) => new TextRun({ text, font: FONT, size: opts.size || 20, bold: opts.bold, italics: opts.italics, color: opts.color });
const para = (children, opts = {}) => new Paragraph({ children: Array.isArray(children) ? children : [children], spacing: { after: opts.after ?? 100, before: opts.before ?? 0 }, ...opts.extra });

function cell(content, width, opts = {}) {
  const children = Array.isArray(content) ? content : [content];
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders,
    columnSpan: opts.span,
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ alignment: opts.align, children })],
  });
}

function sourceRuns(row) {
  if (!row.url) return [run(row.source, { size: 17 })];
  return [new ExternalHyperlink({ link: row.url, children: [new TextRun({ text: row.source, font: FONT, size: 17, style: "Hyperlink" })] })];
}

// ---------- inputs table ----------
const cols = [2400, 2900, 1200, 4300];
const header = new TableRow({
  tableHeader: true,
  children: ["Input", "Value used (central; low–high)", "Type", "Source / how derived"].map((h, i) =>
    cell(run(h, { bold: true, color: "FFFFFF", size: 18 }), cols[i], { fill: HEAD_FILL })),
});
const inputRows = [header];
let group = null;
for (const r of d.rows) {
  if (r.group !== group) {
    group = r.group;
    inputRows.push(new TableRow({ children: [cell(run(group, { bold: true, size: 18 }), W, { span: 4, fill: GROUP_FILL })] }));
  }
  inputRows.push(new TableRow({
    children: [
      cell(run(r.input, { size: 18 }), cols[0]),
      cell(run(r.value, { size: 18 }), cols[1]),
      cell(run(r.kind, { size: 17, italics: r.kind !== "Sourced" }), cols[2]),
      cell(sourceRuns(r), cols[3]),
    ],
  }));
}
const inputsTable = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: cols, rows: inputRows });

// ---------- summary table ----------
const scols = [3400, 1850, 1650, 1950, 1950];
const sumRows = [new TableRow({
  tableHeader: true,
  children: ["Category", "Eligible gallons", "Share switching", "Gallons switched", "State tax forgone"].map((h, i) =>
    cell(run(h, { bold: true, color: "FFFFFF", size: 18 }), scols[i], { fill: HEAD_FILL, align: i ? AlignmentType.RIGHT : undefined })),
})];
d.summary.forEach((row, k) => {
  const last = k === d.summary.length - 1;
  sumRows.push(new TableRow({ children: row.map((v, i) => cell(run(v, { size: 18, bold: last }), scols[i], { align: i ? AlignmentType.RIGHT : undefined, fill: last ? GROUP_FILL : undefined })) }));
});
const summaryTable = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: scols, rows: sumRows });

// ---------- sensitivity table ----------
const names = {
  oneway_miles_to_market: "Haul distance to market", other_ag_hauling_gal: "Calf and anhydrous hauling (fall shares)",
  payload_tons_market: "Truck payload", mpg_loaded: "Loaded fuel economy", onhand_share_trucks: "Trucks fueled from farm tanks",
  done_by_nov30_corn: "Corn harvest finished by Nov. 30", mpg_empty: "Empty fuel economy",
  offfarm_by_dec1_corn: "Share of corn off farm by Dec. 1", offfarm_by_dec1_soybeans: "Share of soybeans off farm by Dec. 1",
  oneway_miles_field_to_bin: "Field-to-bin distance", oneway_miles_beets: "Beet haul distance", border_loss_share: "Trips crossing into MN/SD",
  payload_tons_field_to_bin: "Field-to-bin load size", done_by_nov30_soybeans: "Soybean harvest finished by Nov. 30",
};
const tcols = [4800, 2000, 2000, 2000];
const sensRows = [new TableRow({
  tableHeader: true,
  children: ["Input moved (others at central)", "Gallons at low value", "Gallons at high value", "Swing, % of central"].map((h, i) =>
    cell(run(h, { bold: true, color: "FFFFFF", size: 18 }), tcols[i], { fill: HEAD_FILL, align: i ? AlignmentType.RIGHT : undefined })),
})];
for (const s of d.sens) {
  sensRows.push(new TableRow({ children: [
    cell(run(names[s.input] || s.input, { size: 18 }), tcols[0]),
    cell(run(`${s.low.toFixed(2)}M`, { size: 18 }), tcols[1], { align: AlignmentType.RIGHT }),
    cell(run(`${s.high.toFixed(2)}M`, { size: 18 }), tcols[2], { align: AlignmentType.RIGHT }),
    cell(run(`${s.swing.toFixed(0)}%`, { size: 18 }), tcols[3], { align: AlignmentType.RIGHT }),
  ] }));
}
const sensTable = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: tcols, rows: sensRows });

// ---------- body ----------
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })], spacing: { before: 280, after: 120 } });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })], spacing: { before: 200, after: 80 } });
const bullet = (t) => new Paragraph({ numbering: { reference: "bul", level: 0 }, children: [run(t)], spacing: { after: 60 } });

const body = [
  new Paragraph({ children: [new TextRun({ text: "North Dakota Dyed-Diesel Emergency Order (EO 2026-08)", font: FONT, size: 34, bold: true })], spacing: { after: 60 } }),
  new Paragraph({ children: [new TextRun({ text: "Input assumptions, sources, and calculation walk-through", font: FONT, size: 26, color: "52514E" })], spacing: { after: 60 } }),
  para(run(`Matthew Gammans, NDSU Center for Agricultural Policy and Trade Studies (draft) · ${d.date}`, { size: 18, color: "52514E" }), { after: 200 }),
  para(run("This document lists every input behind the estimate of how many gallons of on-road farm diesel switch to dyed fuel under Executive Order 2026-08 (Sept. 29–Nov. 30, 2026), and what that costs the state. It then walks through the calculation step by step. The estimate covers farm trucks only: pickups are excluded because survey data on them are too thin. It assumes every farmer with dyed fuel on hand is willing to accept the federal penalty risk. All figures come from one model run (python analysis/run_all.py) on the public data saved in the project folder.")),
  H1("1. Input assumptions and sources"),
  para([run("Type: ", { bold: true }), run("Sourced = taken directly from the cited table. Calculated = computed from sourced values as described. Bound = no published source; logical limits shown, midpoint used. Assumption = author's choice. Ranges in parentheses feed the sensitivity analysis.")]),
  inputsTable,
  H1("2. Calculation walk-through"),
];
d.steps.forEach((s, i) => {
  body.push(H2(s.title));
  s.lines.forEach((l) => body.push(bullet(l)));
  if (s.title.startsWith("Step 8")) {
    body.push(para(run("Summary by category", { bold: true }), { before: 120, after: 80 }));
    body.push(summaryTable);
  }
});
body.push(H1("3. Sensitivity"));
body.push(para(run("Gallons switched when one input moves to its low or high value with all others at central (top 10 inputs). Leaving out pickups biases the estimate down; assuming every farmer accepts the federal risk biases it up. Neither appears in this table.")));
body.push(sensTable);
body.push(H1("4. Data and code"));
[
  "data/raw/: every downloaded source file; data/SOURCES.md lists URLs, access dates, and manual steps.",
  "params.yaml: every input value with the report, table, and local file it came from.",
  "analysis/derive.py: computes each calculated input; outputs/derived_params.csv records the calculation.",
  "analysis/run_all.py: runs the model and writes outputs/results.json; this document is generated from it by analysis/methods_doc_data.py and analysis/make_methods_docx.js.",
].forEach((t) => body.push(bullet(t)));

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: FONT, color: "1C5CAB" }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 22, bold: true, font: FONT, color: "0B0B0B" }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 720, right: 720 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ font: FONT, size: 16, color: "898781", children: ["Page ", PageNumber.CURRENT] })] })] }) },
    children: body,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(ROOT, "methods_inputs_and_calculations.docx");
  fs.writeFileSync(out, buf);
  console.log("wrote", out);
});
