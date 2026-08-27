import urllib.request
from bs4 import BeautifulSoup
import json

url = "https://tkdl.res.in/tkdl/langdefault/Ayurveda/Utility/KeywordDemo/Plant-Name.asp"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"Table {i}: {len(rows)} rows")
            if len(rows) > 0:
                print("First row sample:", [td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])])
                if len(rows) > 1:
                    print("Second row sample:", [td.get_text(strip=True) for td in rows[1].find_all(['td', 'th'])])
except Exception as e:
    print("Error:", e)
