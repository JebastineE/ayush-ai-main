import ssl
import urllib.request
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

url = "https://www.tkdl.res.in/tkdl/langdefault/common/Biopiracy.asp"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    print("Title:", soup.title.string if soup.title else "")
    tables = soup.find_all('table')
    print("Tables:", len(tables))
    for i, t in enumerate(tables):
        text = t.get_text(strip=True)
        if len(text) > 0:
            print(f"--- Table {i} ({len(text)} chars) ---")
            print(text[:300])
