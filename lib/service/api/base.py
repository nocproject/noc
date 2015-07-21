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


class ServiceAPI(tornado.web.RequestHandler):
    """
    Service API declares a set of functions accessible
    via HTTP and NSQ JSON-RPC.

    API methods are denoted by @api decorator
    """
    SUPPORTED_METHODS = ("POST",)

    # Name and version of the service
    # RPC URL will be /v<verson>/<name>/
    name = "test"
    version = 1

    def post(self, *args, **kwargs):
        # Parse JSON
        try:
            req = json.loads(self.request.body)
        except ValueError, why:
            return self.api_error(why)
        # Parse request
        id = req.get("id", "0")
        params = req.get("params", [])
        method = req.get("method")
        if not method or not hasattr(self, method):
            return self.api_error(
                "Invalid method: '%s'" % method,
                id=id
            )
        h = getattr(self, method)
        if not hasattr(h, "api"):
            return self.api_error(
                "Method is not callable: '%s'" % method,
                id=id
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

    @classmethod
    def get_base_url(cls):
        return r"/v%s/%s/" % (cls.version, cls.name)

    def api_error(self, msg, id=None):
        rsp = {
            "error": str(msg)
        }
        if id:
            rsp["id"] = id
        self.write(json.dumps(rsp))


def api(method):
    """
    API method decorator
    """
    method.api = True
    return method
