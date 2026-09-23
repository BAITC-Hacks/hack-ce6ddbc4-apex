import csv
import json
import re
import string
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from app.config import settings
from matcher.data import load_catalog

READY = "city=Алматы&date=2026-10-17&event_type=свадьба&category=Ведущий&budget=1000000"
LOCALES = ("ru", "kk", "en")


class Controls(HTMLParser):
    """Collect form controls of the landing brief."""

    def __init__(self):
        super().__init__()
        self.inputs, self.selected, self.links, self.images = [], [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input":
            self.inputs.append(attrs)
        elif tag == "option" and "selected" in attrs:
            self.selected.append(attrs.get("value"))
        elif tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        elif tag == "img":
            self.images.append(attrs)


def controls(html):
    parser = Controls()
    parser.feed(html)
    return parser


def checked(parsed, name):
    return [item["value"] for item in parsed.inputs if item.get("name") == name and "checked" in item]


def test_first_visit_selects_nothing_for_the_visitor(client):
    response = client.get("/")
    parsed = controls(response.text)
    assert checked(parsed, "city") == []
    assert checked(parsed, "event_type") == []
    assert parsed.selected == [""]
    fields = {item.get("name"): item for item in parsed.inputs if item.get("name") in ("date", "budget")}
    assert fields["date"]["value"] == "" and fields["budget"]["value"] == ""
    assert fields["date"]["min"] == "2026-09-23" and fields["date"]["max"] == "2026-12-31"
    assert fields["budget"]["type"] == "text" and fields["budget"]["inputmode"] == "numeric"
    assert "Заполнено 0 из 5 условий" in response.text
    assert 'aria-invalid' not in response.text
    # The hero card never shows candidate monograms next to editable conditions.
    assert "tl-monograms" not in response.text


def test_brief_form_submits_five_named_fields_to_app(client):
    html = client.get("/").text
    form = re.search(r'<form class="tl-brief"[^>]*>', html).group(0)
    assert 'action="/app"' in form and 'method="get"' in form
    names = {item.get("name") for item in controls(html).inputs if item.get("name")}
    assert {"city", "date", "event_type", "budget"} <= names
    assert 'name="category"' in html


def test_url_snapshot_prefills_the_form_and_card(client):
    response = client.get(f"/?{READY}")
    parsed = controls(response.text)
    assert checked(parsed, "city") == ["Алматы"]
    assert checked(parsed, "event_type") == ["свадьба"]
    assert "Ведущий" in parsed.selected
    budget = next(item for item in parsed.inputs if item.get("name") == "budget")
    assert budget["value"] == "1 000 000"
    assert "Заполнено 5 из 5 условий" in response.text
    assert "Профили в каталоге по этой локации — 10" in response.text


def test_landing_shows_server_errors_for_invalid_link_values(client):
    response = client.get("/?budget=1e6&city=Москва")
    assert "Введите целую сумму в тенге" in response.text
    assert "Этой локации нет в каталоге" in response.text
    assert response.text.count('aria-invalid="true"') >= 2
    parsed = controls(response.text)
    assert checked(parsed, "city") == []
    assert next(item for item in parsed.inputs if item.get("name") == "budget")["value"] == "1e6"


def test_catalog_overview_follows_the_brief_city(client):
    html = client.get("/?city=Астана").text
    assert "Профили в каталоге: Астана" in html
    decorator = re.search(r'data-category="Декоратор">(.*?)</a>', html, re.S).group(1)
    assert 'data-count>0<' in decorator
    assert "В каталоге пока нет профилей в этой локации" in decorator
    all_html = client.get("/").text
    host = re.search(r'data-category="Ведущий">(.*?)</a>', all_html, re.S).group(1)
    assert 'data-count>15<' in host


def test_category_fallback_links_keep_other_conditions(client):
    html = client.get("/?city=Астана&budget=500000").text
    link = re.search(r'href="([^"]+)" data-category="Фотограф"', html).group(1).replace("&amp;", "&")
    parts = urlsplit(link)
    query = parse_qs(parts.query, keep_blank_values=True)
    assert parts.fragment == "brief-category"
    assert query["city"] == ["Астана"] and query["budget"] == ["500000"] and query["category"] == ["Фотограф"]
    assert set(query) == {"city", "date", "event_type", "category", "budget"}


def test_public_actions_have_real_destinations(client):
    html = client.get("/").text
    parsed = controls(html)
    for href in parsed.links:
        if href.startswith("#"):
            assert f'id="{href[1:]}"' in html, href
    assert "/login" in parsed.links and "/register" in parsed.links  # phases 2-3: header account actions
    assert "#brief" in parsed.links and "#example" in parsed.links
    # JavaScript-only controls are hidden in the server HTML.
    for marker in ("data-brief-example", "data-budget-presets", "data-catalog-switch"):
        tag = re.search(rf"<[^>]*{marker}[^>]*>", html).group(0)
        assert "hidden" in tag, marker


def test_example_is_labelled_and_uses_catalog_facts(client):
    response = client.get("/")
    cards = response.context["example_cards"]
    catalog = client.app.state.catalog
    assert [card["id"] for card in cards] == ["HK-42352", "HK-35215", "HK-77838"]
    expected = {
        "HK-42352": (900_000, 10, ("русский", "казахский"), ["price_imputed"]),
        "HK-35215": (900_000, 10, ("казахский", "русский", "английский"), []),
        "HK-77838": (1_000_000, 8, ("русский", "казахский"), ["price_equals_budget"]),
    }
    for card in cards:
        profile = catalog.by_id[card["id"]]
        price, hours, languages, badges = expected[card["id"]]
        # If the CSV changes, the prepared explanations must be reviewed too.
        assert (profile.price_from_kzt, profile.max_hours, profile.languages) == (price, hours, languages)
        assert card["badges"] == badges
        assert card["quote"] and card["quote"] in profile.description
        assert card["demo_date_available"] is profile.is_free("2026-10-17")
    html = response.text
    assert "Подготовленный пример из каталога. Условия вашей формы его не меняют." in html
    assert "100 000" in html and "Стартовая цена равна бюджету" in html
    assert "90% лимита примера" in html
    assert "tl-save" not in html and "Избранное" not in html


def test_example_does_not_follow_the_personal_brief(client):
    base = client.get("/").text
    personal = client.get("/?city=Астана&date=2026-12-01&budget=2000000&category=Фотограф&event_type=той").text
    section = lambda html: re.search(r'<section class="tl-workspace-section".*?</section>', html, re.S).group(0)
    assert section(base) == section(personal)


def test_missing_example_profile_is_not_replaced(client, tmp_path):
    with settings.data_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = [row for row in reader if row["id"] != "HK-35215"]
    path = tmp_path / "catalog.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    client.app.state.catalog = load_catalog(path)
    response = client.get("/")
    assert [card["id"] for card in response.context["example_cards"]] == ["HK-42352", "HK-77838"]
    assert "Часть примера недоступна в текущем каталоге." in response.text
    assert "tl-results--2" in response.text


def test_faq_describes_the_current_capability(client):
    html = client.get("/").text
    assert html.count("<details><summary>") == 7
    assert "Подбор по новым условиям пока недоступен." in html
    assert "Бронирования и оплаты в Tandau нет." in html


def test_client_config_is_safe_json(client):
    html = client.get("/").text
    raw = re.search(r'<script type="application/json" id="brief-config">(.*?)</script>', html, re.S).group(1)
    config = json.loads(raw)
    assert config["storageKey"] == "tandau.brief.v1"
    assert config["budgetMax"] == "9007199254740991"
    assert config["window"] == {"start": "2026-09-23", "end": "2026-12-31", "days": 100}
    assert config["example"]["budget"] == "1000000"
    assert config["counts"]["Декоратор"] == {"Алматы": 3}
    assert all(isinstance(value, str) and value for value in config["text"].values())


@pytest.mark.parametrize("path", ["/", f"/?{READY}", "/app", f"/app?{READY}", "/app?city=Москва&budget=0"])
def test_referenced_images_exist(client, path):
    for image in controls(client.get(path).text).images:
        src = image["src"]
        assert src.startswith("/static/assets/tandau/img/")
        assert (settings.base_dir / "app" / src.lstrip("/")).is_file(), src
        assert image.get("alt") == "" and image.get("width") and image.get("height")


# ---- /app guest summary ----

def test_app_without_conditions_invites_to_the_form(client):
    html = client.get("/app/brief").text
    assert "Задайте условия события" in html
    assert 'href="/#brief"' in html
    assert "Условия готовы" not in html


def test_app_ready_summary_without_fake_results(client):
    response = client.get(f"/app/brief?{READY}")
    html = response.text
    assert response.context["brief"].state == "ready"
    assert "Условия готовы" in html and "Сейчас можно посмотреть пример подбора." in html
    for text in ("Алматы", "17 октября 2026", "Свадьба", "Ведущий", "До 1\u00a0000\u00a0000\u00a0₸"):
        assert text in html
    assert "Профили в каталоге по этой локации — 10" in html
    assert "data-profile" not in html and "Подобрать" not in html and "aria-busy" not in html
    assert 'href="/#example"' in html


def test_app_edit_links_carry_all_five_conditions(client):
    response = client.get(f"/app/brief?{READY}")
    for name in ("city", "date", "event_type", "category", "budget"):
        link = response.context["edit_links"][name]
        parts = urlsplit(link)
        assert parts.path == "/" and parts.fragment == f"brief-{name}"
        query = parse_qs(parts.query)
        assert query["budget"] == ["1000000"] and query["city"] == ["Алматы"]
        assert f'href="{link.replace("&", "&amp;")}"' in response.text


def test_app_partial_link_names_missing_conditions_without_red_errors(client):
    response = client.get("/app/brief?city=Алматы&category=Ведущий")
    html = response.text
    assert response.context["brief"].state == "incomplete"
    assert "Не хватает условий" in html and "Дополнить условия" in html
    assert "tl-error-summary" not in html and "is-invalid" not in html
    assert response.context["first_open"] == "date"
    assert "#brief-date" in response.context["edit_links"]["date"]


def test_app_invalid_link_is_not_a_success(client):
    response = client.get("/app/brief?city=Москва&date=2026-02-30&event_type=свадьба&category=Ведущий&budget=-1")
    html = response.text
    assert response.status_code == 200
    assert response.context["brief"].state == "invalid"
    assert "Условия готовы" not in html
    for text in ("Этой локации нет в каталоге", "Укажите существующую дату", "Бюджет должен быть больше нуля"):
        assert text in html
    assert response.context["first_open"] == "city"


def test_app_zero_coverage_is_information_not_error(client):
    response = client.get("/app/brief?city=Астана&date=2026-11-05&event_type=той&category=Декоратор&budget=300000")
    assert response.context["brief"].state == "ready"
    assert "В каталоге нет этой услуги в выбранной локации" in response.text


def test_app_escapes_values_and_drops_unknown_parameters(client):
    payload = '<script>alert("x")</script>'
    response = client.get("/app/brief", params={"budget": payload, "category": payload, "evil": "marker-9f2"})
    html = response.text
    assert payload not in html
    assert "&lt;script&gt;" in html
    assert "marker-9f2" not in html
    assert "matching_available" not in html


def test_app_repeated_parameter_is_a_field_error(client):
    response = client.get(f"/app/brief?{READY}&city=Астана")
    assert response.context["brief"].state == "invalid"
    assert "Условие указано несколько раз" in response.text


@pytest.mark.parametrize("lang", LOCALES)
def test_landing_and_app_render_every_language_without_raw_keys(client, lang):
    for path in ("/", f"/app?{READY}", "/app?city=Москва", "/app?city=Алматы", "/app"):
        html = client.get(f"{path}{'&' if '?' in path else '?'}lang={lang}").text
        assert f'lang="{lang}"' in html
        raw = re.findall(r">\s*((?:brief|landing|request|card|badge|date|nav|footer|common)\.[a-z0-9_.]+)\s*<", html)
        assert raw == [], (lang, path, raw)


def _fields(text):
    return sorted(name for _, name, _, _ in string.Formatter().parse(text) if name)


def test_locales_share_keys_and_placeholders():
    locales = {
        code: json.loads((Path(settings.base_dir) / "app" / "i18n" / f"{code}.json").read_text(encoding="utf-8"))
        for code in LOCALES
    }
    assert set(locales["kk"]) == set(locales["ru"]) == set(locales["en"])
    # Kazakh quotes the singular format name where RU/EN use the plural; the engine passes both.
    def kk_grammar(fields):
        return sorted("event_type_pl" if name == "event_type" else name for name in fields)
    for key, value in locales["ru"].items():
        for code in ("kk", "en"):
            fields, source = _fields(locales[code][key]), _fields(value)
            if code == "kk":
                fields, source = kk_grammar(fields), kk_grammar(source)
            # A translation may drop a value its grammar doesn't need (Kazakh has no gender) but
            # never use one the engine doesn't pass: that would print a raw {placeholder}.
            assert set(fields) <= set(source), (code, key)
            assert locales[code][key].strip(), (code, key)


def test_server_errors_expose_their_message_key_to_the_script(client):
    html = client.get("/?city=Париж&date=2020-01-01&budget=1e6").text
    assert 'data-error-for="city" data-error-key="brief.city.unknown"' in html
    assert 'data-error-for="date" data-error-key="brief.date.window"' in html
    assert 'data-error-for="budget" data-error-key="brief.budget.integer"' in html
    assert 'data-error-for="event_type" hidden' in html


def test_example_evidence_is_translated(client):
    for lang, yes in (("ru", "Да"), ("kk", "Иә"), ("en", "Yes")):
        html = client.get(f"/?lang={lang}").text
        evidence = re.findall(r'<dl class="tl-evidence">(.*?)</dl>', html, re.S)
        assert len(evidence) == 3
        assert all(">True<" not in block and ">False<" not in block for block in evidence)
        assert f"<dd>{yes}</dd>" in evidence[0]  # HK-42352 price_imputed


def test_profile_count_is_not_repeated_in_the_limits_block(client):
    html = client.get("/").text
    limits = re.search(r'<section class="tl-limits".*?</section>', html, re.S).group(0)
    assert ">66<" not in limits and " 66 " not in limits


def test_request_edit_links_sit_inside_the_definition(client):
    html = client.get(f"/app/brief?{READY}").text
    rows = re.findall(r'<div class="tl-request-row[^"]*">(.*?)</div>\s*(?=<div class="tl-request-row|</dl>)', html, re.S)
    assert len(rows) == 5
    for row in rows:
        dd = re.search(r"<dd>(.*?)</dd>", row, re.S).group(1)
        assert 'class="tl-request-edit"' in dd


def test_language_link_name_contains_visible_code(client):
    html = client.get("/").text
    link = re.search(r'<a [^>]*data-lang-link="kk"[^>]*>(.*?)</a>', html, re.S)
    assert "aria-label" not in link.group(0)
    assert link.group(1).startswith("ҚАЗ") and "Қазақша" in link.group(1)


def test_landing_has_a_hidden_storage_warning(client):
    html = client.get("/").text
    assert re.search(r'<p class="tl-brief-note" data-storage-note hidden>', html)
