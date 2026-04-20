import re
import requests
import os
import json
import time
from urllib.parse import quote
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


class ScopusCiterFetcher:#25
    def __init__(self, api_key=None, page_size=50, max_results=5000, delay=1.0):
        self.api_key = api_key or os.getenv("SCOPUS_API_KEY")
        self.page_size = page_size
        self.max_results = max_results
        self.delay = delay

        self.headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": self.api_key
        }

    def clean_scopus_id(self, sid: str):
        """Normalize Scopus ID by removing prefixes."""
        return (
            str(sid)
            .replace("SCOPUS_ID:", "")
            .replace("2-s2.0-", "")
            .strip()
        )
    
    def replace_dict_key(self, data_dict: dict, old_key: str, new_key: str) -> dict:
        """Replace a key with a new key"""
        val = data_dict.pop(old_key)
        data_dict[new_key] = val
        return data_dict

    def fetch_page(self, scopus_id: str, start: int):
        """Fetch one paginated block of citing papers."""
        query = f"REF({scopus_id})"
        url = (
            "https://api.elsevier.com/content/search/scopus?"
            f"query={quote(query)}&start={start}&count={self.page_size}"
        )

        resp = requests.get(url, headers=self.headers)
        #print("6")
        print(resp)
        if resp.status_code != 200:
            print(f"Error {resp.status_code} at start={start} for {scopus_id}")
            return None

        return resp.json()

    def extract_entries(self, data_json):
        """Extract citing-paper info from JSON."""
        if not data_json:
            return []

        entries = data_json.get("search-results", {}).get("entry", [])
        if len(entries) == 1 and "error" in entries[0]:
                return []  # Zero citations
        results = []

        for e in entries:
            results.append({
                "title": e.get("dc:title", ""),
                "doi": e.get("prism:doi", ""),
                "scopus_id": e.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
                "year": e.get("prism:coverDate", "")[:4],
                "type": e.get("subtypeDescription", "")
            })

        return results

    def fetch_all_citers(self, scopus_id: str, key_id: str):
        """Fetch ALL citing documents for a single Scopus ID."""
        scopus_id = self.clean_scopus_id(scopus_id)
        print("4")
        all_results = []

        start = 0
        while start < self.max_results:
            #print("5")
            data_json = self.fetch_page(scopus_id, start)
            #print(f"data_json: {data_json}")
            # Stop if no data or no entries
            if not data_json:
                print("No data returned, stopping.")
                break
            
            # replace cleaned scopus_id with key_id in output entries
            data_json = self.replace_dict_key(data_json, scopus_id, key_id)

            entries = self.extract_entries(data_json)
            #print(f"entries: {entries}")
            #print(not entries)
            if not entries:
                print("No entries found, stopping.")
                break

            all_results.extend(entries)

            start += self.page_size
            time.sleep(self.delay)

        return all_results

    def extract_entries_dict(self, data_json, key_id: str):
        """Extract citing-paper info from JSON."""
        if not data_json:
            return {}

        entries = data_json.get("search-results", {}).get("entry", [])
        if len(entries) == 1 and "error" in entries[0]:
                return {}  # Zero citations
        results = {}
        
        for e in entries:
            citing_key_id = "_".join([e.get("prism:coverDate", "")[:4], self.clean(e.get("dc:title", ""))])
            print("citing_key_id:", citing_key_id)
            results[citing_key_id] = {
                "title": e.get("dc:title", ""),
                "doi": e.get("prism:doi", ""),
                "scopus_id": e.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
                "year": e.get("prism:coverDate", "")[:4],
                "citation_count": e.get("citedby-count", "0"),
                "type": e.get("subtypeDescription", ""),
                "cited_key_id": [key_id]
            }

        return results

    def fetch_all_citers_dict(self, scopus_id: str, key_id: str):
        """Fetch ALL citing documents for a single Scopus ID."""
        scopus_id = self.clean_scopus_id(scopus_id)
        print("4")
        all_results = {}
        total = None # Keep track of total citations
        start = 0
        while start < self.max_results:
            #print("5")
            data_json = self.fetch_page(scopus_id, start)
            #print(f"data_json: {data_json}")
            # Stop if no data or no entries
            #if not data_json:
            #    print("No data returned, stopping.")
            #    break
            
            # replace cleaned scopus_id with key_id in output entries
            #data_json = self.replace_dict_key(data_json, scopus_id, key_id)

                    # Read totalResults ONCE (from first page)
            if total is None and data_json:
                total = int(
                    data_json
                    .get("search-results", {})
                    .get("opensearch:totalResults", "0")
                )
                print(f"📊 Scopus reports total citations: {total}")

            entries = self.extract_entries_dict(data_json, key_id)
            #print(f"entries: {entries}")
            #print(not entries)

            if not bool(entries):
                print("No entries found, stopping.")
                break

            all_results.update(entries) # A citing paper should be unique, so we can use update

            start += self.page_size
            time.sleep(self.delay)
        
        if total is not None and total != len(all_results):
            print(f" Duplicate citations: {total - len(all_results)}------------------------------------")

        return all_results

    def clean(self, s: str) -> str:
        s = str(s)
        s = s.strip()
        s = re.sub(r"\s+", "_", s)  # replace any whitespace with _
        return s.lower()


class HMLVCitationCollector:
    """Wrapper that loads HMLV papers, fetches citers, and saves results."""

    def __init__(self, input_json, filter_json, output_json, fetcher: ScopusCiterFetcher):
        self.input_json = input_json
        self.filter_json = filter_json
        self.output_json = output_json
        self.fetcher = fetcher

        # Load previously scraped data (incremental)
        if Path(output_json).exists():
            with open(output_json, "r") as f:
                self.citing_data = json.load(f)
        else:
            self.citing_data = {}

    def load_hmlv_papers(self, json_path=None):
        """Load list of HMLV papers."""
        path = json_path or self.input_json
        with open(path, "r", encoding="utf-8") as f:
            papers = json.load(f)
        return papers

    def save_progress(self):
        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(self.citing_data, f, indent=2, ensure_ascii=False)

    def clean(self, s: str) -> str:
        s = str(s)
        s = s.strip()
        s = re.sub(r"\s+", "_", s)  # replace any whitespace with _
        return s.lower()

    def run(self):
        """Fetch citing documents for all HMLV papers."""
        papers = self.load_hmlv_papers()
        included_papers = self.load_hmlv_papers(self.filter_json)
        included_key_ids = set([paper.get("key_id", "") for paper in included_papers])
        #print(papers)
        print("1")
        print(f"📚 Loaded {len(papers)} HMLV papers")
        
        for i, paper in enumerate(papers, start=1):
            #print("2")
            sid = paper.get("scopus_id")
            key_id = "_".join([self.clean(paper.get("Year","")), self.clean(paper.get("Title",""))]) #paper.get("key_id")
            print(f"Processing paper {i}/{len(papers)}: {key_id} ({sid})")
            sid = self.fetcher.clean_scopus_id(sid)
            #print("3")
            if not sid:
                continue

            if sid in self.citing_data:
                print(f"[{i}] Skipping {sid} (already fetched)")
                continue

            print(f"[{i}] Fetching citers for {sid}...")
            #citers = self.fetcher.fetch_all_citers(sid, key_id)
            if key_id not in included_key_ids:
                print(f"Key ID {key_id} not in included papers, skipping fetch.")
                continue
            citers = self.fetcher.fetch_all_citers_dict(sid, key_id)
            #self.citing_data[sid] = citers

            # Merge citers into existing data
            for key, val in citers.items():
                if key in self.citing_data:
                    self.citing_data[key]["cited_key_id"].extend(val["cited_key_id"]) # If a paper cites multiple HMLV papers, extend the list it cites.
                else:
                    self.citing_data[key] = val
            #print("4")
            print(f"    ✅ {len(citers)} citing documents saved\n")
            self.save_progress()
            time.sleep(1)

        print(f"🎉 All results saved to {self.output_json}")


if __name__ == "__main__":
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["fetch_citing_papers_level"]

    # Build the fetcher (configurable)
    fetcher = ScopusCiterFetcher(
        api_key=os.getenv("SCOPUS_API_KEY"),
        page_size=25,
        max_results=5000,
        delay=0.8,
    )

    collector = HMLVCitationCollector(
        input_json=resolve_from_root(repo_root, defaults["input_json"]),
        filter_json=resolve_from_root(repo_root, defaults["filter_json"]),
        output_json=resolve_from_root(repo_root, defaults["output_json"]),
        fetcher=fetcher
    )

    collector.run()
