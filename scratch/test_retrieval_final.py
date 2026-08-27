import sys
import asyncio
from pathlib import Path
import logging

# Suppress noisy logs
logging.getLogger("rag_pipeline").setLevel(logging.ERROR)

BASE_DIR = Path(r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main")
sys.path.append(str(BASE_DIR))

from app.services.rag import generate_grounded_response

queries = [
    {
        "name": "PDF retrieval (Normal Legal)",
        "query": "What are the labelling requirements for Phytopharmaceutical Drugs?",
        "expected": "pdf"
    },
    {
        "name": "JSON retrieval",
        "query": "What medicinal plant information is available for Withania somnifera (Ashwagandha)?",
        "expected": "json"
    },
    {
        "name": "CSV retrieval",
        "query": "What are the common therapeutic uses and mode of administration for Triphala churna in classical Ayurveda?",
        "expected": "csv"
    },
    {
        "name": "TKDL retrieval",
        "query": "Is there any TKDL defensive record or prior art for the use of Neem and Turmeric in wound healing?",
        "expected": "tkdl (or json)"
    },
    {
        "name": "Mixed Query",
        "query": "According to the Drugs and Cosmetics Act, can I sell Withania somnifera plant extracts as proprietary medicine?",
        "expected": "pdf and json/csv"
    }
]

async def run_tests():
    for q in queries:
        print(f"\n========================================")
        print(f"Test: {q['name']}")
        print(f"Query: {q['query']}")
        print(f"Expected to retrieve: {q['expected']}")
        
        # Determine jurisdiction based on TKDL
        jurisdiction = "india"
        collection = "legal_docs"
        if q['name'] == "TKDL retrieval":
            collection = "tkdl_records" # The TKDL endpoint normally searches tkdl_records
            
        resp = await generate_grounded_response(q['query'], collection_name=collection, jurisdiction=jurisdiction)
        
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
            
        print(f"Confidence Score: {resp.get('confidence_score')}% ({resp.get('confidence_band')})")
        print(f"Abstained: {resp.get('abstained')}")

if __name__ == "__main__":
    asyncio.run(run_tests())
