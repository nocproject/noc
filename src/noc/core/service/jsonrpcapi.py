# ----------------------------------------------------------------------
# JSON-RPC API object
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from collections import namedtuple
from typing import Any, ClassVar

# Third-party modules
from fastapi import APIRouter, Header, Depends
from fastapi.responses import JSONResponse
import orjson

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


class NOCJSONRPCResponse(JSONResponse):
    """JSON response implementation used by NOC's JSON-RPC APIs.

    JSON-RPC methods may return values such as dataclass instances, including
    nested dataclasses, that the standard-library JSON encoder cannot encode.
    FastAPI's ``ORJSONResponse`` used to handle these values, but it is
    deprecated in favor of response-model serialization. JSON-RPC endpoints
    return a response object directly, so FastAPI's response-model serializer
    does not process the response content.

    This response keeps the ``JSONResponse`` interface while encoding its
    content with :func:`orjson.dumps`. The resulting bytes are used directly as
    the HTTP response body, with the ``application/json`` media type provided
    by the parent class.

    The content must be supported by ``orjson`` and the options enabled below.
    Dataclasses and their nested values are supported by the version of
    ``orjson`` used by NOC. NumPy values and non-string dictionary keys retain
    the behavior of FastAPI's former ``ORJSONResponse`` implementation.
    """

    def render(self, content: Any) -> bytes:
        """Serialize response content to UTF-8 JSON bytes with ``orjson``.

        Starlette calls this method while constructing the response. Returning
        the bytes from ``orjson.dumps`` avoids an intermediate JSON string or
        an extra encoding pass.

        Args:
            content: The JSON-RPC response envelope to serialize.

        Returns:
            The compact UTF-8 encoded JSON response body.

        Raises:
            orjson.JSONEncodeError: If the content contains a value that
                ``orjson`` cannot serialize.
        """
        return orjson.dumps(
            content,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )


class JSONRPCAPI:
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
    # Response class used for all JSON-RPC response envelopes.
    Response: ClassVar[type[NOCJSONRPCResponse]] = NOCJSONRPCResponse

    def __init__(self, router: APIRouter) -> None:
        self.service = get_service()
        self.logger = self.service.logger
        self.current_user: User | None = None
        self.router = router
        self.methods: set[str] = self.get_methods()
        self.setup_routes()

    @classmethod
    def get_methods(cls) -> set[str]:
        """
        Returns a list of available API methods
        """
        return {m for m in dir(cls) if getattr(getattr(cls, m), "api", False)}

    async def api_endpoint(
        self,
        req: JSONRemoteProcedureCall,
        remote_user: User | None = Depends(get_current_user),
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
            return self.Response(
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
                    return self.Response(
                        content={"method": result.method, "params": result.params, "id": req.id},
                        status_code=307,
                        headers={"location": result.location},
                    )
                return self.Response(content={"result": result, "id": req.id})
            except NOCError as e:
                span.set_error_from_exc(e, e.code)
                return self.Response(
                    content={"error": {"message": f"Failed: {e}", "code": e.code}, "id": req.id}
                )
            except Exception as e:
                error_report()
                span.set_error_from_exc(e)
                return self.Response(
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
