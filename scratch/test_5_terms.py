import ssl
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

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

terms = [
    "Abrus precatorius",
    "Acacia catechu",
    "Curcuma longa",
    "Withania somnifera",
    "Zingiber officinale"
]

search_urls = [
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayurveda_search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Global_Search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayu_Home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Unani/Una_Home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Siddha/Sid_Home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Sowarigpa/Sowarigpa_Home.asp"
]

results_summary = []

for term in terms:
    print(f"\n==================================================")
    print(f"Testing Search Term: '{term}'")
    term_res = {"term": term, "accessible": False, "captcha": False, "auth_required": True, "records_found": 0, "urls_tried": []}
    
    for s_url in search_urls:
        query_url = f"{s_url}?Search={urllib.parse.quote(term)}"
        term_res["urls_tried"].append(query_url)
        req = urllib.request.Request(query_url, headers=headers)
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string if soup.title else ""
                
                # Check for session error / login / captcha
                if "Error" in title or "Session Timeout" in html or "Logout" in html:
                    print(f"  Url: {query_url} -> Session / Login Restricted (Title: '{title}')")
                elif "captcha" in html.lower():
                    term_res["captcha"] = True
                    print(f"  Url: {query_url} -> CAPTCHA Detected")
                else:
                    # Check if formulations or tables with records exist
                    tables = soup.find_all('table')
                    print(f"  Url: {query_url} -> Title: '{title}', Tables: {len(tables)}, Len: {len(html)}")
                    if "RS/" in html or "Formulation" in html:
                        term_res["accessible"] = True
                        term_res["auth_required"] = False
                        print(f"    *** FORMULATION FOUND in {query_url}! ***")
        except Exception as e:
            print(f"  Url: {query_url} -> Exception: {e}")
            
    results_summary.append(term_res)

print("\n==================================================")
print("SUMMARY OF 5-TERM TEST:")
for r in results_summary:
    print(f"Term: '{r['term']}' | Accessible: {r['accessible']} | Auth Required: {r['auth_required']} | CAPTCHA: {r['captcha']}")
