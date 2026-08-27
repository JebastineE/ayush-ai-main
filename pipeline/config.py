from pathlib import Path

# Key constants
BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR      = BASE_DIR / "data" / "legal_corpus"
TK_DIR          = BASE_DIR / "data" / "traditional_knowledge"
PROCESSED_DIR   = BASE_DIR / "data" / "processed"
QDRANT_PATH     = BASE_DIR / "data" / "qdrant_store"
INGESTION_LOG   = PROCESSED_DIR / "ingestion_log.json"
LEGAL_CHUNKS    = PROCESSED_DIR / "legal_chunks.jsonl"
TKDL_CHUNKS     = PROCESSED_DIR / "tkdl_chunks.jsonl"

MODEL_NAME             = "law-ai/InLegalBERT"
EMBEDDING_DIM          = 768
CHUNK_SIZE_TOKENS      = 512
CHUNK_OVERLAP_TOKENS   = 64
BATCH_SIZE_EMBED       = 16  # Embeddings per inference batch (RAM-safe)

LEGAL_COLLECTION = "legal_docs"
TKDL_COLLECTION  = "tkdl_records"
