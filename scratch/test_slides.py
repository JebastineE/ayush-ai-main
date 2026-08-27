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

urls = [
    "https://www.tkdl.res.in/tkdl/langdefault/common/SimpleSearchSlide.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/AdvanceSearchSlide.asp"
]

for u in urls:
    print(f"\nURL: {u}")
    req = urllib.request.Request(u, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(strip=True)
        print("Text preview:", text[:500])
        for a in soup.find_all('a'):
            print(f"  Link: '{a.get_text(strip=True)}' -> {a.get('href')}")
