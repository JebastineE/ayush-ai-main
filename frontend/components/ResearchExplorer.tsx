"use client";

import { useState, useEffect } from "react";
import { Search, Loader2, ExternalLink, BookOpen, User, Calendar, Book, Unlock } from "lucide-react";
import { ResearchSearchResult } from "@/types";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

interface ResearchExplorerProps {
  demoQuery?: string | null;
}

export function ResearchExplorer({ demoQuery }: ResearchExplorerProps) {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [result, setResult] = useState<ResearchSearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-fill and search if demo query provided
  useEffect(() => {
    if (demoQuery) {
      setQuery(demoQuery);
      handleSearch(demoQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demoQuery]);

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/research-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data: ResearchSearchResult = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch research literature. Ensure backend is running.");
    } finally {
      setIsSearching(false);
    }
  };

  const getSourceColor = (source: string) => {
    if (source.includes("Europe PMC")) return "bg-blue-100 text-blue-800 border-blue-200";
    if (source.includes("OpenAlex")) return "bg-purple-100 text-purple-800 border-purple-200";
    if (source.includes("Crossref")) return "bg-amber-100 text-amber-800 border-amber-200";
    return "bg-gray-100 text-gray-800 border-gray-200";
  };

  return (
    <div className="flex-1 overflow-y-auto bg-surface flex flex-col relative h-full">
      <div className="p-8 max-w-4xl mx-auto w-full flex-1">
        
        {/* Header section */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center justify-center p-3 bg-primary-container/10 rounded-2xl mb-4">
            <BookOpen className="w-8 h-8 text-primary-container" />
          </div>
          <h1 className="text-3xl font-display-md text-on-surface mb-3">Research Explorer</h1>
          <p className="text-secondary max-w-2xl mx-auto text-sm leading-relaxed">
            Simultaneously search Europe PMC, OpenAlex, and Crossref to discover peer-reviewed literature, clinical studies, and academic research relevant to Ayurveda and traditional medicine.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative mb-8 shadow-sm rounded-xl max-w-2xl mx-auto group">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-secondary group-focus-within:text-primary-container transition-colors" />
          </div>
          <input
            type="text"
            className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded-xl py-4 pl-12 pr-24 focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all text-on-surface font-body-md"
            placeholder="Search for compounds, plants, or clinical studies..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSearch();
            }}
            disabled={isSearching}
          />
          <button
            onClick={() => handleSearch()}
            disabled={isSearching || !query.trim()}
            className="absolute right-2 top-2 bottom-2 bg-primary-container text-white px-4 rounded-lg font-ui-label-bold text-ui-label-sm hover:bg-primary transition-colors disabled:opacity-50"
          >
            {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : "Search"}
          </button>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm mb-6 text-center max-w-2xl mx-auto">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between mb-6 pb-2 border-b border-outline-variant/30">
              <h2 className="text-lg font-display-sm">
                Found {result.records.length} publications
              </h2>
              <span className="text-xs text-secondary bg-surface-container-low px-2.5 py-1 rounded-md border border-outline-variant/20">
                Deduplicated across sources
              </span>
            </div>

            {result.records.length === 0 ? (
              <div className="text-center p-12 bg-surface-container-lowest rounded-2xl border border-dashed border-outline-variant/50">
                <p className="text-secondary">No publications found for this query.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {result.records.map((record, i) => (
                  <div key={i} className="bg-surface-container-lowest p-5 rounded-2xl border border-outline-variant/40 hover:border-primary-container/30 transition-colors shadow-sm group relative">
                    
                    {/* Removed absolute single-source badge */}

                    {/* Title */}
                    <h3 className="text-lg font-display-sm text-on-surface mb-2 leading-snug">
                      {record.title}
                    </h3>
                    
                    {/* Metadata: Authors, Year, Journal */}
                    <div className="flex flex-col gap-1.5 mb-3">
                      {record.authors && record.authors.length > 0 && (
                        <div className="flex items-start gap-1.5 text-sm text-secondary">
                          <User className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <span className="line-clamp-1">{record.authors.join(", ")}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-4 text-xs text-secondary/80">
                        {record.year && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {record.year}
                          </span>
                        )}
                        {record.journal && (
                          <span className="flex items-center gap-1 line-clamp-1">
                            <Book className="w-3.5 h-3.5" />
                            <span className="italic">{record.journal}</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Abstract */}
                    <div className="text-sm text-on-surface/80 leading-relaxed mb-4 bg-surface-container-low/30 p-3 rounded-lg border border-outline-variant/20">
                      {record.abstract}
                    </div>

                    {/* Available On Sources */}
                    {(record.sources && record.sources.length > 0) ? (
                      <div className="flex items-center gap-2 mb-4">
                        <span className="text-xs font-medium text-secondary">Available on:</span>
                        <div className="flex flex-wrap gap-2">
                          {record.sources.map(src => {
                            const srcUrl = record.source_urls?.[src];
                            if (!srcUrl) return null;
                            return (
                              <a
                                key={src}
                                href={srcUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={cn(
                                  "px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider hover:opacity-80 transition-opacity border",
                                  getSourceColor(src)
                                )}
                              >
                                {src}
                              </a>
                            );
                          })}
                        </div>
                      </div>
                    ) : null}

                    {/* Footer Actions */}
                    <div className="flex items-center gap-4 mt-2">
                      {record.doi && (
                        <span className="text-xs font-mono text-secondary bg-surface-container-low px-2 py-1 rounded">
                          DOI: {record.doi}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
