# ----------------------------------------------------------------------
# Base API Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import hashlib
from pathlib import Path

# Third-party modules
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# NOC modules
from noc.config import config
from noc.core.service.loader import get_service

FORBIDDEN_MESSAGE = "<html><title>403: Forbidden</title><body>403: Forbidden</body></html>"


class BaseAPI:
    """
    Base API Class
    """

    # API name
    api_name: str | None = None
    # Tags for OpenAPI documentation
    openapi_tags: list[str] = []

    hash = None
    PREFIX = os.getcwd()

    def __init__(self, router: APIRouter) -> None:
        self.service = get_service()
        self.logger = self.service.logger
        self.router = router
        self.setup_routes()

    def get_routes(self):
        """
        Returns a list of available API methods
        """
        raise NotImplementedError

    def setup_routes(self):
        """
        Setup FastAPI router by adding routes
        """
        for route in self.get_routes():
            self.router.add_api_route(
                path=route["path"],
                methods=[route["method"]],  # ["POST"]
                endpoint=route["endpoint"],
                response_class=route.get("response_class", JSONResponse),
                response_model=route["response_model"],
                name=route["name"],
                description=route["description"],
                response_model_exclude_none=route.get("response_model_exclude_none", False),
                responses={
                    403: {
                        "content": {"text/html": {"example": FORBIDDEN_MESSAGE}},
                        "description": "Forbidden Access by API Key restrictions",
                    }
                },
                tags=self.openapi_tags,
            )
        self.router.add_api_route(
            path="/api/card/index.html",
            methods=["GET"],
            endpoint=self.handler_index,
            response_class=HTMLResponse,
            response_model=None,
            name="card-index",
            description="",
            response_model_exclude_none=False,
            responses={
                403: {
                    "content": {"text/html": {"example": FORBIDDEN_MESSAGE}},
                    "description": "Forbidden Access by API Key restrictions",
                }
            },
            tags=self.openapi_tags,
        )

    def handler_index(self, request: Request):
        templates_dir = os.path.join(self.PREFIX, "ui", self.service.name)
        language = config.card.language
        templates = Jinja2Templates(directory=templates_dir)
        result = templates.TemplateResponse(
            "index.html",
            {
                "hashed": self.hashed,
                "request": request,
                "language": language,
                "theme": config.web.theme,
                "brand": config.brand,
                "installation_name": config.installation_name,
                "name": self.service.name,
                "service": self.service,
            },
        )
        result.headers["Cache-Control"] = "no-cache; must-revalidate"
        result.headers["Expires"] = "0"
        return result

    def hashed(self, url: str) -> str:
        """Convert path to path?hash version."""
        u = url.lstrip("/")
        file_path = Path(self.PREFIX, u)
        hash_hex = "00000000"
        if file_path.is_file():
            hash_hex = hashlib.sha256(file_path.read_bytes()).hexdigest()[:8]
        return f"{url}?{hash_hex}"
