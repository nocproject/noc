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
import random
## Third-party modules
import tornado.concurrent
import tornado.gen
import tornado.httpclient
import ujson
from six.moves import queue
## NOC modules
from noc.lib.log import PrefixLoggerAdapter
from client import (RPCError, RPCNoService, RPCHTTPError,
                    RETRY_SOCKET_ERRORS, RPCException, RPCRemoteError)
import httpclient  # Setup global httpclient
from noc.core.perf import metrics

logger = logging.getLogger(__name__)

# Connection time
CONNECT_TIMEOUT = 20
# Total request time
REQUEST_TIMEOUT = 3600


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
        self._hints = hints
        self._sync = sync

    def __getattr__(self, item):
        @tornado.gen.coroutine
        def async_wrapper(*args, **kwargs):
            result = yield self._call(item, *args, **kwargs)
            raise tornado.gen.Return(result)

        def sync_wrapper(*args, **kwargs):
            @tornado.gen.coroutine
            def _call():
                try:
                    r = yield self._call(item, *args, **kwargs)
                    q.put(r)
                except tornado.gen.Return as e:
                    q.put(e.value)
                except Exception as e:
                    q.put(e)

            q = queue.Queue()
            self._service.ioloop.add_callback(_call)
            result = q.get()
            if isinstance(result, Exception):
                raise result
            return result

        if item.startswith("_"):
            return self.__dict__[item]
        elif self._sync:
            return sync_wrapper
        else:
            return async_wrapper

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
                        "Content-Type": "text/json",
                        "Connection": "close"
                    },
                    follow_redirects=False,
                    raise_error=False,
                    connect_timeout=CONNECT_TIMEOUT,
                    request_timeout=REQUEST_TIMEOUT
                )
            except socket.error as e:
                if e.args[0] in RETRY_SOCKET_ERRORS:
                    self._logger.debug("Socket error: %s" % e)
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
                self._logger.debug("Redirecting to %s", url)
                r = yield make_call(url, response.body, limit - 1)
                raise tornado.gen.Return(r)
            elif response.code == 599:
                self._logger.debug("Timed out")
                raise tornado.gen.Return(None)
            else:
                raise RPCHTTPError(
                    "HTTP Error %s: %s" % (
                        response.code, response.body
                    ))

        t0 = time.time()
        self._logger.debug(
            "[%sCALL>] %s.%s(%s, %s)",
            "SYNC " if self._sync else "",
            self._service_name,
            method, args, kwargs
        )
        metrics["rpc_call_%s_%s" % (self._service_name, method)] += 1
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
        t = time.time() - t0
        self._logger.debug(
            "[CALL<] %s.%s (%.2fms)",
            self._service_name,
            method,
            t * 1000
        )
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
