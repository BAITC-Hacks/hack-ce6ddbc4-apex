from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import date
from typing import Optional
from urllib.parse import parse_qsl, urlencode

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .brief import FIELDS
from .config import settings
from .db import get_user_by_id
from .i18n import HTML_LANG, SUPPORTED, data_label, get_lang, translate

templates = Jinja2Templates(directory=str(settings.base_dir / "app" / "templates"))
_UNSET = object()


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


def _user_stamp(user: dict) -> str:
    """Identifies the row, not just the id. Hashed: the signed cookie is readable, and email must not be in it."""
    raw = f"{user['id']}|{user['email']}|{user['created_at']}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def resolve_user(request: Request) -> dict | None:
    """Signed-in user (dict without password_hash) or None. One SELECT per request, cached in request.state.user."""
    cached = getattr(request.state, "user", _UNSET)
    if cached is not _UNSET:
        return cached
    user = None
    uid = request.session.get("uid")
    if uid is not None:
        try:
            user = get_user_by_id(int(uid))
        except (TypeError, ValueError):
            user = None
        # The cookie is bound to the row it was issued for: after the database is recreated the same id
        # may belong to someone else. Sessions without the binding (fresh sign-in) get it here.
        stamp = _user_stamp(user) if user is not None else None
        bound = request.session.get("uid_stamp")
        if stamp is not None and bound is None:
            request.session["uid_stamp"] = stamp
        elif stamp is not None and not hmac.compare_digest(str(bound), stamp):
            user = None
        if user is None:  # deleted, broken or reused id: the session is no longer valid
            request.session.pop("uid", None)
            request.session.pop("uid_stamp", None)
    request.state.user = user
    return user


def set_flash(request: Request, key: str, kind: str = "ok", **params) -> None:
    """One-time message that survives a redirect: set_flash(request, "flash.welcome", name="Aigerim").
    kind: "ok" | "error" | "info"."""
    request.session["flash"] = {"kind": kind, "key": key, "params": params}


def pop_flash(request: Request) -> dict | None:
    """Takes the flash out of the session: the next page no longer shows it."""
    data = request.session.pop("flash", None)
    if not isinstance(data, dict) or not data.get("key"):
        return None
    params, kind = data.get("params"), data.get("kind")
    return {
        "kind": kind if kind in ("ok", "error", "info") else "ok",
        "key": str(data["key"]),
        "params": params if isinstance(params, dict) else {},
    }


def render(request: Request, name: str, status_code: int = 200, **context):
    resolve_user(request)  # before get_lang(): it reads user.preferred_lang from request.state.user
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
        "flash": pop_flash(request),
    }
    base.update(context)
    response = templates.TemplateResponse(
        request=request, name=name, context=base, status_code=status_code
    )
    if request.query_params.get("lang") in SUPPORTED:
        response.set_cookie("lang", lang, max_age=365 * 24 * 3600, samesite="lax")
    return response
