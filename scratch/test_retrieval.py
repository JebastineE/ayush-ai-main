import os
import sys
from pathlib import Path

BASE_DIR = Path(r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main")
sys.path.append(str(BASE_DIR))

from pipeline.phase2_vectorize import get_or_create_qdrant_client, load_model
from pipeline.config import LEGAL_COLLECTION

def test_retrieval():
    client = get_or_create_qdrant_client()
    model = load_model()
    
    queries = {
        "pdf": "What are the rules regarding Phytopharmaceutical Drugs in India?",
        "json": "Which plant parts are used in siddha medicine?",
        "csv": "What is the mode of administration for ashwagandha?"
    }
    
    for format_type, query in queries.items():
        print(f"\n--- Testing retrieval for expected {format_type.upper()} source ---")
        print(f"Query: {query}")
        
        vector = model.encode(query).tolist()
        results = client.query_points(
            collection_name=LEGAL_COLLECTION,
            query=vector,
            limit=5
        ).points
        
        found_source = False
        for res in results:
            payload = res.payload
            src_type = payload.get("source_type", "unknown")
            print(f"Match Score: {res.score:.4f} | Source Type: {src_type} | File: {payload.get('source_file')}")
            if src_type == format_type:
                found_source = True
                
        if found_source:
            print(f"Successfully retrieved {format_type} data!")
        else:
            print(f"Did not find top-5 matches for {format_type} data.")

if __name__ == "__main__":
    test_retrieval()
