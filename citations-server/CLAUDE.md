# Citations Server — HMLV Survey Browser

## Overview

A React + Vite app for browsing 205 papers from a systematic literature review on HMLV manufacturing decision support systems. Navigation: Level (L0–L3) → DSS Focus → Papers → Paper Detail.

An overview of the included papers and extracted data is provided in \surveydata.
The interactive interface enables researchers and practitioners to explore the corpus of papers across manufacturing levels, with filtering by decision area, year, technologies and methods, and manufacturing level.

## Manufacturing Levels

- L0: Process
- L1: Line / Cell
- L2: Factory
- L3: Enterprise / Supply Chain

## Planned Improvements

### 1. Search & Filtering

- [x] Global search bar (search by title, author/bibtexKey, DOI, technology, method)
- [x] Filter chips on paper list pages (by year range, country, technology, evaluation setting)
- [x] Combine filters with the existing level/focus navigation

### 2. Visualizations & Dashboard (interactive versions of Python figures)

All charts should be interactive: hover for tooltips, click to filter/navigate to paper list.

- [x] **Publication timeline + level distribution** (fig 01+02) — stacked bar chart by level with hatch pattern, matching paper palette
- [x] **Country distribution** (fig 03) — horizontal bar chart, sorted by count
- [ ] **Country choropleth map** (fig 03b) — interactive world map with hover counts
- [x] **Technology landscape** (fig 04) — horizontal bar chart of technologies (≥2)
- [x] **Methods & tech word cloud** (fig 04c) — interactive word cloud
- [x] **DSS focus pie chart** (fig 05) — grouped categories with percentages
- [x] **Evaluation setting** (fig 07) — bar chart (simulation, static eval, lab, industrial)
- [x] **Data source** (fig 08) — horizontal bar chart (synthetic, industrial, benchmark, etc.)
- [x] **Snowball source** (fig 09) — pie chart (database search vs snowball)
- [x] **Industry distribution** (fig 10) — pie chart (includes "Not specified")

### 3. Cross-cutting Views

- [x] Browse by technology (e.g. show all DT papers across all levels)
- [x] Browse by country
- [ ] Browse by country — geographic map view
- [x] Browse by year
- [x] "Related papers" on paper detail (same technologies or methods)

### 4. Paper Detail Enhancements *

- [ ] Copy BibTeX citation to clipboard
- [ ] Export selected papers as .bib file
- [ ] Link to Google Scholar search for the paper title
- [ ] Abstract field (if data becomes available)

### 5. Table Improvements

- [x] Sortable columns (click header to sort by year, title, country, etc.)
- [ ] Column visibility toggle (show/hide columns)
- [ ] Pagination or virtual scrolling for large lists
- [ ] CSV/JSON export of current filtered view *

### 6. UI/UX Polish *

- [ ] Dark mode toggle
- [ ] Improved mobile layout for paper tables (card view on small screens)
- [ ] Keyboard navigation support
- [ ] Loading states and transitions between pages
- [ ] Sticky header with search always accessible

### 7. Data Quality *

- [ ] Flag/highlight snowball papers distinct
- [ ] Show paper count badges in breadcrumb navigation
- [ ] Indicate when a DSS focus area only exists at certain levels
