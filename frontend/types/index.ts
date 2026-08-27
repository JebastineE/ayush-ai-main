export interface CitationItem {
  source: string;
  page: number;
  snippet: string;
}

export interface ChatRequest {
  query: string;
  jurisdiction?: string;
  language?: string;
  formulation_context?: string;
}

export interface ChatResponse {
  answer: string;
  citations: CitationItem[];
  pii_redacted?: boolean;
  language?: string;
  translation_active?: boolean;
}

export interface FormulationRequest {
  ingredients: string[];
  source_text?: string;
  intended_use: string;
}

export interface ABSRequest {
  entity_type: "Indian" | "Foreign";
  resource_source: "Cultivated" | "Wild";
}

export interface ComplianceResponse {
  classification: string;
  statutory_provision: string;
  ip_posture?: string;
  abs_duties?: string;
  required_forms: string[];
  approval_timeline: string;
  recommended_next_steps?: string[];
}

// ── Wizard Types ─────────────────────────────────────────────────────────

export interface WizardStepOption {
  value: string;
  label: string;
}

export interface WizardStepDefinition {
  step: number;
  question: string;
  field: string;
  options: WizardStepOption[];
  hint?: string;
}

export interface WizardState {
  current_step: number;
  answers: Record<string, string>;
}

export interface WizardResponse {
  is_complete: boolean;
  total_steps: number;
  current_step?: number;
  next_step?: WizardStepDefinition;
  result?: ComplianceResponse;
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

// ── Escalation Types ──────────────────────────────────────────────────────

export interface MessageItem {
  role:    "user" | "assistant";
  content: string;
}

export interface EscalationRequest {
  messages:           MessageItem[];
  formulation_result?: ComplianceResponse;
  citations?:          CitationItem[];
  session_id?:         string;
}

