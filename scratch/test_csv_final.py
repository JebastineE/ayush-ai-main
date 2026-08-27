import sys
import asyncio
from pathlib import Path
import logging

logging.getLogger("rag_pipeline").setLevel(logging.ERROR)

BASE_DIR = Path(r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main")
sys.path.append(str(BASE_DIR))

from app.services.rag import generate_grounded_response

queries = [
    {
        "query": "List all the information, synonyms, and local names associated with Acorus calamus Linn.",
    }
]

async def run_tests():
    for q in queries:
        print(f"\n========================================")
        print(f"Query: {q['query']}")
        
        resp = await generate_grounded_response(q['query'], collection_name="legal_docs", jurisdiction="india")
        
        print("\nTop sources passed to Gemini:")
        citations = resp.get("citations", [])
        if not citations:
            print("  [No citations found. Abstained?]", resp.get("abstained"))
        for i, cit in enumerate(citations):
            source = cit.get("source", "unknown")
            if source.endswith(".json"):
                stype = "json"
            elif source.endswith(".csv"):
                stype = "csv"
            elif source.endswith(".pdf"):
                stype = "pdf"
            else:
                stype = "unknown"
            print(f"  {i+1}. File: {source} | Type: {stype}")
            if stype == "csv":
                print(f"     Snippet: {cit.get('snippet', '').encode('utf-8')}")
            
        print(f"\nAnswer: {resp.get('answer', '').encode('utf-8')}")
        print(f"\nConfidence Score: {resp.get('confidence_score')}% ({resp.get('confidence_band')})")
        print(f"Abstained: {resp.get('abstained')}")

if __name__ == "__main__":
    asyncio.run(run_tests())
