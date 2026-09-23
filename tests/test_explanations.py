"""Фаза 5: качество объяснений и честность. Ожидания — только из docs/01_REFERENCE.md (§3.5, §4)."""
import itertools
import json
import re
import time
from dataclasses import asdict, replace

import pytest

from app.i18n import translate
from matcher.compare import compare_dates
from matcher.engine import recommend
from matcher.evidence import best_quote, build_query, get_index
from matcher.explain import are_interchangeable, check_explanation
from matcher.facts import extract_facts
from matcher.models import SearchRequest

S1 = SearchRequest(city="Алматы", date="2026-10-10", event_type="корпоратив", category="Ведущий",
                   budget_kzt=1_500_000, duration_h=6)
S2 = SearchRequest(city="Алматы", date="2026-10-17", event_type="свадьба", category="Ведущий",
                   budget_kzt=1_000_000, duration_h=8, language="казахский")
S2_10 = replace(S2, date="2026-10-10")
S4 = SearchRequest(city="Астана", date="2026-11-14", event_type="свадьба", category="Декоратор", budget_kzt=2_500_000)
S5 = SearchRequest(city="Алматы", date="2026-12-26", event_type="той", category="Ведущий", budget_kzt=700_000)
FORMATS = ("свадьба", "той", "корпоратив", "конференция", "юбилей", "день рождения")


def tr_for(lang: str = "ru"):
    return lambda key, **kw: translate(lang, key, **kw)


@pytest.fixture(scope="module")
def run(catalog):
    return lambda req, lang="ru": recommend(catalog, replace(req, lang=lang), tr_for(lang))


# ---------- facts.py: реальные фрагменты из 01_REFERENCE.md §3.5 ----------

@pytest.mark.parametrize("fragment, years, events", [
    ("Опыт ведения свадеб 13 лет … 356 свадеб, 0 разводов", 13, 356),             # Эмилия
    ("более чем 10-летним опытом и более 1000 реализованных съёмок", 10, 1000),     # Тохру
    ("уже около семи лет", 7, None),                                                 # Альфонс Элрик
    ("проект с шестилетней историей", 6, None),                                      # Сакура Харуно
    ("опытом работы более 10 лет", 10, None),                                        # Буллма
    ("двуязычных ведущих … с опытом более 12 лет", 12, None),                        # Сон Гоку
    ("ВЕДУ МЕРОПРИЯТИЯ УЖЕ БОЛЕЕ 15 ЛЕТ", 15, None),                                 # Нами (капслок)
    ("ведёт 12 лет на каз/рус языках", 12, None),                                    # Тэнъя Иида
    ("Сняла более 80 мероприятий", None, 80),                                        # Какаши Хатаке
    ("Более 5 лет создаём концепции", 5, None),                                      # Уинри Рокбелл
    ("За 2 года она вошла в топ-3", 2, None),                                        # Юдзи Итадори
    ("Ежемесячно реализуем более 1000 заказов", None, 1000),                         # Тони Тони Чоппер
])
def test_facts_from_reference_fragments(fragment, years, events):
    f = extract_facts(fragment)
    assert (f.years_min, f.events_count) == (years, events)
    assert all(span in fragment for _, span in f.evidence_spans)  # основание — точная подстрока


def test_facts_scale_languages_traditions():
    assert extract_facts("крупные бизнес форумы на 3000 человек").audience_max == 3000
    kiki = extract_facts("Работает на казахском, русском и английском … проводы невесты, обряд первых шагов")
    assert set(kiki.languages_mentioned) == {"казахский", "русский", "английский"}
    assert {"kyz_uzatu", "tusaukeser"} <= set(kiki.formats_mentioned)
    assert extract_facts("актёр театра и кино … телеведущий … Язык проведения: казахский").languages_mentioned == ("казахский",)
    assert set(extract_facts("ведёт 12 лет на каз/рус языках").languages_mentioned) == {"казахский", "русский"}
    assert extract_facts("Ежемесячно реализуем более 1000 заказов").events_period == "month"


@pytest.mark.parametrize("text", ["Женат. Есть двое детей", "двуязычных ведущих", "вошла в топ-3", "0 разводов"])
def test_facts_no_false_positives(text):
    f = extract_facts(text)
    assert f.years_min is None and f.events_count is None


# ---------- evidence.py ----------

def test_best_quote_is_short_substring(catalog):
    index = get_index(catalog)
    for c in catalog.contractors:
        for event in FORMATS:
            req = SearchRequest(city=c.city, date="2026-10-10", event_type=event,
                                category=c.categories[0], budget_kzt=10 ** 7)
            quote = best_quote(c.description, build_query(req), index).strip("…")
            assert quote in c.description, (c.id, event)
            assert len(quote.split()) <= 12, (c.id, event)


# ---------- explain.py: DoD «объяснения не взаимозаменяемы» ----------

@pytest.mark.parametrize("lang", ["ru", "kk", "en"])
@pytest.mark.parametrize("req", [S1, S2], ids=["S1", "S2-17.10"])
def test_explanations_distinct_unique_clean(run, catalog, req, lang):
    resp = run(req, lang)
    assert resp.status == "found" and len(resp.cards) == 3
    names = tuple(c.name for c in catalog.contractors)
    for a, b in itertools.combinations(resp.cards, 2):
        assert not are_interchangeable(a.explanation, b.explanation, names), (a.name, b.name)
    for card in resp.cards:
        assert any(atom.unique for atom in card.atoms), card.name
        assert check_explanation(card.explanation, catalog.by_id[card.id].description) == [], card.name
        assert len(re.findall(r"[.!?](?:\s|$)", card.explanation)) <= 2, card.name  # 1–2 предложения


def test_s2_reference_facts_in_texts(run):
    cards = {c.name: c for c in run(S2).cards}
    assert set(cards) == {"Эмилия", "Кики", "Хаул"}
    assert "13 лет" in cards["Эмилия"].explanation and "356 свадеб" in cards["Эмилия"].explanation
    assert "единственный из трёх, кто работает ещё и на английском" in cards["Кики"].explanation.lower()
    assert "ровно бюджет" in cards["Хаул"].explanation
    assert "price_imputed" in cards["Эмилия"].badges and "price_equals_budget" in cards["Хаул"].badges


def test_why_not_more_s1(run):
    resp = run(S1)
    assert resp.more_count == 2
    lines = {line["reason"]: line for line in resp.why_not}
    assert set(lines["busy"]["ids"]) == {"HK-44733", "HK-42352", "HK-44923", "HK-35215"}
    assert lines["budget"]["text"] == "Софи Хаттер — от 2 000 000 ₸ при бюджете 1 500 000 ₸"
    assert lines["rank"]["text"].startswith("Ещё 2 подходят, но ниже в рейтинге")


def test_why_not_more_s2_10(run):
    lines = {line["reason"]: line for line in run(S2_10).why_not}
    assert lines["busy"]["text"].startswith("Эмилия, Кики") and "заняты 10 октября" in lines["busy"]["text"]
    assert set(lines["format"]["ids"]) == {"HK-88430", "HK-29829", "HK-75012"}   # Куррапика, Аня Форджер, Джинбей
    assert lines["budget"]["ids"] == ["HK-72938"]                                   # Софи Хаттер


# ---------- hints.py ----------

def test_hints_s2_nearest_dates(run):
    resp = run(S2_10)
    assert resp.status == "partial"
    hint = next(h for h in resp.hints if h["type"] == "date")
    got = {d["date"]: d["names"] for d in hint["params"]["dates"]}
    assert got == {"2026-10-09": ["Эмилия", "Кики", "Хаул"], "2026-10-11": ["Эмилия", "Хаул", "Сон Гоку"]}
    assert "9 октября (Эмилия, Кики, Хаул) и 11 октября (Эмилия, Хаул, Сон Гоку)" in hint["text"]


def test_hints_s5_combined_and_honest_none(run):
    resp = run(S5)
    assert resp.status == "none_match"
    assert resp.hints[0]["type"] == "date_none"       # ±14 дней при 700 000 ₸ — вариантов нет, говорим прямо
    combo = next(h for h in resp.hints if h["type"] == "combined")
    assert combo["params"]["date"] == "2026-12-27" and combo["params"]["budget_kzt"] == 900_000
    assert combo["text"] == "С бюджетом от 900 000 ₸ 27 декабря свободны Эмилия и Кики"


def test_hints_s4_other_city(run):
    resp = run(S4)
    assert resp.status == "no_category_in_city"
    assert resp.hints[0]["params"] == {"city": "Алматы", "total": 3, "synthetic": 2}
    assert resp.hints[0]["text"] == "В Алматы — 3 профиля в категории «Декоратор», из них 2 синтетических"


# ---------- compare.py + API ----------

def test_compare_s2_diff(catalog):
    res = compare_dates(catalog, S2, "2026-10-10", "2026-10-17", tr_for("ru"))
    diff = res["diff"]
    assert {i["name"] for i in diff["entered"]} == {"Эмилия", "Кики"}
    assert all(i["reason"] == "busy" and i["label"] == "вошёл: был занят 10.10" for i in diff["entered"])
    assert [(i["name"], i["label"]) for i in diff["left"]] == [("Сон Гоку", "выпал: занят 17.10")]
    assert [i["name"] for i in diff["stayed"]] == ["Хаул"]
    emilia = next(c for c in res["b"].cards if c.name == "Эмилия")
    assert emilia.explanation.startswith("17 октября в календаре свободно, а 10 октября было занято")
    assert emilia.atoms[0].type == "availability"


def test_api_compare_and_page(client):
    body = {"request": {"city": "Алматы", "event_type": "свадьба", "category": "Ведущий", "budget_kzt": 1_000_000,
                        "duration_h": 8, "language": "казахский"}, "date_a": "2026-10-10", "date_b": "2026-10-17"}
    data = client.post("/api/compare", json=body).json()
    assert (data["a"]["status"], data["b"]["status"]) == ("partial", "found")
    assert [i["id"] for i in data["diff"]["left"]] == ["HK-27222"]
    assert client.post("/api/compare", json={**body, "date_b": "2026-10-10"}).status_code == 422
    page = client.get("/app/compare", params={"city": "Алматы", "date": "2026-10-10", "event_type": "свадьба",
                                               "category": "Ведущий", "budget": 1_000_000, "language": "казахский", "lang": "ru",
                                               "duration": 8})
    assert page.status_code == 200
    assert "вошёл: был занят 10.10" in page.text and "выпал: занят 17.10" in page.text
    assert client.post("/api/compare", json={**body, "date_a": "2026-10-1"}).status_code == 422
    for bad in ("2026-13-45", "2026-10-1", "завтра"):
        assert client.get("/app/compare", params={"city": "Алматы", "date": bad, "event_type": "свадьба",
                                                  "category": "Ведущий", "budget": 1_000_000}).status_code == 200


def test_malformed_date_is_invalid_request(run):
    assert run(replace(S2, date="2026-10-1")).status == "invalid_request"


# ---------- детерминизм и LLM off ----------

def test_explanations_deterministic(run):
    for req in (S1, S2, S2_10, S5):
        first, second = asdict(run(req)), asdict(run(req))
        for d in (first, second):
            d["meta"].pop("latency_ms", None)
        assert json.dumps(first, sort_keys=True, ensure_ascii=False) == json.dumps(second, sort_keys=True, ensure_ascii=False)


def test_llm_off_by_default(run, monkeypatch):
    monkeypatch.setenv("LLM_MODE", "off")
    started = time.perf_counter()
    resp = run(S2)
    assert resp.meta["llm_used"] is False
    assert time.perf_counter() - started < 1.0   # latency_ms добавляет API-слой (фаза 4), движок детерминирован


def test_guards():
    assert "stop_phrase" in check_explanation("Отличный выбор для вашего мероприятия.", "")
    assert check_explanation("По описанию: «чужая цитата».", "другой текст") == ["quote_not_in_description"]
    assert are_interchangeable("От 900 000 ₸, запас 100 000 ₸.", "От 1 000 000 ₸, запас 500 000 ₸.")
