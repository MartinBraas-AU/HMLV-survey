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


class remove_excluded:
    def __init__(self, reference_json_path, excluded_json_path):
        self.reference_json_path = reference_json_path
        self.excluded_json_path = excluded_json_path
        self.reference_papers = self.load_json(reference_json_path)
        self.excluded_papers = self.load_json(excluded_json_path)

    def load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def get_excluded_scopus_ids(self):
        return {paper.get("scopus_id", "") for paper in self.excluded_papers}
    
    def clean_scopus_id(self, scopus_id: str) -> str:
        return (
            str(scopus_id or "")
            .replace("SCOPUS_ID:", "")
            .replace("2-s2.0-", "")
            .strip()
        )

    def remove_excluded(self):
        excluded_ids = self.get_excluded_scopus_ids()
        print(f"Number of excluded papers: {len(excluded_ids)}")

        cleaned_references = {}

        cleaned_excluded_ids = set([self.clean_scopus_id(scopus_id) for scopus_id in excluded_ids])

        
        for k, v in self.reference_papers.items():
            if k not in cleaned_excluded_ids:
                cleaned_references[k] = v 

        return cleaned_references

    def save_cleaned_references(self, output_path):
        cleaned_references = self.remove_excluded()
        with open(output_path, "w") as f:
            json.dump(cleaned_references, f, indent=2)


if __name__ == "__main__":
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["remove_excluded"]
    reference_json_path = resolve_from_root(repo_root, defaults["reference_json"])
    excluded_json_path = resolve_from_root(repo_root, defaults["excluded_json"])
    output_path = resolve_from_root(repo_root, defaults["output_json"])

    remover = remove_excluded(reference_json_path, excluded_json_path)
    remover.save_cleaned_references(output_path)
    print(f"Cleaned references saved to {output_path}")