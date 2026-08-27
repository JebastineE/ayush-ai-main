# IP-SAKTI Sahayak — Current Dataset Inventory

## Summary

- **Total Dataset Sources**: 4 Primary Sources (Legal Acts & Rules PDF Corpus, TKDL Keyword Representative Database, TKDL Bio-Piracy Case Studies, TKDL Sample Dataset).
- **Total Files**: 127 data files across `data/` directory.
- **Total Raw Records**: 3,012 TKDL Keyword Records + 12 Bio-Piracy Case Studies + 31 Legal PDF Documents + 60 Sample TKDL Records.
- **Total Unique Records**: 1,722 Clean Unique TKDL Keyword Records + 12 Bio-Piracy Case Studies + 31 Legal PDF Documents.
- **Total Indexed Records in Qdrant**: 5,633 Vectors across 2 Collections (`legal_docs`: 5,573 vectors, `tkdl_records`: 60 vectors).

---

## Dataset Inventory Table

| # | Dataset Name | Source | Records / Count | Format | Location | Used by RAG | In Qdrant | Classification |
|---|---|---|---:|---|---|---|---|---|
| 1 | **TKDL Representative Keywords** | Public Official (CSIR/AYUSH TKDL) | 3,012 raw / 1,722 unique | JSON & CSV | `data/tkdl_public/{ayurveda,unani,siddha,sowa_rigpa}/` | NO | NO | CLEANED / RAW |
| 2 | **TKDL Bio-Piracy Case Studies** | Public Official (CSIR/AYUSH TKDL) | 12 case studies | JSON & CSV | `data/tkdl_public/biopiracy/` | NO | NO | PUBLIC TKDL BIO-PIRACY DATA |
| 3 | **Legal & Regulatory PDF Corpus** | Public Official (Govt of India / WIPO / FDA) | 31 PDF Documents | PDF | `data/legal_corpus/` | **YES** | **YES** (5,573 vectors) | SOURCE DATA |
| 4 | **Processed Legal Text Chunks** | Derived from `data/legal_corpus/` | 5,573 token chunks | JSONL | `data/processed/legal_chunks.jsonl` | **YES** | **YES** | DERIVED DATA |
| 5 | **TKDL Initial Sample Dataset** | Derived / Sample Mock | 60 records | JSON | `data/traditional_knowledge/tkdl_sample_dataset.json` | **YES** | **YES** (60 vectors) | GENERATED / SAMPLE |
| 6 | **TKDL Sample Chunks** | Derived from `tkdl_sample_dataset.json` | 60 chunks | JSONL | `data/processed/tkdl_chunks.jsonl` | **YES** | **YES** | DERIVED DATA |
| 7 | **Formulation Search Evaluation Tests** | Technical Test | 0 formulations (5 test error logs) | JSON | `data/tkdl_public/formulations/test/` | NO | NO | PUBLIC TKDL FORMULATION TEST DATA |
| 8 | **Synthetic Patent Claims Mock** | Synthetic / Generated | 1 mock patent record | JSON | `data/test_mocks/synthetic_patent_claims.json` | NO | NO | GENERATED |
| 9 | **ABS Profiles Mock** | Synthetic / Generated | 1 mock profile | JSON | `data/test_mocks/mock_abs_profiles.json` | NO | NO | GENERATED |

---

## Detailed Audit Breakdown

### 1. TKDL Datasets (`data/tkdl_public/`)

#### A. Ayurveda
- **Plant Name**: `plant_name.json` / `plant_name.csv` — 286 records
- **Plant Part & Product**: `plant_part_and_product.json` / `.csv` — 47 records
- **Animal Name**: `animal_name.json` / `.csv` — 8 records
- **Animal Part & Product**: `animal_part_and_product.json` / `.csv` — 47 records
- **Metals / Mineral Name**: `metals___mineral_name.json` / `.csv` — 32 records
- **Devices / Apparatus**: `devices___apparatus.json` / `.csv` — 5 records
- **Products / Processes / Related Terms**: `products___processes___related_terms.json` / `.csv` — 5 records
- **All Diseases**: `all_diseases.json` / `.csv` — 153 records
- **Drug Action / Properties**: `drug_action___properties.json` / `.csv` — 67 records
- **Mode of Administration**: `mode_of_administration.json` / `.csv` — 24 records
- **Others**: `others.json` / `.csv` — 14 records
- **Subtotal**: **696 records** | Validated: YES | Used by RAG: NO

#### B. Unani
- **Plant Name**: 362 records
- **Plant Part & Product**: 44 records
- **Animal Name**: 32 records
- **Animal Part & Product**: 80 records
- **Metals / Mineral Name**: 48 records
- **Devices / Apparatus**: 5 records
- **Products / Processes**: 5 records
- **All Diseases**: 313 records
- **Drug Action / Properties**: 114 records
- **Mode of Administration**: 29 records
- **Others**: 66 records
- **Subtotal**: **1,088 records** | Validated: YES | Used by RAG: NO

#### C. Siddha
- **Plant Name**: 223 records
- **Plant Part & Product**: 34 records
- **Animal Name**: 11 records
- **Animal Part & Product**: 36 records
- **Metals / Mineral Name**: 27 records
- **Devices / Apparatus**: 5 records
- **Products / Processes**: 5 records
- **All Diseases**: 119 records
- **Drug Action / Properties**: 47 records
- **Mode of Administration**: 15 records
- **Others**: 16 records
- **Subtotal**: **533 records** | Validated: YES | Used by RAG: NO

#### D. Sowa Rigpa
- **Plant Name**: 286 records
- **Plant Part & Product**: 47 records
- **Animal Name**: 8 records
- **Animal Part & Product**: 47 records
- **Metals / Mineral Name**: 32 records
- **Devices / Apparatus**: 5 records
- **Products / Processes**: 5 records
- **All Diseases**: 153 records
- **Drug Action / Properties**: 67 records
- **Mode of Administration**: 24 records
- **Others**: 14 records
- **Subtotal**: **695 records** | Validated: YES | Used by RAG: NO

#### E. Bio-Piracy
- `data/tkdl_public/biopiracy/biopiracy_cases.json` / `biopiracy_cases.csv` — **12 case study topics** (Turmeric, Neem, Basmati, Kava, Ayahuasca, Quinoa, Hoodia, Phyllanthus, etc.) | Validated: YES | Used by RAG: NO

#### F. Clean Data
- `data/tkdl_public/clean/clean_keyword_records.json` — **1,722 unique deduplicated records** with cross-category provenance | Validated: YES | Used by RAG: NO

#### G. Formulations Evaluation Data
- `data/tkdl_public/formulations/clean/clean_formulations.json` — **0 formulation records** (All 5 test terms returned session error pages due to active login authentication restrictions).

---

### 2. Reported vs Actual TKDL Verification

| Metric | Reported | Actual | Match |
| :--- | ---: | ---: | :---: |
| **Raw TKDL Records** | 3,012 | 3,012 | **YES** |
| **Unique Clean Records** | 1,722 | 1,722 | **YES** |
| **Duplicates Removed** | 1,290 | 1,290 | **YES** |
| **Ayurveda Plant Name Records** | 286 | 286 | **YES** |
| **Bio-Piracy Topic Case Studies** | 12 | 12 | **YES** |

---

### 3. Legal & Regulatory PDF Corpus (`data/legal_corpus/`)

31 PDF documents containing primary Acts, Rules, Guidelines, and International Treaties:
1. *Ayurvedic Pharmacopoeia of India All Volume.pdf* (5.17 MB)
2. *ayush_ip_guidelines.pdf* (44.6 KB)
3. *bd_act_amendment.pdf* (319 KB)
4. *biologicalDiversityRules2024.pdf* (2.41 MB)
5. *Botanical-Drug-Development--Guidance-for-Industry.pdf* (226 KB)
6. *Budapest Treaty (microorganism deposit).pdf* (176 KB)
7. *conventionOnBiodiversity.pdf* (4.55 MB)
8. *Copyright Act, 1957.pdf* (593 KB)
9. *Designs Act, 2000.pdf* (368 KB)
10. *Digital Personal Data Protection Act, 2023.pdf* (382 KB)
11. *Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954.pdf* (29.5 KB)
12. *DrugsandCosmeticsAct1940Rules1945.pdf* (8.64 MB)
13. *European Union Traditional Herbal Medicinal Products Directive.pdf* (101 KB)
14. *FDA-Export-Certification-Guidance-for-Industry--8-19-21-508.pdf* (352 KB)
15. *Food Safety and Standards (Ayurveda Aahara) Regulations, 2022.pdf* (73 KB)
16. *Geographical Indications of Goods Act, 1999.pdf* (427 KB)
17. *Guidance-for-Industry---Exports-Under-the-FDA-Export-Reform-and-Enhancement-Act-of-1996-(PDF)_0.pdf* (540 KB)
18. *Hague Agreement.pdf* (810 KB)
19. *Landmark_Ayush_IP_Cases.pdf* (24 KB)
20. *Madrid_Protocol.pdf.pdf* (308 KB)
21. *nagoya-protocol-en.pdf* (502 KB)
22. *Patents (Amendment) Rules, 2024.pdf* (847 KB)
23. *Patents_Act_1970.pdf* (715 KB)
24. *Patent_Cooperation_Treaty.pdf* (455 KB)
25. *Protection of Plant Varieties and Farmers' Rights.pdf* (453 KB)
26. *State_wise_Registered_GI_of_India.pdf* (193 KB)
27. *THE BIOLOGICAL DIVERSITY ACT, 2002.pdf* (404 KB)
28. *Trade Marks Act, 1999.pdf* (625 KB)
29. *TRIPS Agreement – full text.pdf* (122 KB)
30. *WIPO Treaty on IP, Genetic Resources and Associated TK (GRATK, 2024).pdf* (278 KB)
31. *DMROA.pdf* (29.5 KB)

---

### 4. Qdrant Vector Store State (`data/qdrant_store/`)

- **Collection `legal_docs`**:
  - Vector count: **5,573** (768-dimensional embeddings via `bge-base-en-v1.5`)
  - Payload keys: `['chunk_id', 'source_file', 'page_number', 'chunk_index', 'text', 'collection']`
  - Ingested Sources: All 31 legal PDF files in `data/legal_corpus/`.
- **Collection `tkdl_records`**:
  - Vector count: **60** (768-dimensional embeddings)
  - Payload keys: `['chunk_id', 'source_file', 'page_number', 'chunk_index', 'text', 'collection', 'ipc_code', 'tkrc_code']`
  - Ingested Source: `data/traditional_knowledge/tkdl_sample_dataset.json` (60 sample records).
  - **Status of `data/tkdl_public/`**: The newly collected 3,012 TKDL keyword records and bio-piracy dataset are **NOT YET INGESTED OR VECTORIZED IN QDRANT**.

---

## Missing Datasets (SIH 26045 Comparison)

To fulfill the complete SIH 26045 problem statement for IP-SAKTI Sahayak, the following datasets are currently missing:

1. **Full Indian Patent Office (IPO) Grant & Application Corpus**: Specific Ayush/herbal patent applications and opposition decisions.
2. **National Biodiversity Authority (NBA) Access & Benefit Sharing (ABS) Approvals Dataset**: Official registry of cleared ABS applications and benefit-sharing agreements.
3. **Comprehensive AYUSH Classical Formulations Database**: Detailed Ayurvedic Pharmacopoeia (API), Siddha Pharmacopoeia (SPI), and Unani Pharmacopoeia (UPI) formulation recipes and ratio breakdowns.
4. **WIPO / EPO Prior-Art Opposition Decisions Database**: Full text of CSIR-TKDL legal challenges and revocation decisions at EPO, USPTO, and IP Australia.

---

## Recommended Next Step

**Next Priority Dataset**: Ingest the **3,012 TKDL Keyword Records & 12 Bio-Piracy Case Studies** (`data/tkdl_public/clean/clean_keyword_records.json` and `data/tkdl_public/biopiracy/biopiracy_cases.json`) into the Qdrant `tkdl_records` collection to expand RAG prior-art search capabilities beyond the current 60 sample records.
