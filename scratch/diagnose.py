import sys
from pathlib import Path

BASE_DIR = Path(r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main")
sys.path.append(str(BASE_DIR))

from pipeline.phase2_vectorize import get_or_create_qdrant_client, load_model
from pipeline.config import LEGAL_COLLECTION
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = get_or_create_qdrant_client()
model = load_model()

query = "What medicinal plant information is available for Withania somnifera (Ashwagandha) in the traditional knowledge dataset?"
vec = model.encode(query, normalize_embeddings=True).tolist()

print("\n--- TEST 1: RAW SEARCH (NO FILTER) ---")
results_raw = client.query_points(
    collection_name=LEGAL_COLLECTION,
    query=vec,
    limit=5
).points

for p in results_raw:
    src_type = p.payload.get("source_type")
    src_file = p.payload.get("source_file")
    jurisdiction = p.payload.get("jurisdiction")
    print(f"Score: {p.score:.4f} | Type: {src_type} | Jur: {jurisdiction} | File: {src_file}")

print("\n--- TEST 2: JURISDICTION = IN (RAG DEFAULT) ---")
qfilter = Filter(must=[FieldCondition(key="jurisdiction", match=MatchValue(value="IN"))])
try:
    results_filtered = client.query_points(
        collection_name=LEGAL_COLLECTION,
        query=vec,
        query_filter=qfilter,
        limit=5
    ).points

    for p in results_filtered:
        src_type = p.payload.get("source_type")
        src_file = p.payload.get("source_file")
        jurisdiction = p.payload.get("jurisdiction")
        print(f"Score: {p.score:.4f} | Type: {src_type} | Jur: {jurisdiction} | File: {src_file}")
except Exception as e:
    print("Filter failed:", repr(e))

print("\n--- TEST 3: CHECK JSON METADATA PAYLOAD ---")
res_json = client.scroll(
    collection_name=LEGAL_COLLECTION,
    scroll_filter=Filter(must=[FieldCondition(key="source_type", match=MatchValue(value="json"))]),
    limit=1
)
if res_json[0]:
    payload = res_json[0][0].payload
    print("JSON Chunk Payload Keys:", list(payload.keys()))
    print("Has jurisdiction?:", "jurisdiction" in payload)
else:
    print("No JSON chunks found or filter failed.")

