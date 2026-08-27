import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main")
DATA_DIR = BASE_DIR / "data"

pdf_files = []
json_files = []
csv_files = []

for root, _, files in os.walk(DATA_DIR):
    if "qdrant_store" in root or "processed" in root or "backup" in root:
        continue
    for file in files:
        ext = file.lower().split('.')[-1]
        filepath = Path(root) / file
        if ext == 'pdf':
            pdf_files.append(filepath)
        elif ext == 'json' and 'metadata' not in root and file != 'benchmark_results.json' and file != 'ip_sakti_benchmark.json' and file != 'citation_validation_report.json' and file != 'new_documents_manifest.json':
            json_files.append(filepath)
        elif ext == 'csv':
            csv_files.append(filepath)

def report_files(files, name):
    total_size = sum(os.path.getsize(f) for f in files)
    print(f"--- {name} ---")
    print(f"Count: {len(files)}")
    print(f"Total Size: {total_size / (1024*1024):.2f} MB")
    if len(files) < 10:
        for f in files:
            print(f"  - {f.relative_to(BASE_DIR)}")

report_files(pdf_files, "PDF Files")
report_files(json_files, "JSON Files")
report_files(csv_files, "CSV Files")
