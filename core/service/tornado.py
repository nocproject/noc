# ----------------------------------------------------------------------
# Tornado-based API service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
import tornado.web
import tornado.netutil
import tornado.httpserver

# NOC modules
from .base import BaseService
from .api import API, APIRequestHandler
from .doc import DocRequestHandler
from .mon import MonRequestHandler
from .metrics import MetricsHandler
from .health import HealthRequestHandler
from .sdl import SDLRequestHandler
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
                ("^/api/%s/sdl.js" % self.name, SDLRequestHandler, {"sdl": sdl}),
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
