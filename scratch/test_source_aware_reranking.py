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
        "id": "A. PDF",
        "query": "What are the labelling requirements for Phytopharmaceutical Drugs?",
    },
    {
        "id": "B. JSON",
        "query": "What medicinal plant information is available for Withania somnifera (Ashwagandha)?",
    },
    {
        "id": "C. CSV",
        "query": "List all the information, synonyms, and local names associated with Acorus calamus Linn.",
    },
    {
        "id": "D. TKDL",
        "query": "Are there any TKDL prior-art records related to Ashwagandha?",
    },
    {
        "id": "E. Mixed",
        "query": "According to the Drugs and Cosmetics Act, can I sell Withania somnifera plant extracts as proprietary medicine?",
    }
]

async def run_tests():
    for q in queries:
        print(f"\n========================================")
        print(f"Test: {q['id']}")
        print(f"Query: {q['query']}")
        
        # Determine jurisdiction based on query content to mimic frontend behavior
        jurisdiction = "india"
        
        resp = await generate_grounded_response(q['query'], collection_name="legal_docs", jurisdiction=jurisdiction)
        
        print("\nTop sources passed to final context:")
        citations = resp.get("citations", [])
        if not citations:
            print("  [No citations found.]")
        for i, cit in enumerate(citations):
            source = cit.get("source", "unknown")
            stype = cit.get("source_type", "unknown")
            if source.endswith(".json"):
                stype = "json"
            elif source.endswith(".csv"):
                stype = "csv"
            elif source.endswith(".pdf"):
                stype = "pdf"
            print(f"  {i+1}. File: {source} | Type: {stype}")
            
        print(f"\nConfidence Score: {resp.get('confidence_score')}% ({resp.get('confidence_band')})")
        print(f"Abstained: {resp.get('abstained')}")
        
        # print first 150 chars of answer
        ans = resp.get('answer', '')
        if isinstance(ans, str):
            ans = ans.encode('utf-8', 'ignore').decode('utf-8')
            print(f"Answer snippet: {ans[:150]}...")
        else:
            print(f"Answer snippet: {str(ans)[:150]}...")

if __name__ == "__main__":
    asyncio.run(run_tests())
