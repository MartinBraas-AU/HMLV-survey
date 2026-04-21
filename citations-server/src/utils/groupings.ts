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

export function normalizeDataSource(val: string): string {
  const v = val.toLowerCase().trim();
  if (v.includes("industrial") && v.includes("synthetic")) return "Industrial + synthetic";
  if (v.includes("industrial") && v.includes("benchmark")) return "Industrial + benchmark";
  if (v.includes("lab") && (v.includes("synthetic") || v.includes("industrial"))) return "Lab + other";
  if (v.includes("synthetic") && v.includes("benchmark")) return "Synthetic + benchmark";
  if (v.includes("benchmark")) return "Benchmark";
  if (v.includes("industrial")) return "Industrial";
  if (v.includes("synthetic") || v.includes("synthic")) return "Synthetic";
  if (v.includes("lab")) return "Lab";
  return "Other";
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
