import json

# 1. Generate Fake Patent Claims ("The Villains")
patent_claims = [
    {
        "claim_id": "PAT-US-2026-001",
        "applicant": "Global Pharma Inc.",
        "jurisdiction": "International",
        "title": "Novel Topical Ointment for Wound Healing",
        "description": "A novel formulation comprising extracts of Curcuma longa (Turmeric) suspended in a clarified butter base, demonstrating exceptional antimicrobial and wound healing properties."
    },
    {
        "claim_id": "PAT-IND-2026-002",
        "applicant": "SynthBio Labs",
        "jurisdiction": "India",
        "title": "Synthetic Polymer for Joint Relief",
        "description": "A completely synthetic, lab-generated polymer chain designed to reduce joint inflammation. Contains no biological or botanical resources."
    },
    {
        "claim_id": "PAT-EU-2026-003",
        "applicant": "EuroCosmetics Ltd",
        "jurisdiction": "International",
        "title": "Anti-Fungal Skin Treatment",
        "description": "An anti-fungal cream utilizing cold-pressed Azadirachta indica (Neem) oil combined with modern stabilizers for treating dermatological disorders."
    }
]

# 2. Generate Mock User Profiles (For ABS Compliance Testing)
user_profiles = [
    {
        "user_id": "USR-001",
        "entity_type": "Indian Academic Researcher",
        "citizenship": "India",
        "intent": "Non-commercial academic research on Withania somnifera."
    },
    {
        "user_id": "USR-002",
        "entity_type": "Foreign Corporation",
        "citizenship": "Germany",
        "intent": "Commercial extraction and patenting of active compounds from Indian botanical sources."
    }
]

# Save the files
with open("synthetic_patent_claims.json", "w") as f:
    json.dump(patent_claims, f, indent=2)

with open("mock_abs_profiles.json", "w") as f:
    json.dump(user_profiles, f, indent=2)

print("✅ Successfully generated 'synthetic_patent_claims.json' and 'mock_abs_profiles.json'!")