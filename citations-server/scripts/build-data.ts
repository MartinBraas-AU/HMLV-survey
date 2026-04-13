import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import * as XLSX from "xlsx";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface Paper {
  id: number;
  title: string;
  year: number;
  doi: string;
  bibtexKey: string;
  manufacturingLevel: string;
  dssFocus: string;
  jobShopVariation: string | null;
  technologies: string[];
  methods: string[];
  evaluationSetting: string;
  dataSource: string;
  country: string;
  industry: string;
  metrics: string;
  snowball: boolean;
}

function titleCase(s: string): string {
  return s
    .trim()
    .split(/\s+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

function normalizeDSSFocus(raw: string | undefined): string {
  if (!raw) return "Unknown";
  const trimmed = raw.trim();
  // Normalize known case variations
  const lower = trimmed.toLowerCase();
  const mapping: Record<string, string> = {
    scheduling: "Scheduling",
    logistics: "Logistics",
    "plant layout": "Plant Layout",
    "human-robot collaboration": "Human-Robot Collaboration",
    "demand forecasting": "Demand Forecasting",
    "data collection and visualization": "Data Collection and Visualization",
    "simulation generation": "Simulation Generation",
    "predictive maintenance": "Predictive Maintenance",
    "lead time prediction": "Lead Time Prediction",
    "supply chain": "Supply Chain",
    "production optimization": "Production Optimization",
    "production planning": "Production Planning",
    "operator allocation": "Operator Allocation",
    "assembly planning": "Assembly Planning",
    "bottleneck prediction": "Bottleneck Prediction",
    "process monitoring": "Process Monitoring",
    "fault detection": "Fault Detection",
    "product quality": "Product Quality",
    "power consumption": "Power Consumption",
    "material flow control": "Material Flow Control",
  };
  return mapping[lower] ?? titleCase(trimmed);
}

function normalizeJobShop(raw: string | undefined): string | null {
  if (!raw) return null;
  const trimmed = raw.trim();
  const lower = trimmed.toLowerCase();

  if (lower === "no" || lower === "yes" || lower === "") return null;

  // Normalize known variations to consistent names
  if (lower.includes("dynamic") && lower.includes("flexible") && lower.includes("job")) {
    return "Dynamic Flexible Job-Shop Scheduling";
  }
  if (lower.includes("dynamic") && lower.includes("distributed")) {
    return "Dynamic Distributed Job-Shop Scheduling";
  }
  if (lower.includes("distributed") && lower.includes("flexible")) {
    return "Distributed Flexible Job-Shop Scheduling";
  }
  if (lower.includes("distributed") && lower.includes("job")) {
    return "Distributed Job-Shop Scheduling";
  }
  if (lower.includes("dynamic") && lower.includes("flexible") && lower.includes("flow")) {
    return "Dynamic Flexible Flow-Shop Scheduling";
  }
  if (lower.includes("dynamic") && lower.includes("job")) {
    return "Dynamic Job-Shop Scheduling";
  }
  if (lower.includes("flexible") && lower.includes("assembly")) {
    return "Flexible Assembly Job-Shop Scheduling";
  }
  if (lower.includes("flexible") && lower.includes("job")) {
    return "Flexible Job-Shop Scheduling";
  }
  if (lower.includes("reconfigurable")) {
    return "Reconfigurable Job-Shop Scheduling";
  }
  if (lower.includes("adaptive")) {
    return "Adaptive Job-Shop Scheduling";
  }
  if (lower.includes("maintenance") && lower.includes("job")) {
    return "Maintenance-Integrated Job-Shop Scheduling";
  }
  if (lower.includes("job") && (lower.includes("ssp") || lower.includes("scheduling"))) {
    return "Job-Shop Scheduling";
  }

  // Return as-is with title case if we don't recognize it
  return titleCase(trimmed);
}

function splitList(raw: string | undefined): string[] {
  if (!raw) return [];
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function normalizeLevel(raw: string | undefined): string {
  if (!raw) return "Unknown";
  const trimmed = raw.trim();
  // Already in good shape: L0, L1, L2, L3, L3/L4, L4
  return trimmed;
}

function main() {
  const xlsxPath = resolve(__dirname, "../data/Master sheet.xlsx");
  const buf = readFileSync(xlsxPath);
  const workbook = XLSX.read(buf);
  const sheet = workbook.Sheets["Cleaned Master sheet"];

  if (!sheet) {
    console.error("Sheet 'Cleaned Master sheet' not found!");
    process.exit(1);
  }

  const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet);

  const papers: Paper[] = [];
  let id = 0;

  for (const row of rows) {
    const title = row["Title"] as string | undefined;
    if (!title || !title.trim()) continue;

    const doi = (row["DOI"] as string) ?? "";
    const bibtexKey = (row["Bibtex ref"] as string) ?? "";
    const yearRaw = row["Date"];
    const year = typeof yearRaw === "number" ? yearRaw : parseInt(String(yearRaw), 10) || 0;

    papers.push({
      id: id++,
      title: title.trim(),
      year,
      doi: doi.trim(),
      bibtexKey: bibtexKey.trim(),
      manufacturingLevel: normalizeLevel(
        row["Manufacturing level (L0,L1,L2,L3/L4)"] as string
      ),
      dssFocus: normalizeDSSFocus(row["DSS focus"] as string),
      jobShopVariation: normalizeJobShop(row["Job-shop variations"] as string),
      technologies: splitList(row["Technologies"] as string),
      methods: splitList(row["Methods"] as string),
      evaluationSetting: ((row["Evaluation setting"] as string) ?? "").trim(),
      dataSource: ((row["Data Source"] as string) ?? "").trim(),
      country: ((row["Country"] as string) ?? "").trim(),
      industry: ((row["Industry"] as string) ?? "").trim(),
      metrics: ((row["Metrics "] as string) ?? "").trim(),
      snowball: String(row["Snowball (Yes/No)"] ?? "")
        .toLowerCase()
        .startsWith("yes"),
    });
  }

  const outPath = resolve(__dirname, "../src/data/papers.json");
  writeFileSync(outPath, JSON.stringify(papers, null, 2));
  console.log(`Wrote ${papers.length} papers to ${outPath}`);
}

main();
