import { useMemo, useState } from "react";
import type { Paper } from "../types";
import type { Filters } from "../hooks/useFilteredPapers";

interface FilterBarProps {
  papers: Paper[];
  filters: Filters;
  toggleFilter: (key: "years" | "countries" | "technologies" | "eval", value: string) => void;
  clearFilters: () => void;
  hasActiveFilters: boolean;
}

type FilterSection = "years" | "countries" | "technologies" | "eval";

export function FilterBar({
  papers,
  filters,
  toggleFilter,
  clearFilters,
  hasActiveFilters,
}: FilterBarProps) {
  const [expanded, setExpanded] = useState<FilterSection | null>(null);

  const options = useMemo(() => {
    const years = new Map<number, number>();
    const countries = new Map<string, number>();
    const technologies = new Map<string, number>();
    const evalSettings = new Map<string, number>();

    for (const p of papers) {
      years.set(p.year, (years.get(p.year) ?? 0) + 1);
      countries.set(p.country, (countries.get(p.country) ?? 0) + 1);
      for (const t of p.technologies) {
        technologies.set(t, (technologies.get(t) ?? 0) + 1);
      }
      evalSettings.set(
        p.evaluationSetting,
        (evalSettings.get(p.evaluationSetting) ?? 0) + 1
      );
    }

    return {
      years: [...years.entries()].sort((a, b) => b[0] - a[0]),
      countries: [...countries.entries()].sort((a, b) => b[1] - a[1]),
      technologies: [...technologies.entries()].sort((a, b) => b[1] - a[1]),
      evalSettings: [...evalSettings.entries()].sort((a, b) => b[1] - a[1]),
    };
  }, [papers]);

  function toggle(section: FilterSection) {
    setExpanded(expanded === section ? null : section);
  }

  return (
    <div className="filter-bar">
      <div className="filter-buttons">
        <FilterButton
          label="Year"
          active={filters.years.size > 0}
          count={filters.years.size}
          onClick={() => toggle("years")}
          isExpanded={expanded === "years"}
        />
        <FilterButton
          label="Country"
          active={filters.countries.size > 0}
          count={filters.countries.size}
          onClick={() => toggle("countries")}
          isExpanded={expanded === "countries"}
        />
        <FilterButton
          label="Technology"
          active={filters.technologies.size > 0}
          count={filters.technologies.size}
          onClick={() => toggle("technologies")}
          isExpanded={expanded === "technologies"}
        />
        <FilterButton
          label="Evaluation"
          active={filters.evaluationSettings.size > 0}
          count={filters.evaluationSettings.size}
          onClick={() => toggle("eval")}
          isExpanded={expanded === "eval"}
        />
        {hasActiveFilters && (
          <button className="filter-clear" onClick={clearFilters}>
            Clear all
          </button>
        )}
      </div>

      {expanded === "years" && (
        <FilterChipList
          items={options.years.map(([y, c]) => ({
            value: String(y),
            label: String(y),
            count: c,
          }))}
          selected={new Set([...filters.years].map(String))}
          onToggle={(v) => toggleFilter("years", v)}
        />
      )}
      {expanded === "countries" && (
        <FilterChipList
          items={options.countries.map(([name, c]) => ({
            value: name,
            label: name,
            count: c,
          }))}
          selected={filters.countries}
          onToggle={(v) => toggleFilter("countries", v)}
        />
      )}
      {expanded === "technologies" && (
        <FilterChipList
          items={options.technologies.map(([name, c]) => ({
            value: name,
            label: name,
            count: c,
          }))}
          selected={filters.technologies}
          onToggle={(v) => toggleFilter("technologies", v)}
        />
      )}
      {expanded === "eval" && (
        <FilterChipList
          items={options.evalSettings.map(([name, c]) => ({
            value: name,
            label: name,
            count: c,
          }))}
          selected={filters.evaluationSettings}
          onToggle={(v) => toggleFilter("eval", v)}
        />
      )}
    </div>
  );
}

function FilterButton({
  label,
  active,
  count,
  onClick,
  isExpanded,
}: {
  label: string;
  active: boolean;
  count: number;
  onClick: () => void;
  isExpanded: boolean;
}) {
  return (
    <button
      className={`filter-btn ${active ? "filter-btn--active" : ""} ${isExpanded ? "filter-btn--expanded" : ""}`}
      onClick={onClick}
    >
      {label}
      {count > 0 && <span className="filter-btn-count">{count}</span>}
    </button>
  );
}

function FilterChipList({
  items,
  selected,
  onToggle,
}: {
  items: { value: string; label: string; count: number }[];
  selected: Set<string>;
  onToggle: (value: string) => void;
}) {
  return (
    <div className="filter-chips">
      {items.map((item) => (
        <button
          key={item.value}
          className={`filter-chip ${selected.has(item.value) ? "filter-chip--selected" : ""}`}
          onClick={() => onToggle(item.value)}
        >
          {item.label}
          <span className="filter-chip-count">{item.count}</span>
        </button>
      ))}
    </div>
  );
}
