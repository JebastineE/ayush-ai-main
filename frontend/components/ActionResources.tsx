"use client";

import { ExternalLink, FileText, Search, CheckSquare, Shield, Utensils, Leaf, Download } from "lucide-react";
import { ActionItem } from "@/types";
import { useState } from "react";
import { PatentChecklist } from "./PatentChecklist";
import { PreparationDraft } from "./PreparationDraft";

interface ActionResourcesProps {
  actions: ActionItem[];
  onOpenPdfViewer?: (url: string, page: number) => void;
  onOpenTKDLScanner?: () => void;
  citations?: any[];
  query?: string;
  answer?: string;
}

export function ActionResources({
  actions,
  onOpenPdfViewer,
  onOpenTKDLScanner,
  citations = [],
  query,
  answer,
}: ActionResourcesProps) {
  const [showChecklist, setShowChecklist] = useState(false);
  const [showPreparationDraft, setShowPreparationDraft] = useState(false);

  if (!actions || actions.length === 0) {
    return null;
  }

  const handleAction = (action: ActionItem) => {
    if (action.type === "external" && action.url) {
      // Open external government URLs in new tab
      window.open(action.url, "_blank", "noopener,noreferrer");
    } else if (action.type === "internal") {
      // Handle internal actions
      switch (action.id) {
        case "patent_checklist":
          setShowChecklist(true);
          break;
        case "supporting_documents":
          // Trigger PDF viewer with first citation
          if (citations.length > 0 && onOpenPdfViewer) {
            const firstCitation = citations[0];
            // Construct URL from citation source
            const pdfUrl = `/docs/${encodeURIComponent(firstCitation.source)}`;
            onOpenPdfViewer(pdfUrl, firstCitation.page || 1);
          }
          break;
        case "tkdl_scan":
          // Open TKDL scanner
          if (onOpenTKDLScanner) {
            onOpenTKDLScanner();
          }
          break;
        case "preparation_draft":
          setShowPreparationDraft(true);
          break;
        default:
          console.warn(`Unknown internal action: ${action.id}`);
      }
    }
  };

  const getActionIcon = (actionId: string) => {
    switch (actionId) {
      case "patent_search":
        return <Search className="w-4 h-4" />;
      case "patent_filing":
        return <FileText className="w-4 h-4" />;
      case "patent_forms":
        return <FileText className="w-4 h-4" />;
      case "ip_india_manual":
        return <FileText className="w-4 h-4" />;
      case "patent_checklist":
        return <CheckSquare className="w-4 h-4" />;
      case "supporting_documents":
        return <FileText className="w-4 h-4" />;
      case "tkdl_scan":
        return <Leaf className="w-4 h-4" />;
      case "nba_resources":
        return <Shield className="w-4 h-4" />;
      case "nba_access_guidelines":
        return <Shield className="w-4 h-4" />;
      case "foscos":
        return <Utensils className="w-4 h-4" />;
      case "fssai_regulations":
        return <Utensils className="w-4 h-4" />;
      case "preparation_draft":
        return <Download className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const officialActions = actions.filter(a => a.type === "external");

  return (
    <>
      <div className="mt-4 pt-4 border-t border-outline-variant/30">
        {/* Official Forms & Resources */}
        {officialActions.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">
              Official Forms & Resources
            </p>
            <div className="flex flex-wrap gap-2">
              {officialActions.map((action) => (
                <button
                  key={action.id}
                  onClick={() => handleAction(action)}
                  title={action.description}
                  className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-100 hover:border-blue-400 transition-all shadow-sm text-sm font-semibold"
                >
                  {getActionIcon(action.id)}
                  {action.label}
                  <ExternalLink className="w-3 h-3" />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Patent Checklist Modal */}
      {showChecklist && (
        <PatentChecklist
          onClose={() => setShowChecklist(false)}
          citations={citations}
        />
      )}

      {/* Preparation Draft Modal */}
      {showPreparationDraft && (
        <PreparationDraft
          onClose={() => setShowPreparationDraft(false)}
          context={{ query, answer, citations }}
        />
      )}
    </>
  );
}
