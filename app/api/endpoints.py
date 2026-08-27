from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import io
from app.schemas.payloads import (
    ChatRequest,
    ChatResponse,
    TKDLScanRequest,
    TKDLScanResult,
    PatentSearchRequest,
    PatentSearchResult,
    EscalationRequest,
    ActionItem,
    ResearchSearchRequest,
    ResearchSearchResult,
)
from app.middleware.cache import process_chat_with_cache
from app.middleware.dpdp import scrub_pii
from app.services.translation import translate_to_english, translate_to_source_lang
from app.services.biopiracy_scanner import scan_patent_claim
from app.services.patent_search_bigquery import search_patents_bigquery
from app.services.escalation import generate_escalation_pdf
from app.db.sqlite_cache import get_cache_stats
from app.services.memory import memory_manager
from app.services.action_selector import suggest_actions
from app.services.action_resources import get_action_suggestions
from app.services.research_explorer import search_research_literature

router = APIRouter()


# ── Chat (RAG + DPDP + Translation) ──────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
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
        deterministic_context=None,
        session_id=request.session_id,
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

    # 6. Suggest relevant actions based on RAG result
    action_ids = suggest_actions(
        query=english_query,
        answer=clean_answer,
        citations=rag_result.get("citations", []),
        confidence_score=rag_result.get("confidence_score", 0.0),
        abstained=rag_result.get("abstained", False)
    )
    action_metadata = get_action_suggestions(action_ids)
    # Convert ActionMetadata to ActionItem for response
    actions = [
        ActionItem(
            id=a.id,
            label=a.label,
            type=a.type,
            url=a.url,
            description=a.description
        )
        for a in action_metadata
    ]

    # 7. Save turn to memory
    if request.session_id:
        memory_manager.add_turn(
            session_id=request.session_id,
            role="user",
            content=request.query,
            normalized_content=english_query
        )
        memory_manager.add_turn(
            session_id=request.session_id,
            role="assistant",
            content=final_answer
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
        actions=actions,
    )


# ── TKDL Biopiracy Scanner ────────────────────────────────────────────────

@router.post("/tkdl-scan", response_model=TKDLScanResult)
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


# ── BigQuery Patent Search ────────────────────────────────────────────

@router.post("/patent-search", response_model=PatentSearchResult)
async def patent_search(request: PatentSearchRequest):
    """
    Search Google Patents Public Dataset via BigQuery for related patent records.
    This endpoint is ONLY used by the Biopiracy Scanner.
    Returns potentially related patent records based on the submitted formulation.

    IMPORTANT: Results are for review purposes only and do not constitute
    a determination of biopiracy, patent infringement, or legal validity.
    """
    clean_claim, _ = scrub_pii(request.claim_text)
    result = search_patents_bigquery(clean_claim)
    return PatentSearchResult(**result)


# ── Research Explorer ──────────────────────────────────────────────────

@router.post("/research-search", response_model=ResearchSearchResult)
async def research_search(request: ResearchSearchRequest):
    """
    Search across multiple academic databases concurrently.
    """
    clean_query, _ = scrub_pii(request.query)
    result = await search_research_literature(clean_query)
    return result


# ── Human IP Facilitator Escalation ───────────────────────────────────

@router.post("/escalate")
async def escalate(request: EscalationRequest):
    """
    Generate and return a PDF dossier for Human IP Facilitator review.
    Includes: chat transcript and citations.
    Uses DPDP PII scrubbing on all message content before PDF generation.
    """
    # Scrub PII from all message content before embedding in the PDF
    scrubbed_messages = [
        {"role": m.role, "content": scrub_pii(m.content)[0]}
        for m in request.messages
    ]
    citations_list = (
        [c.model_dump() for c in request.citations] if request.citations else None
    )

    pdf_bytes = generate_escalation_pdf(
        messages=scrubbed_messages,
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

@router.get("/cache/stats")
async def cache_stats():
    """Return shadow-cache statistics. Used for pre-warm verification."""
    return get_cache_stats()
