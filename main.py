"""
Entry point for the AI News Agent.
Supports: scheduled mode, one-shot mode, and dry-run mode.
"""

import argparse
import time
from datetime import datetime

import pytz
import schedule

from agent import run_agent
from config import SCHEDULE_TIME, TIMEZONE, NEWS_COUNT, NEWS_COUNTRY


def get_local_time() -> str:
    """Get current time in configured timezone."""
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz).strftime("%H:%M:%S %Z")


def scheduled_job():
    """Wrapper for scheduled execution."""
    print(f"\n⏰ Scheduled run triggered at {get_local_time()}")
    run_agent()


def main():
    parser = argparse.ArgumentParser(
        description="🤖 AI News Agent — Daily WhatsApp news briefing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start scheduler (runs daily at configured time)
  python main.py --once             # Run once and exit
  python main.py --once --dry-run   # Test without sending WhatsApp
  python main.py --once --country in --category technology
  python main.py --once --count 10  # Fetch 10 articles instead of 5
        """,
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once immediately and exit (no scheduling).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the message instead of sending via WhatsApp.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=NEWS_COUNT,
        help=f"Number of news articles (default: {NEWS_COUNT}).",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=NEWS_COUNTRY,
        help=f"Country code for news (default: {NEWS_COUNTRY}).",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        choices=["business", "entertainment", "health", "science", "sports", "technology"],
        help="Filter by news category.",
    )

    args = parser.parse_args()

    print(r"""
     _    ___   _   _                       _                    _   
    / \  |_ _| | \ | | _____      _____    / \   __ _  ___ _ __ | |_ 
   / _ \  | |  |  \| |/ _ \ \ /\ / / __|  / _ \ / _` |/ _ \ '_ \| __|
  / ___ \ | |  | |\  |  __/\ V  V /\__ \ / ___ \ (_| |  __/ | | | |_ 
 /_/   \_\___| |_| \_|\___| \_/\_/ |___//_/   \_\__, |\___|_| |_|\__|
                                                 |___/                
    """)

    if args.once:
        # ── One-shot mode ─────────────────────────────────────
        print(f"📡 Running once ({get_local_time()})...\n")
        success = run_agent(
            count=args.count,
            country=args.country,
            category=args.category,
            dry_run=args.dry_run,
        )
        exit(0 if success else 1)

    else:
        # ── Scheduler mode ────────────────────────────────────
        print(f"📡 Scheduler started")
        print(f"   ⏰ Scheduled time : {SCHEDULE_TIME} ({TIMEZONE})")
        print(f"   🌍 Country        : {args.country.upper()}")
        print(f"   📰 Articles       : {args.count}")
        if args.category:
            print(f"   🏷️  Category      : {args.category}")
        print(f"   🕐 Current time   : {get_local_time()}")
        print(f"\n   Waiting for {SCHEDULE_TIME}...\n")

        schedule.every().day.at(SCHEDULE_TIME).do(scheduled_job)

        try:
            while True:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n\n[👋] Agent stopped by user. Goodbye!")
            exit(0)


if __name__ == "__main__":
    main()