"""Подсказки «что изменить»: ближайшие даты, добавка к бюджету, бюджет + дата, другой город.

Порядок фиксирован (даты → бюджет → бюджет+дата → город), максимум 3. Считаем через filters.check(),
а не через recommend(): 29 дат × ≤ 10 кандидатов — это микросекунды.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import replace
from typing import Optional

from .data import CITIES, WINDOW_END, WINDOW_START
from .explain import Tr, fmt_date, fmt_kzt, fmt_list, plural
from .filters import check
from .models import Contractor, SearchRequest

RADIUS_DAYS = 14
MAX_HINTS = 3
NO_LIMIT = 10 ** 12
MAX_NAMES = 4


def _order(catalog) -> dict[str, int]:
    return {c.id: i for i, c in enumerate(catalog.contractors)}


def _sorted(cs: list[Contractor], order: dict[str, int]) -> list[Contractor]:
    return sorted(cs, key=lambda c: (c.price_from_kzt, order[c.id]))  # дешевле — раньше, затем как в каталоге


def _rings(date_iso: str, radius: int):
    """Кольца дат: (1, [d-1, d+1]), (2, [d-2, d+2]) … — только внутри окна календаря."""
    d0 = dt.date.fromisoformat(date_iso)
    for k in range(1, radius + 1):
        ring = [(d0 + dt.timedelta(days=s * k)).isoformat() for s in (-1, 1)]
        yield k, [d for d in ring if WINDOW_START <= d <= WINDOW_END]


def nearest_dates(catalog, req: SearchRequest, need: int, radius: int = RADIUS_DAYS) -> list[tuple[str, list[Contractor]]]:
    """Ближайшие даты (обе стороны на минимальном расстоянии), где проходят ≥ need кандидатов."""
    pool, order = catalog.in_category_city(req.category, req.city), _order(catalog)
    for _, ring in _rings(req.date, radius):
        found = []
        for d in ring:
            ok = [c for c in pool if not check(c, replace(req, date=d))]
            if len(ok) >= need:
                found.append((d, _sorted(ok, order)))
        if found:
            return found
    return []


def budget_hint(catalog, req: SearchRequest) -> Optional[tuple[int, list[Contractor]]]:
    """Минимальная добавка к бюджету ради +1 кандидата на ту же дату (мешает только цена)."""
    pool, order = catalog.in_category_city(req.category, req.city), _order(catalog)
    only_budget = [c for c in pool if check(c, req) == ["budget"]]
    if not only_budget:
        return None
    need = min(c.price_from_kzt for c in only_budget)
    return need, _sorted([c for c in only_budget if c.price_from_kzt == need], order)


def combined_hint(catalog, req: SearchRequest, radius: int = RADIUS_DAYS) -> Optional[tuple[str, int, list[Contractor]]]:
    """Бюджет + дата, когда по отдельности не помогает: минимум денег, затем ближайшая дата, затем раньше."""
    pool, order = catalog.in_category_city(req.category, req.city), _order(catalog)
    best = None
    for k, ring in _rings(req.date, radius):
        for d in ring:
            ok = [c for c in pool if not check(c, replace(req, date=d, budget_kzt=NO_LIMIT))]
            if ok:
                need = min(c.price_from_kzt for c in ok)
                key = (need, k, d)
                if best is None or key < best[0]:
                    best = (key, d, need, [c for c in ok if c.price_from_kzt == need])
    if best is None:
        return None
    _, d, need, cs = best
    return d, need, _sorted(cs, order)


def other_city_hint(catalog, req: SearchRequest) -> list[tuple[str, int, int]]:
    """[(город, всего, из них синтетических)] для той же категории, по убыванию."""
    rows = []
    for city in CITIES:
        if city != req.city:
            cs = catalog.in_category_city(req.category, city)
            if cs:
                rows.append((city, len(cs), sum(c.synthetic for c in cs)))
    return sorted(rows, key=lambda r: (-r[1], CITIES.index(r[0])))


def _names(cs: list[Contractor], tr: Tr, sep: str = ", ") -> str:
    names = [c.name for c in cs[:MAX_NAMES]]
    tail = [tr("hint.more_names", n=len(cs) - MAX_NAMES)] if len(cs) > MAX_NAMES else []
    return sep.join(names + tail) if sep else fmt_list(names + tail, tr)


def _date_hint(found: list[tuple[str, list[Contractor]]], need: int, tr: Tr) -> dict:
    items = [tr("hint.date_item", date=fmt_date(d, tr), names=_names(cs, tr)) for d, cs in found]
    key = "hint.dates_one" if need == 1 else "hint.dates"
    return {"type": "date", "text": tr(key, need=need, items=fmt_list(items, tr)),
            "params": {"need": need, "dates": [{"date": d, "ids": [c.id for c in cs], "names": [c.name for c in cs]}
                                               for d, cs in found]},
            "query": {"date": found[0][0]}}


def build_hints(catalog, req: SearchRequest, status: str, n_passed: int, tr: Tr) -> list[dict]:
    lang, hints = req.lang, []
    if status == "no_category_in_city":
        for city, total, synthetic in other_city_hint(catalog, req):
            count = f"{total} {plural(tr('hint.noun.profile'), total, lang)}"
            synth = (tr("hint.synthetic_part", n=synthetic, adj=plural(tr("hint.noun.synthetic"), synthetic, lang))
                     if synthetic else tr("hint.all_real"))
            hints.append({"type": "other_city",
                          "text": tr("hint.other_city", city_in=tr(f"data.city_in.{city}"), count=count,
                                     category=tr(f"data.category.{req.category}"), synthetic=synth),
                          "params": {"city": city, "total": total, "synthetic": synthetic},
                          "query": {"city": city}})
        return hints[:MAX_HINTS]
    if status not in ("partial", "none_match"):
        return []
    need = 1 if status == "none_match" else min(3, n_passed + 1)
    dates = nearest_dates(catalog, req, need)
    if dates:
        hints.append(_date_hint(dates, need, tr))
        if need == 1:  # второй ориентир: где подходят сразу трое
            dates3 = nearest_dates(catalog, req, 3)
            if dates3 and [d for d, _ in dates3] != [d for d, _ in dates]:
                hints.append(_date_hint(dates3, 3, tr))
    else:
        key = "hint.dates_none" if need == 1 else "hint.dates_none_more"
        hints.append({"type": "date_none", "params": {"radius": RADIUS_DAYS, "need": need},
                      "text": tr(key, radius=RADIUS_DAYS, need=need, budget=fmt_kzt(req.budget_kzt, lang))})
    found = budget_hint(catalog, req)
    if found:
        need_budget, cs = found
        hints.append({"type": "budget", "text": tr("hint.budget", budget=fmt_kzt(need_budget, lang), names=_names(cs, tr)),
                      "params": {"budget_kzt": need_budget, "ids": [c.id for c in cs]},
                      "query": {"budget": need_budget}})
    if status == "none_match" and not dates and not found:
        combo = combined_hint(catalog, req)
        if combo:
            d, need_budget, cs = combo
            key = "hint.combined" if len(cs) > 1 else "hint.combined_one"
            hints.append({"type": "combined",
                          "text": tr(key, budget=fmt_kzt(need_budget, lang), date=fmt_date(d, tr), names=_names(cs, tr, sep="")),
                          "params": {"date": d, "budget_kzt": need_budget, "ids": [c.id for c in cs],
                                     "names": [c.name for c in cs]},
                          "query": {"date": d, "budget": need_budget}})
    return hints[:MAX_HINTS]
