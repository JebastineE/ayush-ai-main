import os
import sys
import json
import time
from pathlib import Path
import asyncio

# Setup paths
BASE_DIR = Path(r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main")
sys.path.append(str(BASE_DIR))

# Import project modules
try:
    from pipeline.config import LEGAL_COLLECTION, TKDL_COLLECTION
    from pipeline.phase2_vectorize import get_or_create_qdrant_client, load_model
    from app.services.rag import generate_grounded_response
    from app.services.biopiracy_scanner import scan_formulation
    has_imports = True
except Exception as e:
    has_imports = False
    import_error = str(e)

DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

audit_results = {
    "1_dataset": {},
    "2_chunks": {},
    "3_embeddings": {},
    "4_qdrant": {},
    "5_consistency": {},
    "retrieval": {},
    "rag": {},
    "rules": {},
    "performance": {}
}

# 1. Dataset Audit
def audit_datasets():
    formats = {"pdf": 0, "json": 0, "csv": 0, "other": 0}
    sizes = {"pdf": 0, "json": 0, "csv": 0, "other": 0}
    
    for root, _, files in os.walk(DATA_DIR):
        if "qdrant_store" in root or "processed" in root or "backup" in root:
            continue
        for file in files:
            ext = file.lower().split('.')[-1]
            filepath = Path(root) / file
            size = os.path.getsize(filepath)
            
            # Use exact filter conditions from the ingestion script
            is_json = (ext == 'json' and 'metadata' not in root and file not in ['benchmark_results.json', 'ip_sakti_benchmark.json', 'citation_validation_report.json', 'new_documents_manifest.json'] and 'biopiracy_cases' not in file and 'clean_keyword_records' not in file)
            is_tkdl = ext == 'json' and ('biopiracy_cases' in file or 'clean_keyword_records' in file)
            
            if ext == 'pdf':
                formats['pdf'] += 1
                sizes['pdf'] += size
            elif is_json:
                formats['json'] += 1
                sizes['json'] += size
            elif is_tkdl:
                formats['other'] += 1 # Counting TKDL separately or as other
            elif ext == 'csv':
                formats['csv'] += 1
                sizes['csv'] += size
            else:
                formats['other'] += 1
                sizes['other'] += size
                
    audit_results['1_dataset'] = {"counts": formats, "sizes_bytes": sizes}

# 2. Chunk Audit
def audit_chunks():
    chunks_info = {}
    for chunk_file in ["legal_chunks.jsonl", "json_chunks.jsonl", "csv_chunks.jsonl", "tkdl_chunks.jsonl"]:
        path = PROCESSED_DIR / chunk_file
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                lines = [json.loads(line) for line in f if line.strip()]
                chunks_info[chunk_file] = {
                    "count": len(lines),
                    "sample_source_type": lines[0].get("source_type", "unknown") if lines else "none",
                    "sample_text_len": len(lines[0].get("text", "")) if lines else 0
                }
        else:
            chunks_info[chunk_file] = {"count": 0, "exists": False}
    audit_results['2_chunks'] = chunks_info

# 3. Qdrant & Consistency & Retrieval
def audit_qdrant_and_retrieval():
    if not has_imports:
        return
        
    client = get_or_create_qdrant_client()
    
    # Collection info
    legal_count = client.count(collection_name=LEGAL_COLLECTION).count
    tkdl_count = client.count(collection_name=TKDL_COLLECTION).count
    
    audit_results['4_qdrant'] = {
        "legal_docs_count": legal_count,
        "tkdl_records_count": tkdl_count
    }
    
    # Load model for tests
    t0 = time.time()
    model = load_model()
    audit_results['performance']['model_load_s'] = time.time() - t0
    
    # 6. PDF Retrieval
    t0 = time.time()
    res_pdf = client.query_points(
        collection_name=LEGAL_COLLECTION,
        query=model.encode("Patents Act 1970 guidelines").tolist(),
        limit=5
    ).points
    pdf_pass = any(p.payload.get("source_type") == "pdf" for p in res_pdf)
    audit_results['performance']['retrieval_pdf_s'] = time.time() - t0
    
    # 7. JSON Retrieval (Targeted)
    res_json = client.query_points(
        collection_name=LEGAL_COLLECTION,
        query=model.encode("siddha plant name abini").tolist(), # targeting a specific json concept if possible
        limit=10
    ).points
    json_pass = any(p.payload.get("source_type") == "json" for p in res_json)
    
    # 8. CSV Retrieval (Targeted)
    res_csv = client.query_points(
        collection_name=LEGAL_COLLECTION,
        query=model.encode("drug action properties of classical medicines").tolist(),
        limit=10
    ).points
    csv_pass = any(p.payload.get("source_type") == "csv" for p in res_csv)
    
    # 9. TKDL Retrieval
    res_tkdl = client.query_points(
        collection_name=TKDL_COLLECTION,
        query=model.encode("Bio-Piracy case of Neem or Turmeric").tolist(),
        limit=5
    ).points
    tkdl_pass = len(res_tkdl) > 0
    
    audit_results['retrieval'] = {
        "pdf": pdf_pass,
        "json": json_pass,
        "csv": csv_pass,
        "tkdl": tkdl_pass
    }

async def audit_rag():
    if not has_imports:
        return
    t0 = time.time()
    try:
        resp = await generate_grounded_response("What are the provisions for traditional knowledge under the Biological Diversity Act?")
        audit_results['rag'] = {
            "success": True,
            "has_answer": bool(resp.get("answer")),
            "citations_count": len(resp.get("citations", [])),
            "abstained": resp.get("abstained")
        }
    except Exception as e:
        audit_results['rag'] = {"success": False, "error": str(e)}
    audit_results['performance']['rag_e2e_s'] = time.time() - t0

def audit_rules():
    if not has_imports:
        return
    try:
        res = scan_formulation("Neem and Turmeric face wash for glowing skin")
        audit_results['rules'] = {
            "success": True,
            "classification": res.classification.value if hasattr(res.classification, 'value') else str(res.classification)
        }
    except Exception as e:
        audit_results['rules'] = {"success": False, "error": str(e)}

def run_all():
    print("Auditing Datasets...")
    audit_datasets()
    print("Auditing Chunks...")
    audit_chunks()
    print("Auditing Qdrant & Retrieval...")
    audit_qdrant_and_retrieval()
    print("Auditing RAG (Async)...")
    asyncio.run(audit_rag())
    print("Auditing Rules...")
    audit_rules()
    
    with open(BASE_DIR / "scratch" / "audit_results.json", "w") as f:
        json.dump(audit_results, f, indent=2)
    print("Audit data saved.")

if __name__ == "__main__":
    run_all()
