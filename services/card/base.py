# ----------------------------------------------------------------------
# Base API Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import hashlib
from typing import List, Optional

# Third-party modules
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# NOC modules
from noc.config import config
from noc.core.comp import smart_bytes
from noc.core.service.loader import get_service

FORBIDDEN_MESSAGE = "<html><title>403: Forbidden</title><body>403: Forbidden</body></html>"


class BaseAPI(object):
    """
    Base API Class
    """

    # API name
    api_name: Optional[str] = None
    # Tags for OpenAPI documentation
    openapi_tags: List[str] = []

    hash = None
    PREFIX = os.getcwd()

    def __init__(self, router: APIRouter):
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
                response_class=route.get("response_class", ORJSONResponse),
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

    def hashed(self, url):
        """
        Convert path to path?hash version
        :param path:
        :return:
        """
        u = url
        if u.startswith("/"):
            u = url[1:]
        path = os.path.join(self.PREFIX, u)
        if not os.path.exists(path):
            return "%s?%s" % (url, "00000000")
        with open(path) as f:
            hash = hashlib.sha256(smart_bytes(f.read())).hexdigest()[:8]
        return "%s?%s" % (url, hash)
