import type { Paper } from "../types";
import { Breadcrumb } from "../components/Breadcrumb";
import { FilterBar } from "../components/FilterBar";
import { PaperTable } from "./PaperList";
import { useFilteredPapers } from "../hooks/useFilteredPapers";

export function SearchResults({ papers }: { papers: Paper[] }) {
  const { filters, filtered, toggleFilter, clearFilters, hasActiveFilters } =
    useFilteredPapers(papers);

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: filters.q ? `Search: "${filters.q}"` : "Search" },
        ]}
      />
      <h1>
        {filters.q ? (
          <>
            Results for &ldquo;{filters.q}&rdquo;
          </>
        ) : (
          "Search"
        )}
      </h1>
      <p className="subtitle">{filtered.length} papers found</p>

      <FilterBar
        papers={papers}
        filters={filters}
        toggleFilter={toggleFilter}
        clearFilters={clearFilters}
        hasActiveFilters={hasActiveFilters}
      />

      {filtered.length > 0 ? (
        <PaperTable papers={filtered} />
      ) : (
        <p className="no-results">
          No papers match your search. Try different keywords or clear some
          filters.
        </p>
      )}
    </div>
  );
}
