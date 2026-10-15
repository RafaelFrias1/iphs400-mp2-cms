"""Account management: admin only. Editors get 403 on every route here.

The Coach creates accounts, changes roles, and deactivates or reactivates
accounts. Accounts are never deleted, and nobody may deactivate or demote
their own account, so the site always keeps an admin.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import accounts
from app.accounts import MIN_PASSWORD_LENGTH, Account, Role
from app.web import require_admin, templates, verify_csrf

router = APIRouter(prefix="/admin/accounts", dependencies=[Depends(require_admin)])


def _page(request: Request, me: Account, *, error: str = "", email: str = "",
          role: str = Role.EDITOR, status_code: int = 200):
    return templates.TemplateResponse(
        request, "admin/accounts.html",
        {"title": "Accounts", "account": me, "roles": list(Role),
         "min_password_length": MIN_PASSWORD_LENGTH,
         "accounts": accounts.list_accounts(request.app.state.db_path),
         "error": error, "email": email, "role": role},
        status_code=status_code,
    )


def _back_to_list() -> RedirectResponse:
    return RedirectResponse("/admin/accounts", status_code=303)


def _target(request: Request, account_id: int) -> Account:
    target = accounts.get_account(request.app.state.db_path, account_id)
    if target is None:
        raise HTTPException(status_code=404, detail="No such account.")
    return target


@router.get("")
def accounts_page(request: Request, me: Account = Depends(require_admin)):
    return _page(request, me)


@router.post("", dependencies=[Depends(verify_csrf)])
def add_account(request: Request, me: Account = Depends(require_admin),
                email: str = Form(""), password: str = Form(""),
                role: str = Form("")):
    email = email.strip()
    error = ""
    if not email:
        error = "Enter an email."
    elif role not in Role:
        error = "Choose a role."
    elif len(password) < MIN_PASSWORD_LENGTH:
        error = f"The password must be at least {MIN_PASSWORD_LENGTH} characters."
    else:
        try:
            accounts.create_account(request.app.state.db_path, email, password,
                                    Role(role))
        except accounts.EmailTaken:
            error = f"{email} already has an account."
    if error:
        return _page(request, me, error=error, email=email, role=role,
                     status_code=400)
    return _back_to_list()


@router.post("/{account_id}/role", dependencies=[Depends(verify_csrf)])
def change_role(request: Request, account_id: int,
                me: Account = Depends(require_admin), role: str = Form("")):
    target = _target(request, account_id)
    if role not in Role:
        return _page(request, me, error="Choose a role.", status_code=400)
    if target.id == me.id:
        return _page(request, me, error="You can't change your own role.",
                     status_code=400)
    accounts.set_role(request.app.state.db_path, target.id, Role(role))
    return _back_to_list()


@router.post("/{account_id}/active", dependencies=[Depends(verify_csrf)])
def change_active(request: Request, account_id: int,
                  me: Account = Depends(require_admin), active: bool = Form()):
    target = _target(request, account_id)
    if target.id == me.id and not active:
        return _page(request, me, error="You can't deactivate your own account.",
                     status_code=400)
    accounts.set_active(request.app.state.db_path, target.id, active)
    return _back_to_list()
