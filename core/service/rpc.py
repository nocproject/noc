# ----------------------------------------------------------------------
# RPC Wrapper
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
import logging
import random
from time import perf_counter
from typing import Optional
import asyncio
import threading

# Third-party modules
import orjson

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.http.async_client import HttpClient
from noc.core.perf import metrics
from noc.config import config
from noc.core.span import Span, get_current_span
from noc.core.ioloop.util import run_sync
from .error import RPCError, RPCNoService, RPCHTTPError, RPCException, RPCRemoteError
from noc.core.comp import DEFAULT_ENCODING

logger = logging.getLogger(__name__)

# Connection time
CONNECT_TIMEOUT = config.rpc.async_connect_timeout
# Total request time
REQUEST_TIMEOUT = config.rpc.async_request_timeout

# WARNING: later ujson versions are not thread-safe when dealing with floating numbers # deserealization,
# so we need the time to prove orjson is thread-safe and
# to remove the lock
# @todo: Check and remove the lock
_orjson_crash_lock = threading.Lock()


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
        self._client = HttpClient(
            max_redirects=None,
            headers={
                "X-NOC-Calling-Service": self._service.name.encode(DEFAULT_ENCODING),
                "Content-Type": b"application/json",
            },
            connect_timeout=CONNECT_TIMEOUT,
            timeout=REQUEST_TIMEOUT,
        )

    def __getattr__(self, item):
        async def _call(method, *args, **kwargs):
            async def make_call(url, body, limit=3) -> Optional[bytes]:
                req_headers = {}
                sample = 1 if span_ctx and span_id else 0
                with Span(
                    server=self._service_name,
                    service=method,
                    sample=sample,
                    context=span_ctx,
                    parent=span_id,
                ) as span:
                    if sample:
                        req_headers["X-NOC-Span-Ctx"] = str(span.span_context).encode(
                            DEFAULT_ENCODING
                        )
                        req_headers["X-NOC-Span"] = str(span.span_id).encode(DEFAULT_ENCODING)
                    code, headers, data = await self._client.post(url, body, headers=req_headers)
                    # Process response
                    if code == 200:
                        return data
                    elif code == 307:
                        # Process redirect
                        if not limit:
                            raise RPCException("Redirects limit exceeded")
                        url = headers.get("location")
                        self._logger.debug("Redirecting to %s", url)
                        r = await make_call(url.decode(DEFAULT_ENCODING), data, limit - 1)
                        return r
                    elif code in (598, 599):
                        span.set_error(code)
                        self._logger.debug("Timed out")
                        return None
                    else:
                        span.set_error(code)
                        raise RPCHTTPError(f"HTTP Error {code}: {body}")

            t0 = perf_counter()
            self._logger.debug(
                "[%sCALL>] %s.%s(%s, %s)",
                "SYNC " if self._sync else "",
                self._service_name,
                method,
                args,
                kwargs,
            )
            metrics["rpc_call", ("called_service", self._service_name), ("method", method)] += 1
            tid = next(self._tid)
            msg = {"method": method, "params": list(args)}
            is_notify = "_notify" in kwargs
            if not is_notify:
                msg["id"] = tid
            body = orjson.dumps(msg)
            # Get services
            response = None
            for t in self._service.iter_rpc_retry_timeout():
                # Resolve service against service catalog
                if self._hints:
                    svc = random.choice(self._hints)
                else:
                    svc = await self._service.dcs.resolve(self._service_name)
                response = await make_call(f"http://{svc}/api/{self._api}/", body)
                if response:
                    break
                else:
                    await asyncio.sleep(t)
            t = perf_counter() - t0
            self._logger.debug("[CALL<] %s.%s (%.2fms)", self._service_name, method, t * 1000)
            if response:
                if not is_notify:
                    try:
                        with _orjson_crash_lock:
                            result = orjson.loads(response)
                    except ValueError as e:
                        raise RPCHTTPError("Cannot decode json: %s" % e)
                    if result.get("error"):
                        self._logger.error("RPC call failed: %s", result["error"])
                        raise RPCRemoteError(
                            f'RPC call failed: {result["error"]["message"]}',
                            remote_code=result["error"].get("code", None),
                        )
                    else:
                        return result["result"]
                else:
                    # Notifications return None
                    return
            else:
                raise RPCNoService(f"No active service {self._service_name} found")

        async def async_wrapper(*args, **kwargs):
            return await _call(item, *args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            async def wrapper():
                return await _call(item, *args, **kwargs)

            return run_sync(wrapper)

        if item.startswith("_"):
            return self.__dict__[item]
        span_ctx, span_id = get_current_span()
        if self._sync:
            return sync_wrapper
        else:
            return async_wrapper
