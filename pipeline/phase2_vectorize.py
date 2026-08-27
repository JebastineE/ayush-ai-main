import json
import uuid
import torch
from pathlib import Path
from typing import Generator
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from .config import (
    MODEL_NAME, QDRANT_PATH, LEGAL_CHUNKS, TKDL_CHUNKS,
    LEGAL_COLLECTION, TKDL_COLLECTION, EMBEDDING_DIM, BATCH_SIZE_EMBED
)
from .utils import setup_logging

logger = setup_logging(__name__)

def load_model() -> SentenceTransformer:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading SentenceTransformer '{MODEL_NAME}' on {device}...")
    model = SentenceTransformer(MODEL_NAME, device=device)
    return model

def get_or_create_qdrant_client() -> QdrantClient:
    logger.info(f"Initializing Qdrant client at {QDRANT_PATH}...")
    client = QdrantClient(path=str(QDRANT_PATH))
    
    # Ensure collections exist
    collections = [c.name for c in client.get_collections().collections]
    
    if LEGAL_COLLECTION not in collections:
        logger.info(f"Creating collection '{LEGAL_COLLECTION}'...")
        client.create_collection(
            collection_name=LEGAL_COLLECTION,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        
    if TKDL_COLLECTION not in collections:
        logger.info(f"Creating collection '{TKDL_COLLECTION}'...")
        client.create_collection(
            collection_name=TKDL_COLLECTION,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        
    return client

def chunk_id_to_uuid(chunk_id: str) -> str:
    """Generate a deterministic UUID5 from the chunk ID."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))

def read_jsonl(file_path: Path) -> Generator[dict, None, None]:
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping malformed JSONL line in {file_path.name}: {e}")

def embed_and_upsert(chunks_iter: Generator[dict, None, None], 
                     model: SentenceTransformer, 
                     client: QdrantClient, 
                     collection: str) -> int:
    total_upserted = 0
    batch = []
    
    for chunk in chunks_iter:
        batch.append(chunk)
        if len(batch) >= BATCH_SIZE_EMBED:
            total_upserted += _process_batch(batch, model, client, collection)
            batch = []
            
    # Process remaining
    if batch:
        total_upserted += _process_batch(batch, model, client, collection)
        
    return total_upserted

def _process_batch(batch: list[dict], model: SentenceTransformer, client: QdrantClient, collection: str) -> int:
    try:
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts, batch_size=len(texts), show_progress_bar=False, normalize_embeddings=True)
        
        points = []
        for i, chunk in enumerate(batch):
            point_id = chunk_id_to_uuid(chunk["chunk_id"])
            vector = embeddings[i].tolist()
            # Keep text in payload for RAG retrieval
            payload = {k: v for k, v in chunk.items()}
            
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))
            
        client.upsert(collection_name=collection, points=points, wait=True)
        return len(points)
    except Exception as e:
        logger.error(f"Failed to process and upsert batch in '{collection}': {e}")
        return 0

def run_vectorization() -> None:
    logger.info("Starting Phase 2: Vectorization...")
    
    if not LEGAL_CHUNKS.exists() and not TKDL_CHUNKS.exists():
        logger.warning("No chunk files found. Did you run Phase 1?")
        return
        
    model = load_model()
    client = get_or_create_qdrant_client()
    
    legal_upserts = 0
    if LEGAL_CHUNKS.exists():
        logger.info("Vectorizing legal chunks...")
        legal_iter = read_jsonl(LEGAL_CHUNKS)
        legal_upserts = embed_and_upsert(legal_iter, model, client, LEGAL_COLLECTION)
        
    tkdl_upserts = 0
    if TKDL_CHUNKS.exists():
        logger.info("Vectorizing TKDL chunks...")
        tkdl_iter = read_jsonl(TKDL_CHUNKS)
        tkdl_upserts = embed_and_upsert(tkdl_iter, model, client, TKDL_COLLECTION)
        
    logger.info(f"✅ Vectorization complete.")
    logger.info(f"legal_docs: {legal_upserts} points upserted/verified.")
    logger.info(f"tkdl_records: {tkdl_upserts} points upserted/verified.")
