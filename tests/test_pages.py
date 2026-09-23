import csv

import pytest

from app.config import settings
from matcher.data import load_catalog


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "profiles": 66}


def test_meta(client):
    response = client.get("/api/meta")
    assert response.status_code == 200
    data = response.json()
    assert data["cities"] == ["Алматы", "Астана", "Зарубежье"]
    assert len(data["categories"]) == 17
    assert len(data["event_formats"]) == 6
    assert len(data["languages"]) == 3
    assert data["window"] == {"start": "2026-09-23", "end": "2026-12-31", "days": 100}
    assert data["stats"]["synthetic"] == 13
    assert data["stats"]["price_imputed"] == 18
    assert data["stats"]["city_imputed"] == 8
    categories = data["categories"]
    assert categories == sorted(categories, key=lambda item: (-item["total"], item["name"]))
    hosts = next(item for item in categories if item["name"] == "Ведущий")
    assert hosts == {"name": "Ведущий", "total": 15, "by_city": {"Алматы": 10, "Астана": 5}}


@pytest.mark.parametrize("language", ["ru", "kk", "en"])
def test_landing_in_each_language(client, language):
    response = client.get(f"/?lang={language}")
    assert response.status_code == 200
    assert "Tandau" in response.text
    assert f'lang="{language}"' in response.text
    assert response.cookies["lang"] == language
    assert response.context["stats"]["profiles"] == 66
    assert response.context["stats"]["days"] == 100


def test_example_cards_use_catalog_records(client):
    response = client.get("/")
    cards = response.context["example_cards"]
    assert [card["id"] for card in cards] == ["HK-42352", "HK-35215", "HK-77838"]
    for card in cards:
        profile = client.app.state.catalog.by_id[card["id"]]
        assert (card["name"], card["city"], card["price"]) == (
            profile.name, profile.city, profile.price_from_kzt
        )
        for flag in ("synthetic", "city_imputed", "price_imputed"):
            assert (flag in card["badges"]) == getattr(profile, flag)


def test_landing_and_api_update_when_catalog_changes(client, tmp_path):
    with settings.data_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)[:5]
    reduced_path = tmp_path / "catalog.csv"
    with reduced_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    client.app.state.catalog = load_catalog(reduced_path)
    assert client.get("/healthz").json()["profiles"] == 5
    assert client.get("/api/meta").json()["stats"]["profiles"] == 5
    assert client.get("/").context["stats"]["profiles"] == 5


@pytest.mark.parametrize("path", ["/app", "/login", "/register"])
def test_guest_pages_keep_language(client, path):
    client.get("/?lang=kk")
    response = client.get(path)
    assert response.status_code == 200
    assert 'lang="kk"' in response.text
    assert response.context["user"] is None
    if path == "/app":
        assert response.context["brief"].state == "empty"
    else:
        assert response.context["placeholder_kind"] == "auth"


def test_query_language_overrides_and_updates_cookie(client):
    client.get("/?lang=kk")
    response = client.get("/?lang=en")
    assert 'lang="en"' in response.text
    assert client.cookies["lang"] == "en"
    assert 'lang="en"' in client.get("/app").text


def test_invalid_language_uses_cookie_then_default(client):
    assert 'lang="ru"' in client.get("/?lang=invalid").text
    client.get("/?lang=kk")
    assert 'lang="kk"' in client.get("/?lang=invalid").text
    assert client.cookies["lang"] == "kk"


def test_language_switch_removes_old_query_language(client):
    client.get("/?lang=ru")
    response = client.get(
        "/lang/en", headers={"referer": "http://testserver/?lang=ru&from=demo#how"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/?from=demo#how"
    assert response.cookies["lang"] == "en"
    assert "Max-Age=31536000" in response.headers["set-cookie"]
    assert 'lang="en"' in client.get(response.headers["location"]).text


@pytest.mark.parametrize("referer", [
    "https://attacker.example/",
    "http://testserver.attacker.example/",
    "http://testserver@attacker.example/",
    "http://testserver:81/",
    "https://testserver/",
    "//attacker.example/",
    "///attacker.example/",
    "/\\attacker.example/",
    "http://testserver/\\attacker.example/",
    "http://testserver//attacker.example/",
    "http://testserver/%2f%2fattacker.example/",
    "/%5cattacker.example/",
    "/%0d%0aLocation:%20https://attacker.example/",
    "javascript:alert(1)",
    "http://[malformed/",
])
def test_language_redirect_rejects_unsafe_referers(client, referer):
    response = client.get("/lang/en", headers={"referer": referer}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


@pytest.mark.parametrize("referer", ["/app?city=Almaty", "http://testserver/app?city=Almaty"])
def test_language_redirect_accepts_same_origin(client, referer):
    response = client.get("/lang/kk", headers={"referer": referer}, follow_redirects=False)
    assert response.headers["location"] == "/app?city=Almaty"


def test_language_next_keeps_the_brief_and_fragment(client):
    target = "/app?city=Алматы&budget=1000000&lang=ru#brief"
    response = client.get("/lang/en", params={"next": target}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == (
        "/app?city=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&budget=1000000#brief"
    )
    assert response.cookies["lang"] == "en"


def test_language_next_wins_over_referer(client):
    response = client.get(
        "/lang/kk", params={"next": "/?city=Астана"},
        headers={"referer": "http://testserver/app"}, follow_redirects=False,
    )
    assert response.headers["location"].startswith("/?city=")


@pytest.mark.parametrize("target", [
    "https://attacker.example/",
    "//attacker.example/",
    "///attacker.example/",
    "/\\attacker.example/",
    "/%5cattacker.example/",
    "/%2f%2fattacker.example/",
    "/%2F/attacker.example/",
    "/%0d%0aLocation:%20https://attacker.example/",
    "/\tattacker",
    "javascript:alert(1)",
    "app",
    "",
])
def test_language_next_rejects_non_local_targets(client, target):
    response = client.get("/lang/en", params={"next": target}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_language_next_repeated_is_rejected(client):
    response = client.get("/lang/en?next=/app&next=/", follow_redirects=False)
    assert response.headers["location"] == "/"


def test_language_links_carry_the_current_page(client):
    response = client.get("/app?city=Алматы&lang=kk")
    assert "/lang/en?next=%2Fapp%3Fcity%3D%25D0%2590" in response.text
    assert "next=%2Fapp%3Fcity%3D%25D0%2590%25D0%25BB%25D0%25BC%25D0%25B0%25D1%2582%25D1%258B%26lang" not in response.text


def test_unknown_language_switch_does_not_change_cookie(client):
    client.get("/?lang=kk")
    response = client.get("/lang/invalid", follow_redirects=False)
    assert response.status_code == 303
    assert "set-cookie" not in response.headers
    assert client.cookies["lang"] == "kk"


def test_docs_and_api_schema(client):
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    assert "/healthz" in paths
    assert "/api/meta" in paths


def test_csrf_token_persists_in_signed_session(client):
    first = client.get("/")
    second = client.get("/app")
    assert first.context["csrf"]
    assert first.context["csrf"] == second.context["csrf"]
    assert "tandau_session=" in first.headers["set-cookie"]
    assert "httponly" in first.headers["set-cookie"].lower()
    assert "samesite=lax" in first.headers["set-cookie"].lower()
