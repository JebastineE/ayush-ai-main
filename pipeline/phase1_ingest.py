import json
import csv
import re
from pathlib import Path
from transformers import AutoTokenizer
import pymupdf4llm

from .config import (
    CORPUS_DIR, TK_DIR, LEGAL_CHUNKS, TKDL_CHUNKS, JSON_CHUNKS, CSV_CHUNKS, INGESTION_LOG,
    MODEL_NAME, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS,
    LEGAL_COLLECTION, TKDL_COLLECTION
)
from .utils import setup_logging, compute_sha256, load_ingestion_log, save_ingestion_log, ensure_dirs

logger = setup_logging(__name__)

# Initialize tokenizer for token-aware chunking
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
except Exception as e:
    logger.error(f"Failed to load tokenizer {MODEL_NAME}: {e}")
    tokenizer = None

def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    try:
        pages = pymupdf4llm.to_markdown(str(pdf_path), page_chunks=True)
        return pages
    except Exception as e:
        logger.error(f"Could not parse PDF {pdf_path.name}: {e}")
        return []

def extract_txt_file(txt_path: Path) -> list[dict]:
    try:
        with open(txt_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return [{"text": content, "page": 1}]
    except Exception as e:
        logger.error(f"Could not read TXT file {txt_path.name}: {e}")
        return []

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if not tokenizer:
        # Fallback if tokenizer fails to load
        return [text]

    token_ids = tokenizer.encode(text, add_special_tokens=False)
    if not token_ids:
        return []

    chunks = []
    stride = chunk_size - overlap
    
    for i in range(0, len(token_ids), stride):
        chunk_token_ids = token_ids[i:i + chunk_size]
        chunk_str = tokenizer.decode(chunk_token_ids, skip_special_tokens=True).strip()
        # Filter out very small chunks
        if len(tokenizer.encode(chunk_str, add_special_tokens=False)) > 20:
            chunks.append(chunk_str)
            
    return chunks

def slugify(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def load_document_metadata() -> dict:
    meta_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "document_metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load document metadata mapping: {e}")
    return {}

def process_legal_corpus(log: dict) -> tuple[list[dict], dict]:
    new_chunks = []
    
    if not CORPUS_DIR.exists():
        logger.error(f"Corpus directory not found: {CORPUS_DIR}")
        return new_chunks, log
        
    doc_meta_map = load_document_metadata()

    for file_path in CORPUS_DIR.rglob("*"):
        if file_path.suffix.lower() not in ['.pdf', '.txt']:
            continue
            
        file_hash = compute_sha256(file_path)
        filename = file_path.name
        
        if log.get(filename) == file_hash:
            logger.info(f"Skipping {filename} (already processed)")
            continue
            
        logger.info(f"Processing {filename}...")
        
        pages = []
        if file_path.suffix.lower() == '.pdf':
            pages = extract_pdf_pages(file_path)
        elif file_path.suffix.lower() == '.txt':
            pages = extract_txt_file(file_path)
            
        if not pages:
            continue
            
        stem_slug = slugify(file_path.stem)
        file_meta = doc_meta_map.get(filename, {})
        
        for page_idx, p in enumerate(pages):
            page_text = p.get("text", "")
            
            meta = p.get("metadata", {})
            if meta.get("page_number") is not None:
                page_num = int(meta["page_number"])          # 1-based from pymupdf4llm
            elif meta.get("page") is not None:
                page_num = int(meta["page"]) + 1             # 0-based → 1-based
            else:
                page_num = page_idx + 1                      # guaranteed-correct fallback
            
            chunks_str = chunk_text(page_text, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)
            for c_idx, c_text in enumerate(chunks_str):
                chunk_id = f"{stem_slug}_p{page_num}_c{c_idx}"
                new_chunks.append({
                    "chunk_id": chunk_id,
                    "source_file": filename,
                    "source_type": "pdf",
                    "page_number": page_num,
                    "chunk_index": c_idx,
                    "text": c_text,
                    "collection": LEGAL_COLLECTION,
                    "jurisdiction": file_meta.get("jurisdiction", "IN"),
                    "document_type": file_meta.get("document_type", "act"),
                    "authority": file_meta.get("authority", "Government of India"),
                    "act_name": file_meta.get("act_name", filename),
                    "version": file_meta.get("version", "current"),
                    "effective_date": file_meta.get("effective_date", None),
                    "source_url": file_meta.get("source_url", None),
                    "section_or_article": file_meta.get("section_or_article", None),
                    "retrieved_at": file_meta.get("retrieved_at", "2026-08-27T11:14:00+05:30"),
                    "language": file_meta.get("language", "en"),
                    "sha256": file_hash,
                    "status": file_meta.get("status", "current")
                })
                
        # Update log with new hash
        log[filename] = file_hash
        
    return new_chunks, log

def process_tkdl_data() -> list[dict]:
    clean_file = Path(__file__).resolve().parent.parent / "data" / "tkdl_public" / "clean" / "clean_keyword_records.json"
    biopiracy_file = Path(__file__).resolve().parent.parent / "data" / "tkdl_public" / "biopiracy" / "biopiracy_cases.json"
    tkdl_chunks = []
    
    if not clean_file.exists():
        logger.warning(f"Public TKDL clean dataset not found at {clean_file}")
        return tkdl_chunks
        
    try:
        with open(clean_file, 'r', encoding='utf-8') as f:
            cdata = json.load(f)
            records = cdata.get("records", [])
            
        for idx, r in enumerate(records, 1):
            term = r.get("scientific_or_english_name", "").strip()
            category = r.get("category", "").strip()
            system = r.get("system", "").strip()
            ayurveda_name = r.get("ayurveda_name", "")
            unani_name = r.get("unani_name", "")
            siddha_name = r.get("siddha_name", "")
            common_name = r.get("common_name", "")
            source_url = r.get("source_url", "")
            provenance = r.get("provenance", [])

            local_names = []
            if ayurveda_name and ayurveda_name != "-": local_names.append(f"Ayurveda: {ayurveda_name}")
            if unani_name and unani_name != "-": local_names.append(f"Unani: {unani_name}")
            if siddha_name and siddha_name != "-": local_names.append(f"Siddha: {siddha_name}")
            local_names_str = "; ".join(local_names) if local_names else "N/A"

            record_id = f"TKDL-KW-{idx:04d}"
            text_content = (
                f"Term: {term}. Category: {category}. System: {system}. "
                f"Local/Sanskrit Names: {local_names_str}. Common/English Synonyms: {common_name}. "
                f"Data Provenance: {', '.join(provenance)}. Source URL: {source_url}."
            )

            tkdl_chunks.append({
                "chunk_id": record_id,
                "source_file": "clean_keyword_records.json",
                "page_number": None,
                "chunk_index": 0,
                "text": text_content,
                "collection": TKDL_COLLECTION,
                "record_id": record_id,
                "system": system,
                "category": category,
                "term_name": term,
                "local_names": local_names_str,
                "english_name": common_name,
                "synonyms": common_name,
                "source_url": source_url,
                "source_category": category,
                "data_status": "public_representative_keyword_data",
                "provenance": provenance
            })

        if biopiracy_file.exists():
            with open(biopiracy_file, 'r', encoding='utf-8') as f:
                bdata = json.load(f)
                b_recs = bdata.get("records", [])
                for idx, b in enumerate(b_recs, 1):
                    title = b.get("topic", b.get("title", f"Bio-Piracy Case {idx}"))
                    desc = b.get("description", b.get("summary", ""))
                    url = "https://www.tkdl.res.in/tkdl/langdefault/common/Biopiracy.asp"
                    record_id = f"TKDL-BIO-{idx:02d}"
                    text_content = f"Bio-Piracy Case Study: {title}. Description: {desc}. Source: {url}."

                    tkdl_chunks.append({
                        "chunk_id": record_id,
                        "source_file": "biopiracy_cases.json",
                        "page_number": None,
                        "chunk_index": 0,
                        "text": text_content,
                        "collection": TKDL_COLLECTION,
                        "record_id": record_id,
                        "system": "Bio-Piracy Defense",
                        "category": "Case Study",
                        "term_name": title,
                        "local_names": "N/A",
                        "english_name": title,
                        "synonyms": "",
                        "source_url": url,
                        "source_category": "Bio-Piracy",
                        "data_status": "public_biopiracy_data",
                        "provenance": ["TKDL Bio-Piracy Public Registry"]
                    })
    except Exception as e:
        logger.critical(f"Failed to decode public TKDL dataset: {e}")
        
    return tkdl_chunks

def process_json_file(file_path: Path, log: dict, collection: str = LEGAL_COLLECTION) -> tuple[list[dict], dict]:
    """
    Dedicated JSON dataset ingestion and chunking path.
    1. Safely loads JSON file.
    2. Detects structure (list of records, object with records array, or dictionary).
    3. Normalizes structured records into textual documents.
    4. Preserves source_type="json", source_file, record_id, and metadata.
    5. Chunks resulting text using existing tokenization strategy if large.
    """
    new_chunks = []
    if not file_path.exists():
        logger.error(f"JSON file not found: {file_path}")
        return new_chunks, log

    file_hash = compute_sha256(file_path)
    filename = file_path.name
    if log.get(filename) == file_hash:
        logger.info(f"Skipping {filename} (already processed)")
        return new_chunks, log

    logger.info(f"Processing JSON file {filename}...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Could not read JSON file {filename}: {e}")
        return new_chunks, log

    records = []
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ["records", "items", "data", "documents", "chunks"]:
            if key in data and isinstance(data[key], list):
                records = data[key]
                break
        if not records:
            records = [data]

    stem_slug = slugify(file_path.stem)

    for idx, rec in enumerate(records, 1):
        rec_id = str(rec.get("id", rec.get("record_id", f"rec_{idx}"))) if isinstance(rec, dict) else f"rec_{idx}"
        
        if isinstance(rec, dict):
            parts = []
            for k, v in rec.items():
                if v is not None and v != "":
                    if isinstance(v, (dict, list)):
                        v_str = json.dumps(v, ensure_ascii=False)
                    else:
                        v_str = str(v).strip()
                    parts.append(f"{k}: {v_str}")
            text_content = "\n".join(parts)
        else:
            text_content = str(rec).strip()

        if not text_content:
            continue

        chunks_str = chunk_text(text_content, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)
        for c_idx, c_text in enumerate(chunks_str):
            rec_id_slug = slugify(rec_id) or f"rec_{idx}"
            chunk_id = f"{stem_slug}_{rec_id_slug}_c{c_idx}"
            new_chunks.append({
                "chunk_id": chunk_id,
                "source_file": filename,
                "source_type": "json",
                "record_id": rec_id,
                "page_number": None,
                "chunk_index": c_idx,
                "text": c_text,
                "collection": collection,
                "sha256": file_hash
            })

    log[filename] = file_hash
    return new_chunks, log


def process_csv_file(file_path: Path, log: dict, collection: str = LEGAL_COLLECTION) -> tuple[list[dict], dict]:
    """
    Dedicated CSV dataset ingestion and chunking path.
    1. Parses CSV rows using csv.DictReader.
    2. Normalizes each row into structured key-value text.
    3. Preserves source_type="csv", source_file, row_number, and metadata.
    4. Chunks large text fields using existing tokenization strategy if large.
    """
    new_chunks = []
    if not file_path.exists():
        logger.error(f"CSV file not found: {file_path}")
        return new_chunks, log

    file_hash = compute_sha256(file_path)
    filename = file_path.name
    if log.get(filename) == file_hash:
        logger.info(f"Skipping {filename} (already processed)")
        return new_chunks, log

    logger.info(f"Processing CSV file {filename}...")

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            stem_slug = slugify(file_path.stem)
            
            for row_idx, row in enumerate(reader, 1):
                parts = []
                for col_name, val in row.items():
                    if val and str(val).strip():
                        parts.append(f"{col_name}: {str(val).strip()}")
                
                text_content = " | ".join(parts)
                if not text_content:
                    continue

                chunks_str = chunk_text(text_content, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS)
                for c_idx, c_text in enumerate(chunks_str):
                    chunk_id = f"{stem_slug}_row{row_idx}_c{c_idx}"
                    new_chunks.append({
                        "chunk_id": chunk_id,
                        "source_file": filename,
                        "source_type": "csv",
                        "row_number": row_idx,
                        "page_number": None,
                        "chunk_index": c_idx,
                        "text": c_text,
                        "collection": collection,
                        "sha256": file_hash
                    })

        log[filename] = file_hash
    except Exception as e:
        logger.error(f"Could not parse CSV file {filename}: {e}")

    return new_chunks, log

def append_jsonl(file_path: Path, records: list[dict]):
    if not records:
        return
    with open(file_path, 'a', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

def run_ingestion() -> None:
    ensure_dirs()
    log = load_ingestion_log(INGESTION_LOG)
    
    logger.info("Starting Phase 1: Ingestion...")
    new_legal_chunks, updated_log = process_legal_corpus(log)
    tkdl_chunks = process_tkdl_data()
    
    if new_legal_chunks:
        append_jsonl(LEGAL_CHUNKS, new_legal_chunks)
    
    # TKDL is small, typically we'd re-process entirely or skip.
    # To avoid appending duplicate TKDL records on re-runs where PDF changed but TKDL didn't,
    # we just rewrite the TKDL chunks file completely since it's small.
    if tkdl_chunks:
        with open(TKDL_CHUNKS, 'w', encoding='utf-8') as f:
            for r in tkdl_chunks:
                f.write(json.dumps(r) + "\n")
                
    save_ingestion_log(updated_log, INGESTION_LOG)
    
    files_processed = len(updated_log)
    logger.info(f"✅ Ingested {len(new_legal_chunks)} new legal chunks from corpus.")
    logger.info(f"✅ {len(tkdl_chunks)} TKDL records written.")
    logger.info("Phase 1 Complete.")
