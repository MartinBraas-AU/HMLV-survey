import { useMemo } from "react";
import { useParams, Navigate } from "react-router-dom";
import type { Paper } from "../types";
import { papersByJobShopVariant, sortedEntries } from "../utils/normalize";
import { CategoryCard } from "../components/CategoryCard";
import { Breadcrumb } from "../components/Breadcrumb";
import { PaperTable } from "./PaperList";

export function SubCategorySelect({ papers }: { papers: Paper[] }) {
  const { level, focus } = useParams<{ level: string; focus: string }>();
  const isAllLevel = level === "all";
  const isAllFocus = focus === "all";

  const filtered = useMemo(() => {
    let result = papers;
    if (!isAllLevel) result = result.filter((p) => p.manufacturingLevel === level);
    if (!isAllFocus) result = result.filter((p) => p.dssFocus === focus);
    return result;
  }, [papers, level, focus, isAllLevel, isAllFocus]);

  const isScheduling = focus?.toLowerCase() === "scheduling";

  // If not scheduling, redirect to paper list directly
  if (!isScheduling) {
    return <Navigate to={`/level/${encodeURIComponent(level!)}/focus/${encodeURIComponent(focus!)}/papers`} replace />;
  }

  const variants = useMemo(() => papersByJobShopVariant(filtered), [filtered]);
  const sorted = useMemo(() => sortedEntries(variants), [variants]);

  const levelLabel = isAllLevel ? "All Levels" : level!;

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: levelLabel, to: `/level/${encodeURIComponent(level!)}` },
          { label: focus! },
        ]}
      />
      <h1>Scheduling — Job-Shop Variations</h1>
      <p className="subtitle">
        {filtered.length} papers — select a variant or view all
      </p>

      <div className="card-grid">
        <CategoryCard
          label="All Scheduling Papers"
          count={filtered.length}
          to={`/level/${encodeURIComponent(level!)}/focus/${encodeURIComponent(focus!)}/papers`}
        />
        {sorted.map(([variant, group]) => (
          <CategoryCard
            key={variant}
            label={variant}
            count={group.length}
            to={`/level/${encodeURIComponent(level!)}/focus/${encodeURIComponent(focus!)}/variant/${encodeURIComponent(variant)}`}
          />
        ))}
      </div>
    </div>
  );
}

export function VariantPaperList({ papers }: { papers: Paper[] }) {
  const { level, focus, variant } = useParams<{
    level: string;
    focus: string;
    variant: string;
  }>();
  const isAllLevel = level === "all";

  const filtered = useMemo(() => {
    let result = papers;
    if (!isAllLevel) result = result.filter((p) => p.manufacturingLevel === level);
    result = result.filter((p) => p.dssFocus === focus);
    if (variant === "Other Scheduling") {
      result = result.filter((p) => !p.jobShopVariation);
    } else {
      result = result.filter((p) => p.jobShopVariation === variant);
    }
    return result;
  }, [papers, level, focus, variant, isAllLevel]);

  const levelLabel = isAllLevel ? "All Levels" : level!;

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          { label: levelLabel, to: `/level/${encodeURIComponent(level!)}` },
          {
            label: focus!,
            to: `/level/${encodeURIComponent(level!)}/focus/${encodeURIComponent(focus!)}`,
          },
          { label: variant! },
        ]}
      />
      <h1>{variant}</h1>
      <p className="subtitle">{filtered.length} papers</p>
      <PaperTable papers={filtered} />
    </div>
  );
}
