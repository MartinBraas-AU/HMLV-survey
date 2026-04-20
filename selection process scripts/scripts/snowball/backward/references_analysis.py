# Analyzes statistics on papers found through backward snowballing (references cited by papers)
# Counts the frequency papers are referenced and produces visualizations
import json
import matplotlib.pyplot as plt
import math
from datetime import datetime
import numpy as np
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


class countRefferences:
    def __init__(self, refference_json_path):
        self.refference_json_path = refference_json_path
        self.refference_papers = self.load_json(refference_json_path)
        self.refferenced = {}

    def load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def utility_filter_existing(self):
        all_refferenced = self.number_of_times_refferenced()

        # Filter paper that exist
        existing_scopus_ids = set(self.refference_papers.keys())
        self.refferenced = {
            k: v for k, v in all_refferenced.items() if k not in existing_scopus_ids
        }
        print(f"Total number of referenced papers so far: {len(self.refferenced)}")

    def number_of_times_refferenced(self):
        """Count the number of times each paper is referenced in the refference json file."""
        result = {}
        print(f"Counting references from {len(self.refference_papers)} papers...")
        if isinstance(self.refference_papers, dict):
            for key, val in self.refference_papers.items():
                if not isinstance(val, dict):
                    val = self.refference_papers[key]
                else:
                    val = val.get("references", [])
                for item in val:
                    it = item.get("scopus_id", "")
                    if it in result:
                        result[it] += 1
                    else:
                        result[it] = 1
        return result


    def histo_plot_citation_distribution(self, level = "?"):
        counts = list(self.refferenced.values())
        plt.hist(
            counts, bins=range(1, max(counts) + 2), align="left", edgecolor="black"
        )
        # plt.plot(sorted(counts, reverse=True), marker='o')
        plt.xlabel("Number of Citations")
        plt.ylabel("Number of Papers")
        plt.title(f"{level} Histogram of the number of times Papers are Cited in References")
        plt.xticks(range(1, max(counts) + 1))
        # plt.yticks(range(0, 101, 5))
        plt.xlim(0, max(counts) + 1)
        # plt.ylim(0, 100)
        plt.show()
        print("Citation distribution plot displayed.")

    def print_highly_refferenced(self, threshold=5):
        counts_dict = self.refferenced
        highly_refferenced = {k: v for k, v in counts_dict.items() if v >= threshold}
        print(f"Papers referenced more than {threshold} times:")
        # Sort by count descending
        highly_refferenced = dict(
            sorted(highly_refferenced.items(), key=lambda item: item[1], reverse=True)
        )
        for k, v in highly_refferenced.items():
            print(f"Scopus ID: {k}, Count: {v}")
        print(f"Total number of selected referenced papers: {len(highly_refferenced)}")


if __name__ == "__main__":
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["references_analysis"]
    refference_json_1 = resolve_from_root(repo_root, defaults["reference_json"])

    counter = countRefferences(refference_json_1)
    counter.utility_filter_existing()
    # counter.number_of_times_refferenced()
    counter.histo_plot_citation_distribution(level=defaults["level_label"])
    counter.print_highly_refferenced(threshold=int(defaults["threshold"]))
