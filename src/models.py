from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    type: str
    url: str
    enabled: bool = True


@dataclass(frozen=True)
class Article:
    title: str
    url: str
    source: str
    published_at: str | None = None
    raw_text: str | None = None

    @property
    def fingerprint(self) -> str:
        return self.url.strip().lower()
