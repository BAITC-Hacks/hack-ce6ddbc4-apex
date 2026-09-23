import pytest

from app.brief import (
    BUDGET_MAX, DUPLICATE_ERROR, EXAMPLE_VALUES, FIELDS, Choices, normalize_budget, parse_brief,
)


@pytest.fixture(scope="module")
def choices(catalog):
    return Choices.from_meta(catalog.meta())


READY = [
    ("city", "Алматы"), ("date", "2026-10-17"), ("event_type", "свадьба"),
    ("category", "Ведущий"), ("budget", "1000000"),
]


@pytest.mark.parametrize(("raw", "expected"), [
    ("1000000", 1_000_000),
    ("1 000 000", 1_000_000),
    ("1\u00a0000\u00a0000", 1_000_000),
    ("1\u202f000\u202f000", 1_000_000),
    ("  250 000 ", 250_000),
    ("000500", 500),
    ("1", 1),
    (str(BUDGET_MAX), BUDGET_MAX),
])
def test_budget_accepts_whole_tenge(raw, expected):
    assert normalize_budget(raw) == (expected, None)


@pytest.mark.parametrize(("raw", "kind"), [
    ("0", "positive"),
    ("0000", "positive"),
    ("-5", "positive"),
    ("-0", "positive"),
    ("1,5", "integer"),
    ("1000.50", "integer"),
    ("1e6", "integer"),
    ("₸1000", "integer"),
    ("1000₸", "integer"),
    ("+100", "integer"),
    ("1\t000", "integer"),
    ("١٢٣", "integer"),
    ("abc", "integer"),
    (str(BUDGET_MAX + 1), "too_large"),
    ("9" * 40, "too_large"),
])
def test_budget_rejects_everything_else(raw, kind):
    assert normalize_budget(raw) == (None, kind)


@pytest.mark.parametrize("raw", ["", "   ", "\u00a0"])
def test_empty_budget_differs_from_zero(raw):
    assert normalize_budget(raw) == (None, None)


@pytest.mark.parametrize(("raw", "error"), [
    ("2026-09-23", None),
    ("2026-12-31", None),
    ("2026-09-22", "brief.date.window"),
    ("2027-01-01", "brief.date.window"),
    ("2026-02-30", "brief.date.invalid"),
    ("2026-13-01", "brief.date.invalid"),
    ("20261017", "brief.date.invalid"),
    ("2026-10-17T00:00", "brief.date.invalid"),
    ("17.10.2026", "brief.date.invalid"),
    ("0000-01-01", "brief.date.invalid"),
])
def test_date_window_and_format(choices, raw, error):
    item = parse_brief([("date", raw)], choices)["date"]
    assert item.error == error
    assert (item.value == raw) is (error is None)


def test_categories_compare_whole_values(choices):
    assert parse_brief([("category", "Ведущий")], choices)["category"].value == "Ведущий"
    assert parse_brief([("category", "Ведущий церемонии")], choices)["category"].value == "Ведущий церемонии"
    for raw in ("ведущий", "Ведущий ", "Ведущ", "Ведущий|Фотограф"):
        item = parse_brief([("category", raw)], choices)["category"]
        assert item.value is None and item.error == "brief.category.error"


@pytest.mark.parametrize(("field", "raw", "error"), [
    ("city", "Москва", "brief.city.unknown"),
    ("city", "алматы", "brief.city.unknown"),
    ("event_type", "Свадьба", "brief.event_type.unknown"),
    ("event_type", "выпускной", "brief.event_type.unknown"),
])
def test_unknown_reference_values(choices, field, raw, error):
    assert parse_brief([(field, raw)], choices)[field].error == error


def test_toi_and_wedding_stay_distinct(choices):
    assert parse_brief([("event_type", "той")], choices)["event_type"].value == "той"
    assert parse_brief([("event_type", "свадьба")], choices)["event_type"].value == "свадьба"


def test_empty_request_is_never_ready(choices):
    brief = parse_brief([], choices)
    assert brief.state == "empty"
    assert not brief.present and not brief.complete and brief.filled == 0


def test_partial_snapshot_names_missing_fields_without_errors(choices):
    brief = parse_brief([("city", "Алматы"), ("category", "Ведущий")], choices)
    assert brief.state == "incomplete"
    assert brief.invalid == []
    assert [item.name for item in brief.missing] == ["date", "event_type", "budget"]
    assert brief.filled == 2


def test_present_empty_values_count_as_a_snapshot(choices):
    brief = parse_brief([(name, "") for name in FIELDS], choices)
    assert brief.present and brief.state == "incomplete" and brief.filled == 0


def test_repeated_field_is_an_error_of_that_field(choices):
    brief = parse_brief(READY + [("city", "Астана")], choices)
    assert brief["city"].error == DUPLICATE_ERROR
    assert brief.state == "invalid"
    assert brief.form_values()["city"] == ""
    # Other conditions stay intact for correction.
    assert brief["budget"].value == 1_000_000


def test_ready_request_normalizes_for_the_future_engine(choices):
    brief = parse_brief(READY, choices)
    assert brief.state == "ready" and brief.complete
    assert brief.normalized("ru") == {
        "city": "Алматы", "date": "2026-10-17", "event_type": "свадьба", "category": "Ведущий",
        "budget_kzt": 1_000_000, "duration_h": None, "language": None, "wishes": None, "lang": "ru",
    }


def test_zero_coverage_category_is_still_valid(choices):
    brief = parse_brief([("city", "Астана"), ("date", "2026-11-05"), ("event_type", "той"),
                         ("category", "Декоратор"), ("budget", "300000")], choices)
    assert brief.state == "ready"


def test_query_keeps_only_the_five_conditions(choices):
    brief = parse_brief(READY + [("wishes", "без конкурсов"), ("matching_available", "1"), ("lang", "en")], choices)
    assert brief.query() == (
        "city=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&date=2026-10-17&event_type=%D1%81%D0%B2%D0%B0%D0%B4%D1%8C%D0%B1%D0%B0"
        "&category=%D0%92%D0%B5%D0%B4%D1%83%D1%89%D0%B8%D0%B9&budget=1000000"
    )


def test_invalid_raw_values_survive_for_correction(choices):
    brief = parse_brief([("budget", "1 000 abc"), ("city", "Алматы")], choices)
    assert brief.form_values()["budget"] == "1 000 abc"
    assert "budget=1+000+abc" in brief.query()


def test_budget_link_value_is_canonical(choices):
    brief = parse_brief([("budget", "0001 000 000")], choices)
    assert brief.form_values()["budget"] == "1000000"


def test_example_values_are_a_ready_request(choices):
    assert parse_brief(EXAMPLE_VALUES.items(), choices).state == "ready"
