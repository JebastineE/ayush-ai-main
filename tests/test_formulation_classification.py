import unittest
import sys
import os

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
sys.path.insert(0, project_dir)

from app.services.rules_engine import _classify_by_answers, classify_formulation
from app.schemas.payloads import FormulationRequest


class TestFormulationClassification(unittest.TestCase):

    def test_01_classical_ayurvedic_formulation(self):
        """1. Classical Ayurvedic formulation -> Classical Ayurvedic Medicine"""
        res = _classify_by_answers(
            from_first_schedule=True,
            intended_use="internal oral formulation for fever and digestive disorders",
            is_novel=False,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "Classical Ayurvedic Medicine")
        self.assertIn("Section 3(a)", res.statutory_provision)

    def test_02_classical_hair_oil(self):
        """2. Classical hair oil from First-Schedule text -> Classical Ayurvedic Medicine (NOT Cosmetic)"""
        res = _classify_by_answers(
            from_first_schedule=True,
            intended_use="classical Ayurvedic hair oil for hair growth, scalp nourishment, and hair fall prevention",
            is_novel=False,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "Classical Ayurvedic Medicine")

    def test_03_classical_topical_formulation(self):
        """3. Classical topical formulation (e.g. Jatyadi Taila/Lepa) -> Classical Ayurvedic Medicine"""
        res = _classify_by_answers(
            from_first_schedule=True,
            intended_use="topical skin application for wound healing and skin lesions",
            is_novel=False,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "Classical Ayurvedic Medicine")

    def test_04_proprietary_medicine(self):
        """4. Proprietary Ayurvedic medicine -> Proprietary Ayurvedic Medicine"""
        res = _classify_by_answers(
            from_first_schedule=False,
            intended_use="proprietary medicine for cough and bronchial relief",
            is_novel=False,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "Proprietary Ayurvedic Medicine")

    def test_05_new_non_classical_drug(self):
        """5. New / non-classical drug -> New / Non-Classical Ayurvedic Drug"""
        res = _classify_by_answers(
            from_first_schedule=False,
            intended_use="novel herbal composition for blood glucose control",
            is_novel=True,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "New / Non-Classical Ayurvedic Drug")

    def test_06_phytopharmaceutical(self):
        """6. Phytopharmaceutical -> Phytopharmaceutical Drug"""
        res = _classify_by_answers(
            from_first_schedule=False,
            intended_use="standardized plant extract purified active fraction for therapeutic use",
            is_novel=False,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "Phytopharmaceutical Drug")

    def test_07_ayurveda_aahar(self):
        """7. Ayurveda-Aahar -> Ayurveda-Aahar / Nutraceutical"""
        res = _classify_by_answers(
            from_first_schedule=False,
            intended_use="dietary food supplement for immunity boost",
            is_novel=False,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "Ayurveda-Aahar / Nutraceutical")

    def test_08_cosmetic(self):
        """8. Cosmetic formulation -> Cosmetic"""
        res = _classify_by_answers(
            from_first_schedule=False,
            intended_use="cosmetic hair oil for hair styling and moisturizing",
            is_novel=False,
            resource_source="cultivated"
        )
        self.assertEqual(res.classification, "Cosmetic")

    def test_09_legacy_classify_endpoint_first_schedule_text(self):
        """9. Legacy classify endpoint with explicit First Schedule text reference"""
        req = FormulationRequest(
            ingredients=["Bhringraj", "Amla", "Sesame Oil"],
            source_text="Sahasrayogam, Taila Prakarana, Verse 45",
            intended_use="hair oil for scalp application"
        )
        res = classify_formulation(req)
        self.assertEqual(res.classification, "Classical Ayurvedic Medicine")

    def test_10_legacy_classify_endpoint_non_classical_hair_oil(self):
        """10. Legacy classify endpoint with non-classical hair oil"""
        req = FormulationRequest(
            ingredients=["Argan Oil", "Coconut Oil", "Fragrance"],
            source_text=None,
            intended_use="hair oil for shine and smoothing"
        )
        res = classify_formulation(req)
        self.assertEqual(res.classification, "Cosmetic")


if __name__ == "__main__":
    unittest.main()
