import { useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import type { Paper } from "../types";
import { Breadcrumb } from "../components/Breadcrumb";
import { FilterBar } from "../components/FilterBar";
import { useFilteredPapers } from "../hooks/useFilteredPapers";

type SortKey = "title" | "year" | "country" | "technologies" | "methods";
type SortDir = "asc" | "desc";

function comparePapers(a: Paper, b: Paper, key: SortKey, dir: SortDir): number {
  let cmp = 0;
  switch (key) {
    case "title":
      cmp = a.title.localeCompare(b.title);
      break;
    case "year":
      cmp = a.year - b.year;
      break;
    case "country":
      cmp = a.country.localeCompare(b.country);
      break;
    case "technologies":
      cmp = a.technologies.join(", ").localeCompare(b.technologies.join(", "));
      break;
    case "methods":
      cmp = a.methods.join(", ").localeCompare(b.methods.join(", "));
      break;
  }
  return dir === "asc" ? cmp : -cmp;
}

export function PaperTable({ papers }: { papers: Paper[] }) {
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
    <table className="paper-table">
      <thead>
        <tr>
          <th className="sortable-th" onClick={() => handleSort("title")}>
            Title{sortIndicator("title")}
          </th>
          <th className="sortable-th" onClick={() => handleSort("year")}>
            Year{sortIndicator("year")}
          </th>
          <th className="sortable-th" onClick={() => handleSort("country")}>
            Country{sortIndicator("country")}
          </th>
          <th className="sortable-th" onClick={() => handleSort("technologies")}>
            Technologies{sortIndicator("technologies")}
          </th>
          <th className="sortable-th" onClick={() => handleSort("methods")}>
            Methods{sortIndicator("methods")}
          </th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((paper) => (
          <tr key={paper.id}>
            <td>
              <Link to={`/paper/${paper.id}`}>{paper.title}</Link>
            </td>
            <td>{paper.year}</td>
            <td>{paper.country}</td>
            <td>{paper.technologies.join(", ")}</td>
            <td>{paper.methods.join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function PaperList({ papers }: { papers: Paper[] }) {
  const { level, focus } = useParams<{ level: string; focus: string }>();
  const isAllLevel = level === "all";
  const isAllFocus = focus === "all";

  const preFiltered = useMemo(() => {
    let result = papers;
    if (!isAllLevel) result = result.filter((p) => p.manufacturingLevel === level);
    if (!isAllFocus) result = result.filter((p) => p.dssFocus === focus);
    return result;
  }, [papers, level, focus, isAllLevel, isAllFocus]);

  const { filters, filtered, toggleFilter, clearFilters, hasActiveFilters } =
    useFilteredPapers(preFiltered);

  const levelLabel = isAllLevel ? "All Levels" : level!;
  const focusLabel = isAllFocus ? "All DSS Focus Areas" : focus!;

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: levelLabel, to: `/level/${encodeURIComponent(level!)}` },
          ...(focus?.toLowerCase() === "scheduling" && !isAllFocus
            ? [
                {
                  label: focusLabel,
                  to: `/level/${encodeURIComponent(level!)}/focus/${encodeURIComponent(focus!)}`,
                },
              ]
            : []),
          { label: isAllFocus ? focusLabel : `${focusLabel} — Papers` },
        ]}
      />
      <h1>{focusLabel}</h1>
      <p className="subtitle">
        {filtered.length}{hasActiveFilters ? ` of ${preFiltered.length}` : ""} papers
      </p>

      <FilterBar
        papers={preFiltered}
        filters={filters}
        toggleFilter={toggleFilter}
        clearFilters={clearFilters}
        hasActiveFilters={hasActiveFilters}
      />

      <PaperTable papers={filtered} />
    </div>
  );
}
