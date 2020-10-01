# ----------------------------------------------------------------------
# Span Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from starlette.types import Scope, Receive, Send
from starlette.datastructures import Headers

# NOC modules
from noc.core.span import Span


class SpanMiddleware(object):
    def __init__(self, app, service_name="service"):
        self.app = app
        self.service_name = service_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = Headers(scope=scope)
        span_ctx = headers.get("x-noc-span-ctx", 0)
        span_id = headers.get("x-noc-span", 0)
        sample = 1 if span_ctx and span_id else 0
        with Span(
            server=self.service_name,
            service="api",
            sample=sample,
            parent=span_id,
            context=span_ctx,
            in_label=scope["path"],
        ):
            await self.app(scope, receive, send)
