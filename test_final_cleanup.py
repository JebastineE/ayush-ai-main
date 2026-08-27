"""
Final Cleanup & Action Resources Test
======================================
Tests RAG output formatting and action layer fixes.
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
    """Send a query and check response"""
    payload = {
        "query": query,
        "jurisdiction": jurisdiction,
        "session_id": session_id or str(uuid4())
    }

    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Query: {query}\n")

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        data = response.json()

        print(f"Confidence: {data.get('confidence_score', 0):.1f}% ({data.get('confidence_band', 'N/A')})")
        print(f"Abstained: {data.get('abstained', False)}")
        print(f"Citations: {len(data.get('citations', []))}")

        # Check actions
        actions = data.get('actions')
        print(f"\nACTIONS TYPE: {type(actions)}")
        if actions is None:
            print("⚠️  WARNING: actions is NULL")
        elif isinstance(actions, list):
            print(f"✅ SUCCESS: actions is a list with {len(actions)} items")
            for action in actions:
                print(f"  - {action.get('label')} ({action.get('type')})")
        else:
            print(f"❌ ERROR: actions is {type(actions)}")

        # Check answer formatting
        answer = data.get('answer', '')

        # Check for duplicate disclaimers
        disclaimer_count = answer.lower().count('legal disclaimer')
        print(f"\nDISCLAIMER COUNT: {disclaimer_count}")
        if disclaimer_count > 1:
            print("⚠️  WARNING: Multiple disclaimers found")
        elif disclaimer_count == 1:
            print("✅ SUCCESS: Single disclaimer")

        # Check for raw markdown
        has_raw_markdown = ('**' in answer and answer.count('**') > 4) or '###' in answer
        if has_raw_markdown:
            print("⚠️  WARNING: Raw markdown syntax detected")
        else:
            print("✅ SUCCESS: Clean text (markdown will render in frontend)")

        print(f"\nANSWER (first 400 chars):")
        print(answer[:400])
        if len(answer) > 400:
            print("...")

        return data

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {}


def main():
    print("\n" + "="*80)
    print("FINAL CLEANUP & ACTION RESOURCES - COMPREHENSIVE TEST")
    print("="*80)

    # Test 1: Patent query
    test_query(
        "Can I patent a traditional Ashwagandha formulation in India?",
        test_name="TEST 1: Patent Query (check actions, formatting, disclaimer)"
    )

    # Test 2: Follow-up
    session_id = str(uuid4())
    test_query(
        "Can I patent an Ashwagandha formulation?",
        session_id=session_id,
        test_name="TEST 2A: First Query in Conversation"
    )
    test_query(
        "What if I use a novel extraction method instead?",
        session_id=session_id,
        test_name="TEST 2B: Follow-up (context maintained)"
    )
    test_query(
        "Which section of the Patents Act applies to this?",
        session_id=session_id,
        test_name="TEST 2C: Follow-up Question"
    )

    # Test 3: Traditional knowledge
    test_query(
        "Does traditional knowledge about medicinal plants affect patentability?",
        test_name="TEST 3: Traditional Knowledge (should suggest TKDL action)"
    )

    print("\n" + "="*80)
    print("TESTS COMPLETED")
    print("="*80)

    print("\n\n📋 VERIFICATION CHECKLIST:")
    print("✓ Verify actions is a list (not null)")
    print("✓ Verify only ONE disclaimer appears")
    print("✓ Verify clean formatting (markdown will render in frontend)")
    print("✓ Verify patent queries suggest relevant actions")
    print("✓ Verify follow-up context is maintained")
    print("✓ Verify citations are present")


if __name__ == "__main__":
    main()
