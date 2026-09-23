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
