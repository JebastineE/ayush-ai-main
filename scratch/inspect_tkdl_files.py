import os
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"

clean_file = os.path.join(project_dir, "data", "tkdl_public", "clean", "clean_keyword_records.json")
sample_file = os.path.join(project_dir, "data", "traditional_knowledge", "tkdl_sample_dataset.json")

print("=== 1. CLEAN KEYWORD RECORDS SCHEMA ===")
if os.path.exists(clean_file):
    with open(clean_file, 'r', encoding='utf-8') as f:
        cdata = json.load(f)
        recs = cdata.get("records", [])
        print(f"Total clean records: {len(recs)}")
        if recs:
            print("Sample clean record keys:", list(recs[0].keys()))
            print("Sample clean record:", json.dumps(recs[0], indent=2, ensure_ascii=False))

print("\n=== 2. OLD SAMPLE DATASET SCHEMA ===")
if os.path.exists(sample_file):
    with open(sample_file, 'r', encoding='utf-8') as f:
        sdata = json.load(f)
        print(f"Total sample records: {len(sdata)}")
        if sdata:
            print("Sample record keys:", list(sdata[0].keys()))
            print("Sample record:", json.dumps(sdata[0], indent=2, ensure_ascii=False))
