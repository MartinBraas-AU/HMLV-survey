import { useMemo } from "react";
import type { Paper } from "../types";
import { papersByLevel, sortLevels } from "../utils/normalize";
import { CategoryCard } from "../components/CategoryCard";

const LEVEL_DESCRIPTIONS: Record<string, string> = {
  L0: "Process",
  L1: "Line / Cell",
  L2: "Factory",
  L3: "Enterprise / Supply Chain",
};

export function LevelSelect({ papers }: { papers: Paper[] }) {
  const levels = useMemo(() => papersByLevel(papers), [papers]);
  const sortedKeys = useMemo(
    () => sortLevels([...levels.keys()]),
    [levels]
  );

  return (
    <div className="page">
      <h1>HMLV Manufacturing DSS Survey</h1>
      <p className="subtitle">
        Systematic literature review — {papers.length} papers across{" "}
        {levels.size} manufacturing levels
      </p>

      <div className="card-grid">
        <CategoryCard
          label="All Levels"
          count={papers.length}
          to="/level/all"
        />
        {sortedKeys.map((level) => (
          <CategoryCard
            key={level}
            label={`${level}${LEVEL_DESCRIPTIONS[level] ? ` — ${LEVEL_DESCRIPTIONS[level]}` : ""}`}
            count={levels.get(level)!.length}
            to={`/level/${encodeURIComponent(level)}`}
          />
        ))}
      </div>
    </div>
  );
}
