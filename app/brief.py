"""Web adapter for the five-condition guest brief.

The module normalises and checks the query values that the landing form sends to
`/app`. It does not rank contractors and it is not the future `SearchResponse`.
The browser mirrors these rules in `static/js/brief.js`; tests keep both honest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional
from urllib.parse import urlencode

FIELDS = ("city", "date", "event_type", "category", "budget")
STORAGE_KEY = "tandau.brief.v1"

# Largest integer that JSON numbers carry exactly between the browser and Python.
# This is a transport limit, not a market cap on event budgets.
BUDGET_MAX = 9_007_199_254_740_991
# Regular, no-break and narrow no-break spaces are accepted as digit separators.
BUDGET_SPACES = (" ", "\u00a0", "\u202f")
_DIGITS = re.compile(r"[0-9]+")
_NEGATIVE = re.compile(r"-[0-9]+")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

# The fixed, labelled scenario of the landing example. Only these five values can
# be copied into the form; language and hours stay in the example caption.
EXAMPLE_VALUES = {
    "city": "Алматы",
    "date": "2026-10-17",
    "event_type": "свадьба",
    "category": "Ведущий",
    "budget": "1000000",
}
EXAMPLE_LANGUAGE = "казахский"
EXAMPLE_HOURS = 8

ERRORS = {
    "city": {"missing": "brief.city.error", "invalid": "brief.city.unknown"},
    "date": {"missing": "brief.date.error", "invalid": "brief.date.invalid", "window": "brief.date.window"},
    "event_type": {"missing": "brief.event_type.error", "invalid": "brief.event_type.unknown"},
    "category": {"missing": "brief.category.error", "invalid": "brief.category.error"},
    "budget": {
        "missing": "brief.budget.error", "positive": "brief.budget.positive",
        "integer": "brief.budget.integer", "too_large": "brief.budget.too_large",
    },
}
DUPLICATE_ERROR = "brief.errors.duplicate"


@dataclass(frozen=True)
class Choices:
    """Canonical allowlists taken from the loaded catalog."""

    cities: tuple[str, ...]
    event_formats: tuple[str, ...]
    categories: tuple[str, ...]
    window_start: str
    window_end: str

    @classmethod
    def from_meta(cls, meta: dict) -> "Choices":
        return cls(
            cities=tuple(meta["cities"]),
            event_formats=tuple(meta["event_formats"]),
            categories=tuple(row["name"] for row in meta["categories"]),
            window_start=meta["window"]["start"],
            window_end=meta["window"]["end"],
        )


@dataclass(frozen=True)
class FieldResult:
    name: str
    raw: str
    value: object = None
    error: Optional[str] = None

    @property
    def missing(self) -> bool:
        return self.error is None and self.value is None

    @property
    def valid(self) -> bool:
        return self.error is None and self.value is not None


@dataclass(frozen=True)
class Brief:
    fields: dict[str, FieldResult]
    present: bool = False

    def __getitem__(self, name: str) -> FieldResult:
        return self.fields[name]

    @property
    def filled(self) -> int:
        return sum(item.valid for item in self.fields.values())

    @property
    def complete(self) -> bool:
        return self.filled == len(FIELDS)

    @property
    def invalid(self) -> list[FieldResult]:
        return [self.fields[name] for name in FIELDS if self.fields[name].error]

    @property
    def missing(self) -> list[FieldResult]:
        return [self.fields[name] for name in FIELDS if self.fields[name].missing]

    @property
    def state(self) -> str:
        if not self.present:
            return "empty"
        if self.invalid:
            return "invalid"
        if self.complete:
            return "ready"
        return "incomplete"

    def form_values(self) -> dict[str, str]:
        """Strings for form controls and links: canonical when valid, raw otherwise."""
        values = {}
        for name in FIELDS:
            item = self.fields[name]
            if item.valid:
                values[name] = str(item.value)
            elif item.error == DUPLICATE_ERROR:
                values[name] = ""
            else:
                values[name] = item.raw
        return values

    def query(self, **overrides: str) -> str:
        """Encode all five conditions for a URL; unknown parameters never pass."""
        values = self.form_values()
        values.update({key: value for key, value in overrides.items() if key in FIELDS})
        return urlencode([(name, values[name]) for name in FIELDS])

    def normalized(self, lang: str) -> dict:
        """The input shape reserved for the phase-four engine."""
        return {
            "city": self["city"].value,
            "date": self["date"].value,
            "event_type": self["event_type"].value,
            "category": self["category"].value,
            "budget_kzt": self["budget"].value,
            "duration_h": None,
            "language": None,
            "wishes": None,
            "lang": lang,
        }


def normalize_budget(raw: str) -> tuple[Optional[int], Optional[str]]:
    """Return (value, error kind). Empty input is (None, None)."""
    compact = raw
    for space in BUDGET_SPACES:
        compact = compact.replace(space, "")
    if compact == "":
        return None, None
    if _NEGATIVE.fullmatch(compact):
        return None, "positive"
    if not _DIGITS.fullmatch(compact):
        return None, "integer"
    digits = compact.lstrip("0") or "0"
    if len(digits) > len(str(BUDGET_MAX)) or int(digits) > BUDGET_MAX:
        return None, "too_large"
    value = int(digits)
    if value <= 0:
        return None, "positive"
    return value, None


def _check_date(raw: str, choices: Choices) -> tuple[Optional[str], Optional[str]]:
    if not _ISO_DATE.fullmatch(raw):
        return None, "invalid"
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        return None, "invalid"
    iso = parsed.isoformat()
    if not choices.window_start <= iso <= choices.window_end:
        return None, "window"
    return iso, None


def check_field(name: str, raw: str, choices: Choices) -> FieldResult:
    errors = ERRORS[name]
    if name == "budget":
        value, kind = normalize_budget(raw)
        if value is None and kind is None:
            return FieldResult(name, raw)
        return FieldResult(name, raw, value, errors[kind] if kind else None)
    if raw == "":
        return FieldResult(name, raw)
    if name == "date":
        value, kind = _check_date(raw, choices)
        return FieldResult(name, raw, value, errors[kind] if kind else None)
    allowed = {
        "city": choices.cities,
        "event_type": choices.event_formats,
        "category": choices.categories,
    }[name]
    # Whole-value comparison: «Ведущий» never matches «Ведущий церемонии».
    if raw in allowed:
        return FieldResult(name, raw, raw)
    return FieldResult(name, raw, None, errors["invalid"])


def parse_brief(items: Iterable[tuple[str, str]], choices: Choices) -> Brief:
    """Build a brief from query items; extra parameters are ignored."""
    collected: dict[str, list[str]] = {name: [] for name in FIELDS}
    for key, value in items:
        if key in collected:
            collected[key].append(value)
    fields = {}
    for name in FIELDS:
        values = collected[name]
        if len(values) > 1:
            fields[name] = FieldResult(name, values[0], None, DUPLICATE_ERROR)
        else:
            fields[name] = check_field(name, values[0] if values else "", choices)
    present = any(collected[name] for name in FIELDS)
    return Brief(fields=fields, present=present)


def empty_brief(choices: Choices) -> Brief:
    return parse_brief((), choices)


def example_brief(choices: Choices) -> Brief:
    return parse_brief(EXAMPLE_VALUES.items(), choices)
