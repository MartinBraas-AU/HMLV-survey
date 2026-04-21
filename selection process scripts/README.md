# HMLV Selection Process Scripts

Academic survey link placeholder: TBD

Replace with publication URL/DOI when available.

This repository contains the scripts used in the PRISMA workflow for
the academic systematic literature review. It supports:

- Rule-based relevance screening (PRISMA screening support)
- Backward snowballing (references cited by included papers)
- Forward snowballing (papers citing included papers)
- Basic analysis of citation and reference connectivity

## Survey objective

This Systematic Literature Review (SLR) maps the current state of decision
support in high-mix low-volume (HMLV) manufacturing across four dimensions:
drivers behind existing approaches, objectives pursued, technologies/methods
used, and how effects are evaluated.

In short, the review aims to:

- Outline current decision support approaches and key problem characteristics
- Provide an overview of support areas across manufacturing levels
- Identify the most widely used technologies and methods
- Highlight research gaps in current approaches

## Research metadata placeholders

Fill this section when preparing manuscript/repository release.

- DOI placeholder: `TBD`
- BibTeX reference placeholder: `TBD`
- Citation text placeholder: `TBD`
- Publication venue placeholder: `TBD`
- Publication year placeholder: `TBD`
- Project page / dataset URL placeholder: `TBD`
- Funding / grant info placeholder: `TBD`
- Contact author placeholder: `TBD`
- Research type notes placeholder: `TBD` (for example SLR, mapping study,
  meta-analysis)
- PRISMA registration / protocol placeholder: `TBD`
- Search date range placeholder: `TBD`
- Inclusion criteria summary placeholder: `TBD`
- Exclusion criteria summary placeholder: `TBD`

## Intended users

- Researchers running systematic literature reviews
- Practitioners performing evidence mapping in a structured way
- Peer reviewers who need visibility into the scripts used in the PRISMA selection process

## Workflow overview

The pipeline is designed to align with PRISMA-style filtering and snowballing:

1. Import query results (CSV)
2. Score relevance with transparent rule-based filters
3. Convert scored output to JSON with stable `key_id`
4. Run backward snowballing on included papers
5. Run forward snowballing on included papers
6. Analyze highly connected papers from forward and backward results

## Project structure

- `data/`: raw query exports (for example Scopus CSV)
- `results/`: filtered datasets and snowballing outputs
- `citers/`: forward citation outputs
- `scripts/`: main processing scripts
- `scripts/snowball/backward/`: backward snowballing and analysis
- `scripts/snowball/forward/`: forward snowballing and analysis
- `paths.txt`: human-readable list of key files and paths
- `paths.json`: machine-readable config used by scripts at runtime

## Requirements

- Python 3.10+
- packages used by scripts: `pandas`, `requests`, `matplotlib`, `openpyxl`, `numpy`
- Scopus API key for fetch scripts

Set API key before running API-backed scripts.

PowerShell example:

```powershell
$env:SCOPUS_API_KEY = "your_key_here"
```

## Quick start

Run these commands from the selection process scripts folder.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pandas requests matplotlib openpyxl numpy
python scripts/relevance_score.py
```

## Configuration

Scripts read runtime paths and defaults from `paths.json`.

- update file paths in `paths.json` when input/output filenames change
- update per-script defaults under `defaults` in `paths.json`
- keep `paths.txt` as human-facing documentation only

## Script map

Core processing:

- `scripts/relevance_score.py`
  - scores papers into relevance levels using explicit regex/rule logic
  - writes scored output to `results/`
- `scripts/scored_csv_to_json.py`
  - converts scored CSV into JSON with `key_id`
- `scripts/fetch_citing_papers.py`
  - fetches citing papers for main forward pass
  - includes comments showing path for failed-only vs non-failed inputs

Forward snowballing:

- `scripts/snowball/forward/fetch_citing_papers_level.py`
  - fetches citing papers for selected level-filtered sets
- `scripts/snowball/forward/citing_papers_analysis.py`
  - computes and prints citation-connectivity summaries
  - supports threshold-based subset selection

Backward snowballing:

- `scripts/snowball/backward/fetch_references_backward.py`
  - fetches references for included papers
- `scripts/snowball/backward/remove_excluded.py`
  - removes references linked to excluded papers
- `scripts/snowball/backward/keep_level_papers.py`
  - keeps references tied to selected level sets
- `scripts/snowball/backward/fetch_info_refferences.py`
  - enriches references with metadata from API
- `scripts/snowball/backward/fetch_info_refferences_level.py`
  - enriches level-specific reference sets
- `scripts/snowball/backward/references_analysis.py`
  - counts and reports highly referenced papers

## Recommended run sequence

Run from the selection process scripts folder so relative paths resolve as expected.

```powershell
python scripts/relevance_score.py
python scripts/scored_csv_to_json.py
python scripts/snowball/backward/fetch_references_backward.py
python scripts/snowball/backward/remove_excluded.py
python scripts/snowball/backward/keep_level_papers.py
python scripts/fetch_citing_papers.py
python scripts/snowball/forward/fetch_citing_papers_level.py
python scripts/snowball/backward/references_analysis.py
python scripts/snowball/forward/citing_papers_analysis.py
```

## Reproducibility notes

- scripts resolve runtime input/output paths from `paths.json`
- keep the repository folder structure unchanged unless you update `paths.json`
- preserve intermediate outputs in `results/` and `citers/` for auditability
- document any threshold changes used for selection and reporting

## Adapting to another domain

To reuse this workflow for another review topic:

1. replace your source CSV in `data/`
2. adjust rule patterns and thresholds in `scripts/relevance_score.py`
3. update output filenames in script `__main__` blocks for your study label/year
4. rerun the pipeline from relevance scoring onward

## Output interpretation

- Forward analysis highlights papers that cite multiple papers from your review set
- Backward analysis highlights papers repeatedly referenced across included papers
- Both are indicators of connectivity and influence, not quality by themselves

## File index

See `paths.txt` for a human-readable file index and `paths.json` for runtime
script configuration.

## Citation

Use this placeholder section until publication metadata is finalized.

- BibTeX:

```bibtex
@article{TBD,
  title   = {TBD},
  author  = {TBD},
  journal = {TBD},
  year    = {TBD},
  doi     = {TBD}
}
```

- In-text citation placeholder: `TBD`

## Contributing

Placeholder: `TBD`.

Suggested minimum contribution process:

1. Open an issue describing the change.
2. Keep script behavior reproducible and path updates in `paths.json`.
3. Update README and `paths.txt` when workflow changes.

## License

Placeholder: `TBD`.
