import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Adjust DB_PATH relative to project root since it's run from there
DB_PATH = Path("data/shadow_cache.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                hash_id      TEXT PRIMARY KEY,
                query        TEXT,
                response_json TEXT,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hit_count    INTEGER   DEFAULT 0
            )
        """)
        # Add hit_count column to existing DBs that pre-date this schema change
        try:
            conn.execute("ALTER TABLE query_cache ADD COLUMN hit_count INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists — safe to ignore
        conn.commit()


# Initialise on import
init_db()


def get_cached_response(hash_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT response_json FROM query_cache WHERE hash_id = ?", (hash_id,)
        )
        row = cursor.fetchone()
        if row:
            # Increment hit counter (non-blocking best-effort)
            conn.execute(
                "UPDATE query_cache SET hit_count = hit_count + 1 WHERE hash_id = ?",
                (hash_id,),
            )
            conn.commit()
            return json.loads(row[0])
    return None


def set_cached_response(hash_id: str, query: str, response: dict) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO query_cache (hash_id, query, response_json, created_at, hit_count)
            VALUES (?, ?, ?, ?, 0)
            """,
            (hash_id, query, json.dumps(response), datetime.utcnow()),
        )
        conn.commit()


def get_cache_stats() -> dict:
    """Return cache statistics for debugging / prewarm verification."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT COUNT(*), SUM(hit_count), MAX(created_at) FROM query_cache"
        )
        total, total_hits, last_added = cursor.fetchone()
    return {
        "total_entries": total or 0,
        "total_cache_hits": total_hits or 0,
        "last_entry_at": last_added,
        "db_path": str(DB_PATH.resolve()),
    }
