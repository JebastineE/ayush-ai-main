"""
Complete Implementation Test - Legal Wording + Actionable Resources
===================================================================
Tests both tasks:
1. Improved legal answer wording (cautious, evidence-grounded)
2. Complete actionable resources feature
"""
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

def test_query(query, session_id, test_name):
    """Test a query and analyze results"""
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
        actions = data.get('actions', [])

        print(f"Status: {'Abstained' if abstained else 'Answered'}")
        print(f"Confidence: {conf_score:.1f}% ({conf_band})")
        print(f"Citations: {citations_count}")
        print(f"Actions: {len(actions)} items")

        if actions:
            print("  Action IDs:", [a.get('id') for a in actions])
            print("  Action Labels:", [a.get('label') for a in actions])

        print()

        # Check legal wording
        print("LEGAL WORDING ANALYSIS:")
        absolute_claims = []
        cautious_phrases = []

        if "can be patented" in answer.lower() or "can be patentable" in answer.lower():
            absolute_claims.append("Uses 'can be patented/patentable'")
        if "may be patented" in answer.lower() or "may be patentable" in answer.lower():
            cautious_phrases.append("Uses 'may be patented/patentable'")

        if "applicants must" in answer.lower() or "must search" in answer.lower():
            absolute_claims.append("Uses absolute 'must' language")
        if "may need" in answer.lower() or "may require" in answer.lower() or "can help" in answer.lower():
            cautious_phrases.append("Uses cautious language")

        if "is patentable" in answer.lower():
            absolute_claims.append("Uses absolute 'is patentable'")
        if "where section" in answer.lower() or "if the" in answer.lower():
            cautious_phrases.append("Uses conditional phrasing")

        if absolute_claims:
            print(f"  Potential absolute claims found: {len(absolute_claims)}")
            for claim in absolute_claims[:3]:
                print(f"    - {claim}")
        else:
            print("  No obvious absolute claims found")

        if cautious_phrases:
            print(f"  Cautious phrases found: {len(cautious_phrases)}")
            for phrase in cautious_phrases[:3]:
                print(f"    - {phrase}")

        print()
        print("ANSWER PREVIEW (first 500 chars):")
        print("-" * 80)
        print(answer[:500])
        if len(answer) > 500:
            print("...")

        return data

    except Exception as e:
        print(f"ERROR: {e}")
        return {}


def main():
    print("\n" + "="*80)
    print("COMPLETE IMPLEMENTATION TEST SUITE")
    print("Legal Wording + Actionable Resources")
    print("="*80)

    # Test 1: Patent query - check legal wording
    session1 = str(uuid4())
    print("\n" + "-"*80)
    print("TASK 1: LEGAL ANSWER WORDING IMPROVEMENTS")
    print("-"*80)

    test_query(
        "Can I patent a novel Ashwagandha formulation?",
        session1,
        "Test 1: Patent Query - Check Cautious Wording"
    )

    # Test 2: Follow-up about extraction method
    test_query(
        "What if I use a novel extraction method?",
        session1,
        "Test 2: Novel Method - Check Conditional Language"
    )

    # Test 3: Legal provisions
    test_query(
        "Which section of the Patents Act applies to this?",
        session1,
        "Test 3: Legal Sections - Check Context Preservation"
    )

    # Test 4: Preparation guidance
    test_query(
        "What should I check before filing?",
        session1,
        "Test 4: Filing Guidance - Check Evidence-Grounded Advice"
    )

    # Test 5: Out-of-domain
    print("\n" + "-"*80)
    print("REGRESSION TEST: OUT-OF-DOMAIN DETECTION")
    print("-"*80)

    session2 = str(uuid4())
    test_query(
        "What is the capital of Mars?",
        session2,
        "Test 5: Out-of-Domain Query - Should Abstain"
    )

    # Test 6: Actions test - patent related
    print("\n" + "-"*80)
    print("TASK 2: ACTIONABLE RESOURCES FEATURE")
    print("-"*80)

    session3 = str(uuid4())
    test_query(
        "How do I search for existing patents on herbal formulations?",
        session3,
        "Test 6: Patent Search Query - Check for patent_search Action"
    )

    # Test 7: TKDL related
    test_query(
        "How can I check if my formulation is traditional knowledge?",
        session3,
        "Test 7: TKDL Query - Check for tkdl_scan Action"
    )

    # Test 8: NBA/regulatory
    test_query(
        "What are the NBA requirements for biological resources?",
        session3,
        "Test 8: NBA Query - Check for nba_resources Action"
    )

    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)

    print("\n\nVERIFICATION SUMMARY:")
    print("-" * 80)
    print("\nTASK 1 - Legal Wording:")
    print("  Check test outputs above for:")
    print("    - Use of 'may be patentable' vs 'can be patented'")
    print("    - Conditional phrases: 'where Section X applies', 'if the claimed invention'")
    print("    - Cautious language: 'may need', 'may require', 'can help'")
    print("    - Avoidance of absolute 'must' statements")
    print()
    print("TASK 2 - Actionable Resources:")
    print("  Check test outputs above for:")
    print("    - Actions returned as list (not null)")
    print("    - Relevant action IDs suggested based on query")
    print("    - patent_search, tkdl_scan, nba_resources available when relevant")
    print()
    print("REGRESSION:")
    print("  - Continuous conversation working (Tests 1-4 same session)")
    print("  - Out-of-domain detection working (Test 5)")
    print("  - Citations still present")
    print("  - Confidence scores displayed")
    print()
    print("NEXT STEPS:")
    print("  1. Open frontend: http://localhost:3000")
    print("  2. Test action buttons in UI:")
    print("     - Search Indian Patents (external link)")
    print("     - Patent Filing Information (external link)")
    print("     - Prepare Patent Checklist (modal)")
    print("     - Open TKDL Scanner (switches tab)")
    print("     - View NBA Resources (external link)")
    print("     - Generate Preparation Draft (modal)")
    print("  3. Verify all modals open correctly")
    print("  4. Verify external links open in new tabs")
    print()


if __name__ == "__main__":
    main()
