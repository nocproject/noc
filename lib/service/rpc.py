# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC Wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import itertools
import uuid
import json
import logging
## Third-party modules
import tornado.concurrent
import tornado.gen
import tornado.httpclient
## NOC modules
from noc.lib.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class RPCError(Exception):
    pass


class RPCProxy(object):
    """
    API Proxy
    """
    def __init__(self, service, service_name):
        self._logger = PrefixLoggerAdapter(logger, service_name)
        self._service = service
        self._service_name = service_name
        self._api = service_name.split("-")[0]
        self._tid = itertools.count()
        self._transactions = {}
        self._methods = {}

    def __del__(self):
        self.close()

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            mw = self._methods.get(item)
            if not mw:
                mw = RPCMethod(self, item)
                self._methods[item] = mw
            return mw

    @tornado.gen.coroutine
    def _call(self, method, *args, **kwargs):
        tid = self._tid.next()
        msg = {
            "method": method,
            "params": list(args)
        }
        is_notify = "_notify" in kwargs
        if not is_notify:
            msg["id"] = tid
        services = self._service.resolve_service(
            self._service_name,
            n=1
        )
        if not services:
            raise RPCError("Service not found")
        msg = json.dumps(msg)
        for svc in services:
            client = tornado.httpclient.AsyncHTTPClient()
            try:
                response = yield client.fetch(
                    "http://%s/api/%s/" % (svc, self._api),
                    method="POST",
                    body=msg
                )
            except Exception, why:
                raise RPCError("RPC Call Failed: %s" % why)
            if not is_notify:
                result = json.loads(response.body)
                if result.get("error"):
                    raise RPCError("RPC Call Failed: %s" % result["error"])
                else:
                    raise tornado.gen.Return(result["result"])


class RPCMethod(object):
    """
    API Method wrapper
    """
    def __init__(self, proxy, name):
        self._proxy = proxy
        self._name = name
        self._metric = "rpc_call_%s_%s" % (proxy._service_name, name)

    @tornado.gen.coroutine
    def __call__(self, *args, **kwargs):
        self._proxy._service.logger.debug(
            "[REMOTE CALL>] %s.%s(%s, %s)",
            self._proxy._service_name,
            self._name, args, kwargs
        )
        self._proxy._service.metrics[self._metric] += 1
        result = yield self._proxy._call(self._name, *args, **kwargs)
        self._proxy._service.logger.debug(
            "[REMOTE CALL<] %s.%s",
            self._proxy._service_name,
            self._name
        )
        raise tornado.gen.Return(result)
