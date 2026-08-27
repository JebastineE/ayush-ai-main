import urllib.request
import json
import sys

# Ensure UTF-8 output on Windows console
sys.stdout.reconfigure(encoding='utf-8')

url = "http://127.0.0.1:8000/api/v1/chat"
payload = {
    "query": "Can I patent an Ashwagandha formulation in India?",
    "jurisdiction": "india",
    "language": "en"
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("CHAT_ENDPOINT_STATUS: SUCCESS")
        print("ANSWER_PREVIEW:\n" + data.get("answer", "")[:400])
        print("\nCITATIONS_COUNT:", len(data.get("citations", [])))
        print("PII_REDACTED:", data.get("pii_redacted"))
except Exception as e:
    print("CHAT_ENDPOINT_STATUS: FAILED")
    print("ERROR:", str(e))
