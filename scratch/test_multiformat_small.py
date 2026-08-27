import os
import sys
import json
import csv
from pathlib import Path

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
sys.path.insert(0, project_dir)

from pipeline.phase1_ingest import process_legal_corpus, process_json_file, process_csv_file
from pipeline.phase2_vectorize import load_model, chunk_id_to_uuid

test_dir = Path(project_dir) / "scratch" / "test_data"
test_dir.mkdir(parents=True, exist_ok=True)

# 1. Create sample JSON file
sample_json_path = test_dir / "sample_ayush_drugs.json"
sample_json_data = [
    {
        "id": "AYUSH-001",
        "drug_name": "Ashwagandharishta",
        "system": "Ayurveda",
        "therapeutic_use": "Nervine tonic, anxiety, general debility",
        "classical_reference": "Bhaishajya Ratnavali",
        "schedule": "First Schedule"
    },
    {
        "id": "AYUSH-002",
        "drug_name": "Sudarshan Churna",
        "system": "Ayurveda",
        "therapeutic_use": "Fever, immune booster, digestive disorders",
        "classical_reference": "Sarangadhara Samhita",
        "schedule": "First Schedule"
    }
]

with open(sample_json_path, 'w', encoding='utf-8') as f:
    json.dump(sample_json_data, f, indent=2)

# 2. Create sample CSV file
sample_csv_path = test_dir / "sample_formulations.csv"
sample_csv_rows = [
    ["Formulation_Name", "Active_Ingredient", "Classical_Source", "Regime"],
    ["Bhringamalakadi Taila", "Bhringraj, Amla", "Sahasrayogam", "Classical Medicine"],
    ["Chyawanprash", "Amla, Dashmoola", "Charaka Samhita", "Classical Medicine"],
    ["Herbal Cough Drops", "Menthol, Tulsi", "Proprietary Formula", "Proprietary Medicine"]
]

with open(sample_csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(sample_csv_rows)

# 3. Select 1 small PDF from data/legal_corpus/
sample_pdf_path = Path(project_dir) / "data" / "legal_corpus" / "Patents (Amendment) Rules, 2024.pdf"

print("=== STEP 10 — TESTING SMALL MULTI-FORMAT INGESTION ===")
log = {}

# A. Test PDF Path
pdf_chunks = []
if sample_pdf_path.exists():
    print(f"\n[1/3] Testing PDF Processing Path on: {sample_pdf_path.name}")
    # Process single PDF file directly
    from pipeline.phase1_ingest import extract_pdf_pages, chunk_text, slugify, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS, LEGAL_COLLECTION
    pages = extract_pdf_pages(sample_pdf_path)
    stem_slug = slugify(sample_pdf_path.stem)
    for p_idx, p in enumerate(pages[:2]): # test first 2 pages
        p_text = p.get("text", "")
        p_chunks = chunk_text(p_text, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)
        for c_idx, c_text in enumerate(p_chunks[:2]):
            pdf_chunks.append({
                "chunk_id": f"{stem_slug}_p{p_idx+1}_c{c_idx}",
                "source_file": sample_pdf_path.name,
                "source_type": "pdf",
                "page_number": p_idx + 1,
                "chunk_index": c_idx,
                "text": c_text,
                "collection": LEGAL_COLLECTION
            })
    print(f"  --> Generated {len(pdf_chunks)} PDF chunks.")
    if pdf_chunks:
        print(f"  --> Sample PDF Chunk Metadata: {json.dumps(pdf_chunks[0], indent=2)}")

# B. Test JSON Path
print(f"\n[2/3] Testing JSON Processing Path on: {sample_json_path.name}")
json_chunks, log = process_json_file(sample_json_path, log)
print(f"  --> Generated {len(json_chunks)} JSON chunks.")
if json_chunks:
    print(f"  --> Sample JSON Chunk Metadata: {json.dumps(json_chunks[0], indent=2)}")

# C. Test CSV Path
print(f"\n[3/3] Testing CSV Processing Path on: {sample_csv_path.name}")
csv_chunks, log = process_csv_file(sample_csv_path, log)
print(f"  --> Generated {len(csv_chunks)} CSV chunks.")
if csv_chunks:
    print(f"  --> Sample CSV Chunk Metadata: {json.dumps(csv_chunks[0], indent=2)}")

# D. Test Embedding Integration (InLegalBERT)
print("\n=== STEP 11 — EMBEDDING VALIDATION WITH INLEGALBERT ===")
all_test_chunks = pdf_chunks + json_chunks + csv_chunks
print(f"Total Test Chunks across formats: {len(all_test_chunks)}")

print("Loading InLegalBERT model...")
model = load_model()

texts = [c["text"] for c in all_test_chunks]
print(f"Generating embeddings for {len(texts)} chunks...")
embeddings = model.encode(texts, batch_size=len(texts), show_progress_bar=False, normalize_embeddings=True)

print(f"✅ Success! Embeddings shape: {embeddings.shape}")
print(f"   Each chunk has a {embeddings.shape[1]}-dimensional vector.")

validation_results = {
    "pdf_chunks_count": len(pdf_chunks),
    "json_chunks_count": len(json_chunks),
    "csv_chunks_count": len(csv_chunks),
    "embedding_dimension": int(embeddings.shape[1]),
    "status": "PASSED_VERIFIED"
}

out_test_res = Path(project_dir) / "scratch" / "multiformat_test_results.json"
with open(out_test_res, 'w', encoding='utf-8') as f:
    json.dump(validation_results, f, indent=2)

print(f"\nSmall test completed successfully. Results saved to {out_test_res}")
