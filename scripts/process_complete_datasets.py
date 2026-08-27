import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pipeline.config import (
    LEGAL_CHUNKS, JSON_CHUNKS, CSV_CHUNKS, INGESTION_LOG, LEGAL_COLLECTION
)
from pipeline.utils import load_ingestion_log, save_ingestion_log, ensure_dirs
from pipeline.phase1_ingest import process_legal_corpus, process_json_file, process_csv_file, append_jsonl
from pipeline.phase2_vectorize import run_vectorization

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def get_files():
    json_files = []
    csv_files = []

    for root, _, files in os.walk(DATA_DIR):
        if "qdrant_store" in root or "processed" in root or "backup" in root:
            continue
        for file in files:
            ext = file.lower().split('.')[-1]
            filepath = Path(root) / file
            if ext == 'json' and 'metadata' not in root and file not in ['benchmark_results.json', 'ip_sakti_benchmark.json', 'citation_validation_report.json', 'new_documents_manifest.json'] and 'biopiracy_cases' not in file and 'clean_keyword_records' not in file:
                json_files.append(filepath)
            elif ext == 'csv':
                csv_files.append(filepath)
    return json_files, csv_files

def main():
    ensure_dirs()
    log = load_ingestion_log(INGESTION_LOG)
    
    json_files, csv_files = get_files()
    
    print(f"Found {len(json_files)} JSON files to process")
    print(f"Found {len(csv_files)} CSV files to process")
    
    # 1. Process PDFs
    print("\n==================================================")
    print("STEP 3 — PROCESS PDFs SEPARATELY")
    print("==================================================")
    # This processes all PDFs in data/legal_corpus recursively now.
    new_legal_chunks, updated_log = process_legal_corpus(log)
    if new_legal_chunks:
        append_jsonl(LEGAL_CHUNKS, new_legal_chunks)
    print(f"PDF Chunks generated: {len(new_legal_chunks)}")
    
    # 2. Process JSONs
    print("\n==================================================")
    print("STEP 4 — PROCESS JSON SEPARATELY")
    print("==================================================")
    total_json_chunks = 0
    for i, filepath in enumerate(json_files, 1):
        print(f"JSON: Processed {i}/{len(json_files)} - {filepath.name}")
        chunks, updated_log = process_json_file(filepath, updated_log, collection=LEGAL_COLLECTION)
        if chunks:
            append_jsonl(JSON_CHUNKS, chunks)
            total_json_chunks += len(chunks)
    print(f"Total JSON chunks generated: {total_json_chunks}")
    
    # 3. Process CSVs
    print("\n==================================================")
    print("STEP 5 — PROCESS CSV SEPARATELY")
    print("==================================================")
    total_csv_chunks = 0
    for i, filepath in enumerate(csv_files, 1):
        print(f"CSV: Processed {i}/{len(csv_files)} - {filepath.name}")
        chunks, updated_log = process_csv_file(filepath, updated_log, collection=LEGAL_COLLECTION)
        if chunks:
            append_jsonl(CSV_CHUNKS, chunks)
            total_csv_chunks += len(chunks)
    print(f"Total CSV chunks generated: {total_csv_chunks}")
    
    save_ingestion_log(updated_log, INGESTION_LOG)
    
    # 4. Vectorize
    print("\n==================================================")
    print("STEPS 7, 8, 9 — VECTORIZATION")
    print("==================================================")
    run_vectorization()
    
    print("\n==================================================")
    print("PROCESSING COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"Total processing time: {time.time() - t0:.2f} seconds")
