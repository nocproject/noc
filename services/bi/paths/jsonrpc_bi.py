# ----------------------------------------------------------------------
# BI JSON-RPC API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple

# Third-party modules
from fastapi import APIRouter, Depends

# NOC modules
from noc.aaa.models.user import User
from noc.core.debug import error_report
from noc.core.error import NOCError
from noc.core.service.deps.user import get_current_user
from noc.core.service.loader import get_service
from noc.core.service.models.jsonrpc import JSONRemoteProcedureCall, JSONRPCResponse
from noc.services.bi.api.bi import BIAPI

RequestHandler = namedtuple("RequestHandler", ["current_user"])

router = APIRouter()


class JSONRPCAPI(object):
    def __init__(self, router: APIRouter):
        self.router = router
        self.openapi_tags = ["JSON-RPC API"]
        self.api_name = "api_bi"
        self.api_description = "Service BI API"
        self.setup_routes()

    def api_bi(self, req: JSONRemoteProcedureCall, current_user: User = Depends(get_current_user)):
        if req.method not in BIAPI.get_methods():
            return {"error": f"Invalid method: '{req.method}'", "id": req.id}
        service = get_service()
        request_handler = RequestHandler(current_user)
        api = BIAPI(service, None, request_handler)
        api_method = getattr(api, req.method)
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
        for path in ("/api/bi/", "/api/bi"):
            self.router.add_api_route(
                path=path,
                endpoint=self.api_bi,
                methods=["POST"],
                response_model=JSONRPCResponse,
                tags=self.openapi_tags,
                name=self.api_name,
                description=self.api_description,
            )


# Install endpoints
JSONRPCAPI(router)
