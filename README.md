# IP-SAKTI Sahayak 🌿⚖️

> **A multilingual, RAG-based AI assistant for Intellectual Property and regulatory guidance in Ayurveda** — developed for Smart India Hackathon (SIH) under Problem Statement ID 26045, Ministry of Ayush.

---

## 🧭 Overview

**IP-SAKTI Sahayak** (_Sahayak_ = "helper" in Sanskrit) is an intelligent assistant that guides Ayurvedic practitioners, AYUSH startups, MSMEs, researchers, and cultivators through the complex landscape of:

- **Intellectual Property Rights (IPR)** — patents, GI, trademarks, copyright, designs, trade secrets, and plant-variety rights
- **Access and Benefit Sharing (ABS)** — Biological Diversity Act (2023 amendment) and the Nagoya Protocol
- **Drug Regulation** — classification under the Drugs and Cosmetics Act, FSSAI Ayurveda-Aahar rules
- **International Frameworks** — TRIPS, CBD, WIPO GRATK Treaty, PCT, Madrid/Hague systems

Every answer is **source-cited**, **jurisdiction-aware**, and augmented with a **hallucination-minimising RAG pipeline** — so users can trace each response back to a specific statute, rule, treaty article, or registry record.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **RAG Legal Chat** | Hybrid BM25 + dense retrieval over a curated legal corpus, grounded generation via Gemini |
| 🌐 **Jurisdiction Toggle** | India vs. International regimes kept explicitly separate |
| 🌿 **Formulation Classifier** | Deterministic classification — classical/generic, possible match, or no match — using ingredient overlap + name similarity scoring |
| 🔬 **TKDL Biopiracy Scanner** | Scan patent claims against TKDL vector database for prior-art matches |
| 🔎 **Patent Search** | Query Google Patents Public Dataset via BigQuery |
| 📚 **Research Explorer** | Concurrent academic literature search across multiple databases |
| 📄 **Escalation Dossier** | Generate a PDF dossier for escalation to a human IP facilitator |
| 🔒 **DPDP Compliance** | PII scrubbing on all inputs and outputs (Digital Personal Data Protection Act) |
| 🗣️ **Multilingual** | Bhashini-powered translation — vernacular → English → vernacular |
| 💬 **Session Memory** | Per-session conversation history for contextual follow-up |
| ⚡ **Shadow Cache** | SQLite-based response cache with pre-warm support |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Next.js Frontend                   │
│  (React 19 · TypeScript · TailwindCSS · Framer      │
│   Motion · Lucide Icons · react-markdown)           │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (port 3000 → 8000)
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend (Python)               │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  RAG Engine │  │  Formulation │  │  Biopiracy│  │
│  │ (Qdrant +   │  │  Classifier  │  │  Scanner  │  │
│  │  InLegalBERT│  │  (det. rules)│  │  (TKDL)   │  │
│  │  + Gemini)  │  └──────────────┘  └───────────┘  │
│  └─────────────┘                                    │
│                                                     │
│  ┌────────────┐  ┌───────────┐  ┌────────────────┐  │
│  │  BigQuery  │  │ Bhashini  │  │  DPDP / Cache  │  │
│  │  Patent DB │  │Translation│  │  Middleware    │  │
│  └────────────┘  └───────────┘  └────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Qdrant Vector Store (local)            │
│  • legal_docs  • classical_formulations             │
│  • tkdl_formulations                               │
└─────────────────────────────────────────────────────┘
```

### Data Pipeline

```
Raw PDFs / Legal Corpus
        │
        ▼
  Phase 1: Ingestion  (run_pipeline.py --phase 1)
  • PyMuPDF / pypdf parsing
  • Metadata extraction
        │
        ▼
  Phase 2: Vectorization  (run_pipeline.py --phase 2)
  • law-ai/InLegalBERT embeddings (SentenceTransformers)
  • Qdrant upsert
```

---

## 📁 Project Structure

```
ayush-ai-main/
├── app/                        # FastAPI backend
│   ├── api/
│   │   └── endpoints.py        # All API routes
│   ├── db/
│   │   └── sqlite_cache.py     # Shadow cache
│   ├── middleware/
│   │   ├── cache.py            # Cache middleware
│   │   └── dpdp.py             # PII scrubbing
│   ├── schemas/
│   │   └── payloads.py         # Pydantic request/response models
│   ├── services/
│   │   ├── rag.py              # Core RAG pipeline
│   │   ├── formulation_classifier.py  # Deterministic formulation classification
│   │   ├── biopiracy_scanner.py       # TKDL prior-art scan
│   │   ├── patent_search_bigquery.py  # BigQuery patent search
│   │   ├── research_explorer.py       # Academic literature search
│   │   ├── translation.py             # Bhashini multilingual
│   │   ├── escalation.py              # PDF dossier generation
│   │   ├── memory.py                  # Session memory
│   │   ├── action_selector.py         # Contextual action suggestions
│   │   └── action_resources.py        # Action metadata
│   └── main.py                 # FastAPI app factory
│
├── pipeline/                   # Data ingestion & vectorization
│   ├── phase1_ingest.py        # PDF ingestion
│   ├── phase1b_ingest_formulations.py
│   ├── phase2_vectorize.py     # Qdrant vectorization
│   ├── phase2b_vectorize_formulations.py
│   └── config.py
│
├── frontend/                   # Next.js frontend
│   ├── app/                    # Next.js app router
│   ├── components/             # React components
│   ├── lib/                    # Shared utilities
│   └── types/                  # TypeScript types
│
├── data/                       # (gitignored) corpus & vector store
│   ├── legal_corpus/           # Source PDFs
│   ├── qdrant_store/           # Local Qdrant DB
│   └── class_data/             # Formulation classifier data
│
├── tests/                      # Test suite
├── run_pipeline.py             # CLI for ingestion pipeline
├── rebuild_db.py               # DB rebuild utility
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── problem_statement.txt       # Original SIH problem statement
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Gemini API key ([get one here](https://aistudio.google.com/apikey))
- Google Cloud credentials (for BigQuery patent search, optional)

### 1. Clone the Repository

```bash
git clone <repo-url>
cd ayush-ai-main
```

### 2. Set Up the Python Backend

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
HF_TOKEN=your_huggingface_token  # suppresses HF warnings
```

> ⚠️ **Never commit `.env` to version control.**

### 4. Build the Data Pipeline

Place your source PDFs inside `data/legal_corpus/`, then run:

```bash
# Run ingestion + vectorization
python run_pipeline.py --phase all

# Or run phases individually
python run_pipeline.py --phase 1   # Ingest PDFs
python run_pipeline.py --phase 2   # Vectorize into Qdrant
```

### 5. Start the Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 6. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: [http://localhost:3000](http://localhost:3000)

---

## 🔌 API Reference

All endpoints are prefixed with `/api/v1`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/v1/chat` | RAG legal chat with jurisdiction filter |
| `POST` | `/api/v1/classify-formulation` | Deterministic formulation classification |
| `POST` | `/api/v1/tkdl-scan` | Biopiracy scanner against TKDL |
| `POST` | `/api/v1/patent-search` | BigQuery patent search |
| `POST` | `/api/v1/research-search` | Academic literature search |
| `POST` | `/api/v1/escalate` | Generate PDF escalation dossier |
| `GET` | `/api/v1/document/{filename}` | Serve corpus PDF for citation viewer |
| `GET` | `/api/v1/cache/stats` | Shadow cache diagnostics |

### Example: Chat Request

```json
POST /api/v1/chat
{
  "query": "Can I patent an Ayurvedic formulation based on Triphala?",
  "jurisdiction": "india",
  "language": "en",
  "session_id": "uuid-here"
}
```

### Example: Formulation Classification

```json
POST /api/v1/classify-formulation
{
  "formulation_name": "Triphala Churna",
  "ingredients": [
    {"name": "haritaki", "part": "fruit", "proportion": "1 part"},
    {"name": "bibhitaki", "part": "fruit", "proportion": "1 part"},
    {"name": "amla", "part": "fruit", "proportion": "1 part"}
  ],
  "method": "Churna (powder)",
  "claimed_indication": "digestive health",
  "route": "oral"
}
```

---

## 🔒 Safety & Compliance Design

- **Deterministic Classification** — The formulation classifier uses a rule-based decision tree with fixed thresholds (`THRESHOLD_HIGH=0.75`, `THRESHOLD_LOW=0.55`). The LLM **only narrates** the result; it **cannot change the category**.
- **DPDP Compliance** — PII scrubbing is applied to all incoming queries and outgoing responses before any processing or storage.
- **Mandatory Disclaimer** — Every response ends with: *"This is information, not legal advice."*
- **Safe Abstention** — The system abstains from answering when confidence is too low, rather than fabricating an answer.
- **No Hallucinated Citations** — Every answer is grounded in retrieved chunks from the legal corpus with source, page, and snippet.

---

## 🌐 Corpus Sources

The legal corpus can be assembled from these open, authoritative public sources:

- [Traditional Knowledge Digital Library (TKDL)](https://www.tkdl.res.in)
- [India Code — Statutes & Rules](https://indiacode.nic.in)
- [IP India — Patents, Trademarks, Designs, GI](https://ipindia.gov.in)
- [WIPO — GRATK Treaty, PCT, Madrid, Hague](https://www.wipo.int)
- [Ayurvedic Pharmacopoeia of India](https://ayush.gov.in)
- [FSSAI](https://fssai.gov.in)

---

## 🛠️ Tech Stack

### Backend
| Library | Purpose |
|---|---|
| `fastapi` | REST API framework |
| `sentence-transformers` | `law-ai/InLegalBERT` dense embeddings |
| `qdrant-client` | Local vector store |
| `google-genai` | Gemini grounded generation |
| `google-cloud-bigquery` | Patent dataset search |
| `rank-bm25` | Sparse retrieval (hybrid RAG) |
| `rapidfuzz` | Fuzzy ingredient name matching |
| `reportlab` | PDF escalation dossier generation |
| `pymupdf4llm` | PDF text extraction |
| `python-dotenv` | Environment variable management |

### Frontend
| Library | Purpose |
|---|---|
| `next` | React framework (App Router) |
| `react` | UI library |
| `tailwindcss` | Utility-first CSS |
| `framer-motion` | Animations |
| `lucide-react` | Icon library |
| `react-markdown` | Render markdown responses |
| `uuid` | Session ID generation |

---

## 🤝 Contributing

This project was built for the Smart India Hackathon. Contributions, issues, and suggestions are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## ⚠️ Disclaimer

This tool provides **information only** and does not constitute legal advice. Users should consult a qualified IP attorney or registered patent agent for any legal determinations, filings, or decisions.

---

## 📄 License

This project is developed for academic and public interest purposes under the Smart India Hackathon initiative (Ministry of Ayush, Problem Statement ID: 26045).

---

<p align="center">Built with ❤️ for the AYUSH community · Smart India Hackathon 2024</p>
