"""Движок: validate → категория×город → фильтры с причинами → скоринг → объяснения → статус и summary.
Чистая функция: без времени, random, I/O и веб-импортов. Тексты — через инъекцию tr."""
from __future__ import annotations

from collections import Counter
from typing import Iterable

from .data import CITIES, WINDOW_END, WINDOW_START, Catalog
from .explain import Translator, badges_for, explain_cards, fmt_date, fmt_kzt, format_plural, join_human, label
from .filters import check, details
from .models import MAX_CARDS, REASON_ORDER, Card, Rejection, SearchRequest, SearchResponse
from .scoring import SCORING_VERSION, WEIGHTS, score, sort_key
from .validation import validate

ENGINE_VERSION = "1.0"
SUMMARY_NAMES_LIMIT = 6
FUNNEL_STEPS = (("free_on_date", "busy"), ("format", "format"), ("budget", "budget"),
                ("language", "language"), ("duration", "duration"))
FIELD_LABEL_KEYS = {"city": "form.city", "date": "form.date", "event_type": "form.event_type",
                    "category": "form.category", "budget_kzt": "form.budget",
                    "duration_h": "form.duration", "language": "form.language"}


def request_labels(req: SearchRequest, tr: Translator) -> dict:
    """Подписи значений запроса на языке ответа (для summary, воронки и шаблонов)."""
    return {
        "city": label(tr, "city", req.city),
        "category": label(tr, "category", req.category),
        "event_type": label(tr, "format", req.event_type),
        "event_type_pl": format_plural(req.event_type, tr),              # «свадьбы», «тои» — для RU/EN
        "language": label(tr, "language", req.language),
        "date": fmt_date(req.date, tr),
        "budget": fmt_kzt(req.budget_kzt),
        "hours": req.duration_h or "",
    }


def recommend(catalog: Catalog, req: SearchRequest, tr: Translator) -> SearchResponse:
    errors = validate(req, catalog.categories)
    if errors:
        return _invalid(req, errors, tr)
    ctx = request_labels(req, tr)
    total = sum(catalog.category_city_counts.get(req.category, {}).values())
    pool = catalog.in_category_city(req.category, req.city)            # порядок CSV
    funnel = [_step("category_total", total, tr, ctx), _step("category_city", len(pool), tr, ctx)]
    if not pool:
        return _no_category(catalog, req, tr, ctx, funnel)

    reasons = {c.id: check(c, req) for c in pool}
    remaining = list(pool)
    for step, code in FUNNEL_STEPS:                                      # последовательная воронка
        remaining = [c for c in remaining if code not in reasons[c.id]]
        funnel.append(_step(step, len(remaining), tr, ctx, applied=_applied(code, req)))

    passed = [c for c in pool if not reasons[c.id]]
    rejected = [Rejection(c.id, c.name, reasons[c.id], details(c, req, reasons[c.id]))
                for c in pool if reasons[c.id]]
    breakdowns = {c.id: score(c, req) for c in passed}
    ranked = sorted(passed, key=lambda c: sort_key(c, breakdowns[c.id]))
    top = ranked[:MAX_CARDS]
    more = len(ranked) - len(top)
    status = "found" if len(passed) >= MAX_CARDS else ("partial" if passed else "none_match")
    return SearchResponse(
        status=status,
        summary=_summary(status, tr, ctx, total_city=len(pool), passed=len(passed), more=more, rejected=rejected),
        cards=_cards(top, req, breakdowns, tr),
        more_count=more,
        rejected=rejected,
        reason_counts=_count(r.reasons for r in rejected),               # по ВСЕМ причинам
        funnel=funnel,
        hints=[],                                                        # фаза 5: hints.py
        meta=_meta(req, primary_counts=_count([r.primary] for r in rejected)),
    )


def why_not_groups(resp: SearchResponse, req: SearchRequest, tr: Translator) -> list[dict]:
    """Блок «Почему не больше»: группа на КАЖДУЮ причину (имя может стоять в нескольких группах —
    числа совпадают с reason_counts). Порядок групп — порядок воронки, имён — порядок каталога."""
    ctx = request_labels(req, tr)
    groups = []
    for code in REASON_ORDER:
        items = [r for r in resp.rejected if code in r.reasons]
        if items:
            groups.append({"code": code, "n": len(items), "title": tr(f"reason.group.{code}", n=len(items), **ctx),
                           "items": [{"id": r.id, "name": r.name, "note": _note(code, r.details, tr)} for r in items]})
    return groups


def _note(code: str, d: dict, tr: Translator) -> str:
    if code == "format":
        return tr("reason.detail.format", formats=join_human([format_plural(f, tr) for f in d["formats"].split("|")], tr))
    if code == "budget":
        return tr("reason.detail.budget", price=fmt_kzt(int(d["price_from_kzt"])), over=fmt_kzt(int(d["over_by_kzt"])))
    if code == "language":
        return tr("reason.detail.language",
                  languages=join_human([label(tr, "language", x) for x in d["languages"].split("|")], tr))
    if code == "duration":
        return tr("reason.detail.duration", max=d["max_hours"])
    return ""                                                            # busy: дата уже в заголовке группы


# ---------- внутреннее ----------

def _applied(code: str, req: SearchRequest) -> bool:
    if code == "language":
        return bool(req.language)
    if code == "duration":
        return bool(req.duration_h)
    return True


def _step(step: str, n: int, tr: Translator, ctx: dict, applied: bool = True) -> dict:
    return {"step": step, "n": n, "applied": applied, "label": tr(f"funnel.{step}", **ctx)}


def _count(groups: Iterable[Iterable[str]]) -> dict[str, int]:
    counter = Counter(code for group in groups for code in group)
    return {code: counter[code] for code in REASON_ORDER if counter[code]}


def _names(names: list[str], tr: Translator) -> str:
    if len(names) <= SUMMARY_NAMES_LIMIT:
        return ", ".join(names)
    return tr("search.names_more", names=", ".join(names[:SUMMARY_NAMES_LIMIT]),
              n=len(names) - SUMMARY_NAMES_LIMIT)


def _summary(status: str, tr: Translator, ctx: dict, *, total_city: int, passed: int, more: int,
             rejected: list[Rejection]) -> str:
    key = "search.summary.found_all" if status == "found" and more == 0 else f"search.summary.{status}"
    head = tr(key, passed=passed, total=total_city, more=more, **ctx)
    parts = []
    for code in REASON_ORDER:                                            # группировка по primary
        names = [r.name for r in rejected if r.primary == code]
        if names:
            parts.append(tr(f"search.why.{code}", names=_names(names, tr), **ctx))
    if not parts:
        return head + "."
    key = "search.summary.tail_all" if status == "none_match" else "search.summary.tail_rest"
    return tr(key, head=head, reasons="; ".join(parts))


def _cards(top, req: SearchRequest, breakdowns: dict, tr: Translator) -> list[Card]:
    explained = explain_cards(top, req, [breakdowns[c.id].total for c in top], tr)
    return [
        Card(id=c.id, name=c.name, category=req.category, city=c.city, price_from_kzt=c.price_from_kzt,
             badges=badges_for(c, req), explanation=text, atoms=atoms,
             score=round(breakdowns[c.id].total, 4), score_breakdown=breakdowns[c.id].as_dict())
        for c, (atoms, text) in zip(top, explained)
    ]


def _no_category(catalog: Catalog, req: SearchRequest, tr: Translator, ctx: dict, funnel: list) -> SearchResponse:
    places = []
    for city in CITIES:
        members = catalog.in_category_city(req.category, city) if city != req.city else []
        if members:
            places.append({"city": city, "n": len(members), "synthetic": sum(c.synthetic for c in members)})
    places.sort(key=lambda p: (-p["n"], CITIES.index(p["city"])))
    items = [tr("search.other_city.item_synthetic" if p["synthetic"] else "search.other_city.item",
                city=label(tr, "city", p["city"]), n=p["n"], m=p["synthetic"]) for p in places]
    hints = []
    if places:
        summary = tr("search.summary.no_category_in_city", places="; ".join(items), **ctx)
        hints.append({"type": "other_city", "text": tr("search.hint.other_city", places="; ".join(items), **ctx),
                      "places": places})
    else:
        summary = tr("search.summary.no_category_anywhere", **ctx)
    return SearchResponse(status="no_category_in_city", summary=summary, funnel=funnel, hints=hints,
                          meta=_meta(req, primary_counts={}))


def _window_labels() -> dict:
    s = WINDOW_START.split("-")
    e = WINDOW_END.split("-")
    return {"start": f"{s[2]}.{s[1]}", "end": f"{e[2]}.{e[1]}.{e[0]}"}


def _invalid(req: SearchRequest, errors: list[dict], tr: Translator) -> SearchResponse:
    hints = []
    for e in errors:
        field_label = tr(FIELD_LABEL_KEYS[e["field"]])
        key = "form.error.required" if e["code"] == "required" else f"form.error.{e['field']}.{e['code']}"
        text = tr(key, value=e["value"], field=field_label, **_window_labels())
        hints.append({"type": "fix", "field": e["field"], "code": e["code"], "text": text})
    summary = tr("search.summary.invalid_request", errors=". ".join(h["text"] for h in hints))
    return SearchResponse(status="invalid_request", summary=summary, hints=hints,
                          meta=_meta(req, primary_counts={}))


def _meta(req: SearchRequest, primary_counts: dict) -> dict:
    return {"engine": ENGINE_VERSION, "scoring": SCORING_VERSION, "weights": dict(WEIGHTS),
            "llm_used": False, "primary_counts": primary_counts, "request": req.to_dict()}
