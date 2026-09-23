"""Phase 6: search history and shortlist. All account SQL lives in this file."""
from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode, urlsplit

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..db import connect
from ..profiles import badges_for
from ..security import require_csrf
from ..web import render, resolve_user, set_flash

router = APIRouter(prefix="/account", include_in_schema=False)  # HTML forms with CSRF are not for Swagger
log = logging.getLogger("tandau.account")

HISTORY_LIMIT = 50
# SearchRequest field → /app query name, in the order of the "Repeat" link. lang is not stored:
# switching the interface language does not make a different request.
QUERY_NAMES = {"city": "city", "date": "date", "event_type": "event_type", "category": "category",
               "budget_kzt": "budget", "language": "language", "duration_h": "duration", "wishes": "wishes"}
ASTANA = timezone(timedelta(hours=5))  # SQLite datetime('now') is UTC; fixed offset, no zoneinfo (no tzdata on Windows)


# ---------- history ----------

def canonical_params(req) -> str:
    """Canonical JSON: non-empty SearchRequest fields, sort_keys. Equal requests give equal strings."""
    data = {}
    for field in QUERY_NAMES:
        value = getattr(req, field, None)
        if isinstance(value, str):
            value = value.strip()
        if value not in (None, ""):
            data[field] = value
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_search(user_id: int, req, result) -> None:
    """Writes a search to history. The same request twice in a row refreshes the time instead of duplicating."""
    params, ids = canonical_params(req), ",".join(card.id for card in result.cards)
    try:
        with closing(connect()) as conn, conn:
            last = conn.execute("SELECT id, params_json FROM searches WHERE user_id = ? "
                                "ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
            if last is not None and last[1] == params:
                conn.execute("UPDATE searches SET status = ?, result_ids = ?, created_at = datetime('now') "
                             "WHERE id = ?", (result.status, ids, last[0]))
                return
            conn.execute("INSERT INTO searches (user_id, params_json, status, result_ids) VALUES (?, ?, ?, ?)",
                         (user_id, params, result.status, ids))
            conn.execute("DELETE FROM searches WHERE user_id = ? AND id NOT IN "
                         "(SELECT id FROM searches WHERE user_id = ? ORDER BY id DESC LIMIT ?)",
                         (user_id, user_id, HISTORY_LIMIT))
    except sqlite3.Error:
        log.exception("history: search not saved")  # history is a side effect; the results page must not fail


def _when(created_at: str) -> tuple[str, str]:
    """'2026-09-23 12:02:11' (UTC) → ('23.09.2026 17:02', '2026-09-23T12:02:11Z')."""
    try:
        utc = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return str(created_at), ""
    return utc.astimezone(ASTANA).strftime("%d.%m.%Y %H:%M"), utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def load_history(user_id: int, catalog) -> list[dict]:
    with closing(connect()) as conn:
        rows = conn.execute("SELECT id, params_json, status, result_ids, created_at FROM searches "
                            "WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, HISTORY_LIMIT)).fetchall()
    items = []
    for row_id, params_json, status, result_ids, created_at in rows:
        try:
            params = json.loads(params_json)
        except ValueError:
            continue
        when, when_iso = _when(created_at)
        # Wishes stay in the saved row but never travel in a URL (docs/PHASE_1_FOUNDATION_AND_LANDING.md).
        query = {QUERY_NAMES[k]: params[k] for k in QUERY_NAMES if k in params and k != "wishes"}
        items.append({
            "id": row_id, "params": params, "status": status, "when": when, "when_iso": when_iso,
            "results": [{"id": cid, "name": catalog.by_id[cid].name if cid in catalog.by_id else cid}
                        for cid in result_ids.split(",") if cid],
            "repeat_url": "/app?" + urlencode(query),
        })
    return items


# ---------- shortlist ----------

def starred_ids(user: Optional[dict]) -> set[str]:
    """Saved state for cards: guest → empty; database failure → empty (the search page matters more)."""
    if not user:
        return set()
    try:
        with closing(connect()) as conn:
            rows = conn.execute("SELECT contractor_id FROM shortlist WHERE user_id = ?", (user["id"],)).fetchall()
        return {row[0] for row in rows}
    except sqlite3.Error:
        log.exception("shortlist: ids not loaded")
        return set()


def set_shortlist(user_id: int, contractor_id: str, action: str = "") -> bool:
    """True — saved, False — removed. action "add"/"remove" is idempotent (a double submit changes nothing);
    no action toggles, as in the master-plan contract. One transaction, no IntegrityError on repeats."""
    with closing(connect()) as conn, conn:
        if action == "add":
            conn.execute("INSERT OR IGNORE INTO shortlist (user_id, contractor_id) VALUES (?, ?)",
                         (user_id, contractor_id))
            return True
        removed = conn.execute("DELETE FROM shortlist WHERE user_id = ? AND contractor_id = ?",
                               (user_id, contractor_id)).rowcount
        if removed or action == "remove":
            return False
        conn.execute("INSERT OR IGNORE INTO shortlist (user_id, contractor_id) VALUES (?, ?)",
                     (user_id, contractor_id))
        return True


# ---------- shared helpers ----------

def _no_store(response):
    response.headers["Cache-Control"] = "no-store"  # personal pages are not cached
    return response


def signed_in(request: Request, next_path: Optional[str] = None):
    """The user, or 303 to sign-in that returns to next_path (default: this page).
    POST routes pass the page with the button: returning to the POST address would give 405."""
    user = resolve_user(request)
    if user is not None:
        return user
    return RedirectResponse("/login?" + urlencode({"next": next_path or request.url.path}), status_code=303)


def safe_back(request: Request, candidates, fallback: str) -> str:
    """First relative path of THIS host among candidates (the next field, Referer), else fallback."""
    for raw in candidates:
        if not raw or any(ord(char) < 32 for char in raw) or "\\" in raw:
            continue
        try:
            parts = urlsplit(raw)
        except ValueError:
            continue
        if parts.scheme not in ("", "http", "https") or (parts.netloc and parts.netloc != request.url.netloc):
            continue  # another host → open redirect
        path = parts.path or "/"
        if not path.startswith("/") or path.startswith("//"):
            continue
        return path + (f"?{parts.query}" if parts.query else "")
    return fallback


# ---------- routes ----------

@router.get("", include_in_schema=False)
def account_home():
    return RedirectResponse("/account/history", status_code=303)


@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    user = signed_in(request)
    if isinstance(user, RedirectResponse):
        return user
    items = load_history(user["id"], request.app.state.catalog)
    return _no_store(render(request, "account/history.html", items=items, limit=HISTORY_LIMIT))


@router.post("/history/clear")
def history_clear(request: Request, csrf: str = Form("")):
    user = signed_in(request, next_path="/account/history")
    if isinstance(user, RedirectResponse):
        return user
    require_csrf(request, csrf)
    with closing(connect()) as conn, conn:
        conn.execute("DELETE FROM searches WHERE user_id = ?", (user["id"],))
    set_flash(request, "history.cleared")
    return RedirectResponse("/account/history", status_code=303)


@router.get("/shortlist", response_class=HTMLResponse)
def shortlist_page(request: Request):
    user = signed_in(request)
    if isinstance(user, RedirectResponse):
        return user
    by_id = request.app.state.catalog.by_id
    with closing(connect()) as conn:
        rows = conn.execute("SELECT contractor_id FROM shortlist WHERE user_id = ? "
                            "ORDER BY created_at DESC, rowid DESC", (user["id"],)).fetchall()
    # A profile that left the catalog keeps its row: the ID and a remove button, not a broken list.
    items = [{"id": r[0], "c": by_id.get(r[0]), "badges": badges_for(by_id[r[0]]) if r[0] in by_id else []}
             for r in rows]
    return _no_store(render(request, "account/shortlist.html", items=items))


@router.post("/shortlist/{contractor_id}")
def shortlist_toggle(contractor_id: str, request: Request, csrf: str = Form(""),
                     next_url: str = Form("", alias="next"), action: str = Form("")):
    cid = contractor_id.strip().upper()
    sources = (next_url, request.headers.get("referer"))
    user = signed_in(request, next_path=safe_back(request, sources, f"/contractors/{cid}"))
    if isinstance(user, RedirectResponse):  # guest: sign in, then back to the page with the button
        return user
    require_csrf(request, csrf)
    contractor = request.app.state.catalog.by_id.get(cid)
    if contractor is None and action != "remove":  # removing a profile that left the catalog stays possible
        raise HTTPException(status_code=404, detail="contractor not found")
    saved = set_shortlist(user["id"], cid, action if action in ("add", "remove") else "")
    set_flash(request, "shortlist.flash_added" if saved else "shortlist.flash_removed",
              name=contractor.name if contractor else cid)
    return RedirectResponse(f"{safe_back(request, sources, '/account/shortlist')}#fav-{cid}", status_code=303)
