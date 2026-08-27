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

url = "https://www.tkdl.res.in/tkdl/langdefault/common/home.asp"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    
    form = soup.find('form', {'name': 'frmIndex'})
    if form:
        print("Found frmIndex form:")
        for inp in form.find_all(['input', 'select', 'button']):
            print(f"  Input: name='{inp.get('name')}' | type='{inp.get('type')}' | value='{inp.get('value')}' | id='{inp.get('id')}'")
    else:
        print("frmIndex form not found.")
        
    print("\nAll input tags on page:")
    for inp in soup.find_all('input'):
        print(f"  Input: name='{inp.get('name')}' | type='{inp.get('type')}' | value='{inp.get('value')}' | id='{inp.get('id')}'")
