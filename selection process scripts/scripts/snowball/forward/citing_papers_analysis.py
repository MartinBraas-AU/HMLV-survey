# Analyzes papers that cite the queried papers (forward snowballing impact analysis)
# Counts the number of times papers in your query are cited and produces visualizations
import json
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
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


class countCitations:
    def __init__(self, citing_json_path_1, citing_json_path_2):
        self.citing_json_path_1 = citing_json_path_1
        self.citing_json_path_2 = citing_json_path_2
        self.citing_papers_1 = self.load_json(citing_json_path_1)
        self.citing_papers_2 = {}  # self.load_json(citing_json_path_2)
        self.citation_count = {}

    def load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def combine(self):
        combined_citing_papers = {**self.citing_papers_1, **self.citing_papers_2}
        return combined_citing_papers

    def plot_total_citation_vs_number_of_papers(self):
        combined_citing_papers = self.combine()
        # Make a plot using x,y arrays. where y is the total citations and x is the number of papers
        # of the queried papers it cites.
        counts = []
        for key, val in combined_citing_papers.items():
            citation_count = int(val.get("citation_count", 0))
            counts.append(citation_count)
        # Sorted into key,value pairs in ascending order

        x = np.array([])
        y = np.array([])
        colors = np.array([])
        colors_per_year = np.array([])
        # Creating x,y arrays.
        for key, val in combined_citing_papers.items():
            citation_count = int(val.get("citation_count", 0))
            cited_key_ids = val.get("cited_key_id", [])
            year = val.get("year", "")
            current_year = datetime.now().year
            cites_per_year = max(1, current_year - int(year))
            number_of_queried_papers_cited = len(set(cited_key_ids))

            x = np.append(x, number_of_queried_papers_cited)
            y = np.append(y, citation_count)
            colors = np.append(colors, int(year))
            colors_per_year = np.append(colors_per_year, cites_per_year)

        # Plot
        plt.figure()
        plt.scatter(x, y, c=colors, s=10)
        # plt.yscale('log')
        # colorbar
        cbar = plt.colorbar()
        cbar.set_label("Year of Citing Paper")
        # cbar.set_label('Cites per Year since Publication')
        plt.xlabel("Number of Queried Papers Cited")
        plt.ylabel("Total Citations of Citing Paper")
        plt.title("Total Citations vs Number of Queried Papers Cited")
        plt.show()

    def plot_selected_citation_vs_number_of_papers(self):
        selected_citing_papers = self.select_subset_by(
            min_citations=5, year_range=(2024, 2026), cited_queried_min=7
        )
        # Make a plot using x,y arrays. where y is the total citations and x is the number of papers
        # of the queried papers it cites.
        counts = []
        for key, val in selected_citing_papers.items():
            citation_count = int(val.get("citation_count", 0))
            counts.append(citation_count)
        # Sorted into key,value pairs in ascending order

        x = np.array([])
        y = np.array([])
        colors = np.array([])
        colors_per_year = np.array([])
        # Creating x,y arrays.
        for key, val in selected_citing_papers.items():
            citation_count = int(val.get("citation_count", 0))
            cited_key_ids = val.get("cited_key_id", [])
            year = val.get("year", "")
            current_year = datetime.now().year
            cites_per_year = max(1, current_year - int(year))
            number_of_queried_papers_cited = len(set(cited_key_ids))

            x = np.append(x, number_of_queried_papers_cited)
            y = np.append(y, citation_count)
            colors = np.append(colors, int(year))
            colors_per_year = np.append(colors_per_year, cites_per_year)

        # Plot
        plt.figure()
        plt.scatter(x, y, c=colors, s=10)
        # plt.yscale('log')
        # colorbar
        cbar = plt.colorbar()
        cbar.set_label("Year of Citing Paper")
        # cbar.set_label('Cites per Year since Publication')
        plt.xlabel("Number of Queried Papers Cited")
        plt.ylabel("Total Citations of Citing Paper")
        plt.title("Total Citations vs Number of Queried Papers Cited")
        plt.show()

    def plot_citation_distribution(self):
        # This function just prints the citation distribution of papers citing the queried papers.
        # use arrays to store the counts
        combined_citing_papers = self.combine()
        # Make a plot using x,y arrays. where y is the number of citations and x is the paper.
        # Extract citation counts (ensure they are integers)
        counts = []
        for key, val in combined_citing_papers.items():
            citation_count = int(val.get("citation_count", 0))
            counts.append(citation_count)
        # Sorted into key,value pairs in ascending order
        sorted_list = sorted(
            combined_citing_papers.items(),
            key=lambda kv: int(kv[1].get("citation_count", 0)),
            reverse=True,
        )
        print("Top 10 papers by total citations:")
        for i in range(10):
            key, val = sorted_list[i]
            print(f"{i+1}. {key}: {val.get('citation_count', 0)} citations")

        # Sort counts descending
        counts_sorted = sorted(counts, reverse=True)

        # X-axis: rank (1 = highest cited)
        x_vals = list(range(1, len(counts_sorted) + 1))

        # Plot
        plt.figure()
        plt.plot(x_vals, counts_sorted, marker="o")
        plt.xlabel("Papers")
        plt.ylabel("Number of Citations")
        plt.title("Total citation count of the Papers Citing the Queried Papers")
        plt.show()

    def count_citations_towards_queried(self):
        combined_citing_papers = self.combine()
        for key, val in combined_citing_papers.items():
            cited_key_ids = val.get("cited_key_id", [])
            unique_cited_key_ids = set(cited_key_ids)
            count = len(unique_cited_key_ids)
            total_count = int(val.get("citation_count"))
            self.citation_count[key] = [count, total_count]

    def print_citation_counts(self):
        total_number_of_papers = 0
        print(f"Total citation counts towards queried papers:{len(self.citation_count)}")
        for key_id, count in self.citation_count.items():
            internal_count = count[0]
            total_count = count[1]
            if internal_count > 6:  # Print only if citations are more than 5
                total_number_of_papers += 1
                print(f"{key_id}: {internal_count} citations")
        print(
            f"Total number of papers with more than 6 citations: {total_number_of_papers}"
        )

    def select_subset_by(
        self,
        min_citations=5,
        year_range=(2024, 2025),
        cited_queried_min=7,
    ):
        """
        Select a subset of citing papers based on minimum citations, year range, and minimum cited in query.
        Returns a dict of selected papers.
        """
        combined_citing_papers = self.combine()
        selected_papers = {}
        for k, count in self.citation_count.items():
            internal_count = count[0]          # cited in query
            total_citations = count[1]         # total/global citations
            citing_info = combined_citing_papers.get(k, {})
            year = citing_info.get("year", 0)
            cited_key_ids = citing_info.get("cited_key_id", [])
            num_cited_in_query = len(set(cited_key_ids))

            if (
                total_citations >= min_citations
                and year_range[0] <= int(year) <= year_range[1]
                and num_cited_in_query >= cited_queried_min
            ):
                selected_papers[k] = citing_info

        print(
            f"Selected {len(selected_papers)} papers with min_citations={min_citations}, year_range={year_range}, cited_queried_min={cited_queried_min}"
        )
        return selected_papers

    def histo_plot_citation_distribution(self):

        counts = [v[0] for v in self.citation_count.values()]
        # print(f"Counts: {counts}")
        plt.hist(
            counts, bins=range(1, max(counts) + 2), align="left", edgecolor="black"
        )
        # plt.plot(sorted(counts, reverse=True), marker='o')
        plt.xlabel("Number of Citations")
        plt.ylabel("Number of Papers")
        plt.title("Histogram of the number of times Papers Cite the Queried Papers")
        plt.xticks(range(1, max(counts) + 1))
        # plt.yticks(range(0, 101, 5))
        plt.xlim(0, max(counts) + 1)
        # plt.ylim(0, 100)
        plt.show()
        print("Citation distribution plot displayed.")

    def _xy_year_arrays(self, papers_dict):
        x, y, years = [], [], []
        current_year = datetime.now().year

        for _, val in papers_dict.items():
            citation_count = int(val.get("citation_count", 0))
            cited_key_ids = val.get("cited_key_id", [])
            year_raw = val.get("year", current_year)
            try:
                year = int(str(year_raw)[:4])
            except ValueError:
                year = current_year

            x.append(len(set(cited_key_ids)))
            y.append(citation_count)
            years.append(year)

        return np.array(x), np.array(y), np.array(years)

    def print_selected_info(self, selected):
        print(f"Selected papers info (Total: {len(selected)}):")
        for k, v in selected.items():
            citation_count = v.get("citation_count", 0)
            # year = v.get("year", "N/A")
            cited_key_ids = v.get("cited_key_id", [])
            num_cited_in_query = len(set(cited_key_ids))
            title = v.get("title", "N/A")
            print(
                f"Paper {title}, Total Citations: {citation_count}, Cited in Query: {num_cited_in_query}"
            )

    def plot_all_and_selected_subplots(self, selected, cmap_name="viridis"):
        all_papers = self.combine()

        x_all, y_all, yr_all = self._xy_year_arrays(all_papers)
        x_sel, y_sel, yr_sel = self._xy_year_arrays(selected)

        # shared year scale across BOTH subplots
        years_for_scale = (
            yr_all if len(yr_sel) == 0 else np.concatenate([yr_all, yr_sel])
        )
        norm = Normalize(
            vmin=int(years_for_scale.min()), vmax=int(years_for_scale.max())
        )
        cmap = plt.get_cmap(cmap_name)

        fig, (ax1, ax2) = plt.subplots(
            1, 2, sharex=True, sharey=True, figsize=(12, 5), constrained_layout=True
        )

        ax1.scatter(x_all, y_all, c=yr_all, cmap=cmap, norm=norm, s=10, alpha=0.8)
        ax1.set_title("All citing papers")

        ax2.scatter(x_sel, y_sel, c=yr_sel, cmap=cmap, norm=norm, s=20, alpha=0.9)
        ax2.set_title("Selected subset")

        for ax in (ax1, ax2):
            ax.set_xlabel("Number of Queried Papers Cited")
            ax.set_ylabel("Total Citations of Citing Paper")
            ax.grid(True, alpha=0.2)

        # one shared colorbar
        sm = ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        fig.colorbar(sm, ax=[ax1, ax2], label="Year of Citing Paper")

        plt.show()


if __name__ == "__main__":
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["citing_papers_analysis"]
    citer_json_1 = resolve_from_root(repo_root, defaults["citer_json_primary"])
    citer_json_2 = resolve_from_root(repo_root, defaults["citer_json_secondary"])

    counter = countCitations(citer_json_1, citer_json_2)
    counter.count_citations_towards_queried()
    counter.print_citation_counts()
    # counter.histo_plot_citation_distribution()
    # counter.plot_citation_distribution()

    # counter.plot_total_citation_vs_number_of_papers()
    # counter.plot_selected_citation_vs_number_of_papers()

    selected = counter.select_subset_by(
        min_citations=5, year_range=(2020, 2026), cited_queried_min=7
    )
    counter.print_selected_info(selected=selected)
    counter.plot_all_and_selected_subplots(selected=selected)

    # counter.select_subset_by(min_citations=5, year_range=(2024,2025), cited_queried_min=7)

    # counter.count_citations_towards_queried()   # fills self.citation_count
    # counter.compute_scores()                    # uses citation_count + year + total citations

    # counter.print_top_by_score(top_n=10, min_internal=0)  # your ">=7 cites our set" idea
    # counter.plot_scores_sorted(min_internal=0)
