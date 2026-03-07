"""
Centralized configuration — loads from .env and validates all required keys.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    """Return env var or exit with a clear error."""
    value = os.getenv(key)
    if not value:
        print(f"[FATAL] Missing required environment variable: {key}")
        print(f"        Copy .env.example → .env and fill in your keys.")
        sys.exit(1)
    return value


# ─── News API ────────────────────────────────────────────────
NEWS_API_KEY   = _require("NEWS_API_KEY")
NEWS_API_URL   = "https://newsapi.org/v2/top-headlines"
NEWS_COUNTRY   = os.getenv("NEWS_COUNTRY", "us")
NEWS_COUNT     = int(os.getenv("NEWS_COUNT", "5"))

# ─── LLM (Groq — free tier) ──────────────────────────────────
GROQ_API_KEY   = _require("GROQ_API_KEY")
GROQ_MODEL     = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# ─── Twilio ──────────────────────────────────────────────────
TWILIO_SID     = _require("TWILIO_ACCOUNT_SID")
TWILIO_AUTH    = _require("TWILIO_AUTH_TOKEN")
TWILIO_FROM    = _require("TWILIO_WHATSAPP_FROM")
MY_NUMBER      = _require("MY_WHATSAPP_NUMBER")

# ─── Scheduler ───────────────────────────────────────────────
SCHEDULE_TIME  = os.getenv("SCHEDULE_TIME", "09:00")
TIMEZONE       = os.getenv("TIMEZONE", "Asia/Kolkata")