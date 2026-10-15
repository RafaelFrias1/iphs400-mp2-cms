"""A preview of the public site at /, for whoever is at the team laptop.

The pages come from the same code that writes site/ (app/publish.py), so the
Coach sees exactly what readers will see once the site update has run. No
login is needed, and drafts are never served: an unknown or draft slug is 404.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from app import publish

router = APIRouter()


@router.get("/")
@router.get("/index.html")
def public_home(request: Request):
    return HTMLResponse(publish.home_html(
        publish.published_posts(request.app.state.db_path)))


@router.get("/posts/{slug}.html")
def public_post(request: Request, slug: str):
    for post in publish.published_posts(request.app.state.db_path):
        if post.slug == slug:
            return HTMLResponse(publish.post_html(post))
    raise HTTPException(status_code=404, detail="No such published post.")


@router.get("/style.css")
def public_css():
    return Response(publish.CSS, media_type="text/css")
