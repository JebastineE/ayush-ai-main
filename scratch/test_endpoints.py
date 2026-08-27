import json
import urllib.request

def test_endpoint(url, data=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8") if data else None,
        headers={"Content-Type": "application/json"} if data else {}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            print(f"SUCCESS {url}: status={resp.status}")
            print("Response:", body[:200])
            return True
    except Exception as e:
        print(f"FAILED {url}: {e}")
        return False

print("--- TESTING BACKEND ENDPOINTS ---")
test_endpoint("http://127.0.0.1:8000/api/health")
test_endpoint("http://127.0.0.1:8000/api/v1/abs-check", {"entity_type": "Indian", "resource_source": "Cultivated"})
test_endpoint("http://127.0.0.1:8000/api/v1/tkdl-scan", {"claim_text": "Topical therapeutic formulation comprising 15% Curcuma longa extract for accelerating dermal wound repair in human subjects."})
test_endpoint("http://127.0.0.1:8000/api/v1/classify/wizard", {"current_step": 1, "answers": {}})
test_endpoint("http://127.0.0.1:8000/api/v1/chat", {"query": "What IP protections apply to Ayurvedic supplements?", "jurisdiction": "india", "language": "en"})
