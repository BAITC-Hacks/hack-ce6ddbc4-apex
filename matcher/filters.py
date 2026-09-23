"""Жёсткие фильтры: только по полям CSV. Возвращают ВСЕ причины в порядке воронки."""
from __future__ import annotations

from .data import EVENT_FORMATS, LANGUAGES
from .models import Contractor, SearchRequest


def check(c: Contractor, req: SearchRequest) -> list[str]:
    """[] — прошёл; иначе коды причин в порядке busy → format → budget → language → duration.
    Категория и город проверяются раньше (Catalog.in_category_city), поэтому здесь их нет."""
    reasons: list[str] = []
    if not c.is_free(req.date):
        reasons.append("busy")
    if req.event_type not in c.event_formats:
        reasons.append("format")
    if c.price_from_kzt > req.budget_kzt:                       # цена «от» = бюджету проходит
        reasons.append("budget")
    if req.language and req.language not in c.languages:
        reasons.append("language")
    if req.duration_h and c.max_hours is not None and c.max_hours < req.duration_h:
        reasons.append("duration")                              # max_hours None — ограничения нет
    return reasons


def _canon(values: tuple[str, ...], order: tuple[str, ...]) -> str:
    """Канонический порядок значений, чтобы «ru|kk» и «kk|ru» выглядели одинаково."""
    return "|".join(sorted(values, key=lambda v: order.index(v) if v in order else len(order)))


def details(c: Contractor, req: SearchRequest, reasons: list[str]) -> dict[str, str]:
    """Машиночитаемые подробности отсева (строки — контракт Rejection.details). Тексты строит UI/summary."""
    d: dict[str, str] = {}
    if "busy" in reasons:
        d["busy_date"] = req.date
    if "format" in reasons:
        d["formats"] = _canon(c.event_formats, EVENT_FORMATS)
    if "budget" in reasons:
        d["price_from_kzt"] = str(c.price_from_kzt)
        d["budget_kzt"] = str(req.budget_kzt)
        d["over_by_kzt"] = str(c.price_from_kzt - req.budget_kzt)
    if "language" in reasons:
        d["languages"] = _canon(c.languages, LANGUAGES)
    if "duration" in reasons:
        d["max_hours"] = str(c.max_hours)
        d["duration_h"] = str(req.duration_h)
    return d
