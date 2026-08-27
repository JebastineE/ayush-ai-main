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

base_url = "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/KeywordHelp/KeywordDemo/keyword.asp"

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as resp:
        return resp.read().decode('utf-8', errors='ignore')

html = fetch(base_url)
soup = BeautifulSoup(html, 'html.parser')

links = soup.find_all('a')
print(f"Total category links in Ayurveda: {len(links)}")

for a in links:
    text = a.get_text(strip=True)
    href = a.get('href', '')
    cat_url = urljoin(base_url, href)
    print(f"\n--- Category: '{text}' ({cat_url}) ---")
    try:
        cat_html = fetch(cat_url)
        cat_soup = BeautifulSoup(cat_html, 'html.parser')
        
        # Check frames/iframes
        iframes = cat_soup.find_all(['iframe', 'frame'])
        print(f"  Iframes found: {[f.get('src') for f in iframes]}")
        
        # Check anchors (A-Z or sublinks)
        a_tags = cat_soup.find_all('a')
        print(f"  Anchors found: {len(a_tags)}")
        
        # Follow frame src if present
        for iframe in iframes:
            src = iframe.get('src')
            if src:
                data_url = urljoin(cat_url, src)
                print(f"  Fetching frame src: {data_url}")
                data_html = fetch(data_url)
                data_soup = BeautifulSoup(data_html, 'html.parser')
                tables = data_soup.find_all('table')
                print(f"    Tables found in frame: {len(tables)}")
                for t_idx, t in enumerate(tables):
                    rows = t.find_all('tr')
                    print(f"    Table {t_idx} has {len(rows)} rows")
                    if rows:
                        headers_text = [td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])]
                        print(f"    Table {t_idx} row 0: {headers_text[:5]}")
    except Exception as e:
        print(f"  Error: {e}")
