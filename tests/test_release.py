"""Релизный DoD-набор (фаза 7): сценарии S1–S7 из docs/01_REFERENCE.md через HTTP API + гигиена релиза."""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

S1 = {"city": "Алматы", "date": "2026-10-10", "event_type": "корпоратив",
      "category": "Ведущий", "budget_kzt": 1_500_000, "duration_h": 6}
S2 = {"city": "Алматы", "event_type": "свадьба", "category": "Ведущий",
      "budget_kzt": 1_000_000, "language": "казахский", "duration_h": 8}
S1_PASSED = {"HK-88430", "HK-29829", "HK-77838", "HK-27222", "HK-75012"}

# имя: (тело запроса, ожидаемый статус, id карточек; None — проверяется отдельным тестом)
CASES = {
    "S1": (S1, "found", None),
    "S2_1010": ({**S2, "date": "2026-10-10"}, "partial", {"HK-77838", "HK-27222"}),
    "S2_1710": ({**S2, "date": "2026-10-17"}, "found", {"HK-42352", "HK-35215", "HK-77838"}),
    "S3": ({"city": "Алматы", "date": "2026-10-10", "event_type": "той", "category": "Ведущий церемонии",
            "budget_kzt": 300_000, "language": "казахский"}, "partial", {"HK-77793"}),
    "S3_florist": ({"city": "Алматы", "date": "2026-11-14", "event_type": "свадьба", "category": "Флорист",
                    "budget_kzt": 300_000}, "partial", {"HK-90001"}),
    "S4": ({"city": "Астана", "date": "2026-11-14", "event_type": "свадьба", "category": "Декоратор",
            "budget_kzt": 2_500_000}, "no_category_in_city", set()),
    "S5": ({"city": "Алматы", "date": "2026-12-26", "event_type": "той", "category": "Ведущий",
            "budget_kzt": 700_000}, "none_match", set()),
    "S6": ({"city": "Алматы", "date": "2026-11-14", "event_type": "свадьба", "category": "Банкетный зал",
            "budget_kzt": 3_500_000}, "partial", {"HK-64395", "HK-90011"}),
    "S7": ({**S1, "date": "2027-01-15"}, "invalid_request", set()),
}


def recommend(client, body: dict) -> dict:
    response = client.post("/api/recommend", json=body)
    assert response.status_code == 200, response.text
    return response.json()


def stable(data: dict) -> str:
    data = dict(data)
    data.pop("meta", None)                       # meta.latency_ms меняется от вызова к вызову
    return json.dumps(data, sort_keys=True, ensure_ascii=False)


def reasons_by_id(data: dict) -> dict[str, set[str]]:
    return {r["id"]: set(r["reasons"]) for r in data["rejected"]}


# ---------- S1–S7: статус, карточки, исход объяснён словами ----------

@pytest.mark.parametrize("name", list(CASES))
def test_scenario_status_and_cards(client, name):
    body, status, expected_ids = CASES[name]
    data = recommend(client, body)
    assert data["status"] == status, (name, data.get("summary"))
    assert data["summary"].strip(), name         # не пустой экран и не ошибка
    ids = [c["id"] for c in data["cards"]]
    assert len(ids) <= 3, name
    if expected_ids is not None:
        assert set(ids) == expected_ids, (name, ids)


def test_s1_top3_of_5_with_reasons(client):
    data = recommend(client, S1)
    assert len(data["cards"]) == 3 and {c["id"] for c in data["cards"]} <= S1_PASSED
    assert data["more_count"] == 2
    reasons = reasons_by_id(data)
    for cid in ("HK-44733", "HK-42352", "HK-44923", "HK-35215"):   # Буллма, Эмилия, Мицури, Кики
        assert "busy" in reasons[cid], cid
    assert "format" in reasons["HK-42352"]                            # Эмилия не берёт корпоративы
    assert "budget" in reasons["HK-72938"]                            # Софи Хаттер дороже бюджета
    counts = [step["n"] for step in data["funnel"]]
    assert counts[-1] == 5 and 10 in counts and 6 in counts           # 10 → 6 → 6 → 5 → 5


def test_s2_two_dates_differ_because_of_busy(client):
    a = recommend(client, {**S2, "date": "2026-10-10"})
    b = recommend(client, {**S2, "date": "2026-10-17"})
    assert "busy" in reasons_by_id(a)["HK-42352"]      # Эмилия занята 10.10
    assert "busy" in reasons_by_id(a)["HK-35215"]      # Кики занята 10.10
    assert "busy" in reasons_by_id(b)["HK-27222"]      # Сон Гоку занят 17.10
    assert a["hints"], "для 10.10 ожидается подсказка про 9 и 11 октября"


def test_compare_api(client):
    response = client.post("/api/compare", json={
        "request": {**S2, "date": "2026-10-10"}, "date_a": "2026-10-10", "date_b": "2026-10-17"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert {c["id"] for c in data["a"]["cards"]} == {"HK-77838", "HK-27222"}
    assert {c["id"] for c in data["b"]["cards"]} == {"HK-42352", "HK-35215", "HK-77838"}
    assert data["diff"]


def test_s4_no_category_has_hint(client):
    data = recommend(client, CASES["S4"][0])
    assert data["cards"] == [] and data["hints"]


def test_s5_none_match_is_explained(client):
    data = recommend(client, CASES["S5"][0])
    reasons = reasons_by_id(data)
    assert len(reasons) == 10                                        # все 10 ведущих Алматы
    assert sum("busy" in r for r in reasons.values()) == 9           # 9 заняты 26.12
    assert "format" in reasons["HK-44923"]                           # свободный Мицури не ведёт тои
    assert data["hints"]


def test_data_quality_badges(client):
    s6 = {c["id"]: c for c in recommend(client, CASES["S6"][0])["cards"]}
    assert "synthetic" in s6["HK-90011"]["badges"]
    assert {"price_imputed", "city_imputed"} <= set(s6["HK-64395"]["badges"])
    florist = recommend(client, CASES["S3_florist"][0])["cards"][0]
    assert "synthetic" in florist["badges"]


# ---------- DoD: детерминизм, скорость, качество объяснений ----------

@pytest.mark.parametrize("name", ["S1", "S2_1010", "S5", "S6"])
def test_determinism_same_json(client, name):
    body = CASES[name][0]
    assert stable(recommend(client, body)) == stable(recommend(client, body))


def test_response_time_under_10s(client):
    for name, (body, _, _) in CASES.items():
        started = time.perf_counter()
        recommend(client, body)
        assert time.perf_counter() - started < 10.0, name


def test_explanations_specific_and_distinct(client):
    from matcher.explain import STOP_PHRASES
    for name in ("S1", "S2_1710", "S6"):
        cards = recommend(client, CASES[name][0])["cards"]
        texts = [c["explanation"].replace(c["name"], "").strip().lower() for c in cards]
        assert len(set(texts)) == len(texts), name                       # без имён не перепутать
        for text in texts:
            assert any(ch.isdigit() for ch in text) or "«" in text, text  # число или цитата
            assert not any(p.lower() in text for p in STOP_PHRASES), text


# ---------- Гигиена релиза: README, секреты, зависимости ----------

README_MUST_HAVE = [
    "Что делает проект", "Что реализовано", "Как это работает", "Технологии", "Архитектура",
    "Установка и запуск", "Демо-доступ", "Как проверить решение", "Данные", "Переменные окружения",
    "Тесты", "Ограничения", "Использованные компоненты", "Языки интерфейса",
    "pip install -r requirements.txt", "python run.py", "demo@tandau.kz", "Demo2026!",
]


def test_readme_complete():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    missing = [item for item in README_MUST_HAVE if item not in text]
    assert not missing, missing
    assert "{{" not in text, "в README остались плейсхолдеры {{…}}"
    for link in re.findall(r"\]\(((?:docs|data)/[^)\s]+)\)", text):
        assert (ROOT / link).exists(), f"README ссылается на отсутствующий файл {link}"


KEY_PATTERNS = [   # строки собраны из частей, чтобы файл не находил сам себя
    re.compile(r"(?<![A-Za-z0-9_-])" + "s" + r"k-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?<![A-Za-z0-9_-])" + "nv" + r"api-[A-Za-z0-9_-]{20,}"),
]
SKIP_DIRS = {".git", ".venv", "venv", "env", "var", "cache", "__pycache__", ".pytest_cache", "node_modules"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".html", ".css", ".js", ".yml", ".yaml", ".toml",
                 ".cfg", ".ini", ".csv", ".example"}


def test_no_api_keys_in_files():
    hits = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix not in TEXT_SUFFIXES and filename != "Dockerfile":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if any(p.search(text) for p in KEY_PATTERNS):
                hits.append(str(path.relative_to(ROOT)))
    assert not hits, f"похоже на ключ API: {hits}"


def test_core_runs_without_llm_and_secrets():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "openai" not in requirements              # LLM — только requirements-llm.txt (п. 5.6.6)
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        if key.strip() in {"SECRET_KEY", "OPENAI_API_KEY"}:
            assert not value.split("#", 1)[0].strip(), line
