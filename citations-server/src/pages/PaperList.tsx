import { useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import type { Paper } from "../types";
import { Breadcrumb } from "../components/Breadcrumb";

export function PaperTable({ papers }: { papers: Paper[] }) {
  const sorted = useMemo(
    () => [...papers].sort((a, b) => b.year - a.year || a.title.localeCompare(b.title)),
    [papers]
  );

  return (
    <table className="paper-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Year</th>
          <th>Country</th>
          <th>Technologies</th>
          <th>Methods</th>
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

  const filtered = useMemo(() => {
    let result = papers;
    if (!isAllLevel) result = result.filter((p) => p.manufacturingLevel === level);
    if (!isAllFocus) result = result.filter((p) => p.dssFocus === focus);
    return result;
  }, [papers, level, focus, isAllLevel, isAllFocus]);

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
      <p className="subtitle">{filtered.length} papers</p>
      <PaperTable papers={filtered} />
    </div>
  );
}
