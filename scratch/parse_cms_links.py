import ssl
import urllib.request
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

urls = [
    ("fssai", "https://www.fssai.gov.in/upload/notifications/2022/03/6244439c636ffGazette_Notification_Health_Supplements_30_03_2022.pdf"),
    ("nba", "https://nbaindia.org/uploaded/pdf/Form1.pdf")
]

for name, url in urls:
    print(f"=== {name} ===")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            print("Title:", soup.title.string if soup.title else "No title")
            links = soup.find_all('a')
            print(f"Found {len(links)} links:")
            for a in links[:10]:
                print(" ", a.get('href'), "|", a.text.strip()[:40])
    except Exception as e:
        print("Error:", e)
