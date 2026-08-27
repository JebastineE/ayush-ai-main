import os
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"

# Read ingestion_log.json
ingestion_log_path = os.path.join(project_dir, "data", "processed", "ingestion_log.json")
if os.path.exists(ingestion_log_path):
    print("=== INGESTION LOG ===")
    with open(ingestion_log_path, 'r', encoding='utf-8') as f:
        print(f.read())

# Search codebase for vector store / RAG ingestion references
print("\n=== SEARCHING CODEBASE FOR INGESTION & QDRANT LOGIC ===")
for root, dirs, files in os.walk(project_dir):
    if any(skip in root for skip in [".git", "node_modules", ".next", "__pycache__", ".venv", "venv", "data/qdrant_store"]):
        continue
    for file in files:
        if file.endswith((".py", ".ts", ".js")):
            fp = os.path.join(root, file)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if "legal_docs" in content or "tkdl_records" in content or "ingest" in content.lower():
                        rel = os.path.relpath(fp, project_dir)
                        print(f"File: {rel}")
            except Exception:
                pass
