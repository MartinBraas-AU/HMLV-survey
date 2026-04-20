import argparse
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


def clean_scopus_id(scopus_id: str) -> str:
    return (
        str(scopus_id or "")
        .replace("SCOPUS_ID:", "")
        .replace("2-s2.0-", "")
        .strip()
    )


def fetch_references_og(scopus_id: str, api_key: str, retries: int = 3, delay: float = 1.0):
    clean_id = clean_scopus_id(scopus_id)
    if not clean_id:
        return []

    url = f"https://api.elsevier.com/content/abstract/scopus_id/{clean_id}?view=REF"
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key,
        "X-ELS-ResourceVersion": "XOCS",
    }

    last_status = None
    for attempt in range(1, retries + 1):
        resp = requests.get(url, headers=headers)
        last_status = resp.status_code

        if resp.status_code == 200:
            break

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            sleep_s = float(retry_after) if retry_after else (10 * attempt)
            print(f"Rate-limited (429) for {clean_id}; sleeping {sleep_s}s")
            time.sleep(sleep_s)
            continue

        print(f"Error {resp.status_code} for {clean_id} (attempt {attempt}/{retries}); sleeping 5s")
        time.sleep(5)
    else:
        print(f"Failed to fetch {clean_id} after {retries} attempts (last_status={last_status})")
        return []

    try:
        data = resp.json()
    except Exception:
        print(f"Failed to parse JSON for {clean_id}")
        return []

    response = data.get("abstracts-retrieval-response", {})
    refs_data = response.get("references", {})
    refs = refs_data.get("reference", []) or []

    out = []
    for ref in refs:
        ref_info = (ref.get("ref-info") or {}).get("ref-publicationinfo") or {}
        out.append(
            {
                "title": ref_info.get("title", "") or "",
                "doi": ref_info.get("doi", "") or "",
                "scopus_id": (ref.get("scopus-id") or "").strip(),
            }
        )

    time.sleep(delay)
    return out

def normalize_reference_list(refs_raw):
    if refs_raw is None:
        return []
    if isinstance(refs_raw, list):
        return refs_raw
    if isinstance(refs_raw, dict):
        return [refs_raw]
    return []


def get_json_with_retries(url: str, headers: dict, retries: int, timeout_s: int = 60):
    last_status = None

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout_s)
        except requests.RequestException as e:
            print(f"Request error (attempt {attempt}/{retries}): {e}")
            time.sleep(5)
            continue

        last_status = resp.status_code

        if resp.status_code == 200:
            try:
                return resp.json(), 200
            except Exception:
                return None, "bad_json"

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            try:
                sleep_s = float(retry_after) if retry_after else (10 * attempt)
            except ValueError:
                sleep_s = 10 * attempt
            print(f"Rate-limited (429); sleeping {sleep_s}s")
            time.sleep(sleep_s)
            continue

        print(f"Error {resp.status_code} (attempt {attempt}/{retries}); sleeping 5s")
        time.sleep(5)

    return None, last_status


def extract_refs_from_abstract_response(data: dict):
    response = (data or {}).get("abstracts-retrieval-response") or {}
    refs_data = response.get("references") or {}
    return normalize_reference_list(refs_data.get("reference"))

def fetch_references_test(scopus_id: str, api_key: str, retries: int = 3, delay: float = 1.0):
    clean_id = clean_scopus_id(scopus_id)
    if not clean_id:
        return []

    # ----------------
    # PAGE 1 (EXACTLY like _og)
    # ----------------
    url1 = f"https://api.elsevier.com/content/abstract/scopus_id/{clean_id}?view=REF"
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key,
        "X-ELS-ResourceVersion": "XOCS",
    }

    last_status = None
    for attempt in range(1, retries + 1):
        resp1 = requests.get(url1, headers=headers)
        last_status = resp1.status_code

        if resp1.status_code == 200:
            break

        if resp1.status_code == 429:
            retry_after = resp1.headers.get("Retry-After")
            sleep_s = float(retry_after) if retry_after else (10 * attempt)
            print(f"Rate-limited (429) for {clean_id}; sleeping {sleep_s}s")
            time.sleep(sleep_s)
            continue

        print(f"Error {resp1.status_code} for {clean_id} (attempt {attempt}/{retries}); sleeping 5s")
        time.sleep(5)
    else:
        print(f"Failed to fetch {clean_id} after {retries} attempts (last_status={last_status})")
        return []

    try:
        data1 = resp1.json()
    except Exception:
        print(f"Failed to parse JSON for {clean_id}")
        return []

    response1 = data1.get("abstracts-retrieval-response", {})
    refs_data1 = response1.get("references", {})
    refs1 = refs_data1.get("reference", []) or []

    out = []
    for ref in refs1:
        ref_info = (ref.get("ref-info") or {}).get("ref-publicationinfo") or {}
        out.append(
            {
                "title": ref_info.get("title", "") or "",
                "doi": ref_info.get("doi", "") or "",
                "scopus_id": (ref.get("scopus-id") or "").strip(),
            }
        )

    # ----------------
    # PAGE 2 (ONE extra page attempt; try 41 then 40)
    print(f"Total refs in page 1 for {clean_id}: {len(refs1)}")
    # ----------------
    if len(refs1) > 0:
        refcount = 40
        startref_candidates = [len(refs1), len(refs1)]
        print(f"recount={refcount}, startref_candidates={startref_candidates}")
        time.sleep(delay)

        got_page2 = False

        for startref in startref_candidates:
            url2 = (
                f"https://api.elsevier.com/content/abstract/scopus_id/{clean_id}"
                f"?view=REF&startref={41+17}&refcount={1}"
            )
            print(url2)
            last_status_2 = None
            for attempt in range(1, retries + 1):
                resp2 = requests.get(url2, headers=headers)
                last_status_2 = resp2.status_code
                print("URL:", resp2.request.url)
                print("Status:", resp2.status_code)
                print("Body:", resp2.text[:2000])
                if resp2.status_code == 200:
                    break

                if resp2.status_code == 429:
                    retry_after = resp2.headers.get("Retry-After")
                    sleep_s = float(retry_after) if retry_after else (10 * attempt)
                    print(f"Rate-limited (429) for {clean_id} page2(startref={startref}); sleeping {sleep_s}s")
                    time.sleep(sleep_s)
                    continue

                print(
                    f"Error {resp2.status_code} for {clean_id} page2(startref={startref}) "
                    f"(attempt {attempt}/{retries}); sleeping 5s"
                )
                time.sleep(5)
            else:
                print(
                    f"Failed page2 for {clean_id} (startref={startref}) "
                    f"after {retries} attempts (last_status={last_status_2})"
                )
                continue

            try:
                data2 = resp2.json()
            except Exception:
                print(f"Failed to parse JSON for {clean_id} page2(startref={startref})")
                continue

            response2 = data2.get("abstracts-retrieval-response", {})
            refs_data2 = response2.get("references", {})
            #refs2 = refs_data2.get("reference", []) or []
            refs2 = normalize_reference_list(refs_data2.get("reference"))

            print(f"Page2 OK for {clean_id} (startref={startref}): got {len(refs2)} refs")
                
            for ref in refs2:
                print(f"Ref2: {ref}")
                ref_info = (ref.get("ref-info") or {}).get("ref-publicationinfo") or {}
                out.append(
                    {
                        "title": ref_info.get("title", "") or "",
                        "doi": ref_info.get("doi", "") or "",
                        "scopus_id": (ref.get("scopus-id") or "").strip(),
                    }
                )

            got_page2 = True
            break

        if not got_page2:
            print(f"Page2 not available for {clean_id} (tried {startref_candidates})")

    time.sleep(delay)
    return out

def extract_into_out(refs, out, seen):
    for ref in refs:
        ref_info = (ref.get("ref-info") or {}).get("ref-publicationinfo") or {}
        title = ref_info.get("title", "") or ""
        doi = ref_info.get("doi", "") or ""
        sid = (ref.get("scopus-id") or "").strip()

        key = (sid, doi, title.lower().strip())
        if key in seen:
            continue

        seen.add(key)
        out.append({
            "title": title,
            "doi": doi,
            "scopus_id": sid,
        })


def fetch_references(scopus_id: str, api_key: str, retries: int = 3, delay: float = 1.0, page_size: int = 40):
    clean_id = clean_scopus_id(scopus_id)
    if not clean_id:
        return []

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
    #params1 = {"view": "REF", "startref": 1, "refcount": page_size}
    params1 = {"view": "REF"}
    #params1 = {"view": "REF", "startref": 1}

    resp1 = None
    for attempt in range(1, retries + 1):
        resp1 = requests.get(base_url, headers=headers, params=params1, timeout=30)
        if resp1.status_code == 200:
            break
        if resp1.status_code == 429:
            retry_after = resp1.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else 10 * attempt)
            continue
        time.sleep(5)

    if resp1 is None or resp1.status_code != 200:
        print(f"Failed page 1 for {clean_id}")
        return []

    data1 = resp1.json()
    refs1_raw = (
        data1.get("abstracts-retrieval-response", {})
             .get("references", {})
             .get("reference")
    )
    refs1 = normalize_reference_list(refs1_raw)
    extract_into_out(refs1, out, seen)
    time.sleep(delay)

    # If fewer than page_size = 40, all references have been fetched
    if len(refs1) < page_size:
        return out

    # =========================================================
    # PART 2 — Specialized algorithm:
    # fetch ALL remaining refs safely (no refcount),
    # then locally exclude the last
    # =========================================================
    tail_refs = []

    
    tail_startref = page_size + 1
    while True:

        params_tail = {"view": "REF", "startref": tail_startref}
        resp_tail = requests.get(base_url, headers=headers, params=params_tail, timeout=30)

        if resp_tail.status_code == 200:
            data_tail = resp_tail.json()
            tail_raw = (
                data_tail.get("abstracts-retrieval-response", {})
                            .get("references", {})
                            .get("reference")
            )
            tail_refs = normalize_reference_list(tail_raw)
            
            #if tail_refs:
            #    break
            # stop condition
            if len(tail_refs) < page_size:
                print(f"stop condition met at tail_startref={tail_startref} with {len(tail_refs)} refs")
                # Add to out
                extract_into_out(tail_refs, out, seen)
                break

            # Add to out
            print(f"Adding {len(tail_refs)} refs from tail_startref={tail_startref}")
            extract_into_out(tail_refs, out, seen)
            
            # prepare for next
            tail_startref += page_size
            time.sleep(delay)

        elif resp_tail.status_code == 429:
            print(f"Rate-limited (429) for {clean_id} tail_startref={tail_startref}; sleeping 10s")
            time.sleep(10)
        else:
            print(f"Error {resp_tail.status_code} for {clean_id} tail_startref={tail_startref}; stopping")
            break
            
    #if not tail_refs:
    #    return out

    # Exclude last locally
    #rest_excluding_last = tail_refs[:-1]
    #extract_into_out(tail_refs, out, seen)
    #time.sleep(delay)

    # =========================================================
    # PART 3 — Last reference trick (only if needed)
    # =========================================================
    """
    last_ref = tail_refs[-1]
    before_len = len(out)
    extract_into_out([last_ref], out, seen)

    if len(out) > before_len:
        return out  # last was successfully added

    # Fallback: explicit last-index trick
    total_refs_guess = page_size + len(tail_refs)
    for last_startref in (total_refs_guess, total_refs_guess + 1):
        params_last = {"view": "REF", "startref": last_startref}
        resp_last = requests.get(base_url, headers=headers, params=params_last, timeout=30)

        if resp_last.status_code != 200:
            continue

        data_last = resp_last.json()
        last_raw = (
            data_last.get("abstracts-retrieval-response", {})
                     .get("references", {})
                     .get("reference")
        )
        last_refs = normalize_reference_list(last_raw)
        if last_refs:
            extract_into_out([last_refs[-1]], out, seen)
            break
    """
    return out




def main():
    api_key = os.getenv("SCOPUS_API_KEY")
    if not api_key:
        raise RuntimeError("Missing SCOPUS_API_KEY env var")
    
    config, repo_root = load_paths_config()
    defaults = config["defaults"]["fetch_references_backward"]
    input = resolve_from_root(repo_root, defaults["input_json"])
    output = resolve_from_root(repo_root, defaults["output_json"])
    delay = 1.0
    retries = 3

    with open(input, "r", encoding="utf-8") as f:
        papers = json.load(f)

    results = {}
    total = len(papers)
    print(f"Loaded {total} papers from {input}")

    for idx, paper in enumerate(papers, start=1):
        sid = paper.get("scopus_id", "")
        clean_id = clean_scopus_id(sid)
        if not clean_id:
            continue

        print(f"[{idx}/{total}] Fetching references for {clean_id}")
        refs = fetch_references(
            scopus_id=sid,
            api_key=api_key,
            retries=retries,
            delay=delay,
        )
        #results[clean_id] = refs
        results[paper.get("key_id", "")] = {
            "key_id": paper.get("key_id", ""),
            "title": paper.get("Title", ""),
            "year": paper.get("Year", ""),
            "doi": paper.get("doi", ""),
            "scopus_id": clean_id,
            "references": refs,
        }
        print(f"  Saved {len(refs)} refs")

        with open(output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Done. Wrote {len(results)} source papers to {output}")



if __name__ == "__main__":
    main()