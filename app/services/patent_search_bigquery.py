"""
Google BigQuery Patent Search Service
======================================
Searches the Google Patents Public Dataset for related patent records.

IMPORTANT:
- This service is ONLY used by the Biopiracy Scanner
- It does NOT modify or interact with the Legal Assistant RAG system
- It keeps patent data in BigQuery (no Qdrant integration)
- Results are for review purposes only, not confirmation of biopiracy

Dataset: `patents-public-data.patents.publications`
"""
import logging
import os
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("patent_search_bigquery")

# BigQuery configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
MAX_RESULTS = 20  # Limit results per query

# Log BigQuery configuration for debugging
if PROJECT_ID:
    logger.info(f"BigQuery configured with project: {PROJECT_ID}")
else:
    logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set")


# Plant name normalization mapping
PLANT_NORMALIZATION = {
    "ashwagandha": ["ashwagandha", "withania somnifera", "withania", "indian ginseng"],
    "turmeric": ["turmeric", "curcuma longa", "curcuma", "haldi"],
    "neem": ["neem", "azadirachta indica", "azadirachta"],
    "tulsi": ["tulsi", "ocimum sanctum", "holy basil", "ocimum tenuiflorum"],
    "ginger": ["ginger", "zingiber officinale", "zingiber"],
    "giloy": ["giloy", "tinospora cordifolia", "guduchi"],
    "brahmi": ["brahmi", "bacopa monnieri", "bacopa"],
    "shatavari": ["shatavari", "asparagus racemosus"],
}


def normalize_plant_terms(text: str) -> List[str]:
    """
    Extract and normalize plant terms from the input text.
    Returns a list of normalized search terms.
    """
    text_lower = text.lower()
    terms = []

    for key, variants in PLANT_NORMALIZATION.items():
        for variant in variants:
            if variant in text_lower:
                # Add all variants for this plant
                terms.extend(variants)
                break

    # If no specific plants found, extract generic keywords
    if not terms:
        # Extract potential keywords (simple approach)
        words = text_lower.split()
        # Filter common words
        stop_words = {"a", "an", "the", "for", "and", "or", "of", "in", "to", "with", "comprising", "containing"}
        terms = [w for w in words if len(w) > 3 and w not in stop_words][:10]

    return list(set(terms))  # Remove duplicates


def normalize_patent_number(publication_number: str) -> str:
    """
    Normalize patent publication number for Google Patents URL.
    Removes hyphens from publication numbers.

    Example:
        CN-224098353-U → CN224098353U
        US-12589067-B2 → US12589067B2
        WO-2026062355-A1 → WO2026062355A1
    """
    if not publication_number:
        return ""
    return publication_number.strip().replace("-", "")


def search_patents_bigquery(claim_text: str) -> Dict[str, Any]:
    """
    Search Google Patents Public Dataset via BigQuery.

    Args:
        claim_text: The patent claim or formulation text to search for

    Returns:
        Dictionary containing:
        - query: The original query text
        - search_terms: Extracted search terms
        - results: List of patent records
        - total_found: Number of results
        - error: Error message if search failed
    """
    if not claim_text or len(claim_text.strip()) < 10:
        return {
            "query": claim_text,
            "search_terms": [],
            "results": [],
            "total_found": 0,
            "error": "Search text must be at least 10 characters"
        }

    # Extract and normalize search terms
    search_terms = normalize_plant_terms(claim_text)

    if not search_terms:
        return {
            "query": claim_text,
            "search_terms": [],
            "results": [],
            "total_found": 0,
            "error": "Could not extract searchable terms from the input"
        }

    # Check if BigQuery is configured
    if not PROJECT_ID:
        logger.warning("GOOGLE_CLOUD_PROJECT not set - BigQuery unavailable")
        return {
            "query": claim_text,
            "search_terms": search_terms,
            "results": [],
            "total_found": 0,
            "error": "BigQuery is not configured. Set GOOGLE_CLOUD_PROJECT environment variable."
        }

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # Build parameterized query
        # Search in title and abstract fields
        query = _build_search_query(search_terms)

        logger.info(f"Executing BigQuery search for terms: {search_terms[:5]}")

        # Execute query with timeout
        query_job = client.query(query, timeout=30.0)
        results = list(query_job.result(max_results=MAX_RESULTS))

        # Format results
        patent_records = []
        for row in results:
            pub_number = row.get("publication_number") or ""
            # Normalize publication number for Google Patents URL (remove hyphens)
            normalized_pub_number = normalize_patent_number(pub_number)

            patent_records.append({
                "publication_number": pub_number,
                "title": (row.get("title_localized") or "")[:500],
                "abstract": (row.get("abstract_localized") or "")[:1000],
                "assignee": (row.get("assignee") or "Unknown")[:200],
                "country_code": row.get("country_code") or "",
                "publication_date": str(row.get("publication_date")) if row.get("publication_date") else "",
                "cpc_code": row.get("cpc_code") or "",
                "source_url": f"https://patents.google.com/patent/{normalized_pub_number}" if normalized_pub_number else ""
            })

        return {
            "query": claim_text[:500],
            "search_terms": search_terms[:10],
            "results": patent_records,
            "total_found": len(patent_records),
            "error": None
        }

    except google_exceptions.NotFound:
        logger.error("BigQuery dataset not found")
        return {
            "query": claim_text,
            "search_terms": search_terms,
            "results": [],
            "total_found": 0,
            "error": "Patent dataset not accessible"
        }
    except google_exceptions.Forbidden as e:
        error_str = str(e)
        logger.error(f"BigQuery access denied: {error_str}")
        logger.error(f"PROJECT_ID: '{PROJECT_ID}'")
        logger.error(f"Query: {claim_text}")

        # Provide specific error message for quota issues
        if "quota" in error_str.lower() or "exceeded" in error_str.lower():
            error_message = "BigQuery query quota exceeded. Enable billing on Google Cloud project or wait for quota reset."
        else:
            error_message = "Access to patent dataset denied. Check credentials."

        return {
            "query": claim_text,
            "search_terms": search_terms,
            "results": [],
            "total_found": 0,
            "error": error_message
        }
    except Exception as e:
        logger.error(f"BigQuery search failed: {e}")
        return {
            "query": claim_text,
            "search_terms": search_terms,
            "results": [],
            "total_found": 0,
            "error": "Patent search temporarily unavailable"
        }


def _build_search_query(terms: List[str]) -> str:
    """
    Build an optimized BigQuery SQL query with minimal bytes scanned.

    Optimization strategy:
    1. Filter by CPC classification (A61K - pharmaceutical preparations) FIRST
    2. Narrow date range to last 8 years (reduces partitions scanned)
    3. Filter by country codes early
    4. Then apply text search on this smaller dataset

    This reduces bytes scanned from ~TB to ~GB range.

    Note: title_localized and abstract_localized are ARRAY<STRUCT<text STRING, language STRING, truncated BOOL>>
    """
    # Build WHERE clause with OR conditions for each term
    # Using LOWER() for case-insensitive search on ARRAY elements
    conditions = []
    for term in terms[:10]:  # Limit to 10 terms to avoid query complexity
        # Escape single quotes in term
        safe_term = term.replace("'", "\\'")
        # Search within title_localized array using EXISTS with UNNEST
        conditions.append(f"EXISTS(SELECT 1 FROM UNNEST(p.title_localized) AS t WHERE LOWER(t.text) LIKE '%{safe_term}%')")
        # Search within abstract_localized array using EXISTS with UNNEST
        conditions.append(f"EXISTS(SELECT 1 FROM UNNEST(p.abstract_localized) AS a WHERE LOWER(a.text) LIKE '%{safe_term}%')")

    text_search_clause = " OR ".join(conditions)

    # Build optimized query with CPC filter as PRIMARY filter
    # CPC A61K = Preparations for medical, dental, or toilet purposes
    # CPC A61K36 = Medicinal preparations from plants/algae/fungi (most relevant for biopiracy)
    # Filter order matters: CPC + Date + Country first, then text search
    query = f"""
    SELECT
        p.publication_number,
        (SELECT text FROM UNNEST(p.title_localized) WHERE language = 'en' LIMIT 1) as title_localized,
        (SELECT text FROM UNNEST(p.abstract_localized) WHERE language = 'en' LIMIT 1) as abstract_localized,
        ARRAY_TO_STRING(p.assignee, ', ') as assignee,
        p.country_code,
        p.publication_date,
        (SELECT STRING_AGG(c.code, ', ') FROM UNNEST(p.cpc) as c LIMIT 5) as cpc_code
    FROM
        `patents-public-data.patents.publications` p
    WHERE
        -- PRIMARY FILTER: CPC classification for pharmaceutical/medicinal preparations
        -- This dramatically reduces dataset size before text search
        EXISTS(SELECT 1 FROM UNNEST(p.cpc) AS cpc WHERE cpc.code LIKE 'A61K%')
        -- Date filter: Last 8 years (leverages table partitioning)
        AND p.publication_date >= 20160101
        -- Country filter: Focus on major patent jurisdictions
        AND p.country_code IN ('US', 'EP', 'WO', 'IN', 'CN', 'JP')
        -- Text search: Now runs on much smaller filtered dataset
        AND ({text_search_clause})
    ORDER BY
        p.publication_date DESC
    LIMIT {MAX_RESULTS}
    """

    return query
