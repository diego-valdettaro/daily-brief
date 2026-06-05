from __future__ import annotations

from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from src.models import Article


TRACKING_PREFIXES = ("utm_",)
TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def dedupe_articles(articles: list[Article], title_threshold: float = 0.88) -> list[Article]:
    unique: list[Article] = []
    seen_urls: set[str] = set()

    for article in articles:
        normalized_url = normalize_url(article.url)
        if normalized_url in seen_urls:
            continue
        if any(_similar_titles(article.title, existing.title, title_threshold) for existing in unique):
            continue
        seen_urls.add(normalized_url)
        unique.append(article)

    return unique


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key not in TRACKING_PARAMS and not key.startswith(TRACKING_PREFIXES)
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def _similar_titles(left: str, right: str, threshold: float) -> bool:
    return SequenceMatcher(None, _clean_title(left), _clean_title(right)).ratio() >= threshold


def _clean_title(title: str) -> str:
    return " ".join(title.lower().strip().split())
