"""Domain records shared by the catalog and the matching engine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Literal, Optional

Status = Literal["found", "partial", "no_category_in_city", "none_match", "invalid_request"]
ReasonCode = Literal["busy", "format", "budget", "language", "duration"]

STATUSES: tuple[str, ...] = ("found", "partial", "no_category_in_city", "none_match", "invalid_request")
REASON_ORDER: tuple[str, ...] = ("busy", "format", "budget", "language", "duration")   # funnel order
MAX_CARDS = 3


@dataclass(frozen=True)
class Contractor:
    id: str
    name: str
    categories: tuple[str, ...]
    city: str
    price_from_kzt: int
    event_formats: tuple[str, ...]
    languages: tuple[str, ...]
    max_hours: Optional[int]
    busy_dates: frozenset[str]
    description: str
    synthetic: bool
    city_imputed: bool
    price_imputed: bool

    def is_free(self, date_iso: str) -> bool:
        """Check a date within the published calendar window."""
        return date_iso not in self.busy_dates

    def has_category(self, category: str) -> bool:
        # Exact list membership: a ceremony host is not a general event host.
        return category in self.categories


@dataclass(frozen=True)
class SearchRequest:
    city: str
    date: str                           # "YYYY-MM-DD"
    event_type: str
    category: str
    budget_kzt: int
    duration_h: Optional[int] = None
    language: Optional[str] = None
    wishes: Optional[str] = None        # stored in v1; never placed into URLs (Phase 1 privacy rule)
    lang: str = "ru"                    # language of response texts

    def to_dict(self) -> dict:
        return asdict(self)

    def canonical_json(self) -> str:
        """History key (phase 6): without lang - language does not change matching."""
        data = {k: v for k, v in self.to_dict().items() if k != "lang"}
        return json.dumps(data, ensure_ascii=False, sort_keys=True)

    def to_query(self) -> dict[str, str]:
        """Reverse mapping to the /app query: budget_kzt->budget, duration_h->duration.
        Free-text wishes are NEVER put into the URL."""
        q = {"city": self.city, "date": self.date, "event_type": self.event_type,
             "category": self.category, "budget": str(self.budget_kzt)}
        if self.duration_h is not None:
            q["duration"] = str(self.duration_h)
        if self.language:
            q["language"] = self.language
        return q


@dataclass
class Atom:
    type: str        # budget|format_focus|language|duration|quote|experience|venue_multi|flag|contrast|availability
    text: str
    unique: bool = False
    weight: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Card:
    id: str
    name: str
    category: str
    city: str
    price_from_kzt: int
    badges: list[str]                   # synthetic|price_imputed|city_imputed|price_equals_budget
    explanation: str                    # 1-2 sentences
    atoms: list[Atom]
    score: float
    score_breakdown: dict[str, float]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Rejection:
    id: str
    name: str
    reasons: list[str]                  # ReasonCode in funnel order; reasons[0] is primary
    details: dict[str, str]

    @property
    def primary(self) -> str:
        return self.reasons[0]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SearchResponse:
    status: str                         # Status
    summary: str
    cards: list[Card] = field(default_factory=list)
    more_count: int = 0
    rejected: list[Rejection] = field(default_factory=list)
    reason_counts: dict[str, int] = field(default_factory=dict)
    funnel: list[dict] = field(default_factory=list)
    hints: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    why_not: list[dict] = field(default_factory=list)   # [P5] [{"reason": "busy", "ids": [...], "text": "..."}]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)
