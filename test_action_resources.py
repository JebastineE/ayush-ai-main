"""
Test Actionable Legal Resources Layer
======================================

Tests the new action suggestion system integrated with the RAG pipeline.
"""
import requests
import json
from uuid import uuid4
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"


def test_query(query, jurisdiction="india", session_id=None, test_name=""):
    """Send a query and check for actions"""
    payload = {
        "query": query,
        "jurisdiction": jurisdiction,
        "session_id": session_id or str(uuid4())
    }

    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Query: {query}")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        data = response.json()

        print(f"\nConfidence: {data.get('confidence_score', 0):.1f}% ({data.get('confidence_band', 'N/A')})")
        print(f"Abstained: {data.get('abstained', False)}")
        print(f"Citations: {len(data.get('citations', []))}")

        # Check actions (handle None)
        actions = data.get('actions') or []
        print(f"\n✨ ACTIONS: {len(actions)}")
        for action in actions:
            action_type = action.get('type', 'unknown')
            action_id = action.get('id', 'unknown')
            action_label = action.get('label', 'Unknown')
            action_url = action.get('url', '')

            if action_type == 'external':
                print(f"  🔗 {action_label} → {action_url}")
            else:
                print(f"  📋 {action_label} (internal: {action_id})")

        # Show first 300 chars of answer
        answer = data.get('answer', '')
        print(f"\nANSWER (first 300 chars):")
        print(answer[:300] + ("..." if len(answer) > 300 else ""))

        return data

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {}


def main():
    print("\n" + "="*80)
    print("ACTIONABLE LEGAL RESOURCES - COMPREHENSIVE TEST SUITE")
    print("="*80)

    # Test 1: Patent query → patent actions
    test_query(
        "Can I patent a novel Ashwagandha formulation?",
        test_name="TEST 1: Patent Query (should suggest patent actions)"
    )

    # Test 2: Follow-up conversation (context maintained)
    session_id = str(uuid4())
    test_query(
        "Can I patent an Ashwagandha formulation?",
        session_id=session_id,
        test_name="TEST 2A: Follow-up Conversation - Initial Query"
    )
    test_query(
        "What if I use a novel extraction method?",
        session_id=session_id,
        test_name="TEST 2B: Follow-up Conversation - Context Maintained"
    )

    # Test 3: Traditional knowledge query → TKDL action
    test_query(
        "Does traditional knowledge about medicinal plants affect patentability?",
        test_name="TEST 3: Traditional Knowledge (should suggest TKDL scan)"
    )

    # Test 4: Biological resources query → NBA resources (NO ABS classifier)
    test_query(
        "I want to check requirements related to biological resources.",
        test_name="TEST 4: Biological Resources (should suggest NBA, no ABS classifier)"
    )

    # Test 5: Ayurveda Aahara query → FoSCoS action
    test_query(
        "What are the requirements for Ayurveda Aahara products?",
        test_name="TEST 5: Ayurveda Aahara (should suggest FoSCoS)"
    )

    # Test 6: Preparation draft request
    test_query(
        "Help me prepare a draft for my patent discussion.",
        test_name="TEST 6: Preparation Draft Request"
    )

    # Test 7: Out-of-corpus query → abstention (no actions)
    test_query(
        "What is the capital of Mars?",
        test_name="TEST 7: Out-of-Corpus (should abstain, no actions)"
    )

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)

    print("\n\n📋 VERIFICATION CHECKLIST:")
    print("✓ Verify patent queries suggest: patent_search, patent_checklist, patent_filing")
    print("✓ Verify follow-up maintains conversation context")
    print("✓ Verify traditional knowledge suggests: tkdl_scan")
    print("✓ Verify biological resources suggests: nba_resources (NOT ABS classifier)")
    print("✓ Verify Ayurveda Aahara suggests: foscos")
    print("✓ Verify draft request suggests: preparation_draft")
    print("✓ Verify out-of-corpus query abstains with no actions")
    print("✓ Verify NO ABS Navigator reintroduced")
    print("✓ Verify NO Formulation Classifier reintroduced")
    print("✓ Verify RAG pipeline still intact (confidence scores, citations)")


if __name__ == "__main__":
    main()
