import ssl
import urllib.request
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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

def scan_url(url, depth=0, max_depth=2, visited=None):
    if visited is None:
        visited = set()
    if url in visited or depth > max_depth:
        return
    visited.add(url)
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all asp references in href, src, action, or scripts
            asp_matches = re.findall(r'[\w\-\.\/]+\.asp(?:\?[\w\=\&\%]*)?', html, re.IGNORECASE)
            print(f"URL: {url} -> found {len(asp_matches)} .asp references:")
            for m in set(asp_matches):
                full_m = urljoin(url, m)
                print(f"  {m} -> {full_m}")
                if depth < max_depth and "logout" not in m.lower() and "session" not in m.lower():
                    scan_url(full_m, depth+1, max_depth, visited)
    except Exception as e:
        print(f"Error scanning {url}: {e}")

scan_url("https://www.tkdl.res.in/tkdl/langdefault/common/home.asp")
