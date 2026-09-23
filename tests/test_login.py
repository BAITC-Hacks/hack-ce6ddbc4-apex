from contextlib import closing

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app import db
from app.db import DEMO_EMAIL, DEMO_PASSWORD
from app.deps import current_user, require_user, safe_next
from app.routes import login as login_routes
from app.routes.login import LoginThrottle


def login_page(client, path="/login"):
    response = client.get(path)
    assert response.status_code == 200
    return response


def log_in(client, email=DEMO_EMAIL, password=DEMO_PASSWORD, next_path="", csrf=None):
    token = csrf if csrf is not None else login_page(client).context["csrf"]
    return client.post(
        "/login",
        data={"email": email, "password": password, "csrf": token, "next": next_path},
        follow_redirects=False,
    )


def signed_in_user(client):
    return client.get("/").context["user"]


# --- login form ---------------------------------------------------------------------------------

def test_login_page_renders_form_and_demo_button(guest):
    response = login_page(guest)
    html = response.text
    assert response.template.name == "auth/login.html"
    assert response.context["user"] is None
    assert response.context["next_path"] == "/app"
    assert 'action="/login"' in html and 'name="csrf"' in html
    assert 'autocomplete="current-password"' in html
    assert response.context["demo_available"] is True
    assert DEMO_EMAIL in html and DEMO_PASSWORD in html  # public by contract: README and sign-in page


@pytest.mark.parametrize("lang, title", [("ru", "Вход в Tandau"), ("kk", "Tandau жүйесіне кіру"), ("en", "Log in to Tandau")])
def test_login_page_in_each_language(guest, lang, title):
    html = guest.get(f"/login?lang={lang}").text
    assert f'lang="{lang}"' in html
    assert title in html
    assert "auth.login." not in html  # no untranslated keys leak into the page


def test_demo_button_hidden_without_demo_account(guest):
    with closing(db.connect()) as conn, conn:
        conn.execute("DELETE FROM users WHERE email = ?", (DEMO_EMAIL,))
    response = login_page(guest)
    assert response.context["demo_available"] is False
    assert DEMO_PASSWORD not in response.text


# --- successful sign-in -------------------------------------------------------------------------

def test_demo_login_redirects_to_app_and_starts_session(guest):
    response = log_in(guest)
    assert response.status_code == 303
    assert response.headers["location"] == "/app"
    page = guest.get("/app")
    user = page.context["user"]
    assert user["email"] == DEMO_EMAIL and user["is_demo"] is True
    assert "password_hash" not in user
    assert page.context["flash"]["key"] == "flash.signed_in"
    assert user["name"] in page.text
    assert guest.get("/app").context["flash"] is None  # flash is shown once


def test_header_switches_to_account_actions_after_login(guest):
    log_in(guest)
    header = guest.get("/").text.split("<header", 1)[1].split("</header>", 1)[0]
    assert 'action="/logout"' in header
    assert 'href="/account/history"' in header
    assert 'href="/login"' not in header


def test_email_is_matched_case_and_space_insensitively(guest):
    response = log_in(guest, email=f"  {DEMO_EMAIL.upper()} ")
    assert response.status_code == 303
    assert signed_in_user(guest)["email"] == DEMO_EMAIL


def test_registered_user_can_log_in(guest):
    db.create_user("aigerim@example.kz", "Айгерим", "Toi2026pass", preferred_lang="kk")
    response = log_in(guest, email="aigerim@example.kz", password="Toi2026pass")
    assert response.status_code == 303
    user = signed_in_user(guest)
    assert user["name"] == "Айгерим"
    assert 'lang="kk"' in guest.get("/").text  # preferred_lang applies once there is no lang cookie


def test_login_replaces_guest_session_and_rotates_csrf(guest):
    old_token = login_page(guest).context["csrf"]
    guest.get("/lang/en")  # language lives in its own cookie and must survive the session reset
    log_in(guest, csrf=old_token)
    new_token = guest.get("/").context["csrf"]
    assert new_token != old_token
    stale = guest.post("/logout", data={"csrf": old_token}, follow_redirects=False)
    assert stale.status_code == 303
    assert signed_in_user(guest) is not None  # the pre-login token cannot sign the user out
    assert guest.cookies["lang"] == "en"


def test_already_signed_in_user_skips_the_form(guest):
    log_in(guest)
    response = guest.get("/login?next=/account/shortlist", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/account/shortlist"
    assert guest.get("/login", follow_redirects=False).headers["location"] == "/app"


# --- failures -----------------------------------------------------------------------------------

def test_wrong_password_and_unknown_email_get_the_same_answer(guest):
    wrong = log_in(guest, password="Wrong2026!")
    unknown = log_in(guest, email="nobody@example.kz", password=DEMO_PASSWORD)
    for response in (wrong, unknown):
        assert response.status_code == 400
        assert response.context["error"] == "auth.login.error_invalid"
        assert "Email или пароль не совпадают." in response.text
        assert 'aria-invalid="true"' in response.text
    assert signed_in_user(guest) is None


def test_failed_login_keeps_email_but_never_echoes_password(guest):
    response = log_in(guest, email="Someone@Example.kz", password="Secret-Typo-99")
    assert 'value="someone@example.kz"' in response.text
    assert "Secret-Typo-99" not in response.text


def test_unknown_email_still_runs_password_check(guest, monkeypatch):
    calls = []
    real_verify = login_routes.verify_password
    monkeypatch.setattr(login_routes, "verify_password", lambda *args: calls.append(args) or real_verify(*args))
    log_in(guest, email="nobody@example.kz", password="Whatever2026")
    assert len(calls) == 1  # same scrypt cost as a wrong password: no timing-based enumeration


@pytest.mark.parametrize("email, password", [("", DEMO_PASSWORD), (DEMO_EMAIL, ""), ("   ", "")])
def test_missing_fields(guest, email, password):
    response = log_in(guest, email=email, password=password)
    assert response.status_code == 400
    assert response.context["error"] == "auth.login.error_missing"


def test_oversized_password_is_rejected_without_hashing(guest, monkeypatch):
    calls = []
    monkeypatch.setattr(login_routes, "verify_password", lambda *args: calls.append(args) or False)
    response = log_in(guest, password="x" * 5000)
    assert response.status_code == 400
    assert calls == []


def _crafted_multipart(fields):
    """Starlette decodes form fields with the request's charset: unicode_escape turns the
    six characters \\ud800 into a lone surrogate, which no browser can send."""
    boundary = "tandau-boundary"
    body = "".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'
        for key, value in fields.items()
    ) + f"--{boundary}--\r\n"
    return {"content": body.encode("latin-1"),
            "headers": {"content-type": f"multipart/form-data; boundary={boundary}; charset=unicode_escape"}}


@pytest.mark.parametrize("fields, status", [
    ({"email": r"\ud800", "password": "x"}, 400),
    ({"email": DEMO_EMAIL, "password": r"\ud800"}, 400),
    ({"email": r"\ud800", "password": "x", "csrf": "forged"}, 403),
    ({"email": DEMO_EMAIL, "password": DEMO_PASSWORD, "csrf": r"\ud800"}, 403),
])
def test_lone_surrogates_in_login_form_are_rejected_not_500(guest, fields, status):
    fields = {"csrf": login_page(guest).context["csrf"], **fields}
    response = guest.post("/login", follow_redirects=False, **_crafted_multipart(fields))
    assert response.status_code == status
    assert signed_in_user(guest) is None


def test_lone_surrogate_in_next_is_dropped(guest):
    fields = {"csrf": login_page(guest).context["csrf"], "email": DEMO_EMAIL, "password": DEMO_PASSWORD,
              "next": r"/app?city=\ud800&date=2026-10-17"}
    response = guest.post("/login", follow_redirects=False, **_crafted_multipart(fields))
    assert response.status_code == 303
    assert response.headers["location"] == "/app?date=2026-10-17"


def test_lone_surrogate_csrf_on_logout_keeps_session(guest):
    log_in(guest)
    response = guest.post("/logout", follow_redirects=False, **_crafted_multipart({"csrf": r"\ud800"}))
    assert response.status_code == 303
    assert signed_in_user(guest) is not None


@pytest.mark.parametrize("token", ["", "forged-token", "токен"])
def test_login_requires_csrf(guest, token):
    login_page(guest)
    response = log_in(guest, csrf=token)
    assert response.status_code == 403
    assert response.context["error"] == "auth.login.error_expired"
    assert response.context["email"] == DEMO_EMAIL
    assert signed_in_user(guest) is None


# --- next -------------------------------------------------------------------------------------

@pytest.mark.parametrize("value, expected", [
    (None, "/app"),
    ("", "/app"),
    ("/app", "/app"),
    ("/account/history", "/account/history"),
    ("/contractors/HK-42352", "/contractors/HK-42352"),
    ("/app?city=Алматы&wishes=без+конкурсов", "/app?city=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B"),
    ("/app?wishes=без+конкурсов", "/app"),
    ("/app?date=2026-10-17&city=A&city=B", "/app?city=A&date=2026-10-17"),
    ("/app?budget=" + "9" * 65, "/app"),
    ("/app?city=%0d%0aSet-Cookie:x=1", "/app"),
    ("/app?demo=s1#results", "/app?demo=s1"),
    ("/account/history?tab=all", "/account/history"),
    ("/app?" + "city=A&" * 2000, "/app"),
    ("/account/history#top", "/account/history"),
    ("https://attacker.example/", "/app"),
    ("//attacker.example/", "/app"),
    ("///attacker.example/", "/app"),
    ("/\\attacker.example", "/app"),
    ("\\\\attacker.example", "/app"),
    ("/%2f%2fattacker.example", "/app"),
    ("/%5cattacker.example", "/app"),
    ("/app/%0d%0aSet-Cookie:x=1", "/app"),
    ("/app\r\nLocation: https://attacker.example", "/app"),
    ("javascript:alert(1)", "/app"),
    ("app", "/app"),
    ("/app//x", "/app"),
    ("/login", "/app"),
    ("/login/", "/app"),
    ("/logout", "/app"),
    ("/register", "/app"),
    ("/аккаунт", "/app"),
    ("/" + "a" * 300, "/app"),
])
def test_safe_next(value, expected):
    assert safe_next(value) == expected


def test_login_returns_to_safe_next(guest):
    response = log_in(guest, next_path="/account/history")
    assert response.headers["location"] == "/account/history"


@pytest.mark.parametrize("next_path", ["https://attacker.example/", "//attacker.example", "/\\attacker.example"])
def test_login_never_redirects_off_site(guest, next_path):
    response = log_in(guest, next_path=next_path)
    assert response.status_code == 303
    assert response.headers["location"] == "/app"


S1_QUERY = ("city=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&date=2026-10-17&event_type=%D1%81%D0%B2%D0%B0%D0%B4%D1%8C%D0%B1%D0%B0"
            "&category=%D0%92%D0%B5%D0%B4%D1%83%D1%89%D0%B8%D0%B9&budget=1000000&duration=8"
            "&language=%D0%BA%D0%B0%D0%B7%D0%B0%D1%85%D1%81%D0%BA%D0%B8%D0%B9")


def test_login_returns_to_the_same_app_results(guest):
    response = log_in(guest, next_path=f"/app?{S1_QUERY}&wishes=private+text&utm=x")
    assert response.headers["location"] == f"/app?{S1_QUERY}"


def test_next_survives_a_failed_attempt(guest):
    token = login_page(guest, "/login?next=/account/shortlist").context["csrf"]
    failed = log_in(guest, password="Wrong2026!", next_path="/account/shortlist", csrf=token)
    assert failed.context["next_path"] == "/account/shortlist"
    assert 'name="next" value="/account/shortlist"' in failed.text


# --- logout -------------------------------------------------------------------------------------

def test_logout_clears_session(guest):
    log_in(guest)
    token = guest.get("/").context["csrf"]
    response = guest.post("/logout", data={"csrf": token}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    page = guest.get("/")
    assert page.context["user"] is None
    assert page.context["flash"]["key"] == "flash.signed_out"
    assert page.context["csrf"] != token


def test_logout_is_post_only(guest):
    log_in(guest)
    assert guest.get("/logout", follow_redirects=False).status_code == 405
    assert signed_in_user(guest) is not None


def test_logout_without_csrf_keeps_session_and_explains(guest):
    log_in(guest)
    response = guest.post("/logout", data={}, follow_redirects=False)
    assert response.status_code == 303
    page = guest.get("/")
    assert page.context["user"] is not None
    assert page.context["flash"] == {"kind": "error", "key": "auth.logout.error_expired", "params": {}}


def test_guest_logout_is_harmless(guest):
    response = guest.post("/logout", data={}, follow_redirects=False)
    assert response.status_code == 303
    assert guest.get("/").context["flash"] is None


# --- guarded pages ------------------------------------------------------------------------------

@pytest.fixture
def guarded(guest):
    @guest.app.get("/account/test-only")
    def private_page(user: dict = Depends(require_user)):
        return {"email": user["email"]}

    @guest.app.get("/test-only/whoami")
    def whoami(user=Depends(current_user)):
        return {"email": user["email"] if user else None}

    return guest


def test_require_user_redirects_guest_to_login_with_next(guarded):
    response = guarded.get("/account/test-only", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=/account/test-only"
    login = guarded.get(response.headers["location"])
    assert login.context["next_path"] == "/account/test-only"


def test_require_user_round_trip(guarded):
    first = guarded.get("/account/test-only", follow_redirects=False)
    token = guarded.get(first.headers["location"]).context["csrf"]
    back = log_in(guarded, next_path="/account/test-only", csrf=token)
    assert back.headers["location"] == "/account/test-only"
    assert guarded.get("/account/test-only").json() == {"email": DEMO_EMAIL}


def test_current_user_is_optional(guarded):
    assert guarded.get("/test-only/whoami").json() == {"email": None}
    log_in(guarded)
    assert guarded.get("/test-only/whoami").json() == {"email": DEMO_EMAIL}


def test_deleted_user_session_is_treated_as_guest(guarded):
    log_in(guarded)
    with closing(db.connect()) as conn, conn:
        conn.execute("DELETE FROM users WHERE email = ?", (DEMO_EMAIL,))
    response = guarded.get("/account/test-only", follow_redirects=False)
    assert response.status_code == 303
    assert guarded.get("/").context["user"] is None


@pytest.mark.parametrize("path", ["/", "/app", "/healthz", "/api/meta"])
def test_guest_pages_and_api_do_not_require_login(guest, path):
    assert guest.get(path, follow_redirects=False).status_code == 200


def test_session_cookie_flags(guest):
    response = log_in(guest)
    cookie = response.headers["set-cookie"].lower()
    assert "tandau_session=" in cookie
    assert "httponly" in cookie and "samesite=lax" in cookie
    assert f"max-age={7 * 24 * 3600}" in cookie


# --- brute-force limit --------------------------------------------------------------------------

def test_five_failures_lock_that_email_for_this_client(guest):
    for _ in range(5):
        assert log_in(guest, password="Wrong2026!").status_code == 400
    blocked = log_in(guest)  # even the right password waits now
    assert blocked.status_code == 429
    assert blocked.context["error"] == "auth.login.error_throttled"
    assert blocked.context["error_params"] == {"minutes": 5}
    assert signed_in_user(guest) is None
    db.create_user("other@example.kz", "Other", "Other2026pass")
    assert log_in(guest, email="other@example.kz", password="Other2026pass").status_code == 303


def test_lockout_does_not_block_demo_account_for_other_clients(guest):
    for _ in range(5):
        log_in(guest, password="Wrong2026!")
    with TestClient(guest.app, client=("203.0.113.7", 50000)) as reviewer:
        assert log_in(reviewer).status_code == 303


def test_success_resets_failure_count(guest):
    for _ in range(4):
        log_in(guest, password="Wrong2026!")
    assert log_in(guest).status_code == 303
    guest.post("/logout", data={"csrf": guest.get("/").context["csrf"]})
    for _ in range(4):
        log_in(guest, password="Wrong2026!")
    assert log_in(guest).status_code == 303


def test_throttle_window_expires():
    now = [1000.0]
    throttle = LoginThrottle(limit=5, window=300, clock=lambda: now[0])
    key = ("demo@tandau.kz", "127.0.0.1")
    for _ in range(5):
        throttle.fail(key)
    assert throttle.retry_after(key) == 300
    now[0] += 299.5
    assert throttle.retry_after(key) == 1
    now[0] += 1
    assert throttle.retry_after(key) == 0
    assert throttle._failures == {}


# --- guest banner (included by phase 4's app/search.html) ----------------------------------------

class _Url:
    def __init__(self, path, query=""):
        self.path, self.query = path, query


class _Request:
    def __init__(self, path, query=""):
        from starlette.datastructures import QueryParams
        self.url = _Url(path, query)
        self.query_params = QueryParams(query)


def render_banner(user, path="/app", query=""):
    from app.web import templates
    return templates.get_template("partials/guest_banner.html").render(
        user=user, request=_Request(path, query), t=lambda key, **kw: key,
    )


def test_guest_banner_links_back_to_the_same_results(guest):
    html = render_banner(None, query=S1_QUERY)
    assert "guest-banner" in html
    href = html.split('<a href="', 1)[1].split('"', 1)[0]
    assert href.startswith("/login?next=/app%3F")  # "?" and "&" encoded, so the query stays inside next
    token = login_page(guest).context["csrf"]
    from urllib.parse import parse_qs, urlsplit
    next_value = parse_qs(urlsplit(href).query)["next"][0]
    assert login_page(guest, href).context["next_path"] == f"/app?{S1_QUERY}"
    assert log_in(guest, next_path=next_value, csrf=token).headers["location"] == f"/app?{S1_QUERY}"


def test_guest_banner_hidden_for_signed_in_user():
    assert "guest-banner" not in render_banner({"id": 1, "name": "Demo"})
