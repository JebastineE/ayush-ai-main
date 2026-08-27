import os
import sys
import json
import time
import asyncio

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
sys.path.insert(0, project_dir)

from app.services.rag import (
    expand_query, _dense_retrieve, _bm25_rank, _rrf_fuse, _cross_encoder_rerank,
    LEGAL_COLLECTION, client, _valid_model, SYSTEM_PROMPT_HEADER, LEGAL_DISCLAIMER
)

queries = [
    ("narrow_legal", "What does Section 3(p) of the Patents Act 1970 state regarding traditional knowledge?"),
    ("cross_regime", "How do Section 3(p) of the Patents Act and Section 3 of the BD Act interact for Ayurvedic patents?"),
    ("formulation", "What are the licensing requirements for classical Ayurvedic formulations under Rule 158-B?"),
    ("abs", "What are the ABS compliance duties for foreign entities accessing Indian biological resources?"),
    ("international_treaty", "What disclosure requirement for genetic resources is mandated by the WIPO GRATK Treaty 2024?")
]

async def eval_top_k(top_k: int):
    results = []
    for qtype, q in queries:
        t0 = time.time()
        expanded = await expand_query(q)
        dense_hits = await _dense_retrieve(expanded, LEGAL_COLLECTION, "all", limit_per_query=15)
        candidates = list(dense_hits.values())
        bm25_scores = _bm25_rank(q, candidates)
        fused = _rrf_fuse(dense_hits, bm25_scores)
        final_results, top_raw, conf_score, conf_band = _cross_encoder_rerank(q, fused[:20], top_n=10)

        context_parts = []
        raw_citations = []
        for hit in final_results[:top_k]:
            payload = hit.payload or {}
            text = payload.get("text", "")
            source = payload.get("source_file", "Unknown.pdf")
            page = int(payload.get("page_number", 1))
            context_parts.append(f"[Source: {source} | Page {page}]\n{text}\n")
            raw_citations.append({"source": source, "page": page, "snippet": text[:150]})

        context = "\n".join(context_parts)
        prompt = (
            f"{SYSTEM_PROMPT_HEADER}"
            f"Jurisdiction scope: Indian Law & International Treaties.\n\n"
            f"Answer using ONLY the provided context below. Cite every fact with source document and page number in square brackets.\n\n"
            f"Context:\n{context}\n\n"
            f"Query: {q}"
        )

        resp = client.models.generate_content(model=_valid_model, contents=prompt)
        elapsed = time.time() - t0

        answer_text = resp.text if resp else ""
        prompt_tokens = len(prompt.split())

        results.append({
            "query_type": qtype,
            "query": q,
            "top_k": top_k,
            "citation_count": len(raw_citations),
            "answer_length": len(answer_text),
            "prompt_tokens_est": prompt_tokens,
            "latency_sec": round(elapsed, 2),
            "conf_score": conf_score
        })
    return results

async def main():
    print("=== EVALUATING TOP-4 vs TOP-6 CONTEXT WINDOW ===")
    print("\nRunning Top-4 evaluation...")
    top4_res = await eval_top_k(4)
    
    print("\nRunning Top-6 evaluation...")
    top6_res = await eval_top_k(6)

    print("\n=== COMPARISON RESULTS ===")
    print(f"{'Type':<20} | {'Top-4 Latency':<13} | {'Top-6 Latency':<13} | {'Top-4 Tokens':<12} | {'Top-6 Tokens':<12}")
    print("-" * 75)
    for r4, r6 in zip(top4_res, top6_res):
        print(f"{r4['query_type']:<20} | {r4['latency_sec']:<13} | {r6['latency_sec']:<13} | {r4['prompt_tokens_est']:<12} | {r6['prompt_tokens_est']:<12}")

    avg_l4 = sum(r["latency_sec"] for r in top4_res) / 5
    avg_l6 = sum(r["latency_sec"] for r in top6_res) / 5
    avg_t4 = sum(r["prompt_tokens_est"] for r in top4_res) / 5
    avg_t6 = sum(r["prompt_tokens_est"] for r in top6_res) / 5

    print("\n=== AVERAGE METRICS ===")
    print(f"Top-4: Avg Latency = {avg_l4:.2f}s | Avg Tokens = {avg_t4:.0f}")
    print(f"Top-6: Avg Latency = {avg_l6:.2f}s | Avg Tokens = {avg_t6:.0f}")

    comp_report = {
        "top4_results": top4_res,
        "top6_results": top6_res,
        "averages": {
            "top4_latency_sec": round(avg_l4, 2),
            "top6_latency_sec": round(avg_l6, 2),
            "top4_tokens_est": round(avg_t4),
            "top6_tokens_est": round(avg_t6)
        }
    }
    with open(r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main\scratch\context_comparison.json", 'w', encoding='utf-8') as f:
        json.dump(comp_report, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
