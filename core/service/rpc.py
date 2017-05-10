# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC Wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import itertools
import logging
import socket
import time
import Queue
import random
## Third-party modules
import tornado.concurrent
import tornado.gen
import tornado.httpclient
import ujson
## NOC modules
from noc.lib.log import PrefixLoggerAdapter
from client import (RPCError, RPCNoService, RPCHTTPError,
                    RETRY_SOCKET_ERRORS, RPCException, RPCRemoteError)
import httpclient  # Setup global httpclient

logger = logging.getLogger(__name__)

# Connection time
CONNECT_TIMEOUT = 20
# Total request time
REQUEST_TIMEOUT = 3600


class AsyncRPCMethod(object):
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


class SyncRPCMethod(object):
    """
    API Method wrapper
    """
    def __init__(self, proxy, name):
        self._proxy = proxy
        self._name = name
        self._metric = "rpc_call_%s_%s" % (proxy._service_name, name)
        self._queue = Queue.Queue()

    @tornado.gen.coroutine
    def _call(self, *args, **kwargs):
        try:
            result = yield self._proxy._call(self._name, *args, **kwargs)
            self._queue.put(result)
        except tornado.gen.Return as e:
            self._queue.put(e.value)
        except Exception as e:
            self._queue.put(e)

    def __call__(self, *args, **kwargs):
        t0 = time.time()
        self._proxy._logger.debug(
            "[SYNC CALL>] %s.%s(%s, %s)",
            self._proxy._service_name,
            self._name, args, kwargs
        )
        self._proxy._service.perf_metrics[self._metric] += 1
        self._proxy._service.ioloop.add_callback(self._call, *args, **kwargs)
        result = self._queue.get()
        if isinstance(result, Exception):
            raise result
        t = time.time() - t0
        self._proxy._logger.debug(
            "[SYNC CALL<] %s.%s (%.2fms)",
            self._proxy._service_name,
            self._name,
            t * 1000
        )
        return result


class RPCProxy(object):
    """
    API Proxy
    """
    RPCError = RPCError

    def __init__(self, service, service_name, sync=False, hints=None):
        self._logger = PrefixLoggerAdapter(logger, service_name)
        self._service = service
        self._service_name = service_name
        self._api = service_name.split("-")[0]
        self._tid = itertools.count()
        self._transactions = {}
        self._methods = {}
        self._hints = hints
        if sync:
            self.rpc_cls = SyncRPCMethod
        else:
            self.rpc_cls = AsyncRPCMethod

    def __del__(self):
        self.close()

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            mw = self._methods.get(item)
            if not mw:
                mw = self.rpc_cls(self, item)
                self._methods[item] = mw
            return mw

    @tornado.gen.coroutine
    def _call(self, method, *args, **kwargs):
        @tornado.gen.coroutine
        def make_call(url, body, limit=3):
            client = tornado.httpclient.AsyncHTTPClient(
                force_instance=True,
                max_clients=1
            )
            try:
                response = yield client.fetch(
                    url,
                    method="POST",
                    body=body,
                    headers={
                        "X-NOC-Calling-Service": self._service.name,
                        "Content-Type": "text/json"
                    },
                    follow_redirects=False,
                    raise_error=False,
                    connect_timeout=CONNECT_TIMEOUT,
                    request_timeout=REQUEST_TIMEOUT
                )
            except socket.error as e:
                if e.args[0] in RETRY_SOCKET_ERRORS:
                    logger.debug("Socket error: %s" % e)
                    raise tornado.gen.Return(None)
                raise RPCException(str(e))
            except Exception as e:
                raise RPCException(str(e))
            finally:
                client.close()
                # Resolve CurlHTTPClient circular dependencies
                client._force_timeout_callback = None
                client._multi = None
            # Process response
            if response.code == 200:
                raise tornado.gen.Return(response)
            elif response.code == 307:
                # Process redirect
                if not limit:
                    raise RPCException("Redirects limit exceeded")
                url = response.headers.get("location")
                logger.debug("Redirecting to %s", url)
                r = yield make_call(url, response.body, limit - 1)
                raise tornado.gen.Return(r)
            elif response.code == 599:
                logger.debug("Timed out")
                raise tornado.gen.Return(None)
            else:
                raise RPCHTTPError(
                    "HTTP Error %s: %s" % (
                        response.code, response.body
                    ))

        tid = self._tid.next()
        msg = {
            "method": method,
            "params": list(args)
        }
        is_notify = "_notify" in kwargs
        if not is_notify:
            msg["id"] = tid
        body = ujson.dumps(msg)
        # Get services
        response = None
        for t in self._service.iter_rpc_retry_timeout():
            # Resolve service against service catalog
            if self._hints:
                svc = random.choice(self._hints)
            else:
                svc = yield self._service.dcs.resolve(self._service_name)
            response = yield make_call(
                "http://%s/api/%s/" % (svc, self._api),
                body
            )
            if response:
                break
            else:
                yield tornado.gen.sleep(t)
        if response:
            if not is_notify:
                result = ujson.loads(response.body)
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
