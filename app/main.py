from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from matcher.data import load_catalog

from .config import settings
from .i18n import load_locales
from .routes import api, pages


def create_app() -> FastAPI:
    application = FastAPI(
        title="Tandau API",
        version="1.0.0",
        description="Подбор event-подрядчиков с объяснениями: до 3 карточек и честное «почему не больше».",
    )
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="tandau_session",
        max_age=7 * 24 * 3600,
        same_site="lax",
        https_only=False,
    )
    application.mount(
        "/static", StaticFiles(directory=str(settings.base_dir / "app" / "static")), name="static"
    )
    load_locales(settings.base_dir / "app" / "i18n")
    application.state.catalog = load_catalog(settings.data_path)
    application.include_router(pages.router)
    application.include_router(api.router)
    return application


app = create_app()
