import os
import json
import hashlib

project_dir = r"c:\Users\JEBASTINE E\Desktop\ayush-ai-main"
corpus_dir = os.path.join(project_dir, "data", "legal_corpus")
processed_dir = os.path.join(project_dir, "data", "processed")

def sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

files = sorted(os.listdir(corpus_dir))
print(f"Total files on disk ({len(files)}):")

metadata_map = {
    "Ayurvedic Pharmacopoeia of India All Volume.pdf": {
        "jurisdiction": "IN",
        "document_type": "pharmacopoeia",
        "authority": "Pharmacopoeial Commission for Indian Medicine & Homoeopathy (PCIM&H), Ministry of AYUSH",
        "act_name": "Ayurvedic Pharmacopoeia of India",
        "version": "consolidated",
        "effective_date": "2016-01-01",
        "source_url": "https://pcimh.gov.in/",
        "language": "en",
        "status": "current"
    },
    "Botanical-Drug-Development--Guidance-for-Industry.pdf": {
        "jurisdiction": "US",
        "document_type": "guidance",
        "authority": "United States Food and Drug Administration (US FDA)",
        "act_name": "Botanical Drug Development Guidance for Industry",
        "version": "revision_1",
        "effective_date": "2016-12-01",
        "source_url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/botanical-drug-development-guidance-industry",
        "language": "en",
        "status": "current"
    },
    "Budapest Treaty (microorganism deposit).pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "World Intellectual Property Organization (WIPO)",
        "act_name": "Budapest Treaty on the International Recognition of the Deposit of Microorganisms for the Purposes of Patent Procedure",
        "version": "as_amended_1980",
        "effective_date": "1980-09-26",
        "source_url": "https://www.wipo.int/treaties/en/registration/budapest/",
        "language": "en",
        "status": "current"
    },
    "Copyright Act, 1957.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Government of India",
        "act_name": "Copyright Act, 1957",
        "version": "as_amended_2012",
        "effective_date": "1958-01-21",
        "source_url": "https://copyright.gov.in/",
        "language": "en",
        "status": "current"
    },
    "Designs Act, 2000.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Government of India",
        "act_name": "Designs Act, 2000",
        "version": "current",
        "effective_date": "2001-05-11",
        "source_url": "https://ipindia.gov.in/act-2000.htm",
        "language": "en",
        "status": "current"
    },
    "Digital Personal Data Protection Act, 2023.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Government of India",
        "act_name": "Digital Personal Data Protection Act, 2023",
        "version": "current",
        "effective_date": "2023-08-11",
        "source_url": "https://www.meity.gov.in/content/digital-personal-data-protection-act-2023",
        "language": "en",
        "status": "current"
    },
    "Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Government of India",
        "act_name": "Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954",
        "version": "as_amended_2002",
        "effective_date": "1955-04-01",
        "source_url": "https://cdsco.gov.in/",
        "language": "en",
        "status": "current"
    },
    "DrugsandCosmeticsAct1940Rules1945.pdf": {
        "jurisdiction": "IN",
        "document_type": "act_and_rules",
        "authority": "Central Drugs Standard Control Organisation (CDSCO), Ministry of Health and Family Welfare",
        "act_name": "Drugs and Cosmetics Act, 1940 and Drugs Rules, 1945",
        "version": "as_amended_2020",
        "effective_date": "1940-04-10",
        "source_url": "https://cdsco.gov.in/opencms/opencms/en/Acts-and-rules/",
        "language": "en",
        "status": "current"
    },
    "European Union Traditional Herbal Medicinal Products Directive.pdf": {
        "jurisdiction": "EU",
        "document_type": "directive",
        "authority": "European Parliament and Council of the European Union",
        "act_name": "Directive 2004/24/EC on Traditional Herbal Medicinal Products",
        "version": "current",
        "effective_date": "2004-04-30",
        "source_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32004L0024",
        "language": "en",
        "status": "current"
    },
    "FDA-Export-Certification-Guidance-for-Industry--8-19-21-508.pdf": {
        "jurisdiction": "US",
        "document_type": "guidance",
        "authority": "United States Food and Drug Administration (US FDA)",
        "act_name": "FDA Export Certification Guidance for Industry",
        "version": "current",
        "effective_date": "2021-08-19",
        "source_url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/fda-export-certification-guidance-industry",
        "language": "en",
        "status": "current"
    },
    "Food Safety and Standards (Ayurveda Aahara) Regulations, 2022.pdf": {
        "jurisdiction": "IN",
        "document_type": "regulation",
        "authority": "Food Safety and Standards Authority of India (FSSAI)",
        "act_name": "Food Safety and Standards (Ayurveda Aahara) Regulations, 2022",
        "version": "current",
        "effective_date": "2022-05-05",
        "source_url": "https://www.fssai.gov.in/upload/notifications/2022/05/6273b5b3e6c38Gazette_Notification_Ayurveda_Aahara_06_05_2022.pdf",
        "language": "en",
        "status": "current"
    },
    "Geographical Indications of Goods Act, 1999.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Government of India",
        "act_name": "Geographical Indications of Goods (Registration and Protection) Act, 1999",
        "version": "current",
        "effective_date": "2003-09-15",
        "source_url": "https://ipindia.gov.in/act-1999.htm",
        "language": "en",
        "status": "current"
    },
    "Guidance-for-Industry---Exports-Under-the-FDA-Export-Reform-and-Enhancement-Act-of-1996-(PDF)_0.pdf": {
        "jurisdiction": "US",
        "document_type": "guidance",
        "authority": "United States Food and Drug Administration (US FDA)",
        "act_name": "Exports Under the FDA Export Reform and Enhancement Act of 1996 Guidance for Industry",
        "version": "current",
        "effective_date": "1996-04-26",
        "source_url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/exports-under-fda-export-reform-and-enhancement-act-1996",
        "language": "en",
        "status": "current"
    },
    "Hague Agreement.pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "World Intellectual Property Organization (WIPO)",
        "act_name": "Hague Agreement Concerning the International Registration of Industrial Designs",
        "version": "Geneva_Act_1999",
        "effective_date": "2003-12-23",
        "source_url": "https://www.wipo.int/treaties/en/registration/hague/",
        "language": "en",
        "status": "current"
    },
    "Landmark_Ayush_IP_Cases.pdf": {
        "jurisdiction": "IN",
        "document_type": "case_law_compilation",
        "authority": "Supreme Court of India / High Courts of India",
        "act_name": "Landmark AYUSH & Traditional Knowledge IP Case Precedents",
        "version": "consolidated",
        "effective_date": None,
        "source_url": "https://main.sci.gov.in/",
        "language": "en",
        "status": "current"
    },
    "Madrid_Protocol.pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "World Intellectual Property Organization (WIPO)",
        "act_name": "Protocol Relating to the Madrid Agreement Concerning the International Registration of Marks",
        "version": "as_amended_2007",
        "effective_date": "1995-12-01",
        "source_url": "https://www.wipo.int/treaties/en/registration/madrid_protocol/",
        "language": "en",
        "status": "current"
    },
    "Patent_Cooperation_Treaty.pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "World Intellectual Property Organization (WIPO)",
        "act_name": "Patent Cooperation Treaty (PCT)",
        "version": "as_modified_2001",
        "effective_date": "1978-01-24",
        "source_url": "https://www.wipo.int/pct/en/treaty/about.html",
        "language": "en",
        "status": "current"
    },
    "Patents (Amendment) Rules, 2024.pdf": {
        "jurisdiction": "IN",
        "document_type": "rules",
        "authority": "Controller General of Patents, Designs and Trade Marks (CGPDTM), Ministry of Commerce and Industry",
        "act_name": "Patents (Amendment) Rules, 2024",
        "version": "amendment_2024",
        "effective_date": "2024-03-15",
        "source_url": "https://ipindia.gov.in/rules-patents.htm",
        "language": "en",
        "status": "current"
    },
    "Patents_Act_1970.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Government of India",
        "act_name": "Patents Act, 1970",
        "version": "as_amended_2005",
        "effective_date": "1972-04-20",
        "source_url": "https://ipindia.gov.in/patents-act-1970.htm",
        "language": "en",
        "status": "current"
    },
    "Protection of Plant Varieties and Farmers' Rights.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Protection of Plant Varieties and Farmers' Rights Authority, Ministry of Agriculture and Farmers Welfare",
        "act_name": "Protection of Plant Varieties and Farmers' Rights Act, 2001",
        "version": "current",
        "effective_date": "2001-10-30",
        "source_url": "https://plantauthority.gov.in/",
        "language": "en",
        "status": "current"
    },
    "State_wise_Registered_GI_of_India.pdf": {
        "jurisdiction": "IN",
        "document_type": "registry",
        "authority": "Geographical Indications Registry, Chennai",
        "act_name": "State-wise Registered Geographical Indications of India Registry",
        "version": "consolidated",
        "effective_date": None,
        "source_url": "https://ipindia.gov.in/registered-gls.htm",
        "language": "en",
        "status": "current"
    },
    "THE BIOLOGICAL DIVERSITY ACT, 2002.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "National Biodiversity Authority (NBA), Ministry of Environment, Forest and Climate Change",
        "act_name": "Biological Diversity Act, 2002",
        "version": "current",
        "effective_date": "2003-02-05",
        "source_url": "https://nbaindia.org/content/17/59/1/act.html",
        "language": "en",
        "status": "current"
    },
    "TRIPS_Agreement_full_text.pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "World Trade Organization (WTO)",
        "act_name": "Agreement on Trade-Related Aspects of Intellectual Property Rights (TRIPS Agreement)",
        "version": "as_amended_2017",
        "effective_date": "1995-01-01",
        "source_url": "https://www.wto.org/english/docs_e/legal_e/31b-trips_e.htm",
        "language": "en",
        "status": "current"
    },
    "Trade Marks Act, 1999.pdf": {
        "jurisdiction": "IN",
        "document_type": "act",
        "authority": "Government of India",
        "act_name": "Trade Marks Act, 1999",
        "version": "as_amended_2010",
        "effective_date": "2003-09-15",
        "source_url": "https://ipindia.gov.in/act-1999-trademarks.htm",
        "language": "en",
        "status": "current"
    },
    "WIPO Treaty on IP, Genetic Resources and Associated TK (GRATK, 2024).pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "World Intellectual Property Organization (WIPO)",
        "act_name": "WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge",
        "version": "adopted_2024",
        "effective_date": "2024-05-24",
        "source_url": "https://www.wipo.int/diplomatic-conferences/en/genetic-resources/",
        "language": "en",
        "status": "current"
    },
    "ayush_ip_guidelines.pdf": {
        "jurisdiction": "IN",
        "document_type": "guidelines",
        "authority": "Ministry of AYUSH, Government of India",
        "act_name": "Guidelines for Intellectual Property Rights in AYUSH Sector",
        "version": "current",
        "effective_date": None,
        "source_url": "https://ayush.gov.in/",
        "language": "en",
        "status": "current"
    },
    "bd_act_amendment.pdf": {
        "jurisdiction": "IN",
        "document_type": "act_amendment",
        "authority": "National Biodiversity Authority (NBA), Ministry of Environment, Forest and Climate Change",
        "act_name": "Biological Diversity (Amendment) Act, 2023",
        "version": "amendment_2023",
        "effective_date": "2023-08-03",
        "source_url": "https://nbaindia.org/",
        "language": "en",
        "status": "current"
    },
    "biologicalDiversityRules2024.pdf": {
        "jurisdiction": "IN",
        "document_type": "rules",
        "authority": "National Biodiversity Authority (NBA), Ministry of Environment, Forest and Climate Change",
        "act_name": "Biological Diversity Rules, 2024",
        "version": "rules_2024",
        "effective_date": "2024-01-01",
        "source_url": "https://nbaindia.org/",
        "language": "en",
        "status": "current"
    },
    "conventionOnBiodiversity.pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "United Nations Convention on Biological Diversity (CBD) Secretariat",
        "act_name": "Convention on Biological Diversity",
        "version": "adopted_1992",
        "effective_date": "1993-12-29",
        "source_url": "https://www.cbd.int/convention/text/",
        "language": "en",
        "status": "current"
    },
    "nagoya-protocol-en.pdf": {
        "jurisdiction": "INT",
        "document_type": "treaty",
        "authority": "United Nations Convention on Biological Diversity (CBD) Secretariat",
        "act_name": "Nagoya Protocol on Access to Genetic Resources and the Fair and Equitable Sharing of Benefits Arising from their Utilization",
        "version": "adopted_2010",
        "effective_date": "2014-10-12",
        "source_url": "https://www.cbd.int/abs/text/",
        "language": "en",
        "status": "current"
    }
}

print(f"Mapped {len(metadata_map)} documents.")
for fname in files:
    if fname not in metadata_map:
        print(f"WARNING: Missing mapping for {fname}")
    else:
        # Add sha256 & retrieved_at
        fp = os.path.join(corpus_dir, fname)
        metadata_map[fname]["sha256"] = sha256(fp)
        metadata_map[fname]["retrieved_at"] = "2026-08-27T11:14:00+05:30"

out_json = os.path.join(processed_dir, "document_metadata.json")
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(metadata_map, f, indent=2)

print(f"Saved document metadata mapping to {out_json}")
