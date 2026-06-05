from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from src.dedupe import normalize_url
from src.models import Article


SCHEMA = """
CREATE TABLE IF NOT EXISTS sent_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    published_at TEXT,
    sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class ArticleDatabase:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute(SCHEMA)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def filter_unsent(self, articles: Iterable[Article]) -> list[Article]:
        return [article for article in articles if not self.was_sent(article.url)]

    def was_sent(self, url: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM sent_articles WHERE url = ? LIMIT 1",
            (normalize_url(url),),
        ).fetchone()
        return row is not None

    def mark_sent(self, articles: Iterable[Article]) -> None:
        self.connection.executemany(
            """
            INSERT OR IGNORE INTO sent_articles (title, url, source, published_at)
            VALUES (?, ?, ?, ?)
            """,
            [
                (article.title, normalize_url(article.url), article.source, article.published_at)
                for article in articles
            ],
        )
        self.connection.commit()
