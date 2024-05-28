# ----------------------------------------------------------------------
# FastAPIService
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from typing import Optional, Tuple, Dict

# Third-party modules
import uvicorn
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.responses import Response, JSONResponse
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.wsgi import WSGIMiddleware

# NOC modules
from noc.core.version import version
from noc.core.log import PrefixLoggerAdapter
from noc.core.debug import error_report
from .base import BaseService
from .paths.loader import loader, ServicePathLoader
from .middleware.logging import LoggingMiddleware
from .middleware.span import SpanMiddleware


class FastAPIService(BaseService):
    BASE_OPENAPI_TAGS_DOCS = {
        "internal": "NOC internal API, including healthchecks, monitoring and tooling",
        "JSON-RPC API": "Implemented by JSON-RPC specification 1.0",
    }
    # Additional OpenAPI tags docs, tag -> description
    OPENAPI_TAGS_DOCS: Dict[str, str] = {}

    def __init__(self):
        super().__init__()
        self.app = None
        # WSGI application of any third-party framework that will be attached to the main
        # FastAPI application. For attaching Django applications of web-service in particular
        self.wsgi_app = None
        # Collect 'api_requests' metric for API calls
        self.collect_req_api_metric = False

    async def error_handler(self, request: "Request", exc) -> Response:
        """
        Error handler for ServerErrorMiddleware
        :return:
        """
        error_report(logger=self.logger)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "error_description": f"Internal Server Error: {exc}",
                "error_uri": str(request.url),
            },
        )

    async def http_error_handler(self, request: "Request", exc: "HTTPException") -> Response:
        """
        Error handler for HTTPException
        :return:
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "invalid_request",
                "error_description": f"{exc.detail}",
                "error_uri": str(request.url),
            },
        )

    async def request_validation_error_handler(self, request: "Request", exc) -> Response:
        """
        Handle request validation and customize response
        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_request",
                "error_description": jsonable_encoder(exc.errors()),
                "error_uri": str(request.url),
            },
        )

    async def init_api(self):
        # Build tags docs
        openapi_tags = []
        for tag in self.BASE_OPENAPI_TAGS_DOCS:
            openapi_tags += [{"name": tag, "description": self.BASE_OPENAPI_TAGS_DOCS[tag]}]
        if self.OPENAPI_TAGS_DOCS:
            for tag in self.OPENAPI_TAGS_DOCS:
                openapi_tags += [{"name": tag, "description": self.OPENAPI_TAGS_DOCS[tag]}]
        # Build FastAPI app
        self.app = FastAPI(
            title=f"NOC '{self.name or 'unknown'}' Service API",
            version=version.version,
            openapi_url=f"/api/{self.name}/openapi.json",
            docs_url=f"/api/{self.name}/docs",
            redoc_url=f"/api/{self.name}/redoc",
            openapi_tags=openapi_tags,
            exception_handlers={
                Exception: self.error_handler,
                HTTPException: self.http_error_handler,
                RequestValidationError: self.request_validation_error_handler,
            },
        )
        self.app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
        self.app.add_middleware(
            LoggingMiddleware,
            logger=PrefixLoggerAdapter(self.logger, "api"),
            is_wsgi_app=bool(self.wsgi_app),
            collect_req_api_metric=self.collect_req_api_metric,
        )
        self.app.add_middleware(SpanMiddleware, service_name=self.name)
        self.server: Optional[uvicorn.Server] = None
        # Initialize routers
        for path in loader.iter_classes():
            self.app.include_router(loader.get_class(path))
        service_paths = ("services", self.name, "paths")
        if os.path.exists(os.path.join(*service_paths)):
            extra_loader = ServicePathLoader()
            extra_loader.base_path = service_paths
            for path in extra_loader.iter_classes():
                kls = extra_loader.get_class(path)
                if kls:
                    self.app.include_router(kls)
        # Attaching third-party WSGI application
        if self.wsgi_app:
            self.app.mount("/", WSGIMiddleware(self.wsgi_app))
        # Get address and port to bind
        addr, port = self.get_service_address()
        # Initialize uvicorn server
        # Reproduce Service.run/.serve method
        uvi_config = uvicorn.Config(
            self.app, host=addr, port=port, lifespan="on", access_log=False, loop="none"
        )
        self.server = uvicorn.Server(config=uvi_config)
        uvi_config.setup_event_loop()
        uvi_config.load()
        self.server.lifespan = uvi_config.lifespan_class(uvi_config)
        await self.server.startup()
        # Get effective listen socket port
        self.address, self.port = self.get_effective_address()
        self.logger.info("Running HTTP APIs at http://%s:%s/", self.address, self.port)
        self.logger.info(
            "Running HTTP APIs Docs at http://%s:%s/api/%s/docs", self.address, self.port, self.name
        )
        self.loop.create_task(self.server.main_loop())

    async def shutdown_api(self):
        self.logger.info("Shutdown FAST API")
        if self.watchdog_waiter:
            self.server.force_exit = True
        await self.server.shutdown()

    def get_effective_address(self) -> Tuple[str, int]:
        for srv in self.server.servers:
            for sock in srv.sockets:
                return sock.getsockname()
