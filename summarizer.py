"""
Uses OpenAI GPT to summarize news articles into a WhatsApp-friendly format.
"""

from datetime import datetime
from typing import List, Dict
from openai import OpenAI
from config import GROQ_API_KEY, GROQ_MODEL

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = """You are a professional yet friendly news anchor who delivers 
a daily briefing via WhatsApp. Your style is:
- Concise (2-3 sentences per story)
- Informative (cover the key facts)
- Engaging (use relevant emojis, but don't overdo it)
- Well-formatted for mobile reading
"""

USER_PROMPT_TEMPLATE = """Summarize each of these {count} trending news stories.

FORMAT (follow exactly):
1. 📰 *Headline* (Source)
   Summary in 2-3 clear sentences.
   🔗 link

2. 📰 *Headline* (Source)
   Summary in 2-3 clear sentences.
   🔗 link

... and so on.

RULES:
- Keep each summary under 50 words
- Highlight why it matters to the reader
- Use simple language (no jargon)
- Include the source name and link for each

Today's date: {date}

─── RAW NEWS ───
{raw_news}
"""


def _format_raw_news(news_items: List[Dict]) -> str:
    """Convert news items into a raw text block for the prompt."""
    lines = []
    for item in news_items:
        lines.append(
            f"{item['rank']}. {item['title']}\n"
            f"   Source: {item['source']}\n"
            f"   Description: {item['description']}\n"
            f"   URL: {item['url']}\n"
            f"   Published: {item.get('published_at', 'N/A')}\n"
        )
    return "\n".join(lines)


def summarize_news(news_items: List[Dict]) -> str:
    """
    Summarize a list of news items using GPT.

    Args:
        news_items: List of dicts from news_fetcher.fetch_top_news()

    Returns:
        A WhatsApp-formatted summary string.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    if not news_items:
        return "No trending news found today. Check back tomorrow! 📭"

    raw_news = _format_raw_news(news_items)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        count=len(news_items),
        date=datetime.now().strftime("%B %d, %Y"),
        raw_news=raw_news,
    )

    print(f"[…] Calling {GROQ_MODEL} for summarization...")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1200,
        temperature=0.7,
    )

    summary = response.choices[0].message.content.strip()

    # Log token usage
    usage = response.usage
    print(
        f"[✓] Summary generated. "
        f"Tokens: {usage.prompt_tokens} prompt + {usage.completion_tokens} completion "
        f"= {usage.total_tokens} total"
    )

    return summary


# ─── Quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    sample_news = [
        {
            "rank": 1,
            "title": "AI Makes Major Breakthrough in Cancer Detection",
            "description": "New AI model detects early-stage cancer with 97% accuracy.",
            "source": "Reuters",
            "url": "https://reuters.com/example",
            "published_at": "2026-03-07T08:00:00Z",
        },
        {
            "rank": 2,
            "title": "SpaceX Starship Completes Mars Orbit Test",
            "description": "Starship successfully entered Mars transfer orbit.",
            "source": "BBC News",
            "url": "https://bbc.com/example",
            "published_at": "2026-03-07T07:30:00Z",
        },
    ]
    print(summarize_news(sample_news))