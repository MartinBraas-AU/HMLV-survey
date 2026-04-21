import { useMemo } from "react";
import { useParams } from "react-router-dom";
import type { Paper } from "../types";
import { Breadcrumb } from "../components/Breadcrumb";
import { CategoryCard } from "../components/CategoryCard";
import { FilterBar } from "../components/FilterBar";
import { PaperTable } from "./PaperList";
import { useFilteredPapers } from "../hooks/useFilteredPapers";
import { countMulti } from "../utils/groupings";

// Browse by Technology — list all technologies
export function TechnologyIndex({ papers }: { papers: Paper[] }) {
  const techs = useMemo(() => countMulti(papers, "technologies"), [papers]);

  return (
    <div className="page">
      <Breadcrumb crumbs={[{ label: "Levels", to: "/" }, { label: "Technologies" }]} />
      <h1>Browse by Technology</h1>
      <p className="subtitle">{techs.length} technologies across {papers.length} papers</p>
      <div className="card-grid">
        {techs.map(({ name, count }) => (
          <CategoryCard
            key={name}
            label={name}
            count={count}
            to={`/technology/${encodeURIComponent(name)}`}
          />
        ))}
      </div>
    </div>
  );
}

// Papers for a specific technology
export function TechnologyPapers({ papers }: { papers: Paper[] }) {
  const { tech } = useParams<{ tech: string }>();
  const preFiltered = useMemo(
    () => papers.filter((p) => p.technologies.includes(tech!)),
    [papers, tech]
  );
  const { filters, filtered, toggleFilter, clearFilters, hasActiveFilters } =
    useFilteredPapers(preFiltered);

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: "Technologies", to: "/technology" },
          { label: tech! },
        ]}
      />
      <h1>{tech}</h1>
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

// Browse by Country — list all countries
export function CountryIndex({ papers }: { papers: Paper[] }) {
  const countries = useMemo(() => {
    const map = new Map<string, number>();
    for (const p of papers) map.set(p.country, (map.get(p.country) ?? 0) + 1);
    return [...map.entries()]
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);
  }, [papers]);

  return (
    <div className="page">
      <Breadcrumb crumbs={[{ label: "Levels", to: "/" }, { label: "Countries" }]} />
      <h1>Browse by Country</h1>
      <p className="subtitle">{countries.length} countries</p>
      <div className="card-grid">
        {countries.map(({ name, count }) => (
          <CategoryCard
            key={name}
            label={name}
            count={count}
            to={`/country/${encodeURIComponent(name)}`}
          />
        ))}
      </div>
    </div>
  );
}

// Papers for a specific country
export function CountryPapers({ papers }: { papers: Paper[] }) {
  const { country } = useParams<{ country: string }>();
  const preFiltered = useMemo(
    () => papers.filter((p) => p.country === country),
    [papers, country]
  );
  const { filters, filtered, toggleFilter, clearFilters, hasActiveFilters } =
    useFilteredPapers(preFiltered);

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: "Countries", to: "/country" },
          { label: country! },
        ]}
      />
      <h1>{country}</h1>
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

// Browse by Year — list all years
export function YearIndex({ papers }: { papers: Paper[] }) {
  const years = useMemo(() => {
    const map = new Map<number, number>();
    for (const p of papers) map.set(p.year, (map.get(p.year) ?? 0) + 1);
    return [...map.entries()]
      .map(([year, count]) => ({ year, count }))
      .sort((a, b) => b.year - a.year);
  }, [papers]);

  return (
    <div className="page">
      <Breadcrumb crumbs={[{ label: "Levels", to: "/" }, { label: "Years" }]} />
      <h1>Browse by Year</h1>
      <p className="subtitle">{years.length} publication years</p>
      <div className="card-grid">
        {years.map(({ year, count }) => (
          <CategoryCard
            key={year}
            label={String(year)}
            count={count}
            to={`/year/${year}`}
          />
        ))}
      </div>
    </div>
  );
}

// Papers for a specific year
export function YearPapers({ papers }: { papers: Paper[] }) {
  const { year } = useParams<{ year: string }>();
  const yearNum = Number(year);
  const preFiltered = useMemo(
    () => papers.filter((p) => p.year === yearNum),
    [papers, yearNum]
  );
  const { filters, filtered, toggleFilter, clearFilters, hasActiveFilters } =
    useFilteredPapers(preFiltered);

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: "Years", to: "/year" },
          { label: year! },
        ]}
      />
      <h1>{year}</h1>
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
