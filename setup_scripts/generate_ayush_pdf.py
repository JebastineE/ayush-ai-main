"""Generate a proper multi-page PDF for the AYUSH IP Guidelines corpus document."""
import sys
sys.path.insert(0, '.')

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMuPDF'])
    import fitz

from pathlib import Path

OUTPUT_PATH = Path("data/legal_corpus/ayush_ip_guidelines.pdf")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

PAGES = [
    # --- Page 1: Title page ---
    """AYUSH IP GUIDELINES
COMPREHENSIVE LEGAL FRAMEWORK FOR
TRADITIONAL KNOWLEDGE IP PROTECTION

Prepared by IP-SAKTI Sahayak Legal Research Division
Version 5.0 — 2024 Edition

This document provides a consolidated reference for intellectual property
protection, Access and Benefit Sharing (ABS) compliance, and regulatory
classification of Ayurvedic formulations under Indian and international law.

Contents:
Chapter 1: Patentability of Ayurvedic Formulations
Chapter 2: Access and Benefit Sharing (ABS) for Biological Resources
Chapter 3: Section 3(p) Traditional Knowledge Bar
Chapter 4: Classification of Ayurvedic Formulations
Chapter 5: International IP Treaties Relevant to Ayurveda""",

    # --- Page 2: Ashwagandha ---
    """CHAPTER 1: PATENTABILITY OF AYURVEDIC FORMULATIONS

1.1 Polyherbal Ashwagandha IP Viability Assessment

Ashwagandha (Withania somnifera) is one of the most commercially significant
herbs in the Ayurvedic pharmacopoeia. Its patentability under Indian law
requires careful analysis of several statutory provisions.

Under the Patents Act, 1970, Section 3(p), an invention which in effect is
traditional knowledge or which is an aggregation or duplication of known
properties of traditionally known component or components is NOT patentable.
This is the primary statutory bar against patenting traditional formulations.

However, a polyherbal formulation containing Ashwagandha CAN be patentable
if the following conditions are met:

(a) The formulation demonstrates a novel synergistic effect not predictable
    from the individual ingredients. For example, Ashwagandha combined with
    Brahmi and Shankhapushpi producing an enhanced nootropic effect that is
    quantifiably superior to any individual ingredient may constitute an
    inventive step under Section 2(1)(ja).

(b) The formulation uses a novel extraction method, novel bioavailability
    enhancement technique (such as nano-encapsulation or phytosome
    technology), or novel delivery system not part of traditional knowledge.

(c) The applicant demonstrates through clinical or pre-clinical data that
    the formulation has enhanced efficacy compared to traditional
    preparations, satisfying Section 3(d) requirements.""",

    # --- Page 3: Ashwagandha IP Strategy ---
    """1.2 IP Protection Strategy for Ashwagandha Products

Key Statutory References for Ashwagandha Patentability:
- Patents Act 1970, Section 3(d): Bars mere new forms of known substances
  unless enhanced efficacy is shown.
- Patents Act 1970, Section 3(p): Bars inventions that are traditional
  knowledge.
- Patents Act 1970, Section 2(1)(ja): Defines inventive step.
- Patents Act 1970, Section 2(1)(l): Defines novelty requirement.
- TKDL Database: Must be searched to ensure the formulation is not already
  documented as traditional knowledge.

Recommended IP Strategy for Ashwagandha Products:
- Patent Protection: Only for genuinely novel formulations with demonstrated
  enhanced efficacy (not traditional formulations).
- Trade Secret Protection: For proprietary extraction and standardization.
- Trademark Protection: For brand names associated with specific products.
- Geographical Indication: Nagori Ashwagandha from Rajasthan holds GI status.

Risk Assessment:
Filing a patent for a traditional Ashwagandha formulation carries HIGH RISK
of rejection under Section 3(p). The TKDL database contains extensive records
of Ashwagandha-based formulations from classical texts including Charaka
Samhita, Bhavaprakasha, and Ashtanga Hridaya.""",

    # --- Page 4: ABS Cultivated Turmeric ---
    """CHAPTER 2: ACCESS AND BENEFIT SHARING (ABS) FOR BIOLOGICAL RESOURCES

2.1 Cultivated Turmeric Export — ABS Compliance Check

Turmeric (Curcuma longa) is both a biological resource and a medicinal plant
extensively used in Ayurveda. Any entity seeking to use or export
turmeric-based products must comply with the Biological Diversity Act, 2002
and the Biological Diversity Rules, 2024.

FOR INDIAN ENTITIES USING CULTIVATED TURMERIC:
Under the 2024 Biological Diversity Rules, Section 7, Indian entities using
CULTIVATED biological resources (including cultivated turmeric) are EXEMPT
from requiring prior approval from the National Biodiversity Authority (NBA).

Requirements:
- File prior intimation with the State Biodiversity Board (SBB) at least
  15 days before commencing commercial utilization.
- Use BMC Form 1 for this intimation.
- Ensure benefit-sharing payments through the ABS mechanism if using the
  resource for commercial purposes.
- Timeline: 15-day prior intimation period only.

FOR FOREIGN ENTITIES SEEKING TO USE INDIAN TURMERIC:
Foreign entities MUST obtain prior approval from the National Biodiversity
Authority (NBA) under Section 3 of the Biological Diversity Act, 2002.

Requirements:
- Filing Form I (Application for access to biological resources) with NBA.
- Detailed research proposal and benefit-sharing agreement.
- NBA Section 3 approval is mandatory.
- Required Forms: Form I (NBA Application), Form III (Transfer Agreement).
- Timeline: 90-180 days for NBA approval.
- Non-compliance penalties: Up to 5 years imprisonment and Rs. 10 lakh fine
  under Section 55 of the Biological Diversity Act.""",

    # --- Page 5: Wild vs Cultivated ---
    """2.2 Wild vs. Cultivated Resource Distinction

The 2024 BD Rules make a critical distinction:
- CULTIVATED resources grown in agricultural settings are subject to
  simplified compliance (BMC intimation only).
- WILD resources collected from natural habitats require full NBA/SBB
  approval processes.
- The burden of proof for establishing "cultivated" status lies with the
  applicant.

2.3 Benefit Sharing Mechanisms

Under the BD Act 2002 and 2024 Rules:
- Benefit sharing is determined by the NBA based on Mutually Agreed Terms.
- For commercial utilization, monetary benefits are typically 1-5% of the
  purchase price or 0.1-0.5% of the annual gross ex-factory sale price.
- Non-monetary benefits may include technology transfer, joint ventures,
  and capacity building.
- All benefit-sharing arrangements must be deposited with the National
  Biodiversity Fund or Local Biodiversity Fund as applicable.""",

    # --- Page 6: Section 3(p) ---
    """CHAPTER 3: SECTION 3(p) TRADITIONAL KNOWLEDGE BAR

3.1 Understanding Section 3(p) of the Patents Act, 1970

Section 3(p) was inserted by the Patents (Amendment) Act, 2005 and states:

"An invention which, in effect, is traditional knowledge or which is an
aggregation or duplication of known properties of traditionally known
component or components, is not an invention within the meaning of this Act."

This provision is India's primary statutory defense against biopiracy and
misappropriation of traditional knowledge. It has been used to successfully
challenge several international patent applications on traditional Indian
medicines.

3.2 Key Case Studies Under Section 3(p)

Case 1 - Turmeric Patent (USPTO Patent No. 5,401,504):
The University of Mississippi Medical Center was granted a US patent for
"Use of Turmeric in Wound Healing" in 1995. India's CSIR challenged this
patent, demonstrating that turmeric's wound-healing properties were
documented in ancient Ayurvedic texts. The USPTO revoked the patent in 1997.

Case 2 - Neem Patent (European Patent No. 0436257):
W.R. Grace Company and USDA were granted a European patent for controlling
fungi using neem extract. India challenged this in 2000, citing traditional
knowledge. The EPO revoked the patent in 2005 after a 10-year legal battle.

Case 3 - Basmati Rice Patent (USPTO Patent No. 5,663,484):
RiceTec Inc. obtained a US patent covering Basmati rice lines. India
challenged multiple claims, and several were struck down.""",

    # --- Page 7: TKDL ---
    """3.3 TKDL as a Defensive Tool Against Section 3(p) Violations

The Traditional Knowledge Digital Library (TKDL) was created specifically
to prevent biopiracy by documenting traditional Indian knowledge in a
patent-examiner accessible format. As of 2024:

- TKDL contains over 4.5 lakh formulations from Ayurveda, Unani, Siddha,
  and Yoga texts.
- It has been instrumental in challenging over 200 patent applications
  globally.
- TKDL access agreements exist with patent offices in the US, EU, UK,
  Japan, Australia, and others.
- TKDL documentation serves as prior art evidence under Section 3(p).

3.4 Practical Implications for Patent Applicants

If you are filing a patent for an Ayurvedic or traditional medicine:
1. Conduct a TKDL search before filing to ensure your formulation is not
   already documented.
2. Clearly demonstrate what aspect of your invention goes BEYOND
   traditional knowledge.
3. Provide data showing enhanced efficacy, novel mechanism, or genuinely
   novel composition.
4. Be prepared for Section 3(p) objections during patent examination.
5. Document all experimental evidence of novelty and inventive step.""",

    # --- Page 8: Classification ---
    """CHAPTER 4: CLASSIFICATION OF AYURVEDIC FORMULATIONS

4.1 Classical vs. Proprietary Ayurvedic Medicines

Classical Ayurvedic Medicine:
- Formulations documented in authoritative texts listed in the First
  Schedule of the Drugs and Cosmetics Act (e.g., Charaka Samhita,
  Sushruta Samhita, Bhavaprakasha, Sharangadhara Samhita).
- Do NOT require individual product licensing; manufactured under a
  general manufacturing license.
- Must follow exact composition, method of preparation, and dosage as
  described in the classical text.

Proprietary Ayurvedic Medicine:
- Novel formulations not found in classical texts.
- Require specific product approval and licensing under the Drugs and
  Cosmetics Act.
- Must undergo safety and efficacy testing as prescribed by AYUSH
  Ministry guidelines.

4.2 Ayurveda Aahar Classification (FSSAI 2022)

Under the Food Safety and Standards (Ayurveda Aahara) Regulations, 2022:
- Products intended for dietary/food use that incorporate Ayurvedic
  ingredients are classified as "Ayurveda Aahar."
- Regulated by FSSAI, NOT by AYUSH/CDSCO drug regulators.
- Products must contain only ingredients from the approved list.
- Labels must include "This is not a medicinal product."
- FSSAI licensing and registration requirements apply.""",

    # --- Page 9: International Treaties ---
    """CHAPTER 5: INTERNATIONAL IP TREATIES RELEVANT TO AYURVEDA

5.1 WIPO Treaty on IP, Genetic Resources and Associated TK (GRATK, 2024)

The WIPO Diplomatic Conference in May 2024 adopted the GRATK Treaty:
- Requires patent applicants to disclose the country of origin of
  genetic resources used in inventions.
- Requires disclosure of traditional knowledge associated with genetic
  resources.
- Strengthens India's position in defending against biopiracy.
- Expected to come into force after ratification by 15 member states.

5.2 Nagoya Protocol on ABS

The Nagoya Protocol (effective October 2014) establishes:
- Prior Informed Consent (PIC) requirement for access to genetic resources.
- Mutually Agreed Terms (MAT) for benefit-sharing.
- Compliance measures that member states must implement.
- India ratified the Nagoya Protocol and implemented it through the BD Act
  2002 and BD Rules.

5.3 TRIPS Agreement and Traditional Knowledge

Article 27.3(b) of TRIPS allows member states to exclude plants, animals,
and biological processes from patentability. India uses this flexibility:
- Section 3(j): Excludes plants and animals from patentability.
- Section 3(p): Excludes traditional knowledge from patentability.
- Section 3(d): Prevents evergreening of patents on known substances.""",
]


def generate_pdf():
    doc = fitz.open()

    for i, page_text in enumerate(PAGES):
        page = doc.new_page(width=612, height=792)  # US Letter

        # Title formatting for first line
        lines = page_text.strip().split('\n')

        y = 50
        for line in lines:
            stripped = line.strip()
            if not stripped:
                y += 8
                continue

            # Determine font size
            if stripped.startswith("CHAPTER") or stripped.startswith("AYUSH IP GUIDELINES"):
                fontsize = 14
                fontname = "helv"
            elif stripped.startswith(("1.", "2.", "3.", "4.", "5.")) and len(stripped) < 80:
                fontsize = 12
                fontname = "helv"
            else:
                fontsize = 10
                fontname = "helv"

            # Word-wrap at ~85 chars
            max_chars = 80
            while len(stripped) > max_chars:
                wrap_at = stripped.rfind(' ', 0, max_chars)
                if wrap_at == -1:
                    wrap_at = max_chars
                page.insert_text(
                    fitz.Point(50, y),
                    stripped[:wrap_at],
                    fontsize=fontsize,
                    fontname=fontname,
                )
                stripped = stripped[wrap_at:].strip()
                y += fontsize + 4
            if stripped:
                page.insert_text(
                    fitz.Point(50, y),
                    stripped,
                    fontsize=fontsize,
                    fontname=fontname,
                )
                y += fontsize + 4

            if y > 730:
                break

    doc.save(str(OUTPUT_PATH))
    doc.close()
    print(f"[OK] Generated {len(PAGES)}-page PDF at: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_pdf()
