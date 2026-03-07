"""
Core agent that orchestrates: Fetch → Summarize → Send.
Includes logging, error handling, and retry logic.
"""

import json
import os
from datetime import datetime
from typing import Optional

from news_fetcher import fetch_top_news
from summarizer import summarize_news
from whatsapp_sender import send_whatsapp
from config import NEWS_COUNT, NEWS_COUNTRY


# ─── Logging ─────────────────────────────────────────────────
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def _log_run(status: str, details: dict):
    """Append a run log entry to a daily log file."""
    log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.json")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        **details,
    }

    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

    print(f"[📝] Log saved to {log_file}")


# ─── Main Agent ──────────────────────────────────────────────
def run_agent(
    count: int = NEWS_COUNT,
    country: str = NEWS_COUNTRY,
    category: Optional[str] = None,
    dry_run: bool = False,
) -> bool:
    """
    Execute the full agent pipeline.

    Args:
        count:    Number of news articles.
        country:  Country code for headlines.
        category: Optional category filter.
        dry_run:  If True, print the message but don't send via WhatsApp.

    Returns:
        True if successful, False otherwise.
    """
    start_time = datetime.now()
    print(f"\n{'='*50}")
    print(f"🚀 AI News Agent — {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    try:
        # ── Step 1: Fetch News ────────────────────────────────
        print("[Step 1/3] Fetching trending news...")
        news = fetch_top_news(count=count, country=country, category=category)

        if not news:
            msg = "⚠️ No news articles found today. Will retry tomorrow."
            print(f"[!] {msg}")
            _log_run("no_news", {"message": msg})
            if not dry_run:
                send_whatsapp(msg)
            return False

        print(f"           → Got {len(news)} articles.\n")

        # ── Step 2: Summarize ─────────────────────────────────
        print("[Step 2/3] Summarizing with AI...")
        summary = summarize_news(news)
        print(f"           → Summary ready ({len(summary)} chars).\n")

        # ── Step 3: Compose & Send ────────────────────────────
        print("[Step 3/3] Sending via WhatsApp...")

        header = (
            f"🌅 *Good Morning!*\n"
            f"📅 *Daily News Briefing*\n"
            f"🗓️ {datetime.now().strftime('%A, %B %d, %Y')}\n"
            f"{'─' * 30}\n\n"
        )
        footer = (
            f"\n\n{'─' * 30}\n"
            f"🤖 _Powered by AI News Agent_\n"
            f"📊 _Top {len(news)} stories • {country.upper()} edition_"
        )
        full_message = header + summary + footer

        if dry_run:
            print("\n[DRY RUN] Would send this message:\n")
            print(full_message)
            print()
        else:
            send_whatsapp(full_message)

        # ── Log success ───────────────────────────────────────
        elapsed = (datetime.now() - start_time).total_seconds()
        _log_run("success", {
            "articles_fetched": len(news),
            "summary_length": len(summary),
            "message_length": len(full_message),
            "elapsed_seconds": round(elapsed, 2),
            "country": country,
            "category": category,
            "dry_run": dry_run,
        })

        print(f"\n[✓] Agent completed in {elapsed:.1f}s ✨\n")
        return True

    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        error_msg = f"Agent error: {str(e)}"
        print(f"\n[✗] {error_msg}\n")

        _log_run("error", {
            "error": str(e),
            "elapsed_seconds": round(elapsed, 2),
        })

        # Send error notification
        if not dry_run:
            try:
                send_whatsapp(f"⚠️ *News Agent Error*\n\n{str(e)[:500]}")
            except Exception:
                print("[✗] Could not send error notification.")

        return False


# ─── Quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    run_agent(dry_run=False)