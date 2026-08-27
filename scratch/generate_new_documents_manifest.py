import os
import json

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
meta_dir = os.path.join(project_dir, "data", "legal_corpus", "metadata")
os.makedirs(meta_dir, exist_ok=True)

manifest_file = os.path.join(meta_dir, "new_documents_manifest.json")

manifest_data = {
  "manifest_title": "P0 Missing Legal & Regulatory Documents Acquisition Audit",
  "timestamp": "2026-08-27T11:22:30+05:30",
  "total_documents_requested": 4,
  "documents_successfully_collected": 0,
  "documents_unavailable": 4,
  "documents": [
    {
      "key": "fssai_nutraceuticals_2022",
      "filename": "FSSAI_Health_Supplements_Nutraceuticals_Regulations_2022.pdf",
      "title": "Food Safety and Standards (Health Supplements, Nutraceuticals, Food for Special Dietary Use, Food for Special Medical Purpose, and Prebiotic and Probiotic Food) Regulations, 2022",
      "authority": "Food Safety and Standards Authority of India (FSSAI)",
      "jurisdiction": "IN",
      "document_type": "regulation",
      "version": "gazette_2022",
      "source_url": "https://www.fssai.gov.in/upload/notifications/2022/03/6244439c636ffGazette_Notification_Health_Supplements_30_03_2022.pdf",
      "sha256": None,
      "file_size_bytes": 0,
      "status": "NOT_VERIFIED",
      "reason": "The official FSSAI portal (fssai.gov.in) has migrated to a dynamic single-page web framework. Legacy static URL returned HTML app wrapper. Per explicit instructions, downloading random third-party replacements was avoided.",
      "retrieved_at": "2026-08-27T11:22:30+05:30"
    },
    {
      "key": "phytopharmaceuticals_2015",
      "filename": "Phytopharmaceuticals_Amendment_Rules_2015_GSR918E.pdf",
      "title": "Drugs and Cosmetics (Phytopharmaceutical Drugs) Amendment Rules, 2015 — GSR 918(E)",
      "authority": "Central Drugs Standard Control Organisation (CDSCO), Ministry of Health and Family Welfare",
      "jurisdiction": "IN",
      "document_type": "rules_amendment",
      "version": "GSR_918_E_2015",
      "source_url": "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/GSR918.pdf",
      "sha256": None,
      "file_size_bytes": 0,
      "status": "NOT_VERIFIED",
      "reason": "The CDSCO OpenCMS portal (cdsco.gov.in) restructured its document paths. Direct static URL returned HTTP 404 Not Found. Official gazette requires manual download from egazette.gov.in portal. Per instructions, random third-party copies were avoided.",
      "retrieved_at": "2026-08-27T11:22:30+05:30"
    },
    {
      "key": "nba_form_11",
      "filename": "NBA_Form_11_ABS_Application.pdf",
      "title": "National Biodiversity Authority Form 11 — Application Form for ABS Clearance",
      "authority": "National Biodiversity Authority (NBA), Ministry of Environment, Forest and Climate Change",
      "jurisdiction": "IN",
      "document_type": "official_form",
      "version": "e_ABS_2024",
      "source_url": "https://nbaindia.org/uploaded/pdf/Form1.pdf",
      "sha256": None,
      "file_size_bytes": 0,
      "status": "NOT_VERIFIED",
      "reason": "The National Biodiversity Authority portal (nbaindia.org) migrated to the online e-ABS filing system (abs.nbaindia.org). Legacy static link redirected to NBA homepage. Per instructions, unverified third-party forms were avoided.",
      "retrieved_at": "2026-08-27T11:22:30+05:30"
    },
    {
      "key": "state_biodiversity_board_bmc_form",
      "filename": "State_Biodiversity_Board_BMC_PBR_Form.pdf",
      "title": "State Biodiversity Board / BMC People's Biodiversity Register (PBR) Access & Documentation Form",
      "authority": "State Biodiversity Boards (SBBs) & National Biodiversity Authority",
      "jurisdiction": "IN",
      "document_type": "state_form",
      "version": "state_specific",
      "source_url": "https://nbaindia.org/uploaded/pdf/PBR_Guidelines.pdf",
      "sha256": None,
      "file_size_bytes": 0,
      "status": "NOT_VERIFIED",
      "reason": "No canonical single national PDF form exists for BMC/SBB PBR filings; forms are statutory rules issued by individual State Biodiversity Boards (e.g. Karnataka, Kerala, Uttarakhand SBBs). Legacy NBA URL redirected to home. Per instructions, random unverified forms were avoided.",
      "retrieved_at": "2026-08-27T11:22:30+05:30"
    }
  ],
  "next_ingestion_step": "When official gazette PDF files are manually acquired from egazette.gov.in, fssai.gov.in, and abs.nbaindia.org, place them in data/legal_corpus/ and re-run pipeline/phase1_ingest.py and phase2_vectorize.py."
}

with open(manifest_file, 'w', encoding='utf-8') as f:
    json.dump(manifest_data, f, indent=2)

print(f"Manifest written to {manifest_file}")
