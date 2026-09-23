"""Один запрос — две даты: кто вошёл, кто выпал и почему. Занятость видна прямо в объяснении."""
from __future__ import annotations

import datetime as dt
from dataclasses import replace

from .data import WINDOW_END, WINDOW_START
from .engine import recommend
from .explain import Tr, fmt_date
from .models import Atom, Card, SearchRequest, SearchResponse


def default_second_date(date_iso: str) -> str:
    """Тот же день недели через неделю (10.10 → 17.10); у конца окна — неделей раньше. Битая дата → ""."""
    try:
        d = dt.date.fromisoformat(date_iso)
    except (TypeError, ValueError):
        return ""
    later = (d + dt.timedelta(days=7)).isoformat()
    return later if later <= WINDOW_END else max(WINDOW_START, (d - dt.timedelta(days=7)).isoformat())


def short_date(iso: str) -> str:
    return f"{iso[8:10]}.{iso[5:7]}"


def _absent_reason(resp: SearchResponse, cid: str) -> str:
    """Почему карточки нет в выдаче: первичная причина отсева или «ниже в рейтинге»."""
    return next((r.reasons[0] for r in resp.rejected if r.id == cid), "rank")


def _mark(card: Card, text: str) -> None:
    card.atoms.insert(0, Atom(type="availability", text=text, unique=True, weight=1.1))
    card.explanation = text[:1].upper() + text[1:] + ". " + card.explanation


def compare_dates(catalog, req: SearchRequest, date_a: str, date_b: str, tr: Tr) -> dict:
    a = recommend(catalog, replace(req, date=date_a), tr)
    b = recommend(catalog, replace(req, date=date_b), tr)
    ids_a, ids_b = [c.id for c in a.cards], [c.id for c in b.cards]
    da, db = fmt_date(date_a, tr), fmt_date(date_b, tr)
    diff: dict[str, list[dict]] = {"entered": [], "left": [], "stayed": []}
    for card in b.cards:
        if card.id in ids_a:
            diff["stayed"].append({"id": card.id, "name": card.name, "reason": None, "date": None,
                                   "label": tr("compare.label.stayed")})
            continue
        reason = _absent_reason(a, card.id)  # по дате отличаются только «занят» и «ниже в рейтинге»
        key = "busy" if reason == "busy" else "rank"
        diff["entered"].append({"id": card.id, "name": card.name, "reason": key, "date": date_a,
                                "label": tr(f"compare.label.entered_{key}", when=short_date(date_a))})
        if key == "busy":
            _mark(card, tr("explain.availability.entered", date_a=da, date_b=db))
    for card in a.cards:
        if card.id in ids_b:
            continue
        reason = _absent_reason(b, card.id)
        key = "busy" if reason == "busy" else "rank"
        diff["left"].append({"id": card.id, "name": card.name, "reason": key, "date": date_b,
                             "label": tr(f"compare.label.left_{key}", when=short_date(date_b))})
        if key == "busy":
            _mark(card, tr("explain.availability.left", date_a=da, date_b=db))
    return {"date_a": date_a, "date_b": date_b, "a": a, "b": b, "diff": diff}
