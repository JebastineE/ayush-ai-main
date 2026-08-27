"""
Wipe old Qdrant collections, clear processed chunks, and re-run the full pipeline.
Usage: python rebuild_db.py
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, '.')
from pipeline.config import QDRANT_PATH, PROCESSED_DIR, INGESTION_LOG, LEGAL_CHUNKS, TKDL_CHUNKS

def main():
    print("[1/4] Wiping Qdrant store...")
    if QDRANT_PATH.exists():
        shutil.rmtree(QDRANT_PATH)
        print(f"  Deleted: {QDRANT_PATH}")
    QDRANT_PATH.mkdir(parents=True, exist_ok=True)

    print("[2/4] Clearing processed chunks and ingestion log...")
    for f in [LEGAL_CHUNKS, TKDL_CHUNKS, INGESTION_LOG]:
        if f.exists():
            f.unlink()
            print(f"  Deleted: {f}")

    print("[3/4] Re-running Phase 1: Ingestion...")
    from pipeline.phase1_ingest import run_ingestion
    run_ingestion()

    print("[4/4] Re-running Phase 2: Vectorization...")
    from pipeline.phase2_vectorize import run_vectorization
    run_vectorization()

    print("\n[DONE] Database fully rebuilt. Restart uvicorn to pick up the new Qdrant store.")

if __name__ == "__main__":
    main()
