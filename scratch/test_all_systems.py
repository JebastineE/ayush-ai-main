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

systems = {
    "Ayurveda": "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/KeywordHelp/KeywordDemo/keyword.asp",
    "Unani": "https://www.tkdl.res.in/tkdl/langdefault/Unani/KeywordHelp/KeywordDemo/keyword.asp",
    "Siddha": "https://www.tkdl.res.in/tkdl/langdefault/Siddha/KeywordHelp/KeywordDemo/keyword.asp",
    "Sowa_Rigpa": "https://www.tkdl.res.in/tkdl/langdefault/Sowarigpa/KeywordHelp/KeywordDemo/keyword.asp"
}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as resp:
        return resp.read().decode('utf-8', errors='ignore')

for sys_name, base_url in systems.items():
    print(f"\n==================== SYSTEM: {sys_name} ====================")
    try:
        html = fetch(base_url)
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        print(f"Total categories found: {len(links)}")
        for a in links:
            text = a.get_text(strip=True)
            href = a.get('href', '')
            cat_url = urljoin(base_url, href)
            print(f"  Category '{text}': {cat_url}")
            # Try fetching F- page and data page
            cat_html = fetch(cat_url)
            cat_soup = BeautifulSoup(cat_html, 'html.parser')
            iframes = cat_soup.find_all(['iframe', 'frame'])
            for iframe in iframes:
                src = iframe.get('src')
                if src:
                    data_url = urljoin(cat_url, src)
                    data_html = fetch(data_url)
                    data_soup = BeautifulSoup(data_html, 'html.parser')
                    tables = data_soup.find_all('table')
                    total_rows = sum(len(t.find_all('tr')) for t in tables)
                    print(f"    -> Data page: {data_url} (Rows: {total_rows})")
    except Exception as e:
        print(f"Error fetching system {sys_name}: {e}")
