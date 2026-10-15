"""The FastAPI application.

The admin console lives under /admin and needs a login (/login); the public
site answers at /. Routes live in their own modules under app/routes/ and are
included here. Keep this file small.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app import db, settings
from app.routes import auth, console
from app.web import LoginRequired, templates


def create_app(db_path: Path | None = None) -> FastAPI:
    app = FastAPI(title="IPHS 400 MP2 CMS")
    app.state.db_path = db_path or settings.DATABASE_PATH
    db.init(app.state.db_path)

    # Signed session cookie that ends when the browser closes (shared laptop).
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY,
                       session_cookie="cms_session", max_age=None,
                       same_site="lax")

    @app.exception_handler(LoginRequired)
    def to_login(request: Request, exc: LoginRequired):
        return RedirectResponse("/login", status_code=303)

    @app.get("/")
    def public_home(request: Request):
        return templates.TemplateResponse(
            request, "public/home.html",
            {"title": settings.SITE_TITLE, "items": []},
        )

    app.include_router(auth.router)
    app.include_router(console.router)
    return app


app = create_app()
