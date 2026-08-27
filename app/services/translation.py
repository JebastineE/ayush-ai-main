"""
Translation Service — Gemini-Powered Multilingual Support
==========================================================
Uses the Gemini LLM for bidirectional translation between
Indian vernacular languages and English.

Replaces the previous deep_translator (Google Translate HTTP) dependency.
Standardized on the same Gemini model used throughout the pipeline.
"""
import os
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-3.5-flash-lite"

_LANG_NAMES: dict[str, str] = {
    "hi": "Hindi",    "bn": "Bengali",    "ta": "Tamil",
    "te": "Telugu",   "mr": "Marathi",    "gu": "Gujarati",
    "kn": "Kannada",  "ml": "Malayalam",  "pa": "Punjabi",
    "or": "Odia",     "as": "Assamese",   "ur": "Urdu",
    "sd": "Sindhi",   "sa": "Sanskrit",
}

# Lazy-initialised to avoid import-time failures if the key is absent.
_client: genai.Client | None = None


def _get_client() -> genai.Client | None:
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("No Gemini API key — translation will be skipped (queries passed as-is).")
        return None
    try:
        _client = genai.Client(api_key=api_key, vertexai=False)
        return _client
    except Exception as exc:
        logger.warning(f"Could not initialise Gemini translation client: {exc}")
        return None


def translate_to_english(text: str) -> str:
    """
    Translate any Indian vernacular text to English via Gemini.
    Returns the original text unchanged if already English or on failure.
    """
    if not text or not text.strip():
        return text
    client = _get_client()
    if not client:
        return text
    try:
        prompt = (
            "Translate the following text to English. "
            "If it is already in English, return it EXACTLY as-is without any modification. "
            "Preserve all legal citations, section numbers, and technical terms. "
            "Return ONLY the translated text — no preamble, no explanation.\n\n"
            f"{text}"
        )
        resp = client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        result = resp.text.strip() if resp and resp.text else ""
        return result or text
    except Exception as exc:
        logger.warning(f"Gemini translation → English failed: {exc}. Using original text.")
        return text


def translate_to_source_lang(text: str, target_lang: str) -> str:
    """
    Translate English text into the specified Indian language via Gemini.
    No-op if target_lang is 'en', 'auto', or empty.
    Legal terms (act names, section numbers) are preserved in English.
    """
    if not text or not text.strip() or target_lang in ("en", "auto", ""):
        return text
    client = _get_client()
    if not client:
        return text

    lang_name = _LANG_NAMES.get(target_lang, target_lang)
    try:
        prompt = (
            f"Translate the following English text to {lang_name}. "
            "IMPORTANT: Keep all legal act names, section numbers, form numbers, and technical "
            "terms (e.g., 'Patents Act Section 3(p)', 'NBA Form 11', 'TKDL', 'GI Registry') "
            "in English within the translated text. "
            "Maintain the original structure — bullet points, paragraphs, line breaks. "
            "Return ONLY the translated text — no preamble, no explanation.\n\n"
            f"{text}"
        )
        resp = client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        result = resp.text.strip() if resp and resp.text else ""
        return result or text
    except Exception as exc:
        logger.warning(f"Gemini translation → {lang_name} failed: {exc}. Returning English.")
        return text
