export interface CitationItem {
  source: string;
  page: number;
  snippet: string;
}

export interface ChatRequest {
  query: string;
  jurisdiction?: string;
  language?: string;
  session_id?: string;
}

export interface ActionItem {
  id: string;
  label: string;
  type: "external" | "internal";
  url?: string;
  description?: string;
}

export interface ChatResponse {
  answer: string;
  citations: CitationItem[];
  pii_redacted?: boolean;
  language?: string;
  translation_active?: boolean;
  confidence_score?: number;
  confidence_band?: string;
  abstained?: boolean;
  actions?: ActionItem[];
}

// ── TKDL Biopiracy Scanner Types ─────────────────────────────────────────

export interface TKDLScanRequest {
  claim_text: string;
}

export interface MatchedRecord {
  chunk_id:    string;
  source_file: string;
  formulation: string;
  ipc_code:    string;
  tkrc_code:   string;
  similarity:  number;
  snippet:     string;
}

export interface TKDLScanResult {
  alert_score:           number;
  alert_level:           "HIGH" | "MEDIUM" | "LOW" | "NONE";
  section_3p_applicable: boolean;
  section_3p_precedent?: string;
  matched_records:       MatchedRecord[];
  recommended_action:    string;
  claim_analyzed:        string;
}

// ── BigQuery Patent Search Types ──────────────────────────────────────────

export interface PatentSearchRequest {
  claim_text: string;
}

export interface PatentRecord {
  publication_number: string;
  title: string;
  abstract: string;
  assignee: string;
  country_code: string;
  publication_date: string;
  cpc_code: string;
  source_url: string;
}

export interface PatentSearchResult {
  query: string;
  search_terms: string[];
  results: PatentRecord[];
  total_found: number;
  error?: string | null;
}

// ── Escalation Types ──────────────────────────────────────────────────────

export interface MessageItem {
  role:    "user" | "assistant";
  content: string;
}

export interface EscalationRequest {
  messages:           MessageItem[];
  citations?:          CitationItem[];
  session_id?:         string;
}
