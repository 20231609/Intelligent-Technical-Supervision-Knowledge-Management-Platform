import { RightOutlined } from "@ant-design/icons";

import { downloadSourceDocument } from "@/services/documentService";
import type { Citation } from "@/types/chat";
import { formatCitationBreadcrumb, formatRelevanceLabel } from "@/utils/citationContent";

import "./CitationDetailCard.css";

interface CitationDetailCardProps {
  citations: Citation[];
}

const CitationDetailCard = ({ citations }: CitationDetailCardProps) => {
  const primary = citations[0];

  if (!primary) {
    return null;
  }

  const handleViewOriginal = () => {
    void downloadSourceDocument(primary.documentId, primary.documentName);
  };

  return (
    <div className="citation-detail-card">
      <div className="citation-detail-card__header">
        <div className="citation-detail-card__title" title={primary.documentName}>
          {primary.documentName}
        </div>
        <div className="citation-detail-card__breadcrumb" title={formatCitationBreadcrumb(primary)}>
          {formatCitationBreadcrumb(primary)}
        </div>
      </div>

      <div className="citation-detail-card__body">
        {citations.map((citation) => (
          <div key={citation.id} className="citation-detail-card__snippet-block">
            {citations.length > 1 ? (
              <div className="citation-detail-card__snippet-label">
                引用 {citation.markerIndex}
                {citation.chunkType ? ` / ${citation.chunkType}` : ""}
              </div>
            ) : null}
            <div className="citation-detail-card__snippet">{citation.snippet}</div>
          </div>
        ))}
      </div>

      <div className="citation-detail-card__footer">
        <span className="citation-detail-card__relevance">
          相关度 {formatRelevanceLabel(primary)}
        </span>
        <button type="button" className="citation-detail-card__view-original" onClick={handleViewOriginal}>
          查看原文
          <RightOutlined />
        </button>
      </div>
    </div>
  );
};

export default CitationDetailCard;
