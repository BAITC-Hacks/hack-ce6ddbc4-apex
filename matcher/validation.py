"""Валидация SearchRequest. NEW: небольшое дополнение к структуре мастер-плана (чистый Python)."""
from __future__ import annotations

import re
from datetime import date as _date

from .data import CITIES, EVENT_FORMATS, LANGUAGES, WINDOW_END, WINDOW_START
from .models import SearchRequest

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DURATION_MIN, DURATION_MAX = 1, 24
FIELD_ORDER = ("city", "date", "event_type", "category", "budget_kzt", "duration_h", "language")


def _error(field: str, code: str, value="") -> dict:
    return {"field": field, "code": code, "value": "" if value is None else str(value)}


def validate(req: SearchRequest, categories: tuple[str, ...]) -> list[dict]:
    """Возвращает ВСЕ ошибки (не первую) в фиксированном порядке полей. Пустой список — запрос валиден."""
    errors: list[dict] = []
    if not req.city:
        errors.append(_error("city", "required"))
    elif req.city not in CITIES:
        errors.append(_error("city", "unknown", req.city))

    if not req.date:
        errors.append(_error("date", "required"))
    elif not _ISO_DATE.match(req.date):
        errors.append(_error("date", "format", req.date))
    else:
        try:
            _date.fromisoformat(req.date)
        except ValueError:
            errors.append(_error("date", "format", req.date))
        else:
            if not (WINDOW_START <= req.date <= WINDOW_END):        # ISO-строки сравниваются как даты
                errors.append(_error("date", "window", req.date))

    if not req.event_type:
        errors.append(_error("event_type", "required"))
    elif req.event_type not in EVENT_FORMATS:
        errors.append(_error("event_type", "unknown", req.event_type))

    if not req.category:
        errors.append(_error("category", "required"))
    elif req.category not in categories:
        errors.append(_error("category", "unknown", req.category))

    if req.budget_kzt is None or req.budget_kzt <= 0:
        errors.append(_error("budget_kzt", "positive", req.budget_kzt))

    if req.duration_h is not None and not (DURATION_MIN <= req.duration_h <= DURATION_MAX):
        errors.append(_error("duration_h", "range", req.duration_h))

    if req.language is not None and req.language not in LANGUAGES:
        errors.append(_error("language", "unknown", req.language))

    return sorted(errors, key=lambda e: FIELD_ORDER.index(e["field"]))
