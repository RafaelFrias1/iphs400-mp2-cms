"""The FastAPI application.

The admin console lives under /admin and needs a login (/login); the public
site answers at /. Routes live in their own modules under app/routes/ and are
included here. Keep this file small.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app import db, publish, settings
from app.routes import accounts, auth, console, posts
from app.web import LoginRequired


def create_app(db_path: Path | None = None,
               site_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="IPHS 400 MP2 CMS")
    app.state.db_path = db_path or settings.DATABASE_PATH
    # Where site updates write; tests pass a temporary directory.
    app.state.site_dir = site_dir or settings.SITE
    db.init(app.state.db_path)

    # Signed session cookie that ends when the browser closes (shared laptop).
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY,
                       session_cookie="cms_session", max_age=None,
                       same_site="lax")

    @app.exception_handler(LoginRequired)
    def to_login(request: Request, exc: LoginRequired):
        return RedirectResponse("/login", status_code=303)

    @app.get("/")
    def public_home():
        # The real public site is site/ (`cms publish`); this is a placeholder.
        return HTMLResponse(publish.environment().get_template(
            "public/home.html").render(title=settings.SITE_TITLE, posts=[]))

    app.include_router(auth.router)
    app.include_router(console.router)
    app.include_router(accounts.router)
    app.include_router(posts.router)
    return app


app = create_app()
