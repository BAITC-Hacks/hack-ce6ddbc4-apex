from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..i18n import SUPPORTED, translate
from ..web import render

router = APIRouter()

EXAMPLE_PROFILES = (
    ("HK-42352", "landing.example.card1"),
    ("HK-35215", "landing.example.card2"),
    ("HK-77838", "landing.example.card3"),
)


def _example_cards(catalog) -> list[dict]:
    cards = []
    for profile_id, text_key in EXAMPLE_PROFILES:
        profile = catalog.by_id.get(profile_id)
        if profile is None:
            continue
        badges = [
            flag for flag in ("synthetic", "price_imputed", "city_imputed")
            if getattr(profile, flag)
        ]
        if profile.price_from_kzt == 1_000_000:
            badges.append("price_equals_budget")
        cards.append({
            "id": profile.id,
            "name": profile.name,
            "category": "Ведущий",
            "city": profile.city,
            "price": profile.price_from_kzt,
            "badges": badges,
            "text_key": text_key,
            "hours": profile.max_hours,
            "languages": profile.languages,
            "event_formats": profile.event_formats,
            "demo_date_available": "2026-10-17" not in profile.busy_dates,
        })
    return cards


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing(request: Request):
    catalog = request.app.state.catalog
    return render(
        request,
        "landing.html",
        stats=catalog.stats(),
        categories=catalog.category_rows(),
        example_cards=_example_cards(catalog),
        meta=catalog.meta(),
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


def _language_redirect_target(request: Request) -> str:
    referer = request.headers.get("referer", "")
    # Browsers normalize backslashes and controls in URLs; reject before parsing.
    decoded = unquote(referer)
    if not referer or any(ord(char) < 32 for char in decoded) or "\\" in decoded:
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
        path = target.path or "/"
        if unquote(path).startswith("//"):
            return "/"
        query = urlencode([(key, value) for key, value in parse_qsl(target.query, keep_blank_values=True) if key != "lang"])
        return urlunsplit(("", "", path, query, target.fragment))
    except ValueError:
        return "/"


@router.get("/lang/{code}", include_in_schema=False)
def switch_lang(code: str, request: Request):
    response = RedirectResponse(_language_redirect_target(request), status_code=303)
    if code in SUPPORTED:
        response.set_cookie("lang", code, max_age=365 * 24 * 3600, samesite="lax")
    return response


@router.get("/app", response_class=HTMLResponse, include_in_schema=False)
def app_placeholder(request: Request):
    return render(request, "app/placeholder.html", placeholder_kind="search", meta=request.app.state.catalog.meta())


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
def auth_placeholder(request: Request):
    return render(request, "app/placeholder.html", placeholder_kind="auth")
