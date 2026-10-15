"""The admin console. Every route on this router requires a logged-in account."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.accounts import Account
from app.web import current_account, templates

router = APIRouter(prefix="/admin", dependencies=[Depends(current_account)])


@router.get("")
def admin_home(request: Request, account: Account = Depends(current_account)):
    return templates.TemplateResponse(
        request, "admin/hello.html", {"title": "Admin", "account": account}
    )
