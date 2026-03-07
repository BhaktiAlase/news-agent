"""
Fetches top trending headlines from NewsAPI.
Handles errors, retries, and returns clean structured data.
"""

import time
import requests
from typing import List, Dict, Optional
from config import NEWS_API_KEY, NEWS_API_URL, NEWS_COUNTRY, NEWS_COUNT


def fetch_top_news(
    count: int = NEWS_COUNT,
    country: str = NEWS_COUNTRY,
    category: Optional[str] = None,
    max_retries: int = 3,
) -> List[Dict]:
    """
    Fetch top trending headlines.

    Args:
        count:       Number of articles to fetch (max 100).
        country:     2-letter country code (us, in, gb, etc.).
        category:    Optional category filter
                     (business, entertainment, health, science, sports, technology).
        max_retries: Number of retry attempts on failure.

    Returns:
        List of dicts with keys: rank, title, description, source, url, published_at
    """
    params = {
        "country": country,
        "pageSize": count,
        "apiKey": NEWS_API_KEY,
    }
    if category:
        params["category"] = category

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(NEWS_API_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                raise ValueError(f"NewsAPI error: {data.get('message', 'Unknown error')}")

            articles = data.get("articles", [])
            if not articles:
                print("[!] NewsAPI returned 0 articles.")
                return []

            news_items = []
            for i, article in enumerate(articles, 1):
                # Skip removed/empty articles
                title = article.get("title") or ""
                if not title or title == "[Removed]":
                    continue

                news_items.append({
                    "rank": len(news_items) + 1,
                    "title": title,
                    "description": article.get("description") or "No description available.",
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                })

            print(f"[✓] Fetched {len(news_items)} articles (attempt {attempt}).")
            return news_items[:count]

        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            print(f"[!] Timeout (attempt {attempt}/{max_retries})")
        except requests.exceptions.ConnectionError:
            last_error = "Connection error"
            print(f"[!] Connection error (attempt {attempt}/{max_retries})")
        except requests.exceptions.HTTPError as e:
            last_error = str(e)
            print(f"[!] HTTP error: {e} (attempt {attempt}/{max_retries})")
        except Exception as e:
            last_error = str(e)
            print(f"[!] Unexpected error: {e} (attempt {attempt}/{max_retries})")

        if attempt < max_retries:
            wait = 2 ** attempt
            print(f"    Retrying in {wait}s...")
            time.sleep(wait)

    print(f"[✗] Failed to fetch news after {max_retries} attempts. Last error: {last_error}")
    return []


# ─── Quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    news = fetch_top_news()
    for item in news:
        print(f"{item['rank']}. {item['title']} ({item['source']})")