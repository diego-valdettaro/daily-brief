from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from src.config_loader import ROOT_DIR, load_environment, load_interests, load_prompt, load_sources
from src.database import ArticleDatabase
from src.dedupe import dedupe_articles, normalize_url
from src.fetch_sources import fetch_articles
from src.llm import generate_brief
from src.telegram_sender import send_telegram_message


LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "daily_brief.log"


def main() -> None:
    load_environment()
    setup_logging()

    openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    database_path = os.getenv("DATABASE_PATH", str(ROOT_DIR / "data" / "daily_brief.sqlite3"))
    max_per_source = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "10"))

    bot_token = require_env("TELEGRAM_BOT_TOKEN")
    chat_id = require_env("TELEGRAM_CHAT_ID")
    require_env("OPENAI_API_KEY")

    sources = load_sources()
    interests = load_interests()
    prompt = load_prompt()

    logging.info("Fetching articles from %s sources", len(sources))
    fetched = fetch_articles(sources, max_per_source=max_per_source)
    unique = dedupe_articles(fetched)

    db = ArticleDatabase(database_path)
    try:
        candidates = db.filter_unsent(unique)
        logging.info("Fetched=%s unique=%s unsent=%s", len(fetched), len(unique), len(candidates))

        brief = generate_brief(candidates, interests, prompt, openai_model)
        send_telegram_message(bot_token, chat_id, brief)

        sent_articles = articles_mentioned_in_brief(candidates, brief)
        db.mark_sent(sent_articles or candidates[:5])
        logging.info("Brief sent. Marked %s articles as sent", len(sent_articles or candidates[:5]))
    finally:
        db.close()


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def articles_mentioned_in_brief(candidates, brief: str):
    urls = set(re.findall(r"https?://\S+", brief))
    cleaned_urls = {normalize_url(url.rstrip(").,]")) for url in urls}
    return [article for article in candidates if normalize_url(article.url) in cleaned_urls]


if __name__ == "__main__":
    main()
