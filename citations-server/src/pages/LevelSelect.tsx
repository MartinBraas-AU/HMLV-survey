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
        Systematic literature review - {papers.length} papers across{" "}
        {levels.size} manufacturing levels
      </p>

      <section className="intro-panel">
        <div className="intro-copy">
          <h2>About the Survey</h2>
          <p>
            This interactive overview presents the paper corpus included in the systematic literature review article “A Survey on Decision Support in High-Mix Low-Volume Manufacturing”, currently in preparation for submission to a peer-reviewed journal.
            It enables researchers and practitioners to filter and explore the corpus by manufacturing level, decision area, and technology. 
            The overview also provides interactive figures and DOI links to the analyzed papers.
            The raw data will be made available on GitHub, with the link added upon publication.
          </p>
          <p className="reference-placeholder">
            Cite Us
          </p>
          <p>
            If you use the survey article, this interactive overview, the paper corpus, or the associated data in academic research, please cite the survey article using the citation provided on this page.
          </p>
          <p>
            The citation currently refers to the preprint version and will be updated with journal publication details if the manuscript is accepted.
          </p>
        </div>
        <div className="bibtex-block">
          <div className="bibtex-title">BibTeX Journal Placeholder</div>
          <pre>{`@article{hmlv_dss_survey_placeholder,
  title = {A Survey on Decision Support in High-Mix Low-Volume Manufacturing},
  author = {Author, First and Author, Second},
  journal = {Journal Name},
  year = {2026},
  note = {Manuscript in preparation}
}`}</pre>
        </div>
        <div className="bibtex-block">
          <div className="bibtex-title">BibTeX Arxiv</div>
          <pre>{`@article{hmlv_dss_survey_placeholder,
  title = {A Survey on Decision Support in High-Mix Low-Volume Manufacturing},
  author = {Author, First and Author, Second},
  journal = {Arxiv preprint},
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
