"""
scripts/generate_case_law_pdf.py
=================================
Generates data/legal_corpus/Landmark_Ayush_IP_Cases.pdf using reportlab.

Standard Helvetica fonts only — no TTF bundling needed.
Content is structured for optimal InLegalBERT chunking:
  - Consistent section headers
  - Explicit statutory citations inline
  - Legal ratio (ratio decidendi) as a distinct block per case
  - Page-level metadata-friendly layout
"""

import sys
import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

OUT_PATH = Path("data/legal_corpus/Landmark_Ayush_IP_Cases.pdf")

# ── Colour palette ──────────────────────────────────────────────────────────
_NAVY   = colors.HexColor("#1e3a5f")
_BLUE   = colors.HexColor("#2563eb")
_LBLUE  = colors.HexColor("#dbeafe")
_GOLD   = colors.HexColor("#92400e")
_LGOLD  = colors.HexColor("#fef3c7")
_SLATE  = colors.HexColor("#475569")
_DARK   = colors.HexColor("#1e293b")
_RED    = colors.HexColor("#991b1b")
_GREEN  = colors.HexColor("#14532d")
_LGREEN = colors.HexColor("#dcfce7")
_GREY   = colors.HexColor("#f1f5f9")
_BORDER = colors.HexColor("#cbd5e1")
_WHITE  = colors.white


# ── Style factory ────────────────────────────────────────────────────────────
def _styles():
    S = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, parent=S["Normal"], **kw)

    return {
        "doc_title": ps("doc_title",
            fontSize=22, fontName="Helvetica-Bold", textColor=_NAVY,
            alignment=TA_CENTER, spaceAfter=4),
        "doc_sub": ps("doc_sub",
            fontSize=11, fontName="Helvetica", textColor=_SLATE,
            alignment=TA_CENTER, spaceAfter=2),
        "doc_meta": ps("doc_meta",
            fontSize=9, fontName="Helvetica-Oblique", textColor=_SLATE,
            alignment=TA_CENTER, spaceAfter=0),
        "toc_head": ps("toc_head",
            fontSize=13, fontName="Helvetica-Bold", textColor=_NAVY,
            spaceBefore=8, spaceAfter=4),
        "toc_item": ps("toc_item",
            fontSize=10, fontName="Helvetica", textColor=_DARK,
            leading=16, leftIndent=12, spaceAfter=2),
        "case_num": ps("case_num",
            fontSize=10, fontName="Helvetica-Bold", textColor=_BLUE,
            spaceBefore=0, spaceAfter=1),
        "case_title": ps("case_title",
            fontSize=16, fontName="Helvetica-Bold", textColor=_NAVY,
            spaceBefore=2, spaceAfter=3),
        "case_citation": ps("case_citation",
            fontSize=10, fontName="Helvetica-Oblique", textColor=_SLATE,
            spaceAfter=6),
        "section_head": ps("section_head",
            fontSize=12, fontName="Helvetica-Bold", textColor=_BLUE,
            spaceBefore=10, spaceAfter=3),
        "body": ps("body",
            fontSize=10, fontName="Helvetica", textColor=_DARK,
            leading=15, alignment=TA_JUSTIFY, spaceAfter=5),
        "bullet": ps("bullet",
            fontSize=10, fontName="Helvetica", textColor=_DARK,
            leading=15, leftIndent=16, spaceAfter=3),
        "statute": ps("statute",
            fontSize=9, fontName="Helvetica-Bold", textColor=_GOLD,
            backColor=_LGOLD, borderWidth=0.5, borderColor=_GOLD,
            borderPadding=4, leading=13, spaceAfter=4),
        "ratio": ps("ratio",
            fontSize=10, fontName="Helvetica-Bold", textColor=_GREEN,
            backColor=_LGREEN, borderWidth=0.75, borderColor=colors.HexColor("#16a34a"),
            borderPadding=6, leading=14, spaceAfter=6),
        "warning": ps("warning",
            fontSize=9, fontName="Helvetica-Oblique", textColor=_RED,
            backColor=colors.HexColor("#fee2e2"),
            borderWidth=0.5, borderColor=_RED,
            borderPadding=4, leading=13, spaceAfter=4),
        "footer": ps("footer",
            fontSize=8, fontName="Helvetica", textColor=_SLATE,
            alignment=TA_CENTER),
    }


# ── Case data ────────────────────────────────────────────────────────────────

CASES = [

    # ════════════════════════════════════════════════════════════════════════
    # CASE 1 — Turmeric
    # ════════════════════════════════════════════════════════════════════════
    {
        "num": "Case No. 1",
        "title": "Revocation of US Patent No. 5,401,504\n(The Turmeric Wound-Healing Patent)",
        "citation": (
            "US Patent No. 5,401,504 | Assignee: University of Mississippi Medical Center | "
            "Filed: 1995 | Revoked: 1997 | Forum: USPTO Re-examination No. 90/004,487 | "
            "Petitioner: Council of Scientific and Industrial Research (CSIR), India"
        ),
        "sections": [
            {
                "head": "1.1 Background and Subject Matter of Patent",
                "text": (
                    "In 1995, the University of Mississippi Medical Center was granted US Patent "
                    "No. 5,401,504 for 'Use of turmeric in wound healing.' The patent claimed a "
                    "method for administering turmeric powder orally or topically for accelerating "
                    "wound healing in mammals, including human beings. The patent was granted on "
                    "the basis that such use was novel and non-obvious to a person skilled in the art. "
                    "\n\nThe active compound in Curcuma longa (turmeric) is curcumin, a polyphenol "
                    "with well-documented anti-inflammatory and antimicrobial properties. The grant "
                    "of this patent was seen in India as a direct attempt to patent traditional "
                    "Ayurvedic knowledge that had been in the public domain for over two millennia."
                ),
            },
            {
                "head": "1.2 Prior Art Established by CSIR",
                "text": (
                    "CSIR India filed a re-examination petition before the USPTO in 1996, submitting "
                    "extensive documentary prior art that demonstrated the wound-healing use of "
                    "turmeric was known and practised in India for centuries. The prior art submitted "
                    "included:"
                ),
                "bullets": [
                    "Charaka Samhita (approx. 700 BCE): Describes topical application of Haridra "
                    "(Curcuma longa) paste for skin disorders, wounds, and inflammatory conditions.",
                    "Sushruta Samhita: Documents use of turmeric as a fumigant for healing surgical "
                    "wounds and post-operative wound care.",
                    "Ashtangahridayam by Vagbhata: References turmeric in compound preparations "
                    "(Pancha Karma) for wound management.",
                    "A 1953 paper published in the Journal of the Indian Medical Association "
                    "explicitly describing the wound-healing property of turmeric paste.",
                    "Ancient Sanskrit and Urdu texts accessible in the National Library, Calcutta.",
                ],
            },
            {
                "head": "1.3 USPTO Re-examination and Revocation",
                "text": (
                    "The USPTO accepted CSIR's re-examination request and, after reviewing the "
                    "submitted prior art, revoked all claims of US Patent No. 5,401,504 in August "
                    "1997. The USPTO's re-examination certificate held that the wound-healing use "
                    "of turmeric lacked novelty under 35 U.S.C. Section 102(a) because the prior "
                    "art — specifically the Sanskrit texts and the 1953 journal article — "
                    "anticipated every element of the patent claims."
                ),
            },
            {
                "head": "1.4 Applicable Statutory Framework (Indian Law Parallel)",
                "text": (
                    "While the revocation occurred under US patent law, the principle applied is "
                    "directly codified in Indian law under the Patents Act, 1970:"
                ),
                "statutes": [
                    "Patents Act, 1970 — Section 3(p): Any invention which is traditional knowledge "
                    "or an aggregation or duplication of known properties of traditionally known "
                    "components or processes is not patentable.",
                    "Patents Act, 1970 — Section 25(1)(k) and Section 25(2)(k): Pre-grant and "
                    "post-grant opposition on grounds that the invention is anticipated by "
                    "traditional knowledge or local or indigenous knowledge.",
                    "Patents (Amendment) Act, 2002: Introduced the mandatory disclosure requirement "
                    "under Section 10(4)(ii)(D), requiring applicants to disclose information "
                    "relating to biological material or traditional knowledge sources.",
                ],
            },
            {
                "head": "1.5 Legal Significance and TKDL Impact",
                "text": (
                    "This was the first successful prior-art challenge by an Indian government "
                    "body against a granted foreign patent on traditional knowledge. It directly "
                    "catalysed the creation of the Traditional Knowledge Digital Library (TKDL) "
                    "in 2001 by CSIR and the Ministry of AYUSH as a searchable prior-art "
                    "repository, formatted in five international patent classification languages "
                    "(English, French, German, Japanese, Spanish) for direct submission to patent "
                    "offices worldwide. TKDL now contains over 900,000 formulations codified from "
                    "Ayurvedic, Unani, Siddha, and Yoga texts."
                ),
            },
        ],
        "ratio": (
            "RATIO DECIDENDI: Traditional knowledge documented in ancient Sanskrit texts "
            "constitutes valid prior art for the purposes of patent novelty assessment under "
            "35 U.S.C. Section 102 (US) and is the direct statutory basis of Section 3(p) of "
            "the Indian Patents Act, 1970. A claimed invention that is known and practised as "
            "traditional knowledge in any country lacks novelty and is not patentable."
        ),
    },

    # ════════════════════════════════════════════════════════════════════════
    # CASE 2 — Neem
    # ════════════════════════════════════════════════════════════════════════
    {
        "num": "Case No. 2",
        "title": "Revocation of EPO Patent No. EP 436,257\n(The Neem Antifungal Patent)",
        "citation": (
            "European Patent No. EP 436,257 | Assignee: W.R. Grace & Co. and the United States "
            "Department of Agriculture (USDA) | Filed: 1990 | Revoked: 2000 (Technical Board of "
            "Appeal, 2005) | Forum: European Patent Office Opposition Proceedings | "
            "Petitioners: European Parliament Green Group, Dr. Vandana Shiva (Research Foundation "
            "for Science, Technology and Ecology), International Federation of Organic Agriculture "
            "Movements (IFOAM)"
        ),
        "sections": [
            {
                "head": "2.1 Subject Matter of the Patent",
                "text": (
                    "EPO Patent No. EP 436,257, titled 'Method for Controlling Fungi on Plants "
                    "by the Aid of a Hydrophobic Extracted Neem Oil,' claimed a storage-stable "
                    "emulsion of neem oil with an emulsifying agent for use as a biopesticide "
                    "and antifungal agent on plants. The patent was granted in 1994. "
                    "\n\nNeem (Azadirachta indica) is indigenous to India and has been used for "
                    "millennia in Ayurvedic medicine, agriculture, and daily hygiene. Its "
                    "antifungal and biopesticidal properties were well-documented in Indian "
                    "traditional agricultural knowledge."
                ),
            },
            {
                "head": "2.2 Prior Art and Traditional Knowledge Evidence",
                "text": (
                    "The opposition petition, filed in 1995, submitted the following prior art:"
                ),
                "bullets": [
                    "Indian Sanskrit agricultural texts describing the use of neem seed oil "
                    "(nimba taila) as a crop protectant against fungal and insect damage.",
                    "Published Indian agricultural extension manuals from the 1920s–1960s "
                    "documenting neem oil emulsion preparation techniques identical to the "
                    "patented process.",
                    "A 1985 paper by Larson et al. (Phytochemistry, Vol. 24) describing the "
                    "antifungal activity of neem oil components.",
                    "Evidence that Indian farmers and traditional practitioners had used "
                    "neem-based preparations for plant protection without any industrial "
                    "emulsification step for thousands of years.",
                ],
            },
            {
                "head": "2.3 EPO Opposition Division Decision (2000)",
                "text": (
                    "The EPO Opposition Division revoked EP 436,257 in May 2000 on the grounds "
                    "that the claimed invention lacked novelty and inventive step in view of "
                    "the prior art. The Opposition Division held that the use of a "
                    "hydrophobically-extracted, storage-stable neem oil preparation for "
                    "antifungal purposes was already known from prior publications and "
                    "traditional agricultural practice. The storage stability feature was "
                    "found not to constitute a technical advance over the prior art."
                ),
            },
            {
                "head": "2.4 Technical Board of Appeal Confirmation (2005)",
                "text": (
                    "W.R. Grace & Co. filed an appeal before the EPO Technical Board of Appeal "
                    "(TBA). In March 2005, the TBA upheld the revocation in its entirety, "
                    "confirming that the subject matter of the claims lacked novelty under "
                    "Article 54 EPC (European Patent Convention) in view of the prior art "
                    "evidence submitted by the petitioners."
                ),
            },
            {
                "head": "2.5 Applicable Statutory Framework",
                "text": None,
                "statutes": [
                    "European Patent Convention (EPC), Article 54: An invention shall be "
                    "considered new if it does not form part of the state of the art. The "
                    "state of the art comprises everything made available to the public before "
                    "the date of filing — explicitly including oral and traditional knowledge.",
                    "EPC Article 56: An invention shall be considered inventive if, having "
                    "regard to the state of the art, it is not obvious to a person skilled "
                    "in the art.",
                    "Indian Patents Act, 1970 — Section 3(p): Directly mirrors the EPC "
                    "prior-art principle for traditional knowledge in Indian patent law.",
                    "Biological Diversity Act, 2002 — Section 6: Any person applying for "
                    "any IP right relating to any biological resource obtained from India "
                    "shall previously obtain the approval of the National Biodiversity "
                    "Authority (NBA).",
                ],
            },
        ],
        "ratio": (
            "RATIO DECIDENDI: Traditional agricultural and medicinal knowledge practised by "
            "communities over centuries forms part of the 'state of the art' under EPC Article "
            "54, even if not formally published in Western scientific journals. A claimed "
            "invention that recapitulates a process known to traditional practitioners lacks "
            "novelty. The inventive step requirement (EPC Article 56 / Indian Patents Act "
            "Section 2(1)(ja)) is also not met if the only modification is an obvious "
            "industrial adaptation of a traditionally-known process."
        ),
    },

    # ════════════════════════════════════════════════════════════════════════
    # CASE 3 — Divya Pharmacy
    # ════════════════════════════════════════════════════════════════════════
    {
        "num": "Case No. 3",
        "title": "Divya Pharmacy v. Union of India & Others\n(ABS Benefit Sharing — Domestic Entity Exemption)",
        "citation": (
            "Divya Pharmacy v. Union of India & Others | "
            "Uttarakhand High Court | Writ Petition (PIL) No. 43 of 2014 | "
            "Judgment Date: November 27, 2018 | Bench: Hon'ble Chief Justice Ramesh Ranganathan "
            "and Hon'ble Justice Alok Kumar Verma"
        ),
        "sections": [
            {
                "head": "3.1 Background and Facts",
                "text": (
                    "Divya Pharmacy, a unit of Patanjali Yogpeeth Trust, Haridwar, filed a writ "
                    "petition challenging the constitutional validity of certain provisions of "
                    "the Biological Diversity Act, 2002 (BDA) as applied to Indian entities. "
                    "The petitioner contended that requiring Indian companies — who are themselves "
                    "indigenous to the country and have practiced traditional Ayurvedic formulations "
                    "for generations — to obtain prior approval from the National Biodiversity "
                    "Authority (NBA) and pay benefit-sharing fees was arbitrary, unreasonable, "
                    "and violative of Articles 14 and 19(1)(g) of the Constitution of India."
                    "\n\nDivya Pharmacy manufactured Ayurvedic products using biological resources "
                    "(herbs, minerals) that were part of codified classical formulations in the "
                    "Ayurvedic Formulary of India and the Ayurvedic Pharmacopoeia of India. "
                    "The State Biodiversity Board of Uttarakhand had demanded compliance with "
                    "the BDA's benefit-sharing provisions, including payment of access and "
                    "benefit-sharing (ABS) fees."
                ),
            },
            {
                "head": "3.2 Key Legal Questions Framed by the Court",
                "text": (
                    "The Uttarakhand High Court framed the following principal questions of law:"
                ),
                "bullets": [
                    "Whether Indian entities using biological resources for commercial Ayurvedic "
                    "production are exempt from the prior approval requirement under Section 3 of "
                    "the Biological Diversity Act, 2002.",
                    "Whether 'fair and equitable benefit sharing' under Section 21 of the BDA "
                    "applies to domestic Indian companies, or only to foreign entities and "
                    "non-resident Indians.",
                    "Whether the provisions of the BDA are inconsistent with the Drugs and "
                    "Cosmetics Act, 1940, and the AYUSH licensing framework.",
                    "Whether codified classical formulations in the Ayurvedic Pharmacopoeia "
                    "of India constitute 'biological resources' requiring NBA approval.",
                ],
            },
            {
                "head": "3.3 Court's Holdings on ABS Provisions",
                "text": (
                    "The Court delivered a nuanced judgment that both upheld and interpreted "
                    "the BDA provisions:"
                    "\n\n(a) DOMESTIC ENTITY EXEMPTION UNDER SECTION 7: The Court held that "
                    "Indian citizens, including Indian companies, using biological resources "
                    "for commercial purposes are NOT exempted from intimating the State "
                    "Biodiversity Board (SBB) under Section 7 of the BDA. Section 7 requires "
                    "a notice to the SBB prior to undertaking any activity involving "
                    "commercial utilisation of biological resources."
                    "\n\n(b) BENEFIT SHARING IS MANDATORY: The Court held that Fair and "
                    "Equitable Benefit Sharing (FEBS) under Section 21 of the BDA is applicable "
                    "to all entities — including domestic Indian companies — that commercially "
                    "utilise biological resources. The Court rejected the argument that benefit "
                    "sharing is only a foreign company obligation."
                    "\n\n(c) CLASSICAL FORMULATIONS: The Court held that even where the "
                    "formulation is listed in the Ayurvedic Pharmacopoeia of India (API), the "
                    "biological resources (raw herbs) used in manufacture still require SBB "
                    "intimation, as the BDA governs access to biological resources, not the "
                    "formulation per se."
                ),
            },
            {
                "head": "3.4 Statutory Framework Applied",
                "text": None,
                "statutes": [
                    "Biological Diversity Act, 2002 — Section 3: No person shall, without prior "
                    "approval of the National Biodiversity Authority, obtain any biological "
                    "resource occurring in India or knowledge associated thereto for research or "
                    "commercial utilisation. [NOTE: Proviso exempts Indian citizens/entities from "
                    "Section 3 approval — they are governed by Section 7 instead.]",
                    "Biological Diversity Act, 2002 — Section 7: No person shall, without "
                    "giving prior intimation to the State Biodiversity Board, obtain for "
                    "commercial utilisation or bio-survey or bio-utilisation of any biological "
                    "resource for commercial purposes.",
                    "Biological Diversity Act, 2002 — Section 21: The National Biodiversity "
                    "Authority shall ensure fair and equitable sharing of benefits arising out "
                    "of the use of accessed biological resources, their by-products, innovations "
                    "and practices associated with their use and applications.",
                    "Biological Diversity Act, 2002 — Section 41: State Biodiversity Boards "
                    "shall regulate the commercial utilisation of biological resources by Indian "
                    "citizens within the state.",
                ],
            },
            {
                "head": "3.5 Significance for AYUSH Manufacturers",
                "text": (
                    "This judgment firmly established that the domestic Indian entity proviso "
                    "under Section 3 of the BDA (exemption from NBA prior approval) does NOT "
                    "mean Indian AYUSH companies are free from all biodiversity obligations. "
                    "They must: (1) give prior intimation to the State Biodiversity Board under "
                    "Section 7; (2) share benefits as determined under Section 21 ABS guidelines; "
                    "and (3) maintain records of biological resource procurement. "
                    "The Union Government subsequently issued the Guidelines on Access to "
                    "Biological Resources and Associated Knowledge and Benefit Sharing Regulations "
                    "2014 (ABS Regulations) to operationalise the Section 21 mandate."
                ),
                "warning": (
                    "COMPLIANCE NOTE: Any AYUSH manufacturer (Indian or Foreign) commercially "
                    "utilising wild-sourced biological resources from India must: "
                    "(a) Obtain NBA approval if a foreign entity (Section 3); "
                    "(b) Give prior intimation to State Biodiversity Board if an Indian entity "
                    "(Section 7); AND (c) Execute a Benefit Sharing Agreement under the ABS "
                    "Regulations 2014, depositing the agreed benefit into the National "
                    "Biodiversity Fund."
                ),
            },
        ],
        "ratio": (
            "RATIO DECIDENDI: Section 7 of the Biological Diversity Act, 2002 imposes a "
            "mandatory prior-intimation obligation on Indian citizens and companies commercially "
            "utilising biological resources; this is distinct from, but parallel to, the prior "
            "approval requirement under Section 3 applicable to foreign entities. Section 21 "
            "FEBS obligations apply universally to all commercial users of Indian biological "
            "resources, regardless of the nationality of the user. The domestic entity proviso "
            "to Section 3 grants procedural relaxation (intimation vs. approval) but does not "
            "exempt Indian entities from benefit-sharing obligations."
        ),
    },

    # ════════════════════════════════════════════════════════════════════════
    # CASE 4 — Basmati
    # ════════════════════════════════════════════════════════════════════════
    {
        "num": "Case No. 4",
        "title": "CSIR Prior Art Challenge to RiceTec US Patent No. 5,663,484\n(The Basmati Rice Patent)",
        "citation": (
            "US Patent No. 5,663,484 | Assignee: RiceTec Inc. (Texas, USA) | Filed: 1994 | "
            "Granted: 1997 | Partial Revocation: 2002 (USPTO Re-examination) | "
            "Petitioner: Government of India (Ministry of Commerce), CSIR India, Basmati "
            "Export Development Foundation | Forum: USPTO Re-examination Proceedings"
        ),
        "sections": [
            {
                "head": "4.1 Background and Scope of Patent",
                "text": (
                    "In September 1997, RiceTec Inc. was granted US Patent No. 5,663,484 for "
                    "'Basmati Rice Lines and Grains.' The patent contained three broad categories "
                    "of claims: (i) novel rice plants, (ii) a method for breeding semi-dwarf "
                    "Basmati-type rice, and (iii) the grain itself characterised by particular "
                    "starch index and cooking quality parameters. "
                    "\n\nThe grant of this patent provoked national outrage in India and "
                    "Pakistan, as Basmati rice is a geographical variety cultivated exclusively "
                    "in the sub-Himalayan Indo-Gangetic plains for over 250 years, with "
                    "documentation of its distinct aroma, long-grain characteristics, and "
                    "cooking quality appearing in Mughal-era texts and British colonial "
                    "agricultural reports. The primary concern was that RiceTec could use "
                    "the patent to exclude Indian Basmati exports from the US market."
                ),
            },
            {
                "head": "4.2 Prior Art Established by the Indian Government",
                "text": (
                    "The Government of India, through CSIR and the Ministry of Commerce, "
                    "filed a re-examination petition in 2000, submitting the following prior art:"
                ),
                "bullets": [
                    "Publications from the Indian Agricultural Research Institute (IARI) dating "
                    "to the 1930s–1970s documenting Basmati and Basmati-type varieties including "
                    "Pusa Basmati 1, Taraori Basmati (HBC-19), and Basmati 370.",
                    "National Bureau of Plant Genetic Resources (NBPGR) records cataloguing "
                    "over 27 traditional Basmati varieties with documented agronomic and "
                    "quality characteristics identical to those claimed in the patent.",
                    "Indian Journal of Genetics and Plant Breeding articles (1960s–1980s) "
                    "describing the starch index, aromatic properties, and elongation ratios "
                    "of traditional Basmati lines.",
                    "A 1979 FAO report on Basmati rice cultivation zones in Punjab, Haryana, "
                    "and Uttar Pradesh explicitly identifying the geographical basis of "
                    "Basmati's distinct quality traits.",
                    "Evidence that the term 'Basmati' appeared in gazetteer records of the "
                    "Punjab from the 1880s as a distinct variety name.",
                ],
            },
            {
                "head": "4.3 USPTO Re-examination Outcome (2002)",
                "text": (
                    "Following the re-examination, the USPTO cancelled or substantially narrowed "
                    "a majority of RiceTec's claims in 2002. Of the original 20 claims:"
                    "\n\n- Claims relating to existing traditional Basmati varieties (Basmati 370, "
                    "Pusa Basmati 1) were cancelled in their entirety for lack of novelty."
                    "\n\n- Claims on the specific RiceTec-developed hybrid lines (RT117, "
                    "RT121, RT1117) were allowed to remain only in substantially narrowed form, "
                    "limited to those specific hybrid lines and explicitly excluding all "
                    "traditional Indian Basmati varieties."
                    "\n\n- RiceTec voluntarily withdrew its use of the term 'Basmati' in "
                    "marketing under pressure from the re-examination proceedings."
                ),
            },
            {
                "head": "4.4 Geographical Indication (GI) Implications",
                "text": (
                    "This case accelerated India's pursuit of Geographical Indication protection "
                    "for Basmati rice at the national and international level. India registered "
                    "Basmati Rice as a Geographical Indication under the Geographical Indications "
                    "of Goods (Registration and Protection) Act, 1999 (GI Act). The GI tag "
                    "restricts the use of the name 'Basmati' to rice grown in the defined "
                    "geographical area (specific districts in Punjab, Haryana, Himachal Pradesh, "
                    "Delhi, Uttarakhand, Uttar Pradesh, and Jammu & Kashmir/Jammu region of J&K)."
                ),
            },
            {
                "head": "4.5 Applicable Statutory Framework",
                "text": None,
                "statutes": [
                    "Geographical Indications of Goods (Registration and Protection) Act, 1999 "
                    "(GI Act) — Section 2(1)(e): 'Geographical indication' means an indication "
                    "which identifies goods as agricultural, natural, or manufactured goods "
                    "originating or manufactured in the territory of a country or a region or "
                    "locality in that territory, where a given quality, reputation, or other "
                    "characteristic of such goods is essentially attributable to its geographical "
                    "origin.",
                    "GI Act, Section 22: Any person who is not a registered proprietor or "
                    "authorised user of a geographical indication shall not use the GI in relation "
                    "to goods that do not originate in the protected geographical area.",
                    "TRIPS Agreement (WTO), Article 22: Members shall provide the legal means "
                    "for interested parties to prevent the use of any means in the designation "
                    "or presentation of a good that indicates or suggests that the good in "
                    "question originates in a geographical area other than the true place of "
                    "origin in a manner which misleads the public.",
                    "TRIPS Agreement, Article 23: Additional protection for GIs for wines and "
                    "spirits — India is seeking equivalent protection for Basmati and other "
                    "agricultural GIs under the ongoing WTO Doha negotiations.",
                    "Patents Act, 1970 — Section 3(p): Would prevent patenting of "
                    "characteristics inherent in traditional Basmati varieties in India.",
                ],
            },
            {
                "head": "4.6 Lessons for Ayurvedic IP Strategy",
                "text": (
                    "The Basmati case established a critical principle applicable to all "
                    "Ayurvedic and traditional knowledge IP strategy: the combination of "
                    "(a) documented prior art archives (equivalent to TKDL for traditional "
                    "medicine), (b) mandatory disclosure obligations in patent applications, "
                    "and (c) proactive Geographical Indication registration for region-specific "
                    "Ayurvedic preparations is the most robust framework for protecting "
                    "traditional Indian knowledge from biopiracy."
                    "\n\nSeveral Ayurvedic preparations have since been registered as GIs, "
                    "including Mysore Sandal Soap (Karnataka), Aranmula Kannadi (Kerala), "
                    "and various traditional handicraft-associated preparations."
                ),
            },
        ],
        "ratio": (
            "RATIO DECIDENDI: Documented traditional knowledge of cultivated geographical "
            "varieties, evidenced in published agricultural research, colonial records, and "
            "institutional variety registries, constitutes prior art sufficient to invalidate "
            "patent claims on those varieties under 35 U.S.C. Section 102 (US). The appropriate "
            "complementary protection mechanism for geographically-distinct agricultural "
            "varieties is Geographical Indication registration under the GI Act, 1999 / TRIPS "
            "Article 22-23, which provides collective community-level protection independent "
            "of patent law."
        ),
    },
]


# ── Builder ──────────────────────────────────────────────────────────────────

def build_pdf(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        rightMargin=2.2*cm, leftMargin=2.2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
        title="Landmark Ayush IP Cases — Case Law Compendium",
        author="IP-SAKTI Sahayak | Ministry of Ayush",
        subject="Ayurvedic Intellectual Property and Traditional Knowledge Law",
    )

    ST  = _styles()
    story: list = []

    # ── Cover Page ────────────────────────────────────────────────────────
    story += [
        Spacer(1, 1.5*cm),
        Paragraph("LANDMARK AYUSH &amp; TRADITIONAL KNOWLEDGE", ST["doc_title"]),
        Paragraph("INTELLECTUAL PROPERTY CASE LAW COMPENDIUM", ST["doc_title"]),
        Spacer(1, 0.4*cm),
        HRFlowable(width="100%", thickness=2, color=_NAVY),
        Spacer(1, 0.3*cm),
        Paragraph(
            "Curated for InLegalBERT RAG Corpus Ingestion | IP-SAKTI Sahayak | Ministry of Ayush",
            ST["doc_sub"],
        ),
        Paragraph("Problem Statement ID: 26045 | All India Institute of Ayurveda", ST["doc_meta"]),
        Spacer(1, 0.3*cm),
        HRFlowable(width="100%", thickness=0.75, color=_SLATE),
        Spacer(1, 1.5*cm),
    ]

    # Cover metadata table
    cov_data = [
        ["Document Type:", "Case Law Compendium — Statutory Referenced Summaries"],
        ["Jurisdiction:",  "India (Patents Act 1970, BDA 2002, GI Act 1999) | US | EPO"],
        ["Cases Covered:", "4 Landmark Biopiracy / ABS / GI Cases"],
        ["Primary Statutes:", "Patents Act 1970 s.3(p), BDA 2002 ss.3/7/21, GI Act 1999"],
        ["Target Use:", "Vector Database Ingestion (InLegalBERT / BM25 Hybrid Retrieval)"],
        ["Generated by:", "scripts/generate_case_law_pdf.py | IP-SAKTI Sahayak v6.0"],
    ]
    cov_t = Table(cov_data, colWidths=[4.5*cm, 11.5*cm])
    cov_t.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",  (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), _NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_GREY, _WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.25, _BORDER),
        ("WORDWRAP", (1, 0), (1, -1), True),
    ]))
    story.append(cov_t)
    story.append(Spacer(1, 1.5*cm))

    # Legal disclaimer
    story.append(Paragraph(
        "DISCLAIMER: This compendium is prepared for educational and informational purposes "
        "to support AI-assisted legal research. It does not constitute legal advice. Case "
        "summaries are accurate to the best of the authors' knowledge but should be verified "
        "against primary sources before reliance in any legal proceeding.",
        ST["warning"],
    ))

    # ── Table of Contents ─────────────────────────────────────────────────
    story += [
        Spacer(1, 0.5*cm),
        Paragraph("TABLE OF CONTENTS", ST["toc_head"]),
        HRFlowable(width="100%", thickness=0.5, color=_BORDER),
        Spacer(1, 0.2*cm),
    ]
    toc_items = [
        "Case No. 1 — US Patent No. 5,401,504 Revocation (Turmeric Wound-Healing Patent)",
        "Case No. 2 — EPO Patent No. EP 436,257 Revocation (Neem Antifungal Patent)",
        "Case No. 3 — Divya Pharmacy v. Union of India (Uttarakhand HC, 2018) — ABS Benefit Sharing",
        "Case No. 4 — CSIR Challenge to RiceTec US Patent No. 5,663,484 (Basmati Rice)",
    ]
    for i, item in enumerate(toc_items, 1):
        story.append(Paragraph(f"{i}.  {item}", ST["toc_item"]))

    story.append(PageBreak())

    # ── Cases ─────────────────────────────────────────────────────────────
    for case in CASES:
        # Case header block
        story += [
            Paragraph(case["num"], ST["case_num"]),
            Paragraph(case["title"].replace("\n", "<br/>"), ST["case_title"]),
            Paragraph(case["citation"], ST["case_citation"]),
            HRFlowable(width="100%", thickness=1.5, color=_NAVY),
            Spacer(1, 0.2*cm),
        ]

        for sec in case["sections"]:
            story.append(Paragraph(sec["head"], ST["section_head"]))

            if sec.get("text"):
                for para in sec["text"].split("\n\n"):
                    para = para.strip()
                    if para:
                        story.append(Paragraph(para, ST["body"]))

            if sec.get("bullets"):
                for b in sec["bullets"]:
                    story.append(Paragraph(f"  \u2022  {b}", ST["bullet"]))
                story.append(Spacer(1, 0.1*cm))

            if sec.get("statutes"):
                for st in sec["statutes"]:
                    story.append(Paragraph(st, ST["statute"]))

            if sec.get("warning"):
                story.append(Paragraph(sec["warning"], ST["warning"]))

        # Ratio decidendi
        story += [
            Spacer(1, 0.2*cm),
            Paragraph(case["ratio"], ST["ratio"]),
            Spacer(1, 0.4*cm),
            HRFlowable(width="100%", thickness=0.5, color=_BORDER),
            Spacer(1, 0.2*cm),
            PageBreak(),
        ]

    # Remove trailing PageBreak
    if story and isinstance(story[-1], PageBreak):
        story.pop()

    # ── Back matter ───────────────────────────────────────────────────────
    story += [
        Spacer(1, 1*cm),
        HRFlowable(width="100%", thickness=1.5, color=_NAVY),
        Spacer(1, 0.3*cm),
        Paragraph(
            "END OF CASE LAW COMPENDIUM",
            ParagraphStyle("end", parent=_styles()["doc_title"],
                           fontSize=13, textColor=_NAVY),
        ),
        Spacer(1, 0.3*cm),
        Paragraph(
            "Source: IP-SAKTI Sahayak | Ministry of Ayush | All India Institute of Ayurveda | "
            "Problem Statement ID: 26045 | SIH 2024",
            _styles()["footer"],
        ),
    ]

    doc.build(story)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating Landmark_Ayush_IP_Cases.pdf ...")
    build_pdf(OUT_PATH)
    size_kb = OUT_PATH.stat().st_size // 1024
    print(f"  Written: {OUT_PATH}  ({size_kb} KB)")
    print("Done.")
