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

url = "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Search.asp?Search=Abrus+precatorius"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    print("Title:", soup.title.string if soup.title else "")
    print("Total length:", len(html))
    print("Tables:", len(soup.find_all('table')))
    print("Frames/Iframes:", len(soup.find_all(['iframe', 'frame'])))
    for f in soup.find_all(['iframe', 'frame']):
        print("  Frame:", f.get('name'), f.get('src'))
        
    for i, t in enumerate(soup.find_all('table')):
        text = t.get_text(strip=True)
        if len(text) > 50:
            print(f"\n--- Table {i} ({len(text)} chars) ---")
            print(text[:400])
