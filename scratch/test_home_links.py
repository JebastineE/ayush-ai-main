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

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as resp:
        return resp.read().decode('utf-8', errors='ignore')

home_html = fetch("https://www.tkdl.res.in/tkdl/langdefault/common/home.asp")
soup = BeautifulSoup(home_html, 'html.parser')
for a in soup.find_all('a'):
    print(f"Link text: '{a.get_text(strip=True)}' | href: '{a.get('href')}' | onclick: '{a.get('onclick')}'")

for script in soup.find_all('script'):
    if script.string:
        print("--- SCRIPT ---")
        print(script.string[:500])
