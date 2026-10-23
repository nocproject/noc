# ----------------------------------------------------------------------
# BaseMiddleware class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any


# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config


class BaseMiddleware:
    name = None

    def __init__(self, http) -> None:
        self.http = http

    def process_request(self, url: str, body: Any, headers: dict[str, bytes]):
        return url, body, headers

    def process_get(self, url: str, body: Any, headers: dict[str, bytes]):
        return self.process_request(url, body, headers)

    def process_post(self, url: str, body: Any, headers: dict[str, bytes]):
        return self.process_request(url, body, headers)

    def process_put(self, url: str, body: Any, headers: dict[str, bytes]):
        return self.process_request(url, body, headers)


middleware_loader = Loader[type[BaseMiddleware]](
    bases=config.iter_customized_bases("noc.core.script.http.middleware"),
    exclude=("base",),
)
