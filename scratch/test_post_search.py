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
    'Content-Type': 'application/x-www-form-urlencoded'
}

test_urls = [
    "https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayurveda_search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Utility/KeywordDemo/Plant-Name.asp"
]

post_data = urllib.parse.urlencode({
    "txtSearch": "Abrus precatorius",
    "SearchString": "Abrus precatorius",
    "Search": "Abrus precatorius",
    "sterm": "Abrus precatorius",
    "keyword": "Abrus precatorius"
}).encode('utf-8')

for url in test_urls:
    print(f"\nTesting POST to: {url}")
    req = urllib.request.Request(url, data=post_data, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            print("  Status:", resp.status)
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            print("  Title:", soup.title.string if soup.title else "")
            print("  Tables:", len(soup.find_all('table')))
            print("  Body text preview:", soup.get_text(strip=True)[:200])
    except Exception as e:
        print("  Error:", e)
