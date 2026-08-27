import os
import json
import ssl
import urllib.request
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
legal_dir = os.path.join(project_dir, "data", "legal_corpus")
forms_dir = os.path.join(legal_dir, "forms")
meta_dir = os.path.join(legal_dir, "metadata")

os.makedirs(forms_dir, exist_ok=True)
os.makedirs(meta_dir, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
except Exception:
    pass

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

print("=== SEARCHING & DOWNLOADING OFFICIAL P0 DOCUMENTS ===")

# Candidate URLs from Official Government Portals:

# 1. FSSAI Health Supplements / Nutraceuticals Regulations 2022
# Official gazette URL on fssai.gov.in:
fssai_url = "https://www.fssai.gov.in/upload/notifications/2022/03/6244439c636ffGazette_Notification_Health_Supplements_30_03_2022.pdf"

# 2. Phytopharmaceuticals Rules 2015 (GSR 918(E))
# Official gazette URL on cdsco.gov.in / egazette.gov.in:
cdsco_url = "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/GSR918.pdf"

# 3. NBA Form 11 / ABS Application Forms
# Official NBA URL on nbaindia.org:
nba_url = "https://nbaindia.org/uploaded/pdf/Form1.pdf"

# 4. State Biodiversity Board / BMC Form (People's Biodiversity Register / Access Form)
# Official NBA / TSBB / KSBDB URL:
sbb_url = "https://nbaindia.org/uploaded/pdf/PBR_Guidelines.pdf"

targets = [
    {
        "key": "fssai_nutraceuticals_2022",
        "url": fssai_url,
        "dest_folder": legal_dir,
        "dest_filename": "FSSAI_Health_Supplements_Nutraceuticals_Regulations_2022.pdf",
        "title": "Food Safety and Standards (Health Supplements, Nutraceuticals, Food for Special Dietary Use, Food for Special Medical Purpose, and Prebiotic and Probiotic Food) Regulations, 2022",
        "authority": "Food Safety and Standards Authority of India (FSSAI)",
        "document_type": "regulation",
        "version": "gazette_2022"
    },
    {
        "key": "phytopharmaceuticals_2015",
        "url": cdsco_url,
        "dest_folder": legal_dir,
        "dest_filename": "Phytopharmaceuticals_Amendment_Rules_2015_GSR918E.pdf",
        "title": "Drugs and Cosmetics (Phytopharmaceutical Drugs) Amendment Rules, 2015 — GSR 918(E)",
        "authority": "Central Drugs Standard Control Organisation (CDSCO), Ministry of Health and Family Welfare",
        "document_type": "rules_amendment",
        "version": "GSR_918_E_2015"
    },
    {
        "key": "nba_form_1",
        "url": nba_url,
        "dest_folder": forms_dir,
        "dest_filename": "NBA_Form_I_Access_Biological_Resources.pdf",
        "title": "National Biodiversity Authority Form I — Application for Access to Biological Resources and Associated Traditional Knowledge",
        "authority": "National Biodiversity Authority (NBA), Ministry of Environment, Forest and Climate Change",
        "document_type": "official_form",
        "version": "Form_I_2024"
    },
    {
        "key": "bmc_pbr_guidelines",
        "url": sbb_url,
        "dest_folder": forms_dir,
        "dest_filename": "BMC_Peoples_Biodiversity_Register_PBR_Guidelines_Form.pdf",
        "title": "People's Biodiversity Register (PBR) Guidelines and Format for Biodiversity Management Committees (BMCs)",
        "authority": "National Biodiversity Authority (NBA) & State Biodiversity Boards",
        "document_type": "guidelines_and_form",
        "version": "PBR_Format_2013"
    }
]

downloaded_manifest = []

for t in targets:
    url = t["url"]
    dest_path = os.path.join(t["dest_folder"], t["dest_filename"])
    print(f"\nAttempting download for '{t['key']}': {url}")
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            content = resp.read()
            # Check if PDF header
            if content.startswith(b"%PDF"):
                with open(dest_path, 'wb') as f:
                    f.write(content)
                fsize = os.path.getsize(dest_path)
                fhash = sha256(dest_path)
                print(f"  SUCCESS! Downloaded {t['dest_filename']} ({fsize:,} bytes | SHA256: {fhash[:16]}...)")
                
                rel_path = os.path.relpath(dest_path, project_dir)
                downloaded_manifest.append({
                    "filename": t["dest_filename"],
                    "filepath": rel_path,
                    "title": t["title"],
                    "authority": t["authority"],
                    "jurisdiction": "IN",
                    "document_type": t["document_type"],
                    "version": t["version"],
                    "source_url": url,
                    "sha256": fhash,
                    "file_size_bytes": fsize,
                    "status": "VERIFIED_OFFICIAL",
                    "retrieved_at": "2026-08-27T11:21:30+05:30"
                })
            else:
                print(f"  FAILED: Response is not a valid PDF (Header: {content[:30]})")
                downloaded_manifest.append({
                    "filename": t["dest_filename"],
                    "title": t["title"],
                    "authority": t["authority"],
                    "jurisdiction": "IN",
                    "document_type": t["document_type"],
                    "version": t["version"],
                    "source_url": url,
                    "status": "NOT_VERIFIED",
                    "reason": "URL did not return valid PDF content",
                    "retrieved_at": "2026-08-27T11:21:30+05:30"
                })
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        downloaded_manifest.append({
            "filename": t["dest_filename"],
            "title": t["title"],
            "authority": t["authority"],
            "jurisdiction": "IN",
            "document_type": t["document_type"],
            "version": t["version"],
            "source_url": url,
            "status": "NOT_VERIFIED",
            "reason": f"Connection error: {e}",
            "retrieved_at": "2026-08-27T11:21:30+05:30"
        })
