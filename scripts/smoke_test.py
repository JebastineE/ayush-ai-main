"""Quick smoke test for all new endpoints."""
import httpx, json, sys, io

# Force UTF-8 stdout on Windows CP1252 terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "http://localhost:8000"
ok = True

print("=" * 55)
print("  IP-SAKTI Endpoint Smoke Tests")
print("=" * 55)

# 1. Cache stats
try:
    r = httpx.get(f"{BASE}/api/v1/cache/stats", timeout=5)
    d = r.json()
    print(f"\n[1] /api/v1/cache/stats  -> {r.status_code}")
    print(f"    entries:    {d.get('total_entries')}")
    print(f"    cache hits: {d.get('total_cache_hits')}")
    assert r.status_code == 200
    print("    PASS")
except Exception as e:
    print(f"    FAIL: {e}"); ok = False

# 2. TKDL scan
try:
    payload = {"claim_text": "Topical formulation comprising Curcuma longa extract for wound healing."}
    r = httpx.post(f"{BASE}/api/v1/tkdl-scan", json=payload, timeout=30)
    d = r.json()
    print(f"\n[2] /api/v1/tkdl-scan  -> {r.status_code}")
    print(f"    alert_level: {d.get('alert_level')}")
    print(f"    alert_score: {d.get('alert_score')}")
    print(f"    matches:     {len(d.get('matched_records', []))}")
    print(f"    section_3p:  {d.get('section_3p_applicable')}")
    assert r.status_code == 200
    assert "alert_level" in d
    print("    PASS")
except Exception as e:
    print(f"    FAIL: {e}"); ok = False

# 3. Escalation PDF
try:
    payload = {
        "messages": [
            {"role": "user",      "content": "Can I patent an Ashwagandha formulation?"},
            {"role": "assistant", "content": "Under Patents Act Section 3(p), classical Ayurvedic formulas face a patent bar."},
        ],
        "session_id": "smoke-test-001"
    }
    r = httpx.post(f"{BASE}/api/v1/escalate", json=payload, timeout=15)
    ctype = r.headers.get("content-type", "")
    print(f"\n[3] /api/v1/escalate  -> {r.status_code}")
    print(f"    content-type: {ctype}")
    print(f"    PDF size:     {len(r.content)} bytes")
    assert r.status_code == 200
    assert "pdf" in ctype
    assert len(r.content) > 1000
    print("    PASS")
except Exception as e:
    print(f"    FAIL: {e}"); ok = False

print("\n" + "=" * 55)
print("  ALL PASSED!" if ok else "  SOME TESTS FAILED -- check uvicorn logs")
print("=" * 55)
sys.exit(0 if ok else 1)
