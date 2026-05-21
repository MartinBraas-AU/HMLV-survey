import { useMemo, useState } from "react";
import type { RelevantPaper } from "../types";
import { Breadcrumb } from "../components/Breadcrumb";

type SortKey = "title" | "year" | "automatedManufacturingLevel" | "dssFocus";
type SortDir = "asc" | "desc";

function comparePapers(a: RelevantPaper, b: RelevantPaper, key: SortKey, dir: SortDir): number {
  let cmp = 0;
  switch (key) {
    case "title":
      cmp = a.title.localeCompare(b.title);
      break;
    case "year":
      cmp = a.year - b.year;
      break;
    case "automatedManufacturingLevel":
      cmp = a.automatedManufacturingLevel.localeCompare(b.automatedManufacturingLevel);
      break;
    case "dssFocus":
      cmp = a.dssFocus.localeCompare(b.dssFocus);
      break;
  }
  return dir === "asc" ? cmp : -cmp;
}

export function RelevantPapers({ papers }: { papers: RelevantPaper[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("year");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const sorted = useMemo(
    () => [...papers].sort((a, b) => comparePapers(a, b, sortKey, sortDir)),
    [papers, sortKey, sortDir]
  );

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir(key === "year" ? "desc" : "asc");
    }
  }

  function sortIndicator(key: SortKey) {
    if (sortKey !== key) return " ↕";
    return sortDir === "asc" ? " ↑" : " ↓";
  }

  return (
    <div className="page">
      <Breadcrumb crumbs={[{ label: "Levels", to: "/" }, { label: "Possibly Relevant Papers" }]} />
      <h1>Possibly Relevant Papers</h1>
      <p className="subtitle">
        {papers.length} papers from the workbook sheet marked for possible review.
      </p>

      <table className="paper-table relevant-paper-table">
        <thead>
          <tr>
            <th className="sortable-th" onClick={() => handleSort("title")}>
              Title{sortIndicator("title")}
            </th>
            <th className="sortable-th" onClick={() => handleSort("year")}>
              Year{sortIndicator("year")}
            </th>
            <th className="sortable-th" onClick={() => handleSort("automatedManufacturingLevel")}>
              Level{sortIndicator("automatedManufacturingLevel")}
            </th>
            <th className="sortable-th" onClick={() => handleSort("dssFocus")}>
              DSS Focus{sortIndicator("dssFocus")}
            </th>
            <th>Technologies</th>
            <th>Methods</th>
            <th>Score</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((paper) => (
            <tr key={paper.id}>
              <td>
                {paper.doi ? (
                  <a href={paper.doi} target="_blank" rel="noreferrer">
                    {paper.title}
                  </a>
                ) : (
                  paper.title
                )}
              </td>
              <td>{paper.year || ""}</td>
              <td>{paper.automatedManufacturingLevel}</td>
              <td>{paper.dssFocus}</td>
              <td>{paper.technologies.join(", ")}</td>
              <td>{paper.methods.join(", ")}</td>
              <td>{paper.relevanceScore}</td>
              <td>
                <div>{paper.reasoning}</div>
                {paper.negativesFound && paper.negativesFound !== "None" ? (
                  <div className="related-meta">{paper.negativesFound}</div>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
