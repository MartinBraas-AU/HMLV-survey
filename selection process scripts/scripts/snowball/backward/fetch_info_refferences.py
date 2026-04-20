# This script fetches reference information from the scopus API
# and save it in a json file called refference_relevance_scored_2026_ETO-14-01_w_info.json
import json
import os
import time
import requests
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


class fetch_info_refferences:
    def __init__(self, refference_json_path, output_json_path):
        self.refference_json_path = refference_json_path
        self.output_json_path = output_json_path
        self.refference_papers = self.load_json(refference_json_path)

    def load_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    # Further methods to fetch info from scopus API would go here

    def clean_scopus_id(self, scopus_id: str) -> str:
        return (
            str(scopus_id or "")
            .replace("SCOPUS_ID:", "")
            .replace("2-s2.0-", "")
            .strip()
        )

    def normalize_reference_list(self, refs_raw):
        if refs_raw is None:
            return []
        if isinstance(refs_raw, list):
            return refs_raw
        if isinstance(refs_raw, dict):
            return [refs_raw]
        return []

    def extract_into_out(self, refs, out, seen):
        for ref in refs:
            ref_info = (ref.get("ref-info") or {}).get("ref-publicationinfo") or {}
            title = ref_info.get("title", "") or ""
            doi = ref_info.get("doi", "") or ""
            sid = (ref.get("scopus-id") or "").strip()

            key = (sid, doi, title.lower().strip())
            if key in seen:
                continue

            seen.add(key)
            out.append(
                {
                    "title": title,
                    "doi": doi,
                    "scopus_id": sid,
                }
            )

    def fetch(
        self, scopus_id: str, api_key: str, page_size: int = 25, retries: int = 3
    ) -> dict:
        clean_id = self.clean_scopus_id(scopus_id)
        if not clean_id:
            return {}

        base_url = f"https://api.elsevier.com/content/abstract/scopus_id/{clean_id}"
        headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": api_key,
            "X-ELS-ResourceVersion": "XOCS",
        }

        out = []
        seen = set()

        # =========================================================
        # PART 1 — First request (always works)
        # =========================================================
        # params1 = {"view": "REF", "startref": 1, "refcount": page_size}
        params1 = {"view": "FULL"}
        # params1 = {"view": "REF", "startref": 1}

        resp = None
        for attempt in range(1, retries + 1):
            resp = requests.get(base_url, headers=headers, params=params1, timeout=30)
            if resp.status_code == 200:
                break
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 10 * attempt)
                continue
            time.sleep(5)

        if resp is None or resp.status_code != 200:
            print(
                f"Failed for {clean_id} (status={resp.status_code if resp else 'None'})"
            )
            return {}

        data = resp.json()

        arr = data.get("abstracts-retrieval-response", {}) or {}
        core = arr.get("coredata", {}) or {}

        title = core.get("dc:title") or ""
        doi = core.get("prism:doi") or ""

        cover_date = core.get("prism:coverDate") or ""  # "YYYY-MM-DD"
        year = (
            int(cover_date[:4])
            if len(cover_date) >= 4 and cover_date[:4].isdigit()
            else None
        )

        scopus_id_out = clean_id

        refs_raw = {
            "title": title,
            "doi": doi,
            "year": year,
            "scopus_id": scopus_id_out,
        }
        # refs1 = self.normalize_reference_list(refs1_raw)
        # self.extract_into_out(refs1, out, seen)

        return refs_raw

    def extract_references_info(self, api_key: str):
        all_references_info = []

        if api_key.strip() == "":
            print("No valid API key provided.")
            return all_references_info

        for scopus_id in self.refference_papers.keys():
            self.print_id(scopus_id)
            # refs_info = self.fetch(scopus_id, api_key)
            # all_references_info.append(refs_info)
            # print(f"Fetched info for refference {scopus_id} where title is '{refs_info.get('title','')}'")

        return all_references_info

    def save_references_info(self, api_key: str):
        all_references_info = self.extract_references_info(api_key)
        with open(self.output_json_path, "w") as f:
            json.dump(all_references_info, f, indent=2)
        print(f"Saved references info to {self.output_json_path}")

    def print_id(self, scopus_id: str):
        print(f"Scopus ID: {scopus_id}")


if __name__ == "__main__":
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["fetch_info_refferences"]
    refference_json_path = resolve_from_root(repo_root, defaults["reference_json"])
    output_json_path = resolve_from_root(repo_root, defaults["output_json"])
    api_key = os.getenv("SCOPUS_API_KEY") or ""

    fetcher = fetch_info_refferences(refference_json_path, output_json_path)
    fetcher.extract_references_info(api_key)
    # fetcher.save_references_info(api_key)
