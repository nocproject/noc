# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service API handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
## Third-party modules
import tornado.web
## NOC modules
from noc.lib.debug import error_report


class APIRequestHandler(tornado.web.RequestHandler):
    """
    HTTP JSON-RPC request handler
    """
    SUPPORTED_METHODS = ("POST",)

    def initialize(self, service, api_class):
        self.service = service
        self.api_class = api_class

    def post(self, *args, **kwargs):
        # Parse JSON
        try:
            req = json.loads(self.request.body)
        except ValueError, why:
            return self.api_error(why)
        # Parse request
        id = req.get("id")
        params = req.get("params", [])
        method = req.get("method")
        if not method or not hasattr(self.api_class, method):
            return self.api_error(
                "Invalid method: '%s'" % method,
                id=id
            )
        api = self.api_class(self.service, self.request)
        h = getattr(api, method)
        if not getattr(h, "api", False):
            return self.api_error(
                "Method is not callable: '%s'" % method,
                id=id
            )
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
        self.service.logger.info(
            "[RPC] %s.%s(%s)",
            api.name, method, params
        )
        try:
            result = h(*params)
        except Exception, why:
            return self.api_error(
                "Failed: %s" % why,
                id=id
            )
        self.write(json.dumps({
            "id": id,
            "error": None,
            "result": result
        }))

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
        self.request = request


def api(method):
    """
    API method decorator
    """
    method.api = True
    return method


class lock(object):
    """
    Decorator to lock api method call with named lock
    """
    def __init__(self, name):
        self.name = name

    def __call__(self, method):
        method.lock = self.name
        return method
