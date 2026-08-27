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

urls_to_check = [
    "https://www.tkdl.res.in/tkdl/langdefault/common/home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Biopiracy.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Outcomes.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/LoginForm.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayurveda_search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/KeywordHelp/KeywordDemo/Search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Outcome.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/PriorArt.asp",
]

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            print(f"URL: {url} -> Status {resp.status}")
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            print(f"  Title: {soup.title.string if soup.title else 'No Title'}")
            print(f"  Links: {len(soup.find_all('a'))}, Forms: {len(soup.find_all('form'))}, Tables: {len(soup.find_all('table'))}")
            # print sample links/text
            for a in soup.find_all('a')[:5]:
                print(f"    Link: '{a.get_text(strip=True)}' -> {a.get('href')}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")

for url in urls_to_check:
    fetch(url)
