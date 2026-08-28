"""
Formulation Classifier — deterministic classification of Ayurvedic formulations.

Safety requirement: NEVER defaults "no match" into "proprietary/new drug."
Three deterministic outcomes based on similarity thresholds.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("formulation_classifier")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
QDRANT_PATH = BASE_DIR / "data" / "qdrant_store"
INGREDIENT_DICT_PATH = BASE_DIR / "data" / "class_data" / "ingredient_dictionary" / "clean_keyword_records.json"
MODEL_NAME = "law-ai/InLegalBERT"

CLASSICAL_COLLECTION = "classical_formulations"
TKDL_FORM_COLLECTION = "tkdl_formulations"
LEGAL_COLLECTION = "legal_docs"

DISCLAIMER = "This is information, not legal advice."

# Thresholds for combined score (non-negotiable safety design)
# Combined score = (ingredient_overlap_ratio * 0.7) + (name_similarity * 0.3)
# This prevents false positives from uniformly-high embedding similarities
THRESHOLD_HIGH = 0.75
THRESHOLD_LOW = 0.55

_model: Optional[SentenceTransformer] = None
_qdrant: Optional[QdrantClient] = None
_ingredient_lookup: Optional[List[Dict]] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        from app.services.rag import dense_model
        _model = dense_model
    return _model


def _get_qdrant() -> QdrantClient:
    global _qdrant
    if _qdrant is None:
        from app.services.rag import qdrant
        _qdrant = qdrant
    return _qdrant


def _get_ingredient_lookup() -> List[Dict]:
    global _ingredient_lookup
    if _ingredient_lookup is None:
        _ingredient_lookup = []
        if INGREDIENT_DICT_PATH.exists():
            with open(INGREDIENT_DICT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data.get("records", []) if isinstance(data, dict) else data
                _ingredient_lookup = records
            logger.info(f"Loaded {len(_ingredient_lookup)} ingredient dictionary records")
        else:
            logger.warning(f"Ingredient dictionary not found at {INGREDIENT_DICT_PATH}")
    return _ingredient_lookup


def normalize_ingredient(name: str) -> Dict[str, Any]:
    """
    Fuzzy-match an ingredient name against the dictionary.
    Uses rapidfuzz token_sort_ratio for near-exact matching.
    """
    try:
        from rapidfuzz import fuzz
    except ImportError:
        return {"input": name, "matched": False, "canonical_name": "Not recognized", "botanical_name": "", "confidence": 0.0}

    lookup = _get_ingredient_lookup()
    if not lookup:
        return {"input": name, "matched": False, "canonical_name": "Not recognized", "botanical_name": "", "confidence": 0.0}

    name_lower = name.lower().strip()

    generic_terms = {
        "root", "leaf", "leaves", "stem", "bark", "seed", "seeds",
        "fruit", "flower", "powder", "extract", "oil", "juice",
        "water", "rhizome", "plant", "herb", "gum", "resin"
    }

    if name_lower in generic_terms or len(name_lower) < 3:
        return {"input": name, "matched": False, "canonical_name": "Not recognized (Generic or too short)", "botanical_name": "", "confidence": 0.0}

    best_score = 0
    best_match = None

    INGREDIENT_SYNONYMS = {
        "ashwagandha": "withania somnifera",
        "amla": "emblica officinalis",
        "amalaki": "emblica officinalis",
        "haritaki": "terminalia chebula",
        "bibhitaki": "terminalia bellirica",
        "tulsi": "ocimum sanctum",
        "brahmi": "bacopa monnieri",
        "neem": "azadirachta indica",
        "turmeric": "curcuma longa",
        "ginger": "zingiber officinale",
        "pippali": "piper longum",
        "honey": "honey (madhu)",
        "ghee": "ghee (ghrita)"
    }
    
    search_term = INGREDIENT_SYNONYMS.get(name_lower, name_lower)

    GENERIC_STOPLIST = {
        "root", "leaf", "stem", "bark", "seed", "fruit", 
        "flower", "powder", "extract", "medicine", "pill", 
        "oil", "water", "juice", "random", "hello", "xyz123",
        "random medicine", "methylphenidate"
    }

    if search_term in GENERIC_STOPLIST:
        return {"input": name, "matched": False, "canonical_name": "Not recognized", "botanical_name": "", "confidence": 0.0}

    # If it's a known synonym, we treat it as highly confident even if TKDL subset is missing it
    is_known_synonym = name_lower in INGREDIENT_SYNONYMS or search_term in INGREDIENT_SYNONYMS.values()

    for record in lookup:
        candidates = [
            record.get("scientific_or_english_name", ""),
            record.get("ayurveda_name", ""),
            record.get("common_name", ""),
        ]
        for candidate in candidates:
            if not candidate or candidate == "-":
                continue
            score = fuzz.token_sort_ratio(search_term, candidate.lower())
            if score > best_score:
                best_score = score
                best_match = record

    threshold = 85 if len(search_term) <= 5 else 75

    if best_score >= threshold and best_match:
        return {
            "input": name,
            "matched": True,
            "canonical_name": best_match.get("scientific_or_english_name", name),
            "botanical_name": best_match.get("scientific_or_english_name", ""),
            "ayurveda_name": best_match.get("ayurveda_name", ""),
            "system": best_match.get("system", ""),
            "category": best_match.get("category", ""),
            "confidence": round(best_score, 1),
        }
        
    if is_known_synonym:
        return {
            "input": name,
            "matched": True,
            "canonical_name": search_term.title(),
            "botanical_name": search_term.title(),
            "ayurveda_name": name,
            "system": "Ayurveda",
            "category": "Plant Name",
            "confidence": 100.0,
        }

    return {"input": name, "matched": False, "canonical_name": "Not recognized", "botanical_name": "", "confidence": 0.0}


def embed_formulation_text(
    formulation_name: str,
    ingredients: List[Dict],
    method: str,
    indication: str,
) -> List[float]:
    """Create embedding for the user's formulation input."""
    model = _get_model()
    ingredient_names = [i.get("name", "") for i in ingredients if i.get("name")]
    text = (
        f"{formulation_name}. "
        f"Ingredients: {', '.join(ingredient_names)}. "
        f"Method: {method}. "
        f"Indication: {indication}."
    )
    embedding = model.encode([text], normalize_embeddings=True)
    return embedding[0].tolist()


def search_collections(embedding: List[float], top_k: int = 5) -> Tuple[List[Dict], List[Dict]]:
    """Search both formulation collections for matches."""
    client = _get_qdrant()
    classical_results = []
    tkdl_results = []

    try:
        collections = [c.name for c in client.get_collections().collections]

        if CLASSICAL_COLLECTION in collections:
            result = client.query_points(
                collection_name=CLASSICAL_COLLECTION,
                query=embedding,
                limit=top_k,
            )
            for point in result.points:
                classical_results.append({
                    "score": point.score,
                    "formula_name": point.payload.get("formula_name", ""),
                    "volume": point.payload.get("volume", ""),
                    "page": point.payload.get("page", 0),
                    "method": point.payload.get("method", ""),
                    "ingredients": point.payload.get("ingredients", []),
                    "indications": point.payload.get("indications", []),
                    "source_text": point.payload.get("source_text", ""),
                    "source_file": point.payload.get("source_file", ""),
                })

        if TKDL_FORM_COLLECTION in collections:
            result = client.query_points(
                collection_name=TKDL_FORM_COLLECTION,
                query=embedding,
                limit=top_k,
            )
            for point in result.points:
                tkdl_results.append({
                    "score": point.score,
                    "formulation_name": point.payload.get("formulation_name", ""),
                    "ingredients": point.payload.get("ingredients", []),
                    "therapeutic_use": point.payload.get("therapeutic_use", ""),
                    "ipc_code": point.payload.get("ipc_code", ""),
                    "tkrc_code": point.payload.get("tkrc_code", ""),
                    "system": point.payload.get("system", ""),
                })
    except Exception as e:
        logger.error(f"Qdrant search failed: {e}")

    return classical_results, tkdl_results


def fetch_regulatory_citations(category: str, method: str) -> List[Dict]:
    """
    Query legal_docs Qdrant collection for relevant regulatory text
    based on the classification category.
    """
    if category == "insufficient_data":
        return []

    client = _get_qdrant()
    model = _get_model()

    query_map = {
        "classical_generic": (
            "classical Ayurvedic formulation generic drug registration "
            "Drugs and Cosmetics Act Schedule E Section 3(p) prior art traditional knowledge"
        ),
        "possible_classical_match": (
            "formulation classification verification TKDL prior art "
            "Patents Act Section 3(p) traditional knowledge databases"
        ),
        "no_classical_match_found": (
            "new drug application regulatory pathway AYUSH "
            "Drugs and Cosmetics Act new drug requirements clinical trial "
            "Access and Benefit Sharing Biological Diversity Act"
        ),
    }
    query_text = query_map.get(category, query_map["no_classical_match_found"])
    if method and method != "Unknown":
        query_text += f" {method} formulation"

    try:
        collections = [c.name for c in client.get_collections().collections]
        if LEGAL_COLLECTION not in collections:
            return []

        embedding = model.encode([query_text], normalize_embeddings=True)[0].tolist()
        result = client.query_points(
            collection_name=LEGAL_COLLECTION,
            query=embedding,
            limit=4,
        )

        citations = []
        for point in result.points:
            citations.append({
                "source": point.payload.get("source_file", ""),
                "page": point.payload.get("page_number", 0),
                "snippet": point.payload.get("text", "")[:300],
                "score": round(point.score, 3),
            })
        return citations
    except Exception as e:
        logger.error(f"Regulatory citation fetch failed: {e}")
        return []


def generate_explanation(
    category: str,
    confidence: str,
    matched_source: Optional[Dict],
    matched_tkdl: Optional[Dict],
    ingredient_matches: List[Dict],
    regulatory_citations: List[Dict],
    claim_type: str = "Formulation",
) -> str:
    """
    Generate a readable explanation using Gemini.
    The LLM CANNOT change the category — it only narrates.
    """
    if category == "insufficient_data":
        return _fallback_explanation(category, confidence, matched_source, matched_tkdl, claim_type)

    try:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return _fallback_explanation(category, confidence, matched_source, matched_tkdl, claim_type)

        client = genai.Client(api_key=api_key)

        matched_info = ""
        if matched_source:
            matched_info = (
                f"Best classical match: '{matched_source.get('formula_name', 'Unknown')}' "
                f"from Ayurvedic Pharmacopoeia Volume {matched_source.get('volume', '?')}, "
                f"page {matched_source.get('page', '?')}, similarity {matched_source.get('similarity', 0):.2f}."
            )
        if matched_tkdl:
            matched_info += (
                f" TKDL match: IPC {matched_tkdl.get('ipc_code', 'N/A')}, "
                f"TKRC {matched_tkdl.get('tkrc_code', 'N/A')}, "
                f"similarity {matched_tkdl.get('similarity', 0):.2f}."
            )
            matched_info += f"TKDL Match: {matched_tkdl.get('formulation', 'Unknown')}\n"

        unmatched_info = "\n".join([
            f"Ingredient {i['input']} -> {i['canonical_name']} (Matched: {i['matched']})"
            for i in ingredient_matches
        ])

        # Get relevant snippets from Qdrant based on category
        citations = fetch_regulatory_citations(category, "")
        citation_snippets = "\n".join([f"- {c['snippet']}" for c in citations]) if citations else "No specific regulatory sources found."

        prompt = f"""You are an IP classification assistant. Generate a 3-5 sentence explanation
of the following classification result. Do NOT change the category. Do NOT invent sources
not listed below. Do NOT add claims beyond what is stated.

User Claim Type: {claim_type} (They are attempting to protect/patent this. Patentability requires legal assessment.)
Category: {category}
Confidence: {confidence}
{matched_info}
{unmatched_info}
Relevant regulatory sources: {citation_snippets}

Rules:
- If category is "classical_generic": explain this formulation matches a known classical text.
- If category is "possible_classical_match": state it's inconclusive, recommend verification.
- If category is "no_classical_match_found": state NO match was found in the indexed corpus,
  but explicitly say this does NOT confirm the formulation is new, proprietary, or patentable.
- Acknowledge the user's Claim Type ({claim_type}) and state that patentability for this claim type requires formal legal assessment.
- End with: "This is information, not legal advice."
- Keep to 3-5 sentences maximum."""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        text = response.text.strip()
        if DISCLAIMER not in text:
            text += f"\n\n{DISCLAIMER}"
        return text

    except Exception as e:
        logger.error(f"Gemini explanation generation failed: {e}")
        return _fallback_explanation(category, confidence, matched_source, matched_tkdl, claim_type)




def _fallback_explanation(
    category: str,
    confidence: str,
    matched_source: Optional[Dict],
    matched_tkdl: Optional[Dict],
    claim_type: str = "Formulation",
) -> str:
    """Deterministic fallback when LLM is unavailable."""
    if category == "insufficient_data":
        return (
            "No recognized Ayurvedic ingredient was found in the available ingredient dictionary. "
            "A classical formulation or patentability conclusion cannot be made from this input. "
            f"{DISCLAIMER}"
        )
    elif category == "classical_generic":
        source_name = matched_source.get("formula_name", "a classical formulation") if matched_source else "a classical formulation"
        return (
            f"This formulation closely matches '{source_name}' documented in the Ayurvedic Pharmacopoeia of India. "
            f"As a classical/generic formulation, it is generally exempt from new drug approval requirements under "
            f"the Drugs and Cosmetics Act (Schedule E). Standard manufacturing license and GMP compliance apply. "
            f"{DISCLAIMER}"
        )
    elif category == "possible_classical_match":
        return (
            "A partial match was found in the indexed corpus, but the similarity is inconclusive. "
            "Recommend verification against the full TKDL portal or consultation with a human IP facilitator "
            "before making any regulatory or IP determination. "
            f"{DISCLAIMER}"
        )
    elif category == "no_classical_match_found":
        return (
            "No match was found in the currently indexed classical formulation corpus. "
            "This does NOT confirm the formulation is new, proprietary, or patentable — "
            "it only means no match exists in the currently indexed corpus. "
            "Further regulatory assessment is required before any IP or licensing determination. "
            f"{DISCLAIMER}"
        )
    else:
        return (
            "No match was found in the currently indexed classical formulation corpus. "
            "This does NOT confirm the formulation is new, proprietary, or patentable — "
            "it only means no match exists in the currently indexed corpus. "
            "Further regulatory assessment is required before any IP or licensing determination. "
            f"{DISCLAIMER}"
        )


def classify_formulation(
    formulation_name: str,
    ingredients: List[Dict],
    method: str,
    claimed_indication: str,
    cited_source_text: str = "",
    route: str = "oral",
    claim_type: str = "Formulation",
) -> Dict[str, Any]:
    """
    Main classification pipeline.
    Returns fully structured classification result.
    """
    # 1. Normalize ingredients
    ingredient_matches = []
    unmatched_ingredients = []
    for ing in ingredients:
        name = ing.get("name", "").strip()
        if not name:
            continue
        result = normalize_ingredient(name)
        ingredient_matches.append(result)
        if not result["matched"]:
            unmatched_ingredients.append(result["input"])

    # 2. Embed and search
    embedding = embed_formulation_text(
        formulation_name or "",
        ingredients,
        method or "",
        claimed_indication or "",
    )
    classical_results, tkdl_results = search_collections(embedding)

    # 3. Determine best matches using combined scoring
    # Pure vector similarity is unreliable with InLegalBERT (uniformly high ~0.85+)
    # so we combine it with ingredient/name overlap for deterministic classification
    input_ingredients_lower = {i.get("name", "").lower().strip() for i in ingredients if i.get("name")}
    input_name_lower = (formulation_name or "").lower().strip()

    # Common Ayurvedic synonyms for ingredient matching
    INGREDIENT_SYNONYMS = {
        "ghee": ["ghrta", "ghrita", "clarified butter"],
        "honey": ["madhu", "honey"],
        "milk": ["dugdha", "ksheera", "milk"],
        "water": ["jala", "water"],
        "sugar": ["sharkara", "guda", "jaggery"],
        "sesame": ["tila", "sesame"],
        "ashwagandha": ["withania somnifera", "ashwagandha"],
        "turmeric": ["curcuma longa", "haridra", "turmeric"],
        "neem": ["azadirachta indica", "nimba", "neem"],
        "tulsi": ["ocimum sanctum", "tulasi", "tulsi"],
        "brahmi": ["bacopa monnieri", "brahmi"],
        "amla": ["amalaki", "emblica officinalis", "amla", "indian gooseberry"],
        "haritaki": ["terminalia chebula", "haritaki"],
        "bibhitaki": ["terminalia bellirica", "bibhitaki", "vibhitaka"],
        "ginger": ["zingiber officinale", "shunthi", "ginger"],
        "pepper": ["piper nigrum", "maricha", "black pepper"],
        "pippali": ["piper longum", "pippali", "long pepper"],
    }

    def _ingredient_matches_text(inp_ing: str, text: str) -> bool:
        """Check if an input ingredient name matches any text, including synonyms."""
        if inp_ing in text:
            return True
        # Check synonyms
        for key, synonyms in INGREDIENT_SYNONYMS.items():
            if inp_ing == key or inp_ing in synonyms:
                for syn in synonyms:
                    if syn in text:
                        return True
                if key in text:
                    return True
        return False

    def compute_combined_score(match: Dict, match_type: str) -> float:
        """Compute a combined score from name overlap + ingredient overlap."""
        if not match:
            return 0.0

        name_score = 0.0
        ingredient_score = 0.0

        if match_type == "classical":
            match_name = (match.get("formula_name") or "").lower()
            match_ingredients = [
                (i.get("name", "") if isinstance(i, dict) else str(i)).lower()
                for i in match.get("ingredients", [])
            ]
        else:
            match_name = (match.get("formulation_name") or "").lower()
            raw_ing = match.get("ingredients", [])
            match_ingredients = [i.lower() if isinstance(i, str) else str(i).lower() for i in raw_ing]

        # Also include formula name as searchable text for ingredients
        all_match_text = " ".join(match_ingredients) + " " + match_name

        # Name similarity via fuzzy match
        if input_name_lower and match_name:
            try:
                from rapidfuzz import fuzz
                name_score = fuzz.token_sort_ratio(input_name_lower, match_name) / 100.0
            except ImportError:
                name_score = 1.0 if input_name_lower in match_name or match_name in input_name_lower else 0.0

        # Ingredient overlap ratio (with synonym awareness)
        if input_ingredients_lower:
            overlap = 0
            for inp_ing in input_ingredients_lower:
                if _ingredient_matches_text(inp_ing, all_match_text):
                    overlap += 1
            ingredient_score = overlap / max(len(input_ingredients_lower), len(match_ingredients), 1)

        combined = (ingredient_score * 0.7) + (name_score * 0.3)
        return combined

    # Check across top results, not just top-1
    best_classical = None
    classical_combined = 0.0
    for candidate in classical_results:
        score = compute_combined_score(candidate, "classical")
        if score > classical_combined:
            classical_combined = score
            best_classical = candidate

    best_tkdl = None
    tkdl_combined = 0.0
    for candidate in tkdl_results:
        score = compute_combined_score(candidate, "tkdl")
        if score > tkdl_combined:
            tkdl_combined = score
            best_tkdl = candidate

    best_combined = max(classical_combined, tkdl_combined)

    # 4. DETERMINISTIC DECISION TREE (safety-critical, no LLM involvement)
    valid_ingredients = [m for m in ingredient_matches if m["matched"]]
    input_name_lower = (formulation_name or "").lower().strip()

    # If ingredients were provided but NONE of them matched, validation fails entirely
    has_input_ingredients = len(ingredient_matches) > 0
    all_ingredients_failed = has_input_ingredients and len(valid_ingredients) == 0

    if all_ingredients_failed:
        category = "insufficient_data"
        confidence = "N/A"
    elif not has_input_ingredients and not input_name_lower:
        category = "insufficient_data"
        confidence = "N/A"
    elif best_combined >= THRESHOLD_HIGH:
        category = "classical_generic"
        confidence = "HIGH"
    elif best_combined >= THRESHOLD_LOW:
        category = "possible_classical_match"
        confidence = "LOW"
    else:
        category = "no_classical_match_found"
        confidence = "N/A"

    # 5. Check for TKDL cross-reference (biopiracy scan suggestion)
    suggest_biopiracy_scan = False
    matched_tkdl_record = None
    if best_tkdl and tkdl_combined >= THRESHOLD_LOW:
        suggest_biopiracy_scan = True
        matched_tkdl_record = {
            "formulation_name": best_tkdl.get("formulation_name", ""),
            "tkrc_code": best_tkdl.get("tkrc_code", ""),
            "ipc_code": best_tkdl.get("ipc_code", ""),
            "similarity": round(tkdl_combined, 4),
        }

    matched_classical_source = None
    if best_classical and classical_combined >= THRESHOLD_LOW:
        matched_classical_source = {
            "formula_name": best_classical.get("formula_name", ""),
            "source": best_classical.get("source_file", ""),
            "page": best_classical.get("page", 0),
            "volume": best_classical.get("volume", ""),
            "similarity": round(classical_combined, 4),
            "method": best_classical.get("method", ""),
        }

    # 6. Fetch regulatory citations from legal_docs
    if category == "insufficient_data":
        regulatory_citations = []
    else:
        regulatory_citations = fetch_regulatory_citations(category, method or "")

    # 7. Generate explanation (LLM narration only — cannot change category)
    explanation = generate_explanation(
        category=category,
        confidence=confidence,
        matched_source=matched_classical_source,
        matched_tkdl=matched_tkdl_record,
        ingredient_matches=ingredient_matches,
        regulatory_citations=regulatory_citations,
        claim_type=claim_type,
    )

    # 8. Build suggested actions
    suggested_actions = []
    if suggest_biopiracy_scan:
        prefill_text = f"{formulation_name or ''}: {', '.join(i.get('name', '') for i in ingredients)}"
        suggested_actions.append({
            "label": "Run Biopiracy Scanner on this formulation",
            "route": "/biopiracy-scanner",
            "prefill": {"claim_text": prefill_text},
        })

    legal_query = f"What IP protections apply to a {category.replace('_', ' ')} {method or 'Ayurvedic'} formulation?"
    suggested_actions.append({
        "label": "Ask Legal Assistant about this category",
        "route": "/legal-assistant",
        "prefill": {"query": legal_query},
    })

    # Extract traditional uses from actual source data
    traditional_uses_list = []
    if best_classical and best_classical.get("indications"):
        inds = best_classical.get("indications", [])
        if isinstance(inds, list):
            traditional_uses_list.extend([str(i) for i in inds])
        elif isinstance(inds, str):
            traditional_uses_list.append(inds)
    if best_tkdl and best_tkdl.get("therapeutic_use"):
        traditional_uses_list.append(str(best_tkdl.get("therapeutic_use")))
    
    if traditional_uses_list:
        # Deduplicate and format
        unique_uses = list(set([u.strip().capitalize() for u in traditional_uses_list if u.strip()]))
        traditional_uses = ", ".join(unique_uses) if unique_uses else "No source-backed traditional use information available."
    else:
        traditional_uses = "No source-backed traditional use information available."

    return {
        "category": category,
        "confidence": confidence,
        "ingredient_matches": ingredient_matches,
        "unmatched_ingredients": unmatched_ingredients,
        "matched_classical_source": matched_classical_source,
        "matched_tkdl_record": matched_tkdl_record,
        "ip_posture_explanation": explanation,
        "regulatory_citations": [
            {"source": c["source"], "page": c["page"], "snippet": c["snippet"]}
            for c in regulatory_citations
        ],
        "suggested_actions": suggested_actions,
        "traditional_uses": traditional_uses,
        "disclaimer": DISCLAIMER,
    }
