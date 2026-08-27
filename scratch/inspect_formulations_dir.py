import os
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
form_dir = os.path.join(project_dir, "data", "tkdl_public", "formulations")

print("=== FORMULATIONS DATASET AUDIT ===")
for root, dirs, files in os.walk(form_dir):
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, project_dir)
        size = os.path.getsize(fp)
        print(f"\nFile: {rel} ({size} bytes)")
        if f.endswith('.json'):
            with open(fp, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
                if isinstance(data, dict):
                    print("  Keys:", list(data.keys()))
                    if "records" in data:
                        recs = data["records"]
                        print("  Record count:", len(recs))
                    if "records_found" in data:
                        print("  records_found:", data["records_found"])
                    if "accessible" in data:
                        print("  accessible:", data["accessible"])
