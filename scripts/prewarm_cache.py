#!/usr/bin/env python3
"""
IP-SAKTI Sahayak — Shadow Cache Pre-Warmer
============================================
Fires all 4 demo scenarios + 15 standard Ayurveda IP queries against
the local API to fully populate shadow_cache.db before a live demo.

Usage:
  python scripts/prewarm_cache.py

Requirements:
  - uvicorn must be running on localhost:8000
  - Run from the project root directory
"""
import asyncio
import sys
import time
from typing import Any

import httpx

BASE = "http://localhost:8000"
TIMEOUT = 120.0   # InLegalBERT on CPU can take up to 90s for cold misses

# ---------------------------------------------------------------------------
# Query Sets
# ---------------------------------------------------------------------------

CHAT_QUERIES = [
    # 4 Core Demo Scenarios (RAG)
    {
        "query": (
            "I want to market an Ayurvedic dietary supplement for diabetes control. "
            "What IP protections, regulatory approvals, and ABS obligations apply?"
        ),
        "jurisdiction": "india",
        "language": "en",
    },
    # Standard Ayurveda IP & Regulatory Queries
    {"query": "Can I patent a novel Ashwagandha formulation combining it with Black Pepper extract?", "jurisdiction": "india",         "language": "en"},
    {"query": "What is the Section 3(p) bar under the Patents Act and how does it affect Ayurvedic products?", "jurisdiction": "india", "language": "en"},
    {"query": "ABS duties for wild-harvested Giloy (Tinospora cordifolia) extract commercialisation.", "jurisdiction": "india",         "language": "en"},
    {"query": "GI registration for a region-specific Ayurvedic preparation like Kottakkal formulas.", "jurisdiction": "india",          "language": "en"},
    {"query": "How does the WIPO GRATK Treaty protect Indian traditional knowledge internationally?", "jurisdiction": "international",   "language": "en"},
    {"query": "What forms do I need for an AYUSH drug manufacturing licence in India?", "jurisdiction": "india",                         "language": "en"},
    {"query": "Can a foreign company access Indian biological resources for Ayurvedic research?", "jurisdiction": "india",               "language": "en"},
    {"query": "What is the TKDL and how does it prevent biopiracy of Indian traditional knowledge?", "jurisdiction": "india",            "language": "en"},
    {"query": "Patent requirements for a phytopharmaceutical drug under CDSCO guidelines 2015.", "jurisdiction": "india",               "language": "en"},
    {"query": "What is the Nagoya Protocol's impact on exporting Ayurvedic products internationally?", "jurisdiction": "international", "language": "en"},
    {"query": "How to protect a proprietary Ayurvedic brand name under the Trade Marks Act 1999?", "jurisdiction": "india",             "language": "en"},
    {"query": "What are the advertising restrictions for Ayurvedic products under AYUSH guidelines 2023?", "jurisdiction": "india",     "language": "en"},
    {"query": "Biological Diversity Act exemptions for cultivated plants under the 2023 amendment.", "jurisdiction": "india",           "language": "en"},
    {"query": "How does the Designs Act 2000 protect novel Ayurvedic product packaging?", "jurisdiction": "india",                     "language": "en"},
    {"query": "TRIPS Agreement obligations for India regarding traditional knowledge protection.", "jurisdiction": "international",      "language": "en"},
]

ABS_CHECKS = [
    {"entity_type": "Foreign",  "resource_source": "Wild"},       # Demo scenario
    {"entity_type": "Indian",   "resource_source": "Cultivated"},
    {"entity_type": "Indian",   "resource_source": "Wild"},
]

TKDL_SCANS = [
    # Demo scenario
    {"claim_text": "Topical therapeutic formulation comprising 15% Curcuma longa extract for accelerating dermal wound repair in human subjects."},
    {"claim_text": "Oral composition comprising Withania somnifera (Ashwagandha) root extract for reducing cortisol levels and stress."},
    {"claim_text": "Method of treating type-2 diabetes using oral administration of Momordica charantia (Bitter Melon) fruit extract."},
    {"claim_text": "Herbal composition comprising Neem (Azadirachta indica) leaf extract for antibacterial and antifungal activity."},
]


# ---------------------------------------------------------------------------
# Async Warmer
# ---------------------------------------------------------------------------

async def warm_chat(client: httpx.AsyncClient, payload: dict[str, Any]) -> tuple[bool, str]:
    try:
        r = await client.post(f"{BASE}/api/v1/chat", json=payload, timeout=TIMEOUT)
        hit = r.headers.get("X-Cache-Status", "MISS")
        return True, hit
    except Exception as e:
        return False, str(e)


async def warm_abs(client: httpx.AsyncClient, payload: dict[str, Any]) -> tuple[bool, str]:
    try:
        r = await client.post(f"{BASE}/api/v1/abs-check", json=payload, timeout=30)
        return r.status_code == 200, str(r.status_code)
    except Exception as e:
        return False, str(e)


async def warm_tkdl(client: httpx.AsyncClient, payload: dict[str, Any]) -> tuple[bool, str]:
    try:
        r = await client.post(f"{BASE}/api/v1/tkdl-scan", json=payload, timeout=60)
        if r.status_code == 200:
            score = r.json().get("alert_score", "?")
            return True, f"score={score}"
        return False, str(r.status_code)
    except Exception as e:
        return False, str(e)


async def main() -> None:
    print("=" * 60)
    print("  IP-SAKTI Sahayak — Shadow Cache Pre-Warmer")
    print("=" * 60)
    print(f"  Backend:  {BASE}")
    print(f"  Timeout:  {TIMEOUT}s per RAG query")
    print()

    # Verify backend is alive
    try:
        async with httpx.AsyncClient() as probe:
            await probe.get(f"{BASE}/api/v1/cache/stats", timeout=5)
    except Exception:
        print("❌  Backend not reachable at", BASE)
        print("    Start uvicorn first: .venv/Scripts/uvicorn app.main:app --reload")
        sys.exit(1)

    passed = 0
    failed = 0

    async with httpx.AsyncClient() as client:

        # ── Chat / RAG ─────────────────────────────────────────────────
        print(f"[1/3] Warming {len(CHAT_QUERIES)} chat/RAG queries…")
        for i, payload in enumerate(CHAT_QUERIES, 1):
            t0 = time.monotonic()
            ok, status = await warm_chat(client, payload)
            elapsed = time.monotonic() - t0
            icon = "✅" if ok else "❌"
            q_short = payload["query"][:55] + "…"
            print(f"  {icon}  [{i:02d}/{len(CHAT_QUERIES)}] {q_short}  [{status}, {elapsed:.1f}s]")
            if ok: passed += 1
            else:  failed += 1

        # ── ABS Checks ─────────────────────────────────────────────────
        print(f"\n[2/3] Warming {len(ABS_CHECKS)} ABS compliance checks…")
        for payload in ABS_CHECKS:
            ok, status = await warm_abs(client, payload)
            icon = "✅" if ok else "❌"
            print(f"  {icon}  {payload['entity_type']}/{payload['resource_source']}  [{status}]")
            if ok: passed += 1
            else:  failed += 1

        # ── TKDL Scans ─────────────────────────────────────────────────
        print(f"\n[3/3] Warming {len(TKDL_SCANS)} TKDL biopiracy scans…")
        for i, payload in enumerate(TKDL_SCANS, 1):
            t0 = time.monotonic()
            ok, status = await warm_tkdl(client, payload)
            elapsed = time.monotonic() - t0
            icon = "✅" if ok else "❌"
            c_short = payload["claim_text"][:55] + "…"
            print(f"  {icon}  [{i}] {c_short}  [{status}, {elapsed:.1f}s]")
            if ok: passed += 1
            else:  failed += 1

    # ── Final Stats ────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"  Pre-warm complete: {passed} passed, {failed} failed")

    # Print cache stats
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{BASE}/api/v1/cache/stats", timeout=5)
            stats = r.json()
            print(f"  Cache entries:    {stats.get('total_entries', '?')}")
            print(f"  Total cache hits: {stats.get('total_cache_hits', '?')}")
            print(f"  DB path:          {stats.get('db_path', '?')}")
    except Exception:
        pass

    print("=" * 60)
    if failed:
        print(f"  ⚠️  {failed} queries failed — check backend logs")
        sys.exit(1)
    else:
        print("  ✅  Cache fully warmed — ready for demo!")


if __name__ == "__main__":
    asyncio.run(main())
