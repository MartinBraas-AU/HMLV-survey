# HMLV Survey

This repository contains material for the HMLV survey project, including the survey article itself "A Survey on Decision Support in High‑Mix Low‑Volume Manufacturing" and its supporting materials. It includes the `citations-server` React app for browsing and visualizing the paper dataset, the master sheet (`data/Master sheet.xlsx`), analysis outputs, and the figures used in the article.

**Cite this paper**

If you use the survey article, the interactive overview, the paper corpus, or the associated data in academic research, please cite the survey article. The citation below currently refers to the preprint placeholder and will be updated with journal publication details when available.

BibTeX (journal placeholder):

```
@article{hmlv_dss_survey_placeholder,
	title = {A Survey on Decision Support in High-Mix Low-Volume Manufacturing},
	author = {Author, First and Author, Second},
	journal = {Journal Name},
	year = {2026},
	note = {Manuscript in preparation}
}
```

BibTeX (arXiv / preprint placeholder):

```
@article{hmlv_dss_survey_placeholder,
	title = {A Survey on Decision Support in High-Mix Low-Volume Manufacturing},
	author = {Author, First and Author, Second},
	journal = {Arxiv preprint},
	year = {2026},
	note = {Manuscript in preparation}
}
```

## Run `citations-server`

### Prerequisites

- Node.js 20+ (LTS recommended)
- npm (comes with Node.js)

### 1) Open a terminal in the project root

From this folder:

`HMLV-survey`

### 2) Install dependencies

```bash
cd citations-server
npm install
```

### 3) Start the development server

```bash
npm run dev
```

This command first builds `citations-server/src/data/papers.json` from:

`data/Master sheet.xlsx` (sheet name: `Cleaned Master sheet`)

Then it starts Vite.

### 4) Open in browser

Vite will print a local URL, typically:

`http://localhost:5173`

## Other useful commands

### Rebuild only the generated JSON data

```bash
npm run build:data
```

### Production build

```bash
npm run build
```

### Preview production build locally

```bash
npm run preview
```

## Common issue

If startup fails with a message about missing sheet data, verify:

- The file exists at `data/Master sheet.xlsx`
- The workbook contains a sheet named `Cleaned Master sheet`
