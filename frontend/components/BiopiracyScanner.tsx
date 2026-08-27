"use client";

import { useState, useEffect, useRef } from "react";
import { Shield, Search, AlertTriangle, CheckCircle, Info, ChevronDown, ChevronUp, Loader2, FileSearch } from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";
import type { TKDLScanResult, MatchedRecord } from "@/types";

interface BiopiraсyScannerProps {
  /** When provided, auto-fills and triggers the scan (demo quick-fill). */
  demoClaim?: string | null;
}

const ALERT_COLORS: Record<string, { bg: string; text: string; border: string; bar: string }> = {
  HIGH:   { bg: "bg-red-50",    text: "text-red-700",    border: "border-red-300",    bar: "bg-red-500"    },
  MEDIUM: { bg: "bg-amber-50",  text: "text-amber-700",  border: "border-amber-300",  bar: "bg-amber-500"  },
  LOW:    { bg: "bg-blue-50",   text: "text-blue-700",   border: "border-blue-300",   bar: "bg-blue-400"   },
  NONE:   { bg: "bg-green-50",  text: "text-green-700",  border: "border-green-300",  bar: "bg-green-500"  },
};

const ALERT_ICONS: Record<string, React.ElementType> = {
  HIGH: AlertTriangle, MEDIUM: AlertTriangle, LOW: Info, NONE: CheckCircle,
};

const DEMO_CLAIM =
  "Topical therapeutic formulation comprising 15% Curcuma longa extract for accelerating dermal wound repair in human subjects.";

export function BiopiracyScanner({ demoClaim }: BiopiraсyScannerProps) {
  const [claim, setClaim]       = useState("");
  const [result, setResult]     = useState<TKDLScanResult | null>(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const autoFiredRef = useRef<string | null>(null);

  // Demo auto-fill: fire once per unique demoClaim value
  useEffect(() => {
    if (demoClaim && demoClaim !== autoFiredRef.current) {
      autoFiredRef.current = demoClaim;
      setClaim(demoClaim);
      handleScan(demoClaim);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demoClaim]);

  const handleScan = async (claimText?: string) => {
    const text = (claimText ?? claim).trim();
    if (!text || text.length < 20) {
      setError("Please enter a patent claim of at least 20 characters.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/tkdl-scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim_text: text }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: TKDLScanResult = await res.json();
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Scan failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const c = result ? (ALERT_COLORS[result.alert_level] ?? ALERT_COLORS.NONE) : null;
  const AlertIcon = result ? (ALERT_ICONS[result.alert_level] ?? Info) : null;

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-primary-container/10 flex items-center justify-center shrink-0">
          <Shield className="w-5 h-5 text-primary-container" />
        </div>
        <div>
          <h2 className="font-headline-sm text-headline-sm text-on-surface">TKDL Biopiracy Scanner</h2>
          <p className="text-ui-label-sm text-secondary">
            Detects prior art in the Traditional Knowledge Digital Library (TKDL) to assess Section 3(p) patent risk.
          </p>
        </div>
      </div>

      {/* Input Panel */}
      <div className="bg-surface p-5 rounded-xl border border-outline-variant/30 space-y-4 shadow-sm">
        <div>
          <label className="block text-ui-label-bold text-secondary mb-2">
            Patent Claim Text
          </label>
          <textarea
            id="biopiracy-claim-input"
            rows={5}
            value={claim}
            onChange={e => setClaim(e.target.value)}
            placeholder={`e.g., "${DEMO_CLAIM}"`}
            className="w-full bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-3 text-body-md resize-none focus:outline-none focus:ring-2 focus:ring-primary-container/30 focus:border-primary-container/50 transition-all"
          />
          <p className="text-ui-label-sm text-secondary mt-1">
            Paste the full independent claim from a patent application for analysis.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            id="biopiracy-scan-btn"
            onClick={() => handleScan()}
            disabled={loading || claim.trim().length < 20}
            className="flex items-center gap-2 px-5 py-2.5 bg-primary-container text-white rounded-lg font-ui-label-bold hover:bg-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {loading ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Scanning TKDL…</>
            ) : (
              <><FileSearch className="w-4 h-4" /> Scan for Prior Art</>
            )}
          </button>
          <button
            onClick={() => { setClaim(DEMO_CLAIM); }}
            className="px-4 py-2.5 rounded-lg border border-outline-variant/50 text-secondary hover:text-primary-container hover:border-primary-container/30 transition-all text-sm font-ui-label-bold"
          >
            Use Demo Claim
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* Results */}
      {result && c && AlertIcon && (
        <div className={cn("rounded-xl border p-5 space-y-5 animate-in fade-in zoom-in duration-200", c.bg, c.border)}>

          {/* Alert Level Badge + Score Meter */}
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-3">
              <AlertIcon className={cn("w-6 h-6", c.text)} />
              <div>
                <p className={cn("font-ui-label-bold text-lg", c.text)}>
                  {result.alert_level} RISK
                </p>
                <p className="text-ui-label-sm text-secondary">
                  {result.alert_level === "HIGH"   && "Strong prior art — Section 3(p) bar likely"}
                  {result.alert_level === "MEDIUM" && "Partial overlap — expert review required"}
                  {result.alert_level === "LOW"    && "Weak similarity — conduct full FTO analysis"}
                  {result.alert_level === "NONE"   && "No significant TKDL prior art found"}
                </p>
              </div>
            </div>
            {/* Score Meter */}
            <div className="flex flex-col items-end gap-1 min-w-[140px]">
              <p className="text-ui-label-sm text-secondary">Biopiracy Alert Score</p>
              <p className={cn("font-headline-md text-headline-md", c.text)}>
                {result.alert_score.toFixed(1)}<span className="text-sm font-normal text-secondary"> / 100</span>
              </p>
              <div className="w-36 h-2.5 bg-surface-container-highest rounded-full overflow-hidden">
                <div
                  className={cn("h-full rounded-full transition-all duration-700", c.bar)}
                  style={{ width: `${result.alert_score}%` }}
                />
              </div>
            </div>
          </div>

          {/* Recommended Action */}
          <div className={cn("rounded-lg p-4 border", c.border, "bg-white/60")}>
            <p className="text-ui-label-bold text-secondary mb-1 text-sm">Recommended Action</p>
            <p className="text-body-md">{result.recommended_action}</p>
          </div>

          {/* Section 3(p) Precedent */}
          {result.section_3p_applicable && result.section_3p_precedent && (
            <div className="bg-red-100/60 border border-red-200 rounded-lg p-4 space-y-1">
              <p className="font-ui-label-bold text-red-800 text-sm flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Section 3(p) — Patents Act Precedent
              </p>
              <p className="text-sm text-red-900 leading-relaxed">{result.section_3p_precedent}</p>
            </div>
          )}

          {/* Matched Prior Art Records */}
          {result.matched_records.length > 0 && (
            <div>
              <p className="font-ui-label-bold text-secondary mb-3 text-sm">
                Matched TKDL Prior Art ({result.matched_records.length} records)
              </p>
              <div className="space-y-2">
                {result.matched_records.map((rec: MatchedRecord, i: number) => (
                  <div
                    key={rec.chunk_id || i}
                    className="bg-white/70 border border-outline-variant/30 rounded-lg overflow-hidden"
                  >
                    <button
                      onClick={() => setExpanded(expanded === (rec.chunk_id || String(i)) ? null : (rec.chunk_id || String(i)))}
                      className="w-full flex items-center justify-between p-3 text-left hover:bg-surface-container-low/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className={cn(
                          "shrink-0 text-xs font-mono px-2 py-0.5 rounded font-bold",
                          rec.similarity >= 70 ? "bg-red-100 text-red-700" :
                          rec.similarity >= 55 ? "bg-amber-100 text-amber-700" :
                          "bg-blue-100 text-blue-700"
                        )}>
                          {rec.similarity.toFixed(1)}%
                        </span>
                        <div>
                          <p className="font-ui-label-bold text-sm text-on-surface">{rec.formulation}</p>
                          <p className="text-ui-label-sm text-secondary">{rec.source_file}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {rec.ipc_code && (
                          <span className="text-xs px-2 py-0.5 rounded bg-primary-container/10 text-primary-container font-mono">
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
                      <div className="px-3 pb-3 border-t border-outline-variant/20">
                        <p className="text-sm text-secondary leading-relaxed mt-2 font-mono bg-surface-container-lowest rounded p-2">
                          {rec.snippet}
                        </p>
                        {rec.tkrc_code && (
                          <p className="text-ui-label-sm text-secondary mt-1">TKRC Code: <span className="font-mono">{rec.tkrc_code}</span></p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
