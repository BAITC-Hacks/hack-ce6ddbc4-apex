from __future__ import annotations

import hashlib
import secrets
from datetime import date
from typing import Optional
from urllib.parse import parse_qsl, urlencode

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .brief import FIELDS
from .config import settings
from .i18n import HTML_LANG, SUPPORTED, data_label, get_lang, translate

templates = Jinja2Templates(directory=str(settings.base_dir / "app" / "templates"))


def format_kzt(value: int) -> str:
    return f"{value:,}".replace(",", "\u00a0") + "\u00a0₸"


def format_digits(value: int) -> str:
    """Group digits with plain spaces for editable inputs."""
    return f"{value:,}".replace(",", " ")


templates.env.filters["kzt"] = format_kzt
templates.env.filters["digits"] = format_digits

STATIC_DIR = settings.base_dir / "app" / "static"


def static_url(path: str) -> str:
    """Static path with a content hash, so browsers never run a stale script or style."""
    try:
        digest = hashlib.sha256((STATIC_DIR / path).read_bytes()).hexdigest()[:10]
    except OSError:
        return f"/static/{path}"
    return f"/static/{path}?v={digest}"


templates.env.globals["static_url"] = static_url


def date_parts(lang: str, iso: Optional[str]) -> Optional[dict]:
    """Localised pieces of an ISO date without any timezone conversion."""
    if not iso:
        return None
    day = date.fromisoformat(iso)
    month = translate(lang, f"date.month.{day.month}")
    genitive = translate(lang, f"date.month_genitive.{day.month}")
    return {
        "day": day.day,
        "month": month,
        "month_short": translate(lang, f"date.month_short.{day.month}"),
        "year": day.year,
        "weekday": translate(lang, f"date.weekday.{day.weekday()}"),
        "day_month": translate(lang, "date.day_month", day=day.day, month=genitive),
        "full": translate(lang, "date.full", day=day.day, month=genitive, year=day.year),
    }


def language_url(request: Request, code: str) -> str:
    """Language switch that carries the current page and only the five brief conditions."""
    query = urlencode([
        (key, value) for key, value in parse_qsl(request.url.query, keep_blank_values=True)
        if key in FIELDS
    ])
    target = request.url.path + (f"?{query}" if query else "")
    return f"/lang/{code}?" + urlencode({"next": target})


def ensure_csrf(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def render(request: Request, name: str, status_code: int = 200, **context):
    lang = get_lang(request)
    base = {
        "lang": lang,
        "html_lang": HTML_LANG[lang],
        "t": lambda key, **kw: translate(lang, key, **kw),
        "label": lambda kind, value: data_label(lang, kind, value),
        "date_parts": lambda iso: date_parts(lang, iso),
        "lang_url": lambda code: language_url(request, code),
        "user": getattr(request.state, "user", None),
        "csrf": ensure_csrf(request),
        "path": request.url.path,
    }
    base.update(context)
    response = templates.TemplateResponse(
        request=request, name=name, context=base, status_code=status_code
    )
    if request.query_params.get("lang") in SUPPORTED:
        response.set_cookie("lang", lang, max_age=365 * 24 * 3600, samesite="lax")
    return response
