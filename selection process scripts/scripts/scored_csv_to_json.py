import pandas as pd
import json
import re
from pathlib import Path


def load_paths_config():
    for parent in Path(__file__).resolve().parents:
        config_path = parent / "paths.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f), config_path.parent
    raise FileNotFoundError("Could not find paths.json from script location")


def resolve_from_root(root_dir: Path, relative_path: str) -> str:
    return str((root_dir / relative_path.lstrip("./")).resolve())


def clean_scopus_id(sid) -> str:
    """Clean Scopus ID by removing prefixes and whitespace."""
    return re.sub(r"SCOPUS_ID:?", "", str(sid)).strip()

def clean(s: str) -> str:
    s = str(s)
    s = s.strip()
    s = re.sub(r"\s+", "_", s)  # replace any whitespace with _
    return s.lower()

def convert_df_to_json(df) -> list[dict]:
    """Convert DataFrame of reviews to list of dicts."""
    reviews = []
    for _, row in df.iterrows():
        scopus_id = clean_scopus_id(row.get("EID", ""))
        title = str(row.get("Title", "")).strip()
        year = str(row.get("Year", "")).strip()
        doi = str(row.get("DOI", "")).strip()
        reviews.append({
            "key_id": "_".join([clean(year), clean(title)]),
            "Title": title,
            "Year": year,
            "doi": doi,
            "scopus_id": scopus_id
        })
        #reviews.append({
        #    "Title": str(row.get("Title", "")).strip(),
        #    "Year": str(row.get("Year", "")).strip(),
        #    "doi": str(row.get("DOI", "")).strip(),
        #    "scopus_id": scopus_id
        #})
    return reviews


def write_json(output_name, reviews):
    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2)

if __name__ == "__main__":
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["scored_csv_to_json"]
    input_file = resolve_from_root(repo_root, defaults["input_file"])
    output_name = resolve_from_root(repo_root, defaults["output_file"])


    df = pd.read_csv(input_file, sep=",", encoding="utf-8")
    reviews = convert_df_to_json(df)
    write_json(output_name, reviews)
    print(f"💾 Saved {len(reviews)} reviews to {output_name}")