from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from enum import Enum
from datetime import datetime


class EntityType(str, Enum):
    INDIAN = "Indian"
    FOREIGN = "Foreign"


class ResourceSource(str, Enum):
    CULTIVATED = "Cultivated"
    WILD = "Wild"


class FormulationRequest(BaseModel):
    ingredients: List[str]
    source_text: Optional[str] = None
    intended_use: str


class ABSRequest(BaseModel):
    entity_type: EntityType
    resource_source: ResourceSource


class ComplianceResponse(BaseModel):
    classification: str
    statutory_provision: str
    ip_posture: Optional[str] = None
    abs_duties: Optional[str] = None
    required_forms: List[str] = Field(default_factory=list)
    approval_timeline: str
    recommended_next_steps: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    query: str
    jurisdiction: Optional[str] = "india"
    language: Optional[str] = "en"
    formulation_context: Optional[str] = None


class CitationItem(BaseModel):
    source: str
    page: int
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem]
    pii_redacted: bool = False
    language: Optional[str] = "en"
    translation_active: bool = False
    confidence_score: float = 0.0
    confidence_band: str = "VERY_LOW"
    abstained: bool = False


# ── Wizard Schemas ────────────────────────────────────────────────────────

class WizardState(BaseModel):
    """Current state of the multi-step formulation diagnostic wizard."""
    current_step: int = Field(1, ge=1, description="1-indexed current step number")
    answers: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Map of field_name → answer_value collected so far"
    )


class WizardStepOption(BaseModel):
    value: str
    label: str


class WizardStepDefinition(BaseModel):
    step: int
    question: str
    field: str
    options: List[WizardStepOption]
    hint: Optional[str] = None


class WizardResponse(BaseModel):
    """Response from the wizard engine for a given state."""
    is_complete: bool
    total_steps: int
    current_step: Optional[int] = None
    next_step: Optional[Any] = None   # WizardStepDefinition dict when not complete
    result: Optional[ComplianceResponse] = None


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


# ── Escalation Dossier Schemas ────────────────────────────────────────────

class MessageItem(BaseModel):
    """A single chat message for the escalation dossier."""
    role:    str   # 'user' | 'assistant'
    content: str


class EscalationRequest(BaseModel):
    """Request payload for the Human IP Facilitator escalation PDF."""
    messages:           List[MessageItem]
    formulation_result: Optional[ComplianceResponse] = None
    citations:          Optional[List[CitationItem]]  = None
    session_id:         Optional[str]                 = None
