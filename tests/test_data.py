import csv
from datetime import date
from pathlib import Path

import pytest

from matcher.data import DEFAULT_CATALOG_PATH, WINDOW_END, WINDOW_START, load_catalog, parse_row


@pytest.fixture(scope="module")
def catalog():
    # The domain can be checked without FastAPI or an application lifespan.
    return load_catalog()


@pytest.fixture
def source_row():
    with DEFAULT_CATALOG_PATH.open(encoding="utf-8-sig", newline="") as stream:
        return next(csv.DictReader(stream))


def write_catalog(path: Path, rows: list[dict]) -> Path:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_row_count_and_unique_ids(catalog):
    assert len(catalog.contractors) == len(catalog.by_id) == 66


def test_flags_parsed_from_true_false(catalog):
    assert sum(c.synthetic for c in catalog.contractors) == 13
    assert sum(c.price_imputed for c in catalog.contractors) == 18
    assert sum(c.city_imputed for c in catalog.contractors) == 8
    assert catalog.by_id["HK-44733"].synthetic is False


def test_categories_are_list_elements(catalog):
    assert len(catalog.categories) == 17
    hosts = [c for c in catalog.contractors if c.has_category("Ведущий")]
    ceremony = [c for c in catalog.contractors if c.has_category("Ведущий церемонии")]
    assert len(hosts) == 15 and len(ceremony) == 3
    assert not catalog.by_id["HK-77793"].has_category("Ведущий")


def test_max_hours_empty_is_none(catalog):
    assert sum(c.max_hours is None for c in catalog.contractors) == 9
    assert catalog.by_id["HK-44733"].max_hours == 6


def test_busy_dates_inside_window(catalog):
    for contractor in catalog.contractors:
        assert isinstance(contractor.busy_dates, frozenset)
        assert all(WINDOW_START <= day <= WINDOW_END for day in contractor.busy_dates), contractor.id
        assert all(date.fromisoformat(day).isoformat() == day for day in contractor.busy_dates)


def test_known_date_availability(catalog):
    assert not catalog.by_id["HK-42352"].is_free("2026-10-10")
    assert catalog.by_id["HK-42352"].is_free("2026-10-17")
    assert catalog.by_id["HK-27222"].is_free("2026-10-10")
    assert not catalog.by_id["HK-27222"].is_free("2026-10-17")


def test_category_city_counts(catalog):
    assert catalog.category_city_counts["Ведущий"] == {"Алматы": 10, "Астана": 5}
    assert "Астана" not in catalog.category_city_counts["Декоратор"]
    assert len(catalog.in_category_city("Ведущий", "Алматы")) == 10
    assert catalog.in_category_city("Декоратор", "Астана") == []


def test_metadata_matches_reference(catalog):
    meta = catalog.meta()
    assert meta["cities"] == ["Алматы", "Астана", "Зарубежье"]
    assert len(meta["event_formats"]) == 6
    assert len(meta["languages"]) == 3
    assert meta["window"] == {"start": WINDOW_START, "end": WINDOW_END, "days": 100}
    assert meta["stats"] == {
        "profiles": 66, "categories": 17, "cities": 3, "days": 100,
        "synthetic": 13, "price_imputed": 18, "city_imputed": 8,
    }
    rows = meta["categories"]
    assert rows == sorted(rows, key=lambda row: (-row["total"], row["name"]))
    assert rows[0] == {"name": "Ведущий", "total": 15, "by_city": {"Алматы": 10, "Астана": 5}}


def test_parse_whitespace_bom_and_uppercase_flags(tmp_path, source_row):
    source_row.update(categories=" Флорист | Декоратор ", synthetic=" TRUE ",
                      city_imputed=" FALSE ", max_hours="  ", city=" Алматы ")
    parsed = load_catalog(write_catalog(tmp_path / "catalog.csv", [source_row]))
    contractor = parsed.contractors[0]
    assert contractor.categories == ("Флорист", "Декоратор")
    assert contractor.synthetic is True and contractor.city_imputed is False
    assert contractor.max_hours is None and contractor.city == "Алматы"
    assert parsed.stats()["profiles"] == 1
    assert parsed.stats()["categories"] == 2
    assert parsed.meta()["cities"] == ["Алматы"]
    assert parsed.meta()["languages"] == ["русский"]


def test_duplicate_id_is_rejected(tmp_path, source_row):
    with pytest.raises(ValueError, match="duplicate contractor id"):
        load_catalog(write_catalog(tmp_path / "catalog.csv", [source_row, source_row]))


@pytest.mark.parametrize(("field", "value"), [
    ("synthetic", "yes"), ("price_from_kzt", "0"), ("max_hours", "-1"),
    ("busy_dates", "2026-02-30"), ("busy_dates", "2027-01-01"),
    ("categories", ""),
])
def test_malformed_catalog_values_are_rejected(source_row, field, value):
    source_row[field] = value
    with pytest.raises(ValueError):
        parse_row(source_row)


def test_missing_columns_are_rejected(tmp_path):
    path = tmp_path / "catalog.csv"
    path.write_text("id,anon_name\nHK-1,Name\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing CSV columns"):
        load_catalog(path)
