# ----------------------------------------------------------------------
# Tornado-based API service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from typing import List

# Third-party modules
import tornado.web
import tornado.netutil
import tornado.httpserver

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from .base import BaseService
from .api import API, APIRequestHandler
from .doc import DocRequestHandler
from .mon import MonRequestHandler
from .metrics import MetricsHandler
from .health import HealthRequestHandler
from .ctl import CtlAPI


class TornadoService(BaseService):
    # List of API instances
    api: List[API] = []
    # Request handler class
    api_request_handler = APIRequestHandler

    def __init__(self):
        super().__init__()
        self.server = None

    async def init_api(self):
        """
        Initialize API routers and handlers
        :return:
        """
        handlers = [
            (r"^/mon/$", MonRequestHandler, {"service": self}),
            (r"^/metrics$", MetricsHandler, {"service": self}),
            (r"^/health/$", HealthRequestHandler, {"service": self}),
        ]
        api = [CtlAPI]
        if self.api:
            api += self.api
        addr, port = self.get_service_address()
        sdl = {}  # api -> [methods]
        # Collect and register exposed API
        for a in api:
            url = "^/api/%s/$" % a.name
            handlers += [(url, self.api_request_handler, {"service": self, "api_class": a})]
            # Populate sdl
            sdl[a.name] = a.get_methods()
        if self.api:
            handlers += [
                ("^/api/%s/doc/$" % self.name, DocRequestHandler, {"service": self}),
            ]
        handlers += self.get_handlers()
        app = tornado.web.Application(handlers, **self.get_app_settings())
        self.server = tornado.httpserver.HTTPServer(app, xheaders=True, no_keep_alive=True)
        self.server.listen(port, addr)
        # Get effective address and port from Tornado TCP server
        for f in self.server._sockets:
            sock = self.server._sockets[f]
            self.address, self.port = sock.getsockname()
            break
        #
        self.logger.info("Running HTTP APIs at http://%s:%s/", self.address, self.port)
        for a in api:
            self.logger.info(
                "Supported API: %s at http://%s:%s/api/%s/", a.name, self.address, self.port, a.name
            )

    async def shutdown_api(self):
        """
        Stop API services
        :return:
        """
        self.logger.info("Stopping API")
        self.server.stop()

    def get_handlers(self):
        """
        Returns a list of additional handlers
        """
        return []

    def get_app_settings(self):
        """
        Returns tornado application settings
        """
        return {
            "template_path": os.getcwd(),
            "cookie_secret": config.secret_key,
            "log_function": self.log_request,
        }

    def log_request(self, handler):
        """
        Custom HTTP Log request handler
        :param handler:
        :return:
        """
        status = handler.get_status()
        method = handler.request.method
        uri = handler.request.uri
        remote_ip = handler.request.remote_ip
        if status == 200 and uri == "/mon/" and method == "GET":
            self.logger.debug("Monitoring request (%s)", remote_ip)
            metrics["mon_requests"] += 1
        elif (status == 200 or status == 429) and uri.startswith("/health/") and method == "GET":
            pass
        elif status == 200 and uri == ("/metrics") and method == "GET":
            pass
        else:
            self.logger.info(
                "%s %s (%s) %.2fms", method, uri, remote_ip, 1000.0 * handler.request.request_time()
            )
            metrics["http_requests", ("method", method.lower())] += 1
            metrics["http_response", ("status", status)] += 1
