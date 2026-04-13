import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import * as XLSX from "xlsx";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Adds a "Counts (definitions.tex)" sheet to the Master sheet.xlsx
 * with COUNTIF/SUMPRODUCT formulas that auto-compute paper counts
 * matching the variables in definitions.tex.
 */

const SHEET_REF = "'Cleaned Master sheet'";
// Data range rows (row 2 to 1000 to be future-proof)
const R = "2:1000";

// Column references — full range like C2:C1000
function colRange(col: string): string {
  return `${SHEET_REF}!${col}2:${col}1000`;
}

const COL = {
  title: colRange("C"),
  level: colRange("F"),
  evalSetting: colRange("I"),
  dataSource: colRange("J"),
  technologies: colRange("K"),
  methods: colRange("L"),
  country: colRange("M"),
  year: colRange("N"),
  industry: colRange("O"),
  dssFocus: colRange("P"),
  jobShop: colRange("Q"),
};

// ARR is the same as COL now (both produce full range refs like F2:F1000)
const ARR = COL;

type Row = [string, string, string]; // [LaTeX variable, description, formula]

function countif(range: string, criteria: string): string {
  return `COUNTIF(${range},"${criteria}")`;
}

function countifs(...pairs: [string, string][]): string {
  const args = pairs.map(([r, c]) => `${r},"${c}"`).join(",");
  return `COUNTIFS(${args})`;
}

// For "contains" matching on comma-separated fields
function countifWild(range: string, keyword: string): string {
  return `COUNTIF(${range},"*${keyword}*")`;
}

// SUMPRODUCT for complex conditions (level=X AND field contains Y)
function sumproductLevelContains(level: string, field: string, keyword: string): string {
  return `SUMPRODUCT((${ARR.level}="${level}")*(ISNUMBER(SEARCH("${keyword}",${field}))))`;
}

function sumproductLevelEquals(level: string, field: string, value: string): string {
  return `SUMPRODUCT((${ARR.level}="${level}")*(${field}="${value}"))`;
}

function sumproductLevelContainsDSS(level: string, keyword: string): string {
  return sumproductLevelContains(level, ARR.dssFocus, keyword);
}

// For job-shop: contains X but not Y
function sumproductJobShop(includes: string[], excludes: string[]): string {
  let expr = `SUMPRODUCT((${ARR.level}="L2")`;
  for (const inc of includes) {
    expr += `*(ISNUMBER(SEARCH("${inc}",${ARR.jobShop})))`;
  }
  for (const exc of excludes) {
    expr += `*(NOT(ISNUMBER(SEARCH("${exc}",${ARR.jobShop}))))`;
  }
  expr += ")";
  return expr;
}

const sections: { header: string; rows: Row[] }[] = [
  {
    header: "Overall Counts",
    rows: [
      [
        "rawIncludedPapers",
        "Total included papers",
        `COUNTA(${COL.title})`,
      ],
      [
        "rawQueryIdentifiedPapers",
        "Query identified (manual — not in this sheet)",
        "616",
      ],
    ],
  },
  {
    header: "By Manufacturing Level",
    rows: [
      ["rawProcessPapers", "L0 — Process level", countif(COL.level, "L0")],
      ["rawLinePapers", "L1 — Line level", countif(COL.level, "L1")],
      ["rawFactoryPapers", "L2 — Factory level", countif(COL.level, "L2")],
      ["rawEnterprisePapers", "L3 — Enterprise level", countif(COL.level, "L3*")],
    ],
  },
  {
    header: "By Industry",
    rows: [
      [
        "rawNoIndustryPapers",
        'No industry specified ("Not specified" or "None")',
        `COUNTIF(${COL.industry},"Not specified")+COUNTIF(${COL.industry},"None")`,
      ],
      [
        "rawIndustryIdentifiedPapers",
        "Has an industry",
        `COUNTA(${COL.title})-COUNTIF(${COL.industry},"Not specified")-COUNTIF(${COL.industry},"None")-COUNTBLANK(${COL.industry})`,
      ],
      ["rawElectronicsPapers", "Electronics + Semiconductor", `COUNTIF(${COL.industry},"Electronics")+COUNTIF(${COL.industry},"Semiconductor")`],
      ["rawMetalAndMachiningPapers", "Metal & machining", countif(COL.industry, "Metal*")],
      ["rawAutomotivePapers", "Automotive", countif(COL.industry, "Automotive")],
      ["rawProcessIndustryPapers", "Process industry (Chemical, Food, Pharmaceutical, etc.)", `COUNTIF(${COL.industry},"Chemical")+COUNTIF(${COL.industry},"Food")+COUNTIF(${COL.industry},"Pharmaceutical")+COUNTIF(${COL.industry},"Food packaging")+COUNTIF(${COL.industry},"Paint")+COUNTIF(${COL.industry},"Ceramic tile")+COUNTIF(${COL.industry},"Oil and gas")`],
      ["rawMachineryAndEquipmentPapers", "Machinery & Equipment", `COUNTIF(${COL.industry},"Pump manufacturing")+COUNTIF(${COL.industry},"Pneumatic components")+COUNTIF(${COL.industry},"Marine engine")+COUNTIF(${COL.industry},"Power equipment")+COUNTIF(${COL.industry},"Home appliances")+COUNTIF(${COL.industry},"Air conditioner")+COUNTIF(${COL.industry},"Cylinder production")+COUNTIF(${COL.industry},"Furniture")+COUNTIF(${COL.industry},"Bicycles")`],
      ["rawAerospacePapers", "Aerospace", countif(COL.industry, "Aerospace")],
    ],
  },
  {
    header: "By DSS Focus",
    rows: [
      ["rawSchedulingPapers", "Scheduling", countif(COL.dssFocus, "scheduling")],
      ["rawlogisticsPapers", "Logistics & Supply chain", `COUNTIF(${COL.dssFocus},"Logistics")+COUNTIF(${COL.dssFocus},"Supply chain")+COUNTIF(${COL.dssFocus},"Safe materials transportation")+COUNTIF(${COL.dssFocus},"Material flow control")`],
      ["rawPlantLayoutPapers", "Plant layout & reconfiguration", `COUNTIF(${COL.dssFocus},"Plant layout")+COUNTIF(${COL.dssFocus},"Reconfigur*")+COUNTIF(${COL.dssFocus},"Combined design*")`],
      ["rawForecastingPapers", "Forecasting & prediction", `COUNTIF(${COL.dssFocus},"Demand forecasting")+COUNTIF(${COL.dssFocus},"Lead time prediction")+COUNTIF(${COL.dssFocus},"Bottleneck prediction")+COUNTIF(${COL.dssFocus},"Customization level prediction")`],
      ["rawVisAndSimPapers", "Visualization & simulation", `COUNTIF(${COL.dssFocus},"Data collection*")+COUNTIF(${COL.dssFocus},"Simulation*")+COUNTIF(${COL.dssFocus},"3D simulation")+COUNTIF(${COL.dssFocus},"Dashboard*")`],
      ["rawQualityPapers", "Quality & maintenance", `COUNTIF(${COL.dssFocus},"Predictive maintenance")+COUNTIF(${COL.dssFocus},"Product quality")+COUNTIF(${COL.dssFocus},"Fault detection")+COUNTIF(${COL.dssFocus},"Process monitoring")+COUNTIF(${COL.dssFocus},"Defect*")`],
      ["rawHumanRobotPapers", "Human-robot collaboration", countif(COL.dssFocus, "Human-robot*")],
    ],
  },
  {
    header: "By Year",
    rows: [
      ["twentyPapers", "2020 (incl. 2016-2019)", `COUNTIF(${COL.year},2020)+COUNTIF(${COL.year},2019)+COUNTIF(${COL.year},2018)+COUNTIF(${COL.year},2016)`],
      ["twentyOnePapers", "2021", countif(COL.year, "2021")],
      ["twentyTwoPapers", "2022", countif(COL.year, "2022")],
      ["twentyThreePapers", "2023", countif(COL.year, "2023")],
      ["twentyFourPapers", "2024", countif(COL.year, "2024")],
      ["twentyFivePapers", "2025", countif(COL.year, "2025")],
      ["twentySixPapers", "2026", countif(COL.year, "2026")],
    ],
  },
  {
    header: "By Country",
    rows: [
      ["chinaPapers", "China", countif(COL.country, "China")],
      ["germanyPapers", "Germany", countif(COL.country, "Germany")],
    ],
  },
  {
    header: "By Evaluation Setting",
    rows: [
      ["rawSimulationEvalPapers", "Simulation", countif(COL.evalSetting, "simulation")],
      ["rawStaticEvalPapers", "Static evaluation", countif(COL.evalSetting, "static evaluation")],
      ["rawLabEvalPapers", "Lab case study", countif(COL.evalSetting, "lab case study")],
      ["rawIndustrialEvalPapers", "Industrial case study / setting", `COUNTIF(${COL.evalSetting},"industrial*")`],
      ["rawOtherEvalPapers", "Other", countif(COL.evalSetting, "Other")],
    ],
  },
  {
    header: "By Data Source",
    rows: [
      ["rawSyntheticDataPapers", "Contains 'synthetic' (case-insensitive)", countifWild(COL.dataSource, "synthetic")],
      ["rawIndustrialDataPapers", "Contains 'industrial'", countifWild(COL.dataSource, "industrial")],
      ["rawBenchmarkDataPapers", "Contains 'benchmark'", countifWild(COL.dataSource, "benchmark")],
      ["rawLabDataPapers", "Contains 'lab'", countifWild(COL.dataSource, "lab*")],
    ],
  },
  {
    header: "Factory Level (L2) — Scheduling vs Non-scheduling",
    rows: [
      ["rawFactorySchedulingPapers", "L2 + Scheduling", sumproductLevelContainsDSS("L2", "scheduling")],
      ["rawFactoryNonSchedulingPapers", "L2 + NOT Scheduling", `COUNTIF(${COL.level},"L2")-` + sumproductLevelContainsDSS("L2", "scheduling")],
    ],
  },
  {
    header: "Factory Level (L2) — Job-shop Variants",
    rows: [
      ["rawFJSPPapers", "Flexible JSP (not dynamic, not distributed)", sumproductJobShop(["flexible", "job"], ["dynamic", "distributed", "assembly"])],
      ["rawJSPPapers", "JSP (not flexible, not dynamic, not distributed)", sumproductJobShop(["job"], ["flexible", "dynamic", "distributed", "reconfigur", "adaptive", "maintenance"])],
      ["rawDFJSPPapers", "Dynamic Flexible JSP", sumproductJobShop(["dynamic", "flexible", "job"], ["distributed"])],
      ["rawDJSPPapers", "Dynamic JSP (not flexible)", sumproductJobShop(["dynamic", "job"], ["flexible", "distributed"])],
      ["rawDistributedPapers", "Distributed variants", sumproductJobShop(["distributed"], [])],
    ],
  },
  {
    header: "Factory Level (L2) — Objectives/Metrics",
    rows: [
      ["rawFactoryMakespanPapers", "L2 + metrics contain 'makespan'", sumproductLevelContains("L2", `${SHEET_REF}!R2:R1000`, "makespan")],
      ["rawFactoryRobustnessPapers", "L2 + metrics contain 'robust' or 'stability'", `${sumproductLevelContains("L2", `${SHEET_REF}!R2:R1000`, "robust")}+${sumproductLevelContains("L2", `${SHEET_REF}!R2:R1000`, "stability")}`],
      ["rawFactoryTardinessPapers", "L2 + metrics contain 'tardiness'", sumproductLevelContains("L2", `${SHEET_REF}!R2:R1000`, "tardiness")],
      ["rawFactoryEnergyPapers", "L2 + metrics contain 'energy'", sumproductLevelContains("L2", `${SHEET_REF}!R2:R1000`, "energy")],
      ["rawFactoryUtilisationPapers", "L2 + metrics contain 'utilisation' or 'utilization'", `${sumproductLevelContains("L2", `${SHEET_REF}!R2:R1000`, "utilisation")}+${sumproductLevelContains("L2", `${SHEET_REF}!R2:R1000`, "utilization")}`],
    ],
  },
  {
    header: "Factory Level (L2) — Technologies",
    rows: [
      ["rawFactoryRLPapers", "L2 + tech contains 'RL'", sumproductLevelContains("L2", ARR.technologies, "RL")],
      ["rawFactoryDLPapers", "L2 + tech contains 'DL'", sumproductLevelContains("L2", ARR.technologies, "DL")],
      ["rawFactoryMLPapers", "L2 + tech contains 'ML'", sumproductLevelContains("L2", ARR.technologies, "ML")],
      ["rawFactoryAIPapers", "L2 + tech contains 'AI'", sumproductLevelContains("L2", ARR.technologies, "AI")],
      ["rawFactoryCPSPapers", "L2 + tech contains 'CPS'", sumproductLevelContains("L2", ARR.technologies, "CPS")],
      ["rawFactoryIoTPapers", "L2 + tech contains 'IoT'", sumproductLevelContains("L2", ARR.technologies, "IoT")],
      ["rawFactoryDTPapers", "L2 + tech contains 'DT'", sumproductLevelContains("L2", ARR.technologies, "DT")],
      ["rawFactoryAGVPapers", "L2 + tech contains 'AGV'", sumproductLevelContains("L2", ARR.technologies, "AGV")],
    ],
  },
  {
    header: "Factory Level (L2) — Methods",
    rows: [
      ["rawFactoryPPOPapers", "L2 + methods contain 'PPO'", sumproductLevelContains("L2", ARR.methods, "PPO")],
      ["rawFactoryDQNPapers", "L2 + methods contain 'DQN'", sumproductLevelContains("L2", ARR.methods, "DQN")],
      ["rawFactoryGNNPapers", "L2 + methods contain 'GNN'", sumproductLevelContains("L2", ARR.methods, "GNN")],
      ["rawFactoryMARLPapers", "L2 + methods contain 'MARL'", sumproductLevelContains("L2", ARR.methods, "MARL")],
      ["rawFactoryGAPapers", "L2 + methods contain 'Genetic algorithm'", sumproductLevelContains("L2", ARR.methods, "Genetic algorithm")],
    ],
  },
  {
    header: "Factory Level (L2) — Evaluation Setting",
    rows: [
      ["rawFactorySimulationEval", "L2 + simulation", sumproductLevelEquals("L2", ARR.evalSetting, "simulation")],
      ["rawFactoryStaticEval", "L2 + static evaluation", sumproductLevelEquals("L2", ARR.evalSetting, "static evaluation")],
      ["rawFactoryLabEval", "L2 + lab case study", sumproductLevelEquals("L2", ARR.evalSetting, "lab case study")],
      ["rawFactoryIndustrialEval", "L2 + industrial", `SUMPRODUCT((${ARR.level}="L2")*(ISNUMBER(SEARCH("industrial",${ARR.evalSetting}))))`],
    ],
  },
];

function main() {
  const xlsxPath = resolve(__dirname, "../Master sheet.xlsx");
  const buf = readFileSync(xlsxPath);
  const workbook = XLSX.read(buf);

  const sheetName = "Counts (definitions.tex)";

  // Remove existing sheet if present
  const idx = workbook.SheetNames.indexOf(sheetName);
  if (idx !== -1) {
    workbook.SheetNames.splice(idx, 1);
    delete workbook.Sheets[sheetName];
  }

  // Build sheet data: collect text rows and formula overrides separately
  const textRows: (string | number | null)[][] = [];
  const formulaCells: { r: number; f: string }[] = [];

  // Title row
  textRows.push(["LaTeX variable", "Description", "Formula result"]);

  for (const section of sections) {
    textRows.push([]);
    textRows.push([section.header, null, null]);
    for (const [varName, desc, formula] of section.rows) {
      const rowIdx = textRows.length;
      if (/^\d+$/.test(formula)) {
        textRows.push([varName, desc, parseInt(formula)]);
      } else {
        textRows.push([varName, desc, null]);
        formulaCells.push({ r: rowIdx, f: formula });
      }
    }
  }

  // Create worksheet from text/number data first
  const ws = XLSX.utils.aoa_to_sheet(textRows);

  // Now overlay formula cells onto column C
  for (const { r, f } of formulaCells) {
    const cellRef = XLSX.utils.encode_cell({ r, c: 2 });
    ws[cellRef] = { t: "n", v: 0, f };
  }

  // Set column widths
  ws["!cols"] = [
    { wch: 35 }, // LaTeX variable
    { wch: 55 }, // Description
    { wch: 18 }, // Formula result
  ];

  // Add the sheet to the workbook
  XLSX.utils.book_append_sheet(workbook, ws, sheetName);

  // Write back
  XLSX.writeFile(workbook, xlsxPath);
  console.log(`Added sheet "${sheetName}" to ${xlsxPath}`);
  console.log(`Total rows: ${textRows.length}, formulas: ${formulaCells.length}`);
}

main();
