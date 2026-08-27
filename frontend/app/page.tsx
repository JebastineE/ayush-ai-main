"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Navbar }                from "@/components/Navbar";
import { ToolTabs }              from "@/components/ToolTabs";
import { ChatInterface }         from "@/components/ChatInterface";
import { ABSNavigator }          from "@/components/ABSNavigator";
import { FormulationClassifier } from "@/components/FormulationClassifier";
import { PdfViewer }             from "@/components/PdfViewer";
import { BiopiracyScanner }      from "@/components/BiopiracyScanner";
import { ChevronDown, Zap }      from "lucide-react";
import { cn }                    from "@/lib/utils";
import { API_BASE_URL }            from "@/lib/config";
import type { EscalationRequest, MessageItem } from "@/types";

// ---------------------------------------------------------------------------
// Demo Scenarios — 4 evaluator-facing quick-fill scenarios
// ---------------------------------------------------------------------------

interface DemoScenario {
  id:          string;
  emoji:       string;
  label:       string;
  description: string;
  tab:         string;
  // Payload fields set when button is clicked
  chatQuery?:        string;
  absEntityType?:    "Indian" | "Foreign";
  absResourceSource?: "Cultivated" | "Wild";
  biopiracyClaim?:   string;
}

const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id:          "classification",
    emoji:       "📋",
    label:       "Classification",
    description: "Polyherbal: Ashwagandha + Guduchi",
    tab:         "formulation",
  },
  {
    id:               "abs",
    emoji:            "🌿",
    label:            "ABS Check",
    description:      "Foreign entity, Curcuma longa (wild)",
    tab:              "abs",
    absEntityType:    "Foreign",
    absResourceSource: "Wild",
  },
  {
    id:              "biopiracy",
    emoji:           "🔬",
    label:           "Biopiracy Scan",
    description:     "Curcuma longa wound-healing claim",
    tab:             "biopiracy",
    biopiracyClaim:
      "Topical therapeutic formulation comprising 15% Curcuma longa extract for accelerating dermal wound repair in human subjects.",
  },
  {
    id:        "rag",
    emoji:     "💬",
    label:     "Chat / RAG",
    description: "Ayurvedic supplement for diabetes",
    tab:       "chat",
    chatQuery: "I want to market an Ayurvedic dietary supplement for diabetes control. What IP protections, regulatory approvals, and ABS obligations apply?",
  },
];

// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------

export default function Dashboard() {
  // ── Core layout state ──────────────────────────────────────────────────
  const [activeTab,      setActiveTab]      = useState("chat");
  const [pdfUrl,         setPdfUrl]         = useState<string | null>(null);
  const [pageNumber,     setPageNumber]     = useState<number | null>(null);
  const [leftPaneWidth,  setLeftPaneWidth]  = useState(50);
  const [jurisdiction,   setJurisdiction]   = useState<"india" | "international">("india");
  const [language,       setLanguage]       = useState<string>("en");

  // ── Demo panel state ───────────────────────────────────────────────────
  const [demoOpen,          setDemoOpen]          = useState(false);
  const [demoQuery,         setDemoQuery]         = useState<string | null>(null);
  const [demoClaim,         setDemoClaim]         = useState<string | null>(null);
  const [demoAbsEntity,     setDemoAbsEntity]     = useState<"Indian" | "Foreign" | null>(null);
  const [demoAbsResource,   setDemoAbsResource]   = useState<"Cultivated" | "Wild" | null>(null);

  // ── Resizer ────────────────────────────────────────────────────────────
  const resizerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const resizer = resizerRef.current;
    if (!resizer) return;
    let dragging = false;
    const onDown  = () => { dragging = true;  document.body.style.cursor = "col-resize"; };
    const onUp    = () => { dragging = false; document.body.style.cursor = "default"; };
    const onMove  = (e: MouseEvent) => {
      if (!dragging) return;
      const w = (e.clientX / window.innerWidth) * 100;
      if (w > 20 && w < 80) setLeftPaneWidth(w);
    };
    resizer.addEventListener("mousedown", onDown);
    document.addEventListener("mousemove",  onMove);
    document.addEventListener("mouseup",    onUp);
    return () => {
      resizer.removeEventListener("mousedown", onDown);
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup",   onUp);
    };
  }, []);

  // ── Handlers ───────────────────────────────────────────────────────────
  const handleCitationClick = (url: string, page: number) => {
    setPdfUrl(url);
    setPageNumber(page);
  };

  const handleEscalate = useCallback(async (messages: { role: string; content: string }[]) => {
    try {
      const body: EscalationRequest = {
        messages: messages as MessageItem[],
        session_id: `session-${Date.now()}`,
      };
      const res = await fetch(`${API_BASE_URL}/api/v1/escalate`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`Escalation failed: ${res.status}`);
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `ip-sakti-dossier-${Date.now()}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Escalation error:", err);
      alert("Failed to generate escalation PDF. Ensure the backend is running.");
    }
  }, []);

  const handleDemoClick = (scenario: DemoScenario) => {
    // Reset all demo state so repeated clicks re-fire effects
    setDemoQuery(null);
    setDemoClaim(null);
    setDemoAbsEntity(null);
    setDemoAbsResource(null);

    setActiveTab(scenario.tab);

    // Small delay so state resets propagate before new values land
    setTimeout(() => {
      if (scenario.chatQuery)        setDemoQuery(scenario.chatQuery);
      if (scenario.biopiracyClaim)   setDemoClaim(scenario.biopiracyClaim);
      if (scenario.absEntityType)    setDemoAbsEntity(scenario.absEntityType);
      if (scenario.absResourceSource) setDemoAbsResource(scenario.absResourceSource);
    }, 80);
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="bg-background text-on-background font-body-md h-screen overflow-hidden flex flex-col antialiased bg-gradient-to-br from-surface-bright to-surface-container-low">
      <Navbar
        jurisdiction={jurisdiction}
        onJurisdictionChange={setJurisdiction}
        language={language}
        onLanguageChange={setLanguage}
      />

      <main className="flex-1 flex overflow-hidden relative">
        {/* ── Left Pane ──────────────────────────────────────────────── */}
        <section
          className="flex flex-col bg-surface-container-lowest/60 backdrop-blur-sm h-full"
          style={{ width: `${leftPaneWidth}%` }}
        >
          <ToolTabs activeTab={activeTab} onTabChange={setActiveTab} />

          {/* ── 🎬 Demo Quick-Fill Panel (Chat tab only) ─────────────── */}
          {activeTab === "chat" && (
            <div className="shrink-0 border-b border-outline-variant/20">
              <button
                onClick={() => setDemoOpen(o => !o)}
                className="w-full flex items-center justify-between px-4 py-2 text-sm text-secondary hover:text-primary-container hover:bg-surface-container-low/50 transition-colors"
              >
                <span className="flex items-center gap-2 font-ui-label-bold">
                  <Zap className="w-3.5 h-3.5 text-amber-500" />
                  🎬 Demo Scenarios
                  <span className="text-xs text-secondary/60 font-normal">(instant cache-backed responses)</span>
                </span>
                <ChevronDown className={cn("w-4 h-4 transition-transform", demoOpen && "rotate-180")} />
              </button>

              {demoOpen && (
                <div className="px-4 pb-3 grid grid-cols-2 gap-2 animate-in fade-in slide-in-from-top-1 duration-150">
                  {DEMO_SCENARIOS.map(s => (
                    <button
                      key={s.id}
                      id={`demo-${s.id}`}
                      onClick={() => handleDemoClick(s)}
                      className="flex flex-col items-start gap-0.5 px-3 py-2.5 rounded-lg border border-outline-variant/40 bg-surface hover:border-primary-container/40 hover:bg-primary-container/5 hover:text-primary-container transition-all text-left group shadow-sm"
                    >
                      <span className="text-sm font-ui-label-bold group-hover:text-primary-container transition-colors">
                        {s.emoji} {s.label}
                      </span>
                      <span className="text-xs text-secondary/80 leading-tight">{s.description}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── Tab Content ───────────────────────────────────────────── */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {activeTab === "chat" && (
              <ChatInterface
                onCitationClick={handleCitationClick}
                jurisdiction={jurisdiction}
                language={language}
                onEscalate={handleEscalate}
                demoQuery={demoQuery}
              />
            )}
            {activeTab === "abs" && (
              <ABSNavigator
                demoEntityType={demoAbsEntity}
                demoResourceSource={demoAbsResource}
              />
            )}
            {activeTab === "formulation" && <FormulationClassifier />}
            {activeTab === "biopiracy"   && (
              <BiopiracyScanner demoClaim={demoClaim} />
            )}
          </div>
        </section>

        {/* ── Resizer ───────────────────────────────────────────────── */}
        <div
          ref={resizerRef}
          className="flex-shrink-0 cursor-col-resize w-2 relative z-10 hover:bg-primary-container/20 active:bg-primary-container/40 transition-colors flex items-center justify-center group"
          title="Drag to resize"
        >
          <div className="h-8 w-1 bg-outline-variant/40 rounded-full group-hover:bg-primary-container" />
        </div>

        {/* ── Right Pane (PDF Viewer) ───────────────────────────────── */}
        <section className="flex flex-col bg-surface-container/30 backdrop-blur-sm flex-1 h-full">
          <PdfViewer pdfUrl={pdfUrl} pageNumber={pageNumber} />
        </section>
      </main>
    </div>
  );
}
