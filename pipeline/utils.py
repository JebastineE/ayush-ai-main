import logging
import hashlib
import json
import os
import tempfile
from pathlib import Path
from .config import PROCESSED_DIR, QDRANT_PATH

def setup_logging(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def compute_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 64K
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

logger = setup_logging(__name__)

def load_ingestion_log(log_path: Path) -> dict:
    if not log_path.exists():
        return {}
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.warning(f"Could not load ingestion log at {log_path} ({e}). Starting fresh.")
        return {}

def save_ingestion_log(log: dict, log_path: Path) -> None:
    # Atomically save the log
    dir_path = log_path.parent
    dir_path.mkdir(parents=True, exist_ok=True)
    
    fd, temp_path = tempfile.mkstemp(dir=dir_path, text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)
    
    os.replace(temp_path, log_path)

def ensure_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    QDRANT_PATH.mkdir(parents=True, exist_ok=True)
