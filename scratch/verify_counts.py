import os
import json
import csv

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
data_dir = os.path.join(project_dir, "data")
tkdl_dir = os.path.join(data_dir, "tkdl_public")

systems = ["ayurveda", "unani", "siddha", "sowa_rigpa"]

print("==================================================")
print("             TKDL REPORTED VS ACTUAL")
print("==================================================")

raw_records_by_system = {}
total_raw_records_actual = 0

for sys_name in systems:
    sys_path = os.path.join(tkdl_dir, sys_name)
    sys_count = 0
    print(f"\n--- System: {sys_name.upper()} ---")
    for f in sorted(os.listdir(sys_path)):
        if f.endswith('.json'):
            fp = os.path.join(sys_path, f)
            with open(fp, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
                recs = data.get("records", [])
                cnt = len(recs)
                sys_count += cnt
                print(f"  {f:35s}: {cnt} records")
    raw_records_by_system[sys_name] = sys_count
    total_raw_records_actual += sys_count

print(f"\nTotal Raw Records Actual: {total_raw_records_actual}")

# Check clean dataset
clean_json = os.path.join(tkdl_dir, "clean", "clean_keyword_records.json")
if os.path.exists(clean_json):
    with open(clean_json, 'r', encoding='utf-8') as jf:
        cdata = json.load(jf)
        crecs = cdata.get("records", [])
        print(f"Clean Dataset Unique Records: {len(crecs)}")
        print(f"Duplicates Removed: {cdata.get('duplicates_removed', 0)}")

# Check Bio-Piracy
bio_json = os.path.join(tkdl_dir, "biopiracy", "biopiracy_cases.json")
if os.path.exists(bio_json):
    with open(bio_json, 'r', encoding='utf-8') as jf:
        bdata = json.load(jf)
        brecs = bdata.get("records", [])
        print(f"Bio-Piracy Records: {len(brecs)}")

# Check Ayurveda Plant Name
ayu_plant = os.path.join(tkdl_dir, "ayurveda", "plant_name.json")
if os.path.exists(ayu_plant):
    with open(ayu_plant, 'r', encoding='utf-8') as jf:
        apdata = json.load(jf)
        aprecs = apdata.get("records", [])
        print(f"Ayurveda Plant Name Records: {len(aprecs)}")

print("\n==================================================")
print("             OTHER DATASETS INSPECTION")
print("==================================================")

for other_dir in ["legal_corpus", "traditional_knowledge", "processed", "test_mocks", "qdrant_store"]:
    dp = os.path.join(data_dir, other_dir)
    if os.path.exists(dp):
        print(f"\nPath: data/{other_dir}")
        for root, dirs, files in os.walk(dp):
            for file in files:
                filepath = os.path.join(root, file)
                rel = os.path.relpath(filepath, project_dir)
                size = os.path.getsize(filepath)
                print(f"  - {rel} ({size:,} bytes)")
