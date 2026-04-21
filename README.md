# HMLV Survey

This repository contains material for the HMLV survey project, including a React app in `citations-server` for browsing and analyzing the paper dataset.

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
