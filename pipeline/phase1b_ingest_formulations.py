"""
Phase 1B: Ingest formulation data for the Formulation Classifier.

Sources:
  - data/legal_corpus/Ayurvedic Pharmacopoeia of India All Volume.pdf (Part II compound formulations)
  - data/class_data/tkdl_formulations/tkdl_sample_dataset.json (60 TKDL formulations)

Output:
  - data/processed/formulation_chunks.jsonl
"""

import json
import re
from pathlib import Path
from typing import Optional

import pymupdf4llm

from .config import BASE_DIR, MODEL_NAME
from .utils import setup_logging

logger = setup_logging(__name__)

API_PDF = BASE_DIR / "data" / "legal_corpus" / "Ayurvedic Pharmacopoeia of India All Volume.pdf"
TKDL_FORMULATIONS = BASE_DIR / "data" / "class_data" / "tkdl_formulations" / "tkdl_sample_dataset.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "formulation_chunks.jsonl"

PART_II_MARKERS = [
    r"PART\s*[-–—]\s*II",
    r"FORMULATIONS",
    r"COMPOUND\s+FORMULATIONS",
]

DOSAGE_FORMS = [
    "Churna", "Vati", "Gutika", "Kashaya", "Kwatha", "Asava", "Arishta",
    "Ghrita", "Taila", "Bhasma", "Pishti", "Lepa", "Avaleha", "Rasayana",
    "Guggulu", "Mandura", "Lauha", "Parpati", "Rasa",
]


def extract_pdf_text(pdf_path: Path) -> list[dict]:
    """Extract pages from the Pharmacopoeia PDF."""
    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return []
    try:
        pages = pymupdf4llm.to_markdown(str(pdf_path), page_chunks=True)
        logger.info(f"Extracted {len(pages)} pages from {pdf_path.name}")
        return pages
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return []


def detect_part_boundaries(pages: list[dict]) -> list[dict]:
    """
    Scan pages to find Part I vs Part II boundaries.
    Returns list of {"page_start", "page_end", "part", "volume"} ranges.
    """
    boundaries = []
    current_part = "I"
    current_volume = "I"
    part_start = 0

    combined_pattern = re.compile("|".join(PART_II_MARKERS), re.IGNORECASE)
    vol_pattern = re.compile(r"VOLUME\s*[-–—:]\s*(I{1,3}|IV|V|VI|[1-6])", re.IGNORECASE)

    for idx, page in enumerate(pages):
        text = page.get("text", "")[:500]

        vol_match = vol_pattern.search(text)
        if vol_match:
            new_vol = vol_match.group(1).upper()
            if new_vol != current_volume:
                if idx > part_start:
                    boundaries.append({
                        "page_start": part_start,
                        "page_end": idx - 1,
                        "part": current_part,
                        "volume": current_volume,
                    })
                current_volume = new_vol
                part_start = idx
                current_part = "I"

        if combined_pattern.search(text):
            if current_part != "II":
                if idx > part_start:
                    boundaries.append({
                        "page_start": part_start,
                        "page_end": idx - 1,
                        "part": current_part,
                        "volume": current_volume,
                    })
                current_part = "II"
                part_start = idx

    boundaries.append({
        "page_start": part_start,
        "page_end": len(pages) - 1,
        "part": current_part,
        "volume": current_volume,
    })

    return boundaries


def parse_formulation_block(text: str, page_num: int, volume: str) -> Optional[dict]:
    """
    Attempt regex-based extraction of a formulation monograph block.
    Returns structured record or None if parsing fails.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) < 3:
        return None

    formula_name = lines[0].strip("# ").strip("*").strip()
    if len(formula_name) > 120 or len(formula_name) < 3:
        return None

    ingredients = []
    method = None
    indications = []
    source_text = text[:1500]

    ingredient_pattern = re.compile(
        r"(?:\d+[\.\)]\s*)?([A-Z][a-z]+(?:\s+[a-z]+)*)"
        r"(?:\s*\(([^)]+)\))?"
        r"(?:\s*[-–—]\s*([\w\s]+))?"
        r"(?:\s*[-–—:]\s*(\d+[\w\s./]*))?",
    )

    in_ingredients = False
    in_indications = False

    for line in lines[1:]:
        lower = line.lower()

        if any(kw in lower for kw in ["composition", "ingredients", "formula", "contents"]):
            in_ingredients = True
            in_indications = False
            continue
        if any(kw in lower for kw in ["indication", "therapeutic", "uses", "rogadhikara"]):
            in_ingredients = False
            in_indications = True
            continue
        if any(kw in lower for kw in ["method", "preparation", "process", "mana"]):
            in_ingredients = False
            in_indications = False
            method_match = re.search(r"(?:method|preparation|process)[:\s]*(.+)", line, re.IGNORECASE)
            if method_match:
                method = method_match.group(1).strip()
            else:
                for form in DOSAGE_FORMS:
                    if form.lower() in lower:
                        method = form
                        break
            continue

        if in_ingredients:
            m = ingredient_pattern.match(line)
            if m:
                ingredients.append({
                    "name": m.group(1).strip(),
                    "botanical_name": m.group(2).strip() if m.group(2) else "",
                    "part_used": m.group(3).strip() if m.group(3) else "",
                    "quantity": m.group(4).strip() if m.group(4) else "",
                })
            elif line and not line.startswith("#"):
                parts = re.split(r"\s{2,}|\t|[-–—]", line)
                if parts:
                    ingredients.append({
                        "name": parts[0].strip(),
                        "botanical_name": parts[1].strip() if len(parts) > 1 else "",
                        "part_used": parts[2].strip() if len(parts) > 2 else "",
                        "quantity": parts[3].strip() if len(parts) > 3 else "",
                    })

        if in_indications:
            clean = re.sub(r"^[\d\.\)\-–—\*\•]+\s*", "", line).strip()
            if clean and len(clean) > 2:
                indications.append(clean)

    if not method:
        for form in DOSAGE_FORMS:
            if form.lower() in formula_name.lower():
                method = form
                break

    if not ingredients and not indications:
        return None

    return {
        "formula_name": formula_name,
        "part": "II",
        "volume": volume,
        "page": page_num,
        "ingredients": ingredients,
        "method": method or "Unknown",
        "indications": indications,
        "source_text": source_text,
    }


def extract_formulations_from_pages(pages: list[dict], boundaries: list[dict]) -> list[dict]:
    """Extract formulation records from Part II pages."""
    formulations = []

    part_ii_ranges = [b for b in boundaries if b["part"] == "II"]
    if not part_ii_ranges:
        logger.warning("No Part II boundaries detected; scanning all pages")
        part_ii_ranges = [{"page_start": 0, "page_end": len(pages) - 1, "volume": "I"}]

    for boundary in part_ii_ranges:
        volume = boundary["volume"]
        for page_idx in range(boundary["page_start"], min(boundary["page_end"] + 1, len(pages))):
            page = pages[page_idx]
            text = page.get("text", "")
            if not text.strip():
                continue

            meta = page.get("metadata", {})
            page_num = meta.get("page_number", meta.get("page", page_idx))
            if isinstance(page_num, int) and page_num == 0:
                page_num = page_idx + 1
            elif not isinstance(page_num, int):
                page_num = page_idx + 1

            blocks = re.split(r"\n#{1,3}\s+", text)
            for block in blocks:
                if len(block.strip()) < 50:
                    continue
                record = parse_formulation_block(block, page_num, volume)
                if record:
                    formulations.append(record)

    logger.info(f"Extracted {len(formulations)} formulation records from Pharmacopoeia")
    return formulations


def load_tkdl_formulations() -> list[dict]:
    """Load and validate the 60 TKDL sample formulations."""
    if not TKDL_FORMULATIONS.exists():
        logger.error(f"TKDL formulations not found: {TKDL_FORMULATIONS}")
        return []

    with open(TKDL_FORMULATIONS, "r", encoding="utf-8") as f:
        records = json.load(f)

    validated = []
    required_keys = {"id", "formulation_name", "ingredients", "therapeutic_use"}

    for rec in records:
        if not isinstance(rec, dict):
            continue
        if not required_keys.issubset(rec.keys()):
            logger.warning(f"TKDL record missing keys: {rec.get('id', 'unknown')}")
            continue
        validated.append(rec)

    logger.info(f"Loaded {len(validated)} validated TKDL formulation records")
    return validated


def formulation_to_chunk(record: dict, source: str) -> dict:
    """Convert a formulation record to a chunk for vectorization."""
    if source == "pharmacopoeia":
        ingredient_names = [i["name"] for i in record.get("ingredients", [])]
        text = (
            f"{record['formula_name']}. "
            f"Ingredients: {', '.join(ingredient_names)}. "
            f"Method: {record.get('method', 'Unknown')}. "
            f"Indications: {', '.join(record.get('indications', []))}."
        )
        chunk_id = f"API_{record['volume']}_p{record['page']}_{re.sub(r'[^a-z0-9]+', '_', record['formula_name'].lower())}"
        return {
            "chunk_id": chunk_id,
            "source_file": "Ayurvedic Pharmacopoeia of India All Volume.pdf",
            "collection": "classical_formulations",
            "text": text,
            "formula_name": record["formula_name"],
            "part": record["part"],
            "volume": record["volume"],
            "page": record["page"],
            "ingredients": record["ingredients"],
            "method": record["method"],
            "indications": record["indications"],
            "source_text": record.get("source_text", ""),
        }
    else:
        ingredients = record.get("ingredients", [])
        if isinstance(ingredients, list):
            ing_text = ", ".join(ingredients)
        else:
            ing_text = str(ingredients)

        text = (
            f"{record['formulation_name']}. "
            f"Ingredients: {ing_text}. "
            f"Therapeutic use: {record.get('therapeutic_use', '')}."
        )
        chunk_id = f"TKDL_{record['id']}"
        return {
            "chunk_id": chunk_id,
            "source_file": "tkdl_sample_dataset.json",
            "collection": "tkdl_formulations",
            "text": text,
            "formulation_name": record["formulation_name"],
            "ingredients": ingredients,
            "therapeutic_use": record.get("therapeutic_use", ""),
            "ipc_code": record.get("ipc_code", ""),
            "tkrc_code": record.get("tkrc_code", ""),
            "system": record.get("system", ""),
        }


def run_formulation_ingestion() -> None:
    """Main entry point for formulation ingestion."""
    logger.info("Starting Phase 1B: Formulation Ingestion...")

    all_chunks = []

    # 1. Process Pharmacopoeia PDF
    pages = extract_pdf_text(API_PDF)
    if pages:
        boundaries = detect_part_boundaries(pages)
        logger.info(f"Detected {len(boundaries)} part/volume boundaries")
        formulations = extract_formulations_from_pages(pages, boundaries)
        for record in formulations:
            chunk = formulation_to_chunk(record, "pharmacopoeia")
            all_chunks.append(chunk)

    # 2. Load TKDL formulations (pass-through)
    tkdl_records = load_tkdl_formulations()
    for record in tkdl_records:
        chunk = formulation_to_chunk(record, "tkdl")
        all_chunks.append(chunk)

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    logger.info(f"Phase 1B complete. Wrote {len(all_chunks)} chunks to {OUTPUT_FILE.name}")
    logger.info(f"  Pharmacopoeia formulations: {len(all_chunks) - len(tkdl_records)}")
    logger.info(f"  TKDL formulations: {len(tkdl_records)}")


if __name__ == "__main__":
    run_formulation_ingestion()
