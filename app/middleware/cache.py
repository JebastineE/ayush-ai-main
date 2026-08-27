import hashlib
from fastapi import Response
from app.db.sqlite_cache import get_cached_response, set_cached_response
from app.services.rag import generate_grounded_response

CACHE_VERSION = "v3_hybrid_rag"


async def process_chat_with_cache(
    query: str,
    response: Response,
    jurisdiction: str = "india",
):
    """
    Cache wrapper around the hybrid RAG pipeline.
    Cache key is jurisdiction-aware to prevent cross-jurisdiction cache pollution.
    """
    # Include jurisdiction in hash to prevent cross-jurisdiction cache hits
    salted = f"{jurisdiction}::{query}::{CACHE_VERSION}"
    hash_id = hashlib.sha256(salted.encode("utf-8")).hexdigest()

    # Check cache
    cached = get_cached_response(hash_id)
    if cached:
        response.headers["X-Cache-Status"] = "HIT"
        response.headers["X-Jurisdiction"] = jurisdiction
        return cached

    # Cache miss — process via hybrid RAG
    rag_result = await generate_grounded_response(
        query=query,
        jurisdiction=jurisdiction,
    )

    # Never cache actionable fallbacks or error responses
    answer_lower = rag_result.get("answer", "").lower()
    is_fallback = (
        "actionable fallback" in answer_lower
        or "i cannot find sufficient information" in answer_lower
        or "error generating response" in answer_lower
    )

    if not is_fallback:
        set_cached_response(hash_id, query, rag_result)

    response.headers["X-Cache-Status"] = "MISS"
    response.headers["X-Jurisdiction"] = jurisdiction
    return rag_result
