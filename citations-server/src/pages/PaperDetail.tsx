import { useParams, useNavigate } from "react-router-dom";
import type { Paper } from "../types";
import { Breadcrumb } from "../components/Breadcrumb";

function Field({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div className="detail-field">
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function ListField({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="detail-field">
      <dt>{label}</dt>
      <dd>
        <div className="tag-list">
          {items.map((item, i) => (
            <span key={i} className="tag">
              {item}
            </span>
          ))}
        </div>
      </dd>
    </div>
  );
}

export function PaperDetail({ papers }: { papers: Paper[] }) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const paper = papers.find((p) => p.id === Number(id));

  if (!paper) {
    return (
      <div className="page">
        <h1>Paper not found</h1>
        <button onClick={() => navigate("/")}>Back to home</button>
      </div>
    );
  }

  return (
    <div className="page">
      <Breadcrumb
        crumbs={[
          { label: "Levels", to: "/" },
          {
            label: paper.manufacturingLevel,
            to: `/level/${encodeURIComponent(paper.manufacturingLevel)}`,
          },
          {
            label: paper.dssFocus,
            to: `/level/${encodeURIComponent(paper.manufacturingLevel)}/focus/${encodeURIComponent(paper.dssFocus)}`,
          },
          { label: "Paper" },
        ]}
      />

      <h1 className="paper-title">{paper.title}</h1>

      <dl className="detail-grid">
        <Field label="Year" value={String(paper.year)} />
        <Field label="Manufacturing Level" value={paper.manufacturingLevel} />
        <Field label="DSS Focus" value={paper.dssFocus} />
        <Field label="Job-Shop Variation" value={paper.jobShopVariation} />
        <Field label="Country" value={paper.country} />
        <Field label="Industry" value={paper.industry} />
        <ListField label="Technologies" items={paper.technologies} />
        <ListField label="Methods" items={paper.methods} />
        <Field label="Evaluation Setting" value={paper.evaluationSetting} />
        <Field label="Data Source" value={paper.dataSource} />
        <Field label="Metrics" value={paper.metrics} />
        <Field label="BibTeX Key" value={paper.bibtexKey} />
        {paper.doi && (
          <div className="detail-field">
            <dt>DOI</dt>
            <dd>
              <a href={paper.doi} target="_blank" rel="noopener noreferrer">
                {paper.doi}
              </a>
            </dd>
          </div>
        )}
        <Field label="Snowball" value={paper.snowball ? "Yes" : "No"} />
      </dl>

      <button className="back-btn" onClick={() => navigate(-1)}>
        Back
      </button>
    </div>
  );
}
