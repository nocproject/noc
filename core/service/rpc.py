# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC Wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import itertools
import json
import logging
import socket
import random
import time
## Third-party modules
import tornado.concurrent
import tornado.gen
import tornado.httpclient
## NOC modules
from noc.lib.log import PrefixLoggerAdapter
from client import (RPCError, RPCNoService, RPCHTTPError,
                    RETRY_SOCKET_ERRORS, RPCException, RPCRemoteError)

logger = logging.getLogger(__name__)


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
        body = json.dumps(msg)
        # Get services
        services = self._service.config.get_service(
            self._service_name
        )
        timeouts = list(self._service.iter_rpc_retry_timeout())
        retries = len(timeouts) + 1
        if len(services) < retries:
            services *= retries
        response = None
        last = None
        for svc in random.sample(services, retries):
            client = tornado.httpclient.AsyncHTTPClient(force_instance=True)
            # Sleep when trying same instance
            if svc == last:
                yield tornado.gen.sleep(timeouts.pop())
            #
            last = svc
            try:
                response = yield client.fetch(
                    "http://%s/api/%s/" % (svc, self._api),
                    method="POST",
                    body=body,
                    headers={
                        "X-NOC-Calling-Service": self._service.name,
                        "Content-Type": "text/json"
                    }
                )
                break
            except tornado.httpclient.HTTPError, why:
                if why.code == 599:
                    logger.debug("Timed out")
                    continue
                raise RPCHTTPError("HTTP Error %s: %s" % (
                    why.code, why.message))
            except socket.error as e:
                if e.args[0] in RETRY_SOCKET_ERRORS:
                    logger.debug("Socket error: %s" % e)
                    continue
                raise RPCException(str(e))
            except Exception, why:
                raise RPCException(why)
        if response:
            if not is_notify:
                result = json.loads(response.body)
                if result.get("error"):
                    self._logger.error("RPC call failed: %s",
                                       result["error"])
                    raise RPCRemoteError(
                        "RPC call failed: %s" % result["error"]
                    )
                else:
                    raise tornado.gen.Return(result["result"])
            else:
                # Notifications return None
                raise tornado.gen.Return()
        else:
            raise RPCNoService(
                "No active service %s found" % self._service_name
            )


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
        t0 = time.time()
        self._proxy._logger.debug(
            "[CALL>] %s.%s(%s, %s)",
            self._proxy._service_name,
            self._name, args, kwargs
        )
        self._proxy._service.perf_metrics[self._metric] += 1
        result = yield self._proxy._call(self._name, *args, **kwargs)
        t = time.time() - t0
        self._proxy._logger.debug(
            "[CALL<] %s.%s (%.2fms)",
            self._proxy._service_name,
            self._name,
            t * 1000
        )
        raise tornado.gen.Return(result)
