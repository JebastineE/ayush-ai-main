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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

urls_to_inspect = [
    "https://www.tkdl.res.in/",
    "https://www.tkdl.res.in/tkdl/langdefault/common/home.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayurveda_search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search_res.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search_Result.asp",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/KeywordHelp/KeywordDemo/keyword.asp"
]

def fetch_and_inspect(url):
    print(f"\n==================================================")
    print(f"URL: {url}")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            status = resp.status
            cookies = resp.headers.get_all('Set-Cookie')
            print(f"Status: {status} | Cookies: {cookies}")
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            print(f"Title: {soup.title.string if soup.title else 'No Title'}")
            
            forms = soup.find_all('form')
            print(f"Forms found: {len(forms)}")
            for idx, form in enumerate(forms):
                print(f"  Form {idx}: action='{form.get('action')}' | method='{form.get('method')}' | name='{form.get('name')}'")
                for inp in form.find_all(['input', 'select', 'textarea']):
                    print(f"    Input: name='{inp.get('name')}' | type='{inp.get('type')}' | value='{inp.get('value')}'")
            
            # Check links that mention search
            search_links = [a for a in soup.find_all('a') if 'search' in (a.get('href','') + a.get('onclick','')).lower()]
            if search_links:
                print(f"Search links ({len(search_links)}):")
                for a in search_links[:10]:
                    print(f"  '{a.get_text(strip=True)}' -> href='{a.get('href')}' | onclick='{a.get('onclick')}'")
    except Exception as e:
        print(f"Error: {e}")

for u in urls_to_inspect:
    fetch_and_inspect(u)
