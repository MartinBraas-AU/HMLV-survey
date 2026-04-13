import { useMemo } from "react";
import { useParams } from "react-router-dom";
import type { Paper } from "../types";
import { papersByDSSFocus, sortedEntries } from "../utils/normalize";
import { CategoryCard } from "../components/CategoryCard";
import { Breadcrumb } from "../components/Breadcrumb";

export function DSSFocusSelect({ papers }: { papers: Paper[] }) {
  const { level } = useParams<{ level: string }>();
  const isAll = level === "all";

  const filtered = useMemo(
    () => (isAll ? papers : papers.filter((p) => p.manufacturingLevel === level)),
    [papers, level, isAll]
  );

  const focuses = useMemo(() => papersByDSSFocus(filtered), [filtered]);
  const sorted = useMemo(() => sortedEntries(focuses), [focuses]);

  const levelLabel = isAll ? "All Levels" : level!;

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: levelLabel },
        ]}
      />
      <h1>{levelLabel}</h1>
      <p className="subtitle">
        {filtered.length} papers — select a DSS focus area
      </p>

      <div className="card-grid">
        <CategoryCard
          label="All DSS Focus Areas"
          count={filtered.length}
          to={`/level/${encodeURIComponent(level!)}/focus/all`}
        />
        {sorted.map(([focus, group]) => (
          <CategoryCard
            key={focus}
            label={focus}
            count={group.length}
            to={`/level/${encodeURIComponent(level!)}/focus/${encodeURIComponent(focus)}`}
          />
        ))}
      </div>
    </div>
  );
}
