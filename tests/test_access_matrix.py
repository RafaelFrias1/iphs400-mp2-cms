"""Access matrix: every admin-only route refuses editors and anonymous clients
(SECURITY-CHECKLIST rows 4, 5 and 10).

The routes are not listed by hand. They are collected from create_app() by
looking for `require_admin` in each route's dependency tree, so a new
admin-only route is covered the moment it exists, and a route that loses its
guard drops out of the matrix (test_matrix_covers_the_known_admin_routes
catches that).
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import fastapi.routing
import pytest
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app import accounts, content
from app.content import Kind
from app.main import create_app
from app.seed import DEMO_EMAILS, seed_demo_content
from app.web import require_admin

# The 403 body require_admin sends. Other guards (such as content.can_change on
# /admin/pages/{item_id}) also answer editors with 403, so the message is what
# proves the refusal came from require_admin.
ADMIN_ONLY = {"detail": "Only admins can do that."}


def _needs_admin(dependant: Dependant) -> bool:
    return any(dep.call is require_admin or _needs_admin(dep)
               for dep in dependant.dependencies)


def _flat_routes(app):
    # FastAPI 0.141 keeps included routers nested in app.routes;
    # iter_route_contexts flattens them (with router-level dependencies merged),
    # as FastAPI's own OpenAPI generator does. Older versions are already flat.
    iter_route_contexts = getattr(fastapi.routing, "iter_route_contexts", None)
    if iter_route_contexts is None:
        return [(route, route) for route in app.routes]
    return [(context.original_route, context)
            for context in iter_route_contexts(app.routes)]


def _admin_routes() -> list[tuple[str, str]]:
    with tempfile.TemporaryDirectory() as tmp:
        app = create_app(db_path=Path(tmp) / "routes.db", site_dir=Path(tmp) / "site")
    return sorted((method, route.path_format)
                  for original, route in _flat_routes(app)
                  if isinstance(original, APIRoute) and _needs_admin(route.dependant)
                  for method in route.methods)


# Built at import time because parametrize needs the list during collection.
# The app only lists its routes; no request reaches it, so no deployer is needed.
ADMIN_ROUTES = _admin_routes()


class _PathParams(dict):
    """Path parameter values; a parameter not named here gets a seeded page's
    id, so a new admin-only route with its own parameter is still requested."""

    def __missing__(self, name: str) -> int:
        return self["item_id"]


@pytest.fixture
def path_params(db_path):
    """Seed the demo content; return the values that fill the path parameters."""
    seed_demo_content(db_path)
    return _PathParams(
        item_id=content.list_items(db_path, Kind.PAGE)[0].id,
        account_id=accounts.find_by_email(db_path, DEMO_EMAILS["editor"]).id)


def _request(c, method: str, path: str, csrf_token: str):
    """Send the request; every state-changing method carries the CSRF token."""
    data = None if method == "GET" else {"csrf_token": csrf_token}
    return c.request(method, path, data=data, follow_redirects=False)


def test_matrix_covers_the_known_admin_routes():
    for known in [("GET", "/admin/accounts"), ("POST", "/admin/accounts/{account_id}/role"),
                  ("GET", "/admin/settings"), ("POST", "/admin/pages/{item_id}")]:
        assert known in ADMIN_ROUTES


@pytest.mark.parametrize(("method", "path"), ADMIN_ROUTES)
def test_editor_is_refused(method, path, path_params, client_as, csrf):
    editor = client_as("editor")
    response = _request(editor, method, path.format_map(path_params), csrf(editor, "/admin"))
    assert response.status_code == 403, (
        f"Editor got {response.status_code} on {method} {path}")
    assert response.json() == ADMIN_ONLY


@pytest.mark.parametrize(("method", "path"), ADMIN_ROUTES)
def test_anonymous_is_sent_to_login(method, path, path_params, client, csrf):
    response = _request(client, method, path.format_map(path_params), csrf(client, "/login"))
    assert response.status_code in (302, 303, 307), (
        f"Anonymous got {response.status_code} on {method} {path}")
    assert urlsplit(response.headers["location"]).path == "/login"
