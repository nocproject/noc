# ----------------------------------------------------------------------
# Logging Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from time import perf_counter

# Third-party modules
from starlette.types import Scope, Receive, Send
from starlette.datastructures import Headers

# NOC modules
from noc.core.perf import metrics
from noc.core.comp import smart_text


class LoggingMiddleware(object):
    def __init__(self, app, logger=None, extended_logging=False):
        self.app = app
        self.logger = logger
        self.extended_logging = extended_logging

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        def to_suppress_logging():
            return (method == "GET") and (
                ((status == 200 or status == 429) and path in ("/health/", "/health"))
                or (status == 200 and path == "/metrics")
            )

        def is_mon_request():
            return status == 200 and path in ("/mon/", "/mon") and method == "GET"

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        t0 = perf_counter()
        try:
            await self.app(scope, receive, send)
        finally:
            t1 = perf_counter()
            status = 200
            method = scope["method"]
            path = scope["path"]
            if to_suppress_logging():
                pass
            elif is_mon_request():
                self.logger.debug("Monitoring request (%s)", scope["client"][0])
                metrics["mon_requests"] += 1
            else:
                if scope["query_string"]:
                    path = "%s?%s" % (path, smart_text(scope["query_string"]))
                remote_ip = scope["client"][0]
                status = 200
                if self.extended_logging:
                    headers = Headers(scope=scope)
                    user = headers.get("Remote-User", "-")
                    agent = headers.get("User-Agent", "-")
                    referer = headers.get("Referer", "-")
                    self.logger.info(
                        '%s %s - "%s %s" HTTP/1.1 %s "%s" %s %.2fms',
                        remote_ip,
                        user,
                        method,
                        path,
                        status,
                        referer,
                        agent,
                        1000.0 * (t1 - t0),
                    )
                    metrics["http_requests"] += 1
                    metrics["http_requests_%s" % method.lower()] += 1
                    metrics["http_response_%s" % status] += 1
                else:
                    self.logger.info(
                        "%s %s (%s) %.2fms",
                        method,
                        path,
                        remote_ip,
                        1000.0 * (t1 - t0),
                    )
                    metrics["http_requests", ("method", method.lower())] += 1
                    metrics["http_response", ("status", status)] += 1
