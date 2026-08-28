import asyncio
import httpx
import logging
import re
import html
from typing import List, Dict, Any
from app.schemas.payloads import PublicationRecord, ResearchSearchResult

logger = logging.getLogger("research_explorer")

USER_AGENT = "IP-SAKTI-Sahayak/1.0 (mailto:admin@ayush.gov.in)"

# Simple keyword normalization to support Ayurvedic scientific names
NORMALIZATION_MAP = {
    "ashwagandha": "Withania somnifera",
    "turmeric": "Curcuma longa",
    "neem": "Azadirachta indica",
    "tulsi": "Ocimum sanctum",
    "brahmi": "Bacopa monnieri"
}

def normalize_query(query: str) -> str:
    lower_q = query.lower()
    for common, scientific in NORMALIZATION_MAP.items():
        if common in lower_q and scientific.lower() not in lower_q:
            # Append scientific name for broader reach
            query += f" OR \"{scientific}\""
    return query

def clean_html(text: str) -> str:
    """Remove HTML tags and decode HTML entities from text."""
    if not text:
        return text
    # First unescape HTML entities (&lt; -> <, &gt; -> >, etc.)
    text = html.unescape(text)
    # Then strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

async def fetch_europe_pmc(query: str, client: httpx.AsyncClient) -> List[PublicationRecord]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "resultType": "core",
        "pageSize": 10
    }
    try:
        response = await client.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        results = data.get("resultList", {}).get("result", [])
        
        records = []
        for item in results:
            title = clean_html(item.get("title", "Unknown Title"))
            raw_abstract = item.get("abstractText", "")
            abstract = clean_html(raw_abstract) if raw_abstract else "No abstract available."
            doi = item.get("doi", "")
            url = f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/MED/{item.get('pmid', '')}"
            
            # Extract authors
            authors_list = item.get("authorList", {}).get("author", [])
            authors = [a.get("fullName", "") for a in authors_list if a.get("fullName")]
            
            # Extract additional fields
            year = int(item.get("pubYear")) if item.get("pubYear") else None
            journal = item.get("journalTitle")
            open_access = (item.get("isOpenAccess") == "Y")
            
            records.append(PublicationRecord(
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                url=url,
                doi=doi,
                source="Europe PMC",
                open_access=open_access
            ))
        return records
    except Exception as e:
        logger.error(f"Europe PMC search failed: {e}")
        return []

async def fetch_openalex(query: str, client: httpx.AsyncClient) -> List[PublicationRecord]:
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "mailto": "admin@ayush.gov.in",
        "per-page": 10
    }
    try:
        response = await client.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        records = []
        for item in results:
            title = clean_html(item.get("title") or "Unknown Title")
            abstract_inverted = item.get("abstract_inverted_index")
            abstract = "No abstract available."
            if abstract_inverted:
                # Reconstruct abstract from inverted index
                words = []
                for word, positions in abstract_inverted.items():
                    for pos in positions:
                        words.append((pos, word))
                words.sort(key=lambda x: x[0])
                abstract = " ".join([w[1] for w in words])
                
            raw_doi = item.get("doi") or ""
            doi = raw_doi.replace("https://doi.org/", "") if raw_doi else ""
            url = item.get("doi") or item.get("id", "")
            
            authorships = item.get("authorships", [])
            authors = [a.get("author", {}).get("display_name", "") for a in authorships]
            
            year = item.get("publication_year")
            
            prim_loc = item.get("primary_location") or {}
            source = prim_loc.get("source") or {}
            journal = source.get("display_name")
            
            oa = item.get("open_access") or {}
            open_access = oa.get("is_oa", False)
            if open_access:
                oa_url = oa.get("oa_url")
                if oa_url:
                    url = oa_url
            
            records.append(PublicationRecord(
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                url=url,
                doi=doi,
                source="OpenAlex",
                open_access=open_access
            ))
        return records
    except Exception as e:
        logger.error(f"OpenAlex search failed: {e}")
        return []

async def fetch_crossref(query: str, client: httpx.AsyncClient) -> List[PublicationRecord]:
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "mailto": "admin@ayush.gov.in",
        "rows": 10
    }
    try:
        response = await client.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        results = data.get("message", {}).get("items", [])
        
        records = []
        for item in results:
            title_list = item.get("title", [])
            title = clean_html(title_list[0]) if title_list else "Unknown Title"
            abstract = clean_html(item.get("abstract", "No abstract available."))
            
            doi = item.get("DOI", "")
            url = item.get("URL", f"https://doi.org/{doi}")
            
            authors_list = item.get("author", [])
            authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list]
            
            year = None
            published_print = item.get("published-print", {}).get("date-parts", [[]])
            if published_print and published_print[0]:
                year = published_print[0][0]
            if not year:
                published_online = item.get("published-online", {}).get("date-parts", [[]])
                if published_online and published_online[0]:
                    year = published_online[0][0]
                    
            journal = item.get("container-title", [])
            journal = journal[0] if journal else None
            
            # Crossref links usually contain fulltext links if open access
            open_access = False
            link_list = item.get("link", [])
            for ln in link_list:
                if ln.get("intended-application") == "text-mining" or ln.get("content-type") == "application/pdf":
                    open_access = True
                    url = ln.get("URL", url)
                    break
            
            records.append(PublicationRecord(
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                url=url,
                doi=doi,
                source="Crossref",
                open_access=open_access
            ))
        return records
    except Exception as e:
        logger.error(f"Crossref search failed: {e}")
        return []

async def search_research_literature(query: str) -> ResearchSearchResult:
    """
    Search across multiple academic databases concurrently.
    """
    normalized_query = normalize_query(query)
    logger.info(f"Research search: '{query}' -> '{normalized_query}'")
    
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(headers=headers) as client:
        results = await asyncio.gather(
            fetch_europe_pmc(normalized_query, client),
            fetch_openalex(normalized_query, client),
            fetch_crossref(normalized_query, client),
            return_exceptions=True
        )
        
    all_records = []
    for res in results:
        if isinstance(res, list):
            all_records.extend(res)
            
    merged_records = {}
    deduped_records = []
    
    for record in all_records:
        if not record.sources:
            record.sources = [record.source]
        if not record.source_urls:
            record.source_urls = {record.source: record.url}
            
        key = f"doi:{record.doi.lower().strip()}" if record.doi else f"title:{record.title.lower().strip()}"
        
        if key in merged_records:
            existing = merged_records[key]
            if record.source not in existing.sources:
                existing.sources.append(record.source)
                existing.source_urls[record.source] = record.url
                
            # Prefer longer abstract
            if len(record.abstract) > len(existing.abstract) and record.abstract != "No abstract available.":
                existing.abstract = record.abstract
                
            # Prefer open access URL as primary
            if record.open_access and not existing.open_access:
                existing.open_access = True
                existing.url = record.url
        else:
            merged_records[key] = record
            deduped_records.append(record)
            
    for record in deduped_records:
        # Limit abstract length
        if len(record.abstract) > 800:
            record.abstract = record.abstract[:797] + "..."
        
    return ResearchSearchResult(
        query_analyzed=normalized_query,
        records=deduped_records[:25]
    )
