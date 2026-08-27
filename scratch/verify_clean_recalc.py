import os
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
clean_json_path = os.path.join(project_dir, "data", "tkdl_public", "clean", "clean_keyword_records.json")

with open(clean_json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data.get("records", [])
print(f"Total Unique Records in clean dataset: {len(records)}")

# Count systems in provenance
sys_counts = {"ayurveda": 0, "unani": 0, "siddha": 0, "sowa_rigpa": 0, "unique_non_sowa": 0}
for r in records:
    prov = r.get("provenance", [])
    systems_in_prov = set(p.split(" > ")[0].lower() for p in prov)
    if "ayurveda" in systems_in_prov and "sowa rigpa" in systems_in_prov and len(systems_in_prov) == 2:
        sys_counts["ayurveda"] += 1
    for s in systems_in_prov:
        if s in sys_counts:
            sys_counts[s] += 1

print("Provenance breakdown:", sys_counts)
