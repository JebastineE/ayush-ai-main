import os
import sys
import asyncio
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
sys.path.insert(0, project_dir)

from app.services.rag import (
    expand_query, _dense_retrieve, _bm25_rank, _rrf_fuse, cross_encoder, LEGAL_COLLECTION
)

# 10 In-Corpus Questions
in_corpus_queries = [
    "What does Section 3(p) of the Indian Patents Act 1970 state regarding traditional knowledge?",
    "What are the ABS requirements for foreign entities under Section 3 of the Biological Diversity Act 2002?",
    "What is the regulatory pathway for Phytopharmaceutical drugs under CDSCO GSR 918(E) 2015?",
    "What are the FSSAI 2022 regulations for Ayurveda-Aahar and Health Supplements?",
    "What are the key provisions of Article 27 of the TRIPS Agreement?",
    "What disclosure requirement is mandated by the WIPO GRATK Treaty 2024 for genetic resources?",
    "How was the US patent on Turmeric wound healing challenged and revoked by CSIR using TKDL?",
    "What is the procedure for prior intimation to State Biodiversity Board for cultivated resources under Rule 7 of BD Rules 2024?",
    "What constitutes a Geographical Indication under the GI of Goods Act 1999?",
    "What are the requirements for Form 24-D ASU drug manufacturing licence under Drugs & Cosmetics Rules 1945?"
]

# 10 Out-Of-Corpus Questions
out_of_corpus_queries = [
    "How does quantum error correction work using surface codes in quantum computers?",
    "What is the best recipe for baking fluffy chocolate chip cookies at high altitude?",
    "What are the rules for Leg Before Wicket (LBW) in international cricket?",
    "What was the closing price of Bitcoin on December 31 2024?",
    "How do you replace an oil filter on a 2018 Honda Civic sedan?",
    "What are the lyrics to Beethoven's Ode to Joy in German?",
    "How do black holes collapse and emit Hawking radiation?",
    "What is the capital city of Australia and its current population?",
    "How to configure Nginx as a reverse proxy for a Python Flask application?",
    "What is the plot summary of Shakespeare's play Hamlet?"
]

async def run_eval():
    print("=== EVALUATING CROSS-ENCODER SCORE DISTRIBUTION ===")
    
    in_corpus_results = []
    out_of_corpus_results = []

    for idx, q in enumerate(in_corpus_queries, 1):
        dense_hits = await _dense_retrieve([q], LEGAL_COLLECTION, "all", limit_per_query=15)
        candidates = list(dense_hits.values())
        bm25_scores = _bm25_rank(q, candidates)
        fused = _rrf_fuse(dense_hits, bm25_scores)
        top_candidates = fused[:10]
        
        top_score = -999.0
        if top_candidates and cross_encoder is not None:
            pairs = [(q, c.payload.get("text", "")) for c in top_candidates]
            scores = cross_encoder.predict(pairs)
            top_score = float(max(scores))
        
        dense_max = float(max([c.score for c in candidates])) if candidates else 0.0
        in_corpus_results.append({"id": idx, "query": q, "cross_encoder_score": top_score, "dense_max": dense_max})
        print(f"In-Corpus Q{idx:02d}: CrossEncoder Top Score = {top_score:6.3f} | Dense Max = {dense_max:.3f}")

    print("\n--- Out-of-Corpus Queries ---")
    for idx, q in enumerate(out_of_corpus_queries, 1):
        dense_hits = await _dense_retrieve([q], LEGAL_COLLECTION, "all", limit_per_query=15)
        candidates = list(dense_hits.values())
        bm25_scores = _bm25_rank(q, candidates)
        fused = _rrf_fuse(dense_hits, bm25_scores)
        top_candidates = fused[:10]
        
        top_score = -999.0
        if top_candidates and cross_encoder is not None:
            pairs = [(q, c.payload.get("text", "")) for c in top_candidates]
            scores = cross_encoder.predict(pairs)
            top_score = float(max(scores))

        dense_max = float(max([c.score for c in candidates])) if candidates else 0.0
        out_of_corpus_results.append({"id": idx, "query": q, "cross_encoder_score": top_score, "dense_max": dense_max})
        print(f"Out-of-Corpus Q{idx:02d}: CrossEncoder Top Score = {top_score:6.3f} | Dense Max = {dense_max:.3f}")

    in_scores = [r["cross_encoder_score"] for r in in_corpus_results]
    out_scores = [r["cross_encoder_score"] for r in out_of_corpus_results]

    print("\n=== SUMMARY STATISTICS ===")
    print(f"In-Corpus     : Min = {min(in_scores):6.3f} | Max = {max(in_scores):6.3f} | Avg = {sum(in_scores)/len(in_scores):6.3f}")
    print(f"Out-Of-Corpus : Min = {min(out_scores):6.3f} | Max = {max(out_scores):6.3f} | Avg = {sum(out_scores)/len(out_scores):6.3f}")

if __name__ == "__main__":
    asyncio.run(run_eval())
