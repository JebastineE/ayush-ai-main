"use client";

import { useState } from "react";
import { Shield, ChevronDown, ChevronUp, Loader2, FileSearch, ExternalLink, Database } from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";
import type { TKDLScanResult, MatchedRecord, PatentSearchResult, PatentRecord } from "@/types";

interface BiopiraсyScannerProps {
  /** Reserved for future use */
  demoClaim?: string | null;
}

export function BiopiracyScanner({ demoClaim }: BiopiraсyScannerProps) {
  const [claim, setClaim]       = useState("");
  const [result, setResult]     = useState<TKDLScanResult | null>(null);
  const [patentResults, setPatentResults] = useState<PatentSearchResult | null>(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [expandedPatent, setExpandedPatent] = useState<string | null>(null);

  // Safe date formatter for BigQuery YYYYMMDD format (e.g., "20260410")
  const formatPatentDate = (dateValue: string | null | undefined): string => {
    if (!dateValue || typeof dateValue !== 'string') {
      return "Date unavailable";
    }

    // BigQuery returns dates as YYYYMMDD (e.g., "20260410")
    // Extract year (first 4 characters)
    if (dateValue.length >= 4) {
      const year = dateValue.substring(0, 4);
      // Validate it's a number
      if (/^\d{4}$/.test(year)) {
        return year;
      }
    }

    // Fallback: try to parse as ISO date
    const date = new Date(dateValue);
    if (!Number.isNaN(date.getTime())) {
      return date.getFullYear().toString();
    }

    return "Date unavailable";
  };

  const handleScan = async (claimText?: string) => {
    const text = (claimText ?? claim).trim();
    if (!text || text.length < 10) {
      setError("Please enter a plant name or formulation (at least 10 characters).");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    setPatentResults(null);

    try {
      // Call both TKDL scan and BigQuery patent search in parallel
      const [tkdlRes, patentRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/tkdl-scan`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ claim_text: text }),
        }),
        fetch(`${API_BASE_URL}/api/v1/patent-search`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ claim_text: text }),
        })
      ]);

      // Process TKDL results
      if (tkdlRes.ok) {
        const tkdlData: TKDLScanResult = await tkdlRes.json();
        setResult(tkdlData);
      } else {
        console.error("TKDL scan failed:", tkdlRes.status);
        setResult({
          alert_score: 0,
          alert_level: "NONE",
          section_3p_applicable: false,
          matched_records: [],
          recommended_action: "",
          claim_analyzed: text
        });
      }

      // Process BigQuery patent results (non-blocking)
      if (patentRes.ok) {
        const patentData: PatentSearchResult = await patentRes.json();
        setPatentResults(patentData);
      } else {
        console.error("Patent search failed:", patentRes.status);
        setPatentResults({
          query: text,
          search_terms: [],
          results: [],
          total_found: 0,
          error: "Patent search temporarily unavailable"
        });
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Search failed. Please check if the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-primary-container/10 flex items-center justify-center shrink-0">
          <Shield className="w-5 h-5 text-primary-container" />
        </div>
        <div>
          <h2 className="font-headline-sm text-headline-sm text-on-surface">Biopiracy Scanner</h2>
          <p className="text-ui-label-sm text-secondary">
            Search for related patent records using the Google Patents Public Dataset.
          </p>
        </div>
      </div>

      {/* Input Panel */}
      <div className="bg-surface p-5 rounded-xl border border-outline-variant/30 space-y-4 shadow-sm">
        <div>
          <label className="block text-ui-label-bold text-secondary mb-2">
            Formulation or Plant Name
          </label>
          <textarea
            id="biopiracy-claim-input"
            rows={5}
            value={claim}
            onChange={e => setClaim(e.target.value)}
            placeholder="e.g., Ashwagandha formulation for stress relief"
            className="w-full bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-3 text-body-md resize-none focus:outline-none focus:ring-2 focus:ring-primary-container/30 focus:border-primary-container/50 transition-all"
          />
          <p className="text-ui-label-sm text-secondary mt-1">
            Enter a plant name or formulation to search for related patent records.
          </p>
        </div>
        <button
          id="biopiracy-scan-btn"
          onClick={() => handleScan()}
          disabled={loading || claim.trim().length < 10}
          className="flex items-center gap-2 px-5 py-2.5 bg-primary-container text-white rounded-lg font-ui-label-bold hover:bg-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          {loading ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Searching…</>
          ) : (
            <><FileSearch className="w-4 h-4" /> Search Related Patents</>
          )}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* TKDL Results */}
      {result && result.matched_records.length > 0 && (
        <div className="bg-surface rounded-xl border border-outline-variant/30 p-5 space-y-4 shadow-sm">
          <div className="flex items-center gap-3 border-b border-outline-variant/20 pb-3">
            <Shield className="w-5 h-5 text-primary-container" />
            <div>
              <h3 className="font-ui-label-bold text-on-surface">Related TKDL Records</h3>
              <p className="text-ui-label-sm text-secondary">
                {result.matched_records.length} potentially relevant traditional knowledge records
              </p>
            </div>
          </div>

          <div className="space-y-2">
            {result.matched_records.map((rec: MatchedRecord, i: number) => (
              <div
                key={rec.chunk_id || i}
                className="bg-white border border-outline-variant/30 rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => setExpanded(expanded === (rec.chunk_id || String(i)) ? null : (rec.chunk_id || String(i)))}
                  className="w-full flex items-center justify-between p-3 text-left hover:bg-surface-container-low/50 transition-colors gap-3"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-ui-label-bold text-sm text-on-surface">{rec.formulation}</p>
                    <p className="text-ui-label-sm text-secondary mt-0.5">{rec.source_file}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {rec.ipc_code && (
                      <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 font-mono">
                        {rec.ipc_code}
                      </span>
                    )}
                    {expanded === (rec.chunk_id || String(i))
                      ? <ChevronUp className="w-4 h-4 text-secondary" />
                      : <ChevronDown className="w-4 h-4 text-secondary" />
                    }
                  </div>
                </button>
                {expanded === (rec.chunk_id || String(i)) && (
                  <div className="px-3 pb-3 border-t border-outline-variant/20 space-y-2">
                    <div className="mt-2">
                      <p className="text-xs font-ui-label-bold text-secondary mb-1">Description</p>
                      <p className="text-sm text-secondary leading-relaxed bg-surface-container-lowest rounded p-2">
                        {rec.snippet}
                      </p>
                    </div>
                    {rec.tkrc_code && (
                      <p className="text-ui-label-sm text-secondary">
                        TKRC Code: <span className="font-mono">{rec.tkrc_code}</span>
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* BigQuery Patent Search Results */}
      {patentResults && patentResults.total_found > 0 && (
        <div className="bg-surface rounded-xl border border-outline-variant/30 p-5 space-y-4 shadow-sm">
          <div className="flex items-center gap-3 border-b border-outline-variant/20 pb-3">
            <Database className="w-5 h-5 text-blue-600" />
            <div>
              <h3 className="font-ui-label-bold text-on-surface">Related Patent Records</h3>
              <p className="text-ui-label-sm text-secondary">
                {patentResults.total_found} potentially relevant patents from Google Patents Public Dataset
              </p>
            </div>
          </div>

          {/* Patent Records */}
          <div className="space-y-2">
            {patentResults.results.map((patent: PatentRecord, i: number) => (
              <div
                key={patent.publication_number || i}
                className="bg-white border border-outline-variant/30 rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => setExpandedPatent(expandedPatent === patent.publication_number ? null : patent.publication_number)}
                  className="w-full flex items-start justify-between p-3 text-left hover:bg-surface-container-low/50 transition-colors gap-3"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-2 flex-wrap">
                      <span className="shrink-0 text-xs font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-700 font-bold">
                        {patent.country_code}
                      </span>
                      <p className="font-ui-label-bold text-sm text-on-surface flex-1">
                        {patent.title || "Untitled Patent"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-ui-label-sm text-secondary flex-wrap">
                      <span className="font-mono">{patent.publication_number}</span>
                      {patent.publication_date && (
                        <>
                          <span>•</span>
                          <span>{formatPatentDate(patent.publication_date)}</span>
                        </>
                      )}
                      {patent.assignee && patent.assignee !== "Unknown" && (
                        <>
                          <span>•</span>
                          <span className="truncate max-w-[200px]">{patent.assignee}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {patent.cpc_code && (
                      <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700 font-mono">
                        {patent.cpc_code.split(',')[0]}
                      </span>
                    )}
                    {expandedPatent === patent.publication_number
                      ? <ChevronUp className="w-4 h-4 text-secondary" />
                      : <ChevronDown className="w-4 h-4 text-secondary" />
                    }
                  </div>
                </button>
                {expandedPatent === patent.publication_number && (
                  <div className="px-3 pb-3 border-t border-outline-variant/20 space-y-3">
                    {patent.abstract && (
                      <div className="mt-2">
                        <p className="text-xs font-ui-label-bold text-secondary mb-1">Abstract</p>
                        <p className="text-sm text-secondary leading-relaxed bg-surface-container-lowest rounded p-2">
                          {patent.abstract}
                        </p>
                      </div>
                    )}
                    {patent.source_url && (
                      <a
                        href={patent.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-ui-label-bold"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        View on Google Patents
                      </a>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Search Terms */}
          {patentResults.search_terms.length > 0 && (
            <div className="text-xs text-secondary border-t border-outline-variant/20 pt-3">
              <span className="font-ui-label-bold">Search terms used:</span> {patentResults.search_terms.slice(0, 10).join(', ')}
            </div>
          )}
        </div>
      )}

      {/* No TKDL Results */}
      {result && result.matched_records.length === 0 && (
        <div className="bg-surface rounded-xl border border-outline-variant/30 p-5 text-center text-secondary">
          <p className="text-sm">No related TKDL records were found.</p>
        </div>
      )}

      {/* No Patent Results */}
      {patentResults && patentResults.total_found === 0 && !patentResults.error && (
        <div className="bg-surface rounded-xl border border-outline-variant/30 p-5 text-center text-secondary">
          <p className="text-sm">No related patent records were found.</p>
        </div>
      )}

      {/* BigQuery Patent Search Error */}
      {patentResults && patentResults.error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-amber-800 text-sm">
          ℹ️ Patent search is temporarily unavailable. Please try again.
        </div>
      )}

      {/* Disclaimer */}
      {(result || patentResults) && (
        <div className="bg-blue-50/50 border border-blue-200/50 rounded-lg p-4 text-xs text-blue-900 leading-relaxed">
          <strong>Disclaimer:</strong> Search results are informational and are not a legal determination. Patent records should be independently reviewed by a qualified professional.
        </div>
      )}
    </div>
  );
}
