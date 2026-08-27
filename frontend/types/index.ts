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

export interface ClassificationResult {
  category:             string;
  regulatory_path:      string;
  ip_status:            string;
  abs_requirement:      string;
  gemini_explanation:   string;
  needs_review:         boolean;
}

export interface TriageChatRequest {
  session_id:     string;
  current_step:   number;
  answers:        Record<string, string>;
  latest_answer?: string;
}

export interface TriageChatResponse {
  session_id:              string;
  is_complete:             boolean;
  current_step:            number;
  total_steps:             number;
  next_question?:          string;
  next_step?:              number;
  classification_result?:  ClassificationResult;
  answers:                 Record<string, string>;
}

// ── Research Explorer Types ──────────────────────────────────────────────

export interface ResearchSearchRequest {
  query: string;
}

export interface PublicationRecord {
  title: string;
  authors: string[];
  year?: number;
  journal?: string;
  abstract: string;
  url: string;
  doi: string;
  source: string;
  sources?: string[];
  source_urls?: Record<string, string>;
  open_access?: boolean;
}

export interface ResearchSearchResult {
  query_analyzed: string;
  records: PublicationRecord[];
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
