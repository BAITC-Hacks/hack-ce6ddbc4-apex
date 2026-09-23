"""DoD движка: сценарии S1–S7 из docs/01_REFERENCE.md §4 + детерминизм, стоп-фразы, различимость, скорость, API."""
import json
import time

import pytest

from app.config import settings
from app.i18n import load_locales, translate
from matcher.engine import invalid_response, recommend
from matcher.explain import STOP_PHRASES, has_stop_phrase
from matcher.models import SearchRequest
from matcher.scoring import budget_fit
from matcher.validation import BUDGET_MAX, error, normalize_budget


@pytest.fixture(autouse=True, scope="module")
def _locales():
    load_locales(settings.base_dir / "app" / "i18n")      # engine tests call translate() without the app

S = {  # точные параметры сценариев
    "S1": dict(city="Алматы", date="2026-10-10", event_type="корпоратив", category="Ведущий",
               budget_kzt=1_500_000, duration_h=6),
    "S2_1010": dict(city="Алматы", date="2026-10-10", event_type="свадьба", category="Ведущий",
                    budget_kzt=1_000_000, language="казахский", duration_h=8),
    "S2_1710": dict(city="Алматы", date="2026-10-17", event_type="свадьба", category="Ведущий",
                    budget_kzt=1_000_000, language="казахский", duration_h=8),
    "S3": dict(city="Алматы", date="2026-10-10", event_type="той", category="Ведущий церемонии",
               budget_kzt=300_000, language="казахский"),
    "S3b": dict(city="Алматы", date="2026-11-14", event_type="свадьба", category="Флорист", budget_kzt=300_000),
    "S4": dict(city="Астана", date="2026-11-14", event_type="свадьба", category="Декоратор", budget_kzt=2_500_000),
    "S5": dict(city="Алматы", date="2026-12-26", event_type="той", category="Ведущий", budget_kzt=700_000),
    "S6": dict(city="Алматы", date="2026-11-14", event_type="свадьба", category="Банкетный зал",
               budget_kzt=3_500_000),
    "S7": dict(city="Алматы", date="2027-01-15", event_type="корпоратив", category="Ведущий",
               budget_kzt=1_500_000, duration_h=6),
}


def run(catalog, name, lang="ru", **override):
    req = SearchRequest(**{**S[name], **override, "lang": lang})
    return recommend(catalog, req, lambda k, **kw: translate(lang, k, **kw))


def ids(resp):
    return [c.id for c in resp.cards]


def rej(resp):
    return {r.id: r.reasons for r in resp.rejected}


# ---------- S1–S7 ----------

def test_s1_dense_found(catalog):
    r = run(catalog, "S1")
    assert r.status == "found"
    assert len(r.cards) == 3 and r.more_count == 2
    assert set(ids(r)) <= {"HK-88430", "HK-29829", "HK-77838", "HK-27222", "HK-75012"}
    assert {k for k, v in rej(r).items() if "busy" in v} == {"HK-44733", "HK-42352", "HK-44923", "HK-35215"}
    assert rej(r)["HK-72938"] == ["budget"]                       # Софи Хаттер — дороже бюджета
    assert rej(r)["HK-42352"] == ["busy", "format"]               # Эмилия — занята и не берёт корпоративы
    assert [s["n"] for s in r.funnel] == [15, 10, 6, 6, 5, 5, 5]
    assert [s["applied"] for s in r.funnel][-2:] == [False, True]  # язык не задан, часы заданы


def test_s2_two_dates_busy_is_the_reason(catalog):
    a = run(catalog, "S2_1010")
    assert a.status == "partial" and set(ids(a)) == {"HK-77838", "HK-27222"}
    assert rej(a)["HK-42352"][0] == "busy" and rej(a)["HK-35215"][0] == "busy"
    assert "Эмилия" in a.summary and "Кики" in a.summary and "10 октября" in a.summary
    b = run(catalog, "S2_1710")
    assert b.status == "found" and set(ids(b)) == {"HK-42352", "HK-35215", "HK-77838"}
    assert rej(b)["HK-27222"] == ["busy"]                         # Сон Гоку занят 17 октября
    assert "17 октября" in b.summary
    assert set(ids(a)) != set(ids(b))


def test_s3_rare_category(catalog):
    r = run(catalog, "S3")
    assert r.status == "partial" and ids(r) == ["HK-77793"]
    assert rej(r)["HK-90007"] == ["busy", "format"]


def test_s3b_synthetic_florist_is_flagged(catalog):
    r = run(catalog, "S3b")
    assert r.status == "partial" and ids(r) == ["HK-90001"]
    assert "synthetic" in r.cards[0].badges
    assert rej(r)["HK-39372"][0] == "busy"


def test_s4_no_category_in_city(catalog):
    r = run(catalog, "S4")
    assert r.status == "no_category_in_city" and r.cards == []
    assert r.hints[0]["type"] == "other_city"
    assert r.hints[0]["places"] == [{"city": "Алматы", "n": 3, "synthetic": 2}]
    assert "Алматы" in r.summary and "3" in r.summary


def test_s5_none_match_explained(catalog):
    r = run(catalog, "S5")
    assert r.status == "none_match" and r.cards == [] and r.more_count == 0
    assert r.reason_counts["busy"] == 9
    assert rej(r)["HK-44923"] == ["format"]                        # свободен, но не ведёт тои
    assert "Мицури Канроджи" in r.summary and r.summary.strip()


def test_s6_banquet_hall(catalog):
    r = run(catalog, "S6")
    assert r.status == "partial" and set(ids(r)) == {"HK-64395", "HK-90011"}
    by_id = {c.id: c for c in r.cards}
    assert "synthetic" in by_id["HK-90011"].badges
    assert {"price_imputed", "city_imputed"} <= set(by_id["HK-64395"].badges)
    assert rej(r)["HK-72785"] == ["busy", "budget"]
    assert rej(r)["HK-99701"] == ["busy", "format", "budget"]
    for cid in ("HK-58236", "HK-50695", "HK-69010"):
        assert rej(r)[cid] == ["busy"]


def test_s7_invalid_request(catalog):
    r = run(catalog, "S7")
    assert r.status == "invalid_request" and r.cards == [] and r.funnel == []
    assert [h["field"] for h in r.hints] == ["date"]
    assert "23.09–31.12.2026" in r.summary


@pytest.mark.parametrize("override,field", [
    ({"budget_kzt": 0}, "budget_kzt"), ({"city": "Шымкент"}, "city"), ({"category": "Ведущ"}, "category"),
    ({"event_type": "выпускной"}, "event_type"), ({"language": "французский"}, "language"),
    ({"duration_h": 30}, "duration_h"), ({"date": "10.10.2026"}, "date"), ({"date": "2026-02-30"}, "date"),
])
def test_invalid_fields(catalog, override, field):
    r = run(catalog, "S1", **override)
    assert r.status == "invalid_request"
    assert field in [h["field"] for h in r.hints]


def test_all_errors_reported_at_once(catalog):
    r = run(catalog, "S1", budget_kzt=-5, city="Шымкент", duration_h=0)
    assert [h["field"] for h in r.hints] == ["city", "budget_kzt", "duration_h"]


# ---------- детерминизм, тексты, скорость ----------

@pytest.mark.parametrize("name", list(S))
def test_deterministic_json(catalog, name):
    one = json.dumps(run(catalog, name).to_dict(), ensure_ascii=False, sort_keys=True)
    two = json.dumps(run(catalog, name).to_dict(), ensure_ascii=False, sort_keys=True)
    assert one == two


def test_sort_order_is_score_price_id(catalog):
    r = run(catalog, "S1")
    keys = [(-c.score, c.price_from_kzt, c.id) for c in r.cards]
    assert keys == sorted(keys)


@pytest.mark.parametrize("lang", ["ru", "kk", "en"])
def test_no_stop_phrases(catalog, lang):
    for name in S:
        r = run(catalog, name, lang=lang)
        texts = [r.summary] + [c.explanation for c in r.cards] + [a.text for c in r.cards for a in c.atoms]
        for text in texts:
            assert not has_stop_phrase(text), (name, lang, text)


def test_stop_phrase_detector_works():
    assert has_stop_phrase("Отличный выбор для вашего мероприятия!")
    assert has_stop_phrase("Идеально подойдёт")          # ё нормализуется
    assert not has_stop_phrase("Цена от 900 000 ₸ — 90% бюджета, запас 100 000 ₸.")
    assert len(STOP_PHRASES) >= 10


@pytest.mark.parametrize("name", ["S1", "S2_1010", "S2_1710", "S6"])
def test_explanations_distinct_without_names(catalog, name):
    r = run(catalog, name)
    names = sorted({c.name for c in catalog.contractors}, key=len, reverse=True)
    texts = []
    for card in r.cards:
        text = card.explanation
        for n in names:
            text = text.replace(n, "")
        texts.append(text)
    assert len(texts) == len(set(texts)), texts
    for card in r.cards:
        assert any(a.unique for a in card.atoms), card.id
        assert 1 <= card.explanation.count(". ") + 1 <= 2, card.explanation   # 1–2 предложения
        assert any(ch.isdigit() for ch in card.explanation)                  # в объяснении есть число


def test_latency_under_one_second(catalog):
    started = time.perf_counter()
    for name in S:
        run(catalog, name)
    assert time.perf_counter() - started < 1.0


def test_budget_fit_curve():
    # фаза 5: скоринг v2 — доля бюджета, которая остаётся: clip(1 − price / budget)
    from types import SimpleNamespace as NS
    fit = lambda price, budget: budget_fit(NS(price_from_kzt=price), NS(budget_kzt=budget))  # noqa: E731
    assert fit(100, 1000) == pytest.approx(0.9)
    assert fit(900, 1000) == pytest.approx(0.1)
    assert fit(1000, 1000) == 0.0
    assert fit(1001, 1000) == 0.0


# ---------- API ----------

def _payload(name, **extra):
    body = {**S[name], **extra}
    return {k: v for k, v in body.items() if v is not None}


def test_api_recommend_s1(client):
    r = client.post("/api/recommend", json=_payload("S1"))
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "found" and len(data["cards"]) == 3 and data["more_count"] == 2
    assert {"summary", "rejected", "reason_counts", "funnel", "hints", "meta"} <= set(data)
    assert "latency_ms" in data["meta"]


def test_api_business_error_is_200(client):
    r = client.post("/api/recommend", json=_payload("S7"))
    assert r.status_code == 200 and r.json()["status"] == "invalid_request"


def test_api_broken_json_is_422(client):
    r = client.post("/api/recommend", content="{not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_api_wrong_type_is_422(client):
    r = client.post("/api/recommend", json={**_payload("S1"), "budget_kzt": "много"})
    assert r.status_code == 422


def test_api_repeat_is_identical(client):
    def call():
        data = client.post("/api/recommend", json=_payload("S2_1010")).json()
        data["meta"].pop("latency_ms")
        return json.dumps(data, ensure_ascii=False, sort_keys=True)
    assert call() == call()


def test_api_lang_kk(client):
    data = client.post("/api/recommend", json=_payload("S4", lang="kk")).json()
    assert data["status"] == "no_category_in_city" and "Алматы" in data["summary"]


# ---------- Phase 1 contract ----------

def test_budget_too_large_is_invalid(catalog):
    r = run(catalog, "S1", budget_kzt=BUDGET_MAX + 1)
    assert r.status == "invalid_request"
    assert [(h["field"], h["code"]) for h in r.hints] == [("budget_kzt", "too_large")]


@pytest.mark.parametrize("raw,expected", [
    ("1 500 000", (1_500_000, None)), ("1\u00a0000", (1000, None)), ("1\u202f000", (1000, None)),
    ("007", (7, None)), ("", (None, None)), ("0", (None, "positive")), ("-5", (None, "positive")),
    ("1e6", (None, "integer")), ("1,5", (None, "integer")), ("1000.50", (None, "integer")),
    ("₸1000", (None, "integer")), (str(BUDGET_MAX + 1), (None, "too_large")), (str(BUDGET_MAX), (BUDGET_MAX, None)),
])
def test_normalize_budget(raw, expected):
    assert normalize_budget(raw) == expected


def test_to_query_omits_wishes():
    req = SearchRequest(**S["S1"], wishes="живой звук, без конкурсов")
    q = req.to_query()
    assert "wishes" not in q
    assert q["budget"] == "1500000" and q["duration"] == "6"


def test_invalid_response_duplicate_code(catalog):
    req = SearchRequest(**S["S1"])
    r = invalid_response(req, [error("city", "duplicate", "")], lambda k, **kw: translate("ru", k, **kw))
    assert r.status == "invalid_request"
    assert r.hints[0]["field"] == "city" and r.hints[0]["code"] == "duplicate"
    assert "{" not in r.hints[0]["text"] and "{" not in r.summary
