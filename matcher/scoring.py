"""Скоринг v2: прозрачная линейная формула, каждый фактор нормирован в [0, 1] и виден в карточке."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .evidence import TfidfIndex, build_query, get_index
from .facts import Facts, extract_facts
from .models import Contractor, SearchRequest

SCORING_VERSION = "2.0"
WEIGHTS = {"budget_fit": 0.30, "relevance": 0.25, "focus": 0.20,
           "experience": 0.15, "extras": 0.10, "flags": -0.05}
FORMAT_FAMILY = {  # «родственные» форматы: узкий профиль = все форматы из одного семейства
    "свадьба": ("свадьба", "той"), "той": ("свадьба", "той"),
    "корпоратив": ("корпоратив", "конференция"), "конференция": ("корпоратив", "конференция"),
    "юбилей": ("юбилей", "день рождения"), "день рождения": ("юбилей", "день рождения"),
}
RELEVANT_MENTIONS = {  # какие упоминания из facts.formats_mentioned подтверждают формат запроса
    "свадьба": ("kyz_uzatu", "betashar", "tusaukeser"), "той": ("kyz_uzatu", "betashar", "tusaukeser"),
    "корпоратив": ("teambuilding", "forum"), "конференция": ("forum", "conference"),
    "юбилей": (), "день рождения": (),
}
VENUE_CATEGORIES = ("Банкетный зал", "Ресторан", "Загородная площадка", "Отель")
YEARS_CAP, EVENTS_CAP, SLACK_CAP, EXTRA_LANG_CAP = 15, 1000, 4, 2


@dataclass
class ScoreContext:
    req: SearchRequest
    pool: list[Contractor]            # прошли все фильтры (в порядке каталога)
    facts: dict[str, Facts]
    relevance_raw: dict[str, float]   # косинус описания и запроса
    index: TfidfIndex
    query: str


@dataclass(frozen=True)
class ScoreBreakdown:
    total: float
    parts: dict                       # нормированные факторы [0, 1], округлены до 4 знаков


def budget_fit(c: Contractor, req: SearchRequest) -> float:
    """Доля бюджета, которая остаётся: 900 000 при 1 000 000 → 0.1; цена = бюджет → 0."""
    if req.budget_kzt <= 0:
        return 0.0
    return max(0.0, min(1.0, 1 - c.price_from_kzt / req.budget_kzt))


def focus(c: Contractor, req: SearchRequest) -> float:
    """Доля форматов профиля из семейства запроса: «свадьба, той» для свадьбы → 1.0."""
    family = FORMAT_FAMILY.get(req.event_type, (req.event_type,))
    return sum(f in family for f in c.event_formats) / len(c.event_formats) if c.event_formats else 0.0


def experience(f: Facts) -> float:
    years = min(f.years_min or 0, YEARS_CAP) / YEARS_CAP
    events = min(math.log1p(f.events_count or 0) / math.log1p(EVENTS_CAP), 1.0)
    return 0.5 * years + 0.5 * events


def hours_slack(c: Contractor, req: SearchRequest) -> Optional[int]:
    if not req.duration_h or c.max_hours is None:
        return None
    return c.max_hours - req.duration_h


def extra_languages(c: Contractor, req: SearchRequest) -> tuple[str, ...]:
    base = req.language or (c.languages[0] if c.languages else None)
    return tuple(x for x in c.languages if x != base)


def relevant_mentions(f: Facts, req: SearchRequest) -> tuple[str, ...]:
    wanted = RELEVANT_MENTIONS.get(req.event_type, ())
    return tuple(m for m in f.formats_mentioned if m in wanted)


def venues_of(c: Contractor) -> tuple[str, ...]:
    return tuple(x for x in c.categories if x in VENUE_CATEGORIES)


def extras(c: Contractor, req: SearchRequest, f: Facts) -> float:
    lang = min(len(extra_languages(c, req)), EXTRA_LANG_CAP) / EXTRA_LANG_CAP
    slack = min(max(hours_slack(c, req) or 0, 0), SLACK_CAP) / SLACK_CAP
    mention = 1.0 if (relevant_mentions(f, req) or len(venues_of(c)) >= 2 or (f.audience_max or 0) >= 500) else 0.0
    return (lang + slack + mention) / 3


def flags(c: Contractor) -> float:
    return min(1.0, 0.6 * c.synthetic + 0.2 * c.price_imputed + 0.2 * c.city_imputed)


def build_context(catalog, req: SearchRequest, pool: list[Contractor]) -> ScoreContext:
    index = get_index(catalog)
    query = build_query(req)
    qvec = index.vector(query)
    return ScoreContext(
        req=req,
        pool=list(pool),
        facts={c.id: extract_facts(c.description) for c in pool},
        relevance_raw={c.id: index.similarity(c.id, qvec) for c in pool},
        index=index,
        query=query,
    )


def score(c: Contractor, req: SearchRequest, ctx: ScoreContext) -> ScoreBreakdown:
    top = max(ctx.relevance_raw.values(), default=0.0)
    parts = {
        "budget_fit": budget_fit(c, req),
        "relevance": ctx.relevance_raw.get(c.id, 0.0) / top if top > 0 else 0.0,  # 1.0 у самого близкого
        "focus": focus(c, req),
        "experience": experience(ctx.facts[c.id]),
        "extras": extras(c, req, ctx.facts[c.id]),
        "flags": flags(c),
    }
    parts = {k: round(v, 4) for k, v in parts.items()}
    total = round(sum(WEIGHTS[k] * v for k, v in parts.items()), 4)
    return ScoreBreakdown(total=total, parts=parts)


def rank(pool: list[Contractor], req: SearchRequest, ctx: ScoreContext) -> list[tuple[Contractor, ScoreBreakdown]]:
    scored = [(c, score(c, req, ctx)) for c in pool]
    return sorted(scored, key=lambda pair: (-round(pair[1].total, 4), pair[0].price_from_kzt, pair[0].id))
