import os
import sys
import json
import csv
import ssl
import datetime
import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Ensure stdout uses UTF-8 encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup SSL context for legacy TLS negotiation on tkdl.res.in
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
try:
    ssl_ctx.set_ciphers('DEFAULT@SECLEVEL=1')
except Exception:
    pass

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "tkdl_public"))

SYSTEMS_CONFIG = {
    "ayurveda": {
        "name": "Ayurveda",
        "entry_url": "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/KeywordHelp/KeywordDemo/keyword.asp",
        "output_dir": os.path.join(BASE_DIR, "ayurveda")
    },
    "unani": {
        "name": "Unani",
        "entry_url": "https://www.tkdl.res.in/tkdl/langdefault/Unani/KeywordHelp/KeywordDemo/keyword.asp",
        "output_dir": os.path.join(BASE_DIR, "unani")
    },
    "siddha": {
        "name": "Siddha",
        "entry_url": "https://www.tkdl.res.in/tkdl/langdefault/Siddha/KeywordHelp/KeywordDemo/keyword.asp",
        "output_dir": os.path.join(BASE_DIR, "siddha")
    },
    "sowa_rigpa": {
        "name": "Sowa Rigpa",
        "entry_url": "https://www.tkdl.res.in/tkdl/langdefault/Sowarigpa/KeywordHelp/KeywordDemo/keyword.asp",
        "output_dir": os.path.join(BASE_DIR, "sowa_rigpa")
    }
}

DEFAULT_COLUMNS_BY_CAT = {
    "plant_name": ["scientific_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "plant_part_product": ["english_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "animal_name": ["scientific_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "animal_part_product": ["english_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "minerals": ["scientific_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "devices": ["english_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "products_processes": ["english_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "diseases": ["english_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "drug_properties": ["english_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "administration": ["english_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"],
    "others": ["scientific_name", "ayurveda_name", "unani_name", "siddha_name", "common_name"]
}

def sanitize_filename(text):
    text = text.lower().strip()
    text = text.replace("&", "and").replace("/", "_").replace(" ", "_")
    clean = "".join(c for c in text if c.isalnum() or c in ("_", "-"))
    return clean

def fetch_url(url):
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def discover_frames_recursive(url, depth=0, max_depth=5, visited=None):
    if visited is None:
        visited = set()
    if url in visited or depth > max_depth:
        return url, None, []
    visited.add(url)

    try:
        html = fetch_url(url)
    except Exception as e:
        return url, None, [f"Error fetching {url}: {str(e)}"]

    soup = BeautifulSoup(html, 'html.parser')
    frames = soup.find_all(['iframe', 'frame'])
    
    # Check if there are child frames to recurse into first
    best_url = None
    best_tables = None
    max_row_count = 0
    errors = []

    for frame in frames:
        src = frame.get('src')
        if src and not src.startswith('javascript:'):
            frame_url = urljoin(url, src)
            target_url, target_tables, frame_errs = discover_frames_recursive(frame_url, depth+1, max_depth, visited)
            errors.extend(frame_errs)
            if target_tables:
                total_rows = sum(len(t.find_all('tr')) for t in target_tables)
                if total_rows > max_row_count:
                    max_row_count = total_rows
                    best_url = target_url
                    best_tables = target_tables

    if best_tables and max_row_count > 10:
        return best_url, best_tables, errors

    # Otherwise check tables in current page
    tables = soup.find_all('table')
    data_tables = []
    for t in tables:
        rows = t.find_all('tr')
        if len(rows) > 1:
            data_tables.append(t)

    current_total = sum(len(t.find_all('tr')) for t in data_tables)
    if current_total > max_row_count:
        return url, data_tables, errors

    if best_tables:
        return best_url, best_tables, errors

    return url, None, errors

def extract_headers_from_frame(url):
    try:
        html = fetch_url(url)
        soup = BeautifulSoup(html, 'html.parser')
        headers = []
        for th in soup.find_all(['th', 'td']):
            text = th.get_text(strip=True)
            if text and text not in headers:
                headers.append(text)
        if len(headers) >= 3:
            return headers
    except Exception:
        pass
    return None

def main():
    print("==================================================")
    print("      TKDL PUBLIC DATA COLLECTOR (IP-SAKTI)")
    print("==================================================")
    start_time = datetime.datetime.now()

    # Ensure output directories exist
    dirs_to_create = [
        os.path.join(BASE_DIR, "raw"),
        os.path.join(BASE_DIR, "clean"),
        os.path.join(BASE_DIR, "metadata"),
        os.path.join(BASE_DIR, "biopiracy"),
        os.path.join(BASE_DIR, "outcomes")
    ]
    for sys_key, sys_cfg in SYSTEMS_CONFIG.items():
        dirs_to_create.append(sys_cfg["output_dir"])
    
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)

    sources_meta = {}
    errors_log = []
    report = {
        "collection_date": start_time.isoformat(),
        "systems": {},
        "total_raw_records": 0,
        "total_unique_records": 0,
        "duplicates_removed": 0,
        "failed_pages": [],
        "restricted_pages": [],
        "notes": []
    }

    all_raw_records = []
    category_summary = {}

    # PHASE 1 - 6: PROCESS ALL SYSTEMS & CATEGORIES
    for sys_key, sys_cfg in SYSTEMS_CONFIG.items():
        sys_name = sys_cfg["name"]
        entry_url = sys_cfg["entry_url"]
        out_dir = sys_cfg["output_dir"]

        print(f"\n[+] System: {sys_name} ({entry_url})")
        report["systems"][sys_key] = {
            "name": sys_name,
            "entry_url": entry_url,
            "categories": {},
            "total_records": 0
        }

        try:
            entry_html = fetch_url(entry_url)
            sources_meta[entry_url] = {
                "system": sys_name,
                "type": "entry_page",
                "retrieved_at": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            err_msg = f"Failed to access entry URL for {sys_name}: {str(e)}"
            print(f"  [!] {err_msg}")
            errors_log.append({"url": entry_url, "system": sys_name, "error": str(e)})
            report["failed_pages"].append(entry_url)
            continue

        soup = BeautifulSoup(entry_html, 'html.parser')
        category_links = soup.find_all('a')
        print(f"  Found {len(category_links)} category links on entry page.")

        for a in category_links:
            cat_display = a.get_text(strip=True)
            href = a.get('href', '')
            if not href or href.startswith('javascript:'):
                continue

            cat_url = urljoin(entry_url, href)
            cat_slug = sanitize_filename(cat_display)

            print(f"  --> Processing Category: '{cat_display}' ({cat_url})")

            # Try discovering nested frame data page
            data_url, data_tables, frame_errs = discover_frames_recursive(cat_url)
            if frame_errs:
                for fe in frame_errs:
                    errors_log.append({"url": cat_url, "system": sys_name, "category": cat_display, "error": fe})

            if not data_tables:
                print(f"      [!] No data tables found for {cat_display}")
                report["failed_pages"].append(cat_url)
                continue

            # Check if intermediate frame (like F-Plant-Name.asp) had header titles
            custom_headers = extract_headers_from_frame(cat_url)

            cat_records = []
            retrieved_at = datetime.datetime.now().isoformat()

            for table in data_tables:
                rows = table.find_all('tr')
                for r_idx, tr in enumerate(rows):
                    cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    if not cols or all(len(c) == 0 for c in cols):
                        continue

                    # Create record dict
                    record_dict = {
                        "system": sys_name,
                        "category": cat_display,
                        "row_index": len(cat_records) + 1,
                        "columns": cols,
                        "source_url": data_url
                    }

                    # Map named fields if columns match default schema or extracted headers
                    if len(cols) == 5:
                        record_dict["scientific_or_english_name"] = cols[0]
                        record_dict["ayurveda_name"] = cols[1]
                        record_dict["unani_name"] = cols[2]
                        record_dict["siddha_name"] = cols[3]
                        record_dict["common_name"] = cols[4]
                    elif len(cols) == 4:
                        record_dict["scientific_or_english_name"] = cols[0]
                        record_dict["ayurveda_name"] = cols[1]
                        record_dict["unani_name"] = cols[2]
                        record_dict["common_name"] = cols[3]

                    cat_records.append(record_dict)

            rec_count = len(cat_records)
            print(f"      [✓] Extracted {rec_count} records from {data_url}")

            report["systems"][sys_key]["categories"][cat_slug] = {
                "display_name": cat_display,
                "url": cat_url,
                "data_url": data_url,
                "record_count": rec_count
            }
            report["systems"][sys_key]["total_records"] += rec_count
            report["total_raw_records"] += rec_count

            category_summary[f"{sys_key}_{cat_slug}"] = rec_count

            # Write Category JSON & CSV to system folder
            cat_json_path = os.path.join(out_dir, f"{cat_slug}.json")
            cat_csv_path = os.path.join(out_dir, f"{cat_slug}.csv")

            json_payload = {
                "source": "TKDL",
                "system": sys_name,
                "category": cat_display,
                "source_url": data_url,
                "parent_url": cat_url,
                "retrieved_at": retrieved_at,
                "total_records": rec_count,
                "records": cat_records
            }

            with open(cat_json_path, 'w', encoding='utf-8') as f:
                json.dump(json_payload, f, ensure_ascii=False, indent=2)

            with open(cat_csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if custom_headers and len(custom_headers) == 5:
                    writer.writerow(custom_headers + ["Source URL"])
                else:
                    writer.writerow(["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Source URL"])
                
                for r in cat_records:
                    row_cols = r.get("columns", [])
                    writer.writerow(row_cols + [r.get("source_url", "")])

            # Write Raw JSON dump
            raw_path = os.path.join(BASE_DIR, "raw", f"{sys_key}_{cat_slug}.json")
            with open(raw_path, 'w', encoding='utf-8') as f:
                json.dump(json_payload, f, ensure_ascii=False, indent=2)

            all_raw_records.extend(cat_records)

    # PHASE 9: CLEANING & DEDUPLICATION WITH PROVENANCE
    print("\n[+] Deduplicating records and building clean dataset...")
    unique_map = {}
    duplicate_count = 0

    for rec in all_raw_records:
        # Create a unique key from primary terms
        cols_key = " | ".join(rec.get("columns", [])).lower()
        if cols_key in unique_map:
            duplicate_count += 1
            # Append provenance
            existing = unique_map[cols_key]
            prov = f"{rec['system']} > {rec['category']}"
            if prov not in existing["provenance"]:
                existing["provenance"].append(prov)
        else:
            rec_copy = dict(rec)
            rec_copy["provenance"] = [f"{rec['system']} > {rec['category']}"]
            unique_map[cols_key] = rec_copy

    clean_records = list(unique_map.values())
    report["total_unique_records"] = len(clean_records)
    report["duplicates_removed"] = duplicate_count

    print(f"    Raw Records: {len(all_raw_records)}")
    print(f"    Unique Records: {len(clean_records)}")
    print(f"    Duplicates Removed: {duplicate_count}")

    # Write clean records dataset
    clean_json_path = os.path.join(BASE_DIR, "clean", "clean_keyword_records.json")
    with open(clean_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "source": "TKDL Representative Public Database",
            "retrieved_at": start_time.isoformat(),
            "total_records": len(clean_records),
            "duplicates_removed": duplicate_count,
            "records": clean_records
        }, f, ensure_ascii=False, indent=2)

    # PHASE 10: PUBLIC FORMULATION SEARCH & RESTRICTED PAGES EVALUATION
    print("\n[+] Inspecting restricted search & outcome pages...")
    restricted_urls = [
        "https://www.tkdl.res.in/tkdl/langdefault/common/Search.asp",
        "https://www.tkdl.res.in/tkdl/langdefault/common/LoginForm.asp",
        "https://www.tkdl.res.in/tkdl/langdefault/common/Outcomes.asp",
        "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayurveda_search.asp",
        "https://www.tkdl.res.in/tkdl/langdefault/common/PriorArt.asp"
    ]

    for r_url in restricted_urls:
        try:
            r_html = fetch_url(r_url)
            r_soup = BeautifulSoup(r_html, 'html.parser')
            title = r_soup.title.string if r_soup.title else ""
            if "Error" in title or "Logout" in r_html or "login" in r_html.lower():
                print(f"  [!] Restricted / Session Required: {r_url} (Title: '{title}')")
                report["restricted_pages"].append({
                    "url": r_url,
                    "reason": "Requires user session / login authentication or returns session error."
                })
        except Exception as e:
            report["restricted_pages"].append({
                "url": r_url,
                "reason": str(e)
            })

    # PHASE 11: PUBLIC BIOPIRACY DATA COLLECTION
    print("\n[+] Collecting Public Bio-Piracy Data...")
    biopiracy_url = "https://www.tkdl.res.in/tkdl/langdefault/common/Biopiracy.asp"
    biopiracy_records = []

    try:
        bio_html = fetch_url(biopiracy_url)
        bio_soup = BeautifulSoup(bio_html, 'html.parser')
        bio_tables = bio_soup.find_all('table')
        
        current_title = "General Bio-piracy Overview"
        for t in bio_tables:
            text = t.get_text(strip=True)
            if not text:
                continue
            # Header tables are short and contain target names
            if len(text) < 100 and any(kw in text for kw in ["Turmeric", "Neem", "Basmati", "Kava", "Ayahuasca", "Quinoa", "Hoodia", "Phyllanthus", "Piper"]):
                current_title = text
            elif len(text) > 200:
                biopiracy_records.append({
                    "topic": current_title,
                    "description": text,
                    "source_url": biopiracy_url
                })
        
        print(f"    [✓] Collected {len(biopiracy_records)} Bio-piracy topic descriptions.")
    except Exception as e:
        print(f"    [!] Error collecting Bio-piracy page: {e}")
        errors_log.append({"url": biopiracy_url, "error": str(e)})

    # Write Biopiracy CSV and JSON
    bio_json_path = os.path.join(BASE_DIR, "biopiracy", "biopiracy_cases.json")
    bio_csv_path = os.path.join(BASE_DIR, "biopiracy", "biopiracy_cases.csv")

    with open(bio_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "source": "TKDL Bio-Piracy Section",
            "source_url": biopiracy_url,
            "retrieved_at": datetime.datetime.now().isoformat(),
            "records": biopiracy_records
        }, f, ensure_ascii=False, indent=2)

    with open(bio_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Topic", "Description", "Source URL"])
        for b in biopiracy_records:
            writer.writerow([b["topic"], b["description"], b["source_url"]])

    # PHASE 14: SANITY CHECK ON AYURVEDA PLANT NAME
    ayurveda_plant_count = report["systems"].get("ayurveda", {}).get("categories", {}).get("plant_name", {}).get("record_count", 0)
    sanity_check_passed = (ayurveda_plant_count == 286)
    print(f"\n[+] Sanity Check (Ayurveda Plant Name == 286 rows): {ayurveda_plant_count} rows -> {'PASSED [✓]' if sanity_check_passed else 'FAILED [X]'}")

    report["notes"].append(f"Ayurveda Plant Name benchmark check (target ~286): Extracted {ayurveda_plant_count} rows. Match: {sanity_check_passed}.")
    report["notes"].append("Public representative formulation search requires active login session/authentication and was safely skipped per access boundaries.")

    # PHASE 13: SAVE METADATA & REPORT
    with open(os.path.join(BASE_DIR, "metadata", "sources.json"), 'w', encoding='utf-8') as f:
        json.dump(sources_meta, f, ensure_ascii=False, indent=2)

    with open(os.path.join(BASE_DIR, "metadata", "errors.json"), 'w', encoding='utf-8') as f:
        json.dump(errors_log, f, ensure_ascii=False, indent=2)

    with open(os.path.join(BASE_DIR, "metadata", "collection_report.json"), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"\n[✓] Collection finished in {duration:.2f} seconds.")
    print(f"    Report saved to: {os.path.join(BASE_DIR, 'metadata', 'collection_report.json')}\n")

if __name__ == "__main__":
    main()
