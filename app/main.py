"""The FastAPI application.

The admin console lives under /admin and needs a login (/login); a preview
of the public site answers at /. Routes live in their own modules under
app/routes/ and are included here. Keep this file small.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app import db, deploy, settings
from app.routes import accounts, auth, console, items, public
from app.web import LoginRequired


def create_app(db_path: Path | None = None,
               site_dir: Path | None = None,
               deployer: deploy.Deployer | None = None) -> FastAPI:
    app = FastAPI(title="IPHS 400 MP2 CMS")
    app.state.db_path = db_path or settings.DATABASE_PATH
    # Where site updates write; tests pass a temporary directory.
    app.state.site_dir = site_dir or settings.SITE
    # Sends each site update to the web host; tests pass a fake (ADR-004).
    app.state.deployer = deployer or (
        deploy.push_to_gh_pages if settings.DEPLOY else deploy.render_only)
    db.init(app.state.db_path)

    # Signed session cookie that ends when the browser closes (shared laptop).
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY,
                       session_cookie="cms_session", max_age=None,
                       same_site="lax")

    @app.exception_handler(LoginRequired)
    def to_login(request: Request, exc: LoginRequired):
        return RedirectResponse("/login", status_code=303)

    app.include_router(auth.router)
    app.include_router(console.router)
    app.include_router(accounts.router)
    app.include_router(items.posts_router)
    app.include_router(items.pages_router)
    app.include_router(public.router)
    return app


app = create_app()
