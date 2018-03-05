# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RPC Wrapper
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import itertools
import logging
import time
import random
import threading
import sys
# Third-party modules
import tornado.concurrent
import tornado.gen
import ujson
import six
# NOC modules
from noc.core.log import PrefixLoggerAdapter
from .client import (RPCError, RPCNoService, RPCHTTPError,
                     RPCException, RPCRemoteError)
from noc.core.http.client import fetch
from noc.core.perf import metrics
from noc.config import config
from noc.core.span import Span, get_current_span

logger = logging.getLogger(__name__)

# Connection time
CONNECT_TIMEOUT = config.rpc.async_connect_timeout
# Total request time
REQUEST_TIMEOUT = config.rpc.async_request_timeout


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
        def _call(method, *args, **kwargs):
            @tornado.gen.coroutine
            def make_call(url, body, limit=3):
                req_headers = {
                    "X-NOC-Calling-Service": self._service.name,
                    "Content-Type": "text/json"
                }
                sample = 1 if span_ctx and span_id else 0
                with Span(server=self._service_name, service=method,
                          sample=sample, context=span_ctx,
                          parent=span_id) as span:
                    if sample:
                        req_headers["X-NOC-Span-Ctx"] = span.span_context
                        req_headers["X-NOC-Span"] = span.span_id
                    code, headers, data = yield fetch(
                        url,
                        method="POST",
                        headers=req_headers,
                        body=body,
                        connect_timeout=CONNECT_TIMEOUT,
                        request_timeout=REQUEST_TIMEOUT
                    )
                    # Process response
                    if code == 200:
                        raise tornado.gen.Return(data)
                    elif code == 307:
                        # Process redirect
                        if not limit:
                            raise RPCException("Redirects limit exceeded")
                        url = headers.get("location")
                        self._logger.debug("Redirecting to %s", url)
                        r = yield make_call(url, data, limit - 1)
                        raise tornado.gen.Return(r)
                    elif code in (598, 599):
                        span.error_code = code
                        self._logger.debug("Timed out")
                        raise tornado.gen.Return(None)
                    else:
                        span.error_code = code
                        raise RPCHTTPError(
                            "HTTP Error %s: %s" % (
                                code, body
                            ))

            t0 = time.time()
            self._logger.debug(
                "[%sCALL>] %s.%s(%s, %s)",
                "SYNC " if self._sync else "",
                self._service_name,
                method, args, kwargs
            )
            metrics["rpc_call", ("called_service", self._service_name), ("method", method)] += 1
            tid = next(self._tid)
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
                    try:
                        result = ujson.loads(response)
                    except ValueError as e:
                        raise RPCHTTPError("Cannot decode json: %s" % e)
                    if result.get("error"):
                        self._logger.error("RPC call failed: %s",
                                           result["error"])
                        raise RPCRemoteError(
                            "RPC call failed: %s" % result["error"],
                            remote_code=result.get("code", None)
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

        @tornado.gen.coroutine
        def async_wrapper(*args, **kwargs):
            result = yield _call(item, *args, **kwargs)
            raise tornado.gen.Return(result)

        def sync_wrapper(*args, **kwargs):
            @tornado.gen.coroutine
            def _sync_call():
                try:
                    r = yield _call(item, *args, **kwargs)
                    result.append(r)
                except tornado.gen.Return as e:
                    result.append(e.value)
                except Exception:
                    error.append(sys.exc_info())
                finally:
                    ev.set()

            ev = threading.Event()
            result = []
            error = []
            self._service.ioloop.add_callback(_sync_call)
            ev.wait()
            if error:
                six.reraise(*error[0])
            else:
                return result[0]

        if item.startswith("_"):
            return self.__dict__[item]
        span_ctx, span_id = get_current_span()
        if self._sync:
            return sync_wrapper
        else:
            return async_wrapper
