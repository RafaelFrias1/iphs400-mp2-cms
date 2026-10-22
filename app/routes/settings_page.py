"""The Settings page: admin only. Editors get 403 on every route here.

The Coach chooses the site-wide options, starting with the theme. Saving a
theme is a site update (ADR-004): the public site is rebuilt in the new
theme and deployed, and if the deploy fails the choice is not saved.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app import publish, theme
from app.accounts import Account
from app.web import require_admin, templates, verify_csrf

router = APIRouter(prefix="/admin/settings", dependencies=[Depends(require_admin)])

SAVED = "Theme saved and the website updated."


def _page(request: Request, me: Account, *, chosen: str | None = None,
          error: str = "", saved: str = "", status_code: int = 200):
    db_path = request.app.state.db_path
    return templates.TemplateResponse(
        request, "admin/settings.html",
        {"title": "Settings", "account": me, "themes": theme.available(),
         "chosen": chosen or theme.selected(db_path),
         "error": error, "saved": saved},
        status_code=status_code,
    )


@router.get("")
def settings_page(request: Request, me: Account = Depends(require_admin)):
    return _page(request, me, saved=request.session.pop("settings_saved", ""))


@router.post("", dependencies=[Depends(verify_csrf)])
def save_settings(request: Request, me: Account = Depends(require_admin),
                  name: str = Form("", alias="theme")):
    if name not in theme.available():
        return _page(request, me, error="Choose one of the themes.",
                     status_code=400)
    state = request.app.state
    try:
        publish.update_site(state.db_path, state.site_dir, state.deployer,
                            lambda conn: theme.set_theme(conn, name))
    except publish.SiteUpdateFailed:
        return _page(request, me, chosen=name, error=publish.OFFLINE,
                     status_code=503)
    request.session["settings_saved"] = SAVED
    return RedirectResponse("/admin/settings", status_code=303)
