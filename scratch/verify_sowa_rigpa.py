import os
import json
import ssl
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
tkdl_dir = os.path.join(project_dir, "data", "tkdl_public")
ayurveda_dir = os.path.join(tkdl_dir, "ayurveda")
sowa_rigpa_dir = os.path.join(tkdl_dir, "sowa_rigpa")
raw_dir = os.path.join(tkdl_dir, "raw")

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

print("==================================================")
print("     SOWA RIGPA VS AYURVEDA DATA INTEGRITY AUDIT")
print("==================================================")

categories = [
    "plant_name",
    "plant_part_and_product",
    "animal_name",
    "animal_part_and_product",
    "metals___mineral_name",
    "devices___apparatus",
    "products___processes___related_terms",
    "all_diseases",
    "drug_action___properties",
    "mode_of_administration",
    "others"
]

audit_results = []

for cat in categories:
    ayu_json_path = os.path.join(ayurveda_dir, f"{cat}.json")
    sr_json_path = os.path.join(sowa_rigpa_dir, f"{cat}.json")
    
    ayu_data = {}
    sr_data = {}
    
    if os.path.exists(ayu_json_path):
        with open(ayu_json_path, 'r', encoding='utf-8') as f:
            ayu_data = json.load(f)
            
    if os.path.exists(sr_json_path):
        with open(sr_json_path, 'r', encoding='utf-8') as f:
            sr_data = json.load(f)

    ayu_url = ayu_data.get("source_url", "")
    sr_url = sr_data.get("source_url", "")
    
    ayu_recs = ayu_data.get("records", [])
    sr_recs = sr_data.get("records", [])

    ayu_count = len(ayu_recs)
    sr_count = len(sr_recs)

    # Compare column contents
    ayu_cols_list = [" | ".join(r.get("columns", [])) for r in ayu_recs]
    sr_cols_list = [" | ".join(r.get("columns", [])) for r in sr_recs]

    ayu_set = set(ayu_cols_list)
    sr_set = set(sr_cols_list)

    overlap = len(ayu_set.intersection(sr_set))
    overlap_pct = (overlap / max(1, len(sr_set))) * 100.0 if sr_set else 0.0

    identical_by_position = 0
    min_len = min(ayu_count, sr_count)
    for i in range(min_len):
        if ayu_cols_list[i] == sr_cols_list[i]:
            identical_by_position += 1

    byte_for_byte_identical = (ayu_cols_list == sr_cols_list)

    print(f"\n--- Category: '{cat}' ---")
    print(f"  Ayurveda URL  : {ayu_url}")
    print(f"  Sowa Rigpa URL: {sr_url}")
    print(f"  Ayurveda Count: {ayu_count} | Sowa Rigpa Count: {sr_count}")
    print(f"  Overlap Count : {overlap} / {len(sr_set)} ({overlap_pct:.1f}%)")
    print(f"  Positional Identical: {identical_by_position} / {min_len}")
    print(f"  Byte-for-byte identical lists: {byte_for_byte_identical}")

    conclusion = "VALID"
    evidence = []

    if ayu_url == sr_url:
        conclusion = "COLLECTION BUG"
        evidence.append(f"Sowa Rigpa source URL ({sr_url}) is identical to Ayurveda source URL ({ayu_url}).")

    if byte_for_byte_identical and sr_count > 0:
        conclusion = "COLLECTION BUG"
        evidence.append("Sowa Rigpa records are 100% byte-for-byte identical to Ayurveda records.")
    elif overlap_pct > 80:
        conclusion = "SUSPICIOUS"
        evidence.append(f"High overlap percentage ({overlap_pct:.1f}%) between Sowa Rigpa and Ayurveda.")

    if not evidence:
        evidence.append("Records and URLs are distinct and valid.")

    audit_results.append({
        "category": cat,
        "ayurveda_url": ayu_url,
        "sowa_rigpa_url": sr_url,
        "ayurveda_count": ayu_count,
        "sowa_rigpa_count": sr_count,
        "overlap_count": overlap,
        "overlap_percentage": round(overlap_pct, 2),
        "identical_records": identical_by_position,
        "byte_for_byte_identical": byte_for_byte_identical,
        "conclusion": conclusion,
        "evidence": " ".join(evidence)
    })

print("\n==================================================")
print("  CHECKING ACTUAL SOWA RIGPA ENDPOINTS ON WEBSITE")
print("==================================================")

sowarigpa_entry = "https://www.tkdl.res.in/tkdl/langdefault/Sowarigpa/KeywordHelp/KeywordDemo/keyword.asp"
print(f"Fetching entry URL: {sowarigpa_entry}")

req = urllib.request.Request(sowarigpa_entry, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        print(f"Entry page title: '{soup.title.string if soup.title else ''}'")
        print(f"Found {len(links)} links on Sowarigpa keyword.asp:")
        for a in links:
            text = a.get_text(strip=True)
            href = a.get('href', '')
            cat_url = urljoin(sowarigpa_entry, href)
            print(f"  '{text}' -> href='{href}' | absolute='{cat_url}'")
            
            # Fetch F- page and check iframe src
            try:
                f_html = urllib.request.urlopen(urllib.request.Request(cat_url, headers=headers), context=ctx).read().decode('utf-8', errors='ignore')
                f_soup = BeautifulSoup(f_html, 'html.parser')
                iframes = f_soup.find_all(['iframe', 'frame'])
                for f_tag in iframes:
                    src = f_tag.get('src', '')
                    data_url = urljoin(cat_url, src)
                    print(f"    -> frame src: '{src}' | absolute: '{data_url}'")
            except Exception as fe:
                print(f"    -> Error fetching F- page: {fe}")

except Exception as e:
    print(f"Error fetching entry page: {e}")
