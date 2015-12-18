# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service API handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
import functools
## Third-party modules
import tornado.web
import tornado.gen
## NOC modules
from noc.lib.debug import error_report


class APIRequestHandler(tornado.web.RequestHandler):
    """
    HTTP JSON-RPC request handler
    """
    SUPPORTED_METHODS = ("POST",)
    CALLING_SERVICE_HEADER = "X-NOC-Calling-Service"

    def initialize(self, service, api_class):
        self.service = service
        self.api_class = api_class

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        # Parse JSON
        try:
            req = json.loads(self.request.body)
        except ValueError, why:
            self.api_error(why)
            raise tornado.gen.Return()
        # Parse request
        id = req.get("id")
        params = req.get("params", [])
        method = req.get("method")
        if not method or not hasattr(self.api_class, method):
            self.api_error(
                "Invalid method: '%s'" % method,
                id=id
            )
            raise tornado.gen.Return()
        api = self.api_class(self.service, self.request)
        h = getattr(api, method)
        if not getattr(h, "api", False):
            self.api_error(
                "Method is not callable: '%s'" % method,
                id=id
            )
            raise tornado.gen.Return()
        # lock = getattr(h, "lock", None)
        # if lock:
        #     # Locked call
        #     try:
        #         lock_name = lock % self.service.config
        #         with self.service.lock(lock_name):
        #             result = h(*params)
        #     except Exception, why:
        #         return self.api_error(
        #             "Failed: %s" % why,
        #             id=id
        #         )
        # else:
        calling_service = self.request.headers.get(
            self.CALLING_SERVICE_HEADER,
            "unknown"
        )
        self.service.logger.info(
            "[RPC call from %s] %s.%s(%s)",
            calling_service, api.name, method, params
        )
        try:
            if getattr(h, "executor", ""):
                # Threadpool version
                executor = self.service.get_executor(h.executor)
                result = executor.submit(h, *params)
            else:
                # Serialized version
                result = h(*params)
            if tornado.gen.is_future(result):
                result = yield result
            self.write(json.dumps({
                "id": id,
                "error": None,
                "result": result
            }))
        except APIError, why:
            self.api_error(
                "Failed: %s" % why,
                id=id
            )
        except Exception, why:
            error_report()
            self.api_error(
                "Failed: %s" % why,
                id=id
            )

    def api_error(self, msg, id=None):
        if id is not None:
            rsp = {
                "error": str(msg)
            }
            if id:
                rsp["id"] = id
            self.write(json.dumps(rsp))


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

    def __init__(self, service, request):
        self.service = service
        self.logger = service.logger
        self.request = request


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


class APIError(Exception):
    pass
