"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Bot, ShieldCheck, Shield, Globe, AlertCircle, FileText, Download } from "lucide-react";
import { ChatRequest, ChatResponse } from "@/types";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

interface ChatInterfaceProps {
  onCitationClick: (pdfUrl: string, pageNumber: number) => void;
  jurisdiction: "india" | "international";
  language: string;
  /** Called when user requests Human IP Facilitator escalation. */
  onEscalate?: (messages: Message[]) => void;
  /** When set, auto-sends this query (demo quick-fill). */
  demoQuery?: string | null;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  cacheHit?: boolean;
  citations?: ChatResponse["citations"];
  piiRedacted?: boolean;
  translationActive?: boolean;
  language?: string;
}

const DEMO_PILLS = [
  "Can I patent a novel Ashwagandha formulation?",
  "ABS duties for a wild-harvested Giloy extract",
  "Section 3(p) bar — what does it mean for classical formulas?",
  "WIPO GRATK Treaty and Indian traditional knowledge",
  "GI registration for a region-specific Ayurvedic preparation",
];

const LEGAL_DISCLAIMER_FOOTER = (
  <div className="mt-3 pt-3 border-t border-outline-variant/30 flex items-start gap-2">
    <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
    <p className="text-xs text-secondary leading-relaxed">
      <span className="font-semibold text-amber-700">Legal Disclaimer:</span>{" "}
      This response is for informational purposes only and does{" "}
      <strong>not</strong> constitute legal advice. Always consult a qualified IP
      attorney or the relevant statutory authority before taking legal action.
    </p>
  </div>
);

export function ChatInterface({
  onCitationClick,
  jurisdiction,
  language,
  onEscalate,
  demoQuery,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const autoFiredRef = useRef<string | null>(null);

  // Auto-send demo query when changed (fires once per unique value)
  useEffect(() => {
    if (demoQuery && demoQuery !== autoFiredRef.current) {
      autoFiredRef.current = demoQuery;
      sendMessage(demoQuery);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demoQuery]);

  const sendMessage = async (query: string) => {
    if (!query.trim()) return;

    const userMsg: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const payload: ChatRequest = {
        query,
        jurisdiction,
        language,
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const isCacheHit = response.headers.get("X-Cache-Status") === "HIT";
      const data: ChatResponse = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          cacheHit: isCacheHit,
          citations: data.citations,
          piiRedacted: data.pii_redacted,
          translationActive: data.translation_active,
          language: data.language,
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Error communicating with backend. Is it running on port 8000?",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCitationClick = (filename: string, pageNum: number) => {
    // Route into the right-hand PdfViewer pane via the parent handler
    onCitationClick(`${API_BASE_URL}/docs/${encodeURIComponent(filename)}`, pageNum);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* Jurisdiction Banner */}
      <div
        className={cn(
          "flex items-center gap-2 px-4 py-2 text-xs font-semibold border-b shrink-0",
          jurisdiction === "india"
            ? "bg-blue-500/5 border-blue-500/20 text-blue-700"
            : "bg-purple-500/5 border-purple-500/20 text-purple-700"
        )}
      >
        <Globe className="w-3.5 h-3.5" />
        {jurisdiction === "india"
          ? "🇮🇳 Indian Law — Patents Act, BD Act, GI, Trade Marks, AYUSH, FSSAI"
          : "🌐 International Treaties — TRIPS, CBD, Nagoya, WIPO GRATK, PCT, Madrid, Hague"}
        <span className="ml-auto opacity-60">
          Results filtered to this jurisdiction only
        </span>
      </div>

      {/* Message History */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 flex flex-col">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={cn(
              "flex",
              msg.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[85%] rounded-2xl p-5 shadow-sm border",
                msg.role === "user"
                  ? "bg-primary-container text-white rounded-tr-sm border-transparent"
                  : "bg-surface/80 backdrop-blur-md text-on-surface rounded-tl-sm border-outline-variant/30"
              )}
            >
              {msg.role === "assistant" && (
                <div className="flex items-center gap-2 mb-4 flex-wrap">
                  <Bot className="text-primary-container w-4 h-4" />
                  <span className="font-ui-label-bold text-ui-label-bold text-primary-container">
                    IP-SAKTI Sahayak
                  </span>

                  <div className="flex gap-2 ml-auto flex-wrap">
                    {/* Cache Status */}
                    {msg.cacheHit !== undefined && (
                      <span
                        className={cn(
                          "px-2.5 py-1 rounded-full text-ui-label-sm font-ui-label-bold flex items-center gap-1.5 border",
                          msg.cacheHit
                            ? "bg-green-500/10 text-green-700 border-green-500/20"
                            : "bg-amber-500/10 text-amber-700 border-amber-500/20"
                        )}
                      >
                        <span
                          className={cn(
                            "w-1.5 h-1.5 rounded-full",
                            msg.cacheHit ? "bg-green-500" : "bg-amber-500"
                          )}
                        />
                        {msg.cacheHit ? "Cache Hit" : "Cache Miss"}
                      </span>
                    )}

                    {/* Grounded badge */}
                    <span className="px-2.5 py-1 rounded-full bg-primary-container/10 text-primary-container text-ui-label-sm font-ui-label-bold flex items-center gap-1.5 border border-primary-container/20">
                      <ShieldCheck className="w-3 h-3" />
                      Grounded
                    </span>

                    {/* PII Redacted badge */}
                    {msg.piiRedacted && (
                      <span className="px-2.5 py-1 rounded-full bg-red-500/10 text-red-700 text-ui-label-sm font-ui-label-bold flex items-center gap-1.5 border border-red-500/20">
                        <Shield className="w-3 h-3" />
                        PII Redacted
                      </span>
                    )}

                    {/* Translation badge */}
                    {msg.translationActive && (
                      <span className="px-2.5 py-1 rounded-full bg-teal-500/10 text-teal-700 text-ui-label-sm font-ui-label-bold flex items-center gap-1.5 border border-teal-500/20">
                        <Globe className="w-3 h-3" />
                        Translated ({msg.language?.toUpperCase()})
                      </span>
                    )}
                  </div>
                </div>
              )}

              <div className="space-y-4 font-body-md whitespace-pre-wrap text-sm">
                {msg.content}
              </div>

              {/* Citations */}
              {msg.role === "assistant" &&
                msg.citations &&
                msg.citations.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-outline-variant/30 flex flex-wrap gap-2">
                    <span className="font-ui-label-sm text-secondary w-full">
                      Citations:
                    </span>
                    {msg.citations.map((cit: any, idx: number) => (
                      <button
                        key={idx}
                        onClick={() =>
                          handleCitationClick(cit.source, cit.page)
                        }
                        className="inline-flex items-center px-2 py-1 rounded-md bg-surface-container-low border border-outline-variant/50 font-mono-label text-mono-label text-secondary hover:bg-primary-container/5 hover:border-primary-container/30 hover:text-primary-container transition-all cursor-pointer shadow-sm text-xs"
                      >
                        📄 {cit.source} (p. {cit.page})
                      </button>
                    ))}
                  </div>
                )}

              {/* Escalation Button */}
              {msg.role === "assistant" && (
                <div className="mt-5 pt-4 border-t border-outline-variant/30 flex items-center justify-between">
                  <button
                    id="escalate-btn"
                    onClick={() => onEscalate?.(messages)}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-outline-variant/50 text-secondary hover:text-primary-container hover:bg-surface-container-low/50 hover:border-primary-container/30 transition-all font-ui-label-bold text-ui-label-bold shadow-sm text-sm"
                  >
                    <Download className="w-4 h-4" />
                    Escalate to Human IP Facilitator
                  </button>
                </div>
              )}

              {/* Mandatory Legal Disclaimer Footer */}
              {msg.role === "assistant" && LEGAL_DISCLAIMER_FOOTER}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-surface/80 p-5 rounded-2xl rounded-tl-sm shadow-sm border border-outline-variant/30">
              <p className="text-secondary animate-pulse text-sm">
                Generating grounded response via hybrid RAG…
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-surface/70 backdrop-blur-md border-t border-outline-variant/30 shrink-0">
        <div className="flex gap-2 overflow-x-auto pb-3 scrollbar-hide">
          {DEMO_PILLS.map((pill) => (
            <button
              key={pill}
              onClick={() => setInput(pill)}
              className="whitespace-nowrap px-3 py-1.5 rounded-md bg-surface border border-outline-variant/40 text-ui-label-sm font-ui-label-bold text-secondary hover:border-primary-container hover:text-primary-container transition-all shadow-sm text-xs"
            >
              {pill}
            </button>
          ))}
        </div>

        <div className="relative flex items-center">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage(input);
              }
            }}
            className="w-full bg-surface-container-lowest/80 backdrop-blur-sm border border-outline-variant/40 rounded-xl py-3 pl-4 pr-12 focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container font-body-md text-on-surface resize-none shadow-sm transition-all text-sm"
            placeholder={`Ask a ${jurisdiction === "india" ? "Indian IP/AYUSH law" : "international IP treaty"} question…`}
            rows={2}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={isLoading || !input.trim()}
            className="absolute right-3 bottom-3 text-white bg-primary-container rounded-lg p-2 hover:bg-primary transition-colors flex items-center justify-center shadow-md disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
