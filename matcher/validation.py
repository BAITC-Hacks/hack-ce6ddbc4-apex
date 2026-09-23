"""SearchRequest validation and form-value normalization (pure Python, shared by /app and the API)."""
from __future__ import annotations

import re
from datetime import date as _date
from typing import Optional

from .data import CITIES, EVENT_FORMATS, LANGUAGES, WINDOW_END, WINDOW_START
from .models import SearchRequest

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DIGITS = re.compile(r"^\d+$")
_SPACES = (" ", " ", " ")
DURATION_MIN, DURATION_MAX = 1, 24
BUDGET_MAX = 9_007_199_254_740_991          # Number.MAX_SAFE_INTEGER - same limit as the Phase 1 form
FIELD_ORDER = ("city", "date", "event_type", "category", "budget_kzt", "duration_h", "language")


def error(field: str, code: str, value="") -> dict:
    return {"field": field, "code": code, "value": "" if value is None else str(value)}


_error = error          # spec name


def normalize_budget(raw: Optional[str]) -> tuple[Optional[int], Optional[str]]:
    """Phase 1 budget rules: -> (value, None) | (None, None) for empty | (None, code) for an error."""
    text = raw or ""
    for space in _SPACES:
        text = text.replace(space, "")
    text = text.strip()
    if not text:
        return None, None
    if text.startswith("-") and _DIGITS.match(text[1:]):
        return None, "positive"
    if not _DIGITS.match(text):
        return None, "integer"
    value = int(text)
    if value > BUDGET_MAX:
        return None, "too_large"
    if value <= 0:
        return None, "positive"
    return value, None


def normalize_hours(raw: Optional[str]) -> tuple[Optional[int], Optional[str]]:
    """"" -> (None, None); digits -> int (range is checked by validate); anything else -> (None, "range")."""
    text = (raw or "").strip()
    if not text:
        return None, None
    if _DIGITS.match(text):
        return int(text), None
    return None, "range"


def validate(req: SearchRequest, categories: tuple[str, ...]) -> list[dict]:
    """Returns ALL errors (not the first) in a fixed field order. Empty list - the request is valid."""
    errors: list[dict] = []
    if not req.city:
        errors.append(error("city", "required"))
    elif req.city not in CITIES:
        errors.append(error("city", "unknown", req.city))

    if not req.date:
        errors.append(error("date", "required"))
    elif not _ISO_DATE.match(req.date):
        errors.append(error("date", "format", req.date))
    else:
        try:
            _date.fromisoformat(req.date)
        except ValueError:
            errors.append(error("date", "format", req.date))
        else:
            if not (WINDOW_START <= req.date <= WINDOW_END):        # ISO strings compare as dates
                errors.append(error("date", "window", req.date))

    if not req.event_type:
        errors.append(error("event_type", "required"))
    elif req.event_type not in EVENT_FORMATS:
        errors.append(error("event_type", "unknown", req.event_type))

    if not req.category:
        errors.append(error("category", "required"))
    elif req.category not in categories:
        errors.append(error("category", "unknown", req.category))

    if req.budget_kzt is None or req.budget_kzt <= 0:
        errors.append(error("budget_kzt", "positive", req.budget_kzt))
    elif req.budget_kzt > BUDGET_MAX:
        errors.append(error("budget_kzt", "too_large", req.budget_kzt))

    if req.duration_h is not None and not (DURATION_MIN <= req.duration_h <= DURATION_MAX):
        errors.append(error("duration_h", "range", req.duration_h))

    if req.language is not None and req.language not in LANGUAGES:
        errors.append(error("language", "unknown", req.language))

    return sorted(errors, key=lambda e: FIELD_ORDER.index(e["field"]))
