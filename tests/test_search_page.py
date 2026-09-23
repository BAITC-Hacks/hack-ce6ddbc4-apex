"""/app: form, five outcomes, prefill without a fake result, Phase 1 query contract, three languages."""
import re
from urllib.parse import urlencode

import pytest

from app.search import DEMO_SCENARIOS, demo_links

S1 = {"city": "Алматы", "date": "2026-10-10", "event_type": "корпоратив", "category": "Ведущий",
      "budget": "1500000", "duration": "6"}
EXPECTED = {"s1": "found", "s2a": "partial", "s2b": "found", "s3": "partial", "s3b": "partial",
            "s4": "nocat", "s5": "none", "s6": "partial", "s7": "invalid"}
RAW_KEY = re.compile(r"(?<![\w/.-])(search|status|result|form|explain|funnel|reason|demo|data|badge)\.[a-z_]+")


def results_html(text):
    start = text.index('id="results"')
    return text[start:text.index("</section>", start)]


def test_app_form_without_params(client):
    r = client.get("/app")
    assert r.status_code == 200 and 'name="category"' in r.text and "banner--" not in r.text
    assert 'name="wishes"' not in r.text


def test_app_found_renders_three_cards(client):
    r = client.get("/app?" + urlencode(S1))
    assert r.status_code == 200
    assert "banner--found" in r.text and r.text.count('class="result-card"') == 3
    assert "funnel" in r.text and "whynot" in r.text


def test_app_other_statuses(client):
    cases = {
        "banner--nocat": {"city": "Астана", "date": "2026-11-14", "event_type": "свадьба",
                          "category": "Декоратор", "budget": "2500000"},
        "banner--none": {"city": "Алматы", "date": "2026-12-26", "event_type": "той",
                         "category": "Ведущий", "budget": "700000"},
        "banner--invalid": {**S1, "date": "2027-01-15"},
    }
    for css, params in cases.items():
        r = client.get("/app?" + urlencode(params))
        assert r.status_code == 200 and css in r.text, css


def test_app_garbage_budget_is_invalid_not_422(client):
    r = client.get("/app?" + urlencode({**S1, "budget": "abc"}))
    assert r.status_code == 200 and "banner--invalid" in r.text
    assert 'aria-invalid="true"' in r.text


def test_app_budget_with_spaces_is_accepted(client):
    r = client.get("/app?" + urlencode({**S1, "budget": "1 500 000"}))
    assert "banner--found" in r.text


def test_app_partial_query_prefills_without_result(client):
    r = client.get("/app?" + urlencode({"city": "Алматы", "category": "Ведущий"}))
    assert r.status_code == 200 and "banner--" not in r.text and "result-card" not in r.text
    assert "search-empty--prefill" in r.text


def test_app_duplicate_base_param_is_field_error(client):
    r = client.get("/app?" + urlencode(S1) + "&city=" + "Астана")
    assert "banner--invalid" in r.text


def test_app_wishes_never_in_links(client):
    r = client.get("/app?" + urlencode({**S1, "wishes": "живой звук"}))
    assert "banner--found" in r.text and "wishes" not in r.text


def test_demo_links_are_marked():
    links = {d["key"]: d["href"] for d in demo_links()}
    assert "demo=s1" in links["s1"] and len(links) == len(DEMO_SCENARIOS)


@pytest.mark.parametrize("lang", ["ru", "kk", "en"])
def test_demo_scenarios_render_in_every_language(client, lang):
    for d in demo_links():
        r = client.get(d["href"].split("#")[0] + "&lang=" + lang)
        assert r.status_code == 200 and f'lang="{lang}"' in r.text
        assert f"banner--{EXPECTED[d['key']]}" in r.text, (d["key"], lang)
        block = results_html(r.text)
        assert "{" not in block and "}" not in block, (d["key"], lang)
        assert not RAW_KEY.search(re.sub(r"<[^>]+>", " ", block)), (d["key"], lang, RAW_KEY.search(block))


def test_history_hook_saves_members_only(client, monkeypatch):
    import app.search as search
    saved = []
    monkeypatch.setattr(search, "save_search", lambda uid, req, resp: saved.append((uid, resp.status)))
    client.get("/app?" + urlencode(S1))
    assert saved == []                                        # guest: never saved
    monkeypatch.setattr(search, "get_current_user", lambda request: {"id": 7})
    client.get("/app?" + urlencode(S1))
    client.get("/app?" + urlencode({**S1, "date": "2027-01-15"}))   # invalid_request: not saved
    assert saved == [(7, "found")]


def test_cards_link_to_profiles_only_when_route_exists(client):
    assert 'href="/contractors/' not in client.get("/app?" + urlencode(S1)).text
    client.app.add_api_route("/contractors/{contractor_id}", lambda contractor_id: {}, methods=["GET"])
    assert 'href="/contractors/HK-' in client.get("/app?" + urlencode(S1)).text
