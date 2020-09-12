# ----------------------------------------------------------------------
# Service API handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple
import asyncio

# Third-party modules
import tornado.web
import tornado.gen
import orjson

# NOC modules
from noc.core.error import NOCError
from noc.core.debug import error_report
from noc.core.span import Span
from noc.config import config


Redirect = namedtuple("Redirect", ["location", "method", "params"])


class APIRequestHandler(tornado.web.RequestHandler):
    """
    HTTP JSON-RPC request handler
    """

    SUPPORTED_METHODS = ("POST",)
    CALLING_SERVICE_HEADER = "X-NOC-Calling-Service"

    def initialize(self, service, api_class):
        self.service = service
        self.api_class = api_class

    async def post(self, *args, **kwargs):
        span_ctx = self.request.headers.get("X-NOC-Span-Ctx", 0)
        span_id = self.request.headers.get("X-NOC-Span", 0)
        sample = 1 if span_ctx and span_id else 0
        # Parse JSON
        try:
            req = orjson.loads(self.request.body)
        except ValueError as e:
            self.api_error(e)
            return
        # Parse request
        id = req.get("id")
        params = req.get("params", [])
        method = req.get("method")
        if not method or not hasattr(self.api_class, method):
            self.api_error("Invalid method: '%s'" % method, id=id)
            return
        api = self.api_class(self.service, self.request, self)
        h = getattr(api, method)
        if not getattr(h, "api", False):
            self.api_error("Method is not callable: '%s'" % method, id=id)
            return
        calling_service = self.request.headers.get(self.CALLING_SERVICE_HEADER, "unknown")
        self.service.logger.debug(
            "[RPC call from %s] %s.%s(%s)", calling_service, api.name, method, params
        )
        in_label = None
        if config.features.forensic:
            lh = getattr(api, "%s_get_label" % method, None)
            if lh:
                in_label = lh(*params)
        with Span(
            server=self.service.name,
            service="api.%s" % method,
            sample=sample,
            parent=span_id,
            context=span_ctx,
            in_label=in_label,
        ) as span:
            try:
                if getattr(h, "executor", ""):
                    # Threadpool version
                    result = await self.service.run_in_executor(h.executor, h, *params)
                else:
                    # Serialized version
                    result = h(*params)
                if tornado.gen.is_future(result):
                    # @todo: Deprecated
                    result = await result
                elif asyncio.isfuture(result) or asyncio.iscoroutine(result):
                    result = await result
                if isinstance(result, Redirect):
                    # Redirect protocol extension
                    self.set_status(307, "Redirect")
                    self.set_header("Location", result.location)
                    self.write(
                        orjson.dumps({"id": id, "method": result.method, "params": result.params})
                    )
                else:
                    # Dump output
                    self.write(orjson.dumps({"id": id, "error": None, "result": result}))
            except NOCError as e:
                span.set_error_from_exc(e, e.code)
                self.api_error("Failed: %s" % e, id=id, code=e.code)
            except Exception as e:
                error_report()
                span.set_error_from_exc(e)
                self.api_error("Failed: %s" % e, id=id)

    def api_error(self, msg, id=None, code=None):
        if id is not None:
            rsp = {"error": str(msg)}
            if id:
                rsp["id"] = id
            if code:
                rsp["code"] = code
            self.write(orjson.dumps(rsp))


class API(object):
    """
    Service API declares a set of functions accessible
    via HTTP JSON-RPC.

    API methods are denoted by @api decorator

    Service registers SRV records
    <name> for non-pooled
    <name>-<pool> for pooled
    """

    # API name
    name = None

    def __init__(self, service, request, handler):
        self.service = service
        self.logger = service.logger
        self.request = request
        self.handler = handler

    @classmethod
    def get_methods(cls):
        """
        Returns a list of available API methods
        """
        return [m for m in dir(cls) if getattr(getattr(cls, m), "api", False)]

    def redirect(self, location, method, params):
        return Redirect(location=location, method=method, params=params)


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


class lock(object):
    """
    Decorator to lock api method call with named lock
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, method):
        method.lock = self.name
        return method


class APIError(NOCError):
    pass
