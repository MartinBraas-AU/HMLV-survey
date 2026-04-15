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
import re
import textwrap
from pathlib import Path

import pandas as pd
import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors

# ================================================================
# CONFIG
# ================================================================
EXCEL_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/Master sheet.xlsx"
OUTPUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("figures")
SHEET_NAME = "Cleaned Master sheet"
DPI = 300
FIG_FORMAT = "pdf"  # Change to "png" if needed

# Publication-friendly style
plt.rcParams.update(
    {
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
    }
)

# Color palette — colorblind-friendly, works in B&W
COLORS = {
    "primary": "#2C3E50",
    "secondary": "#E74C3C",
    "tertiary": "#3498DB",
    "quaternary": "#2ECC71",
    "quinary": "#F39C12",
    "light_gray": "#BDC3C7",
    "dark_gray": "#7F8C8D",
}
PALETTE = [
    "#2C3E50",
    "#E74C3C",
    "#3498DB",
    "#2ECC71",
    "#F39C12",
    "#9B59B6",
    "#1ABC9C",
    "#E67E22",
    "#34495E",
    "#E91E63",
]


# ================================================================
# NORMALIZATION MAPPINGS
# ================================================================
# These handle any remaining inconsistencies or values added after
# the initial cleanup. Add new entries here when the sheet changes.

COUNTRY_MAP = {
    "CN": "China",
    "DE": "Germany",
    "NL": "Netherlands",
    "KR": "South Korea",
    "IT": "Italy",
    "FR": "France",
    "EG": "Egypt",
    "PT": "Portugal",
    "HU": "Hungary",
    "CO": "Colombia",
    "AUS": "Australia",
    "UK": "United Kingdom",
    "china": "China",
    "italy": "Italy",
    "South korea": "South Korea",
    "Korea": "South Korea",
    "singapore": "Singapore",
    "Singapore.": "Singapore",
    "Germany/Sweden": "Germany",
    "China, Germany": "China",
}

DSS_FOCUS_MAP = {
    "scheduling": "Scheduling",
    "sceduling": "Scheduling",
    "Scheduling": "Scheduling",
    "scheduling ": "Scheduling",
    "Scheduling with minimization of tardiness.": "Scheduling",
    "Sustainability through scheduling": "Scheduling",
    "scheduling and reconfiguration": "Scheduling",
    "demand forecasting": "Demand forecasting",
    "Demand forecasting": "Demand forecasting",
    "Demand forecast": "Demand forecasting",
    "demand forecasting, strategic planning": "Demand forecasting",
    "plant layout": "Plant layout",
    "production layout": "Plant layout",
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
    "logistics": "Logistics",
    "lead time prediction": "Lead time prediction",
    "data collection and visualization": "Data collection and visualization",
    "supply-chain": "Supply chain",
    "safe materials transportation": "Safe materials transportation",
    "machine configurations": "Machine configurations",
    "interoperability": "Interoperability",
    "power consumption": "Power consumption",
    "product quality": "Product quality",
    "material flow control": "Material flow control",
    "reconfigurability": "Reconfigurability",
    "multi agent systems": "Multi-agent systems",
    "systems integration": "Systems integration",
    "energy cost optimization": "Energy cost optimization",
    "operator allocation": "Operator allocation",
    "dashboard perspectives": "Dashboard perspectives",
    "reconfiguration management": "Reconfiguration management",
    "production optimization": "Production optimization",
    "3d simulation": "3D simulation",
    "assembly planning": "Assembly planning",
    "bottleneck prediction": "Bottleneck prediction",
    "network topology": "Network topology",
    "Fault detection": "Fault detection",
}

INDUSTRY_MAP = {
    "None": "Not specified",
    "Nonr": "Not specified",
    "Unknown": "Not specified",
    "Customised and personalized manufacturing": "Not specified",
    "Automotive": "Automotive",
    "Automotive industry": "Automotive",
    "Automotive ": "Automotive",
    "Semiconductor": "Semiconductor",
    "Semi-conductor": "Semiconductor",
    "Semi-condutor": "Semiconductor",
    "Semiconductor Manufacturing": "Semiconductor",
    "Electronics": "Electronics",
    "OLED display": "Electronics",
    "PCB assembly": "Electronics",
    "Microwave components": "Electronics",
    "3D printer assembly": "Electronics",
    "None (electronics)": "Electronics",
    "Aerospace": "Aerospace",
    "Avionics": "Aerospace",
    "None (aerospace)": "Aerospace",
    "Metal components": "Metal & machining",
    "Mechanical Components": "Metal & machining",
    "Sheet metal": "Metal & machining",
    "Stainless steel": "Metal & machining",
    "Aluminium components": "Metal & machining",
    "Mold fabrication": "Metal & machining",
    "Turbomachinery components": "Metal & machining",
    "Extrusion": "Metal & machining",
    "Chemical": "Chemical",
    "Nuclear": "Nuclear",
    "Paint": "Paint",
    "Precast concrete": "Precast concrete",
    "Cylinders": "Cylinder production",
    "Cylinder production": "Cylinder production",
    "Marine engine": "Marine engine",
    "Food": "Food",
    "Food production": "Food",
    "Candy wrapping": "Food packaging",
    "Packaging": "Packaging",
    "Pharmaseutical": "Pharmaceutical",
    "Furniture": "Furniture",
    "bicycles": "Bicycles",
    "Ceramic tile": "Ceramic tile",
    "Appliances": "Home appliances",
    "Home appliance": "Home appliances",
    "Pneumatic components": "Pneumatic components",
    "Pump": "Pump manufacturing",
    "power equibment": "Power equipment",
    "Laboratory": "Laboratory",
    "Pressure vessels": "Metal & machining",
    "Air conditioner": "Home appliances",
}

MFG_LEVEL_MAP = {
    "L3/L4": "L3/L4",
}

# ----------------------------------------------------------------
# HIGH-LEVEL GROUPING MAPS
# Applied *after* normalization to collapse many fine-grained
# categories into broader groups suitable for figures.
# ----------------------------------------------------------------

# Industry → grouped industry  (applied to already-normalized values)
INDUSTRY_GROUP_MAP = {
    "Automotive": "Automotive",
    "Aerospace": "Aerospace",
    "Electronics": "Electronics & Semiconductor",
    "Semiconductor": "Electronics & Semiconductor",
    "Metal & machining": "Metal & Machining",
    # Process industry — chemical/physical transformation of materials
    "Food": "Process Industry",
    "Food packaging": "Process Industry",
    "Chemical": "Process Industry",
    "Pharmaceutical": "Process Industry",
    "Paint": "Process Industry",
    # Machinery & equipment — discrete manufacturing of industrial goods
    "Marine engine": "Machinery & Equipment",
    "Cylinder production": "Machinery & Equipment",
    "Pump manufacturing": "Machinery & Equipment",
    "Pneumatic components": "Machinery & Equipment",
    "Power equipment": "Machinery & Equipment",
    # Remaining — too diverse to form a coherent group
    "Home appliances": "Other",
    "Furniture": "Other",
    "Bicycles": "Other",
    "Ceramic tile": "Other",
    "Packaging": "Other",
    "Precast concrete": "Other",
    "Nuclear": "Other",
    "Laboratory": "Other",
    "Not specified": "Not specified",
}

# DSS focus → grouped DSS focus  (applied to already-normalized values)
DSS_FOCUS_GROUP_MAP = {
    # Dominant category — kept as-is
    "Scheduling": "Scheduling",
    # Logistics & supply chain
    "Logistics": "Logistics & supply chain",
    "Supply chain": "Logistics & supply chain",
    "Material flow control": "Logistics & supply chain",
    "Safe materials transportation": "Logistics & supply chain",
    # Plant layout & reconfiguration
    "Plant layout": "Plant layout & reconfiguration",
    "Reconfigurability": "Plant layout & reconfiguration",
    "Reconfiguration management": "Plant layout & reconfiguration",
    "Production setup": "Plant layout & reconfiguration",
    # Visualization & simulation
    "Data collection and visualization": "Visualization & simulation",
    "Dashboard perspectives": "Visualization & simulation",
    "3D simulation": "Visualization & simulation",
    "Simulation generation": "Visualization & simulation",
    # Quality & maintenance
    "Predictive maintenance": "Quality & maintenance",
    "Fault detection": "Quality & maintenance",
    "Process monitoring": "Quality & maintenance",
    "Defect prevenetion": "Quality & maintenance",
    "Product quality": "Quality & maintenance",
    # Forecasting & prediction
    "Demand forecasting": "Forecasting & prediction",
    "Lead time prediction": "Forecasting & prediction",
    "Bottleneck prediction": "Forecasting & prediction",
    "Customization level prediction": "Forecasting & prediction",
    # Human-robot collaboration — own group (6 papers)
    "Human-robot collaboration": "Human-robot collaboration",
    # Fits naturally into Plant layout & reconfiguration
    "Assembly planning": "Plant layout & reconfiguration",
    "Machine configurations": "Plant layout & reconfiguration",
    # Reclassified based on paper content
    "Energy cost optimization": "Scheduling",
    "Production optimization": "Scheduling",
    "Operator allocation": "Visualization & simulation",
    "Combined design and production optimization": "Other",
    # Remaining singletons → Other
    "Product family modularization": "Other",
    "Process parameter recommendation": "Other",
    "Risk supplier assessment": "Other",
    "Power consumption": "Other",
    "Interoperability": "Other",
    "Multi-agent systems": "Other",
    "Systems integration": "Other",
    "Network topology": "Other",
}

EVAL_SETTING_MAP = {
    "static evaluation": "Static evaluation",
    "simulation": "Simulation",
    "lab case study": "Lab case study",
    "instance-based": "Instance-based",
    "Industrial case study": "Industrial case study",
    "Other": "Other",
    "None": "Other",
    "?": "Other",
}

SNOWBALL_MAP = {
    "No": "No",
    "no": "No",
    "No--": "No",
    "Yes": "Yes",
    "yes": "Yes",
}

# Technology normalization: split comma-separated, normalize each token
TECH_NORMALIZE = {
    # Core AI/ML
    "rl": "RL",
    "RL": "RL",
    "drl": "RL",
    "DRL": "RL",
    "dl": "DL",
    "DL": "DL",
    "ml": "ML",
    "ML": "ML",
    "ai": "AI",
    "AI": "AI",
    "Artificial intelligence": "AI",
    "artificial intelligence": "AI",
    "llm": "LLM",
    "LLM": "LLM",
    "gnn": "GNN",
    "GNN": "GNN",
    "ga": "GA",
    "GA": "GA",
    # Manufacturing systems
    "cps": "CPS",
    "CPS": "CPS",
    "cyber-physical production systems": "CPS",
    "CPPS": "CPS",
    "iot": "IoT",
    "IoT": "IoT",
    "IIoT": "IoT",
    "iiot": "IoT",
    "ioT": "IoT",
    "dt": "Digital Twin",
    "DT": "Digital Twin",
    "Digital Twin": "Digital Twin",
    "digital twin": "Digital Twin",
    "digital twins": "Digital Twin",
    "mas": "MAS",
    "MAS": "MAS",
    "multi-agent systems": "MAS",
    "Multi-agent systems": "MAS",
    "mes": "MES",
    "MES": "MES",
    "des": "DES",
    "DES": "DES",
    "fms": "FMS",
    "FMS": "FMS",
    "rms": "RMS",
    "RMS": "RMS",
    "erp": "ERP",
    "ERP": "ERP",
    "agv": "AGV",
    "agvs": "AGV",
    "AGV": "AGV",
    "AGVs": "AGV",
    "AGVS": "AGV",
    # Methods
    "metaheuristics": "Metaheuristics",
    "Metaheuristics": "Metaheuristics",
    "heuristics": "Heuristics",
    "Heuristics": "Heuristics",
    "heuristic": "Heuristics",
    "Heuristic": "Heuristics",
    "data-driven": "Data-driven",
    "Data-driven": "Data-driven",
    "data driven": "Data-driven",
    "ontology": "Ontology",
    "Ontology": "Ontology",
    "MILP": "MILP",
    "milp": "MILP",
    # Robotics
    "robotics": "Robotics",
    "robot": "Robotics",
    "Robotics": "Robotics",
    "hrc": "HRC",
    "HRC": "HRC",
    "human-robot collaboration": "HRC",
    # Analytics
    "analytics": "Analytics",
    "Analytics": "Analytics",
    "predictive maintenance": "Predictive maintenance",
    "Predictive maintenance": "Predictive maintenance",
}

# Job-shop variant normalization
JOBSHOP_MAP = {
    "No": "No",
    "no": "No",
    "Yes": "Other",
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


# Data source normalization
def normalize_data_source(val):
    if val is None:
        return None
    v = str(val).lower().strip()
    if "industrial" in v and "synthetic" in v:
        return "Industrial + synthetic"
    if "industrial" in v and "benchmark" in v:
        return "Industrial + benchmark"
    if "lab" in v and ("synthetic" in v or "industrial" in v):
        return "Lab + other"
    if "synthetic" in v and "benchmark" in v:
        return "Synthetic + benchmark"
    if "benchmark" in v:
        return "Benchmark"
    if "industrial" in v:
        return "Industrial"
    if "synthetic" in v or "synthic" in v:
        return "Synthetic"
    if "lab" in v:
        return "Lab"
    if "survey" in v or "literature" in v:
        return "Literature/survey"
    return "Other"


# ================================================================
# DATA LOADING & CLEANING
# ================================================================
def load_data(path=EXCEL_PATH, sheet=SHEET_NAME):
    df = pd.read_excel(path, sheet_name=sheet)

    # Drop rows with no key_id
    df = df.dropna(subset=["key_id"]).copy()

    # Apply mappings
    df["Country"] = df["Country"].map(
        lambda x: COUNTRY_MAP.get(x, x) if pd.notna(x) else x
    )
    df["DSS focus"] = df["DSS focus"].map(
        lambda x: DSS_FOCUS_MAP.get(x, x) if pd.notna(x) else x
    )
    df["Industry"] = df["Industry"].map(
        lambda x: INDUSTRY_MAP.get(x, x) if pd.notna(x) else x
    )
    df["Snowball (Yes/No)"] = df["Snowball (Yes/No)"].map(
        lambda x: SNOWBALL_MAP.get(x, x) if pd.notna(x) else x
    )
    df["Evaluation setting"] = df["Evaluation setting"].map(
        lambda x: EVAL_SETTING_MAP.get(x, x) if pd.notna(x) else x
    )
    df["Manufacturing level (L0,L1,L2,L3/L4)"] = df[
        "Manufacturing level (L0,L1,L2,L3/L4)"
    ].map(lambda x: MFG_LEVEL_MAP.get(x, x) if pd.notna(x) else x)

    # Normalize date to int
    df["Year"] = pd.to_numeric(df["Date"], errors="coerce").astype("Int64")

    # Normalize data source
    df["Data Source (clean)"] = df["Data Source"].apply(normalize_data_source)

    # Normalize job-shop
    df["Job-shop (clean)"] = df["Job-shop variations"].map(
        lambda x: JOBSHOP_MAP.get(x, "Other") if pd.notna(x) else x
    )

    # High-level groupings for Industry and DSS focus
    df["Industry (grouped)"] = df["Industry"].map(
        lambda x: INDUSTRY_GROUP_MAP.get(x, "Other") if pd.notna(x) else x
    )
    df["DSS focus (grouped)"] = df["DSS focus"].map(
        lambda x: DSS_FOCUS_GROUP_MAP.get(x, "Other") if pd.notna(x) else x
    )

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
            records.append(
                {
                    "key_id": row["key_id"],
                    "Year": row["Year"],
                    "Technology": norm,
                    "Manufacturing level (L0,L1,L2,L3/L4)": row[
                        "Manufacturing level (L0,L1,L2,L3/L4)"
                    ],
                }
            )
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


def fig_publication_timeline(df):
    """Fig 1: Publication count per year."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    years = df["Year"].dropna().astype(int)
    year_range = range(years.min(), years.max() + 1)
    counts = years.value_counts().reindex(year_range, fill_value=0).sort_index()

    bars = ax.bar(
        counts.index.astype(str),
        counts.values,
        color=COLORS["primary"],
        edgecolor="white",
        linewidth=0.5,
    )
    for bar, cnt in zip(bars, counts.values):
        if cnt > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                cnt + 0.5,
                str(cnt),
                ha="center",
                fontsize=9,
            )

    ax.set_xlabel("Publication year")
    ax.set_ylabel("Number of papers")
    # ax.set_title("Distribution of publications by year")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "01_publication_timeline")


def fig_manufacturing_level(df):
    """Fig 2: Distribution across manufacturing levels."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    col = "Manufacturing level (L0,L1,L2,L3/L4)"
    order = ["L0", "L1", "L2", "L3", "L3/L4", "L4"]
    counts = df[col].value_counts().reindex(order).dropna()

    bars = ax.bar(
        counts.index,
        counts.values,
        color=PALETTE[: len(counts)],
        edgecolor="white",
        linewidth=0.5,
    )
    for bar, cnt in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            cnt + 0.5,
            str(int(cnt)),
            ha="center",
            fontsize=9,
        )

    ax.set_xlabel("Manufacturing level")
    ax.set_ylabel("Number of papers")
    # ax.set_title("Distribution of papers by manufacturing level")
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

    bars = ax.barh(
        range(len(main)),
        main.values,
        color=COLORS["primary"],
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_yticks(range(len(main)))
    ax.set_yticklabels(main.index)
    for i, cnt in enumerate(main.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    # ax.set_title("Geographic distribution of papers")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "03_country_distribution")


# Mapping from data country names to Natural Earth NAME field
COUNTRY_TO_GEO = {
    "USA": "United States of America",
    "South Korea": "Korea",  # NE uses "Korea" for South Korea in some versions
}

# Small countries missing from 110m resolution — plotted as point markers
SMALL_COUNTRY_COORDS = {
    "Singapore": (103.8, 1.35),
}


def fig_country_choropleth(df):
    """Fig 3b: World map choropleth of paper counts by country."""
    # Load shapefile
    shapefile = Path(__file__).parent / "ne_110m_countries.gpkg"
    if not shapefile.exists():
        world = gpd.read_file(
            "https://naciscdn.org/naturalearth/110m/cultural/"
            "ne_110m_admin_0_countries.zip"
        )
        world.to_file(shapefile, driver="GPKG")
    else:
        world = gpd.read_file(shapefile)

    # Build paper counts per country
    counts = df["Country"].value_counts()

    # Map data country names → geo names
    geo_counts = {}
    point_counts = {}
    for country, cnt in counts.items():
        if country in SMALL_COUNTRY_COORDS:
            point_counts[country] = cnt
        else:
            geo_name = COUNTRY_TO_GEO.get(country, country)
            geo_counts[geo_name] = geo_counts.get(geo_name, 0) + cnt

    # Also try matching via NAME_LONG for South Korea
    # NE 110m uses "South Korea" in NAME but let's be safe
    world["paper_count"] = world["NAME"].map(geo_counts).fillna(0)
    # Fix South Korea if not matched via NAME
    sk_mask = world["NAME"].isin(["South Korea", "Korea", "Republic of Korea"])
    if sk_mask.any() and "South Korea" in counts.index:
        world.loc[sk_mask, "paper_count"] = counts["South Korea"]

    # Color scale — use discrete bins for better visual contrast
    max_count = int(world["paper_count"].max())
    bounds = [0, 1, 2, 4, 8, 16, max(32, max_count + 1)]
    cmap = plt.cm.Blues
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot countries with no papers in light gray
    world[world["paper_count"] == 0].plot(
        ax=ax, color="#EDEDED", edgecolor="white", linewidth=0.3
    )
    # Plot countries with papers using colormap
    world[world["paper_count"] > 0].plot(
        ax=ax,
        column="paper_count",
        cmap=cmap,
        norm=norm,
        edgecolor="white",
        linewidth=0.3,
        legend=False,
    )

    # Add point markers for small countries (e.g. Singapore)
    for country, (lon, lat) in SMALL_COUNTRY_COORDS.items():
        if country in point_counts:
            cnt = point_counts[country]
            color = cmap(norm(cnt))
            ax.plot(
                lon,
                lat,
                marker="o",
                markersize=6,
                color=color,
                markeredgecolor="black",
                markeredgewidth=0.5,
                zorder=5,
            )

    # Annotate countries with counts
    labeled = world[world["paper_count"] > 0].copy()
    for _, row in labeled.iterrows():
        centroid = row.geometry.centroid
        cnt = int(row["paper_count"])
        ax.annotate(
            str(cnt),
            xy=(centroid.x, centroid.y),
            ha="center",
            va="center",
            fontsize=6,
            fontweight="bold",
            color="black" if cnt < 8 else "white",
        )
    # Annotate small countries
    for country, (lon, lat) in SMALL_COUNTRY_COORDS.items():
        if country in point_counts:
            ax.annotate(
                str(point_counts[country]),
                xy=(lon, lat + 4),
                ha="center",
                va="bottom",
                fontsize=6,
                fontweight="bold",
            )

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.02, aspect=20)
    cbar.set_label("Number of papers", fontsize=9)

    ax.set_xlim(-170, 180)
    ax.set_ylim(-60, 85)
    ax.set_axis_off()
    # ax.set_title("Geographic distribution of reviewed papers", fontsize=11, pad=10)
    fig.tight_layout()
    save_fig(fig, "03b_country_choropleth")


def fig_technology_landscape(df):
    """Fig 4: Most common technologies (exploded from comma-separated)."""
    tech_df = explode_technologies(df)
    tech_counts = tech_df["Technology"].value_counts()

    # Only show techs with >= 2 occurrences
    tech_counts = tech_counts[tech_counts >= 2]

    fig, ax = plt.subplots(figsize=(7, 5))
    tech_counts = tech_counts.sort_values()
    bars = ax.barh(
        range(len(tech_counts)),
        tech_counts.values,
        color=COLORS["tertiary"],
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_yticks(range(len(tech_counts)))
    ax.set_yticklabels(tech_counts.index)
    for i, cnt in enumerate(tech_counts.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    # ax.set_title("Technology adoption across studies (≥2 occurrences)")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "04_technology_landscape")


def fig_methods_tech_wordcloud(df):
    """Fig 4c: Word cloud combining Methods and Technologies columns."""
    from wordcloud import WordCloud
    from collections import Counter
    counts = Counter()
    for col in ("Methods", "Technologies"):
        for _, row in df.iterrows():
            if pd.isna(row.get(col)):
                continue
            for t in re.split(r"[,+/]", str(row[col])):
                t = t.strip().rstrip(".")
                if t:
                    counts[t] += 1

    wc = WordCloud(
        width=1600,
        height=900,
        background_color="white",
        colormap="viridis",
        prefer_horizontal=0.9,
        relative_scaling=0.5,
    ).generate_from_frequencies(counts)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout(pad=0)
    save_fig(fig, "04c_methods_tech_wordcloud")


def fig_methods_landscape(df):
    """Fig 4b: Most common methods (exploded from comma-separated)."""
    records = []
    for _, row in df.iterrows():
        if pd.isna(row.get("Methods")):
            continue
        for t in re.split(r"[,+/]", str(row["Methods"])):
            t = t.strip().rstrip(".")
            if t:
                records.append(t)
    counts = pd.Series(records).value_counts()
    counts = counts[counts >= 2]

    fig, ax = plt.subplots(figsize=(7, 5))
    counts = counts.sort_values()
    ax.barh(
        range(len(counts)),
        counts.values,
        color=COLORS["tertiary"],
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index)
    for i, cnt in enumerate(counts.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "04b_methods_landscape")


def fig_dss_focus(df):
    """Fig 5: DSS focus areas (grouped) — pie chart."""
    fig, ax = plt.subplots(figsize=(8, 6))
    counts = df["DSS focus (grouped)"].value_counts()

    # Assign Scheduling a distinct teal; use palette (skipping teal) for the rest
    scheduling_color = "#1ABC9C"
    non_sched_palette = [c for c in PALETTE if c != scheduling_color]
    colors = []
    j = 0
    for v in counts.index:
        if v == "Scheduling":
            colors.append(scheduling_color)
        else:
            colors.append(non_sched_palette[j % len(non_sched_palette)])
            j += 1

    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=None,
        autopct=lambda p: f"{p:.1f}%\n({int(round(p * counts.sum() / 100))})",
        colors=colors,
        startangle=90,
        pctdistance=0.78,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 8},
    )

    for at, c in zip(autotexts, colors):
        at.set_fontsize(10)
        # Use white text on dark slices for readability
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        at.set_color("white" if luminance < 140 else "black")

    ax.legend(
        wedges,
        counts.index,
        title="DSS Focus",
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        fontsize=12,
    )
    # ax.set_title("Distribution of DSS focus areas")
    fig.tight_layout()
    save_fig(fig, "05_dss_focus")


def fig_jobshop_variants(df):
    """Fig 6: Job-shop scheduling variant breakdown."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    counts = df["Job-shop (clean)"].value_counts()
    order = [
        "No",
        "JSP",
        "FJSP",
        "DJSP",
        "DFJSP",
        "Distributed JSP",
        "Flow shop",
        "Other",
    ]
    counts = counts.reindex(order).dropna()

    bars = ax.bar(
        counts.index,
        counts.values,
        color=COLORS["primary"],
        edgecolor="white",
        linewidth=0.5,
    )
    for bar, cnt in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            cnt + 0.3,
            str(int(cnt)),
            ha="center",
            fontsize=8,
        )

    ax.set_xlabel("Job-shop variant")
    ax.set_ylabel("Number of papers")
    # ax.set_title("Job-shop scheduling problem variants")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    save_fig(fig, "06_jobshop_variants")


def fig_evaluation_setting(df):
    """Fig 7: Evaluation methodology distribution."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    counts = df["Evaluation setting"].value_counts()
    counts = counts[counts >= 1]

    bars = ax.bar(
        counts.index,
        counts.values,
        color=COLORS["quaternary"],
        edgecolor="white",
        linewidth=0.5,
    )
    for bar, cnt in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            cnt + 0.3,
            str(int(cnt)),
            ha="center",
            fontsize=8,
        )

    ax.set_xlabel("Evaluation setting")
    ax.set_ylabel("Number of papers")
    # ax.set_title("Evaluation methodology distribution")
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    save_fig(fig, "07_evaluation_setting")


def fig_data_source(df):
    """Fig 8: Data source distribution."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    counts = df["Data Source (clean)"].value_counts()
    counts = counts.sort_values()

    bars = ax.barh(
        range(len(counts)),
        counts.values,
        color=COLORS["quinary"],
        edgecolor="white",
        linewidth=0.5,
    )
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index)
    for i, cnt in enumerate(counts.values):
        ax.text(cnt + 0.3, i, str(cnt), va="center", fontsize=8)

    ax.set_xlabel("Number of papers")
    # ax.set_title("Data source distribution")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save_fig(fig, "08_data_source")


def fig_snowball(df):
    """Fig 9: Snowball vs database search papers."""
    fig, ax = plt.subplots(figsize=(4, 3))
    counts = df["Snowball (Yes/No)"].value_counts()

    colors = [COLORS["primary"], COLORS["secondary"]]
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.0f%%",
        colors=colors[: len(counts)],
        startangle=90,
        textprops={"fontsize": 10},
    )

    # ax.set_title("Paper source: database vs. snowballing")
    fig.tight_layout()
    save_fig(fig, "09_snowball_source")


def fig_industry(df):
    """Fig 10: Industry distribution (grouped, excluding Not specified) — pie chart."""
    fig, ax = plt.subplots(figsize=(8, 6))
    counts = df["Industry (grouped)"].value_counts()
    # Remove "Not specified" for this chart
    counts = counts.drop("Not specified", errors="ignore")

    colors = PALETTE[: len(counts)]

    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=None,
        autopct=lambda p: f"{p:.1f}%\n({int(round(p * counts.sum() / 100))})",
        colors=colors,
        startangle=90,
        pctdistance=0.78,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 8},
    )

    for at, c in zip(autotexts, colors):
        at.set_fontsize(10)
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        at.set_color("white" if luminance < 140 else "black")

    ax.legend(
        wedges,
        counts.index,
        title="Industry",
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        fontsize=12,
    )
    # ax.set_title("Industry application domains (grouped, excluding unspecified)")
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
            ax.plot(
                pivot.index,
                pivot[tech],
                marker="o",
                markersize=4,
                label=tech,
                color=PALETTE[i],
                linewidth=1.5,
            )

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of papers")
    # ax.set_title("Technology adoption trends over time")
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
                ax.text(
                    j,
                    i,
                    str(int(val)),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color=color,
                )

    # ax.set_title("Technology usage by manufacturing level")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Count")
    fig.tight_layout()
    save_fig(fig, "12_tech_by_mfg_level")


def fig_dss_by_mfg_level(df):
    """Fig 13: DSS focus (grouped) × Manufacturing level heatmap."""
    col = "Manufacturing level (L0,L1,L2,L3/L4)"
    dss_col = "DSS focus (grouped)"

    pivot = df.groupby([col, dss_col]).size().unstack(fill_value=0)
    level_order = ["L0", "L1", "L2", "L3", "L3/L4", "L4"]
    pivot = pivot.reindex([l for l in level_order if l in pivot.index])

    fig, ax = plt.subplots(figsize=(9, 3.5))
    im = ax.imshow(pivot.values, cmap="Oranges", aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(
        wrap_labels(pivot.columns, 18), rotation=45, ha="right", fontsize=7
    )
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if val > 0:
                color = "white" if val > pivot.values.max() * 0.6 else "black"
                ax.text(
                    j,
                    i,
                    str(int(val)),
                    ha="center",
                    va="center",
                    fontsize=7,
                    color=color,
                )

    # ax.set_title("DSS focus areas (grouped) by manufacturing level")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Count")
    fig.tight_layout()
    save_fig(fig, "13_dss_by_mfg_level")


# ================================================================
# MAIN
# ================================================================
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("excel", nargs="?", default=EXCEL_PATH)
    args = parser.parse_args()

    print(f"Reading: {args.excel}")
    print(f"Output:  {OUTPUT_DIR}/")
    print()

    df = load_data(path=args.excel)
    print(f"\nGenerating figures...\n")

    fig_publication_timeline(df)
    fig_manufacturing_level(df)
    fig_country_distribution(df)
    fig_country_choropleth(df)
    fig_technology_landscape(df)
    fig_methods_landscape(df)
    fig_methods_tech_wordcloud(df)
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
