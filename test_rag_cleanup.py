"""
Test script for RAG-only legal assistant after triage cleanup
"""
import requests
import json
from uuid import uuid4
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

def test_query(query, jurisdiction="india", session_id=None):
    """Send a query to the chat endpoint"""
    payload = {
        "query": query,
        "jurisdiction": jurisdiction,
        "session_id": session_id or str(uuid4())
    }

    response = requests.post(f"{BASE_URL}/chat", json=payload)
    data = response.json()

    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")
    print(f"Confidence: {data.get('confidence_score', 0):.1f}% ({data.get('confidence_band', 'N/A')})")
    print(f"Abstained: {data.get('abstained', False)}")
    print(f"Citations: {len(data.get('citations', []))}")
    print(f"\nANSWER:")
    answer = data.get('answer', '')
    # Print first 500 chars
    print(answer[:500] + ("..." if len(answer) > 500 else ""))
    print(f"\nCITATIONS:")
    for i, cit in enumerate(data.get('citations', [])[:3], 1):
        print(f"  {i}. {cit['source']} (p. {cit['page']})")

    return data

def main():
    print("\n" + "="*80)
    print("IP-SAKTI SAHAYAK - RAG-ONLY LEGAL ASSISTANT TESTS")
    print("="*80)

    # Test 1: Section 3(p) query
    print("\n\nTEST 1: Section 3(p) - Traditional Knowledge Patentability")
    test_query("Can traditional knowledge about a medicinal plant be patented in India?")

    # Test 2: Three-turn conversation
    print("\n\nTEST 2: Three-Turn Conversation (Context Maintenance)")
    session_id = str(uuid4())
    test_query("Can I patent an Ashwagandha formulation?", session_id=session_id)
    test_query("What if I use a novel extraction method?", session_id=session_id)
    test_query("What section of the Patents Act applies?", session_id=session_id)

    # Test 3: TKDL medicinal plant info
    print("\n\nTEST 3: TKDL Medicinal Plant Information")
    test_query("What medicinal plant information is available for Withania somnifera?")

    # Test 4: TKDL CSV record retrieval
    print("\n\nTEST 4: TKDL CSV Record - Synonyms/Local Names")
    test_query("List the synonyms and local names for Acorus calamus Linn.")

    # Test 5: Mixed retrieval (PDF + TK)
    print("\n\nTEST 5: Mixed Retrieval - Traditional Ashwagandha Formulation")
    test_query("Can a traditional Ashwagandha formulation be patented?")

    # Test 6: Out-of-corpus abstention
    print("\n\nTEST 6: Out-of-Corpus Query (Should Abstain)")
    test_query("What is the capital of Mars?")

    print("\n\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()
