import os
import json
import sys

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
sys.path.insert(0, project_dir)

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, PayloadSchemaType
from pipeline.phase2_vectorize import run_vectorization
from pipeline.config import QDRANT_PATH, LEGAL_COLLECTION

print("=== 1. RUNNING PHASE 2 VECTORIZATION ===")
run_vectorization()

print("\n=== 2. CREATING PAYLOAD INDEX ===")
client = QdrantClient(path=str(QDRANT_PATH))
try:
    client.create_payload_index(
        collection_name=LEGAL_COLLECTION,
        field_name="jurisdiction",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("Created payload index for 'jurisdiction'.")
except Exception as e:
    print(f"Payload index creation note: {e}")

print("\n=== 3. VERIFYING QDRANT PAYLOADS ===")
res = client.scroll(LEGAL_COLLECTION, limit=5)
for p in res[0]:
    print(f"Point ID: {p.id} | source_file: {p.payload.get('source_file')} | jurisdiction: {p.payload.get('jurisdiction')}")
