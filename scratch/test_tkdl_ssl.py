import ssl
import urllib.request
from bs4 import BeautifulSoup

# Create custom SSL context allowing legacy server connects
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
# Allow legacy renegotiation if supported
try:
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
except Exception as e:
    print("Cipher set note:", e)

url = "https://tkdl.res.in/tkdl/langdefault/Ayurveda/Utility/KeywordDemo/Plant-Name.asp"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        print(f"Success! Found {len(tables)} tables")
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"Table {i}: {len(rows)} rows")
            if len(rows) > 0:
                print("First row sample:", [td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])])
                if len(rows) > 1:
                    print("Second row sample:", [td.get_text(strip=True) for td in rows[1].find_all(['td', 'th'])])
except Exception as e:
    print("Error:", e)
