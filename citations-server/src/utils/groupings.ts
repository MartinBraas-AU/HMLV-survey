import type { Paper } from "../types";

// DSS focus → grouped category (mirrors generate_figures.py DSS_FOCUS_GROUP_MAP)
const DSS_FOCUS_GROUP: Record<string, string> = {
  Scheduling: "Scheduling",
  "Production Optimization": "Scheduling",
  "Production Planning": "Scheduling",
  "Logistics": "Logistics & supply chain",
  "Supply Chain": "Logistics & supply chain",
  "Material Flow Control": "Logistics & supply chain",
  "Safe Materials Transportation": "Logistics & supply chain",
  "Manufacturing Service Selection": "Logistics & supply chain",
  "Plant Layout": "Plant layout & reconfiguration",
  Reconfigurability: "Plant layout & reconfiguration",
  "Reconfiguration Management": "Plant layout & reconfiguration",
  "Production Setup": "Plant layout & reconfiguration",
  "Assembly Planning": "Plant layout & reconfiguration",
  "Machine Configurations": "Plant layout & reconfiguration",
  "Data Collection and Visualization": "Visualization & simulation",
  "Dashboard Perspectives": "Visualization & simulation",
  "3d Simulation": "Visualization & simulation",
  "Simulation Generation": "Visualization & simulation",
  "Operator Allocation": "Visualization & simulation",
  "Predictive Maintenance": "Quality & maintenance",
  "Fault Detection": "Quality & maintenance",
  "Process Monitoring": "Quality & maintenance",
  "Defect Prevenetion": "Quality & maintenance",
  "Product Quality": "Quality & maintenance",
  "Demand Forecasting": "Forecasting & prediction",
  "Lead Time Prediction": "Forecasting & prediction",
  "Bottleneck Prediction": "Forecasting & prediction",
  "Customization Level Prediction": "Forecasting & prediction",
  "Human-Robot Collaboration": "Human-robot collaboration",
  "Combined Design And Production Optimization": "Other",
  "Product Family Modularization": "Other",
  "Process Parameter Recommendation": "Other",
  "Risk Supplier Assessment": "Other",
  "Power Consumption": "Other",
  Interoperability: "Other",
  "Multi-agent Systems": "Other",
  "Systems Integration": "Other",
};

// Industry → grouped category (mirrors generate_figures.py INDUSTRY_GROUP_MAP)
const INDUSTRY_GROUP: Record<string, string> = {
  Automotive: "Automotive",
  Aerospace: "Aerospace",
  Electronics: "Electronics & Semiconductor",
  Semiconductor: "Electronics & Semiconductor",
  "Metal & machining": "Metal & Machining",
  "Metal & Machining": "Metal & Machining",
  Food: "Process Industry",
  "Food packaging": "Process Industry",
  Chemical: "Process Industry",
  Pharmaceutical: "Process Industry",
  Paint: "Process Industry",
  "Marine engine": "Machinery & Equipment",
  "Cylinder production": "Machinery & Equipment",
  "Pump manufacturing": "Machinery & Equipment",
  "Pneumatic components": "Machinery & Equipment",
  "Power equipment": "Machinery & Equipment",
  "Home appliances": "Other",
  Furniture: "Other",
  Bicycles: "Other",
  "Ceramic tile": "Other",
  Packaging: "Other",
  "Precast concrete": "Other",
  Nuclear: "Other",
  Laboratory: "Other",
  "Not specified": "Not specified",
};

export function getDSSFocusGroup(focus: string): string {
  return DSS_FOCUS_GROUP[focus] ?? "Other";
}

export function getIndustryGroup(industry: string): string {
  return INDUSTRY_GROUP[industry] ?? "Other";
}

export function normalizeDataSource(val: string | null | undefined): string {
  if (val == null) return "Other";

  const v = String(val).toLowerCase().trim();
  const labels: string[] = [];

  if (/\bindustrial\b/i.test(v)) labels.push("Industrial");
  if (/\bbenchmarks?\b/i.test(v)) labels.push("Benchmark");
  if (/\bsynthetic\b/i.test(v)) labels.push("Synthetic");
  if (/\blab\b/i.test(v)) labels.push("Lab");

  if (labels.length > 0) {
    return labels.join(" + ");
  }

  if (/\bsurvey\b/i.test(v) || /\bliterature\b/i.test(v)) {
    return "Literature/survey";
  }

  return "Other";
}

export function countDataSourceKeywords(
  papers: Paper[],
  field: "dataSource" = "dataSource"
): { name: string; count: number }[] {
  const counts = {
    Industrial: 0,
    Benchmark: 0,
    Synthetic: 0,
    Lab: 0,
    Other: 0,
  };

  for (const paper of papers) {
    const sources = paper[field] ?? [];
    const matchesIndustrial = sources.some(src => /\bindustrial\b/i.test(src));
    const matchesBenchmark = sources.some(src => /\bbenchmarks?\b/i.test(src));
    const matchesSynthetic = sources.some(src => /\bsynthetic\b|\bsynthic\b/i.test(src));
    const matchesLab = sources.some(src => /\blab\b|\blaboratory\b/i.test(src));

    let matchedAny = false;

    if (matchesIndustrial) {
      counts.Industrial += 1;
      matchedAny = true;
    }
    if (matchesBenchmark) {
      counts.Benchmark += 1;
      matchedAny = true;
    }
    if (matchesSynthetic) {
      counts.Synthetic += 1;
      matchedAny = true;
    }
    if (matchesLab) {
      counts.Lab += 1;
      matchedAny = true;
    }

    if (!matchedAny) {
      counts.Other += 1;
    }
  }

  return Object.entries(counts)
    .filter(([, count]) => count > 0)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}

export function matchesDataSourceKeyword(src: string, label: string): boolean {
  const v = String(src ?? "").toLowerCase();

  switch (label.trim().toLowerCase()) {
    case "industrial":
      return /\bindustrial\b/i.test(v);
    case "benchmark":
      return /\bbenchmarks?\b/i.test(v);
    case "synthetic":
      return /\bsynthetic\b|\bsynthic\b/i.test(v);
    case "lab":
      return /\blab\b|\blaboratory\b/i.test(v);
    case "literature/survey":
      return /\bsurvey\b/i.test(v) || /\bliterature\b/i.test(v);
    case "other":
      return !(/\bindustrial\b|\bbenchmarks?\b|\bsynthetic\b|\bsynthic\b|\blab\b|\blaboratory\b/i.test(v));
    default:
      return false;
  }
}

// Job-shop variant normalization (mirrors generate_figures.py)
export function getJobShopVariant(variation: string | null): string {
  if (!variation) return "No";
  const v = variation.toLowerCase();
  if (v.includes("dynamic") && v.includes("flexible")) return "DFJSP";
  if (v.includes("distributed")) return "Distributed JSP";
  if (v.includes("dynamic") && v.includes("flow")) return "Flow shop";
  if (v.includes("dynamic")) return "DJSP";
  if (v.includes("flexible")) return "FJSP";
  if (v.includes("hybrid") || v.includes("reconfigurable") || v.includes("open")) return "Other";
  return "JSP";
}

// Helper: count occurrences and return sorted array
export function countBy<T>(
  items: T[],
  keyFn: (item: T) => string
): { name: string; count: number }[] {
  const map = new Map<string, number>();
  for (const item of items) {
    const k = keyFn(item);
    map.set(k, (map.get(k) ?? 0) + 1);
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}

// Count technologies/methods (multi-valued fields)
export function countMulti(
  papers: Paper[],
  field: "technologies" | "methods"
): { name: string; count: number }[] {
  const map = new Map<string, number>();
  for (const p of papers) {
    for (const v of p[field]) {
      map.set(v, (map.get(v) ?? 0) + 1);
    }
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}
