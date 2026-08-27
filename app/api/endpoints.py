from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
import io
from app.schemas.payloads import (
    ABSRequest,
    FormulationRequest,
    ComplianceResponse,
    ChatRequest,
    ChatResponse,
    WizardState,
    WizardResponse,
    TKDLScanRequest,
    TKDLScanResult,
    EscalationRequest,
)
from app.services.rules_engine import (
    evaluate_abs_compliance,
    classify_formulation,
    run_wizard_step,
    WIZARD_STEPS,
)
from app.middleware.cache import process_chat_with_cache
from app.middleware.dpdp import scrub_pii
from app.services.translation import translate_to_english, translate_to_source_lang
from app.services.biopiracy_scanner import scan_patent_claim
from app.services.escalation import generate_escalation_pdf
from app.db.sqlite_cache import get_cache_stats

router = APIRouter()


# ── ABS Compliance Check ─────────────────────────────────────────────────

@router.post("/api/v1/abs-check", response_model=ComplianceResponse)
async def abs_check(request: ABSRequest):
    return evaluate_abs_compliance(request)


# ── Legacy Single-Shot Classifier ────────────────────────────────────────

@router.post("/api/v1/classify", response_model=ComplianceResponse)
async def classify(request: FormulationRequest):
    return classify_formulation(request)


# ── Multi-Step Wizard ─────────────────────────────────────────────────────

@router.post("/api/v1/classify/wizard", response_model=WizardResponse)
async def classify_wizard(state: WizardState):
    """
    Interactive multi-step formulation diagnostic wizard.
    POST the current WizardState; receive the next question or final result.
    """
    return run_wizard_step(state)


@router.get("/api/v1/classify/wizard/steps")
async def get_wizard_steps():
    """Return all wizard step definitions for frontend pre-loading."""
    return {"steps": WIZARD_STEPS, "total": len(WIZARD_STEPS)}


# ── Chat (RAG + DPDP + Translation) ──────────────────────────────────────

@router.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, response: Response):
    """
    Full RAG chat endpoint with:
      - DPDP PII scrubbing on incoming query
      - Bhashini translation (vernacular → English → vernacular)
      - Jurisdiction-filtered hybrid retrieval
      - Legal disclaimer injected by RAG layer
      - DPDP PII scrubbing on outgoing response
    """
    # 1. Scrub PII from incoming query
    clean_query, query_pii_types = scrub_pii(request.query)
    pii_was_redacted = bool(query_pii_types)

    # 2. Translate vernacular input to English (no-op if lang=en or no key)
    source_lang = request.language or "en"
    english_query = translate_to_english(clean_query)

    # 3. Process via RAG (with jurisdiction filter + DPDP on response)
    rag_result = await process_chat_with_cache(
        query=english_query,
        response=response,
        jurisdiction=request.jurisdiction or "india",
    )

    # 4. Scrub PII from outgoing answer
    clean_answer, answer_pii_types = scrub_pii(rag_result.get("answer", ""))
    if answer_pii_types:
        pii_was_redacted = True

    # 5. Translate response back to source language
    final_answer = translate_to_source_lang(
        clean_answer,
        target_lang=source_lang,
    )

    return ChatResponse(
        answer=final_answer,
        citations=rag_result.get("citations", []),
        pii_redacted=pii_was_redacted,
        language=source_lang,
        translation_active=(source_lang != "en"),
        confidence_score=rag_result.get("confidence_score", 0.0),
        confidence_band=rag_result.get("confidence_band", "VERY_LOW"),
        abstained=rag_result.get("abstained", False),
    )


# ── TKDL Biopiracy Scanner ────────────────────────────────────────────────

@router.post("/api/v1/tkdl-scan", response_model=TKDLScanResult)
async def tkdl_scan(request: TKDLScanRequest):
    """
    Scan a patent claim against the TKDL vector database.
    Returns a biopiracy alert score (0–100), alert level, matched prior-art
    records, and the applicable Section 3(p) precedent.
    DPDP PII scrubbing applied to the claim text before scanning.
    """
    clean_claim, _ = scrub_pii(request.claim_text)
    result = scan_patent_claim(clean_claim)
    return TKDLScanResult(**result)


# ── Human IP Facilitator Escalation ───────────────────────────────────

@router.post("/api/v1/escalate")
async def escalate(request: EscalationRequest):
    """
    Generate and return a PDF dossier for Human IP Facilitator review.
    Includes: formulation classification, full chat transcript, citations.
    Uses DPDP PII scrubbing on all message content before PDF generation.
    """
    # Scrub PII from all message content before embedding in the PDF
    scrubbed_messages = [
        {"role": m.role, "content": scrub_pii(m.content)[0]}
        for m in request.messages
    ]
    formulation_dict = (
        request.formulation_result.model_dump() if request.formulation_result else None
    )
    citations_list = (
        [c.model_dump() for c in request.citations] if request.citations else None
    )

    pdf_bytes = generate_escalation_pdf(
        messages=scrubbed_messages,
        formulation_result=formulation_dict,
        citations=citations_list,
        session_id=request.session_id,
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="ips-escalation-dossier.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


# ── Cache Diagnostics ──────────────────────────────────────────────────────

@router.get("/api/v1/cache/stats")
async def cache_stats():
    """Return shadow-cache statistics. Used for pre-warm verification."""
    return get_cache_stats()
