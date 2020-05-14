# ----------------------------------------------------------------------
# URLRequestId middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseMiddleware


class JSONRequestIdMiddleware(BaseMiddleware):
    """
    Append request_id:XXXXX to requests.
    Request id is automatically increased with each next request.
    `request_id` name may be changed via `request_id_param`
    """

    name = "jsonrequestid"

    def __init__(self, http, request_id_param="request_id"):
        super().__init__(http)
        self.request_id_param = request_id_param

    def process_post(self, url, body, headers):
        if isinstance(body, dict):
            body[self.request_id_param] = self.http.request_id
        return url, body, headers

    def process_put(self, url, body, headers):
        return self.process_post(url, body, headers)
