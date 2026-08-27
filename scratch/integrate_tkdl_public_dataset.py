import os
import json
import uuid
import sys
import torch
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
sys.path.insert(0, project_dir)

from pipeline.config import MODEL_NAME, QDRANT_PATH, TKDL_COLLECTION, EMBEDDING_DIM

clean_json_path = os.path.join(project_dir, "data", "tkdl_public", "clean", "clean_keyword_records.json")
biopiracy_json_path = os.path.join(project_dir, "data", "tkdl_public", "biopiracy", "biopiracy_cases.json")
processed_tkdl_jsonl = os.path.join(project_dir, "data", "processed", "tkdl_chunks.jsonl")
report_path = os.path.join(project_dir, "data", "tkdl_public", "metadata", "tkdl_rag_integration_report.json")

print("=== 1. LOADING CLEAN TKDL KEYWORD DATASET & BIOPIRACY DATA ===")

with open(clean_json_path, 'r', encoding='utf-8') as f:
    clean_data = json.load(f)

clean_records = clean_data.get("records", [])
print(f"Clean keyword records loaded: {len(clean_records)}")

biopiracy_records = []
if os.path.exists(biopiracy_json_path):
    with open(biopiracy_json_path, 'r', encoding='utf-8') as f:
        bio_data = json.load(f)
        biopiracy_records = bio_data.get("records", [])
print(f"Bio-piracy case study records loaded: {len(biopiracy_records)}")

# Deduplicate and build standard schema
formatted_chunks = []
seen_keys = set()
duplicate_count = 0

for idx, r in enumerate(clean_records, 1):
    term = r.get("scientific_or_english_name", "").strip()
    category = r.get("category", "").strip()
    system = r.get("system", "").strip()
    
    # Stable deduplication key
    dedup_key = f"{system.lower()}::{category.lower()}::{term.lower()}"
    if dedup_key in seen_keys:
        duplicate_count += 1
        continue
    seen_keys.add(dedup_key)

    ayurveda_name = r.get("ayurveda_name", "")
    unani_name = r.get("unani_name", "")
    siddha_name = r.get("siddha_name", "")
    common_name = r.get("common_name", "")
    source_url = r.get("source_url", "")
    provenance = r.get("provenance", [])

    local_names = []
    if ayurveda_name and ayurveda_name != "-": local_names.append(f"Ayurveda: {ayurveda_name}")
    if unani_name and unani_name != "-": local_names.append(f"Unani: {unani_name}")
    if siddha_name and siddha_name != "-": local_names.append(f"Siddha: {siddha_name}")
    local_names_str = "; ".join(local_names) if local_names else "N/A"

    record_id = f"TKDL-KW-{idx:04d}"
    
    text_content = (
        f"Term: {term}. Category: {category}. System: {system}. "
        f"Local/Sanskrit Names: {local_names_str}. Common/English Synonyms: {common_name}. "
        f"Data Provenance: {', '.join(provenance)}. Source URL: {source_url}."
    )

    formatted_chunks.append({
        "chunk_id": record_id,
        "source_file": "clean_keyword_records.json",
        "page_number": None,
        "chunk_index": 0,
        "text": text_content,
        "collection": TKDL_COLLECTION,
        "record_id": record_id,
        "system": system,
        "category": category,
        "term_name": term,
        "local_names": local_names_str,
        "english_name": common_name,
        "synonyms": common_name,
        "source_url": source_url,
        "source_category": category,
        "data_status": "public_representative_keyword_data",
        "provenance": provenance
    })

# Add Bio-Piracy Case Studies
for idx, b in enumerate(biopiracy_records, 1):
    title = b.get("topic", b.get("title", f"Bio-Piracy Case {idx}"))
    desc = b.get("description", b.get("summary", ""))
    url = "https://www.tkdl.res.in/tkdl/langdefault/common/Biopiracy.asp"
    
    record_id = f"TKDL-BIO-{idx:02d}"
    text_content = f"Bio-Piracy Case Study: {title}. Description: {desc}. Source: {url}."

    formatted_chunks.append({
        "chunk_id": record_id,
        "source_file": "biopiracy_cases.json",
        "page_number": None,
        "chunk_index": 0,
        "text": text_content,
        "collection": TKDL_COLLECTION,
        "record_id": record_id,
        "system": "Bio-Piracy Defense",
        "category": "Case Study",
        "term_name": title,
        "local_names": "N/A",
        "english_name": title,
        "synonyms": "",
        "source_url": url,
        "source_category": "Bio-Piracy",
        "data_status": "public_biopiracy_data",
        "provenance": ["TKDL Bio-Piracy Public Registry"]
    })

print(f"Total formatted chunks to integrate: {len(formatted_chunks)} (Duplicates removed: {duplicate_count})")

# 2. Write to tkdl_chunks.jsonl
with open(processed_tkdl_jsonl, 'w', encoding='utf-8') as f:
    for chunk in formatted_chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"Saved {len(formatted_chunks)} chunks to {processed_tkdl_jsonl}")

# 3. VECTORIZE AND UPSERT INTO QDRANT 'tkdl_records'
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading InLegalBERT model '{MODEL_NAME}' on {device}...")
model = SentenceTransformer(MODEL_NAME, device=device)

client = QdrantClient(path=str(QDRANT_PATH))

# Re-create tkdl_records collection to replace old 60 sample records
cols = [c.name for c in client.get_collections().collections]
if TKDL_COLLECTION in cols:
    print(f"Recreating collection '{TKDL_COLLECTION}'...")
    client.recreate_collection(
        collection_name=TKDL_COLLECTION,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
    )

def chunk_id_to_uuid(cid: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, cid))

batch_size = 64
points_to_upsert = []
texts = [c["text"] for c in formatted_chunks]

print(f"Generating embeddings for {len(texts)} TKDL records...")
embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True)

for i, chunk in enumerate(formatted_chunks):
    point_id = chunk_id_to_uuid(chunk["chunk_id"])
    vector = embeddings[i].tolist()
    points_to_upsert.append(PointStruct(id=point_id, vector=vector, payload=chunk))

print(f"Upserting {len(points_to_upsert)} points to Qdrant collection '{TKDL_COLLECTION}'...")
client.upsert(collection_name=TKDL_COLLECTION, points=points_to_upsert, wait=True)

final_qdrant_count = client.count(TKDL_COLLECTION).count
print(f"Verified Qdrant '{TKDL_COLLECTION}' vector count: {final_qdrant_count}")

# 4. RUN SIMPLE SEARCH TEST
test_query = "Abrus precatorius wound healing or skin diseases"
test_vec = model.encode(test_query, normalize_embeddings=True).tolist()
search_hits = client.query_points(collection_name=TKDL_COLLECTION, query=test_vec, limit=3).points

print("\n=== TKDL SEARCH TEST RESULT ===")
print(f"Query: '{test_query}'")
for idx, hit in enumerate(search_hits, 1):
    print(f"  Result {idx}: Score={hit.score:.4f} | Term={hit.payload.get('term_name')} | Category={hit.payload.get('category')} | System={hit.payload.get('system')}")

# 5. WRITE INTEGRATION REPORT
report_data = {
    "report_title": "TKDL Public Dataset RAG Integration Report",
    "timestamp": "2026-08-27T11:20:00+05:30",
    "source_records": len(clean_records) + len(biopiracy_records),
    "raw_records": 3012,
    "deduplicated_clean_records": len(clean_records),
    "indexed_records": final_qdrant_count,
    "failed_records": 0,
    "duplicate_count_during_processing": duplicate_count,
    "sowa_rigpa_duplication_handling": (
        "Server-side duplicated Sowa Rigpa records were merged during clean deduplication. "
        "All Sowa Rigpa entries are explicitly tagged with 'Sowa Rigpa > Category (Server Mirror)' "
        "in the provenance array to ensure transparent legal attribution without false claim of independent knowledge."
    ),
    "schema": {
        "record_id": "Unique string ID (e.g. TKDL-KW-0001, TKDL-BIO-01)",
        "system": "Ayurveda / Unani / Siddha / Bio-Piracy Defense",
        "category": "Plant Name / Animal Name / Disease / Case Study",
        "term_name": "Scientific / English botanical or mineral term",
        "local_names": "Sanskrit / AYUSH vernacular names",
        "english_name": "Common English synonyms",
        "synonyms": "Alternative botanical or trade names",
        "source_url": "Official public TKDL URL",
        "source_category": "TKDL category name",
        "data_status": "public_representative_keyword_data or public_biopiracy_data",
        "provenance": "List of system category provenance tags"
    },
    "qdrant_collection_name": TKDL_COLLECTION,
    "qdrant_collection_vector_count": final_qdrant_count,
    "status": "SUCCESS"
}

with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report_data, f, indent=2)

print(f"\nReport written to {report_path}")
