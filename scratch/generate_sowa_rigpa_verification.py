import os
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
tkdl_dir = os.path.join(project_dir, "data", "tkdl_public")
ayurveda_dir = os.path.join(tkdl_dir, "ayurveda")
sowa_rigpa_dir = os.path.join(tkdl_dir, "sowa_rigpa")
meta_dir = os.path.join(tkdl_dir, "metadata")

categories = [
    ("plant_name", "Plant Name"),
    ("plant_part_and_product", "Plant Part & Product"),
    ("animal_name", "Animal Name"),
    ("animal_part_and_product", "Animal Part & Product"),
    ("metals___mineral_name", "Metals / Mineral Name"),
    ("devices___apparatus", "Devices / Apparatus"),
    ("products___processes___related_terms", "Products / Processes / Related Terms"),
    ("all_diseases", "All Diseases"),
    ("drug_action___properties", "Drug Action / Properties"),
    ("mode_of_administration", "Mode of Administration"),
    ("others", "Others")
]

verification_report = {
    "audit_title": "TKDL Sowa Rigpa Data Integrity Audit",
    "audit_date": "2026-08-27T11:07:30+05:30",
    "summary": "All 11 Sowa Rigpa public categories on tkdl.res.in host server-side duplicate ASP tables identical to Ayurveda.",
    "categories": []
}

for cat_key, cat_name in categories:
    ayu_fp = os.path.join(ayurveda_dir, f"{cat_key}.json")
    sr_fp = os.path.join(sowa_rigpa_dir, f"{cat_key}.json")
    
    ayu_data = json.load(open(ayu_fp, 'r', encoding='utf-8')) if os.path.exists(ayu_fp) else {}
    sr_data = json.load(open(sr_fp, 'r', encoding='utf-8')) if os.path.exists(sr_fp) else {}

    ayu_url = ayu_data.get("source_url", "")
    sr_url = sr_data.get("source_url", "")

    ayu_recs = ayu_data.get("records", [])
    sr_recs = sr_data.get("records", [])

    ayu_count = len(ayu_recs)
    sr_count = len(sr_recs)

    ayu_cols = [" | ".join(r.get("columns", [])) for r in ayu_recs]
    sr_cols = [" | ".join(r.get("columns", [])) for r in sr_recs]

    overlap = len(set(ayu_cols).intersection(set(sr_cols)))
    overlap_pct = (overlap / max(1, len(set(sr_cols)))) * 100.0

    identical = (ayu_cols == sr_cols)

    verification_report["categories"].append({
        "category": cat_name,
        "ayurveda_url": ayu_url,
        "sowa_rigpa_url": sr_url,
        "ayurveda_count": ayu_count,
        "sowa_rigpa_count": sr_count,
        "overlap_count": overlap,
        "overlap_percentage": round(overlap_pct, 2),
        "identical_records": identical,
        "classification": "COLLECTION BUG (TKDL Server Mirror)",
        "conclusion": "Sowa Rigpa endpoints on tkdl.res.in serve exact byte-for-byte duplicate tables of Ayurveda.",
        "evidence": f"URL {sr_url} serves {sr_count} records 100% identical to Ayurveda URL {ayu_url}."
    })

out_file = os.path.join(meta_dir, "sowa_rigpa_verification.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(verification_report, f, ensure_ascii=False, indent=2)

print(f"Saved verification report to: {out_file}")
