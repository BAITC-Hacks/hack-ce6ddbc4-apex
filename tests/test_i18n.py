import json

from fastapi import Request

from app import i18n


def test_translation_fallback_and_formatting(monkeypatch, tmp_path):
    monkeypatch.setattr(i18n, "_LOCALES", {})
    (tmp_path / "ru.json").write_text(json.dumps({
        "greeting": "Привет, {name}", "only_ru": "Русский текст",
        "data.city.Алматы": "Алматы",
    }), encoding="utf-8")
    (tmp_path / "en.json").write_text(json.dumps({"greeting": "Hello, {name}"}), encoding="utf-8")
    i18n.load_locales(tmp_path)
    assert i18n.translate("en", "greeting", name="Aruzhan") == "Hello, Aruzhan"
    assert i18n.translate("kk", "only_ru") == "Русский текст"
    assert i18n.translate("en", "missing.key") == "missing.key"
    assert i18n.translate("en", "greeting", wrong="value") == "Hello, {name}"
    assert i18n.data_label("kk", "city", "Алматы") == "Алматы"


def test_language_precedence_including_user():
    request = Request({
        "type": "http", "query_string": b"", "headers": [],
        "state": {"user": {"preferred_lang": "kk"}},
    })
    assert i18n.get_lang(request) == "kk"
    request = Request({
        "type": "http", "query_string": b"lang=ru", "headers": [(b"cookie", b"lang=en")],
        "state": {"user": {"preferred_lang": "kk"}},
    })
    assert i18n.get_lang(request) == "ru"
    request = Request({
        "type": "http", "query_string": b"lang=invalid", "headers": [(b"cookie", b"lang=en")],
        "state": {"user": {"preferred_lang": "kk"}},
    })
    assert i18n.get_lang(request) == "en"
