"""
Quick test for out-of-domain query only
"""
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

payload = {
    "query": "What is the capital of Mars?",
    "jurisdiction": "india",
    "session_id": str(uuid4())
}

print("\n" + "="*80)
print("TEST: Out-of-Domain Query - 'What is the capital of Mars?'")
print("="*80)
print("Expected: Should ABSTAIN via Semantic Gate")
print()

response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
data = response.json()

abstained = data.get('abstained', False)
conf_score = data.get('confidence_score', 0)
conf_band = data.get('confidence_band', 'N/A')

print(f"Confidence: {conf_score:.1f}% ({conf_band})")
print(f"Abstained: {abstained}")
print(f"Citations: {len(data.get('citations', []))}")
print()

if abstained and conf_band == "OUT_OF_DOMAIN":
    print("✅ SUCCESS: Query rejected by semantic gate!")
elif abstained:
    print("⚠️  PARTIAL: Abstained but not via semantic gate")
else:
    print("❌ FAIL: Should have abstained")

print("\nAnswer preview:")
print(data.get('answer', '')[:400])
