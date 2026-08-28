"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Bot, ShieldCheck, Shield, Globe, AlertCircle } from "lucide-react";
import { v4 as uuidv4 } from "uuid";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatRequest, ChatResponse, ActionItem } from "@/types";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";
import { ActionResources } from "./ActionResources";

interface ChatInterfaceProps {
  onCitationClick: (pdfUrl: string, pageNumber: number) => void;
  jurisdiction: "india" | "international";
  language: string;
  /** Called when user requests Human IP Facilitator escalation. */
  onEscalate?: (messages: Message[]) => void;
  /** Called when user wants to open TKDL Biopiracy Scanner. */
  onOpenTKDLScanner?: () => void;
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
  confidenceScore?: number;
  confidenceBand?: string;
  abstained?: boolean;
  actions?: ActionItem[];
}

const DEMO_PILLS = [
  "Can I patent a novel Ashwagandha formulation?",
  "ABS duties for a wild-harvested Giloy extract",
  "Section 3(p) bar — what does it mean for classical formulas?",
  "WIPO GRATK Treaty and Indian traditional knowledge",
  "GI registration for a region-specific Ayurvedic preparation",
];

export function ChatInterface({
  onCitationClick,
  jurisdiction,
  language,
  onEscalate,
  onOpenTKDLScanner,
  demoQuery,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const autoFiredRef = useRef<string | null>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  // Initialize sessionId on mount
  useEffect(() => {
    setSessionId(uuidv4());
  }, []);

  // Auto-scroll
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

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
        session_id: sessionId,
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
          confidenceScore: data.confidence_score,
          confidenceBand: data.confidence_band,
          abstained: data.abstained,
          actions: data.actions,
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
    onCitationClick(`${API_BASE_URL}/api/v1/document/${encodeURIComponent(filename)}`, pageNum);
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(uuidv4());
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
                    {/* Confidence badge */}
                    {msg.confidenceScore !== undefined && !msg.abstained && (
                      <span
                        className={cn(
                          "px-2.5 py-1 rounded-full text-ui-label-sm font-ui-label-bold flex items-center gap-1.5 border",
                          msg.confidenceBand === "HIGH"
                            ? "bg-green-500/10 text-green-700 border-green-500/20"
                            : msg.confidenceBand === "MEDIUM"
                            ? "bg-blue-500/10 text-blue-700 border-blue-500/20"
                            : msg.confidenceBand === "LOW"
                            ? "bg-amber-500/10 text-amber-700 border-amber-500/20"
                            : "bg-red-500/10 text-red-700 border-red-500/20"
                        )}
                      >
                        <ShieldCheck className="w-3 h-3" />
                        {msg.confidenceBand && msg.confidenceBand.charAt(0) + msg.confidenceBand.slice(1).toLowerCase()} · {msg.confidenceScore?.toFixed(1)}%
                      </span>
                    )}

                    {/* Abstained badge */}
                    {msg.abstained && (
                      <span className="px-2.5 py-1 rounded-full bg-red-500/10 text-red-700 text-ui-label-sm font-ui-label-bold flex items-center gap-1.5 border border-red-500/20">
                        <AlertCircle className="w-3 h-3" />
                        Abstained
                      </span>
                    )}

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

              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Customize heading styles
                    h1: ({ node, ...props }) => <h1 className="text-xl font-bold mt-4 mb-2 text-gray-900" {...props} />,
                    h2: ({ node, ...props }) => <h2 className="text-lg font-bold mt-3 mb-2 text-gray-900" {...props} />,
                    h3: ({ node, ...props }) => <h3 className="text-base font-semibold mt-2 mb-1 text-gray-800" {...props} />,
                    // List styles
                    ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1 my-2" {...props} />,
                    ol: ({ node, ...props }) => <ol className="list-decimal list-inside space-y-1 my-2" {...props} />,
                    li: ({ node, ...props }) => <li className="text-sm text-gray-700 leading-relaxed" {...props} />,
                    // Paragraph styles
                    p: ({ node, ...props }) => <p className="text-sm text-gray-700 leading-relaxed my-2" {...props} />,
                    // Strong/bold
                    strong: ({ node, ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
                    // Links
                    a: ({ node, ...props }) => <a className="text-blue-600 hover:underline" {...props} />,
                    // Code
                    code: ({ node, inline, ...props }: any) =>
                      inline ?
                        <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-gray-800" {...props} /> :
                        <code className="block bg-gray-100 p-2 rounded text-sm font-mono text-gray-800 my-2" {...props} />,
                    // Horizontal rule
                    hr: ({ node, ...props }) => <hr className="my-4 border-gray-300" {...props} />,
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>

              {/* Citations */}
              {msg.role === "assistant" &&
                msg.citations &&
                msg.citations.length > 0 && (
                  (() => {
                    const pdfCitations = msg.citations.filter((c: any) => c.source.toLowerCase().endsWith('.pdf'));
                    const uniqueCitations: any[] = [];
                    const seen = new Set();
                    for (const c of pdfCitations) {
                      if (!seen.has(c.source)) {
                        seen.add(c.source);
                        uniqueCitations.push(c);
                      }
                    }
                    if (uniqueCitations.length === 0) return null;
                    
                    return (
                      <div className="mt-4 pt-4 border-t border-outline-variant/30">
                        <span className="font-ui-label-sm text-secondary block mb-2">
                          Sources
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {uniqueCitations.map((cit: any, idx: number) => (
                            <button
                              key={idx}
                              onClick={() =>
                                handleCitationClick(cit.source, cit.page)
                              }
                              className="inline-flex items-center px-2 py-1 rounded-md bg-surface-container-low border border-outline-variant/50 font-mono-label text-mono-label text-secondary hover:bg-primary-container/5 hover:border-primary-container/30 hover:text-primary-container transition-all cursor-pointer shadow-sm text-xs"
                            >
                              📄 {cit.source} · Page {cit.page}
                            </button>
                          ))}
                        </div>
                      </div>
                    );
                  })()
                )}

              {/* Actionable Resources */}
              {msg.role === "assistant" && msg.actions && msg.actions.length > 0 && (
                <ActionResources
                  actions={msg.actions}
                  citations={msg.citations}
                  onOpenPdfViewer={onCitationClick}
                  onOpenTKDLScanner={onOpenTKDLScanner}
                  query={i > 0 && messages[i-1]?.role === "user" ? messages[i-1].content : undefined}
                  answer={msg.content}
                />
              )}
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
        <div ref={endOfMessagesRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-surface/70 backdrop-blur-md border-t border-outline-variant/30 shrink-0">
        <div className="flex gap-2 overflow-x-auto pb-3 scrollbar-hide">
          <button
            onClick={handleNewChat}
            disabled={isLoading}
            className="whitespace-nowrap px-3 py-1.5 rounded-md bg-blue-50 border border-blue-200 text-ui-label-sm font-ui-label-bold text-blue-700 hover:border-blue-400 hover:bg-blue-100 transition-all shadow-sm text-xs flex items-center gap-1.5 disabled:opacity-50"
          >
            New Chat
          </button>
          {DEMO_PILLS.map((pill) => (
            <button
              key={pill}
              onClick={() => setInput(pill)}
              disabled={isLoading}
              className="whitespace-nowrap px-3 py-1.5 rounded-md bg-surface border border-outline-variant/40 text-ui-label-sm font-ui-label-bold text-secondary hover:border-primary-container hover:text-primary-container transition-all shadow-sm text-xs disabled:opacity-50"
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
            disabled={isLoading}
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
