# ----------------------------------------------------------------------
# NBI API Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Optional

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.core.service.loader import get_service


API_ACCESS_HEADER = "X-NOC-API-Access"

FORBIDDEN_MESSAGE = "<html><title>403: Forbidden</title><body>403: Forbidden</body></html>"


class NBIAPI(object):
    """
    NBI API Base Class
    """

    # API name
    api_name: Optional[str] = None
    # Tags for OpenAPI documentation
    openapi_tags: List[str] = []

    def __init__(self, router: APIRouter):
        self.service = get_service()
        self.logger = self.service.logger
        self.router = router
        self.setup_routes()

    @classmethod
    def access_tokens_set(cls):
        return {"nbi:*", f"nbi:{cls.api_name}"}

    @classmethod
    def access_granted(cls, access_header):
        """
        Checks that each access_header contains at least one required token
        """
        a_set = set(access_header.split(","))
        if cls.access_tokens_set() & a_set:
            return True
        return False

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
