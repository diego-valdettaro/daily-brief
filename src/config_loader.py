from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from src.models import Source


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_environment() -> None:
    load_dotenv(ROOT_DIR / ".env")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_sources(path: Path | None = None) -> list[Source]:
    config_path = path or ROOT_DIR / "config" / "sources.yaml"
    data = load_yaml(config_path)
    sources = []
    for item in data.get("sources", []):
        if not item.get("enabled", True):
            continue
        sources.append(
            Source(
                name=str(item["name"]),
                type=str(item.get("type", "rss")),
                url=str(item["url"]),
                enabled=bool(item.get("enabled", True)),
            )
        )
    return sources


def load_interests(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or ROOT_DIR / "config" / "interests.yaml")


def load_prompt(path: Path | None = None) -> str:
    prompt_path = path or ROOT_DIR / "config" / "prompt.md"
    return prompt_path.read_text(encoding="utf-8")
