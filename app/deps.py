from __future__ import annotations

import re
from typing import Optional
from urllib.parse import parse_qsl, quote, urlencode

from fastapi import HTTPException, Request

from .web import resolve_user

DEFAULT_NEXT = "/app"
MAX_NEXT_LENGTH = 200
MAX_RAW_NEXT = 2048
MAX_QUERY_VALUE = 64
# Letters, digits and "/._~-" only: no scheme, host, backslash, control character or
# percent-encoding can pass in the path, so every encoded bypass is rejected by construction.
_SAFE_PATH = re.compile(r"/[A-Za-z0-9._~/-]*")
# Returning here after sign-in would loop or sign the user straight out.
_AUTH_PATHS = ("/login", "/logout", "/register")
# Query keys that survive the round trip, per path: only the structured /app search fields
# (phase 4 query names), so a guest returns to the same results. Free text such as wishes
# is never on this list (docs/PHASE_1_FOUNDATION_AND_LANDING.md, 11.3).
_KEEP_QUERY = {
    "/app": ("city", "date", "event_type", "category", "budget", "duration", "language", "demo"),
}


def _kept_query(path: str, query: str) -> str:
    allowed = _KEEP_QUERY.get(path)
    if not allowed or not query:
        return ""
    first: dict[str, str] = {}
    for key, value in parse_qsl(query, max_num_fields=50):
        if key in allowed and key not in first:
            first[key] = value
    pairs = [
        (key, first[key]) for key in allowed
        if key in first and len(first[key]) <= MAX_QUERY_VALUE
        and not any(ord(char) < 32 or ord(char) == 127 for char in first[key])
    ]
    return urlencode(pairs, quote_via=quote)


def safe_next(value: Optional[str], default: str = DEFAULT_NEXT) -> str:
    """Local address to return to after sign-in; anything else gives `default`.

    The path must be plain ASCII on this site. The query is rebuilt from the allow-list
    above and dropped everywhere else; the fragment is always dropped.
    """
    if not value or len(value) > MAX_RAW_NEXT:
        return default
    path = re.split(r"[?#]", value, maxsplit=1)[0]
    if (
        len(path) > MAX_NEXT_LENGTH
        or not _SAFE_PATH.fullmatch(path)
        or "//" in path
        or any(path == auth or path.startswith(auth + "/") for auth in _AUTH_PATHS)
    ):
        return default
    rest = value[len(path):]
    query = rest[1:].split("#", 1)[0] if rest.startswith("?") else ""
    kept = _kept_query(path, query)
    return f"{path}?{kept}" if kept else path


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
