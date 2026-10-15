"""Logging in and out of the admin console."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app import accounts
from app.web import templates, verify_csrf

router = APIRouter()

# The same message for a wrong password, an unknown email and a deactivated
# account, so the response never reveals which emails have accounts.
LOGIN_ERROR = "Incorrect email or password."


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "admin/login.html",
                                      {"title": "Log in", "email": ""})


@router.post("/login", dependencies=[Depends(verify_csrf)])
def login(request: Request, email: str = Form(""), password: str = Form("")):
    account = accounts.authenticate(request.app.state.db_path, email, password)
    if account is None:
        return templates.TemplateResponse(
            request, "admin/login.html",
            {"title": "Log in", "email": email, "error": LOGIN_ERROR},
            status_code=401,
        )
    # A fresh session on login, so a session id or CSRF token planted before
    # login is worthless afterwards.
    request.session.clear()
    request.session["account_id"] = account.id
    return RedirectResponse("/admin", status_code=303)


@router.post("/logout", dependencies=[Depends(verify_csrf)])
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
