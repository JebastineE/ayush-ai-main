import ssl
import urllib.request
import urllib.parse
import http.cookiejar
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
except Exception:
    pass

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), urllib.request.HTTPCookieProcessor(cj))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# 1. Visit homepage to obtain session cookie
home_url = "https://www.tkdl.res.in/tkdl/langdefault/common/Home.asp?GL=Eng"
req1 = urllib.request.Request(home_url, headers=headers)
with opener.open(req1) as resp:
    print("Home status:", resp.status)
    print("Cookies after home:", [c.name + "=" + c.value for c in cj])

# 2. Try POST search on Home.asp
search_data = urllib.parse.urlencode({
    "SearchString": "Abrus precatorius",
    "txtSearch": "Abrus precatorius",
    "sterm": "Abrus precatorius"
}).encode('utf-8')

req2 = urllib.request.Request(home_url, data=search_data, headers=headers)
with opener.open(req2) as resp:
    html2 = resp.read().decode('utf-8', errors='ignore')
    soup2 = BeautifulSoup(html2, 'html.parser')
    print("Home search post status:", resp.status, "Title:", soup2.title.string if soup2.title else "")
    if "Abrus" in html2 or "RS/" in html2:
        print("  Found search results in Home.asp POST!")
    else:
        print("  No search result content in Home.asp POST.")

# 3. Test other candidate search URLs with active session
urls_to_test = [
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search.asp?Search=Abrus+precatorius",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search_res.asp?Search=Abrus+precatorius",
    "https://www.tkdl.res.in/tkdl/langdefault/common/Search_Result.asp?Search=Abrus+precatorius",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Ayurveda_search.asp?Search=Abrus+precatorius",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Search.asp?Search=Abrus+precatorius",
    "https://www.tkdl.res.in/tkdl/langdefault/Ayurveda/Utility/KeywordDemo/Search.asp?Search=Abrus+precatorius"
]

for url in urls_to_test:
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener.open(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else ""
            print(f"URL: {url} -> Title: '{title}' (Len: {len(html)})")
            if "Abrus" in html or "RS/" in html:
                print(f"  *** MATCH FOUND in {url}! ***")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
