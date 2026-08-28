"""
Phase 2B: Vectorize formulation chunks into dedicated Qdrant collections.

Creates two new collections:
  - classical_formulations: Pharmacopoeia compound formulations (768-dim)
  - tkdl_formulations: TKDL sample formulations (768-dim)

Reuses InLegalBERT embedding model from existing pipeline.
"""

import json
import uuid
from pathlib import Path
from typing import Generator

import torch
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from .config import BASE_DIR, MODEL_NAME, EMBEDDING_DIM, BATCH_SIZE_EMBED, QDRANT_PATH
from .utils import setup_logging

logger = setup_logging(__name__)

FORMULATION_CHUNKS = BASE_DIR / "data" / "processed" / "formulation_chunks.jsonl"
CLASSICAL_COLLECTION = "classical_formulations"
TKDL_FORM_COLLECTION = "tkdl_formulations"


def load_model() -> SentenceTransformer:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading SentenceTransformer '{MODEL_NAME}' on {device}...")
    return SentenceTransformer(MODEL_NAME, device=device)


def get_qdrant_client() -> QdrantClient:
    logger.info(f"Initializing Qdrant at {QDRANT_PATH}...")
    client = QdrantClient(path=str(QDRANT_PATH))
    collections = [c.name for c in client.get_collections().collections]

    for coll_name in [CLASSICAL_COLLECTION, TKDL_FORM_COLLECTION]:
        if coll_name not in collections:
            logger.info(f"Creating collection '{coll_name}'...")
            client.create_collection(
                collection_name=coll_name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )

    return client


def chunk_id_to_uuid(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))


def read_formulation_chunks() -> tuple[list[dict], list[dict]]:
    """Read formulation chunks and split by collection."""
    classical = []
    tkdl = []

    if not FORMULATION_CHUNKS.exists():
        logger.error(f"Formulation chunks not found: {FORMULATION_CHUNKS}")
        return classical, tkdl

    with open(FORMULATION_CHUNKS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if record.get("collection") == CLASSICAL_COLLECTION:
                    classical.append(record)
                elif record.get("collection") == TKDL_FORM_COLLECTION:
                    tkdl.append(record)
            except json.JSONDecodeError:
                continue

    return classical, tkdl


def embed_and_upsert_batch(
    chunks: list[dict],
    model: SentenceTransformer,
    client: QdrantClient,
    collection: str,
) -> int:
    """Embed and upsert a list of chunks into a Qdrant collection."""
    if not chunks:
        return 0

    total = 0
    for i in range(0, len(chunks), BATCH_SIZE_EMBED):
        batch = chunks[i : i + BATCH_SIZE_EMBED]
        texts = [c["text"] for c in batch]

        try:
            embeddings = model.encode(
                texts,
                batch_size=len(texts),
                show_progress_bar=False,
                normalize_embeddings=True,
            )

            points = []
            for j, chunk in enumerate(batch):
                point_id = chunk_id_to_uuid(chunk["chunk_id"])
                vector = embeddings[j].tolist()
                payload = {k: v for k, v in chunk.items()}
                points.append(PointStruct(id=point_id, vector=vector, payload=payload))

            client.upsert(collection_name=collection, points=points, wait=True)
            total += len(points)
        except Exception as e:
            logger.error(f"Batch upsert failed for '{collection}': {e}")

    return total


def run_formulation_vectorization() -> None:
    """Main entry point for formulation vectorization."""
    logger.info("Starting Phase 2B: Formulation Vectorization...")

    classical_chunks, tkdl_chunks = read_formulation_chunks()
    logger.info(f"Loaded {len(classical_chunks)} classical + {len(tkdl_chunks)} TKDL chunks")

    if not classical_chunks and not tkdl_chunks:
        logger.warning("No formulation chunks found. Run Phase 1B first.")
        return

    model = load_model()
    client = get_qdrant_client()

    classical_count = embed_and_upsert_batch(classical_chunks, model, client, CLASSICAL_COLLECTION)
    tkdl_count = embed_and_upsert_batch(tkdl_chunks, model, client, TKDL_FORM_COLLECTION)

    logger.info(f"Phase 2B complete.")
    logger.info(f"  classical_formulations: {classical_count} vectors upserted")
    logger.info(f"  tkdl_formulations: {tkdl_count} vectors upserted")


if __name__ == "__main__":
    run_formulation_vectorization()
