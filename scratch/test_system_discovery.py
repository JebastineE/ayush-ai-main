import ssl
import urllib.request
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

base_urls = [
    "https://www.tkdl.res.in/",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/KeywordHelp/KeywordDemo/keyword.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Unani/KeywordHelp/KeywordDemo/keyword.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Siddha/KeywordHelp/KeywordDemo/keyword.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/SowaRigpa/KeywordHelp/KeywordDemo/keyword.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Sowa_Rigpa/KeywordHelp/KeywordDemo/keyword.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Sowarigpa/KeywordHelp/KeywordDemo/keyword.asp"
]

for url in base_urls:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            print(f"URL: {url} -> Status: {resp.status}")
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a')
            print(f"  Found {len(links)} links")
            for a in links[:10]:
                href = a.get('href', '')
                text = a.get_text(strip=True)
                if href:
                    print(f"    '{text}' -> {href}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
