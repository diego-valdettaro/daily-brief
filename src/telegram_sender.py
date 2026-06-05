from __future__ import annotations

import requests


TELEGRAM_LIMIT = 4096


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    for chunk in _chunks(message, TELEGRAM_LIMIT):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 400:
            payload.pop("parse_mode", None)
            response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()


def _chunks(message: str, size: int) -> list[str]:
    return [message[index : index + size] for index in range(0, len(message), size)] or [""]
