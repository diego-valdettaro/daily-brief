from __future__ import annotations

import json
from datetime import date
from typing import Any

from openai import OpenAI

from src.models import Article


def generate_brief(
    articles: list[Article],
    interests: dict[str, Any],
    prompt: str,
    model: str,
) -> str:
    if not articles:
        return "# Brief Tech Diario (06:00 Amsterdam)\n\nNo hay articulos nuevos suficientes para generar el brief de hoy."

    client = OpenAI()
    payload = {
        "date": date.today().isoformat(),
        "interests": interests,
        "candidate_articles": [article_to_dict(article) for article in articles],
    }
    user_message = (
        "Selecciona las mejores noticias y genera el brief final. "
        "Usa solo los articulos candidatos y conserva los links originales.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI returned an empty brief")
    return content.strip()


def article_to_dict(article: Article) -> dict[str, str | None]:
    return {
        "title": article.title,
        "url": article.url,
        "source": article.source,
        "published_at": article.published_at,
        "summary_or_raw_text": article.raw_text,
    }
