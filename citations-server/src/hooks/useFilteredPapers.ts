import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import type { Paper } from "../types";
import { getDSSFocusGroup, getIndustryGroup, normalizeDataSource } from "../utils/groupings";

export interface Filters {
  q: string;
  years: Set<number>;
  countries: Set<string>;
  technologies: Set<string>;
  evaluationSettings: Set<string>;
  industries: Set<string>;
  dssFocusGroups: Set<string>;
  dataSources: Set<string>;
  snowball: boolean | null;
}

export function parseFilters(searchParams: URLSearchParams): Filters {
  const snowballParam = searchParams.get("snowball");
  return {
    q: searchParams.get("q") ?? "",
    years: new Set(
      (searchParams.get("years") ?? "")
        .split(",")
        .filter(Boolean)
        .map(Number)
    ),
    countries: new Set(
      (searchParams.get("countries") ?? "").split(",").filter(Boolean)
    ),
    technologies: new Set(
      (searchParams.get("technologies") ?? "").split(",").filter(Boolean)
    ),
    evaluationSettings: new Set(
      (searchParams.get("eval") ?? "").split(",").filter(Boolean)
    ),
    industries: new Set(
      (searchParams.get("industry") ?? "").split(",").filter(Boolean)
    ),
    dssFocusGroups: new Set(
      (searchParams.get("dssFocus") ?? "").split(",").filter(Boolean)
    ),
    dataSources: new Set(
      (searchParams.get("dataSource") ?? "").split(",").filter(Boolean)
    ),
    snowball: snowballParam === "yes" ? true : snowballParam === "no" ? false : null,
  };
}

function matchesSearch(paper: Paper, q: string): boolean {
  if (!q) return true;
  const terms = q.toLowerCase().split(/\s+/);
  const haystack = [
    paper.title,
    paper.bibtexKey,
    paper.doi,
    paper.country,
    paper.industry,
    paper.manufacturingLevel,
    paper.dssFocus,
    paper.evaluationSetting,
    paper.dataSource,
    paper.metrics,
    paper.jobShopVariation ?? "",
    ...paper.technologies,
    ...paper.methods,
  ]
    .join(" ")
    .toLowerCase();

  return terms.every((term) => haystack.includes(term));
}

function matchesFilters(paper: Paper, filters: Filters): boolean {
  if (filters.years.size > 0 && !filters.years.has(paper.year)) return false;
  if (filters.countries.size > 0 && !filters.countries.has(paper.country))
    return false;
  if (
    filters.technologies.size > 0 &&
    !paper.technologies.some((t) => filters.technologies.has(t))
  )
    return false;
  if (
    filters.evaluationSettings.size > 0 &&
    !filters.evaluationSettings.has(paper.evaluationSetting)
  )
    return false;
  if (
    filters.industries.size > 0 &&
    !filters.industries.has(getIndustryGroup(paper.industry))
  )
    return false;
  if (
    filters.dssFocusGroups.size > 0 &&
    !filters.dssFocusGroups.has(getDSSFocusGroup(paper.dssFocus))
  )
    return false;
  if (
    filters.dataSources.size > 0 &&
    !filters.dataSources.has(normalizeDataSource(paper.dataSource))
  )
    return false;
  if (filters.snowball !== null && paper.snowball !== filters.snowball)
    return false;
  return true;
}

export function filterPapers(papers: Paper[], filters: Filters): Paper[] {
  return papers.filter(
    (p) => matchesSearch(p, filters.q) && matchesFilters(p, filters)
  );
}

export function useFilteredPapers(papers: Paper[]) {
  const [searchParams, setSearchParams] = useSearchParams();
  const filters = useMemo(() => parseFilters(searchParams), [searchParams]);

  const filtered = useMemo(
    () => filterPapers(papers, filters),
    [papers, filters]
  );

  function toggleFilter(
    key: "years" | "countries" | "technologies" | "eval" | "industry" | "dssFocus" | "dataSource",
    value: string
  ) {
    const params = new URLSearchParams(searchParams);
    const current = (params.get(key) ?? "").split(",").filter(Boolean);
    const idx = current.indexOf(value);
    if (idx >= 0) {
      current.splice(idx, 1);
    } else {
      current.push(value);
    }
    if (current.length > 0) {
      params.set(key, current.join(","));
    } else {
      params.delete(key);
    }
    setSearchParams(params, { replace: true });
  }

  function clearFilters() {
    const params = new URLSearchParams();
    const q = searchParams.get("q");
    if (q) params.set("q", q);
    setSearchParams(params, { replace: true });
  }

  const hasActiveFilters =
    filters.years.size > 0 ||
    filters.countries.size > 0 ||
    filters.technologies.size > 0 ||
    filters.evaluationSettings.size > 0 ||
    filters.industries.size > 0 ||
    filters.dssFocusGroups.size > 0 ||
    filters.dataSources.size > 0 ||
    filters.snowball !== null;

  return { filters, filtered, toggleFilter, clearFilters, hasActiveFilters };
}
