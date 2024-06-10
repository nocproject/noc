# ----------------------------------------------------------------------
# BaseMiddleware class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any


class BaseMiddleware(object):
    name = None

    def __init__(self, http):
        self.http = http

    def process_request(self, url: str, body: Any, headers: Dict[str, bytes]):
        return url, body, headers

    def process_get(self, url: str, body: Any, headers: Dict[str, bytes]):
        return self.process_request(url, body, headers)

    def process_post(self, url: str, body: Any, headers: Dict[str, bytes]):
        return self.process_request(url, body, headers)

    def process_put(self, url: str, body: Any, headers: Dict[str, bytes]):
        return self.process_request(url, body, headers)
