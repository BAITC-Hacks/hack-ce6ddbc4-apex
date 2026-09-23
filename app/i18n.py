from __future__ import annotations

import json
from pathlib import Path

from fastapi import Request

SUPPORTED = ("ru", "kk", "en")
DEFAULT_LANG = "ru"
HTML_LANG = {code: code for code in SUPPORTED}
_LOCALES: dict[str, dict[str, str]] = {}


def load_locales(directory: Path) -> None:
    for code in SUPPORTED:
        path = directory / f"{code}.json"
        values = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        if not isinstance(values, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in values.items()
        ):
            raise ValueError(f"Locale {code} must be a flat dictionary of strings")
        _LOCALES[code] = values


def translate(lang: str, key: str, **kwargs) -> str:
    text = _LOCALES.get(lang, {}).get(key) or _LOCALES.get(DEFAULT_LANG, {}).get(key) or key
    if not kwargs:
        return text
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return text


def data_label(lang: str, kind: str, value: str) -> str:
    return translate(lang, f"data.{kind}.{value}") if value else value


def get_lang(request: Request) -> str:
    query = request.query_params.get("lang")
    if query in SUPPORTED:
        return query
    cookie = request.cookies.get("lang")
    if cookie in SUPPORTED:
        return cookie
    user = getattr(request.state, "user", None)
    if user and user.get("preferred_lang") in SUPPORTED:
        return user["preferred_lang"]
    return DEFAULT_LANG
