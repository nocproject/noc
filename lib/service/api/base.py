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


class ServiceAPIRequestHandler(tornado.web.RequestHandler):
    """
    HTTP JSON-RPC request handler
    """
    SUPPORTED_METHODS = ("POST",)

    def initialize(self, service, api_class):
        self.service = service
        self.api = api_class(service)

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
        if not method or not hasattr(self.api, method):
            return self.api_error(
                "Invalid method: '%s'" % method,
                id=id
            )
        h = getattr(self.api, method)
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

    def api_error(self, msg, id=None):
        rsp = {
            "error": str(msg)
        }
        if id:
            rsp["id"] = id
        self.write(json.dumps(rsp))


class ServiceSubscriber(object):
    def __init__(self, service, api_class):
        self.service = service
        self.api_class = api_class

    def get_topic(self):
        return self.api_class.get_service_topic(
            name=self.service.name,
            pool=self.service.config.pool,
            dc=self.service.config.dc,
            node=self.service.config.node
        )

    def on_message(self, message):
        # Parse JSON
        try:
            req = json.loads(message.body)
        except ValueError, why:
            return self.api_error(message, why)
        # Parse request
        id = req.get("id", "0")
        params = req.get("params", [])
        method = req.get("method")
        if not method or not hasattr(self.api_class, method):
            return self.api_error(
                "Invalid method: '%s'" % method,
                id=id
            )
        api = self.api_class(self.service)
        h = getattr(api, method)
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
        # self.write(json.dumps({
        #     "id": id,
        #     "error": None,
        #     "result": result
        # }))
        return True

    def api_error(self, msg, id=None):
        rsp = {
            "error": str(msg)
        }
        if id:
            rsp["id"] = id
        self.write(json.dumps(rsp))


class ServiceAPI(object):
    """
    Service API declares a set of functions accessible
    via HTTP and NSQ JSON-RPC.

    API methods are denoted by @api decorator
    """
    # Name and version of the service
    # RPC URL will be /v<verson>/<name>/
    name = "test"
    version = 1
    # Tornado JSON-RPC request handler
    http_request_handler = ServiceAPIRequestHandler
    # API LEVEL Constants
    # Do not register and advertise
    AL_NONE = 0
    # Advertise at global level
    AL_GLOBAL = 1
    # Advertise at pool level
    AL_POOL = 2
    # Advertise at node level
    AL_NODE = 3
    # Advertise at service level
    AL_SERVICE = 4
    # API level
    level = AL_NONE

    def __init__(self, service):
        self.service = service

    @classmethod
    def get_service_url(cls):
        return r"/v%s/%s/" % (cls.version, cls.name)

    @classmethod
    def get_service_topic(cls, name=None, pool=None, dc=None, node=None):
        if cls.level == cls.AL_GLOBAL:
            return "v%s-%s" % (cls.version, cls.name)
        elif cls.level == cls.AL_POOL:
            return "v%s-%s-%s" % (cls.version, cls.name, pool)
        elif cls.level == cls.AL_NODE:
            return "v%s-%s-%s-%s" % (cls.version, cls.name, dc, node)
        elif cls.level == cls.AL_SERVICE:
            return "v%s-%s-%s-%s-%s" % (cls.version, name, cls.name, dc, node)
        else:
            return None

    @classmethod
    def get_http_request_handler(cls):
        return cls.http_request_handler


def api(method):
    """
    API method decorator
    """
    method.api = True
    return method
