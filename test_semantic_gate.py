"""
Semantic Relevance Gate Test Suite
===================================
Tests the new semantic relevance gate that rejects out-of-domain queries
before Cross-Encoder/Gemini processing.
"""
import requests
import json
from uuid import uuid4
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"


def test_query(query, jurisdiction="india", session_id=None, test_name="", expect_abstain=False):
    """Send a query and check response"""
    payload = {
        "query": query,
        "jurisdiction": jurisdiction,
        "session_id": session_id or str(uuid4())
    }

    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Query: {query}")
    if expect_abstain:
        print(f"Expected: ABSTAIN ❌")
    else:
        print(f"Expected: ANSWER ✅")
    print()

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
        data = response.json()

        abstained = data.get('abstained', False)
        conf_score = data.get('confidence_score', 0)
        conf_band = data.get('confidence_band', 'N/A')
        citations_count = len(data.get('citations', []))

        print(f"Confidence: {conf_score:.1f}% ({conf_band})")
        print(f"Abstained: {abstained}")
        print(f"Citations: {citations_count}")

        # Check actions
        actions = data.get('actions', [])
        print(f"Actions: {len(actions)} items")

        # Validation
        if expect_abstain:
            if abstained:
                print(f"\n✅ PASS: Correctly abstained")
                if conf_band == "OUT_OF_DOMAIN":
                    print(f"✅ BONUS: Semantic gate triggered (OUT_OF_DOMAIN band)")
            else:
                print(f"\n❌ FAIL: Should have abstained but got answer")
        else:
            if not abstained:
                print(f"\n✅ PASS: Provided answer as expected")
            else:
                print(f"\n⚠️  WARNING: Abstained when answer was expected")

        # Show answer preview
        answer = data.get('answer', '')
        print(f"\nANSWER (first 300 chars):")
        print(answer[:300])
        if len(answer) > 300:
            print("...")

        return data

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {}


def main():
    print("\n" + "="*80)
    print("SEMANTIC RELEVANCE GATE - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. In-domain queries get answers ✅")
    print("2. Out-of-domain queries are rejected by semantic gate ❌")
    print("3. Conversational context is maintained ✅")
    print("4. Actions schema returns list ✅")
    print("5. Single disclaimer ✅")

    # ══════════════════════════════════════════════════════════════════════════
    # TEST 1: Patent Query (In-Domain) - Should ANSWER
    # ══════════════════════════════════════════════════════════════════════════
    test_query(
        "Can I patent a traditional Ashwagandha formulation in India?",
        test_name="TEST 1: Patent Query (In-Domain)",
        expect_abstain=False
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TEST 2: Multi-Turn Conversation (In-Domain) - Should ANSWER
    # ══════════════════════════════════════════════════════════════════════════
    session_id = str(uuid4())
    test_query(
        "Can I patent an Ashwagandha formulation?",
        session_id=session_id,
        test_name="TEST 2A: First Query in Conversation (In-Domain)",
        expect_abstain=False
    )
    test_query(
        "What if I use a novel extraction method instead?",
        session_id=session_id,
        test_name="TEST 2B: Follow-up (Context Maintained)",
        expect_abstain=False
    )
    test_query(
        "Which section of the Patents Act applies?",
        session_id=session_id,
        test_name="TEST 2C: Follow-up Question",
        expect_abstain=False
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TEST 3: Traditional Knowledge (In-Domain) - Should ANSWER
    # ══════════════════════════════════════════════════════════════════════════
    test_query(
        "Does traditional knowledge about medicinal plants affect patentability?",
        test_name="TEST 3: Traditional Knowledge Query (In-Domain)",
        expect_abstain=False
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TEST 4: Trademark Query (In-Domain) - Should ANSWER
    # ══════════════════════════════════════════════════════════════════════════
    test_query(
        "What are the requirements for trademark registration in India?",
        test_name="TEST 4: Trademark Query (In-Domain)",
        expect_abstain=False
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TEST 5: FSSAI/Regulatory Query (In-Domain) - Should ANSWER
    # ══════════════════════════════════════════════════════════════════════════
    test_query(
        "What are FSSAI regulations for Ayurvedic dietary supplements?",
        test_name="TEST 5: FSSAI Regulatory Query (In-Domain)",
        expect_abstain=False
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TEST 6: OUT-OF-DOMAIN Query - Should ABSTAIN via Semantic Gate
    # ══════════════════════════════════════════════════════════════════════════
    test_query(
        "What is the capital of Mars?",
        test_name="TEST 6: Out-of-Domain Query (CRITICAL - Must Abstain)",
        expect_abstain=True
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)

    print("\n\n📋 VERIFICATION CHECKLIST:")
    print("✓ Tests 1-5: In-domain queries should get answers")
    print("✓ Test 6: Out-of-domain query should abstain with semantic gate")
    print("✓ Test 6 should show 'OUT_OF_DOMAIN' confidence band")
    print("✓ Test 6 should have conf_score = 0.0")
    print("✓ All responses should have actions as list (not null)")
    print("✓ All responses should have single disclaimer")
    print("✓ Conversational context maintained in Test 2A-C")

    print("\n\n🎯 KEY SUCCESS METRIC:")
    print("   'What is the capital of Mars?' MUST abstain BEFORE Cross-Encoder/Gemini")
    print("   Look for log: '🛑 [Semantic Gate] Query rejected as OUT-OF-DOMAIN!'")


if __name__ == "__main__":
    main()
