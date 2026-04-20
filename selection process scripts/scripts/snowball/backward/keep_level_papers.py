# This script removes excluded papers from the references_2026_ETO-14-01 json file
import json
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


class keep_level_papers:
    def __init__(self, reference_json_path, excluded_json_path):
        self.reference_json_path = reference_json_path
        self.excluded_json_path = excluded_json_path
        self.reference_papers = self.load_json(reference_json_path)
        self.excluded_papers = self.load_json(excluded_json_path)

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_excluded_key_ids(self):
        return {paper.get("key_id", "") for paper in self.excluded_papers}
    
    def clean_scopus_id(self, scopus_id: str) -> str:
        return (
            str(scopus_id or "")
            .replace("SCOPUS_ID:", "")
            .replace("2-s2.0-", "")
            .strip()
        )

    def keep_included(self):
        included_ids = self.get_excluded_key_ids()
        print(f"Number of included papers: {len(included_ids)}")

        cleaned_references = {}

        cleaned_included_ids = set([self.clean_scopus_id(scopus_id) for scopus_id in included_ids])

        
        for k, v in self.reference_papers.items():
            if k in cleaned_included_ids:
                cleaned_references[k] = v 

        return cleaned_references

    def save_cleaned_references(self, output_path):
        cleaned_references = self.keep_included()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_references, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["keep_level_papers"]
    reference_json_path = resolve_from_root(repo_root, defaults["reference_json"])
    excluded_json_path = resolve_from_root(repo_root, defaults["included_json"])
    output_path = resolve_from_root(repo_root, defaults["output_json"])

    keeper = keep_level_papers(reference_json_path, excluded_json_path)
    keeper.save_cleaned_references(output_path)
    print(f"Cleaned references saved to {output_path}")