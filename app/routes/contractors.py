"""Phase 6: public contractor profile with the 100-day calendar, and its JSON twin for the API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from jinja2 import pass_context

from ..profiles import availability, badges_for, build_calendar, day_state, profile_payload, search_url
from ..web import render, resolve_user, templates
from .account import safe_back, starred_ids

router = APIRouter()


@pass_context
def human_date(ctx, iso) -> str:
    """"2026-10-10" → «10 октября 2026» / «2026 жылғы 10 қазан» / «10 October 2026» (calendar.* keys)."""
    try:
        year, month, day = (int(part) for part in str(iso).split("-"))
    except ValueError:
        return str(iso)
    t = ctx["t"]
    return t("calendar.date", day=day, month=t(f"calendar.month_gen.{month}"), year=year)


def short_date(iso) -> str:
    """"2026-09-23" → "23.09"."""
    s = str(iso)
    return f"{s[8:10]}.{s[5:7]}" if len(s) == 10 else s


templates.env.filters["human_date"] = human_date
templates.env.filters["short_date"] = short_date


@router.get("/contractors/{contractor_id}", response_class=HTMLResponse, include_in_schema=False)
def contractor_page(contractor_id: str, request: Request):
    c = request.app.state.catalog.by_id.get(contractor_id.strip().upper())
    if c is None:
        return render(request, "app/contractor.html", status_code=404, contractor=None,
                      requested_id=contractor_id[:40])
    months = build_calendar(c.busy_dates)
    selected = request.query_params.get("date", "")
    # Back to the results the visitor came from; only this host's search or account pages qualify.
    back = safe_back(request, (request.headers.get("referer"),), "/app")
    if not back.startswith(("/app", "/account")):
        back = "/app"
    return render(
        request, "app/contractor.html",
        contractor=c,
        badges=badges_for(c),
        months=months,
        december=months[-1],  # the window ends on 31.12, so the last grid month is always December
        avail=availability(c),
        similar=[(cat, search_url(c.city, cat)) for cat in c.categories],
        selected=selected if day_state(c, selected) else "",
        selected_state=day_state(c, selected),
        back_url=back,
        shortlist_ids=starred_ids(resolve_user(request)),
    )


@router.get("/api/contractors/{contractor_id}", tags=["catalog"])
def contractor_profile(contractor_id: str, request: Request) -> dict:
    """Профиль подрядчика: поля каталога (значения по-русски, как в CSV), busy_dates по возрастанию,
    сводка свободных дней (всего, ближайшие 30 от 23.09, по месяцам). Неизвестный id → 404."""
    c = request.app.state.catalog.by_id.get(contractor_id.strip().upper())
    if c is None:
        raise HTTPException(status_code=404, detail="contractor not found")
    return profile_payload(c)
