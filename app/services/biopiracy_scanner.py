"""
TKDL Biopiracy Claim Scanner
==============================
Performs cosine-similarity vector search against the tkdl_records
Qdrant collection to detect potential biopiracy in patent claims.

Alert Levels:
  HIGH   — score ≥ 70  (strong prior art, near-certain Section 3(p) bar)
  MEDIUM — score ≥ 55  (probable match, warrants expert review)
  LOW    — score ≥ 35  (weak match, monitor)
  NONE   — score <  35 (no significant prior art found)

Tune thresholds here before a demo — raise ALERT_THRESHOLD_MEDIUM to 0.65
to reduce false positives on a sparse TKDL dataset, or lower to 0.45 if
the scanner is missing obvious turmeric/neem/Ashwagandha matches.
"""
import logging
from app.services.rag import dense_model, qdrant
from pipeline.config import TKDL_COLLECTION

logger = logging.getLogger("biopiracy_scanner")

# ---------------------------------------------------------------------------
# Tunable Thresholds
# ---------------------------------------------------------------------------
ALERT_THRESHOLD_HIGH   = 0.70   # cosine similarity → alert_score ≥ 70
ALERT_THRESHOLD_MEDIUM = 0.55   # approved baseline
ALERT_THRESHOLD_LOW    = 0.35

# ---------------------------------------------------------------------------
# Statutory Precedent (injected into HIGH/MEDIUM results)
# ---------------------------------------------------------------------------
SECTION_3P_PRECEDENT = (
    "Patents Act 1970, Section 3(p): Any invention which, in effect, is "
    "traditional knowledge or an aggregation or duplication of known properties "
    "of traditionally known components or processes shall not be patentable. "
    "Landmark precedents — Turmeric wound-healing patent (US 5,401,504) revoked "
    "in 1997 by USPTO after CSIR prior-art challenge using ancient Sanskrit texts; "
    "Neem biopesticide (EP 0436257) revoked by EPO in 2000. The TKDL was created "
    "specifically as a prior-art repository to prevent such grants."
)


# ---------------------------------------------------------------------------
# Main Scanner
# ---------------------------------------------------------------------------

def scan_patent_claim(claim_text: str) -> dict:
    """
    Scan a patent claim against the TKDL records collection.
    Returns a structured biopiracy analysis report.
    """
    # Encode the claim with the already-loaded InLegalBERT dense model
    claim_vec = dense_model.encode(
        claim_text, normalize_embeddings=True
    ).tolist()

    # Query top-5 TKDL prior-art records
    hits = []
    try:
        result = qdrant.query_points(
            collection_name=TKDL_COLLECTION,
            query=claim_vec,
            limit=5,
        )
        hits = result.points
    except Exception as exc:
        logger.error(f"Qdrant TKDL scan failed: {exc}")

    if not hits:
        return _build_result(max_score=0.0, hits=[], claim_text=claim_text)

    max_score = max(h.score for h in hits)
    return _build_result(max_score=max_score, hits=hits, claim_text=claim_text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _alert_level(score: float) -> str:
    if score >= ALERT_THRESHOLD_HIGH:
        return "HIGH"
    elif score >= ALERT_THRESHOLD_MEDIUM:
        return "MEDIUM"
    elif score >= ALERT_THRESHOLD_LOW:
        return "LOW"
    return "NONE"


def _build_result(max_score: float, hits: list, claim_text: str) -> dict:
    level = _alert_level(max_score)
    alert_score = round(max_score * 100, 1)

    matched_records = []
    for h in hits:
        p = h.payload or {}
        matched_records.append({
            "chunk_id":    p.get("chunk_id", ""),
            "source_file": p.get("source_file", "tkdl_sample_dataset.json"),
            "formulation": _extract_formulation(p.get("text", "")),
            "ipc_code":    p.get("ipc_code", ""),
            "tkrc_code":   p.get("tkrc_code", ""),
            "similarity":  round(h.score * 100, 1),
            "snippet":     p.get("text", "")[:300],
        })

    section_3p_applicable = level in ("HIGH", "MEDIUM")

    recommended_action = {
        "HIGH": (
            "⛔ STRONG BIOPIRACY RISK — This claim closely resembles TKDL-documented "
            "traditional knowledge. Section 3(p) of the Patents Act would very likely bar "
            "this claim. Do NOT file without substantially differentiating the inventive step "
            "from the prior art identified above."
        ),
        "MEDIUM": (
            "⚠️ MODERATE RISK — Prior art in TKDL partially overlaps with this claim. "
            "A formal TKDL prior-art search and legal opinion are strongly recommended "
            "before filing. Section 3(p) opposition from CSIR/AYUSH is probable."
        ),
        "LOW": (
            "🔍 LOW RISK — Weak similarity detected. Conduct a full freedom-to-operate "
            "analysis and TKDL clearance search before proceeding to grant stage."
        ),
        "NONE": (
            "✅ NO SIGNIFICANT PRIOR ART FOUND — No strong TKDL match detected for this "
            "claim. Standard patent novelty and inventive step analysis still required. "
            "Consider commissioning a full TKDL and InPASS prior-art search."
        ),
    }[level]

    return {
        "alert_score":           alert_score,
        "alert_level":           level,
        "section_3p_applicable": section_3p_applicable,
        "section_3p_precedent":  SECTION_3P_PRECEDENT if section_3p_applicable else None,
        "matched_records":       matched_records,
        "recommended_action":    recommended_action,
        "claim_analyzed":        claim_text[:300],
    }


def _extract_formulation(text: str) -> str:
    """Extract the term, case study, or formulation name from a TKDL chunk's text field."""
    for part in text.split("."):
        if "Term:" in part:
            return part.replace("Term:", "").strip()
        elif "Bio-Piracy Case Study:" in part:
            return part.replace("Bio-Piracy Case Study:", "").strip()
        elif "Formulation:" in part:
            return part.replace("Formulation:", "").strip()
    return "Traditional Knowledge Representative Term"
