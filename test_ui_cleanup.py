"""
Test UI Cleanup Changes
========================
Verifies:
1. No Ministry footer in response
2. Single clean disclaimer
3. Actions returns list
"""
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

print("="*80)
print("UI CLEANUP TEST")
print("="*80)
print()

# Test query
payload = {
    "query": "Can traditional knowledge about medicinal plants be patented?",
    "jurisdiction": "india",
    "session_id": str(uuid4())
}

print(f"Query: {payload['query']}")
print()

try:
    response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=120)
    data = response.json()

    answer = data.get('answer', '')

    print("VERIFICATION RESULTS:")
    print("-" * 80)

    # Check 1: No Ministry footer in answer
    has_ministry_footer = "Ministry of Ayush | All India Institute of Ayurveda" in answer
    print(f"1. Ministry footer removed: {'YES' if not has_ministry_footer else 'NO - STILL PRESENT'}")

    # Check 2: Single disclaimer
    disclaimer_count = answer.lower().count('legal disclaimer')
    print(f"2. Disclaimer count: {disclaimer_count} ({'PASS' if disclaimer_count == 1 else 'FAIL'})")

    # Check 3: Actions is list
    actions = data.get('actions')
    actions_is_list = isinstance(actions, list)
    print(f"3. Actions is list: {'YES' if actions_is_list else 'NO'}")

    # Check 4: Response details
    print(f"4. Confidence: {data.get('confidence_score', 0):.1f}% ({data.get('confidence_band', 'N/A')})")
    print(f"5. Citations: {len(data.get('citations', []))}")
    print(f"6. Abstained: {data.get('abstained', False)}")

    print()
    print("ANSWER PREVIEW (first 400 chars):")
    print("-" * 80)
    print(answer[:400])
    if len(answer) > 400:
        print("...")

    print()
    print("DISCLAIMER SECTION:")
    print("-" * 80)
    # Extract disclaimer section
    if "---" in answer:
        parts = answer.split("---")
        if len(parts) >= 2:
            disclaimer_section = parts[-1].strip()
            print(disclaimer_section[:300])

    print()
    print("="*80)
    if not has_ministry_footer and disclaimer_count == 1 and actions_is_list:
        print("SUCCESS: All UI cleanup checks passed!")
    else:
        print("ATTENTION: Some checks did not pass")
    print("="*80)

except Exception as e:
    print(f"ERROR: {e}")
