from __future__ import annotations

from email.utils import parsedate_to_datetime
from typing import Iterable

import feedparser

from src.models import Article, Source


def fetch_articles(sources: Iterable[Source], max_per_source: int = 10) -> list[Article]:
    articles: list[Article] = []
    for source in sources:
        if source.type != "rss":
            continue
        try:
            feed = feedparser.parse(source.url)
            for entry in feed.entries[:max_per_source]:
                url = str(entry.get("link", "")).strip()
                title = str(entry.get("title", "")).strip()
                if not url or not title:
                    continue
                articles.append(
                    Article(
                        title=title,
                        url=url,
                        source=source.name,
                        published_at=_published_at(entry),
                        raw_text=_entry_text(entry),
                    )
                )
        except Exception:
            continue
    return articles


def _published_at(entry: dict) -> str | None:
    value = entry.get("published") or entry.get("updated")
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).isoformat()
    except Exception:
        return str(value)


def _entry_text(entry: dict) -> str | None:
    summary = entry.get("summary") or entry.get("description")
    if summary:
        return str(summary)
    content = entry.get("content")
    if isinstance(content, list) and content:
        return str(content[0].get("value", ""))
    return None
