"""Скоринг v1: прозрачный балл из двух компонент. Фаза 5 (v2) добавит relevance/experience/extras/flags."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional

from .models import Contractor, SearchRequest

SCORING_VERSION = "v1"
Component = Callable[[Contractor, SearchRequest, dict], float]

MENTION_BONUS = 0.25
FORMAT_STEMS: dict[str, tuple[str, ...]] = {        # поиск по началу слова в описании (ё → е)
    "свадьба": ("свад",),
    "той": ("тоя", "тою", "тоем", "тоев", "тои"),   # голое «той» не ищем: совпадает с местоимением
    "корпоратив": ("корпоратив",),
    "конференция": ("конференц", "форум"),
    "юбилей": ("юбиле",),
    "день рождения": ("день рождения", "дня рождения", "дни рождения", "днем рождения"),
}


def budget_fit(price: int, budget: int) -> float:
    """r = price/budget: ≤0.2 → 0.5; 0.2…0.5 → линейно 0.5…1.0; 0.5…0.9 → 1.0; 0.9…1.0 → линейно 1.0…0.6."""
    if budget <= 0 or price > budget:
        return 0.0
    r = price / budget
    if r <= 0.2:
        return 0.5
    if r < 0.5:
        return 0.5 + (r - 0.2) / 0.3 * 0.5
    if r <= 0.9:
        return 1.0
    return 1.0 - (r - 0.9) / 0.1 * 0.4


def format_mentioned(description: str, event_type: str) -> bool:
    text = description.lower().replace("ё", "е")
    for stem in FORMAT_STEMS.get(event_type, (event_type,)):
        if re.search(r"(?<![а-яa-z])" + re.escape(stem), text):
            return True
    return False


def _budget_component(c: Contractor, req: SearchRequest, ctx: dict) -> float:
    return budget_fit(c.price_from_kzt, req.budget_kzt)


def _focus_component(c: Contractor, req: SearchRequest, ctx: dict) -> float:
    base = 1.0 / max(1, len(c.event_formats))            # узкий профиль → выше
    bonus = MENTION_BONUS if format_mentioned(c.description, req.event_type) else 0.0
    return min(1.0, base + bonus)


# Точка расширения фазы 5: COMPONENTS.update({...}) + новые WEIGHTS (v2), сумма весов = 1.0
COMPONENTS: dict[str, Component] = {"budget_fit": _budget_component, "focus": _focus_component}
WEIGHTS: dict[str, float] = {"budget_fit": 0.6, "focus": 0.4}


@dataclass(frozen=True)
class ScoreBreakdown:
    components: dict[str, float]     # значения 0..1 до весов
    weights: dict[str, float]
    notes: dict[str, float]          # невзвешенные пояснения для UI
    total: float

    def as_dict(self) -> dict[str, float]:
        d = {k: round(v, 4) for k, v in self.components.items()}
        d.update({k: round(v, 4) for k, v in self.notes.items()})
        d["total"] = round(self.total, 4)
        return d


def score(c: Contractor, req: SearchRequest, ctx: Optional[dict] = None) -> ScoreBreakdown:
    ctx = ctx or {}
    components = {name: COMPONENTS[name](c, req, ctx) for name in WEIGHTS}
    total = sum(WEIGHTS[name] * value for name, value in components.items())
    notes = {"format_in_description": 1.0 if format_mentioned(c.description, req.event_type) else 0.0}
    return ScoreBreakdown(components, dict(WEIGHTS), notes, round(total, 4))


def sort_key(c: Contractor, breakdown: ScoreBreakdown) -> tuple:
    """Детерминированный порядок: балл ↓, цена ↑, id ↑. Никакого random."""
    return (-round(breakdown.total, 4), c.price_from_kzt, c.id)
