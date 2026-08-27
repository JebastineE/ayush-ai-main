from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from enum import Enum
from datetime import datetime


class ChatRequest(BaseModel):
    query: str
    jurisdiction: Optional[str] = "india"
    language: Optional[str] = "en"
    session_id: Optional[str] = None


class CitationItem(BaseModel):
    source: str
    page: int
    snippet: str


class ActionItem(BaseModel):
    """Actionable resource suggestion"""
    id: str
    label: str
    type: str  # "external" or "internal"
    url: Optional[str] = None  # Only for external actions
    description: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem]
    pii_redacted: bool = False
    language: Optional[str] = "en"
    translation_active: bool = False
    confidence_score: float = 0.0
    confidence_band: str = "VERY_LOW"
    abstained: bool = False
    actions: List[ActionItem] = Field(default_factory=list)  # NEW: Actionable resources


# ── TKDL Biopiracy Scanner Schemas ───────────────────────────────────────

class TKDLScanRequest(BaseModel):
    """Request payload for the TKDL biopiracy scanner."""
    claim_text: str = Field(
        ...,
        min_length=20,
        description="The full text of the patent claim to scan for biopiracy.",
        examples=["Topical formulation comprising 15% Curcuma longa extract for wound repair."],
    )


class MatchedRecord(BaseModel):
    """A single TKDL prior-art record returned by the scanner."""
    chunk_id:    str
    source_file: str
    formulation: str
    ipc_code:    str
    tkrc_code:   str
    similarity:  float  # 0–100
    snippet:     str


class TKDLScanResult(BaseModel):
    """Full biopiracy scan result with alert level and prior art citations."""
    alert_score:           float             # 0.0–100.0
    alert_level:           str               # HIGH | MEDIUM | LOW | NONE
    section_3p_applicable: bool
    section_3p_precedent:  Optional[str]     = None
    matched_records:       List[MatchedRecord] = Field(default_factory=list)
    recommended_action:    str
    claim_analyzed:        str


# ── BigQuery Patent Search Schemas ───────────────────────────────────────

class PatentSearchRequest(BaseModel):
    """Request payload for BigQuery patent search."""
    claim_text: str = Field(
        ...,
        min_length=10,
        description="The formulation or patent claim text to search for related patents.",
    )


class PatentRecord(BaseModel):
    """A single patent record from Google Patents Public Dataset."""
    publication_number: str
    title: str
    abstract: str
    assignee: str
    country_code: str
    publication_date: str
    cpc_code: str
    source_url: str


class PatentSearchResult(BaseModel):
    """BigQuery patent search results."""
    query: str
    search_terms: List[str] = Field(default_factory=list)
    results: List[PatentRecord] = Field(default_factory=list)
    total_found: int = 0
    error: Optional[str] = None


# ── Escalation Dossier Schemas ────────────────────────────────────────────

class MessageItem(BaseModel):
    """A single chat message for the escalation dossier."""
    role:    str   # 'user' | 'assistant'
    content: str


class EscalationRequest(BaseModel):
    """Request payload for the Human IP Facilitator escalation PDF."""
    messages:           List[MessageItem]
    citations:          Optional[List[CitationItem]]  = None
    session_id:         Optional[str]                 = None

# ── Research Explorer Schemas ───────────────────────────────────────────────

class ResearchSearchRequest(BaseModel):
    query: str

class PublicationRecord(BaseModel):
    title: str
    authors: List[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    abstract: str
    url: str
    doi: str
    source: str
    sources: List[str] = Field(default_factory=list)
    source_urls: Dict[str, str] = Field(default_factory=dict)
    open_access: bool = False

class ResearchSearchResult(BaseModel):
    query_analyzed: str
    records: List[PublicationRecord]
