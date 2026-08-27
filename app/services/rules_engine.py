"""
Formulation Classification — 6-Category Decision Tree
=======================================================
Implements the multi-step diagnostic triage defined in Problem Statement ID 26045.

Categories:
  1. Classical Ayurvedic Medicine   — First Schedule text, Section 3(p) bar, TKDL defense
  2. Proprietary Ayurvedic Medicine — Novel formula, patent potential, ASU licensing
  3. New / Non-Classical Drug        — Safety & efficacy data required, patent viable
  4. Phytopharmaceutical             — CDSCO plant-extract pathway, ABS mandatory
  5. Ayurveda-Aahar / Nutraceutical — FSSAI 2022 regime, health-claim rules
  6. Cosmetic                        — Drugs & Cosmetics Act Schedule Q, label rules

Each category returns:
  - Classification label
  - Statutory provision (Act + Section)
  - IP posture summary
  - ABS duties
  - Recommended next steps
  - Required forms
  - Approval timeline
"""

from dataclasses import dataclass, field
from typing import Optional
from app.schemas.payloads import (
    ABSRequest,
    FormulationRequest,
    ComplianceResponse,
    EntityType,
    ResourceSource,
    WizardState,
    WizardResponse,
)


# ---------------------------------------------------------------------------
# ABS Compliance Engine (unchanged + extended)
# ---------------------------------------------------------------------------

def evaluate_abs_compliance(data: ABSRequest) -> ComplianceResponse:
    if data.entity_type == EntityType.FOREIGN:
        return ComplianceResponse(
            classification="Foreign Entity — ABS Approval Required",
            statutory_provision="Biological Diversity Act 2002, Section 3 & NBA Regulations 2014",
            ip_posture=(
                "Foreign entities MUST obtain prior approval from the National Biodiversity "
                "Authority (NBA) before accessing any Indian biological resource or associated "
                "traditional knowledge for commercial/research purposes."
            ),
            abs_duties=(
                "File Form 11 with the NBA. Benefit-sharing agreement mandatory. "
                "No access without written approval — violation attracts imprisonment up to 5 years."
            ),
            required_forms=["Form 11 (NBA)", "Benefit-Sharing Agreement"],
            approval_timeline="90–180 days (NBA review)",
            recommended_next_steps=[
                "File NBA Form 11 before accessing any biological resource.",
                "Negotiate benefit-sharing terms with local communities / State Biodiversity Boards.",
                "Register with the People's Biodiversity Register (PBR) of the source district.",
            ],
        )
    elif data.entity_type == EntityType.INDIAN and data.resource_source == ResourceSource.CULTIVATED:
        return ComplianceResponse(
            classification="Indian Entity — Cultivated Resource (2024 BD Rules Exemption)",
            statutory_provision="BD (Amendment) Act 2023; BD Rules 2024, Rule 7 Exemption",
            ip_posture=(
                "Cultivated Indian biological resources are largely exempt from NBA prior approval "
                "under the 2023 amendment. IP filings (patents, trademarks) may proceed with "
                "a Section 20 declaration in the patent application."
            ),
            abs_duties=(
                "Prior intimation to the State Biodiversity Board (SBB) via BMC Form 1 at least "
                "15 days before commercialisation. Benefit-sharing with local cultivators if "
                "traditional knowledge associated with the cultivar is used."
            ),
            required_forms=["BMC Form 1 (SBB Prior Intimation)"],
            approval_timeline="15-day prior intimation (no formal approval required for cultivated resources)",
            recommended_next_steps=[
                "File BMC Form 1 with the State Biodiversity Board.",
                "Confirm cultivation records proving resource is not wild-collected.",
                "Proceed with IP filings; include BD Act Section 20 declaration.",
            ],
        )
    elif data.entity_type == EntityType.INDIAN and data.resource_source == ResourceSource.WILD:
        return ComplianceResponse(
            classification="Indian Entity — Wild-Sourced Resource",
            statutory_provision="BD Act 2002, Section 7; BD Rules 2004/2024",
            ip_posture=(
                "Wild-sourced biological resources require State Biodiversity Board (SBB) approval "
                "for commercial use. IP filing is permissible but the patent application must "
                "declare the biological material source (Patents Act Section 10(4)(d))."
            ),
            abs_duties=(
                "Obtain SBB approval via Form I. Benefit-sharing with local communities. "
                "Disclose biological resource source in any patent application."
            ),
            required_forms=["Form I (SBB Approval)", "Source Disclosure in Patent Application"],
            approval_timeline="Variable — SBB review typically 30–90 days",
            recommended_next_steps=[
                "Apply to State Biodiversity Board for commercial access approval.",
                "Engage local communities for benefit-sharing terms.",
                "Ensure source declaration is included in all IP filings.",
            ],
        )
    else:
        return ComplianceResponse(
            classification="Indian Entity — General BD Act Provisions Apply",
            statutory_provision="BD Act 2002 & 2024 Rules",
            ip_posture="Context-dependent — consult State Biodiversity Board.",
            abs_duties="Consult SBB for specific requirements based on resource type and end use.",
            required_forms=["Form I (SBB)"],
            approval_timeline="Variable",
            recommended_next_steps=["Consult nearest State Biodiversity Board office."],
        )


# ---------------------------------------------------------------------------
# Simple (legacy) formulation classifier — kept for backward-compatibility
# ---------------------------------------------------------------------------

def classify_formulation(data: FormulationRequest) -> ComplianceResponse:
    """Legacy single-shot classifier. Prefer run_wizard_step() for full triage."""
    first_sched = False
    if getattr(data, "from_first_schedule", None) is not None:
        first_sched = bool(data.from_first_schedule)
    elif data.source_text:
        src_lower = data.source_text.lower()
        first_schedule_texts = [
            "charaka", "sushruta", "ashtanga", "sahasrayogam", "bhavaprakasha",
            "sharangadhara", "bhaishajya", "ayurvedic pharmacopoeia", "api", "first schedule",
            "first-schedule", "schedule 1", "classical"
        ]
        first_sched = any(txt in src_lower for txt in first_schedule_texts) or "yes" in src_lower or "true" in src_lower

    return _classify_by_answers(
        from_first_schedule=first_sched,
        intended_use=data.intended_use.lower(),
        is_novel=getattr(data, "is_novel", False),
        resource_source="cultivated",
    )


# ---------------------------------------------------------------------------
# 6-Category Decision Logic
# ---------------------------------------------------------------------------

def _classify_by_answers(
    from_first_schedule: bool,
    intended_use: str,
    is_novel: bool,
    resource_source: str,
) -> ComplianceResponse:
    """
    Core 6-category decision tree.
    Statutory ordering:
    1. Classical Ayurvedic Medicine (First Schedule check MUST execute first!)
    2. Phytopharmaceutical Drug (CDSCO GSR 918(E) extract pathway)
    3. New / Non-Classical Ayurvedic Drug (Genuinely novel formula)
    4. Ayurveda-Aahar / Nutraceutical (FSSAI 2022 food/diet regime)
    5. Cosmetic (Schedule Q / Drugs & Cosmetics Rules 1945 cosmetic use)
    6. Proprietary Ayurvedic Medicine (Default proprietary medicine)
    """

    # ── 1. CLASSICAL AYURVEDIC MEDICINE ─────────────────────────────────────
    # Must precede cosmetic/food checks! A classical formulation (e.g. hair oil,
    # skin taila, lepa) derived from First Schedule texts is statutorily a Classical Medicine.
    if from_first_schedule:
        return ComplianceResponse(
            classification="Classical Ayurvedic Medicine",
            statutory_provision=(
                "Drugs and Cosmetics Act 1940, Section 3(a) & First Schedule; "
                "ASU Drugs (Manufacture, Sale and Distribution) Rules 1964"
            ),
            ip_posture=(
                "Classical formulations derived from First Schedule authoritative texts "
                "(Charaka Samhita, Sushruta Samhita, Ashtanga Hridayam, Bhavaprakasha, Sahasrayogam, etc.) "
                "face an ABSOLUTE PATENT BAR under Patents Act Section 3(p). "
                "They are defended as Traditional Knowledge through the TKDL. "
                "Geographical Indication (GI) may be available for region-specific preparations "
                "(e.g., Kottakkal Arya Vaidya Sala formulations)."
            ),
            abs_duties=(
                "Classical formulations drawing on community traditional knowledge may attract "
                "ABS duties if a novel commercial extraction process is used on wild resources. "
                "Cultivated ingredients are exempt under BD Amendment 2023."
            ),
            required_forms=[
                "Form 24-D (ASU Drug Manufacturing Licence)",
                "GMP Certificate for AYUSH",
            ],
            approval_timeline="60–120 days (State Licensing Authority for manufacturing)",
            recommended_next_steps=[
                "No patent viable — focus on brand, trademark, and GI strategies.",
                "Search TKDL to confirm prior-art coverage and defensive record.",
                "Apply for ASU Drug Manufacturing Licence (Form 24-D) at State AYUSH Directorate.",
                "Consider GI registration if geographically distinct traditional practice involved.",
            ],
        )

    # ── 2. PHYTOPHARMACEUTICAL ───────────────────────────────────────────────
    if "phyto" in intended_use or "extract" in intended_use or "standardized" in intended_use:
        return ComplianceResponse(
            classification="Phytopharmaceutical Drug",
            statutory_provision=(
                "Drugs and Cosmetics Act 1940, Section 3 (as amended); "
                "Phytopharmaceuticals Rules 2015 (Gazette Notification GSR 918(E)); "
                "CDSCO Phytopharmaceutical Guidance 2015"
            ),
            ip_posture=(
                "Phytopharmaceuticals occupy a distinct IP space. The plant-extract process, "
                "novel dosage form, or purified active fraction may be patented. "
                "The underlying plant and traditional use are not patentable (Section 3(p)). "
                "CDSCO requires standardisation data (HPLC fingerprinting, biomarkers)."
            ),
            abs_duties=(
                "Strong ABS duties apply if wild-sourced plant material is used. "
                "NBA approval required for foreign entities; SBB approval for Indian entities "
                "using wild resources. Disclosure of biological source mandatory in patent filings."
            ),
            required_forms=[
                "CDSCO Form 44 (New Drug Application — Phytopharmaceutical)",
                "NBA Form 11 or SBB Form I (ABS)",
                "HPLC Fingerprint & Biomarker Standardisation Report",
            ],
            approval_timeline="18–24 months (CDSCO new drug approval pathway)",
            recommended_next_steps=[
                "File IND (Investigational New Drug) application with CDSCO before clinical trials.",
                "Ensure ABS approval before accessing wild-sourced raw material.",
                "Patent the novel extraction process or standardised formulation (not the plant itself).",
                "Commission HPLC/GC-MS standardisation studies per CDSCO guidance.",
            ],
        )

    # ── 3. NEW / NON-CLASSICAL DRUG ──────────────────────────────────────────
    if is_novel:
        return ComplianceResponse(
            classification="New / Non-Classical Ayurvedic Drug",
            statutory_provision=(
                "Drugs and Cosmetics Act 1940, Section 3 & Schedule Y (as adapted for AYUSH); "
                "New Drugs and Clinical Trials Rules 2019; "
                "CDSCO-AYUSH Guidelines for New AYUSH Drugs 2022"
            ),
            ip_posture=(
                "New drugs with a novel formula, mechanism, or dosage form HAVE genuine patent "
                "potential under the Patents Act 1970, provided novelty, inventive step, and "
                "industrial applicability are established. "
                "Section 3(p) does not bar truly novel combinations not documented in ancient texts. "
                "However, if the combination is a mere admixture of known Ayurvedic ingredients, "
                "it may be rejected under Section 3(e) (obvious combination)."
            ),
            abs_duties=(
                "ABS duties fully apply. NBA/SBB prior approval required based on entity type "
                "and whether wild resources are used. Disclose biological source in patent application "
                "per Patents Act Section 10(4)(d)."
            ),
            required_forms=[
                "CDSCO Form 44 (New Drug Application)",
                "Ethics Committee Approval",
                "Phase I/II/III Clinical Trial Data",
                "NBA Form 11 or SBB Form I (ABS)",
            ],
            approval_timeline="3–7 years (full new drug approval pathway with clinical trials)",
            recommended_next_steps=[
                "File provisional patent application immediately to establish priority date.",
                "Engage CDSCO pre-submission meeting for IND pathway clarity.",
                "Conduct TKDL and patent database prior-art search before final patent filing.",
                "Ensure ABS compliance before sourcing biological materials.",
                "Budget for Phase I safety study as minimum clinical evidence requirement.",
            ],
        )

    # ── 4. AYURVEDA-AAHAR / NUTRACEUTICAL ───────────────────────────────────
    if "food" in intended_use or "diet" in intended_use or "nutraceutical" in intended_use or "supplement" in intended_use or "aahar" in intended_use:
        return ComplianceResponse(
            classification="Ayurveda-Aahar / Nutraceutical",
            statutory_provision=(
                "FSSAI Act 2006; Food Safety and Standards (Health Supplements, Nutraceuticals, "
                "etc.) Regulations 2022; FSSAI Ayurveda-Aahar Guidelines 2022"
            ),
            ip_posture=(
                "Nutraceutical formulas may be patented if non-obvious and not merely a known "
                "Ayurvedic combination. Traditional combinations documented in TKDL are anticipated "
                "prior art and face Section 3(p) rejection. "
                "Health claims on packaging are restricted under FSSAI Regulations."
            ),
            abs_duties=(
                "ABS obligations apply if wild-sourced biological resources are used. "
                "FSSAI requires ingredient traceability documentation."
            ),
            required_forms=[
                "FSSAI Central Licence (Form B)",
                "Product Approval (FSSAI Nutraceutical Cell)",
                "BMC Form 1 (if wild-sourced ingredients)",
            ],
            approval_timeline="90–180 days (FSSAI Central approval)",
            recommended_next_steps=[
                "Apply for FSSAI Central Licence under Health Supplements/Nutraceuticals category.",
                "Obtain product-specific approval from FSSAI Nutraceutical Cell.",
                "Review permissible health claims under Schedule — avoid disease-cure claims.",
                "Conduct TKDL prior-art search before filing any patent application.",
            ],
        )

    # ── 5. COSMETIC ─────────────────────────────────────────────────────────
    if "cosmetic" in intended_use or "skin" in intended_use or "hair" in intended_use or "beauty" in intended_use or "topical" in intended_use:
        return ComplianceResponse(
            classification="Cosmetic",
            statutory_provision=(
                "Drugs and Cosmetics Act 1940, Schedule Q; "
                "Drugs and Cosmetics Rules 1945, Rule 144-167"
            ),
            ip_posture=(
                "Cosmetic formulas are patentable if novel and non-obvious. "
                "Trademark and trade-dress protection strongly recommended for branding. "
                "No Section 3(p) bar applies unless formula claims therapeutic action."
            ),
            abs_duties=(
                "ABS duties apply only if wild biological resources are used as ingredients. "
                "Cultivated plant extracts are exempt under BD Amendment 2023."
            ),
            required_forms=["Form 31 (Cosmetic Manufacturing Licence)", "GMP Certificate"],
            approval_timeline="60–90 days (State Licensing Authority)",
            recommended_next_steps=[
                "Obtain Cosmetic Manufacturing Licence (Form 31) from State FDA.",
                "Ensure labelling complies with Schedule Q and Rule 145.",
                "File trademark application for brand name at IP India.",
                "Check ABS duties if wild-sourced botanical ingredients are used.",
            ],
        )

    # ── 6. PROPRIETARY AYURVEDIC MEDICINE (default) ──────────────────────────
    return ComplianceResponse(
        classification="Proprietary Ayurvedic Medicine",
        statutory_provision=(
            "Drugs and Cosmetics Act 1940, Rule 158-B; "
            "Drugs (Prices Control) Order 2013; "
            "AYUSH Ministry Advertising Guidelines 2023"
        ),
        ip_posture=(
            "Proprietary Ayurvedic medicines (novel formulas marketed under a brand name) "
            "may be trademarked and, if genuinely novel and non-obvious, may be patented. "
            "If the formula relies on known Ayurvedic ingredients in standard combinations, "
            "the patent route is narrow — focus on trademark, trade dress, and trade secrets. "
            "Section 3(p) bars claims on known traditional knowledge formulas."
        ),
        abs_duties=(
            "ABS duties apply if wild-sourced biological resources are used. "
            "BD Amendment 2023 exempts cultivated ingredients from NBA prior approval."
        ),
        required_forms=[
            "Form 26-D (Proprietary ASU Drug Manufacturing Licence)",
            "GMP Certificate (AYUSH)",
            "AYUSH Product Approval (if making therapeutic claims)",
        ],
        approval_timeline="90–180 days (State Licensing + AYUSH Product Approval)",
        recommended_next_steps=[
            "Register trademark for brand name at IP India (Trade Marks Registry).",
            "Conduct freedom-to-operate analysis before launch.",
            "Obtain Form 26-D manufacturing licence from State AYUSH Directorate.",
            "Ensure advertising complies with AYUSH Advertising Guidelines 2023 (no false claims).",
            "Conduct TKDL search to confirm no prior-art issues.",
        ],
    )


# ---------------------------------------------------------------------------
# Multi-Step Wizard Engine
# ---------------------------------------------------------------------------

# Wizard step definitions — ordered sequence of questions
WIZARD_STEPS = [
    {
        "step": 1,
        "question": "Is the formulation derived from a classical Ayurvedic authoritative text listed in the First Schedule of the Drugs & Cosmetics Act? (e.g., Charaka Samhita, Sushruta Samhita, Bhavaprakasha, Ashtanga Hridayam)",
        "field": "from_first_schedule",
        "options": [
            {"value": "yes", "label": "Yes — the formula is from a First Schedule text"},
            {"value": "no",  "label": "No — it is a novel or proprietary formula"},
        ],
        "hint": "Classical formulations face a patent bar (Section 3(p)) but have TKDL protection.",
    },
    {
        "step": 2,
        "question": "What is the primary intended use of this product?",
        "field": "intended_use",
        "options": [
            {"value": "medicine",      "label": "Therapeutic medicine (treat/cure/prevent disease)"},
            {"value": "food",          "label": "Food / nutraceutical / dietary supplement"},
            {"value": "cosmetic",      "label": "Cosmetic (skin, hair, beauty application)"},
            {"value": "phyto",         "label": "Standardised plant extract / phytopharmaceutical"},
        ],
        "hint": "The intended use determines which regulatory authority (CDSCO/AYUSH/FSSAI/State FDA) governs your product.",
    },
    {
        "step": 3,
        "question": "Does the formulation contain any genuinely novel element — a new combination, novel process, purified active fraction, or new mechanism of action not documented in any existing Ayurvedic text or patent?",
        "field": "is_novel",
        "options": [
            {"value": "yes", "label": "Yes — there is a novel element with patent potential"},
            {"value": "no",  "label": "No — it is based on known ingredients/combinations"},
        ],
        "hint": "Novelty is required for patent protection. If no novel element, focus on trademark and trade-secret strategies.",
    },
    {
        "step": 4,
        "question": "How is the primary biological resource (plant/animal/microbial material) in your formulation sourced?",
        "field": "resource_source",
        "options": [
            {"value": "cultivated", "label": "Cultivated / farmed — grown under controlled conditions"},
            {"value": "wild",       "label": "Wild-collected — sourced from forests or natural habitats"},
            {"value": "synthetic",  "label": "Synthetic / lab-derived — no wild biological resource"},
        ],
        "hint": "Wild-sourced resources attract full ABS obligations under the Biological Diversity Act. Cultivated resources are largely exempt under the 2023 amendment.",
    },
    {
        "step": 5,
        "question": "What is the legal status of your entity?",
        "field": "entity_type",
        "options": [
            {"value": "indian",  "label": "Indian entity (Indian national / Indian company / Indian institution)"},
            {"value": "foreign", "label": "Foreign entity (foreign national / foreign company / joint venture with foreign majority)"},
        ],
        "hint": "Foreign entities require NBA prior approval for ANY access to Indian biological resources or associated traditional knowledge.",
    },
]


def get_wizard_step(step_number: int) -> dict:
    """Return the wizard step definition for the given step number (1-indexed)."""
    if step_number < 1 or step_number > len(WIZARD_STEPS):
        return {}
    return WIZARD_STEPS[step_number - 1]


def run_wizard_step(state: WizardState) -> WizardResponse:
    """
    Process the current wizard state and return:
      - If not all steps complete: the next question to ask
      - If all steps complete: the full classification result
    """
    answers = state.answers or {}
    current_step = state.current_step

    # Validate the current answer
    if current_step > len(WIZARD_STEPS):
        # All questions answered — compute classification
        from_first_schedule = answers.get("from_first_schedule", "no") == "yes"
        intended_use = answers.get("intended_use", "medicine").lower()
        is_novel = answers.get("is_novel", "no") == "yes"
        resource_source = answers.get("resource_source", "cultivated").lower()

        classification = _classify_by_answers(
            from_first_schedule=from_first_schedule,
            intended_use=intended_use,
            is_novel=is_novel,
            resource_source=resource_source,
        )

        return WizardResponse(
            is_complete=True,
            result=classification,
            next_step=None,
            total_steps=len(WIZARD_STEPS),
        )

    # Return the next question
    step_def = get_wizard_step(current_step)
    return WizardResponse(
        is_complete=False,
        result=None,
        next_step=step_def,
        total_steps=len(WIZARD_STEPS),
        current_step=current_step,
    )
