import { useMemo } from "react";
import { Link } from "react-router-dom";
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

      <section className="intro-panel">
        <div className="intro-copy">
          <h2>About the Survey</h2>
          <p>
            This interactive companion presents the papers included in the
            systematic survey of decision support systems for high-mix,
            low-volume manufacturing. Introductory text and references for the
            survey can be added here before publication.
          </p>
          <p className="reference-placeholder">
            References placeholder: cite the survey manuscript and any companion
            protocol, data, or review-method papers here.
          </p>
        </div>
        <div className="bibtex-block">
          <div className="bibtex-title">BibTeX</div>
          <pre>{`@article{hmlv_dss_survey_placeholder,
  title = {Decision Support Systems for High-Mix Low-Volume Manufacturing: A Systematic Literature Review},
  author = {Author, First and Author, Second},
  journal = {Journal Name},
  year = {2026},
  note = {Manuscript in preparation}
}`}</pre>
        </div>
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
