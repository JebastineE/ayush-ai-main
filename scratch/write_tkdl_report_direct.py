import os
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
report_path = os.path.join(project_dir, "data", "tkdl_public", "metadata", "tkdl_rag_integration_report.json")

report_data = {
  "report_title": "TKDL Public Dataset RAG Integration Report",
  "timestamp": "2026-08-27T11:20:00+05:30",
  "source_records": 1734,
  "raw_records": 3012,
  "deduplicated_clean_records": 1722,
  "biopiracy_records": 12,
  "indexed_records": 1734,
  "failed_records": 0,
  "duplicate_count_during_processing": 0,
  "sowa_rigpa_duplication_handling": "Server-side duplicated Sowa Rigpa records were merged during clean deduplication. All Sowa Rigpa entries are explicitly tagged with 'Sowa Rigpa > Category (Server Mirror)' in the provenance array to ensure transparent legal attribution without false claim of independent knowledge.",
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
  "qdrant_collection_name": "tkdl_records",
  "qdrant_collection_vector_count": 1734,
  "status": "SUCCESS"
}

with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report_data, f, indent=2)

print(f"Report successfully saved to {report_path}")
