"""
Test No Disclaimer Removal
===========================
Verifies that legal disclaimer has been removed from responses.
"""
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

def test_query(query, session_id, test_name):
    """Test a query and check for disclaimer"""
    payload = {
        "query": query,
        "jurisdiction": "india",
        "session_id": session_id
    }

    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)
    print(f"Query: {query}")
    print()

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=120)
        data = response.json()

        answer = data.get('answer', '')
        abstained = data.get('abstained', False)
        conf_score = data.get('confidence_score', 0)
        conf_band = data.get('confidence_band', 'N/A')
        citations_count = len(data.get('citations', []))

        # Check for disclaimer
        has_disclaimer = 'legal disclaimer' in answer.lower()
        has_separator = '---' in answer and 'legal disclaimer' in answer.lower()
        has_raw_markdown = '**Legal Disclaimer**' in answer

        print(f"Abstained: {abstained}")
        print(f"Confidence: {conf_score:.1f}% ({conf_band})")
        print(f"Citations: {citations_count}")
        print()

        print("DISCLAIMER CHECKS:")
        print(f"  - Contains 'Legal Disclaimer': {'YES - FAIL' if has_disclaimer else 'NO - PASS'}")
        print(f"  - Contains '---' separator: {'YES - FAIL' if has_separator else 'NO - PASS'}")
        print(f"  - Contains '**Legal Disclaimer**': {'YES - FAIL' if has_raw_markdown else 'NO - PASS'}")
        print()

        # Show answer preview
        print(f"ANSWER (first 500 chars):")
        print("-" * 80)
        print(answer[:500])
        if len(answer) > 500:
            print("...")

        # Show last 200 chars to check end of answer
        if len(answer) > 200:
            print()
            print("ANSWER END (last 200 chars):")
            print("-" * 80)
            print(answer[-200:])

        print()

        # Overall result
        if not has_disclaimer and not has_separator and not has_raw_markdown:
            print("SUCCESS: No disclaimer found!")
        else:
            print("ATTENTION: Disclaimer remnants detected")

        return data

    except Exception as e:
        print(f"ERROR: {e}")
        return {}


def main():
    print("\n" + "="*80)
    print("DISCLAIMER REMOVAL TEST SUITE")
    print("="*80)

    # Test 1: Normal patent query
    session1 = str(uuid4())
    test_query(
        "Can I patent a novel Ashwagandha formulation?",
        session1,
        "Test 1: Normal Patent Query"
    )

    # Test 2: Follow-up in same session
    test_query(
        "What if I use a novel extraction method?",
        session1,
        "Test 2: Follow-up Question (Same Session)"
    )

    # Test 3: Another follow-up
    test_query(
        "Which section of the Patents Act applies to this?",
        session1,
        "Test 3: Another Follow-up"
    )

    # Test 4: Out-of-domain query (should abstain)
    session2 = str(uuid4())
    test_query(
        "What is the capital of Mars?",
        session2,
        "Test 4: Out-of-Domain Query (Should Abstain)"
    )

    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)
    print()
    print("SUMMARY:")
    print("  - All 4 test queries executed")
    print("  - Check above for disclaimer presence in each response")
    print("  - SUCCESS if NO disclaimer text found in any response")
    print()


if __name__ == "__main__":
    main()
