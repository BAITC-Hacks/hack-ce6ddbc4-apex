"""Load the organiser's CSV and build deterministic catalog metadata."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from .models import Contractor

# Calendar coverage is supplied by the organiser, not inferred from busy dates:
# an unbooked day at either end is still inside the availability calendar.
WINDOW_START = "2026-09-23"
WINDOW_END = "2026-12-31"
WINDOW_DAYS = (date.fromisoformat(WINDOW_END) - date.fromisoformat(WINDOW_START)).days + 1
EVENT_FORMATS = ("свадьба", "той", "корпоратив", "конференция", "юбилей", "день рождения")
LANGUAGES = ("русский", "казахский", "английский")
CITIES = ("Алматы", "Астана", "Зарубежье")
DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "hackathon-dataset-anonymized.csv"
REQUIRED_COLUMNS = frozenset({
    "id", "anon_name", "categories", "city", "price_from_kzt", "event_formats",
    "languages", "max_hours", "busy_dates", "description", "synthetic",
    "city_imputed", "price_imputed",
})


def _split(value: Optional[str]) -> tuple[str, ...]:
    return tuple(part.strip() for part in (value or "").split("|") if part.strip())


def _bool(value: Optional[str]) -> bool:
    normalized = (value or "").strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"expected True/False, got {value!r}")
    return normalized == "true"


def _int_or_none(value: Optional[str]) -> Optional[int]:
    value = (value or "").strip()
    return int(value) if value else None


def parse_row(row: dict[str, str]) -> Contractor:
    """Parse one CSV row without changing the original Russian data values."""
    contractor = Contractor(
        id=row["id"].strip(),
        name=row["anon_name"].strip(),
        categories=_split(row["categories"]),
        city=row["city"].strip(),
        price_from_kzt=int(row["price_from_kzt"]),
        event_formats=_split(row["event_formats"]),
        languages=_split(row["languages"]),
        max_hours=_int_or_none(row["max_hours"]),
        busy_dates=frozenset(_split(row["busy_dates"])),
        description=(row.get("description") or "").strip(),
        synthetic=_bool(row["synthetic"]),
        city_imputed=_bool(row["city_imputed"]),
        price_imputed=_bool(row["price_imputed"]),
    )
    if not all((contractor.id, contractor.name, contractor.city, contractor.categories,
                contractor.event_formats, contractor.languages)):
        raise ValueError("id, name, city, categories, event_formats and languages must not be empty")
    if contractor.price_from_kzt <= 0:
        raise ValueError("price_from_kzt must be positive")
    if contractor.max_hours is not None and contractor.max_hours <= 0:
        raise ValueError("max_hours must be positive or empty")
    if len(set(contractor.categories)) != len(contractor.categories):
        raise ValueError("categories must not contain duplicates")
    for busy_date in sorted(contractor.busy_dates):
        if date.fromisoformat(busy_date).isoformat() != busy_date:
            raise ValueError(f"busy date must use YYYY-MM-DD: {busy_date!r}")
        if not WINDOW_START <= busy_date <= WINDOW_END:
            raise ValueError(f"busy date outside calendar window: {busy_date}")
    return contractor


def _ordered_values(values: set[str], preferred_order: tuple[str, ...]) -> list[str]:
    """Keep familiar form ordering while deriving available options from data."""
    return [value for value in preferred_order if value in values] + sorted(values.difference(preferred_order))


@dataclass(frozen=True)
class Catalog:
    contractors: tuple[Contractor, ...]
    by_id: dict[str, Contractor]
    category_city_counts: dict[str, dict[str, int]]
    categories: tuple[str, ...]

    def in_category_city(self, category: str, city: str) -> list[Contractor]:
        return [c for c in self.contractors if c.has_category(category) and c.city == city]

    def stats(self) -> dict[str, int]:
        return {
            "profiles": len(self.contractors),
            "categories": len(self.categories),
            "cities": len({c.city for c in self.contractors}),
            "days": WINDOW_DAYS,
            "synthetic": sum(c.synthetic for c in self.contractors),
            "price_imputed": sum(c.price_imputed for c in self.contractors),
            "city_imputed": sum(c.city_imputed for c in self.contractors),
        }

    def category_rows(self) -> list[dict]:
        return [
            {"name": name, "total": sum(self.category_city_counts[name].values()),
             "by_city": dict(self.category_city_counts[name])}
            for name in self.categories
        ]

    def meta(self) -> dict:
        return {
            "cities": _ordered_values({c.city for c in self.contractors}, CITIES),
            "categories": self.category_rows(),
            "event_formats": _ordered_values({f for c in self.contractors for f in c.event_formats}, EVENT_FORMATS),
            "languages": _ordered_values({lang for c in self.contractors for lang in c.languages}, LANGUAGES),
            "window": {"start": WINDOW_START, "end": WINDOW_END, "days": WINDOW_DAYS},
            "stats": self.stats(),
        }


def load_catalog(path: Path | str | None = None) -> Catalog:
    """Load UTF-8 CSV, rejecting malformed records before serving partial data."""
    catalog_path = Path(path) if path is not None else DEFAULT_CATALOG_PATH
    contractors_list = []
    ids = set()
    with catalog_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{catalog_path}: missing CSV columns: {', '.join(sorted(missing))}")
        for row in reader:
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("row does not match CSV columns")
                contractor = parse_row(row)
                if contractor.id in ids:
                    raise ValueError(f"duplicate contractor id: {contractor.id}")
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                raise ValueError(f"{catalog_path}, CSV line {reader.line_num}: {exc}") from exc
            ids.add(contractor.id)
            contractors_list.append(contractor)
    if not contractors_list:
        raise ValueError(f"{catalog_path}: catalog contains no profiles")
    contractors = tuple(contractors_list)
    counts: dict[str, Counter] = defaultdict(Counter)
    for contractor in contractors:
        for category in contractor.categories:
            counts[category][contractor.city] += 1
    categories = tuple(sorted(counts, key=lambda name: (-sum(counts[name].values()), name)))
    return Catalog(
        contractors=contractors,
        by_id={c.id: c for c in contractors},
        category_city_counts={name: dict(sorted(counts[name].items())) for name in categories},
        categories=categories,
    )
