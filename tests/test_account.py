"""Phase 6: history, shortlist, contractor profile and the profile API."""
import dataclasses
import json
import re
from base64 import b64encode
from contextlib import closing
from types import SimpleNamespace
from urllib.parse import unquote

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

import app.db as db
from app.config import settings
from app.main import create_app
from app.routes.account import HISTORY_LIMIT, record_search
from app.security import hash_password

TOKEN = "phase6-csrf-token"
# S2 from 01_REFERENCE.md: 17.10 → found (Эмилия, Кики, Хаул); 10.10 → partial (Хаул, Сон Гоку)
S2 = {"city": "Алматы", "date": "2026-10-17", "event_type": "свадьба", "category": "Ведущий",
      "budget": "1000000", "language": "казахский", "duration": "8"}
DAY_RE = re.compile(r'class="cal-day cal-day--(free|busy)" data-date="(\d{4}-\d{2}-\d{2})"')


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Every test gets its own SQLite file; app.db.connect() reads the patched settings."""
    monkeypatch.setattr(db, "settings", dataclasses.replace(settings, database_path=tmp_path / "tandau.db"))
    db.init_db()


def sql(query, args=()):
    with closing(db.connect()) as conn, conn:
        return [tuple(row) for row in conn.execute(query, args).fetchall()]


def history(uid):
    return sql("SELECT params_json, status, result_ids FROM searches WHERE user_id = ? ORDER BY id", (uid,))


def sign_in(client, uid):
    """Same cookie Starlette's SessionMiddleware writes after the phase 3 login: uid + csrf."""
    payload = b64encode(json.dumps({"uid": uid, "csrf": TOKEN}).encode("utf-8"))
    client.cookies.set("tandau_session", TimestampSigner(settings.secret_key).sign(payload).decode("utf-8"))


@pytest.fixture
def anon():
    with TestClient(create_app()) as c:
        yield c


@pytest.fixture
def member():
    with closing(db.connect()) as conn, conn:
        uid = conn.execute("INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
                           ("phase6@example.com", "Тест", hash_password("Phase6pass1"))).lastrowid
    with TestClient(create_app()) as c:
        sign_in(c, uid)
        yield c, uid


def req(budget, date="2026-10-10"):
    return SimpleNamespace(city="Алматы", date=date, event_type="свадьба", category="Ведущий",
                           budget_kzt=budget, duration_h=None, language=None, wishes=None, lang="ru")


# ---------- history ----------

def test_history_dedup_is_consecutive_only_and_capped(member):
    _, uid = member
    res = SimpleNamespace(status="partial", cards=[SimpleNamespace(id="HK-77838")])
    for budget in (500000, 600000, 500000):  # A, B, A: a non-consecutive repeat is a new row
        record_search(uid, req(budget), res)
    record_search(uid, req(500000), res)     # A again right away (F5): no new row
    assert len(history(uid)) == 3
    for i in range(HISTORY_LIMIT + 5):
        record_search(uid, req(700000 + i), res)
    budgets = [json.loads(p)["budget_kzt"] for p, _, _ in history(uid)]
    assert len(budgets) == HISTORY_LIMIT and budgets[-1] == 700000 + HISTORY_LIMIT + 4 and 500000 not in budgets


def test_history_page_lists_search_with_repeat_link(member):
    client, uid = member
    wishes = SimpleNamespace(**{**vars(req(1000000)), "language": "казахский", "duration_h": 8,
                                "wishes": "ведущий на двух языках"})
    record_search(uid, wishes, SimpleNamespace(status="partial",
                                               cards=[SimpleNamespace(id="HK-77838"), SimpleNamespace(id="HK-27222")]))
    params_json = history(uid)[0][0]
    assert '"lang"' not in params_json and json.loads(params_json)["budget_kzt"] == 1000000
    r = client.get("/account/history")
    assert r.status_code == 200 and r.headers["cache-control"] == "no-store"
    page = r.text
    assert 'href="/app?city=' in page and "date=2026-10-10" in page and "budget=1000000" in page
    assert "duration=8" in page and "wishes=" not in page  # wishes never travel in a URL
    assert 'href="/contractors/HK-77838"' in page and "Меньше трёх" in page


def test_history_empty_state_and_clear(member):
    client, uid = member
    assert "Запросов пока нет" in client.get("/account/history").text
    record_search(uid, req(500000), SimpleNamespace(status="none_match", cards=[]))
    assert client.post("/account/history/clear", data={"csrf": "wrong"}).status_code == 403
    r = client.post("/account/history/clear", data={"csrf": TOKEN}, follow_redirects=False)
    assert r.status_code == 303 and history(uid) == []


def test_guest_is_sent_to_login(anon):
    r = anon.get("/account/history", follow_redirects=False)
    assert r.status_code == 303 and unquote(r.headers["location"]).startswith("/login?next=/account/history")
    r = anon.get("/account/shortlist", follow_redirects=False)
    assert r.status_code == 303 and unquote(r.headers["location"]) == "/login?next=/account/shortlist"
    r = anon.post("/account/shortlist/HK-42352", data={"csrf": "x", "next": "/app?city=Алматы"},
                  follow_redirects=False)  # back to the page with the button, not the POST address
    assert r.status_code == 303 and unquote(r.headers["location"]) == "/login?next=/app?city=Алматы"
    assert sql("SELECT COUNT(*) FROM shortlist") == [(0,)]


# ---------- shortlist ----------

def test_shortlist_toggle_adds_and_removes(member):
    client, uid = member
    r = client.post("/account/shortlist/HK-42352", data={"csrf": TOKEN}, follow_redirects=False,
                    headers={"referer": "http://testserver/contractors/HK-42352"})
    assert r.status_code == 303 and r.headers["location"] == "/contractors/HK-42352#fav-HK-42352"
    assert sql("SELECT contractor_id FROM shortlist WHERE user_id = ?", (uid,)) == [("HK-42352",)]
    page = client.get("/account/shortlist").text
    assert 'href="/contractors/HK-42352"' in page and "Эмилия — в избранном" in page  # one-time flash
    assert "Эмилия — в избранном" not in client.get("/account/shortlist").text
    r = client.post("/account/shortlist/HK-42352", data={"csrf": TOKEN}, follow_redirects=False)
    assert r.headers["location"] == "/account/shortlist#fav-HK-42352"  # no Referer → the shortlist
    assert sql("SELECT COUNT(*) FROM shortlist WHERE user_id = ?", (uid,)) == [(0,)]


def test_explicit_action_survives_double_submit(member):
    client, uid = member
    for _ in range(2):
        client.post("/account/shortlist/hk-42352", data={"csrf": TOKEN, "action": "add"})
    assert sql("SELECT contractor_id FROM shortlist WHERE user_id = ?", (uid,)) == [("HK-42352",)]
    page = client.get("/contractors/HK-42352").text
    assert 'name="action" value="remove"' in page and "В избранном" in page
    for _ in range(2):
        client.post("/account/shortlist/HK-42352", data={"csrf": TOKEN, "action": "remove"})
    assert sql("SELECT COUNT(*) FROM shortlist WHERE user_id = ?", (uid,)) == [(0,)]


def test_shortlist_rejects_bad_csrf_and_unknown_id(member):
    client, uid = member
    assert client.post("/account/shortlist/HK-42352", data={"csrf": "wrong"}).status_code == 403
    assert client.post("/account/shortlist/HK-00000", data={"csrf": TOKEN}).status_code == 404
    assert sql("SELECT COUNT(*) FROM shortlist WHERE user_id = ?", (uid,)) == [(0,)]


def test_shortlist_keeps_profile_that_left_catalog(member):
    client, uid = member
    sql("INSERT INTO shortlist (user_id, contractor_id) VALUES (?, ?)", (uid, "HK-GONE1"))
    page = client.get("/account/shortlist").text
    assert "HK-GONE1" in page and "Профиль больше не доступен" in page
    client.post("/account/shortlist/HK-GONE1", data={"csrf": TOKEN, "action": "remove"})
    assert sql("SELECT COUNT(*) FROM shortlist WHERE user_id = ?", (uid,)) == [(0,)]


def test_open_redirect_is_refused(member):
    client, _ = member
    for evil in ("https://attacker.example/", "//attacker.example/x", "/\\attacker.example/"):
        r = client.post("/account/shortlist/HK-42352", data={"csrf": TOKEN, "next": evil, "action": "add"},
                        follow_redirects=False)
        assert r.headers["location"] == "/account/shortlist#fav-HK-42352"


def test_guest_profile_shows_sign_in_to_save(anon):
    page = anon.get("/contractors/HK-42352?date=2026-10-10").text
    assert 'href="/login?next=/contractors/HK-42352%3Fdate%3D2026-10-10"' in page
    assert "10 октября 2026: занято по данным каталога" in page


# ---------- profile and API ----------

def test_profile_hk42352_calendar(anon):
    r = anon.get("/contractors/HK-42352")
    assert r.status_code == 200 and "Эмилия" in r.text
    days = {d: state for state, d in DAY_RE.findall(r.text)}
    assert len(days) == 100                                   # window 23.09–31.12.2026
    assert sum(s == "busy" for s in days.values()) == 47      # 01_REFERENCE.md: "Занято 47 (22)"
    assert sum(s == "free" for d, s in days.items() if d.startswith("2026-12")) == 9  # 31 − 22
    assert days["2026-10-10"] == "busy" and days["2026-10-17"] == "free"             # S1 and S2
    assert 'aria-label="10 октября 2026, суббота: занято"' in r.text
    assert "цена проставлена при подготовке данных" in r.text and 'lang="ru"' in r.text
    assert 'href="/app?city=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&amp;category=' in r.text


@pytest.mark.parametrize(("lang", "label"), [
    ("kk", "2026 жылғы 10 қазан, сенбі: бос емес"),
    ("en", "Saturday, 10 October 2026: booked"),
])
def test_calendar_labels_are_translated(anon, lang, label):
    assert f'aria-label="{label}"' in anon.get(f"/contractors/HK-42352?lang={lang}").text


def test_profile_without_hours_and_multi_category(anon):
    synthetic = anon.get("/contractors/HK-90001").text
    assert "синтетический" in synthetic and "Не указана" in synthetic
    venue = anon.get("/contractors/hk-64395")  # lower-case id is normalised
    assert venue.status_code == 200 and "Другие категории профиля" in venue.text


def test_unknown_contractor_is_404(anon):
    r = anon.get("/contractors/HK-00000")
    assert r.status_code == 404 and "HK-00000" in r.text and "tl-header" in r.text
    assert anon.get("/api/contractors/HK-00000").json() == {"detail": "contractor not found"}


def test_api_contractor_profile(anon):
    data = anon.get("/api/contractors/HK-42352").json()
    assert (data["name"], data["city"], data["categories"]) == ("Эмилия", "Алматы", ["Ведущий"])
    assert (data["price_from_kzt"], data["max_hours"]) == (900000, 10)
    assert set(data["event_formats"]) == {"свадьба", "той"} and set(data["languages"]) == {"русский", "казахский"}
    assert (data["synthetic"], data["price_imputed"], data["city_imputed"]) == (False, True, False)
    assert len(data["busy_dates"]) == 47 and data["busy_dates"] == sorted(data["busy_dates"])
    assert data["free_days_count"] == 53 and data["free_by_month"]["2026-12"] == {"days": 31, "free": 9}
    assert data["free_next_30"]["start"] == "2026-09-23" and data["free_next_30"]["days"] == 30
    assert "/api/contractors/{contractor_id}" in anon.get("/openapi.json").json()["paths"]


# ---------- /app integration (runs once phase 4's engine and the history hook are merged) ----------

def _needs_engine():
    return pytest.importorskip("matcher.engine")


def test_guest_search_is_not_saved(anon):
    _needs_engine()
    assert anon.get("/app", params=S2).status_code == 200
    assert sql("SELECT COUNT(*) FROM searches") == [(0,)]


def test_member_search_saved_once(member):
    _needs_engine()
    client, uid = member
    for _ in range(2):  # the same request twice in a row (F5, return after saving) — one row
        assert client.get("/app", params=S2).status_code == 200
    rows = history(uid)
    assert len(rows) == 1
    params_json, status, result_ids = rows[0]
    assert status == "found" and set(result_ids.split(",")) == {"HK-42352", "HK-35215", "HK-77838"}
    client.get("/app", params={**S2, "date": "2027-01-15"})  # S7: invalid_request is not recorded
    assert len(history(uid)) == 1


def test_cards_link_to_profile_and_guest_sees_sign_in_to_save(anon):
    _needs_engine()
    page = anon.get("/app", params=S2).text
    assert 'href="/contractors/HK-42352"' in page and 'href="/login?next=/app%3F' in page
