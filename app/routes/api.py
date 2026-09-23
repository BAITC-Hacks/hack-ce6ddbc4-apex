from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/healthz", tags=["service"])
def healthz(request: Request) -> dict:
    return {"status": "ok", "profiles": len(request.app.state.catalog.contractors)}


@router.get("/api/meta", tags=["catalog"])
def meta(request: Request) -> dict:
    """Города, категории с количеством по городам, форматы, языки и окно дат."""
    return request.app.state.catalog.meta()


# ---------- Фаза 5: POST /api/compare ----------
import time
from dataclasses import asdict
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field

from matcher.compare import compare_dates
from matcher.models import SearchRequest

from ..i18n import SUPPORTED, translate


class CompareRequestIn(BaseModel):
    city: str = Field(examples=["Алматы"])
    event_type: str = Field(examples=["свадьба"])
    category: str = Field(examples=["Ведущий"])
    budget_kzt: int = Field(examples=[1_000_000])
    duration_h: Optional[int] = Field(default=None, examples=[8])
    language: Optional[str] = Field(default=None, examples=["казахский"])
    wishes: Optional[str] = None
    lang: str = "ru"
    date: Optional[str] = None                        # игнорируется: даты — в date_a / date_b


class CompareIn(BaseModel):
    request: CompareRequestIn
    date_a: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-10-10"])
    date_b: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-10-17"])


@router.post("/api/compare", tags=["matching"])
def api_compare(body: CompareIn, request: Request) -> dict:
    """Один запрос на две даты: обе выдачи и diff — кто вошёл, кто выпал (с причиной), кто остался."""
    if body.date_a == body.date_b:
        raise HTTPException(status_code=422, detail="date_a и date_b должны различаться")
    started = time.perf_counter()
    data = body.request.model_dump(exclude={"date"})
    lang = data["lang"] if data["lang"] in SUPPORTED else "ru"
    req = SearchRequest(date=body.date_a, **{**data, "lang": lang})
    result = compare_dates(request.app.state.catalog, req, body.date_a, body.date_b,
                           lambda key, **kw: translate(lang, key, **kw))
    a, b = asdict(result["a"]), asdict(result["b"])
    latency = round((time.perf_counter() - started) * 1000, 1)
    a["meta"]["latency_ms"] = b["meta"]["latency_ms"] = latency   # как в /api/recommend: движок без времени
    return {"date_a": body.date_a, "date_b": body.date_b, "a": a, "b": b, "diff": result["diff"]}
