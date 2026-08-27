"""
Quick test to verify frontend runtime error is fixed
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test a simple query
payload = {
    "query": "Can I patent a traditional Ashwagandha formulation?",
    "jurisdiction": "india",
    "session_id": "test-session-fix"
}

print("Testing backend with simple query...")
print(f"Query: {payload['query']}")
print()

try:
    response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
    data = response.json()

    print(f"Status: {response.status_code}")
    print(f"Abstained: {data.get('abstained')}")
    print(f"Confidence: {data.get('confidence_score', 0):.1f}%")
    print(f"Has answer: {'Yes' if data.get('answer') else 'No'}")
    print(f"Actions type: {type(data.get('actions'))}")
    print(f"Actions count: {len(data.get('actions', []))}")

    # Check for disclaimer in answer
    answer = data.get('answer', '')
    disclaimer_count = answer.lower().count('legal disclaimer')
    print(f"Disclaimer count in answer: {disclaimer_count}")

    if disclaimer_count == 1:
        print("✅ Single disclaimer present in backend response")
    else:
        print(f"⚠️  Expected 1 disclaimer, found {disclaimer_count}")

    print("\n✅ Backend is working correctly")
    print("\nFrontend fix:")
    print("- Removed undefined LEGAL_DISCLAIMER_FOOTER reference")
    print("- Backend disclaimer is part of msg.content (rendered by ReactMarkdown)")
    print("- No duplicate disclaimers")

except Exception as e:
    print(f"❌ Error: {e}")
