"""Web adapter for /app: query string -> SearchRequest -> engine -> template context.

Results are strictly query-based. Free-text wishes never travel through the URL.
"""
from __future__ import annotations

from urllib.parse import urlencode

from fastapi import Request

from matcher.data import EVENT_FORMATS, LANGUAGES
from matcher.engine import invalid_response, recommend, request_labels, why_not_groups
from matcher.models import SearchRequest, SearchResponse
from matcher.validation import error, normalize_budget, normalize_hours, validate

from .i18n import get_lang, translate

# Hooks of other phases; each falls back to a no-op until that phase is merged.
try:  # Phase 2: signed-in user from the session
    from .web import resolve_user as get_current_user  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - depends on which phases are merged
    try:  # Phases 2-3 plan: app/deps.py
        from .deps import get_current_user  # type: ignore[attr-defined]
    except ImportError:
        def get_current_user(request: Request):
            return getattr(request.state, "user", None)
try:  # Phase 6: history and shortlist
    from .routes.account import record_search as save_search, starred_ids  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - depends on which phases are merged
    save_search = None

    def starred_ids(user) -> set[str]:
        return set()


REQUIRED = ("city", "date", "event_type", "category", "budget")
OPTIONAL = ("duration", "language")
QUERY_FIELDS = REQUIRED + OPTIONAL
# Query name -> SearchRequest field name (the name validation and hints use).
FIELD_OF = {"city": "city", "date": "date", "event_type": "event_type", "category": "category",
            "budget": "budget_kzt", "duration": "duration_h", "language": "language"}
FIELD_ORDER = ("city", "date", "event_type", "category", "budget_kzt", "duration_h", "language")
FIELD_LABEL_KEYS = {"city": "form.city", "date": "form.date", "event_type": "form.event_type",
                    "category": "form.category", "budget": "form.budget",
                    "duration": "form.duration", "language": "form.language"}

# Ready-made requests from 01_REFERENCE.md §4 (query names: budget, duration).
DEMO_SCENARIOS = [
    ("s1", {"city": "Алматы", "date": "2026-10-10", "event_type": "корпоратив", "category": "Ведущий",
            "budget": "1500000", "duration": "6"}),
    ("s2a", {"city": "Алматы", "date": "2026-10-10", "event_type": "свадьба", "category": "Ведущий",
             "budget": "1000000", "language": "казахский", "duration": "8"}),
    ("s2b", {"city": "Алматы", "date": "2026-10-17", "event_type": "свадьба", "category": "Ведущий",
             "budget": "1000000", "language": "казахский", "duration": "8"}),
    ("s3", {"city": "Алматы", "date": "2026-10-10", "event_type": "той", "category": "Ведущий церемонии",
            "budget": "300000", "language": "казахский"}),
    ("s3b", {"city": "Алматы", "date": "2026-11-14", "event_type": "свадьба", "category": "Флорист",
             "budget": "300000"}),
    ("s4", {"city": "Астана", "date": "2026-11-14", "event_type": "свадьба", "category": "Декоратор",
            "budget": "2500000"}),
    ("s5", {"city": "Алматы", "date": "2026-12-26", "event_type": "той", "category": "Ведущий",
            "budget": "700000"}),
    ("s6", {"city": "Алматы", "date": "2026-11-14", "event_type": "свадьба", "category": "Банкетный зал",
            "budget": "3500000"}),
    ("s7", {"city": "Алматы", "date": "2027-01-15", "event_type": "корпоратив", "category": "Ведущий",
            "budget": "1500000", "duration": "6"}),
]
DEMO_KEYS = {key for key, _ in DEMO_SCENARIOS}


def app_href(params: dict) -> str:
    return "/app?" + urlencode({k: v for k, v in params.items() if v}) + "#results"


def demo_links() -> list[dict]:
    return [{"key": key, "href": app_href({**params, "demo": key})} for key, params in DEMO_SCENARIOS]


def record_search(request: Request, req: SearchRequest, resp: SearchResponse) -> None:
    """History hook: Phase 6 saves members' valid searches; guests and invalid requests are never saved."""
    user = get_current_user(request)
    if not user or resp.status == "invalid_request" or save_search is None:
        return
    save_search(user["id"], req, resp)


def _profiles_enabled(request: Request) -> bool:
    """Phase 6 adds /contractors/{id}; cards link to it only when the route exists."""
    return any(getattr(r, "path", "").startswith("/contractors/") for r in request.app.routes)


def _parse_query(request: Request) -> tuple[dict[str, str], dict[str, str]]:
    """Return (form values as strings, {query name: 'duplicate'} for repeated base params)."""
    form: dict[str, str] = {}
    duplicates: dict[str, str] = {}
    for name in QUERY_FIELDS:
        values = request.query_params.getlist(name)
        if len(values) > 1:
            duplicates[name] = values[0]
        form[name] = values[0].strip() if values else ""
    return form, duplicates


def _card_facts(catalog, cards) -> dict[str, dict]:
    facts = {}
    for card in cards:
        profile = catalog.by_id.get(card.id)
        if profile is None:
            continue
        facts[card.id] = {
            "languages": [x for x in LANGUAGES if x in profile.languages]
                         + sorted(set(profile.languages) - set(LANGUAGES)),
            "max_hours": profile.max_hours,
            "formats": [x for x in EVENT_FORMATS if x in profile.event_formats]
                       + sorted(set(profile.event_formats) - set(EVENT_FORMATS)),
        }
    return facts


def _card_view(cards, budget: int) -> dict[str, dict]:
    views = {}
    for card in cards:
        price = card.price_from_kzt
        pct = min(100, max(0, round(price * 100 / budget))) if budget > 0 else 0
        views[card.id] = {"pct": pct, "margin": max(0, budget - price), "equal": price == budget}
    return views


def search_context(request: Request) -> dict:
    catalog = request.app.state.catalog
    lang = get_lang(request)

    def tr(key: str, **kw) -> str:
        return translate(lang, key, **kw)

    form, duplicates = _parse_query(request)
    demo_key = request.query_params.get("demo", "")
    ctx: dict = {
        "meta": catalog.meta(), "demo": demo_links(), "form": form, "state": "empty",
        "resp": None, "groups": [], "field_errors": {}, "city_links": [], "missing_fields": [],
        "demo_key": demo_key if demo_key in DEMO_KEYS else "", "lang": lang,
        "card_facts": {}, "card_view": {}, "req_labels": {}, "budget": 0,
    }

    present = any(form[name] or name in duplicates for name in QUERY_FIELDS)
    missing = [name for name in REQUIRED if not form[name]]
    if present and missing:
        ctx["state"] = "prefill"
        ctx["missing_fields"] = [tr(FIELD_LABEL_KEYS[name]) for name in missing]
    elif present:
        ctx["state"] = "result"
        parse_errors: list[dict] = []
        for name, first in duplicates.items():
            parse_errors.append(error(FIELD_OF[name], "duplicate", first))
        budget, budget_code = normalize_budget(form["budget"])
        if budget_code and "budget" not in duplicates:
            parse_errors.append(error("budget_kzt", budget_code, form["budget"]))
        hours, hours_code = normalize_hours(form["duration"])
        if hours_code and "duration" not in duplicates:
            parse_errors.append(error("duration_h", hours_code, form["duration"]))

        req = SearchRequest(
            city=form["city"], date=form["date"], event_type=form["event_type"], category=form["category"],
            budget_kzt=budget if budget is not None else 0, duration_h=hours,
            language=form["language"] or None, lang=lang,
        )
        broken = {e["field"] for e in parse_errors}
        errors = parse_errors + [e for e in validate(req, catalog.categories) if e["field"] not in broken]
        errors.sort(key=lambda e: FIELD_ORDER.index(e["field"]) if e["field"] in FIELD_ORDER else len(FIELD_ORDER))

        resp = invalid_response(req, errors, tr) if errors else recommend(catalog, req, tr)
        ctx["resp"] = resp
        ctx["budget"] = req.budget_kzt
        ctx["field_errors"] = {h["field"]: h["text"] for h in resp.hints if h.get("type") == "fix"}
        if resp.status in ("found", "partial", "none_match"):
            ctx["groups"] = why_not_groups(resp, req, tr)
        for hint in resp.hints:
            if hint.get("type") == "other_city":
                ctx["city_links"] = [dict(p, href=app_href({**form, "city": p["city"]}))
                                     for p in hint.get("places", [])]
        if resp.status != "invalid_request":
            ctx["req_labels"] = request_labels(req, tr)
            ctx["card_facts"] = _card_facts(catalog, resp.cards)
            ctx["card_view"] = _card_view(resp.cards, req.budget_kzt)
        record_search(request, req, resp)

    user = get_current_user(request)
    ctx["shortlist_ids"] = starred_ids(user)
    ctx["profiles_enabled"] = _profiles_enabled(request)
    if not form["city"] and user and user.get("preferred_city"):
        form["city"] = user["preferred_city"]    # matching above already ran strictly on the query
    return ctx
