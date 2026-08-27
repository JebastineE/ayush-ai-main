"""
Action Selector — Lightweight Action Relevance Suggestions
===========================================================

This module suggests relevant actions based on RAG answer content.

IMPORTANT:
- This is NOT a deterministic rule engine
- This does NOT classify formulations
- This does NOT determine ABS requirements
- This does NOT recreate the old rules_engine

It only performs lightweight keyword matching to suggest potentially
relevant next actions based on the grounded RAG answer.

The legal reasoning comes from the RAG answer itself, not from this module.
"""
from typing import List, Optional


def suggest_actions(
    query: str,
    answer: str,
    citations: List[dict],
    confidence_score: float,
    abstained: bool
) -> List[str]:
    """
    Suggest relevant action IDs based on the RAG answer content.

    This uses simple keyword matching to suggest actions. It does NOT
    make legal determinations or classifications.

    Parameters
    ----------
    query : str
        The user's original query
    answer : str
        The grounded RAG answer
    citations : List[dict]
        Retrieved citations (source, page, snippet)
    confidence_score : float
        Confidence score from cross-encoder (0-100)
    abstained : bool
        Whether the system abstained from answering

    Returns
    -------
    List[str]
        List of suggested action IDs (NOT URLs)
    """
    # If abstained, return no actions
    if abstained or confidence_score < 40.0:
        return []

    actions = []
    combined_text = (query + " " + answer).lower()

    # ── Patent-related actions ─────────────────────────────────────────────
    if any(term in combined_text for term in [
        "patent", "patentability", "patentable", "invention",
        "prior art", "novelty", "inventive step", "section 3"
    ]):
        # Suggest patent search for any patent-related query
        if "patent" in query.lower():
            actions.append("patent_search")

        # Suggest patent forms if query is about filing/application
        if any(term in query.lower() for term in [
            "file", "filing", "apply", "application", "form",
            "how to patent", "patent process", "submit"
        ]):
            actions.append("patent_forms")
            actions.append("patent_filing")

        # Suggest patent checklist if query is about preparation
        if any(term in query.lower() for term in [
            "prepare", "preparation", "ready", "check", "should i",
            "what should", "can i patent", "requirements"
        ]):
            actions.append("patent_checklist")

        # Suggest patent manual for detailed guidance
        if any(term in query.lower() for term in [
            "procedure", "process", "guide", "manual", "how to",
            "steps", "requirements"
        ]):
            actions.append("ip_india_manual")

    # ── Traditional Knowledge / TKDL actions ───────────────────────────────
    if any(term in combined_text for term in [
        "traditional knowledge", "tkdl", "section 3(p)", "biopiracy",
        "prior art", "ayurvedic formulation", "classical"
    ]):
        # Suggest TKDL scan if discussing prior art or biopiracy
        if any(term in combined_text for term in [
            "traditional knowledge", "tkdl", "biopiracy", "prior art",
            "section 3(p)", "classical formulation"
        ]):
            actions.append("tkdl_scan")

    # ── NBA / Biological Resources actions ─────────────────────────────────
    # NOTE: This does NOT classify ABS requirements
    # It only suggests the resource link if the answer discusses biological resources
    if any(term in combined_text for term in [
        "biological diversity", "biodiversity act", "nba", "biological resource",
        "access and benefit", "abs", "bioresource", "genetic resource"
    ]):
        actions.append("nba_resources")

        # Suggest NBA guidelines if query is about access/compliance
        if any(term in query.lower() for term in [
            "access", "permission", "approval", "apply", "compliance",
            "requirement", "how to", "need to"
        ]):
            actions.append("nba_access_guidelines")

    # ── FSSAI / FoSCoS actions ─────────────────────────────────────────────
    if any(term in combined_text for term in [
        "fssai", "foscos", "food safety", "ayurveda aahara", "nutraceutical",
        "food standards", "dietary supplement", "food product"
    ]):
        actions.append("foscos")

        # Suggest FSSAI regulations for regulatory/compliance queries
        if any(term in query.lower() for term in [
            "regulation", "requirement", "standard", "compliance",
            "rule", "law", "legal", "permit", "license"
        ]):
            actions.append("fssai_regulations")

    # ── Supporting Documents ───────────────────────────────────────────────
    # Suggest if there are multiple citations (user may want to review them)
    if len(citations) >= 2:
        actions.append("supporting_documents")

    # ── Preparation Draft ──────────────────────────────────────────────────
    # Suggest if query asks for preparation/draft/document generation
    if any(term in query.lower() for term in [
        "prepare", "draft", "document", "generate", "create", "help me write"
    ]):
        actions.append("preparation_draft")

    # Remove duplicates while preserving order
    seen = set()
    unique_actions = []
    for action in actions:
        if action not in seen:
            seen.add(action)
            unique_actions.append(action)

    return unique_actions
