from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from matcher.engine import recommend
from matcher.models import SearchRequest

from ..i18n import SUPPORTED, translate

router = APIRouter()

S1_EXAMPLE = {"city": "Алматы", "date": "2026-10-10", "event_type": "корпоратив", "category": "Ведущий",
              "budget_kzt": 1500000, "duration_h": 6, "language": None, "wishes": None, "lang": "ru"}


class RecommendIn(BaseModel):
    """Форма запроса. Типы проверяет pydantic (иначе 422); смысл — matcher.validation (200 + invalid_request)."""
    model_config = ConfigDict(json_schema_extra={"examples": [S1_EXAMPLE]})

    city: str = Field(description="Алматы | Астана | Зарубежье — как в CSV")
    date: str = Field(description="YYYY-MM-DD, окно 2026-09-23…2026-12-31")
    event_type: str = Field(description="свадьба | той | корпоратив | конференция | юбилей | день рождения")
    category: str = Field(description="одна из 17 категорий каталога, например «Ведущий»")
    budget_kzt: int = Field(description="бюджет в тенге, > 0")
    duration_h: Optional[int] = Field(default=None, description="1..24, необязательно")
    language: Optional[str] = Field(default=None, description="русский | казахский | английский, необязательно")
    wishes: Optional[str] = Field(default=None, description="свободный текст, до 500 символов (только в теле, не в URL)")
    lang: str = Field(default="ru", description="язык текстов ответа: ru | kk | en")

    def to_request(self) -> SearchRequest:
        return SearchRequest(
            city=self.city.strip(), date=self.date.strip(), event_type=self.event_type.strip(),
            category=self.category.strip(), budget_kzt=self.budget_kzt, duration_h=self.duration_h,
            language=(self.language or "").strip() or None,
            wishes=(self.wishes or "").strip()[:500] or None,
            lang=self.lang if self.lang in SUPPORTED else "ru",
        )


@router.get("/healthz", tags=["service"])
def healthz(request: Request) -> dict:
    return {"status": "ok", "profiles": len(request.app.state.catalog.contractors)}


@router.get("/api/meta", tags=["catalog"])
def meta(request: Request) -> dict:
    return request.app.state.catalog.meta()


@router.post("/api/recommend", tags=["matching"])
def api_recommend(body: RecommendIn, request: Request) -> dict:
    """До 3 карточек с объяснениями + статус, причины отсева, воронка. Бизнес-ошибки → 200 и status=invalid_request."""
    started = time.perf_counter()
    req = body.to_request()
    resp = recommend(request.app.state.catalog, req, lambda k, **kw: translate(req.lang, k, **kw))
    data = resp.to_dict()
    data["meta"]["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)   # только здесь: движок чистый
    return data
