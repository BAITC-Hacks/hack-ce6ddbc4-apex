from __future__ import annotations

import re
from typing import Optional

from fastapi import HTTPException, Request

from .web import resolve_user

DEFAULT_NEXT = "/app"
MAX_NEXT_LENGTH = 200
# Letters, digits and "/._~-" only: no scheme, host, query, fragment, backslash, control
# character or percent-encoding can pass, so every encoded bypass is rejected by construction.
_SAFE_PATH = re.compile(r"/[A-Za-z0-9._~/-]*")
# Returning here after sign-in would loop or sign the user straight out.
_AUTH_PATHS = ("/login", "/logout", "/register")


def safe_next(value: Optional[str], default: str = DEFAULT_NEXT) -> str:
    """Local path to return to after sign-in; anything else gives `default`.

    Only the path is kept. Query strings are dropped on purpose: free text such as event
    wishes must never travel in a return URL (docs/PHASE_1_FOUNDATION_AND_LANDING.md, 11.3).
    """
    if not value:
        return default
    path = re.split(r"[?#]", value, maxsplit=1)[0]
    if (
        len(path) > MAX_NEXT_LENGTH
        or not _SAFE_PATH.fullmatch(path)
        or "//" in path
        or any(path == auth or path.startswith(auth + "/") for auth in _AUTH_PATHS)
    ):
        return default
    return path


def current_user(request: Request) -> Optional[dict]:
    """Signed-in user without password_hash, or None for a guest."""
    return resolve_user(request)


def require_user(request: Request) -> dict:
    """Dependency for signed-in pages: a guest gets 303 to /login?next=<current path>."""
    user = resolve_user(request)
    if user is None:
        target = safe_next(request.url.path, default="")
        location = f"/login?next={target}" if target else "/login"
        raise HTTPException(status_code=303, headers={"Location": location})
    return user
