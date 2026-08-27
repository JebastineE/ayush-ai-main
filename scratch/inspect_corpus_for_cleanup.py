import os
import json
import hashlib

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
corpus_dir = os.path.join(project_dir, "data", "legal_corpus")
processed_dir = os.path.join(project_dir, "data", "processed")

chunks_file = os.path.join(processed_dir, "legal_chunks.jsonl")
log_file = os.path.join(processed_dir, "ingestion_log.json")

def sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

print("=== 1. FILES IN DATA/LEGAL_CORPUS ===")
files = os.listdir(corpus_dir)
file_hashes = {}
for f in sorted(files):
    fp = os.path.join(corpus_dir, f)
    if os.path.isfile(fp):
        size = os.path.getsize(fp)
        h = sha256(fp)
        file_hashes[f] = (h, size)
        print(f"  {f:60s} | size: {size:10,} | hash: {h}")

print("\n=== 2. INGESTION LOG ENTRIES ===")
ingestion_log = {}
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        ingestion_log = json.load(f)
    for fname, fhash in ingestion_log.items():
        exists_on_disk = fname in file_hashes
        print(f"  Log: {fname:60s} | hash: {fhash} | on disk: {exists_on_disk}")

print("\n=== 3. CHUNKS FILE SOURCES ===")
chunk_sources = {}
if os.path.exists(chunks_file):
    with open(chunks_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip(): continue
            try:
                data = json.loads(line)
                src = data.get("source_file", "")
                chunk_sources[src] = chunk_sources.get(src, 0) + 1
            except Exception as e:
                print(f"Error reading line {line_num}: {e}")

for src, cnt in sorted(chunk_sources.items()):
    exists_on_disk = src in file_hashes
    print(f"  Chunk Source: {src:60s} | chunks: {cnt:5d} | on disk: {exists_on_disk}")
