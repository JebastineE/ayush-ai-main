import unittest
import asyncio
import sys
import os

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
sys.path.insert(0, project_dir)

from app.services.rag import generate_grounded_response


class TestRAGConfidenceAndAbstention(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_01_in_corpus_high_confidence(self):
        """In-corpus query should yield HIGH/MEDIUM confidence, abstained=False, and non-empty answer"""
        q = "What does Section 3(p) of the Patents Act 1970 state regarding traditional knowledge?"
        res = self.loop.run_until_complete(generate_grounded_response(q, jurisdiction="india"))
        
        self.assertFalse(res["abstained"])
        self.assertIn(res["confidence_band"], ["HIGH", "MEDIUM", "LOW"])
        self.assertGreaterEqual(res["confidence_score"], 40.0)
        self.assertIn("Patents Act", res["answer"])
        self.assertGreater(len(res["citations"]), 0)

    def test_02_out_of_corpus_hard_abstention(self):
        """Out-of-corpus query should trigger hard abstention (abstained=True, band=VERY_LOW, score < 40.0)"""
        q = "What is the best recipe for baking chocolate chip cookies at high altitude?"
        res = self.loop.run_until_complete(generate_grounded_response(q, jurisdiction="india"))
        
        self.assertTrue(res["abstained"])
        self.assertEqual(res["confidence_band"], "VERY_LOW")
        self.assertLess(res["confidence_score"], 40.0)
        self.assertIn("Insufficient Authoritative Legal Evidence", res["answer"])
        self.assertEqual(len(res["citations"]), 0)

    def test_03_out_of_corpus_quantum_computing(self):
        """Unrelated tech query should abstain without calling LLM"""
        q = "How does quantum error correction work using surface codes?"
        res = self.loop.run_until_complete(generate_grounded_response(q, jurisdiction="international"))
        
        self.assertTrue(res["abstained"])
        self.assertEqual(res["confidence_band"], "VERY_LOW")
        self.assertEqual(len(res["citations"]), 0)


if __name__ == "__main__":
    unittest.main()
