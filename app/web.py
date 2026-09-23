from __future__ import annotations

import secrets

from fastapi import Request
from fastapi.templating import Jinja2Templates

from matcher.scoring import WEIGHTS

from .config import settings
from .i18n import HTML_LANG, SUPPORTED, data_label, get_lang, translate

templates = Jinja2Templates(directory=str(settings.base_dir / "app" / "templates"))


def format_kzt(value: int) -> str:
    return f"{value:,}".replace(",", "\u00a0") + "\u00a0₸"


templates.env.filters["kzt"] = format_kzt
templates.env.globals["SCORE_WEIGHTS"] = WEIGHTS   # фаза 5: раскрывашка балла в карточке


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
