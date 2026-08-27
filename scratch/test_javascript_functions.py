import ssl
import urllib.request
import re
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

url = "https://www.tkdl.res.in/tkdl/langdefault/common/home.asp"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    
    print("=== SCRIPT TAGS IN HOME.ASP ===")
    for idx, s in enumerate(soup.find_all('script')):
        src = s.get('src')
        if src:
            print(f"Script src {idx}: {src}")
            # Fetch external JS
            js_url = urllib.parse.urljoin(url, src)
            try:
                js_req = urllib.request.Request(js_url, headers=headers)
                with urllib.request.urlopen(js_req, context=ctx) as js_resp:
                    js_code = js_resp.read().decode('utf-8', errors='ignore')
                    print(f"  --- External JS ({js_url}) ---")
                    print(js_code[:1000])
            except Exception as e:
                print(f"  Error fetching {js_url}: {e}")
        elif s.string:
            print(f"Script inline {idx}:")
            print(s.string[:1000])
