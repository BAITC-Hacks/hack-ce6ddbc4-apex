from __future__ import annotations

import secrets

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .config import settings
from .db import get_user_by_id
from .i18n import HTML_LANG, SUPPORTED, data_label, get_lang, translate

templates = Jinja2Templates(directory=str(settings.base_dir / "app" / "templates"))
_UNSET = object()


def format_kzt(value: int) -> str:
    return f"{value:,}".replace(",", "\u00a0") + "\u00a0₸"


templates.env.filters["kzt"] = format_kzt


def ensure_csrf(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


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
        if user is None:  # database was recreated or uid is broken: the session is no longer valid
            request.session.pop("uid", None)
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
