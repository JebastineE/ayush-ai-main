import os
import json
import ssl
import urllib.request
import hashlib

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
legal_dir = os.path.join(project_dir, "data", "legal_corpus")
forms_dir = os.path.join(legal_dir, "forms")

os.makedirs(forms_dir, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
except Exception:
    pass

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

test_urls = [
    ("fssai_nutra", "https://www.fssai.gov.in/upload/notifications/2022/03/6244439c636ffGazette_Notification_Health_Supplements_30_03_2022.pdf", legal_dir, "FSSAI_Health_Supplements_Nutraceuticals_Regulations_2022.pdf"),
    ("cdsco_gsr918", "https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/GSR918.pdf", legal_dir, "Phytopharmaceuticals_Amendment_Rules_2015_GSR918E.pdf"),
    ("nba_form1", "https://nbaindia.org/uploaded/pdf/Form1.pdf", forms_dir, "NBA_Form_I_Access_Biological_Resources.pdf"),
    ("nba_pbr", "https://nbaindia.org/uploaded/pdf/PBR_Guidelines.pdf", forms_dir, "BMC_Peoples_Biodiversity_Register_PBR_Guidelines_Form.pdf")
]

for name, url, folder, fname in test_urls:
    print(f"\nTesting {name} -> {url}")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = resp.read()
            print(f"  Status: {resp.status} | Content-Type: {resp.headers.get('Content-Type')} | Length: {len(data):,}")
            if data.startswith(b"%PDF"):
                dest = os.path.join(folder, fname)
                with open(dest, 'wb') as f:
                    f.write(data)
                print(f"  SAVED VALID PDF TO {dest}")
            else:
                print(f"  Header preview: {data[:100]}")
    except Exception as e:
        print(f"  Failed: {e}")
