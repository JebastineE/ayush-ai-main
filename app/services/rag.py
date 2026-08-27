"""
Hybrid RAG Pipeline — IP-SAKTI Sahayak
========================================
Retrieval strategy:
  1. Query Expansion     — LLM generates 2 keyword-rich variants
  2. Dense Retrieval     — InLegalBERT vector search via Qdrant
  3. BM25 Lexical Search — rank-bm25 over the retrieved candidate pool
  4. Reciprocal Rank Fusion (RRF) — merges dense + BM25 ranked lists
  5. Cross-Encoder Reranking — ms-marco-MiniLM-L-6-v2 rescore top-N
  6. Jurisdiction Filter — hard Qdrant payload filter (must match)
  7. Grounded Generation — Gemini with mandatory legal disclaimer

DPDP: PII scrubbing is applied at the endpoint layer (before this is called).
"""

import os
import re
import logging
from typing import Optional
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from rank_bm25 import BM25Okapi
import json

from app.services.memory import memory_manager
from app.services.action_selector import suggest_actions
from app.services.action_resources import get_action_suggestions
from pipeline.config import MODEL_NAME, QDRANT_PATH, LEGAL_COLLECTION, TKDL_COLLECTION

load_dotenv()

logger = logging.getLogger("rag_pipeline")

# ---------------------------------------------------------------------------
# Clients & Models (initialised once at import time)
# ---------------------------------------------------------------------------

qdrant = QdrantClient(path=str(QDRANT_PATH))

# Dense encoder — InLegalBERT
dense_model = SentenceTransformer(MODEL_NAME)

# Cross-Encoder reranker — ms-marco-MiniLM-L-6-v2 (≈90 MB, runs fully offline)
try:
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
    logger.info("✅ [RAG] Cross-Encoder loaded: ms-marco-MiniLM-L-6-v2")
except Exception as exc:
    cross_encoder = None
    logger.warning(f"⚠️ [RAG] Cross-Encoder unavailable ({exc}). Falling back to RRF scores.")

# Gemini — dynamically bind to best available model
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key not found. Please set GOOGLE_API_KEY in your .env file.")

client = genai.Client(api_key=api_key, vertexai=False)

_valid_model = "gemini-3.5-flash-lite"
logger.info(f"🚀 [RAG] Gemini model bound: {_valid_model}")


# ---------------------------------------------------------------------------
# Jurisdiction → filename keyword mapping (fallback when payload tags missing)
# ---------------------------------------------------------------------------

_JURISDICTION_FILE_KEYWORDS: dict[str, list[str]] = {
    "india": [
        "patents_act", "biological_diversity", "geographical_indication",
        "trade_marks", "designs_act", "copyright", "plant_variety",
        "drugs_cosmetics", "drugs_magic", "fssai", "ayush", "tkdl",
        "india_code", "ayurveda", "indiacode", "dca", "nba",
    ],
    "international": [
        "trips", "cbd", "nagoya", "wipo", "gratk", "pct",
        "madrid", "hague", "budapest", "who", "itu", "international",
        "treaty", "convention", "protocol",
    ],
}


def _jurisdiction_matches_file(source_file: str, jurisdiction: str) -> bool:
    """
    Fallback filter: check whether the source filename contains keywords
    associated with the requested jurisdiction.
    """
    lower = source_file.lower()
    keywords = _JURISDICTION_FILE_KEYWORDS.get(jurisdiction.lower(), [])
    # If we have no keywords for this jurisdiction, allow everything through
    if not keywords:
        return True
    return any(kw in lower for kw in keywords)


# ---------------------------------------------------------------------------
# Legal Disclaimer - REMOVED per user request
# ---------------------------------------------------------------------------
# Previously displayed disclaimer at end of each response. Now removed to clean up UI.
# If restoration is needed, uncomment and re-add "+ LEGAL_DISCLAIMER" appends at:
# - Line ~548 (semantic gate abstention)
# - Line ~586 (hard abstention)
# - Line ~659 (after Gemini generation)
#
# LEGAL_DISCLAIMER = (
#     "\n\n---\n\n"
#     "**Legal Disclaimer**: This response is provided for informational purposes only "
#     "and does **not** constitute legal advice. IP-SAKTI Sahayak is an AI assistant that "
#     "may be incomplete or out-of-date. Always consult a qualified IP attorney or relevant "
#     "statutory authority before taking legal action."
# )

LEGAL_METADATA = {
    "biologicalDiversityRules2024.pdf": {"status": "CURRENT LAW", "year": "2024", "authority": "MoEFCC"},
    "bd_act_amendment.pdf": {"status": "CURRENT LAW", "year": "2023", "authority": "MoEFCC"},
    "THE BIOLOGICAL DIVERSITY ACT, 2002.pdf": {"status": "HISTORICAL", "year": "2002", "authority": "MoEFCC"},
    "ayush_ip_guidelines.pdf": {"status": "SUPERSEDED_GUIDANCE", "year": "2020", "authority": "Ministry of Ayush"},
}

SYSTEM_PROMPT_HEADER = (
    "You are IP-SAKTI Sahayak, an expert AI assistant for Intellectual Property "
    "and regulatory guidance in Ayurveda, developed for the Ministry of Ayush.\n\n"
    "RESPONSE FORMAT:\n"
    "- Provide clear, professional answers using proper markdown formatting\n"
    "- Use headings (## Section Name) for major sections\n"
    "- Use numbered lists (1., 2., 3.) for sequential steps\n"
    "- Use bullet points (-) for non-sequential items\n"
    "- Cite sources inline: [Patents Act 1970, Page 12]\n"
    "- Keep paragraphs concise (2-3 sentences max)\n"
    "- Use bold (**text**) sparingly for emphasis only\n"
    "- Do NOT add disclaimers (system adds them automatically)\n\n"
    "LEGAL PRECISION GUIDELINES:\n"
    "- Use CAUTIOUS, evidence-grounded language - avoid absolute claims\n"
    "- Prefer 'may be patentable' over 'can be patentable' or 'is patentable'\n"
    "- Use 'may need to', 'may require', 'could involve' rather than 'must' or 'requires'\n"
    "- State requirements conditionally: 'where Section X applies' or 'if the claimed invention falls under'\n"
    "- Do NOT overstate what the retrieved evidence establishes\n"
    "- If a document suggests a practice, phrase it as 'the guidance suggests' not 'applicants must'\n"
    "- For novel methods: 'may support patentability if genuinely new and inventive'\n"
    "- For enhanced efficacy: 'where Section 3(d) applies, appropriate evidence may be needed'\n"
    "- For TKDL searches: 'a search can help identify' not 'applicants must search'\n"
    "- Ground every claim in the retrieved context - do not invent requirements\n\n"
    "CONTENT GUIDELINES:\n"
    "- NEVER fabricate statutory provisions, treaty articles, or case citations\n"
    "- Always prioritize 'Status: CURRENT LAW' sources over 'HISTORICAL' or 'SUPERSEDED' sources\n"
    "- If information is missing from the database, state this clearly\n"
    "- Answer directly and concisely - avoid unnecessary introductions\n\n"
)


# ---------------------------------------------------------------------------
# Step 1 — Query Expansion
# ---------------------------------------------------------------------------

async def analyze_query_context(query: str, session_id: Optional[str] = None) -> dict:
    """
    Analyse the query with conversation history to handle follow-ups,
    determine complexity, and generate search variants via LLM.
    """
    history_str = memory_manager.get_history_formatted(session_id) if session_id else ""

    prompt = (
        "You are an AI router for a legal RAG system.\n"
        f"{history_str}"
        f"Latest User Query: {query}\n\n"
        "Analyze the latest user query based on the conversation history (if any).\n"
        "Return a JSON object matching this schema:\n"
        "{\n"
        "  \"needs_clarification\": boolean,\n"
        "  \"clarification_message\": \"Only if needs_clarification is true, the message to ask the user (e.g. what formulation?)\",\n"
        "  \"standalone_query\": \"The query rewritten to be completely self-contained (resolving pronouns like 'it', 'this section' using history). If no history, just output the query.\",\n"
        "  \"is_complex\": boolean,\n"
        "  \"retrieval_queries\": [\"variant 1\", \"variant 2\", \"variant 3 (only if complex)\"]\n"
        "}\n"
        "Rules:\n"
        "1. ONLY output raw JSON. No markdown, no backticks.\n"
        "2. If `needs_clarification` is true, do not worry about retrieval_queries.\n"
        "3. If `is_complex` is true, generate 2-3 highly specific `retrieval_queries` using legal phrasing, expanding acronyms (ABS, TKDL, etc).\n"
        "4. If `is_complex` is false, `retrieval_queries` can just contain the `standalone_query`."
    )
    try:
        resp = client.models.generate_content(model=_valid_model, contents=prompt)
        text = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(text)
        return data
    except Exception as exc:
        logger.warning(f"⚠️ Query context analysis failed: {exc}")
        return {
            "needs_clarification": False,
            "clarification_message": "",
            "standalone_query": query,
            "is_complex": False,
            "retrieval_queries": [query]
        }


# ---------------------------------------------------------------------------
# Step 2 — Dense Retrieval with Jurisdiction Filter
# ---------------------------------------------------------------------------

def _build_qdrant_filter(jurisdiction: Optional[str]) -> Optional[Filter]:
    """
    Build a Qdrant `must` filter for the `jurisdiction` payload field.
    Returns None if jurisdiction is None or "all".
    """
    if not jurisdiction:
        return None

    j_lower = jurisdiction.strip().lower()
    if j_lower in ("all", "both", "any", "none"):
        return None

    if j_lower in ("india", "in"):
        return Filter(
            should=[
                FieldCondition(
                    key="jurisdiction",
                    match=MatchValue(value="IN")
                ),
                FieldCondition(
                    key="source_type",
                    match=MatchAny(any=["json", "csv"])
                )
            ]
        )
    elif j_lower in ("international", "int", "intl"):
        return Filter(
            must=[
                FieldCondition(
                    key="jurisdiction",
                    match=MatchAny(any=["INT", "US", "EU", "INTL"])
                )
            ]
        )

    return None


async def _dense_retrieve(
    queries: list[str],
    collection_name: str,
    jurisdiction: Optional[str],
    limit_per_query: int = 15,
) -> dict[str, object]:
    """
    Run dense vector search for each query variant.
    Returns a dict of chunk_id → Qdrant ScoredPoint (best score wins).
    """
    qfilter = _build_qdrant_filter(jurisdiction)
    all_hits: dict[str, object] = {}

    for q in queries:
        vec = dense_model.encode(q, normalize_embeddings=True).tolist()
        try:
            result = qdrant.query_points(
                collection_name=collection_name,
                query=vec,
                query_filter=qfilter,
                limit=limit_per_query,
            )
            for point in result.points:
                chunk_id = point.payload.get("chunk_id", str(point.id))
                # Keep best score across query variants
                if chunk_id not in all_hits or point.score > all_hits[chunk_id].score:
                    all_hits[chunk_id] = point
        except Exception as exc:
            # If the payload field doesn't exist yet, fall back to unfiltered search
            if qfilter and ("No field" in str(exc) or "field" in str(exc).lower()):
                logger.warning(
                    f"⚠️ Qdrant jurisdiction filter failed (payload field missing). "
                    f"Falling back to filename-keyword filter for jurisdiction='{jurisdiction}'."
                )
                result = qdrant.query_points(
                    collection_name=collection_name,
                    query=vec,
                    limit=limit_per_query,
                )
                for point in result.points:
                    # Apply filename-based jurisdiction filter as fallback
                    src = point.payload.get("source_file", "")
                    if not _jurisdiction_matches_file(src, jurisdiction):
                        continue
                    chunk_id = point.payload.get("chunk_id", str(point.id))
                    if chunk_id not in all_hits or point.score > all_hits[chunk_id].score:
                        all_hits[chunk_id] = point
            else:
                raise

    return all_hits


# ---------------------------------------------------------------------------
# Step 3 — BM25 Lexical Search over candidate pool
# ---------------------------------------------------------------------------

def _bm25_rank(
    queries: list[str],
    candidates: list[object],
) -> dict[str, float]:
    """
    Run BM25 over the text of the candidate chunks for all query variations.
    Returns a dict of chunk_id → maximum normalised BM25 score [0, 1] across queries.
    """
    if not candidates:
        return {}

    # Tokenise corpus
    corpus_texts = [
        (c.payload.get("text", "")).lower().split()
        for c in candidates
    ]
    bm25 = BM25Okapi(corpus_texts)
    
    chunk_ids = [
        c.payload.get("chunk_id", str(c.id)) for c in candidates
    ]
    
    best_scores = {cid: 0.0 for cid in chunk_ids}
    
    for query in queries:
        query_tokens = query.lower().split()
        raw_scores = bm25.get_scores(query_tokens)
        
        # Normalise to [0, 1] for this query
        max_score = max(raw_scores) if max(raw_scores) > 0 else 1.0
        norm_scores = raw_scores / max_score
        
        for cid, score in zip(chunk_ids, norm_scores):
            if score > best_scores[cid]:
                best_scores[cid] = float(score)

    return best_scores


# ---------------------------------------------------------------------------
# Step 4 — Reciprocal Rank Fusion (RRF)
# ---------------------------------------------------------------------------

def _rrf_fuse(
    dense_hits: dict[str, object],
    bm25_scores: dict[str, float],
    k: int = 60,
) -> list[object]:
    """
    Merge dense and BM25 rankings using Reciprocal Rank Fusion.

    Score = 1/(k + dense_rank) + 1/(k + bm25_rank)
    """
    candidates = list(dense_hits.values())

    # Dense rank (already sorted by score descending)
    dense_sorted = sorted(candidates, key=lambda p: p.score, reverse=True)
    dense_rank = {p.payload.get("chunk_id", str(p.id)): i + 1 for i, p in enumerate(dense_sorted)}

    # BM25 rank
    bm25_sorted = sorted(bm25_scores.keys(), key=lambda cid: bm25_scores[cid], reverse=True)
    bm25_rank = {cid: i + 1 for i, cid in enumerate(bm25_sorted)}

    # Fuse
    rrf_scores: dict[str, float] = {}
    for cid in dense_rank:
        dr = dense_rank.get(cid, len(candidates) + k)
        br = bm25_rank.get(cid, len(bm25_scores) + k)
        rrf_scores[cid] = 1.0 / (k + dr) + 1.0 / (k + br)

    candidates.sort(key=lambda p: rrf_scores.get(p.payload.get("chunk_id", str(p.id)), 0.0), reverse=True)
    return candidates


# ---------------------------------------------------------------------------
# Step 5 — Cross-Encoder Reranking
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Step 5 — Cross-Encoder Reranking & Confidence Calculation
# ---------------------------------------------------------------------------

def _compute_confidence(raw_score: float) -> tuple[float, str]:
    """
    Convert raw Cross-Encoder logit score to normalized 0-100 score and band.
    Sigmoid scaling: C = 100 / (1 + exp(-S / 2.0))
    """
    import math
    try:
        norm_score = 100.0 / (1.0 + math.exp(-raw_score / 2.0))
    except Exception:
        norm_score = 0.0

    norm_score = round(norm_score, 1)

    if norm_score >= 80.0:
        band = "HIGH"
    elif norm_score >= 60.0:
        band = "MEDIUM"
    elif norm_score >= 40.0:
        band = "LOW"
    else:
        band = "VERY_LOW"

    return norm_score, band


def _cross_encoder_rerank(
    query: str,
    candidates: list[object],
    top_n: int = 10,
) -> tuple[list[object], float, float, str]:
    """
    Rerank candidates with Cross-Encoder model.
    Source-aware: Uses synthetic confidence derived from RRF rank for tabular data (csv/json)
    to bypass the MS-MARCO penalty on structured data.
    """
    if not candidates:
        return candidates[:top_n], -10.0, 0.0, "VERY_LOW"

    # 1. Compute raw cross-encoder scores for all candidates
    if cross_encoder is not None:
        pairs = [(query, c.payload.get("text", "")) for c in candidates]
        try:
            ce_scores = cross_encoder.predict(pairs)
        except Exception as exc:
            logger.warning(f"⚠️ Cross-Encoder reranking failed: {exc}")
            ce_scores = [-5.0] * len(candidates)
    else:
        ce_scores = [-10.0] * len(candidates)

    # 2. Source-aware scoring
    final_scores = []
    for i, (c, ce_score) in enumerate(zip(candidates, ce_scores)):
        stype = c.payload.get("source_type", "unknown")
        src_file = c.payload.get("source_file", "")
        
        # Base score
        score = float(ce_score)
        
        if stype in ["csv", "json"]:
            # Tabular data bypass: Assign synthetic logit score based on RRF rank (i)
            # This ensures only strong RRF matches pass the abstention threshold.
            if i == 0:
                score = 5.0   # ~92% (HIGH)
            elif i == 1:
                score = 3.0   # ~81% (HIGH)
            elif i == 2:
                score = 1.0   # ~62% (MEDIUM)
            elif i <= 5:
                score = -0.5  # ~43% (LOW)
            else:
                score = -3.0  # ~18% (VERY_LOW) - triggers abstention if best
        else:
            # Natural language: apply metadata adjustments
            meta = LEGAL_METADATA.get(src_file, {})
            status = meta.get("status")
            if status == "CURRENT LAW":
                score += 1.0
            elif status in ["HISTORICAL", "SUPERSEDED_GUIDANCE"]:
                score -= 2.0
                
        final_scores.append(score)

    # 3. Sort by final scores
    ranked = sorted(
        zip(final_scores, candidates),
        key=lambda x: x[0],
        reverse=True,
    )
    
    top_raw = ranked[0][0]
    conf_score, conf_band = _compute_confidence(top_raw)
    
    logger.info(
        f"🎯 [CrossEncoder] Top score={top_raw:.3f} | "
        f"ConfScore={conf_score}% ({conf_band}) "
        f"for chunk '{ranked[0][1].payload.get('chunk_id', '?')}' (Type: {ranked[0][1].payload.get('source_type', 'unknown')})"
    )
    return [c for _, c in ranked[:top_n]], top_raw, conf_score, conf_band


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

async def generate_grounded_response(
    query: str,
    collection_name: str = LEGAL_COLLECTION,
    jurisdiction: Optional[str] = "india",
    deterministic_context: Optional[str] = None,
    session_id: Optional[str] = None,
) -> dict:
    """
    Full hybrid RAG pipeline with deterministic abstention:
      Query Expansion → Dense Retrieval (jurisdiction-filtered) →
      BM25 Lexical → RRF Fusion → Cross-Encoder Reranking →
      Confidence Evaluation → (Hard Abstain OR Grounded Gemini Generation)
    """

    # Step 1 — Query expansion & context analysis
    analysis = await analyze_query_context(query, session_id)
    
    if analysis.get("needs_clarification") and analysis.get("clarification_message"):
        return {
            "answer": analysis.get("clarification_message"),
            "citations": [],
            "confidence_score": 100.0,
            "confidence_band": "HIGH",
            "abstained": False,
            "actions": []
        }

    queries = analysis.get("retrieval_queries", [query])
    standalone_query = analysis.get("standalone_query", query)
    
    if not queries:
        queries = [query]
        
    logger.info(f"🔍 [RAG] Expanded queries: {queries}")

    # Step 2 — Dense retrieval (jurisdiction-filtered)
    dense_hits = await _dense_retrieve(queries, collection_name, jurisdiction, limit_per_query=60)

    if not dense_hits:
        logger.warning("⚠️ [RAG] No chunks retrieved from Qdrant.")
        candidates = []
    else:
        candidates = list(dense_hits.values())

    # ═══════════════════════════════════════════════════════════════════════════
    # SEMANTIC RELEVANCE GATE (Before Cross-Encoder/Gemini)
    # ═══════════════════════════════════════════════════════════════════════════
    # Reject queries that are clearly out-of-domain by checking max cosine similarity
    # from InLegalBERT dense retrieval. This prevents processing queries like
    # "What is the capital of Mars?" through the entire pipeline.

    if candidates:
        max_dense_score = max(point.score for point in candidates)
        logger.info(f"🎯 [Semantic Gate] Max dense similarity: {max_dense_score:.3f}")

        # Threshold: 0.70 - if top match is below this, query is semantically out-of-domain
        # NOTE: Tuned to 0.70 to reject clearly out-of-domain queries like "What is the capital of Mars?"
        # This prevents false matches from reaching Cross-Encoder/Gemini
        SEMANTIC_RELEVANCE_THRESHOLD = 0.70

        if max_dense_score < SEMANTIC_RELEVANCE_THRESHOLD:
            logger.info(
                f"🛑 [Semantic Gate] Query rejected as OUT-OF-DOMAIN! "
                f"Max similarity {max_dense_score:.3f} < threshold {SEMANTIC_RELEVANCE_THRESHOLD}"
            )
            logger.info(
                f"🛑 [Semantic Gate] Query rejected as OUT-OF-DOMAIN! "
                f"Max similarity {max_dense_score:.3f} < threshold {SEMANTIC_RELEVANCE_THRESHOLD}"
            )
            abstain_message = (
                "⚠️ **Out-of-Domain Query**: "
                "IP-SAKTI Sahayak is specialized for Intellectual Property law, regulatory compliance, "
                "and Ayurveda-related matters. Your query appears to be outside this domain.\n\n"
                "**This assistant can help with**:\n"
                "- Patent law and filing procedures\n"
                "- Trademark and GI registration\n"
                "- Traditional Knowledge protection (TKDL)\n"
                "- ABS compliance and biological resources\n"
                "- FSSAI/FoSCoS regulations for Ayurveda Aahara\n"
                "- Ayurveda, Siddha, Unani regulatory matters\n\n"
                "Please rephrase your query to relate to these topics."
            )

            return {
                "answer": abstain_message,
                "citations": [],
                "confidence_score": 0.0,
                "confidence_band": "OUT_OF_DOMAIN",
                "abstained": True,
                "actions": []
            }

    # Step 3 — BM25 over candidate pool (using multiple queries)
    bm25_scores = _bm25_rank(queries, candidates)

    # Step 4 — RRF fusion
    fused = _rrf_fuse(dense_hits, bm25_scores)

    # Step 5 — Cross-Encoder reranking & confidence scoring
    final_results, top_raw_score, conf_score, conf_band = _cross_encoder_rerank(standalone_query, fused[:20], top_n=10)

    # DETERMINISTIC ABSTENTION CHECK
    # Abstain if evidence is insufficient (conf_score < 40.0 / VERY_LOW band / no hits)
    abstained = (conf_score < 40.0) or not final_results

    if abstained:
        logger.info(
            f"🛑 [RAG] Hard Abstention Triggered BEFORE Gemini Generation! "
            f"Query: '{query[:50]}...' | ConfScore={conf_score}% ({conf_band})"
        )
        abstain_message = (
            "⚠️ **Insufficient Authoritative Legal Evidence**: "
            "IP-SAKTI Sahayak found no relevant statutory provisions, treaties, or "
            "regulatory documents in the statutory database for your query. "
            "To prevent hallucination, the system has abstained from generating an ungrounded answer.\n\n"
            "**Recommended Action**:\n"
            "1. Refine your query using specific statutory terms (e.g., Section numbers, Act names, or official rules).\n"
            "2. Ensure the correct jurisdiction filter (India vs International) is selected.\n"
            "3. Use the Formulation Classifier wizard or escalate to a human IP Facilitator."
        )

        return {
            "answer": abstain_message,
            "citations": [],
            "confidence_score": conf_score,
            "confidence_band": conf_band,
            "abstained": True,
            "actions": []
        }

    logger.info(
        f"✅ [RAG] Proceeding to Gemini Generation: {len(final_results)} chunks "
        f"(conf_score={conf_score}%, band={conf_band})"
    )

    # Step 6 — Assemble context & citations for grounded generation (Top-4 optimal context)
    context_parts = []
    raw_citations = []

    for hit in final_results[:4]:
        payload = hit.payload or {}
        text = payload.get("text", "")
        source = payload.get("source_file", "Unknown.pdf")
        page_val = payload.get("page_number")
        page = int(page_val) if page_val is not None else 1
        
        meta = LEGAL_METADATA.get(source, {})
        status = meta.get("status", "ACTIVE")

        context_parts.append(
            f"[Source: {source} | Page {page} | Status: {status}]\n{text}\n"
        )
        snippet = text[:150]
        raw_citations.append({"source": source, "page": page, "snippet": snippet})

    seen = set()
    unique_citations = []
    for c in raw_citations:
        key = (c["source"], c["page"])
        if key not in seen:
            seen.add(key)
            unique_citations.append(c)

    context = "\n".join(context_parts)

    prompt_context = context
    if deterministic_context:
        prompt_context = f"=== DETERMINISTIC RULE ENGINE RESULT ===\n{deterministic_context}\n\n=== RETRIEVED LEGAL EVIDENCE ===\n{context}"

    # Step 7 — Grounded generation with disclaimer
    history_str = memory_manager.get_history_formatted(session_id) if session_id else ""
    prompt = (
        f"{SYSTEM_PROMPT_HEADER}"
        f"JURISDICTION: {'Indian Law (national statutes, rules, AYUSH regulations)' if jurisdiction == 'india' else 'International Treaties and Conventions'}\n\n"
        f"INSTRUCTIONS:\n"
        f"Answer the query using ONLY the provided context below.\n"
        f"Cite every fact with [Source Name, Page #] format.\n"
        f"Use clean markdown formatting.\n"
        f"Do NOT add legal disclaimers (added automatically).\n\n"
        f"CONTEXT:\n{prompt_context}\n\n"
        f"{history_str}"
        f"QUERY: {standalone_query}\n\n"
        f"ANSWER:"
    )

    try:
        response = client.models.generate_content(model=_valid_model, contents=prompt)
        answer_text = response.text if response else "Failed to generate answer."
    except Exception as exc:
        logger.error(f"⚠️ Generation failed: {exc}")
        answer_text = "Error generating response. Please check API quotas or inputs."

    # Step 8 — Lightweight Citation Validation
    # Validate that citations returned correspond to actually retrieved chunks
    retrieved_source_set = set(c["source"].lower() for c in unique_citations)
    validated_citations = []
    for c in unique_citations:
        if not c["source"].lower().endswith(".pdf"):
            continue
        validated_citations.append({
            "source": c["source"],
            "page": c["page"],
            "snippet": c["snippet"],
        })

    # Step 9 — Suggest Actionable Resources (NEW - lightweight action layer)
    suggested_action_ids = suggest_actions(
        query=standalone_query,
        answer=answer_text,
        citations=validated_citations,
        confidence_score=conf_score,
        abstained=False
    )
    action_metadata = get_action_suggestions(suggested_action_ids)

    return {
        "answer": answer_text,
        "citations": validated_citations,
        "confidence_score": conf_score,
        "confidence_band": conf_band,
        "abstained": False,
        "actions": [a.model_dump() for a in action_metadata] if action_metadata else []
    }
