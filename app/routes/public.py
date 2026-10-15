"""A preview of the public site at /, for whoever is at the team laptop.

The pages come from the same code that writes site/ (app/publish.py), so the
Coach sees exactly what readers will see once the site update has run. No
login is needed, and drafts are never served: an unknown or draft slug is 404.
Only this preview links to the console; the files in site/ never do.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from app import publish
from app.content import Kind

router = APIRouter()


@router.get("/")
@router.get("/index.html")
def public_home(request: Request):
    db_path = request.app.state.db_path
    return HTMLResponse(publish.home_html(
        publish.published(db_path, Kind.PAGE),
        publish.published(db_path, Kind.POST), preview=True))


@router.get("/posts/{slug}.html")
def public_post(request: Request, slug: str):
    return _public_item(request, Kind.POST, slug)


@router.get("/pages/{slug}.html")
def public_page(request: Request, slug: str):
    return _public_item(request, Kind.PAGE, slug)


def _public_item(request: Request, kind: Kind, slug: str) -> HTMLResponse:
    db_path = request.app.state.db_path
    pages = publish.published(db_path, Kind.PAGE)
    items = pages if kind is Kind.PAGE else publish.published(db_path, kind)
    for item in items:
        if item.slug == slug:
            return HTMLResponse(publish.item_html(item, pages, preview=True))
    raise HTTPException(status_code=404, detail=f"No such published {kind}.")


@router.get("/style.css")
def public_css():
    return Response(publish.CSS, media_type="text/css")
