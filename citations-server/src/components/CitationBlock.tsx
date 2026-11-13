import { useState } from "react";

interface CitationBlockProps {
  title: string;
  citation: string;
}

export function CitationBlock({ title, citation }: CitationBlockProps) {
  const [copyStatus, setCopyStatus] = useState<"idle" | "copied" | "error">(
    "idle"
  );

  async function copyCitation() {
    try {
      await navigator.clipboard.writeText(citation);
      setCopyStatus("copied");
    } catch (error) {
      console.error("Could not copy citation to clipboard", error);
      setCopyStatus("error");
    }
  }

  return (
    <div className="bibtex-block">
      <div className="bibtex-header">
        <div className="bibtex-title">{title}</div>
        <button type="button" className="copy-button" onClick={copyCitation}>
          {copyStatus === "copied" ? "Copied" : "Copy BibTeX"}
        </button>
      </div>
      <pre>{citation}</pre>
      {copyStatus === "error" && (
        <p className="copy-status" role="alert">
          Copying failed. Please select and copy the citation manually.
        </p>
      )}
    </div>
  );
}
