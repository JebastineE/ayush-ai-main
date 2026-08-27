"""
DPDP Privacy Guardrails Middleware
====================================
Digital Personal Data Protection Act (DPDP) 2023 compliance layer.

Scrubs PII from:
  - Incoming user queries (before RAG retrieval)
  - Outgoing LLM responses (before returning to client)

PII patterns covered:
  - Aadhaar numbers (12-digit, with or without spaces/dashes)
  - PAN card numbers (ABCDE1234F format)
  - Indian mobile numbers (10-digit starting with 6-9, optionally +91)
  - Email addresses (RFC 5322 simplified)

Audit trail: logs WHAT type of PII was redacted (never the actual value).
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger("dpdp_middleware")

# ---------------------------------------------------------------------------
# PII Pattern Registry
# ---------------------------------------------------------------------------

_PII_PATTERNS = [
    {
        "name": "Aadhaar",
        # 12-digit Aadhaar: xxxx xxxx xxxx or xxxx-xxxx-xxxx or continuous
        "pattern": re.compile(
            r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
            re.IGNORECASE
        ),
        "replacement": "[AADHAAR-REDACTED]",
    },
    {
        "name": "PAN",
        # PAN: 5 alpha + 4 digits + 1 alpha
        "pattern": re.compile(
            r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
            re.IGNORECASE
        ),
        "replacement": "[PAN-REDACTED]",
    },
    {
        "name": "IndianMobile",
        # +91 optional, then 10-digit starting with 6-9
        "pattern": re.compile(
            r'(\+91[\s\-]?)?[6-9]\d{9}\b'
        ),
        "replacement": "[PHONE-REDACTED]",
    },
    {
        "name": "Email",
        "pattern": re.compile(
            r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
        ),
        "replacement": "[EMAIL-REDACTED]",
    },
]


def scrub_pii(text: str) -> Tuple[str, list[str]]:
    """
    Scrub all detected PII from the input text.

    Returns:
        Tuple of (scrubbed_text, list_of_redacted_field_types)
    """
    redacted_types: list[str] = []

    for rule in _PII_PATTERNS:
        matches = rule["pattern"].findall(text)
        if matches:
            redacted_types.append(rule["name"])
            text = rule["pattern"].sub(rule["replacement"], text)

    if redacted_types:
        logger.info(
            f"🔒 [DPDP] Redacted PII fields: {redacted_types}  "
            f"(values not logged per DPDP §8)"
        )

    return text, redacted_types
