import { useMemo } from "react";
import { Link } from "react-router-dom";
import type { Paper } from "../types";
import { papersByLevel, sortLevels } from "../utils/normalize";
import { CategoryCard } from "../components/CategoryCard";
import { CitationBlock } from "../components/CitationBlock";
import { surveyBibtex } from "../data/citations";

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
        A survey on decision support in high-mix low-volume manufacturing - {papers.length} papers across{" "}
        {levels.size} manufacturing levels
      </p>

      <section className="intro-panel">
        <div className="intro-copy">
          <h2>About the Survey</h2>
          <p>
            This interactive overview presents the paper corpus included in the systematic literature review article {" "}
  <a
    href="https://doi.org/10.3389/fmtec.2026.1905224"
    target="_blank"
    rel="noopener noreferrer"
  >
    “A Survey on Decision Support in High-Mix Low-Volume Manufacturing”
  </a>, published in Frontiers in Manufacturing Technology (2026).
            It enables researchers and practitioners to filter and explore the corpus by manufacturing level, decision area, and technology. 
            The overview also provides interactive figures and DOI links to the analyzed papers.
            The raw data will is available on GitHub, with the link added upon publication.
          </p>
          <p className="reference-placeholder">
            Cite Us
          </p>
          <p>
            If you use the survey article, this interactive overview, the paper corpus, or the associated data in academic research, please cite the survey article using the citation provided on this page.
          </p>
        </div>
        <CitationBlock title="BibTeX" citation={surveyBibtex} />
      </section>
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

      <div className="level-actions">
        <Link to="/possibly-relevant" className="primary-link-button">
          View Possibly Relevant Papers
        </Link>
      </div>
    </div>
  );
}
