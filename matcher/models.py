"""Domain records shared by the catalog and the future matching engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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
