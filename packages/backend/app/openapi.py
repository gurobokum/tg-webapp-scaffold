from typing import Any, Callable

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from app.conf import settings


def configure_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="TG WebApp scaffold",
        version=settings.VERSION,
        summary="TG WebApp scaffold",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    if settings.ENV == "prod":
        app.openapi_url = ""
        app.redoc_url = ""

    return app.openapi_schema


def generate_unique_id_function(
    prefix: str | int | None = None,
) -> Callable[[APIRoute], str]:
    def _generate_unique_id_function(route: APIRoute) -> str:
        if not prefix:
            return route.name
        return f"{str(prefix)}::{route.name}"

    return _generate_unique_id_function
