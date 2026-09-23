"""Sign-in, sign-out and the demo account button (phase 3)."""
from __future__ import annotations

import math
import secrets
import time
from collections import deque
from functools import lru_cache
from typing import Callable

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..db import DEMO_EMAIL, DEMO_PASSWORD, get_user_by_email, normalize_email
from ..deps import safe_next
from ..security import hash_password, require_csrf, rotate_csrf, verify_password
from ..web import render, resolve_user, set_flash

router = APIRouter()

MAX_EMAIL_LENGTH = 254
MAX_PASSWORD_LENGTH = 1024


class LoginThrottle:
    """At most `limit` failed sign-ins per (email, client address) within `window` seconds.

    Keyed by email AND client so that nobody can lock the public demo account for
    reviewers by typing a wrong password five times. In memory: a restart clears it.
    """

    def __init__(self, limit: int = 5, window: float = 300.0, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window = window
        self.clock = clock
        self._failures: dict[tuple[str, str], deque[float]] = {}

    def _recent(self, key: tuple[str, str]) -> deque[float]:
        attempts = self._failures.get(key, deque())
        cutoff = self.clock() - self.window
        while attempts and attempts[0] <= cutoff:
            attempts.popleft()
        if not attempts:
            self._failures.pop(key, None)
        return attempts

    def retry_after(self, key: tuple[str, str]) -> int:
        """Seconds until the next attempt is allowed; 0 when allowed now."""
        attempts = self._recent(key)
        if len(attempts) < self.limit:
            return 0
        return max(1, math.ceil(attempts[0] + self.window - self.clock()))

    def fail(self, key: tuple[str, str]) -> None:
        if len(self._failures) > 10_000:  # bound memory under a spray of random emails
            for stale in [k for k, v in self._failures.items() if v and v[-1] <= self.clock() - self.window]:
                del self._failures[stale]
        self._recent(key)
        self._failures.setdefault(key, deque()).append(self.clock())

    def reset(self, key: tuple[str, str]) -> None:
        self._failures.pop(key, None)


def _throttle(request: Request) -> LoginThrottle:
    state = request.app.state
    if not hasattr(state, "login_throttle"):
        state.login_throttle = LoginThrottle()
    return state.login_throttle


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    """Verified against when the email is unknown, so both failures cost one scrypt."""
    return hash_password(secrets.token_urlsafe(16))


def _encodable(value: str) -> bool:
    """False for a lone surrogate, which only a crafted request can carry (for example multipart
    with charset=unicode_escape). sqlite, scrypt and the response encoder would all raise on it."""
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _render_login(request: Request, *, next_path: str, email: str = "", error: str | None = None,
                  error_params: dict | None = None, status_code: int = 200):
    return render(
        request,
        "auth/login.html",
        status_code=status_code,
        email=email,
        error=error,
        error_params=error_params or {},
        next_path=next_path,
        demo_available=get_user_by_email(DEMO_EMAIL) is not None,
        demo_email=DEMO_EMAIL,
        demo_password=DEMO_PASSWORD,
    )


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_form(request: Request, next: str | None = None):
    target = safe_next(next)
    if resolve_user(request):
        return RedirectResponse(target, status_code=303)
    return _render_login(request, next_path=target)


@router.post("/login", response_class=HTMLResponse, include_in_schema=False)
def login(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    csrf: str = Form(""),
    next: str = Form(""),
):
    target = safe_next(next)
    malformed = not (_encodable(email) and _encodable(password))
    email = "" if malformed else normalize_email(email)[:MAX_EMAIL_LENGTH]
    try:
        require_csrf(request, csrf if _encodable(csrf) else "")
    except HTTPException:
        # A tab opened before another sign-in holds an old token: ask to resend, don't 403 as JSON.
        return _render_login(request, next_path=target, email=email,
                             error="auth.login.error_expired", status_code=403)
    if malformed:
        return _render_login(request, next_path=target, error="auth.login.error_invalid", status_code=400)
    if not email or not password:
        return _render_login(request, next_path=target, email=email,
                             error="auth.login.error_missing", status_code=400)

    throttle = _throttle(request)
    key = (email, request.client.host if request.client else "")
    wait = throttle.retry_after(key)
    if wait:
        return _render_login(request, next_path=target, email=email, error="auth.login.error_throttled",
                             error_params={"minutes": math.ceil(wait / 60)}, status_code=429)

    user = get_user_by_email(email)
    valid = len(password) <= MAX_PASSWORD_LENGTH and verify_password(
        password, user["password_hash"] if user else _dummy_hash()
    )
    if not (user and valid):
        throttle.fail(key)
        # One message for an unknown email and a wrong password: no account enumeration.
        return _render_login(request, next_path=target, email=email,
                             error="auth.login.error_invalid", status_code=400)

    throttle.reset(key)
    request.session.clear()  # nothing from the guest session survives into the signed-in one
    request.session["uid"] = user["id"]
    rotate_csrf(request)
    set_flash(request, "flash.signed_in", name=user["name"])
    return RedirectResponse(target, status_code=303)


@router.post("/logout", include_in_schema=False)
def logout(request: Request, csrf: str = Form("")):
    try:
        require_csrf(request, csrf if _encodable(csrf) else "")
    except HTTPException:
        if resolve_user(request):
            # Stale form: stay signed in and say so rather than pretend the sign-out worked.
            set_flash(request, "auth.logout.error_expired", kind="error")
        return RedirectResponse("/", status_code=303)
    request.session.clear()
    set_flash(request, "flash.signed_out", kind="info")
    return RedirectResponse("/", status_code=303)
