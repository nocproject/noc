# ----------------------------------------------------------------------
# JSON-RPC API object
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter, Depends

# NOC modules
from noc.aaa.models.user import User
from noc.core.debug import error_report
from noc.core.error import NOCError
from noc.core.service.deps.user import get_current_user
from noc.core.service.loader import get_service
from noc.core.service.models.jsonrpc import JSONRemoteProcedureCall, JSONRPCResponse


class JSONRPCAPI(object):
    """JSON-RPC API implementation for FastAPI service.

    Implemented by JSON-RPC specification 1.0.

    """

    # API name for OpenAPI docs
    api_name = None
    # API description for OpenAPI docs
    api_description = None
    # Tags for OpenAPI docs
    openapi_tags = []
    # url-path for API endpoint (without closing /), e.g. /api/service_name
    url_path = None

    def __init__(self, router: APIRouter):
        self.service = get_service()
        self.logger = self.service.logger
        self.current_user = None
        self.router = router
        self.setup_routes()

    @classmethod
    def get_methods(cls):
        """Returns a list of available API methods."""

        return [m for m in dir(cls) if getattr(getattr(cls, m), "api", False)]

    def api_endpoint(
        self, req: JSONRemoteProcedureCall, current_user: User = Depends(get_current_user)
    ):
        """Endpoint for FastAPI route.

        Execute selected API-method as method of JSONRPAPI child class instance

        """

        if req.method not in self.get_methods():
            return {"error": f"Invalid method: '{req.method}'", "id": req.id}
        self.current_user = current_user
        api_method = getattr(self, req.method)
        result = None
        error = None
        try:
            result = api_method(*req.params)
        except NOCError as e:
            error = f"Failed: {e}"
        except Exception as e:
            error_report()
            error = f"Failed: {e}"
        return {"result": result, "error": error, "id": req.id}

    def setup_routes(self):
        """Setup FastAPI router by adding routes."""

        for path in (self.url_path, f"{self.url_path}/"):
            self.router.add_api_route(
                path=path,
                endpoint=self.api_endpoint,
                methods=["POST"],
                response_model=JSONRPCResponse,
                tags=self.openapi_tags,
                name=self.api_name,
                description=self.api_description,
            )
