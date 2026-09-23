from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..brief import (
    BUDGET_MAX, EXAMPLE_HOURS, EXAMPLE_LANGUAGE, EXAMPLE_VALUES, FIELDS, STORAGE_KEY,
    Choices, example_brief, parse_brief,
)
from ..i18n import SUPPORTED, get_lang, translate
from ..search import search_context
from ..web import date_parts, render

router = APIRouter()

EXAMPLE_PROFILES = (
    ("HK-42352", "landing.example.card1", "Статистика: 356 свадеб, 0 разводов"),
    ("HK-35215", "landing.example.card2", "Работает на казахском, русском и английском языках"),
    ("HK-77838", "landing.example.card3", "актёр театра и кино"),
)
EXAMPLE_CATEGORY = EXAMPLE_VALUES["category"]
EXAMPLE_DATE = EXAMPLE_VALUES["date"]
EXAMPLE_BUDGET = int(EXAMPLE_VALUES["budget"])

# Strings the brief script needs; the server stays the single source of wording.
CLIENT_TEXT_KEYS = (
    "brief.city.error", "brief.city.unknown", "brief.date.error", "brief.date.invalid",
    "brief.date.window", "brief.date.empty", "brief.event_type.error", "brief.event_type.unknown",
    "brief.category.error", "brief.category.coverage",
    "brief.category.coverage_zero", "brief.category.coverage_city",
    "brief.budget.error", "brief.budget.positive", "brief.budget.integer",
    "brief.budget.too_large", "brief.errors.duplicate", "brief.errors.title",
    "brief.draft.restored", "brief.draft.unavailable", "brief.draft.cleared",
    "brief.draft.example_filled", "brief.draft.category_selected",
    "brief.category.help_empty", "landing.event_card.city_empty", "landing.event_card.date_empty",
    "landing.event_card.event_type_empty", "landing.event_card.category_empty",
    "landing.event_card.budget_empty", "landing.event_card.budget_value",
    "landing.event_card.progress", "landing.event_card.announce",
    "landing.catalog.zero", "landing.catalog.caption_all", "landing.catalog.caption_city",
    "date.full",
)


def _example_cards(catalog) -> list[dict]:
    """Three fixed catalogue records; missing ones are never replaced."""
    cards = []
    for profile_id, text_key, quote in EXAMPLE_PROFILES:
        profile = catalog.by_id.get(profile_id)
        if profile is None:
            continue
        badges = [
            flag for flag in ("synthetic", "price_imputed", "city_imputed")
            if getattr(profile, flag)
        ]
        if profile.price_from_kzt == EXAMPLE_BUDGET:
            badges.append("price_equals_budget")
        cards.append({
            "id": profile.id,
            "name": profile.name,
            "category": EXAMPLE_CATEGORY,
            "city": profile.city,
            "price": profile.price_from_kzt,
            "headroom": EXAMPLE_BUDGET - profile.price_from_kzt,
            "share": round(profile.price_from_kzt * 100 / EXAMPLE_BUDGET),
            "badges": badges,
            "text_key": text_key,
            "quote": quote if quote in profile.description else None,
            "hours": profile.max_hours,
            "languages": profile.languages,
            "speaks_example_language": EXAMPLE_LANGUAGE in profile.languages,
            "event_formats": profile.event_formats,
            "demo_date_available": profile.is_free(EXAMPLE_DATE),
            "flags": {flag: getattr(profile, flag) for flag in ("synthetic", "price_imputed", "city_imputed")},
        })
    return cards


def _client_config(lang: str, meta: dict) -> dict:
    t = lambda key: translate(lang, key)  # noqa: E731
    return {
        "storageKey": STORAGE_KEY,
        "fields": list(FIELDS),
        "budgetMax": str(BUDGET_MAX),
        "window": meta["window"],
        "cities": meta["cities"],
        "formats": meta["event_formats"],
        "categories": [row["name"] for row in meta["categories"]],
        "counts": {row["name"]: row["by_city"] for row in meta["categories"]},
        "totals": {row["name"]: row["total"] for row in meta["categories"]},
        "example": EXAMPLE_VALUES,
        "labels": {
            "city": {value: translate(lang, f"data.city.{value}") for value in meta["cities"]},
            "event_type": {value: translate(lang, f"data.format.{value}") for value in meta["event_formats"]},
            "category": {row["name"]: translate(lang, f"data.category.{row['name']}") for row in meta["categories"]},
        },
        "fieldLabels": {name: t(f"brief.{name}.label") for name in FIELDS},
        "months": [t(f"date.month.{n}") for n in range(1, 13)],
        "monthsGenitive": [t(f"date.month_genitive.{n}") for n in range(1, 13)],
        "monthsShort": [t(f"date.month_short.{n}") for n in range(1, 13)],
        "weekdays": [t(f"date.weekday.{n}") for n in range(7)],
        "text": {key: t(key) for key in CLIENT_TEXT_KEYS},
    }


def _catalog_city(brief) -> str:
    city = brief["city"]
    return city.value if city.valid else ""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing(request: Request):
    catalog = request.app.state.catalog
    lang = get_lang(request)
    meta = catalog.meta()
    choices = Choices.from_meta(meta)
    brief = parse_brief(request.query_params.multi_items(), choices)
    city_totals = Counter(contractor.city for contractor in catalog.contractors)
    return render(
        request,
        "landing.html",
        stats=catalog.stats(),
        categories=catalog.category_rows(),
        example_cards=_example_cards(catalog),
        example_expected=len(EXAMPLE_PROFILES),
        example=example_brief(choices),
        example_query=urlencode(list(EXAMPLE_VALUES.items())),
        example_language=EXAMPLE_LANGUAGE,
        example_hours=EXAMPLE_HOURS,
        meta=meta,
        brief=brief,
        city_totals=city_totals,
        catalog_city=_catalog_city(brief),
        budget_presets=(500_000, 1_000_000, 2_000_000),
        client_config=_client_config(lang, meta),
    )


@router.get("/designbook", response_class=HTMLResponse, include_in_schema=False)
def designbook(request: Request):
    """Team-facing visual specimens; no matching or account mutations."""
    catalog = request.app.state.catalog
    return render(
        request,
        "designbook.html",
        stats=catalog.stats(),
        example_cards=_example_cards(catalog),
        categories=catalog.category_rows(),
        asset_briefs=json.loads(
            (Path(__file__).resolve().parents[1] / "static/assets/tandau/asset-briefs.json")
            .read_text(encoding="utf-8")
        ),
        t=lambda key, **values: translate("ru", key, **values),
    )


@router.get("/designbook/landing", response_class=HTMLResponse, include_in_schema=False)
def landing_sample(request: Request):
    """Full-page design specimen with local-only controls and fixed examples."""
    catalog = request.app.state.catalog
    return render(
        request,
        "landing_sample.html",
        stats=catalog.stats(),
        categories=catalog.category_rows(),
        example_cards=_example_cards(catalog),
        t=lambda key, **values: translate("ru", key, **values),
    )


def _unsafe_text(value: str) -> bool:
    decoded = unquote(value)
    return any(ord(char) < 32 or ord(char) == 127 for char in value + decoded) or "\\" in decoded


def _local_target(path: str, query: str, fragment: str) -> Optional[str]:
    if not path.startswith("/") or unquote(path).startswith("//"):
        return None
    query = urlencode([
        (key, value) for key, value in parse_qsl(query, keep_blank_values=True) if key != "lang"
    ])
    return urlunsplit(("", "", path, query, fragment))


def _next_target(value: str) -> Optional[str]:
    """Accept only a relative local path; anything else falls back to `/`."""
    if not value or _unsafe_text(value) or not value.startswith("/") or value.startswith("//"):
        return None
    try:
        target = urlsplit(value)
    except ValueError:
        return None
    if target.scheme or target.netloc:
        return None
    return _local_target(target.path, target.query, target.fragment)


def _language_redirect_target(request: Request) -> str:
    referer = request.headers.get("referer", "")
    # Browsers normalize backslashes and controls in URLs; reject before parsing.
    if not referer or _unsafe_text(referer):
        return "/"
    try:
        target = urlsplit(referer)
        origin = urlsplit(str(request.base_url))
        if target.scheme or target.netloc:
            if (
                target.scheme not in ("http", "https")
                or target.scheme != origin.scheme
                or target.hostname != origin.hostname
                or (target.port or (443 if target.scheme == "https" else 80))
                != (origin.port or (443 if origin.scheme == "https" else 80))
                or target.username is not None
                or target.password is not None
            ):
                return "/"
        elif not referer.startswith("/") or referer.startswith("//"):
            return "/"
        return _local_target(target.path or "/", target.query, target.fragment) or "/"
    except ValueError:
        return "/"


@router.get("/lang/{code}", include_in_schema=False)
def switch_lang(code: str, request: Request):
    next_values = request.query_params.getlist("next")
    if next_values:
        target = _next_target(next_values[0]) if len(next_values) == 1 else None
        target = target or "/"
    else:
        target = _language_redirect_target(request)
    response = RedirectResponse(target, status_code=303)
    if code in SUPPORTED:
        response.set_cookie("lang", code, max_age=365 * 24 * 3600, samesite="lax")
    return response


@router.get("/app", response_class=HTMLResponse, include_in_schema=False)
def search_page(request: Request):
    return render(request, "app/search.html", **search_context(request))


# ---------- Фаза 5: GET /app/compare ----------
import re

from matcher.compare import compare_dates, default_second_date, short_date
from matcher.data import WINDOW_END, WINDOW_START
from matcher.models import SearchRequest

from ..i18n import get_lang

QUERY_FIELDS = ("city", "event_type", "category", "budget", "language", "duration")   # wishes не передаём в URL
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _int_or_none(value):
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def _compare_request(params, date: str, lang: str):
    """Query-строка /app (город, тип, категория, budget, language, duration) → SearchRequest; None, если неполно."""
    budget = _int_or_none(params.get("budget"))
    if not (params.get("city") and params.get("event_type") and params.get("category") and budget and date):
        return None
    return SearchRequest(city=params["city"], date=date, event_type=params["event_type"], category=params["category"],
                         budget_kzt=budget, duration_h=_int_or_none(params.get("duration")),
                         language=params.get("language") or None, wishes=params.get("wishes") or None, lang=lang)


@router.get("/app/compare", response_class=HTMLResponse)
def compare_page(request: Request):
    lang, qp = get_lang(request), request.query_params
    date_a = qp.get("date_a") or qp.get("date") or ""
    date_a = date_a if ISO_DATE.match(date_a) else ""
    date_b = qp.get("date_b") or (default_second_date(date_a) if date_a else "")
    date_b = date_b if ISO_DATE.match(date_b) else ""
    req = _compare_request(qp, date_a, lang) if date_b else None
    ctx = {"date_a": date_a, "date_b": date_b, "hidden": {k: qp.get(k) for k in QUERY_FIELDS if qp.get(k)},
           "window": (WINDOW_START, WINDOW_END), "result": None, "error": None, "short_date": short_date}
    if req is None:
        ctx["error"] = "compare.need_request"
    elif date_a == date_b:
        ctx["error"] = "compare.same_dates"
    else:
        tr = lambda key, **kw: translate(lang, key, **kw)  # noqa: E731
        result = compare_dates(request.app.state.catalog, req, date_a, date_b, tr)
        labels = {}
        for kind, items in result["diff"].items():
            for item in items:
                labels[item["id"]] = (kind, item["label"])
        ctx.update(result=result, labels=labels)
    return render(request, "app/compare.html", **ctx)


@router.get("/app/brief", response_class=HTMLResponse, include_in_schema=False)
def guest_request(request: Request):
    """Guest summary of the five conditions. It never runs matching."""
    catalog = request.app.state.catalog
    meta = catalog.meta()
    brief = parse_brief(request.query_params.multi_items(), Choices.from_meta(meta))
    edit_links = {name: f"/?{brief.query()}#brief-{name}" for name in FIELDS}
    first_open = next((item.name for item in brief.invalid + brief.missing), None)
    counts = meta["categories"]
    category = brief["category"]
    city = brief["city"]
    coverage = None
    if category.valid and city.valid:
        row = next(row for row in counts if row["name"] == category.value)
        coverage = row["by_city"].get(city.value, 0)
    return render(
        request,
        "app/request.html",
        brief=brief,
        fields=FIELDS,
        edit_links=edit_links,
        edit_all=f"/?{brief.query()}#brief",
        first_open=first_open,
        coverage=coverage,
        date_value=date_parts(get_lang(request), brief["date"].value),
        meta=meta,
        storage_key=STORAGE_KEY,
    )

