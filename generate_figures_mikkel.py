"""
Figure generation script for systematic literature review on
Decision Support Systems in High-Mix Low-Volume Manufacturing.

Usage:
    python generate_figures.py [path_to_excel] [output_dir]

Defaults:
    - Excel: Master_sheet_cleaned.xlsx (current directory)
    - Output: ./figures/

All normalization mappings are defined in this file so the process
is repeatable when the spreadsheet is updated.
"""

import sys
import os
import re
import textwrap
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

# ================================================================
# CONFIG
# ================================================================
EXCEL_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/Master sheet.xlsx"
OUTPUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("figures")
SHEET_NAME = "Cleaned Master sheet"
DPI = 300
FIG_FORMAT = "pdf"  # Change to "png" if needed

# Publication-friendly style
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": DPI,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Color palette — colorblind-friendly, works in B&W
COLORS = {
    "primary": "#2C3E50",
    "secondary": "#E74C3C",
    "tertiary": "#3498DB",
    "quaternary": "#208346",
    "quinary": "#F39C12",
    "light_gray": "#BDC3C7",
    "dark_gray": "#7F8C8D",
    "black": "#000000",
}
PALETTE = ["#2C3E50", "#E74C3C", "#3498DB", "#208346", "#F39C12",
           "#9B59B6", "#1ABC9C", "#E67E22", "#34495E", "#E91E63"]


# ================================================================
# NORMALIZATION MAPPINGS
# ================================================================
# These handle any remaining inconsistencies or values added after
# the initial cleanup. Add new entries here when the sheet changes.

COUNTRY_MAP = {
    "CN": "China", "DE": "Germany", "NL": "Netherlands", "KR": "South Korea",
    "IT": "Italy", "FR": "France", "EG": "Egypt", "PT": "Portugal",
    "HU": "Hungary", "CO": "Colombia", "AUS": "Australia", "UK": "United Kingdom",
    "china": "China", "italy": "Italy", "South korea": "South Korea",
    "Korea": "South Korea", "singapore": "Singapore", "Singapore.": "Singapore",
    "Germany/Sweden": "Germany", "China, Germany": "China",
}

DSS_FOCUS_MAP = {
    "scheduling": "Scheduling", "sceduling": "Scheduling", "Scheduling": "Scheduling",
    "scheduling ": "Scheduling",
    "Scheduling with minimization of tardiness.": "Scheduling",
    "Sustainability through scheduling": "Scheduling",
    "scheduling and reconfiguration": "Scheduling",
    "demand forecasting": "Demand forecasting", "Demand forecasting": "Demand forecasting",
    "Demand forecast": "Demand forecasting",
    "demand forecasting, strategic planning": "Demand forecasting",
    "plant layout": "Plant layout", "production layout": "Plant layout",
    "production layout optimization": "Plant layout",
    "human robot collaboration": "Human-robot collaboration",
    "Human robot collaboration": "Human-robot collaboration",
    "predictive maintainence": "Predictive maintenance",
    "simulation gnereation": "Simulation generation",
    "simulation model generation": "Simulation generation",
    "product family modulaization": "Product family modularization",
    "process parameters reccomendation": "Process parameter recommendation",
    "combined desing and production optimization": "Combined design and production optimization",
    "Costumization level prediction": "Customization level prediction",
    "Risk supplier assement": "Risk supplier assessment",
    "logistics": "Logistics", "lead time prediction": "Lead time prediction",
    "data collection and visualization": "Data collection and visualization",
    "supply-chain": "Supply chain",
    "safe materials transportation": "Safe materials transportation",
    "machine configurations": "Machine configurations",
    "interoperability": "Interoperability", "power consumption": "Power consumption",
    "product quality": "Product quality", "material flow control": "Material flow control",
    "reconfigurability": "Reconfigurability",
    "multi agent systems": "Multi-agent systems",
    "systems integration": "Systems integration",
    "energy cost optimization": "Energy cost optimization",
    "operator allocation": "Operator allocation",
    "dashboard perspectives": "Dashboard perspectives",
    "reconfiguration management": "Reconfiguration management",
    "production optimization": "Production optimization",
    "3d simulation": "3D simulation", "assembly planning": "Assembly planning",
    "bottleneck prediction": "Bottleneck prediction",
    "network topology": "Network topology",
    "Fault detection": "Fault detection",
}

INDUSTRY_MAP = {
    "None": "Not specified", "Nonr": "Not specified", "Unknown": "Not specified",
    "Customised and personalized manufacturing": "Not specified",
    "Automotive": "Automotive", "Automotive industry": "Automotive", "Automotive ": "Automotive",
    "Semiconductor": "Semiconductor", "Semi-conductor": "Semiconductor",
    "Semi-condutor": "Semiconductor", "Semiconductor Manufacturing": "Semiconductor",
    "Electronics": "Electronics", "OLED display": "Electronics",
    "PCB assembly": "Electronics", "Microwave components": "Electronics",
    "3D printer assembly": "Electronics", "None (electronics)": "Electronics",
    "Aerospace": "Aerospace", "Avionics": "Aerospace", "None (aerospace)": "Aerospace",
    "Metal components": "Metal & machining", "Mechanical Components": "Metal & machining",
    "Sheet metal": "Metal & machining", "Stainless steel": "Metal & machining",
    "Aluminium components": "Metal & machining", "Mold fabrication": "Metal & machining",
    "Turbomachinery components": "Metal & machining", "Extrusion": "Metal & machining",
    "Chemical": "Chemical", "Nuclear": "Nuclear", "Paint": "Paint",
    "Precast concrete": "Precast concrete",
    "Cylinders": "Cylinder production", "Cylinder production": "Cylinder production",
    "Marine engine": "Marine engine",
    "Food": "Food", "Food production": "Food",
    "Candy wrapping": "Food packaging", "Packaging": "Packaging",
    "Pharmaseutical": "Pharmaceutical",
    "Furniture": "Furniture", "bicycles": "Bicycles", "Ceramic tile": "Ceramic tile",
    "Appliances": "Home appliances", "Home appliance": "Home appliances",
    "Pneumatic components": "Pneumatic components",
    "Pump": "Pump manufacturing", "power equibment": "Power equipment",
    "Laboratory": "Laboratory",
}

MFG_LEVEL_MAP = {
    "L3/L4": "L3/L4",
}

EVAL_SETTING_MAP = {
    "static evaluation": "Static evaluation",
    "simulation": "Simulation evaluation",
    "lab case study": "Laboratory evaluation",
    "Lab case study": "Laboratory evaluation",
    "Industrial case study": "Industrial evaluation",
    "industrial case study": "Industrial evaluation",
    "industrial setting": "Industrial evaluation",
    "Other": "Other",
    "None": "Other",
}

SNOWBALL_MAP = {
    "No": "No", "no": "No", "No--": "No",
    "Yes": "Yes", "yes": "Yes",
}

# Technology normalization: split comma-separated, normalize each token
TECH_NORMALIZE = {
    # Core AI/ML
    "rl": "RL", "RL": "RL", "drl": "RL", "DRL": "RL",
    "dl": "DL", "DL": "DL",
    "ml": "ML", "ML": "ML",
    "ai": "AI", "AI": "AI", "Artificial intelligence": "AI", "artificial intelligence": "AI",
    "llm": "LLM", "LLM": "LLM",
    "gnn": "GNN", "GNN": "GNN",
    "ga": "GA", "GA": "GA",
    # Manufacturing systems
    "cps": "CPS", "CPS": "CPS",
    "cyber-physical production systems": "CPS", "CPPS": "CPS",
    "iot": "IoT", "IoT": "IoT", "IIoT": "IoT", "iiot": "IoT", "ioT": "IoT",
    "dt": "Digital Twin", "DT": "Digital Twin", "Digital Twin": "Digital Twin",
    "digital twin": "Digital Twin", "digital twins": "Digital Twin",
    "mas": "MAS", "MAS": "MAS", "multi-agent systems": "MAS", "Multi-agent systems": "MAS",
    "mes": "MES", "MES": "MES",
    "des": "DES", "DES": "DES",
    "fms": "FMS", "FMS": "FMS",
    "rms": "RMS", "RMS": "RMS",
    "erp": "ERP", "ERP": "ERP",
    "agv": "AGV", "agvs": "AGV", "AGV": "AGV", "AGVs": "AGV", "AGVS": "AGV",
    # Methods
    "metaheuristics": "Metaheuristics", "Metaheuristics": "Metaheuristics",
    "heuristics": "Heuristics", "Heuristics": "Heuristics",
    "heuristic": "Heuristics", "Heuristic": "Heuristics",
    "data-driven": "Data-driven", "Data-driven": "Data-driven",
    "data driven": "Data-driven",
    "ontology": "Ontology", "Ontology": "Ontology",
    "MILP": "MILP", "milp": "MILP",
    # Robotics
    "robotics": "Robotics", "robot": "Robotics", "Robotics": "Robotics",
    "hrc": "HRC", "HRC": "HRC", "human-robot collaboration": "HRC",
    # Analytics
    "analytics": "Analytics", "Analytics": "Analytics",
    "predictive maintenance": "Predictive maintenance",
    "Predictive maintenance": "Predictive maintenance",
}

# Job-shop variant normalization
JOBSHOP_MAP = {
    "No": "No", "no": "No", "Yes": "Other",
    "flexible Job Shop Scheduling": "FJSP",
    "Flexible Job Shop Scheduling": "FJSP",
    "Flexible Job SSP": "FJSP",
    "Dynamic flexible job shop scheduling": "DFJSP",
    "Dynamic flexible flow shop": "DFJSP",
    "Dynamic Job Shop Scheduling": "DJSP",
    "Dynamic job Shop Scheduling": "DJSP",
    "job shop Scheduling": "JSP",
    "Job SSP": "JSP",
    "Job Shop Scheduling": "JSP",
    "Job shop Scheduling": "JSP",
    "distributed job shop scheduling": "Distributed JSP",
    "Dynamic Distributed Job Shop Scheduling": "Distributed JSP",
    "Distributed dynamic flow shop scheduling": "Distributed JSP",
    "flow shop scheduling": "Flow shop",
    "Dynamic Flow Shop Scheduling": "Flow shop",
    "Reconfigurable Job Shop Scheduling": "Other",
    "Open Shop Scheduling": "Other",
    "Hybrid Flow Shop Scheduling": "Other",
    "Hybrid flow shop": "Other",
}

# Manufacturing level normalization
def normalize_manufacturing_level(val):
    if val is None or pd.isna(val):
        return None

    v = str(val).lower().strip()

    # "L0", "L1", "L2", "L3", "L3/L4", "L4" -> "L0", "L1", "L2", "L3"
    if re.search(r"\bL0\b", v):
        return "L0"
    if re.search(r"\bL1\b", v):
        return "L1"
    if re.search(r"\bL2\b", v):
        return "L2"
    if re.search(r"\bL3\b", v) or re.search(r"\bL4\b", v) or re.search(r"\bL3/L4\b", v):
        return "L3"

    return "Unspecified"

# Data source normalization
def normalize_data_source(val):
    if val is None or pd.isna(val):
        return None

    v = str(val).lower().strip()

    # Extract all mentioned sources and combine instead of collapsing to a single bucket.
    # Word-boundary matching avoids false positives like "collaboration" -> "lab".
    labels = []
    if re.search(r"\bindustrial\b", v):
        labels.append("Industrial")
    if re.search(r"\bbenchmarks?\b", v):
        labels.append("Benchmark")
    if re.search(r"\bsynthetic\b", v):
        labels.append("Synthetic")
    if re.search(r"\blab\b", v):
        labels.append("Lab")

    if labels:
        return " + ".join(labels)

    if re.search(r"\bsurvey\b", v) or re.search(r"\bliterature\b", v):
        return "Literature/survey"

    return "Other"


def count_data_source_keywords(df, source_col="Data Source"):
    """Count row-level occurrences of predefined data-source categories.

    A single row can contribute to multiple categories (e.g., "industrial benchmark"),
    so the sum of counts can exceed the number of rows.

    `Other` is defined as rows that match none of the predefined categories.
    Returns a `pd.Series` with keys: Industrial, Benchmark, Synthetic, Lab,
    Literature/survey, Other.
    """
    if source_col not in df.columns:
        raise KeyError(f"Column '{source_col}' not found in dataframe")

    s = df[source_col].astype("string")

    patterns = {
        "Industrial": r"\bindustrial\b",
        "Benchmark": r"\bbenchmarks?\b",
        "Synthetic": r"\bsynthetic\b|\bsynthic\b",
        "Lab": r"\blab\b|\blaboratory\b",
    }

    masks = {
        label: s.str.contains(pattern, case=False, regex=True, na=False)
        for label, pattern in patterns.items()
    }

    counts = {label: int(mask.sum()) for label, mask in masks.items()}
    any_match = pd.concat(masks.values(), axis=1).any(axis=1)
    if int((~any_match).sum()) > 0:
        counts["Other"] = int((~any_match).sum())
    # Print Other strings for debugging
    other_strings = s[~any_match].unique()
    print(f"Other data source strings ({len(other_strings)} unique): {other_strings}")
    return pd.Series(counts).sort_values(ascending=False)


# ================================================================
# DATA LOADING & CLEANING
# ================================================================
def load_data(path=EXCEL_PATH, sheet=SHEET_NAME):
    df = pd.read_excel(path, sheet_name=sheet)

    # Drop rows with no key_id
    df = df.dropna(subset=["key_id"]).copy()

    # Apply mappings
    df["Country"] = df["Country"].map(lambda x: COUNTRY_MAP.get(x, x) if pd.notna(x) else x)
    df["DSS focus"] = df["DSS focus"].map(lambda x: DSS_FOCUS_MAP.get(x, x) if pd.notna(x) else x)
    df["Industry"] = df["Industry"].map(lambda x: INDUSTRY_MAP.get(x, x) if pd.notna(x) else x)
    df["Snowball (Yes/No)"] = df["Snowball (Yes/No)"].map(lambda x: SNOWBALL_MAP.get(x, x) if pd.notna(x) else x)
    df["Evaluation setting"] = df["Evaluation setting"].map(lambda x: EVAL_SETTING_MAP.get(x, x) if pd.notna(x) else x)
    df["Manufacturing level (L0,L1,L2,L3/L4)"] = df["Manufacturing level (L0,L1,L2,L3/L4)"].map(
        lambda x: MFG_LEVEL_MAP.get(x, x) if pd.notna(x) else x)

    # Normalize date to int
    df["Year"] = pd.to_numeric(df["Date"], errors="coerce").astype("Int64")

    # Normalize data source
    df["Data Source (clean)"] = df["Data Source"].apply(normalize_data_source)

    # Normalize job-shop
    df["Job-shop (clean)"] = df["Job-shop variations"].map(
        lambda x: JOBSHOP_MAP.get(x, "Other") if pd.notna(x) else x)

    print(f"Loaded {len(df)} papers from '{sheet}'")
    return df


def explode_technologies(df):
    """Split comma-separated Technologies into individual normalized tokens."""
    records = []
    for _, row in df.iterrows():
        if pd.isna(row["Technologies"]):
            continue
        raw = str(row["Technologies"])
        tokens = re.split(r"[,+/]", raw)
        for t in tokens:
            t = t.strip().rstrip(".")
            if not t:
                continue
            norm = TECH_NORMALIZE.get(t, TECH_NORMALIZE.get(t.upper(), t))
            # Try to categorize anything with "scenario" or "comparative" as methodology
            if "scenario" in t.lower() or "comparative" in t.lower():
                norm = "Scenario-based"
            records.append({"key_id": row["key_id"], "Year": row["Year"], "Technology": norm,
                            "Manufacturing level (L0,L1,L2,L3/L4)": row["Manufacturing level (L0,L1,L2,L3/L4)"]})
    return pd.DataFrame(records)


# ================================================================
# HELPER FUNCTIONS
# ================================================================
def save_fig(fig, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.{FIG_FORMAT}"
    fig.savefig(path, format=FIG_FORMAT)
    plt.close(fig)
    print(f"  Saved: {path}")


def bar_counts(series, ax, color=COLORS["primary"], horizontal=False, top_n=None):
    """Plot a value_counts bar chart."""
    counts = series.value_counts()
    if top_n:
        counts = counts.head(top_n)
    if horizontal:
        counts = counts.sort_values()
        counts.plot.barh(ax=ax, color=color, edgecolor="white", linewidth=0.5)
        for i, (val, cnt) in enumerate(counts.items()):
            ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)
    else:
        counts.plot.bar(ax=ax, color=color, edgecolor="white", linewidth=0.5)
        for i, (val, cnt) in enumerate(counts.items()):
            ax.text(i, cnt + 0.3, str(cnt), ha="center", fontsize=8)
    return counts


def wrap_labels(labels, width=18):
    return [textwrap.fill(str(l), width) for l in labels]


# ================================================================
# FIGURE FUNCTIONS
# ================================================================

def fig_publication_timeline_og(df):
    """Fig 1: Publication count per year."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    years = df["Year"].dropna().astype(int)
    year_range = range(years.min(), years.max() + 1)
    counts = years.value_counts().reindex(year_range, fill_value=0).sort_index()

    # Extract counts per year for manufacturing levels (L0–L3)
    level_col = "Manufacturing level (L0,L1,L2,L3/L4)"
    by_year_level = None
    if level_col in df.columns:
        tmp = df[["Year", level_col]].copy()
        tmp = tmp.dropna(subset=["Year", level_col])
        tmp["Year"] = tmp["Year"].astype(int)

        # Normalize levels for extraction: treat L3/L4 as L3
        lvl = tmp[level_col].astype(str).str.strip()
        lvl = lvl.where(lvl.isin(["L0", "L1", "L2", "L3", "L3/L4", "L4"]))
        lvl = lvl.replace({"L3/L4": "L3"})
        lvl = lvl.replace({"L4": "L3"})  # Treat L4 as L3 for this analysis
        tmp["_lvl"] = lvl

        by_year_level = (
            tmp.dropna(subset=["_lvl"])
               .groupby(["Year", "_lvl"]).size()
               .unstack(fill_value=0)
        )
        by_year_level = by_year_level.reindex(list(year_range), fill_value=0)
        by_year_level = by_year_level.reindex(columns=["L0", "L1", "L2", "L3"], fill_value=0)

        print("\nPublication timeline by manufacturing level (count):")
        print(by_year_level.to_string())

    if by_year_level is not None and not by_year_level.empty:
        x = np.arange(len(by_year_level.index), dtype=float)
        bottoms = np.zeros(len(by_year_level.index), dtype=float)
        level_order = ["L0", "L1", "L2", "L3"]
        level_colors = {
            "L0": PALETTE[0],
            "L1": PALETTE[2],
            "L2": PALETTE[3],
            "L3": PALETTE[1],
        }

        for lvl in level_order:
            vals = by_year_level[lvl].to_numpy(dtype=float)
            ax.bar(
                x,
                vals,
                bottom=bottoms,
                label=lvl,
                color=level_colors.get(lvl, COLORS["primary"]),
                edgecolor="white",
                linewidth=0.5,
            )
            bottoms += vals

        # Annotate total per year (across L0–L3)
        for xi, total in zip(x, bottoms.tolist()):
            if total > 0:
                ax.text(float(xi), total + 0.5, str(int(total)), ha="center", fontsize=9)

        ax.set_xticks(x)
        ax.set_xticklabels([str(y) for y in by_year_level.index.tolist()])
        ax.legend(title="Manufacturing level", loc="upper left", frameon=True, framealpha=0.9)
        ax.set_title("Distribution of publications by year (stacked by manufacturing level)")
    else:
        bars = ax.bar(counts.index.astype(str), counts.values,
                      color=COLORS["primary"], edgecolor="white", linewidth=0.5)
        for bar, cnt in zip(bars, counts.values):
            if cnt > 0:
                ax.text(bar.get_x() + bar.get_width()/2, cnt + 0.5,
                        str(cnt), ha="center", fontsize=9)
        ax.set_title("Distribution of publications by year")

    ax.set_xlabel("Publication year")
    ax.set_ylabel("Number of papers")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "01_publication_timeline")

def fig_publication_timeline(df):
    """Fig 1: Publication count per year (refined stacked + hatches)."""
    fig, ax = plt.subplots(figsize=(7, 3.5))

    years = df["Year"].dropna().astype(int)
    year_range = range(years.min(), years.max() + 1)

    level_col = "Manufacturing level (L0,L1,L2,L3/L4)"
    tmp = df[["Year", level_col]].dropna(subset=["Year", level_col]).copy()
    tmp["Year"] = tmp["Year"].astype(int)

    # Normalize levels
    lvl = tmp[level_col].astype(str).str.strip()
    lvl = lvl.replace({"L3/L4": "L3", "L4": "L3"})
    tmp["_lvl"] = lvl

    by_year_level = (
        tmp.groupby(["Year", "_lvl"]).size().unstack(fill_value=0)
    )

    by_year_level = by_year_level.reindex(list(year_range), fill_value=0)
    by_year_level = by_year_level.reindex(columns=["L0", "L1", "L2", "L3"], fill_value=0)

    # Drop empty years
    by_year_level = by_year_level.loc[by_year_level.sum(axis=1) > 0]

    x = np.arange(len(by_year_level.index), dtype=float)
    bottoms = np.zeros(len(by_year_level.index))

    level_colors = {
        "L0": PALETTE[0],
        "L1": PALETTE[3],
        "L2": PALETTE[4],
        "L3": PALETTE[1],
    }

    # Hatch patterns for grayscale/print robustness
    hatches = {
        "L0": "",
        "L1": "",
        "L2": "///",
        "L3": "",
    }

    with plt.rc_context({"hatch.linewidth": 0.1}):
    # draw your hatched bars here
        for lvl in ["L0", "L1", "L2", "L3"]:
            vals = by_year_level[lvl].to_numpy()
            bars = ax.bar(
                x,
                vals,
                bottom=bottoms,
                color=level_colors[lvl],
                edgecolor="white",
                linewidth=0.6,
                label=lvl
            )

            # Apply hatch pattern
            for bar in bars:
                bar.set_hatch(hatches[lvl])
                bar.set_edgecolor(COLORS["black"]) # black for hatch visibility
                bar.set_linewidth(0) 

            bottoms += vals

    # Annotate totals
    for xi, total in zip(x, bottoms):
        if total > 0:
            ax.text(float(xi), float(total) + 0.3, str(int(total)),
                    ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(by_year_level.index.astype(int))

    ax.set_title("Publications per year (stacked by manufacturing level)")
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Number of papers")

    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.set_axisbelow(True)

    ax.legend(title="Manufacturing level",
              bbox_to_anchor=(1.02, 1),
              loc="upper left",
              frameon=False)

    fig.tight_layout()
    save_fig(fig, "01_publication_timeline")


def fig_manufacturing_level(df):
    """Fig 2: Distribution across manufacturing levels."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    col = "Manufacturing level (L0,L1,L2,L3/L4)"
    order = ["L0", "L1", "L2", "L3"]

    # Normalize so we don't show L3/L4 and L4 separately; count them under L3.
    normalized = (
        df[col]
        .astype("string")
        .str.strip()
        .replace({"L3/L4": "L3", "L4": "L3"})
    )
    counts = normalized.value_counts().reindex(order).dropna()

    bars = ax.bar(counts.index, counts.values, color=PALETTE[:len(counts)],
                  edgecolor="white", linewidth=0.5)
    for bar, cnt in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, cnt + 0.5,
                str(int(cnt)), ha="center", fontsize=9)

    ax.set_xlabel("Manufacturing level")
    ax.set_ylabel("Number of papers")
    ax.set_title("Distribution of papers by manufacturing level")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "02_manufacturing_level")


def fig_country_distribution(df):
    """Fig 3: Geographic distribution of papers."""
    fig, ax = plt.subplots(figsize=(8, 5))
    counts = df["Country"].value_counts()

    # Group countries with < 2 papers as "Other"
    threshold = 2
    main = counts[counts >= threshold]
    other_count = counts[counts < threshold].sum()
    if other_count > 0:
        main["Other"] = other_count
    main = main.sort_values()

    bars = ax.barh(range(len(main)), main.values, color=COLORS["primary"],
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(main)))
    ax.set_yticklabels(main.index)
    for i, cnt in enumerate(main.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    ax.set_title("Geographic distribution of papers")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "03_country_distribution")


def fig_technology_landscape(df):
    """Fig 4: Most common technologies (exploded from comma-separated)."""
    tech_df = explode_technologies(df)
    tech_counts = tech_df["Technology"].value_counts()

    # Only show techs with >= 2 occurrences
    tech_counts = tech_counts[tech_counts >= 2]

    fig, ax = plt.subplots(figsize=(7, 5))
    tech_counts = tech_counts.sort_values()
    bars = ax.barh(range(len(tech_counts)), tech_counts.astype(float).to_numpy(),
                   color=COLORS["tertiary"], edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(tech_counts)))
    ax.set_yticklabels(tech_counts.index)
    for i, cnt in enumerate(tech_counts.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    ax.set_title("Technology adoption across studies (≥2 occurrences)")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "04_technology_landscape")


def fig_dss_focus(df):
    """Fig 5: DSS focus areas."""
    fig, ax = plt.subplots(figsize=(7, 5.5))
    counts = df["DSS focus"].value_counts()

    # Split into Scheduling (dominant) and others
    scheduling_count = counts.get("Scheduling", 0)
    others = counts.drop("Scheduling", errors="ignore")
    others = others[others >= 1].sort_values()

    # Plot all together
    all_counts = pd.concat([others, pd.Series({"Scheduling": scheduling_count})])
    all_counts = all_counts.sort_values()

    colors = [COLORS["primary"] if v != "Scheduling" else COLORS["secondary"]
              for v in all_counts.index]

    bars = ax.barh(range(len(all_counts)), all_counts.astype(float).to_numpy(), color=colors,
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(all_counts)))
    ax.set_yticklabels(wrap_labels(all_counts.index, 30), fontsize=7)
    for i, cnt in enumerate(all_counts.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=7)

    ax.set_xlabel("Number of papers")
    ax.set_title("Distribution of DSS focus areas")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "05_dss_focus")


def fig_jobshop_variants(df):
    """Fig 6: Job-shop scheduling variant breakdown."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    counts = df["Job-shop (clean)"].value_counts()
    order = ["No", "JSP", "FJSP", "DJSP", "DFJSP", "Distributed JSP", "Flow shop", "Other"]
    counts = counts.reindex(order).dropna()

    bars = ax.bar(counts.index, counts.values, color=COLORS["primary"],
                  edgecolor="white", linewidth=0.5)
    for bar, cnt in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, cnt + 0.3,
                str(int(cnt)), ha="center", fontsize=8)

    ax.set_xlabel("Job-shop variant")
    ax.set_ylabel("Number of papers")
    ax.set_title("Job-shop scheduling problem variants")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    save_fig(fig, "06_jobshop_variants")


def fig_evaluation_setting(df):
    """Fig 7: Evaluation methodology distribution."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    counts = df["Evaluation setting"].value_counts()
    counts = counts[counts >= 1]

    total = int(counts.sum())
    print("\nEvaluation setting distribution (count, %):")
    if total == 0:
        print("  (no data)")
    else:
        sorted_counts = counts.sort_values(ascending=False)
        for label, cnt in zip(sorted_counts.index.tolist(), sorted_counts.values.tolist()):
            pct = (cnt / total) * 100
            print(f"  {label}: {int(cnt)} ({pct:.1f}%)")

    bars = ax.bar(counts.index, counts.values, color=COLORS["quaternary"],
                  edgecolor="white", linewidth=0.5)
    for bar, cnt in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, cnt + 0.3,
                str(int(cnt)), ha="center", fontsize=8)

    ax.set_xlabel("Evaluation setting")
    ax.set_ylabel("Number of papers")
    ax.set_title("Evaluation methodology distribution")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    save_fig(fig, "07_evaluation_setting")


def fig_data_source(df):
    """Fig 8: Data source distribution."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    #counts = df["Data Source (clean)"].value_counts()
    counts = count_data_source_keywords(df, source_col="Data Source")

    denom = int(df["Data Source"].notna().sum())
    print("\nData source distribution (count, % of papers):")
    if denom == 0:
        print("  (no data)")
    else:
        sorted_counts = counts.sort_values(ascending=False)
        for label, cnt in zip(sorted_counts.index.tolist(), sorted_counts.values.tolist()):
            pct = (cnt / denom) * 100
            print(f"  {label}: {int(cnt)} ({pct:.1f}%)")

        if int(counts.sum()) != denom:
            print("  Note: categories can overlap, so totals may exceed 100%.")

    counts = counts.sort_values()

    bars = ax.barh(range(len(counts)), counts.values, color=COLORS["quinary"],
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index)
    for i, cnt in enumerate(counts.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    ax.set_title("Data source distribution")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "08_data_source")


def fig_snowball(df):
    """Fig 9: Snowball vs database search papers."""
    fig, ax = plt.subplots(figsize=(4, 3))
    counts = df["Snowball (Yes/No)"].value_counts()

    colors = [COLORS["primary"], COLORS["secondary"]]
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct="%1.0f%%",
        colors=colors[:len(counts)], startangle=90,
        textprops={"fontsize": 10})

    ax.set_title("Paper source: database vs. snowballing")
    fig.tight_layout()
    save_fig(fig, "09_snowball_source")


def fig_industry(df):
    """Fig 10: Industry distribution (excluding Not specified)."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    counts = df["Industry"].value_counts()
    # Remove "Not specified" for this chart
    counts = counts.drop("Not specified", errors="ignore")
    counts = counts.sort_values()

    bars = ax.barh(range(len(counts)), counts.values, color=COLORS["primary"],
                   edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index, fontsize=8)
    for i, cnt in enumerate(counts.values):
        ax.text(cnt + 0.1, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    ax.set_title("Industry application domains (excluding unspecified)")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "10_industry_distribution")


def fig_tech_by_year(df):
    """Fig 11: Technology trends over time (top technologies)."""
    tech_df = explode_technologies(df)
    top_techs = tech_df["Technology"].value_counts().head(6).index.tolist()
    subset = tech_df[tech_df["Technology"].isin(top_techs)].copy()

    pivot = subset.groupby(["Year", "Technology"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(columns=top_techs)

    fig, ax = plt.subplots(figsize=(7, 4))
    for i, tech in enumerate(top_techs):
        if tech in pivot.columns:
            ax.plot(pivot.index, pivot[tech], marker="o", markersize=4,
                    label=tech, color=PALETTE[i], linewidth=1.5)

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of papers")
    ax.set_title("Technology adoption trends over time")
    ax.legend(loc="upper left", frameon=True, framealpha=0.9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "11_tech_by_year")


def fig_tech_by_mfg_level(df):
    """Fig 12: Technology × Manufacturing level heatmap."""
    tech_df = explode_technologies(df)
    top_techs = tech_df["Technology"].value_counts().head(8).index.tolist()
    subset = tech_df[tech_df["Technology"].isin(top_techs)]

    col = "Manufacturing level (L0,L1,L2,L3/L4)"
    pivot = subset.groupby([col, "Technology"]).size().unstack(fill_value=0)
    level_order = ["L0", "L1", "L2", "L3", "L3/L4", "L4"]
    pivot = pivot.reindex([l for l in level_order if l in pivot.index])
    pivot = pivot.reindex(columns=top_techs)

    fig, ax = plt.subplots(figsize=(8, 3.5))
    im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    # Annotate cells
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if val > 0:
                color = "white" if val > pivot.values.max() * 0.6 else "black"
                ax.text(j, i, str(int(val)), ha="center", va="center",
                        fontsize=8, color=color)

    ax.set_title("Technology usage by manufacturing level")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Count")
    fig.tight_layout()
    save_fig(fig, "12_tech_by_mfg_level")


def fig_dss_by_mfg_level(df):
    """Fig 13: DSS focus × Manufacturing level heatmap."""
    col = "Manufacturing level (L0,L1,L2,L3/L4)"
    # Only use DSS focus areas with >= 2 papers
    focus_counts = df["DSS focus"].value_counts()
    top_focus = focus_counts[focus_counts >= 2].index.tolist()
    subset = df[df["DSS focus"].isin(top_focus)]

    pivot = subset.groupby([col, "DSS focus"]).size().unstack(fill_value=0)
    level_order = ["L0", "L1", "L2", "L3", "L3/L4", "L4"]
    pivot = pivot.reindex([l for l in level_order if l in pivot.index])

    fig, ax = plt.subplots(figsize=(9, 3.5))
    im = ax.imshow(pivot.values, cmap="Oranges", aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(wrap_labels(pivot.columns, 16), rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if val > 0:
                color = "white" if val > pivot.values.max() * 0.6 else "black"
                ax.text(j, i, str(int(val)), ha="center", va="center",
                        fontsize=7, color=color)

    ax.set_title("DSS focus areas by manufacturing level")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Count")
    fig.tight_layout()
    save_fig(fig, "13_dss_by_mfg_level")


# ================================================================
# MAIN
# ================================================================
def main():
    print(f"Reading: {EXCEL_PATH}")
    print(f"Output:  {OUTPUT_DIR}/")
    print()

    df = load_data()
    print(f"\nGenerating figures...\n")

    fig_publication_timeline(df)
    fig_manufacturing_level(df)
    fig_country_distribution(df)
    fig_technology_landscape(df)
    fig_dss_focus(df)
    fig_jobshop_variants(df)
    fig_evaluation_setting(df)
    fig_data_source(df)
    fig_snowball(df)
    fig_industry(df)
    fig_tech_by_year(df)
    fig_tech_by_mfg_level(df)
    fig_dss_by_mfg_level(df)

    print(f"\nDone! {len(list(OUTPUT_DIR.glob(f'*.{FIG_FORMAT}')))} figures generated.")


if __name__ == "__main__":
    main()
