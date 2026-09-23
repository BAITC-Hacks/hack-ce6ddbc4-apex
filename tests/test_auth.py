"""Phase 2: registration. Phase 3 adds login, logout and protected routes in its own test file."""
import json
import re
from contextlib import closing

import pytest
from fastapi import HTTPException, Request

from app import db
from app.config import settings
from app.i18n import get_lang, translate
from app.routes.auth import validate_registration
from app.security import hash_password, require_csrf, verify_password

CSRF_RE = re.compile(r'name="csrf" value="([^"]+)"')
PASSWORD = "Toi2026pass"
GOOD = {"name": "Айгерим", "email": "Aigerim@Example.KZ", "password": PASSWORD,
        "password_confirm": PASSWORD, "preferred_lang": "kk", "preferred_city": "Алматы"}
REGISTRATION_SOURCES = ("app/routes/auth.py", "app/templates/auth/register.html", "app/templates/partials/auth_nav.html")
KEY_RE = re.compile(r"(?:auth\.register|auth\.nav|validation|flash)\.[a-z_]+")


def get_csrf(client) -> str:
    r = client.get("/register")
    match = CSRF_RE.search(r.text)
    assert r.status_code == 200 and match, "no form or hidden csrf field"
    return match.group(1)


def post_register(client, **overrides):
    data = {**GOOD, "csrf": get_csrf(client), **overrides}
    return client.post("/register", data=data, follow_redirects=False)


def post_multipart(client, fields: dict, charset: str):
    """Multipart body with a client-chosen charset: Starlette decodes parts with it, which is how
    lone surrogates reach the handler."""
    boundary = "tandau-boundary"
    body = b"".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'.encode() + value + b"\r\n"
        for name, value in fields.items()
    ) + f"--{boundary}--\r\n".encode()
    return client.post("/register", content=body, follow_redirects=False,
                       headers={"content-type": f"multipart/form-data; boundary={boundary}; charset={charset}"})


def count_users() -> int:
    with closing(db.connect()) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def assert_field_error(html: str, field: str, key: str, **params) -> None:
    assert f'id="{field}-error"' in html
    assert re.search(rf'id="{field}"[^>]*aria-invalid="true"', html), f"{field}: no aria-invalid"
    assert re.search(rf'id="{field}"[^>]*aria-describedby="[^"]*{field}-error', html), f"{field}: error not described"
    assert translate("ru", key, **params) in html


def test_register_success_logs_in_and_hashes_password(guest):
    r = post_register(guest)
    assert r.status_code == 303 and r.headers["location"] == "/app"
    assert "lang=kk" in r.headers.get("set-cookie", "")

    user = db.get_user_by_email("aigerim@example.kz")  # email stored in lower()
    assert (user["name"], user["preferred_lang"], user["preferred_city"], user["is_demo"]) == (
        "Айгерим", "kk", "Алматы", False)
    assert user["password_hash"].startswith("scrypt$16384$8$1$") and PASSWORD not in user["password_hash"]
    assert verify_password(PASSWORD, user["password_hash"])
    assert PASSWORD.encode() not in settings.database_path.read_bytes()  # not even in the raw file bytes
    assert "password_hash" not in db.get_user_by_id(user["id"])  # the hash never reaches templates

    page = guest.get("/app")  # auto sign-in: signed-in header and the flash exactly once
    welcome = translate("kk", "flash.welcome", name="Айгерим")
    assert page.status_code == 200 and 'action="/logout"' in page.text and welcome in page.text
    assert 'lang="kk"' in page.text
    assert welcome not in guest.get("/app").text


def test_register_rotates_session_and_csrf(guest):
    before = get_csrf(guest)
    r = guest.post("/register", data={**GOOD, "csrf": before}, follow_redirects=False)
    assert r.status_code == 303
    after = CSRF_RE.search(guest.get("/app").text).group(1)
    assert after != before  # a token from another tab no longer works
    assert PASSWORD not in r.headers.get("set-cookie", "")


def test_duplicate_email_case_insensitive(guest):
    r = post_register(guest, email="DEMO@Tandau.kz")
    assert r.status_code == 400
    assert_field_error(r.text, "email", "validation.email_taken")
    assert count_users() == 1  # only the demo account
    assert 'value="Айгерим"' in r.text and PASSWORD not in r.text  # name returned, password never
    assert re.search(r'id="email"[^>]*autofocus', r.text)  # focus on the first invalid field
    assert 'role="alert"' in r.text and 'href="#email"' in r.text  # summary links to the field


def test_empty_form_reports_every_required_field(guest):
    r = guest.post("/register", data={"csrf": get_csrf(guest)}, follow_redirects=False)
    assert r.status_code == 400
    for field in ("name", "email", "password", "password_confirm"):
        assert_field_error(r.text, field, "validation.required")
    assert re.search(r'id="name"[^>]*autofocus', r.text)
    assert count_users() == 1


@pytest.mark.parametrize("overrides, field, key, params", [
    ({"password": "Ab1cd", "password_confirm": "Ab1cd"}, "password", "validation.password_short", {"min": 8}),
    ({"password": "onlyletters", "password_confirm": "onlyletters"}, "password", "validation.password_weak", {}),
    ({"password": "1234567890", "password_confirm": "1234567890"}, "password", "validation.password_weak", {}),
    ({"password": "a1" * 65, "password_confirm": "a1" * 65}, "password", "validation.password_long", {"max": 128}),
    ({"password_confirm": PASSWORD + "x"}, "password_confirm", "validation.password_mismatch", {}),
    ({"email": "aigerim@example"}, "email", "validation.email_invalid", {}),
    ({"email": "ai gerim@example.kz"}, "email", "validation.email_invalid", {}),
    ({"email": "a@b@c.kz"}, "email", "validation.email_invalid", {}),
    ({"email": "a" * 250 + "@x.kz"}, "email", "validation.email_too_long", {"max": 254}),
    ({"email": ""}, "email", "validation.required", {}),
    ({"name": "А"}, "name", "validation.name_length", {"min": 2, "max": 60}),
    ({"name": "Я" * 61}, "name", "validation.name_length", {"min": 2, "max": 60}),
    ({"name": "Ай‮герим"}, "name", "validation.name_chars", {}),
    ({"preferred_lang": "de"}, "preferred_lang", "validation.choice_invalid", {}),
    ({"preferred_city": "Париж"}, "preferred_city", "validation.choice_invalid", {}),
])
def test_invalid_input_returns_form_with_field_error(guest, overrides, field, key, params):
    r = post_register(guest, **overrides)
    assert r.status_code == 400
    assert_field_error(r.text, field, key, **params)
    assert count_users() == 1  # nothing created


def test_name_whitespace_is_collapsed(guest):
    assert post_register(guest, name="  Айгерим \t  Сейткали ").status_code == 303
    assert db.get_user_by_email("aigerim@example.kz")["name"] == "Айгерим Сейткали"


def test_empty_city_is_stored_as_null(guest):
    assert post_register(guest, preferred_city="").status_code == 303
    assert db.get_user_by_email("aigerim@example.kz")["preferred_city"] is None


def test_missing_language_defaults_to_interface_language(guest):
    guest.get("/?lang=en")
    assert post_register(guest, preferred_lang="").status_code == 303
    assert db.get_user_by_email("aigerim@example.kz")["preferred_lang"] == "en"


def test_register_without_csrf_is_forbidden(guest):
    guest.get("/register")  # the session has a token, but the form does not send it or sends a foreign one
    assert guest.post("/register", data=GOOD, follow_redirects=False).status_code == 403
    assert guest.post("/register", data={**GOOD, "csrf": "forged"}, follow_redirects=False).status_code == 403
    assert guest.post("/register", data={**GOOD, "csrf": "абв"}, follow_redirects=False).status_code == 403
    assert count_users() == 1


def test_register_without_session_is_forbidden(guest):
    r = guest.post("/register", data={**GOOD, "csrf": "anything"}, follow_redirects=False)
    assert r.status_code == 403 and r.json() == {"detail": "CSRF token missing or invalid"}
    assert count_users() == 1


def test_logged_in_user_is_redirected_from_register(guest):
    post_register(guest)
    r = guest.get("/register", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/app"
    assert translate("kk", "flash.already_signed_in") in guest.get("/app").text


def test_logged_in_user_post_creates_nothing(guest):
    post_register(guest)
    csrf = CSRF_RE.search(guest.get("/app").text).group(1)
    r = guest.post("/register", data={**GOOD, "email": "second@example.kz", "csrf": csrf}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/app"
    assert count_users() == 2  # demo + the first registration only


def test_stale_session_uid_is_treated_as_guest(guest):
    post_register(guest)
    with closing(db.connect()) as conn, conn:
        conn.execute("DELETE FROM users WHERE email = ?", ("aigerim@example.kz",))
    page = guest.get("/register")  # the uid points to a deleted user: show the form, not a redirect
    assert page.status_code == 200 and 'action="/logout"' not in page.text


def test_session_is_bound_to_the_user_row(guest):
    post_register(guest)
    guest.get("/app")  # the first signed-in request binds the cookie to the row
    with closing(db.connect()) as conn:  # database recreated (e.g. var/tandau.db deleted), SECRET_KEY unchanged
        conn.executescript("DROP TABLE shortlist; DROP TABLE searches; DROP TABLE users;")
    db.init_db()
    db.seed_demo_user()
    other_id = db.create_user("bob@example.kz", "Бекзат", "Another2026")
    assert other_id == 2  # same id as the old session
    page = guest.get("/register")  # the old cookie must not open the new account
    assert page.status_code == 200 and 'action="/logout"' not in page.text


def test_user_is_resolved_before_handlers(guest):
    """Handlers that call get_lang() before render() must see the signed-in user's language."""
    @guest.app.get("/_probe_lang")
    def probe(request: Request):
        return {"lang": get_lang(request)}

    post_register(guest)  # preferred_lang=kk
    guest.cookies.delete("lang")  # e.g. a new browser: only the session cookie identifies the user
    assert guest.get("/_probe_lang").json() == {"lang": "kk"}


def test_header_shows_account_actions(guest):
    page = guest.get("/app")
    assert 'href="/login"' in page.text and 'href="/register"' in page.text and 'action="/logout"' not in page.text
    post_register(guest)
    page = guest.get("/app")
    assert 'action="/logout"' in page.text and 'href="/account/history"' in page.text
    assert 'href="/register"' not in page.text


def test_non_ascii_csrf_token_is_forbidden_not_500():
    request = Request({"type": "http", "headers": [], "session": {"csrf": "token"}})
    for token in ("\ud800", "абв", "token\u0301"):
        with pytest.raises(HTTPException) as exc:
            require_csrf(request, token)
        assert exc.value.status_code == 403


def test_surrogate_csrf_over_http_is_forbidden(guest):
    get_csrf(guest)
    r = post_multipart(guest, {"csrf": b"\\ud800", "name": b"x"}, charset="unicode_escape")
    assert r.status_code == 403
    assert count_users() == 1


@pytest.mark.parametrize("field, value", [
    ("email", b"a\\ud800@b.kz"),
    ("email", b"\\ud800"),
    ("password", b"Passw0rd1\\ud800"),
    ("name", b"\\ud800\\ud800"),
])
def test_surrogates_in_fields_give_a_field_error_not_500(guest, field, value):
    csrf = get_csrf(guest).encode()
    fields = {"csrf": csrf, "name": b"Aigerim", "email": b"aigerim@example.kz",
              "password": b"Toi2026pass", "password_confirm": b"Toi2026pass", field: value}
    if field == "password":
        fields["password_confirm"] = value
    r = post_multipart(guest, fields, charset="unicode_escape")
    assert r.status_code == 400
    assert f'id="{field}-error"' in r.text
    assert count_users() == 1


def test_validate_registration_rejects_surrogates():
    raw = {**GOOD, "email": "a\ud800@b.kz", "password": "Passw0rd1\ud800", "password_confirm": "Passw0rd1\ud800"}
    form, errors = validate_registration(raw, default_lang="ru")
    assert errors["email"]["key"] == errors["password"]["key"] == "validation.chars_invalid"
    form["email"].encode("utf-8")  # safe to echo back


def test_guest_mode_is_not_broken(guest):
    page = guest.get("/register")
    assert 'href="/app"' in page.text  # "continue without an account" on the form
    assert 'href="/login"' in page.text
    assert guest.get("/app").status_code == 200  # matching works without an account


@pytest.mark.parametrize("lang", ["ru", "kk", "en"])
def test_register_form_in_each_language(guest, lang):
    page = guest.get(f"/register?lang={lang}")
    assert page.status_code == 200 and f'lang="{lang}"' in page.text
    assert translate(lang, "auth.register.title") in page.text
    assert re.search(rf'<option value="{lang}" lang="{lang}" selected>', page.text)  # interface language preselected
    assert 'novalidate' in page.text and 'autocomplete="new-password"' in page.text


def test_register_is_hidden_from_openapi(client):
    assert "/register" not in client.get("/openapi.json").json()["paths"]


def test_demo_user_seeded_on_startup(fresh_db):
    from app.main import create_app

    with closing(db.connect()) as conn:
        conn.executescript("DROP TABLE shortlist; DROP TABLE searches; DROP TABLE users;")
    create_app()  # like `python run.py` on an empty database
    create_app()  # a second start does not create a duplicate
    demo = db.get_user_by_email(db.DEMO_EMAIL)
    assert (demo["name"], demo["preferred_lang"], demo["preferred_city"], demo["is_demo"]) == (
        "Демо-пользователь", "ru", "Алматы", True)
    assert verify_password("Demo2026!", demo["password_hash"]) and count_users() == 1
    with closing(db.connect()) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"users", "searches", "shortlist"} <= tables


def test_demo_row_is_identical_in_every_fresh_database(fresh_db):
    """Serverless instances each seed their own database: a demo session must stay valid on all of them."""
    demo = db.get_user_by_email(db.DEMO_EMAIL)
    assert (demo["id"], demo["created_at"]) == (1, db.DEMO_CREATED_AT)


def test_demo_stamp_survives_a_recreated_database(fresh_db):
    from app.web import _user_stamp

    stamp = _user_stamp(db.get_user_by_id(1))
    with closing(db.connect()) as conn:
        conn.executescript("DROP TABLE shortlist; DROP TABLE searches; DROP TABLE users;")
    db.init_db()
    db.seed_demo_user()  # another instance or a fresh clone: same demo row, same session stamp
    assert _user_stamp(db.get_user_by_id(1)) == stamp


def test_foreign_keys_cascade(fresh_db):
    user_id = db.create_user("cascade@example.kz", "Каскад", "Cascade2026")
    with closing(db.connect()) as conn, conn:
        conn.execute("INSERT INTO shortlist (user_id, contractor_id) VALUES (?, ?)", (user_id, "HK-42352"))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        assert conn.execute("SELECT COUNT(*) FROM shortlist").fetchone()[0] == 0


def test_create_user_rejects_duplicate(fresh_db):
    with pytest.raises(db.EmailTakenError):
        db.create_user("  Demo@Tandau.KZ ", "Второй", "Another2026")


def test_hash_verify_roundtrip():
    h1, h2 = hash_password("Demo2026!"), hash_password("Demo2026!")
    assert h1 != h2  # every hash has its own salt
    algo, n, r, p, salt_hex, hash_hex = h1.split("$")
    assert (algo, n, r, p) == ("scrypt", "16384", "8", "1")
    assert len(bytes.fromhex(salt_hex)) == 16 and len(bytes.fromhex(hash_hex)) == 64
    assert verify_password("Demo2026!", h1) and verify_password("Demo2026!", h2)
    assert not verify_password("demo2026!", h1)
    assert not verify_password("Demo2026!", "plain-text") and not verify_password("Demo2026!", "")
    assert not verify_password("Demo2026!", "bcrypt$16384$8$1$00$00")
    assert not verify_password("Demo2026!", "scrypt$abc$8$1$00$00")


def test_all_locales_have_registration_keys():
    sources = "".join((settings.base_dir / p).read_text(encoding="utf-8") for p in REGISTRATION_SOURCES)
    used = set(KEY_RE.findall(sources))
    assert used
    for lang in ("ru", "kk", "en"):
        values = json.loads((settings.base_dir / f"app/i18n/{lang}.json").read_text(encoding="utf-8"))
        assert not sorted(used - values.keys()), lang
