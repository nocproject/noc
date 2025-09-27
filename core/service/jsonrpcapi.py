# ----------------------------------------------------------------------
# JSON-RPC API object
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from collections import namedtuple
from typing import Optional, Set

# Third-party modules
from fastapi import APIRouter, Header, Depends
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.aaa.models.user import User
from noc.core.service.deps.user import get_current_user
from noc.config import config
from noc.core.debug import error_report
from noc.core.error import NOCError
from noc.core.service.loader import get_service
from noc.core.service.models.jsonrpc import JSONRemoteProcedureCall, JSONRPCResponse
from noc.core.span import Span


Redirect = namedtuple("Redirect", ["location", "method", "params"])


class JSONRPCAPI(object):
    """
    JSON-RPC (specification 2.0) API implementation for FastAPI service
    https://www.jsonrpc.org/specification
    """

    CALLING_SERVICE_HEADER = "X-NOC-Calling-Service"

    # API name for OpenAPI docs
    api_name = None
    # API description for OpenAPI docs
    api_description = None
    # Tags for OpenAPI docs
    openapi_tags = []
    # url-path for API endpoint (without closing /), e.g. /api/service_name
    url_path = None
    # Indicates whether the REMOTE-HTTP header is required in the request
    auth_required = False

    def __init__(self, router: APIRouter):
        self.service = get_service()
        self.logger = self.service.logger
        self.current_user: Optional[User] = None
        self.router = router
        self.methods: Set[str] = self.get_methods()
        self.setup_routes()

    @classmethod
    def get_methods(cls) -> Set[str]:
        """
        Returns a list of available API methods
        """
        return {m for m in dir(cls) if getattr(getattr(cls, m), "api", False)}

    async def api_endpoint(
        self,
        req: JSONRemoteProcedureCall,
        remote_user: Optional[User] = Depends(get_current_user),
        span_ctx: int = Header(0, alias="X-NOC-Span-Ctx"),
        span_id: int = Header(0, alias="X-NOC-Span"),
        calling_service: str = Header("unknown", alias=CALLING_SERVICE_HEADER),
    ):
        """
        Endpoint for FastAPI route.
        Execute selected API-method as method of JSONRPAPI child class instance
        """

        self.current_user = remote_user
        if req.method not in self.methods:
            return ORJSONResponse(
                content={
                    "error": {"message": f"Method not found: '{req.method}'", "code": -32601},
                    "id": req.id,
                }
            )
        h = getattr(self, req.method)
        self.service.logger.debug(
            "[RPC call from %s] %s.%s(%s)", calling_service, self.api_name, req.method, req.params
        )
        in_label = None
        if config.features.forensic:
            lh = getattr(self, f"{req.method}_get_label", None)
            if lh:
                in_label = lh(*req.params)
        sample = 1 if span_ctx and span_id else 0
        with Span(
            server=self.service.name,
            service=f"api.{req.method}",
            sample=sample,
            parent=span_id,
            context=span_ctx,
            in_label=in_label,
        ) as span:
            try:
                if getattr(h, "executor", ""):
                    # Threadpool version
                    result = await self.service.run_in_executor(h.executor, h, *req.params)
                else:
                    # Serialized version
                    result = h(*req.params)
                if asyncio.isfuture(result) or asyncio.iscoroutine(result):
                    result = await result
                if isinstance(result, Redirect):
                    # Redirect protocol extension
                    return ORJSONResponse(
                        content={"method": result.method, "params": result.params, "id": req.id},
                        status_code=307,
                        headers={"location": result.location},
                    )
                return ORJSONResponse(content={"result": result, "id": req.id})
            except NOCError as e:
                span.set_error_from_exc(e, e.code)
                return ORJSONResponse(
                    content={"error": {"message": f"Failed: {e}", "code": e.code}, "id": req.id}
                )
            except Exception as e:
                error_report()
                span.set_error_from_exc(e)
                return ORJSONResponse(
                    content={"error": {"message": f"Failed: {e}", "code": -32000}, "id": req.id}
                )

    def redirect(self, location, method, params):
        return Redirect(location=location, method=method, params=params)

    def setup_routes(self):
        """
        Setup FastAPI router by adding routes
        """
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


def api(method):
    """
    API method decorator
    """
    method.api = True
    return method


def executor(name):
    """
    Denote API methods as been executed on threadpool executor

    @executor("script")
    @api
    def script(....)
    """

    def wrap(f):
        f.executor = name
        return f

    return wrap


class APIError(NOCError):
    pass
