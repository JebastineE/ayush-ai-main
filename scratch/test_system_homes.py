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

urls = [
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayu_Home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Unani/Una_Home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Siddha/Sid_Home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Sowarigpa/Sowarigpa_Home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/SimpleSearchSlide.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/AdvanceSearchSlide.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/TKRC.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Global_Search.asp"
]

for url in urls:
    print(f"\n==================================================")
    print(f"URL: {url}")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            print(f"  Status: {resp.status} | Title: '{soup.title.string if soup.title else ''}' | Len: {len(html)}")
            iframes = soup.find_all(['iframe', 'frame'])
            forms = soup.find_all('form')
            tables = soup.find_all('table')
            print(f"  Iframes: {len(iframes)}, Forms: {len(forms)}, Tables: {len(tables)}")
            for f in iframes:
                print(f"    Frame src: {f.get('src')}")
            for form in forms:
                print(f"    Form action: {form.get('action')}")
                for inp in form.find_all(['input', 'select']):
                    print(f"      Input: name='{inp.get('name')}' type='{inp.get('type')}' value='{inp.get('value')}'")
    except Exception as e:
        print(f"  Error: {e}")
