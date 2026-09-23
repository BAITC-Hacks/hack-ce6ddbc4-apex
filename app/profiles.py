"""Phase 6: contractor profile — availability calendar and summaries. Pure functions, no FastAPI."""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
from urllib.parse import urlencode

from matcher.data import WINDOW_END, WINDOW_START
from matcher.models import Contractor

NEAR_DAYS = 30  # "next 30 days" counts from the window start (23.09), never date.today(): output and tests stay deterministic
FLAGS = ("synthetic", "price_imputed", "city_imputed")


@dataclass(frozen=True)
class CalendarDay:
    iso: str      # "2026-10-10"
    day: int
    month: int
    weekday: int  # 0 = Monday … 6 = Sunday
    state: str    # "free" | "busy" | "out" (before 23.09 — outside the catalog window)


@dataclass(frozen=True)
class CalendarMonth:
    year: int
    month: int
    weeks: tuple      # weeks of 7 cells: CalendarDay or None (a day of the neighbouring month)
    days: int         # days of this month inside the window (September — 8, the rest — whole)
    free: int
    free_days: tuple  # numbers of free days — for the text list under the grid


def window_dates(start: str = WINDOW_START, end: str = WINDOW_END) -> list[str]:
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    return [(first + timedelta(days=i)).isoformat() for i in range((last - first).days + 1)]


def build_calendar(busy_dates, start: str = WINDOW_START, end: str = WINDOW_END) -> list[CalendarMonth]:
    """Window months → weeks (from Monday) → days. September 1–22 is drawn as "no data"."""
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    busy, grid, months = set(busy_dates), calendar.Calendar(firstweekday=0), []
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month):
        weeks, free_days, days = [], [], 0
        for week in grid.monthdatescalendar(year, month):
            row: list[Optional[CalendarDay]] = []
            for d in week:
                if d.month != month:
                    row.append(None)
                    continue
                state = "out"
                if first <= d <= last:
                    days += 1
                    state = "busy" if d.isoformat() in busy else "free"
                    if state == "free":
                        free_days.append(d.day)
                row.append(CalendarDay(d.isoformat(), d.day, d.month, d.weekday(), state))
            weeks.append(tuple(row))
        months.append(CalendarMonth(year, month, tuple(weeks), days, len(free_days), tuple(free_days)))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def availability(c: Contractor) -> dict:
    """Occupancy summary over the catalog window; one source for both the page and the API."""
    days = window_dates()
    near = days[:NEAR_DAYS]
    by_month: dict[str, dict[str, int]] = {}
    for d in days:
        slot = by_month.setdefault(d[:7], {"days": 0, "free": 0})
        slot["days"] += 1
        slot["free"] += d not in c.busy_dates
    busy = sorted(set(c.busy_dates) & set(days))
    return {
        "window": {"start": days[0], "end": days[-1], "days": len(days)},
        "busy_dates": busy,
        "busy_days_count": len(busy),
        "free_days_count": len(days) - len(busy),
        "free_next_30": {"start": near[0], "end": near[-1], "days": len(near),
                         "free": sum(d not in c.busy_dates for d in near)},
        "free_by_month": by_month,
    }


def day_state(c: Contractor, iso: str) -> Optional[str]:
    """State of one requested date: free/busy inside the window, "out" outside it, None if not a date."""
    try:
        day = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return None
    if day.isoformat() != iso:
        return None
    if not WINDOW_START <= iso <= WINDOW_END:
        return "out"
    return "busy" if iso in c.busy_dates else "free"


def profile_payload(c: Contractor) -> dict:
    """JSON for GET /api/contractors/{id}: catalog fields as in the CSV (Russian values) + occupancy."""
    return {
        "id": c.id, "name": c.name, "categories": list(c.categories), "city": c.city,
        "price_from_kzt": c.price_from_kzt, "event_formats": list(c.event_formats),
        "languages": list(c.languages), "max_hours": c.max_hours, "description": c.description,
        "synthetic": c.synthetic, "price_imputed": c.price_imputed, "city_imputed": c.city_imputed,
        **availability(c),
    }


def badges_for(c: Contractor) -> list[str]:
    return [flag for flag in FLAGS if getattr(c, flag)]


def search_url(city: str, category: str) -> str:
    """"Find similar": /app with city and category; the customer adds date, event type and budget."""
    return "/app?" + urlencode({"city": city, "category": category})
