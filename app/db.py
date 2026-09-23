from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import Optional

from .config import settings
from .security import hash_password

# Schema is verbatim from docs/00_MASTER_PLAN.md, section 5. All three tables are created now:
# phases 4 and 6 only write to searches/shortlist and never touch the schema.
SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  email           TEXT    NOT NULL UNIQUE,          -- stored as lower()
  name            TEXT    NOT NULL,
  password_hash   TEXT    NOT NULL,                 -- scrypt$16384$8$1$<salt_hex>$<hash_hex>
  preferred_lang  TEXT    NOT NULL DEFAULT 'ru' CHECK (preferred_lang IN ('ru','kk','en')),
  preferred_city  TEXT,
  is_demo         INTEGER NOT NULL DEFAULT 0,
  created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS searches (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  params_json  TEXT    NOT NULL,        -- canonical SearchRequest JSON (sort_keys=True)
  status       TEXT    NOT NULL,        -- found|partial|no_category_in_city|none_match|invalid_request
  result_ids   TEXT    NOT NULL,        -- "HK-42352,HK-35215,HK-77838"
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_searches_user ON searches(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS shortlist (
  user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  contractor_id  TEXT    NOT NULL,
  created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (user_id, contractor_id)
);
"""

DEMO_EMAIL = "demo@tandau.kz"
DEMO_PASSWORD = "Demo2026!"  # public by design: it is in the README and on the sign-in page
DEMO_NAME = "Демо-пользователь"
# Fixed, so every fresh database (new clone, serverless instance with its own /tmp) holds an identical demo row
# and a demo session stays valid whichever copy answers the request.
DEMO_CREATED_AT = "2026-09-23 00:00:00"


class EmailTakenError(Exception):
    """The email already exists in users (UNIQUE). Raised by create_user()."""


def connect() -> sqlite3.Connection:
    """A new connection per call. Usage: with closing(connect()) as conn, conn: ..."""
    path = settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)  # var/ does not exist on a clean clone
    conn = sqlite3.connect(path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # per-connection setting, so it lives here and not only in SCHEMA
    return conn


def init_db() -> None:
    """Creates the tables if they are missing. Idempotent: runs on every start."""
    with closing(connect()) as conn:
        conn.executescript(SCHEMA)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _as_user(row: Optional[sqlite3.Row]) -> Optional[dict]:
    if row is None:
        return None
    user = dict(row)
    user["is_demo"] = bool(user["is_demo"])
    return user


def create_user(
    email: str,
    name: str,
    password: str,
    preferred_lang: str = "ru",
    preferred_city: Optional[str] = None,
    is_demo: bool = False,
) -> int:
    """Hashes the password and inserts the user, returns the id. Duplicate email -> EmailTakenError."""
    password_hash = hash_password(password)  # the plain password goes no further than this line
    try:
        with closing(connect()) as conn, conn:
            cur = conn.execute(
                "INSERT INTO users (email, name, password_hash, preferred_lang, preferred_city, is_demo) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (normalize_email(email), name.strip(), password_hash, preferred_lang,
                 preferred_city or None, int(is_demo)),
            )
            return int(cur.lastrowid)
    except sqlite3.IntegrityError as exc:
        if "users.email" in str(exc):
            raise EmailTakenError(normalize_email(email)) from exc
        raise


def get_user_by_email(email: str) -> Optional[dict]:
    """Full row INCLUDING password_hash: only for the duplicate check and password check (sign-in, phase 3)."""
    with closing(connect()) as conn, conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (normalize_email(email),)).fetchone()
    return _as_user(row)


def get_user_by_id(user_id: int) -> Optional[dict]:
    """User WITHOUT password_hash: for the session, the header and templates."""
    with closing(connect()) as conn, conn:
        row = conn.execute(
            "SELECT id, email, name, preferred_lang, preferred_city, is_demo, created_at "
            "FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _as_user(row)


def seed_demo_user() -> int:
    """Demo account for reviewers: created when missing. Returns its id."""
    existing = get_user_by_email(DEMO_EMAIL)
    if existing:
        return existing["id"]
    try:
        user_id = create_user(DEMO_EMAIL, DEMO_NAME, DEMO_PASSWORD, preferred_lang="ru",
                              preferred_city="Алматы", is_demo=True)
    except EmailTakenError:  # two processes started at the same time
        return get_user_by_email(DEMO_EMAIL)["id"]
    with closing(connect()) as conn, conn:
        conn.execute("UPDATE users SET created_at = ? WHERE id = ?", (DEMO_CREATED_AT, user_id))
    return user_id
