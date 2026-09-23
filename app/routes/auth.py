from __future__ import annotations

import re

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from matcher.data import CITIES

from ..db import EmailTakenError, create_user, get_user_by_email
from ..i18n import SUPPORTED, get_lang
from ..security import require_csrf, rotate_csrf
from ..web import render, resolve_user, set_flash

# CSRF-protected HTML forms stay out of Swagger: they cannot be sent from there (always 403), and the API is guest-only
router = APIRouter(include_in_schema=False)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")  # master plan, section 6
NAME_MIN, NAME_MAX = 2, 60
EMAIL_MAX = 254
PASSWORD_MIN, PASSWORD_MAX = 8, 128
FIELDS = ("name", "email", "password", "password_confirm", "preferred_lang", "preferred_city")
LANG_OPTIONS = (("ru", "Русский"), ("kk", "Қазақша"), ("en", "English"))
LANG_COOKIE_MAX_AGE = 365 * 24 * 3600


def _error(key: str, **params) -> dict:
    return {"key": key, "params": params}


def _encodable(value: str) -> bool:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:  # lone surrogates: a client can smuggle them in through a multipart charset
        return False
    return True


def validate_registration(raw: dict, default_lang: str) -> tuple[dict, dict]:
    """Cleans the input and checks every field. form is what goes back to the template (never passwords),
    errors is {field: {"key": i18n key, "params": {...}}}."""
    broken = [field for field in FIELDS if not _encodable(raw.get(field, ""))]
    raw = {key: value if _encodable(value) else value.encode("utf-8", "replace").decode("utf-8")
           for key, value in raw.items()}
    name = " ".join(raw.get("name", "").split())
    email = raw.get("email", "").strip().lower()
    password = raw.get("password", "")
    confirm = raw.get("password_confirm", "")
    form = {
        "name": name,
        "email": email,
        "preferred_lang": raw.get("preferred_lang", "").strip() or default_lang,
        "preferred_city": raw.get("preferred_city", "").strip(),
    }
    errors: dict = {}
    if not name:
        errors["name"] = _error("validation.required")
    elif not NAME_MIN <= len(name) <= NAME_MAX:
        errors["name"] = _error("validation.name_length", min=NAME_MIN, max=NAME_MAX)
    elif not name.isprintable():
        errors["name"] = _error("validation.name_chars")
    if not email:
        errors["email"] = _error("validation.required")
    elif len(email) > EMAIL_MAX:
        errors["email"] = _error("validation.email_too_long", max=EMAIL_MAX)
    elif not EMAIL_RE.fullmatch(email):
        errors["email"] = _error("validation.email_invalid")
    if not password:
        errors["password"] = _error("validation.required")
    elif len(password) < PASSWORD_MIN:
        errors["password"] = _error("validation.password_short", min=PASSWORD_MIN)
    elif len(password) > PASSWORD_MAX:
        errors["password"] = _error("validation.password_long", max=PASSWORD_MAX)
    elif not (any(ch.isalpha() for ch in password) and any(ch.isdigit() for ch in password)):
        errors["password"] = _error("validation.password_weak")
    if not confirm:
        errors["password_confirm"] = _error("validation.required")
    elif confirm != password:
        errors["password_confirm"] = _error("validation.password_mismatch")
    if form["preferred_lang"] not in SUPPORTED:
        errors["preferred_lang"] = _error("validation.choice_invalid")
    if form["preferred_city"] and form["preferred_city"] not in CITIES:
        errors["preferred_city"] = _error("validation.choice_invalid")
    for field in broken:  # never hashed, stored or echoed as is
        errors[field] = _error("validation.chars_invalid")
    return form, errors


def _sign_in(request: Request, user_id: int) -> None:
    """Sign-in after registration: clean session (fixation defence), uid and a new CSRF token.
    Private name: phase 3 can import deps.start_session(request, user) here without shadowing it."""
    request.session.clear()
    request.session["uid"] = user_id
    rotate_csrf(request)


def _form_page(request: Request, form: dict, errors: dict, status_code: int = 200):
    first_error = next((f for f in FIELDS if f in errors), None)
    return render(request, "auth/register.html", status_code=status_code, form=form, errors=errors,
                  first_error=first_error, fields=FIELDS, cities=CITIES, lang_options=LANG_OPTIONS)


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    if resolve_user(request):
        set_flash(request, "flash.already_signed_in", kind="info")
        return RedirectResponse("/app", status_code=303)
    form = {"name": "", "email": "", "preferred_lang": get_lang(request), "preferred_city": ""}
    return _form_page(request, form, {})


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    password_confirm: str = Form(""),
    preferred_lang: str = Form(""),
    preferred_city: str = Form(""),
    csrf: str = Form(""),
):
    require_csrf(request, csrf)  # 403 before any work with data
    if resolve_user(request):
        return RedirectResponse("/app", status_code=303)

    raw = {"name": name, "email": email, "password": password, "password_confirm": password_confirm,
           "preferred_lang": preferred_lang, "preferred_city": preferred_city}
    form, errors = validate_registration(raw, default_lang=get_lang(request))
    if "email" not in errors and get_user_by_email(form["email"]):
        errors["email"] = _error("validation.email_taken")
    if not errors:
        try:
            user_id = create_user(form["email"], form["name"], password,
                                  preferred_lang=form["preferred_lang"],
                                  preferred_city=form["preferred_city"] or None)
        except EmailTakenError:  # race: two identical forms submitted at once
            errors["email"] = _error("validation.email_taken")
    if errors:
        return _form_page(request, form, errors, status_code=400)

    _sign_in(request, user_id)
    set_flash(request, "flash.welcome", name=form["name"])
    response = RedirectResponse("/app", status_code=303)
    response.set_cookie("lang", form["preferred_lang"], max_age=LANG_COOKIE_MAX_AGE, samesite="lax")
    return response
